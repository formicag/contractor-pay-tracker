#!/usr/bin/env python3
"""
Import contractors from HTML Resources Report
- Stores ALL resources (contractors + perm staff)
- Only displays contractors (Engagement Type = "Umbrella Company (PAYE)")
- Perm staff (PAYE on payroll) stored but hidden
"""
import boto3
from bs4 import BeautifulSoup
from decimal import Decimal
from datetime import datetime
import re

AWS_PROFILE = "AdministratorAccess-016164185850"
AWS_REGION = "eu-west-2"
TABLE_NAME = "contractor-pay-development"
HTML_FILE = "/Users/gianlucaformica/Projects/contractor-pay-tracker/Projects/Resources Report.html"

session = boto3.Session(profile_name=AWS_PROFILE, region_name=AWS_REGION)
dynamodb = session.resource('dynamodb', region_name=AWS_REGION)
table = dynamodb.Table(TABLE_NAME)

def parse_currency(value):
    """Parse currency string to Decimal"""
    if not value or value.strip() == '':
        return None
    # Remove £, commas, spaces
    cleaned = re.sub(r'[£,\s]', '', value)
    try:
        return Decimal(cleaned)
    except:
        return None

def parse_percentage(value):
    """Parse percentage string to Decimal"""
    if not value or value.strip() == '':
        return None
    # Remove % sign
    cleaned = value.replace('%', '').strip()
    try:
        return Decimal(cleaned)
    except:
        return None

def generate_email(first_name, last_name, customer):
    """Generate email from name and customer"""
    # Use customer domain logic
    domain_map = {
        'Tesco Mobile': 'tesco.com',
        'Tesco': 'tesco.com',
        'Virgin Media O2': 'virginmediao2.co.uk',
        'DRAX': 'drax.com',
    }

    domain = domain_map.get(customer, 'virginmediao2.co.uk')
    email = f"{first_name.lower()}.{last_name.lower()}@{domain}"
    return email

def parse_boolean(value):
    """Parse Active field to boolean"""
    if not value:
        return False
    return value.strip().lower() in ['yes', 'true', 'active', '1']

# Get umbrella company IDs
print("Loading umbrella companies...")
umbrella_map = {}
response = table.scan(FilterExpression=boto3.dynamodb.conditions.Attr('EntityType').eq('Umbrella'))
for item in response['Items']:
    code = item.get('ShortCode', '')
    umbrella_map[code.upper()] = item['PK'].replace('UMBRELLA#', '')
    # Add variations
    legal_name = item.get('LegalName', '')
    if legal_name:
        umbrella_map[legal_name.upper()] = item['PK'].replace('UMBRELLA#', '')

print(f"Found {len(umbrella_map)} umbrella companies")

# Parse HTML
print(f"\nParsing HTML file: {HTML_FILE}")
with open(HTML_FILE, 'r', encoding='utf-8') as f:
    html = f.read()

soup = BeautifulSoup(html, 'html.parser')
table_elem = soup.find('table')

# Get headers
header_row = table_elem.find('thead').find('tr') if table_elem.find('thead') else table_elem.find('tr')
headers = [th.get_text(strip=True) for th in header_row.find_all(['th', 'td'])]

# Get data rows
tbody = table_elem.find('tbody') if table_elem.find('tbody') else table_elem
rows = tbody.find_all('tr')[1:] if not table_elem.find('thead') else tbody.find_all('tr')

print(f"Found {len(rows)} total resources")

imported_contractors = 0
imported_perm_staff = 0
skipped = 0
errors = []

for row_num, row in enumerate(rows, 1):
    cells = row.find_all(['td', 'th'])

    if len(cells) < len(headers):
        continue

    # Parse row data
    data = {}
    for i, cell in enumerate(cells):
        if i < len(headers):
            data[headers[i]] = cell.get_text(strip=True)

    try:
        # Extract fields
        resource_id = data.get('Resource ID', '')
        first_name = data.get('First Name', '').strip()
        last_name = data.get('Last Name', '').strip()
        engagement_type = data.get('Engagement Type', '').strip()

        if not first_name or not last_name:
            print(f"⚠️  Row {row_num}: Missing name, skipping")
            skipped += 1
            continue

        # Parse rates
        buy_rate = parse_currency(data.get('Buy Rate', ''))
        sell_rate = parse_currency(data.get('Sell Rate', ''))

        # Determine if this is perm staff or contractor
        is_perm_staff = engagement_type == "PAYE (on payroll)"
        is_contractor = "Umbrella" in engagement_type

        # Generate email
        customer = data.get('Customer', 'Virgin Media O2')
        email = generate_email(first_name, last_name, customer)

        # Calculate margin if both rates present
        margin = None
        margin_percent = None
        if sell_rate and buy_rate:
            margin = sell_rate - buy_rate
            if sell_rate > 0:
                margin_percent = (margin / sell_rate) * Decimal('100')

        # Validate margin for contractors only
        if is_contractor and margin is not None and margin <= 0:
            print(f"⚠️  {first_name} {last_name}: Negative margin £{margin}, skipping")
            errors.append(f"{first_name} {last_name}: Negative margin")
            skipped += 1
            continue

        # Map payroll company to umbrella
        payroll_co = data.get('Payroll Co', '').strip().upper()
        umbrella_code = None
        umbrella_id = None

        if payroll_co:
            # Try exact match first
            if payroll_co in umbrella_map:
                umbrella_id = umbrella_map[payroll_co]
            else:
                # Try partial match
                for key, value in umbrella_map.items():
                    if payroll_co in key or key in payroll_co:
                        umbrella_id = value
                        umbrella_code = key
                        break

        # Determine umbrella code from ID
        if umbrella_id and not umbrella_code:
            for code, uid in umbrella_map.items():
                if uid == umbrella_id:
                    umbrella_code = code
                    break

        # Create contractor record
        contractor_id = f"CONTRACTOR#{email}"
        timestamp = datetime.now().isoformat() + 'Z'

        item = {
            'PK': contractor_id,
            'SK': 'METADATA',
            'EntityType': 'Contractor',
            'ResourceID': resource_id,
            'Email': email,
            'FirstName': first_name,
            'LastName': last_name,
            'NormalizedName': f"{first_name} {last_name}".lower(),
            'Title': data.get('Title', 'Mr'),
            'JobTitle': data.get('Job Title', ''),
            'Customer': customer,
            'Agency': data.get('Agency', ''),
            'ProjectName': data.get('Project Name', ''),
            'CostCentre': data.get('Cost Centre', ''),
            'ProjectCode': data.get('Project Code', ''),
            'ContractID': data.get('Contract ID', ''),
            'ContractStartDate': data.get('Start Date', ''),
            'ContractEndDate': data.get('End Date', ''),
            'ContractType': data.get('Contract Type', ''),
            'ContractReference': data.get('Contract ID', ''),
            'SellRate': sell_rate if sell_rate else Decimal('0'),
            'BuyRate': buy_rate if buy_rate else Decimal('0'),
            'Margin': margin if margin else Decimal('0'),
            'MarginPercent': margin_percent if margin_percent else Decimal('0'),
            'SNOWUnitRate': (sell_rate / 2) if sell_rate else Decimal('0'),
            'LineManagerName': data.get('Customer Line Manager', ''),
            'LineManagerEmail': data.get('Customer Manager Email', ''),
            'WorkingLocation': data.get('Location', ''),
            'Country': data.get('Country', 'UK'),
            'EngagementType': engagement_type,
            'Division': data.get('Division', ''),
            'SubContractorCompany': data.get('Subcontractor', ''),
            'UmbrellaCompany': umbrella_code if umbrella_code else payroll_co,
            'TenureOnAccount': data.get('Tenure', ''),
            'IsActive': parse_boolean(data.get('Active', 'Yes')),
            'IsPermanentStaff': is_perm_staff,
            'Status': 'Active' if parse_boolean(data.get('Active', 'Yes')) else 'Inactive',
            'CreatedAt': timestamp,
            'UpdatedAt': timestamp,
            'GSI1PK': 'CONTRACTORS',
            'GSI1SK': f"{last_name}#{first_name}",
            'GSI2PK': f"{first_name} {last_name}".lower(),
            'GSI2SK': contractor_id,
        }

        table.put_item(Item=item)

        # Create umbrella association if umbrella ID found
        if umbrella_id and not is_perm_staff:
            assoc_item = {
                'PK': contractor_id,
                'SK': f"UMBRELLA#{umbrella_id}",
                'EntityType': 'ContractorUmbrellaAssociation',
                'UmbrellaID': f"UMBRELLA#{umbrella_id}",
                'UmbrellaCode': umbrella_code,
                'ContractorID': contractor_id,
                'Email': email,
                'AssociatedAt': timestamp,
                'IsActive': True
            }
            table.put_item(Item=assoc_item)

        # Track what was imported
        if is_perm_staff:
            imported_perm_staff += 1
            print(f"✅ [PERM {imported_perm_staff}] {first_name} {last_name} (hidden from display)")
        else:
            imported_contractors += 1
            if margin:
                print(f"✅ [CONT {imported_contractors}] {first_name} {last_name} - Sell: £{sell_rate}, Buy: £{buy_rate}, Margin: £{margin} ({margin_percent:.1f}%)")
            else:
                print(f"✅ [CONT {imported_contractors}] {first_name} {last_name} - Sell: £{sell_rate}")

    except Exception as e:
        print(f"❌ ERROR Row {row_num} ({first_name} {last_name}): {e}")
        errors.append(f"Row {row_num}: {e}")
        skipped += 1

print(f"\n{'='*80}")
print(f"✅ IMPORT COMPLETE!")
print(f"{'='*80}")
print(f"Contractors imported (DISPLAYED):  {imported_contractors}")
print(f"Perm staff imported (HIDDEN):      {imported_perm_staff}")
print(f"Total imported:                    {imported_contractors + imported_perm_staff}")
print(f"Skipped:                           {skipped}")
if errors:
    print(f"\nErrors/Warnings:")
    for error in errors:
        print(f"  - {error}")
print(f"{'='*80}")
