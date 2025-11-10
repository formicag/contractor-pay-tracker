#!/usr/bin/env python3
"""
Flush Contractors Script

Deletes all existing contractor records from DynamoDB.
WARNING: This only deletes contractors, not files or pay records.
"""

import boto3
import sys
from decimal import Decimal

# Configuration
AWS_PROFILE = "AdministratorAccess-016164185850"
AWS_REGION = "eu-west-2"
TABLE_NAME = "contractor-pay-development"

# Initialize clients
session = boto3.Session(profile_name=AWS_PROFILE, region_name=AWS_REGION)
dynamodb = session.resource('dynamodb')
table = dynamodb.Table(TABLE_NAME)

def flush_contractors():
    """Delete all contractor records from DynamoDB."""

    print(f"\n{'='*80}")
    print(f"🗑️  FLUSHING CONTRACTOR DATA")
    print(f"{'='*80}\n")

    # Scan for all Contractor entities
    print("📊 Scanning for contractor records...")

    response = table.scan(
        FilterExpression="EntityType = :et",
        ExpressionAttributeValues={
            ":et": "Contractor"
        }
    )

    items = response.get('Items', [])
    total_items = len(items)

    # Handle pagination
    while 'LastEvaluatedKey' in response:
        response = table.scan(
            FilterExpression="EntityType = :et",
            ExpressionAttributeValues={
                ":et": "Contractor"
            },
            ExclusiveStartKey=response['LastEvaluatedKey']
        )
        items.extend(response.get('Items', []))
        total_items = len(items)

    print(f"Found {total_items} contractor records to delete\n")

    if total_items == 0:
        print("✅ No contractor records found. Database already clean.\n")
        return 0

    # Delete items
    deleted_count = 0
    error_count = 0

    for item in items:
        try:
            pk = item['PK']
            sk = item['SK']

            table.delete_item(Key={'PK': pk, 'SK': sk})

            deleted_count += 1

            # Show progress
            if deleted_count % 10 == 0:
                print(f"🗑️  Deleted {deleted_count}/{total_items} records...")

        except Exception as e:
            error_count += 1
            print(f"❌ Error deleting {item.get('PK', 'Unknown')}: {str(e)}")

    print(f"\n{'='*80}")
    print(f"✅ FLUSH COMPLETE!")
    print(f"{'='*80}")
    print(f"Deleted: {deleted_count}")
    print(f"Errors: {error_count}")
    print(f"{'='*80}\n")

    return deleted_count

if __name__ == "__main__":
    print("\n⚠️  WARNING: This will delete ALL contractor records!")
    print("Files and pay records will NOT be affected.\n")

    confirmation = input("Type 'FLUSH' to continue (or Ctrl+C to cancel): ")

    if confirmation != "FLUSH":
        print("❌ Cancelled. No changes made.")
        sys.exit(1)

    deleted = flush_contractors()

    print("💡 Next: Run import_team_snapshot.py to load clean data")
    print("   python3 scripts/import_team_snapshot.py\n")
