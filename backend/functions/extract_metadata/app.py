"""
Extract Metadata Lambda
======================
SIMPLE SQS-triggered Lambda that:
1. Reads message from upload-queue
2. Downloads Excel from S3
3. Extracts: umbrella_code, submission_date, period
4. ADDS results to message dict
5. Sends to validation-queue

NO STEP FUNCTIONS. NO JSONPATH. JUST SIMPLE DICTS.
"""

import json
import os
import boto3
import tempfile
from datetime import datetime
from urllib.parse import unquote_plus

# Simple imports from common layer
from common.excel_parser import PayFileParser
from common.logger import StructuredLogger

# AWS clients
s3_client = boto3.client('s3')
sqs_client = boto3.client('sqs')
dynamodb = boto3.resource('dynamodb')

# Environment variables
VALIDATION_QUEUE_URL = os.environ['VALIDATION_QUEUE_URL']
TABLE_NAME = os.environ['TABLE_NAME']

# Logger
logger = StructuredLogger('extract-metadata')

def lambda_handler(event, context):
    """
    Process SQS messages from upload-queue
    """
    logger.info("🚀 Extract-metadata Lambda started", event=event)

    for record in event['Records']:
        try:
            # Parse the SQS message
            message = json.loads(record['body'])
            logger.info("📥 RECEIVED MESSAGE", file_key=message.get('s3_key'))

            # Extract S3 details
            bucket = message['s3_bucket']
            key = unquote_plus(message['s3_key'])

            logger.info("📂 Processing file", bucket=bucket, key=key)

            # Generate file_id (use existing or create new)
            file_id = message.get('file_id')
            if not file_id:
                import uuid
                file_id = str(uuid.uuid4())
                message['file_id'] = file_id
                logger.info("🆔 Generated new file_id", file_id=file_id)

            # Download Excel file to /tmp
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx')
            logger.info("⬇️  Downloading from S3", local_path=temp_file.name)

            s3_client.download_file(bucket, key, temp_file.name)
            logger.info("✅ Downloaded successfully")

            # Parse Excel file
            filename = key.split('/')[-1]
            logger.info("📊 Parsing Excel file", filename=filename)

            parser = PayFileParser(temp_file.name, original_filename=filename)
            metadata = parser.extract_metadata()
            parser.close()

            logger.info("✅ Metadata extracted", metadata=metadata)

            # Clean up temp file
            os.unlink(temp_file.name)

            # Get umbrella company from database
            umbrella_code = metadata['umbrella_code']
            if not umbrella_code:
                raise ValueError(f"Could not extract umbrella code from filename: {filename}")

            logger.info("🔍 Looking up umbrella company", umbrella_code=umbrella_code)

            table = dynamodb.Table(TABLE_NAME)
            response = table.query(
                IndexName='GSI1',
                KeyConditionExpression='GSI1PK = :pk',
                ExpressionAttributeValues={':pk': f'UMBRELLA_CODE#{umbrella_code.upper()}'}
            )

            if not response.get('Items'):
                raise ValueError(f"Umbrella company '{umbrella_code}' not found in database")

            umbrella = response['Items'][0]
            umbrella_id = umbrella['UmbrellaID']
            logger.info("✅ Umbrella found", umbrella_id=umbrella_id, umbrella_code=umbrella_code)

            # Match pay period
            submission_date = metadata['submission_date']
            if not submission_date:
                raise ValueError(f"Could not extract submission date from filename: {filename}")

            # Convert date from DDMMYYYY to YYYY-MM-DD for DynamoDB comparison
            submission_date_formatted = f"{submission_date[4:8]}-{submission_date[2:4]}-{submission_date[0:2]}"
            logger.info("📅 Matching pay period", submission_date=submission_date, formatted=submission_date_formatted)

            # Query all periods
            period_response = table.scan(
                FilterExpression='begins_with(PK, :prefix) AND SK = :sk',
                ExpressionAttributeValues={
                    ':prefix': 'PERIOD#',
                    ':sk': 'PROFILE'
                }
            )

            period = None
            period_number = None

            # Try exact match on SubmissionDate first
            for period_item in period_response.get('Items', []):
                if period_item.get('SubmissionDate') == submission_date_formatted:
                    period = period_item
                    period_number = int(period_item['PeriodNumber'])  # Convert Decimal to int
                    logger.info("✅ Period matched (exact)", period_number=period_number)
                    break

            # Fallback: check if submission falls within work period
            if not period:
                for period_item in period_response.get('Items', []):
                    work_start = period_item.get('WorkStartDate')
                    work_end = period_item.get('WorkEndDate')
                    if work_start and work_end and work_start <= submission_date <= work_end:
                        period = period_item
                        period_number = int(period_item['PeriodNumber'])  # Convert Decimal to int
                        logger.info("✅ Period matched (fallback)", period_number=period_number)
                        break

            if not period:
                raise ValueError(f"No pay period found for submission date {submission_date}")

            # ⭐ ADD METADATA TO MESSAGE (don't replace, just add!)
            message['umbrella_code'] = umbrella_code
            message['umbrella_id'] = umbrella_id
            message['period_number'] = period_number
            message['period_id'] = period['PK']
            message['submission_date'] = submission_date
            message['filename'] = filename
            message['metadata_extracted'] = True
            message['metadata_extracted_at'] = datetime.utcnow().isoformat() + 'Z'

            # Create FILE record in DynamoDB
            logger.info("💾 Creating FILE record in DynamoDB", file_id=file_id)

            table.put_item(Item={
                'PK': f'FILE#{file_id}',
                'SK': 'METADATA',
                'EntityType': 'File',
                'FileID': file_id,
                'S3Bucket': bucket,
                'S3Key': key,
                'OriginalFilename': filename,
                'UmbrellaCode': umbrella_code,
                'UmbrellaID': umbrella_id,
                'PeriodNumber': period_number,
                'SubmissionDate': submission_date,
                'Status': 'PROCESSING',
                'UploadedAt': message.get('upload_time', datetime.utcnow().isoformat() + 'Z'),
                'ProcessingStartedAt': datetime.utcnow().isoformat() + 'Z',
                'FileSizeBytes': message.get('file_size', 0),
                'IsCurrentVersion': True,
                'Version': 1,
                'GSI3PK': 'FILES',
                'GSI3SK': datetime.utcnow().isoformat() + 'Z'
            })

            logger.info("✅ FILE record created")

            # 📤 SEND TO VALIDATION QUEUE
            logger.info("📤 FORWARDING TO VALIDATION QUEUE", message_preview=str(message)[:200])

            sqs_client.send_message(
                QueueUrl=VALIDATION_QUEUE_URL,
                MessageBody=json.dumps(message)
            )

            logger.info("✅ STAGE COMPLETE: Metadata extraction successful", file_id=file_id)

        except Exception as e:
            logger.error("❌ ERROR in metadata extraction", error=str(e))

            # Add error to message for visibility
            if 'errors' not in message:
                message['errors'] = []
            message['errors'].append({
                'stage': 'extract-metadata',
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat() + 'Z'
            })

            # Update FILE status to FAILED if we created a record
            if 'file_id' in message:
                try:
                    table = dynamodb.Table(TABLE_NAME)
                    table.update_item(
                        Key={'PK': f'FILE#{message["file_id"]}', 'SK': 'METADATA'},
                        UpdateExpression='SET #status = :status, ErrorMessage = :error',
                        ExpressionAttributeNames={'#status': 'Status'},
                        ExpressionAttributeValues={
                            ':status': 'FAILED',
                            ':error': str(e)
                        }
                    )
                except:
                    pass  # Best effort

            # Re-raise so SQS retries (3x) then sends to DLQ
            raise

    return {'statusCode': 200, 'body': 'Success'}
