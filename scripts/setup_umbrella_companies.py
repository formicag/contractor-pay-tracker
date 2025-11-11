#!/usr/bin/env python3
"""
Setup Umbrella Companies - Password Protected Reference Data
This script adds the 6 umbrella companies to DynamoDB with password protection.

SECURITY: These records are LOCKED and can only be modified with password "luca"
"""

import boto3
import bcrypt
import json
from datetime import datetime
from decimal import Decimal

# AWS Configuration
AWS_REGION = 'eu-west-1'
TABLE_NAME = 'contractor-pay-files-metadata'

# Password for unlocking (bcrypt hashed)
UNLOCK_PASSWORD = 'luca'

# Umbrella companies data
UMBRELLA_COMPANIES = [
    {
        'id': 'nasa-umbrella',
        'trading_name': 'Nasa Group',
        'legal_name': 'Nasa Umbrella Ltd',
        'company_number': '06836385',
        'vat_number': 'GB971214923',
        'registered_address': '5th Floor, Blok 1 Castle Park, Bristol BS2 0JA'
    },
    {
        'id': 'jsa-workwell',
        'trading_name': 'Workwell',
        'legal_name': 'JSA Services Ltd (trading as Workwell)',
        'company_number': '02407547',
        'vat_number': '505587830',
        'registered_address': '51 Clarendon Road, Watford, Hertfordshire WD17 1HP'
    },
    {
        'id': 'parasol-group',
        'trading_name': 'Parasol Group',
        'legal_name': 'Parasol Group Ltd',
        'company_number': '15030534',
        'vat_number': '',  # Not found publicly
        'registered_address': '5 Bensbury Close, London SW15 3TB'
    },
    {
        'id': 'clarity-umbrella',
        'trading_name': 'Clarity Umbrella',
        'legal_name': 'Clarity Umbrella Ltd',
        'company_number': '12210720',
        'vat_number': 'GB332863792',
        'registered_address': '2 Appletree Barns, Folly Lane, Copdock, Ipswich, Suffolk IP8 3JQ'
    },
    {
        'id': 'paystream-mymax',
        'trading_name': 'PayStream My Max',
        'legal_name': 'PayStream My Max Limited',
        'company_number': '06042225',
        'vat_number': 'GB945787073',
        'registered_address': 'Mansion House, Manchester Road, Altrincham, Greater Manchester WA14 4RW'
    },
    {
        'id': 'giant-umbrella',
        'trading_name': 'Giant Umbrella',
        'legal_name': 'Giant Umbrella Limited',
        'company_number': '14016400',
        'vat_number': 'GB448623375',
        'registered_address': '4 Carlton Grove, Bradford, England BD5 7PB'
    }
]


def hash_password(password: str) -> str:
    """Hash password using bcrypt."""
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')


def insert_umbrella_companies():
    """Insert umbrella companies into DynamoDB with password protection."""

    # Initialize DynamoDB
    dynamodb = boto3.resource('dynamodb', region_name=AWS_REGION)
    table = dynamodb.Table(TABLE_NAME)

    # Hash the unlock password
    password_hash = hash_password(UNLOCK_PASSWORD)

    print("=" * 80)
    print("UMBRELLA COMPANIES - PASSWORD PROTECTED REFERENCE DATA")
    print("=" * 80)
    print()
    print("⚠️  WARNING: This data will be LOCKED with password protection")
    print("⚠️  Password required to modify: ****")
    print()

    # Current timestamp
    from datetime import timezone
    created_at = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
    created_by = 'setup_script'

    success_count = 0

    for company in UMBRELLA_COMPANIES:
        try:
            # Build DynamoDB item
            item = {
                'file_id': f"UMBRELLA#{company['id']}",
                'entity_type': 'umbrella_company',
                'company_id': company['id'],
                'trading_name': company['trading_name'],
                'legal_name': company['legal_name'],
                'company_number': company['company_number'],
                'vat_number': company['vat_number'],
                'registered_address': company['registered_address'],

                # Lock metadata
                'locked': True,
                'password_hash': password_hash,

                # Audit trail
                'created_at': created_at,
                'created_by': created_by,
                'modified_at': created_at,
                'modified_by': created_by,
                'version': 1
            }

            # Insert with condition - only if doesn't exist
            table.put_item(
                Item=item,
                ConditionExpression='attribute_not_exists(file_id)'
            )

            print(f"✅ {company['trading_name']} ({company['legal_name']})")
            print(f"   Company #: {company['company_number']}")
            print(f"   VAT #: {company['vat_number'] or 'N/A'}")
            print(f"   Address: {company['registered_address']}")
            print(f"   🔒 LOCKED")
            print()

            success_count += 1

        except dynamodb.meta.client.exceptions.ConditionalCheckFailedException:
            print(f"⚠️  {company['trading_name']} - Already exists (skipping)")
            print()
        except Exception as e:
            print(f"❌ {company['trading_name']} - Error: {str(e)}")
            print()

    print("=" * 80)
    print(f"Completed: {success_count}/{len(UMBRELLA_COMPANIES)} companies inserted")
    print("=" * 80)
    print()
    print("🔒 All records are LOCKED with password protection")
    print("🔑 Unlock password: luca")
    print()


def verify_password(password: str, password_hash: str) -> bool:
    """Verify password against hash."""
    return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))


def list_umbrella_companies():
    """List all umbrella companies in the database."""

    # Initialize DynamoDB
    dynamodb = boto3.resource('dynamodb', region_name=AWS_REGION)
    table = dynamodb.Table(TABLE_NAME)

    print()
    print("=" * 80)
    print("REGISTERED UMBRELLA COMPANIES")
    print("=" * 80)
    print()

    # Scan for umbrella companies (file_id starts with UMBRELLA#)
    response = table.scan(
        FilterExpression='begins_with(file_id, :prefix)',
        ExpressionAttributeValues={
            ':prefix': 'UMBRELLA#'
        }
    )

    companies = response.get('Items', [])

    if not companies:
        print("No umbrella companies found in database.")
        print()
        return

    for i, company in enumerate(companies, 1):
        print(f"{i}. {company.get('trading_name', 'N/A')}")
        print(f"   Legal Name: {company.get('legal_name', 'N/A')}")
        print(f"   Company #: {company.get('company_number', 'N/A')}")
        print(f"   VAT #: {company.get('vat_number', 'N/A')}")
        print(f"   Address: {company.get('registered_address', 'N/A')}")
        print(f"   Status: {'🔒 LOCKED' if company.get('locked') else '🔓 Unlocked'}")
        print(f"   Created: {company.get('created_at', 'N/A')}")
        print()

    print(f"Total: {len(companies)} umbrella companies")
    print("=" * 80)
    print()


if __name__ == '__main__':
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == 'list':
        list_umbrella_companies()
    else:
        insert_umbrella_companies()
        print()
        print("To verify the data was inserted, run:")
        print(f"  python3 {sys.argv[0]} list")
        print()
