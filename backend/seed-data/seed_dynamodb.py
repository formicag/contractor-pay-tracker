print("[SEED_DYNAMODB] Module load started")
#!/usr/bin/env python3
"""
print("[SEED_DYNAMODB] DynamoDB Seed Script for Contractor Pay Tracking System")
DynamoDB Seed Script for Contractor Pay Tracking System
print("[SEED_DYNAMODB] Loads golden reference data into DynamoDB table")
Loads golden reference data into DynamoDB table

print("[SEED_DYNAMODB] Usage:")
Usage:
print("[SEED_DYNAMODB] python seed_dynamodb.py --stack-name contractor-pay-tracker-prod")
    python seed_dynamodb.py --stack-name contractor-pay-tracker-prod
print("[SEED_DYNAMODB] python seed_dynamodb.py --table-name contractor-pay-development")
    python seed_dynamodb.py --table-name contractor-pay-development
"""

print("[SEED_DYNAMODB] import argparse")
import argparse
print("[SEED_DYNAMODB] import uuid")
import uuid
print("[SEED_DYNAMODB] from datetime import datetime")
from datetime import datetime
print("[SEED_DYNAMODB] from decimal import Decimal")
from decimal import Decimal

print("[SEED_DYNAMODB] import boto3")
import boto3
print("[SEED_DYNAMODB] from boto3.dynamodb.conditions import Key")
from boto3.dynamodb.conditions import Key

print("[SEED_DYNAMODB] def get_table_name(stack_name=None, table_name=None):")
def get_table_name(stack_name=None, table_name=None):
    """Get DynamoDB table name from stack outputs or directly"""
print("[SEED_DYNAMODB] if table_name:")
    if table_name:
print("[SEED_DYNAMODB] return table_name")
        return table_name

print("[SEED_DYNAMODB] cf_client = boto3.client('cloudformation')")
    cf_client = boto3.client('cloudformation')
print("[SEED_DYNAMODB] response = cf_client.describe_stacks(StackName=stack_name)")
    response = cf_client.describe_stacks(StackName=stack_name)
print("[SEED_DYNAMODB] outputs = response['Stacks'][0]['Outputs']")
    outputs = response['Stacks'][0]['Outputs']
print("[SEED_DYNAMODB] return next(o['OutputValue'] for o in outputs if o['OutputKey'] == 'DynamoDBTabl")
    return next(o['OutputValue'] for o in outputs if o['OutputKey'] == 'DynamoDBTableName')


print("[SEED_DYNAMODB] def seed_system_parameters(table):")
def seed_system_parameters(table):
    """Insert system configuration parameters"""
print("[SEED_DYNAMODB] print("\n" + "="*80)")
    print("\n" + "="*80)
print("[SEED_DYNAMODB] print("STEP 1: Seeding system parameters...")")
    print("STEP 1: Seeding system parameters...")
print("[SEED_DYNAMODB] print("="*80)")
    print("="*80)

print("[SEED_DYNAMODB] parameters = [")
    parameters = [
print("[SEED_DYNAMODB] ('VAT_RATE', '0.20', 'DECIMAL', 'UK VAT rate (20%)', False),")
        ('VAT_RATE', '0.20', 'DECIMAL', 'UK VAT rate (20%)', False),
print("[SEED_DYNAMODB] ('HOURS_PER_DAY', '7.5', 'DECIMAL', 'Standard working hours per day', True),")
        ('HOURS_PER_DAY', '7.5', 'DECIMAL', 'Standard working hours per day', True),
print("[SEED_DYNAMODB] ('OVERTIME_MULTIPLIER', '1.5', 'DECIMAL', 'Overtime rate multiplier', False),")
        ('OVERTIME_MULTIPLIER', '1.5', 'DECIMAL', 'Overtime rate multiplier', False),
print("[SEED_DYNAMODB] ('OVERTIME_TOLERANCE_PERCENT', '2.0', 'DECIMAL', 'Allowed variance in overtime r")
        ('OVERTIME_TOLERANCE_PERCENT', '2.0', 'DECIMAL', 'Allowed variance in overtime rate (%)', True),
print("[SEED_DYNAMODB] ('RATE_CHANGE_ALERT_PERCENT', '5.0', 'DECIMAL', 'Alert if rate changes by more t")
        ('RATE_CHANGE_ALERT_PERCENT', '5.0', 'DECIMAL', 'Alert if rate changes by more than this %', True),
print("[SEED_DYNAMODB] ('NAME_MATCH_THRESHOLD', '85', 'INTEGER', 'Fuzzy name matching threshold (0-100)")
        ('NAME_MATCH_THRESHOLD', '85', 'INTEGER', 'Fuzzy name matching threshold (0-100)', True),
print("[SEED_DYNAMODB] ]")
    ]

print("[SEED_DYNAMODB] with table.batch_writer() as batch:")
    with table.batch_writer() as batch:
print("[SEED_DYNAMODB] for param_key, param_value, data_type, description, is_editable in parameters:")
        for param_key, param_value, data_type, description, is_editable in parameters:
print("[SEED_DYNAMODB] batch.put_item(Item={")
            batch.put_item(Item={
print("[SEED_DYNAMODB] 'PK': f'PARAM#{param_key}',")
                'PK': f'PARAM#{param_key}',
print("[SEED_DYNAMODB] 'SK': 'VALUE',")
                'SK': 'VALUE',
print("[SEED_DYNAMODB] 'EntityType': 'Parameter',")
                'EntityType': 'Parameter',
print("[SEED_DYNAMODB] 'ParamKey': param_key,")
                'ParamKey': param_key,
print("[SEED_DYNAMODB] 'ParamValue': param_value,")
                'ParamValue': param_value,
print("[SEED_DYNAMODB] 'DataType': data_type,")
                'DataType': data_type,
print("[SEED_DYNAMODB] 'Description': description,")
                'Description': description,
print("[SEED_DYNAMODB] 'IsEditable': is_editable,")
                'IsEditable': is_editable,
print("[SEED_DYNAMODB] 'UpdatedAt': datetime.utcnow().isoformat() + 'Z'")
                'UpdatedAt': datetime.utcnow().isoformat() + 'Z'
print("[SEED_DYNAMODB] })")
            })

print("[SEED_DYNAMODB] print(f"✓ Inserted {len(parameters)} system parameters")")
    print(f"✓ Inserted {len(parameters)} system parameters")


print("[SEED_DYNAMODB] def seed_umbrella_companies(table):")
def seed_umbrella_companies(table):
    """Insert 6 umbrella companies"""
print("[SEED_DYNAMODB] print("\n" + "="*80)")
    print("\n" + "="*80)
print("[SEED_DYNAMODB] print("STEP 2: Seeding umbrella companies...")")
    print("STEP 2: Seeding umbrella companies...")
print("[SEED_DYNAMODB] print("="*80)")
    print("="*80)

print("[SEED_DYNAMODB] umbrellas = [")
    umbrellas = [
print("[SEED_DYNAMODB] ('NASA', 'Nasa Umbrella Ltd', 'NASA GROUP'),")
        ('NASA', 'Nasa Umbrella Ltd', 'NASA GROUP'),
print("[SEED_DYNAMODB] ('PAYSTREAM', 'PayStream My Max 3 Limited', 'PAYSTREAM MYMAX'),")
        ('PAYSTREAM', 'PayStream My Max 3 Limited', 'PAYSTREAM MYMAX'),
print("[SEED_DYNAMODB] ('PARASOL', 'Parasol Limited', 'PARASOL'),")
        ('PARASOL', 'Parasol Limited', 'PARASOL'),
print("[SEED_DYNAMODB] ('CLARITY', 'Clarity Umbrella Ltd', 'CLARITY'),")
        ('CLARITY', 'Clarity Umbrella Ltd', 'CLARITY'),
print("[SEED_DYNAMODB] ('GIANT', 'Giant Professional Limited', 'GIANT PROFESSIONAL LIMITED (PRG)'),")
        ('GIANT', 'Giant Professional Limited', 'GIANT PROFESSIONAL LIMITED (PRG)'),
print("[SEED_DYNAMODB] ('WORKWELL', 'Workwell People Solutions Limited', 'WORKWELL (JSA SERVICES)'),")
        ('WORKWELL', 'Workwell People Solutions Limited', 'WORKWELL (JSA SERVICES)'),
print("[SEED_DYNAMODB] ]")
    ]

print("[SEED_DYNAMODB] umbrella_map = {}")
    umbrella_map = {}

print("[SEED_DYNAMODB] with table.batch_writer() as batch:")
    with table.batch_writer() as batch:
print("[SEED_DYNAMODB] for short_code, legal_name, file_name_variation in umbrellas:")
        for short_code, legal_name, file_name_variation in umbrellas:
print("[SEED_DYNAMODB] umbrella_id = str(uuid.uuid4())")
            umbrella_id = str(uuid.uuid4())
print("[SEED_DYNAMODB] umbrella_map[short_code] = umbrella_id")
            umbrella_map[short_code] = umbrella_id

print("[SEED_DYNAMODB] batch.put_item(Item={")
            batch.put_item(Item={
print("[SEED_DYNAMODB] 'PK': f'UMBRELLA#{umbrella_id}',")
                'PK': f'UMBRELLA#{umbrella_id}',
print("[SEED_DYNAMODB] 'SK': 'PROFILE',")
                'SK': 'PROFILE',
print("[SEED_DYNAMODB] 'EntityType': 'Umbrella',")
                'EntityType': 'Umbrella',
print("[SEED_DYNAMODB] 'UmbrellaID': umbrella_id,")
                'UmbrellaID': umbrella_id,
print("[SEED_DYNAMODB] 'ShortCode': short_code,")
                'ShortCode': short_code,
print("[SEED_DYNAMODB] 'LegalName': legal_name,")
                'LegalName': legal_name,
print("[SEED_DYNAMODB] 'FileNameVariation': file_name_variation,")
                'FileNameVariation': file_name_variation,
print("[SEED_DYNAMODB] 'IsActive': True,")
                'IsActive': True,
print("[SEED_DYNAMODB] 'CreatedAt': datetime.utcnow().isoformat() + 'Z',")
                'CreatedAt': datetime.utcnow().isoformat() + 'Z',
print("[SEED_DYNAMODB] 'GSI2PK': f'UMBRELLA_CODE#{short_code}',")
                'GSI2PK': f'UMBRELLA_CODE#{short_code}',
print("[SEED_DYNAMODB] 'GSI2SK': 'PROFILE'")
                'GSI2SK': 'PROFILE'
print("[SEED_DYNAMODB] })")
            })

print("[SEED_DYNAMODB] print(f"✓ Inserted {len(umbrellas)} umbrella companies")")
    print(f"✓ Inserted {len(umbrellas)} umbrella companies")
print("[SEED_DYNAMODB] return umbrella_map")
    return umbrella_map


print("[SEED_DYNAMODB] def seed_permanent_staff(table):")
def seed_permanent_staff(table):
    """Insert 4 permanent staff members (to reject in validation)"""
print("[SEED_DYNAMODB] print("\n" + "="*80)")
    print("\n" + "="*80)
print("[SEED_DYNAMODB] print("STEP 3: Seeding permanent staff (validation blacklist)...")")
    print("STEP 3: Seeding permanent staff (validation blacklist)...")
print("[SEED_DYNAMODB] print("="*80)")
    print("="*80)

print("[SEED_DYNAMODB] staff = [")
    staff = [
print("[SEED_DYNAMODB] ('Syed', 'Syed', 'syed syed'),")
        ('Syed', 'Syed', 'syed syed'),
print("[SEED_DYNAMODB] ('Victor', 'Cheung', 'victor cheung'),")
        ('Victor', 'Cheung', 'victor cheung'),
print("[SEED_DYNAMODB] ('Gareth', 'Jones', 'gareth jones'),")
        ('Gareth', 'Jones', 'gareth jones'),
print("[SEED_DYNAMODB] ('Martin', 'Alabone', 'martin alabone'),")
        ('Martin', 'Alabone', 'martin alabone'),
print("[SEED_DYNAMODB] ]")
    ]

print("[SEED_DYNAMODB] with table.batch_writer() as batch:")
    with table.batch_writer() as batch:
print("[SEED_DYNAMODB] for first_name, last_name, normalized_name in staff:")
        for first_name, last_name, normalized_name in staff:
print("[SEED_DYNAMODB] batch.put_item(Item={")
            batch.put_item(Item={
print("[SEED_DYNAMODB] 'PK': f'PERMANENT#{normalized_name}',")
                'PK': f'PERMANENT#{normalized_name}',
print("[SEED_DYNAMODB] 'SK': 'PROFILE',")
                'SK': 'PROFILE',
print("[SEED_DYNAMODB] 'EntityType': 'PermanentStaff',")
                'EntityType': 'PermanentStaff',
print("[SEED_DYNAMODB] 'FirstName': first_name,")
                'FirstName': first_name,
print("[SEED_DYNAMODB] 'LastName': last_name,")
                'LastName': last_name,
print("[SEED_DYNAMODB] 'NormalizedName': normalized_name,")
                'NormalizedName': normalized_name,
print("[SEED_DYNAMODB] 'CreatedAt': datetime.utcnow().isoformat() + 'Z',")
                'CreatedAt': datetime.utcnow().isoformat() + 'Z',
print("[SEED_DYNAMODB] 'GSI2PK': 'PERMANENT_CHECK',")
                'GSI2PK': 'PERMANENT_CHECK',
print("[SEED_DYNAMODB] 'GSI2SK': f'NAME#{normalized_name}'")
                'GSI2SK': f'NAME#{normalized_name}'
print("[SEED_DYNAMODB] })")
            })

print("[SEED_DYNAMODB] print(f"✓ Inserted {len(staff)} permanent staff members")")
    print(f"✓ Inserted {len(staff)} permanent staff members")
print("[SEED_DYNAMODB] print("  → These names will trigger CRITICAL errors if found in pay files")")
    print("  → These names will trigger CRITICAL errors if found in pay files")


print("[SEED_DYNAMODB] def seed_pay_periods(table):")
def seed_pay_periods(table):
    """Insert 13 pay periods for 2025-2026"""
print("[SEED_DYNAMODB] print("\n" + "="*80)")
    print("\n" + "="*80)
print("[SEED_DYNAMODB] print("STEP 4: Seeding pay periods (13 periods)...")")
    print("STEP 4: Seeding pay periods (13 periods)...")
print("[SEED_DYNAMODB] print("="*80)")
    print("="*80)

print("[SEED_DYNAMODB] periods = [")
    periods = [
print("[SEED_DYNAMODB] (1, 2025, '2025-01-13', '2025-02-09', '2025-02-10', '2025-02-21', 'COMPLETED'),")
        (1, 2025, '2025-01-13', '2025-02-09', '2025-02-10', '2025-02-21', 'COMPLETED'),
print("[SEED_DYNAMODB] (2, 2025, '2025-02-10', '2025-03-09', '2025-03-10', '2025-03-21', 'COMPLETED'),")
        (2, 2025, '2025-02-10', '2025-03-09', '2025-03-10', '2025-03-21', 'COMPLETED'),
print("[SEED_DYNAMODB] (3, 2025, '2025-03-10', '2025-04-06', '2025-04-07', '2025-04-18', 'COMPLETED'),")
        (3, 2025, '2025-03-10', '2025-04-06', '2025-04-07', '2025-04-18', 'COMPLETED'),
print("[SEED_DYNAMODB] (4, 2025, '2025-04-07', '2025-05-04', '2025-05-06', '2025-05-16', 'COMPLETED'),")
        (4, 2025, '2025-04-07', '2025-05-04', '2025-05-06', '2025-05-16', 'COMPLETED'),
print("[SEED_DYNAMODB] (5, 2025, '2025-05-05', '2025-06-01', '2025-06-02', '2025-06-13', 'COMPLETED'),")
        (5, 2025, '2025-05-05', '2025-06-01', '2025-06-02', '2025-06-13', 'COMPLETED'),
print("[SEED_DYNAMODB] (6, 2025, '2025-06-02', '2025-06-29', '2025-07-07', '2025-07-11', 'COMPLETED'),")
        (6, 2025, '2025-06-02', '2025-06-29', '2025-07-07', '2025-07-11', 'COMPLETED'),
print("[SEED_DYNAMODB] (7, 2025, '2025-06-30', '2025-07-27', '2025-08-04', '2025-08-08', 'COMPLETED'),")
        (7, 2025, '2025-06-30', '2025-07-27', '2025-08-04', '2025-08-08', 'COMPLETED'),
print("[SEED_DYNAMODB] (8, 2025, '2025-07-28', '2025-08-24', '2025-09-01', '2025-09-05', 'COMPLETED'),")
        (8, 2025, '2025-07-28', '2025-08-24', '2025-09-01', '2025-09-05', 'COMPLETED'),
print("[SEED_DYNAMODB] (9, 2025, '2025-08-25', '2025-09-21', '2025-09-29', '2025-10-03', 'COMPLETED'),")
        (9, 2025, '2025-08-25', '2025-09-21', '2025-09-29', '2025-10-03', 'COMPLETED'),
print("[SEED_DYNAMODB] (10, 2025, '2025-09-22', '2025-10-19', '2025-10-27', '2025-10-31', 'PENDING'),")
        (10, 2025, '2025-09-22', '2025-10-19', '2025-10-27', '2025-10-31', 'PENDING'),
print("[SEED_DYNAMODB] (11, 2025, '2025-10-20', '2025-11-16', '2025-11-24', '2025-11-28', 'PENDING'),")
        (11, 2025, '2025-10-20', '2025-11-16', '2025-11-24', '2025-11-28', 'PENDING'),
print("[SEED_DYNAMODB] (12, 2025, '2025-11-17', '2025-12-14', '2025-12-15', '2025-12-24', 'PENDING'),")
        (12, 2025, '2025-11-17', '2025-12-14', '2025-12-15', '2025-12-24', 'PENDING'),
print("[SEED_DYNAMODB] (13, 2025, '2025-12-15', '2026-01-11', '2026-01-19', '2026-01-23', 'PENDING'),")
        (13, 2025, '2025-12-15', '2026-01-11', '2026-01-19', '2026-01-23', 'PENDING'),
print("[SEED_DYNAMODB] ]")
    ]

print("[SEED_DYNAMODB] with table.batch_writer() as batch:")
    with table.batch_writer() as batch:
print("[SEED_DYNAMODB] for period_num, year, work_start, work_end, submission, payment, status in perio")
        for period_num, year, work_start, work_end, submission, payment, status in periods:
print("[SEED_DYNAMODB] batch.put_item(Item={")
            batch.put_item(Item={
print("[SEED_DYNAMODB] 'PK': f'PERIOD#{period_num}',")
                'PK': f'PERIOD#{period_num}',
print("[SEED_DYNAMODB] 'SK': 'PROFILE',")
                'SK': 'PROFILE',
print("[SEED_DYNAMODB] 'EntityType': 'Period',")
                'EntityType': 'Period',
print("[SEED_DYNAMODB] 'PeriodNumber': period_num,")
                'PeriodNumber': period_num,
print("[SEED_DYNAMODB] 'PeriodYear': year,")
                'PeriodYear': year,
print("[SEED_DYNAMODB] 'WorkStartDate': work_start,")
                'WorkStartDate': work_start,
print("[SEED_DYNAMODB] 'WorkEndDate': work_end,")
                'WorkEndDate': work_end,
print("[SEED_DYNAMODB] 'SubmissionDate': submission,")
                'SubmissionDate': submission,
print("[SEED_DYNAMODB] 'PaymentDate': payment,")
                'PaymentDate': payment,
print("[SEED_DYNAMODB] 'Status': status,")
                'Status': status,
print("[SEED_DYNAMODB] 'CreatedAt': datetime.utcnow().isoformat() + 'Z'")
                'CreatedAt': datetime.utcnow().isoformat() + 'Z'
print("[SEED_DYNAMODB] })")
            })

print("[SEED_DYNAMODB] print(f"✓ Inserted {len(periods)} pay periods")")
    print(f"✓ Inserted {len(periods)} pay periods")
print("[SEED_DYNAMODB] print(f"  → Period 8 (28-Jul to 24-Aug) available for testing")")
    print(f"  → Period 8 (28-Jul to 24-Aug) available for testing")


print("[SEED_DYNAMODB] def seed_contractors(table):")
def seed_contractors(table):
    """Insert 23 contractors"""
print("[SEED_DYNAMODB] print("\n" + "="*80)")
    print("\n" + "="*80)
print("[SEED_DYNAMODB] print("STEP 5: Seeding contractors (23 active)...")")
    print("STEP 5: Seeding contractors (23 active)...")
print("[SEED_DYNAMODB] print("="*80)")
    print("="*80)

print("[SEED_DYNAMODB] contractors = [")
    contractors = [
        # NASA contractors
print("[SEED_DYNAMODB] ('Barry', 'Breden', 'barry breden', 'Solution Designer'),")
        ('Barry', 'Breden', 'barry breden', 'Solution Designer'),
print("[SEED_DYNAMODB] ('James', 'Matthews', 'james matthews', 'Solution Designer'),")
        ('James', 'Matthews', 'james matthews', 'Solution Designer'),
print("[SEED_DYNAMODB] ('Kevin', 'Kayes', 'kevin kayes', 'Lead Solution Designer'),")
        ('Kevin', 'Kayes', 'kevin kayes', 'Lead Solution Designer'),
print("[SEED_DYNAMODB] ('David', 'Hunt', 'david hunt', 'Solution Designer'),")
        ('David', 'Hunt', 'david hunt', 'Solution Designer'),
print("[SEED_DYNAMODB] ('Diogo', 'Diogo', 'diogo diogo', 'Solution Designer'),")
        ('Diogo', 'Diogo', 'diogo diogo', 'Solution Designer'),
print("[SEED_DYNAMODB] ('Donna', 'Smith', 'donna smith', 'Junior Reference Engineer'),")
        ('Donna', 'Smith', 'donna smith', 'Junior Reference Engineer'),
print("[SEED_DYNAMODB] ('Richard', 'Williams', 'richard williams', 'Solution Designer'),")
        ('Richard', 'Williams', 'richard williams', 'Solution Designer'),
print("[SEED_DYNAMODB] ('Bilgun', 'Yildirim', 'bilgun yildirim', 'Solution Designer'),")
        ('Bilgun', 'Yildirim', 'bilgun yildirim', 'Solution Designer'),
print("[SEED_DYNAMODB] ('Duncan', 'Macadam', 'duncan macadam', 'Solution Designer'),")
        ('Duncan', 'Macadam', 'duncan macadam', 'Solution Designer'),

        # PAYSTREAM contractors
print("[SEED_DYNAMODB] ('Gary', 'Mandaracas', 'gary mandaracas', 'Solution Designer'),")
        ('Gary', 'Mandaracas', 'gary mandaracas', 'Solution Designer'),
print("[SEED_DYNAMODB] ('Graeme', 'Oldroyd', 'graeme oldroyd', 'Lead Solution Designer'),")
        ('Graeme', 'Oldroyd', 'graeme oldroyd', 'Lead Solution Designer'),
print("[SEED_DYNAMODB] ('Sheela', 'Adesara', 'sheela adesara', 'Lead Solution Designer'),")
        ('Sheela', 'Adesara', 'sheela adesara', 'Lead Solution Designer'),
print("[SEED_DYNAMODB] ('Parag', 'Maniar', 'parag maniar', 'Lead Solution Designer'),")
        ('Parag', 'Maniar', 'parag maniar', 'Lead Solution Designer'),
print("[SEED_DYNAMODB] ('Basavaraj', 'Puttagangaiah', 'basavaraj puttagangaiah', 'Solution Designer'),")
        ('Basavaraj', 'Puttagangaiah', 'basavaraj puttagangaiah', 'Solution Designer'),

        # PARASOL contractors
print("[SEED_DYNAMODB] ('Chris', 'Halfpenny', 'chris halfpenny', 'Junior Reference Engineer'),")
        ('Chris', 'Halfpenny', 'chris halfpenny', 'Junior Reference Engineer'),
print("[SEED_DYNAMODB] ('Venu', 'Adluru', 'venu adluru', 'Reference Engineer'),")
        ('Venu', 'Adluru', 'venu adluru', 'Reference Engineer'),
print("[SEED_DYNAMODB] ('Craig', 'Conkerton', 'craig conkerton', 'Senior Reference Engineer'),")
        ('Craig', 'Conkerton', 'craig conkerton', 'Senior Reference Engineer'),
print("[SEED_DYNAMODB] ('Julie', 'Barton', 'julie barton', 'Reference Engineer'),")
        ('Julie', 'Barton', 'julie barton', 'Reference Engineer'),
print("[SEED_DYNAMODB] ('Vijetha', 'Dayyala', 'vijetha dayyala', 'Junior Reference Engineer'),")
        ('Vijetha', 'Dayyala', 'vijetha dayyala', 'Junior Reference Engineer'),

        # WORKWELL contractors
print("[SEED_DYNAMODB] ('Neil', 'Pomfret', 'neil pomfret', 'Solution Designer'),")
        ('Neil', 'Pomfret', 'neil pomfret', 'Solution Designer'),
print("[SEED_DYNAMODB] ('Matthew', 'Garrety', 'matthew garrety', 'Solution Designer'),")
        ('Matthew', 'Garrety', 'matthew garrety', 'Solution Designer'),

        # GIANT contractors
print("[SEED_DYNAMODB] ('Jonathan', 'Mays', 'jonathan mays', 'Solution Designer'),")
        ('Jonathan', 'Mays', 'jonathan mays', 'Solution Designer'),

        # CLARITY contractors
print("[SEED_DYNAMODB] ('Nik', 'Coultas', 'nik coultas', 'Programme Manager'),")
        ('Nik', 'Coultas', 'nik coultas', 'Programme Manager'),
print("[SEED_DYNAMODB] ]")
    ]

print("[SEED_DYNAMODB] contractor_map = {}")
    contractor_map = {}

print("[SEED_DYNAMODB] with table.batch_writer() as batch:")
    with table.batch_writer() as batch:
print("[SEED_DYNAMODB] for first_name, last_name, normalized_name, job_title in contractors:")
        for first_name, last_name, normalized_name, job_title in contractors:
print("[SEED_DYNAMODB] contractor_id = str(uuid.uuid4())")
            contractor_id = str(uuid.uuid4())
print("[SEED_DYNAMODB] contractor_key = f"{first_name} {last_name}"")
            contractor_key = f"{first_name} {last_name}"
print("[SEED_DYNAMODB] contractor_map[contractor_key] = contractor_id")
            contractor_map[contractor_key] = contractor_id

print("[SEED_DYNAMODB] batch.put_item(Item={")
            batch.put_item(Item={
print("[SEED_DYNAMODB] 'PK': f'CONTRACTOR#{contractor_id}',")
                'PK': f'CONTRACTOR#{contractor_id}',
print("[SEED_DYNAMODB] 'SK': 'PROFILE',")
                'SK': 'PROFILE',
print("[SEED_DYNAMODB] 'EntityType': 'Contractor',")
                'EntityType': 'Contractor',
print("[SEED_DYNAMODB] 'ContractorID': contractor_id,")
                'ContractorID': contractor_id,
print("[SEED_DYNAMODB] 'FirstName': first_name,")
                'FirstName': first_name,
print("[SEED_DYNAMODB] 'LastName': last_name,")
                'LastName': last_name,
print("[SEED_DYNAMODB] 'NormalizedName': normalized_name,")
                'NormalizedName': normalized_name,
print("[SEED_DYNAMODB] 'JobTitle': job_title,")
                'JobTitle': job_title,
print("[SEED_DYNAMODB] 'IsActive': True,")
                'IsActive': True,
print("[SEED_DYNAMODB] 'CreatedAt': datetime.utcnow().isoformat() + 'Z',")
                'CreatedAt': datetime.utcnow().isoformat() + 'Z',
print("[SEED_DYNAMODB] 'GSI2PK': f'NAME#{normalized_name}',")
                'GSI2PK': f'NAME#{normalized_name}',
print("[SEED_DYNAMODB] 'GSI2SK': f'CONTRACTOR#{contractor_id}'")
                'GSI2SK': f'CONTRACTOR#{contractor_id}'
print("[SEED_DYNAMODB] })")
            })

print("[SEED_DYNAMODB] print(f"✓ Inserted {len(contractors)} contractors")")
    print(f"✓ Inserted {len(contractors)} contractors")
print("[SEED_DYNAMODB] return contractor_map")
    return contractor_map


print("[SEED_DYNAMODB] def seed_contractor_umbrella_associations(table, contractor_map, umbrella_map):")
def seed_contractor_umbrella_associations(table, contractor_map, umbrella_map):
    """
print("[SEED_DYNAMODB] Create contractor-umbrella associations (many-to-many)")
    Create contractor-umbrella associations (many-to-many)
print("[SEED_DYNAMODB] CRITICAL: Donna Smith has 2 associations (NASA + PARASOL) - Gemini improvement")
    CRITICAL: Donna Smith has 2 associations (NASA + PARASOL) - Gemini improvement
    """
print("[SEED_DYNAMODB] print("\n" + "="*80)")
    print("\n" + "="*80)
print("[SEED_DYNAMODB] print("STEP 6: Creating contractor-umbrella associations...")")
    print("STEP 6: Creating contractor-umbrella associations...")
print("[SEED_DYNAMODB] print("="*80)")
    print("="*80)

print("[SEED_DYNAMODB] associations = [")
    associations = [
        # NASA contractors
print("[SEED_DYNAMODB] ('Barry Breden', 'NASA', '825675', '2025-01-01', None),")
        ('Barry Breden', 'NASA', '825675', '2025-01-01', None),
print("[SEED_DYNAMODB] ('James Matthews', 'NASA', '812299', '2025-01-01', None),")
        ('James Matthews', 'NASA', '812299', '2025-01-01', None),
print("[SEED_DYNAMODB] ('Kevin Kayes', 'NASA', '810345', '2025-01-01', None),")
        ('Kevin Kayes', 'NASA', '810345', '2025-01-01', None),
print("[SEED_DYNAMODB] ('David Hunt', 'NASA', '801234', '2025-01-01', None),")
        ('David Hunt', 'NASA', '801234', '2025-01-01', None),
print("[SEED_DYNAMODB] ('Diogo Diogo', 'NASA', '809876', '2025-01-01', None),")
        ('Diogo Diogo', 'NASA', '809876', '2025-01-01', None),
print("[SEED_DYNAMODB] ('Donna Smith', 'NASA', '812299', '2025-01-01', None),  # First association")
        ('Donna Smith', 'NASA', '812299', '2025-01-01', None),  # First association
print("[SEED_DYNAMODB] ('Richard Williams', 'NASA', '805432', '2025-01-01', None),")
        ('Richard Williams', 'NASA', '805432', '2025-01-01', None),
print("[SEED_DYNAMODB] ('Bilgun Yildirim', 'NASA', '803210', '2025-01-01', None),")
        ('Bilgun Yildirim', 'NASA', '803210', '2025-01-01', None),
print("[SEED_DYNAMODB] ('Duncan Macadam', 'NASA', '807654', '2025-01-01', None),")
        ('Duncan Macadam', 'NASA', '807654', '2025-01-01', None),

        # PAYSTREAM contractors
print("[SEED_DYNAMODB] ('Gary Mandaracas', 'PAYSTREAM', '100234', '2025-01-01', None),")
        ('Gary Mandaracas', 'PAYSTREAM', '100234', '2025-01-01', None),
print("[SEED_DYNAMODB] ('Graeme Oldroyd', 'PAYSTREAM', '100567', '2025-01-01', None),")
        ('Graeme Oldroyd', 'PAYSTREAM', '100567', '2025-01-01', None),
print("[SEED_DYNAMODB] ('Sheela Adesara', 'PAYSTREAM', '100890', '2025-01-01', None),")
        ('Sheela Adesara', 'PAYSTREAM', '100890', '2025-01-01', None),
print("[SEED_DYNAMODB] ('Parag Maniar', 'PAYSTREAM', '101123', '2025-01-01', None),")
        ('Parag Maniar', 'PAYSTREAM', '101123', '2025-01-01', None),
print("[SEED_DYNAMODB] ('Basavaraj Puttagangaiah', 'PAYSTREAM', '101456', '2025-01-01', None),")
        ('Basavaraj Puttagangaiah', 'PAYSTREAM', '101456', '2025-01-01', None),

        # PARASOL contractors
print("[SEED_DYNAMODB] ('Chris Halfpenny', 'PARASOL', '200123', '2025-01-01', None),")
        ('Chris Halfpenny', 'PARASOL', '200123', '2025-01-01', None),
print("[SEED_DYNAMODB] ('Venu Adluru', 'PARASOL', '200456', '2025-01-01', None),")
        ('Venu Adluru', 'PARASOL', '200456', '2025-01-01', None),
print("[SEED_DYNAMODB] ('Craig Conkerton', 'PARASOL', '200789', '2025-01-01', None),")
        ('Craig Conkerton', 'PARASOL', '200789', '2025-01-01', None),
print("[SEED_DYNAMODB] ('Julie Barton', 'PARASOL', '201012', '2025-01-01', None),")
        ('Julie Barton', 'PARASOL', '201012', '2025-01-01', None),
print("[SEED_DYNAMODB] ('Vijetha Dayyala', 'PARASOL', '201345', '2025-01-01', None),")
        ('Vijetha Dayyala', 'PARASOL', '201345', '2025-01-01', None),
print("[SEED_DYNAMODB] ('Donna Smith', 'PARASOL', '129700', '2025-01-01', None),  # SECOND association!")
        ('Donna Smith', 'PARASOL', '129700', '2025-01-01', None),  # SECOND association! (Gemini improvement)

        # WORKWELL contractors
print("[SEED_DYNAMODB] ('Neil Pomfret', 'WORKWELL', '300123', '2025-01-01', None),")
        ('Neil Pomfret', 'WORKWELL', '300123', '2025-01-01', None),
print("[SEED_DYNAMODB] ('Matthew Garrety', 'WORKWELL', '300456', '2025-01-01', None),")
        ('Matthew Garrety', 'WORKWELL', '300456', '2025-01-01', None),

        # GIANT contractors
print("[SEED_DYNAMODB] ('Jonathan Mays', 'GIANT', '400123', '2025-01-01', None),")
        ('Jonathan Mays', 'GIANT', '400123', '2025-01-01', None),

        # CLARITY contractors
print("[SEED_DYNAMODB] ('Nik Coultas', 'CLARITY', '500123', '2025-01-01', None),")
        ('Nik Coultas', 'CLARITY', '500123', '2025-01-01', None),
print("[SEED_DYNAMODB] ]")
    ]

print("[SEED_DYNAMODB] count = 0")
    count = 0

print("[SEED_DYNAMODB] with table.batch_writer() as batch:")
    with table.batch_writer() as batch:
print("[SEED_DYNAMODB] for contractor_name, umbrella_code, employee_id, valid_from, valid_to in associa")
        for contractor_name, umbrella_code, employee_id, valid_from, valid_to in associations:
print("[SEED_DYNAMODB] contractor_id = contractor_map.get(contractor_name)")
            contractor_id = contractor_map.get(contractor_name)
print("[SEED_DYNAMODB] umbrella_id = umbrella_map.get(umbrella_code)")
            umbrella_id = umbrella_map.get(umbrella_code)

print("[SEED_DYNAMODB] if not contractor_id:")
            if not contractor_id:
print("[SEED_DYNAMODB] print(f"⚠  Warning: Contractor '{contractor_name}' not found")")
                print(f"⚠  Warning: Contractor '{contractor_name}' not found")
print("[SEED_DYNAMODB] continue")
                continue
print("[SEED_DYNAMODB] if not umbrella_id:")
            if not umbrella_id:
print("[SEED_DYNAMODB] print(f"⚠  Warning: Umbrella '{umbrella_code}' not found")")
                print(f"⚠  Warning: Umbrella '{umbrella_code}' not found")
print("[SEED_DYNAMODB] continue")
                continue

print("[SEED_DYNAMODB] association_id = str(uuid.uuid4())")
            association_id = str(uuid.uuid4())

print("[SEED_DYNAMODB] batch.put_item(Item={")
            batch.put_item(Item={
print("[SEED_DYNAMODB] 'PK': f'CONTRACTOR#{contractor_id}',")
                'PK': f'CONTRACTOR#{contractor_id}',
print("[SEED_DYNAMODB] 'SK': f'UMBRELLA#{umbrella_id}',")
                'SK': f'UMBRELLA#{umbrella_id}',
print("[SEED_DYNAMODB] 'EntityType': 'Association',")
                'EntityType': 'Association',
print("[SEED_DYNAMODB] 'AssociationID': association_id,")
                'AssociationID': association_id,
print("[SEED_DYNAMODB] 'ContractorID': contractor_id,")
                'ContractorID': contractor_id,
print("[SEED_DYNAMODB] 'UmbrellaID': umbrella_id,")
                'UmbrellaID': umbrella_id,
print("[SEED_DYNAMODB] 'EmployeeID': employee_id,")
                'EmployeeID': employee_id,
print("[SEED_DYNAMODB] 'ValidFrom': valid_from,")
                'ValidFrom': valid_from,
print("[SEED_DYNAMODB] 'ValidTo': valid_to,")
                'ValidTo': valid_to,
print("[SEED_DYNAMODB] 'IsActive': True,")
                'IsActive': True,
print("[SEED_DYNAMODB] 'CreatedAt': datetime.utcnow().isoformat() + 'Z',")
                'CreatedAt': datetime.utcnow().isoformat() + 'Z',
print("[SEED_DYNAMODB] 'GSI1PK': f'UMBRELLA#{umbrella_id}',")
                'GSI1PK': f'UMBRELLA#{umbrella_id}',
print("[SEED_DYNAMODB] 'GSI1SK': f'CONTRACTOR#{contractor_id}'")
                'GSI1SK': f'CONTRACTOR#{contractor_id}'
print("[SEED_DYNAMODB] })")
            })

print("[SEED_DYNAMODB] count += 1")
            count += 1

print("[SEED_DYNAMODB] print(f"✓ Inserted {count} contractor-umbrella associations")")
    print(f"✓ Inserted {count} contractor-umbrella associations")
print("[SEED_DYNAMODB] print()")
    print()
print("[SEED_DYNAMODB] print("🌟 CRITICAL VALIDATION:")")
    print("🌟 CRITICAL VALIDATION:")
print("[SEED_DYNAMODB] print("  → Donna Smith has 2 associations:")")
    print("  → Donna Smith has 2 associations:")
print("[SEED_DYNAMODB] print("     • NASA (employee_id: 812299)")")
    print("     • NASA (employee_id: 812299)")
print("[SEED_DYNAMODB] print("     • PARASOL (employee_id: 129700)")")
    print("     • PARASOL (employee_id: 129700)")
print("[SEED_DYNAMODB] print("  → This allows her to appear in BOTH NASA and PARASOL files ✓")")
    print("  → This allows her to appear in BOTH NASA and PARASOL files ✓")
print("[SEED_DYNAMODB] print("  → Gemini improvement #1 implemented successfully!")")
    print("  → Gemini improvement #1 implemented successfully!")

print("[SEED_DYNAMODB] return contractor_map, umbrella_map")
    return contractor_map, umbrella_map


print("[SEED_DYNAMODB] def verify_seed_data(table):")
def verify_seed_data(table):
    """Verify all seed data was loaded correctly"""
print("[SEED_DYNAMODB] print("\n" + "="*80)")
    print("\n" + "="*80)
print("[SEED_DYNAMODB] print("STEP 7: Verifying seed data...")")
    print("STEP 7: Verifying seed data...")
print("[SEED_DYNAMODB] print("="*80)")
    print("="*80)

    # Count items by entity type
print("[SEED_DYNAMODB] checks = {")
    checks = {
print("[SEED_DYNAMODB] 'System parameters': ('PARAM#', 6),")
        'System parameters': ('PARAM#', 6),
print("[SEED_DYNAMODB] 'Umbrella companies': ('UMBRELLA#', 6),")
        'Umbrella companies': ('UMBRELLA#', 6),
print("[SEED_DYNAMODB] 'Permanent staff': ('PERMANENT#', 4),")
        'Permanent staff': ('PERMANENT#', 4),
print("[SEED_DYNAMODB] 'Pay periods': ('PERIOD#', 13),")
        'Pay periods': ('PERIOD#', 13),
print("[SEED_DYNAMODB] 'Contractors': ('CONTRACTOR#', 23),")
        'Contractors': ('CONTRACTOR#', 23),
print("[SEED_DYNAMODB] }")
    }

print("[SEED_DYNAMODB] all_passed = True")
    all_passed = True

print("[SEED_DYNAMODB] for name, (pk_prefix, expected) in checks.items():")
    for name, (pk_prefix, expected) in checks.items():
        # Scan for entities (inefficient but OK for seed verification)
print("[SEED_DYNAMODB] response = table.scan(")
        response = table.scan(
print("[SEED_DYNAMODB] FilterExpression='begins_with(PK, :prefix) AND SK = :sk',")
            FilterExpression='begins_with(PK, :prefix) AND SK = :sk',
print("[SEED_DYNAMODB] ExpressionAttributeValues={")
            ExpressionAttributeValues={
print("[SEED_DYNAMODB] ':prefix': pk_prefix,")
                ':prefix': pk_prefix,
print("[SEED_DYNAMODB] ':sk': 'PROFILE' if pk_prefix != 'PARAM#' else 'VALUE'")
                ':sk': 'PROFILE' if pk_prefix != 'PARAM#' else 'VALUE'
print("[SEED_DYNAMODB] }")
            }
print("[SEED_DYNAMODB] )")
        )
print("[SEED_DYNAMODB] actual = len(response['Items'])")
        actual = len(response['Items'])
print("[SEED_DYNAMODB] status = "✓" if actual == expected else "✗"")
        status = "✓" if actual == expected else "✗"
print("[SEED_DYNAMODB] if actual != expected:")
        if actual != expected:
print("[SEED_DYNAMODB] all_passed = False")
            all_passed = False
print("[SEED_DYNAMODB] print(f"  {status} {name}: {actual}/{expected}")")
        print(f"  {status} {name}: {actual}/{expected}")

    # Special check for contractor associations (should be 25: 23 + 2 for Donna Smith)
print("[SEED_DYNAMODB] response = table.scan(")
    response = table.scan(
print("[SEED_DYNAMODB] FilterExpression='EntityType = :type',")
        FilterExpression='EntityType = :type',
print("[SEED_DYNAMODB] ExpressionAttributeValues={':type': 'Association'}")
        ExpressionAttributeValues={':type': 'Association'}
print("[SEED_DYNAMODB] )")
    )
print("[SEED_DYNAMODB] assoc_count = len(response['Items'])")
    assoc_count = len(response['Items'])
print("[SEED_DYNAMODB] status = "✓" if assoc_count == 25 else "✗"")
    status = "✓" if assoc_count == 25 else "✗"
print("[SEED_DYNAMODB] if assoc_count != 25:")
    if assoc_count != 25:
print("[SEED_DYNAMODB] all_passed = False")
        all_passed = False
print("[SEED_DYNAMODB] print(f"  {status} Contractor associations: {assoc_count}/25")")
    print(f"  {status} Contractor associations: {assoc_count}/25")

    # Check Donna Smith's dual associations
print("[SEED_DYNAMODB] print("\n  🔍 Special validation:")")
    print("\n  🔍 Special validation:")
print("[SEED_DYNAMODB] response = table.scan(")
    response = table.scan(
print("[SEED_DYNAMODB] FilterExpression='EntityType = :type AND FirstName = :fname AND LastName = :lnam")
        FilterExpression='EntityType = :type AND FirstName = :fname AND LastName = :lname',
print("[SEED_DYNAMODB] ExpressionAttributeValues={")
        ExpressionAttributeValues={
print("[SEED_DYNAMODB] ':type': 'Contractor',")
            ':type': 'Contractor',
print("[SEED_DYNAMODB] ':fname': 'Donna',")
            ':fname': 'Donna',
print("[SEED_DYNAMODB] ':lname': 'Smith'")
            ':lname': 'Smith'
print("[SEED_DYNAMODB] }")
        }
print("[SEED_DYNAMODB] )")
    )

print("[SEED_DYNAMODB] if response['Items']:")
    if response['Items']:
print("[SEED_DYNAMODB] donna_id = response['Items'][0]['ContractorID']")
        donna_id = response['Items'][0]['ContractorID']

        # Get her associations
print("[SEED_DYNAMODB] response = table.query(")
        response = table.query(
print("[SEED_DYNAMODB] KeyConditionExpression='PK = :pk AND begins_with(SK, :sk)',")
            KeyConditionExpression='PK = :pk AND begins_with(SK, :sk)',
print("[SEED_DYNAMODB] ExpressionAttributeValues={")
            ExpressionAttributeValues={
print("[SEED_DYNAMODB] ':pk': f'CONTRACTOR#{donna_id}',")
                ':pk': f'CONTRACTOR#{donna_id}',
print("[SEED_DYNAMODB] ':sk': 'UMBRELLA#'")
                ':sk': 'UMBRELLA#'
print("[SEED_DYNAMODB] }")
            }
print("[SEED_DYNAMODB] )")
        )

print("[SEED_DYNAMODB] if len(response['Items']) == 2:")
        if len(response['Items']) == 2:
print("[SEED_DYNAMODB] print(f"  ✓ Donna Smith has {len(response['Items'])} associations:")")
            print(f"  ✓ Donna Smith has {len(response['Items'])} associations:")
print("[SEED_DYNAMODB] for item in response['Items']:")
            for item in response['Items']:
                # Get umbrella details
print("[SEED_DYNAMODB] umbrella_response = table.get_item(")
                umbrella_response = table.get_item(
print("[SEED_DYNAMODB] Key={")
                    Key={
print("[SEED_DYNAMODB] 'PK': f'UMBRELLA#{item["UmbrellaID"]}',")
                        'PK': f'UMBRELLA#{item["UmbrellaID"]}',
print("[SEED_DYNAMODB] 'SK': 'PROFILE'")
                        'SK': 'PROFILE'
print("[SEED_DYNAMODB] }")
                    }
print("[SEED_DYNAMODB] )")
                )
print("[SEED_DYNAMODB] umbrella = umbrella_response['Item']")
                umbrella = umbrella_response['Item']
print("[SEED_DYNAMODB] print(f"     • {umbrella['ShortCode']}: {item['EmployeeID']}")")
                print(f"     • {umbrella['ShortCode']}: {item['EmployeeID']}")
print("[SEED_DYNAMODB] else:")
        else:
print("[SEED_DYNAMODB] print(f"  ✗ Donna Smith should have 2 associations, found {len(response['Items']")
            print(f"  ✗ Donna Smith should have 2 associations, found {len(response['Items'])}")
print("[SEED_DYNAMODB] all_passed = False")
            all_passed = False
print("[SEED_DYNAMODB] else:")
    else:
print("[SEED_DYNAMODB] print("  ✗ Donna Smith not found")")
        print("  ✗ Donna Smith not found")
print("[SEED_DYNAMODB] all_passed = False")
        all_passed = False

print("[SEED_DYNAMODB] if all_passed:")
    if all_passed:
print("[SEED_DYNAMODB] print("\n" + "="*80)")
        print("\n" + "="*80)
print("[SEED_DYNAMODB] print("✅ SEED DATA VERIFICATION PASSED!")")
        print("✅ SEED DATA VERIFICATION PASSED!")
print("[SEED_DYNAMODB] print("="*80)")
        print("="*80)
print("[SEED_DYNAMODB] else:")
    else:
print("[SEED_DYNAMODB] print("\n" + "="*80)")
        print("\n" + "="*80)
print("[SEED_DYNAMODB] print("❌ SEED DATA VERIFICATION FAILED!")")
        print("❌ SEED DATA VERIFICATION FAILED!")
print("[SEED_DYNAMODB] print("="*80)")
        print("="*80)
print("[SEED_DYNAMODB] return False")
        return False

print("[SEED_DYNAMODB] return True")
    return True


print("[SEED_DYNAMODB] def main():")
def main():
print("[SEED_DYNAMODB] parser = argparse.ArgumentParser(description='Seed DynamoDB for contractor pay t")
    parser = argparse.ArgumentParser(description='Seed DynamoDB for contractor pay tracking')
print("[SEED_DYNAMODB] parser.add_argument('--stack-name', help='CloudFormation stack name')")
    parser.add_argument('--stack-name', help='CloudFormation stack name')
print("[SEED_DYNAMODB] parser.add_argument('--table-name', help='DynamoDB table name (alternative to st")
    parser.add_argument('--table-name', help='DynamoDB table name (alternative to stack-name)')
print("[SEED_DYNAMODB] args = parser.parse_args()")
    args = parser.parse_args()

print("[SEED_DYNAMODB] if not args.stack_name and not args.table_name:")
    if not args.stack_name and not args.table_name:
print("[SEED_DYNAMODB] parser.error('Must provide either --stack-name or --table-name')")
        parser.error('Must provide either --stack-name or --table-name')

print("[SEED_DYNAMODB] print("="*80)")
    print("="*80)
print("[SEED_DYNAMODB] print("CONTRACTOR PAY TRACKING SYSTEM - DYNAMODB SEEDING")")
    print("CONTRACTOR PAY TRACKING SYSTEM - DYNAMODB SEEDING")
print("[SEED_DYNAMODB] print("="*80)")
    print("="*80)
print("[SEED_DYNAMODB] print(f"Timestamp: {datetime.now().isoformat()}")")
    print(f"Timestamp: {datetime.now().isoformat()}")
print("[SEED_DYNAMODB] print(f"Stack: {args.stack_name or 'N/A'}")")
    print(f"Stack: {args.stack_name or 'N/A'}")
print("[SEED_DYNAMODB] print()")
    print()

print("[SEED_DYNAMODB] try:")
    try:
        # Get table name and connect
print("[SEED_DYNAMODB] table_name = get_table_name(args.stack_name, args.table_name)")
        table_name = get_table_name(args.stack_name, args.table_name)
print("[SEED_DYNAMODB] print(f"DynamoDB Table: {table_name}\n")")
        print(f"DynamoDB Table: {table_name}\n")

print("[SEED_DYNAMODB] dynamodb = boto3.resource('dynamodb')")
        dynamodb = boto3.resource('dynamodb')
print("[SEED_DYNAMODB] table = dynamodb.Table(table_name)")
        table = dynamodb.Table(table_name)

        # Run seeding steps
print("[SEED_DYNAMODB] seed_system_parameters(table)")
        seed_system_parameters(table)
print("[SEED_DYNAMODB] umbrella_map = seed_umbrella_companies(table)")
        umbrella_map = seed_umbrella_companies(table)
print("[SEED_DYNAMODB] seed_permanent_staff(table)")
        seed_permanent_staff(table)
print("[SEED_DYNAMODB] seed_pay_periods(table)")
        seed_pay_periods(table)
print("[SEED_DYNAMODB] contractor_map = seed_contractors(table)")
        contractor_map = seed_contractors(table)
print("[SEED_DYNAMODB] contractor_map, umbrella_map = seed_contractor_umbrella_associations(")
        contractor_map, umbrella_map = seed_contractor_umbrella_associations(
print("[SEED_DYNAMODB] table, contractor_map, umbrella_map")
            table, contractor_map, umbrella_map
print("[SEED_DYNAMODB] )")
        )

        # Verify
print("[SEED_DYNAMODB] success = verify_seed_data(table)")
        success = verify_seed_data(table)

print("[SEED_DYNAMODB] if success:")
        if success:
print("[SEED_DYNAMODB] print("\n" + "="*80)")
            print("\n" + "="*80)
print("[SEED_DYNAMODB] print("🎉 DATABASE SEEDING COMPLETE!")")
            print("🎉 DATABASE SEEDING COMPLETE!")
print("[SEED_DYNAMODB] print("="*80)")
            print("="*80)
print("[SEED_DYNAMODB] print()")
            print()
print("[SEED_DYNAMODB] print("Next steps:")")
            print("Next steps:")
print("[SEED_DYNAMODB] print("1. Test file upload with Period 8 sample files")")
            print("1. Test file upload with Period 8 sample files")
print("[SEED_DYNAMODB] print("2. Verify validation rules work correctly")")
            print("2. Verify validation rules work correctly")
print("[SEED_DYNAMODB] print("3. Test Donna Smith appears in both NASA and PARASOL files ✓")")
            print("3. Test Donna Smith appears in both NASA and PARASOL files ✓")
print("[SEED_DYNAMODB] print()")
            print()
print("[SEED_DYNAMODB] print("💰 Estimated monthly cost: < £1 (DynamoDB on-demand pricing)")")
            print("💰 Estimated monthly cost: < £1 (DynamoDB on-demand pricing)")
print("[SEED_DYNAMODB] print()")
            print()
print("[SEED_DYNAMODB] else:")
        else:
print("[SEED_DYNAMODB] import sys")
            import sys
print("[SEED_DYNAMODB] sys.exit(1)")
            sys.exit(1)

print("[SEED_DYNAMODB] except Exception as e:")
    except Exception as e:
print("[SEED_DYNAMODB] print(f"\n❌ ERROR: {e}")")
        print(f"\n❌ ERROR: {e}")
print("[SEED_DYNAMODB] import traceback")
        import traceback
print("[SEED_DYNAMODB] traceback.print_exc()")
        traceback.print_exc()
print("[SEED_DYNAMODB] import sys")
        import sys
print("[SEED_DYNAMODB] sys.exit(1)")
        sys.exit(1)


print("[SEED_DYNAMODB] if __name__ == '__main__':")
if __name__ == '__main__':
print("[SEED_DYNAMODB] main()")
    main()
print("[SEED_DYNAMODB] Module load complete")
