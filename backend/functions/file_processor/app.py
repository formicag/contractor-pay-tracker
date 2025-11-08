print("[FILE_PROCESSOR] Module load started")
"""
print("[FILE_PROCESSOR] File Processor Lambda Function")
File Processor Lambda Function
print("[FILE_PROCESSOR] Processes Excel files, validates contractor data, and imports to DynamoDB")
Processes Excel files, validates contractor data, and imports to DynamoDB

print("[FILE_PROCESSOR] Implements Gemini improvements:")
Implements Gemini improvements:
print("[FILE_PROCESSOR] - Automatic supersede (improvement #4)")
- Automatic supersede (improvement #4)
print("[FILE_PROCESSOR] - Many-to-many contractor-umbrella validation (improvement #1)")
- Many-to-many contractor-umbrella validation (improvement #1)
print("[FILE_PROCESSOR] - Error vs Warning handling (improvement #2)")
- Error vs Warning handling (improvement #2)
"""

print("[FILE_PROCESSOR] import json")
import json
print("[FILE_PROCESSOR] import os")
import os
print("[FILE_PROCESSOR] import tempfile")
import tempfile
print("[FILE_PROCESSOR] import uuid")
import uuid
print("[FILE_PROCESSOR] from datetime import datetime")
from datetime import datetime
print("[FILE_PROCESSOR] from decimal import Decimal")
from decimal import Decimal

print("[FILE_PROCESSOR] import boto3")
import boto3

# Import from common layer
print("[FILE_PROCESSOR] from common.logger import StructuredLogger")
from common.logger import StructuredLogger
print("[FILE_PROCESSOR] from common.dynamodb import DynamoDBClient")
from common.dynamodb import DynamoDBClient
print("[FILE_PROCESSOR] from common.excel_parser import PayFileParser")
from common.excel_parser import PayFileParser
print("[FILE_PROCESSOR] from common.validators import ValidationEngine")
from common.validators import ValidationEngine


print("[FILE_PROCESSOR] s3_client = boto3.client('s3')")
s3_client = boto3.client('s3')
print("[FILE_PROCESSOR] dynamodb_client = DynamoDBClient()")
dynamodb_client = DynamoDBClient()


print("[FILE_PROCESSOR] def lambda_handler(event, context):")
def lambda_handler(event, context):
    """Main Lambda handler"""

logger = StructuredLogger("file-processor", context.aws_request_id)
    logger = StructuredLogger("file-processor", context.aws_request_id)
print("[FILE_PROCESSOR] logger.info("File processor invoked", event=event)")
    logger.info("File processor invoked", event=event)

print("[FILE_PROCESSOR] action = event.get('action', 'unknown')")
    action = event.get('action', 'unknown')

print("[FILE_PROCESSOR] try:")
    try:
print("[FILE_PROCESSOR] if action == 'extract_metadata':")
        if action == 'extract_metadata':
print("[FILE_PROCESSOR] return extract_metadata(event, logger)")
            return extract_metadata(event, logger)

print("[FILE_PROCESSOR] elif action == 'match_period':")
        elif action == 'match_period':
print("[FILE_PROCESSOR] return match_period(event, logger)")
            return match_period(event, logger)

print("[FILE_PROCESSOR] elif action == 'check_duplicates':")
        elif action == 'check_duplicates':
print("[FILE_PROCESSOR] return check_duplicates(event, logger)")
            return check_duplicates(event, logger)

print("[FILE_PROCESSOR] elif action == 'supersede_existing':")
        elif action == 'supersede_existing':
print("[FILE_PROCESSOR] return supersede_existing(event, logger)")
            return supersede_existing(event, logger)

print("[FILE_PROCESSOR] elif action == 'parse_records':")
        elif action == 'parse_records':
print("[FILE_PROCESSOR] return parse_records(event, logger)")
            return parse_records(event, logger)

print("[FILE_PROCESSOR] elif action == 'import_records':")
        elif action == 'import_records':
print("[FILE_PROCESSOR] return import_records(event, logger)")
            return import_records(event, logger)

print("[FILE_PROCESSOR] elif action == 'mark_complete':")
        elif action == 'mark_complete':
print("[FILE_PROCESSOR] return mark_complete(event, logger)")
            return mark_complete(event, logger)

print("[FILE_PROCESSOR] elif action == 'mark_error':")
        elif action == 'mark_error':
print("[FILE_PROCESSOR] return mark_error(event, logger)")
            return mark_error(event, logger)

print("[FILE_PROCESSOR] elif action == 'mark_failed':")
        elif action == 'mark_failed':
print("[FILE_PROCESSOR] return mark_failed(event, logger)")
            return mark_failed(event, logger)

print("[FILE_PROCESSOR] else:")
        else:
print("[FILE_PROCESSOR] raise ValueError(f"Unknown action: {action}")")
            raise ValueError(f"Unknown action: {action}")

print("[FILE_PROCESSOR] except Exception as e:")
    except Exception as e:
print("[FILE_PROCESSOR] logger.error("File processor error", error=str(e), action=action)")
        logger.error("File processor error", error=str(e), action=action)
print("[FILE_PROCESSOR] raise")
        raise


print("[FILE_PROCESSOR] def extract_metadata(event: dict, logger: StructuredLogger) -> dict:")
def extract_metadata(event: dict, logger: StructuredLogger) -> dict:
    """
print("[FILE_PROCESSOR] Extract metadata from uploaded file")
    Extract metadata from uploaded file
print("[FILE_PROCESSOR] Step 1 of Step Functions workflow")
    Step 1 of Step Functions workflow
    """
print("[FILE_PROCESSOR] file_id = event['file_id']")
    file_id = event['file_id']
print("[FILE_PROCESSOR] logger.info("Extracting metadata", file_id=file_id)")
    logger.info("Extracting metadata", file_id=file_id)

    # Get file metadata from DynamoDB
print("[FILE_PROCESSOR] file_metadata = dynamodb_client.get_file_metadata(file_id)")
    file_metadata = dynamodb_client.get_file_metadata(file_id)

print("[FILE_PROCESSOR] if not file_metadata:")
    if not file_metadata:
print("[FILE_PROCESSOR] raise ValueError(f"File {file_id} not found")")
        raise ValueError(f"File {file_id} not found")

    # Download file from S3 to temp location
print("[FILE_PROCESSOR] s3_bucket = file_metadata['S3Bucket']")
    s3_bucket = file_metadata['S3Bucket']
print("[FILE_PROCESSOR] s3_key = file_metadata['S3Key']")
    s3_key = file_metadata['S3Key']

print("[FILE_PROCESSOR] temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx')")
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx')
print("[FILE_PROCESSOR] s3_client.download_file(s3_bucket, s3_key, temp_file.name)")
    s3_client.download_file(s3_bucket, s3_key, temp_file.name)

    # Parse Excel file
print("[FILE_PROCESSOR] parser = PayFileParser(temp_file.name)")
    parser = PayFileParser(temp_file.name)
print("[FILE_PROCESSOR] metadata = parser.extract_metadata()")
    metadata = parser.extract_metadata()
print("[FILE_PROCESSOR] parser.close()")
    parser.close()

    # Clean up temp file
print("[FILE_PROCESSOR] os.unlink(temp_file.name)")
    os.unlink(temp_file.name)

print("[FILE_PROCESSOR] logger.info("Metadata extracted", metadata=metadata)")
    logger.info("Metadata extracted", metadata=metadata)

print("[FILE_PROCESSOR] return {")
    return {
print("[FILE_PROCESSOR] 'file_id': file_id,")
        'file_id': file_id,
print("[FILE_PROCESSOR] 'umbrella_code': metadata['umbrella_code'],")
        'umbrella_code': metadata['umbrella_code'],
print("[FILE_PROCESSOR] 'submission_date': metadata['submission_date'],")
        'submission_date': metadata['submission_date'],
print("[FILE_PROCESSOR] 'filename': metadata['filename']")
        'filename': metadata['filename']
print("[FILE_PROCESSOR] }")
    }


print("[FILE_PROCESSOR] def match_period(event: dict, logger: StructuredLogger) -> dict:")
def match_period(event: dict, logger: StructuredLogger) -> dict:
    """
print("[FILE_PROCESSOR] Match file to pay period")
    Match file to pay period
print("[FILE_PROCESSOR] Step 2 of Step Functions workflow")
    Step 2 of Step Functions workflow
    """
print("[FILE_PROCESSOR] file_id = event['file_id']")
    file_id = event['file_id']
print("[FILE_PROCESSOR] metadata = event.get('metadata_result', {})")
    metadata = event.get('metadata_result', {})

print("[FILE_PROCESSOR] logger.info("Matching period", file_id=file_id, metadata=metadata)")
    logger.info("Matching period", file_id=file_id, metadata=metadata)

    # Get umbrella company by code
print("[FILE_PROCESSOR] umbrella_code = metadata.get('umbrella_code')")
    umbrella_code = metadata.get('umbrella_code')
print("[FILE_PROCESSOR] if not umbrella_code:")
    if not umbrella_code:
print("[FILE_PROCESSOR] raise ValueError("Could not determine umbrella company from filename")")
        raise ValueError("Could not determine umbrella company from filename")

    # Query DynamoDB for umbrella
print("[FILE_PROCESSOR] response = dynamodb_client.table.query(")
    response = dynamodb_client.table.query(
print("[FILE_PROCESSOR] IndexName='GSI2',")
        IndexName='GSI2',
print("[FILE_PROCESSOR] KeyConditionExpression='GSI2PK = :pk',")
        KeyConditionExpression='GSI2PK = :pk',
print("[FILE_PROCESSOR] ExpressionAttributeValues={':pk': f'UMBRELLA_CODE#{umbrella_code}'}")
        ExpressionAttributeValues={':pk': f'UMBRELLA_CODE#{umbrella_code}'}
print("[FILE_PROCESSOR] )")
    )

print("[FILE_PROCESSOR] if not response.get('Items'):")
    if not response.get('Items'):
print("[FILE_PROCESSOR] raise ValueError(f"Umbrella company '{umbrella_code}' not found")")
        raise ValueError(f"Umbrella company '{umbrella_code}' not found")

print("[FILE_PROCESSOR] umbrella = response['Items'][0]")
    umbrella = response['Items'][0]
print("[FILE_PROCESSOR] umbrella_id = umbrella['UmbrellaID']")
    umbrella_id = umbrella['UmbrellaID']

    # Determine period from submission date
print("[FILE_PROCESSOR] submission_date = metadata.get('submission_date')")
    submission_date = metadata.get('submission_date')
print("[FILE_PROCESSOR] if not submission_date:")
    if not submission_date:
print("[FILE_PROCESSOR] raise ValueError("Could not determine submission date from filename")")
        raise ValueError("Could not determine submission date from filename")

    # Find matching period
    # For now, use simple logic - in production, match by date range
print("[FILE_PROCESSOR] period_number = 8  # TODO: Implement proper period matching")
    period_number = 8  # TODO: Implement proper period matching

print("[FILE_PROCESSOR] response = dynamodb_client.table.get_item(")
    response = dynamodb_client.table.get_item(
print("[FILE_PROCESSOR] Key={'PK': f'PERIOD#{period_number}', 'SK': 'PROFILE'}")
        Key={'PK': f'PERIOD#{period_number}', 'SK': 'PROFILE'}
print("[FILE_PROCESSOR] )")
    )

print("[FILE_PROCESSOR] if 'Item' not in response:")
    if 'Item' not in response:
print("[FILE_PROCESSOR] raise ValueError(f"Period {period_number} not found")")
        raise ValueError(f"Period {period_number} not found")

print("[FILE_PROCESSOR] period = response['Item']")
    period = response['Item']

print("[FILE_PROCESSOR] logger.info("Period matched", umbrella_id=umbrella_id, period_number=period_numb")
    logger.info("Period matched", umbrella_id=umbrella_id, period_number=period_number)

print("[FILE_PROCESSOR] return {")
    return {
print("[FILE_PROCESSOR] 'file_id': file_id,")
        'file_id': file_id,
print("[FILE_PROCESSOR] 'umbrella_id': umbrella_id,")
        'umbrella_id': umbrella_id,
print("[FILE_PROCESSOR] 'umbrella_code': umbrella_code,")
        'umbrella_code': umbrella_code,
print("[FILE_PROCESSOR] 'period_id': str(period_number),")
        'period_id': str(period_number),
print("[FILE_PROCESSOR] 'period_data': period")
        'period_data': period
print("[FILE_PROCESSOR] }")
    }


print("[FILE_PROCESSOR] def check_duplicates(event: dict, logger: StructuredLogger) -> dict:")
def check_duplicates(event: dict, logger: StructuredLogger) -> dict:
    """
print("[FILE_PROCESSOR] Check for duplicate file (same umbrella + period)")
    Check for duplicate file (same umbrella + period)
print("[FILE_PROCESSOR] Step 3 of Step Functions workflow")
    Step 3 of Step Functions workflow
print("[FILE_PROCESSOR] Gemini improvement #4: Automatic supersede")
    Gemini improvement #4: Automatic supersede
    """
print("[FILE_PROCESSOR] file_id = event['file_id']")
    file_id = event['file_id']
print("[FILE_PROCESSOR] umbrella_id = event['umbrella_id']")
    umbrella_id = event['umbrella_id']
print("[FILE_PROCESSOR] period_id = event['period_id']")
    period_id = event['period_id']

print("[FILE_PROCESSOR] logger.info("Checking duplicates", file_id=file_id, umbrella_id=umbrella_id, per")
    logger.info("Checking duplicates", file_id=file_id, umbrella_id=umbrella_id, period_id=period_id)

    # Query GSI1 for existing files with same umbrella + period
print("[FILE_PROCESSOR] response = dynamodb_client.table.query(")
    response = dynamodb_client.table.query(
print("[FILE_PROCESSOR] IndexName='GSI1',")
        IndexName='GSI1',
print("[FILE_PROCESSOR] KeyConditionExpression='GSI1PK = :pk',")
        KeyConditionExpression='GSI1PK = :pk',
print("[FILE_PROCESSOR] FilterExpression='IsCurrentVersion = :current AND #status <> :deleted',")
        FilterExpression='IsCurrentVersion = :current AND #status <> :deleted',
print("[FILE_PROCESSOR] ExpressionAttributeNames={'#status': 'Status'},")
        ExpressionAttributeNames={'#status': 'Status'},
print("[FILE_PROCESSOR] ExpressionAttributeValues={")
        ExpressionAttributeValues={
print("[FILE_PROCESSOR] ':pk': f'PERIOD#{period_id}#UMBRELLA#{umbrella_id}',")
            ':pk': f'PERIOD#{period_id}#UMBRELLA#{umbrella_id}',
print("[FILE_PROCESSOR] ':current': True,")
            ':current': True,
print("[FILE_PROCESSOR] ':deleted': 'DELETED'")
            ':deleted': 'DELETED'
print("[FILE_PROCESSOR] }")
        }
print("[FILE_PROCESSOR] )")
    )

print("[FILE_PROCESSOR] existing_files = [item for item in response.get('Items', []) if item['FileID'] !")
    existing_files = [item for item in response.get('Items', []) if item['FileID'] != file_id]

print("[FILE_PROCESSOR] if existing_files:")
    if existing_files:
print("[FILE_PROCESSOR] logger.info("Duplicate found - will supersede", existing_file_id=existing_files[")
        logger.info("Duplicate found - will supersede", existing_file_id=existing_files[0]['FileID'])
print("[FILE_PROCESSOR] return {")
        return {
print("[FILE_PROCESSOR] 'file_id': file_id,")
            'file_id': file_id,
print("[FILE_PROCESSOR] 'duplicate_found': True,")
            'duplicate_found': True,
print("[FILE_PROCESSOR] 'existing_file_id': existing_files[0]['FileID']")
            'existing_file_id': existing_files[0]['FileID']
print("[FILE_PROCESSOR] }")
        }

print("[FILE_PROCESSOR] logger.info("No duplicates found")")
    logger.info("No duplicates found")
print("[FILE_PROCESSOR] return {")
    return {
print("[FILE_PROCESSOR] 'file_id': file_id,")
        'file_id': file_id,
print("[FILE_PROCESSOR] 'duplicate_found': False")
        'duplicate_found': False
print("[FILE_PROCESSOR] }")
    }


print("[FILE_PROCESSOR] def supersede_existing(event: dict, logger: StructuredLogger) -> dict:")
def supersede_existing(event: dict, logger: StructuredLogger) -> dict:
    """
print("[FILE_PROCESSOR] Automatically supersede existing file")
    Automatically supersede existing file
print("[FILE_PROCESSOR] Gemini improvement #4: No user prompt, automatic supersede")
    Gemini improvement #4: No user prompt, automatic supersede
    """
print("[FILE_PROCESSOR] file_id = event['file_id']")
    file_id = event['file_id']
print("[FILE_PROCESSOR] existing_file_id = event['existing_file_id']")
    existing_file_id = event['existing_file_id']

print("[FILE_PROCESSOR] logger.info("Superseding existing file", new_file=file_id, old_file=existing_fil")
    logger.info("Superseding existing file", new_file=file_id, old_file=existing_file_id)

    # Mark old file as SUPERSEDED
print("[FILE_PROCESSOR] dynamodb_client.table.update_item(")
    dynamodb_client.table.update_item(
print("[FILE_PROCESSOR] Key={'PK': f'FILE#{existing_file_id}', 'SK': 'METADATA'},")
        Key={'PK': f'FILE#{existing_file_id}', 'SK': 'METADATA'},
print("[FILE_PROCESSOR] UpdateExpression='SET #status = :status, IsCurrentVersion = :current, Superseded")
        UpdateExpression='SET #status = :status, IsCurrentVersion = :current, SupersededAt = :time, SupersededBy = :by',
print("[FILE_PROCESSOR] ExpressionAttributeNames={'#status': 'Status'},")
        ExpressionAttributeNames={'#status': 'Status'},
print("[FILE_PROCESSOR] ExpressionAttributeValues={")
        ExpressionAttributeValues={
print("[FILE_PROCESSOR] ':status': 'SUPERSEDED',")
            ':status': 'SUPERSEDED',
print("[FILE_PROCESSOR] ':current': False,")
            ':current': False,
print("[FILE_PROCESSOR] ':time': datetime.utcnow().isoformat() + 'Z',")
            ':time': datetime.utcnow().isoformat() + 'Z',
print("[FILE_PROCESSOR] ':by': file_id")
            ':by': file_id
print("[FILE_PROCESSOR] }")
        }
print("[FILE_PROCESSOR] )")
    )

    # Mark old pay records as inactive
    # Query all records for old file
print("[FILE_PROCESSOR] response = dynamodb_client.table.query(")
    response = dynamodb_client.table.query(
print("[FILE_PROCESSOR] KeyConditionExpression='PK = :pk AND begins_with(SK, :sk)',")
        KeyConditionExpression='PK = :pk AND begins_with(SK, :sk)',
print("[FILE_PROCESSOR] ExpressionAttributeValues={")
        ExpressionAttributeValues={
print("[FILE_PROCESSOR] ':pk': f'FILE#{existing_file_id}',")
            ':pk': f'FILE#{existing_file_id}',
print("[FILE_PROCESSOR] ':sk': 'RECORD#'")
            ':sk': 'RECORD#'
print("[FILE_PROCESSOR] }")
        }
print("[FILE_PROCESSOR] )")
    )

    # Batch update records
print("[FILE_PROCESSOR] with dynamodb_client.table.batch_writer() as batch:")
    with dynamodb_client.table.batch_writer() as batch:
print("[FILE_PROCESSOR] for record in response.get('Items', []):")
        for record in response.get('Items', []):
print("[FILE_PROCESSOR] record['IsActive'] = False")
            record['IsActive'] = False
print("[FILE_PROCESSOR] batch.put_item(Item=record)")
            batch.put_item(Item=record)

print("[FILE_PROCESSOR] logger.info("Supersede complete", records_deactivated=len(response.get('Items', ")
    logger.info("Supersede complete", records_deactivated=len(response.get('Items', [])))

print("[FILE_PROCESSOR] return {")
    return {
print("[FILE_PROCESSOR] 'file_id': file_id,")
        'file_id': file_id,
print("[FILE_PROCESSOR] 'superseded_file_id': existing_file_id,")
        'superseded_file_id': existing_file_id,
print("[FILE_PROCESSOR] 'records_deactivated': len(response.get('Items', []))")
        'records_deactivated': len(response.get('Items', []))
print("[FILE_PROCESSOR] }")
    }


print("[FILE_PROCESSOR] def parse_records(event: dict, logger: StructuredLogger) -> dict:")
def parse_records(event: dict, logger: StructuredLogger) -> dict:
    """
print("[FILE_PROCESSOR] Parse Excel file into records")
    Parse Excel file into records
print("[FILE_PROCESSOR] Step 4 of Step Functions workflow")
    Step 4 of Step Functions workflow
    """
print("[FILE_PROCESSOR] file_id = event['file_id']")
    file_id = event['file_id']
print("[FILE_PROCESSOR] umbrella_id = event['umbrella_id']")
    umbrella_id = event['umbrella_id']
print("[FILE_PROCESSOR] period_id = event['period_id']")
    period_id = event['period_id']

print("[FILE_PROCESSOR] logger.info("Parsing records", file_id=file_id)")
    logger.info("Parsing records", file_id=file_id)

    # Get file metadata
print("[FILE_PROCESSOR] file_metadata = dynamodb_client.get_file_metadata(file_id)")
    file_metadata = dynamodb_client.get_file_metadata(file_id)

    # Download file
print("[FILE_PROCESSOR] s3_bucket = file_metadata['S3Bucket']")
    s3_bucket = file_metadata['S3Bucket']
print("[FILE_PROCESSOR] s3_key = file_metadata['S3Key']")
    s3_key = file_metadata['S3Key']

print("[FILE_PROCESSOR] temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx')")
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx')
print("[FILE_PROCESSOR] s3_client.download_file(s3_bucket, s3_key, temp_file.name)")
    s3_client.download_file(s3_bucket, s3_key, temp_file.name)

    # Parse records
print("[FILE_PROCESSOR] parser = PayFileParser(temp_file.name)")
    parser = PayFileParser(temp_file.name)
print("[FILE_PROCESSOR] records = parser.parse_records()")
    records = parser.parse_records()
print("[FILE_PROCESSOR] parser.close()")
    parser.close()

    # Clean up
print("[FILE_PROCESSOR] os.unlink(temp_file.name)")
    os.unlink(temp_file.name)

print("[FILE_PROCESSOR] logger.info("Records parsed", record_count=len(records))")
    logger.info("Records parsed", record_count=len(records))

    # Update file metadata with record count
print("[FILE_PROCESSOR] dynamodb_client.update_file_status(")
    dynamodb_client.update_file_status(
print("[FILE_PROCESSOR] file_id,")
        file_id,
print("[FILE_PROCESSOR] 'PROCESSING',")
        'PROCESSING',
print("[FILE_PROCESSOR] TotalRecords=len(records),")
        TotalRecords=len(records),
print("[FILE_PROCESSOR] ProcessingStartedAt=datetime.utcnow().isoformat() + 'Z'")
        ProcessingStartedAt=datetime.utcnow().isoformat() + 'Z'
print("[FILE_PROCESSOR] )")
    )

print("[FILE_PROCESSOR] return {")
    return {
print("[FILE_PROCESSOR] 'file_id': file_id,")
        'file_id': file_id,
print("[FILE_PROCESSOR] 'umbrella_id': umbrella_id,")
        'umbrella_id': umbrella_id,
print("[FILE_PROCESSOR] 'period_id': period_id,")
        'period_id': period_id,
print("[FILE_PROCESSOR] 'records': records,")
        'records': records,
print("[FILE_PROCESSOR] 'record_count': len(records)")
        'record_count': len(records)
print("[FILE_PROCESSOR] }")
    }


print("[FILE_PROCESSOR] def import_records(event: dict, logger: StructuredLogger) -> dict:")
def import_records(event: dict, logger: StructuredLogger) -> dict:
    """
print("[FILE_PROCESSOR] Import validated records to DynamoDB")
    Import validated records to DynamoDB
print("[FILE_PROCESSOR] Step 5 of Step Functions workflow")
    Step 5 of Step Functions workflow
    """
print("[FILE_PROCESSOR] file_id = event['file_id']")
    file_id = event['file_id']
print("[FILE_PROCESSOR] validated_records = event.get('validated_records', [])")
    validated_records = event.get('validated_records', [])
print("[FILE_PROCESSOR] has_warnings = event.get('has_warnings', False)")
    has_warnings = event.get('has_warnings', False)

print("[FILE_PROCESSOR] logger.info("Importing records", file_id=file_id, record_count=len(validated_rec")
    logger.info("Importing records", file_id=file_id, record_count=len(validated_records))

    # Batch write records
print("[FILE_PROCESSOR] records_to_write = []")
    records_to_write = []

print("[FILE_PROCESSOR] for idx, record_data in enumerate(validated_records, start=1):")
    for idx, record_data in enumerate(validated_records, start=1):
print("[FILE_PROCESSOR] record = record_data['record']")
        record = record_data['record']
print("[FILE_PROCESSOR] contractor_id = record_data.get('contractor_id')")
        contractor_id = record_data.get('contractor_id')
print("[FILE_PROCESSOR] association_id = record_data.get('association_id')")
        association_id = record_data.get('association_id')

print("[FILE_PROCESSOR] record_id = str(uuid.uuid4())")
        record_id = str(uuid.uuid4())

print("[FILE_PROCESSOR] item = {")
        item = {
print("[FILE_PROCESSOR] 'PK': f'FILE#{file_id}',")
            'PK': f'FILE#{file_id}',
print("[FILE_PROCESSOR] 'SK': f'RECORD#{idx:03d}',")
            'SK': f'RECORD#{idx:03d}',
print("[FILE_PROCESSOR] 'EntityType': 'PayRecord',")
            'EntityType': 'PayRecord',
print("[FILE_PROCESSOR] 'RecordID': record_id,")
            'RecordID': record_id,
print("[FILE_PROCESSOR] 'FileID': file_id,")
            'FileID': file_id,
print("[FILE_PROCESSOR] 'ContractorID': contractor_id,")
            'ContractorID': contractor_id,
print("[FILE_PROCESSOR] 'UmbrellaID': record_data.get('umbrella_id'),")
            'UmbrellaID': record_data.get('umbrella_id'),
print("[FILE_PROCESSOR] 'PeriodID': record_data.get('period_id'),")
            'PeriodID': record_data.get('period_id'),
print("[FILE_PROCESSOR] 'AssociationID': association_id,")
            'AssociationID': association_id,
print("[FILE_PROCESSOR] 'EmployeeID': record['employee_id'],")
            'EmployeeID': record['employee_id'],
print("[FILE_PROCESSOR] 'UnitDays': Decimal(str(record['unit_days'])),")
            'UnitDays': Decimal(str(record['unit_days'])),
print("[FILE_PROCESSOR] 'DayRate': Decimal(str(record['day_rate'])),")
            'DayRate': Decimal(str(record['day_rate'])),
print("[FILE_PROCESSOR] 'Amount': Decimal(str(record['amount'])),")
            'Amount': Decimal(str(record['amount'])),
print("[FILE_PROCESSOR] 'VATAmount': Decimal(str(record['vat_amount'])),")
            'VATAmount': Decimal(str(record['vat_amount'])),
print("[FILE_PROCESSOR] 'GrossAmount': Decimal(str(record['gross_amount'])),")
            'GrossAmount': Decimal(str(record['gross_amount'])),
print("[FILE_PROCESSOR] 'TotalHours': Decimal(str(record.get('total_hours', 0))),")
            'TotalHours': Decimal(str(record.get('total_hours', 0))),
print("[FILE_PROCESSOR] 'RecordType': record['record_type'],")
            'RecordType': record['record_type'],
print("[FILE_PROCESSOR] 'Notes': record.get('notes', ''),")
            'Notes': record.get('notes', ''),
print("[FILE_PROCESSOR] 'IsActive': True,")
            'IsActive': True,
print("[FILE_PROCESSOR] 'CreatedAt': datetime.utcnow().isoformat() + 'Z',")
            'CreatedAt': datetime.utcnow().isoformat() + 'Z',
print("[FILE_PROCESSOR] 'GSI1PK': f'CONTRACTOR#{contractor_id}',")
            'GSI1PK': f'CONTRACTOR#{contractor_id}',
print("[FILE_PROCESSOR] 'GSI1SK': f'RECORD#{datetime.utcnow().isoformat()}Z',")
            'GSI1SK': f'RECORD#{datetime.utcnow().isoformat()}Z',
print("[FILE_PROCESSOR] 'GSI2PK': f'PERIOD#{record_data.get("period_id")}',")
            'GSI2PK': f'PERIOD#{record_data.get("period_id")}',
print("[FILE_PROCESSOR] 'GSI2SK': f'CONTRACTOR#{contractor_id}'")
            'GSI2SK': f'CONTRACTOR#{contractor_id}'
print("[FILE_PROCESSOR] }")
        }

print("[FILE_PROCESSOR] records_to_write.append(item)")
        records_to_write.append(item)

    # Write in batches
print("[FILE_PROCESSOR] dynamodb_client.batch_write_pay_records(records_to_write)")
    dynamodb_client.batch_write_pay_records(records_to_write)

print("[FILE_PROCESSOR] logger.info("Records imported", count=len(records_to_write))")
    logger.info("Records imported", count=len(records_to_write))

print("[FILE_PROCESSOR] return {")
    return {
print("[FILE_PROCESSOR] 'file_id': file_id,")
        'file_id': file_id,
print("[FILE_PROCESSOR] 'records_imported': len(records_to_write),")
        'records_imported': len(records_to_write),
print("[FILE_PROCESSOR] 'has_warnings': has_warnings")
        'has_warnings': has_warnings
print("[FILE_PROCESSOR] }")
    }


print("[FILE_PROCESSOR] def mark_complete(event: dict, logger: StructuredLogger) -> dict:")
def mark_complete(event: dict, logger: StructuredLogger) -> dict:
    """
print("[FILE_PROCESSOR] Mark file processing as complete")
    Mark file processing as complete
print("[FILE_PROCESSOR] Final step of successful workflow")
    Final step of successful workflow
    """
print("[FILE_PROCESSOR] file_id = event['file_id']")
    file_id = event['file_id']
print("[FILE_PROCESSOR] import_result = event.get('import_result', {})")
    import_result = event.get('import_result', {})
print("[FILE_PROCESSOR] has_warnings = event.get('has_warnings', False)")
    has_warnings = event.get('has_warnings', False)
print("[FILE_PROCESSOR] was_supersede = event.get('was_supersede', False)")
    was_supersede = event.get('was_supersede', False)

print("[FILE_PROCESSOR] records_imported = import_result.get('records_imported', 0)")
    records_imported = import_result.get('records_imported', 0)

    # Determine status
print("[FILE_PROCESSOR] status = 'COMPLETED_WITH_WARNINGS' if has_warnings else 'COMPLETED'")
    status = 'COMPLETED_WITH_WARNINGS' if has_warnings else 'COMPLETED'

print("[FILE_PROCESSOR] logger.info("Marking complete", file_id=file_id, status=status)")
    logger.info("Marking complete", file_id=file_id, status=status)

print("[FILE_PROCESSOR] dynamodb_client.update_file_status(")
    dynamodb_client.update_file_status(
print("[FILE_PROCESSOR] file_id,")
        file_id,
print("[FILE_PROCESSOR] status,")
        status,
print("[FILE_PROCESSOR] ValidRecords=records_imported,")
        ValidRecords=records_imported,
print("[FILE_PROCESSOR] ProcessingCompletedAt=datetime.utcnow().isoformat() + 'Z'")
        ProcessingCompletedAt=datetime.utcnow().isoformat() + 'Z'
print("[FILE_PROCESSOR] )")
    )

print("[FILE_PROCESSOR] return {")
    return {
print("[FILE_PROCESSOR] 'file_id': file_id,")
        'file_id': file_id,
print("[FILE_PROCESSOR] 'status': status,")
        'status': status,
print("[FILE_PROCESSOR] 'records_imported': records_imported,")
        'records_imported': records_imported,
print("[FILE_PROCESSOR] 'message': 'File processing complete'")
        'message': 'File processing complete'
print("[FILE_PROCESSOR] }")
    }


print("[FILE_PROCESSOR] def mark_error(event: dict, logger: StructuredLogger) -> dict:")
def mark_error(event: dict, logger: StructuredLogger) -> dict:
    """
print("[FILE_PROCESSOR] Mark file as ERROR due to critical validation errors")
    Mark file as ERROR due to critical validation errors
print("[FILE_PROCESSOR] Gemini improvement #2: Errors block import")
    Gemini improvement #2: Errors block import
    """
print("[FILE_PROCESSOR] file_id = event['file_id']")
    file_id = event['file_id']
print("[FILE_PROCESSOR] validation_errors = event.get('validation_errors', [])")
    validation_errors = event.get('validation_errors', [])

print("[FILE_PROCESSOR] logger.error("Marking file as ERROR", file_id=file_id, error_count=len(validatio")
    logger.error("Marking file as ERROR", file_id=file_id, error_count=len(validation_errors))

print("[FILE_PROCESSOR] dynamodb_client.update_file_status(")
    dynamodb_client.update_file_status(
print("[FILE_PROCESSOR] file_id,")
        file_id,
print("[FILE_PROCESSOR] 'ERROR',")
        'ERROR',
print("[FILE_PROCESSOR] ErrorRecords=len(validation_errors),")
        ErrorRecords=len(validation_errors),
print("[FILE_PROCESSOR] ValidRecords=0,")
        ValidRecords=0,
print("[FILE_PROCESSOR] TotalRecords=0,")
        TotalRecords=0,
print("[FILE_PROCESSOR] ProcessingCompletedAt=datetime.utcnow().isoformat() + 'Z'")
        ProcessingCompletedAt=datetime.utcnow().isoformat() + 'Z'
print("[FILE_PROCESSOR] )")
    )

print("[FILE_PROCESSOR] return {")
    return {
print("[FILE_PROCESSOR] 'file_id': file_id,")
        'file_id': file_id,
print("[FILE_PROCESSOR] 'status': 'ERROR',")
        'status': 'ERROR',
print("[FILE_PROCESSOR] 'message': 'File rejected due to critical validation errors'")
        'message': 'File rejected due to critical validation errors'
print("[FILE_PROCESSOR] }")
    }


print("[FILE_PROCESSOR] def mark_failed(event: dict, logger: StructuredLogger) -> dict:")
def mark_failed(event: dict, logger: StructuredLogger) -> dict:
    """
print("[FILE_PROCESSOR] Mark file processing as failed due to system error")
    Mark file processing as failed due to system error
    """
print("[FILE_PROCESSOR] file_id = event['file_id']")
    file_id = event['file_id']
print("[FILE_PROCESSOR] error = event.get('error', {})")
    error = event.get('error', {})

print("[FILE_PROCESSOR] logger.error("Processing failed", file_id=file_id, error=error)")
    logger.error("Processing failed", file_id=file_id, error=error)

print("[FILE_PROCESSOR] dynamodb_client.update_file_status(")
    dynamodb_client.update_file_status(
print("[FILE_PROCESSOR] file_id,")
        file_id,
print("[FILE_PROCESSOR] 'FAILED',")
        'FAILED',
print("[FILE_PROCESSOR] ProcessingCompletedAt=datetime.utcnow().isoformat() + 'Z'")
        ProcessingCompletedAt=datetime.utcnow().isoformat() + 'Z'
print("[FILE_PROCESSOR] )")
    )

print("[FILE_PROCESSOR] return {")
    return {
print("[FILE_PROCESSOR] 'file_id': file_id,")
        'file_id': file_id,
print("[FILE_PROCESSOR] 'status': 'FAILED',")
        'status': 'FAILED',
print("[FILE_PROCESSOR] 'message': 'File processing failed'")
        'message': 'File processing failed'
print("[FILE_PROCESSOR] }")
    }
print("[FILE_PROCESSOR] Module load complete")
