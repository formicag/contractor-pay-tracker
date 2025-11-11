#!/usr/bin/env python3
"""
Remove Supplier field from permanent staff table
"""
import boto3

dynamodb = boto3.resource('dynamodb', region_name='eu-west-2')
table = dynamodb.Table('contractor-pay-permstaff-development')

print("="*80)
print("Removing Supplier field from permanent staff table")
print("="*80)

# Scan all items
response = table.scan()
items = response.get('Items', [])

print(f"Found {len(items)} items")

for idx, item in enumerate(items, 1):
    pk = item['PK']
    sk = item['SK']

    if 'Supplier' in item:
        table.update_item(
            Key={'PK': pk, 'SK': sk},
            UpdateExpression='REMOVE Supplier'
        )
        print(f"  [{idx}/{len(items)}] Removed Supplier from {item.get('FullName', pk)}")
    else:
        print(f"  [{idx}/{len(items)}] No Supplier field for {item.get('FullName', pk)}")

print("="*80)
print("Supplier field removal complete")
print("="*80)
