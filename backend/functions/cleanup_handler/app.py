print("[CLEANUP_HANDLER] Module load started")
"""
print("[CLEANUP_HANDLER] Cleanup Handler Lambda Function")
Cleanup Handler Lambda Function
print("[CLEANUP_HANDLER] Daily maintenance and cleanup tasks")
Daily maintenance and cleanup tasks
"""

print("[CLEANUP_HANDLER] print("[CLEANUP_HANDLER] ========================================")")
print("[CLEANUP_HANDLER] ========================================")
print("[CLEANUP_HANDLER] print("[CLEANUP_HANDLER] Module loading started")")
print("[CLEANUP_HANDLER] Module loading started")
print("[CLEANUP_HANDLER] print("[CLEANUP_HANDLER] ========================================")")
print("[CLEANUP_HANDLER] ========================================")

print("[CLEANUP_HANDLER] print("[CLEANUP_HANDLER] Importing json")")
print("[CLEANUP_HANDLER] Importing json")
print("[CLEANUP_HANDLER] import json")
import json
print("[CLEANUP_HANDLER] print(f"[CLEANUP_HANDLER] json imported: {json}")")
print(f"[CLEANUP_HANDLER] json imported: {json}")

print("[CLEANUP_HANDLER] print("[CLEANUP_HANDLER] Importing os")")
print("[CLEANUP_HANDLER] Importing os")
print("[CLEANUP_HANDLER] import os")
import os
print("[CLEANUP_HANDLER] print(f"[CLEANUP_HANDLER] os imported: {os}")")
print(f"[CLEANUP_HANDLER] os imported: {os}")

print("[CLEANUP_HANDLER] print("[CLEANUP_HANDLER] Importing datetime from datetime")")
print("[CLEANUP_HANDLER] Importing datetime from datetime")
print("[CLEANUP_HANDLER] from datetime import datetime")
from datetime import datetime
print("[CLEANUP_HANDLER] print(f"[CLEANUP_HANDLER] datetime imported: {datetime}")")
print(f"[CLEANUP_HANDLER] datetime imported: {datetime}")

print("[CLEANUP_HANDLER] print("[CLEANUP_HANDLER] Importing boto3")")
print("[CLEANUP_HANDLER] Importing boto3")
print("[CLEANUP_HANDLER] import boto3")
import boto3
print("[CLEANUP_HANDLER] print(f"[CLEANUP_HANDLER] boto3 imported: {boto3}")")
print(f"[CLEANUP_HANDLER] boto3 imported: {boto3}")

print("[CLEANUP_HANDLER] print("[CLEANUP_HANDLER] Importing from common layer")")
print("[CLEANUP_HANDLER] Importing from common layer")
print("[CLEANUP_HANDLER] print("[CLEANUP_HANDLER] Importing StructuredLogger from common.logger")")
print("[CLEANUP_HANDLER] Importing StructuredLogger from common.logger")
print("[CLEANUP_HANDLER] from common.logger import StructuredLogger")
from common.logger import StructuredLogger
print("[CLEANUP_HANDLER] print(f"[CLEANUP_HANDLER] StructuredLogger imported: {StructuredLogger}")")
print(f"[CLEANUP_HANDLER] StructuredLogger imported: {StructuredLogger}")

print("[CLEANUP_HANDLER] print("[CLEANUP_HANDLER] Importing DynamoDBClient from common.dynamodb")")
print("[CLEANUP_HANDLER] Importing DynamoDBClient from common.dynamodb")
print("[CLEANUP_HANDLER] from common.dynamodb import DynamoDBClient")
from common.dynamodb import DynamoDBClient
print("[CLEANUP_HANDLER] print(f"[CLEANUP_HANDLER] DynamoDBClient imported: {DynamoDBClient}")")
print(f"[CLEANUP_HANDLER] DynamoDBClient imported: {DynamoDBClient}")

print("[CLEANUP_HANDLER] print("[CLEANUP_HANDLER] Creating boto3 DynamoDB resource")")
print("[CLEANUP_HANDLER] Creating boto3 DynamoDB resource")
print("[CLEANUP_HANDLER] dynamodb = boto3.resource('dynamodb')")
dynamodb = boto3.resource('dynamodb')
print("[CLEANUP_HANDLER] print(f"[CLEANUP_HANDLER] dynamodb resource created: {dynamodb}")")
print(f"[CLEANUP_HANDLER] dynamodb resource created: {dynamodb}")

print("[CLEANUP_HANDLER] print("[CLEANUP_HANDLER] Creating DynamoDB client")")
print("[CLEANUP_HANDLER] Creating DynamoDB client")
print("[CLEANUP_HANDLER] dynamodb_client = DynamoDBClient()")
dynamodb_client = DynamoDBClient()
print("[CLEANUP_HANDLER] print(f"[CLEANUP_HANDLER] dynamodb_client created: {dynamodb_client}")")
print(f"[CLEANUP_HANDLER] dynamodb_client created: {dynamodb_client}")

print("[CLEANUP_HANDLER] print("[CLEANUP_HANDLER] Reading DYNAMODB_TABLE_NAME from environment")")
print("[CLEANUP_HANDLER] Reading DYNAMODB_TABLE_NAME from environment")
print("[CLEANUP_HANDLER] DYNAMODB_TABLE = os.environ.get('DYNAMODB_TABLE_NAME')")
DYNAMODB_TABLE = os.environ.get('DYNAMODB_TABLE_NAME')
print("[CLEANUP_HANDLER] print(f"[CLEANUP_HANDLER] DYNAMODB_TABLE set to: {DYNAMODB_TABLE}")")
print(f"[CLEANUP_HANDLER] DYNAMODB_TABLE set to: {DYNAMODB_TABLE}")

print("[CLEANUP_HANDLER] print("[CLEANUP_HANDLER] Reading RETENTION_DAYS from environment")")
print("[CLEANUP_HANDLER] Reading RETENTION_DAYS from environment")
print("[CLEANUP_HANDLER] RETENTION_DAYS = int(os.environ.get('RETENTION_DAYS', '30'))")
RETENTION_DAYS = int(os.environ.get('RETENTION_DAYS', '30'))
print("[CLEANUP_HANDLER] print(f"[CLEANUP_HANDLER] RETENTION_DAYS set to: {RETENTION_DAYS}")")
print(f"[CLEANUP_HANDLER] RETENTION_DAYS set to: {RETENTION_DAYS}")

print("[CLEANUP_HANDLER] print("[CLEANUP_HANDLER] ========================================")")
print("[CLEANUP_HANDLER] ========================================")
print("[CLEANUP_HANDLER] print("[CLEANUP_HANDLER] Module loading completed")")
print("[CLEANUP_HANDLER] Module loading completed")
print("[CLEANUP_HANDLER] print("[CLEANUP_HANDLER] ========================================")")
print("[CLEANUP_HANDLER] ========================================")


print("[CLEANUP_HANDLER] def lambda_handler(event, context):")
def lambda_handler(event, context):
    """
print("[CLEANUP_HANDLER] Perform daily cleanup")
    Perform daily cleanup
print("[CLEANUP_HANDLER] Phase 1: Stub implementation")
    Phase 1: Stub implementation
    """
print("[CLEANUP_HANDLER] print("[CLEANUP_HANDLER] ========================================")")
    print("[CLEANUP_HANDLER] ========================================")
print("[CLEANUP_HANDLER] print("[CLEANUP_HANDLER] lambda_handler() invoked")")
    print("[CLEANUP_HANDLER] lambda_handler() invoked")
print("[CLEANUP_HANDLER] print("[CLEANUP_HANDLER] ========================================")")
    print("[CLEANUP_HANDLER] ========================================")
print("[CLEANUP_HANDLER] print(f"[CLEANUP_HANDLER] event parameter: {event}")")
    print(f"[CLEANUP_HANDLER] event parameter: {event}")
print("[CLEANUP_HANDLER] print(f"[CLEANUP_HANDLER] context parameter: {context}")")
    print(f"[CLEANUP_HANDLER] context parameter: {context}")
print("[CLEANUP_HANDLER] print(f"[CLEANUP_HANDLER] context.request_id: {context.request_id}")")
    print(f"[CLEANUP_HANDLER] context.request_id: {context.request_id}")

print("[CLEANUP_HANDLER] print("[CLEANUP_HANDLER] Creating StructuredLogger")")
    print("[CLEANUP_HANDLER] Creating StructuredLogger")
print("[CLEANUP_HANDLER] logger = StructuredLogger("cleanup-handler", context.request_id)")
    logger = StructuredLogger("cleanup-handler", context.request_id)
print("[CLEANUP_HANDLER] print(f"[CLEANUP_HANDLER] logger created: {logger}")")
    print(f"[CLEANUP_HANDLER] logger created: {logger}")

print("[CLEANUP_HANDLER] print("[CLEANUP_HANDLER] Logging info message: Cleanup handler invoked")")
    print("[CLEANUP_HANDLER] Logging info message: Cleanup handler invoked")
print("[CLEANUP_HANDLER] logger.info("Cleanup handler invoked")")
    logger.info("Cleanup handler invoked")
print("[CLEANUP_HANDLER] print("[CLEANUP_HANDLER] Info message logged")")
    print("[CLEANUP_HANDLER] Info message logged")

print("[CLEANUP_HANDLER] print("[CLEANUP_HANDLER] Initializing results dictionary")")
    print("[CLEANUP_HANDLER] Initializing results dictionary")
print("[CLEANUP_HANDLER] results = {")
    results = {
print("[CLEANUP_HANDLER] 'statusCode': 200,")
        'statusCode': 200,
print("[CLEANUP_HANDLER] 'body': json.dumps({")
        'body': json.dumps({
print("[CLEANUP_HANDLER] 'message': 'Cleanup handler - Phase 1 stub',")
            'message': 'Cleanup handler - Phase 1 stub',
print("[CLEANUP_HANDLER] 'tasks_completed': []")
            'tasks_completed': []
print("[CLEANUP_HANDLER] })")
        })
print("[CLEANUP_HANDLER] }")
    }
print("[CLEANUP_HANDLER] print(f"[CLEANUP_HANDLER] results dictionary initialized: {results}")")
    print(f"[CLEANUP_HANDLER] results dictionary initialized: {results}")

print("[CLEANUP_HANDLER] try:")
    try:
print("[CLEANUP_HANDLER] print("[CLEANUP_HANDLER] Entering try block")")
        print("[CLEANUP_HANDLER] Entering try block")

print("[CLEANUP_HANDLER] print("[CLEANUP_HANDLER] Logging input event")")
        print("[CLEANUP_HANDLER] Logging input event")
print("[CLEANUP_HANDLER] print(f"[CLEANUP_HANDLER] Received event: {json.dumps(event)}")")
        print(f"[CLEANUP_HANDLER] Received event: {json.dumps(event)}")

print("[CLEANUP_HANDLER] print("[CLEANUP_HANDLER] Getting current UTC time")")
        print("[CLEANUP_HANDLER] Getting current UTC time")
print("[CLEANUP_HANDLER] now = datetime.utcnow()")
        now = datetime.utcnow()
print("[CLEANUP_HANDLER] print(f"[CLEANUP_HANDLER] Current UTC time: {now}")")
        print(f"[CLEANUP_HANDLER] Current UTC time: {now}")

print("[CLEANUP_HANDLER] print("[CLEANUP_HANDLER] Calculating cutoff date for retention")")
        print("[CLEANUP_HANDLER] Calculating cutoff date for retention")
print("[CLEANUP_HANDLER] from datetime import timedelta")
        from datetime import timedelta
print("[CLEANUP_HANDLER] print("[CLEANUP_HANDLER] Imported timedelta from datetime")")
        print("[CLEANUP_HANDLER] Imported timedelta from datetime")
print("[CLEANUP_HANDLER] cutoff_date = now - timedelta(days=RETENTION_DAYS)")
        cutoff_date = now - timedelta(days=RETENTION_DAYS)
print("[CLEANUP_HANDLER] print(f"[CLEANUP_HANDLER] Cutoff date (items older than {RETENTION_DAYS} days): ")
        print(f"[CLEANUP_HANDLER] Cutoff date (items older than {RETENTION_DAYS} days): {cutoff_date}")

print("[CLEANUP_HANDLER] print("[CLEANUP_HANDLER] Converting cutoff_date to ISO format")")
        print("[CLEANUP_HANDLER] Converting cutoff_date to ISO format")
print("[CLEANUP_HANDLER] cutoff_timestamp = cutoff_date.isoformat() + 'Z'")
        cutoff_timestamp = cutoff_date.isoformat() + 'Z'
print("[CLEANUP_HANDLER] print(f"[CLEANUP_HANDLER] Cutoff timestamp: {cutoff_timestamp}")")
        print(f"[CLEANUP_HANDLER] Cutoff timestamp: {cutoff_timestamp}")

print("[CLEANUP_HANDLER] print("[CLEANUP_HANDLER] Initializing task_results list")")
        print("[CLEANUP_HANDLER] Initializing task_results list")
print("[CLEANUP_HANDLER] task_results = []")
        task_results = []
print("[CLEANUP_HANDLER] print(f"[CLEANUP_HANDLER] task_results: {task_results}")")
        print(f"[CLEANUP_HANDLER] task_results: {task_results}")

print("[CLEANUP_HANDLER] print("[CLEANUP_HANDLER] ========================================")")
        print("[CLEANUP_HANDLER] ========================================")
print("[CLEANUP_HANDLER] print("[CLEANUP_HANDLER] Starting cleanup tasks")")
        print("[CLEANUP_HANDLER] Starting cleanup tasks")
print("[CLEANUP_HANDLER] print("[CLEANUP_HANDLER] ========================================")")
        print("[CLEANUP_HANDLER] ========================================")

print("[CLEANUP_HANDLER] print("[CLEANUP_HANDLER] Calling cleanup_expired_files()")")
        print("[CLEANUP_HANDLER] Calling cleanup_expired_files()")
print("[CLEANUP_HANDLER] expired_files_result = cleanup_expired_files(logger, cutoff_timestamp)")
        expired_files_result = cleanup_expired_files(logger, cutoff_timestamp)
print("[CLEANUP_HANDLER] print(f"[CLEANUP_HANDLER] cleanup_expired_files() returned: {expired_files_resul")
        print(f"[CLEANUP_HANDLER] cleanup_expired_files() returned: {expired_files_result}")

print("[CLEANUP_HANDLER] print("[CLEANUP_HANDLER] Appending expired_files_result to task_results")")
        print("[CLEANUP_HANDLER] Appending expired_files_result to task_results")
print("[CLEANUP_HANDLER] task_results.append(expired_files_result)")
        task_results.append(expired_files_result)
print("[CLEANUP_HANDLER] print(f"[CLEANUP_HANDLER] task_results: {task_results}")")
        print(f"[CLEANUP_HANDLER] task_results: {task_results}")

print("[CLEANUP_HANDLER] print("[CLEANUP_HANDLER] Calling cleanup_old_logs()")")
        print("[CLEANUP_HANDLER] Calling cleanup_old_logs()")
print("[CLEANUP_HANDLER] old_logs_result = cleanup_old_logs(logger, cutoff_timestamp)")
        old_logs_result = cleanup_old_logs(logger, cutoff_timestamp)
print("[CLEANUP_HANDLER] print(f"[CLEANUP_HANDLER] cleanup_old_logs() returned: {old_logs_result}")")
        print(f"[CLEANUP_HANDLER] cleanup_old_logs() returned: {old_logs_result}")

print("[CLEANUP_HANDLER] print("[CLEANUP_HANDLER] Appending old_logs_result to task_results")")
        print("[CLEANUP_HANDLER] Appending old_logs_result to task_results")
print("[CLEANUP_HANDLER] task_results.append(old_logs_result)")
        task_results.append(old_logs_result)
print("[CLEANUP_HANDLER] print(f"[CLEANUP_HANDLER] task_results: {task_results}")")
        print(f"[CLEANUP_HANDLER] task_results: {task_results}")

print("[CLEANUP_HANDLER] print("[CLEANUP_HANDLER] Calling cleanup_stale_sessions()")")
        print("[CLEANUP_HANDLER] Calling cleanup_stale_sessions()")
print("[CLEANUP_HANDLER] stale_sessions_result = cleanup_stale_sessions(logger, cutoff_timestamp)")
        stale_sessions_result = cleanup_stale_sessions(logger, cutoff_timestamp)
print("[CLEANUP_HANDLER] print(f"[CLEANUP_HANDLER] cleanup_stale_sessions() returned: {stale_sessions_res")
        print(f"[CLEANUP_HANDLER] cleanup_stale_sessions() returned: {stale_sessions_result}")

print("[CLEANUP_HANDLER] print("[CLEANUP_HANDLER] Appending stale_sessions_result to task_results")")
        print("[CLEANUP_HANDLER] Appending stale_sessions_result to task_results")
print("[CLEANUP_HANDLER] task_results.append(stale_sessions_result)")
        task_results.append(stale_sessions_result)
print("[CLEANUP_HANDLER] print(f"[CLEANUP_HANDLER] task_results: {task_results}")")
        print(f"[CLEANUP_HANDLER] task_results: {task_results}")

print("[CLEANUP_HANDLER] print("[CLEANUP_HANDLER] Building response body")")
        print("[CLEANUP_HANDLER] Building response body")
print("[CLEANUP_HANDLER] response_body = {")
        response_body = {
print("[CLEANUP_HANDLER] 'message': 'Cleanup handler executed successfully',")
            'message': 'Cleanup handler executed successfully',
print("[CLEANUP_HANDLER] 'timestamp': now.isoformat() + 'Z',")
            'timestamp': now.isoformat() + 'Z',
print("[CLEANUP_HANDLER] 'retention_days': RETENTION_DAYS,")
            'retention_days': RETENTION_DAYS,
print("[CLEANUP_HANDLER] 'cutoff_date': cutoff_timestamp,")
            'cutoff_date': cutoff_timestamp,
print("[CLEANUP_HANDLER] 'tasks_completed': task_results")
            'tasks_completed': task_results
print("[CLEANUP_HANDLER] }")
        }
print("[CLEANUP_HANDLER] print(f"[CLEANUP_HANDLER] response_body: {response_body}")")
        print(f"[CLEANUP_HANDLER] response_body: {response_body}")

print("[CLEANUP_HANDLER] print("[CLEANUP_HANDLER] Updating results dictionary with success response")")
        print("[CLEANUP_HANDLER] Updating results dictionary with success response")
print("[CLEANUP_HANDLER] results = {")
        results = {
print("[CLEANUP_HANDLER] 'statusCode': 200,")
            'statusCode': 200,
print("[CLEANUP_HANDLER] 'body': json.dumps(response_body)")
            'body': json.dumps(response_body)
print("[CLEANUP_HANDLER] }")
        }
print("[CLEANUP_HANDLER] print(f"[CLEANUP_HANDLER] results: {results}")")
        print(f"[CLEANUP_HANDLER] results: {results}")

print("[CLEANUP_HANDLER] print("[CLEANUP_HANDLER] Logging success message")")
        print("[CLEANUP_HANDLER] Logging success message")
print("[CLEANUP_HANDLER] logger.info("Cleanup completed successfully", tasks=len(task_results))")
        logger.info("Cleanup completed successfully", tasks=len(task_results))
print("[CLEANUP_HANDLER] print("[CLEANUP_HANDLER] Success message logged")")
        print("[CLEANUP_HANDLER] Success message logged")

print("[CLEANUP_HANDLER] print("[CLEANUP_HANDLER] ========================================")")
        print("[CLEANUP_HANDLER] ========================================")
print("[CLEANUP_HANDLER] print("[CLEANUP_HANDLER] lambda_handler() completed successfully")")
        print("[CLEANUP_HANDLER] lambda_handler() completed successfully")
print("[CLEANUP_HANDLER] print("[CLEANUP_HANDLER] ========================================")")
        print("[CLEANUP_HANDLER] ========================================")
print("[CLEANUP_HANDLER] return results")
        return results

print("[CLEANUP_HANDLER] except Exception as e:")
    except Exception as e:
print("[CLEANUP_HANDLER] print("[CLEANUP_HANDLER] !!! EXCEPTION CAUGHT !!!")")
        print("[CLEANUP_HANDLER] !!! EXCEPTION CAUGHT !!!")
print("[CLEANUP_HANDLER] print(f"[CLEANUP_HANDLER] Exception type: {type(e)}")")
        print(f"[CLEANUP_HANDLER] Exception type: {type(e)}")
print("[CLEANUP_HANDLER] print(f"[CLEANUP_HANDLER] Exception message: {str(e)}")")
        print(f"[CLEANUP_HANDLER] Exception message: {str(e)}")
print("[CLEANUP_HANDLER] print(f"[CLEANUP_HANDLER] Exception args: {e.args}")")
        print(f"[CLEANUP_HANDLER] Exception args: {e.args}")

print("[CLEANUP_HANDLER] print("[CLEANUP_HANDLER] Logging error via logger")")
        print("[CLEANUP_HANDLER] Logging error via logger")
print("[CLEANUP_HANDLER] logger.error("Cleanup handler error", error=str(e))")
        logger.error("Cleanup handler error", error=str(e))
print("[CLEANUP_HANDLER] print("[CLEANUP_HANDLER] Error logged")")
        print("[CLEANUP_HANDLER] Error logged")

print("[CLEANUP_HANDLER] print("[CLEANUP_HANDLER] Building error response")")
        print("[CLEANUP_HANDLER] Building error response")
print("[CLEANUP_HANDLER] error_response = {")
        error_response = {
print("[CLEANUP_HANDLER] 'statusCode': 500,")
            'statusCode': 500,
print("[CLEANUP_HANDLER] 'body': json.dumps({")
            'body': json.dumps({
print("[CLEANUP_HANDLER] 'error': 'Cleanup handler failed',")
                'error': 'Cleanup handler failed',
print("[CLEANUP_HANDLER] 'message': str(e)")
                'message': str(e)
print("[CLEANUP_HANDLER] })")
            })
print("[CLEANUP_HANDLER] }")
        }
print("[CLEANUP_HANDLER] print(f"[CLEANUP_HANDLER] error_response: {error_response}")")
        print(f"[CLEANUP_HANDLER] error_response: {error_response}")
print("[CLEANUP_HANDLER] print("[CLEANUP_HANDLER] lambda_handler() returning error response")")
        print("[CLEANUP_HANDLER] lambda_handler() returning error response")
print("[CLEANUP_HANDLER] return error_response")
        return error_response


print("[CLEANUP_HANDLER] def cleanup_expired_files(logger: StructuredLogger, cutoff_timestamp: str):")
def cleanup_expired_files(logger: StructuredLogger, cutoff_timestamp: str):
    """
print("[CLEANUP_HANDLER] Clean up expired file entries from DynamoDB")
    Clean up expired file entries from DynamoDB
print("[CLEANUP_HANDLER] Remove files older than retention period")
    Remove files older than retention period
    """
print("[CLEANUP_HANDLER] print("[CLEANUP_HANDLER] ========================================")")
    print("[CLEANUP_HANDLER] ========================================")
print("[CLEANUP_HANDLER] print("[CLEANUP_HANDLER] cleanup_expired_files() started")")
    print("[CLEANUP_HANDLER] cleanup_expired_files() started")
print("[CLEANUP_HANDLER] print("[CLEANUP_HANDLER] ========================================")")
    print("[CLEANUP_HANDLER] ========================================")
print("[CLEANUP_HANDLER] print(f"[CLEANUP_HANDLER] logger: {logger}")")
    print(f"[CLEANUP_HANDLER] logger: {logger}")
print("[CLEANUP_HANDLER] print(f"[CLEANUP_HANDLER] cutoff_timestamp: {cutoff_timestamp}")")
    print(f"[CLEANUP_HANDLER] cutoff_timestamp: {cutoff_timestamp}")

print("[CLEANUP_HANDLER] print("[CLEANUP_HANDLER] Logging info: Starting expired files cleanup")")
    print("[CLEANUP_HANDLER] Logging info: Starting expired files cleanup")
print("[CLEANUP_HANDLER] logger.info("Starting expired files cleanup")")
    logger.info("Starting expired files cleanup")
print("[CLEANUP_HANDLER] print("[CLEANUP_HANDLER] Info logged")")
    print("[CLEANUP_HANDLER] Info logged")

print("[CLEANUP_HANDLER] print("[CLEANUP_HANDLER] Initializing cleaned_count variable")")
    print("[CLEANUP_HANDLER] Initializing cleaned_count variable")
print("[CLEANUP_HANDLER] cleaned_count = 0")
    cleaned_count = 0
print("[CLEANUP_HANDLER] print(f"[CLEANUP_HANDLER] cleaned_count: {cleaned_count}")")
    print(f"[CLEANUP_HANDLER] cleaned_count: {cleaned_count}")

print("[CLEANUP_HANDLER] try:")
    try:
print("[CLEANUP_HANDLER] print("[CLEANUP_HANDLER] Entering try block")")
        print("[CLEANUP_HANDLER] Entering try block")

print("[CLEANUP_HANDLER] print("[CLEANUP_HANDLER] Querying DynamoDB for expired files")")
        print("[CLEANUP_HANDLER] Querying DynamoDB for expired files")
print("[CLEANUP_HANDLER] print("[CLEANUP_HANDLER] Scanning for Files with UploadedAt < cutoff_timestamp")")
        print("[CLEANUP_HANDLER] Scanning for Files with UploadedAt < cutoff_timestamp")
print("[CLEANUP_HANDLER] print(f"[CLEANUP_HANDLER] Cutoff timestamp: {cutoff_timestamp}")")
        print(f"[CLEANUP_HANDLER] Cutoff timestamp: {cutoff_timestamp}")

print("[CLEANUP_HANDLER] print("[CLEANUP_HANDLER] Building scan parameters")")
        print("[CLEANUP_HANDLER] Building scan parameters")
print("[CLEANUP_HANDLER] scan_params = {")
        scan_params = {
print("[CLEANUP_HANDLER] 'FilterExpression': 'UploadedAt < :cutoff AND EntityType = :entity_type',")
            'FilterExpression': 'UploadedAt < :cutoff AND EntityType = :entity_type',
print("[CLEANUP_HANDLER] 'ExpressionAttributeValues': {")
            'ExpressionAttributeValues': {
print("[CLEANUP_HANDLER] ':cutoff': cutoff_timestamp,")
                ':cutoff': cutoff_timestamp,
print("[CLEANUP_HANDLER] ':entity_type': 'File'")
                ':entity_type': 'File'
print("[CLEANUP_HANDLER] }")
            }
print("[CLEANUP_HANDLER] }")
        }
print("[CLEANUP_HANDLER] print(f"[CLEANUP_HANDLER] scan_params: {scan_params}")")
        print(f"[CLEANUP_HANDLER] scan_params: {scan_params}")

print("[CLEANUP_HANDLER] print("[CLEANUP_HANDLER] Executing table.scan()")")
        print("[CLEANUP_HANDLER] Executing table.scan()")
print("[CLEANUP_HANDLER] response = dynamodb_client.table.scan(**scan_params)")
        response = dynamodb_client.table.scan(**scan_params)
print("[CLEANUP_HANDLER] print(f"[CLEANUP_HANDLER] scan response received: {type(response)}")")
        print(f"[CLEANUP_HANDLER] scan response received: {type(response)}")

print("[CLEANUP_HANDLER] print("[CLEANUP_HANDLER] Extracting Items from response")")
        print("[CLEANUP_HANDLER] Extracting Items from response")
print("[CLEANUP_HANDLER] items = response.get('Items', [])")
        items = response.get('Items', [])
print("[CLEANUP_HANDLER] print(f"[CLEANUP_HANDLER] Number of expired file items found: {len(items)}")")
        print(f"[CLEANUP_HANDLER] Number of expired file items found: {len(items)}")

print("[CLEANUP_HANDLER] print("[CLEANUP_HANDLER] Iterating through expired file items")")
        print("[CLEANUP_HANDLER] Iterating through expired file items")
print("[CLEANUP_HANDLER] for idx, item in enumerate(items):")
        for idx, item in enumerate(items):
print("[CLEANUP_HANDLER] print(f"[CLEANUP_HANDLER] --- Processing item {idx + 1}/{len(items)} ---")")
            print(f"[CLEANUP_HANDLER] --- Processing item {idx + 1}/{len(items)} ---")
print("[CLEANUP_HANDLER] print(f"[CLEANUP_HANDLER] item: {item}")")
            print(f"[CLEANUP_HANDLER] item: {item}")

print("[CLEANUP_HANDLER] print("[CLEANUP_HANDLER] Extracting PK from item")")
            print("[CLEANUP_HANDLER] Extracting PK from item")
print("[CLEANUP_HANDLER] pk = item.get('PK')")
            pk = item.get('PK')
print("[CLEANUP_HANDLER] print(f"[CLEANUP_HANDLER] PK: {pk}")")
            print(f"[CLEANUP_HANDLER] PK: {pk}")

print("[CLEANUP_HANDLER] print("[CLEANUP_HANDLER] Extracting SK from item")")
            print("[CLEANUP_HANDLER] Extracting SK from item")
print("[CLEANUP_HANDLER] sk = item.get('SK')")
            sk = item.get('SK')
print("[CLEANUP_HANDLER] print(f"[CLEANUP_HANDLER] SK: {sk}")")
            print(f"[CLEANUP_HANDLER] SK: {sk}")

print("[CLEANUP_HANDLER] print("[CLEANUP_HANDLER] Extracting FileID from item")")
            print("[CLEANUP_HANDLER] Extracting FileID from item")
print("[CLEANUP_HANDLER] file_id = item.get('FileID')")
            file_id = item.get('FileID')
print("[CLEANUP_HANDLER] print(f"[CLEANUP_HANDLER] FileID: {file_id}")")
            print(f"[CLEANUP_HANDLER] FileID: {file_id}")

print("[CLEANUP_HANDLER] try:")
            try:
print("[CLEANUP_HANDLER] print("[CLEANUP_HANDLER] Deleting item from DynamoDB")")
                print("[CLEANUP_HANDLER] Deleting item from DynamoDB")
print("[CLEANUP_HANDLER] print(f"[CLEANUP_HANDLER] Calling table.delete_item() with PK={pk}, SK={sk}")")
                print(f"[CLEANUP_HANDLER] Calling table.delete_item() with PK={pk}, SK={sk}")
print("[CLEANUP_HANDLER] dynamodb_client.table.delete_item(")
                dynamodb_client.table.delete_item(
print("[CLEANUP_HANDLER] Key={")
                    Key={
print("[CLEANUP_HANDLER] 'PK': pk,")
                        'PK': pk,
print("[CLEANUP_HANDLER] 'SK': sk")
                        'SK': sk
print("[CLEANUP_HANDLER] }")
                    }
print("[CLEANUP_HANDLER] )")
                )
print("[CLEANUP_HANDLER] print("[CLEANUP_HANDLER] Delete operation completed")")
                print("[CLEANUP_HANDLER] Delete operation completed")

print("[CLEANUP_HANDLER] print("[CLEANUP_HANDLER] Incrementing cleaned_count")")
                print("[CLEANUP_HANDLER] Incrementing cleaned_count")
print("[CLEANUP_HANDLER] cleaned_count += 1")
                cleaned_count += 1
print("[CLEANUP_HANDLER] print(f"[CLEANUP_HANDLER] cleaned_count: {cleaned_count}")")
                print(f"[CLEANUP_HANDLER] cleaned_count: {cleaned_count}")

print("[CLEANUP_HANDLER] print("[CLEANUP_HANDLER] Logging deleted file info")")
                print("[CLEANUP_HANDLER] Logging deleted file info")
print("[CLEANUP_HANDLER] logger.info("Deleted expired file", file_id=file_id)")
                logger.info("Deleted expired file", file_id=file_id)
print("[CLEANUP_HANDLER] print("[CLEANUP_HANDLER] File deletion logged")")
                print("[CLEANUP_HANDLER] File deletion logged")

print("[CLEANUP_HANDLER] except Exception as e:")
            except Exception as e:
print("[CLEANUP_HANDLER] print("[CLEANUP_HANDLER] !!! EXCEPTION deleting item !!!")")
                print("[CLEANUP_HANDLER] !!! EXCEPTION deleting item !!!")
print("[CLEANUP_HANDLER] print(f"[CLEANUP_HANDLER] Exception: {e}")")
                print(f"[CLEANUP_HANDLER] Exception: {e}")

print("[CLEANUP_HANDLER] print("[CLEANUP_HANDLER] Logging deletion error")")
                print("[CLEANUP_HANDLER] Logging deletion error")
print("[CLEANUP_HANDLER] logger.error("Failed to delete expired file", file_id=file_id, error=str(e))")
                logger.error("Failed to delete expired file", file_id=file_id, error=str(e))
print("[CLEANUP_HANDLER] print("[CLEANUP_HANDLER] Deletion error logged")")
                print("[CLEANUP_HANDLER] Deletion error logged")

print("[CLEANUP_HANDLER] print("[CLEANUP_HANDLER] Checking if scan response has more items")")
        print("[CLEANUP_HANDLER] Checking if scan response has more items")
print("[CLEANUP_HANDLER] while 'LastEvaluatedKey' in response:")
        while 'LastEvaluatedKey' in response:
print("[CLEANUP_HANDLER] print("[CLEANUP_HANDLER] LastEvaluatedKey found, paginating for more items")")
            print("[CLEANUP_HANDLER] LastEvaluatedKey found, paginating for more items")
print("[CLEANUP_HANDLER] print(f"[CLEANUP_HANDLER] LastEvaluatedKey: {response.get('LastEvaluatedKey')}")")
            print(f"[CLEANUP_HANDLER] LastEvaluatedKey: {response.get('LastEvaluatedKey')}")

print("[CLEANUP_HANDLER] print("[CLEANUP_HANDLER] Building scan parameters for next page")")
            print("[CLEANUP_HANDLER] Building scan parameters for next page")
print("[CLEANUP_HANDLER] scan_params['ExclusiveStartKey'] = response['LastEvaluatedKey']")
            scan_params['ExclusiveStartKey'] = response['LastEvaluatedKey']
print("[CLEANUP_HANDLER] print(f"[CLEANUP_HANDLER] scan_params with pagination: {scan_params}")")
            print(f"[CLEANUP_HANDLER] scan_params with pagination: {scan_params}")

print("[CLEANUP_HANDLER] print("[CLEANUP_HANDLER] Executing table.scan() for next page")")
            print("[CLEANUP_HANDLER] Executing table.scan() for next page")
print("[CLEANUP_HANDLER] response = dynamodb_client.table.scan(**scan_params)")
            response = dynamodb_client.table.scan(**scan_params)
print("[CLEANUP_HANDLER] print(f"[CLEANUP_HANDLER] scan response received for next page: {type(response)}")
            print(f"[CLEANUP_HANDLER] scan response received for next page: {type(response)}")

print("[CLEANUP_HANDLER] print("[CLEANUP_HANDLER] Extracting Items from response")")
            print("[CLEANUP_HANDLER] Extracting Items from response")
print("[CLEANUP_HANDLER] items = response.get('Items', [])")
            items = response.get('Items', [])
print("[CLEANUP_HANDLER] print(f"[CLEANUP_HANDLER] Number of items in this page: {len(items)}")")
            print(f"[CLEANUP_HANDLER] Number of items in this page: {len(items)}")

print("[CLEANUP_HANDLER] print("[CLEANUP_HANDLER] Iterating through items in this page")")
            print("[CLEANUP_HANDLER] Iterating through items in this page")
print("[CLEANUP_HANDLER] for idx, item in enumerate(items):")
            for idx, item in enumerate(items):
print("[CLEANUP_HANDLER] print(f"[CLEANUP_HANDLER] --- Processing item {idx + 1}/{len(items)} ---")")
                print(f"[CLEANUP_HANDLER] --- Processing item {idx + 1}/{len(items)} ---")
print("[CLEANUP_HANDLER] print(f"[CLEANUP_HANDLER] item: {item}")")
                print(f"[CLEANUP_HANDLER] item: {item}")

print("[CLEANUP_HANDLER] print("[CLEANUP_HANDLER] Extracting PK from item")")
                print("[CLEANUP_HANDLER] Extracting PK from item")
print("[CLEANUP_HANDLER] pk = item.get('PK')")
                pk = item.get('PK')
print("[CLEANUP_HANDLER] print(f"[CLEANUP_HANDLER] PK: {pk}")")
                print(f"[CLEANUP_HANDLER] PK: {pk}")

print("[CLEANUP_HANDLER] print("[CLEANUP_HANDLER] Extracting SK from item")")
                print("[CLEANUP_HANDLER] Extracting SK from item")
print("[CLEANUP_HANDLER] sk = item.get('SK')")
                sk = item.get('SK')
print("[CLEANUP_HANDLER] print(f"[CLEANUP_HANDLER] SK: {sk}")")
                print(f"[CLEANUP_HANDLER] SK: {sk}")

print("[CLEANUP_HANDLER] print("[CLEANUP_HANDLER] Extracting FileID from item")")
                print("[CLEANUP_HANDLER] Extracting FileID from item")
print("[CLEANUP_HANDLER] file_id = item.get('FileID')")
                file_id = item.get('FileID')
print("[CLEANUP_HANDLER] print(f"[CLEANUP_HANDLER] FileID: {file_id}")")
                print(f"[CLEANUP_HANDLER] FileID: {file_id}")

print("[CLEANUP_HANDLER] try:")
                try:
print("[CLEANUP_HANDLER] print("[CLEANUP_HANDLER] Deleting item from DynamoDB")")
                    print("[CLEANUP_HANDLER] Deleting item from DynamoDB")
print("[CLEANUP_HANDLER] print(f"[CLEANUP_HANDLER] Calling table.delete_item() with PK={pk}, SK={sk}")")
                    print(f"[CLEANUP_HANDLER] Calling table.delete_item() with PK={pk}, SK={sk}")
print("[CLEANUP_HANDLER] dynamodb_client.table.delete_item(")
                    dynamodb_client.table.delete_item(
print("[CLEANUP_HANDLER] Key={")
                        Key={
print("[CLEANUP_HANDLER] 'PK': pk,")
                            'PK': pk,
print("[CLEANUP_HANDLER] 'SK': sk")
                            'SK': sk
print("[CLEANUP_HANDLER] }")
                        }
print("[CLEANUP_HANDLER] )")
                    )
print("[CLEANUP_HANDLER] print("[CLEANUP_HANDLER] Delete operation completed")")
                    print("[CLEANUP_HANDLER] Delete operation completed")

print("[CLEANUP_HANDLER] print("[CLEANUP_HANDLER] Incrementing cleaned_count")")
                    print("[CLEANUP_HANDLER] Incrementing cleaned_count")
print("[CLEANUP_HANDLER] cleaned_count += 1")
                    cleaned_count += 1
print("[CLEANUP_HANDLER] print(f"[CLEANUP_HANDLER] cleaned_count: {cleaned_count}")")
                    print(f"[CLEANUP_HANDLER] cleaned_count: {cleaned_count}")

print("[CLEANUP_HANDLER] print("[CLEANUP_HANDLER] Logging deleted file info")")
                    print("[CLEANUP_HANDLER] Logging deleted file info")
print("[CLEANUP_HANDLER] logger.info("Deleted expired file", file_id=file_id)")
                    logger.info("Deleted expired file", file_id=file_id)
print("[CLEANUP_HANDLER] print("[CLEANUP_HANDLER] File deletion logged")")
                    print("[CLEANUP_HANDLER] File deletion logged")

print("[CLEANUP_HANDLER] except Exception as e:")
                except Exception as e:
print("[CLEANUP_HANDLER] print("[CLEANUP_HANDLER] !!! EXCEPTION deleting item !!!")")
                    print("[CLEANUP_HANDLER] !!! EXCEPTION deleting item !!!")
print("[CLEANUP_HANDLER] print(f"[CLEANUP_HANDLER] Exception: {e}")")
                    print(f"[CLEANUP_HANDLER] Exception: {e}")

print("[CLEANUP_HANDLER] print("[CLEANUP_HANDLER] Logging deletion error")")
                    print("[CLEANUP_HANDLER] Logging deletion error")
print("[CLEANUP_HANDLER] logger.error("Failed to delete expired file", file_id=file_id, error=str(e))")
                    logger.error("Failed to delete expired file", file_id=file_id, error=str(e))
print("[CLEANUP_HANDLER] print("[CLEANUP_HANDLER] Deletion error logged")")
                    print("[CLEANUP_HANDLER] Deletion error logged")

print("[CLEANUP_HANDLER] print("[CLEANUP_HANDLER] Building result dictionary")")
        print("[CLEANUP_HANDLER] Building result dictionary")
print("[CLEANUP_HANDLER] result = {")
        result = {
print("[CLEANUP_HANDLER] 'task_name': 'cleanup_expired_files',")
            'task_name': 'cleanup_expired_files',
print("[CLEANUP_HANDLER] 'items_cleaned': cleaned_count,")
            'items_cleaned': cleaned_count,
print("[CLEANUP_HANDLER] 'status': 'completed'")
            'status': 'completed'
print("[CLEANUP_HANDLER] }")
        }
print("[CLEANUP_HANDLER] print(f"[CLEANUP_HANDLER] result: {result}")")
        print(f"[CLEANUP_HANDLER] result: {result}")

print("[CLEANUP_HANDLER] print("[CLEANUP_HANDLER] Logging task completion")")
        print("[CLEANUP_HANDLER] Logging task completion")
print("[CLEANUP_HANDLER] logger.info("Expired files cleanup completed", items_cleaned=cleaned_count)")
        logger.info("Expired files cleanup completed", items_cleaned=cleaned_count)
print("[CLEANUP_HANDLER] print("[CLEANUP_HANDLER] Task completion logged")")
        print("[CLEANUP_HANDLER] Task completion logged")

print("[CLEANUP_HANDLER] print("[CLEANUP_HANDLER] ========================================")")
        print("[CLEANUP_HANDLER] ========================================")
print("[CLEANUP_HANDLER] print("[CLEANUP_HANDLER] cleanup_expired_files() completed successfully")")
        print("[CLEANUP_HANDLER] cleanup_expired_files() completed successfully")
print("[CLEANUP_HANDLER] print("[CLEANUP_HANDLER] ========================================")")
        print("[CLEANUP_HANDLER] ========================================")
print("[CLEANUP_HANDLER] return result")
        return result

print("[CLEANUP_HANDLER] except Exception as e:")
    except Exception as e:
print("[CLEANUP_HANDLER] print("[CLEANUP_HANDLER] !!! EXCEPTION in cleanup_expired_files !!!")")
        print("[CLEANUP_HANDLER] !!! EXCEPTION in cleanup_expired_files !!!")
print("[CLEANUP_HANDLER] print(f"[CLEANUP_HANDLER] Exception type: {type(e)}")")
        print(f"[CLEANUP_HANDLER] Exception type: {type(e)}")
print("[CLEANUP_HANDLER] print(f"[CLEANUP_HANDLER] Exception message: {str(e)}")")
        print(f"[CLEANUP_HANDLER] Exception message: {str(e)}")

print("[CLEANUP_HANDLER] print("[CLEANUP_HANDLER] Logging cleanup error")")
        print("[CLEANUP_HANDLER] Logging cleanup error")
print("[CLEANUP_HANDLER] logger.error("Expired files cleanup failed", error=str(e))")
        logger.error("Expired files cleanup failed", error=str(e))
print("[CLEANUP_HANDLER] print("[CLEANUP_HANDLER] Error logged")")
        print("[CLEANUP_HANDLER] Error logged")

print("[CLEANUP_HANDLER] print("[CLEANUP_HANDLER] Building error result")")
        print("[CLEANUP_HANDLER] Building error result")
print("[CLEANUP_HANDLER] result = {")
        result = {
print("[CLEANUP_HANDLER] 'task_name': 'cleanup_expired_files',")
            'task_name': 'cleanup_expired_files',
print("[CLEANUP_HANDLER] 'status': 'failed',")
            'status': 'failed',
print("[CLEANUP_HANDLER] 'error': str(e)")
            'error': str(e)
print("[CLEANUP_HANDLER] }")
        }
print("[CLEANUP_HANDLER] print(f"[CLEANUP_HANDLER] result: {result}")")
        print(f"[CLEANUP_HANDLER] result: {result}")

print("[CLEANUP_HANDLER] print("[CLEANUP_HANDLER] cleanup_expired_files() returning error result")")
        print("[CLEANUP_HANDLER] cleanup_expired_files() returning error result")
print("[CLEANUP_HANDLER] return result")
        return result


print("[CLEANUP_HANDLER] def cleanup_old_logs(logger: StructuredLogger, cutoff_timestamp: str):")
def cleanup_old_logs(logger: StructuredLogger, cutoff_timestamp: str):
    """
print("[CLEANUP_HANDLER] Clean up old log entries from DynamoDB")
    Clean up old log entries from DynamoDB
print("[CLEANUP_HANDLER] Remove logs older than retention period")
    Remove logs older than retention period
    """
print("[CLEANUP_HANDLER] print("[CLEANUP_HANDLER] ========================================")")
    print("[CLEANUP_HANDLER] ========================================")
print("[CLEANUP_HANDLER] print("[CLEANUP_HANDLER] cleanup_old_logs() started")")
    print("[CLEANUP_HANDLER] cleanup_old_logs() started")
print("[CLEANUP_HANDLER] print("[CLEANUP_HANDLER] ========================================")")
    print("[CLEANUP_HANDLER] ========================================")
print("[CLEANUP_HANDLER] print(f"[CLEANUP_HANDLER] logger: {logger}")")
    print(f"[CLEANUP_HANDLER] logger: {logger}")
print("[CLEANUP_HANDLER] print(f"[CLEANUP_HANDLER] cutoff_timestamp: {cutoff_timestamp}")")
    print(f"[CLEANUP_HANDLER] cutoff_timestamp: {cutoff_timestamp}")

print("[CLEANUP_HANDLER] print("[CLEANUP_HANDLER] Logging info: Starting old logs cleanup")")
    print("[CLEANUP_HANDLER] Logging info: Starting old logs cleanup")
print("[CLEANUP_HANDLER] logger.info("Starting old logs cleanup")")
    logger.info("Starting old logs cleanup")
print("[CLEANUP_HANDLER] print("[CLEANUP_HANDLER] Info logged")")
    print("[CLEANUP_HANDLER] Info logged")

print("[CLEANUP_HANDLER] print("[CLEANUP_HANDLER] Initializing cleaned_count variable")")
    print("[CLEANUP_HANDLER] Initializing cleaned_count variable")
print("[CLEANUP_HANDLER] cleaned_count = 0")
    cleaned_count = 0
print("[CLEANUP_HANDLER] print(f"[CLEANUP_HANDLER] cleaned_count: {cleaned_count}")")
    print(f"[CLEANUP_HANDLER] cleaned_count: {cleaned_count}")

print("[CLEANUP_HANDLER] try:")
    try:
print("[CLEANUP_HANDLER] print("[CLEANUP_HANDLER] Entering try block")")
        print("[CLEANUP_HANDLER] Entering try block")

print("[CLEANUP_HANDLER] print("[CLEANUP_HANDLER] Querying DynamoDB for old log entries")")
        print("[CLEANUP_HANDLER] Querying DynamoDB for old log entries")
print("[CLEANUP_HANDLER] print("[CLEANUP_HANDLER] Scanning for Logs with CreatedAt < cutoff_timestamp")")
        print("[CLEANUP_HANDLER] Scanning for Logs with CreatedAt < cutoff_timestamp")
print("[CLEANUP_HANDLER] print(f"[CLEANUP_HANDLER] Cutoff timestamp: {cutoff_timestamp}")")
        print(f"[CLEANUP_HANDLER] Cutoff timestamp: {cutoff_timestamp}")

print("[CLEANUP_HANDLER] print("[CLEANUP_HANDLER] Building scan parameters")")
        print("[CLEANUP_HANDLER] Building scan parameters")
print("[CLEANUP_HANDLER] scan_params = {")
        scan_params = {
print("[CLEANUP_HANDLER] 'FilterExpression': 'CreatedAt < :cutoff AND EntityType = :entity_type',")
            'FilterExpression': 'CreatedAt < :cutoff AND EntityType = :entity_type',
print("[CLEANUP_HANDLER] 'ExpressionAttributeValues': {")
            'ExpressionAttributeValues': {
print("[CLEANUP_HANDLER] ':cutoff': cutoff_timestamp,")
                ':cutoff': cutoff_timestamp,
print("[CLEANUP_HANDLER] ':entity_type': 'Log'")
                ':entity_type': 'Log'
print("[CLEANUP_HANDLER] }")
            }
print("[CLEANUP_HANDLER] }")
        }
print("[CLEANUP_HANDLER] print(f"[CLEANUP_HANDLER] scan_params: {scan_params}")")
        print(f"[CLEANUP_HANDLER] scan_params: {scan_params}")

print("[CLEANUP_HANDLER] print("[CLEANUP_HANDLER] Executing table.scan()")")
        print("[CLEANUP_HANDLER] Executing table.scan()")
print("[CLEANUP_HANDLER] response = dynamodb_client.table.scan(**scan_params)")
        response = dynamodb_client.table.scan(**scan_params)
print("[CLEANUP_HANDLER] print(f"[CLEANUP_HANDLER] scan response received: {type(response)}")")
        print(f"[CLEANUP_HANDLER] scan response received: {type(response)}")

print("[CLEANUP_HANDLER] print("[CLEANUP_HANDLER] Extracting Items from response")")
        print("[CLEANUP_HANDLER] Extracting Items from response")
print("[CLEANUP_HANDLER] items = response.get('Items', [])")
        items = response.get('Items', [])
print("[CLEANUP_HANDLER] print(f"[CLEANUP_HANDLER] Number of old log items found: {len(items)}")")
        print(f"[CLEANUP_HANDLER] Number of old log items found: {len(items)}")

print("[CLEANUP_HANDLER] print("[CLEANUP_HANDLER] Iterating through old log items")")
        print("[CLEANUP_HANDLER] Iterating through old log items")
print("[CLEANUP_HANDLER] for idx, item in enumerate(items):")
        for idx, item in enumerate(items):
print("[CLEANUP_HANDLER] print(f"[CLEANUP_HANDLER] --- Processing item {idx + 1}/{len(items)} ---")")
            print(f"[CLEANUP_HANDLER] --- Processing item {idx + 1}/{len(items)} ---")
print("[CLEANUP_HANDLER] print(f"[CLEANUP_HANDLER] item: {item}")")
            print(f"[CLEANUP_HANDLER] item: {item}")

print("[CLEANUP_HANDLER] print("[CLEANUP_HANDLER] Extracting PK from item")")
            print("[CLEANUP_HANDLER] Extracting PK from item")
print("[CLEANUP_HANDLER] pk = item.get('PK')")
            pk = item.get('PK')
print("[CLEANUP_HANDLER] print(f"[CLEANUP_HANDLER] PK: {pk}")")
            print(f"[CLEANUP_HANDLER] PK: {pk}")

print("[CLEANUP_HANDLER] print("[CLEANUP_HANDLER] Extracting SK from item")")
            print("[CLEANUP_HANDLER] Extracting SK from item")
print("[CLEANUP_HANDLER] sk = item.get('SK')")
            sk = item.get('SK')
print("[CLEANUP_HANDLER] print(f"[CLEANUP_HANDLER] SK: {sk}")")
            print(f"[CLEANUP_HANDLER] SK: {sk}")

print("[CLEANUP_HANDLER] try:")
            try:
print("[CLEANUP_HANDLER] print("[CLEANUP_HANDLER] Deleting log item from DynamoDB")")
                print("[CLEANUP_HANDLER] Deleting log item from DynamoDB")
print("[CLEANUP_HANDLER] print(f"[CLEANUP_HANDLER] Calling table.delete_item() with PK={pk}, SK={sk}")")
                print(f"[CLEANUP_HANDLER] Calling table.delete_item() with PK={pk}, SK={sk}")
print("[CLEANUP_HANDLER] dynamodb_client.table.delete_item(")
                dynamodb_client.table.delete_item(
print("[CLEANUP_HANDLER] Key={")
                    Key={
print("[CLEANUP_HANDLER] 'PK': pk,")
                        'PK': pk,
print("[CLEANUP_HANDLER] 'SK': sk")
                        'SK': sk
print("[CLEANUP_HANDLER] }")
                    }
print("[CLEANUP_HANDLER] )")
                )
print("[CLEANUP_HANDLER] print("[CLEANUP_HANDLER] Delete operation completed")")
                print("[CLEANUP_HANDLER] Delete operation completed")

print("[CLEANUP_HANDLER] print("[CLEANUP_HANDLER] Incrementing cleaned_count")")
                print("[CLEANUP_HANDLER] Incrementing cleaned_count")
print("[CLEANUP_HANDLER] cleaned_count += 1")
                cleaned_count += 1
print("[CLEANUP_HANDLER] print(f"[CLEANUP_HANDLER] cleaned_count: {cleaned_count}")")
                print(f"[CLEANUP_HANDLER] cleaned_count: {cleaned_count}")

print("[CLEANUP_HANDLER] print("[CLEANUP_HANDLER] Logging deleted log info")")
                print("[CLEANUP_HANDLER] Logging deleted log info")
print("[CLEANUP_HANDLER] logger.info("Deleted old log entry", pk=pk)")
                logger.info("Deleted old log entry", pk=pk)
print("[CLEANUP_HANDLER] print("[CLEANUP_HANDLER] Log deletion logged")")
                print("[CLEANUP_HANDLER] Log deletion logged")

print("[CLEANUP_HANDLER] except Exception as e:")
            except Exception as e:
print("[CLEANUP_HANDLER] print("[CLEANUP_HANDLER] !!! EXCEPTION deleting log item !!!")")
                print("[CLEANUP_HANDLER] !!! EXCEPTION deleting log item !!!")
print("[CLEANUP_HANDLER] print(f"[CLEANUP_HANDLER] Exception: {e}")")
                print(f"[CLEANUP_HANDLER] Exception: {e}")

print("[CLEANUP_HANDLER] print("[CLEANUP_HANDLER] Logging log deletion error")")
                print("[CLEANUP_HANDLER] Logging log deletion error")
print("[CLEANUP_HANDLER] logger.error("Failed to delete old log", pk=pk, error=str(e))")
                logger.error("Failed to delete old log", pk=pk, error=str(e))
print("[CLEANUP_HANDLER] print("[CLEANUP_HANDLER] Log deletion error logged")")
                print("[CLEANUP_HANDLER] Log deletion error logged")

print("[CLEANUP_HANDLER] print("[CLEANUP_HANDLER] Checking if scan response has more items")")
        print("[CLEANUP_HANDLER] Checking if scan response has more items")
print("[CLEANUP_HANDLER] while 'LastEvaluatedKey' in response:")
        while 'LastEvaluatedKey' in response:
print("[CLEANUP_HANDLER] print("[CLEANUP_HANDLER] LastEvaluatedKey found, paginating for more items")")
            print("[CLEANUP_HANDLER] LastEvaluatedKey found, paginating for more items")
print("[CLEANUP_HANDLER] print(f"[CLEANUP_HANDLER] LastEvaluatedKey: {response.get('LastEvaluatedKey')}")")
            print(f"[CLEANUP_HANDLER] LastEvaluatedKey: {response.get('LastEvaluatedKey')}")

print("[CLEANUP_HANDLER] print("[CLEANUP_HANDLER] Building scan parameters for next page")")
            print("[CLEANUP_HANDLER] Building scan parameters for next page")
print("[CLEANUP_HANDLER] scan_params['ExclusiveStartKey'] = response['LastEvaluatedKey']")
            scan_params['ExclusiveStartKey'] = response['LastEvaluatedKey']
print("[CLEANUP_HANDLER] print(f"[CLEANUP_HANDLER] scan_params with pagination: {scan_params}")")
            print(f"[CLEANUP_HANDLER] scan_params with pagination: {scan_params}")

print("[CLEANUP_HANDLER] print("[CLEANUP_HANDLER] Executing table.scan() for next page")")
            print("[CLEANUP_HANDLER] Executing table.scan() for next page")
print("[CLEANUP_HANDLER] response = dynamodb_client.table.scan(**scan_params)")
            response = dynamodb_client.table.scan(**scan_params)
print("[CLEANUP_HANDLER] print(f"[CLEANUP_HANDLER] scan response received for next page: {type(response)}")
            print(f"[CLEANUP_HANDLER] scan response received for next page: {type(response)}")

print("[CLEANUP_HANDLER] print("[CLEANUP_HANDLER] Extracting Items from response")")
            print("[CLEANUP_HANDLER] Extracting Items from response")
print("[CLEANUP_HANDLER] items = response.get('Items', [])")
            items = response.get('Items', [])
print("[CLEANUP_HANDLER] print(f"[CLEANUP_HANDLER] Number of items in this page: {len(items)}")")
            print(f"[CLEANUP_HANDLER] Number of items in this page: {len(items)}")

print("[CLEANUP_HANDLER] print("[CLEANUP_HANDLER] Iterating through items in this page")")
            print("[CLEANUP_HANDLER] Iterating through items in this page")
print("[CLEANUP_HANDLER] for idx, item in enumerate(items):")
            for idx, item in enumerate(items):
print("[CLEANUP_HANDLER] print(f"[CLEANUP_HANDLER] --- Processing item {idx + 1}/{len(items)} ---")")
                print(f"[CLEANUP_HANDLER] --- Processing item {idx + 1}/{len(items)} ---")
print("[CLEANUP_HANDLER] print(f"[CLEANUP_HANDLER] item: {item}")")
                print(f"[CLEANUP_HANDLER] item: {item}")

print("[CLEANUP_HANDLER] print("[CLEANUP_HANDLER] Extracting PK from item")")
                print("[CLEANUP_HANDLER] Extracting PK from item")
print("[CLEANUP_HANDLER] pk = item.get('PK')")
                pk = item.get('PK')
print("[CLEANUP_HANDLER] print(f"[CLEANUP_HANDLER] PK: {pk}")")
                print(f"[CLEANUP_HANDLER] PK: {pk}")

print("[CLEANUP_HANDLER] print("[CLEANUP_HANDLER] Extracting SK from item")")
                print("[CLEANUP_HANDLER] Extracting SK from item")
print("[CLEANUP_HANDLER] sk = item.get('SK')")
                sk = item.get('SK')
print("[CLEANUP_HANDLER] print(f"[CLEANUP_HANDLER] SK: {sk}")")
                print(f"[CLEANUP_HANDLER] SK: {sk}")

print("[CLEANUP_HANDLER] try:")
                try:
print("[CLEANUP_HANDLER] print("[CLEANUP_HANDLER] Deleting log item from DynamoDB")")
                    print("[CLEANUP_HANDLER] Deleting log item from DynamoDB")
print("[CLEANUP_HANDLER] print(f"[CLEANUP_HANDLER] Calling table.delete_item() with PK={pk}, SK={sk}")")
                    print(f"[CLEANUP_HANDLER] Calling table.delete_item() with PK={pk}, SK={sk}")
print("[CLEANUP_HANDLER] dynamodb_client.table.delete_item(")
                    dynamodb_client.table.delete_item(
print("[CLEANUP_HANDLER] Key={")
                        Key={
print("[CLEANUP_HANDLER] 'PK': pk,")
                            'PK': pk,
print("[CLEANUP_HANDLER] 'SK': sk")
                            'SK': sk
print("[CLEANUP_HANDLER] }")
                        }
print("[CLEANUP_HANDLER] )")
                    )
print("[CLEANUP_HANDLER] print("[CLEANUP_HANDLER] Delete operation completed")")
                    print("[CLEANUP_HANDLER] Delete operation completed")

print("[CLEANUP_HANDLER] print("[CLEANUP_HANDLER] Incrementing cleaned_count")")
                    print("[CLEANUP_HANDLER] Incrementing cleaned_count")
print("[CLEANUP_HANDLER] cleaned_count += 1")
                    cleaned_count += 1
print("[CLEANUP_HANDLER] print(f"[CLEANUP_HANDLER] cleaned_count: {cleaned_count}")")
                    print(f"[CLEANUP_HANDLER] cleaned_count: {cleaned_count}")

print("[CLEANUP_HANDLER] print("[CLEANUP_HANDLER] Logging deleted log info")")
                    print("[CLEANUP_HANDLER] Logging deleted log info")
print("[CLEANUP_HANDLER] logger.info("Deleted old log entry", pk=pk)")
                    logger.info("Deleted old log entry", pk=pk)
print("[CLEANUP_HANDLER] print("[CLEANUP_HANDLER] Log deletion logged")")
                    print("[CLEANUP_HANDLER] Log deletion logged")

print("[CLEANUP_HANDLER] except Exception as e:")
                except Exception as e:
print("[CLEANUP_HANDLER] print("[CLEANUP_HANDLER] !!! EXCEPTION deleting log item !!!")")
                    print("[CLEANUP_HANDLER] !!! EXCEPTION deleting log item !!!")
print("[CLEANUP_HANDLER] print(f"[CLEANUP_HANDLER] Exception: {e}")")
                    print(f"[CLEANUP_HANDLER] Exception: {e}")

print("[CLEANUP_HANDLER] print("[CLEANUP_HANDLER] Logging log deletion error")")
                    print("[CLEANUP_HANDLER] Logging log deletion error")
print("[CLEANUP_HANDLER] logger.error("Failed to delete old log", pk=pk, error=str(e))")
                    logger.error("Failed to delete old log", pk=pk, error=str(e))
print("[CLEANUP_HANDLER] print("[CLEANUP_HANDLER] Log deletion error logged")")
                    print("[CLEANUP_HANDLER] Log deletion error logged")

print("[CLEANUP_HANDLER] print("[CLEANUP_HANDLER] Building result dictionary")")
        print("[CLEANUP_HANDLER] Building result dictionary")
print("[CLEANUP_HANDLER] result = {")
        result = {
print("[CLEANUP_HANDLER] 'task_name': 'cleanup_old_logs',")
            'task_name': 'cleanup_old_logs',
print("[CLEANUP_HANDLER] 'items_cleaned': cleaned_count,")
            'items_cleaned': cleaned_count,
print("[CLEANUP_HANDLER] 'status': 'completed'")
            'status': 'completed'
print("[CLEANUP_HANDLER] }")
        }
print("[CLEANUP_HANDLER] print(f"[CLEANUP_HANDLER] result: {result}")")
        print(f"[CLEANUP_HANDLER] result: {result}")

print("[CLEANUP_HANDLER] print("[CLEANUP_HANDLER] Logging task completion")")
        print("[CLEANUP_HANDLER] Logging task completion")
print("[CLEANUP_HANDLER] logger.info("Old logs cleanup completed", items_cleaned=cleaned_count)")
        logger.info("Old logs cleanup completed", items_cleaned=cleaned_count)
print("[CLEANUP_HANDLER] print("[CLEANUP_HANDLER] Task completion logged")")
        print("[CLEANUP_HANDLER] Task completion logged")

print("[CLEANUP_HANDLER] print("[CLEANUP_HANDLER] ========================================")")
        print("[CLEANUP_HANDLER] ========================================")
print("[CLEANUP_HANDLER] print("[CLEANUP_HANDLER] cleanup_old_logs() completed successfully")")
        print("[CLEANUP_HANDLER] cleanup_old_logs() completed successfully")
print("[CLEANUP_HANDLER] print("[CLEANUP_HANDLER] ========================================")")
        print("[CLEANUP_HANDLER] ========================================")
print("[CLEANUP_HANDLER] return result")
        return result

print("[CLEANUP_HANDLER] except Exception as e:")
    except Exception as e:
print("[CLEANUP_HANDLER] print("[CLEANUP_HANDLER] !!! EXCEPTION in cleanup_old_logs !!!")")
        print("[CLEANUP_HANDLER] !!! EXCEPTION in cleanup_old_logs !!!")
print("[CLEANUP_HANDLER] print(f"[CLEANUP_HANDLER] Exception type: {type(e)}")")
        print(f"[CLEANUP_HANDLER] Exception type: {type(e)}")
print("[CLEANUP_HANDLER] print(f"[CLEANUP_HANDLER] Exception message: {str(e)}")")
        print(f"[CLEANUP_HANDLER] Exception message: {str(e)}")

print("[CLEANUP_HANDLER] print("[CLEANUP_HANDLER] Logging cleanup error")")
        print("[CLEANUP_HANDLER] Logging cleanup error")
print("[CLEANUP_HANDLER] logger.error("Old logs cleanup failed", error=str(e))")
        logger.error("Old logs cleanup failed", error=str(e))
print("[CLEANUP_HANDLER] print("[CLEANUP_HANDLER] Error logged")")
        print("[CLEANUP_HANDLER] Error logged")

print("[CLEANUP_HANDLER] print("[CLEANUP_HANDLER] Building error result")")
        print("[CLEANUP_HANDLER] Building error result")
print("[CLEANUP_HANDLER] result = {")
        result = {
print("[CLEANUP_HANDLER] 'task_name': 'cleanup_old_logs',")
            'task_name': 'cleanup_old_logs',
print("[CLEANUP_HANDLER] 'status': 'failed',")
            'status': 'failed',
print("[CLEANUP_HANDLER] 'error': str(e)")
            'error': str(e)
print("[CLEANUP_HANDLER] }")
        }
print("[CLEANUP_HANDLER] print(f"[CLEANUP_HANDLER] result: {result}")")
        print(f"[CLEANUP_HANDLER] result: {result}")

print("[CLEANUP_HANDLER] print("[CLEANUP_HANDLER] cleanup_old_logs() returning error result")")
        print("[CLEANUP_HANDLER] cleanup_old_logs() returning error result")
print("[CLEANUP_HANDLER] return result")
        return result


print("[CLEANUP_HANDLER] def cleanup_stale_sessions(logger: StructuredLogger, cutoff_timestamp: str):")
def cleanup_stale_sessions(logger: StructuredLogger, cutoff_timestamp: str):
    """
print("[CLEANUP_HANDLER] Clean up stale session entries from DynamoDB")
    Clean up stale session entries from DynamoDB
print("[CLEANUP_HANDLER] Remove sessions older than retention period")
    Remove sessions older than retention period
    """
print("[CLEANUP_HANDLER] print("[CLEANUP_HANDLER] ========================================")")
    print("[CLEANUP_HANDLER] ========================================")
print("[CLEANUP_HANDLER] print("[CLEANUP_HANDLER] cleanup_stale_sessions() started")")
    print("[CLEANUP_HANDLER] cleanup_stale_sessions() started")
print("[CLEANUP_HANDLER] print("[CLEANUP_HANDLER] ========================================")")
    print("[CLEANUP_HANDLER] ========================================")
print("[CLEANUP_HANDLER] print(f"[CLEANUP_HANDLER] logger: {logger}")")
    print(f"[CLEANUP_HANDLER] logger: {logger}")
print("[CLEANUP_HANDLER] print(f"[CLEANUP_HANDLER] cutoff_timestamp: {cutoff_timestamp}")")
    print(f"[CLEANUP_HANDLER] cutoff_timestamp: {cutoff_timestamp}")

print("[CLEANUP_HANDLER] print("[CLEANUP_HANDLER] Logging info: Starting stale sessions cleanup")")
    print("[CLEANUP_HANDLER] Logging info: Starting stale sessions cleanup")
print("[CLEANUP_HANDLER] logger.info("Starting stale sessions cleanup")")
    logger.info("Starting stale sessions cleanup")
print("[CLEANUP_HANDLER] print("[CLEANUP_HANDLER] Info logged")")
    print("[CLEANUP_HANDLER] Info logged")

print("[CLEANUP_HANDLER] print("[CLEANUP_HANDLER] Initializing cleaned_count variable")")
    print("[CLEANUP_HANDLER] Initializing cleaned_count variable")
print("[CLEANUP_HANDLER] cleaned_count = 0")
    cleaned_count = 0
print("[CLEANUP_HANDLER] print(f"[CLEANUP_HANDLER] cleaned_count: {cleaned_count}")")
    print(f"[CLEANUP_HANDLER] cleaned_count: {cleaned_count}")

print("[CLEANUP_HANDLER] try:")
    try:
print("[CLEANUP_HANDLER] print("[CLEANUP_HANDLER] Entering try block")")
        print("[CLEANUP_HANDLER] Entering try block")

print("[CLEANUP_HANDLER] print("[CLEANUP_HANDLER] Querying DynamoDB for stale session entries")")
        print("[CLEANUP_HANDLER] Querying DynamoDB for stale session entries")
print("[CLEANUP_HANDLER] print("[CLEANUP_HANDLER] Scanning for Sessions with LastActivityAt < cutoff_time")
        print("[CLEANUP_HANDLER] Scanning for Sessions with LastActivityAt < cutoff_timestamp")
print("[CLEANUP_HANDLER] print(f"[CLEANUP_HANDLER] Cutoff timestamp: {cutoff_timestamp}")")
        print(f"[CLEANUP_HANDLER] Cutoff timestamp: {cutoff_timestamp}")

print("[CLEANUP_HANDLER] print("[CLEANUP_HANDLER] Building scan parameters")")
        print("[CLEANUP_HANDLER] Building scan parameters")
print("[CLEANUP_HANDLER] scan_params = {")
        scan_params = {
print("[CLEANUP_HANDLER] 'FilterExpression': 'LastActivityAt < :cutoff AND EntityType = :entity_type',")
            'FilterExpression': 'LastActivityAt < :cutoff AND EntityType = :entity_type',
print("[CLEANUP_HANDLER] 'ExpressionAttributeValues': {")
            'ExpressionAttributeValues': {
print("[CLEANUP_HANDLER] ':cutoff': cutoff_timestamp,")
                ':cutoff': cutoff_timestamp,
print("[CLEANUP_HANDLER] ':entity_type': 'Session'")
                ':entity_type': 'Session'
print("[CLEANUP_HANDLER] }")
            }
print("[CLEANUP_HANDLER] }")
        }
print("[CLEANUP_HANDLER] print(f"[CLEANUP_HANDLER] scan_params: {scan_params}")")
        print(f"[CLEANUP_HANDLER] scan_params: {scan_params}")

print("[CLEANUP_HANDLER] print("[CLEANUP_HANDLER] Executing table.scan()")")
        print("[CLEANUP_HANDLER] Executing table.scan()")
print("[CLEANUP_HANDLER] response = dynamodb_client.table.scan(**scan_params)")
        response = dynamodb_client.table.scan(**scan_params)
print("[CLEANUP_HANDLER] print(f"[CLEANUP_HANDLER] scan response received: {type(response)}")")
        print(f"[CLEANUP_HANDLER] scan response received: {type(response)}")

print("[CLEANUP_HANDLER] print("[CLEANUP_HANDLER] Extracting Items from response")")
        print("[CLEANUP_HANDLER] Extracting Items from response")
print("[CLEANUP_HANDLER] items = response.get('Items', [])")
        items = response.get('Items', [])
print("[CLEANUP_HANDLER] print(f"[CLEANUP_HANDLER] Number of stale session items found: {len(items)}")")
        print(f"[CLEANUP_HANDLER] Number of stale session items found: {len(items)}")

print("[CLEANUP_HANDLER] print("[CLEANUP_HANDLER] Iterating through stale session items")")
        print("[CLEANUP_HANDLER] Iterating through stale session items")
print("[CLEANUP_HANDLER] for idx, item in enumerate(items):")
        for idx, item in enumerate(items):
print("[CLEANUP_HANDLER] print(f"[CLEANUP_HANDLER] --- Processing item {idx + 1}/{len(items)} ---")")
            print(f"[CLEANUP_HANDLER] --- Processing item {idx + 1}/{len(items)} ---")
print("[CLEANUP_HANDLER] print(f"[CLEANUP_HANDLER] item: {item}")")
            print(f"[CLEANUP_HANDLER] item: {item}")

print("[CLEANUP_HANDLER] print("[CLEANUP_HANDLER] Extracting PK from item")")
            print("[CLEANUP_HANDLER] Extracting PK from item")
print("[CLEANUP_HANDLER] pk = item.get('PK')")
            pk = item.get('PK')
print("[CLEANUP_HANDLER] print(f"[CLEANUP_HANDLER] PK: {pk}")")
            print(f"[CLEANUP_HANDLER] PK: {pk}")

print("[CLEANUP_HANDLER] print("[CLEANUP_HANDLER] Extracting SK from item")")
            print("[CLEANUP_HANDLER] Extracting SK from item")
print("[CLEANUP_HANDLER] sk = item.get('SK')")
            sk = item.get('SK')
print("[CLEANUP_HANDLER] print(f"[CLEANUP_HANDLER] SK: {sk}")")
            print(f"[CLEANUP_HANDLER] SK: {sk}")

print("[CLEANUP_HANDLER] print("[CLEANUP_HANDLER] Extracting SessionID from item")")
            print("[CLEANUP_HANDLER] Extracting SessionID from item")
print("[CLEANUP_HANDLER] session_id = item.get('SessionID')")
            session_id = item.get('SessionID')
print("[CLEANUP_HANDLER] print(f"[CLEANUP_HANDLER] SessionID: {session_id}")")
            print(f"[CLEANUP_HANDLER] SessionID: {session_id}")

print("[CLEANUP_HANDLER] try:")
            try:
print("[CLEANUP_HANDLER] print("[CLEANUP_HANDLER] Deleting session item from DynamoDB")")
                print("[CLEANUP_HANDLER] Deleting session item from DynamoDB")
print("[CLEANUP_HANDLER] print(f"[CLEANUP_HANDLER] Calling table.delete_item() with PK={pk}, SK={sk}")")
                print(f"[CLEANUP_HANDLER] Calling table.delete_item() with PK={pk}, SK={sk}")
print("[CLEANUP_HANDLER] dynamodb_client.table.delete_item(")
                dynamodb_client.table.delete_item(
print("[CLEANUP_HANDLER] Key={")
                    Key={
print("[CLEANUP_HANDLER] 'PK': pk,")
                        'PK': pk,
print("[CLEANUP_HANDLER] 'SK': sk")
                        'SK': sk
print("[CLEANUP_HANDLER] }")
                    }
print("[CLEANUP_HANDLER] )")
                )
print("[CLEANUP_HANDLER] print("[CLEANUP_HANDLER] Delete operation completed")")
                print("[CLEANUP_HANDLER] Delete operation completed")

print("[CLEANUP_HANDLER] print("[CLEANUP_HANDLER] Incrementing cleaned_count")")
                print("[CLEANUP_HANDLER] Incrementing cleaned_count")
print("[CLEANUP_HANDLER] cleaned_count += 1")
                cleaned_count += 1
print("[CLEANUP_HANDLER] print(f"[CLEANUP_HANDLER] cleaned_count: {cleaned_count}")")
                print(f"[CLEANUP_HANDLER] cleaned_count: {cleaned_count}")

print("[CLEANUP_HANDLER] print("[CLEANUP_HANDLER] Logging deleted session info")")
                print("[CLEANUP_HANDLER] Logging deleted session info")
print("[CLEANUP_HANDLER] logger.info("Deleted stale session", session_id=session_id)")
                logger.info("Deleted stale session", session_id=session_id)
print("[CLEANUP_HANDLER] print("[CLEANUP_HANDLER] Session deletion logged")")
                print("[CLEANUP_HANDLER] Session deletion logged")

print("[CLEANUP_HANDLER] except Exception as e:")
            except Exception as e:
print("[CLEANUP_HANDLER] print("[CLEANUP_HANDLER] !!! EXCEPTION deleting session item !!!")")
                print("[CLEANUP_HANDLER] !!! EXCEPTION deleting session item !!!")
print("[CLEANUP_HANDLER] print(f"[CLEANUP_HANDLER] Exception: {e}")")
                print(f"[CLEANUP_HANDLER] Exception: {e}")

print("[CLEANUP_HANDLER] print("[CLEANUP_HANDLER] Logging session deletion error")")
                print("[CLEANUP_HANDLER] Logging session deletion error")
print("[CLEANUP_HANDLER] logger.error("Failed to delete stale session", session_id=session_id, error=str(")
                logger.error("Failed to delete stale session", session_id=session_id, error=str(e))
print("[CLEANUP_HANDLER] print("[CLEANUP_HANDLER] Session deletion error logged")")
                print("[CLEANUP_HANDLER] Session deletion error logged")

print("[CLEANUP_HANDLER] print("[CLEANUP_HANDLER] Checking if scan response has more items")")
        print("[CLEANUP_HANDLER] Checking if scan response has more items")
print("[CLEANUP_HANDLER] while 'LastEvaluatedKey' in response:")
        while 'LastEvaluatedKey' in response:
print("[CLEANUP_HANDLER] print("[CLEANUP_HANDLER] LastEvaluatedKey found, paginating for more items")")
            print("[CLEANUP_HANDLER] LastEvaluatedKey found, paginating for more items")
print("[CLEANUP_HANDLER] print(f"[CLEANUP_HANDLER] LastEvaluatedKey: {response.get('LastEvaluatedKey')}")")
            print(f"[CLEANUP_HANDLER] LastEvaluatedKey: {response.get('LastEvaluatedKey')}")

print("[CLEANUP_HANDLER] print("[CLEANUP_HANDLER] Building scan parameters for next page")")
            print("[CLEANUP_HANDLER] Building scan parameters for next page")
print("[CLEANUP_HANDLER] scan_params['ExclusiveStartKey'] = response['LastEvaluatedKey']")
            scan_params['ExclusiveStartKey'] = response['LastEvaluatedKey']
print("[CLEANUP_HANDLER] print(f"[CLEANUP_HANDLER] scan_params with pagination: {scan_params}")")
            print(f"[CLEANUP_HANDLER] scan_params with pagination: {scan_params}")

print("[CLEANUP_HANDLER] print("[CLEANUP_HANDLER] Executing table.scan() for next page")")
            print("[CLEANUP_HANDLER] Executing table.scan() for next page")
print("[CLEANUP_HANDLER] response = dynamodb_client.table.scan(**scan_params)")
            response = dynamodb_client.table.scan(**scan_params)
print("[CLEANUP_HANDLER] print(f"[CLEANUP_HANDLER] scan response received for next page: {type(response)}")
            print(f"[CLEANUP_HANDLER] scan response received for next page: {type(response)}")

print("[CLEANUP_HANDLER] print("[CLEANUP_HANDLER] Extracting Items from response")")
            print("[CLEANUP_HANDLER] Extracting Items from response")
print("[CLEANUP_HANDLER] items = response.get('Items', [])")
            items = response.get('Items', [])
print("[CLEANUP_HANDLER] print(f"[CLEANUP_HANDLER] Number of items in this page: {len(items)}")")
            print(f"[CLEANUP_HANDLER] Number of items in this page: {len(items)}")

print("[CLEANUP_HANDLER] print("[CLEANUP_HANDLER] Iterating through items in this page")")
            print("[CLEANUP_HANDLER] Iterating through items in this page")
print("[CLEANUP_HANDLER] for idx, item in enumerate(items):")
            for idx, item in enumerate(items):
print("[CLEANUP_HANDLER] print(f"[CLEANUP_HANDLER] --- Processing item {idx + 1}/{len(items)} ---")")
                print(f"[CLEANUP_HANDLER] --- Processing item {idx + 1}/{len(items)} ---")
print("[CLEANUP_HANDLER] print(f"[CLEANUP_HANDLER] item: {item}")")
                print(f"[CLEANUP_HANDLER] item: {item}")

print("[CLEANUP_HANDLER] print("[CLEANUP_HANDLER] Extracting PK from item")")
                print("[CLEANUP_HANDLER] Extracting PK from item")
print("[CLEANUP_HANDLER] pk = item.get('PK')")
                pk = item.get('PK')
print("[CLEANUP_HANDLER] print(f"[CLEANUP_HANDLER] PK: {pk}")")
                print(f"[CLEANUP_HANDLER] PK: {pk}")

print("[CLEANUP_HANDLER] print("[CLEANUP_HANDLER] Extracting SK from item")")
                print("[CLEANUP_HANDLER] Extracting SK from item")
print("[CLEANUP_HANDLER] sk = item.get('SK')")
                sk = item.get('SK')
print("[CLEANUP_HANDLER] print(f"[CLEANUP_HANDLER] SK: {sk}")")
                print(f"[CLEANUP_HANDLER] SK: {sk}")

print("[CLEANUP_HANDLER] print("[CLEANUP_HANDLER] Extracting SessionID from item")")
                print("[CLEANUP_HANDLER] Extracting SessionID from item")
print("[CLEANUP_HANDLER] session_id = item.get('SessionID')")
                session_id = item.get('SessionID')
print("[CLEANUP_HANDLER] print(f"[CLEANUP_HANDLER] SessionID: {session_id}")")
                print(f"[CLEANUP_HANDLER] SessionID: {session_id}")

print("[CLEANUP_HANDLER] try:")
                try:
print("[CLEANUP_HANDLER] print("[CLEANUP_HANDLER] Deleting session item from DynamoDB")")
                    print("[CLEANUP_HANDLER] Deleting session item from DynamoDB")
print("[CLEANUP_HANDLER] print(f"[CLEANUP_HANDLER] Calling table.delete_item() with PK={pk}, SK={sk}")")
                    print(f"[CLEANUP_HANDLER] Calling table.delete_item() with PK={pk}, SK={sk}")
print("[CLEANUP_HANDLER] dynamodb_client.table.delete_item(")
                    dynamodb_client.table.delete_item(
print("[CLEANUP_HANDLER] Key={")
                        Key={
print("[CLEANUP_HANDLER] 'PK': pk,")
                            'PK': pk,
print("[CLEANUP_HANDLER] 'SK': sk")
                            'SK': sk
print("[CLEANUP_HANDLER] }")
                        }
print("[CLEANUP_HANDLER] )")
                    )
print("[CLEANUP_HANDLER] print("[CLEANUP_HANDLER] Delete operation completed")")
                    print("[CLEANUP_HANDLER] Delete operation completed")

print("[CLEANUP_HANDLER] print("[CLEANUP_HANDLER] Incrementing cleaned_count")")
                    print("[CLEANUP_HANDLER] Incrementing cleaned_count")
print("[CLEANUP_HANDLER] cleaned_count += 1")
                    cleaned_count += 1
print("[CLEANUP_HANDLER] print(f"[CLEANUP_HANDLER] cleaned_count: {cleaned_count}")")
                    print(f"[CLEANUP_HANDLER] cleaned_count: {cleaned_count}")

print("[CLEANUP_HANDLER] print("[CLEANUP_HANDLER] Logging deleted session info")")
                    print("[CLEANUP_HANDLER] Logging deleted session info")
print("[CLEANUP_HANDLER] logger.info("Deleted stale session", session_id=session_id)")
                    logger.info("Deleted stale session", session_id=session_id)
print("[CLEANUP_HANDLER] print("[CLEANUP_HANDLER] Session deletion logged")")
                    print("[CLEANUP_HANDLER] Session deletion logged")

print("[CLEANUP_HANDLER] except Exception as e:")
                except Exception as e:
print("[CLEANUP_HANDLER] print("[CLEANUP_HANDLER] !!! EXCEPTION deleting session item !!!")")
                    print("[CLEANUP_HANDLER] !!! EXCEPTION deleting session item !!!")
print("[CLEANUP_HANDLER] print(f"[CLEANUP_HANDLER] Exception: {e}")")
                    print(f"[CLEANUP_HANDLER] Exception: {e}")

print("[CLEANUP_HANDLER] print("[CLEANUP_HANDLER] Logging session deletion error")")
                    print("[CLEANUP_HANDLER] Logging session deletion error")
print("[CLEANUP_HANDLER] logger.error("Failed to delete stale session", session_id=session_id, error=str(")
                    logger.error("Failed to delete stale session", session_id=session_id, error=str(e))
print("[CLEANUP_HANDLER] print("[CLEANUP_HANDLER] Session deletion error logged")")
                    print("[CLEANUP_HANDLER] Session deletion error logged")

print("[CLEANUP_HANDLER] print("[CLEANUP_HANDLER] Building result dictionary")")
        print("[CLEANUP_HANDLER] Building result dictionary")
print("[CLEANUP_HANDLER] result = {")
        result = {
print("[CLEANUP_HANDLER] 'task_name': 'cleanup_stale_sessions',")
            'task_name': 'cleanup_stale_sessions',
print("[CLEANUP_HANDLER] 'items_cleaned': cleaned_count,")
            'items_cleaned': cleaned_count,
print("[CLEANUP_HANDLER] 'status': 'completed'")
            'status': 'completed'
print("[CLEANUP_HANDLER] }")
        }
print("[CLEANUP_HANDLER] print(f"[CLEANUP_HANDLER] result: {result}")")
        print(f"[CLEANUP_HANDLER] result: {result}")

print("[CLEANUP_HANDLER] print("[CLEANUP_HANDLER] Logging task completion")")
        print("[CLEANUP_HANDLER] Logging task completion")
print("[CLEANUP_HANDLER] logger.info("Stale sessions cleanup completed", items_cleaned=cleaned_count)")
        logger.info("Stale sessions cleanup completed", items_cleaned=cleaned_count)
print("[CLEANUP_HANDLER] print("[CLEANUP_HANDLER] Task completion logged")")
        print("[CLEANUP_HANDLER] Task completion logged")

print("[CLEANUP_HANDLER] print("[CLEANUP_HANDLER] ========================================")")
        print("[CLEANUP_HANDLER] ========================================")
print("[CLEANUP_HANDLER] print("[CLEANUP_HANDLER] cleanup_stale_sessions() completed successfully")")
        print("[CLEANUP_HANDLER] cleanup_stale_sessions() completed successfully")
print("[CLEANUP_HANDLER] print("[CLEANUP_HANDLER] ========================================")")
        print("[CLEANUP_HANDLER] ========================================")
print("[CLEANUP_HANDLER] return result")
        return result

print("[CLEANUP_HANDLER] except Exception as e:")
    except Exception as e:
print("[CLEANUP_HANDLER] print("[CLEANUP_HANDLER] !!! EXCEPTION in cleanup_stale_sessions !!!")")
        print("[CLEANUP_HANDLER] !!! EXCEPTION in cleanup_stale_sessions !!!")
print("[CLEANUP_HANDLER] print(f"[CLEANUP_HANDLER] Exception type: {type(e)}")")
        print(f"[CLEANUP_HANDLER] Exception type: {type(e)}")
print("[CLEANUP_HANDLER] print(f"[CLEANUP_HANDLER] Exception message: {str(e)}")")
        print(f"[CLEANUP_HANDLER] Exception message: {str(e)}")

print("[CLEANUP_HANDLER] print("[CLEANUP_HANDLER] Logging cleanup error")")
        print("[CLEANUP_HANDLER] Logging cleanup error")
print("[CLEANUP_HANDLER] logger.error("Stale sessions cleanup failed", error=str(e))")
        logger.error("Stale sessions cleanup failed", error=str(e))
print("[CLEANUP_HANDLER] print("[CLEANUP_HANDLER] Error logged")")
        print("[CLEANUP_HANDLER] Error logged")

print("[CLEANUP_HANDLER] print("[CLEANUP_HANDLER] Building error result")")
        print("[CLEANUP_HANDLER] Building error result")
print("[CLEANUP_HANDLER] result = {")
        result = {
print("[CLEANUP_HANDLER] 'task_name': 'cleanup_stale_sessions',")
            'task_name': 'cleanup_stale_sessions',
print("[CLEANUP_HANDLER] 'status': 'failed',")
            'status': 'failed',
print("[CLEANUP_HANDLER] 'error': str(e)")
            'error': str(e)
print("[CLEANUP_HANDLER] }")
        }
print("[CLEANUP_HANDLER] print(f"[CLEANUP_HANDLER] result: {result}")")
        print(f"[CLEANUP_HANDLER] result: {result}")

print("[CLEANUP_HANDLER] print("[CLEANUP_HANDLER] cleanup_stale_sessions() returning error result")")
        print("[CLEANUP_HANDLER] cleanup_stale_sessions() returning error result")
print("[CLEANUP_HANDLER] return result")
        return result
print("[CLEANUP_HANDLER] Module load complete")
