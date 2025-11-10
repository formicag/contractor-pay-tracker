#!/usr/bin/env python3
"""
DynamoDB Cleanup Script
Finds and deletes:
1. Duplicate file records (keeps most recent COMPLETED)
2. Old FAILED records
3. Stale data (SUPERSEDED, old UPLOADED, etc.)

Only keeps the most recent COMPLETED version of each file for each umbrella+period combination.
"""

import boto3
import sys
from datetime import datetime
from collections import defaultdict
from typing import Dict, List, Set
from decimal import Decimal

# Configuration
REGION = 'eu-west-2'
TABLE_NAME = 'contractor-pay-development'

# Initialize clients
dynamodb = boto3.resource('dynamodb', region_name=REGION)
table = dynamodb.Table(TABLE_NAME)


def scan_all_file_records() -> List[Dict]:
    """Scan and retrieve all FILE metadata records"""
    print("\n" + "="*80)
    print("SCANNING ALL FILE RECORDS")
    print("="*80)

    items = []
    scan_kwargs = {
        'FilterExpression': 'begins_with(PK, :pk_prefix) AND SK = :sk',
        'ExpressionAttributeValues': {
            ':pk_prefix': 'FILE#',
            ':sk': 'METADATA'
        }
    }

    while True:
        response = table.scan(**scan_kwargs)
        items.extend(response.get('Items', []))

        if 'LastEvaluatedKey' not in response:
            break
        scan_kwargs['ExclusiveStartKey'] = response['LastEvaluatedKey']

    print(f"Found {len(items)} file metadata records")
    return items


def scan_all_pay_records() -> List[Dict]:
    """Scan and retrieve all PAY records"""
    print("\n" + "="*80)
    print("SCANNING ALL PAY RECORDS")
    print("="*80)

    items = []
    scan_kwargs = {
        'FilterExpression': 'begins_with(PK, :pk_prefix) AND begins_with(SK, :sk_prefix)',
        'ExpressionAttributeValues': {
            ':pk_prefix': 'FILE#',
            ':sk_prefix': 'RECORD#'
        }
    }

    while True:
        response = table.scan(**scan_kwargs)
        items.extend(response.get('Items', []))

        if 'LastEvaluatedKey' not in response:
            break
        scan_kwargs['ExclusiveStartKey'] = response['LastEvaluatedKey']

    print(f"Found {len(items)} pay records")
    return items


def analyze_files(file_records: List[Dict]) -> Dict:
    """
    Analyze file records and categorize them
    Returns dict with:
    - duplicates: files with same umbrella+period (keep most recent COMPLETED)
    - failed: FAILED status files
    - superseded: SUPERSEDED status files
    - old_uploaded: UPLOADED status files older than most recent
    - to_keep: files that should be kept
    """
    print("\n" + "="*80)
    print("ANALYZING FILES")
    print("="*80)

    # Group files by umbrella+period
    groups = defaultdict(list)

    for file_record in file_records:
        file_id = file_record.get('FileID')
        status = file_record.get('Status', 'UNKNOWN')
        umbrella_code = file_record.get('UmbrellaCode', 'UNKNOWN')
        period_id = file_record.get('PeriodID', 'UNKNOWN')
        uploaded_at = file_record.get('UploadedAt', '')

        # Create grouping key
        group_key = f"{umbrella_code}#{period_id}"

        groups[group_key].append({
            'file_id': file_id,
            'status': status,
            'uploaded_at': uploaded_at,
            'umbrella_code': umbrella_code,
            'period_id': period_id,
            'record': file_record
        })

    # Analyze each group
    result = {
        'duplicates_to_delete': [],
        'failed_to_delete': [],
        'superseded_to_delete': [],
        'old_uploaded_to_delete': [],
        'error_to_delete': [],
        'to_keep': [],
        'stats': {
            'total_files': len(file_records),
            'groups': len(groups)
        }
    }

    print(f"\nFound {len(groups)} unique umbrella+period combinations")
    print(f"Total files: {len(file_records)}")

    for group_key, files in groups.items():
        print(f"\n  Group: {group_key} - {len(files)} file(s)")

        # Sort by upload time (most recent first)
        files.sort(key=lambda x: x['uploaded_at'], reverse=True)

        # Find the most recent COMPLETED file
        most_recent_completed = None
        for f in files:
            if f['status'] in ['COMPLETED', 'COMPLETED_WITH_WARNINGS']:
                most_recent_completed = f
                print(f"    ✓ Keep: {f['file_id'][:8]}... - {f['status']} - {f['uploaded_at']}")
                result['to_keep'].append(f)
                break

        # Process remaining files
        for f in files:
            if most_recent_completed and f['file_id'] == most_recent_completed['file_id']:
                continue  # Already marked to keep

            file_id = f['file_id']
            status = f['status']

            if status == 'FAILED':
                print(f"    ✗ Delete (FAILED): {file_id[:8]}... - {f['uploaded_at']}")
                result['failed_to_delete'].append(f)

            elif status == 'ERROR':
                print(f"    ✗ Delete (ERROR): {file_id[:8]}... - {f['uploaded_at']}")
                result['error_to_delete'].append(f)

            elif status == 'SUPERSEDED':
                print(f"    ✗ Delete (SUPERSEDED): {file_id[:8]}... - {f['uploaded_at']}")
                result['superseded_to_delete'].append(f)

            elif status == 'UPLOADED':
                print(f"    ✗ Delete (old UPLOADED): {file_id[:8]}... - {f['uploaded_at']}")
                result['old_uploaded_to_delete'].append(f)

            elif status in ['COMPLETED', 'COMPLETED_WITH_WARNINGS']:
                # Duplicate completed file - older than the one we're keeping
                print(f"    ✗ Delete (duplicate COMPLETED): {file_id[:8]}... - {f['uploaded_at']}")
                result['duplicates_to_delete'].append(f)

            elif status == 'PROCESSING':
                # Old stuck processing records
                print(f"    ✗ Delete (stuck PROCESSING): {file_id[:8]}... - {f['uploaded_at']}")
                result['old_uploaded_to_delete'].append(f)

            else:
                print(f"    ? Unknown status: {file_id[:8]}... - {status} - {f['uploaded_at']}")
                result['old_uploaded_to_delete'].append(f)

    return result


def get_pay_records_for_file(file_id: str) -> List[Dict]:
    """Get all pay records for a specific file"""
    response = table.query(
        KeyConditionExpression='PK = :pk AND begins_with(SK, :sk)',
        ExpressionAttributeValues={
            ':pk': f'FILE#{file_id}',
            ':sk': 'RECORD#'
        }
    )
    return response.get('Items', [])


def delete_file_and_records(file_id: str, dry_run: bool = True) -> int:
    """Delete a file metadata record and all its pay records"""
    records_deleted = 0

    # Get all pay records for this file
    pay_records = get_pay_records_for_file(file_id)

    if dry_run:
        print(f"    [DRY RUN] Would delete file {file_id[:8]}... and {len(pay_records)} pay records")
        return len(pay_records) + 1

    # Delete pay records in batches
    if pay_records:
        with table.batch_writer() as batch:
            for record in pay_records:
                batch.delete_item(
                    Key={
                        'PK': record['PK'],
                        'SK': record['SK']
                    }
                )
                records_deleted += 1

    # Delete file metadata
    table.delete_item(
        Key={
            'PK': f'FILE#{file_id}',
            'SK': 'METADATA'
        }
    )
    records_deleted += 1

    print(f"    ✓ Deleted file {file_id[:8]}... and {len(pay_records)} pay records")

    return records_deleted


def perform_cleanup(analysis: Dict, dry_run: bool = True) -> Dict:
    """Perform the cleanup based on analysis"""
    print("\n" + "="*80)
    if dry_run:
        print("DRY RUN - NO ACTUAL DELETIONS")
    else:
        print("PERFORMING CLEANUP - DELETING RECORDS")
    print("="*80)

    stats = {
        'duplicates_deleted': 0,
        'failed_deleted': 0,
        'superseded_deleted': 0,
        'error_deleted': 0,
        'old_uploaded_deleted': 0,
        'total_records_deleted': 0,
        'files_kept': len(analysis['to_keep'])
    }

    # Delete duplicates
    print(f"\n--- Deleting {len(analysis['duplicates_to_delete'])} duplicate COMPLETED files ---")
    for f in analysis['duplicates_to_delete']:
        records_deleted = delete_file_and_records(f['file_id'], dry_run)
        stats['duplicates_deleted'] += 1
        stats['total_records_deleted'] += records_deleted

    # Delete FAILED files
    print(f"\n--- Deleting {len(analysis['failed_to_delete'])} FAILED files ---")
    for f in analysis['failed_to_delete']:
        records_deleted = delete_file_and_records(f['file_id'], dry_run)
        stats['failed_deleted'] += 1
        stats['total_records_deleted'] += records_deleted

    # Delete ERROR files
    print(f"\n--- Deleting {len(analysis['error_to_delete'])} ERROR files ---")
    for f in analysis['error_to_delete']:
        records_deleted = delete_file_and_records(f['file_id'], dry_run)
        stats['error_deleted'] += 1
        stats['total_records_deleted'] += records_deleted

    # Delete SUPERSEDED files
    print(f"\n--- Deleting {len(analysis['superseded_to_delete'])} SUPERSEDED files ---")
    for f in analysis['superseded_to_delete']:
        records_deleted = delete_file_and_records(f['file_id'], dry_run)
        stats['superseded_deleted'] += 1
        stats['total_records_deleted'] += records_deleted

    # Delete old UPLOADED/PROCESSING files
    print(f"\n--- Deleting {len(analysis['old_uploaded_to_delete'])} old UPLOADED/PROCESSING files ---")
    for f in analysis['old_uploaded_to_delete']:
        records_deleted = delete_file_and_records(f['file_id'], dry_run)
        stats['old_uploaded_deleted'] += 1
        stats['total_records_deleted'] += records_deleted

    return stats


def print_summary(analysis: Dict, stats: Dict, dry_run: bool):
    """Print cleanup summary"""
    print("\n" + "="*80)
    print("CLEANUP SUMMARY")
    print("="*80)

    if dry_run:
        print("\n⚠️  DRY RUN MODE - No actual deletions were made\n")
    else:
        print("\n✓ CLEANUP COMPLETED\n")

    print(f"Total files analyzed:           {analysis['stats']['total_files']}")
    print(f"Umbrella+Period groups:         {analysis['stats']['groups']}")
    print(f"Files to keep (most recent):    {stats['files_kept']}")
    print()
    print("Files to delete:")
    print(f"  - Duplicate COMPLETED:        {stats['duplicates_deleted']}")
    print(f"  - FAILED status:              {stats['failed_deleted']}")
    print(f"  - ERROR status:               {stats['error_deleted']}")
    print(f"  - SUPERSEDED status:          {stats['superseded_deleted']}")
    print(f"  - Old UPLOADED/PROCESSING:    {stats['old_uploaded_deleted']}")
    print()
    print(f"Total files to delete:          {stats['duplicates_deleted'] + stats['failed_deleted'] + stats['error_deleted'] + stats['superseded_deleted'] + stats['old_uploaded_deleted']}")
    print(f"Total records to delete:        {stats['total_records_deleted']}")

    if dry_run:
        print("\n" + "="*80)
        print("To perform actual cleanup, run with --execute flag:")
        print("python cleanup_dynamodb.py --execute")
        print("="*80)


def main():
    """Main execution"""
    import argparse

    parser = argparse.ArgumentParser(description='Cleanup DynamoDB duplicate and stale records')
    parser.add_argument('--execute', action='store_true',
                       help='Actually perform deletions (default is dry run)')
    args = parser.parse_args()

    dry_run = not args.execute

    print("\n" + "="*80)
    print("DynamoDB CLEANUP UTILITY")
    print("="*80)
    print(f"Region:     {REGION}")
    print(f"Table:      {TABLE_NAME}")
    print(f"Mode:       {'DRY RUN' if dry_run else 'EXECUTE'}")
    print("="*80)

    try:
        # Step 1: Scan all file records
        file_records = scan_all_file_records()

        if not file_records:
            print("\n✓ No file records found. Database is clean.")
            return

        # Step 2: Analyze files
        analysis = analyze_files(file_records)

        # Step 3: Perform cleanup
        stats = perform_cleanup(analysis, dry_run)

        # Step 4: Print summary
        print_summary(analysis, stats, dry_run)

        # Return number of duplicates deleted
        if not dry_run:
            print(f"\n✓ Cleanup complete. Deleted {stats['duplicates_deleted']} duplicate files.")

    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
