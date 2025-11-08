print("[VALIDATION_ENGINE] Module load started")
"""
print("[VALIDATION_ENGINE] Validation Engine Lambda Function")
Validation Engine Lambda Function
print("[VALIDATION_ENGINE] Validates pay records against business rules")
Validates pay records against business rules

print("[VALIDATION_ENGINE] Implements Gemini improvements:")
Implements Gemini improvements:
print("[VALIDATION_ENGINE] - Error vs Warning distinction (improvement #2)")
- Error vs Warning distinction (improvement #2)
print("[VALIDATION_ENGINE] - Many-to-many contractor-umbrella validation (improvement #1)")
- Many-to-many contractor-umbrella validation (improvement #1)
"""

print("[VALIDATION_ENGINE] import json")
import json
print("[VALIDATION_ENGINE] import uuid")
import uuid
print("[VALIDATION_ENGINE] from datetime import datetime")
from datetime import datetime

# Import from common layer
print("[VALIDATION_ENGINE] from common.logger import StructuredLogger")
from common.logger import StructuredLogger
print("[VALIDATION_ENGINE] from common.dynamodb import DynamoDBClient")
from common.dynamodb import DynamoDBClient
print("[VALIDATION_ENGINE] from common.validators import ValidationEngine")
from common.validators import ValidationEngine


print("[VALIDATION_ENGINE] dynamodb_client = DynamoDBClient()")
dynamodb_client = DynamoDBClient()


print("[VALIDATION_ENGINE] def lambda_handler(event, context):")
def lambda_handler(event, context):
    """
print("[VALIDATION_ENGINE] Validate all pay records")
    Validate all pay records

print("[VALIDATION_ENGINE] Returns:")
    Returns:
print("[VALIDATION_ENGINE] {")
        {
print("[VALIDATION_ENGINE] 'has_critical_errors': bool,")
            'has_critical_errors': bool,
print("[VALIDATION_ENGINE] 'has_warnings': bool,")
            'has_warnings': bool,
print("[VALIDATION_ENGINE] 'valid_records': List[Dict],  # Records that passed validation")
            'valid_records': List[Dict],  # Records that passed validation
print("[VALIDATION_ENGINE] 'errors': List[Dict],         # Critical errors")
            'errors': List[Dict],         # Critical errors
print("[VALIDATION_ENGINE] 'warnings': List[Dict]        # Non-blocking warnings")
            'warnings': List[Dict]        # Non-blocking warnings
print("[VALIDATION_ENGINE] }")
        }
    """

logger = StructuredLogger("validation-engine", context.aws_request_id)
    logger = StructuredLogger("validation-engine", context.aws_request_id)
print("[VALIDATION_ENGINE] logger.info("Validation engine invoked", event=event)")
    logger.info("Validation engine invoked", event=event)

print("[VALIDATION_ENGINE] try:")
    try:
print("[VALIDATION_ENGINE] file_id = event['file_id']")
        file_id = event['file_id']
print("[VALIDATION_ENGINE] umbrella_id = event['umbrella_id']")
        umbrella_id = event['umbrella_id']
print("[VALIDATION_ENGINE] period_id = event['period_id']")
        period_id = event['period_id']
print("[VALIDATION_ENGINE] records = event['records']")
        records = event['records']

print("[VALIDATION_ENGINE] logger.info("Starting validation", file_id=file_id, record_count=len(records))")
        logger.info("Starting validation", file_id=file_id, record_count=len(records))

        # Initialize validation engine
print("[VALIDATION_ENGINE] validator = ValidationEngine(dynamodb_client)")
        validator = ValidationEngine(dynamodb_client)

        # Get period data
print("[VALIDATION_ENGINE] period_response = dynamodb_client.table.get_item(")
        period_response = dynamodb_client.table.get_item(
print("[VALIDATION_ENGINE] Key={'PK': f'PERIOD#{period_id}', 'SK': 'PROFILE'}")
            Key={'PK': f'PERIOD#{period_id}', 'SK': 'PROFILE'}
print("[VALIDATION_ENGINE] )")
        )
print("[VALIDATION_ENGINE] period_data = period_response.get('Item', {})")
        period_data = period_response.get('Item', {})

        # Validate all records
print("[VALIDATION_ENGINE] valid_records = []")
        valid_records = []
print("[VALIDATION_ENGINE] all_errors = []")
        all_errors = []
print("[VALIDATION_ENGINE] all_warnings = []")
        all_warnings = []
print("[VALIDATION_ENGINE] has_critical_errors = False")
        has_critical_errors = False

        # Pre-load contractors for performance
print("[VALIDATION_ENGINE] contractors_cache = _load_contractors_cache()")
        contractors_cache = _load_contractors_cache()

print("[VALIDATION_ENGINE] for record in records:")
        for record in records:
print("[VALIDATION_ENGINE] is_valid, errors, warnings = validator.validate_record(")
            is_valid, errors, warnings = validator.validate_record(
print("[VALIDATION_ENGINE] record,")
                record,
print("[VALIDATION_ENGINE] umbrella_id,")
                umbrella_id,
print("[VALIDATION_ENGINE] period_data,")
                period_data,
print("[VALIDATION_ENGINE] contractors_cache")
                contractors_cache
print("[VALIDATION_ENGINE] )")
            )

print("[VALIDATION_ENGINE] if not is_valid:")
            if not is_valid:
print("[VALIDATION_ENGINE] has_critical_errors = True")
                has_critical_errors = True
print("[VALIDATION_ENGINE] all_errors.extend(errors)")
                all_errors.extend(errors)

                # Store errors in DynamoDB
print("[VALIDATION_ENGINE] _store_validation_errors(file_id, errors, logger)")
                _store_validation_errors(file_id, errors, logger)
print("[VALIDATION_ENGINE] else:")
            else:
                # Add contractor/association info to record
print("[VALIDATION_ENGINE] contractor_result = validator.find_contractor(record, contractors_cache)")
                contractor_result = validator.find_contractor(record, contractors_cache)
print("[VALIDATION_ENGINE] contractor_id = contractor_result.get('contractor_id')")
                contractor_id = contractor_result.get('contractor_id')

print("[VALIDATION_ENGINE] assoc_result = validator.validate_umbrella_association(")
                assoc_result = validator.validate_umbrella_association(
print("[VALIDATION_ENGINE] contractor_id,")
                    contractor_id,
print("[VALIDATION_ENGINE] umbrella_id,")
                    umbrella_id,
print("[VALIDATION_ENGINE] period_data")
                    period_data
print("[VALIDATION_ENGINE] )")
                )
print("[VALIDATION_ENGINE] association_id = assoc_result.get('association', {}).get('AssociationID')")
                association_id = assoc_result.get('association', {}).get('AssociationID')

print("[VALIDATION_ENGINE] valid_records.append({")
                valid_records.append({
print("[VALIDATION_ENGINE] 'record': record,")
                    'record': record,
print("[VALIDATION_ENGINE] 'contractor_id': contractor_id,")
                    'contractor_id': contractor_id,
print("[VALIDATION_ENGINE] 'association_id': association_id,")
                    'association_id': association_id,
print("[VALIDATION_ENGINE] 'umbrella_id': umbrella_id,")
                    'umbrella_id': umbrella_id,
print("[VALIDATION_ENGINE] 'period_id': period_id")
                    'period_id': period_id
print("[VALIDATION_ENGINE] })")
                })

print("[VALIDATION_ENGINE] if warnings:")
            if warnings:
print("[VALIDATION_ENGINE] all_warnings.extend(warnings)")
                all_warnings.extend(warnings)
print("[VALIDATION_ENGINE] _store_validation_warnings(file_id, warnings, logger)")
                _store_validation_warnings(file_id, warnings, logger)

print("[VALIDATION_ENGINE] logger.info("Validation complete",")
        logger.info("Validation complete",
print("[VALIDATION_ENGINE] total_records=len(records),")
                   total_records=len(records),
print("[VALIDATION_ENGINE] valid_records=len(valid_records),")
                   valid_records=len(valid_records),
print("[VALIDATION_ENGINE] errors=len(all_errors),")
                   errors=len(all_errors),
print("[VALIDATION_ENGINE] warnings=len(all_warnings))")
                   warnings=len(all_warnings))

print("[VALIDATION_ENGINE] return {")
        return {
print("[VALIDATION_ENGINE] 'has_critical_errors': has_critical_errors,")
            'has_critical_errors': has_critical_errors,
print("[VALIDATION_ENGINE] 'has_warnings': len(all_warnings) > 0,")
            'has_warnings': len(all_warnings) > 0,
print("[VALIDATION_ENGINE] 'valid_records': valid_records,")
            'valid_records': valid_records,
print("[VALIDATION_ENGINE] 'errors': all_errors,")
            'errors': all_errors,
print("[VALIDATION_ENGINE] 'warnings': all_warnings,")
            'warnings': all_warnings,
print("[VALIDATION_ENGINE] 'validation_summary': {")
            'validation_summary': {
print("[VALIDATION_ENGINE] 'total_records': len(records),")
                'total_records': len(records),
print("[VALIDATION_ENGINE] 'valid_records': len(valid_records),")
                'valid_records': len(valid_records),
print("[VALIDATION_ENGINE] 'error_count': len(all_errors),")
                'error_count': len(all_errors),
print("[VALIDATION_ENGINE] 'warning_count': len(all_warnings)")
                'warning_count': len(all_warnings)
print("[VALIDATION_ENGINE] }")
            }
print("[VALIDATION_ENGINE] }")
        }

print("[VALIDATION_ENGINE] except Exception as e:")
    except Exception as e:
print("[VALIDATION_ENGINE] logger.error("Validation engine error", error=str(e))")
        logger.error("Validation engine error", error=str(e))
print("[VALIDATION_ENGINE] raise")
        raise


print("[VALIDATION_ENGINE] def _load_contractors_cache() -> dict:")
def _load_contractors_cache() -> dict:
    """Pre-load all contractors for performance"""
print("[VALIDATION_ENGINE] response = dynamodb_client.table.scan(")
    response = dynamodb_client.table.scan(
print("[VALIDATION_ENGINE] FilterExpression='EntityType = :type',")
        FilterExpression='EntityType = :type',
print("[VALIDATION_ENGINE] ExpressionAttributeValues={':type': 'Contractor'}")
        ExpressionAttributeValues={':type': 'Contractor'}
print("[VALIDATION_ENGINE] )")
    )

print("[VALIDATION_ENGINE] contractors = {}")
    contractors = {}
print("[VALIDATION_ENGINE] for item in response.get('Items', []):")
    for item in response.get('Items', []):
print("[VALIDATION_ENGINE] contractors[item['ContractorID']] = item")
        contractors[item['ContractorID']] = item

print("[VALIDATION_ENGINE] return contractors")
    return contractors


print("[VALIDATION_ENGINE] def _store_validation_errors(file_id: str, errors: list, logger: StructuredLogge")
def _store_validation_errors(file_id: str, errors: list, logger: StructuredLogger):
    """Store validation errors in DynamoDB"""

print("[VALIDATION_ENGINE] items = []")
    items = []
print("[VALIDATION_ENGINE] for idx, error in enumerate(errors, start=1):")
    for idx, error in enumerate(errors, start=1):
print("[VALIDATION_ENGINE] error_id = str(uuid.uuid4())")
        error_id = str(uuid.uuid4())

print("[VALIDATION_ENGINE] item = {")
        item = {
print("[VALIDATION_ENGINE] 'PK': f'FILE#{file_id}',")
            'PK': f'FILE#{file_id}',
print("[VALIDATION_ENGINE] 'SK': f'ERROR#{idx:03d}',")
            'SK': f'ERROR#{idx:03d}',
print("[VALIDATION_ENGINE] 'EntityType': 'ValidationError',")
            'EntityType': 'ValidationError',
print("[VALIDATION_ENGINE] 'ErrorID': error_id,")
            'ErrorID': error_id,
print("[VALIDATION_ENGINE] 'FileID': file_id,")
            'FileID': file_id,
print("[VALIDATION_ENGINE] 'ErrorType': error.get('error_type'),")
            'ErrorType': error.get('error_type'),
print("[VALIDATION_ENGINE] 'Severity': error.get('severity', 'CRITICAL'),")
            'Severity': error.get('severity', 'CRITICAL'),
print("[VALIDATION_ENGINE] 'RowNumber': error.get('row_number'),")
            'RowNumber': error.get('row_number'),
print("[VALIDATION_ENGINE] 'EmployeeID': error.get('employee_id'),")
            'EmployeeID': error.get('employee_id'),
print("[VALIDATION_ENGINE] 'ContractorName': error.get('contractor_name'),")
            'ContractorName': error.get('contractor_name'),
print("[VALIDATION_ENGINE] 'ErrorMessage': error.get('error_message'),")
            'ErrorMessage': error.get('error_message'),
print("[VALIDATION_ENGINE] 'SuggestedFix': error.get('suggested_fix'),")
            'SuggestedFix': error.get('suggested_fix'),
print("[VALIDATION_ENGINE] 'CreatedAt': datetime.utcnow().isoformat() + 'Z',")
            'CreatedAt': datetime.utcnow().isoformat() + 'Z',
print("[VALIDATION_ENGINE] 'GSI1PK': 'ERRORS',")
            'GSI1PK': 'ERRORS',
print("[VALIDATION_ENGINE] 'GSI1SK': datetime.utcnow().isoformat() + 'Z'")
            'GSI1SK': datetime.utcnow().isoformat() + 'Z'
print("[VALIDATION_ENGINE] }")
        }

print("[VALIDATION_ENGINE] items.append(item)")
        items.append(item)

    # Batch write
print("[VALIDATION_ENGINE] with dynamodb_client.table.batch_writer() as batch:")
    with dynamodb_client.table.batch_writer() as batch:
print("[VALIDATION_ENGINE] for item in items:")
        for item in items:
print("[VALIDATION_ENGINE] batch.put_item(Item=item)")
            batch.put_item(Item=item)

print("[VALIDATION_ENGINE] logger.info("Stored validation errors", count=len(items))")
    logger.info("Stored validation errors", count=len(items))


print("[VALIDATION_ENGINE] def _store_validation_warnings(file_id: str, warnings: list, logger: StructuredL")
def _store_validation_warnings(file_id: str, warnings: list, logger: StructuredLogger):
    """Store validation warnings in DynamoDB"""

print("[VALIDATION_ENGINE] items = []")
    items = []
print("[VALIDATION_ENGINE] for idx, warning in enumerate(warnings, start=1):")
    for idx, warning in enumerate(warnings, start=1):
print("[VALIDATION_ENGINE] warning_id = str(uuid.uuid4())")
        warning_id = str(uuid.uuid4())

print("[VALIDATION_ENGINE] item = {")
        item = {
print("[VALIDATION_ENGINE] 'PK': f'FILE#{file_id}',")
            'PK': f'FILE#{file_id}',
print("[VALIDATION_ENGINE] 'SK': f'WARNING#{idx:03d}',")
            'SK': f'WARNING#{idx:03d}',
print("[VALIDATION_ENGINE] 'EntityType': 'ValidationWarning',")
            'EntityType': 'ValidationWarning',
print("[VALIDATION_ENGINE] 'WarningID': warning_id,")
            'WarningID': warning_id,
print("[VALIDATION_ENGINE] 'FileID': file_id,")
            'FileID': file_id,
print("[VALIDATION_ENGINE] 'WarningType': warning.get('warning_type'),")
            'WarningType': warning.get('warning_type'),
print("[VALIDATION_ENGINE] 'RowNumber': warning.get('row_number'),")
            'RowNumber': warning.get('row_number'),
print("[VALIDATION_ENGINE] 'WarningMessage': warning.get('warning_message'),")
            'WarningMessage': warning.get('warning_message'),
print("[VALIDATION_ENGINE] 'AutoResolved': warning.get('auto_resolved', False),")
            'AutoResolved': warning.get('auto_resolved', False),
print("[VALIDATION_ENGINE] 'ResolutionNotes': warning.get('resolution_notes'),")
            'ResolutionNotes': warning.get('resolution_notes'),
print("[VALIDATION_ENGINE] 'CreatedAt': datetime.utcnow().isoformat() + 'Z',")
            'CreatedAt': datetime.utcnow().isoformat() + 'Z',
print("[VALIDATION_ENGINE] 'GSI1PK': 'WARNINGS',")
            'GSI1PK': 'WARNINGS',
print("[VALIDATION_ENGINE] 'GSI1SK': datetime.utcnow().isoformat() + 'Z'")
            'GSI1SK': datetime.utcnow().isoformat() + 'Z'
print("[VALIDATION_ENGINE] }")
        }

print("[VALIDATION_ENGINE] items.append(item)")
        items.append(item)

    # Batch write
print("[VALIDATION_ENGINE] with dynamodb_client.table.batch_writer() as batch:")
    with dynamodb_client.table.batch_writer() as batch:
print("[VALIDATION_ENGINE] for item in items:")
        for item in items:
print("[VALIDATION_ENGINE] batch.put_item(Item=item)")
            batch.put_item(Item=item)

print("[VALIDATION_ENGINE] logger.info("Stored validation warnings", count=len(items))")
    logger.info("Stored validation warnings", count=len(items))
print("[VALIDATION_ENGINE] Module load complete")
