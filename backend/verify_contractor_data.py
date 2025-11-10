#!/usr/bin/env python3
"""
Verify contractor data in DynamoDB - show what Flask app will see

Usage:
    python verify_contractor_data.py --table-name contractor-pay-development
"""

import argparse
from decimal import Decimal
import boto3
from boto3.dynamodb.conditions import Key


def verify_contractor_data(table_name):
    """Query and display all contractor data as Flask app would see it"""

    dynamodb = boto3.resource('dynamodb', region_name='eu-west-2')
    table = dynamodb.Table(table_name)

    print("="*100)
    print("CONTRACTOR DATA VERIFICATION - FLASK APP VIEW")
    print("="*100)
    print()

    # Query all contractors
    response = table.scan(
        FilterExpression='EntityType = :et AND SK = :sk',
        ExpressionAttributeValues={
            ':et': 'Contractor',
            ':sk': 'METADATA'
        }
    )

    contractors = sorted(response.get('Items', []), key=lambda x: x.get('LastName', ''))

    print(f"Total contractors in database: {len(contractors)}\n")

    # Expected rates from spreadsheet for verification
    expected_rates = {
        'kieran.maceidan@tesco.com': ('600', '700.00', '350.00'),
        'bassavaraj.puttanaganiaiah@tesco.com': ('350.00', '700.00', '350.00'),
        'bikam.wildimo@tesco.com': ('350.00', '700.00', '350.00'),
        'david.hunt2@virginmedia02.co.uk': ('672.03', '631.77', '315.89'),
        'diogo.diogo-cruz@virginmedia02.co.uk': ('557.41', '681.41', '340.70'),
        'graeme.oldroyd@virginmedia02.co.uk': ('534.96', '681.41', '340.70'),
        'jonathan.may@virginmedia02.co.uk': ('524.48', '681.41', '340.70'),
        'kevin.kayes1@virginmedia02.co.uk': ('544.96', '681.41', '340.70'),
        'neil.birchett@virginmedia02.co.uk': ('503.49', '631.77', '315.88'),
        'parag.maniar2@virginmedia02.co.uk': ('573.59', '681.41', '340.70'),
        'paul.mach@virginmedia02.co.uk': ('542.30', '681.41', '340.70'),
        'sheela.adearig@virginmedia02.co.uk': ('547.51', '681.41', '340.70'),
        'gary.manifesticas@virginmedia02.co.uk': ('454.45', '699.13', '349.56'),
        'barry.breden3@virginmedia02.co.uk': ('438.43', '631.77', '315.88'),
        'chris.keveney1@virginmedia02.co.uk': ('300.00', '325.00', '162.50'),
        'craig.conkerton@virginmedia02.co.uk': ('300.00', '361.00', '180.50'),
        'donna.smith2@virginmedia02.co.uk': ('290.00', '325.00', '162.50'),
        'james.matthews@virginmedia02.co.uk': ('490.00', '631.77', '315.88'),
        'julie.bennett@virginmedia02.co.uk': ('415.00', '480.00', '240.00'),
        'matthew.garretty@virginmedia02.co.uk': ('444.23', '631.77', '315.88'),
        'richard.williams@virginmedia02.co.uk': ('450.00', '631.77', '315.88'),
        'venu.adluru@virginmedia02.co.uk': ('425.00', '500.00', '250.00'),
        'vijetha.dayyala@virginmedia02.co.uk': ('280.00', '325.00', '162.50'),
    }

    print("-" * 100)
    print(f"{'#':<3} {'Name':<25} {'Email':<35} {'Buy Rate':<12} {'Sell Rate':<12} {'SNOW Rate':<12}")
    print("-" * 100)

    all_match = True
    for idx, contractor in enumerate(contractors, 1):
        first_name = contractor.get('FirstName', '')
        last_name = contractor.get('LastName', '')
        email = contractor.get('Email', '').lower()

        buy_rate = contractor.get('BuyRate', Decimal('0'))
        sell_rate = contractor.get('SellRate', Decimal('0'))
        snow_rate = contractor.get('SNOWUnitRate', Decimal('0'))

        name = f"{first_name} {last_name}"

        # Check if rates match expected
        expected = expected_rates.get(email)
        status = "✓"

        if expected:
            exp_buy = Decimal(expected[0])
            exp_sell = Decimal(expected[1])
            exp_snow = Decimal(expected[2])

            if buy_rate != exp_buy or sell_rate != exp_sell or snow_rate != exp_snow:
                status = "✗"
                all_match = False
        else:
            status = "?"
            all_match = False

        print(f"{idx:<3} {name:<25} {email:<35} £{buy_rate:<11} £{sell_rate:<11} £{snow_rate:<11} {status}")

    print("-" * 100)
    print()

    # Summary of umbrella associations
    print("="*100)
    print("UMBRELLA COMPANY ASSOCIATIONS")
    print("="*100)
    print()

    response = table.scan(
        FilterExpression='EntityType = :et',
        ExpressionAttributeValues={':et': 'ContractorUmbrellaAssociation'}
    )

    associations = response.get('Items', [])

    # Group by umbrella
    by_umbrella = {}
    for assoc in associations:
        umbrella_code = assoc.get('UmbrellaCode', 'UNKNOWN')
        if umbrella_code not in by_umbrella:
            by_umbrella[umbrella_code] = []

        # Get contractor details
        contractor_email = assoc.get('ContractorEmail', '')
        employee_id = assoc.get('EmployeeID', '')

        by_umbrella[umbrella_code].append({
            'email': contractor_email,
            'employee_id': employee_id
        })

    for umbrella_code in sorted(by_umbrella.keys()):
        contractors_list = by_umbrella[umbrella_code]
        print(f"{umbrella_code}: {len(contractors_list)} contractors")
        for c in sorted(contractors_list, key=lambda x: x['email']):
            print(f"  - {c['email']} (Employee ID: {c['employee_id']})")
        print()

    print("="*100)
    print("VERIFICATION RESULT")
    print("="*100)

    if all_match and len(contractors) == 23:
        print("\n✅ ALL VERIFICATIONS PASSED!")
        print(f"   → 23/23 contractors in database")
        print(f"   → All rates match spreadsheet exactly")
        print(f"   → Flask app will display correct data")
    else:
        print("\n⚠️ VERIFICATION WARNINGS")
        if len(contractors) != 23:
            print(f"   → Expected 23 contractors, found {len(contractors)}")
        if not all_match:
            print(f"   → Some rates do not match expected values")

    print()


def main():
    parser = argparse.ArgumentParser(description='Verify contractor data in DynamoDB')
    parser.add_argument('--table-name', required=True, help='DynamoDB table name')

    args = parser.parse_args()

    verify_contractor_data(args.table_name)


if __name__ == '__main__':
    main()
