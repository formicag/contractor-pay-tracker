#!/usr/bin/env python3
"""
Reprocess All Pay Files

Downloads all files from S3 and updates DynamoDB with extracted contractor names
"""

import sys
import os
import boto3
from datetime import datetime

# Add flask-app to path to import excel_processor
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../flask-app'))

from excel_processor import extract_contractor_names, get_contractor_summary

# AWS Configuration
AWS_REGION = 'eu-west-1'
TABLE_NAME = 'contractor-pay-files-metadata'
S3_BUCKET = 'contractor-pay-files-development-016164185850'

# Initialize AWS clients
dynamodb = boto3.resource('dynamodb', region_name=AWS_REGION)
table = dynamodb.Table(TABLE_NAME)
s3_client = boto3.client('s3', region_name=AWS_REGION)

def reprocess_file(file_item):
    """
    Reprocess a single file to extract contractor names

    Args:
        file_item: DynamoDB item dict with file metadata

    Returns:
        Dict with status and message
    """
    file_id = file_item.get('file_id')
    filename = file_item.get('filename')
    s3_key = file_item.get('s3_key')
    s3_bucket = file_item.get('s3_bucket', S3_BUCKET)

    print(f"  Processing: {filename}")

    try:
        # Download file from S3
        response = s3_client.get_object(Bucket=s3_bucket, Key=s3_key)
        file_content = response['Body'].read()

        # Extract contractor names
        contractor_names = extract_contractor_names(file_content)
        contractor_name = get_contractor_summary(contractor_names)

        if not contractor_names:
            print(f"    ⚠️  No contractors found in {filename}")
            return {
                'success': False,
                'message': 'No contractors found',
                'contractor_count': 0
            }

        # Update DynamoDB
        table.update_item(
            Key={'file_id': file_id},
            UpdateExpression='SET contractor_name = :name, contractor_names_list = :names_list, contractor_count = :count, processing_status = :status, updated_at = :updated',
            ExpressionAttributeValues={
                ':name': contractor_name,
                ':names_list': contractor_names,
                ':count': len(contractor_names),
                ':status': 'completed',
                ':updated': int(datetime.now().timestamp())
            }
        )

        print(f"    ✅ Updated: {len(contractor_names)} contractors - {contractor_name}")

        return {
            'success': True,
            'message': f'Extracted {len(contractor_names)} contractors',
            'contractor_count': len(contractor_names),
            'contractor_names': contractor_names
        }

    except Exception as e:
        print(f"    ❌ Error: {str(e)}")
        return {
            'success': False,
            'message': str(e),
            'contractor_count': 0
        }


def main():
    """Main reprocessing function"""
    print("=" * 80)
    print("REPROCESSING ALL PAY FILES")
    print("=" * 80)
    print()

    # Get all files from DynamoDB (excluding umbrella company data)
    print("Fetching files from DynamoDB...")
    response = table.scan()
    items = response.get('Items', [])

    # Handle pagination
    while 'LastEvaluatedKey' in response:
        response = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
        items.extend(response.get('Items', []))

    # Filter out umbrella company reference data
    pay_files = [item for item in items if not item.get('file_id', '').startswith('UMBRELLA#')]

    print(f"Found {len(pay_files)} pay files to process")
    print()

    # Reprocess each file
    results = {
        'success': 0,
        'failed': 0,
        'total': len(pay_files)
    }

    for idx, file_item in enumerate(pay_files, 1):
        print(f"[{idx}/{len(pay_files)}]", end=" ")

        result = reprocess_file(file_item)

        if result['success']:
            results['success'] += 1
        else:
            results['failed'] += 1

    print()
    print("=" * 80)
    print("REPROCESSING COMPLETE")
    print("=" * 80)
    print()
    print(f"Total files:      {results['total']}")
    print(f"✅ Successful:    {results['success']}")
    print(f"❌ Failed:        {results['failed']}")
    print()


if __name__ == '__main__':
    main()
