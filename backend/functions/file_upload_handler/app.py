"""
File Upload Handler Lambda Function
Handles file uploads to S3 and triggers processing workflow

Supports both:
1. Direct file upload via API Gateway (base64 encoded)
2. S3 event trigger after file uploaded
"""

import base64
import hashlib
import json
import os
import uuid
from datetime import datetime

import boto3

# Import from common layer
from common.logger import StructuredLogger
from common.dynamodb import DynamoDBClient


s3_client = boto3.client('s3')
sfn_client = boto3.client('stepfunctions')
dynamodb_client = DynamoDBClient()

S3_BUCKET = os.environ.get('S3_BUCKET_NAME')
STATE_MACHINE_ARN = os.environ.get('STATE_MACHINE_ARN', '')


def lambda_handler(event, context):
    """Main Lambda handler"""

    logger = StructuredLogger("file-upload-handler", context.request_id)
    logger.info("File upload handler invoked")

    try:
        # Check if this is an S3 event or API Gateway event
        if 'Records' in event:
            # S3 event trigger
            return handle_s3_event(event, logger)
        else:
            # API Gateway upload
            return handle_api_upload(event, logger)

    except Exception as e:
        logger.error("File upload error", error=str(e))
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'error': str(e)})
        }


def handle_api_upload(event, logger: StructuredLogger):
    """
    Handle file upload via API Gateway
    Expects multipart/form-data with base64 encoded file
    """
    logger.info("Handling API upload")

    # Parse request
    if event.get('isBase64Encoded'):
        body = base64.b64decode(event['body'])
    else:
        body = event.get('body', '')

    # For now, handle JSON upload (Phase 4 will add multipart)
    if isinstance(body, bytes):
        body = body.decode('utf-8')

    try:
        request_data = json.loads(body) if body else {}
    except json.JSONDecodeError:
        # Might be multipart form data - simplified for Phase 3
        request_data = {}

    # Extract file data
    # In production, parse multipart form data properly
    filename = request_data.get('filename', 'upload.xlsx')
    file_content = request_data.get('file_content_base64', '')
    uploaded_by = request_data.get('uploaded_by', 'unknown')
    notes = request_data.get('notes', '')

    if not file_content:
        return {
            'statusCode': 400,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'error': 'No file content provided'})
        }

    # Decode file content
    file_bytes = base64.b64decode(file_content)

    # Generate file ID and S3 key
    file_id = str(uuid.uuid4())
    timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
    s3_key = f"uploads/{datetime.utcnow().year}/{datetime.utcnow().month:02d}/{timestamp}_{file_id}.xlsx"

    # Calculate file hash
    file_hash = hashlib.sha256(file_bytes).hexdigest()

    # Upload to S3
    s3_client.put_object(
        Bucket=S3_BUCKET,
        Key=s3_key,
        Body=file_bytes,
        ContentType='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        Metadata={
            'original-filename': filename,
            'uploaded-by': uploaded_by,
            'file-id': file_id
        }
    )

    logger.info("File uploaded to S3", file_id=file_id, s3_key=s3_key, size=len(file_bytes))

    # Create metadata in DynamoDB
    file_metadata = {
        'PK': f'FILE#{file_id}',
        'SK': 'METADATA',
        'EntityType': 'File',
        'FileID': file_id,
        'OriginalFilename': filename,
        'S3Bucket': S3_BUCKET,
        'S3Key': s3_key,
        'S3VersionID': '',  # Would be populated if versioning enabled
        'FileSizeBytes': len(file_bytes),
        'FileHashSHA256': file_hash,
        'Status': 'UPLOADED',
        'UploadedAt': datetime.utcnow().isoformat() + 'Z',
        'UploadedBy': uploaded_by,
        'Notes': notes,
        'IsCurrentVersion': True,
        'Version': 1,
        'GSI3PK': 'FILES',
        'GSI3SK': datetime.utcnow().isoformat() + 'Z'
    }

    dynamodb_client.table.put_item(Item=file_metadata)

    logger.info("File metadata created", file_id=file_id)

    # Trigger Step Functions workflow
    if STATE_MACHINE_ARN:
        try:
            execution_response = sfn_client.start_execution(
                stateMachineArn=STATE_MACHINE_ARN,
                name=f'process-{file_id}',
                input=json.dumps({
                    'file_id': file_id,
                    's3_bucket': S3_BUCKET,
                    's3_key': s3_key
                })
            )

            logger.info("Step Functions execution started",
                       execution_arn=execution_response['executionArn'])

            execution_arn = execution_response['executionArn']
        except Exception as e:
            logger.error("Failed to start Step Functions", error=str(e))
            execution_arn = None
    else:
        logger.warning("STATE_MACHINE_ARN not set, skipping workflow trigger")
        execution_arn = None

    # Return success response
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
        'body': json.dumps({
            'message': 'File uploaded successfully',
            'file_id': file_id,
            's3_bucket': S3_BUCKET,
            's3_key': s3_key,
            'file_size': len(file_bytes),
            'file_hash': file_hash,
            'status': 'UPLOADED',
            'execution_arn': execution_arn,
            'uploaded_at': file_metadata['UploadedAt']
        })
    }


def handle_s3_event(event, logger: StructuredLogger):
    """
    Handle S3 event trigger
    Called when file is uploaded directly to S3
    """
    logger.info("Handling S3 event", event=event)

    responses = []

    for record in event.get('Records', []):
        if record.get('eventName', '').startswith('ObjectCreated'):
            s3_bucket = record['s3']['bucket']['name']
            s3_key = record['s3']['object']['key']
            file_size = record['s3']['object']['size']

            logger.info("Processing S3 object", bucket=s3_bucket, key=s3_key, size=file_size)

            # Generate file ID
            file_id = str(uuid.uuid4())

            # Get object metadata
            try:
                head_response = s3_client.head_object(Bucket=s3_bucket, Key=s3_key)
                metadata = head_response.get('Metadata', {})
                uploaded_by = metadata.get('uploaded-by', 'direct-s3-upload')
                original_filename = metadata.get('original-filename', s3_key.split('/')[-1])
                version_id = head_response.get('VersionId', '')
            except Exception as e:
                logger.error("Failed to get object metadata", error=str(e))
                uploaded_by = 'direct-s3-upload'
                original_filename = s3_key.split('/')[-1]
                version_id = ''

            # Calculate file hash
            try:
                obj_response = s3_client.get_object(Bucket=s3_bucket, Key=s3_key)
                file_content = obj_response['Body'].read()
                file_hash = hashlib.sha256(file_content).hexdigest()
            except Exception as e:
                logger.error("Failed to read object for hash", error=str(e))
                file_hash = ''

            # Create metadata in DynamoDB
            file_metadata = {
                'PK': f'FILE#{file_id}',
                'SK': 'METADATA',
                'EntityType': 'File',
                'FileID': file_id,
                'OriginalFilename': original_filename,
                'S3Bucket': s3_bucket,
                'S3Key': s3_key,
                'S3VersionID': version_id,
                'FileSizeBytes': file_size,
                'FileHashSHA256': file_hash,
                'Status': 'UPLOADED',
                'UploadedAt': datetime.utcnow().isoformat() + 'Z',
                'UploadedBy': uploaded_by,
                'IsCurrentVersion': True,
                'Version': 1,
                'GSI3PK': 'FILES',
                'GSI3SK': datetime.utcnow().isoformat() + 'Z'
            }

            dynamodb_client.table.put_item(Item=file_metadata)

            logger.info("File metadata created from S3 event", file_id=file_id)

            # Trigger Step Functions workflow
            if STATE_MACHINE_ARN:
                try:
                    execution_response = sfn_client.start_execution(
                        stateMachineArn=STATE_MACHINE_ARN,
                        name=f'process-{file_id}',
                        input=json.dumps({
                            'file_id': file_id,
                            's3_bucket': s3_bucket,
                            's3_key': s3_key
                        })
                    )

                    logger.info("Step Functions execution started",
                               execution_arn=execution_response['executionArn'])

                    responses.append({
                        'file_id': file_id,
                        'status': 'processing_started',
                        'execution_arn': execution_response['executionArn']
                    })
                except Exception as e:
                    logger.error("Failed to start Step Functions", error=str(e))
                    responses.append({
                        'file_id': file_id,
                        'status': 'uploaded',
                        'error': str(e)
                    })
            else:
                logger.warning("STATE_MACHINE_ARN not set")
                responses.append({
                    'file_id': file_id,
                    'status': 'uploaded'
                })

    return {
        'statusCode': 200,
        'body': json.dumps({
            'message': 'S3 events processed',
            'files': responses
        })
    }
