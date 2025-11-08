"""
File Processor Lambda Function
Processes Excel files, validates contractor data, and imports to DynamoDB

Implements Gemini improvements:
- Automatic supersede (improvement #4)
- Many-to-many contractor-umbrella validation (improvement #1)
- Error vs Warning handling (improvement #2)
"""

print("[FILE_PROCESSOR] About to execute: import json")
import json
print("[FILE_PROCESSOR] Result: json module imported")

print("[FILE_PROCESSOR] About to execute: import os")
import os
print("[FILE_PROCESSOR] Result: os module imported")

print("[FILE_PROCESSOR] About to execute: import tempfile")
import tempfile
print("[FILE_PROCESSOR] Result: tempfile module imported")

print("[FILE_PROCESSOR] About to execute: import uuid")
import uuid
print("[FILE_PROCESSOR] Result: uuid module imported")

print("[FILE_PROCESSOR] About to execute: from datetime import datetime")
from datetime import datetime
print("[FILE_PROCESSOR] Result: datetime imported from datetime module")

print("[FILE_PROCESSOR] About to execute: from decimal import Decimal")
from decimal import Decimal
print("[FILE_PROCESSOR] Result: Decimal imported from decimal module")

print("[FILE_PROCESSOR] About to execute: import boto3")
import boto3
print("[FILE_PROCESSOR] Result: boto3 module imported")

# Import from common layer
print("[FILE_PROCESSOR] About to execute: from common.logger import StructuredLogger")
from common.logger import StructuredLogger
print("[FILE_PROCESSOR] Result: StructuredLogger imported from common.logger")

print("[FILE_PROCESSOR] About to execute: from common.dynamodb import DynamoDBClient")
from common.dynamodb import DynamoDBClient
print("[FILE_PROCESSOR] Result: DynamoDBClient imported from common.dynamodb")

print("[FILE_PROCESSOR] About to execute: from common.excel_parser import PayFileParser")
from common.excel_parser import PayFileParser
print("[FILE_PROCESSOR] Result: PayFileParser imported from common.excel_parser")

print("[FILE_PROCESSOR] About to execute: from common.validators import ValidationEngine")
from common.validators import ValidationEngine
print("[FILE_PROCESSOR] Result: ValidationEngine imported from common.validators")


print("[FILE_PROCESSOR] About to execute: s3_client = boto3.client('s3')")
s3_client = boto3.client('s3')
print(f"[FILE_PROCESSOR] Result: s3_client created = {s3_client}")

print("[FILE_PROCESSOR] About to execute: dynamodb_client = DynamoDBClient()")
dynamodb_client = DynamoDBClient()
print(f"[FILE_PROCESSOR] Result: dynamodb_client created = {dynamodb_client}")


def lambda_handler(event, context):
    """Main Lambda handler"""
    print(f"[FILE_PROCESSOR] About to execute: lambda_handler with event = {event}, context = {context}")

    print(f"[FILE_PROCESSOR] About to execute: logger = StructuredLogger('file-processor', context.aws_request_id)")
    logger = StructuredLogger("file-processor", context.aws_request_id)
    print(f"[FILE_PROCESSOR] Logger created: {logger}")

    print(f"[FILE_PROCESSOR] About to execute: logger.info with message 'File processor invoked'")
    logger.info("File processor invoked", event=event)
    print("[FILE_PROCESSOR] Result: logger.info executed successfully")

    print("[FILE_PROCESSOR] About to execute: action = event.get('action', 'unknown')")
    action = event.get('action', 'unknown')
    print(f"[FILE_PROCESSOR] Result: action = {action}")

    try:
        print(f"[FILE_PROCESSOR] About to execute: check if action == 'extract_metadata'")
        if action == 'extract_metadata':
            print(f"[FILE_PROCESSOR] About to execute: return extract_metadata(event, logger)")
            result = extract_metadata(event, logger)
            print(f"[FILE_PROCESSOR] Result: extract_metadata returned = {result}")
            return result

        elif action == 'match_period':
            print(f"[FILE_PROCESSOR] About to execute: check if action == 'match_period'")
            print(f"[FILE_PROCESSOR] About to execute: return match_period(event, logger)")
            result = match_period(event, logger)
            print(f"[FILE_PROCESSOR] Result: match_period returned = {result}")
            return result

        elif action == 'check_duplicates':
            print(f"[FILE_PROCESSOR] About to execute: check if action == 'check_duplicates'")
            print(f"[FILE_PROCESSOR] About to execute: return check_duplicates(event, logger)")
            result = check_duplicates(event, logger)
            print(f"[FILE_PROCESSOR] Result: check_duplicates returned = {result}")
            return result

        elif action == 'supersede_existing':
            print(f"[FILE_PROCESSOR] About to execute: return supersede_existing(event, logger)")
            result = supersede_existing(event, logger)
            print(f"[FILE_PROCESSOR] Result: supersede_existing returned = {result}")
            return result

        elif action == 'parse_records':
            print(f"[FILE_PROCESSOR] About to execute: check if action == 'parse_records'")
            print(f"[FILE_PROCESSOR] About to execute: return parse_records(event, logger)")
            result = parse_records(event, logger)
            print(f"[FILE_PROCESSOR] Result: parse_records returned = {result}")
            return result

        elif action == 'import_records':
            print(f"[FILE_PROCESSOR] About to execute: check if action == 'import_records'")
            print(f"[FILE_PROCESSOR] About to execute: return import_records(event, logger)")
            result = import_records(event, logger)
            print(f"[FILE_PROCESSOR] Result: import_records returned = {result}")
            return result

        elif action == 'mark_complete':
            print(f"[FILE_PROCESSOR] About to execute: check if action == 'mark_complete'")
            print(f"[FILE_PROCESSOR] About to execute: return mark_complete(event, logger)")
            result = mark_complete(event, logger)
            print(f"[FILE_PROCESSOR] Result: mark_complete returned = {result}")
            return result

        elif action == 'mark_error':
            print(f"[FILE_PROCESSOR] About to execute: check if action == 'mark_error'")
            print(f"[FILE_PROCESSOR] About to execute: return mark_error(event, logger)")
            result = mark_error(event, logger)
            print(f"[FILE_PROCESSOR] Result: mark_error returned = {result}")
            return result

        elif action == 'mark_failed':
            print(f"[FILE_PROCESSOR] About to execute: check if action == 'mark_failed'")
            print(f"[FILE_PROCESSOR] About to execute: return mark_failed(event, logger)")
            result = mark_failed(event, logger)
            print(f"[FILE_PROCESSOR] Result: mark_failed returned = {result}")
            return result

        else:
            print(f"[FILE_PROCESSOR] About to execute: raise ValueError for unknown action: {action}")
            raise ValueError(f"Unknown action: {action}")

    except Exception as e:
        print(f"[FILE_PROCESSOR] About to execute: logger.error for exception = {e}")
        logger.error("File processor error", error=str(e), action=action)
        print("[FILE_PROCESSOR] Result: logger.error executed successfully")
        print(f"[FILE_PROCESSOR] About to execute: raise exception = {e}")
        raise


def extract_metadata(event: dict, logger: StructuredLogger) -> dict:
    """
    Extract metadata from uploaded file
    Step 1 of Step Functions workflow
    """
    print(f"[FILE_PROCESSOR] About to execute: extract_metadata with event = {event}")

    print("[FILE_PROCESSOR] About to execute: file_id = event['file_id']")
    file_id = event['file_id']
    print(f"[FILE_PROCESSOR] Result: file_id = {file_id}")

    print(f"[FILE_PROCESSOR] About to execute: logger.info 'Extracting metadata' for file_id = {file_id}")
    logger.info("Extracting metadata", file_id=file_id)
    print("[FILE_PROCESSOR] Result: logger.info executed successfully")

    # Get file metadata from DynamoDB
    print(f"[FILE_PROCESSOR] About to execute: dynamodb_client.get_file_metadata({file_id})")
    file_metadata = dynamodb_client.get_file_metadata(file_id)
    print(f"[FILE_PROCESSOR] Result: file_metadata = {file_metadata}")

    print(f"[FILE_PROCESSOR] About to execute: check if not file_metadata")
    if not file_metadata:
        print(f"[FILE_PROCESSOR] About to execute: raise ValueError for file {file_id} not found")
        raise ValueError(f"File {file_id} not found")

    # Download file from S3 to temp location
    print("[FILE_PROCESSOR] About to execute: s3_bucket = file_metadata['S3Bucket']")
    s3_bucket = file_metadata['S3Bucket']
    print(f"[FILE_PROCESSOR] Result: s3_bucket = {s3_bucket}")

    print("[FILE_PROCESSOR] About to execute: s3_key = file_metadata['S3Key']")
    s3_key = file_metadata['S3Key']
    print(f"[FILE_PROCESSOR] Result: s3_key = {s3_key}")

    print("[FILE_PROCESSOR] About to execute: tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx')")
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx')
    print(f"[FILE_PROCESSOR] Result: temp_file = {temp_file.name}")

    print(f"[FILE_PROCESSOR] About to execute: s3_client.download_file({s3_bucket}, {s3_key}, {temp_file.name})")
    s3_client.download_file(s3_bucket, s3_key, temp_file.name)
    print(f"[FILE_PROCESSOR] Result: file downloaded to {temp_file.name}")

    # Parse Excel file
    print(f"[FILE_PROCESSOR] About to execute: parser = PayFileParser({temp_file.name})")
    parser = PayFileParser(temp_file.name)
    print(f"[FILE_PROCESSOR] Result: parser created = {parser}")

    print("[FILE_PROCESSOR] About to execute: metadata = parser.extract_metadata()")
    metadata = parser.extract_metadata()
    print(f"[FILE_PROCESSOR] Result: metadata = {metadata}")

    print("[FILE_PROCESSOR] About to execute: parser.close()")
    parser.close()
    print("[FILE_PROCESSOR] Result: parser closed")

    # Clean up temp file
    print(f"[FILE_PROCESSOR] About to execute: os.unlink({temp_file.name})")
    os.unlink(temp_file.name)
    print(f"[FILE_PROCESSOR] Result: temp file {temp_file.name} deleted")

    print(f"[FILE_PROCESSOR] About to execute: logger.info 'Metadata extracted' with metadata = {metadata}")
    logger.info("Metadata extracted", metadata=metadata)
    print("[FILE_PROCESSOR] Result: logger.info executed successfully")

    print("[FILE_PROCESSOR] About to execute: build return dict with file_id, umbrella_code, submission_date, filename")
    result = {
        'file_id': file_id,
        'umbrella_code': metadata['umbrella_code'],
        'submission_date': metadata['submission_date'],
        'filename': metadata['filename']
    }
    print(f"[FILE_PROCESSOR] Result: returning = {result}")
    return result


def match_period(event: dict, logger: StructuredLogger) -> dict:
    """
    Match file to pay period
    Step 2 of Step Functions workflow
    """
    print(f"[FILE_PROCESSOR] About to execute: match_period with event = {event}")

    print("[FILE_PROCESSOR] About to execute: file_id = event['file_id']")
    file_id = event['file_id']
    print(f"[FILE_PROCESSOR] Result: file_id = {file_id}")

    print("[FILE_PROCESSOR] About to execute: metadata = event.get('metadata_result', {})")
    metadata = event.get('metadata_result', {})
    print(f"[FILE_PROCESSOR] Result: metadata = {metadata}")

    print(f"[FILE_PROCESSOR] About to execute: logger.info 'Matching period' for file_id = {file_id}")
    logger.info("Matching period", file_id=file_id, metadata=metadata)
    print("[FILE_PROCESSOR] Result: logger.info executed successfully")

    # Get umbrella company by code
    print("[FILE_PROCESSOR] About to execute: umbrella_code = metadata.get('umbrella_code')")
    umbrella_code = metadata.get('umbrella_code')
    print(f"[FILE_PROCESSOR] Result: umbrella_code = {umbrella_code}")

    print(f"[FILE_PROCESSOR] About to execute: check if not umbrella_code")
    if not umbrella_code:
        print("[FILE_PROCESSOR] About to execute: raise ValueError for missing umbrella company")
        raise ValueError("Could not determine umbrella company from filename")

    # Query DynamoDB for umbrella
    print(f"[FILE_PROCESSOR] About to execute: dynamodb_client.table.query for umbrella_code = {umbrella_code}")
    response = dynamodb_client.table.query(
        IndexName='GSI2',
        KeyConditionExpression='GSI2PK = :pk',
        ExpressionAttributeValues={':pk': f'UMBRELLA_CODE#{umbrella_code}'}
    )
    print(f"[FILE_PROCESSOR] Result: query response = {response}")

    print("[FILE_PROCESSOR] About to execute: check if not response.get('Items')")
    if not response.get('Items'):
        print(f"[FILE_PROCESSOR] About to execute: raise ValueError for umbrella '{umbrella_code}' not found")
        raise ValueError(f"Umbrella company '{umbrella_code}' not found")

    print("[FILE_PROCESSOR] About to execute: umbrella = response['Items'][0]")
    umbrella = response['Items'][0]
    print(f"[FILE_PROCESSOR] Result: umbrella = {umbrella}")

    print("[FILE_PROCESSOR] About to execute: umbrella_id = umbrella['UmbrellaID']")
    umbrella_id = umbrella['UmbrellaID']
    print(f"[FILE_PROCESSOR] Result: umbrella_id = {umbrella_id}")

    # Determine period from submission date
    print("[FILE_PROCESSOR] About to execute: submission_date = metadata.get('submission_date')")
    submission_date = metadata.get('submission_date')
    print(f"[FILE_PROCESSOR] Result: submission_date = {submission_date}")

    print(f"[FILE_PROCESSOR] About to execute: check if not submission_date")
    if not submission_date:
        print("[FILE_PROCESSOR] About to execute: raise ValueError for missing submission date")
        raise ValueError("Could not determine submission date from filename")

    # Find matching period by date-based lookup
    # Query all periods and find the one where submission_date falls within StartDate/EndDate range
    print("[FILE_PROCESSOR] About to execute: Scan table for all PERIOD entities")
    response = dynamodb_client.table.scan(
        FilterExpression='begins_with(PK, :pk_prefix) AND SK = :sk',
        ExpressionAttributeValues={
            ':pk_prefix': 'PERIOD#',
            ':sk': 'PROFILE'
        }
    )
    print(f"[FILE_PROCESSOR] Result: scan response with {len(response.get('Items', []))} periods found")

    print("[FILE_PROCESSOR] About to execute: Parse submission_date to compare with period date ranges")
    try:
        print(f"[FILE_PROCESSOR] About to execute: datetime.strptime({submission_date}, '%d%m%Y')")
        submission_dt = datetime.strptime(submission_date, '%d%m%Y')
        print(f"[FILE_PROCESSOR] Result: submission_dt = {submission_dt}")

        print("[FILE_PROCESSOR] About to execute: Format submission_dt to YYYY-MM-DD for comparison")
        submission_date_formatted = submission_dt.strftime('%Y-%m-%d')
        print(f"[FILE_PROCESSOR] Result: submission_date_formatted = {submission_date_formatted}")
    except ValueError as e:
        print(f"[FILE_PROCESSOR] About to execute: raise ValueError for invalid submission date format: {e}")
        raise ValueError(f"Invalid submission date format '{submission_date}'. Expected DDMMYYYY format. Error: {e}")

    print("[FILE_PROCESSOR] About to execute: Iterate through periods to find matching period")
    period = None
    period_number = None

    print(f"[FILE_PROCESSOR] About to execute: Loop through {len(response.get('Items', []))} periods")
    for period_item in response.get('Items', []):
        print(f"[FILE_PROCESSOR] About to execute: Check period {period_item.get('PeriodNumber')}")

        work_start_date = period_item.get('WorkStartDate')
        print(f"[FILE_PROCESSOR] Result: work_start_date = {work_start_date}")

        work_end_date = period_item.get('WorkEndDate')
        print(f"[FILE_PROCESSOR] Result: work_end_date = {work_end_date}")

        print(f"[FILE_PROCESSOR] About to execute: Check if {submission_date_formatted} falls between {work_start_date} and {work_end_date}")

        if work_start_date and work_end_date:
            print(f"[FILE_PROCESSOR] About to execute: Compare dates: {work_start_date} <= {submission_date_formatted} <= {work_end_date}")

            if work_start_date <= submission_date_formatted <= work_end_date:
                print(f"[FILE_PROCESSOR] Result: Match found! submission_date falls within period {period_item.get('PeriodNumber')}")
                period = period_item
                period_number = period_item.get('PeriodNumber')
                print(f"[FILE_PROCESSOR] Result: period_number = {period_number}, period = {period}")
                break
            else:
                print(f"[FILE_PROCESSOR] Result: No match - submission_date outside range")
        else:
            print(f"[FILE_PROCESSOR] Result: Period {period_item.get('PeriodNumber')} missing WorkStartDate or WorkEndDate, skipping")

    print("[FILE_PROCESSOR] About to execute: Check if matching period was found")
    if not period or period_number is None:
        print(f"[FILE_PROCESSOR] About to execute: raise ValueError - no period found for submission_date {submission_date_formatted}")
        raise ValueError(f"No pay period found for submission date {submission_date_formatted}. Please verify the submission date falls within a valid pay period.")

    print(f"[FILE_PROCESSOR] Result: Successfully matched to period {period_number}")

    print(f"[FILE_PROCESSOR] About to execute: logger.info 'Period matched' for umbrella_id = {umbrella_id}, period_number = {period_number}")
    logger.info("Period matched", umbrella_id=umbrella_id, period_number=period_number)
    print("[FILE_PROCESSOR] Result: logger.info executed successfully")

    print("[FILE_PROCESSOR] About to execute: build return dict with file_id, umbrella_id, umbrella_code, period_id, period_data")
    result = {
        'file_id': file_id,
        'umbrella_id': umbrella_id,
        'umbrella_code': umbrella_code,
        'period_id': str(period_number),
        'period_data': period
    }
    print(f"[FILE_PROCESSOR] Result: returning = {result}")
    return result


def check_duplicates(event: dict, logger: StructuredLogger) -> dict:
    """
    Check for duplicate file (same umbrella + period)
    Step 3 of Step Functions workflow
    Gemini improvement #4: Automatic supersede
    """
    print(f"[FILE_PROCESSOR] About to execute: check_duplicates with event = {event}")

    print("[FILE_PROCESSOR] About to execute: file_id = event['file_id']")
    file_id = event['file_id']
    print(f"[FILE_PROCESSOR] Result: file_id = {file_id}")

    print("[FILE_PROCESSOR] About to execute: umbrella_id = event['umbrella_id']")
    umbrella_id = event['umbrella_id']
    print(f"[FILE_PROCESSOR] Result: umbrella_id = {umbrella_id}")

    print("[FILE_PROCESSOR] About to execute: period_id = event['period_id']")
    period_id = event['period_id']
    print(f"[FILE_PROCESSOR] Result: period_id = {period_id}")

    print(f"[FILE_PROCESSOR] About to execute: logger.info 'Checking duplicates' for file_id = {file_id}, umbrella_id = {umbrella_id}, period_id = {period_id}")
    logger.info("Checking duplicates", file_id=file_id, umbrella_id=umbrella_id, period_id=period_id)
    print("[FILE_PROCESSOR] Result: logger.info executed successfully")

    # Query GSI1 for existing files with same umbrella + period
    print(f"[FILE_PROCESSOR] About to execute: dynamodb_client.table.query for period_id = {period_id}, umbrella_id = {umbrella_id}")
    response = dynamodb_client.table.query(
        IndexName='GSI1',
        KeyConditionExpression='GSI1PK = :pk',
        FilterExpression='IsCurrentVersion = :current AND #status <> :deleted',
        ExpressionAttributeNames={'#status': 'Status'},
        ExpressionAttributeValues={
            ':pk': f'PERIOD#{period_id}#UMBRELLA#{umbrella_id}',
            ':current': True,
            ':deleted': 'DELETED'
        }
    )
    print(f"[FILE_PROCESSOR] Result: query response = {response}")

    print(f"[FILE_PROCESSOR] About to execute: filter existing_files from response items where FileID != {file_id}")
    existing_files = [item for item in response.get('Items', []) if item['FileID'] != file_id]
    print(f"[FILE_PROCESSOR] Result: existing_files = {existing_files}")

    print(f"[FILE_PROCESSOR] About to execute: check if existing_files")
    if existing_files:
        print(f"[FILE_PROCESSOR] About to execute: logger.info 'Duplicate found' for existing_file_id = {existing_files[0]['FileID']}")
        logger.info("Duplicate found - will supersede", existing_file_id=existing_files[0]['FileID'])
        print("[FILE_PROCESSOR] Result: logger.info executed successfully")

        print("[FILE_PROCESSOR] About to execute: build return dict with duplicate_found = True")
        result = {
            'file_id': file_id,
            'duplicate_found': True,
            'existing_file_id': existing_files[0]['FileID']
        }
        print(f"[FILE_PROCESSOR] Result: returning = {result}")
        return result

    print("[FILE_PROCESSOR] About to execute: logger.info 'No duplicates found'")
    logger.info("No duplicates found")
    print("[FILE_PROCESSOR] Result: logger.info executed successfully")

    print("[FILE_PROCESSOR] About to execute: build return dict with duplicate_found = False")
    result = {
        'file_id': file_id,
        'duplicate_found': False
    }
    print(f"[FILE_PROCESSOR] Result: returning = {result}")
    return result


def supersede_existing(event: dict, logger: StructuredLogger) -> dict:
    """
    Automatically supersede existing file
    Gemini improvement #4: No user prompt, automatic supersede
    """
    print(f"[FILE_PROCESSOR] About to execute: supersede_existing with event = {event}")

    print("[FILE_PROCESSOR] About to execute: file_id = event['file_id']")
    file_id = event['file_id']
    print(f"[FILE_PROCESSOR] Result: file_id = {file_id}")

    print("[FILE_PROCESSOR] About to execute: existing_file_id = event['existing_file_id']")
    existing_file_id = event['existing_file_id']
    print(f"[FILE_PROCESSOR] Result: existing_file_id = {existing_file_id}")

    print(f"[FILE_PROCESSOR] About to execute: logger.info 'Superseding existing file' for new_file = {file_id}, old_file = {existing_file_id}")
    logger.info("Superseding existing file", new_file=file_id, old_file=existing_file_id)
    print("[FILE_PROCESSOR] Result: logger.info executed successfully")

    # Mark old file as SUPERSEDED
    print(f"[FILE_PROCESSOR] About to execute: datetime.utcnow().isoformat() + 'Z'")
    timestamp = datetime.utcnow().isoformat() + 'Z'
    print(f"[FILE_PROCESSOR] Result: timestamp = {timestamp}")

    print(f"[FILE_PROCESSOR] About to execute: dynamodb_client.table.update_item to mark file {existing_file_id} as SUPERSEDED")
    dynamodb_client.table.update_item(
        Key={'PK': f'FILE#{existing_file_id}', 'SK': 'METADATA'},
        UpdateExpression='SET #status = :status, IsCurrentVersion = :current, SupersededAt = :time, SupersededBy = :by',
        ExpressionAttributeNames={'#status': 'Status'},
        ExpressionAttributeValues={
            ':status': 'SUPERSEDED',
            ':current': False,
            ':time': timestamp,
            ':by': file_id
        }
    )
    print(f"[FILE_PROCESSOR] Result: file {existing_file_id} marked as SUPERSEDED")

    # Mark old pay records as inactive
    # Query all records for old file
    print(f"[FILE_PROCESSOR] About to execute: dynamodb_client.table.query for records of file {existing_file_id}")
    response = dynamodb_client.table.query(
        KeyConditionExpression='PK = :pk AND begins_with(SK, :sk)',
        ExpressionAttributeValues={
            ':pk': f'FILE#{existing_file_id}',
            ':sk': 'RECORD#'
        }
    )
    print(f"[FILE_PROCESSOR] Result: query response with {len(response.get('Items', []))} records")

    # Batch update records
    print(f"[FILE_PROCESSOR] About to execute: dynamodb_client.table.batch_writer()")
    with dynamodb_client.table.batch_writer() as batch:
        print(f"[FILE_PROCESSOR] Result: batch_writer context entered")
        print(f"[FILE_PROCESSOR] About to execute: iterate through {len(response.get('Items', []))} records")
        for record in response.get('Items', []):
            print(f"[FILE_PROCESSOR] About to execute: set record['IsActive'] = False for record SK = {record.get('SK')}")
            record['IsActive'] = False
            print(f"[FILE_PROCESSOR] Result: record['IsActive'] = {record['IsActive']}")

            print(f"[FILE_PROCESSOR] About to execute: batch.put_item(Item=record)")
            batch.put_item(Item=record)
            print(f"[FILE_PROCESSOR] Result: record put to batch")

    print(f"[FILE_PROCESSOR] Result: batch_writer context exited, all records updated")

    print(f"[FILE_PROCESSOR] About to execute: logger.info 'Supersede complete' with records_deactivated = {len(response.get('Items', []))}")
    logger.info("Supersede complete", records_deactivated=len(response.get('Items', [])))
    print("[FILE_PROCESSOR] Result: logger.info executed successfully")

    print("[FILE_PROCESSOR] About to execute: build return dict with superseded_file_id and records_deactivated")
    result = {
        'file_id': file_id,
        'superseded_file_id': existing_file_id,
        'records_deactivated': len(response.get('Items', []))
    }
    print(f"[FILE_PROCESSOR] Result: returning = {result}")
    return result


def parse_records(event: dict, logger: StructuredLogger) -> dict:
    """
    Parse Excel file into records
    Step 4 of Step Functions workflow
    """
    print(f"[FILE_PROCESSOR] About to execute: parse_records with event = {event}")

    print("[FILE_PROCESSOR] About to execute: file_id = event['file_id']")
    file_id = event['file_id']
    print(f"[FILE_PROCESSOR] Result: file_id = {file_id}")

    print("[FILE_PROCESSOR] About to execute: umbrella_id = event['umbrella_id']")
    umbrella_id = event['umbrella_id']
    print(f"[FILE_PROCESSOR] Result: umbrella_id = {umbrella_id}")

    print("[FILE_PROCESSOR] About to execute: period_id = event['period_id']")
    period_id = event['period_id']
    print(f"[FILE_PROCESSOR] Result: period_id = {period_id}")

    print(f"[FILE_PROCESSOR] About to execute: logger.info 'Parsing records' for file_id = {file_id}")
    logger.info("Parsing records", file_id=file_id)
    print("[FILE_PROCESSOR] Result: logger.info executed successfully")

    # Get file metadata
    print(f"[FILE_PROCESSOR] About to execute: dynamodb_client.get_file_metadata({file_id})")
    file_metadata = dynamodb_client.get_file_metadata(file_id)
    print(f"[FILE_PROCESSOR] Result: file_metadata = {file_metadata}")

    # Download file
    print("[FILE_PROCESSOR] About to execute: s3_bucket = file_metadata['S3Bucket']")
    s3_bucket = file_metadata['S3Bucket']
    print(f"[FILE_PROCESSOR] Result: s3_bucket = {s3_bucket}")

    print("[FILE_PROCESSOR] About to execute: s3_key = file_metadata['S3Key']")
    s3_key = file_metadata['S3Key']
    print(f"[FILE_PROCESSOR] Result: s3_key = {s3_key}")

    print("[FILE_PROCESSOR] About to execute: tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx')")
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx')
    print(f"[FILE_PROCESSOR] Result: temp_file = {temp_file.name}")

    print(f"[FILE_PROCESSOR] About to execute: s3_client.download_file({s3_bucket}, {s3_key}, {temp_file.name})")
    s3_client.download_file(s3_bucket, s3_key, temp_file.name)
    print(f"[FILE_PROCESSOR] Result: file downloaded to {temp_file.name}")

    # Parse records
    print(f"[FILE_PROCESSOR] About to execute: parser = PayFileParser({temp_file.name})")
    parser = PayFileParser(temp_file.name)
    print(f"[FILE_PROCESSOR] Result: parser created = {parser}")

    print("[FILE_PROCESSOR] About to execute: records = parser.parse_records()")
    records = parser.parse_records()
    print(f"[FILE_PROCESSOR] Result: records parsed, count = {len(records)}")

    print("[FILE_PROCESSOR] About to execute: parser.close()")
    parser.close()
    print("[FILE_PROCESSOR] Result: parser closed")

    # Clean up
    print(f"[FILE_PROCESSOR] About to execute: os.unlink({temp_file.name})")
    os.unlink(temp_file.name)
    print(f"[FILE_PROCESSOR] Result: temp file {temp_file.name} deleted")

    print(f"[FILE_PROCESSOR] About to execute: logger.info 'Records parsed' with record_count = {len(records)}")
    logger.info("Records parsed", record_count=len(records))
    print("[FILE_PROCESSOR] Result: logger.info executed successfully")

    # Update file metadata with record count
    print(f"[FILE_PROCESSOR] About to execute: datetime.utcnow().isoformat() + 'Z'")
    timestamp = datetime.utcnow().isoformat() + 'Z'
    print(f"[FILE_PROCESSOR] Result: timestamp = {timestamp}")

    print(f"[FILE_PROCESSOR] About to execute: dynamodb_client.update_file_status({file_id}, 'PROCESSING', TotalRecords={len(records)}, ProcessingStartedAt={timestamp})")
    dynamodb_client.update_file_status(
        file_id,
        'PROCESSING',
        TotalRecords=len(records),
        ProcessingStartedAt=timestamp
    )
    print(f"[FILE_PROCESSOR] Result: file status updated to PROCESSING")

    print("[FILE_PROCESSOR] About to execute: build return dict with file_id, umbrella_id, period_id, records, record_count")
    result = {
        'file_id': file_id,
        'umbrella_id': umbrella_id,
        'period_id': period_id,
        'records': records,
        'record_count': len(records)
    }
    print(f"[FILE_PROCESSOR] Result: returning dict with record_count = {len(records)}")
    return result


def import_records(event: dict, logger: StructuredLogger) -> dict:
    """
    Import validated records to DynamoDB
    Step 5 of Step Functions workflow
    """
    print(f"[FILE_PROCESSOR] About to execute: import_records with event keys = {event.keys()}")

    print("[FILE_PROCESSOR] About to execute: file_id = event['file_id']")
    file_id = event['file_id']
    print(f"[FILE_PROCESSOR] Result: file_id = {file_id}")

    print("[FILE_PROCESSOR] About to execute: validated_records = event.get('validated_records', [])")
    validated_records = event.get('validated_records', [])
    print(f"[FILE_PROCESSOR] Result: validated_records count = {len(validated_records)}")

    print("[FILE_PROCESSOR] About to execute: has_warnings = event.get('has_warnings', False)")
    has_warnings = event.get('has_warnings', False)
    print(f"[FILE_PROCESSOR] Result: has_warnings = {has_warnings}")

    print(f"[FILE_PROCESSOR] About to execute: logger.info 'Importing records' for file_id = {file_id}, record_count = {len(validated_records)}")
    logger.info("Importing records", file_id=file_id, record_count=len(validated_records))
    print("[FILE_PROCESSOR] Result: logger.info executed successfully")

    # Batch write records
    print("[FILE_PROCESSOR] About to execute: records_to_write = []")
    records_to_write = []
    print(f"[FILE_PROCESSOR] Result: records_to_write initialized = {records_to_write}")

    print(f"[FILE_PROCESSOR] About to execute: enumerate through {len(validated_records)} validated_records starting from 1")
    for idx, record_data in enumerate(validated_records, start=1):
        print(f"[FILE_PROCESSOR] About to execute: process record idx = {idx}")

        print(f"[FILE_PROCESSOR] About to execute: record = record_data['record']")
        record = record_data['record']
        print(f"[FILE_PROCESSOR] Result: record extracted from record_data")

        print(f"[FILE_PROCESSOR] About to execute: contractor_id = record_data.get('contractor_id')")
        contractor_id = record_data.get('contractor_id')
        print(f"[FILE_PROCESSOR] Result: contractor_id = {contractor_id}")

        print(f"[FILE_PROCESSOR] About to execute: association_id = record_data.get('association_id')")
        association_id = record_data.get('association_id')
        print(f"[FILE_PROCESSOR] Result: association_id = {association_id}")

        print(f"[FILE_PROCESSOR] About to execute: record_id = str(uuid.uuid4())")
        record_id = str(uuid.uuid4())
        print(f"[FILE_PROCESSOR] Result: record_id = {record_id}")

        print(f"[FILE_PROCESSOR] About to execute: datetime.utcnow().isoformat() + 'Z'")
        timestamp = datetime.utcnow().isoformat() + 'Z'
        print(f"[FILE_PROCESSOR] Result: timestamp = {timestamp}")

        print(f"[FILE_PROCESSOR] About to execute: build item dict for record {idx}")
        item = {
            'PK': f'FILE#{file_id}',
            'SK': f'RECORD#{idx:03d}',
            'EntityType': 'PayRecord',
            'RecordID': record_id,
            'FileID': file_id,
            'ContractorID': contractor_id,
            'UmbrellaID': record_data.get('umbrella_id'),
            'PeriodID': record_data.get('period_id'),
            'AssociationID': association_id,
            'EmployeeID': record['employee_id'],
            'UnitDays': Decimal(str(record['unit_days'])),
            'DayRate': Decimal(str(record['day_rate'])),
            'Amount': Decimal(str(record['amount'])),
            'VATAmount': Decimal(str(record['vat_amount'])),
            'GrossAmount': Decimal(str(record['gross_amount'])),
            'TotalHours': Decimal(str(record.get('total_hours', 0))),
            'RecordType': record['record_type'],
            'Notes': record.get('notes', ''),
            'IsActive': True,
            'CreatedAt': timestamp,
            'GSI1PK': f'CONTRACTOR#{contractor_id}',
            'GSI1SK': f'RECORD#{timestamp}',
            'GSI2PK': f'PERIOD#{record_data.get("period_id")}',
            'GSI2SK': f'CONTRACTOR#{contractor_id}'
        }
        print(f"[FILE_PROCESSOR] Result: item dict built for record {idx}")

        print(f"[FILE_PROCESSOR] About to execute: records_to_write.append(item)")
        records_to_write.append(item)
        print(f"[FILE_PROCESSOR] Result: item appended, records_to_write length = {len(records_to_write)}")

    # Write in batches
    print(f"[FILE_PROCESSOR] About to execute: dynamodb_client.batch_write_pay_records with {len(records_to_write)} records")
    dynamodb_client.batch_write_pay_records(records_to_write)
    print(f"[FILE_PROCESSOR] Result: batch_write_pay_records completed for {len(records_to_write)} records")

    print(f"[FILE_PROCESSOR] About to execute: logger.info 'Records imported' with count = {len(records_to_write)}")
    logger.info("Records imported", count=len(records_to_write))
    print("[FILE_PROCESSOR] Result: logger.info executed successfully")

    print("[FILE_PROCESSOR] About to execute: build return dict with records_imported and has_warnings")
    result = {
        'file_id': file_id,
        'records_imported': len(records_to_write),
        'has_warnings': has_warnings
    }
    print(f"[FILE_PROCESSOR] Result: returning = {result}")
    return result


def mark_complete(event: dict, logger: StructuredLogger) -> dict:
    """
    Mark file processing as complete
    Final step of successful workflow
    """
    print(f"[FILE_PROCESSOR] About to execute: mark_complete with event keys = {event.keys()}")

    print("[FILE_PROCESSOR] About to execute: file_id = event['file_id']")
    file_id = event['file_id']
    print(f"[FILE_PROCESSOR] Result: file_id = {file_id}")

    print("[FILE_PROCESSOR] About to execute: import_result = event.get('import_result', {})")
    import_result = event.get('import_result', {})
    print(f"[FILE_PROCESSOR] Result: import_result = {import_result}")

    print("[FILE_PROCESSOR] About to execute: has_warnings = event.get('has_warnings', False)")
    has_warnings = event.get('has_warnings', False)
    print(f"[FILE_PROCESSOR] Result: has_warnings = {has_warnings}")

    print("[FILE_PROCESSOR] About to execute: was_supersede = event.get('was_supersede', False)")
    was_supersede = event.get('was_supersede', False)
    print(f"[FILE_PROCESSOR] Result: was_supersede = {was_supersede}")

    print("[FILE_PROCESSOR] About to execute: records_imported = import_result.get('records_imported', 0)")
    records_imported = import_result.get('records_imported', 0)
    print(f"[FILE_PROCESSOR] Result: records_imported = {records_imported}")

    # Determine status
    print(f"[FILE_PROCESSOR] About to execute: determine status based on has_warnings = {has_warnings}")
    status = 'COMPLETED_WITH_WARNINGS' if has_warnings else 'COMPLETED'
    print(f"[FILE_PROCESSOR] Result: status = {status}")

    print(f"[FILE_PROCESSOR] About to execute: logger.info 'Marking complete' for file_id = {file_id}, status = {status}")
    logger.info("Marking complete", file_id=file_id, status=status)
    print("[FILE_PROCESSOR] Result: logger.info executed successfully")

    print(f"[FILE_PROCESSOR] About to execute: datetime.utcnow().isoformat() + 'Z'")
    timestamp = datetime.utcnow().isoformat() + 'Z'
    print(f"[FILE_PROCESSOR] Result: timestamp = {timestamp}")

    print(f"[FILE_PROCESSOR] About to execute: dynamodb_client.update_file_status({file_id}, {status}, ValidRecords={records_imported}, ProcessingCompletedAt={timestamp})")
    dynamodb_client.update_file_status(
        file_id,
        status,
        ValidRecords=records_imported,
        ProcessingCompletedAt=timestamp
    )
    print(f"[FILE_PROCESSOR] Result: file status updated to {status}")

    print("[FILE_PROCESSOR] About to execute: build return dict with file_id, status, records_imported, message")
    result = {
        'file_id': file_id,
        'status': status,
        'records_imported': records_imported,
        'message': 'File processing complete'
    }
    print(f"[FILE_PROCESSOR] Result: returning = {result}")
    return result


def mark_error(event: dict, logger: StructuredLogger) -> dict:
    """
    Mark file as ERROR due to critical validation errors
    Gemini improvement #2: Errors block import
    """
    print(f"[FILE_PROCESSOR] About to execute: mark_error with event keys = {event.keys()}")

    print("[FILE_PROCESSOR] About to execute: file_id = event['file_id']")
    file_id = event['file_id']
    print(f"[FILE_PROCESSOR] Result: file_id = {file_id}")

    print("[FILE_PROCESSOR] About to execute: validation_errors = event.get('validation_errors', [])")
    validation_errors = event.get('validation_errors', [])
    print(f"[FILE_PROCESSOR] Result: validation_errors count = {len(validation_errors)}")

    print(f"[FILE_PROCESSOR] About to execute: logger.error 'Marking file as ERROR' for file_id = {file_id}, error_count = {len(validation_errors)}")
    logger.error("Marking file as ERROR", file_id=file_id, error_count=len(validation_errors))
    print("[FILE_PROCESSOR] Result: logger.error executed successfully")

    print(f"[FILE_PROCESSOR] About to execute: datetime.utcnow().isoformat() + 'Z'")
    timestamp = datetime.utcnow().isoformat() + 'Z'
    print(f"[FILE_PROCESSOR] Result: timestamp = {timestamp}")

    print(f"[FILE_PROCESSOR] About to execute: dynamodb_client.update_file_status({file_id}, 'ERROR', ErrorRecords={len(validation_errors)}, ValidRecords=0, TotalRecords=0, ProcessingCompletedAt={timestamp})")
    dynamodb_client.update_file_status(
        file_id,
        'ERROR',
        ErrorRecords=len(validation_errors),
        ValidRecords=0,
        TotalRecords=0,
        ProcessingCompletedAt=timestamp
    )
    print(f"[FILE_PROCESSOR] Result: file status updated to ERROR")

    print("[FILE_PROCESSOR] About to execute: build return dict with file_id, status='ERROR', message")
    result = {
        'file_id': file_id,
        'status': 'ERROR',
        'message': 'File rejected due to critical validation errors'
    }
    print(f"[FILE_PROCESSOR] Result: returning = {result}")
    return result


def mark_failed(event: dict, logger: StructuredLogger) -> dict:
    """
    Mark file processing as failed due to system error
    """
    print(f"[FILE_PROCESSOR] About to execute: mark_failed with event keys = {event.keys()}")

    print("[FILE_PROCESSOR] About to execute: file_id = event['file_id']")
    file_id = event['file_id']
    print(f"[FILE_PROCESSOR] Result: file_id = {file_id}")

    print("[FILE_PROCESSOR] About to execute: error = event.get('error', {})")
    error = event.get('error', {})
    print(f"[FILE_PROCESSOR] Result: error = {error}")

    print(f"[FILE_PROCESSOR] About to execute: logger.error 'Processing failed' for file_id = {file_id}, error = {error}")
    logger.error("Processing failed", file_id=file_id, error=error)
    print("[FILE_PROCESSOR] Result: logger.error executed successfully")

    print(f"[FILE_PROCESSOR] About to execute: datetime.utcnow().isoformat() + 'Z'")
    timestamp = datetime.utcnow().isoformat() + 'Z'
    print(f"[FILE_PROCESSOR] Result: timestamp = {timestamp}")

    print(f"[FILE_PROCESSOR] About to execute: dynamodb_client.update_file_status({file_id}, 'FAILED', ProcessingCompletedAt={timestamp})")
    dynamodb_client.update_file_status(
        file_id,
        'FAILED',
        ProcessingCompletedAt=timestamp
    )
    print(f"[FILE_PROCESSOR] Result: file status updated to FAILED")

    print("[FILE_PROCESSOR] About to execute: build return dict with file_id, status='FAILED', message")
    result = {
        'file_id': file_id,
        'status': 'FAILED',
        'message': 'File processing failed'
    }
    print(f"[FILE_PROCESSOR] Result: returning = {result}")
    return result
