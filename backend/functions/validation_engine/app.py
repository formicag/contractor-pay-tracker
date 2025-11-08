"""
Validation Engine Lambda Function
Validates pay records against business rules

Implements Gemini improvements:
- Error vs Warning distinction (improvement #2)
- Many-to-many contractor-umbrella validation (improvement #1)
"""

import json
import uuid
from datetime import datetime

# Import from common layer
from common.logger import StructuredLogger
from common.dynamodb import DynamoDBClient
from common.validators import ValidationEngine


dynamodb_client = DynamoDBClient()


def lambda_handler(event, context):
    """
    Validate all pay records

    Returns:
        {
            'has_critical_errors': bool,
            'has_warnings': bool,
            'valid_records': List[Dict],  # Records that passed validation
            'errors': List[Dict],         # Critical errors
            'warnings': List[Dict]        # Non-blocking warnings
        }
    """

    logger = StructuredLogger("validation-engine", context.request_id)
    logger.info("Validation engine invoked", event=event)

    try:
        file_id = event['file_id']
        umbrella_id = event['umbrella_id']
        period_id = event['period_id']
        records = event['records']

        logger.info("Starting validation", file_id=file_id, record_count=len(records))

        # Initialize validation engine
        validator = ValidationEngine(dynamodb_client)

        # Get period data
        period_response = dynamodb_client.table.get_item(
            Key={'PK': f'PERIOD#{period_id}', 'SK': 'PROFILE'}
        )
        period_data = period_response.get('Item', {})

        # Validate all records
        valid_records = []
        all_errors = []
        all_warnings = []
        has_critical_errors = False

        # Pre-load contractors for performance
        contractors_cache = _load_contractors_cache()

        for record in records:
            is_valid, errors, warnings = validator.validate_record(
                record,
                umbrella_id,
                period_data,
                contractors_cache
            )

            if not is_valid:
                has_critical_errors = True
                all_errors.extend(errors)

                # Store errors in DynamoDB
                _store_validation_errors(file_id, errors, logger)
            else:
                # Add contractor/association info to record
                contractor_result = validator.find_contractor(record, contractors_cache)
                contractor_id = contractor_result.get('contractor_id')

                assoc_result = validator.validate_umbrella_association(
                    contractor_id,
                    umbrella_id,
                    period_data
                )
                association_id = assoc_result.get('association', {}).get('AssociationID')

                valid_records.append({
                    'record': record,
                    'contractor_id': contractor_id,
                    'association_id': association_id,
                    'umbrella_id': umbrella_id,
                    'period_id': period_id
                })

            if warnings:
                all_warnings.extend(warnings)
                _store_validation_warnings(file_id, warnings, logger)

        logger.info("Validation complete",
                   total_records=len(records),
                   valid_records=len(valid_records),
                   errors=len(all_errors),
                   warnings=len(all_warnings))

        return {
            'has_critical_errors': has_critical_errors,
            'has_warnings': len(all_warnings) > 0,
            'valid_records': valid_records,
            'errors': all_errors,
            'warnings': all_warnings,
            'validation_summary': {
                'total_records': len(records),
                'valid_records': len(valid_records),
                'error_count': len(all_errors),
                'warning_count': len(all_warnings)
            }
        }

    except Exception as e:
        logger.error("Validation engine error", error=str(e))
        raise


def _load_contractors_cache() -> dict:
    """Pre-load all contractors for performance"""
    response = dynamodb_client.table.scan(
        FilterExpression='EntityType = :type',
        ExpressionAttributeValues={':type': 'Contractor'}
    )

    contractors = {}
    for item in response.get('Items', []):
        contractors[item['ContractorID']] = item

    return contractors


def _store_validation_errors(file_id: str, errors: list, logger: StructuredLogger):
    """Store validation errors in DynamoDB"""

    items = []
    for idx, error in enumerate(errors, start=1):
        error_id = str(uuid.uuid4())

        item = {
            'PK': f'FILE#{file_id}',
            'SK': f'ERROR#{idx:03d}',
            'EntityType': 'ValidationError',
            'ErrorID': error_id,
            'FileID': file_id,
            'ErrorType': error.get('error_type'),
            'Severity': error.get('severity', 'CRITICAL'),
            'RowNumber': error.get('row_number'),
            'EmployeeID': error.get('employee_id'),
            'ContractorName': error.get('contractor_name'),
            'ErrorMessage': error.get('error_message'),
            'SuggestedFix': error.get('suggested_fix'),
            'CreatedAt': datetime.utcnow().isoformat() + 'Z',
            'GSI1PK': 'ERRORS',
            'GSI1SK': datetime.utcnow().isoformat() + 'Z'
        }

        items.append(item)

    # Batch write
    with dynamodb_client.table.batch_writer() as batch:
        for item in items:
            batch.put_item(Item=item)

    logger.info("Stored validation errors", count=len(items))


def _store_validation_warnings(file_id: str, warnings: list, logger: StructuredLogger):
    """Store validation warnings in DynamoDB"""

    items = []
    for idx, warning in enumerate(warnings, start=1):
        warning_id = str(uuid.uuid4())

        item = {
            'PK': f'FILE#{file_id}',
            'SK': f'WARNING#{idx:03d}',
            'EntityType': 'ValidationWarning',
            'WarningID': warning_id,
            'FileID': file_id,
            'WarningType': warning.get('warning_type'),
            'RowNumber': warning.get('row_number'),
            'WarningMessage': warning.get('warning_message'),
            'AutoResolved': warning.get('auto_resolved', False),
            'ResolutionNotes': warning.get('resolution_notes'),
            'CreatedAt': datetime.utcnow().isoformat() + 'Z',
            'GSI1PK': 'WARNINGS',
            'GSI1SK': datetime.utcnow().isoformat() + 'Z'
        }

        items.append(item)

    # Batch write
    with dynamodb_client.table.batch_writer() as batch:
        for item in items:
            batch.put_item(Item=item)

    logger.info("Stored validation warnings", count=len(items))
