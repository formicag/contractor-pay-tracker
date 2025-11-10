#!/usr/bin/env python3
"""
Test script to verify validation snapshot functionality
Queries DynamoDB for validation snapshots and displays results
"""

import boto3
import json
from decimal import Decimal
from datetime import datetime


class DecimalEncoder(json.JSONEncoder):
    """JSON encoder that handles Decimal types"""
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super(DecimalEncoder, self).default(obj)


def query_validation_snapshots():
    """Query all validation snapshots from DynamoDB"""
    dynamodb = boto3.resource('dynamodb', region_name='eu-west-2')
    table = dynamodb.Table('contractor-pay-development')

    print("=" * 80)
    print("QUERYING VALIDATION SNAPSHOTS")
    print("=" * 80)

    # Query all validation snapshots using GSI1
    response = table.query(
        IndexName='GSI1',
        KeyConditionExpression='GSI1PK = :pk',
        ExpressionAttributeValues={
            ':pk': 'VALIDATIONS'
        },
        ScanIndexForward=False,  # Most recent first
        Limit=10
    )

    snapshots = response.get('Items', [])
    print(f"\nFound {len(snapshots)} validation snapshot(s)\n")

    for idx, snapshot in enumerate(snapshots, 1):
        print(f"\n{'=' * 80}")
        print(f"SNAPSHOT #{idx}")
        print(f"{'=' * 80}")
        print(f"File ID: {snapshot.get('FileID')}")
        print(f"File Name: {snapshot.get('FileName')}")
        print(f"Validated At: {snapshot.get('ValidatedAt')}")
        print(f"Status: {snapshot.get('Status')}")
        print(f"Umbrella ID: {snapshot.get('UmbrellaID')}")
        print(f"Period ID: {snapshot.get('PeriodID')}")
        print(f"\nSUMMARY:")
        print(f"  Total Records: {snapshot.get('TotalRecords')}")
        print(f"  Valid Records: {snapshot.get('ValidRecords')}")
        print(f"  Total Rules: {snapshot.get('TotalRules')}")
        print(f"  Passed Rules: {snapshot.get('PassedRules')}")
        print(f"  Failed Rules: {snapshot.get('FailedRules')}")
        print(f"  Error Count: {snapshot.get('ErrorCount')}")
        print(f"  Warning Count: {snapshot.get('WarningCount')}")

        validation_results = snapshot.get('ValidationResults', {})
        if validation_results:
            print(f"\nVALIDATION RESULTS ({len(validation_results)} rule types):")
            for rule_type, rule_data in validation_results.items():
                passed = rule_data.get('passed', False)
                severity = rule_data.get('severity', 'UNKNOWN')
                messages = rule_data.get('messages', [])
                affected = rule_data.get('affected_records', [])

                status_icon = "✓" if passed else "✗"
                print(f"\n  {status_icon} {rule_type} [{severity}]")
                print(f"     Messages: {len(messages)}")
                for msg in messages[:3]:  # Show first 3 messages
                    print(f"       - {msg[:100]}...")
                print(f"     Affected Records: {len(affected)}")

        print(f"\n{'=' * 80}")

    return snapshots


def query_snapshots_for_file(file_id):
    """Query validation snapshots for a specific file"""
    dynamodb = boto3.resource('dynamodb', region_name='eu-west-2')
    table = dynamodb.Table('contractor-pay-development')

    print("\n" + "=" * 80)
    print(f"QUERYING SNAPSHOTS FOR FILE: {file_id}")
    print("=" * 80)

    response = table.query(
        KeyConditionExpression='PK = :pk AND begins_with(SK, :sk)',
        ExpressionAttributeValues={
            ':pk': f'FILE#{file_id}',
            ':sk': 'VALIDATION#'
        },
        ScanIndexForward=False
    )

    snapshots = response.get('Items', [])
    print(f"\nFound {len(snapshots)} snapshot(s) for this file\n")

    for idx, snapshot in enumerate(snapshots, 1):
        print(f"\nSnapshot {idx}:")
        print(f"  Validated At: {snapshot.get('ValidatedAt')}")
        print(f"  Status: {snapshot.get('Status')}")
        print(f"  Total Records: {snapshot.get('TotalRecords')}")
        print(f"  Valid Records: {snapshot.get('ValidRecords')}")
        print(f"  Errors: {snapshot.get('ErrorCount')}")
        print(f"  Warnings: {snapshot.get('WarningCount')}")

    return snapshots


def get_latest_files():
    """Get the latest files to test with"""
    dynamodb = boto3.resource('dynamodb', region_name='eu-west-2')
    table = dynamodb.Table('contractor-pay-development')

    print("\n" + "=" * 80)
    print("FINDING LATEST FILES")
    print("=" * 80)

    # Query files using GSI1
    response = table.query(
        IndexName='GSI1',
        KeyConditionExpression='GSI1PK = :pk',
        ExpressionAttributeValues={
            ':pk': 'FILES'
        },
        ScanIndexForward=False,
        Limit=5
    )

    files = response.get('Items', [])
    print(f"\nFound {len(files)} recent file(s)\n")

    for idx, file in enumerate(files, 1):
        file_id = file.get('FileID')
        file_name = file.get('FileName')
        status = file.get('Status')
        uploaded_at = file.get('UploadedAt')

        print(f"{idx}. {file_name}")
        print(f"   ID: {file_id}")
        print(f"   Status: {status}")
        print(f"   Uploaded: {uploaded_at}")

    return files


if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("VALIDATION SNAPSHOT VERIFICATION SCRIPT")
    print("=" * 80)

    # Query all validation snapshots
    snapshots = query_validation_snapshots()

    # Get latest files
    files = get_latest_files()

    # If we have files, query their validation snapshots
    if files and len(files) > 0:
        print("\n" + "=" * 80)
        print("TESTING FILE-SPECIFIC QUERIES")
        print("=" * 80)

        # Test with first file
        first_file = files[0]
        file_id = first_file.get('FileID')
        query_snapshots_for_file(file_id)

    print("\n" + "=" * 80)
    print("VERIFICATION COMPLETE")
    print("=" * 80)

    # Summary
    print("\n✓ VALIDATION SNAPSHOT SYSTEM STATUS:")
    print(f"  - Total snapshots found: {len(snapshots)}")
    print(f"  - Recent files with potential snapshots: {len(files)}")

    if len(snapshots) > 0:
        print("\n✓ SUCCESS: Validation snapshots are being created and stored!")
        print("  The validation results storage system is working correctly.")
    else:
        print("\n⚠ NOTE: No validation snapshots found yet.")
        print("  Upload a file to trigger validation and create snapshots.")
