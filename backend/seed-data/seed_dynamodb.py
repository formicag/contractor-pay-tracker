#!/usr/bin/env python3
"""
DynamoDB Seed Script for Contractor Pay Tracking System
Loads golden reference data into DynamoDB table

Usage:
    python seed_dynamodb.py --stack-name contractor-pay-tracker-prod
    python seed_dynamodb.py --table-name contractor-pay-development
"""

import argparse
import uuid
from datetime import datetime
from decimal import Decimal

import boto3
from boto3.dynamodb.conditions import Key


def get_table_name(stack_name=None, table_name=None):
    """Get DynamoDB table name from stack outputs or directly"""
    if table_name:
        return table_name

    cf_client = boto3.client('cloudformation')
    response = cf_client.describe_stacks(StackName=stack_name)
    outputs = response['Stacks'][0]['Outputs']
    return next(o['OutputValue'] for o in outputs if o['OutputKey'] == 'DynamoDBTableName')


def seed_system_parameters(table):
    """Insert system configuration parameters"""
    print("\n" + "="*80)
    print("STEP 1: Seeding system parameters...")
    print("="*80)

    parameters = [
        ('VAT_RATE', '0.20', 'DECIMAL', 'UK VAT rate (20%)', False),
        ('HOURS_PER_DAY', '7.5', 'DECIMAL', 'Standard working hours per day', True),
        ('OVERTIME_MULTIPLIER', '1.5', 'DECIMAL', 'Overtime rate multiplier', False),
        ('OVERTIME_TOLERANCE_PERCENT', '2.0', 'DECIMAL', 'Allowed variance in overtime rate (%)', True),
        ('RATE_CHANGE_ALERT_PERCENT', '5.0', 'DECIMAL', 'Alert if rate changes by more than this %', True),
        ('NAME_MATCH_THRESHOLD', '85', 'INTEGER', 'Fuzzy name matching threshold (0-100)', True),
    ]

    with table.batch_writer() as batch:
        for param_key, param_value, data_type, description, is_editable in parameters:
            batch.put_item(Item={
                'PK': f'PARAM#{param_key}',
                'SK': 'VALUE',
                'EntityType': 'Parameter',
                'ParamKey': param_key,
                'ParamValue': param_value,
                'DataType': data_type,
                'Description': description,
                'IsEditable': is_editable,
                'UpdatedAt': datetime.utcnow().isoformat() + 'Z'
            })

    print(f"✓ Inserted {len(parameters)} system parameters")


def seed_umbrella_companies(table):
    """Insert 6 umbrella companies"""
    print("\n" + "="*80)
    print("STEP 2: Seeding umbrella companies...")
    print("="*80)

    umbrellas = [
        ('NASA', 'Nasa Umbrella Ltd', 'NASA GROUP'),
        ('PAYSTREAM', 'PayStream My Max 3 Limited', 'PAYSTREAM MYMAX'),
        ('PARASOL', 'Parasol Limited', 'PARASOL'),
        ('CLARITY', 'Clarity Umbrella Ltd', 'CLARITY'),
        ('GIANT', 'Giant Professional Limited', 'GIANT PROFESSIONAL LIMITED (PRG)'),
        ('WORKWELL', 'Workwell People Solutions Limited', 'WORKWELL (JSA SERVICES)'),
    ]

    umbrella_map = {}

    with table.batch_writer() as batch:
        for short_code, legal_name, file_name_variation in umbrellas:
            umbrella_id = str(uuid.uuid4())
            umbrella_map[short_code] = umbrella_id

            batch.put_item(Item={
                'PK': f'UMBRELLA#{umbrella_id}',
                'SK': 'PROFILE',
                'EntityType': 'Umbrella',
                'UmbrellaID': umbrella_id,
                'ShortCode': short_code,
                'LegalName': legal_name,
                'FileNameVariation': file_name_variation,
                'IsActive': True,
                'CreatedAt': datetime.utcnow().isoformat() + 'Z',
                'GSI2PK': f'UMBRELLA_CODE#{short_code}',
                'GSI2SK': 'PROFILE'
            })

    print(f"✓ Inserted {len(umbrellas)} umbrella companies")
    return umbrella_map


def seed_permanent_staff(table):
    """Insert 4 permanent staff members (to reject in validation)"""
    print("\n" + "="*80)
    print("STEP 3: Seeding permanent staff (validation blacklist)...")
    print("="*80)

    staff = [
        ('Syed', 'Syed', 'syed syed'),
        ('Victor', 'Cheung', 'victor cheung'),
        ('Gareth', 'Jones', 'gareth jones'),
        ('Martin', 'Alabone', 'martin alabone'),
    ]

    with table.batch_writer() as batch:
        for first_name, last_name, normalized_name in staff:
            batch.put_item(Item={
                'PK': f'PERMANENT#{normalized_name}',
                'SK': 'PROFILE',
                'EntityType': 'PermanentStaff',
                'FirstName': first_name,
                'LastName': last_name,
                'NormalizedName': normalized_name,
                'CreatedAt': datetime.utcnow().isoformat() + 'Z',
                'GSI2PK': 'PERMANENT_CHECK',
                'GSI2SK': f'NAME#{normalized_name}'
            })

    print(f"✓ Inserted {len(staff)} permanent staff members")
    print("  → These names will trigger CRITICAL errors if found in pay files")


def seed_pay_periods(table):
    """Insert 13 pay periods for 2025-2026"""
    print("\n" + "="*80)
    print("STEP 4: Seeding pay periods (13 periods)...")
    print("="*80)

    periods = [
        (1, 2025, '2025-01-13', '2025-02-09', '2025-02-10', '2025-02-21', 'COMPLETED'),
        (2, 2025, '2025-02-10', '2025-03-09', '2025-03-10', '2025-03-21', 'COMPLETED'),
        (3, 2025, '2025-03-10', '2025-04-06', '2025-04-07', '2025-04-18', 'COMPLETED'),
        (4, 2025, '2025-04-07', '2025-05-04', '2025-05-06', '2025-05-16', 'COMPLETED'),
        (5, 2025, '2025-05-05', '2025-06-01', '2025-06-02', '2025-06-13', 'COMPLETED'),
        (6, 2025, '2025-06-02', '2025-06-29', '2025-07-07', '2025-07-11', 'COMPLETED'),
        (7, 2025, '2025-06-30', '2025-07-27', '2025-08-04', '2025-08-08', 'COMPLETED'),
        (8, 2025, '2025-07-28', '2025-08-24', '2025-09-01', '2025-09-05', 'COMPLETED'),
        (9, 2025, '2025-08-25', '2025-09-21', '2025-09-29', '2025-10-03', 'COMPLETED'),
        (10, 2025, '2025-09-22', '2025-10-19', '2025-10-27', '2025-10-31', 'PENDING'),
        (11, 2025, '2025-10-20', '2025-11-16', '2025-11-24', '2025-11-28', 'PENDING'),
        (12, 2025, '2025-11-17', '2025-12-14', '2025-12-15', '2025-12-24', 'PENDING'),
        (13, 2025, '2025-12-15', '2026-01-11', '2026-01-19', '2026-01-23', 'PENDING'),
    ]

    with table.batch_writer() as batch:
        for period_num, year, work_start, work_end, submission, payment, status in periods:
            batch.put_item(Item={
                'PK': f'PERIOD#{period_num}',
                'SK': 'PROFILE',
                'EntityType': 'Period',
                'PeriodNumber': period_num,
                'PeriodYear': year,
                'WorkStartDate': work_start,
                'WorkEndDate': work_end,
                'SubmissionDate': submission,
                'PaymentDate': payment,
                'Status': status,
                'CreatedAt': datetime.utcnow().isoformat() + 'Z'
            })

    print(f"✓ Inserted {len(periods)} pay periods")
    print(f"  → Period 8 (28-Jul to 24-Aug) available for testing")


def seed_contractors(table):
    """Insert 23 contractors"""
    print("\n" + "="*80)
    print("STEP 5: Seeding contractors (23 active)...")
    print("="*80)

    contractors = [
        # NASA contractors
        ('Barry', 'Breden', 'barry breden', 'Solution Designer'),
        ('James', 'Matthews', 'james matthews', 'Solution Designer'),
        ('Kevin', 'Kayes', 'kevin kayes', 'Lead Solution Designer'),
        ('David', 'Hunt', 'david hunt', 'Solution Designer'),
        ('Diogo', 'Diogo', 'diogo diogo', 'Solution Designer'),
        ('Donna', 'Smith', 'donna smith', 'Junior Reference Engineer'),
        ('Richard', 'Williams', 'richard williams', 'Solution Designer'),
        ('Bilgun', 'Yildirim', 'bilgun yildirim', 'Solution Designer'),
        ('Duncan', 'Macadam', 'duncan macadam', 'Solution Designer'),

        # PAYSTREAM contractors
        ('Gary', 'Mandaracas', 'gary mandaracas', 'Solution Designer'),
        ('Graeme', 'Oldroyd', 'graeme oldroyd', 'Lead Solution Designer'),
        ('Sheela', 'Adesara', 'sheela adesara', 'Lead Solution Designer'),
        ('Parag', 'Maniar', 'parag maniar', 'Lead Solution Designer'),
        ('Basavaraj', 'Puttagangaiah', 'basavaraj puttagangaiah', 'Solution Designer'),

        # PARASOL contractors
        ('Chris', 'Halfpenny', 'chris halfpenny', 'Junior Reference Engineer'),
        ('Venu', 'Adluru', 'venu adluru', 'Reference Engineer'),
        ('Craig', 'Conkerton', 'craig conkerton', 'Senior Reference Engineer'),
        ('Julie', 'Barton', 'julie barton', 'Reference Engineer'),
        ('Vijetha', 'Dayyala', 'vijetha dayyala', 'Junior Reference Engineer'),

        # WORKWELL contractors
        ('Neil', 'Pomfret', 'neil pomfret', 'Solution Designer'),
        ('Matthew', 'Garrety', 'matthew garrety', 'Solution Designer'),

        # GIANT contractors
        ('Jonathan', 'Mays', 'jonathan mays', 'Solution Designer'),

        # CLARITY contractors
        ('Nik', 'Coultas', 'nik coultas', 'Programme Manager'),
    ]

    contractor_map = {}

    with table.batch_writer() as batch:
        for first_name, last_name, normalized_name, job_title in contractors:
            contractor_id = str(uuid.uuid4())
            contractor_key = f"{first_name} {last_name}"
            contractor_map[contractor_key] = contractor_id

            batch.put_item(Item={
                'PK': f'CONTRACTOR#{contractor_id}',
                'SK': 'PROFILE',
                'EntityType': 'Contractor',
                'ContractorID': contractor_id,
                'FirstName': first_name,
                'LastName': last_name,
                'NormalizedName': normalized_name,
                'JobTitle': job_title,
                'IsActive': True,
                'CreatedAt': datetime.utcnow().isoformat() + 'Z',
                'GSI2PK': f'NAME#{normalized_name}',
                'GSI2SK': f'CONTRACTOR#{contractor_id}'
            })

    print(f"✓ Inserted {len(contractors)} contractors")
    return contractor_map


def seed_contractor_umbrella_associations(table, contractor_map, umbrella_map):
    """
    Create contractor-umbrella associations (many-to-many)
    CRITICAL: Donna Smith has 2 associations (NASA + PARASOL) - Gemini improvement
    """
    print("\n" + "="*80)
    print("STEP 6: Creating contractor-umbrella associations...")
    print("="*80)

    associations = [
        # NASA contractors
        ('Barry Breden', 'NASA', '825675', '2025-01-01', None),
        ('James Matthews', 'NASA', '812299', '2025-01-01', None),
        ('Kevin Kayes', 'NASA', '810345', '2025-01-01', None),
        ('David Hunt', 'NASA', '801234', '2025-01-01', None),
        ('Diogo Diogo', 'NASA', '809876', '2025-01-01', None),
        ('Donna Smith', 'NASA', '812299', '2025-01-01', None),  # First association
        ('Richard Williams', 'NASA', '805432', '2025-01-01', None),
        ('Bilgun Yildirim', 'NASA', '803210', '2025-01-01', None),
        ('Duncan Macadam', 'NASA', '807654', '2025-01-01', None),

        # PAYSTREAM contractors
        ('Gary Mandaracas', 'PAYSTREAM', '100234', '2025-01-01', None),
        ('Graeme Oldroyd', 'PAYSTREAM', '100567', '2025-01-01', None),
        ('Sheela Adesara', 'PAYSTREAM', '100890', '2025-01-01', None),
        ('Parag Maniar', 'PAYSTREAM', '101123', '2025-01-01', None),
        ('Basavaraj Puttagangaiah', 'PAYSTREAM', '101456', '2025-01-01', None),

        # PARASOL contractors
        ('Chris Halfpenny', 'PARASOL', '200123', '2025-01-01', None),
        ('Venu Adluru', 'PARASOL', '200456', '2025-01-01', None),
        ('Craig Conkerton', 'PARASOL', '200789', '2025-01-01', None),
        ('Julie Barton', 'PARASOL', '201012', '2025-01-01', None),
        ('Vijetha Dayyala', 'PARASOL', '201345', '2025-01-01', None),
        ('Donna Smith', 'PARASOL', '129700', '2025-01-01', None),  # SECOND association! (Gemini improvement)

        # WORKWELL contractors
        ('Neil Pomfret', 'WORKWELL', '300123', '2025-01-01', None),
        ('Matthew Garrety', 'WORKWELL', '300456', '2025-01-01', None),

        # GIANT contractors
        ('Jonathan Mays', 'GIANT', '400123', '2025-01-01', None),

        # CLARITY contractors
        ('Nik Coultas', 'CLARITY', '500123', '2025-01-01', None),
    ]

    count = 0

    with table.batch_writer() as batch:
        for contractor_name, umbrella_code, employee_id, valid_from, valid_to in associations:
            contractor_id = contractor_map.get(contractor_name)
            umbrella_id = umbrella_map.get(umbrella_code)

            if not contractor_id:
                print(f"⚠  Warning: Contractor '{contractor_name}' not found")
                continue
            if not umbrella_id:
                print(f"⚠  Warning: Umbrella '{umbrella_code}' not found")
                continue

            association_id = str(uuid.uuid4())

            batch.put_item(Item={
                'PK': f'CONTRACTOR#{contractor_id}',
                'SK': f'UMBRELLA#{umbrella_id}',
                'EntityType': 'Association',
                'AssociationID': association_id,
                'ContractorID': contractor_id,
                'UmbrellaID': umbrella_id,
                'EmployeeID': employee_id,
                'ValidFrom': valid_from,
                'ValidTo': valid_to,
                'IsActive': True,
                'CreatedAt': datetime.utcnow().isoformat() + 'Z',
                'GSI1PK': f'UMBRELLA#{umbrella_id}',
                'GSI1SK': f'CONTRACTOR#{contractor_id}'
            })

            count += 1

    print(f"✓ Inserted {count} contractor-umbrella associations")
    print()
    print("🌟 CRITICAL VALIDATION:")
    print("  → Donna Smith has 2 associations:")
    print("     • NASA (employee_id: 812299)")
    print("     • PARASOL (employee_id: 129700)")
    print("  → This allows her to appear in BOTH NASA and PARASOL files ✓")
    print("  → Gemini improvement #1 implemented successfully!")

    return contractor_map, umbrella_map


def verify_seed_data(table):
    """Verify all seed data was loaded correctly"""
    print("\n" + "="*80)
    print("STEP 7: Verifying seed data...")
    print("="*80)

    # Count items by entity type
    checks = {
        'System parameters': ('PARAM#', 6),
        'Umbrella companies': ('UMBRELLA#', 6),
        'Permanent staff': ('PERMANENT#', 4),
        'Pay periods': ('PERIOD#', 13),
        'Contractors': ('CONTRACTOR#', 23),
    }

    all_passed = True

    for name, (pk_prefix, expected) in checks.items():
        # Scan for entities (inefficient but OK for seed verification)
        response = table.scan(
            FilterExpression='begins_with(PK, :prefix) AND SK = :sk',
            ExpressionAttributeValues={
                ':prefix': pk_prefix,
                ':sk': 'PROFILE' if pk_prefix != 'PARAM#' else 'VALUE'
            }
        )
        actual = len(response['Items'])
        status = "✓" if actual == expected else "✗"
        if actual != expected:
            all_passed = False
        print(f"  {status} {name}: {actual}/{expected}")

    # Special check for contractor associations (should be 25: 23 + 2 for Donna Smith)
    response = table.scan(
        FilterExpression='EntityType = :type',
        ExpressionAttributeValues={':type': 'Association'}
    )
    assoc_count = len(response['Items'])
    status = "✓" if assoc_count == 25 else "✗"
    if assoc_count != 25:
        all_passed = False
    print(f"  {status} Contractor associations: {assoc_count}/25")

    # Check Donna Smith's dual associations
    print("\n  🔍 Special validation:")
    response = table.scan(
        FilterExpression='EntityType = :type AND FirstName = :fname AND LastName = :lname',
        ExpressionAttributeValues={
            ':type': 'Contractor',
            ':fname': 'Donna',
            ':lname': 'Smith'
        }
    )

    if response['Items']:
        donna_id = response['Items'][0]['ContractorID']

        # Get her associations
        response = table.query(
            KeyConditionExpression='PK = :pk AND begins_with(SK, :sk)',
            ExpressionAttributeValues={
                ':pk': f'CONTRACTOR#{donna_id}',
                ':sk': 'UMBRELLA#'
            }
        )

        if len(response['Items']) == 2:
            print(f"  ✓ Donna Smith has {len(response['Items'])} associations:")
            for item in response['Items']:
                # Get umbrella details
                umbrella_response = table.get_item(
                    Key={
                        'PK': f'UMBRELLA#{item["UmbrellaID"]}',
                        'SK': 'PROFILE'
                    }
                )
                umbrella = umbrella_response['Item']
                print(f"     • {umbrella['ShortCode']}: {item['EmployeeID']}")
        else:
            print(f"  ✗ Donna Smith should have 2 associations, found {len(response['Items'])}")
            all_passed = False
    else:
        print("  ✗ Donna Smith not found")
        all_passed = False

    if all_passed:
        print("\n" + "="*80)
        print("✅ SEED DATA VERIFICATION PASSED!")
        print("="*80)
    else:
        print("\n" + "="*80)
        print("❌ SEED DATA VERIFICATION FAILED!")
        print("="*80)
        return False

    return True


def main():
    parser = argparse.ArgumentParser(description='Seed DynamoDB for contractor pay tracking')
    parser.add_argument('--stack-name', help='CloudFormation stack name')
    parser.add_argument('--table-name', help='DynamoDB table name (alternative to stack-name)')
    args = parser.parse_args()

    if not args.stack_name and not args.table_name:
        parser.error('Must provide either --stack-name or --table-name')

    print("="*80)
    print("CONTRACTOR PAY TRACKING SYSTEM - DYNAMODB SEEDING")
    print("="*80)
    print(f"Timestamp: {datetime.now().isoformat()}")
    print(f"Stack: {args.stack_name or 'N/A'}")
    print()

    try:
        # Get table name and connect
        table_name = get_table_name(args.stack_name, args.table_name)
        print(f"DynamoDB Table: {table_name}\n")

        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table(table_name)

        # Run seeding steps
        seed_system_parameters(table)
        umbrella_map = seed_umbrella_companies(table)
        seed_permanent_staff(table)
        seed_pay_periods(table)
        contractor_map = seed_contractors(table)
        contractor_map, umbrella_map = seed_contractor_umbrella_associations(
            table, contractor_map, umbrella_map
        )

        # Verify
        success = verify_seed_data(table)

        if success:
            print("\n" + "="*80)
            print("🎉 DATABASE SEEDING COMPLETE!")
            print("="*80)
            print()
            print("Next steps:")
            print("1. Test file upload with Period 8 sample files")
            print("2. Verify validation rules work correctly")
            print("3. Test Donna Smith appears in both NASA and PARASOL files ✓")
            print()
            print("💰 Estimated monthly cost: < £1 (DynamoDB on-demand pricing)")
            print()
        else:
            import sys
            sys.exit(1)

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        import sys
        sys.exit(1)


if __name__ == '__main__':
    main()
