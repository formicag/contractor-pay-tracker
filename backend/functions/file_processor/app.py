"""
File Processor Lambda Function
Processes Excel files, validates contractor data, and imports to DynamoDB

Implements Gemini improvements:
- Automatic supersede (improvement #4)
- Many-to-many contractor-umbrella validation (improvement #1)
- Error vs Warning handling (improvement #2)
"""

import json
import os
import tempfile
import uuid
from datetime import datetime
from decimal import Decimal

import boto3

# Import from common layer
from common.logger import StructuredLogger
from common.dynamodb import DynamoDBClient
from common.excel_parser import PayFileParser
from common.validators import ValidationEngine


s3_client = boto3.client('s3')
dynamodb_client = DynamoDBClient()


def lambda_handler(event, context):
    """Main Lambda handler"""

    logger = StructuredLogger("file-processor", context.request_id)
    logger.info("File processor invoked", event=event)

    action = event.get('action', 'unknown')

    try:
        if action == 'extract_metadata':
            return extract_metadata(event, logger)

        elif action == 'match_period':
            return match_period(event, logger)

        elif action == 'check_duplicates':
            return check_duplicates(event, logger)

        elif action == 'supersede_existing':
            return supersede_existing(event, logger)

        elif action == 'parse_records':
            return parse_records(event, logger)

        elif action == 'import_records':
            return import_records(event, logger)

        elif action == 'mark_complete':
            return mark_complete(event, logger)

        elif action == 'mark_error':
            return mark_error(event, logger)

        elif action == 'mark_failed':
            return mark_failed(event, logger)

        else:
            raise ValueError(f"Unknown action: {action}")

    except Exception as e:
        logger.error("File processor error", error=str(e), action=action)
        raise


def extract_metadata(event: dict, logger: StructuredLogger) -> dict:
    """
    Extract metadata from uploaded file
    Step 1 of Step Functions workflow
    """
    file_id = event['file_id']
    logger.info("Extracting metadata", file_id=file_id)

    # Get file metadata from DynamoDB
    file_metadata = dynamodb_client.get_file_metadata(file_id)

    if not file_metadata:
        raise ValueError(f"File {file_id} not found")

    # Download file from S3 to temp location
    s3_bucket = file_metadata['S3Bucket']
    s3_key = file_metadata['S3Key']

    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx')
    s3_client.download_file(s3_bucket, s3_key, temp_file.name)

    # Parse Excel file
    parser = PayFileParser(temp_file.name)
    metadata = parser.extract_metadata()
    parser.close()

    # Clean up temp file
    os.unlink(temp_file.name)

    logger.info("Metadata extracted", metadata=metadata)

    return {
        'file_id': file_id,
        'umbrella_code': metadata['umbrella_code'],
        'submission_date': metadata['submission_date'],
        'filename': metadata['filename']
    }


def match_period(event: dict, logger: StructuredLogger) -> dict:
    """
    Match file to pay period
    Step 2 of Step Functions workflow
    """
    file_id = event['file_id']
    metadata = event.get('metadata_result', {})

    logger.info("Matching period", file_id=file_id, metadata=metadata)

    # Get umbrella company by code
    umbrella_code = metadata.get('umbrella_code')
    if not umbrella_code:
        raise ValueError("Could not determine umbrella company from filename")

    # Query DynamoDB for umbrella
    response = dynamodb_client.table.query(
        IndexName='GSI2',
        KeyConditionExpression='GSI2PK = :pk',
        ExpressionAttributeValues={':pk': f'UMBRELLA_CODE#{umbrella_code}'}
    )

    if not response.get('Items'):
        raise ValueError(f"Umbrella company '{umbrella_code}' not found")

    umbrella = response['Items'][0]
    umbrella_id = umbrella['UmbrellaID']

    # Determine period from submission date
    submission_date = metadata.get('submission_date')
    if not submission_date:
        raise ValueError("Could not determine submission date from filename")

    # Find matching period
    # For now, use simple logic - in production, match by date range
    period_number = 8  # TODO: Implement proper period matching

    response = dynamodb_client.table.get_item(
        Key={'PK': f'PERIOD#{period_number}', 'SK': 'PROFILE'}
    )

    if 'Item' not in response:
        raise ValueError(f"Period {period_number} not found")

    period = response['Item']

    logger.info("Period matched", umbrella_id=umbrella_id, period_number=period_number)

    return {
        'file_id': file_id,
        'umbrella_id': umbrella_id,
        'umbrella_code': umbrella_code,
        'period_id': str(period_number),
        'period_data': period
    }


def check_duplicates(event: dict, logger: StructuredLogger) -> dict:
    """
    Check for duplicate file (same umbrella + period)
    Step 3 of Step Functions workflow
    Gemini improvement #4: Automatic supersede
    """
    file_id = event['file_id']
    umbrella_id = event['umbrella_id']
    period_id = event['period_id']

    logger.info("Checking duplicates", file_id=file_id, umbrella_id=umbrella_id, period_id=period_id)

    # Query GSI1 for existing files with same umbrella + period
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

    existing_files = [item for item in response.get('Items', []) if item['FileID'] != file_id]

    if existing_files:
        logger.info("Duplicate found - will supersede", existing_file_id=existing_files[0]['FileID'])
        return {
            'file_id': file_id,
            'duplicate_found': True,
            'existing_file_id': existing_files[0]['FileID']
        }

    logger.info("No duplicates found")
    return {
        'file_id': file_id,
        'duplicate_found': False
    }


def supersede_existing(event: dict, logger: StructuredLogger) -> dict:
    """
    Automatically supersede existing file
    Gemini improvement #4: No user prompt, automatic supersede
    """
    file_id = event['file_id']
    existing_file_id = event['existing_file_id']

    logger.info("Superseding existing file", new_file=file_id, old_file=existing_file_id)

    # Mark old file as SUPERSEDED
    dynamodb_client.table.update_item(
        Key={'PK': f'FILE#{existing_file_id}', 'SK': 'METADATA'},
        UpdateExpression='SET #status = :status, IsCurrentVersion = :current, SupersededAt = :time, SupersededBy = :by',
        ExpressionAttributeNames={'#status': 'Status'},
        ExpressionAttributeValues={
            ':status': 'SUPERSEDED',
            ':current': False,
            ':time': datetime.utcnow().isoformat() + 'Z',
            ':by': file_id
        }
    )

    # Mark old pay records as inactive
    # Query all records for old file
    response = dynamodb_client.table.query(
        KeyConditionExpression='PK = :pk AND begins_with(SK, :sk)',
        ExpressionAttributeValues={
            ':pk': f'FILE#{existing_file_id}',
            ':sk': 'RECORD#'
        }
    )

    # Batch update records
    with dynamodb_client.table.batch_writer() as batch:
        for record in response.get('Items', []):
            record['IsActive'] = False
            batch.put_item(Item=record)

    logger.info("Supersede complete", records_deactivated=len(response.get('Items', [])))

    return {
        'file_id': file_id,
        'superseded_file_id': existing_file_id,
        'records_deactivated': len(response.get('Items', []))
    }


def parse_records(event: dict, logger: StructuredLogger) -> dict:
    """
    Parse Excel file into records
    Step 4 of Step Functions workflow
    """
    file_id = event['file_id']
    umbrella_id = event['umbrella_id']
    period_id = event['period_id']

    logger.info("Parsing records", file_id=file_id)

    # Get file metadata
    file_metadata = dynamodb_client.get_file_metadata(file_id)

    # Download file
    s3_bucket = file_metadata['S3Bucket']
    s3_key = file_metadata['S3Key']

    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx')
    s3_client.download_file(s3_bucket, s3_key, temp_file.name)

    # Parse records
    parser = PayFileParser(temp_file.name)
    records = parser.parse_records()
    parser.close()

    # Clean up
    os.unlink(temp_file.name)

    logger.info("Records parsed", record_count=len(records))

    # Update file metadata with record count
    dynamodb_client.update_file_status(
        file_id,
        'PROCESSING',
        TotalRecords=len(records),
        ProcessingStartedAt=datetime.utcnow().isoformat() + 'Z'
    )

    return {
        'file_id': file_id,
        'umbrella_id': umbrella_id,
        'period_id': period_id,
        'records': records,
        'record_count': len(records)
    }


def import_records(event: dict, logger: StructuredLogger) -> dict:
    """
    Import validated records to DynamoDB
    Step 5 of Step Functions workflow
    """
    file_id = event['file_id']
    validated_records = event.get('validated_records', [])
    has_warnings = event.get('has_warnings', False)

    logger.info("Importing records", file_id=file_id, record_count=len(validated_records))

    # Batch write records
    records_to_write = []

    for idx, record_data in enumerate(validated_records, start=1):
        record = record_data['record']
        contractor_id = record_data.get('contractor_id')
        association_id = record_data.get('association_id')

        record_id = str(uuid.uuid4())

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
            'CreatedAt': datetime.utcnow().isoformat() + 'Z',
            'GSI1PK': f'CONTRACTOR#{contractor_id}',
            'GSI1SK': f'RECORD#{datetime.utcnow().isoformat()}Z',
            'GSI2PK': f'PERIOD#{record_data.get("period_id")}',
            'GSI2SK': f'CONTRACTOR#{contractor_id}'
        }

        records_to_write.append(item)

    # Write in batches
    dynamodb_client.batch_write_pay_records(records_to_write)

    logger.info("Records imported", count=len(records_to_write))

    return {
        'file_id': file_id,
        'records_imported': len(records_to_write),
        'has_warnings': has_warnings
    }


def mark_complete(event: dict, logger: StructuredLogger) -> dict:
    """
    Mark file processing as complete
    Final step of successful workflow
    """
    file_id = event['file_id']
    import_result = event.get('import_result', {})
    has_warnings = event.get('has_warnings', False)
    was_supersede = event.get('was_supersede', False)

    records_imported = import_result.get('records_imported', 0)

    # Determine status
    status = 'COMPLETED_WITH_WARNINGS' if has_warnings else 'COMPLETED'

    logger.info("Marking complete", file_id=file_id, status=status)

    dynamodb_client.update_file_status(
        file_id,
        status,
        ValidRecords=records_imported,
        ProcessingCompletedAt=datetime.utcnow().isoformat() + 'Z'
    )

    return {
        'file_id': file_id,
        'status': status,
        'records_imported': records_imported,
        'message': 'File processing complete'
    }


def mark_error(event: dict, logger: StructuredLogger) -> dict:
    """
    Mark file as ERROR due to critical validation errors
    Gemini improvement #2: Errors block import
    """
    file_id = event['file_id']
    validation_errors = event.get('validation_errors', [])

    logger.error("Marking file as ERROR", file_id=file_id, error_count=len(validation_errors))

    dynamodb_client.update_file_status(
        file_id,
        'ERROR',
        ErrorRecords=len(validation_errors),
        ValidRecords=0,
        TotalRecords=0,
        ProcessingCompletedAt=datetime.utcnow().isoformat() + 'Z'
    )

    return {
        'file_id': file_id,
        'status': 'ERROR',
        'message': 'File rejected due to critical validation errors'
    }


def mark_failed(event: dict, logger: StructuredLogger) -> dict:
    """
    Mark file processing as failed due to system error
    """
    file_id = event['file_id']
    error = event.get('error', {})

    logger.error("Processing failed", file_id=file_id, error=error)

    dynamodb_client.update_file_status(
        file_id,
        'FAILED',
        ProcessingCompletedAt=datetime.utcnow().isoformat() + 'Z'
    )

    return {
        'file_id': file_id,
        'status': 'FAILED',
        'message': 'File processing failed'
    }
