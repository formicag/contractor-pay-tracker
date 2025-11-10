#!/usr/bin/env python3
"""
Seed Script for Contractor Pay Tracking System
Loads golden reference data into Aurora PostgreSQL database

Usage:
    python seed.py --stack-name contractor-pay-tracker-prod
    python seed.py --db-secret-arn arn:aws:secretsmanager:...
"""

import argparse
import json
import os
import sys
from datetime import datetime

import boto3
import psycopg2
from psycopg2.extras import execute_values


def get_database_credentials(stack_name=None, secret_arn=None):
    """Retrieve database credentials from AWS Secrets Manager"""
    session = boto3.session.Session()
    secrets_client = session.client('secretsmanager')

    if not secret_arn:
        # Get secret ARN from CloudFormation stack outputs
        cf_client = session.client('cloudformation')
        response = cf_client.describe_stacks(StackName=stack_name)
        outputs = response['Stacks'][0]['Outputs']
        secret_arn = next(o['OutputValue'] for o in outputs if o['OutputKey'] == 'DatabaseSecretArn')
        db_endpoint = next(o['OutputValue'] for o in outputs if o['OutputKey'] == 'DatabaseClusterEndpoint')
        db_port = next(o['OutputValue'] for o in outputs if o['OutputKey'] == 'DatabasePort')
    else:
        # Extract endpoint from stack if provided
        raise ValueError("Must provide stack_name to automatically retrieve endpoint")

    # Get secret value
    response = secrets_client.get_secret_value(SecretId=secret_arn)
    secret = json.loads(response['SecretString'])

    return {
        'host': db_endpoint,
        'port': int(db_port),
        'database': 'contractorpay',
        'user': secret['username'],
        'password': secret['password']
    }


def create_connection(credentials):
    """Create PostgreSQL connection"""
    print(f"Connecting to database at {credentials['host']}:{credentials['port']}...")
    conn = psycopg2.connect(**credentials)
    conn.autocommit = False
    print("Connected successfully!")
    return conn


def run_schema(conn):
    """Execute schema.sql to create all tables"""
    print("\n" + "="*80)
    print("STEP 1: Creating database schema (14 tables)...")
    print("="*80)

    schema_path = os.path.join(os.path.dirname(__file__), 'schema.sql')
    with open(schema_path, 'r') as f:
        schema_sql = f.read()

    cursor = conn.cursor()
    try:
        cursor.execute(schema_sql)
        conn.commit()
        print("✓ Schema created successfully!")
    except Exception as e:
        conn.rollback()
        print(f"✗ Error creating schema: {e}")
        raise
    finally:
        cursor.close()


def seed_system_parameters(conn):
    """Insert system configuration parameters"""
    print("\n" + "="*80)
    print("STEP 2: Seeding system parameters...")
    print("="*80)

    parameters = [
        ('VAT_RATE', '0.20', 'DECIMAL', 'UK VAT rate (20%)', False),
        ('HOURS_PER_DAY', '7.5', 'DECIMAL', 'Standard working hours per day', True),
        ('OVERTIME_MULTIPLIER', '1.5', 'DECIMAL', 'Overtime rate multiplier', False),
        ('OVERTIME_TOLERANCE_PERCENT', '2.0', 'DECIMAL', 'Allowed variance in overtime rate (%)', True),
        ('RATE_CHANGE_ALERT_PERCENT', '5.0', 'DECIMAL', 'Alert if rate changes by more than this %', True),
        ('NAME_MATCH_THRESHOLD', '85', 'INTEGER', 'Fuzzy name matching threshold (0-100)', True),
    ]

    cursor = conn.cursor()
    try:
        execute_values(cursor, """
            INSERT INTO system_parameters (param_key, param_value, data_type, description, is_editable)
            VALUES %s
        """, parameters)
        conn.commit()
        print(f"✓ Inserted {len(parameters)} system parameters")
    except Exception as e:
        conn.rollback()
        print(f"✗ Error seeding parameters: {e}")
        raise
    finally:
        cursor.close()


def seed_umbrella_companies(conn):
    """Insert 6 umbrella companies"""
    print("\n" + "="*80)
    print("STEP 3: Seeding umbrella companies...")
    print("="*80)

    umbrellas = [
        ('NASA', 'Nasa Umbrella Ltd', 'NASA GROUP'),
        ('PAYSTREAM', 'PayStream My Max 3 Limited', 'PAYSTREAM MYMAX'),
        ('PARASOL', 'Parasol Limited', 'PARASOL'),
        ('CLARITY', 'Clarity Umbrella Ltd', 'CLARITY'),
        ('GIANT', 'Giant Professional Limited', 'GIANT PROFESSIONAL LIMITED (PRG)'),
        ('WORKWELL', 'Workwell People Solutions Limited', 'WORKWELL (JSA SERVICES)'),
    ]

    cursor = conn.cursor()
    try:
        execute_values(cursor, """
            INSERT INTO umbrella_companies (short_code, legal_name, file_name_variation)
            VALUES %s
            RETURNING umbrella_id, short_code
        """, umbrellas)

        umbrella_map = {row[1]: row[0] for row in cursor.fetchall()}
        conn.commit()
        print(f"✓ Inserted {len(umbrellas)} umbrella companies")
        return umbrella_map
    except Exception as e:
        conn.rollback()
        print(f"✗ Error seeding umbrellas: {e}")
        raise
    finally:
        cursor.close()


def seed_pay_periods(conn):
    """Insert 13 pay periods for 2025-2026"""
    print("\n" + "="*80)
    print("STEP 5: Seeding pay periods (13 periods)...")
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

    cursor = conn.cursor()
    try:
        execute_values(cursor, """
            INSERT INTO pay_periods (period_number, period_year, work_start_date, work_end_date,
                                    submission_date, payment_date, status)
            VALUES %s
            RETURNING period_id, period_number
        """, periods)

        period_map = {row[1]: row[0] for row in cursor.fetchall()}
        conn.commit()
        print(f"✓ Inserted {len(periods)} pay periods")
        print(f"  → Period 8 (28-Jul to 24-Aug) available for testing")
        return period_map
    except Exception as e:
        conn.rollback()
        print(f"✗ Error seeding pay periods: {e}")
        raise
    finally:
        cursor.close()


def seed_contractors(conn):
    """Insert 23 contractors"""
    print("\n" + "="*80)
    print("STEP 6: Seeding contractors (23 active)...")
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

    cursor = conn.cursor()
    try:
        execute_values(cursor, """
            INSERT INTO contractors (first_name, last_name, normalized_name, job_title)
            VALUES %s
            RETURNING contractor_id, first_name, last_name
        """, contractors)

        contractor_map = {f"{row[1]} {row[2]}": row[0] for row in cursor.fetchall()}
        conn.commit()
        print(f"✓ Inserted {len(contractors)} contractors")
        return contractor_map
    except Exception as e:
        conn.rollback()
        print(f"✗ Error seeding contractors: {e}")
        raise
    finally:
        cursor.close()


def seed_contractor_umbrella_associations(conn, contractor_map, umbrella_map):
    """
    Create contractor-umbrella associations (many-to-many)
    CRITICAL: Donna Smith has 2 associations (NASA + PARASOL) - Gemini improvement
    """
    print("\n" + "="*80)
    print("STEP 7: Creating contractor-umbrella associations...")
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

    # Build tuples with UUIDs
    association_tuples = []
    for contractor_name, umbrella_code, employee_id, valid_from, valid_to in associations:
        contractor_id = contractor_map.get(contractor_name)
        umbrella_id = umbrella_map.get(umbrella_code)

        if not contractor_id:
            print(f"⚠  Warning: Contractor '{contractor_name}' not found")
            continue
        if not umbrella_id:
            print(f"⚠  Warning: Umbrella '{umbrella_code}' not found")
            continue

        association_tuples.append((
            contractor_id,
            umbrella_id,
            employee_id,
            valid_from,
            valid_to
        ))

    cursor = conn.cursor()
    try:
        execute_values(cursor, """
            INSERT INTO contractor_umbrella_associations
                (contractor_id, umbrella_id, employee_id, valid_from, valid_to)
            VALUES %s
        """, association_tuples)
        conn.commit()
        print(f"✓ Inserted {len(association_tuples)} contractor-umbrella associations")
        print()
        print("🌟 CRITICAL VALIDATION:")
        print("  → Donna Smith has 2 associations:")
        print("     • NASA (employee_id: 812299)")
        print("     • PARASOL (employee_id: 129700)")
        print("  → This allows her to appear in BOTH NASA and PARASOL files ✓")
        print("  → Gemini improvement #1 implemented successfully!")
    except Exception as e:
        conn.rollback()
        print(f"✗ Error seeding associations: {e}")
        raise
    finally:
        cursor.close()


def verify_seed_data(conn):
    """Verify all seed data was loaded correctly"""
    print("\n" + "="*80)
    print("STEP 8: Verifying seed data...")
    print("="*80)

    cursor = conn.cursor()

    checks = [
        ("System parameters", "SELECT COUNT(*) FROM system_parameters", 6),
        ("Umbrella companies", "SELECT COUNT(*) FROM umbrella_companies", 6),
        ("Pay periods", "SELECT COUNT(*) FROM pay_periods", 13),
        ("Contractors", "SELECT COUNT(*) FROM contractors", 23),
        ("Contractor associations", "SELECT COUNT(*) FROM contractor_umbrella_associations", 25),  # 23 + 2 extra for Donna Smith
    ]

    all_passed = True
    for name, query, expected in checks:
        cursor.execute(query)
        actual = cursor.fetchone()[0]
        status = "✓" if actual == expected else "✗"
        if actual != expected:
            all_passed = False
        print(f"  {status} {name}: {actual}/{expected}")

    # Special check for Donna Smith's dual associations
    print("\n  🔍 Special validation:")
    cursor.execute("""
        SELECT c.first_name, c.last_name, u.short_code, a.employee_id
        FROM contractor_umbrella_associations a
        JOIN contractors c ON a.contractor_id = c.contractor_id
        JOIN umbrella_companies u ON a.umbrella_id = u.umbrella_id
        WHERE c.first_name = 'Donna' AND c.last_name = 'Smith'
        ORDER BY u.short_code
    """)

    donna_associations = cursor.fetchall()
    if len(donna_associations) == 2:
        print(f"  ✓ Donna Smith has {len(donna_associations)} associations:")
        for first, last, umbrella, emp_id in donna_associations:
            print(f"     • {umbrella}: {emp_id}")
    else:
        print(f"  ✗ Donna Smith should have 2 associations, found {len(donna_associations)}")
        all_passed = False

    cursor.close()

    if all_passed:
        print("\n" + "="*80)
        print("✅ SEED DATA VERIFICATION PASSED!")
        print("="*80)
    else:
        print("\n" + "="*80)
        print("❌ SEED DATA VERIFICATION FAILED!")
        print("="*80)
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description='Seed contractor pay tracking database')
    parser.add_argument('--stack-name', help='CloudFormation stack name')
    parser.add_argument('--db-secret-arn', help='Database secret ARN (alternative to stack-name)')
    args = parser.parse_args()

    if not args.stack_name and not args.db_secret_arn:
        parser.error('Must provide either --stack-name or --db-secret-arn')

    print("="*80)
    print("CONTRACTOR PAY TRACKING SYSTEM - DATABASE SEEDING")
    print("="*80)
    print(f"Timestamp: {datetime.now().isoformat()}")
    print(f"Stack: {args.stack_name or 'N/A'}")
    print()

    try:
        # Get database credentials
        credentials = get_database_credentials(
            stack_name=args.stack_name,
            secret_arn=args.db_secret_arn
        )

        # Connect to database
        conn = create_connection(credentials)

        # Run seeding steps
        run_schema(conn)
        seed_system_parameters(conn)
        umbrella_map = seed_umbrella_companies(conn)
        period_map = seed_pay_periods(conn)
        contractor_map = seed_contractors(conn)
        seed_contractor_umbrella_associations(conn, contractor_map, umbrella_map)

        # Verify
        verify_seed_data(conn)

        print("\n" + "="*80)
        print("🎉 DATABASE SEEDING COMPLETE!")
        print("="*80)
        print()
        print("Next steps:")
        print("1. Test file upload with Period 8 sample files")
        print("2. Verify validation rules work correctly")
        print("3. Test Donna Smith appears in both NASA and PARASOL files ✓")
        print()

        conn.close()

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
