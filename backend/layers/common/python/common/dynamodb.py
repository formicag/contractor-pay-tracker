"""
DynamoDB access layer for contractor pay tracking
Provides convenient methods for common data access patterns
"""

import os
from decimal import Decimal

import boto3
from boto3.dynamodb.conditions import Key, Attr


class DynamoDBClient:
    """DynamoDB client for contractor pay tracking"""

    def __init__(self):
        self.table_name = os.environ.get('TABLE_NAME')
        if not self.table_name:
            raise ValueError("TABLE_NAME environment variable not set")

        dynamodb = boto3.resource('dynamodb')
        self.table = dynamodb.Table(self.table_name)

    def get_contractor_by_name(self, first_name, last_name):
        """Get contractor by name (for fuzzy matching)"""
        normalized_name = f"{first_name} {last_name}".lower()

        response = self.table.query(
            IndexName='GSI2',
            KeyConditionExpression='GSI2PK = :pk',
            ExpressionAttributeValues={
                ':pk': f'NAME#{normalized_name}'
            }
        )

        return response.get('Items', [])

    def get_contractor_umbrella_associations(self, contractor_id):
        """Get all umbrella associations for a contractor"""
        response = self.table.query(
            KeyConditionExpression='PK = :pk AND begins_with(SK, :sk)',
            ExpressionAttributeValues={
                ':pk': f'CONTRACTOR#{contractor_id}',
                ':sk': 'UMBRELLA#'
            }
        )

        return response.get('Items', [])

    def check_permanent_staff(self, first_name, last_name):
        """Check if person is permanent staff (should NOT be in contractor files)"""
        normalized_name = f"{first_name} {last_name}".lower()

        try:
            response = self.table.get_item(
                Key={
                    'PK': f'PERMANENT#{normalized_name}',
                    'SK': 'PROFILE'
                }
            )
            return 'Item' in response
        except:
            return False

    def get_system_parameter(self, param_key):
        """Get system configuration parameter"""
        response = self.table.get_item(
            Key={
                'PK': f'PARAM#{param_key}',
                'SK': 'VALUE'
            }
        )

        if 'Item' in response:
            return response['Item']['ParamValue']
        return None

    def create_file_metadata(self, file_data):
        """Create pay file metadata record"""
        self.table.put_item(Item=file_data)

    def get_file_metadata(self, file_id):
        """Get pay file metadata"""
        response = self.table.get_item(
            Key={
                'PK': f'FILE#{file_id}',
                'SK': 'METADATA'
            }
        )
        return response.get('Item')

    def update_file_status(self, file_id, status, **kwargs):
        """Update file processing status"""
        update_expr = 'SET #status = :status'
        expr_values = {':status': status}
        expr_names = {'#status': 'Status'}

        for key, value in kwargs.items():
            update_expr += f', {key} = :{key}'
            expr_values[f':{key}'] = value

        self.table.update_item(
            Key={'PK': f'FILE#{file_id}', 'SK': 'METADATA'},
            UpdateExpression=update_expr,
            ExpressionAttributeNames=expr_names,
            ExpressionAttributeValues=expr_values
        )

    def batch_write_pay_records(self, records):
        """Batch write pay records"""
        with self.table.batch_writer() as batch:
            for record in records:
                batch.put_item(Item=record)
