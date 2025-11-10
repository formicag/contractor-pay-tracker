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

print("[VALIDATION_ENGINE] About to execute: from common.validators_enterprise import EnterpriseValidationEngine")
from common.validators_enterprise import EnterpriseValidationEngine
print("[VALIDATION_ENGINE] Completed: from common.validators_enterprise import EnterpriseValidationEngine")


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
                'validated_records': [],
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

        # Initialize enterprise validation engine
        print("[VALIDATION_ENGINE] Creating EnterpriseValidationEngine instance")
        print(f"[VALIDATION_ENGINE] About to execute: validator = EnterpriseValidationEngine(dynamodb_client={dynamodb_client})")
        validator = EnterpriseValidationEngine(dynamodb_client)
        print(f"[VALIDATION_ENGINE] Completed: EnterpriseValidationEngine created: {validator}")

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

        # Validate all records with enterprise validation
        print("[VALIDATION_ENGINE] About to execute: valid_records = []")
        valid_records = []
        print(f"[VALIDATION_ENGINE] Completed: valid_records = {valid_records}")

        print("[VALIDATION_ENGINE] About to execute: all_validation_checks = []")
        all_validation_checks = []
        print(f"[VALIDATION_ENGINE] Completed: all_validation_checks = {all_validation_checks}")

        print("[VALIDATION_ENGINE] About to execute: has_critical_errors = False")
        has_critical_errors = False
        print(f"[VALIDATION_ENGINE] Completed: has_critical_errors = {has_critical_errors}")

        print("[VALIDATION_ENGINE] About to execute: Get file_name from event")
        file_name = event.get('file_name', 'unknown.xlsx')
        print(f"[VALIDATION_ENGINE] Completed: file_name = {file_name}")

        print(f"[VALIDATION_ENGINE] About to execute: for loop over {len(records)} records")
        for record_index, record in enumerate(records):
            print(f"[VALIDATION_ENGINE] Processing record {record_index + 1}/{len(records)}: {record.get('contractor_name', 'Unknown')}")

            print(f"[VALIDATION_ENGINE] About to execute: validator.validate_record for record {record_index + 1}")
            is_valid, validation_checks = validator.validate_record(
                record,
                umbrella_id,
                period_data,
                file_name
            )
            print(f"[VALIDATION_ENGINE] Completed: validator.validate_record - is_valid={is_valid}, checks_count={len(validation_checks)}")

            # Separate critical failures from warnings
            critical_failures = [c for c in validation_checks if not c.passed and c.severity == 'CRITICAL']
            warnings = [c for c in validation_checks if not c.passed and c.severity == 'WARNING']
            passed_checks = [c for c in validation_checks if c.passed]

            print(f"[VALIDATION_ENGINE] Record {record_index + 1}: critical_failures={len(critical_failures)}, warnings={len(warnings)}, passed={len(passed_checks)}")

            # Store ALL checks (passed and failed) for compliance audit trail
            for check in validation_checks:
                check_dict = check.to_dict()
                check_dict['record_index'] = record_index
                check_dict['contractor_name'] = record.get('contractor_name', 'Unknown')
                check_dict['employee_id'] = record.get('employee_id', '')
                all_validation_checks.append(check_dict)

            print(f"[VALIDATION_ENGINE] About to execute: if critical_failures check (count={len(critical_failures)})")
            if len(critical_failures) > 0:
                print(f"[VALIDATION_ENGINE] Record {record_index + 1} has CRITICAL failures - REJECTING import")

                print(f"[VALIDATION_ENGINE] About to execute: has_critical_errors = True")
                has_critical_errors = True
                print(f"[VALIDATION_ENGINE] Completed: has_critical_errors = {has_critical_errors}")

                # DO NOT add to valid_records - record is rejected
                print(f"[VALIDATION_ENGINE] Record {record_index + 1} NOT added to valid_records (critical failures)")
            else:
                print(f"[VALIDATION_ENGINE] Record {record_index + 1} has no CRITICAL failures - ACCEPTING import (may have warnings)")

                # Add record to valid records even if it has warnings
                # Warnings are informational only and don't block import
                print(f"[VALIDATION_ENGINE] About to execute: valid_records.append for record {record_index + 1}")
                valid_records.append({
                    'record': record,
                    'contractor_id': record.get('contractor_id', ''),
                    'umbrella_id': umbrella_id,
                    'period_id': period_id,
                    'warnings': [w.to_dict() for w in warnings] if warnings else []
                })
                print(f"[VALIDATION_ENGINE] Completed: valid_records.append - total valid records = {len(valid_records)}")

        print(f"[VALIDATION_ENGINE] Completed: for loop over all {len(records)} records")

        # Count total errors and warnings from all checks
        total_critical_failures = sum(1 for c in all_validation_checks if not c.get('passed') and c.get('severity') == 'CRITICAL')
        total_warnings = sum(1 for c in all_validation_checks if not c.get('passed') and c.get('severity') == 'WARNING')
        total_passed = sum(1 for c in all_validation_checks if c.get('passed'))

        print(f"[VALIDATION_ENGINE] About to execute: logger.info('Validation complete') with stats")
        logger.info("Validation complete",
                   total_records=len(records),
                   valid_records=len(valid_records),
                   total_checks=len(all_validation_checks),
                   passed_checks=total_passed,
                   critical_failures=total_critical_failures,
                   warnings=total_warnings)
        print("[VALIDATION_ENGINE] Completed: logger.info - Validation complete logged")

        print("[VALIDATION_ENGINE] About to execute: return validation results dictionary with ALL validation checks")
        result = {
            'has_critical_errors': has_critical_errors,
            'has_warnings': total_warnings > 0,
            'validated_records': valid_records,
            'all_validation_checks': all_validation_checks,  # FULL AUDIT TRAIL
            'validation_summary': {
                'total_records': len(records),
                'valid_records': len(valid_records),
                'rejected_records': len(records) - len(valid_records),
                'total_checks': len(all_validation_checks),
                'passed_checks': total_passed,
                'critical_failures': total_critical_failures,
                'warnings': total_warnings
            }
        }
        print(f"[VALIDATION_ENGINE] Completed: return dict created - has_critical_errors={has_critical_errors}, valid_records={len(valid_records)}, total_checks={len(all_validation_checks)}")

        # Store validation snapshot with ALL checks for compliance
        print("[VALIDATION_ENGINE] About to execute: _store_validation_snapshot with all checks")
        _store_validation_snapshot(file_id, umbrella_id, period_data, result, logger)
        print("[VALIDATION_ENGINE] Completed: _store_validation_snapshot")

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


def _build_rates_cache(records, contractors_cache):
    """Build cache of normal rates from current batch for overtime validation"""
    print("[VALIDATION_ENGINE] _build_rates_cache() called")

    rates_cache = {}

    for record in records:
        if record.get('record_type') != 'NORMAL':
            continue

        employee_id = record.get('employee_id')
        day_rate = record.get('day_rate')

        if not employee_id or not day_rate:
            continue

        # Find contractor by employee_id
        for contractor_id, contractor in contractors_cache.items():
            if contractor.get('EmployeeID') == employee_id:
                rates_cache[contractor_id] = day_rate
                print(f"[VALIDATION_ENGINE] Added rate {day_rate} for contractor {contractor_id}")
                break

    print(f"[VALIDATION_ENGINE] _build_rates_cache() returning {len(rates_cache)} rates")
    return rates_cache


def _store_validation_snapshot(
    file_id: str,
    umbrella_id: str,
    period_data: dict,
    validation_results: dict,
    logger: StructuredLogger
):
    """
    Store a complete validation snapshot in DynamoDB

    Args:
        file_id: File ID being validated
        validation_results: Complete validation results from lambda_handler
        event: Original event data (for metadata)
        logger: Logger instance
    """
    print(f"[VALIDATION_ENGINE] _store_validation_snapshot() called with file_id={file_id}")

    # Extract metadata
    period_id = period_data.get('PeriodID', 'UNKNOWN')
    period_name = period_data.get('PeriodName', 'UNKNOWN')

    # Get file metadata
    print(f"[VALIDATION_ENGINE] Fetching file metadata for file_id={file_id}")
    file_metadata = dynamodb_client.get_file_metadata(file_id)
    file_name = file_metadata.get('OriginalFilename', 'UNKNOWN') if file_metadata else 'UNKNOWN'

    # Extract summary and ALL validation checks
    has_critical_errors = validation_results.get('has_critical_errors', False)
    status = 'FAILED' if has_critical_errors else 'PASSED'

    validation_summary = validation_results.get('validation_summary', {})
    all_checks = validation_results.get('all_validation_checks', [])

    # Create timestamp
    validated_at = datetime.utcnow().isoformat() + 'Z'

    # Create enterprise validation snapshot with ALL checks for audit trail
    snapshot_item = {
        'PK': f'FILE#{file_id}',
        'SK': f'VALIDATION#{validated_at}',
        'EntityType': 'ValidationSnapshot',
        'FileID': file_id,
        'ValidatedAt': validated_at,
        'Status': status,
        'TotalRecords': validation_summary.get('total_records', 0),
        'ValidRecords': validation_summary.get('valid_records', 0),
        'RejectedRecords': validation_summary.get('rejected_records', 0),
        'TotalChecks': validation_summary.get('total_checks', 0),
        'PassedChecks': validation_summary.get('passed_checks', 0),
        'CriticalFailures': validation_summary.get('critical_failures', 0),
        'Warnings': validation_summary.get('warnings', 0),
        'AllValidationChecks': all_checks,  # FULL AUDIT TRAIL - EVERY CHECK
        'UmbrellaID': umbrella_id,
        'PeriodID': period_id,
        'PeriodName': period_name,
        'FileName': file_name,
        'GSI1PK': 'VALIDATIONS',
        'GSI1SK': validated_at
    }

    print(f"[VALIDATION_ENGINE] Created snapshot with {len(all_checks)} total checks (Status={status})")

    # Convert any float values to Decimal for DynamoDB
    from decimal import Decimal

    def convert_floats_to_decimal(obj):
        """Recursively convert floats to Decimal for DynamoDB compatibility"""
        if isinstance(obj, dict):
            return {k: convert_floats_to_decimal(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [convert_floats_to_decimal(item) for item in obj]
        elif isinstance(obj, float):
            return Decimal(str(obj))
        else:
            return obj

    snapshot_item = convert_floats_to_decimal(snapshot_item)

    # Store in DynamoDB
    print(f"[VALIDATION_ENGINE] Storing validation snapshot in DynamoDB")
    dynamodb_client.table.put_item(Item=snapshot_item)

    logger.info(
        "Stored validation snapshot",
        file_id=file_id,
        status=status,
        total_rules=len(validation_rules),
        passed_rules=snapshot_item['PassedRules'],
        failed_rules=snapshot_item['FailedRules']
    )

    print(f"[VALIDATION_ENGINE] Validation snapshot stored successfully")
    return snapshot_item


print("[VALIDATION_ENGINE] Module load complete")
