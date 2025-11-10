#!/usr/bin/env python3
"""
Add Paul Marsh as active contractor to DynamoDB

Usage:
    python add_paul_marsh.py --table-name contractor-pay-development
"""

import argparse
import uuid
from datetime import datetime
from decimal import Decimal
import boto3


def add_paul_marsh(table_name):
    """Add Paul Marsh to the database"""

    dynamodb = boto3.resource('dynamodb', region_name='eu-west-2')
    table = dynamodb.Table(table_name)

    contractor_id = str(uuid.uuid4())
    normalized_name = "paul marsh"

    print("="*80)
    print("ADDING PAUL MARSH TO DATABASE")
    print("="*80)
    print()

    item = {
        'PK': f'CONTRACTOR#{contractor_id}',
        'SK': 'PROFILE',
        'EntityType': 'Contractor',
        'ContractorID': contractor_id,
        'FirstName': 'Paul',
        'LastName': 'Marsh',
        'NormalizedName': normalized_name,
        'JobTitle': 'Solution Designer',  # Assumed based on similar contractors
        'IsActive': True,
        'SellRate': Decimal('681.41'),
        'BuyRate': Decimal('542.30'),
        'CreatedAt': datetime.utcnow().isoformat() + 'Z',
        'RatesUpdatedAt': '2025-11-09T00:00:00Z',
        'GSI2PK': f'NAME#{normalized_name}',
        'GSI2SK': f'CONTRACTOR#{contractor_id}'
    }

    print(f"Adding contractor:")
    print(f"  Name: Paul Marsh")
    print(f"  ID: {contractor_id}")
    print(f"  Sell Rate: £681.41")
    print(f"  Buy Rate: £542.30")
    print(f"  Status: Active")
    print()

    table.put_item(Item=item)

    print("✓ Paul Marsh successfully added to database")
    print()

    return contractor_id


def main():
    parser = argparse.ArgumentParser(description='Add Paul Marsh to contractor database')
    parser.add_argument('--table-name', required=True, help='DynamoDB table name')

    args = parser.parse_args()

    contractor_id = add_paul_marsh(args.table_name)
    print(f"Contractor ID: {contractor_id}")


if __name__ == '__main__':
    main()
