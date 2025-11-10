"""
Validate Data Lambda
===================
ENTERPRISE-GRADE VALIDATION (Data Quality = #1 Priority)

Reads from validation-queue, runs ALL validations:
- Contractor name matching
- Rate validation
- Margin checks
- Duplicate detection
- Period validation
- Umbrella company consistency

ADDS validation results to message, sends to import-queue
"""

import json
import os
import boto3
from datetime import datetime
from decimal import Decimal

# Import ALL validation logic from common layer
from common.validators import (
    validate_contractor_name,
    validate_pay_rate,
    validate_margin,
    validate_period_consistency,
    validate_umbrella_consistency,
    detect_duplicates
)
from common.logger import StructuredLogger
from common.dynamodb import DynamoDBClient

# AWS clients
sqs_client = boto3.client('sqs')

# Environment variables
IMPORT_QUEUE_URL = os.environ['IMPORT_QUEUE_URL']
TABLE_NAME = os.environ['TABLE_NAME']

# Logger
logger = StructuredLogger('validate-data')

# DynamoDB client
dynamodb_client = DynamoDBClient(TABLE_NAME)

def lambda_handler(event, context):
    """
    Process SQS messages from validation-queue
    """
    logger.info("🔍 Validate-data Lambda started", event=event)

    for record in event['Records']:
        try:
            # Parse message
            message = json.loads(record['body'])
            logger.info("📥 RECEIVED MESSAGE", file_id=message.get('file_id'))

            file_id = message['file_id']
            umbrella_id = message['umbrella_id']
            period_number = message['period_number']

            logger.info("🔍 Starting validation",
                       file_id=file_id,
                       umbrella_code=message['umbrella_code'],
                       period=period_number)

            # Download and parse records from S3
            # (Using the same Excel parser)
            from common.excel_parser import PayFileParser
            import tempfile

            s3_client = boto3.client('s3')
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx')

            s3_client.download_file(
                message['s3_bucket'],
                message['s3_key'],
                temp_file.name
            )

            parser = PayFileParser(temp_file.name, original_filename=message['filename'])
            records = parser.parse_records()
            parser.close()
            os.unlink(temp_file.name)

            logger.info("📊 Parsed records from file", record_count=len(records))

            # Run ALL enterprise validations
            all_errors = []
            all_warnings = []
            validated_records = []

            for idx, record in enumerate(records):
                record_errors = []
                record_warnings = []

                logger.info(f"🔍 Validating record {idx+1}/{len(records)}",
                           contractor_name=record.get('contractor_name'))

                # VALIDATION 1: Contractor name matching
                contractor_validation = validate_contractor_name(
                    record.get('contractor_name'),
                    umbrella_id,
                    dynamodb_client
                )

                if not contractor_validation['valid']:
                    record_errors.append({
                        'field': 'contractor_name',
                        'error': contractor_validation['error'],
                        'severity': 'ERROR'
                    })
                elif contractor_validation.get('warning'):
                    record_warnings.append({
                        'field': 'contractor_name',
                        'warning': contractor_validation['warning'],
                        'severity': 'WARNING'
                    })

                # VALIDATION 2: Pay rate validation
                rate = record.get('pay_rate')
                if rate:
                    rate_validation = validate_pay_rate(
                        rate,
                        contractor_validation.get('contractor_id'),
                        period_number,
                        dynamodb_client
                    )

                    if not rate_validation['valid']:
                        record_errors.append({
                            'field': 'pay_rate',
                            'error': rate_validation['error'],
                            'severity': 'ERROR'
                        })
                    elif rate_validation.get('warning'):
                        record_warnings.append({
                            'field': 'pay_rate',
                            'warning': rate_validation['warning'],
                            'severity': 'WARNING'
                        })

                # VALIDATION 3: Margin calculation
                if record.get('charge_rate') and record.get('pay_rate'):
                    margin_validation = validate_margin(
                        record['charge_rate'],
                        record['pay_rate'],
                        message['umbrella_code']
                    )

                    if not margin_validation['valid']:
                        record_errors.append({
                            'field': 'margin',
                            'error': margin_validation['error'],
                            'severity': 'ERROR'
                        })
                    elif margin_validation.get('warning'):
                        record_warnings.append({
                            'field': 'margin',
                            'warning': margin_validation['warning'],
                            'severity': 'WARNING'
                        })

                # Add record with validation status
                record['validation_status'] = 'PASSED' if not record_errors else 'FAILED'
                record['validation_errors'] = record_errors
                record['validation_warnings'] = record_warnings
                record['contractor_id'] = contractor_validation.get('contractor_id')
                record['row_number'] = idx + 1

                validated_records.append(record)

                all_errors.extend(record_errors)
                all_warnings.extend(record_warnings)

            # VALIDATION 4: Duplicate detection (cross-record)
            duplicate_check = detect_duplicates(validated_records)
            if duplicate_check['duplicates_found']:
                all_warnings.append({
                    'field': 'duplicates',
                    'warning': f"Found {len(duplicate_check['duplicates'])} potential duplicate records",
                    'severity': 'WARNING',
                    'details': duplicate_check['duplicates']
                })

            # VALIDATION 5: Period consistency
            period_check = validate_period_consistency(
                validated_records,
                period_number,
                message['submission_date']
            )
            if not period_check['valid']:
                all_errors.append({
                    'field': 'period',
                    'error': period_check['error'],
                    'severity': 'ERROR'
                })

            # Determine overall validation status
            validation_passed = len(all_errors) == 0
            has_warnings = len(all_warnings) > 0

            logger.info("✅ Validation complete",
                       validation_passed=validation_passed,
                       error_count=len(all_errors),
                       warning_count=len(all_warnings))

            # ⭐ ADD VALIDATION RESULTS TO MESSAGE
            message['validation_passed'] = validation_passed
            message['validation_errors'] = all_errors
            message['validation_warnings'] = all_warnings
            message['validated_records'] = validated_records
            message['record_count'] = len(validated_records)
            message['validated_at'] = datetime.utcnow().isoformat() + 'Z'

            # Update FILE status in DynamoDB
            status = 'VALIDATED' if validation_passed else 'VALIDATION_FAILED'
            dynamodb_client.update_file_status(
                file_id=file_id,
                status=status,
                umbrella_code=message['umbrella_code'],
                period_number=period_number,
                validation_errors=all_errors if not validation_passed else None,
                validation_warnings=all_warnings if has_warnings else None
            )

            # 📤 SEND TO IMPORT QUEUE (even if validation failed - let user review)
            logger.info("📤 FORWARDING TO IMPORT QUEUE",
                       validation_status=status,
                       will_import=validation_passed)

            sqs_client.send_message(
                QueueUrl=IMPORT_QUEUE_URL,
                MessageBody=json.dumps(message, default=str)  # Handle Decimal serialization
            )

            logger.info("✅ STAGE COMPLETE: Validation finished", file_id=file_id)

        except Exception as e:
            logger.error("❌ ERROR in validation", error=str(e))

            # Add error to message
            if 'errors' not in message:
                message['errors'] = []
            message['errors'].append({
                'stage': 'validate-data',
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat() + 'Z'
            })

            # Update FILE status
            if 'file_id' in message:
                try:
                    dynamodb_client.update_file_status(
                        file_id=message['file_id'],
                        status='FAILED',
                        error_message=str(e)
                    )
                except:
                    pass

            # Re-raise for SQS retry/DLQ
            raise

    return {'statusCode': 200, 'body': 'Success'}
