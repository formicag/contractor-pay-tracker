"""
File Upload Handler Lambda Function
Handles file uploads to S3 and triggers processing workflow

Supports both:
1. Direct file upload via API Gateway (base64 encoded)
2. S3 event trigger after file uploaded
"""

print("[FILE_UPLOAD_HANDLER] ========================================")
print("[FILE_UPLOAD_HANDLER] Module loading started")
print("[FILE_UPLOAD_HANDLER] ========================================")

print("[FILE_UPLOAD_HANDLER] Importing base64")
import base64
print(f"[FILE_UPLOAD_HANDLER] base64 imported: {base64}")

print("[FILE_UPLOAD_HANDLER] Importing hashlib")
import hashlib
print(f"[FILE_UPLOAD_HANDLER] hashlib imported: {hashlib}")

print("[FILE_UPLOAD_HANDLER] Importing json")
import json
print(f"[FILE_UPLOAD_HANDLER] json imported: {json}")

print("[FILE_UPLOAD_HANDLER] Importing os")
import os
print(f"[FILE_UPLOAD_HANDLER] os imported: {os}")

print("[FILE_UPLOAD_HANDLER] Importing uuid")
import uuid
print(f"[FILE_UPLOAD_HANDLER] uuid imported: {uuid}")

print("[FILE_UPLOAD_HANDLER] Importing datetime from datetime")
from datetime import datetime
print(f"[FILE_UPLOAD_HANDLER] datetime imported: {datetime}")

print("[FILE_UPLOAD_HANDLER] Importing boto3")
import boto3
print(f"[FILE_UPLOAD_HANDLER] boto3 imported: {boto3}")

print("[FILE_UPLOAD_HANDLER] Importing from common layer")
# Import from common layer
print("[FILE_UPLOAD_HANDLER] Importing StructuredLogger from common.logger")
from common.logger import StructuredLogger
print(f"[FILE_UPLOAD_HANDLER] StructuredLogger imported: {StructuredLogger}")

print("[FILE_UPLOAD_HANDLER] Importing DynamoDBClient from common.dynamodb")
from common.dynamodb import DynamoDBClient
print(f"[FILE_UPLOAD_HANDLER] DynamoDBClient imported: {DynamoDBClient}")

print("[FILE_UPLOAD_HANDLER] Creating boto3 S3 client")
s3_client = boto3.client('s3')
print(f"[FILE_UPLOAD_HANDLER] s3_client created: {s3_client}")

print("[FILE_UPLOAD_HANDLER] Creating boto3 Step Functions client")
sfn_client = boto3.client('stepfunctions')
print(f"[FILE_UPLOAD_HANDLER] sfn_client created: {sfn_client}")

print("[FILE_UPLOAD_HANDLER] Creating DynamoDB client")
dynamodb_client = DynamoDBClient()
print(f"[FILE_UPLOAD_HANDLER] dynamodb_client created: {dynamodb_client}")

print("[FILE_UPLOAD_HANDLER] Reading S3_BUCKET_NAME from environment")
S3_BUCKET = os.environ.get('S3_BUCKET_NAME')
print(f"[FILE_UPLOAD_HANDLER] S3_BUCKET set to: {S3_BUCKET}")

print("[FILE_UPLOAD_HANDLER] Reading STEP_FUNCTION_ARN from environment")
STEP_FUNCTION_ARN = os.environ.get('STEP_FUNCTION_ARN', '')
print(f"[FILE_UPLOAD_HANDLER] STEP_FUNCTION_ARN set to: {STEP_FUNCTION_ARN}")

print("[FILE_UPLOAD_HANDLER] ========================================")
print("[FILE_UPLOAD_HANDLER] Module loading completed")
print("[FILE_UPLOAD_HANDLER] ========================================")


def lambda_handler(event, context):
    """Main Lambda handler"""
    print("[FILE_UPLOAD_HANDLER] ========================================")
    print("[FILE_UPLOAD_HANDLER] lambda_handler() invoked")
    print("[FILE_UPLOAD_HANDLER] ========================================")
    print(f"[FILE_UPLOAD_HANDLER] event parameter: {event}")
    print(f"[FILE_UPLOAD_HANDLER] context parameter: {context}")
    print(f"[FILE_UPLOAD_HANDLER] context.aws_request_id: {context.aws_request_id}")

    print("[FILE_UPLOAD_HANDLER] Creating StructuredLogger")
    logger = StructuredLogger("file-upload-handler", context.aws_request_id)
    print(f"[FILE_UPLOAD_HANDLER] logger created: {logger}")

    print("[FILE_UPLOAD_HANDLER] Logging info message: File upload handler invoked")
    logger.info("File upload handler invoked")
    print("[FILE_UPLOAD_HANDLER] Info message logged")

    try:
        print("[FILE_UPLOAD_HANDLER] Entering try block")

        # Check if this is an S3 event or API Gateway event
        print("[FILE_UPLOAD_HANDLER] Checking if 'Records' in event")
        has_records = 'Records' in event
        print(f"[FILE_UPLOAD_HANDLER] has_records: {has_records}")

        if has_records:
            print("[FILE_UPLOAD_HANDLER] Event type: S3 event trigger")
            # S3 event trigger
            print("[FILE_UPLOAD_HANDLER] Calling handle_s3_event()")
            result = handle_s3_event(event, logger)
            print(f"[FILE_UPLOAD_HANDLER] handle_s3_event() returned: {result}")
            print("[FILE_UPLOAD_HANDLER] lambda_handler() returning result from S3 handler")
            return result
        else:
            print("[FILE_UPLOAD_HANDLER] Event type: API Gateway upload")
            # API Gateway upload
            print("[FILE_UPLOAD_HANDLER] Calling handle_api_upload()")
            result = handle_api_upload(event, logger)
            print(f"[FILE_UPLOAD_HANDLER] handle_api_upload() returned: {result}")
            print("[FILE_UPLOAD_HANDLER] lambda_handler() returning result from API handler")
            return result

    except Exception as e:
        print("[FILE_UPLOAD_HANDLER] !!! EXCEPTION CAUGHT !!!")
        print(f"[FILE_UPLOAD_HANDLER] Exception type: {type(e)}")
        print(f"[FILE_UPLOAD_HANDLER] Exception message: {str(e)}")
        print(f"[FILE_UPLOAD_HANDLER] Exception args: {e.args}")

        print("[FILE_UPLOAD_HANDLER] Logging error via logger")
        logger.error("File upload error", error=str(e))
        print("[FILE_UPLOAD_HANDLER] Error logged")

        print("[FILE_UPLOAD_HANDLER] Building error response")
        error_response = {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'error': str(e)})
        }
        print(f"[FILE_UPLOAD_HANDLER] error_response: {error_response}")
        print("[FILE_UPLOAD_HANDLER] lambda_handler() returning error response")
        return error_response


def handle_api_upload(event, logger: StructuredLogger):
    """
    Handle file upload via API Gateway
    Expects multipart/form-data with base64 encoded file
    """
    print("[FILE_UPLOAD_HANDLER] ========================================")
    print("[FILE_UPLOAD_HANDLER] handle_api_upload() started")
    print("[FILE_UPLOAD_HANDLER] ========================================")
    print(f"[FILE_UPLOAD_HANDLER] event: {event}")
    print(f"[FILE_UPLOAD_HANDLER] logger: {logger}")

    print("[FILE_UPLOAD_HANDLER] Logging info: Handling API upload")
    logger.info("Handling API upload")
    print("[FILE_UPLOAD_HANDLER] Info logged")

    # Parse request
    print("[FILE_UPLOAD_HANDLER] Parsing request")
    print("[FILE_UPLOAD_HANDLER] Checking if event.get('isBase64Encoded')")
    is_base64_encoded = event.get('isBase64Encoded')
    print(f"[FILE_UPLOAD_HANDLER] is_base64_encoded: {is_base64_encoded}")

    if is_base64_encoded:
        print("[FILE_UPLOAD_HANDLER] Event is base64 encoded, decoding body")
        print(f"[FILE_UPLOAD_HANDLER] event['body'] before decode: {event['body'][:100]}...")
        body = base64.b64decode(event['body'])
        print(f"[FILE_UPLOAD_HANDLER] body after decode: {body[:100]}...")
    else:
        print("[FILE_UPLOAD_HANDLER] Event is not base64 encoded, getting body directly")
        body = event.get('body', '')
        print(f"[FILE_UPLOAD_HANDLER] body: {body[:100] if body else ''}")

    # For now, handle JSON upload (Phase 4 will add multipart)
    print("[FILE_UPLOAD_HANDLER] Checking if body is bytes")
    is_bytes = isinstance(body, bytes)
    print(f"[FILE_UPLOAD_HANDLER] is_bytes: {is_bytes}")

    if is_bytes:
        print("[FILE_UPLOAD_HANDLER] Body is bytes, decoding to utf-8")
        body = body.decode('utf-8')
        print(f"[FILE_UPLOAD_HANDLER] body decoded to string: {body[:100] if body else ''}")

    try:
        print("[FILE_UPLOAD_HANDLER] Attempting to parse body as JSON")
        print(f"[FILE_UPLOAD_HANDLER] body value: {body[:100] if body else ''}")
        request_data = json.loads(body) if body else {}
        print(f"[FILE_UPLOAD_HANDLER] request_data parsed: {request_data}")
    except json.JSONDecodeError as jde:
        print("[FILE_UPLOAD_HANDLER] JSON decode error caught")
        print(f"[FILE_UPLOAD_HANDLER] JSONDecodeError: {jde}")
        # Might be multipart form data - simplified for Phase 3
        print("[FILE_UPLOAD_HANDLER] Setting request_data to empty dict (multipart not supported yet)")
        request_data = {}
        print(f"[FILE_UPLOAD_HANDLER] request_data: {request_data}")

    # Extract file data
    print("[FILE_UPLOAD_HANDLER] Extracting file data from request")

    print("[FILE_UPLOAD_HANDLER] Getting 'filename' from request_data")
    filename = request_data.get('filename', 'upload.xlsx')
    print(f"[FILE_UPLOAD_HANDLER] filename: {filename}")

    print("[FILE_UPLOAD_HANDLER] Getting 'file_content_base64' from request_data")
    file_content = request_data.get('file_content_base64', '')
    print(f"[FILE_UPLOAD_HANDLER] file_content length: {len(file_content) if file_content else 0}")

    print("[FILE_UPLOAD_HANDLER] Getting 'uploaded_by' from request_data")
    uploaded_by = request_data.get('uploaded_by', 'unknown')
    print(f"[FILE_UPLOAD_HANDLER] uploaded_by: {uploaded_by}")

    print("[FILE_UPLOAD_HANDLER] Getting 'notes' from request_data")
    notes = request_data.get('notes', '')
    print(f"[FILE_UPLOAD_HANDLER] notes: {notes}")

    print("[FILE_UPLOAD_HANDLER] Checking if file_content exists")
    if not file_content:
        print("[FILE_UPLOAD_HANDLER] No file content provided, returning 400 error")
        error_response = {
            'statusCode': 400,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'error': 'No file content provided'})
        }
        print(f"[FILE_UPLOAD_HANDLER] error_response: {error_response}")
        print("[FILE_UPLOAD_HANDLER] handle_api_upload() returning error")
        return error_response

    # Decode file content
    print("[FILE_UPLOAD_HANDLER] Decoding file content from base64")
    file_bytes = base64.b64decode(file_content)
    print(f"[FILE_UPLOAD_HANDLER] file_bytes decoded, length: {len(file_bytes)}")

    # Generate file ID and S3 key
    print("[FILE_UPLOAD_HANDLER] Generating file ID")
    file_id = str(uuid.uuid4())
    print(f"[FILE_UPLOAD_HANDLER] file_id generated: {file_id}")

    print("[FILE_UPLOAD_HANDLER] Getting current UTC time")
    now = datetime.utcnow()
    print(f"[FILE_UPLOAD_HANDLER] now: {now}")

    print("[FILE_UPLOAD_HANDLER] Formatting timestamp")
    timestamp = now.strftime('%Y%m%d_%H%M%S')
    print(f"[FILE_UPLOAD_HANDLER] timestamp: {timestamp}")

    print("[FILE_UPLOAD_HANDLER] Building S3 key")
    year = now.year
    print(f"[FILE_UPLOAD_HANDLER] year: {year}")
    month = now.month
    print(f"[FILE_UPLOAD_HANDLER] month: {month}")
    s3_key = f"uploads/{year}/{month:02d}/{timestamp}_{file_id}.xlsx"
    print(f"[FILE_UPLOAD_HANDLER] s3_key: {s3_key}")

    # Calculate file hash
    print("[FILE_UPLOAD_HANDLER] Calculating SHA256 hash of file")
    file_hash = hashlib.sha256(file_bytes).hexdigest()
    print(f"[FILE_UPLOAD_HANDLER] file_hash: {file_hash}")

    # Upload to S3
    print("[FILE_UPLOAD_HANDLER] Uploading file to S3")
    print(f"[FILE_UPLOAD_HANDLER] S3 Bucket: {S3_BUCKET}")
    print(f"[FILE_UPLOAD_HANDLER] S3 Key: {s3_key}")
    print(f"[FILE_UPLOAD_HANDLER] File size: {len(file_bytes)}")

    print("[FILE_UPLOAD_HANDLER] Calling s3_client.put_object()")
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
    print("[FILE_UPLOAD_HANDLER] s3_client.put_object() completed successfully")

    print("[FILE_UPLOAD_HANDLER] Logging file upload info")
    logger.info("File uploaded to S3", file_id=file_id, s3_key=s3_key, size=len(file_bytes))
    print("[FILE_UPLOAD_HANDLER] File upload logged")

    # Create metadata in DynamoDB
    print("[FILE_UPLOAD_HANDLER] Creating file metadata for DynamoDB")
    upload_time = datetime.utcnow().isoformat() + 'Z'
    print(f"[FILE_UPLOAD_HANDLER] upload_time: {upload_time}")

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
        'UploadedAt': upload_time,
        'UploadedBy': uploaded_by,
        'Notes': notes,
        'IsCurrentVersion': True,
        'Version': 1,
        'GSI3PK': 'FILES',
        'GSI3SK': upload_time
    }
    print(f"[FILE_UPLOAD_HANDLER] file_metadata created: {file_metadata}")

    print("[FILE_UPLOAD_HANDLER] Writing metadata to DynamoDB")
    dynamodb_client.table.put_item(Item=file_metadata)
    print("[FILE_UPLOAD_HANDLER] DynamoDB put_item completed")

    print("[FILE_UPLOAD_HANDLER] Logging metadata creation")
    logger.info("File metadata created", file_id=file_id)
    print("[FILE_UPLOAD_HANDLER] Metadata creation logged")

    # Trigger Step Functions workflow
    print("[FILE_UPLOAD_HANDLER] Checking if STEP_FUNCTION_ARN is set")
    print(f"[FILE_UPLOAD_HANDLER] STEP_FUNCTION_ARN: {STEP_FUNCTION_ARN}")

    if STEP_FUNCTION_ARN:
        print("[FILE_UPLOAD_HANDLER] STEP_FUNCTION_ARN is set, triggering Step Functions")
        try:
            print("[FILE_UPLOAD_HANDLER] Building Step Functions execution input")
            sfn_input = {
                'fileId': file_id,
                's3_bucket': S3_BUCKET,
                'key': s3_key
            }
            print(f"[FILE_UPLOAD_HANDLER] sfn_input: {sfn_input}")

            execution_name = f'process-{file_id}'
            print(f"[FILE_UPLOAD_HANDLER] execution_name: {execution_name}")

            print("[FILE_UPLOAD_HANDLER] Calling sfn_client.start_execution()")
            execution_response = sfn_client.start_execution(
                stateMachineArn=STEP_FUNCTION_ARN,
                name=execution_name,
                input=json.dumps(sfn_input)
            )
            print(f"[FILE_UPLOAD_HANDLER] execution_response: {execution_response}")

            execution_arn = execution_response['executionArn']
            print(f"[FILE_UPLOAD_HANDLER] execution_arn: {execution_arn}")

            print("[FILE_UPLOAD_HANDLER] Logging Step Functions start")
            logger.info("Step Functions execution started", execution_arn=execution_arn)
            print("[FILE_UPLOAD_HANDLER] Step Functions start logged")

        except Exception as e:
            print("[FILE_UPLOAD_HANDLER] !!! EXCEPTION in Step Functions start !!!")
            print(f"[FILE_UPLOAD_HANDLER] Exception: {e}")

            print("[FILE_UPLOAD_HANDLER] Logging Step Functions error")
            logger.error("Failed to start Step Functions", error=str(e))
            print("[FILE_UPLOAD_HANDLER] Error logged")

            print("[FILE_UPLOAD_HANDLER] Setting execution_arn to None")
            execution_arn = None
            print(f"[FILE_UPLOAD_HANDLER] execution_arn: {execution_arn}")
    else:
        print("[FILE_UPLOAD_HANDLER] STEP_FUNCTION_ARN not set, skipping workflow trigger")
        logger.warning("STEP_FUNCTION_ARN not set, skipping workflow trigger")
        print("[FILE_UPLOAD_HANDLER] Warning logged")
        execution_arn = None
        print(f"[FILE_UPLOAD_HANDLER] execution_arn: {execution_arn}")

    # Return success response
    print("[FILE_UPLOAD_HANDLER] Building success response")
    response_body = {
        'message': 'File uploaded successfully',
        'file_id': file_id,
        's3_bucket': S3_BUCKET,
        's3_key': s3_key,
        'file_size': len(file_bytes),
        'file_hash': file_hash,
        'status': 'UPLOADED',
        'execution_arn': execution_arn,
        'uploaded_at': file_metadata['UploadedAt']
    }
    print(f"[FILE_UPLOAD_HANDLER] response_body: {response_body}")

    success_response = {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
        'body': json.dumps(response_body)
    }
    print(f"[FILE_UPLOAD_HANDLER] success_response: {success_response}")

    print("[FILE_UPLOAD_HANDLER] ========================================")
    print("[FILE_UPLOAD_HANDLER] handle_api_upload() completed successfully")
    print("[FILE_UPLOAD_HANDLER] ========================================")
    return success_response


def handle_s3_event(event, logger: StructuredLogger):
    """
    Handle S3 event trigger
    Called when file is uploaded directly to S3
    """
    print("[FILE_UPLOAD_HANDLER] ========================================")
    print("[FILE_UPLOAD_HANDLER] handle_s3_event() started")
    print("[FILE_UPLOAD_HANDLER] ========================================")
    print(f"[FILE_UPLOAD_HANDLER] event: {event}")
    print(f"[FILE_UPLOAD_HANDLER] logger: {logger}")

    print("[FILE_UPLOAD_HANDLER] Logging S3 event handling")
    logger.info("Handling S3 event", event=event)
    print("[FILE_UPLOAD_HANDLER] S3 event logged")

    print("[FILE_UPLOAD_HANDLER] Initializing responses list")
    responses = []
    print(f"[FILE_UPLOAD_HANDLER] responses: {responses}")

    print("[FILE_UPLOAD_HANDLER] Getting Records from event")
    records = event.get('Records', [])
    print(f"[FILE_UPLOAD_HANDLER] Number of records: {len(records)}")

    print("[FILE_UPLOAD_HANDLER] Iterating through records")
    for idx, record in enumerate(records):
        print(f"[FILE_UPLOAD_HANDLER] --- Processing record {idx + 1}/{len(records)} ---")
        print(f"[FILE_UPLOAD_HANDLER] record: {record}")

        print("[FILE_UPLOAD_HANDLER] Getting eventName from record")
        event_name = record.get('eventName', '')
        print(f"[FILE_UPLOAD_HANDLER] event_name: {event_name}")

        print("[FILE_UPLOAD_HANDLER] Checking if eventName starts with 'ObjectCreated'")
        is_object_created = event_name.startswith('ObjectCreated')
        print(f"[FILE_UPLOAD_HANDLER] is_object_created: {is_object_created}")

        if is_object_created:
            print("[FILE_UPLOAD_HANDLER] Event is ObjectCreated, processing")

            print("[FILE_UPLOAD_HANDLER] Extracting S3 bucket name")
            s3_bucket = record['s3']['bucket']['name']
            print(f"[FILE_UPLOAD_HANDLER] s3_bucket: {s3_bucket}")

            print("[FILE_UPLOAD_HANDLER] Extracting S3 object key")
            s3_key = record['s3']['object']['key']
            print(f"[FILE_UPLOAD_HANDLER] s3_key: {s3_key}")

            print("[FILE_UPLOAD_HANDLER] Extracting file size")
            file_size = record['s3']['object']['size']
            print(f"[FILE_UPLOAD_HANDLER] file_size: {file_size}")

            print("[FILE_UPLOAD_HANDLER] Logging S3 object processing")
            logger.info("Processing S3 object", bucket=s3_bucket, key=s3_key, size=file_size)
            print("[FILE_UPLOAD_HANDLER] S3 object logged")

            # Generate file ID
            print("[FILE_UPLOAD_HANDLER] Generating file ID")
            file_id = str(uuid.uuid4())
            print(f"[FILE_UPLOAD_HANDLER] file_id: {file_id}")

            # Get object metadata
            print("[FILE_UPLOAD_HANDLER] Getting object metadata from S3")
            try:
                print("[FILE_UPLOAD_HANDLER] Calling s3_client.head_object()")
                head_response = s3_client.head_object(Bucket=s3_bucket, Key=s3_key)
                print(f"[FILE_UPLOAD_HANDLER] head_response: {head_response}")

                print("[FILE_UPLOAD_HANDLER] Extracting metadata from head_response")
                metadata = head_response.get('Metadata', {})
                print(f"[FILE_UPLOAD_HANDLER] metadata: {metadata}")

                print("[FILE_UPLOAD_HANDLER] Getting 'uploaded-by' from metadata")
                uploaded_by = metadata.get('uploaded-by', 'direct-s3-upload')
                print(f"[FILE_UPLOAD_HANDLER] uploaded_by: {uploaded_by}")

                print("[FILE_UPLOAD_HANDLER] Getting 'original-filename' from metadata")
                original_filename = metadata.get('original-filename', s3_key.split('/')[-1])
                print(f"[FILE_UPLOAD_HANDLER] original_filename: {original_filename}")

                print("[FILE_UPLOAD_HANDLER] Getting VersionId from head_response")
                version_id = head_response.get('VersionId', '')
                print(f"[FILE_UPLOAD_HANDLER] version_id: {version_id}")

            except Exception as e:
                print("[FILE_UPLOAD_HANDLER] !!! EXCEPTION getting object metadata !!!")
                print(f"[FILE_UPLOAD_HANDLER] Exception: {e}")

                print("[FILE_UPLOAD_HANDLER] Logging metadata error")
                logger.error("Failed to get object metadata", error=str(e))
                print("[FILE_UPLOAD_HANDLER] Error logged")

                print("[FILE_UPLOAD_HANDLER] Setting default values")
                uploaded_by = 'direct-s3-upload'
                print(f"[FILE_UPLOAD_HANDLER] uploaded_by: {uploaded_by}")
                original_filename = s3_key.split('/')[-1]
                print(f"[FILE_UPLOAD_HANDLER] original_filename: {original_filename}")
                version_id = ''
                print(f"[FILE_UPLOAD_HANDLER] version_id: {version_id}")

            # Calculate file hash
            print("[FILE_UPLOAD_HANDLER] Calculating file hash")
            try:
                print("[FILE_UPLOAD_HANDLER] Calling s3_client.get_object()")
                obj_response = s3_client.get_object(Bucket=s3_bucket, Key=s3_key)
                print(f"[FILE_UPLOAD_HANDLER] obj_response keys: {obj_response.keys()}")

                print("[FILE_UPLOAD_HANDLER] Reading file content from Body")
                file_content = obj_response['Body'].read()
                print(f"[FILE_UPLOAD_HANDLER] file_content length: {len(file_content)}")

                print("[FILE_UPLOAD_HANDLER] Calculating SHA256 hash")
                file_hash = hashlib.sha256(file_content).hexdigest()
                print(f"[FILE_UPLOAD_HANDLER] file_hash: {file_hash}")

            except Exception as e:
                print("[FILE_UPLOAD_HANDLER] !!! EXCEPTION reading object for hash !!!")
                print(f"[FILE_UPLOAD_HANDLER] Exception: {e}")

                print("[FILE_UPLOAD_HANDLER] Logging hash calculation error")
                logger.error("Failed to read object for hash", error=str(e))
                print("[FILE_UPLOAD_HANDLER] Error logged")

                print("[FILE_UPLOAD_HANDLER] Setting file_hash to empty string")
                file_hash = ''
                print(f"[FILE_UPLOAD_HANDLER] file_hash: {file_hash}")

            # Create metadata in DynamoDB
            print("[FILE_UPLOAD_HANDLER] Creating file metadata for DynamoDB")
            upload_time = datetime.utcnow().isoformat() + 'Z'
            print(f"[FILE_UPLOAD_HANDLER] upload_time: {upload_time}")

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
                'UploadedAt': upload_time,
                'UploadedBy': uploaded_by,
                'IsCurrentVersion': True,
                'Version': 1,
                'GSI3PK': 'FILES',
                'GSI3SK': upload_time
            }
            print(f"[FILE_UPLOAD_HANDLER] file_metadata: {file_metadata}")

            print("[FILE_UPLOAD_HANDLER] Writing metadata to DynamoDB")
            dynamodb_client.table.put_item(Item=file_metadata)
            print("[FILE_UPLOAD_HANDLER] DynamoDB put_item completed")

            print("[FILE_UPLOAD_HANDLER] Logging metadata creation from S3 event")
            logger.info("File metadata created from S3 event", file_id=file_id)
            print("[FILE_UPLOAD_HANDLER] Metadata creation logged")

            # Trigger Step Functions workflow
            print("[FILE_UPLOAD_HANDLER] Checking if STEP_FUNCTION_ARN is set")
            if STEP_FUNCTION_ARN:
                print("[FILE_UPLOAD_HANDLER] STEP_FUNCTION_ARN is set, triggering workflow")
                try:
                    print("[FILE_UPLOAD_HANDLER] Building Step Functions input")
                    sfn_input = {
                        'fileId': file_id,
                        's3_bucket': s3_bucket,
                        'key': s3_key
                    }
                    print(f"[FILE_UPLOAD_HANDLER] sfn_input: {sfn_input}")

                    execution_name = f'process-{file_id}'
                    print(f"[FILE_UPLOAD_HANDLER] execution_name: {execution_name}")

                    print("[FILE_UPLOAD_HANDLER] Calling sfn_client.start_execution()")
                    execution_response = sfn_client.start_execution(
                        stateMachineArn=STEP_FUNCTION_ARN,
                        name=execution_name,
                        input=json.dumps(sfn_input)
                    )
                    print(f"[FILE_UPLOAD_HANDLER] execution_response: {execution_response}")

                    execution_arn = execution_response['executionArn']
                    print(f"[FILE_UPLOAD_HANDLER] execution_arn: {execution_arn}")

                    print("[FILE_UPLOAD_HANDLER] Logging Step Functions execution start")
                    logger.info("Step Functions execution started", execution_arn=execution_arn)
                    print("[FILE_UPLOAD_HANDLER] Step Functions start logged")

                    print("[FILE_UPLOAD_HANDLER] Building success response for this file")
                    response_item = {
                        'file_id': file_id,
                        'status': 'processing_started',
                        'execution_arn': execution_arn
                    }
                    print(f"[FILE_UPLOAD_HANDLER] response_item: {response_item}")

                    print("[FILE_UPLOAD_HANDLER] Appending to responses")
                    responses.append(response_item)
                    print(f"[FILE_UPLOAD_HANDLER] responses: {responses}")

                except Exception as e:
                    print("[FILE_UPLOAD_HANDLER] !!! EXCEPTION starting Step Functions !!!")
                    print(f"[FILE_UPLOAD_HANDLER] Exception: {e}")

                    print("[FILE_UPLOAD_HANDLER] Logging Step Functions error")
                    logger.error("Failed to start Step Functions", error=str(e))
                    print("[FILE_UPLOAD_HANDLER] Error logged")

                    print("[FILE_UPLOAD_HANDLER] Building error response for this file")
                    response_item = {
                        'file_id': file_id,
                        'status': 'uploaded',
                        'error': str(e)
                    }
                    print(f"[FILE_UPLOAD_HANDLER] response_item: {response_item}")

                    print("[FILE_UPLOAD_HANDLER] Appending to responses")
                    responses.append(response_item)
                    print(f"[FILE_UPLOAD_HANDLER] responses: {responses}")
            else:
                print("[FILE_UPLOAD_HANDLER] STEP_FUNCTION_ARN not set")
                logger.warning("STEP_FUNCTION_ARN not set")
                print("[FILE_UPLOAD_HANDLER] Warning logged")

                print("[FILE_UPLOAD_HANDLER] Building response without workflow")
                response_item = {
                    'file_id': file_id,
                    'status': 'uploaded'
                }
                print(f"[FILE_UPLOAD_HANDLER] response_item: {response_item}")

                print("[FILE_UPLOAD_HANDLER] Appending to responses")
                responses.append(response_item)
                print(f"[FILE_UPLOAD_HANDLER] responses: {responses}")
        else:
            print(f"[FILE_UPLOAD_HANDLER] Skipping event (not ObjectCreated): {event_name}")

    print("[FILE_UPLOAD_HANDLER] Building final response")
    response_body = {
        'message': 'S3 events processed',
        'files': responses
    }
    print(f"[FILE_UPLOAD_HANDLER] response_body: {response_body}")

    final_response = {
        'statusCode': 200,
        'body': json.dumps(response_body)
    }
    print(f"[FILE_UPLOAD_HANDLER] final_response: {final_response}")

    print("[FILE_UPLOAD_HANDLER] ========================================")
    print("[FILE_UPLOAD_HANDLER] handle_s3_event() completed")
    print("[FILE_UPLOAD_HANDLER] ========================================")
    return final_response
