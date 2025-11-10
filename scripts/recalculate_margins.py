#!/usr/bin/env python3
"""
Recalculate Margins for All Existing Contractors

This script scans all contractors in DynamoDB and recalculates their margins
based on their current sell and buy rates. Updates the Margin and MarginPercent
fields in the database.
"""

import boto3
from decimal import Decimal
from datetime import datetime

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


def recalculate_all_margins():
    """
    Scan all contractor METADATA records and recalculate margins
    """
    print(f"\n{'='*80}")
    print(f"🔄 Recalculating Margins for All Contractors")
    print(f"{'='*80}\n")

    # Query DynamoDB for all Contractor METADATA records
    response = table.scan(
        FilterExpression='EntityType = :et AND SK = :sk',
        ExpressionAttributeValues={
            ':et': 'Contractor',
            ':sk': 'METADATA'
        }
    )

    contractors = response.get('Items', [])
    print(f"Found {len(contractors)} contractors\n")

    updated_count = 0
    error_count = 0
    validation_errors = []

    for contractor in contractors:
        try:
            email = contractor.get('Email') or contractor.get('ResourceContactEmail')
            first_name = contractor.get('FirstName', 'Unknown')
            last_name = contractor.get('LastName', 'Unknown')

            sell_rate = contractor.get('SellRate', Decimal('0'))
            buy_rate = contractor.get('BuyRate', Decimal('0'))

            # Convert to Decimal if not already
            if not isinstance(sell_rate, Decimal):
                sell_rate = Decimal(str(sell_rate))
            if not isinstance(buy_rate, Decimal):
                buy_rate = Decimal(str(buy_rate))

            # Calculate margin
            try:
                margin, margin_percent = calculate_margin(sell_rate, buy_rate)

                # Update the contractor record
                table.update_item(
                    Key={
                        'PK': contractor['PK'],
                        'SK': 'METADATA'
                    },
                    UpdateExpression='SET #Margin = :margin, #MarginPercent = :margin_percent, #UpdatedAt = :updated_at',
                    ExpressionAttributeNames={
                        '#Margin': 'Margin',
                        '#MarginPercent': 'MarginPercent',
                        '#UpdatedAt': 'UpdatedAt'
                    },
                    ExpressionAttributeValues={
                        ':margin': margin,
                        ':margin_percent': margin_percent,
                        ':updated_at': datetime.now().isoformat()
                    }
                )

                updated_count += 1
                print(f"✅ [{updated_count}/{len(contractors)}] Updated: {first_name} {last_name}")
                print(f"   Sell: £{sell_rate}, Buy: £{buy_rate}, Margin: £{margin} ({margin_percent:.1f}%)\n")

            except ValueError as e:
                error_msg = f"{first_name} {last_name} ({email}): {str(e)}"
                validation_errors.append(error_msg)
                print(f"⚠️  VALIDATION ERROR: {error_msg}\n")
                error_count += 1

        except Exception as e:
            print(f"❌ Error processing {contractor.get('Email', 'Unknown')}: {str(e)}\n")
            error_count += 1

    print(f"\n{'='*80}")
    print(f"✅ Margin Recalculation Complete!")
    print(f"{'='*80}")
    print(f"Successfully updated: {updated_count}")
    print(f"Errors: {error_count}")

    if validation_errors:
        print(f"\n⚠️  VALIDATION ERRORS FOUND:")
        print(f"{'='*80}")
        for error in validation_errors:
            print(f"  • {error}")
        print(f"\nThese contractors have zero or negative margins and need attention!")

    print(f"{'='*80}\n")

    return updated_count, error_count


if __name__ == "__main__":
    print(f"\n🚀 Starting Margin Recalculation Script")
    print(f"📅 Timestamp: {datetime.now().isoformat()}")
    print(f"🗄️  Table: {TABLE_NAME}")
    print(f"🌍 Region: {AWS_REGION}\n")

    updated, errors = recalculate_all_margins()

    print(f"💡 Next Steps:")
    print(f"  1. Check Flask app: http://localhost:5556/contractors")
    print(f"  2. Verify all margins are displaying correctly")
    print(f"  3. Look for warning icons (⚠️) on contractors with margin issues")
    print(f"\n📊 Summary: {updated} updated, {errors} errors\n")
