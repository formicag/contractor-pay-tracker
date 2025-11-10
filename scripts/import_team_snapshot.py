#!/usr/bin/env python3
"""
Team Roster Snapshot Import Script

Imports team roster data with snapshot metadata for tracking changes over time.
Supports multiple snapshots to track headcount, rate changes, etc.
"""

import boto3
import json
import sys
from datetime import datetime
from decimal import Decimal

# Configuration
AWS_PROFILE = "AdministratorAccess-016164185850"
AWS_REGION = "eu-west-2"
TABLE_NAME = "contractor-pay-development"

# Initialize clients
session = boto3.Session(profile_name=AWS_PROFILE, region_name=AWS_REGION)
dynamodb = session.resource('dynamodb')
table = dynamodb.Table(TABLE_NAME)

def calculate_margin(sell_rate, buy_rate):
    """
    Calculate margin and margin percentage

    Args:
        sell_rate: Sell rate (Decimal)
        buy_rate: Buy rate (Decimal)

    Returns:
        tuple: (margin, margin_percent)

    Raises:
        ValueError: If margin would be zero or negative
    """
    if sell_rate <= buy_rate:
        raise ValueError(f"Sell Rate (£{sell_rate}) must be greater than Buy Rate (£{buy_rate}). Margin cannot be zero or negative.")

    margin = sell_rate - buy_rate
    margin_percent = (margin / sell_rate) * Decimal('100')
    return margin, margin_percent


def import_team_snapshot(team_data, snapshot_date=None, snapshot_version=None):
    """
    Import team roster with snapshot metadata.

    Args:
        team_data: List of contractor dictionaries
        snapshot_date: ISO format date (defaults to today)
        snapshot_version: Version string (defaults to auto-increment)
    """

    if not snapshot_date:
        snapshot_date = datetime.now().isoformat()

    if not snapshot_version:
        # Auto-generate version from date
        snapshot_version = datetime.now().strftime("v%Y%m%d_%H%M%S")

    print(f"\n{'='*80}")
    print(f"📊 Team Roster Snapshot Import")
    print(f"{'='*80}")
    print(f"Snapshot Date: {snapshot_date}")
    print(f"Snapshot Version: {snapshot_version}")
    print(f"Total Contractors: {len(team_data)}")
    print(f"{'='*80}\n")

    imported_count = 0
    error_count = 0
    validation_errors = []

    for contractor in team_data:
        try:
            # Generate contractor ID from email
            email = contractor['ResourceContactEmail']
            contractor_id = f"CONTRACTOR#{email}"

            # Convert rates to Decimal for DynamoDB
            buy_rate = Decimal(str(contractor.get('BuyRate', 0)))
            sell_rate = Decimal(str(contractor.get('SellRate', 0)))
            snow_unit_rate = Decimal(str(contractor.get('SNOWUnitRate', 0)))

            # Calculate and validate margin
            try:
                margin, margin_percent = calculate_margin(sell_rate, buy_rate)
            except ValueError as e:
                error_msg = f"{contractor['FirstName']} {contractor['LastName']}: {str(e)}"
                validation_errors.append(error_msg)
                print(f"⚠️  VALIDATION ERROR: {error_msg}")
                error_count += 1
                continue

            # Prepare item for DynamoDB
            item = {
                'PK': contractor_id,
                'SK': f"SNAPSHOT#{snapshot_version}",
                'EntityType': 'ContractorSnapshot',
                'SnapshotDate': snapshot_date,
                'SnapshotVersion': snapshot_version,

                # Personal Info
                'FirstName': contractor['FirstName'],
                'LastName': contractor['LastName'],
                'Title': contractor.get('Title', ''),

                # Contact Info
                'ResourceContactEmail': email,
                'NasstarEmail': contractor.get('NasstarEmail', ''),
                'LineManagerEmail': contractor.get('LineManagerEmail', ''),

                # Employment Details
                'JobTitle': contractor['JobTitle'],
                'EmployeeID': contractor.get('EmployeeID', ''),
                'EngagementType': contractor.get('EngagementType', 'PAYE'),
                'UmbrellaCompany': contractor['UmbrellaCompany'],

                # SNOW Details
                'SNOWProductOffering': contractor.get('SNOWProductOffering', ''),

                # Financial Details
                'BuyRate': buy_rate,
                'SellRate': sell_rate,
                'SNOWUnitRate': snow_unit_rate,
                'Margin': margin,
                'MarginPercent': margin_percent,

                # Metadata
                'Customer': contractor.get('Customer', ''),
                'ImportedAt': datetime.now().isoformat(),
            }

            # Write to DynamoDB
            table.put_item(Item=item)

            imported_count += 1
            print(f"✅ [{imported_count}/{len(team_data)}] Imported: {contractor['FirstName']} {contractor['LastName']} ({contractor['UmbrellaCompany']})")

        except Exception as e:
            error_count += 1
            print(f"❌ Error importing {contractor.get('FirstName', 'Unknown')}: {str(e)}")

    print(f"\n{'='*80}")
    print(f"✅ Import Complete!")
    print(f"{'='*80}")
    print(f"Successfully imported: {imported_count}")
    print(f"Errors: {error_count}")
    print(f"{'='*80}\n")

    return imported_count, error_count


def create_current_contractor_records(team_data):
    """
    Create/update current contractor records (without snapshot versioning).
    This maintains a single "current state" record for each contractor.
    """
    print(f"\n{'='*80}")
    print(f"📋 Creating Current Contractor Records")
    print(f"{'='*80}\n")

    updated_count = 0
    error_count = 0

    for contractor in team_data:
        try:
            email = contractor['ResourceContactEmail']
            contractor_id = f"CONTRACTOR#{email}"

            # Convert rates to Decimal
            buy_rate = Decimal(str(contractor.get('BuyRate', 0)))
            sell_rate = Decimal(str(contractor.get('SellRate', 0)))
            snow_unit_rate = Decimal(str(contractor.get('SNOWUnitRate', 0)))

            # Calculate and validate margin
            try:
                margin, margin_percent = calculate_margin(sell_rate, buy_rate)
            except ValueError as e:
                error_msg = f"{contractor['FirstName']} {contractor['LastName']}: {str(e)}"
                print(f"⚠️  VALIDATION ERROR: {error_msg}")
                error_count += 1
                continue

            # Prepare current state item
            item = {
                'PK': contractor_id,
                'SK': 'METADATA',
                'EntityType': 'Contractor',

                # Personal Info
                'FirstName': contractor['FirstName'],
                'LastName': contractor['LastName'],
                'Title': contractor.get('Title', ''),
                'FullName': f"{contractor['FirstName']} {contractor['LastName']}",

                # Contact Info
                'ResourceContactEmail': email,
                'NasstarEmail': contractor.get('NasstarEmail', ''),
                'LineManagerEmail': contractor.get('LineManagerEmail', ''),

                # Employment Details
                'JobTitle': contractor['JobTitle'],
                'EmployeeID': contractor.get('EmployeeID', ''),
                'EngagementType': contractor.get('EngagementType', 'PAYE'),
                'UmbrellaCompany': contractor['UmbrellaCompany'],

                # SNOW Details
                'SNOWProductOffering': contractor.get('SNOWProductOffering', ''),

                # Financial Details
                'BuyRate': buy_rate,
                'SellRate': sell_rate,
                'SNOWUnitRate': snow_unit_rate,
                'Margin': margin,
                'MarginPercent': margin_percent,

                # Metadata
                'Customer': contractor.get('Customer', ''),
                'Status': 'ACTIVE',
                'UpdatedAt': datetime.now().isoformat(),
            }

            table.put_item(Item=item)

            updated_count += 1
            print(f"✅ [{updated_count}/{len(team_data)}] Updated: {contractor['FirstName']} {contractor['LastName']}")

        except Exception as e:
            error_count += 1
            print(f"❌ Error updating {contractor.get('FirstName', 'Unknown')}: {str(e)}")

    print(f"\n{'='*80}")
    print(f"✅ Current Records Updated!")
    print(f"{'='*80}")
    print(f"Successfully updated: {updated_count}")
    print(f"Errors: {error_count}")
    print(f"{'='*80}\n")

    return updated_count, error_count


if __name__ == "__main__":
    # Team roster data extracted from the table
    TEAM_ROSTER = [
        {
            "Customer": "Tesco Mobile",
            "Title": "Mr.",
            "FirstName": "Kieran",
            "LastName": "Maceidan",
            "ResourceContactEmail": "kieran.maceidan@tesco.com",
            "NasstarEmail": "Duncan.Maceidan@nasstar.com",
            "JobTitle": "Solution Designer",
            "SNOWProductOffering": "Lead Solution Designer - 0.5 Day",
            "BuyRate": 350.00,
            "SellRate": 700.00,
            "LineManagerEmail": "errol.raguaram@tesco.com",
            "EngagementType": "Umbrella Company (PAYE)",
            "SNOWUnitRate": 350.00,
            "UmbrellaCompany": "NASA",
            "EmployeeID": "846384"
        },
        {
            "Customer": "Tesco Mobile",
            "Title": "Mr.",
            "FirstName": "Bassavaraj",
            "LastName": "Puttanaganiaiah",
            "ResourceContactEmail": "Bassavaraj.Puttanaganiaiah@tesco.com",
            "NasstarEmail": "Bas.Puttanaganiaiah@nasstar.com",
            "JobTitle": "Solution Designer",
            "SNOWProductOffering": "Lead Solution Designer - 0.5 Day",
            "BuyRate": 350.00,
            "SellRate": 700.00,
            "LineManagerEmail": "peter.jugurnath@tesco.com",
            "EngagementType": "Umbrella Company (PAYE)",
            "SNOWUnitRate": 350.00,
            "UmbrellaCompany": "Paystream",
            "EmployeeID": "3936922"
        },
        {
            "Customer": "Tesco Mobile",
            "Title": "Mr.",
            "FirstName": "Bikam",
            "LastName": "Wildimo",
            "ResourceContactEmail": "bikam.wildimo@tesco.com",
            "NasstarEmail": "Bikam.Wildimo@nasstar.com",
            "JobTitle": "Solution Designer",
            "SNOWProductOffering": "Solution Architect (EN-SE) 0.5 Day",
            "BuyRate": 350.00,
            "SellRate": 700.00,
            "LineManagerEmail": "peter.jugurnath@tesco.com",
            "EngagementType": "Umbrella Company (PAYE)",
            "SNOWUnitRate": 350.00,
            "UmbrellaCompany": "NASA",
            "EmployeeID": "841360"
        },
        {
            "Customer": "WM02",
            "Title": "Mr",
            "FirstName": "David",
            "LastName": "Hunt",
            "ResourceContactEmail": "David.Hunt2@virginmedia02.co.uk",
            "NasstarEmail": "David.Hunt@GCIonline.microsoft.com",
            "JobTitle": "Solution Designer",
            "SNOWProductOffering": "O2 Solution Designer (EN-SE) 0.5 Day",
            "BuyRate": 315.89,
            "SellRate": 631.77,
            "LineManagerEmail": "john.pete@virginmedia02.co.uk",
            "EngagementType": "Umbrella Company (PAYE)",
            "SNOWUnitRate": 672.03,
            "UmbrellaCompany": "NASA",
            "EmployeeID": "812277"
        },
        {
            "Customer": "WM02",
            "Title": "Mr",
            "FirstName": "Diego",
            "LastName": "Diego-Cruz",
            "ResourceContactEmail": "Diego.Diego-Cruz@virginmedia02.co.uk",
            "NasstarEmail": "Diego.Diego-Cruz@nasstar.com",
            "JobTitle": "Lead Solution Designer",
            "SNOWProductOffering": "O2 Lead Solution Designer (EN-SE) 0.5 Day",
            "BuyRate": 340.70,
            "SellRate": 681.41,
            "LineManagerEmail": "Tracy.farley@telefonics.com",
            "EngagementType": "Umbrella Company (PAYE)",
            "SNOWUnitRate": 557.41,
            "UmbrellaCompany": "NASA",
            "EmployeeID": "808042"
        },
        {
            "Customer": "WM02",
            "Title": "Mr",
            "FirstName": "Graeme",
            "LastName": "Oldroyd",
            "ResourceContactEmail": "Graeme.Oldroyd@virginmedia02.co.uk",
            "NasstarEmail": "Graeme.Oldroyd@nasstar.com",
            "JobTitle": "Lead Solution Designer",
            "SNOWProductOffering": "O2 Lead Solution Designer (EN-SE) 0.5 Day",
            "BuyRate": 340.70,
            "SellRate": 681.41,
            "LineManagerEmail": "Barbara.Hall@telefonics.com",
            "EngagementType": "Umbrella Company (PAYE)",
            "SNOWUnitRate": 534.96,
            "UmbrellaCompany": "Paystream",
            "EmployeeID": "3860377"
        },
        {
            "Customer": "WM02",
            "Title": "Mr",
            "FirstName": "Jonathan",
            "LastName": "May",
            "ResourceContactEmail": "Jonathan.May@virginmedia02.co.uk",
            "NasstarEmail": "Jonathan.May@nasstar.com",
            "JobTitle": "Lead Solution Designer",
            "SNOWProductOffering": "O2 Lead Solution Designer (EN-SE) 0.5 Day",
            "BuyRate": 340.70,
            "SellRate": 681.41,
            "LineManagerEmail": "james.concepcion@virginmedia02.co.uk",
            "EngagementType": "Umbrella Company (PAYE)",
            "SNOWUnitRate": 524.48,
            "UmbrellaCompany": "Clarity",
            "EmployeeID": "445288"
        },
        {
            "Customer": "WM02",
            "Title": "Mr",
            "FirstName": "Kevin",
            "LastName": "Kayes",
            "ResourceContactEmail": "Kevin.Kayes1@virginmedia02.co.uk",
            "NasstarEmail": "Kevin.Kayes@nasstar.com",
            "JobTitle": "Lead Solution Designer",
            "SNOWProductOffering": "O2 Solution Designer (EN-SE) 0.5 Day",
            "BuyRate": 340.70,
            "SellRate": 681.41,
            "LineManagerEmail": "Tracy.farley@telefonics.com",
            "EngagementType": "Umbrella Company (PAYE)",
            "SNOWUnitRate": 544.96,
            "UmbrellaCompany": "NASA",
            "EmployeeID": "814829"
        },
        {
            "Customer": "WM02",
            "Title": "Mr",
            "FirstName": "Neil",
            "LastName": "Birchett",
            "ResourceContactEmail": "Neil.Birchett@virginmedia02.co.uk",
            "NasstarEmail": "Neil.Diemer@telefonics.com",
            "JobTitle": "Lead Solution Designer",
            "SNOWProductOffering": "O2 Solution Designer (EN-SE) 0.5 Day",
            "BuyRate": 315.88,
            "SellRate": 631.77,
            "LineManagerEmail": "Rajinder.Birch@virginmedia02.co.uk",
            "EngagementType": "Umbrella Company (PAYE)",
            "SNOWUnitRate": 503.49,
            "UmbrellaCompany": "Workwell",
            "EmployeeID": "2223089"
        },
        {
            "Customer": "WM02",
            "Title": "Mr",
            "FirstName": "Parag",
            "LastName": "Maniar",
            "ResourceContactEmail": "Parag.Maniar2@virginmedia02.co.uk",
            "NasstarEmail": "parag.maniar@nasstar.com",
            "JobTitle": "Lead Solution Designer",
            "SNOWProductOffering": "O2 Lead Solution Designer (EN-SE) 0.5 Day",
            "BuyRate": 340.70,
            "SellRate": 681.41,
            "LineManagerEmail": "Tracy.farley@telefonics.com",
            "EngagementType": "Umbrella Company (PAYE)",
            "SNOWUnitRate": 573.59,
            "UmbrellaCompany": "Paystream",
            "EmployeeID": "3886353"
        },
        {
            "Customer": "WM02",
            "Title": "Mr",
            "FirstName": "Paul",
            "LastName": "Mach",
            "ResourceContactEmail": "Paul.Mach@virginmedia02.co.uk",
            "NasstarEmail": "Paul.Mach@nasstar.com",
            "JobTitle": "Lead Solution Designer",
            "SNOWProductOffering": "O2 Lead Solution Designer (EN-SE) 0.5 Day",
            "BuyRate": 340.70,
            "SellRate": 681.41,
            "LineManagerEmail": "jonathan.tlali@telefonics.com",
            "EngagementType": "Umbrella Company (PAYE)",
            "SNOWUnitRate": 542.30,
            "UmbrellaCompany": "Clarity",
            "EmployeeID": "445308"
        },
        {
            "Customer": "WM02",
            "Title": "Ms",
            "FirstName": "Sheela",
            "LastName": "Adearig",
            "ResourceContactEmail": "Sheela.Adearig@virginmedia02.co.uk",
            "NasstarEmail": "Sheela.Adearig@nasstar.com",
            "JobTitle": "Lead Solution Designer",
            "SNOWProductOffering": "O2 Lead Solution Designer (EN-SE) 0.5 Day",
            "BuyRate": 340.70,
            "SellRate": 681.41,
            "LineManagerEmail": "Tracy.farley@telefonics.com",
            "EngagementType": "Umbrella Company (PAYE)",
            "SNOWUnitRate": 547.51,
            "UmbrellaCompany": "Paystream",
            "EmployeeID": "3861472"
        },
        {
            "Customer": "WM02",
            "Title": "Mr",
            "FirstName": "Gary",
            "LastName": "Manifesticas",
            "ResourceContactEmail": "Gary.Manifesticas@virginmedia02.co.uk",
            "NasstarEmail": "Gary.Manifesticas@nasstar.com",
            "JobTitle": "Solution Designer",
            "SNOWProductOffering": "Solution Architect (EN-SE) 0.5 Day",
            "BuyRate": 349.56,
            "SellRate": 699.13,
            "LineManagerEmail": "neil.pidgett@virginmedia02.co.uk",
            "EngagementType": "Umbrella Company (PAYE)",
            "SNOWUnitRate": 454.45,
            "UmbrellaCompany": "NASA",
            "EmployeeID": "3879216"
        },
        {
            "Customer": "WM02",
            "Title": "Mr",
            "FirstName": "Barry",
            "LastName": "Breden",
            "ResourceContactEmail": "Barry.Breden3@virginmedia02.co.uk",
            "NasstarEmail": "Barry.Breden@nasstar.com",
            "JobTitle": "Solution Designer",
            "SNOWProductOffering": "Solution Architect (EN-SE) 0.5 Day",
            "BuyRate": 315.88,
            "SellRate": 631.77,
            "LineManagerEmail": "Tracy.farley@telefonics.com",
            "EngagementType": "Umbrella Company (PAYE)",
            "SNOWUnitRate": 438.43,
            "UmbrellaCompany": "NASA",
            "EmployeeID": "825675"
        },
        {
            "Customer": "WM02",
            "Title": "Mr",
            "FirstName": "Chris",
            "LastName": "Keveney",
            "ResourceContactEmail": "chris.keveney1@virginmedia02.co.uk",
            "NasstarEmail": "Chris.Keveney@nasstar.com",
            "JobTitle": "Senior Reference Data Analyst",
            "SNOWProductOffering": "Senior Reference Data Analyst (EN-SE) O2 0.5 Day",
            "BuyRate": 162.50,
            "SellRate": 325.00,
            "LineManagerEmail": "kevin.mayhew@virginmedia02.co.uk",
            "EngagementType": "Umbrella Company (PAYE)",
            "SNOWUnitRate": 300.00,
            "UmbrellaCompany": "PARASOL",
            "EmployeeID": "104877"
        },
        {
            "Customer": "WM02",
            "Title": "Mr",
            "FirstName": "Craig",
            "LastName": "Conkerton",
            "ResourceContactEmail": "craig.conkerton@virginmedia02.co.uk",
            "NasstarEmail": "Craig.Conkerton@nasstar.com",
            "JobTitle": "Senior Reference Data Analyst",
            "SNOWProductOffering": "Senior Reference Data Analyst (EN-SE) O2 0.5 Day",
            "BuyRate": 180.50,
            "SellRate": 361.00,
            "LineManagerEmail": "kevin.mayhew@virginmedia02.co.uk",
            "EngagementType": "Umbrella Company (PAYE)",
            "SNOWUnitRate": 300.00,
            "UmbrellaCompany": "PARASOL",
            "EmployeeID": "102399"
        },
        {
            "Customer": "WM02",
            "Title": "Ms",
            "FirstName": "Donna",
            "LastName": "Smith",
            "ResourceContactEmail": "Donna.Smith2@virginmedia02.co.uk",
            "NasstarEmail": "Donna.Smith@nasstar.com",
            "JobTitle": "Senior Reference Data Analyst",
            "SNOWProductOffering": "Senior Reference Data Analyst (EN-SE) O2 0.5 Day",
            "BuyRate": 162.50,
            "SellRate": 325.00,
            "LineManagerEmail": "kevin.mayhew@virginmedia02.co.uk",
            "EngagementType": "Umbrella Company (PAYE)",
            "SNOWUnitRate": 290.00,
            "UmbrellaCompany": "PARASOL",
            "EmployeeID": "129700"
        },
        {
            "Customer": "WM02",
            "Title": "Mr",
            "FirstName": "James",
            "LastName": "Matthews",
            "ResourceContactEmail": "james.matthews@virginmedia02.co.uk",
            "NasstarEmail": "James.Matthews@nasstar.com",
            "JobTitle": "Solution Designer",
            "SNOWProductOffering": "Solution Architect (EN-SE) 0.5 Day",
            "BuyRate": 315.88,
            "SellRate": 631.77,
            "LineManagerEmail": "kevin.mayhew@virginmedia02.co.uk",
            "EngagementType": "Umbrella Company (PAYE)",
            "SNOWUnitRate": 490.00,
            "UmbrellaCompany": "NASA",
            "EmployeeID": "829112"
        },
        {
            "Customer": "WM02",
            "Title": "Ms",
            "FirstName": "Julie",
            "LastName": "Bennett",
            "ResourceContactEmail": "Julie.Bennett@virginmedia02.co.uk",
            "NasstarEmail": "Julie.Bennett@nasstar.com",
            "JobTitle": "Reference Data Manager",
            "SNOWProductOffering": "Reference Data Manager (EN-SE) O2 0.5 Day",
            "BuyRate": 240.00,
            "SellRate": 480.00,
            "LineManagerEmail": "kevin.mayhew@virginmedia02.co.uk",
            "EngagementType": "Umbrella Company (PAYE)",
            "SNOWUnitRate": 415.00,
            "UmbrellaCompany": "PARASOL",
            "EmployeeID": "104226"
        },
        {
            "Customer": "WM02",
            "Title": "Mr",
            "FirstName": "Matthew",
            "LastName": "Garretty",
            "ResourceContactEmail": "matthew.garretty@virginmedia02.co.uk",
            "NasstarEmail": "Matthew.Garretty@nasstar.com",
            "JobTitle": "Solution Designer",
            "SNOWProductOffering": "Solution Architect (EN-SE) 0.5 Day",
            "BuyRate": 315.88,
            "SellRate": 631.77,
            "LineManagerEmail": "kevin.mayhew@virginmedia02.co.uk",
            "EngagementType": "Umbrella Company (PAYE)",
            "SNOWUnitRate": 444.23,
            "UmbrellaCompany": "Workwell",
            "EmployeeID": "2158980"
        },
        {
            "Customer": "WM02",
            "Title": "Ms",
            "FirstName": "Richard",
            "LastName": "Williams",
            "ResourceContactEmail": "Richard.Williams@virginmedia02.co.uk",
            "NasstarEmail": "Richard.Williams@nasstar.com",
            "JobTitle": "Solution Designer",
            "SNOWProductOffering": "Solution Architect (EN-SE) 0.5 Day",
            "BuyRate": 315.88,
            "SellRate": 631.77,
            "LineManagerEmail": "kevin.mayhew@virginmedia02.co.uk",
            "EngagementType": "Umbrella Company (PAYE)",
            "SNOWUnitRate": 450.00,
            "UmbrellaCompany": "NASA",
            "EmployeeID": "814233"
        },
        {
            "Customer": "WM02",
            "Title": "Mr",
            "FirstName": "Venu",
            "LastName": "Adluru",
            "ResourceContactEmail": "Venu.Adluru@virginmedia02.co.uk",
            "NasstarEmail": "Venu.Adluru@nasstar.com",
            "JobTitle": "Reference Data Consultant",
            "SNOWProductOffering": "Senior Reference Data Analyst (EN-SE) O2 0.5 Day",
            "BuyRate": 250.00,
            "SellRate": 500.00,
            "LineManagerEmail": "kevin.mayhew@virginmedia02.co.uk",
            "EngagementType": "Umbrella Company (PAYE)",
            "SNOWUnitRate": 425.00,
            "UmbrellaCompany": "PARASOL",
            "EmployeeID": "135433"
        },
        {
            "Customer": "WM02",
            "Title": "Ms",
            "FirstName": "Vijetha",
            "LastName": "Dayaala",
            "ResourceContactEmail": "Vijetha.Dayaala@virginmedia02.co.uk",
            "NasstarEmail": "Vijetha.Dayaala@nasstar.com",
            "JobTitle": "Senior Reference Data Analyst",
            "SNOWProductOffering": "Senior Reference Data Analyst (EN-SE) O2 0.5 Day",
            "BuyRate": 162.50,
            "SellRate": 325.00,
            "LineManagerEmail": "kevin.mayhew@virginmedia02.co.uk",
            "EngagementType": "Umbrella Company (PAYE)",
            "SNOWUnitRate": 280.00,
            "UmbrellaCompany": "PARASOL",
            "EmployeeID": "135278"
        },
    ]

    # Generate snapshot metadata
    snapshot_date = datetime.now().isoformat()
    snapshot_version = datetime.now().strftime("v%Y%m%d_%H%M%S")

    print(f"\n🚀 Starting Team Roster Import")
    print(f"📅 Snapshot Date: {snapshot_date}")
    print(f"🔖 Snapshot Version: {snapshot_version}")
    print(f"👥 Total Contractors: {len(TEAM_ROSTER)}\n")

    # Step 1: Import snapshot data
    snap_success, snap_errors = import_team_snapshot(
        TEAM_ROSTER,
        snapshot_date=snapshot_date,
        snapshot_version=snapshot_version
    )

    # Step 2: Update current contractor records
    curr_success, curr_errors = create_current_contractor_records(TEAM_ROSTER)

    # Final summary
    print(f"\n{'='*80}")
    print(f"🎉 IMPORT COMPLETE!")
    print(f"{'='*80}")
    print(f"Snapshot Records Created: {snap_success}")
    print(f"Current Records Updated: {curr_success}")
    print(f"Total Errors: {snap_errors + curr_errors}")
    print(f"{'='*80}\n")

    print(f"💡 Next Steps:")
    print(f"  1. Check Flask app: http://localhost:5556/contractors")
    print(f"  2. Verify all 24 contractors are visible")
    print(f"  3. Confirm data quality is excellent")
    print(f"\n📊 Snapshot saved as: {snapshot_version}")
    print(f"📅 You can now track changes over time!")
