#!/usr/bin/env python3
"""
Remove UmbrellaName and ShortCode fields (duplicates of UmbrellaCode)
Keep only UmbrellaCode
"""
import boto3

dynamodb = boto3.resource('dynamodb', region_name='eu-west-2')
table = dynamodb.Table('contractor-pay-umbrellas-development')

print("="*80)
print("Removing UmbrellaName and ShortCode from umbrella table")
print("="*80)

# Scan all items
response = table.scan()
items = response.get('Items', [])

print(f"Found {len(items)} items")

for idx, item in enumerate(items, 1):
    pk = item['PK']
    sk = item['SK']

    remove_parts = []

    if 'UmbrellaName' in item:
        remove_parts.append('UmbrellaName')

    if 'ShortCode' in item:
        remove_parts.append('ShortCode')

    if remove_parts:
        remove_expr = 'REMOVE ' + ', '.join(remove_parts)

        table.update_item(
            Key={'PK': pk, 'SK': sk},
            UpdateExpression=remove_expr
        )

        print(f"  [{idx}/{len(items)}] Removed {', '.join(remove_parts)} from {item.get('UmbrellaCode', pk)}")
    else:
        print(f"  [{idx}/{len(items)}] No fields to remove for {item.get('UmbrellaCode', pk)}")

print("="*80)
print("Removal complete")
print("="*80)
