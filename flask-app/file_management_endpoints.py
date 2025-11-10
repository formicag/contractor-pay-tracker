"""
File Management API Endpoints for Debugging Interface

These endpoints provide:
1. File listing with ordering and filtering
2. Navigation support (previous/next file IDs)
3. Comprehensive file deletion (S3 + DynamoDB)
"""

# Add these endpoints to flask-app/app.py after the /api/files endpoint


@app.route('/api/files/list', methods=['GET'])
def api_files_list():
    """
    API endpoint to list all files with ordering and filtering

    Query Parameters:
        - status: Filter by status (COMPLETED, ERROR, FAILED, PROCESSING)
        - umbrella_code: Filter by umbrella company code
        - order: Sort order (asc/desc, default: asc for oldest first)

    Returns: JSON with ordered files array and total count
    """
    try:
        # Get query parameters
        status_filter = request.args.get('status')
        umbrella_filter = request.args.get('umbrella_code')
        order = request.args.get('order', 'asc')  # Default to oldest first

        # Build filter expression
        filter_expr = 'EntityType = :et'
        expression_values = {':et': 'File'}
        expression_names = {}

        # Add status filter if provided
        if status_filter:
            filter_expr += ' AND #status = :status'
            expression_values[':status'] = status_filter
            expression_names['#status'] = 'Status'

        # Add umbrella filter if provided
        if umbrella_filter:
            filter_expr += ' AND UmbrellaCode = :umbrella'
            expression_values[':umbrella'] = umbrella_filter

        # Query DynamoDB for File records
        scan_kwargs = {
            'FilterExpression': filter_expr,
            'ExpressionAttributeValues': expression_values
        }

        # Add ExpressionAttributeNames if status filter is used (reserved keyword)
        if expression_names:
            scan_kwargs['ExpressionAttributeNames'] = expression_names

        response = table.scan(**scan_kwargs)

        files_list = []
        for item in response.get('Items', []):
            file_data = {
                'file_id': item.get('FileID'),
                'filename': item.get('OriginalFilename', 'Unknown'),
                'status': item.get('Status', 'UNKNOWN'),
                'uploaded_at': item.get('UploadedAt', item.get('CreatedAt', '')),
                'umbrella_code': item.get('UmbrellaCode', 'Unknown')
            }
            files_list.append(file_data)

        # Sort by UploadedAt timestamp
        reverse_sort = (order == 'desc')
        files_list.sort(key=lambda x: x.get('uploaded_at', ''), reverse=reverse_sort)

        return jsonify({
            'files': files_list,
            'total': len(files_list)
        })

    except Exception as e:
        app.logger.error(f"Error listing files: {str(e)}")
        return jsonify({'error': 'Failed to list files', 'message': str(e)}), 500


@app.route('/api/files/<file_id>/navigation', methods=['GET'])
def api_file_navigation(file_id):
    """
    API endpoint to get navigation info (previous/next file IDs)

    Returns: JSON with previous and next file IDs, current index, and total
    """
    try:
        # Get query parameters for filtering
        status_filter = request.args.get('status')
        umbrella_filter = request.args.get('umbrella_code')

        # Build filter expression (same as list endpoint)
        filter_expr = 'EntityType = :et'
        expression_values = {':et': 'File'}
        expression_names = {}

        if status_filter:
            filter_expr += ' AND #status = :status'
            expression_values[':status'] = status_filter
            expression_names['#status'] = 'Status'

        if umbrella_filter:
            filter_expr += ' AND UmbrellaCode = :umbrella'
            expression_values[':umbrella'] = umbrella_filter

        # Query DynamoDB
        scan_kwargs = {
            'FilterExpression': filter_expr,
            'ExpressionAttributeValues': expression_values
        }

        if expression_names:
            scan_kwargs['ExpressionAttributeNames'] = expression_names

        response = table.scan(**scan_kwargs)

        # Build and sort file list (oldest first)
        files_list = []
        for item in response.get('Items', []):
            files_list.append({
                'file_id': item.get('FileID'),
                'uploaded_at': item.get('UploadedAt', item.get('CreatedAt', ''))
            })

        files_list.sort(key=lambda x: x.get('uploaded_at', ''))

        # Find current file index
        current_index = None
        for idx, file_item in enumerate(files_list):
            if file_item['file_id'] == file_id:
                current_index = idx
                break

        if current_index is None:
            return jsonify({'error': 'File not found'}), 404

        # Get previous and next file IDs
        previous_id = files_list[current_index - 1]['file_id'] if current_index > 0 else None
        next_id = files_list[current_index + 1]['file_id'] if current_index < len(files_list) - 1 else None

        return jsonify({
            'previous': previous_id,
            'next': next_id,
            'current_index': current_index + 1,  # 1-indexed for display
            'total': len(files_list)
        })

    except Exception as e:
        app.logger.error(f"Error getting file navigation: {str(e)}")
        return jsonify({'error': 'Failed to get navigation info', 'message': str(e)}), 500


# UPDATE THE EXISTING DELETE ENDPOINT TO:

@app.route('/api/files/<file_id>', methods=['DELETE'])
def api_delete_file(file_id):
    """
    API endpoint to delete a file comprehensively

    Deletes:
    - S3 file from bucket
    - File metadata record (PK=FILE#{file_id}, SK=METADATA)
    - All PayRecord entries for this file
    - All ValidationError records
    - All ValidationWarning records

    Returns: JSON with success status
    """
    try:
        app.logger.info(f"Starting deletion of file: {file_id}")

        # 1. Get file metadata to get S3 location
        file_response = table.get_item(
            Key={
                'PK': f'FILE#{file_id}',
                'SK': 'METADATA'
            }
        )

        if 'Item' not in file_response:
            return jsonify({'error': 'File not found'}), 404

        file_item = file_response['Item']
        s3_bucket = file_item.get('S3Bucket')
        s3_key = file_item.get('S3Key')

        deletion_summary = {
            'file_id': file_id,
            'filename': file_item.get('OriginalFilename'),
            's3_deleted': False,
            'metadata_deleted': False,
            'payrecords_deleted': 0,
            'errors_deleted': 0,
            'warnings_deleted': 0
        }

        # 2. Delete from S3
        if s3_bucket and s3_key:
            try:
                s3_client.delete_object(Bucket=s3_bucket, Key=s3_key)
                deletion_summary['s3_deleted'] = True
                app.logger.info(f"Deleted S3 object: s3://{s3_bucket}/{s3_key}")
            except ClientError as e:
                app.logger.error(f"Error deleting S3 object: {str(e)}")
                # Continue with DynamoDB deletion even if S3 fails

        # 3. Query all records for this file (PayRecords, Errors, Warnings)
        records_response = table.query(
            KeyConditionExpression=Key('PK').eq(f'FILE#{file_id}')
        )

        # 4. Batch delete all records
        items_to_delete = records_response.get('Items', [])

        with table.batch_writer() as batch:
            for item in items_to_delete:
                pk = item['PK']
                sk = item['SK']
                entity_type = item.get('EntityType', '')

                # Delete the item
                batch.delete_item(Key={'PK': pk, 'SK': sk})

                # Track what was deleted
                if sk == 'METADATA':
                    deletion_summary['metadata_deleted'] = True
                elif entity_type == 'PayRecord':
                    deletion_summary['payrecords_deleted'] += 1
                elif entity_type == 'ValidationError':
                    deletion_summary['errors_deleted'] += 1
                elif entity_type == 'ValidationWarning':
                    deletion_summary['warnings_deleted'] += 1

                app.logger.info(f"Deleted {entity_type}: {pk} / {sk}")

        app.logger.info(f"File deletion complete: {deletion_summary}")

        return jsonify({
            'message': 'File deleted successfully',
            'deleted': deletion_summary
        })

    except ClientError as e:
        app.logger.error(f"DynamoDB error deleting file: {str(e)}")
        return jsonify({'error': 'Database error', 'message': str(e)}), 500
    except Exception as e:
        app.logger.error(f"Error deleting file: {str(e)}")
        import traceback
        app.logger.error(traceback.format_exc())
        return jsonify({'error': 'Failed to delete file', 'message': str(e)}), 500
