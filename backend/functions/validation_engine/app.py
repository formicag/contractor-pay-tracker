"""
Validation Engine Lambda Function
Validates pay records against business rules

Implements Gemini improvements:
- Error vs Warning distinction (improvement #2)
- Many-to-many contractor-umbrella validation (improvement #1)
"""
print("[VALIDATION_ENGINE] Module load started")

print("[VALIDATION_ENGINE] About to execute: import json")
import json
print("[VALIDATION_ENGINE] Completed: import json")

print("[VALIDATION_ENGINE] About to execute: import uuid")
import uuid
print("[VALIDATION_ENGINE] Completed: import uuid")

print("[VALIDATION_ENGINE] About to execute: from datetime import datetime")
from datetime import datetime
print("[VALIDATION_ENGINE] Completed: from datetime import datetime")

# Import from common layer
print("[VALIDATION_ENGINE] About to execute: from common.logger import StructuredLogger")
from common.logger import StructuredLogger
print("[VALIDATION_ENGINE] Completed: from common.logger import StructuredLogger")

print("[VALIDATION_ENGINE] About to execute: from common.dynamodb import DynamoDBClient")
from common.dynamodb import DynamoDBClient
print("[VALIDATION_ENGINE] Completed: from common.dynamodb import DynamoDBClient")

print("[VALIDATION_ENGINE] About to execute: from common.validators import ValidationEngine")
from common.validators import ValidationEngine
print("[VALIDATION_ENGINE] Completed: from common.validators import ValidationEngine")


print("[VALIDATION_ENGINE] About to execute: dynamodb_client = DynamoDBClient()")
dynamodb_client = DynamoDBClient()
print(f"[VALIDATION_ENGINE] Completed: dynamodb_client = {dynamodb_client}")


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
    print("[VALIDATION_ENGINE] Creating StructuredLogger instance")
    print("[VALIDATION_ENGINE] About to execute: logger = StructuredLogger('validation-engine', context.aws_request_id)")
    logger = StructuredLogger("validation-engine", context.aws_request_id)
    print(f"[VALIDATION_ENGINE] Completed: logger = {logger}")

    print("[VALIDATION_ENGINE] Logging invocation")
    print(f"[VALIDATION_ENGINE] About to execute: logger.info('Validation engine invoked', event={event})")
    logger.info("Validation engine invoked", event=event)
    print("[VALIDATION_ENGINE] Completed: logger.info - Invocation logged")

    print("[VALIDATION_ENGINE] Entering try block")
    try:
        # Validate required event fields
        print("[VALIDATION_ENGINE] Validating required event fields")
        required_fields = ['file_id', 'umbrella_id', 'period_id', 'records']
        missing_fields = [field for field in required_fields if field not in event]

        if missing_fields:
            print(f"[VALIDATION_ENGINE] Missing required fields: {missing_fields}")
            error_msg = f"Missing required fields in event: {', '.join(missing_fields)}"
            logger.error("Validation engine error", error=error_msg, event_keys=list(event.keys()))
            return {
                'has_critical_errors': True,
                'has_warnings': False,
                'valid_records': [],
                'errors': [{
                    'error_type': 'MISSING_EVENT_FIELDS',
                    'severity': 'CRITICAL',
                    'error_message': error_msg,
                    'missing_fields': missing_fields
                }],
                'warnings': [],
                'validation_summary': {
                    'total_records': 0,
                    'valid_records': 0,
                    'error_count': 1,
                    'warning_count': 0
                }
            }

        print("[VALIDATION_ENGINE] Extracting file_id from event")
        print("[VALIDATION_ENGINE] About to execute: file_id = event['file_id']")
        file_id = event['file_id']
        print(f"[VALIDATION_ENGINE] Completed: file_id = {file_id}")

        print("[VALIDATION_ENGINE] Extracting umbrella_id from event")
        print("[VALIDATION_ENGINE] About to execute: umbrella_id = event['umbrella_id']")
        umbrella_id = event['umbrella_id']
        print(f"[VALIDATION_ENGINE] Completed: umbrella_id = {umbrella_id}")

        print("[VALIDATION_ENGINE] Extracting period_id from event")
        print("[VALIDATION_ENGINE] About to execute: period_id = event['period_id']")
        period_id = event['period_id']
        print(f"[VALIDATION_ENGINE] Completed: period_id = {period_id}")

        print("[VALIDATION_ENGINE] Extracting records from event")
        print("[VALIDATION_ENGINE] About to execute: records = event['records']")
        records = event['records']
        print(f"[VALIDATION_ENGINE] Completed: records extracted, count = {len(records)}")

        print("[VALIDATION_ENGINE] Logging validation start")
        print(f"[VALIDATION_ENGINE] About to execute: logger.info('Starting validation', file_id={file_id}, record_count={len(records)})")
        logger.info("Starting validation", file_id=file_id, record_count=len(records))
        print("[VALIDATION_ENGINE] Completed: logger.info - Validation start logged")

        # Initialize validation engine
        print("[VALIDATION_ENGINE] Creating ValidationEngine instance")
        print(f"[VALIDATION_ENGINE] About to execute: validator = ValidationEngine(dynamodb_client={dynamodb_client})")
        validator = ValidationEngine(dynamodb_client)
        print(f"[VALIDATION_ENGINE] Completed: ValidationEngine created: {validator}")

        # Get period data
        print(f"[VALIDATION_ENGINE] Getting period data for period_id: {period_id}")
        print(f"[VALIDATION_ENGINE] About to execute: dynamodb_client.table.get_item with Key PK='PERIOD#{period_id}', SK='PROFILE'")
        period_response = dynamodb_client.table.get_item(
            Key={'PK': f'PERIOD#{period_id}', 'SK': 'PROFILE'}
        )
        print(f"[VALIDATION_ENGINE] Completed: Period response received: {type(period_response)}")

        print("[VALIDATION_ENGINE] About to execute: period_data = period_response.get('Item', {})")
        period_data = period_response.get('Item', {})
        print(f"[VALIDATION_ENGINE] Completed: Period data retrieved, has_data = {bool(period_data)}, keys = {list(period_data.keys()) if period_data else []}")

        # Validate all records
        print("[VALIDATION_ENGINE] About to execute: valid_records = []")
        valid_records = []
        print(f"[VALIDATION_ENGINE] Completed: valid_records = {valid_records}")

        print("[VALIDATION_ENGINE] About to execute: all_errors = []")
        all_errors = []
        print(f"[VALIDATION_ENGINE] Completed: all_errors = {all_errors}")

        print("[VALIDATION_ENGINE] About to execute: all_warnings = []")
        all_warnings = []
        print(f"[VALIDATION_ENGINE] Completed: all_warnings = {all_warnings}")

        print("[VALIDATION_ENGINE] About to execute: has_critical_errors = False")
        has_critical_errors = False
        print(f"[VALIDATION_ENGINE] Completed: has_critical_errors = {has_critical_errors}")

        # Pre-load contractors for performance
        print("[VALIDATION_ENGINE] About to execute: contractors_cache = _load_contractors_cache()")
        contractors_cache = _load_contractors_cache()
        print(f"[VALIDATION_ENGINE] Completed: contractors_cache loaded with {len(contractors_cache)} contractors")

        print(f"[VALIDATION_ENGINE] About to execute: for loop over {len(records)} records")
        for record in records:
            print(f"[VALIDATION_ENGINE] Processing record: {record}")

            print(f"[VALIDATION_ENGINE] About to execute: validator.validate_record for record with employee_id={record.get('employee_id')}")
            is_valid, errors, warnings = validator.validate_record(
                record,
                umbrella_id,
                period_data,
                contractors_cache
            )
            print(f"[VALIDATION_ENGINE] Completed: validator.validate_record - is_valid={is_valid}, errors_count={len(errors)}, warnings_count={len(warnings)}")

            print(f"[VALIDATION_ENGINE] About to execute: if not is_valid check (is_valid={is_valid})")
            if not is_valid:
                print("[VALIDATION_ENGINE] Record is NOT valid, processing errors")

                print(f"[VALIDATION_ENGINE] About to execute: has_critical_errors = True")
                has_critical_errors = True
                print(f"[VALIDATION_ENGINE] Completed: has_critical_errors = {has_critical_errors}")

                print(f"[VALIDATION_ENGINE] About to execute: all_errors.extend(errors) - adding {len(errors)} errors")
                all_errors.extend(errors)
                print(f"[VALIDATION_ENGINE] Completed: all_errors.extend - total errors now = {len(all_errors)}")

                # Store errors in DynamoDB
                print(f"[VALIDATION_ENGINE] About to execute: _store_validation_errors(file_id={file_id}, errors={len(errors)}, logger)")
                _store_validation_errors(file_id, errors, logger)
                print("[VALIDATION_ENGINE] Completed: _store_validation_errors")
            else:
                print("[VALIDATION_ENGINE] Record IS valid, processing contractor info")

                # Add contractor/association info to record
                print(f"[VALIDATION_ENGINE] About to execute: validator.find_contractor(record={record.get('employee_id')}, contractors_cache)")
                contractor_result = validator.find_contractor(record, contractors_cache)
                print(f"[VALIDATION_ENGINE] Completed: validator.find_contractor - result keys = {list(contractor_result.keys())}")

                print(f"[VALIDATION_ENGINE] About to execute: contractor_id = contractor_result.get('contractor_id')")
                contractor_id = contractor_result.get('contractor_id')
                print(f"[VALIDATION_ENGINE] Completed: contractor_id = {contractor_id}")

                print(f"[VALIDATION_ENGINE] About to execute: validator.validate_umbrella_association(contractor_id={contractor_id}, umbrella_id={umbrella_id})")
                assoc_result = validator.validate_umbrella_association(
                    contractor_id,
                    umbrella_id,
                    period_data
                )
                print(f"[VALIDATION_ENGINE] Completed: validator.validate_umbrella_association - result keys = {list(assoc_result.keys())}")

                print(f"[VALIDATION_ENGINE] About to execute: association_id = assoc_result.get('association', {{}}).get('AssociationID')")
                association_id = assoc_result.get('association', {}).get('AssociationID')
                print(f"[VALIDATION_ENGINE] Completed: association_id = {association_id}")

                print(f"[VALIDATION_ENGINE] About to execute: valid_records.append - creating record dict")
                valid_records.append({
                    'record': record,
                    'contractor_id': contractor_id,
                    'association_id': association_id,
                    'umbrella_id': umbrella_id,
                    'period_id': period_id
                })
                print(f"[VALIDATION_ENGINE] Completed: valid_records.append - total valid records = {len(valid_records)}")

            print(f"[VALIDATION_ENGINE] About to execute: if warnings check (warnings_count={len(warnings)})")
            if warnings:
                print(f"[VALIDATION_ENGINE] Warnings found, processing {len(warnings)} warnings")

                print(f"[VALIDATION_ENGINE] About to execute: all_warnings.extend(warnings) - adding {len(warnings)} warnings")
                all_warnings.extend(warnings)
                print(f"[VALIDATION_ENGINE] Completed: all_warnings.extend - total warnings now = {len(all_warnings)}")

                print(f"[VALIDATION_ENGINE] About to execute: _store_validation_warnings(file_id={file_id}, warnings={len(warnings)}, logger)")
                _store_validation_warnings(file_id, warnings, logger)
                print("[VALIDATION_ENGINE] Completed: _store_validation_warnings")

        print(f"[VALIDATION_ENGINE] Completed: for loop over all {len(records)} records")

        print(f"[VALIDATION_ENGINE] About to execute: logger.info('Validation complete') with stats")
        logger.info("Validation complete",
                   total_records=len(records),
                   valid_records=len(valid_records),
                   errors=len(all_errors),
                   warnings=len(all_warnings))
        print("[VALIDATION_ENGINE] Completed: logger.info - Validation complete logged")

        print("[VALIDATION_ENGINE] About to execute: return validation results dictionary")
        result = {
            'hasCriticalErrors': has_critical_errors,
            'hasWarnings': len(all_warnings) > 0,
            'validatedRecords': valid_records,
            'errors': all_errors,
            'warnings': all_warnings,
            'validationSummary': {
                'totalRecords': len(records),
                'validRecords': len(valid_records),
                'errorCount': len(all_errors),
                'warningCount': len(all_warnings)
            }
        }
        print(f"[VALIDATION_ENGINE] Completed: return dict created - has_critical_errors={has_critical_errors}, valid_records={len(valid_records)}, errors={len(all_errors)}, warnings={len(all_warnings)}")
        return result

    except Exception as e:
        print(f"[VALIDATION_ENGINE] Exception caught: {type(e).__name__}: {str(e)}")
        print(f"[VALIDATION_ENGINE] About to execute: logger.error('Validation engine error', error={str(e)})")
        logger.error("Validation engine error", error=str(e))
        print("[VALIDATION_ENGINE] Completed: logger.error")
        print("[VALIDATION_ENGINE] About to execute: raise exception")
        raise


def _load_contractors_cache() -> dict:
    """Pre-load all contractors for performance"""
    print("[VALIDATION_ENGINE] _load_contractors_cache() called")

    print("[VALIDATION_ENGINE] About to execute: dynamodb_client.table.scan with FilterExpression='EntityType = :type'")
    response = dynamodb_client.table.scan(
        FilterExpression='EntityType = :type',
        ExpressionAttributeValues={':type': 'Contractor'}
    )
    print(f"[VALIDATION_ENGINE] Completed: dynamodb_client.table.scan - response type = {type(response)}")

    print("[VALIDATION_ENGINE] About to execute: contractors = {}")
    contractors = {}
    print(f"[VALIDATION_ENGINE] Completed: contractors = {contractors}")

    print(f"[VALIDATION_ENGINE] About to execute: for loop over {len(response.get('Items', []))} items")
    for item in response.get('Items', []):
        print(f"[VALIDATION_ENGINE] Processing contractor item: ContractorID = {item.get('ContractorID')}")

        print(f"[VALIDATION_ENGINE] About to execute: contractors[{item.get('ContractorID')}] = item")
        contractors[item['ContractorID']] = item
        print(f"[VALIDATION_ENGINE] Completed: Added contractor to cache, total = {len(contractors)}")

    print(f"[VALIDATION_ENGINE] Completed: for loop over items - total contractors cached = {len(contractors)}")

    print(f"[VALIDATION_ENGINE] About to execute: return contractors dict with {len(contractors)} entries")
    return contractors


def _store_validation_errors(file_id: str, errors: list, logger: StructuredLogger):
    """Store validation errors in DynamoDB"""
    print(f"[VALIDATION_ENGINE] _store_validation_errors() called with file_id={file_id}, errors_count={len(errors)}")

    print("[VALIDATION_ENGINE] About to execute: items = []")
    items = []
    print(f"[VALIDATION_ENGINE] Completed: items = {items}")

    print(f"[VALIDATION_ENGINE] About to execute: for loop over {len(errors)} errors with enumerate")
    for idx, error in enumerate(errors, start=1):
        print(f"[VALIDATION_ENGINE] Processing error {idx}/{len(errors)}: type={error.get('error_type')}, row={error.get('row_number')}")

        print(f"[VALIDATION_ENGINE] About to execute: error_id = str(uuid.uuid4())")
        error_id = str(uuid.uuid4())
        print(f"[VALIDATION_ENGINE] Completed: error_id = {error_id}")

        print(f"[VALIDATION_ENGINE] About to execute: create item dict for error {idx}")
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
        print(f"[VALIDATION_ENGINE] Completed: item dict created with PK={item['PK']}, SK={item['SK']}")

        print(f"[VALIDATION_ENGINE] About to execute: items.append(item)")
        items.append(item)
        print(f"[VALIDATION_ENGINE] Completed: items.append - total items = {len(items)}")

    print(f"[VALIDATION_ENGINE] Completed: for loop over errors - total items to write = {len(items)}")

    # Batch write
    print(f"[VALIDATION_ENGINE] About to execute: batch_writer context manager for {len(items)} items")
    with dynamodb_client.table.batch_writer() as batch:
        print(f"[VALIDATION_ENGINE] Entered batch_writer context")

        print(f"[VALIDATION_ENGINE] About to execute: for loop over {len(items)} items for batch write")
        for item in items:
            print(f"[VALIDATION_ENGINE] About to execute: batch.put_item for PK={item['PK']}, SK={item['SK']}")
            batch.put_item(Item=item)
            print(f"[VALIDATION_ENGINE] Completed: batch.put_item for {item['SK']}")

        print(f"[VALIDATION_ENGINE] Completed: for loop over items in batch")

    print("[VALIDATION_ENGINE] Completed: batch_writer context manager - all items written")

    print(f"[VALIDATION_ENGINE] About to execute: logger.info('Stored validation errors', count={len(items)})")
    logger.info("Stored validation errors", count=len(items))
    print("[VALIDATION_ENGINE] Completed: logger.info - stored errors logged")


def _store_validation_warnings(file_id: str, warnings: list, logger: StructuredLogger):
    """Store validation warnings in DynamoDB"""
    print(f"[VALIDATION_ENGINE] _store_validation_warnings() called with file_id={file_id}, warnings_count={len(warnings)}")

    print("[VALIDATION_ENGINE] About to execute: items = []")
    items = []
    print(f"[VALIDATION_ENGINE] Completed: items = {items}")

    print(f"[VALIDATION_ENGINE] About to execute: for loop over {len(warnings)} warnings with enumerate")
    for idx, warning in enumerate(warnings, start=1):
        print(f"[VALIDATION_ENGINE] Processing warning {idx}/{len(warnings)}: type={warning.get('warning_type')}, row={warning.get('row_number')}")

        print(f"[VALIDATION_ENGINE] About to execute: warning_id = str(uuid.uuid4())")
        warning_id = str(uuid.uuid4())
        print(f"[VALIDATION_ENGINE] Completed: warning_id = {warning_id}")

        print(f"[VALIDATION_ENGINE] About to execute: create item dict for warning {idx}")
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
        print(f"[VALIDATION_ENGINE] Completed: item dict created with PK={item['PK']}, SK={item['SK']}")

        print(f"[VALIDATION_ENGINE] About to execute: items.append(item)")
        items.append(item)
        print(f"[VALIDATION_ENGINE] Completed: items.append - total items = {len(items)}")

    print(f"[VALIDATION_ENGINE] Completed: for loop over warnings - total items to write = {len(items)}")

    # Batch write
    print(f"[VALIDATION_ENGINE] About to execute: batch_writer context manager for {len(items)} items")
    with dynamodb_client.table.batch_writer() as batch:
        print(f"[VALIDATION_ENGINE] Entered batch_writer context")

        print(f"[VALIDATION_ENGINE] About to execute: for loop over {len(items)} items for batch write")
        for item in items:
            print(f"[VALIDATION_ENGINE] About to execute: batch.put_item for PK={item['PK']}, SK={item['SK']}")
            batch.put_item(Item=item)
            print(f"[VALIDATION_ENGINE] Completed: batch.put_item for {item['SK']}")

        print(f"[VALIDATION_ENGINE] Completed: for loop over items in batch")

    print("[VALIDATION_ENGINE] Completed: batch_writer context manager - all items written")

    print(f"[VALIDATION_ENGINE] About to execute: logger.info('Stored validation warnings', count={len(items)})")
    logger.info("Stored validation warnings", count=len(items))
    print("[VALIDATION_ENGINE] Completed: logger.info - stored warnings logged")

print("[VALIDATION_ENGINE] Module load complete")
