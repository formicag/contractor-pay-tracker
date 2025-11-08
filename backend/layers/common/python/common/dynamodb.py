"""
DynamoDB access layer for contractor pay tracking
Provides convenient methods for common data access patterns
"""

print("[DYNAMODB_MODULE] Starting dynamodb.py module load")

import os
from decimal import Decimal

print("[DYNAMODB_MODULE] Imported os and Decimal")

import boto3
from boto3.dynamodb.conditions import Key, Attr

print("[DYNAMODB_MODULE] Imported boto3 and dynamodb conditions")


class DynamoDBClient:
    """DynamoDB client for contractor pay tracking"""

    def __init__(self):
        print("[DYNAMODB_INIT] Starting DynamoDBClient initialization")

        self.table_name = os.environ.get('TABLE_NAME')
        print(f"[DYNAMODB_INIT] Retrieved TABLE_NAME from environment: {self.table_name}")

        if not self.table_name:
            print("[DYNAMODB_INIT] ERROR: TABLE_NAME not set, raising ValueError")
            raise ValueError("TABLE_NAME environment variable not set")

        print(f"[DYNAMODB_INIT] TABLE_NAME is valid: {self.table_name}")

        dynamodb = boto3.resource('dynamodb')
        print(f"[DYNAMODB_INIT] Created boto3 dynamodb resource: {dynamodb}")

        self.table = dynamodb.Table(self.table_name)
        print(f"[DYNAMODB_INIT] Created table reference: {self.table}")
        print("[DYNAMODB_INIT] DynamoDBClient initialization complete")

    def get_contractor_by_name(self, first_name, last_name):
        """Get contractor by name (for fuzzy matching)"""
        print(f"[GET_CONTRACTOR_BY_NAME] Called with first_name={first_name}, last_name={last_name}")

        normalized_name = f"{first_name} {last_name}".lower()
        print(f"[GET_CONTRACTOR_BY_NAME] Normalized name: {normalized_name}")

        pk_value = f'NAME#{normalized_name}'
        print(f"[GET_CONTRACTOR_BY_NAME] Generated PK value: {pk_value}")

        print(f"[GET_CONTRACTOR_BY_NAME] Querying GSI2 with KeyConditionExpression")
        response = self.table.query(
            IndexName='GSI2',
            KeyConditionExpression='GSI2PK = :pk',
            ExpressionAttributeValues={
                ':pk': pk_value
            }
        )
        print(f"[GET_CONTRACTOR_BY_NAME] Query response: {response}")

        items = response.get('Items', [])
        print(f"[GET_CONTRACTOR_BY_NAME] Extracted items from response: {items}")
        print(f"[GET_CONTRACTOR_BY_NAME] Returning {len(items)} items")
        return items

    def get_contractor_umbrella_associations(self, contractor_id):
        """Get all umbrella associations for a contractor"""
        print(f"[GET_CONTRACTOR_UMBRELLA_ASSOC] Called with contractor_id={contractor_id}")

        pk_value = f'CONTRACTOR#{contractor_id}'
        print(f"[GET_CONTRACTOR_UMBRELLA_ASSOC] Generated PK value: {pk_value}")

        sk_prefix = 'UMBRELLA#'
        print(f"[GET_CONTRACTOR_UMBRELLA_ASSOC] Using SK prefix: {sk_prefix}")

        print(f"[GET_CONTRACTOR_UMBRELLA_ASSOC] Querying table with KeyConditionExpression")
        response = self.table.query(
            KeyConditionExpression='PK = :pk AND begins_with(SK, :sk)',
            ExpressionAttributeValues={
                ':pk': pk_value,
                ':sk': sk_prefix
            }
        )
        print(f"[GET_CONTRACTOR_UMBRELLA_ASSOC] Query response: {response}")

        items = response.get('Items', [])
        print(f"[GET_CONTRACTOR_UMBRELLA_ASSOC] Extracted items from response: {items}")
        print(f"[GET_CONTRACTOR_UMBRELLA_ASSOC] Returning {len(items)} items")
        return items

    def check_permanent_staff(self, first_name, last_name):
        """Check if person is permanent staff (should NOT be in contractor files)"""
        print(f"[CHECK_PERMANENT_STAFF] Called with first_name={first_name}, last_name={last_name}")

        normalized_name = f"{first_name} {last_name}".lower()
        print(f"[CHECK_PERMANENT_STAFF] Normalized name: {normalized_name}")

        pk_value = f'PERMANENT#{normalized_name}'
        sk_value = 'PROFILE'
        print(f"[CHECK_PERMANENT_STAFF] Generated key: PK={pk_value}, SK={sk_value}")

        try:
            print(f"[CHECK_PERMANENT_STAFF] Attempting get_item query")
            response = self.table.get_item(
                Key={
                    'PK': pk_value,
                    'SK': sk_value
                }
            )
            print(f"[CHECK_PERMANENT_STAFF] get_item response: {response}")

            is_permanent = 'Item' in response
            print(f"[CHECK_PERMANENT_STAFF] Is permanent staff: {is_permanent}")
            return is_permanent
        except Exception as e:
            print(f"[CHECK_PERMANENT_STAFF] Exception caught: {type(e).__name__}: {str(e)}")
            print(f"[CHECK_PERMANENT_STAFF] Returning False due to exception")
            return False

    def get_system_parameter(self, param_key):
        """Get system configuration parameter"""
        print(f"[GET_SYSTEM_PARAMETER] Called with param_key={param_key}")

        pk_value = f'PARAM#{param_key}'
        sk_value = 'VALUE'
        print(f"[GET_SYSTEM_PARAMETER] Generated key: PK={pk_value}, SK={sk_value}")

        print(f"[GET_SYSTEM_PARAMETER] Attempting get_item query")
        response = self.table.get_item(
            Key={
                'PK': pk_value,
                'SK': sk_value
            }
        )
        print(f"[GET_SYSTEM_PARAMETER] get_item response: {response}")

        if 'Item' in response:
            print(f"[GET_SYSTEM_PARAMETER] Item found in response")
            param_value = response['Item']['ParamValue']
            print(f"[GET_SYSTEM_PARAMETER] Extracted ParamValue: {param_value}")
            print(f"[GET_SYSTEM_PARAMETER] Returning param value")
            return param_value

        print(f"[GET_SYSTEM_PARAMETER] No item found, returning None")
        return None

    def create_file_metadata(self, file_data):
        """Create pay file metadata record"""
        print(f"[CREATE_FILE_METADATA] Called with file_data={file_data}")

        print(f"[CREATE_FILE_METADATA] Calling table.put_item")
        self.table.put_item(Item=file_data)
        print(f"[CREATE_FILE_METADATA] put_item complete")

    def get_file_metadata(self, file_id):
        """Get pay file metadata"""
        print(f"[GET_FILE_METADATA] Called with file_id={file_id}")

        pk_value = f'FILE#{file_id}'
        sk_value = 'METADATA'
        print(f"[GET_FILE_METADATA] Generated key: PK={pk_value}, SK={sk_value}")

        print(f"[GET_FILE_METADATA] Attempting get_item query")
        response = self.table.get_item(
            Key={
                'PK': pk_value,
                'SK': sk_value
            }
        )
        print(f"[GET_FILE_METADATA] get_item response: {response}")

        item = response.get('Item')
        print(f"[GET_FILE_METADATA] Extracted item: {item}")
        print(f"[GET_FILE_METADATA] Returning item")
        return item

    def update_file_status(self, file_id, status, **kwargs):
        """Update file processing status"""
        print(f"[UPDATE_FILE_STATUS] Called with file_id={file_id}, status={status}, kwargs={kwargs}")

        update_expr = 'SET #status = :status'
        print(f"[UPDATE_FILE_STATUS] Initial update expression: {update_expr}")

        expr_values = {':status': status}
        print(f"[UPDATE_FILE_STATUS] Initial expression values: {expr_values}")

        expr_names = {'#status': 'Status'}
        print(f"[UPDATE_FILE_STATUS] Initial expression names: {expr_names}")

        print(f"[UPDATE_FILE_STATUS] Iterating through kwargs to build update expression")
        for key, value in kwargs.items():
            print(f"[UPDATE_FILE_STATUS] Processing kwarg: {key}={value}")
            update_expr += f', {key} = :{key}'
            print(f"[UPDATE_FILE_STATUS] Updated expression: {update_expr}")
            expr_values[f':{key}'] = value
            print(f"[UPDATE_FILE_STATUS] Updated expr_values: {expr_values}")

        pk_value = f'FILE#{file_id}'
        sk_value = 'METADATA'
        print(f"[UPDATE_FILE_STATUS] Generated key: PK={pk_value}, SK={sk_value}")

        print(f"[UPDATE_FILE_STATUS] Final update expression: {update_expr}")
        print(f"[UPDATE_FILE_STATUS] Final expression names: {expr_names}")
        print(f"[UPDATE_FILE_STATUS] Final expression values: {expr_values}")

        print(f"[UPDATE_FILE_STATUS] Calling table.update_item")
        self.table.update_item(
            Key={'PK': pk_value, 'SK': sk_value},
            UpdateExpression=update_expr,
            ExpressionAttributeNames=expr_names,
            ExpressionAttributeValues=expr_values
        )
        print(f"[UPDATE_FILE_STATUS] update_item complete")

    def batch_write_pay_records(self, records):
        """Batch write pay records"""
        print(f"[BATCH_WRITE_PAY_RECORDS] Called with {len(records)} records")
        print(f"[BATCH_WRITE_PAY_RECORDS] Records: {records}")

        print(f"[BATCH_WRITE_PAY_RECORDS] Creating batch_writer context")
        with self.table.batch_writer() as batch:
            print(f"[BATCH_WRITE_PAY_RECORDS] Batch writer created: {batch}")

            print(f"[BATCH_WRITE_PAY_RECORDS] Iterating through records")
            for idx, record in enumerate(records):
                print(f"[BATCH_WRITE_PAY_RECORDS] Processing record {idx+1}/{len(records)}: {record}")
                batch.put_item(Item=record)
                print(f"[BATCH_WRITE_PAY_RECORDS] Record {idx+1} written to batch")

            print(f"[BATCH_WRITE_PAY_RECORDS] All records added to batch")

        print(f"[BATCH_WRITE_PAY_RECORDS] Batch writer context closed, writes committed")
        print(f"[BATCH_WRITE_PAY_RECORDS] batch_write_pay_records complete")

    def get_contractor_pay_records(self, contractor_id, limit=10):
        """
        Get recent pay records for contractor (for rate history lookup)

        Args:
            contractor_id: Contractor UUID
            limit: Maximum number of records to return (default 10, most recent first)

        Returns:
            List of pay records sorted by date descending
        """
        print(f"[GET_CONTRACTOR_PAY_RECORDS] Called with contractor_id={contractor_id}, limit={limit}")

        print("[GET_CONTRACTOR_PAY_RECORDS] About to execute: Query GSI1 for contractor pay records")
        gsi1pk_value = f'CONTRACTOR#{contractor_id}'
        print(f"[GET_CONTRACTOR_PAY_RECORDS] Generated GSI1PK value: {gsi1pk_value}")

        print(f"[GET_CONTRACTOR_PAY_RECORDS] Querying GSI1 with KeyConditionExpression")
        response = self.table.query(
            IndexName='GSI1',
            KeyConditionExpression='GSI1PK = :pk AND begins_with(GSI1SK, :sk_prefix)',
            FilterExpression='IsActive = :is_active AND RecordType = :record_type',
            ExpressionAttributeValues={
                ':pk': gsi1pk_value,
                ':sk_prefix': 'RECORD#',
                ':is_active': True,
                ':record_type': 'STANDARD'
            },
            ScanIndexForward=False,  # Sort descending (most recent first)
            Limit=limit
        )
        print(f"[GET_CONTRACTOR_PAY_RECORDS] Query response: {response}")

        items = response.get('Items', [])
        print(f"[GET_CONTRACTOR_PAY_RECORDS] Extracted {len(items)} items from response")
        print(f"[GET_CONTRACTOR_PAY_RECORDS] Returning items: {items}")
        return items

    def get_contractor_rate_in_period(self, contractor_id, period_id):
        """
        Get contractor's normal (STANDARD) rate for a specific period

        Args:
            contractor_id: Contractor UUID
            period_id: Period number as string

        Returns:
            Decimal day rate if found, None otherwise
        """
        print(f"[GET_CONTRACTOR_RATE_IN_PERIOD] Called with contractor_id={contractor_id}, period_id={period_id}")

        print("[GET_CONTRACTOR_RATE_IN_PERIOD] About to execute: Query GSI2 for contractor rate in period")
        gsi2pk_value = f'PERIOD#{period_id}'
        gsi2sk_value = f'CONTRACTOR#{contractor_id}'
        print(f"[GET_CONTRACTOR_RATE_IN_PERIOD] Generated GSI2PK={gsi2pk_value}, GSI2SK={gsi2sk_value}")

        print(f"[GET_CONTRACTOR_RATE_IN_PERIOD] Querying GSI2 with KeyConditionExpression")
        response = self.table.query(
            IndexName='GSI2',
            KeyConditionExpression='GSI2PK = :pk AND GSI2SK = :sk',
            FilterExpression='IsActive = :is_active AND RecordType = :record_type',
            ExpressionAttributeValues={
                ':pk': gsi2pk_value,
                ':sk': gsi2sk_value,
                ':is_active': True,
                ':record_type': 'STANDARD'
            },
            Limit=1
        )
        print(f"[GET_CONTRACTOR_RATE_IN_PERIOD] Query response: {response}")

        items = response.get('Items', [])
        print(f"[GET_CONTRACTOR_RATE_IN_PERIOD] Extracted {len(items)} items from response")

        if items:
            day_rate = items[0].get('DayRate')
            print(f"[GET_CONTRACTOR_RATE_IN_PERIOD] Found day rate: {day_rate}")
            print(f"[GET_CONTRACTOR_RATE_IN_PERIOD] Returning day_rate: {day_rate}")
            return day_rate

        print(f"[GET_CONTRACTOR_RATE_IN_PERIOD] No rate found, returning None")
        return None

print("[DYNAMODB_MODULE] dynamodb.py module load complete")
