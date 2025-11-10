"""
Contractor Pay Tracker - Flask Web Application

Main Flask application with smart port selection
"""

import os
import socket
from datetime import datetime
import uuid
import json
import logging
import webbrowser
import threading

from flask import Flask, render_template, request, jsonify, redirect, url_for, send_file
from dotenv import load_dotenv
import boto3
from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError
from decimal import Decimal
from logging_config import setup_logging, log_request, log_response, log_errors
import openpyxl
import io

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Setup comprehensive logging
setup_logging(app)
log_request(app)
log_response(app)
log_errors(app)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

# AWS Configuration
AWS_REGION = os.environ.get('AWS_REGION', 'eu-west-2')
AWS_PROFILE = os.environ.get('AWS_PROFILE', 'AdministratorAccess-016164185850')
S3_BUCKET = os.environ.get('S3_BUCKET_NAME', '')
DYNAMODB_TABLE = os.environ.get('DYNAMODB_TABLE_NAME', '')
FILE_PROCESSOR_ARN = os.environ.get('FILE_PROCESSOR_ARN', '')

# Initialize AWS clients
session = boto3.Session(profile_name=AWS_PROFILE, region_name=AWS_REGION)
s3_client = session.client('s3')
dynamodb = session.resource('dynamodb')
lambda_client = session.client('lambda')
table = dynamodb.Table(DYNAMODB_TABLE) if DYNAMODB_TABLE else None


def calculate_margin(sell_rate, buy_rate):
    """
    Calculate margin and margin percentage from sell and buy rates

    Args:
        sell_rate: Sell rate (what we charge customers)
        buy_rate: Buy rate (what we pay contractors)

    Returns:
        tuple: (margin, margin_percent) where:
            - margin = sell_rate - buy_rate
            - margin_percent = ((sell_rate - buy_rate) / sell_rate) * 100

    Raises:
        ValueError: If sell_rate <= buy_rate (would result in zero or negative margin)
    """
    sell_rate = Decimal(str(sell_rate))
    buy_rate = Decimal(str(buy_rate))

    # Validate that margin will be positive
    if sell_rate <= buy_rate:
        raise ValueError(f"Sell Rate (£{sell_rate}) must be greater than Buy Rate (£{buy_rate}). Margin cannot be zero or negative.")

    margin = sell_rate - buy_rate
    margin_percent = (margin / sell_rate) * Decimal('100')

    return margin, margin_percent


def find_available_port(start_port=5555, max_attempts=100):
    """
    Find an available port starting from start_port

    Args:
        start_port: Starting port number (default: 5555)
        max_attempts: Maximum number of ports to try

    Returns:
        int: Available port number
    """
    for port in range(start_port, start_port + max_attempts):
        try:
            # Try to bind to the port
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex(('127.0.0.1', port))
            sock.close()

            if result != 0:  # Port is available
                return port
        except socket.error:
            continue

    # Fallback to a random high port if all attempts fail
    return start_port + max_attempts


@app.route('/')
def index():
    """Home page - redirect to upload page"""
    return redirect(url_for('upload'))


@app.route('/upload')
def upload():
    """File upload page"""
    return render_template('upload.html')


@app.route('/files')
def files():
    """Files management dashboard"""
    return render_template('files.html')


@app.route('/file/<file_id>')
def file_detail(file_id):
    """File detail page with validation errors"""
    return render_template('file_detail.html', file_id=file_id)


@app.route('/contractors')
def contractors():
    """Contractors management page"""
    return render_template('contractors.html')


@app.route('/perm-staff')
def perm_staff():
    """Permanent staff management page"""
    return render_template('perm_staff.html')


@app.route('/contractors/edit/<email>')
def edit_contractor(email):
    """Edit contractor page"""
    try:
        # Query DynamoDB for contractor by email
        response = table.get_item(
            Key={
                'PK': f'CONTRACTOR#{email}',
                'SK': 'METADATA'
            }
        )

        if 'Item' not in response:
            return render_template('404.html'), 404

        contractor = response['Item']

        # Use Email or ResourceContactEmail (backward compatibility)
        contractor_email = contractor.get('Email') or contractor.get('ResourceContactEmail', email)

        # Format contractor data for template
        contractor_data = {
            'email': contractor_email,
            'contractor_id': contractor.get('ContractorID'),
            'title': contractor.get('Title', 'Mr'),
            'first_name': contractor.get('FirstName', ''),
            'last_name': contractor.get('LastName', ''),
            'job_title': contractor.get('JobTitle'),
            'resource_email': contractor.get('ResourceEmail') or contractor.get('ResourceContactEmail'),
            'nasstar_email': contractor.get('NasstarEmail'),
            'line_manager_email': contractor.get('LineManagerEmail'),
            'sell_rate': contractor.get('SellRate', 0),
            'buy_rate': contractor.get('BuyRate', 0),
            'snow_unit_rate': contractor.get('SNOWUnitRate'),
            'engagement_type': contractor.get('EngagementType'),
            'customer': contractor.get('Customer'),
            'snow_product': contractor.get('SNOWProduct') or contractor.get('SNOWProductOffering'),
            'is_active': contractor.get('IsActive', contractor.get('Status', 'ACTIVE') == 'ACTIVE')
        }

        return render_template('edit_contractor.html', contractor=contractor_data)

    except Exception as e:
        app.logger.error(f"Error loading contractor for edit: {str(e)}")
        return render_template('500.html'), 500


@app.route('/umbrella-dashboard')
def umbrella_dashboard():
    """Umbrella company reporting dashboard"""
    return render_template('umbrella_dashboard.html')


@app.route('/debug')
def debug():
    """Debugging interface for comparing Excel files with database records"""
    return render_template('debug.html')


@app.route('/ops/debug-files')
def debug_files():
    """Debug files page - Three-panel view for operations"""
    return render_template('debug_files.html')


@app.route('/api/upload', methods=['POST'])
def api_upload():
    """
    API endpoint for file upload

    Expected: multipart/form-data with file
    Returns: JSON with file_id and status
    """
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    if not file.filename.endswith('.xlsx'):
        return jsonify({'error': 'Only .xlsx files are supported'}), 400

    # TODO: Implement S3 upload via Lambda
    # For now, return mock response

    return jsonify({
        'message': 'File upload endpoint ready',
        'filename': file.filename,
        'size': len(file.read()),
        'status': 'pending'
    })


@app.route('/api/files', methods=['GET'])
def api_files():
    """
    API endpoint to list files

    Returns: JSON with files list
    """
    try:
        # First, load all Period records for date lookup
        periods_response = table.scan(
            FilterExpression='EntityType = :et',
            ExpressionAttributeValues={':et': 'Period'}
        )

        # Create period lookup dict
        periods_dict = {}
        for period_item in periods_response.get('Items', []):
            period_id = period_item.get('PeriodNumber')
            if period_id:
                start_date = period_item.get('WorkStartDate', '')
                end_date = period_item.get('WorkEndDate', '')
                periods_dict[period_id] = {
                    'start': start_date,
                    'end': end_date
                }

        # Query DynamoDB for all File records
        response = table.scan(
            FilterExpression='EntityType = :et',
            ExpressionAttributeValues={':et': 'File'}
        )

        files_list = []
        for item in response.get('Items', []):
            file_id = item.get('FileID')

            # Get period from PayRecords for this file
            period_display = 'N/A'
            if file_id:
                try:
                    # Query PayRecords for this file (they use PK = FILE#{file_id})
                    payrecord_response = table.query(
                        KeyConditionExpression=Key('PK').eq(f'FILE#{file_id}') & Key('SK').begins_with('RECORD#'),
                        Limit=1
                    )

                    if payrecord_response.get('Items'):
                        period_id = payrecord_response['Items'][0].get('PeriodID', 'N/A')

                        # Look up period dates
                        if period_id in periods_dict:
                            period_info = periods_dict[period_id]
                            start = period_info['start']
                            end = period_info['end']

                            # Format as "2 Jun - 29 Jun 2025"
                            if start and end:
                                from datetime import datetime
                                start_dt = datetime.fromisoformat(start)
                                end_dt = datetime.fromisoformat(end)
                                # Use .day to avoid platform-specific strftime issues
                                period_display = f"{start_dt.day} {start_dt.strftime('%b')} - {end_dt.day} {end_dt.strftime('%b %Y')}"
                            else:
                                period_display = f"Period {period_id}"
                        else:
                            period_display = f"Period {period_id}" if period_id != 'N/A' else 'N/A'
                except:
                    pass  # If query fails, keep period as N/A

            # Extract file info
            file_data = {
                'file_id': file_id,
                'filename': item.get('OriginalFilename', 'Unknown'),
                'umbrella': item.get('UmbrellaCode', 'Unknown'),
                'period': period_display,
                'status': item.get('Status', 'UNKNOWN'),
                'uploaded_at': item.get('UploadedAt', item.get('CreatedAt', '')),
                'records': item.get('ValidRecords', 0)
            }

            # Add warnings/errors if present
            if item.get('TotalWarnings', 0) > 0:
                file_data['warnings'] = item.get('TotalWarnings')
            if item.get('TotalErrors', 0) > 0:
                file_data['errors'] = item.get('TotalErrors')

            files_list.append(file_data)

        # Sort by upload date (newest first)
        files_list.sort(key=lambda x: x.get('uploaded_at', ''), reverse=True)

        return jsonify({'files': files_list})

    except Exception as e:
        logger.error(f"Error fetching files: {str(e)}")
        return jsonify({'error': 'Failed to fetch files', 'message': str(e)}), 500


@app.route('/api/file/<file_id>', methods=['GET'])
def api_file_detail(file_id):
    """
    API endpoint to get file details

    Returns: JSON with file metadata and validation results
    """
    # TODO: Query DynamoDB for file details

    # Mock data
    mock_file = {
        'file_id': file_id,
        'filename': 'NASA_GCI_Nasstar_Contractor_Pay_01092025.xlsx',
        'umbrella': 'NASA',
        'period': 8,
        'status': 'COMPLETED',
        'uploaded_at': '2025-09-01T14:30:00Z',
        'total_records': 14,
        'valid_records': 14,
        'errors': [],
        'warnings': []
    }

    return jsonify(mock_file)


@app.route('/api/file/<file_id>', methods=['DELETE'])
def api_delete_file(file_id):
    """
    API endpoint to delete a file completely (hard delete)
    Removes: S3 file, File metadata, PayRecords, ValidationErrors, ValidationWarnings

    Returns: JSON with success status
    """
    try:
        app.logger.info(f"Deleting file {file_id} and all associated data")

        # Get file metadata to find S3 location
        file_response = table.get_item(
            Key={'PK': f'FILE#{file_id}', 'SK': 'METADATA'}
        )

        if 'Item' not in file_response:
            return jsonify({'error': 'File not found'}), 404

        file_metadata = file_response['Item']
        s3_bucket = file_metadata.get('S3Bucket', S3_BUCKET)
        s3_key = file_metadata.get('S3Key')

        # Delete S3 file
        if s3_key:
            try:
                s3_client.delete_object(Bucket=s3_bucket, Key=s3_key)
                app.logger.info(f"Deleted S3 object: {s3_bucket}/{s3_key}")
            except Exception as e:
                app.logger.error(f"Error deleting S3 object: {str(e)}")

        # Query all items with PK = FILE#{file_id}
        response = table.query(
            KeyConditionExpression=Key('PK').eq(f'FILE#{file_id}')
        )

        # Delete all items in batch
        with table.batch_writer() as batch:
            for item in response.get('Items', []):
                batch.delete_item(
                    Key={
                        'PK': item['PK'],
                        'SK': item['SK']
                    }
                )

        app.logger.info(f"Deleted {len(response.get('Items', []))} items from DynamoDB for file {file_id}")

        return jsonify({
            'success': True,
            'message': f'File {file_id} deleted successfully',
            'items_deleted': len(response.get('Items', []))
        })

    except Exception as e:
        app.logger.error(f"Error deleting file {file_id}: {str(e)}")
        return jsonify({'error': 'Failed to delete file', 'message': str(e)}), 500


@app.route('/api/files/list', methods=['GET'])
def api_files_list():
    """
    API endpoint to list all files ordered by upload timestamp (oldest first)

    Returns: JSON with files list
    """
    try:
        # Query DynamoDB for all File records
        response = table.scan(
            FilterExpression='EntityType = :et',
            ExpressionAttributeValues={':et': 'File'}
        )

        files_list = []
        for item in response.get('Items', []):
            file_data = {
                'file_id': item.get('FileID'),
                'filename': item.get('OriginalFilename', 'Unknown'),
                'uploaded_at': item.get('UploadedAt', item.get('CreatedAt', '')),
                'status': item.get('Status', 'UNKNOWN'),
                'umbrella_code': item.get('UmbrellaCode'),
                'umbrella_name': item.get('UmbrellaName'),
                'period_start': item.get('PeriodStart'),
                'period_end': item.get('PeriodEnd')
            }
            files_list.append(file_data)

        # Sort by upload date (oldest first) for systematic review
        files_list.sort(key=lambda x: x.get('uploaded_at', ''))

        return jsonify({'files': files_list, 'count': len(files_list)})

    except Exception as e:
        app.logger.error(f"Error fetching files list: {str(e)}")
        return jsonify({'error': 'Failed to fetch files', 'message': str(e)}), 500


@app.route('/api/files/<file_id>/navigation', methods=['GET'])
def api_file_navigation(file_id):
    """
    API endpoint to get navigation info (previous/next file IDs)

    Query Parameters:
        - status: Filter by status (optional)
        - umbrella_code: Filter by umbrella company code (optional)

    Returns: JSON with previous and next file IDs, current index, and total
    """
    try:
        # Get query parameters for filtering
        status_filter = request.args.get('status')
        umbrella_filter = request.args.get('umbrella_code')

        # Build filter expression
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


@app.route('/api/files/<file_id>/xls', methods=['GET'])
def api_file_xls(file_id):
    """
    API endpoint to fetch Excel file from S3 and return as JSON

    Returns: JSON with Excel data organized by sheets
    """
    try:
        # Get file metadata
        file_response = table.get_item(
            Key={'PK': f'FILE#{file_id}', 'SK': 'METADATA'}
        )

        if 'Item' not in file_response:
            return jsonify({'error': 'File not found'}), 404

        file_metadata = file_response['Item']
        s3_bucket = file_metadata.get('S3Bucket', S3_BUCKET)
        s3_key = file_metadata.get('S3Key')

        if not s3_key:
            return jsonify({'error': 'S3 key not found in file metadata'}), 404

        # Download file from S3
        file_obj = io.BytesIO()
        s3_client.download_fileobj(s3_bucket, s3_key, file_obj)
        file_obj.seek(0)

        # Load workbook
        workbook = openpyxl.load_workbook(file_obj, data_only=True)

        # Convert to JSON structure
        sheets_data = {}
        for sheet_name in workbook.sheetnames:
            sheet = workbook[sheet_name]
            sheet_data = []

            # Get all rows
            for row in sheet.iter_rows(values_only=True):
                # Convert Decimal to float for JSON serialization
                row_data = []
                for cell in row:
                    if isinstance(cell, Decimal):
                        row_data.append(float(cell))
                    elif cell is None:
                        row_data.append('')
                    else:
                        row_data.append(cell)
                sheet_data.append(row_data)

            sheets_data[sheet_name] = sheet_data

        return jsonify({
            'file_id': file_id,
            'filename': file_metadata.get('OriginalFilename', 'Unknown'),
            'sheets': sheets_data
        })

    except ClientError as e:
        app.logger.error(f"S3 error fetching file {file_id}: {str(e)}")
        return jsonify({'error': 'Failed to fetch file from S3', 'message': str(e)}), 500
    except Exception as e:
        app.logger.error(f"Error fetching Excel file {file_id}: {str(e)}")
        return jsonify({'error': 'Failed to process Excel file', 'message': str(e)}), 500


@app.route('/api/files/<file_id>/database', methods=['GET'])
def api_file_database(file_id):
    """
    API endpoint to get all database records for a file

    Returns: JSON with file metadata, pay records, and errors
    """
    try:
        # Get file metadata
        file_response = table.get_item(
            Key={'PK': f'FILE#{file_id}', 'SK': 'METADATA'}
        )

        if 'Item' not in file_response:
            return jsonify({'error': 'File not found'}), 404

        file_metadata = file_response['Item']

        # Query all items for this file
        response = table.query(
            KeyConditionExpression=Key('PK').eq(f'FILE#{file_id}')
        )

        # Organize data by type
        pay_records = []
        validation_errors = []
        validation_warnings = []

        for item in response.get('Items', []):
            entity_type = item.get('EntityType', '')

            if entity_type == 'PayRecord':
                # Convert Decimal to float
                record_data = {k: (float(v) if isinstance(v, Decimal) else v) for k, v in item.items()}
                pay_records.append(record_data)
            elif entity_type == 'ValidationError':
                validation_errors.append(item)
            elif entity_type == 'ValidationWarning':
                validation_warnings.append(item)

        # Sort pay records by SK (record number)
        pay_records.sort(key=lambda x: x.get('SK', ''))

        return jsonify({
            'file_metadata': {k: (float(v) if isinstance(v, Decimal) else v) for k, v in file_metadata.items()},
            'pay_records': pay_records,
            'pay_records_count': len(pay_records),
            'validation_errors': validation_errors,
            'validation_warnings': validation_warnings
        })

    except Exception as e:
        app.logger.error(f"Error fetching database data for file {file_id}: {str(e)}")
        return jsonify({'error': 'Failed to fetch database data', 'message': str(e)}), 500


@app.route('/api/files/<file_id>/validation', methods=['GET'])
def api_file_validation(file_id):
    """
    API endpoint to get validation results for a file

    Returns: JSON with validation snapshot and all errors/warnings
    """
    try:
        # Query for ValidationSnapshot (most recent)
        snapshot_response = table.query(
            KeyConditionExpression=Key('PK').eq(f'FILE#{file_id}') & Key('SK').begins_with('VALIDATION#'),
            ScanIndexForward=False,  # Get most recent first
            Limit=1
        )

        # Query validation errors for detailed info
        errors_response = table.query(
            KeyConditionExpression=Key('PK').eq(f'FILE#{file_id}') & Key('SK').begins_with('ERROR#')
        )

        # Query validation warnings
        warnings_response = table.query(
            KeyConditionExpression=Key('PK').eq(f'FILE#{file_id}') & Key('SK').begins_with('WARNING#')
        )

        # Get file metadata for status
        file_response = table.get_item(
            Key={'PK': f'FILE#{file_id}', 'SK': 'METADATA'}
        )

        file_status = 'UNKNOWN'
        if 'Item' in file_response:
            file_status = file_response['Item'].get('Status', 'UNKNOWN')

        # Use ValidationSnapshot if available, otherwise build from errors/warnings
        validation_rules = []
        snapshot_data = None

        if snapshot_response.get('Items'):
            snapshot = snapshot_response['Items'][0]
            snapshot_data = {
                'status': snapshot.get('Status'),
                'validated_at': snapshot.get('ValidatedAt'),
                'total_records': snapshot.get('TotalRecords'),
                'valid_records': snapshot.get('ValidRecords'),
                'rejected_records': snapshot.get('RejectedRecords', 0),
                'total_checks': snapshot.get('TotalChecks', 0),
                'passed_checks': snapshot.get('PassedChecks', 0),
                'critical_failures': snapshot.get('CriticalFailures', 0),
                'warnings': snapshot.get('Warnings', 0),
                # Legacy fields for backwards compatibility
                'total_rules': snapshot.get('TotalRules', 0),
                'passed_rules': snapshot.get('PassedRules', 0),
                'failed_rules': snapshot.get('FailedRules', 0),
                'error_count': snapshot.get('ErrorCount', 0),
                'warning_count': snapshot.get('WarningCount', 0)
            }

            # Use new enterprise validation checks if available
            all_validation_checks = snapshot.get('AllValidationChecks', [])

            if all_validation_checks:
                # Return all validation checks directly (enterprise format)
                validation_rules = all_validation_checks
            else:
                # Fallback to old format for backwards compatibility
                validation_results = snapshot.get('ValidationResults', {})

                for error_type, rule_data in validation_results.items():
                    validation_rules.append({
                        'name': error_type.replace('_', ' ').title(),
                        'key': error_type,
                        'passed': rule_data.get('passed', True),
                        'severity': rule_data.get('severity', 'UNKNOWN'),
                        'is_warning': rule_data.get('severity') == 'WARNING',
                        'messages': rule_data.get('messages', []),
                        'affected_count': len(rule_data.get('affected_records', []))
                    })

        else:
            # Fallback: build from individual error/warning records
            rule_map = {}

            for error in errors_response.get('Items', []):
                error_type = error.get('ErrorType', '')
                if error_type not in rule_map:
                    rule_map[error_type] = {
                        'name': error_type.replace('_', ' ').title(),
                        'key': error_type,
                        'passed': False,
                        'severity': error.get('Severity', 'CRITICAL'),
                        'is_warning': False,
                        'messages': [],
                        'errors': []
                    }

                rule_map[error_type]['errors'].append({
                    'row': error.get('RowNumber'),
                    'employee_id': error.get('EmployeeID'),
                    'contractor_name': error.get('ContractorName'),
                    'message': error.get('ErrorMessage')
                })
                if error.get('ErrorMessage'):
                    rule_map[error_type]['messages'].append(error.get('ErrorMessage'))

            for warning in warnings_response.get('Items', []):
                warning_type = warning.get('WarningType', '')
                if warning_type not in rule_map:
                    rule_map[warning_type] = {
                        'name': warning_type.replace('_', ' ').title(),
                        'key': warning_type,
                        'passed': True,
                        'severity': 'WARNING',
                        'is_warning': True,
                        'messages': [],
                        'errors': []
                    }

                rule_map[warning_type]['errors'].append({
                    'row': warning.get('RowNumber'),
                    'message': warning.get('WarningMessage'),
                    'auto_resolved': warning.get('AutoResolved', False)
                })
                if warning.get('WarningMessage'):
                    rule_map[warning_type]['messages'].append(warning.get('WarningMessage'))

            validation_rules = list(rule_map.values())

        return jsonify({
            'file_id': file_id,
            'file_status': file_status,
            'snapshot': snapshot_data,
            'has_errors': len(errors_response.get('Items', [])) > 0,
            'has_warnings': len(warnings_response.get('Items', [])) > 0,
            'total_errors': len(errors_response.get('Items', [])),
            'total_warnings': len(warnings_response.get('Items', [])),
            'validation_rules': validation_rules
        })

    except Exception as e:
        app.logger.error(f"Error fetching validation data for file {file_id}: {str(e)}")
        return jsonify({'error': 'Failed to fetch validation data', 'message': str(e)}), 500


@app.route('/api/contractors', methods=['GET'])
def api_contractors():
    """
    API endpoint to list contractors

    Returns: JSON with contractors list
    """
    try:
        # Query DynamoDB for all Contractor records (METADATA only, not PROFILE or SNAPSHOT)
        response = table.scan(
            FilterExpression='EntityType = :et AND SK = :sk',
            ExpressionAttributeValues={
                ':et': 'Contractor',
                ':sk': 'METADATA'
            }
        )

        contractors_list = []
        for item in response.get('Items', []):
            # Skip permanent staff - only display contractors
            if item.get('IsPermanentStaff', False):
                continue

            sell_rate = float(item.get('SellRate', 0))
            buy_rate = float(item.get('BuyRate', 0))

            # Get margin from DB if available, otherwise calculate
            margin = item.get('Margin')
            margin_percent = item.get('MarginPercent')

            if margin is None or margin_percent is None:
                # Calculate margin if not in database
                if sell_rate > 0 and sell_rate > buy_rate:
                    margin = sell_rate - buy_rate
                    margin_percent = ((sell_rate - buy_rate) / sell_rate) * 100
                else:
                    margin = 0
                    margin_percent = 0
            else:
                margin = float(margin)
                margin_percent = float(margin_percent)

            # Use Email or ResourceContactEmail (backward compatibility)
            email = item.get('Email') or item.get('ResourceContactEmail', '')

            contractor_data = {
                'contractor_id': item.get('ContractorID'),
                'email': email,
                'first_name': item.get('FirstName', ''),
                'last_name': item.get('LastName', ''),
                'full_name': f"{item.get('FirstName', '')} {item.get('LastName', '')}".strip(),
                'job_title': item.get('JobTitle', 'N/A'),
                'sell_rate': sell_rate,
                'buy_rate': buy_rate,
                'margin': margin,
                'margin_percent': margin_percent,
                'is_active': item.get('IsActive', item.get('Status', 'ACTIVE') == 'ACTIVE'),
                'created_at': item.get('CreatedAt', item.get('UpdatedAt', ''))
            }
            contractors_list.append(contractor_data)

        # Sort by last name
        contractors_list.sort(key=lambda x: x.get('last_name', ''))

        return jsonify({'contractors': contractors_list})

    except Exception as e:
        app.logger.error(f"Error fetching contractors: {str(e)}")
        return jsonify({'error': 'Failed to fetch contractors', 'message': str(e)}), 500


@app.route('/api/perm-staff', methods=['GET'])
def api_perm_staff():
    """
    API endpoint to list permanent staff

    Returns: JSON with permanent staff list
    """
    try:
        # Query DynamoDB for all Contractor records with IsPermanentStaff=True
        response = table.scan(
            FilterExpression='EntityType = :et AND SK = :sk AND IsPermanentStaff = :ps',
            ExpressionAttributeValues={
                ':et': 'Contractor',
                ':sk': 'METADATA',
                ':ps': True
            }
        )

        staff_list = []
        for item in response.get('Items', []):
            sell_rate = float(item.get('SellRate', 0))

            # Use Email or ResourceContactEmail (backward compatibility)
            email = item.get('Email') or item.get('ResourceContactEmail', '')

            staff_data = {
                'staff_id': item.get('ContractorID'),
                'email': email,
                'first_name': item.get('FirstName', ''),
                'last_name': item.get('LastName', ''),
                'full_name': f"{item.get('FirstName', '')} {item.get('LastName', '')}".strip(),
                'job_title': item.get('JobTitle', 'N/A'),
                'customer': item.get('Customer', ''),
                'engagement_type': item.get('EngagementType', 'PAYE'),
                'sell_rate': sell_rate,
                'is_active': item.get('IsActive', item.get('Status', 'ACTIVE') == 'ACTIVE'),
                'created_at': item.get('CreatedAt', item.get('UpdatedAt', ''))
            }
            staff_list.append(staff_data)

        # Sort by last name
        staff_list.sort(key=lambda x: x.get('last_name', ''))

        return jsonify({'staff': staff_list})

    except Exception as e:
        app.logger.error(f"Error fetching permanent staff: {str(e)}")
        return jsonify({'error': 'Failed to fetch permanent staff', 'message': str(e)}), 500


@app.route('/api/perm-staff/<email>', methods=['POST'])
def update_perm_staff(email):
    """
    API endpoint to update permanent staff member

    Returns: JSON with success status
    """
    try:
        data = request.get_json()

        # Build update expression
        update_expr = []
        expr_values = {}
        expr_names = {}

        # Map frontend fields to DynamoDB fields
        field_mapping = {
            'first_name': 'FirstName',
            'last_name': 'LastName',
            'job_title': 'JobTitle',
            'customer': 'Customer',
            'sell_rate': 'SellRate',
            'is_active': 'IsActive'
        }

        for frontend_field, dynamo_field in field_mapping.items():
            if frontend_field in data:
                value = data[frontend_field]

                # Convert sell_rate to Decimal
                if frontend_field == 'sell_rate':
                    value = Decimal(str(value))

                update_expr.append(f'#{dynamo_field} = :{dynamo_field}')
                expr_names[f'#{dynamo_field}'] = dynamo_field
                expr_values[f':{dynamo_field}'] = value

        # Always update UpdatedAt timestamp
        update_expr.append('#UpdatedAt = :UpdatedAt')
        expr_names['#UpdatedAt'] = 'UpdatedAt'
        expr_values[':UpdatedAt'] = datetime.now().isoformat() + 'Z'

        # Update full name if first/last name changed
        if 'first_name' in data or 'last_name' in data:
            first_name = data.get('first_name', '')
            last_name = data.get('last_name', '')
            update_expr.append('#NormalizedName = :NormalizedName')
            expr_names['#NormalizedName'] = 'NormalizedName'
            expr_values[':NormalizedName'] = f"{first_name} {last_name}".lower()

        # Update status based on is_active
        if 'is_active' in data:
            status = 'Active' if data['is_active'] else 'Inactive'
            update_expr.append('#Status = :Status')
            expr_names['#Status'] = 'Status'
            expr_values[':Status'] = status

        # Perform update
        table.update_item(
            Key={
                'PK': f'CONTRACTOR#{email}',
                'SK': 'METADATA'
            },
            UpdateExpression='SET ' + ', '.join(update_expr),
            ExpressionAttributeNames=expr_names,
            ExpressionAttributeValues=expr_values
        )

        return jsonify({'success': True, 'message': 'Permanent staff member updated successfully'})

    except Exception as e:
        app.logger.error(f"Error updating permanent staff {email}: {str(e)}")
        return jsonify({'success': False, 'error': 'Failed to update permanent staff', 'message': str(e)}), 500


@app.route('/api/umbrella-stats', methods=['GET'])
def api_umbrella_stats():
    """
    API endpoint to get umbrella company statistics

    Returns: JSON with umbrella companies, contractor counts, and monthly payments
    """
    try:
        from collections import defaultdict
        from datetime import datetime

        # Get all umbrella companies
        umbrellas_response = table.scan(
            FilterExpression='EntityType = :et',
            ExpressionAttributeValues={':et': 'Umbrella'}
        )

        umbrellas = {}
        for item in umbrellas_response.get('Items', []):
            umbrella_code = item.get('UmbrellaCode', item.get('ShortCode'))
            if umbrella_code:
                umbrellas[umbrella_code] = {
                    'code': umbrella_code,
                    'name': item.get('CompanyName', umbrella_code),
                    'umbrella_id': item.get('UmbrellaID')
                }

        # Get all PayRecords
        payrecords_response = table.scan(
            FilterExpression='EntityType = :et',
            ExpressionAttributeValues={':et': 'PayRecord'}
        )

        # Get all Periods for month mapping
        periods_response = table.scan(
            FilterExpression='EntityType = :et',
            ExpressionAttributeValues={':et': 'Period'}
        )

        # Create period to month mapping
        period_to_month = {}
        for period in periods_response.get('Items', []):
            period_id = period.get('PeriodNumber', period.get('PeriodID'))
            if period_id and period.get('WorkStartDate'):
                try:
                    start_date = datetime.fromisoformat(period['WorkStartDate'])
                    month_abbr = start_date.strftime('%b')  # Feb, Mar, Apr, etc.
                    period_to_month[str(period_id)] = month_abbr
                except:
                    period_to_month[str(period_id)] = f'P{period_id}'

        # Aggregate data by umbrella and month
        umbrella_stats = defaultdict(lambda: {
            'code': '',
            'name': '',
            'contractors': set(),
            'monthly_totals': defaultdict(Decimal),
            'total_paid': Decimal('0')
        })

        for record in payrecords_response.get('Items', []):
            umbrella_code = record.get('UmbrellaCode')
            if not umbrella_code:
                continue

            contractor_id = record.get('ContractorID')
            period_id = str(record.get('PeriodID', ''))
            # Use 'Amount' field (actual field name in DynamoDB PayRecords)
            total_pay = Decimal(str(record.get('Amount', 0)))

            # Get month from period
            month = period_to_month.get(period_id, f'P{period_id}')

            # Update stats
            if umbrella_code in umbrellas:
                umbrella_stats[umbrella_code]['code'] = umbrella_code
                umbrella_stats[umbrella_code]['name'] = umbrellas[umbrella_code]['name']
            else:
                umbrella_stats[umbrella_code]['code'] = umbrella_code
                umbrella_stats[umbrella_code]['name'] = umbrella_code

            if contractor_id:
                umbrella_stats[umbrella_code]['contractors'].add(contractor_id)

            umbrella_stats[umbrella_code]['monthly_totals'][month] += total_pay
            umbrella_stats[umbrella_code]['total_paid'] += total_pay

        # Convert to list and format
        result = []
        for umbrella_code, stats in umbrella_stats.items():
            # Convert monthly totals to sorted list
            monthly_data = {}
            for month, amount in stats['monthly_totals'].items():
                monthly_data[month] = float(amount)

            result.append({
                'code': stats['code'],
                'name': stats['name'],
                'contractor_count': len(stats['contractors']),
                'monthly_totals': monthly_data,
                'total_paid': float(stats['total_paid'])
            })

        # Sort by umbrella code
        result.sort(key=lambda x: x['code'])

        # Calculate summary stats
        all_contractors = set()
        for stats in umbrella_stats.values():
            all_contractors.update(stats['contractors'])

        # Count unique files (FileMetadata entities)
        files_response = table.scan(
            FilterExpression='EntityType = :et',
            ExpressionAttributeValues={':et': 'FileMetadata'}
        )
        total_files = len(files_response.get('Items', []))

        unique_months = sorted(set(period_to_month.values()))

        return jsonify({
            'umbrellas': result,
            'months': unique_months,
            'summary': {
                'total_files': total_files,
                'total_umbrellas': len(result),
                'total_contractors': len(all_contractors),
                'total_months': len(unique_months)
            }
        })

    except Exception as e:
        app.logger.error(f"Error fetching umbrella stats: {str(e)}")
        import traceback
        app.logger.error(traceback.format_exc())
        return jsonify({'error': 'Failed to fetch umbrella statistics', 'message': str(e)}), 500


@app.route('/api/contractors/<email>', methods=['POST'])
def api_update_contractor(email):
    """
    API endpoint to update contractor with full audit trail

    Expects: JSON with contractor fields
    Returns: JSON with success status and snapshot info
    """
    try:
        # Get current contractor data for snapshot
        current_response = table.get_item(
            Key={
                'PK': f'CONTRACTOR#{email}',
                'SK': 'METADATA'
            }
        )

        if 'Item' not in current_response:
            return jsonify({'error': 'Contractor not found'}), 404

        current_contractor = current_response['Item']

        # Get update data from request
        update_data = request.json
        app.logger.info(f"Received update data: {update_data}")

        # Validate margin if rates are being changed
        sell_rate = update_data.get('sell_rate')
        buy_rate = update_data.get('buy_rate')

        if sell_rate is not None and buy_rate is not None:
            try:
                # Validate and calculate margin
                margin, margin_percent = calculate_margin(sell_rate, buy_rate)
                # Add margin fields to update_data
                update_data['margin'] = float(margin)
                update_data['margin_percent'] = float(margin_percent)
            except ValueError as e:
                return jsonify({'error': str(e)}), 400

        # Track what changed
        changes = {}
        field_mapping = {
            'title': 'Title',
            'first_name': 'FirstName',
            'last_name': 'LastName',
            'job_title': 'JobTitle',
            'resource_email': 'ResourceEmail',
            'nasstar_email': 'NasstarEmail',
            'line_manager_email': 'LineManagerEmail',
            'sell_rate': 'SellRate',
            'buy_rate': 'BuyRate',
            'margin': 'Margin',
            'margin_percent': 'MarginPercent',
            'snow_unit_rate': 'SNOWUnitRate',
            'engagement_type': 'EngagementType',
            'customer': 'Customer',
            'snow_product': 'SNOWProduct',
            'is_active': 'IsActive'
        }

        for api_field, db_field in field_mapping.items():
            if api_field in update_data:
                new_value = update_data[api_field]
                old_value = current_contractor.get(db_field)

                # Handle None values
                if new_value != old_value:
                    changes[db_field] = {
                        'old': old_value,
                        'new': new_value
                    }

        # Only proceed if there are changes
        if not changes:
            return jsonify({
                'message': 'No changes detected',
                'snapshot_created': False
            })

        # Create snapshot with timestamp
        snapshot_timestamp = datetime.utcnow().isoformat() + 'Z'
        snapshot_sk = f"SNAPSHOT#{snapshot_timestamp}"

        # Prepare snapshot item (copy of current state before changes)
        snapshot_item = dict(current_contractor)
        snapshot_item['SK'] = snapshot_sk
        snapshot_item['EntityType'] = 'ContractorSnapshot'
        snapshot_item['SnapshotTimestamp'] = snapshot_timestamp

        # Convert changes dict to be DynamoDB compatible
        changes_serialized = {}
        for field, change_info in changes.items():
            old_val = change_info['old']
            new_val = change_info['new']

            # Convert values to DynamoDB-safe format
            if isinstance(old_val, (Decimal, int, float)):
                old_val = Decimal(str(old_val))
            elif old_val is None:
                old_val = 'null'

            if isinstance(new_val, (Decimal, int, float)):
                new_val = Decimal(str(new_val))
            elif new_val is None:
                new_val = 'null'

            changes_serialized[field] = {
                'old': old_val,
                'new': new_val
            }

        snapshot_item['Changes'] = changes_serialized
        snapshot_item['ChangeReason'] = 'Manual edit via Flask web interface'
        snapshot_item['ChangedBy'] = 'flask-web-user'  # Could be enhanced with actual user tracking

        # Update the main contractor record
        update_expression_parts = []
        expression_attribute_values = {}
        expression_attribute_names = {}

        for api_field, db_field in field_mapping.items():
            if api_field in update_data:
                value = update_data[api_field]

                # Skip empty values - don't update them
                if value == '' or value is None:
                    continue

                attr_name = f'#{db_field}'
                attr_value = f':{api_field}'
                update_expression_parts.append(f'{attr_name} = {attr_value}')
                expression_attribute_names[attr_name] = db_field

                # Convert float/int to Decimal for numeric fields (but not booleans!)
                if isinstance(value, (int, float)) and value is not None and not isinstance(value, bool):
                    try:
                        value = Decimal(str(value))
                    except Exception as e:
                        app.logger.error(f"Error converting {api_field}={value} (type={type(value)}) to Decimal: {e}")
                        raise

                expression_attribute_values[attr_value] = value

        # Add UpdatedAt timestamp
        update_expression_parts.append('#UpdatedAt = :updated_at')
        expression_attribute_names['#UpdatedAt'] = 'UpdatedAt'
        expression_attribute_values[':updated_at'] = snapshot_timestamp

        # Convert snapshot_item numeric values to Decimal for DynamoDB (but not booleans!)
        for key, value in snapshot_item.items():
            if isinstance(value, (int, float)) and not isinstance(value, bool):
                snapshot_item[key] = Decimal(str(value))

        # Also update RatesUpdatedAt if rates changed
        if 'SellRate' in changes or 'BuyRate' in changes or 'SNOWUnitRate' in changes:
            update_expression_parts.append('#RatesUpdatedAt = :rates_updated_at')
            expression_attribute_names['#RatesUpdatedAt'] = 'RatesUpdatedAt'
            expression_attribute_values[':rates_updated_at'] = snapshot_timestamp

        # Update NormalizedName if name changed
        if 'FirstName' in changes or 'LastName' in changes:
            normalized_name = f"{update_data.get('first_name', '')} {update_data.get('last_name', '')}".strip().lower()
            update_expression_parts.append('#NormalizedName = :normalized_name')
            expression_attribute_names['#NormalizedName'] = 'NormalizedName'
            expression_attribute_values[':normalized_name'] = normalized_name

        update_expression = 'SET ' + ', '.join(update_expression_parts)

        # Perform DynamoDB updates in a transaction-like manner
        # 1. Put the snapshot
        table.put_item(Item=snapshot_item)

        # 2. Update the main record
        table.update_item(
            Key={
                'PK': f'CONTRACTOR#{email}',
                'SK': 'METADATA'
            },
            UpdateExpression=update_expression,
            ExpressionAttributeNames=expression_attribute_names,
            ExpressionAttributeValues=expression_attribute_values
        )

        # 3. Update GSI2 if name changed
        if 'FirstName' in changes or 'LastName' in changes:
            normalized_name = f"{update_data.get('first_name', '')} {update_data.get('last_name', '')}".strip().lower()
            table.update_item(
                Key={
                    'PK': f'CONTRACTOR#{email}',
                    'SK': 'METADATA'
                },
                UpdateExpression='SET #GSI2PK = :gsi2pk',
                ExpressionAttributeNames={'#GSI2PK': 'GSI2PK'},
                ExpressionAttributeValues={':gsi2pk': f'NAME#{normalized_name}'}
            )

        app.logger.info(f"Contractor {email} updated successfully. Snapshot created: {snapshot_sk}")

        return jsonify({
            'message': 'Contractor updated successfully',
            'snapshot_created': True,
            'snapshot_timestamp': snapshot_timestamp,
            'changes': changes,
            'snapshot_id': snapshot_sk
        })

    except ClientError as e:
        app.logger.error(f"DynamoDB error updating contractor: {str(e)}")
        return jsonify({'error': 'Database error', 'message': str(e)}), 500
    except Exception as e:
        import traceback
        app.logger.error(f"Error updating contractor: {str(e)}")
        app.logger.error(traceback.format_exc())
        return jsonify({'error': 'Failed to update contractor', 'message': str(e), 'traceback': traceback.format_exc()}), 500


@app.route('/api/files/<file_id>/download', methods=['GET'])
def api_download_file(file_id):
    """
    API endpoint to download Excel file from S3

    Returns: Excel file as binary stream or error JSON
    """
    try:
        # Get file metadata from DynamoDB
        response = table.get_item(
            Key={
                'PK': f'FILE#{file_id}',
                'SK': 'METADATA'
            }
        )

        if 'Item' not in response:
            return jsonify({'error': 'File not found'}), 404

        file_item = response['Item']
        s3_key = file_item.get('S3Key')
        original_filename = file_item.get('OriginalFilename', 'file.xlsx')

        if not s3_key:
            return jsonify({'error': 'S3 key not found for file'}), 404

        # Download file from S3
        try:
            s3_response = s3_client.get_object(Bucket=S3_BUCKET, Key=s3_key)
            file_content = s3_response['Body'].read()

            # Return file as binary response
            from flask import make_response
            response = make_response(file_content)
            response.headers['Content-Type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            response.headers['Content-Disposition'] = f'attachment; filename="{original_filename}"'
            return response

        except ClientError as e:
            app.logger.error(f"S3 error downloading file: {str(e)}")
            return jsonify({'error': 'Failed to download file from S3', 'message': str(e)}), 500

    except Exception as e:
        app.logger.error(f"Error downloading file {file_id}: {str(e)}")
        return jsonify({'error': 'Failed to download file', 'message': str(e)}), 500


@app.route('/api/debug/files', methods=['GET'])
def api_debug_files():
    """
    API endpoint to get list of files for debugging interface

    Returns: JSON with files metadata including navigation info
    """
    try:
        # Query DynamoDB for all File records
        response = table.scan(
            FilterExpression='EntityType = :et',
            ExpressionAttributeValues={':et': 'File'}
        )

        files_list = []
        for item in response.get('Items', []):
            # Convert Decimal to int/float for JSON serialization
            from decimal import Decimal

            def convert_decimal(value):
                if isinstance(value, Decimal):
                    return int(value) if value % 1 == 0 else float(value)
                return value

            file_data = {
                'file_id': item.get('FileID'),
                'filename': item.get('OriginalFilename', 'Unknown'),
                'umbrella': item.get('UmbrellaCode', 'Unknown'),
                'status': item.get('Status', 'UNKNOWN'),
                'uploaded_at': item.get('UploadedAt', item.get('CreatedAt', '')),
                's3_key': item.get('S3Key', ''),
                'file_size': convert_decimal(item.get('FileSizeBytes', 0)),
                'total_records': convert_decimal(item.get('TotalRecords', 0)),
                'valid_records': convert_decimal(item.get('ValidRecords', 0)),
                'error_records': convert_decimal(item.get('ErrorRecords', 0)),
                'error_count': convert_decimal(item.get('ErrorCount', 0)),
                'warning_count': convert_decimal(item.get('WarningCount', 0)),
                'period_id': item.get('PeriodID', 'Unknown'),
                'error_message': item.get('ErrorMessage', '')
            }
            files_list.append(file_data)

        # Sort by upload date (newest first)
        files_list.sort(key=lambda x: x.get('uploaded_at', ''), reverse=True)

        return jsonify({'files': files_list})

    except Exception as e:
        app.logger.error(f"Error fetching debug files: {str(e)}")
        return jsonify({'error': 'Failed to fetch files', 'message': str(e)}), 500


@app.route('/api/files/<file_id>/records', methods=['GET'])
def api_file_records(file_id):
    """
    API endpoint to get PayRecords for a specific file

    Returns: JSON with PayRecords from DynamoDB
    """
    try:
        # Query PayRecords for this file
        response = table.query(
            KeyConditionExpression=Key('PK').eq(f'FILE#{file_id}') & Key('SK').begins_with('RECORD#')
        )

        records = []
        for item in response.get('Items', []):
            # Convert Decimal to float for JSON serialization
            record_data = {}
            for key, value in item.items():
                if isinstance(value, Decimal):
                    record_data[key] = float(value)
                else:
                    record_data[key] = value
            records.append(record_data)

        return jsonify({'records': records, 'count': len(records)})

    except Exception as e:
        app.logger.error(f"Error fetching records for file {file_id}: {str(e)}")
        return jsonify({'error': 'Failed to fetch records', 'message': str(e)}), 500


@app.errorhandler(404)
def not_found(error):
    """404 error handler"""
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_error(error):
    """500 error handler"""
    return render_template('500.html'), 500


@app.context_processor
def inject_globals():
    """Inject global variables into templates"""
    return {
        'app_name': 'Contractor Pay Tracker',
        'current_year': datetime.now().year
    }


if __name__ == '__main__':
    # Use environment variable for port, or find available port
    # This ensures consistent port across Flask reloader restarts
    if 'FLASK_RUN_PORT' not in os.environ:
        port = find_available_port(start_port=5555)
        os.environ['FLASK_RUN_PORT'] = str(port)
    else:
        port = int(os.environ['FLASK_RUN_PORT'])

    # Only print banner and open browser once (not on reloader restart)
    if os.environ.get('WERKZEUG_RUN_MAIN') != 'true':
        print("\n" + "="*60)
        print("🚀 Contractor Pay Tracker - Flask App")
        print("="*60)
        print(f"\n✅ Server starting on http://127.0.0.1:{port}")
        print(f"✅ Local access: http://localhost:{port}")
        print(f"\n📁 Upload files: http://localhost:{port}/upload")
        print(f"📊 View files: http://localhost:{port}/files")
        print(f"\n⚠️  Press CTRL+C to stop the server")
        print("="*60 + "\n")

        # Open browser after server starts
        def open_browser():
            import time
            time.sleep(2)  # Wait for server to start
            webbrowser.open(f'http://localhost:{port}')

        threading.Thread(target=open_browser, daemon=True).start()

    app.run(
        host='127.0.0.1',
        port=port,
        debug=True,
        use_reloader=True
    )
