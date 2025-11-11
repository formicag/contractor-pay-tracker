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

    VERBOSE LOGGING ENABLED FOR DEBUGGING
    """
    logger.info("=" * 80)
    logger.info("🚀 EXTRACT-METADATA LAMBDA INVOKED")
    logger.info("=" * 80)
    logger.info("📋 Full event payload", event=event)
    logger.info("📊 Event structure",
                record_count=len(event.get('Records', [])),
                context_request_id=context.request_id if context else None)

    # Process each SQS record
    for idx, record in enumerate(event['Records'], 1):
        logger.info("-" * 80)
        logger.info(f"🔄 PROCESSING RECORD {idx}/{len(event['Records'])}")
        logger.info("-" * 80)

        try:
            # ============================================================
            # STEP 1: Parse SQS Message Body
            # ============================================================
            logger.info("STEP 1: Parsing SQS message body")
            logger.info("📦 Raw message body (first 500 chars)",
                       raw_body=record['body'][:500])

            message = json.loads(record['body'])

            logger.info("✅ Message parsed successfully")
            logger.info("📨 Message keys present", keys=list(message.keys()))
            logger.info("📄 Full message content", message=message)
            logger.info("🔑 S3 Key from message", s3_key=message.get('s3_key'))
            logger.info("🪣 S3 Bucket from message", s3_bucket=message.get('s3_bucket'))
            logger.info("📏 File size from message", file_size=message.get('file_size', 'NOT_PROVIDED'))

            # ============================================================
            # STEP 2: Extract and Validate S3 Details
            # ============================================================
            logger.info("STEP 2: Extracting S3 details")

            if 's3_bucket' not in message:
                raise ValueError("Missing 's3_bucket' in message")
            if 's3_key' not in message:
                raise ValueError("Missing 's3_key' in message")

            bucket = message['s3_bucket']
            key_raw = message['s3_key']
            key = unquote_plus(key_raw)

            logger.info("✅ S3 details validated")
            logger.info("🪣 Bucket name", bucket=bucket)
            logger.info("🔑 Raw S3 key", key_raw=key_raw)
            logger.info("🔑 Decoded S3 key", key=key)
            logger.info("📁 Filename from path", filename=key.split('/')[-1])

            # ============================================================
            # STEP 3: Generate or Validate File ID
            # ============================================================
            logger.info("STEP 3: Handling file ID")

            file_id = message.get('file_id')

            if not file_id:
                logger.info("⚠️  No file_id in message, generating new UUID")
                import uuid
                file_id = str(uuid.uuid4())
                message['file_id'] = file_id
                logger.info("✅ Generated new file_id", file_id=file_id)
            else:
                logger.info("✅ Using existing file_id from message", file_id=file_id)

            # Validate UUID format
            try:
                import uuid
                uuid.UUID(file_id)
                logger.info("✅ File ID is valid UUID format")
            except ValueError:
                logger.warning("⚠️  File ID is NOT a valid UUID", file_id=file_id)

            # ============================================================
            # STEP 4: Download File from S3
            # ============================================================
            logger.info("STEP 4: Downloading file from S3")

            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx')
            temp_path = temp_file.name

            logger.info("📂 Created temporary file", temp_path=temp_path)
            logger.info("⬇️  Initiating S3 download",
                       bucket=bucket,
                       key=key,
                       destination=temp_path)

            try:
                s3_response = s3_client.download_file(bucket, key, temp_path)
                logger.info("✅ S3 download completed")

                # Verify file was downloaded
                file_size_on_disk = os.path.getsize(temp_path)
                logger.info("📏 Downloaded file size", bytes=file_size_on_disk,
                           kb=round(file_size_on_disk / 1024, 2))

                if file_size_on_disk == 0:
                    raise ValueError("Downloaded file is empty (0 bytes)")

            except Exception as s3_error:
                logger.error("❌ S3 download failed", error=str(s3_error),
                            bucket=bucket, key=key)
                raise

            # ============================================================
            # STEP 5: Parse Excel File and Extract Metadata
            # ============================================================
            logger.info("STEP 5: Parsing Excel file")

            filename = key.split('/')[-1]
            logger.info("📁 Filename extracted from path", filename=filename)
            logger.info("📊 Initializing PayFileParser", file_path=temp_path)

            try:
                parser = PayFileParser(temp_path, original_filename=filename)
                logger.info("✅ Parser initialized successfully")

                logger.info("🔍 Calling extract_metadata()")
                metadata = parser.extract_metadata()

                logger.info("✅ Metadata extraction completed")
                logger.info("📋 Metadata keys", keys=list(metadata.keys()) if metadata else None)
                logger.info("📄 Full metadata content", metadata=metadata)

                # Log each metadata field individually for clarity
                if metadata:
                    logger.info("🏢 Umbrella code", umbrella_code=metadata.get('umbrella_code'))
                    logger.info("📅 Submission date", submission_date=metadata.get('submission_date'))
                    logger.info("📊 Period number", period=metadata.get('period'))
                    logger.info("👥 Contractor count", contractor_count=metadata.get('contractor_count'))

                parser.close()
                logger.info("✅ Parser closed")

            except Exception as parse_error:
                logger.error("❌ Excel parsing failed", error=str(parse_error),
                            filename=filename, temp_path=temp_path)
                raise

            # ============================================================
            # STEP 6: Cleanup Temporary File
            # ============================================================
            logger.info("STEP 6: Cleaning up temporary file")
            try:
                os.unlink(temp_path)
                logger.info("✅ Temporary file deleted", path=temp_path)
            except Exception as cleanup_error:
                logger.warning("⚠️  Failed to delete temp file", error=str(cleanup_error))

            # ============================================================
            # STEP 7: Validate and Lookup Umbrella Company
            # ============================================================
            logger.info("STEP 7: Looking up umbrella company in DynamoDB")

            umbrella_code = metadata.get('umbrella_code')
            logger.info("🏢 Umbrella code from metadata", umbrella_code=umbrella_code)

            if not umbrella_code:
                logger.error("❌ No umbrella code extracted", filename=filename, metadata=metadata)
                raise ValueError(f"Could not extract umbrella code from filename: {filename}")

            logger.info("✅ Umbrella code validated", code=umbrella_code)

            # Normalize to uppercase for consistency
            umbrella_code_upper = umbrella_code.upper()
            logger.info("🔤 Normalized umbrella code", original=umbrella_code, normalized=umbrella_code_upper)

            # Query DynamoDB for umbrella company
            table = dynamodb.Table(TABLE_NAME)
            logger.info("📊 DynamoDB table initialized", table_name=TABLE_NAME)

            gsi1_pk = f'UMBRELLA_CODE#{umbrella_code_upper}'
            logger.info("🔍 Querying GSI1 for umbrella",
                       index_name='GSI1',
                       gsi1_pk=gsi1_pk)

            try:
                response = table.query(
                    IndexName='GSI1',
                    KeyConditionExpression='GSI1PK = :pk',
                    ExpressionAttributeValues={':pk': gsi1_pk}
                )

                logger.info("✅ DynamoDB query executed")
                logger.info("📊 Query result", item_count=len(response.get('Items', [])))

                if response.get('Items'):
                    logger.info("📄 Items returned from query", items=response['Items'])

            except Exception as dynamo_error:
                logger.error("❌ DynamoDB query failed",
                            error=str(dynamo_error),
                            index='GSI1',
                            pk=gsi1_pk)
                raise

            # Validate we found the umbrella company
            if not response.get('Items'):
                logger.error("❌ Umbrella company NOT FOUND in database",
                            umbrella_code=umbrella_code,
                            gsi1_pk=gsi1_pk,
                            table=TABLE_NAME)
                raise ValueError(f"Umbrella company '{umbrella_code}' not found in database")

            umbrella = response['Items'][0]
            logger.info("✅ Umbrella company found", umbrella_data=umbrella)

            umbrella_id = umbrella.get('UmbrellaID')
            logger.info("🆔 Extracted umbrella ID", umbrella_id=umbrella_id)

            if not umbrella_id:
                logger.error("❌ Umbrella record missing UmbrellaID field", umbrella=umbrella)
                raise ValueError("Umbrella record in database is missing UmbrellaID")

            logger.info("✅ STEP 7 COMPLETE",
                       umbrella_code=umbrella_code,
                       umbrella_id=umbrella_id)

            # ============================================================
            # STEP 8: Match Pay Period
            # ============================================================
            logger.info("STEP 8: Matching pay period for submission date")

            submission_date = metadata.get('submission_date')
            logger.info("📅 Submission date from metadata", submission_date=submission_date)

            if not submission_date:
                logger.error("❌ No submission date extracted", filename=filename, metadata=metadata)
                raise ValueError(f"Could not extract submission date from filename: {filename}")

            logger.info("✅ Submission date validated", submission_date=submission_date)

            # Parse and format the submission date
            # Expected format: DDMMYYYY (e.g., "02062025")
            logger.info("🔄 Parsing submission date",
                       format="DDMMYYYY",
                       raw_value=submission_date,
                       length=len(submission_date) if submission_date else 0)

            if len(submission_date) != 8:
                logger.error("❌ Invalid submission date length",
                            expected=8,
                            actual=len(submission_date),
                            value=submission_date)
                raise ValueError(f"Invalid submission date format: {submission_date} (expected DDMMYYYY)")

            # Extract day, month, year
            day = submission_date[0:2]
            month = submission_date[2:4]
            year = submission_date[4:8]

            logger.info("📅 Parsed date components",
                       day=day,
                       month=month,
                       year=year)

            # Convert to YYYY-MM-DD for DynamoDB comparison
            submission_date_formatted = f"{year}-{month}-{day}"
            logger.info("✅ Formatted submission date",
                       original=submission_date,
                       formatted=submission_date_formatted)

            # Query all periods from DynamoDB
            logger.info("🔍 Querying all pay periods",
                       filter="PK begins_with PERIOD# AND SK = PROFILE")

            try:
                period_response = table.scan(
                    FilterExpression='begins_with(PK, :prefix) AND SK = :sk',
                    ExpressionAttributeValues={
                        ':prefix': 'PERIOD#',
                        ':sk': 'PROFILE'
                    }
                )

                logger.info("✅ Period scan completed")
                logger.info("📊 Periods found", count=len(period_response.get('Items', [])))

                if period_response.get('Items'):
                    logger.info("📄 Period records", periods=[
                        {
                            'PK': p.get('PK'),
                            'PeriodNumber': str(p.get('PeriodNumber')),
                            'SubmissionDate': p.get('SubmissionDate'),
                            'WorkStartDate': p.get('WorkStartDate'),
                            'WorkEndDate': p.get('WorkEndDate')
                        }
                        for p in period_response.get('Items', [])
                    ])

            except Exception as scan_error:
                logger.error("❌ Period scan failed", error=str(scan_error))
                raise

            period = None
            period_number = None
            match_type = None

            # MATCHING STRATEGY 1: Try exact match on SubmissionDate
            logger.info("🔍 Attempting EXACT match on SubmissionDate",
                       target_date=submission_date_formatted)

            for idx, period_item in enumerate(period_response.get('Items', []), 1):
                period_submission_date = period_item.get('SubmissionDate')
                logger.info(f"  Checking period {idx}",
                           period_number=str(period_item.get('PeriodNumber')),
                           submission_date=period_submission_date,
                           match=period_submission_date == submission_date_formatted)

                if period_submission_date == submission_date_formatted:
                    period = period_item
                    period_number = int(period_item['PeriodNumber'])
                    match_type = "EXACT_SUBMISSION_DATE"
                    logger.info("✅ EXACT MATCH FOUND",
                               period_number=period_number,
                               matched_date=period_submission_date)
                    break

            # MATCHING STRATEGY 2: Fallback - check if submission falls within work period
            if not period:
                logger.info("⚠️  No exact match, trying RANGE match (WorkStartDate <= date <= WorkEndDate)")

                for idx, period_item in enumerate(period_response.get('Items', []), 1):
                    work_start = period_item.get('WorkStartDate')
                    work_end = period_item.get('WorkEndDate')

                    logger.info(f"  Checking period {idx} range",
                               period_number=str(period_item.get('PeriodNumber')),
                               work_start=work_start,
                               work_end=work_end,
                               target_date=submission_date_formatted)

                    if work_start and work_end:
                        is_in_range = work_start <= submission_date_formatted <= work_end
                        logger.info(f"    Range check: {is_in_range}",
                                   calculation=f"{work_start} <= {submission_date_formatted} <= {work_end}")

                        if is_in_range:
                            period = period_item
                            period_number = int(period_item['PeriodNumber'])
                            match_type = "WORK_PERIOD_RANGE"
                            logger.info("✅ RANGE MATCH FOUND",
                                       period_number=period_number,
                                       work_start=work_start,
                                       work_end=work_end)
                            break

            # Validate we found a period
            if not period:
                logger.error("❌ NO PERIOD MATCH FOUND",
                            submission_date=submission_date,
                            formatted_date=submission_date_formatted,
                            total_periods_checked=len(period_response.get('Items', [])))
                raise ValueError(f"No pay period found for submission date {submission_date}")

            logger.info("✅ STEP 8 COMPLETE",
                       match_type=match_type,
                       period_number=period_number,
                       period_pk=period.get('PK'))

            # ============================================================
            # STEP 9: Enrich Message with Extracted Metadata
            # ============================================================
            logger.info("STEP 9: Adding metadata to message payload")

            # Add extracted metadata fields to message (don't replace, just add!)
            message['umbrella_code'] = umbrella_code
            message['umbrella_id'] = umbrella_id
            message['period_number'] = period_number
            message['period_id'] = period['PK']
            message['submission_date'] = submission_date
            message['filename'] = filename
            message['metadata_extracted'] = True
            message['metadata_extracted_at'] = datetime.utcnow().isoformat() + 'Z'

            logger.info("✅ Message enriched with metadata")
            logger.info("📦 Updated message keys", keys=list(message.keys()))
            logger.info("📄 Full enriched message", message=message)

            # ============================================================
            # STEP 10: Create FILE Record in DynamoDB
            # ============================================================
            logger.info("STEP 10: Creating FILE record in DynamoDB")

            processing_timestamp = datetime.utcnow().isoformat() + 'Z'
            file_pk = f'FILE#{file_id}'

            file_item = {
                # Primary Keys
                'PK': file_pk,
                'SK': 'METADATA',
                'EntityType': 'File',

                # File Identification
                'FileID': file_id,
                'OriginalFilename': filename,

                # S3 Location
                'S3Bucket': bucket,
                'S3Key': key,
                'FileSizeBytes': message.get('file_size', 0),

                # Business Data
                'UmbrellaCode': umbrella_code,
                'UmbrellaID': umbrella_id,
                'PeriodNumber': period_number,
                'SubmissionDate': submission_date,

                # Processing Status
                'Status': 'PROCESSING',
                'UploadedAt': message.get('upload_time', processing_timestamp),
                'ProcessingStartedAt': processing_timestamp,

                # Versioning
                'IsCurrentVersion': True,
                'Version': 1,

                # GSI Keys for querying
                'GSI3PK': 'FILES',
                'GSI3SK': processing_timestamp
            }

            logger.info("📋 FILE item prepared", item_keys=list(file_item.keys()))
            logger.info("💾 Writing to DynamoDB",
                       pk=file_pk,
                       sk='METADATA',
                       table=TABLE_NAME)

            try:
                table.put_item(Item=file_item)
                logger.info("✅ FILE record created successfully",
                           file_id=file_id,
                           pk=file_pk)
            except Exception as put_error:
                logger.error("❌ Failed to create FILE record",
                            error=str(put_error),
                            file_item=file_item)
                raise

            # ============================================================
            # STEP 11: Send Message to Validation Queue
            # ============================================================
            logger.info("STEP 11: Sending message to validation queue")
            logger.info("📤 Target queue", url=VALIDATION_QUEUE_URL)

            # Serialize message to JSON
            message_body = json.dumps(message)
            logger.info("📦 Message body size", bytes=len(message_body))
            logger.info("📄 Message preview (first 500 chars)",
                       preview=message_body[:500])

            try:
                sqs_response = sqs_client.send_message(
                    QueueUrl=VALIDATION_QUEUE_URL,
                    MessageBody=message_body
                )

                message_id = sqs_response.get('MessageId')
                logger.info("✅ Message sent to SQS successfully",
                           message_id=message_id,
                           queue=VALIDATION_QUEUE_URL)

            except Exception as sqs_error:
                logger.error("❌ Failed to send message to SQS",
                            error=str(sqs_error),
                            queue=VALIDATION_QUEUE_URL)
                raise

            # ============================================================
            # STEP 12: Processing Complete
            # ============================================================
            logger.info("=" * 80)
            logger.info("✅ ✅ ✅ METADATA EXTRACTION COMPLETE ✅ ✅ ✅")
            logger.info("=" * 80)
            logger.info("📊 Summary",
                       file_id=file_id,
                       filename=filename,
                       umbrella=umbrella_code,
                       period=period_number,
                       next_stage="validation")

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
