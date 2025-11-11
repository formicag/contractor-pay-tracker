"""
File Management API Endpoints

Provides API endpoints for file listing, navigation, and deletion
"""

from flask import request, jsonify
import logging

def register_file_endpoints(app, payfiles_table, s3_client):
    """Register file management endpoints with the Flask app"""

    @app.route('/api/files/list', methods=['GET'])
    def api_files_list():
        """
        List all payfiles from DynamoDB

        Query Parameters:
            - status: Filter by status
            - umbrella: Filter by umbrella company
            - order: Sort order (asc/desc, default: desc for newest first)

        Returns: JSON with files array and total count
        """
        try:
            # Get query parameters
            status_filter = request.args.get('status')
            umbrella_filter = request.args.get('umbrella')
            order = request.args.get('order', 'desc')  # Default to newest first

            app.logger.info(f"Listing files: status={status_filter}, umbrella={umbrella_filter}, order={order}")

            # Scan all files (excluding umbrella company reference data)
            scan_kwargs = {}

            # Build filter expression
            filter_parts = []
            expression_values = {}

            # Exclude umbrella company data
            filter_parts.append('NOT begins_with(file_id, :umbrella_prefix)')
            expression_values[':umbrella_prefix'] = 'UMBRELLA#'

            # Add status filter
            if status_filter:
                filter_parts.append('#status = :status')
                expression_values[':status'] = status_filter
                scan_kwargs['ExpressionAttributeNames'] = {'#status': 'status'}

            # Add umbrella filter
            if umbrella_filter:
                filter_parts.append('umbrella_company = :umbrella')
                expression_values[':umbrella'] = umbrella_filter

            if filter_parts:
                scan_kwargs['FilterExpression'] = ' AND '.join(filter_parts)
                scan_kwargs['ExpressionAttributeValues'] = expression_values

            # Scan table
            response = payfiles_table.scan(**scan_kwargs)
            items = response.get('Items', [])

            # Handle pagination
            while 'LastEvaluatedKey' in response:
                scan_kwargs['ExclusiveStartKey'] = response['LastEvaluatedKey']
                response = payfiles_table.scan(**scan_kwargs)
                items.extend(response.get('Items', []))

            # Format files for frontend
            files_list = []
            for item in items:
                file_data = {
                    'file_id': item.get('file_id', 'Unknown'),
                    'filename': item.get('filename', 'Unknown'),
                    'status': item.get('status', 'unknown'),
                    'contractor_name': item.get('contractor_name', 'Unknown'),
                    'umbrella_company': item.get('umbrella_company', 'Unknown'),
                    'uploaded_at': item.get('uploaded_at', 0),
                    'created_at': item.get('created_at', 0),
                    'processing_status': item.get('processing_status', 'unknown'),
                    'file_size': item.get('file_size', 0)
                }
                files_list.append(file_data)

            # Sort files by uploaded_at timestamp
            reverse_sort = (order == 'desc')
            files_list.sort(key=lambda x: int(x.get('uploaded_at', 0) or 0), reverse=reverse_sort)

            app.logger.info(f"Found {len(files_list)} files")

            return jsonify({
                'files': files_list,
                'total': len(files_list)
            })

        except Exception as e:
            app.logger.error(f"Error listing files: {str(e)}")
            import traceback
            app.logger.error(traceback.format_exc())
            return jsonify({'error': 'Failed to list files', 'message': str(e)}), 500


    @app.route('/api/files/<file_id>', methods=['GET'])
    def api_get_file(file_id):
        """Get a single file's details"""
        try:
            response = payfiles_table.get_item(Key={'file_id': file_id})

            if 'Item' not in response:
                return jsonify({'error': 'File not found'}), 404

            item = response['Item']

            file_data = {
                'file_id': item.get('file_id'),
                'filename': item.get('filename'),
                'status': item.get('status'),
                'contractor_name': item.get('contractor_name', 'Unknown'),
                'umbrella_company': item.get('umbrella_company'),
                'uploaded_at': item.get('uploaded_at'),
                'created_at': item.get('created_at'),
                'processing_status': item.get('processing_status'),
                'file_size': item.get('file_size'),
                's3_bucket': item.get('s3_bucket'),
                's3_key': item.get('s3_key')
            }

            return jsonify(file_data)

        except Exception as e:
            app.logger.error(f"Error getting file {file_id}: {str(e)}")
            return jsonify({'error': 'Failed to get file', 'message': str(e)}), 500


    @app.route('/api/files/<file_id>', methods=['DELETE'])
    def api_delete_file(file_id):
        """Delete a file from S3 and DynamoDB"""
        try:
            app.logger.info(f"Deleting file: {file_id}")

            # Get file metadata first
            response = payfiles_table.get_item(Key={'file_id': file_id})

            if 'Item' not in response:
                return jsonify({'error': 'File not found'}), 404

            item = response['Item']
            s3_bucket = item.get('s3_bucket')
            s3_key = item.get('s3_key')

            deletion_summary = {
                'file_id': file_id,
                'filename': item.get('filename'),
                's3_deleted': False,
                'db_deleted': False
            }

            # Delete from S3
            if s3_bucket and s3_key:
                try:
                    s3_client.delete_object(Bucket=s3_bucket, Key=s3_key)
                    deletion_summary['s3_deleted'] = True
                    app.logger.info(f"Deleted from S3: s3://{s3_bucket}/{s3_key}")
                except Exception as e:
                    app.logger.error(f"Failed to delete from S3: {str(e)}")

            # Delete from DynamoDB
            try:
                payfiles_table.delete_item(Key={'file_id': file_id})
                deletion_summary['db_deleted'] = True
                app.logger.info(f"Deleted from DynamoDB: {file_id}")
            except Exception as e:
                app.logger.error(f"Failed to delete from DynamoDB: {str(e)}")
                raise

            return jsonify({
                'message': 'File deleted successfully',
                'deleted': deletion_summary
            })

        except Exception as e:
            app.logger.error(f"Error deleting file {file_id}: {str(e)}")
            import traceback
            app.logger.error(traceback.format_exc())
            return jsonify({'error': 'Failed to delete file', 'message': str(e)}), 500
