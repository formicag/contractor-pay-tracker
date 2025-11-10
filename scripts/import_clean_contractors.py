#!/usr/bin/env python3
"""
Clean contractor import - ONE record per contractor, margins validated
"""
import boto3
from decimal import Decimal
from datetime import datetime

AWS_PROFILE = "AdministratorAccess-016164185850"
AWS_REGION = "eu-west-2"
TABLE_NAME = "contractor-pay-development"

session = boto3.Session(profile_name=AWS_PROFILE, region_name=AWS_REGION)
dynamodb = session.resource('dynamodb', region_name=AWS_REGION)
table = dynamodb.Table(TABLE_NAME)

# User's ACTUAL contractor data from spreadsheet (23 unique contractors)
contractors = [
    {"FirstName": "Sheela", "LastName": "Adearig", "Email": "sheela.adearig@virginmedia02.co.uk", "JobTitle": "Lead Solution Designer", "SellRate": Decimal("681.41"), "BuyRate": Decimal("547.51"), "SNOWUnitRate": Decimal("340.7"), "UmbrellaCompany": "PARASOL", "EmployeeID": "2218859", "Title": "Ms", "Customer": "Virgin Media O2"},
    {"FirstName": "Venu", "LastName": "Adluru", "Email": "venu.adluru@virginmedia02.co.uk", "JobTitle": "Reference Engineer", "SellRate": Decimal("500"), "BuyRate": Decimal("425"), "SNOWUnitRate": Decimal("250"), "UmbrellaCompany": "WORKWELL", "EmployeeID": "2215733", "Title": "Mr", "Customer": "Virgin Media O2"},
    {"FirstName": "Julie", "LastName": "Bennett", "Email": "julie.bennett@virginmedia02.co.uk", "JobTitle": "Reference Data Manager", "SellRate": Decimal("480"), "BuyRate": Decimal("415"), "SNOWUnitRate": Decimal("240"), "UmbrellaCompany": "WORKWELL", "EmployeeID": "2223058", "Title": "Ms", "Customer": "Virgin Media O2"},
    {"FirstName": "Neil", "LastName": "Birchett", "Email": "neil.birchett@virginmedia02.co.uk", "JobTitle": "Lead Solution Designer", "SellRate": Decimal("631.77"), "BuyRate": Decimal("503.49"), "SNOWUnitRate": Decimal("315.88"), "UmbrellaCompany": "GIANT", "EmployeeID": "2212356", "Title": "Mr", "Customer": "Virgin Media O2"},
    {"FirstName": "Barry", "LastName": "Breden", "Email": "barry.breden3@virginmedia02.co.uk", "JobTitle": "Solution Designer", "SellRate": Decimal("631.77"), "BuyRate": Decimal("438.43"), "SNOWUnitRate": Decimal("315.88"), "UmbrellaCompany": "NASA", "EmployeeID": "2132046", "Title": "Mr", "Customer": "Virgin Media O2"},
    {"FirstName": "Craig", "LastName": "Conkerton", "Email": "craig.conkerton@virginmedia02.co.uk", "JobTitle": "Senior Reference Engineer", "SellRate": Decimal("361"), "BuyRate": Decimal("300"), "SNOWUnitRate": Decimal("180.5"), "UmbrellaCompany": "WORKWELL", "EmployeeID": "2222656", "Title": "Mr", "Customer": "Virgin Media O2"},
    {"FirstName": "Vijetha", "LastName": "Dayyala", "Email": "vijetha.dayyala@virginmedia02.co.uk", "JobTitle": "Junior Reference Engineer", "SellRate": Decimal("325"), "BuyRate": Decimal("280"), "SNOWUnitRate": Decimal("162.5"), "UmbrellaCompany": "WORKWELL", "EmployeeID": "2224048", "Title": "Ms", "Customer": "Virgin Media O2"},
    {"FirstName": "Diogo", "LastName": "Diogo-Cruz", "Email": "diogo.diogo-cruz@virginmedia02.co.uk", "JobTitle": "Lead Solution Designer", "SellRate": Decimal("681.41"), "BuyRate": Decimal("557.41"), "SNOWUnitRate": Decimal("340.7"), "UmbrellaCompany": "NASA", "EmployeeID": "2221340", "Title": "Mr", "Customer": "Virgin Media O2"},
    {"FirstName": "Matthew", "LastName": "Garretty", "Email": "matthew.garretty@virginmedia02.co.uk", "JobTitle": "Solution Designer", "SellRate": Decimal("631.77"), "BuyRate": Decimal("444.23"), "SNOWUnitRate": Decimal("315.88"), "UmbrellaCompany": "GIANT", "EmployeeID": "2223089", "Title": "Mr", "Customer": "Virgin Media O2"},
    {"FirstName": "David", "LastName": "Hunt", "Email": "david.hunt2@virginmedia02.co.uk", "JobTitle": "Solution Designer", "SellRate": Decimal("631.77"), "BuyRate": Decimal("672.03"), "SNOWUnitRate": Decimal("315.89"), "UmbrellaCompany": "NASA", "EmployeeID": "2158980", "Title": "Mr", "Customer": "Virgin Media O2"},
    {"FirstName": "Kevin", "LastName": "Kayes", "Email": "kevin.kayes1@virginmedia02.co.uk", "JobTitle": "Lead Solution Designer", "SellRate": Decimal("681.41"), "BuyRate": Decimal("544.96"), "SNOWUnitRate": Decimal("340.7"), "UmbrellaCompany": "NASA", "EmployeeID": "2219452", "Title": "Mr", "Customer": "Virgin Media O2"},
    {"FirstName": "Chris", "LastName": "Keveney", "Email": "chris.keveney1@virginmedia02.co.uk", "JobTitle": "Senior Reference Data Analyst", "SellRate": Decimal("325"), "BuyRate": Decimal("300"), "SNOWUnitRate": Decimal("162.5"), "UmbrellaCompany": "WORKWELL", "EmployeeID": "2205133", "Title": "Mr", "Customer": "Virgin Media O2"},
    {"FirstName": "Kieran", "LastName": "Maceidan", "Email": "kieran.maceidan@tesco.com", "JobTitle": "Solution Designer", "SellRate": Decimal("700"), "BuyRate": Decimal("600"), "SNOWUnitRate": Decimal("350"), "UmbrellaCompany": "NASA", "EmployeeID": "2204537", "Title": "Mr", "Customer": "Tesco"},
    {"FirstName": "Parag", "LastName": "Maniar", "Email": "parag.maniar2@virginmedia02.co.uk", "JobTitle": "Lead Solution Designer", "SellRate": Decimal("681.41"), "BuyRate": Decimal("573.59"), "SNOWUnitRate": Decimal("340.7"), "UmbrellaCompany": "PARASOL", "EmployeeID": "2218341", "Title": "Mr", "Customer": "Virgin Media O2"},
    {"FirstName": "Gary", "LastName": "Manifesticas", "Email": "gary.manifesticas@virginmedia02.co.uk", "JobTitle": "Solution Designer", "SellRate": Decimal("699.13"), "BuyRate": Decimal("454.45"), "SNOWUnitRate": Decimal("349.56"), "UmbrellaCompany": "NASA", "EmployeeID": "2222656", "Title": "Mr", "Customer": "Virgin Media O2"},
    {"FirstName": "James", "LastName": "Matthews", "Email": "james.matthews@virginmedia02.co.uk", "JobTitle": "Solution Designer", "SellRate": Decimal("631.77"), "BuyRate": Decimal("490"), "SNOWUnitRate": Decimal("315.88"), "UmbrellaCompany": "NASA", "EmployeeID": "2215037", "Title": "Mr", "Customer": "Virgin Media O2"},
    {"FirstName": "Jonathan", "LastName": "May", "Email": "jonathan.may@virginmedia02.co.uk", "JobTitle": "Lead Solution Designer", "SellRate": Decimal("681.41"), "BuyRate": Decimal("524.48"), "SNOWUnitRate": Decimal("340.7"), "UmbrellaCompany": "PAYSTREAM", "EmployeeID": "2219247", "Title": "Mr", "Customer": "Virgin Media O2"},
    {"FirstName": "Graeme", "LastName": "Oldroyd", "Email": "graeme.oldroyd@virginmedia02.co.uk", "JobTitle": "Lead Solution Designer", "SellRate": Decimal("681.41"), "BuyRate": Decimal("534.96"), "SNOWUnitRate": Decimal("340.7"), "UmbrellaCompany": "PARASOL", "EmployeeID": "2209658", "Title": "Mr", "Customer": "Virgin Media O2"},
    {"FirstName": "Paul", "LastName": "Mach", "Email": "paul.mach@virginmedia02.co.uk", "JobTitle": "Lead Solution Designer", "SellRate": Decimal("681.41"), "BuyRate": Decimal("542.3"), "SNOWUnitRate": Decimal("340.7"), "UmbrellaCompany": "PAYSTREAM", "EmployeeID": "2219247", "Title": "Mr", "Customer": "Virgin Media O2"},
    {"FirstName": "Bassavaraj", "LastName": "Puttanaganiaiah", "Email": "bassavaraj.puttanaganiaiah@tesco.com", "JobTitle": "Solution Designer", "SellRate": Decimal("700"), "BuyRate": Decimal("350"), "SNOWUnitRate": Decimal("350"), "UmbrellaCompany": "PARASOL", "EmployeeID": "2160195", "Title": "Mr", "Customer": "Tesco"},
    {"FirstName": "Donna", "LastName": "Smith", "Email": "donna.smith2@virginmedia02.co.uk", "JobTitle": "Senior Reference Data Analyst", "SellRate": Decimal("325"), "BuyRate": Decimal("290"), "SNOWUnitRate": Decimal("162.5"), "UmbrellaCompany": "WORKWELL", "EmployeeID": "2222960", "Title": "Ms", "Customer": "Virgin Media O2"},
    {"FirstName": "Bikam", "LastName": "Wildimo", "Email": "bikam.wildimo@tesco.com", "JobTitle": "Solution Designer", "SellRate": Decimal("700"), "BuyRate": Decimal("350"), "SNOWUnitRate": Decimal("350"), "UmbrellaCompany": "NASA", "EmployeeID": "2158980", "Title": "Mr", "Customer": "Tesco"},
    {"FirstName": "Richard", "LastName": "Williams", "Email": "richard.williams@virginmedia02.co.uk", "JobTitle": "Solution Designer", "SellRate": Decimal("631.77"), "BuyRate": Decimal("450"), "SNOWUnitRate": Decimal("315.88"), "UmbrellaCompany": "NASA", "EmployeeID": "2209753", "Title": "Mr", "Customer": "Virgin Media O2"},
]

# Get umbrella company IDs
umbrella_map = {}
response = table.scan(FilterExpression=boto3.dynamodb.conditions.Attr('EntityType').eq('Umbrella'))
for item in response['Items']:
    umbrella_map[item['ShortCode']] = item['PK'].replace('UMBRELLA#', '')

print(f"Found {len(umbrella_map)} umbrella companies: {list(umbrella_map.keys())}")

imported = 0
skipped = 0
errors = []

for contractor in contractors:
    try:
        # Calculate margin
        sell_rate = float(contractor['SellRate'])
        buy_rate = float(contractor['BuyRate'])
        margin = sell_rate - buy_rate
        margin_percent = (margin / sell_rate) * 100 if sell_rate > 0 else 0

        # Validate margin
        if margin <= 0:
            print(f"⚠️ WARNING: {contractor['FirstName']} {contractor['LastName']} has margin £{margin:.2f} ({margin_percent:.1f}%)")
            errors.append(f"{contractor['FirstName']} {contractor['LastName']}: Negative margin")
            skipped += 1
            continue

        email = contractor['Email']
        umbrella_code = contractor['UmbrellaCompany']
        umbrella_id = umbrella_map.get(umbrella_code)

        if not umbrella_id:
            print(f"❌ ERROR: Umbrella {umbrella_code} not found for {contractor['FirstName']} {contractor['LastName']}")
            skipped += 1
            continue

        # Create ONE Contractor record per person
        contractor_id = f"CONTRACTOR#{email}"
        timestamp = datetime.utcnow().isoformat() + 'Z'

        item = {
            'PK': contractor_id,
            'SK': 'METADATA',
            'EntityType': 'Contractor',
            'Email': email,
            'FirstName': contractor['FirstName'],
            'LastName': contractor['LastName'],
            'NormalizedName': f"{contractor['FirstName']} {contractor['LastName']}".lower(),
            'JobTitle': contractor['JobTitle'],
            'Title': contractor.get('Title', 'Mr'),
            'SellRate': contractor['SellRate'],
            'BuyRate': contractor['BuyRate'],
            'SNOWUnitRate': contractor['SNOWUnitRate'],
            'Margin': Decimal(str(margin)),
            'MarginPercent': Decimal(str(margin_percent)),
            'UmbrellaCompany': umbrella_code,
            'EmployeeID': contractor['EmployeeID'],
            'Customer': contractor.get('Customer', 'Virgin Media O2'),
            'IsActive': True,
            'Status': 'Active',
            'CreatedAt': timestamp,
            'UpdatedAt': timestamp,
            'GSI1PK': 'CONTRACTORS',
            'GSI1SK': f"{contractor['LastName']}#{contractor['FirstName']}",
            'GSI2PK': f"{contractor['FirstName']} {contractor['LastName']}".lower(),
            'GSI2SK': contractor_id,
        }

        table.put_item(Item=item)

        # Create ContractorUmbrellaAssociation
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

        imported += 1
        print(f"✅ [{imported}/23] {contractor['FirstName']} {contractor['LastName']} - Margin: £{margin:.2f} ({margin_percent:.1f}%)")

    except Exception as e:
        print(f"❌ ERROR importing {contractor['FirstName']} {contractor['LastName']}: {e}")
        errors.append(f"{contractor['FirstName']} {contractor['LastName']}: {e}")
        skipped += 1

print(f"\n{'='*80}")
print(f"✅ Import Complete!")
print(f"{'='*80}")
print(f"Successfully imported: {imported}")
print(f"Skipped: {skipped}")
if errors:
    print(f"\nErrors/Warnings:")
    for error in errors:
        print(f"  - {error}")
print(f"{'='*80}")
