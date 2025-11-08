"""
Cleanup Handler Lambda Function
Daily maintenance and cleanup tasks

Performs:
1. Delete old uploaded files from S3 older than RETENTION_DAYS
2. Archive or delete old records from DynamoDB
3. Clean up failed/error state files
4. Remove orphaned validation errors/warnings
5. Maintain audit log of cleanup operations
6. Return detailed cleanup statistics
"""

print("[CLEANUP_HANDLER] ==================== MODULE LOAD START ====================")
print("[CLEANUP_HANDLER] Importing json module")
import json
print(f"[CLEANUP_HANDLER] json module imported: {json}")

print("[CLEANUP_HANDLER] Importing os module")
import os
print(f"[CLEANUP_HANDLER] os module imported: {os}")

print("[CLEANUP_HANDLER] Importing datetime and timedelta from datetime module")
from datetime import datetime, timedelta, timezone
print(f"[CLEANUP_HANDLER] datetime, timedelta, timezone imported: {datetime}, {timedelta}, {timezone}")

print("[CLEANUP_HANDLER] Importing boto3 module")
import boto3
print(f"[CLEANUP_HANDLER] boto3 module imported: {boto3}")

print("[CLEANUP_HANDLER] Importing uuid module")
import uuid
print(f"[CLEANUP_HANDLER] uuid module imported: {uuid}")

print("[CLEANUP_HANDLER] Importing StructuredLogger from common.logger")
from common.logger import StructuredLogger
print(f"[CLEANUP_HANDLER] StructuredLogger imported: {StructuredLogger}")

print("[CLEANUP_HANDLER] Importing DynamoDBClient from common.dynamodb")
from common.dynamodb import DynamoDBClient
print(f"[CLEANUP_HANDLER] DynamoDBClient imported: {DynamoDBClient}")

print("[CLEANUP_HANDLER] Importing boto3 dynamodb conditions")
from boto3.dynamodb.conditions import Key, Attr
print(f"[CLEANUP_HANDLER] Key, Attr imported: {Key}, {Attr}")

print("[CLEANUP_HANDLER] Creating DynamoDBClient instance")
dynamodb_client = DynamoDBClient()
print(f"[CLEANUP_HANDLER] dynamodb_client created: {dynamodb_client}")

print("[CLEANUP_HANDLER] Creating boto3 S3 client")
s3_client = boto3.client('s3')
print(f"[CLEANUP_HANDLER] s3_client created: {s3_client}")

print("[CLEANUP_HANDLER] Creating boto3 DynamoDB resource for direct table access")
dynamodb_resource = boto3.resource('dynamodb')
print(f"[CLEANUP_HANDLER] dynamodb_resource created: {dynamodb_resource}")

print("[CLEANUP_HANDLER] Reading TABLE_NAME from environment")
TABLE_NAME = os.environ.get('TABLE_NAME')
print(f"[CLEANUP_HANDLER] TABLE_NAME = {TABLE_NAME}")

print("[CLEANUP_HANDLER] Reading S3_BUCKET_NAME from environment")
S3_BUCKET_NAME = os.environ.get('S3_BUCKET_NAME')
print(f"[CLEANUP_HANDLER] S3_BUCKET_NAME = {S3_BUCKET_NAME}")

print("[CLEANUP_HANDLER] Reading RETENTION_DAYS from environment (default 30)")
RETENTION_DAYS = int(os.environ.get('RETENTION_DAYS', '30'))
print(f"[CLEANUP_HANDLER] RETENTION_DAYS = {RETENTION_DAYS}")

print("[CLEANUP_HANDLER] Getting table reference from dynamodb_resource")
table = dynamodb_resource.Table(TABLE_NAME)
print(f"[CLEANUP_HANDLER] table reference: {table}")

print("[CLEANUP_HANDLER] ==================== MODULE LOAD COMPLETE ====================")


def lambda_handler(event, context):
    """
    Cleanup handler main entry point
    Performs comprehensive cleanup of old data from S3 and DynamoDB
    """
    print("[CLEANUP_HANDLER] ==================== LAMBDA_HANDLER INVOKED ====================")
    print(f"[CLEANUP_HANDLER] Event received: {json.dumps(event)}")
    print(f"[CLEANUP_HANDLER] Context: {context}")
    print(f"[CLEANUP_HANDLER] Request ID: {context.aws_request_id}")

    print("[CLEANUP_HANDLER] Creating StructuredLogger instance")
    logger = StructuredLogger("cleanup-handler", context.aws_request_id)
    print(f"[CLEANUP_HANDLER] Logger created: {logger}")

    print("[CLEANUP_HANDLER] Logging invocation via logger")
    logger.info("Cleanup handler invoked", event=event, retention_days=RETENTION_DAYS)
    print("[CLEANUP_HANDLER] Invocation logged")

    # Initialize statistics
    print("[CLEANUP_HANDLER] Initializing cleanup statistics dictionary")
    stats = {
        's3_files_deleted': 0,
        's3_files_failed': 0,
        's3_bytes_freed': 0,
        'dynamodb_files_archived': 0,
        'dynamodb_records_deleted': 0,
        'dynamodb_errors_deleted': 0,
        'dynamodb_warnings_deleted': 0,
        'orphaned_errors_deleted': 0,
        'orphaned_warnings_deleted': 0,
        'failed_files_cleaned': 0,
        'audit_logs_created': 0,
        'errors': []
    }
    print(f"[CLEANUP_HANDLER] Statistics initialized: {stats}")

    try:
        print("[CLEANUP_HANDLER] ==================== STARTING CLEANUP OPERATIONS ====================")

        print("[CLEANUP_HANDLER] Calculating cutoff date for retention")
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=RETENTION_DAYS)
        print(f"[CLEANUP_HANDLER] Cutoff date calculated: {cutoff_date.isoformat()}")
        print(f"[CLEANUP_HANDLER] Items older than {cutoff_date.isoformat()} will be cleaned up")

        logger.info("Starting cleanup operations", cutoff_date=cutoff_date.isoformat())
        print("[CLEANUP_HANDLER] Cleanup start logged")

        # Step 1: Clean up old S3 files
        print("[CLEANUP_HANDLER] ==================== STEP 1: S3 FILE CLEANUP ====================")
        cleanup_old_s3_files(logger, cutoff_date, stats)
        print(f"[CLEANUP_HANDLER] S3 cleanup complete. Stats: {stats}")

        # Step 2: Archive old file metadata in DynamoDB
        print("[CLEANUP_HANDLER] ==================== STEP 2: DYNAMODB FILE ARCHIVAL ====================")
        archive_old_file_metadata(logger, cutoff_date, stats)
        print(f"[CLEANUP_HANDLER] DynamoDB file archival complete. Stats: {stats}")

        # Step 3: Delete old pay records
        print("[CLEANUP_HANDLER] ==================== STEP 3: PAY RECORDS CLEANUP ====================")
        delete_old_pay_records(logger, cutoff_date, stats)
        print(f"[CLEANUP_HANDLER] Pay records cleanup complete. Stats: {stats}")

        # Step 4: Clean up validation errors and warnings
        print("[CLEANUP_HANDLER] ==================== STEP 4: VALIDATION DATA CLEANUP ====================")
        cleanup_validation_data(logger, cutoff_date, stats)
        print(f"[CLEANUP_HANDLER] Validation data cleanup complete. Stats: {stats}")

        # Step 5: Remove orphaned validation data
        print("[CLEANUP_HANDLER] ==================== STEP 5: ORPHANED DATA CLEANUP ====================")
        cleanup_orphaned_validation_data(logger, stats)
        print(f"[CLEANUP_HANDLER] Orphaned data cleanup complete. Stats: {stats}")

        # Step 6: Clean up failed/error state files
        print("[CLEANUP_HANDLER] ==================== STEP 6: FAILED FILES CLEANUP ====================")
        cleanup_failed_files(logger, cutoff_date, stats)
        print(f"[CLEANUP_HANDLER] Failed files cleanup complete. Stats: {stats}")

        # Step 7: Create audit log entry
        print("[CLEANUP_HANDLER] ==================== STEP 7: AUDIT LOG CREATION ====================")
        create_cleanup_audit_log(logger, stats, cutoff_date)
        print(f"[CLEANUP_HANDLER] Audit log created. Stats: {stats}")

        print("[CLEANUP_HANDLER] ==================== CLEANUP OPERATIONS COMPLETE ====================")
        print(f"[CLEANUP_HANDLER] Final statistics: {json.dumps(stats, indent=2)}")

        logger.info("Cleanup handler completed successfully", statistics=stats)
        print("[CLEANUP_HANDLER] Success logged")

        print("[CLEANUP_HANDLER] Building success response")
        response = {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Cleanup operations completed successfully',
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'retention_days': RETENTION_DAYS,
                'cutoff_date': cutoff_date.isoformat(),
                'statistics': stats
            }, default=str)
        }
        print(f"[CLEANUP_HANDLER] Response built: {response}")

        print("[CLEANUP_HANDLER] ==================== LAMBDA_HANDLER RETURNING SUCCESS ====================")
        return response

    except Exception as e:
        print("[CLEANUP_HANDLER] !!!!!!!!!!! EXCEPTION CAUGHT !!!!!!!!!!!")
        print(f"[CLEANUP_HANDLER] Exception type: {type(e).__name__}")
        print(f"[CLEANUP_HANDLER] Exception message: {str(e)}")
        print(f"[CLEANUP_HANDLER] Exception args: {e.args}")

        import traceback
        print(f"[CLEANUP_HANDLER] Full traceback: {traceback.format_exc()}")

        print("[CLEANUP_HANDLER] Logging error via logger")
        logger.error("Cleanup handler error", error=str(e), error_type=type(e).__name__, statistics=stats)
        print("[CLEANUP_HANDLER] Error logged")

        print("[CLEANUP_HANDLER] Building error response")
        error_response = {
            'statusCode': 500,
            'body': json.dumps({
                'error': 'Cleanup handler failed',
                'message': str(e),
                'type': type(e).__name__,
                'partial_statistics': stats
            }, default=str)
        }
        print(f"[CLEANUP_HANDLER] Error response: {error_response}")

        print("[CLEANUP_HANDLER] ==================== LAMBDA_HANDLER RETURNING ERROR ====================")
        return error_response


def cleanup_old_s3_files(logger, cutoff_date, stats):
    """
    Delete old uploaded files from S3 older than cutoff_date
    """
    print(f"[CLEANUP_S3] ==================== Starting S3 file cleanup ====================")
    print(f"[CLEANUP_S3] Bucket: {S3_BUCKET_NAME}")
    print(f"[CLEANUP_S3] Cutoff date: {cutoff_date.isoformat()}")

    logger.info("Starting S3 file cleanup", bucket=S3_BUCKET_NAME, cutoff_date=cutoff_date.isoformat())
    print("[CLEANUP_S3] S3 cleanup start logged")

    try:
        print("[CLEANUP_S3] Creating paginator for list_objects_v2")
        paginator = s3_client.get_paginator('list_objects_v2')
        print(f"[CLEANUP_S3] Paginator created: {paginator}")

        print(f"[CLEANUP_S3] Starting pagination over bucket: {S3_BUCKET_NAME}")
        page_iterator = paginator.paginate(Bucket=S3_BUCKET_NAME)
        print(f"[CLEANUP_S3] Page iterator created: {page_iterator}")

        print("[CLEANUP_S3] Iterating through pages")
        for page_num, page in enumerate(page_iterator, 1):
            print(f"[CLEANUP_S3] ==================== Processing page {page_num} ====================")
            print(f"[CLEANUP_S3] Page contents: {page.get('Contents', [])}")

            if 'Contents' not in page:
                print(f"[CLEANUP_S3] Page {page_num} has no Contents, skipping")
                continue

            print(f"[CLEANUP_S3] Page {page_num} has {len(page['Contents'])} objects")

            for obj_num, obj in enumerate(page['Contents'], 1):
                print(f"[CLEANUP_S3] -------------------- Processing object {obj_num} on page {page_num} --------------------")
                print(f"[CLEANUP_S3] Object key: {obj['Key']}")
                print(f"[CLEANUP_S3] Object size: {obj['Size']} bytes")
                print(f"[CLEANUP_S3] Object last modified: {obj['LastModified']}")

                # Make LastModified timezone-aware for comparison
                print(f"[CLEANUP_S3] Converting LastModified to timezone-aware datetime")
                last_modified = obj['LastModified']
                if last_modified.tzinfo is None:
                    print(f"[CLEANUP_S3] LastModified is naive, adding UTC timezone")
                    last_modified = last_modified.replace(tzinfo=timezone.utc)
                print(f"[CLEANUP_S3] Timezone-aware LastModified: {last_modified}")

                print(f"[CLEANUP_S3] Comparing {last_modified} < {cutoff_date}")
                if last_modified < cutoff_date:
                    print(f"[CLEANUP_S3] Object is older than cutoff date, marking for deletion")

                    try:
                        print(f"[CLEANUP_S3] Deleting object: {obj['Key']} from bucket: {S3_BUCKET_NAME}")
                        s3_client.delete_object(Bucket=S3_BUCKET_NAME, Key=obj['Key'])
                        print(f"[CLEANUP_S3] Successfully deleted: {obj['Key']}")

                        print(f"[CLEANUP_S3] Incrementing s3_files_deleted counter")
                        stats['s3_files_deleted'] += 1
                        print(f"[CLEANUP_S3] Current s3_files_deleted: {stats['s3_files_deleted']}")

                        print(f"[CLEANUP_S3] Adding {obj['Size']} bytes to s3_bytes_freed")
                        stats['s3_bytes_freed'] += obj['Size']
                        print(f"[CLEANUP_S3] Current s3_bytes_freed: {stats['s3_bytes_freed']}")

                        logger.info("Deleted S3 object", key=obj['Key'], size=obj['Size'], last_modified=last_modified.isoformat())
                        print(f"[CLEANUP_S3] Logged deletion of {obj['Key']}")

                    except Exception as e:
                        print(f"[CLEANUP_S3] !!!!!!!!!!! EXCEPTION deleting {obj['Key']} !!!!!!!!!!!")
                        print(f"[CLEANUP_S3] Exception type: {type(e).__name__}")
                        print(f"[CLEANUP_S3] Exception message: {str(e)}")

                        print(f"[CLEANUP_S3] Incrementing s3_files_failed counter")
                        stats['s3_files_failed'] += 1
                        print(f"[CLEANUP_S3] Current s3_files_failed: {stats['s3_files_failed']}")

                        print(f"[CLEANUP_S3] Adding error to stats")
                        error_msg = f"Failed to delete S3 object {obj['Key']}: {str(e)}"
                        stats['errors'].append(error_msg)
                        print(f"[CLEANUP_S3] Error added: {error_msg}")

                        logger.error("Failed to delete S3 object", key=obj['Key'], error=str(e))
                        print(f"[CLEANUP_S3] Logged error for {obj['Key']}")
                else:
                    print(f"[CLEANUP_S3] Object is newer than cutoff date, keeping")

        print(f"[CLEANUP_S3] ==================== S3 cleanup complete ====================")
        print(f"[CLEANUP_S3] Files deleted: {stats['s3_files_deleted']}")
        print(f"[CLEANUP_S3] Files failed: {stats['s3_files_failed']}")
        print(f"[CLEANUP_S3] Bytes freed: {stats['s3_bytes_freed']}")

        logger.info("S3 cleanup completed",
                   files_deleted=stats['s3_files_deleted'],
                   files_failed=stats['s3_files_failed'],
                   bytes_freed=stats['s3_bytes_freed'])
        print("[CLEANUP_S3] S3 cleanup completion logged")

    except Exception as e:
        print(f"[CLEANUP_S3] !!!!!!!!!!! EXCEPTION in cleanup_old_s3_files !!!!!!!!!!!")
        print(f"[CLEANUP_S3] Exception type: {type(e).__name__}")
        print(f"[CLEANUP_S3] Exception message: {str(e)}")

        error_msg = f"S3 cleanup error: {str(e)}"
        stats['errors'].append(error_msg)
        print(f"[CLEANUP_S3] Error added to stats: {error_msg}")

        logger.error("S3 cleanup error", error=str(e))
        print(f"[CLEANUP_S3] Error logged")


def archive_old_file_metadata(logger, cutoff_date, stats):
    """
    Archive or mark old file metadata records in DynamoDB
    """
    print(f"[ARCHIVE_FILES] ==================== Starting file metadata archival ====================")
    print(f"[ARCHIVE_FILES] Cutoff date: {cutoff_date.isoformat()}")

    logger.info("Starting file metadata archival", cutoff_date=cutoff_date.isoformat())
    print("[ARCHIVE_FILES] Archival start logged")

    try:
        print("[ARCHIVE_FILES] Querying GSI3 for all files")
        print(f"[ARCHIVE_FILES] GSI3PK = 'FILES'")

        response = table.query(
            IndexName='GSI3',
            KeyConditionExpression=Key('GSI3PK').eq('FILES')
        )
        print(f"[ARCHIVE_FILES] Query response: {response}")
        print(f"[ARCHIVE_FILES] Items found: {len(response.get('Items', []))} files")

        print("[ARCHIVE_FILES] Iterating through file metadata items")
        for idx, item in enumerate(response.get('Items', []), 1):
            print(f"[ARCHIVE_FILES] -------------------- Processing file {idx} --------------------")
            print(f"[ARCHIVE_FILES] File item: {item}")

            print(f"[ARCHIVE_FILES] Extracting UploadedAt from item")
            uploaded_at_str = item.get('UploadedAt')
            print(f"[ARCHIVE_FILES] UploadedAt string: {uploaded_at_str}")

            if not uploaded_at_str:
                print(f"[ARCHIVE_FILES] No UploadedAt field, skipping file")
                continue

            print(f"[ARCHIVE_FILES] Parsing UploadedAt as ISO format datetime")
            uploaded_at = datetime.fromisoformat(uploaded_at_str.replace('Z', '+00:00'))
            print(f"[ARCHIVE_FILES] Parsed uploaded_at: {uploaded_at}")

            print(f"[ARCHIVE_FILES] Comparing {uploaded_at} < {cutoff_date}")
            if uploaded_at < cutoff_date:
                print(f"[ARCHIVE_FILES] File is older than cutoff date, archiving")

                print(f"[ARCHIVE_FILES] Extracting FileID: {item.get('FileID')}")
                file_id = item.get('FileID')
                print(f"[ARCHIVE_FILES] FileID: {file_id}")

                try:
                    print(f"[ARCHIVE_FILES] Updating file metadata to archived status")
                    print(f"[ARCHIVE_FILES] PK = FILE#{file_id}, SK = METADATA")

                    update_response = table.update_item(
                        Key={
                            'PK': f'FILE#{file_id}',
                            'SK': 'METADATA'
                        },
                        UpdateExpression='SET #status = :status, ArchivedAt = :archived_at, IsActive = :is_active',
                        ExpressionAttributeNames={
                            '#status': 'Status'
                        },
                        ExpressionAttributeValues={
                            ':status': 'ARCHIVED',
                            ':archived_at': datetime.now(timezone.utc).isoformat(),
                            ':is_active': False
                        }
                    )
                    print(f"[ARCHIVE_FILES] Update response: {update_response}")

                    print(f"[ARCHIVE_FILES] Incrementing dynamodb_files_archived counter")
                    stats['dynamodb_files_archived'] += 1
                    print(f"[ARCHIVE_FILES] Current dynamodb_files_archived: {stats['dynamodb_files_archived']}")

                    logger.info("Archived file metadata", file_id=file_id, uploaded_at=uploaded_at_str)
                    print(f"[ARCHIVE_FILES] Logged archival of file {file_id}")

                except Exception as e:
                    print(f"[ARCHIVE_FILES] !!!!!!!!!!! EXCEPTION archiving file {file_id} !!!!!!!!!!!")
                    print(f"[ARCHIVE_FILES] Exception type: {type(e).__name__}")
                    print(f"[ARCHIVE_FILES] Exception message: {str(e)}")

                    error_msg = f"Failed to archive file metadata {file_id}: {str(e)}"
                    stats['errors'].append(error_msg)
                    print(f"[ARCHIVE_FILES] Error added: {error_msg}")

                    logger.error("Failed to archive file metadata", file_id=file_id, error=str(e))
                    print(f"[ARCHIVE_FILES] Error logged for file {file_id}")
            else:
                print(f"[ARCHIVE_FILES] File is newer than cutoff date, keeping active")

        print(f"[ARCHIVE_FILES] ==================== File metadata archival complete ====================")
        print(f"[ARCHIVE_FILES] Files archived: {stats['dynamodb_files_archived']}")

        logger.info("File metadata archival completed", files_archived=stats['dynamodb_files_archived'])
        print("[ARCHIVE_FILES] Archival completion logged")

    except Exception as e:
        print(f"[ARCHIVE_FILES] !!!!!!!!!!! EXCEPTION in archive_old_file_metadata !!!!!!!!!!!")
        print(f"[ARCHIVE_FILES] Exception type: {type(e).__name__}")
        print(f"[ARCHIVE_FILES] Exception message: {str(e)}")

        error_msg = f"File metadata archival error: {str(e)}"
        stats['errors'].append(error_msg)
        print(f"[ARCHIVE_FILES] Error added to stats: {error_msg}")

        logger.error("File metadata archival error", error=str(e))
        print(f"[ARCHIVE_FILES] Error logged")


def delete_old_pay_records(logger, cutoff_date, stats):
    """
    Delete old pay records from DynamoDB for archived files
    """
    print(f"[DELETE_RECORDS] ==================== Starting pay records deletion ====================")
    print(f"[DELETE_RECORDS] Cutoff date: {cutoff_date.isoformat()}")

    logger.info("Starting pay records deletion", cutoff_date=cutoff_date.isoformat())
    print("[DELETE_RECORDS] Deletion start logged")

    try:
        print("[DELETE_RECORDS] Scanning table for archived file metadata")
        print("[DELETE_RECORDS] FilterExpression: Status = ARCHIVED")

        scan_response = table.scan(
            FilterExpression=Attr('EntityType').eq('File') & Attr('Status').eq('ARCHIVED')
        )
        print(f"[DELETE_RECORDS] Scan response: {scan_response}")
        print(f"[DELETE_RECORDS] Archived files found: {len(scan_response.get('Items', []))}")

        print("[DELETE_RECORDS] Iterating through archived files")
        for idx, file_item in enumerate(scan_response.get('Items', []), 1):
            print(f"[DELETE_RECORDS] -------------------- Processing archived file {idx} --------------------")
            print(f"[DELETE_RECORDS] File item: {file_item}")

            file_id = file_item.get('FileID')
            print(f"[DELETE_RECORDS] FileID: {file_id}")

            try:
                print(f"[DELETE_RECORDS] Querying for pay records of file {file_id}")
                print(f"[DELETE_RECORDS] PK = FILE#{file_id}, SK begins_with RECORD#")

                records_response = table.query(
                    KeyConditionExpression=Key('PK').eq(f'FILE#{file_id}') & Key('SK').begins_with('RECORD#')
                )
                print(f"[DELETE_RECORDS] Query response: {records_response}")
                print(f"[DELETE_RECORDS] Records found: {len(records_response.get('Items', []))}")

                print("[DELETE_RECORDS] Deleting records in batch")
                print(f"[DELETE_RECORDS] Creating batch_writer for table {TABLE_NAME}")
                with table.batch_writer() as batch:
                    print(f"[DELETE_RECORDS] Batch writer created: {batch}")

                    for rec_num, record in enumerate(records_response.get('Items', []), 1):
                        print(f"[DELETE_RECORDS] Processing record {rec_num} for deletion")
                        print(f"[DELETE_RECORDS] Record PK: {record['PK']}, SK: {record['SK']}")

                        batch.delete_item(
                            Key={
                                'PK': record['PK'],
                                'SK': record['SK']
                            }
                        )
                        print(f"[DELETE_RECORDS] Record {rec_num} added to batch delete")

                        print(f"[DELETE_RECORDS] Incrementing dynamodb_records_deleted counter")
                        stats['dynamodb_records_deleted'] += 1
                        print(f"[DELETE_RECORDS] Current dynamodb_records_deleted: {stats['dynamodb_records_deleted']}")

                print(f"[DELETE_RECORDS] Batch delete complete for file {file_id}")
                print(f"[DELETE_RECORDS] Deleted {len(records_response.get('Items', []))} records")

                logger.info("Deleted pay records for archived file",
                           file_id=file_id,
                           records_deleted=len(records_response.get('Items', [])))
                print(f"[DELETE_RECORDS] Logged deletion for file {file_id}")

            except Exception as e:
                print(f"[DELETE_RECORDS] !!!!!!!!!!! EXCEPTION deleting records for file {file_id} !!!!!!!!!!!")
                print(f"[DELETE_RECORDS] Exception type: {type(e).__name__}")
                print(f"[DELETE_RECORDS] Exception message: {str(e)}")

                error_msg = f"Failed to delete records for file {file_id}: {str(e)}"
                stats['errors'].append(error_msg)
                print(f"[DELETE_RECORDS] Error added: {error_msg}")

                logger.error("Failed to delete pay records", file_id=file_id, error=str(e))
                print(f"[DELETE_RECORDS] Error logged for file {file_id}")

        print(f"[DELETE_RECORDS] ==================== Pay records deletion complete ====================")
        print(f"[DELETE_RECORDS] Records deleted: {stats['dynamodb_records_deleted']}")

        logger.info("Pay records deletion completed", records_deleted=stats['dynamodb_records_deleted'])
        print("[DELETE_RECORDS] Deletion completion logged")

    except Exception as e:
        print(f"[DELETE_RECORDS] !!!!!!!!!!! EXCEPTION in delete_old_pay_records !!!!!!!!!!!")
        print(f"[DELETE_RECORDS] Exception type: {type(e).__name__}")
        print(f"[DELETE_RECORDS] Exception message: {str(e)}")

        error_msg = f"Pay records deletion error: {str(e)}"
        stats['errors'].append(error_msg)
        print(f"[DELETE_RECORDS] Error added to stats: {error_msg}")

        logger.error("Pay records deletion error", error=str(e))
        print(f"[DELETE_RECORDS] Error logged")


def cleanup_validation_data(logger, cutoff_date, stats):
    """
    Clean up old validation errors and warnings for archived files
    """
    print(f"[CLEANUP_VALIDATION] ==================== Starting validation data cleanup ====================")
    print(f"[CLEANUP_VALIDATION] Cutoff date: {cutoff_date.isoformat()}")

    logger.info("Starting validation data cleanup", cutoff_date=cutoff_date.isoformat())
    print("[CLEANUP_VALIDATION] Cleanup start logged")

    try:
        print("[CLEANUP_VALIDATION] Querying GSI1 for old errors")
        print("[CLEANUP_VALIDATION] GSI1PK = ERRORS")

        errors_response = table.query(
            IndexName='GSI1',
            KeyConditionExpression=Key('GSI1PK').eq('ERRORS')
        )
        print(f"[CLEANUP_VALIDATION] Errors query response: {errors_response}")
        print(f"[CLEANUP_VALIDATION] Errors found: {len(errors_response.get('Items', []))}")

        print("[CLEANUP_VALIDATION] Processing errors for deletion")
        for idx, error_item in enumerate(errors_response.get('Items', []), 1):
            print(f"[CLEANUP_VALIDATION] -------------------- Processing error {idx} --------------------")
            print(f"[CLEANUP_VALIDATION] Error item: {error_item}")

            created_at_str = error_item.get('CreatedAt')
            print(f"[CLEANUP_VALIDATION] CreatedAt string: {created_at_str}")

            if not created_at_str:
                print(f"[CLEANUP_VALIDATION] No CreatedAt field, skipping error")
                continue

            print(f"[CLEANUP_VALIDATION] Parsing CreatedAt as ISO format datetime")
            created_at = datetime.fromisoformat(created_at_str.replace('Z', '+00:00'))
            print(f"[CLEANUP_VALIDATION] Parsed created_at: {created_at}")

            print(f"[CLEANUP_VALIDATION] Comparing {created_at} < {cutoff_date}")
            if created_at < cutoff_date:
                print(f"[CLEANUP_VALIDATION] Error is older than cutoff date, deleting")

                try:
                    print(f"[CLEANUP_VALIDATION] Deleting error: PK={error_item['PK']}, SK={error_item['SK']}")

                    table.delete_item(
                        Key={
                            'PK': error_item['PK'],
                            'SK': error_item['SK']
                        }
                    )
                    print(f"[CLEANUP_VALIDATION] Error deleted successfully")

                    print(f"[CLEANUP_VALIDATION] Incrementing dynamodb_errors_deleted counter")
                    stats['dynamodb_errors_deleted'] += 1
                    print(f"[CLEANUP_VALIDATION] Current dynamodb_errors_deleted: {stats['dynamodb_errors_deleted']}")

                    logger.info("Deleted old validation error",
                               error_id=error_item.get('ErrorID'),
                               created_at=created_at_str)
                    print(f"[CLEANUP_VALIDATION] Logged deletion of error {error_item.get('ErrorID')}")

                except Exception as e:
                    print(f"[CLEANUP_VALIDATION] !!!!!!!!!!! EXCEPTION deleting error !!!!!!!!!!!")
                    print(f"[CLEANUP_VALIDATION] Exception type: {type(e).__name__}")
                    print(f"[CLEANUP_VALIDATION] Exception message: {str(e)}")

                    error_msg = f"Failed to delete validation error: {str(e)}"
                    stats['errors'].append(error_msg)
                    print(f"[CLEANUP_VALIDATION] Error added: {error_msg}")

                    logger.error("Failed to delete validation error", error=str(e))
            else:
                print(f"[CLEANUP_VALIDATION] Error is newer than cutoff date, keeping")

        print("[CLEANUP_VALIDATION] Querying GSI1 for old warnings")
        print("[CLEANUP_VALIDATION] GSI1PK = WARNINGS")

        warnings_response = table.query(
            IndexName='GSI1',
            KeyConditionExpression=Key('GSI1PK').eq('WARNINGS')
        )
        print(f"[CLEANUP_VALIDATION] Warnings query response: {warnings_response}")
        print(f"[CLEANUP_VALIDATION] Warnings found: {len(warnings_response.get('Items', []))}")

        print("[CLEANUP_VALIDATION] Processing warnings for deletion")
        for idx, warning_item in enumerate(warnings_response.get('Items', []), 1):
            print(f"[CLEANUP_VALIDATION] -------------------- Processing warning {idx} --------------------")
            print(f"[CLEANUP_VALIDATION] Warning item: {warning_item}")

            created_at_str = warning_item.get('CreatedAt')
            print(f"[CLEANUP_VALIDATION] CreatedAt string: {created_at_str}")

            if not created_at_str:
                print(f"[CLEANUP_VALIDATION] No CreatedAt field, skipping warning")
                continue

            print(f"[CLEANUP_VALIDATION] Parsing CreatedAt as ISO format datetime")
            created_at = datetime.fromisoformat(created_at_str.replace('Z', '+00:00'))
            print(f"[CLEANUP_VALIDATION] Parsed created_at: {created_at}")

            print(f"[CLEANUP_VALIDATION] Comparing {created_at} < {cutoff_date}")
            if created_at < cutoff_date:
                print(f"[CLEANUP_VALIDATION] Warning is older than cutoff date, deleting")

                try:
                    print(f"[CLEANUP_VALIDATION] Deleting warning: PK={warning_item['PK']}, SK={warning_item['SK']}")

                    table.delete_item(
                        Key={
                            'PK': warning_item['PK'],
                            'SK': warning_item['SK']
                        }
                    )
                    print(f"[CLEANUP_VALIDATION] Warning deleted successfully")

                    print(f"[CLEANUP_VALIDATION] Incrementing dynamodb_warnings_deleted counter")
                    stats['dynamodb_warnings_deleted'] += 1
                    print(f"[CLEANUP_VALIDATION] Current dynamodb_warnings_deleted: {stats['dynamodb_warnings_deleted']}")

                    logger.info("Deleted old validation warning",
                               warning_id=warning_item.get('WarningID'),
                               created_at=created_at_str)
                    print(f"[CLEANUP_VALIDATION] Logged deletion of warning {warning_item.get('WarningID')}")

                except Exception as e:
                    print(f"[CLEANUP_VALIDATION] !!!!!!!!!!! EXCEPTION deleting warning !!!!!!!!!!!")
                    print(f"[CLEANUP_VALIDATION] Exception type: {type(e).__name__}")
                    print(f"[CLEANUP_VALIDATION] Exception message: {str(e)}")

                    error_msg = f"Failed to delete validation warning: {str(e)}"
                    stats['errors'].append(error_msg)
                    print(f"[CLEANUP_VALIDATION] Error added: {error_msg}")

                    logger.error("Failed to delete validation warning", error=str(e))
            else:
                print(f"[CLEANUP_VALIDATION] Warning is newer than cutoff date, keeping")

        print(f"[CLEANUP_VALIDATION] ==================== Validation data cleanup complete ====================")
        print(f"[CLEANUP_VALIDATION] Errors deleted: {stats['dynamodb_errors_deleted']}")
        print(f"[CLEANUP_VALIDATION] Warnings deleted: {stats['dynamodb_warnings_deleted']}")

        logger.info("Validation data cleanup completed",
                   errors_deleted=stats['dynamodb_errors_deleted'],
                   warnings_deleted=stats['dynamodb_warnings_deleted'])
        print("[CLEANUP_VALIDATION] Cleanup completion logged")

    except Exception as e:
        print(f"[CLEANUP_VALIDATION] !!!!!!!!!!! EXCEPTION in cleanup_validation_data !!!!!!!!!!!")
        print(f"[CLEANUP_VALIDATION] Exception type: {type(e).__name__}")
        print(f"[CLEANUP_VALIDATION] Exception message: {str(e)}")

        error_msg = f"Validation data cleanup error: {str(e)}"
        stats['errors'].append(error_msg)
        print(f"[CLEANUP_VALIDATION] Error added to stats: {error_msg}")

        logger.error("Validation data cleanup error", error=str(e))
        print(f"[CLEANUP_VALIDATION] Error logged")


def cleanup_orphaned_validation_data(logger, stats):
    """
    Remove orphaned validation errors/warnings that reference non-existent files
    """
    print(f"[CLEANUP_ORPHANS] ==================== Starting orphaned validation data cleanup ====================")

    logger.info("Starting orphaned validation data cleanup")
    print("[CLEANUP_ORPHANS] Cleanup start logged")

    try:
        print("[CLEANUP_ORPHANS] Querying GSI1 for all errors")
        errors_response = table.query(
            IndexName='GSI1',
            KeyConditionExpression=Key('GSI1PK').eq('ERRORS')
        )
        print(f"[CLEANUP_ORPHANS] Errors found: {len(errors_response.get('Items', []))}")

        print("[CLEANUP_ORPHANS] Checking for orphaned errors")
        for idx, error_item in enumerate(errors_response.get('Items', []), 1):
            print(f"[CLEANUP_ORPHANS] -------------------- Checking error {idx} --------------------")
            file_id = error_item.get('FileID')
            print(f"[CLEANUP_ORPHANS] Error FileID: {file_id}")

            if not file_id:
                print(f"[CLEANUP_ORPHANS] No FileID, skipping")
                continue

            print(f"[CLEANUP_ORPHANS] Checking if file {file_id} exists")
            try:
                file_response = table.get_item(
                    Key={
                        'PK': f'FILE#{file_id}',
                        'SK': 'METADATA'
                    }
                )
                print(f"[CLEANUP_ORPHANS] File lookup response: {file_response}")

                if 'Item' not in file_response:
                    print(f"[CLEANUP_ORPHANS] File {file_id} does not exist, error is orphaned")

                    print(f"[CLEANUP_ORPHANS] Deleting orphaned error: PK={error_item['PK']}, SK={error_item['SK']}")
                    table.delete_item(
                        Key={
                            'PK': error_item['PK'],
                            'SK': error_item['SK']
                        }
                    )
                    print(f"[CLEANUP_ORPHANS] Orphaned error deleted")

                    print(f"[CLEANUP_ORPHANS] Incrementing orphaned_errors_deleted counter")
                    stats['orphaned_errors_deleted'] += 1
                    print(f"[CLEANUP_ORPHANS] Current orphaned_errors_deleted: {stats['orphaned_errors_deleted']}")

                    logger.info("Deleted orphaned validation error",
                               error_id=error_item.get('ErrorID'),
                               file_id=file_id)
                    print(f"[CLEANUP_ORPHANS] Logged orphaned error deletion")
                else:
                    print(f"[CLEANUP_ORPHANS] File {file_id} exists, error is not orphaned")

            except Exception as e:
                print(f"[CLEANUP_ORPHANS] !!!!!!!!!!! EXCEPTION checking/deleting orphaned error !!!!!!!!!!!")
                print(f"[CLEANUP_ORPHANS] Exception: {str(e)}")
                error_msg = f"Failed to process orphaned error: {str(e)}"
                stats['errors'].append(error_msg)

        print("[CLEANUP_ORPHANS] Querying GSI1 for all warnings")
        warnings_response = table.query(
            IndexName='GSI1',
            KeyConditionExpression=Key('GSI1PK').eq('WARNINGS')
        )
        print(f"[CLEANUP_ORPHANS] Warnings found: {len(warnings_response.get('Items', []))}")

        print("[CLEANUP_ORPHANS] Checking for orphaned warnings")
        for idx, warning_item in enumerate(warnings_response.get('Items', []), 1):
            print(f"[CLEANUP_ORPHANS] -------------------- Checking warning {idx} --------------------")
            file_id = warning_item.get('FileID')
            print(f"[CLEANUP_ORPHANS] Warning FileID: {file_id}")

            if not file_id:
                print(f"[CLEANUP_ORPHANS] No FileID, skipping")
                continue

            print(f"[CLEANUP_ORPHANS] Checking if file {file_id} exists")
            try:
                file_response = table.get_item(
                    Key={
                        'PK': f'FILE#{file_id}',
                        'SK': 'METADATA'
                    }
                )
                print(f"[CLEANUP_ORPHANS] File lookup response: {file_response}")

                if 'Item' not in file_response:
                    print(f"[CLEANUP_ORPHANS] File {file_id} does not exist, warning is orphaned")

                    print(f"[CLEANUP_ORPHANS] Deleting orphaned warning: PK={warning_item['PK']}, SK={warning_item['SK']}")
                    table.delete_item(
                        Key={
                            'PK': warning_item['PK'],
                            'SK': warning_item['SK']
                        }
                    )
                    print(f"[CLEANUP_ORPHANS] Orphaned warning deleted")

                    print(f"[CLEANUP_ORPHANS] Incrementing orphaned_warnings_deleted counter")
                    stats['orphaned_warnings_deleted'] += 1
                    print(f"[CLEANUP_ORPHANS] Current orphaned_warnings_deleted: {stats['orphaned_warnings_deleted']}")

                    logger.info("Deleted orphaned validation warning",
                               warning_id=warning_item.get('WarningID'),
                               file_id=file_id)
                    print(f"[CLEANUP_ORPHANS] Logged orphaned warning deletion")
                else:
                    print(f"[CLEANUP_ORPHANS] File {file_id} exists, warning is not orphaned")

            except Exception as e:
                print(f"[CLEANUP_ORPHANS] !!!!!!!!!!! EXCEPTION checking/deleting orphaned warning !!!!!!!!!!!")
                print(f"[CLEANUP_ORPHANS] Exception: {str(e)}")
                error_msg = f"Failed to process orphaned warning: {str(e)}"
                stats['errors'].append(error_msg)

        print(f"[CLEANUP_ORPHANS] ==================== Orphaned validation data cleanup complete ====================")
        print(f"[CLEANUP_ORPHANS] Orphaned errors deleted: {stats['orphaned_errors_deleted']}")
        print(f"[CLEANUP_ORPHANS] Orphaned warnings deleted: {stats['orphaned_warnings_deleted']}")

        logger.info("Orphaned validation data cleanup completed",
                   orphaned_errors_deleted=stats['orphaned_errors_deleted'],
                   orphaned_warnings_deleted=stats['orphaned_warnings_deleted'])
        print("[CLEANUP_ORPHANS] Cleanup completion logged")

    except Exception as e:
        print(f"[CLEANUP_ORPHANS] !!!!!!!!!!! EXCEPTION in cleanup_orphaned_validation_data !!!!!!!!!!!")
        print(f"[CLEANUP_ORPHANS] Exception type: {type(e).__name__}")
        print(f"[CLEANUP_ORPHANS] Exception message: {str(e)}")

        error_msg = f"Orphaned validation data cleanup error: {str(e)}"
        stats['errors'].append(error_msg)
        print(f"[CLEANUP_ORPHANS] Error added to stats: {error_msg}")

        logger.error("Orphaned validation data cleanup error", error=str(e))
        print(f"[CLEANUP_ORPHANS] Error logged")


def cleanup_failed_files(logger, cutoff_date, stats):
    """
    Clean up files in FAILED or ERROR status older than cutoff date
    """
    print(f"[CLEANUP_FAILED] ==================== Starting failed files cleanup ====================")
    print(f"[CLEANUP_FAILED] Cutoff date: {cutoff_date.isoformat()}")

    logger.info("Starting failed files cleanup", cutoff_date=cutoff_date.isoformat())
    print("[CLEANUP_FAILED] Cleanup start logged")

    try:
        print("[CLEANUP_FAILED] Scanning for failed/error status files")

        for status in ['FAILED', 'ERROR']:
            print(f"[CLEANUP_FAILED] -------------------- Processing status: {status} --------------------")
            print(f"[CLEANUP_FAILED] FilterExpression: EntityType=File AND Status={status}")

            scan_response = table.scan(
                FilterExpression=Attr('EntityType').eq('File') & Attr('Status').eq(status)
            )
            print(f"[CLEANUP_FAILED] Scan response: {scan_response}")
            print(f"[CLEANUP_FAILED] Files with status {status}: {len(scan_response.get('Items', []))}")

            print(f"[CLEANUP_FAILED] Processing {status} files for deletion")
            for idx, file_item in enumerate(scan_response.get('Items', []), 1):
                print(f"[CLEANUP_FAILED] -------------------- Processing {status} file {idx} --------------------")
                print(f"[CLEANUP_FAILED] File item: {file_item}")

                uploaded_at_str = file_item.get('UploadedAt')
                print(f"[CLEANUP_FAILED] UploadedAt string: {uploaded_at_str}")

                if not uploaded_at_str:
                    print(f"[CLEANUP_FAILED] No UploadedAt field, skipping")
                    continue

                print(f"[CLEANUP_FAILED] Parsing UploadedAt as ISO format datetime")
                uploaded_at = datetime.fromisoformat(uploaded_at_str.replace('Z', '+00:00'))
                print(f"[CLEANUP_FAILED] Parsed uploaded_at: {uploaded_at}")

                print(f"[CLEANUP_FAILED] Comparing {uploaded_at} < {cutoff_date}")
                if uploaded_at < cutoff_date:
                    print(f"[CLEANUP_FAILED] File is older than cutoff date, cleaning up")

                    file_id = file_item.get('FileID')
                    s3_key = file_item.get('S3Key')
                    print(f"[CLEANUP_FAILED] FileID: {file_id}")
                    print(f"[CLEANUP_FAILED] S3Key: {s3_key}")

                    try:
                        # Delete from S3 if S3Key exists
                        if s3_key:
                            print(f"[CLEANUP_FAILED] Deleting S3 object: {s3_key}")
                            try:
                                s3_client.delete_object(Bucket=S3_BUCKET_NAME, Key=s3_key)
                                print(f"[CLEANUP_FAILED] S3 object deleted: {s3_key}")
                            except Exception as s3_error:
                                print(f"[CLEANUP_FAILED] Failed to delete S3 object: {str(s3_error)}")
                                print(f"[CLEANUP_FAILED] Continuing with DynamoDB deletion")

                        # Delete file metadata from DynamoDB
                        print(f"[CLEANUP_FAILED] Deleting file metadata: PK=FILE#{file_id}, SK=METADATA")
                        table.delete_item(
                            Key={
                                'PK': f'FILE#{file_id}',
                                'SK': 'METADATA'
                            }
                        )
                        print(f"[CLEANUP_FAILED] File metadata deleted")

                        # Delete associated errors and warnings
                        print(f"[CLEANUP_FAILED] Querying for associated errors and warnings")
                        associated_items = table.query(
                            KeyConditionExpression=Key('PK').eq(f'FILE#{file_id}')
                        )
                        print(f"[CLEANUP_FAILED] Associated items found: {len(associated_items.get('Items', []))}")

                        print(f"[CLEANUP_FAILED] Deleting associated items in batch")
                        with table.batch_writer() as batch:
                            for item in associated_items.get('Items', []):
                                print(f"[CLEANUP_FAILED] Deleting: PK={item['PK']}, SK={item['SK']}")
                                batch.delete_item(
                                    Key={
                                        'PK': item['PK'],
                                        'SK': item['SK']
                                    }
                                )

                        print(f"[CLEANUP_FAILED] Incrementing failed_files_cleaned counter")
                        stats['failed_files_cleaned'] += 1
                        print(f"[CLEANUP_FAILED] Current failed_files_cleaned: {stats['failed_files_cleaned']}")

                        logger.info("Cleaned up failed file",
                                   file_id=file_id,
                                   status=status,
                                   s3_key=s3_key,
                                   uploaded_at=uploaded_at_str)
                        print(f"[CLEANUP_FAILED] Logged cleanup of failed file {file_id}")

                    except Exception as e:
                        print(f"[CLEANUP_FAILED] !!!!!!!!!!! EXCEPTION cleaning up failed file {file_id} !!!!!!!!!!!")
                        print(f"[CLEANUP_FAILED] Exception type: {type(e).__name__}")
                        print(f"[CLEANUP_FAILED] Exception message: {str(e)}")

                        error_msg = f"Failed to clean up failed file {file_id}: {str(e)}"
                        stats['errors'].append(error_msg)
                        print(f"[CLEANUP_FAILED] Error added: {error_msg}")

                        logger.error("Failed to clean up failed file", file_id=file_id, error=str(e))
                else:
                    print(f"[CLEANUP_FAILED] File is newer than cutoff date, keeping")

        print(f"[CLEANUP_FAILED] ==================== Failed files cleanup complete ====================")
        print(f"[CLEANUP_FAILED] Failed files cleaned: {stats['failed_files_cleaned']}")

        logger.info("Failed files cleanup completed", failed_files_cleaned=stats['failed_files_cleaned'])
        print("[CLEANUP_FAILED] Cleanup completion logged")

    except Exception as e:
        print(f"[CLEANUP_FAILED] !!!!!!!!!!! EXCEPTION in cleanup_failed_files !!!!!!!!!!!")
        print(f"[CLEANUP_FAILED] Exception type: {type(e).__name__}")
        print(f"[CLEANUP_FAILED] Exception message: {str(e)}")

        error_msg = f"Failed files cleanup error: {str(e)}"
        stats['errors'].append(error_msg)
        print(f"[CLEANUP_FAILED] Error added to stats: {error_msg}")

        logger.error("Failed files cleanup error", error=str(e))
        print(f"[CLEANUP_FAILED] Error logged")


def create_cleanup_audit_log(logger, stats, cutoff_date):
    """
    Create audit log entry for cleanup operation
    """
    print(f"[AUDIT_LOG] ==================== Creating cleanup audit log ====================")

    logger.info("Creating cleanup audit log")
    print("[AUDIT_LOG] Audit log creation start logged")

    try:
        print("[AUDIT_LOG] Getting current timestamp")
        now = datetime.now(timezone.utc)
        print(f"[AUDIT_LOG] Current timestamp: {now.isoformat()}")

        print("[AUDIT_LOG] Generating audit ID")
        audit_id = str(uuid.uuid4())
        print(f"[AUDIT_LOG] Audit ID: {audit_id}")

        print("[AUDIT_LOG] Extracting date for PK")
        date_str = now.strftime('%Y-%m-%d')
        print(f"[AUDIT_LOG] Date string: {date_str}")

        print("[AUDIT_LOG] Building audit log item")
        audit_item = {
            'PK': f'AUDIT#{date_str}',
            'SK': f'{now.isoformat()}#CLEANUP#{audit_id}',
            'EntityType': 'AuditLog',
            'AuditID': audit_id,
            'TableName': 'System',
            'RecordID': 'cleanup-operation',
            'Action': 'CLEANUP',
            'OldValues': None,
            'NewValues': {
                'statistics': stats,
                'cutoff_date': cutoff_date.isoformat(),
                'retention_days': RETENTION_DAYS
            },
            'ChangedFields': ['cleanup_executed'],
            'UserEmail': 'system@cleanup-handler',
            'Reason': f'Automated daily cleanup - {RETENTION_DAYS} day retention',
            'IPAddress': 'lambda-internal',
            'CreatedAt': now.isoformat()
        }
        print(f"[AUDIT_LOG] Audit item built: {audit_item}")

        print("[AUDIT_LOG] Writing audit log to DynamoDB")
        table.put_item(Item=audit_item)
        print("[AUDIT_LOG] Audit log written successfully")

        print(f"[AUDIT_LOG] Incrementing audit_logs_created counter")
        stats['audit_logs_created'] += 1
        print(f"[AUDIT_LOG] Current audit_logs_created: {stats['audit_logs_created']}")

        logger.info("Cleanup audit log created", audit_id=audit_id, statistics=stats)
        print(f"[AUDIT_LOG] Logged audit log creation")

        print(f"[AUDIT_LOG] ==================== Audit log creation complete ====================")

    except Exception as e:
        print(f"[AUDIT_LOG] !!!!!!!!!!! EXCEPTION creating audit log !!!!!!!!!!!")
        print(f"[AUDIT_LOG] Exception type: {type(e).__name__}")
        print(f"[AUDIT_LOG] Exception message: {str(e)}")

        error_msg = f"Failed to create audit log: {str(e)}"
        stats['errors'].append(error_msg)
        print(f"[AUDIT_LOG] Error added: {error_msg}")

        logger.error("Failed to create audit log", error=str(e))
        print(f"[AUDIT_LOG] Error logged")


print("[CLEANUP_HANDLER] Module fully loaded and ready")
