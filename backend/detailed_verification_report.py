#!/usr/bin/env python3
"""
Detailed verification report - Spreadsheet vs Database comparison

Usage:
    python detailed_verification_report.py --table-name contractor-pay-development
"""

import argparse
from decimal import Decimal
import boto3


def detailed_verification(table_name):
    """Generate detailed comparison of spreadsheet data vs database"""

    dynamodb = boto3.resource('dynamodb', region_name='eu-west-2')
    table = dynamodb.Table(table_name)

    print("="*120)
    print("DETAILED VERIFICATION REPORT - SPREADSHEET VS DATABASE")
    print("="*120)
    print()

    # Spreadsheet data (original source of truth)
    spreadsheet_data = [
        {'name': 'Kieran Maceidan', 'email': 'kieran.maceidan@tesco.com', 'buy': '600', 'sell': '700.00', 'snow': '350.00', 'umbrella': 'NASA', 'emp_id': '846384'},
        {'name': 'Bassavaraj Puttanaganiaiah', 'email': 'bassavaraj.puttanaganiaiah@tesco.com', 'buy': '350.00', 'sell': '700.00', 'snow': '350.00', 'umbrella': 'Paystream', 'emp_id': '3936922'},
        {'name': 'Bikam Wildimo', 'email': 'bikam.wildimo@tesco.com', 'buy': '350.00', 'sell': '700.00', 'snow': '350.00', 'umbrella': 'NASA', 'emp_id': '841360'},
        {'name': 'David Hunt', 'email': 'david.hunt2@virginmedia02.co.uk', 'buy': '672.03', 'sell': '631.77', 'snow': '315.89', 'umbrella': 'NASA', 'emp_id': '812277'},
        {'name': 'Diogo Diogo-Cruz', 'email': 'diogo.diogo-cruz@virginmedia02.co.uk', 'buy': '557.41', 'sell': '681.41', 'snow': '340.70', 'umbrella': 'NASA', 'emp_id': '808042'},
        {'name': 'Graeme Oldroyd', 'email': 'graeme.oldroyd@virginmedia02.co.uk', 'buy': '534.96', 'sell': '681.41', 'snow': '340.70', 'umbrella': 'Paystream', 'emp_id': '3860377'},
        {'name': 'Jonathan May', 'email': 'jonathan.may@virginmedia02.co.uk', 'buy': '524.48', 'sell': '681.41', 'snow': '340.70', 'umbrella': 'Clarity', 'emp_id': '445288'},
        {'name': 'Kevin Kayes', 'email': 'kevin.kayes1@virginmedia02.co.uk', 'buy': '544.96', 'sell': '681.41', 'snow': '340.70', 'umbrella': 'NASA', 'emp_id': '814829'},
        {'name': 'Neil Birchett', 'email': 'neil.birchett@virginmedia02.co.uk', 'buy': '503.49', 'sell': '631.77', 'snow': '315.88', 'umbrella': 'Workwell', 'emp_id': '2223089'},
        {'name': 'Parag Maniar', 'email': 'parag.maniar2@virginmedia02.co.uk', 'buy': '573.59', 'sell': '681.41', 'snow': '340.70', 'umbrella': 'Paystream', 'emp_id': '3886353'},
        {'name': 'Paul Mach', 'email': 'paul.mach@virginmedia02.co.uk', 'buy': '542.30', 'sell': '681.41', 'snow': '340.70', 'umbrella': 'Clarity', 'emp_id': '445308'},
        {'name': 'Sheela Adearig', 'email': 'sheela.adearig@virginmedia02.co.uk', 'buy': '547.51', 'sell': '681.41', 'snow': '340.70', 'umbrella': 'Paystream', 'emp_id': '3861472'},
        {'name': 'Gary Manifesticas', 'email': 'gary.manifesticas@virginmedia02.co.uk', 'buy': '454.45', 'sell': '699.13', 'snow': '349.56', 'umbrella': 'NASA', 'emp_id': '3879216'},
        {'name': 'Barry Breden', 'email': 'barry.breden3@virginmedia02.co.uk', 'buy': '438.43', 'sell': '631.77', 'snow': '315.88', 'umbrella': 'NASA', 'emp_id': '825675'},
        {'name': 'Chris Keveney', 'email': 'chris.keveney1@virginmedia02.co.uk', 'buy': '300.00', 'sell': '325.00', 'snow': '162.50', 'umbrella': 'PARASOL', 'emp_id': '104877'},
        {'name': 'Craig Conkerton', 'email': 'craig.conkerton@virginmedia02.co.uk', 'buy': '300.00', 'sell': '361.00', 'snow': '180.50', 'umbrella': 'PARASOL', 'emp_id': '102399'},
        {'name': 'Donna Smith', 'email': 'donna.smith2@virginmedia02.co.uk', 'buy': '290.00', 'sell': '325.00', 'snow': '162.50', 'umbrella': 'PARASOL', 'emp_id': '129700'},
        {'name': 'James Matthews', 'email': 'james.matthews@virginmedia02.co.uk', 'buy': '490.00', 'sell': '631.77', 'snow': '315.88', 'umbrella': 'NASA', 'emp_id': '829112'},
        {'name': 'Julie Bennett', 'email': 'julie.bennett@virginmedia02.co.uk', 'buy': '415.00', 'sell': '480.00', 'snow': '240.00', 'umbrella': 'PARASOL', 'emp_id': '104226'},
        {'name': 'Matthew Garretty', 'email': 'matthew.garretty@virginmedia02.co.uk', 'buy': '444.23', 'sell': '631.77', 'snow': '315.88', 'umbrella': 'Workwell', 'emp_id': '2158980'},
        {'name': 'Richard Williams', 'email': 'richard.williams@virginmedia02.co.uk', 'buy': '450.00', 'sell': '631.77', 'snow': '315.88', 'umbrella': 'NASA', 'emp_id': '814233'},
        {'name': 'Venu Adluru', 'email': 'venu.adluru@virginmedia02.co.uk', 'buy': '425.00', 'sell': '500.00', 'snow': '250.00', 'umbrella': 'PARASOL', 'emp_id': '135433'},
        {'name': 'Vijetha Dayyala', 'email': 'vijetha.dayyala@virginmedia02.co.uk', 'buy': '280.00', 'sell': '325.00', 'snow': '162.50', 'umbrella': 'PARASOL', 'emp_id': '135278'},
    ]

    # Query database
    response = table.scan(
        FilterExpression='EntityType = :et AND SK = :sk',
        ExpressionAttributeValues={
            ':et': 'Contractor',
            ':sk': 'METADATA'
        }
    )

    db_contractors = {c['Email'].lower(): c for c in response.get('Items', [])}

    # Get umbrella associations
    response = table.scan(
        FilterExpression='EntityType = :et',
        ExpressionAttributeValues={':et': 'ContractorUmbrellaAssociation'}
    )
    db_associations = {a['ContractorEmail'].lower(): a for a in response.get('Items', [])}

    print("COMPARISON TABLE:")
    print("-" * 120)
    print(f"{'#':<3} {'Contractor':<25} {'Source':<15} {'Buy Rate':<15} {'Sell Rate':<15} {'SNOW Rate':<15} {'Match':<6}")
    print("-" * 120)

    all_match = True
    for idx, row in enumerate(spreadsheet_data, 1):
        email = row['email'].lower()
        name = row['name']

        # Spreadsheet values
        ss_buy = Decimal(row['buy'])
        ss_sell = Decimal(row['sell'])
        ss_snow = Decimal(row['snow'])

        # Database values
        db_contractor = db_contractors.get(email)

        if not db_contractor:
            print(f"{idx:<3} {name:<25} SPREADSHEET     £{ss_buy:<14} £{ss_sell:<14} £{ss_snow:<14}")
            print(f"{'':>3} {'':>25} DATABASE       NOT FOUND")
            all_match = False
            continue

        db_buy = db_contractor.get('BuyRate', Decimal('0'))
        db_sell = db_contractor.get('SellRate', Decimal('0'))
        db_snow = db_contractor.get('SNOWUnitRate', Decimal('0'))

        # Check match
        buy_match = (ss_buy == db_buy)
        sell_match = (ss_sell == db_sell)
        snow_match = (ss_snow == db_snow)

        match = buy_match and sell_match and snow_match
        match_symbol = "✓" if match else "✗"

        if not match:
            all_match = False

        # Print spreadsheet row
        print(f"{idx:<3} {name:<25} SPREADSHEET     £{ss_buy:<14} £{ss_sell:<14} £{ss_snow:<14}")

        # Print database row
        db_marker = f"{'✓' if buy_match else '✗'}{' ' if buy_match else '!'}"
        db_sell_marker = f"{'✓' if sell_match else '✗'}{' ' if sell_match else '!'}"
        db_snow_marker = f"{'✓' if snow_match else '✗'}{' ' if snow_match else '!'}"

        print(f"{'':>3} {'':>25} DATABASE       £{db_buy:<14} £{db_sell:<14} £{db_snow:<14} {match_symbol}")

        if not match:
            print(f"{'':>3} {'':>25} MISMATCH!")

        print()

    print("-" * 120)
    print()

    print("="*120)
    print("UMBRELLA ASSOCIATION VERIFICATION")
    print("="*120)
    print()

    print(f"{'#':<3} {'Contractor':<30} {'Spreadsheet':<20} {'Database':<20} {'Employee ID Match':<20}")
    print("-" * 120)

    umbrella_match = True
    for idx, row in enumerate(spreadsheet_data, 1):
        email = row['email'].lower()
        name = row['name']
        ss_umbrella = row['umbrella'].upper()
        ss_emp_id = row['emp_id']

        db_assoc = db_associations.get(email)

        if not db_assoc:
            print(f"{idx:<3} {name:<30} {ss_umbrella:<20} NOT FOUND            ✗")
            umbrella_match = False
            continue

        db_umbrella = db_assoc.get('UmbrellaCode', 'UNKNOWN')
        db_emp_id = db_assoc.get('EmployeeID', '')

        # Normalize umbrella codes for comparison
        ss_umbrella_norm = 'PAYSTREAM' if 'PAYSTREAM' in ss_umbrella.upper() else ss_umbrella.upper()

        match = (ss_umbrella_norm == db_umbrella and ss_emp_id == db_emp_id)
        match_symbol = "✓" if match else "✗"

        if not match:
            umbrella_match = False

        print(f"{idx:<3} {name:<30} {ss_umbrella:<20} {db_umbrella:<20} {ss_emp_id} / {db_emp_id} {match_symbol}")

    print("-" * 120)
    print()

    print("="*120)
    print("FINAL VERIFICATION RESULT")
    print("="*120)
    print()

    if all_match and umbrella_match:
        print("✅ 100% PERFECT MATCH - ZERO ERRORS")
        print()
        print(f"   ✓ All {len(spreadsheet_data)} contractors imported successfully")
        print(f"   ✓ All buy rates match spreadsheet exactly")
        print(f"   ✓ All sell rates match spreadsheet exactly")
        print(f"   ✓ All SNOW unit rates match spreadsheet exactly")
        print(f"   ✓ All umbrella associations correct")
        print(f"   ✓ All employee IDs correct")
        print()
        print(f"   Flask app will display 100% accurate contractor data!")
    else:
        print("❌ MISMATCHES DETECTED")
        if not all_match:
            print("   → Rate mismatches found (see table above)")
        if not umbrella_match:
            print("   → Umbrella association mismatches found (see table above)")

    print()


def main():
    parser = argparse.ArgumentParser(description='Detailed verification report')
    parser.add_argument('--table-name', required=True, help='DynamoDB table name')

    args = parser.parse_args()

    detailed_verification(args.table_name)


if __name__ == '__main__':
    main()
