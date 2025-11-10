#!/usr/bin/env python3
"""
CRITICAL DATA IMPORT - 24 Contractors with ZERO ERRORS
Deletes all contractor data and imports fresh from spreadsheet

Usage:
    python import_24_contractors.py --table-name contractor-pay-development
"""

import argparse
import uuid
from datetime import datetime
from decimal import Decimal
import boto3
from boto3.dynamodb.conditions import Key


def parse_currency(value):
    """Parse currency string to Decimal (£350.00 -> Decimal('350.00'))"""
    if isinstance(value, Decimal):
        return value
    if isinstance(value, (int, float)):
        return Decimal(str(value))
    # Remove £ and any commas
    cleaned = str(value).replace('£', '').replace(',', '').strip()
    return Decimal(cleaned)


def normalize_name(first, last):
    """Normalize name for matching"""
    return f"{first.lower()} {last.lower()}"


def delete_all_contractor_data(table):
    """Delete ALL contractor-related records from DynamoDB"""
    print("\n" + "="*80)
    print("STEP 1: DELETING ALL CONTRACTOR DATA")
    print("="*80)

    # Entity types to delete
    entity_types = ['Contractor', 'ContractorSnapshot', 'ContractorUmbrellaAssociation']

    total_deleted = 0

    for entity_type in entity_types:
        print(f"\nDeleting {entity_type} records...")

        # Scan for all records of this type
        items_to_delete = []
        response = table.scan(
            FilterExpression='EntityType = :et',
            ExpressionAttributeValues={':et': entity_type}
        )
        items_to_delete.extend(response.get('Items', []))

        # Handle pagination
        while 'LastEvaluatedKey' in response:
            response = table.scan(
                FilterExpression='EntityType = :et',
                ExpressionAttributeValues={':et': entity_type},
                ExclusiveStartKey=response['LastEvaluatedKey']
            )
            items_to_delete.extend(response.get('Items', []))

        # Delete in batches
        if items_to_delete:
            with table.batch_writer() as batch:
                for item in items_to_delete:
                    batch.delete_item(
                        Key={
                            'PK': item['PK'],
                            'SK': item['SK']
                        }
                    )
                    total_deleted += 1

            print(f"  ✓ Deleted {len(items_to_delete)} {entity_type} records")
        else:
            print(f"  → No {entity_type} records found")

    print(f"\n✓ Total records deleted: {total_deleted}")
    return total_deleted


def get_umbrella_map(table):
    """Get umbrella company ID mapping from database"""
    print("\n" + "="*80)
    print("STEP 2: LOADING UMBRELLA COMPANY MAPPINGS")
    print("="*80)

    response = table.scan(
        FilterExpression='EntityType = :et',
        ExpressionAttributeValues={':et': 'Umbrella'}
    )

    umbrella_map = {}
    for item in response['Items']:
        short_code = item['ShortCode']
        umbrella_id = item['UmbrellaID']
        umbrella_map[short_code] = umbrella_id
        print(f"  ✓ {short_code}: {umbrella_id}")

    return umbrella_map


def import_contractors(table, umbrella_map):
    """Import all 23 contractors with EXACT data from spreadsheet"""
    print("\n" + "="*80)
    print("STEP 3: IMPORTING 23 CONTRACTORS")
    print("="*80)

    # ALL 23 rows from the spreadsheet (23 unique contractors)
    # Format: (Customer, Title, FirstName, LastName, ResourceEmail, NasstarEmail, JobTitle,
    #          SNOWProduct, SNOWUnitRate, SellRate, LineManager, EngagementType, BuyRate, UmbrellaCode, EmployeeID)
    contractors_data = [
        ('Tesco Mobile', 'Mr.', 'Kieran', 'Maceidan', 'kieran.maceidan@tesco.com', 'Duncan.Maceidan@nasstar.com',
         'Solution Designer', 'Lead Solution Designer - 0.5 Day', '350.00', '700.00', 'errol.raguaram@tesco.com',
         'Umbrella Company (PAYE)', '600', 'NASA', '846384'),

        ('Tesco Mobile', 'Mr.', 'Bassavaraj', 'Puttanaganiaiah', 'Bassavaraj.Puttanaganiaiah@tesco.com', 'Bas.Puttanaganiaiah@nasstar.com',
         'Solution Designer', 'Lead Solution Designer - 0.5 Day', '350.00', '700.00', 'peter.jugurnath@tesco.com',
         'Umbrella Company (PAYE)', '350.00', 'Paystream', '3936922'),

        ('Tesco Mobile', 'Mr.', 'Bikam', 'Wildimo', 'bikam.wildimo@tesco.com', 'Bikam.Wildimo@nasstar.com',
         'Solution Designer', 'Solution Architect (EN-SE) 0.5 Day', '350.00', '700.00', 'peter.jugurnath@tesco.com',
         'Umbrella Company (PAYE)', '350.00', 'NASA', '841360'),

        ('WM02', 'Mr', 'David', 'Hunt', 'David.Hunt2@virginmedia02.co.uk', 'David.Hunt@GCIonline.microsoft.com',
         'Solution Designer', 'O2 Solution Designer (EN-SE) 0.5 Day', '315.89', '631.77', 'john.pete@virginmedia02.co.uk',
         'Umbrella Company (PAYE)', '672.03', 'NASA', '812277'),

        ('WM02', 'Mr', 'Diogo', 'Diogo-Cruz', 'Diogo.Diogo-Cruz@virginmedia02.co.uk', 'Diogo.Diogo-Cruz@nasstar.com',
         'Lead Solution Designer', 'O2 Lead Solution Designer (EN-SE) 0.5 Day', '340.70', '681.41', 'Tracy.farley@telefonics.com',
         'Umbrella Company (PAYE)', '557.41', 'NASA', '808042'),

        ('WM02', 'Mr', 'Graeme', 'Oldroyd', 'Graeme.Oldroyd@virginmedia02.co.uk', 'Graeme.Oldroyd@nasstar.com',
         'Lead Solution Designer', 'O2 Lead Solution Designer (EN-SE) 0.5 Day', '340.70', '681.41', 'Barbara.Hall@telefonics.com',
         'Umbrella Company (PAYE)', '534.96', 'Paystream', '3860377'),

        ('WM02', 'Mr', 'Jonathan', 'May', 'Jonathan.May@virginmedia02.co.uk', 'Jonathan.May@nasstar.com',
         'Lead Solution Designer', 'O2 Lead Solution Designer (EN-SE) 0.5 Day', '340.70', '681.41', 'james.concepcion@virginmedia02.co.uk',
         'Umbrella Company (PAYE)', '524.48', 'Clarity', '445288'),

        ('WM02', 'Mr', 'Kevin', 'Kayes', 'Kevin.Kayes1@virginmedia02.co.uk', 'Kevin.Kayes@nasstar.com',
         'Lead Solution Designer', 'O2 Solution Designer (EN-SE) 0.5 Day', '340.70', '681.41', 'Tracy.farley@telefonics.com',
         'Umbrella Company (PAYE)', '544.96', 'NASA', '814829'),

        ('WM02', 'Mr', 'Neil', 'Birchett', 'Neil.Birchett@virginmedia02.co.uk', 'Neil.Diemer@telefonics.com',
         'Lead Solution Designer', 'O2 Solution Designer (EN-SE) 0.5 Day', '315.88', '631.77', 'Rajinder.Birch@virginmedia02.co.uk',
         'Umbrella Company (PAYE)', '503.49', 'Workwell', '2223089'),

        ('WM02', 'Mr', 'Parag', 'Maniar', 'Parag.Maniar2@virginmedia02.co.uk', 'parag.maniar@nasstar.com',
         'Lead Solution Designer', 'O2 Lead Solution Designer (EN-SE) 0.5 Day', '340.70', '681.41', 'Tracy.farley@telefonics.com',
         'Umbrella Company (PAYE)', '573.59', 'Paystream', '3886353'),

        ('WM02', 'Mr', 'Paul', 'Mach', 'Paul.Mach@virginmedia02.co.uk', 'Paul.Mach@nasstar.com',
         'Lead Solution Designer', 'O2 Lead Solution Designer (EN-SE) 0.5 Day', '340.70', '681.41', 'jonathan.tlali@telefonics.com',
         'Umbrella Company (PAYE)', '542.30', 'Clarity', '445308'),

        ('WM02', 'Ms', 'Sheela', 'Adearig', 'Sheela.Adearig@virginmedia02.co.uk', 'Sheela.Adearig@nasstar.com',
         'Lead Solution Designer', 'O2 Lead Solution Designer (EN-SE) 0.5 Day', '340.70', '681.41', 'Tracy.farley@telefonics.com',
         'Umbrella Company (PAYE)', '547.51', 'Paystream', '3861472'),

        ('WM02', 'Mr', 'Gary', 'Manifesticas', 'Gary.Manifesticas@virginmedia02.co.uk', 'Gary.Manifesticas@nasstar.com',
         'Solution Designer', 'Solution Architect (EN-SE) 0.5 Day', '349.56', '699.13', 'neil.pidgett@virginmedia02.co.uk',
         'Umbrella Company (PAYE)', '454.45', 'NASA', '3879216'),

        ('WM02', 'Mr', 'Barry', 'Breden', 'Barry.Breden3@virginmedia02.co.uk', 'Barry.Breden@nasstar.com',
         'Solution Designer', 'Solution Architect (EN-SE) 0.5 Day', '315.88', '631.77', 'Tracy.farley@telefonics.com',
         'Umbrella Company (PAYE)', '438.43', 'NASA', '825675'),

        ('WM02', 'Mr', 'Chris', 'Keveney', 'chris.keveney1@virginmedia02.co.uk', 'Chris.Keveney@nasstar.com',
         'Senior Reference Data Analyst', 'Senior Reference Data Analyst (EN-SE) O2 0.5 Day', '162.50', '325.00', 'kevin.mayhew@virginmedia02.co.uk',
         'Umbrella Company (PAYE)', '300.00', 'PARASOL', '104877'),

        ('WM02', 'Mr', 'Craig', 'Conkerton', 'craig.conkerton@virginmedia02.co.uk', 'Craig.Conkerton@nasstar.com',
         'Senior Reference Data Analyst', 'Senior Reference Data Analyst (EN-SE) O2 0.5 Day', '180.50', '361.00', 'kevin.mayhew@virginmedia02.co.uk',
         'Umbrella Company (PAYE)', '300.00', 'PARASOL', '102399'),

        ('WM02', 'Ms', 'Donna', 'Smith', 'Donna.Smith2@virginmedia02.co.uk', 'Donna.Smith@nasstar.com',
         'Senior Reference Data Analyst', 'Senior Reference Data Analyst (EN-SE) O2 0.5 Day', '162.50', '325.00', 'kevin.mayhew@virginmedia02.co.uk',
         'Umbrella Company (PAYE)', '290.00', 'PARASOL', '129700'),

        ('WM02', 'Mr', 'James', 'Matthews', 'james.matthews@virginmedia02.co.uk', 'James.Matthews@nasstar.com',
         'Solution Designer', 'Solution Architect (EN-SE) 0.5 Day', '315.88', '631.77', 'kevin.mayhew@virginmedia02.co.uk',
         'Umbrella Company (PAYE)', '490.00', 'NASA', '829112'),

        ('WM02', 'Ms', 'Julie', 'Bennett', 'Julie.Bennett@virginmedia02.co.uk', 'Julie.Bennett@nasstar.com',
         'Reference Data Manager', 'Reference Data Manager (EN-SE) O2 0.5 Day', '240.00', '480.00', 'kevin.mayhew@virginmedia02.co.uk',
         'Umbrella Company (PAYE)', '415.00', 'PARASOL', '104226'),

        ('WM02', 'Mr', 'Matthew', 'Garretty', 'matthew.garretty@virginmedia02.co.uk', 'Matthew.Garretty@nasstar.com',
         'Solution Designer', 'Solution Architect (EN-SE) 0.5 Day', '315.88', '631.77', 'kevin.mayhew@virginmedia02.co.uk',
         'Umbrella Company (PAYE)', '444.23', 'Workwell', '2158980'),

        ('WM02', 'Ms', 'Richard', 'Williams', 'Richard.Williams@virginmedia02.co.uk', 'Richard.Williams@nasstar.com',
         'Solution Designer', 'Solution Architect (EN-SE) 0.5 Day', '315.88', '631.77', 'kevin.mayhew@virginmedia02.co.uk',
         'Umbrella Company (PAYE)', '450.00', 'NASA', '814233'),

        ('WM02', 'Mr', 'Venu', 'Adluru', 'Venu.Adluru@virginmedia02.co.uk', 'Venu.Adluru@nasstar.com',
         'Reference Data Consultant', 'Senior Reference Data Analyst (EN-SE) O2 0.5 Day', '250.00', '500.00', 'kevin.mayhew@virginmedia02.co.uk',
         'Umbrella Company (PAYE)', '425.00', 'PARASOL', '135433'),

        ('WM02', 'Ms', 'Vijetha', 'Dayyala', 'Vijetha.Dayyala@virginmedia02.co.uk', 'Vijetha.Dayyala@nasstar.com',
         'Junior Reference Engineer', 'Senior Reference Data Analyst (EN-SE) O2 0.5 Day', '162.50', '325.00', 'kevin.mayhew@virginmedia02.co.uk',
         'Umbrella Company (PAYE)', '280.00', 'PARASOL', '135278'),
    ]

    contractor_map = {}
    imported_count = 0

    for data in contractors_data:
        customer, title, first_name, last_name, resource_email, nasstar_email, job_title, \
        snow_product, snow_unit_rate, sell_rate, line_manager, engagement_type, buy_rate, \
        umbrella_code, employee_id = data

        # Use Resource Contact Email as primary key
        contractor_email = resource_email.lower()

        # Check if we've already added this contractor (handle duplicates in spreadsheet)
        if contractor_email in contractor_map:
            print(f"  → Skipping duplicate: {first_name} {last_name} ({contractor_email})")
            continue

        # Generate contractor ID
        contractor_id = str(uuid.uuid4())
        contractor_map[contractor_email] = contractor_id

        normalized_name = normalize_name(first_name, last_name)

        # Parse rates
        buy_rate_decimal = parse_currency(buy_rate)
        sell_rate_decimal = parse_currency(sell_rate)
        snow_unit_rate_decimal = parse_currency(snow_unit_rate)

        # Normalize umbrella code to match database
        umbrella_code_normalized = umbrella_code.upper()
        if 'PAYSTREAM' in umbrella_code_normalized:
            umbrella_code_normalized = 'PAYSTREAM'

        umbrella_id = umbrella_map.get(umbrella_code_normalized)
        if not umbrella_id:
            print(f"  ✗ ERROR: Umbrella company '{umbrella_code}' not found in database")
            continue

        # Create Contractor METADATA record
        contractor_item = {
            'PK': f'CONTRACTOR#{contractor_email}',
            'SK': 'METADATA',
            'EntityType': 'Contractor',
            'ContractorID': contractor_id,
            'Email': contractor_email,
            'FirstName': first_name,
            'LastName': last_name,
            'NormalizedName': normalized_name,
            'Title': title,
            'JobTitle': job_title,
            'Customer': customer,
            'ResourceEmail': resource_email,
            'NasstarEmail': nasstar_email,
            'LineManagerEmail': line_manager,
            'SNOWProduct': snow_product,
            'SNOWUnitRate': snow_unit_rate_decimal,
            'SellRate': sell_rate_decimal,
            'BuyRate': buy_rate_decimal,
            'EngagementType': engagement_type,
            'IsActive': True,
            'CreatedAt': datetime.utcnow().isoformat() + 'Z',
            'RatesUpdatedAt': datetime.utcnow().isoformat() + 'Z',
            'GSI2PK': f'NAME#{normalized_name}',
            'GSI2SK': f'CONTRACTOR#{contractor_id}'
        }

        table.put_item(Item=contractor_item)

        # Create ContractorUmbrellaAssociation record
        association_id = str(uuid.uuid4())
        association_item = {
            'PK': f'CONTRACTOR#{contractor_email}',
            'SK': f'UMBRELLA#{umbrella_id}',
            'EntityType': 'ContractorUmbrellaAssociation',
            'AssociationID': association_id,
            'ContractorID': contractor_id,
            'ContractorEmail': contractor_email,
            'UmbrellaID': umbrella_id,
            'UmbrellaCode': umbrella_code_normalized,
            'EmployeeID': employee_id,
            'ValidFrom': '2025-01-01',
            'ValidTo': None,
            'IsActive': True,
            'CreatedAt': datetime.utcnow().isoformat() + 'Z',
            'GSI1PK': f'UMBRELLA#{umbrella_id}',
            'GSI1SK': f'CONTRACTOR#{contractor_email}'
        }

        table.put_item(Item=association_item)

        print(f"  ✓ {first_name} {last_name} ({contractor_email})")
        print(f"    Buy: £{buy_rate_decimal} | Sell: £{sell_rate_decimal} | SNOW: £{snow_unit_rate_decimal}")
        print(f"    Umbrella: {umbrella_code_normalized} | Employee ID: {employee_id}")

        imported_count += 1

    print(f"\n✓ Successfully imported {imported_count} contractors")
    return contractor_map


def verify_import_first_pass(table):
    """FIRST VERIFICATION: Count contractors and check rates are populated"""
    print("\n" + "="*80)
    print("VERIFICATION PASS 1: COUNT & RATE POPULATION CHECK")
    print("="*80)

    # Count Contractor METADATA records
    response = table.scan(
        FilterExpression='EntityType = :et AND SK = :sk',
        ExpressionAttributeValues={
            ':et': 'Contractor',
            ':sk': 'METADATA'
        }
    )

    contractors = response.get('Items', [])
    contractor_count = len(contractors)

    print(f"\nContractor count: {contractor_count}/23")

    if contractor_count != 23:
        print(f"  ✗ FAILED: Expected 23 contractors, found {contractor_count}")
        return False

    print(f"  ✓ PASSED: Found all 23 contractors")

    # Check rates are populated (not £0.00 or missing)
    missing_rates = []
    zero_rates = []

    for contractor in contractors:
        email = contractor.get('Email', 'UNKNOWN')
        buy_rate = contractor.get('BuyRate')
        sell_rate = contractor.get('SellRate')
        snow_rate = contractor.get('SNOWUnitRate')

        if buy_rate is None or sell_rate is None or snow_rate is None:
            missing_rates.append(email)
        elif buy_rate == Decimal('0') or sell_rate == Decimal('0') or snow_rate == Decimal('0'):
            zero_rates.append(email)

    if missing_rates:
        print(f"  ✗ FAILED: {len(missing_rates)} contractors missing rates:")
        for email in missing_rates:
            print(f"    - {email}")
        return False

    if zero_rates:
        print(f"  ✗ FAILED: {len(zero_rates)} contractors have £0.00 rates:")
        for email in zero_rates:
            print(f"    - {email}")
        return False

    print(f"  ✓ PASSED: All contractors have rates populated (not £0.00)")

    # Count umbrella associations
    response = table.scan(
        FilterExpression='EntityType = :et',
        ExpressionAttributeValues={':et': 'ContractorUmbrellaAssociation'}
    )

    assoc_count = len(response.get('Items', []))
    print(f"\nUmbrella associations: {assoc_count}/23")

    if assoc_count != 23:
        print(f"  ✗ FAILED: Expected 23 associations, found {assoc_count}")
        return False

    print(f"  ✓ PASSED: Found all 23 umbrella associations")

    return True


def verify_import_second_pass(table):
    """SECOND VERIFICATION: Query what Flask app will see - verify rates match spreadsheet"""
    print("\n" + "="*80)
    print("VERIFICATION PASS 2: FLASK APP VIEW & RATE ACCURACY")
    print("="*80)

    # Expected rates from spreadsheet (email -> (buy_rate, sell_rate, snow_rate))
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

    # Query contractors as Flask app would
    response = table.scan(
        FilterExpression='EntityType = :et AND SK = :sk',
        ExpressionAttributeValues={
            ':et': 'Contractor',
            ':sk': 'METADATA'
        }
    )

    contractors = response.get('Items', [])

    print(f"\nVerifying rates for all {len(contractors)} contractors:\n")

    all_match = True
    verification_results = []

    for contractor in contractors:
        email = contractor.get('Email', '').lower()
        first_name = contractor.get('FirstName', '')
        last_name = contractor.get('LastName', '')

        db_buy = contractor.get('BuyRate')
        db_sell = contractor.get('SellRate')
        db_snow = contractor.get('SNOWUnitRate')

        expected = expected_rates.get(email)

        if not expected:
            print(f"  ⚠  {first_name} {last_name} ({email}): NOT IN EXPECTED LIST")
            verification_results.append({
                'email': email,
                'name': f"{first_name} {last_name}",
                'status': 'UNKNOWN',
                'db_rates': (db_buy, db_sell, db_snow),
                'expected_rates': None
            })
            all_match = False
            continue

        exp_buy, exp_sell, exp_snow = expected
        exp_buy_decimal = parse_currency(exp_buy)
        exp_sell_decimal = parse_currency(exp_sell)
        exp_snow_decimal = parse_currency(exp_snow)

        match = (db_buy == exp_buy_decimal and
                db_sell == exp_sell_decimal and
                db_snow == exp_snow_decimal)

        status = "✓" if match else "✗"

        if not match:
            all_match = False
            print(f"  {status} {first_name} {last_name} ({email})")
            print(f"      Expected: Buy £{exp_buy} | Sell £{exp_sell} | SNOW £{exp_snow}")
            print(f"      Database: Buy £{db_buy} | Sell £{db_sell} | SNOW £{db_snow}")
        else:
            print(f"  {status} {first_name} {last_name} ({email})")
            print(f"      Buy £{db_buy} | Sell £{db_sell} | SNOW £{db_snow}")

        verification_results.append({
            'email': email,
            'name': f"{first_name} {last_name}",
            'status': 'MATCH' if match else 'MISMATCH',
            'db_rates': (db_buy, db_sell, db_snow),
            'expected_rates': (exp_buy_decimal, exp_sell_decimal, exp_snow_decimal)
        })

    return all_match, verification_results


def main():
    parser = argparse.ArgumentParser(description='Import 24 contractors with ZERO ERRORS')
    parser.add_argument('--table-name', required=True, help='DynamoDB table name')

    args = parser.parse_args()

    print("="*80)
    print("CRITICAL CONTRACTOR DATA IMPORT - 100% ACCURACY REQUIRED")
    print("="*80)
    print(f"Table: {args.table_name}")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print()

    # Connect to DynamoDB
    dynamodb = boto3.resource('dynamodb', region_name='eu-west-2')
    table = dynamodb.Table(args.table_name)

    try:
        # Step 1: Delete all contractor data
        delete_all_contractor_data(table)

        # Step 2: Get umbrella company mappings
        umbrella_map = get_umbrella_map(table)

        # Step 3: Import 24 contractors
        contractor_map = import_contractors(table, umbrella_map)

        # Step 4: First verification pass
        first_pass = verify_import_first_pass(table)

        if not first_pass:
            print("\n" + "="*80)
            print("❌ FIRST VERIFICATION FAILED - IMPORT INCOMPLETE")
            print("="*80)
            import sys
            sys.exit(1)

        # Step 5: Second verification pass
        second_pass, verification_results = verify_import_second_pass(table)

        # Final summary
        print("\n" + "="*80)
        print("FINAL VERIFICATION SUMMARY")
        print("="*80)

        if first_pass and second_pass:
            print("\n✅ 100% SUCCESS - ALL VERIFICATIONS PASSED!")
            print(f"   → {len(contractor_map)} contractors imported")
            print(f"   → All rates match spreadsheet exactly")
            print(f"   → Flask app will see correct data")
        else:
            print("\n❌ VERIFICATION FAILED")
            if not first_pass:
                print("   → First pass failed (count or missing rates)")
            if not second_pass:
                print("   → Second pass failed (rate mismatches)")

                mismatches = [r for r in verification_results if r['status'] == 'MISMATCH']
                print(f"\n   {len(mismatches)} rate mismatches found:")
                for m in mismatches:
                    print(f"     - {m['name']} ({m['email']})")

            import sys
            sys.exit(1)

        print("\n" + "="*80)

    except Exception as e:
        print(f"\n❌ FATAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        import sys
        sys.exit(1)


if __name__ == '__main__':
    main()
