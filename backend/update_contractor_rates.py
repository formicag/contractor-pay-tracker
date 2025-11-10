#!/usr/bin/env python3
"""
Update contractor buy and sell rates in DynamoDB

Usage:
    python update_contractor_rates.py --table-name contractor-pay-development
"""

import argparse
from decimal import Decimal
import boto3
from boto3.dynamodb.conditions import Key


def normalize_name(first, last):
    """Normalize name for matching"""
    return f"{first.lower()} {last.lower()}"


def update_contractor_rates(table_name, dry_run=False):
    """Update contractor rates in DynamoDB"""

    # Contractor rates from the user's spreadsheet
    # Note: Some names corrected to match database (Puttagangaiah, Diogo, Garrety, Donna)
    contractor_rates = [
        ('Duncan', 'Macadam', '700.00', '700.00'),
        ('Basavaraj', 'Puttagangaiah', '700.00', '580.00'),  # Fixed: was Puttagangalai
        ('Bilgun', 'Yildirim', '700.00', '590.00'),
        ('Nik', 'Coultas', '645.00', '535.00'),
        ('David', 'Hunt', '631.77', '472.03'),
        ('Diogo', 'Diogo', '681.41', '557.41'),  # Fixed: was Diego
        ('Graeme', 'Oldroyd', '681.41', '534.96'),
        ('Jonathan', 'Mays', '681.41', '524.48'),
        ('Kevin', 'Kayes', '681.41', '544.96'),
        ('Neil', 'Pomfret', '631.77', '503.49'),
        ('Parag', 'Maniar', '681.41', '573.59'),
        # ('Paul', 'Marsh', '681.41', '542.30'),  # NOT IN DATABASE - skipped
        ('Sheela', 'Adesara', '681.41', '547.51'),
        ('Gary', 'Mandaracas', '699.13', '545.45'),
        ('Barry', 'Breden', '631.77', '438.43'),
        # ('James', 'Halbenny', '325.00', '300.00'),  # NOT IN DATABASE - skipped
        ('Craig', 'Conkerton', '361.00', '300.00'),
        ('Donna', 'Smith', '325.00', '250.00'),  # Fixed: was Dennis
        ('James', 'Matthews', '631.77', '490.00'),
        ('Julie', 'Barton', '480.00', '415.00'),
        ('Matthew', 'Garrety', '631.77', '444.23'),  # Fixed: was Garretty
        ('Richard', 'Williams', '631.77', '450.00'),
        # ('Simon', 'Adler', '500.00', '425.00'),  # NOT IN DATABASE - skipped
        ('Vijetha', 'Dayyala', '325.00', '280.00'),
    ]

    dynamodb = boto3.resource('dynamodb', region_name='eu-west-2')
    table = dynamodb.Table(table_name)

    print("="*80)
    print("UPDATING CONTRACTOR RATES")
    print("="*80)
    if dry_run:
        print("DRY RUN MODE - No changes will be made")
    print()

    updated_count = 0
    not_found_count = 0
    not_found_names = []

    for first_name, last_name, sell_rate, buy_rate in contractor_rates:
        normalized_name = normalize_name(first_name, last_name)

        # Try to find contractor by normalized name using GSI2
        try:
            response = table.query(
                IndexName='GSI2',
                KeyConditionExpression=Key('GSI2PK').eq(f'NAME#{normalized_name}'),
                FilterExpression='EntityType = :et',
                ExpressionAttributeValues={':et': 'Contractor'}
            )

            if response['Items']:
                contractor = response['Items'][0]
                contractor_id = contractor['ContractorID']
                pk = contractor['PK']
                sk = contractor['SK']

                print(f"✓ Found: {first_name} {last_name} (ID: {contractor_id})")
                print(f"  Sell Rate: £{sell_rate} | Buy Rate: £{buy_rate}")

                if not dry_run:
                    # Update the contractor record with rates
                    table.update_item(
                        Key={'PK': pk, 'SK': sk},
                        UpdateExpression='SET SellRate = :sell, BuyRate = :buy, RatesUpdatedAt = :updated',
                        ExpressionAttributeValues={
                            ':sell': Decimal(sell_rate),
                            ':buy': Decimal(buy_rate),
                            ':updated': '2025-11-09T00:00:00Z'
                        }
                    )
                    print(f"  → Updated in database")
                else:
                    print(f"  → Would update (dry run)")

                updated_count += 1
            else:
                print(f"✗ NOT FOUND: {first_name} {last_name} (normalized: {normalized_name})")
                not_found_count += 1
                not_found_names.append(f"{first_name} {last_name}")

        except Exception as e:
            print(f"✗ ERROR for {first_name} {last_name}: {e}")
            not_found_count += 1
            not_found_names.append(f"{first_name} {last_name}")

        print()

    print("="*80)
    print("SUMMARY")
    print("="*80)
    print(f"Total contractors in list: {len(contractor_rates)}")
    print(f"Successfully updated: {updated_count}")
    print(f"Not found: {not_found_count}")

    if not_found_names:
        print(f"\nContractors not found in database:")
        for name in not_found_names:
            print(f"  - {name}")
        print(f"\nThese may be:")
        print(f"  1. Typos in the spreadsheet")
        print(f"  2. New contractors not yet in the system")
        print(f"  3. Name variations (e.g., 'Diego' vs 'Diogo')")

    print()


def main():
    parser = argparse.ArgumentParser(description='Update contractor buy and sell rates')
    parser.add_argument('--table-name', required=True, help='DynamoDB table name')
    parser.add_argument('--dry-run', action='store_true', help='Preview changes without updating')

    args = parser.parse_args()

    update_contractor_rates(args.table_name, dry_run=args.dry_run)


if __name__ == '__main__':
    main()
