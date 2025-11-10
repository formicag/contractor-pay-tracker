"""
Import Records Lambda
====================
Final stage: Import validated records to DynamoDB

Reads from import-queue, writes to DynamoDB in batches
Updates FILE status to COMPLETED
"""

import json
import os
import boto3
from datetime import datetime
from decimal import Decimal

from common.logger import StructuredLogger
from common.dynamodb import DynamoDBClient

# AWS clients
dynamodb = boto3.resource('dynamodb')

# Environment variables
TABLE_NAME = os.environ['TABLE_NAME']

# Logger
logger = StructuredLogger('import-records')

# DynamoDB client (reads TABLE_NAME from environment)
dynamodb_client = DynamoDBClient()

def lambda_handler(event, context):
    """
    Process SQS messages from import-queue
    """
    logger.info("💾 Import-records Lambda started", event=event)

    for record in event['Records']:
        try:
            # Parse message
            message = json.loads(record['body'])
            logger.info("📥 RECEIVED MESSAGE", file_id=message.get('file_id'))

            file_id = message['file_id']
            umbrella_id = message['umbrella_id']
            period_number = message['period_number']
            validation_passed = message.get('validation_passed', False)

            logger.info("💾 Starting import",
                       file_id=file_id,
                       validation_passed=validation_passed,
                       record_count=len(message.get('validated_records', [])))

            # Only import if validation passed
            if not validation_passed:
                logger.info("⚠️  Validation failed, skipping import. FILE marked as VALIDATION_FAILED",
                           error_count=len(message.get('validation_errors', [])))

                # Update FILE status
                dynamodb_client.update_file_status(
                    file_id=file_id,
                    status='VALIDATION_FAILED',
                    error_message=f"Validation failed with {len(message.get('validation_errors', []))} errors"
                )

                # Still return success (don't retry)
                return {'statusCode': 200, 'body': 'Validation failed, no import'}

            # Import records to DynamoDB in batches
            validated_records = message.get('validated_records', [])
            table = dynamodb.Table(TABLE_NAME)

            imported_count = 0
            failed_count = 0

            logger.info("📝 Importing records in batches")

            with table.batch_writer() as batch:
                for idx, pay_record in enumerate(validated_records):
                    try:
                        # Create TimeRecord item
                        item = {
                            'PK': f'FILE#{file_id}',
                            'SK': f'RECORD#{idx:04d}',
                            'EntityType': 'TimeRecord',
                            'FileID': file_id,
                            'UmbrellaID': umbrella_id,
                            'PeriodNumber': period_number,
                            'ContractorID': pay_record.get('contractor_id'),
                            'ContractorName': pay_record.get('contractor_name'),
                            'EmployeeID': pay_record.get('employee_id'),
                            'PayRate': Decimal(str(pay_record.get('pay_rate', 0))),
                            'ChargeRate': Decimal(str(pay_record.get('charge_rate', 0))),
                            'Units': Decimal(str(pay_record.get('units', 0))),
                            'PayAmount': Decimal(str(pay_record.get('pay_amount', 0))),
                            'ChargeAmount': Decimal(str(pay_record.get('charge_amount', 0))),
                            'Margin': Decimal(str(pay_record.get('margin', 0))),
                            'MarginPercent': Decimal(str(pay_record.get('margin_percent', 0))),
                            'RowNumber': pay_record.get('row_number', idx + 1),
                            'ValidationStatus': pay_record.get('validation_status', 'PASSED'),
                            'ValidationWarnings': pay_record.get('validation_warnings', []),
                            'CreatedAt': datetime.utcnow().isoformat() + 'Z',
                            # GSI1 for querying by contractor
                            'GSI1PK': f'CONTRACTOR#{pay_record.get("contractor_id")}',
                            'GSI1SK': f'PERIOD#{period_number}#FILE#{file_id}'
                        }

                        batch.put_item(Item=item)
                        imported_count += 1

                        if (idx + 1) % 25 == 0:
                            logger.info(f"  Progress: {idx + 1}/{len(validated_records)} records")

                    except Exception as e:
                        logger.error(f"Failed to import record {idx}", error=str(e))
                        failed_count += 1

            logger.info("✅ Import complete",
                       imported=imported_count,
                       failed=failed_count,
                       total=len(validated_records))

            # ⭐ ADD IMPORT RESULTS TO MESSAGE
            message['records_imported'] = imported_count
            message['records_failed'] = failed_count
            message['import_complete'] = True
            message['imported_at'] = datetime.utcnow().isoformat() + 'Z'

            # Update FILE status to COMPLETED
            dynamodb_client.update_file_status(
                file_id=file_id,
                status='COMPLETED',
                umbrella_code=message['umbrella_code'],
                period_number=period_number,
                record_count=imported_count,
                validation_warnings=message.get('validation_warnings')
            )

            logger.info("✅ STAGE COMPLETE: Import successful", file_id=file_id)

            # No next queue - this is the final stage!
            # Results are in DynamoDB

        except Exception as e:
            logger.error("❌ ERROR in import", error=str(e))

            # Add error to message
            if 'errors' not in message:
                message['errors'] = []
            message['errors'].append({
                'stage': 'import-records',
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
