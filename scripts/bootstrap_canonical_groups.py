#!/usr/bin/env python3
"""
Bootstrap Canonical Customer Groups

Loads initial canonical customer group data from CSV format.
"""

import sys
import os

# Add flask-app to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../flask-app'))

from canonical_groups_manager import canonical_groups_manager

# Unlock password
UNLOCK_PASSWORD = 'luca'

# Canonical entity data (from provided CSV)
CANONICAL_DATA = [
    # Nasstar Group
    {'CanonicalID': 'CG-0001', 'GroupName': 'Nasstar Group', 'LegalEntity': 'Nasstar (UK) Ltd', 'CompanyNo': '03499514', 'Alias': 'Nasstar', 'AliasType': 'Brand', 'StartDate': '2005-01-01', 'EndDate': None, 'Notes': ''},
    {'CanonicalID': 'CG-0001', 'GroupName': 'Nasstar Group', 'LegalEntity': 'Nasstar (UK) Ltd', 'CompanyNo': '03499514', 'Alias': 'Nasstar (UK) Limited', 'AliasType': 'Legal Name', 'StartDate': '2005-01-01', 'EndDate': None, 'Notes': ''},
    {'CanonicalID': 'CG-0001', 'GroupName': 'Nasstar Group', 'LegalEntity': 'Nasstar (UK) Ltd', 'CompanyNo': '03499514', 'Alias': 'Space Internet Ltd', 'AliasType': 'Former Name', 'StartDate': '1998-01-21', 'EndDate': '2000-01-01', 'Notes': ''},
    {'CanonicalID': 'CG-0001', 'GroupName': 'Nasstar Group', 'LegalEntity': 'Nasstar (UK) Ltd', 'CompanyNo': '03499514', 'Alias': 'Space 7 Ltd', 'AliasType': 'Former Name', 'StartDate': '2000-01-01', 'EndDate': '2002-01-01', 'Notes': ''},
    {'CanonicalID': 'CG-0001', 'GroupName': 'Nasstar Group', 'LegalEntity': 'Nasstar (UK) Ltd', 'CompanyNo': '03499514', 'Alias': 'Nasstar Ltd', 'AliasType': 'Former Legal', 'StartDate': '2002-01-01', 'EndDate': '2005-01-01', 'Notes': ''},
    {'CanonicalID': 'CG-0001', 'GroupName': 'Nasstar Group', 'LegalEntity': 'GCI Network Solutions Ltd', 'CompanyNo': '04082862', 'Alias': 'GCI', 'AliasType': 'Brand', 'StartDate': '2000-01-01', 'EndDate': '2021-01-01', 'Notes': 'Merged with Nasstar'},
    {'CanonicalID': 'CG-0001', 'GroupName': 'Nasstar Group', 'LegalEntity': 'Colibri Digital Ltd', 'CompanyNo': '08763735', 'Alias': 'Colibri', 'AliasType': 'Brand', 'StartDate': '2023-02-01', 'EndDate': None, 'Notes': 'Subsidiary'},
    {'CanonicalID': 'CG-0001', 'GroupName': 'Nasstar Group', 'LegalEntity': 'KCOM Group Ltd', 'CompanyNo': '02161326', 'Alias': 'KCOM National', 'AliasType': 'Acquired Unit', 'StartDate': '2021-08-01', 'EndDate': None, 'Notes': 'ICT Services Acquired'},

    # Virgin Media O2 Group
    {'CanonicalID': 'CG-0002', 'GroupName': 'Virgin Media O2 Group', 'LegalEntity': 'VMED O2 UK Ltd', 'CompanyNo': '12580944', 'Alias': 'Virgin Media O2', 'AliasType': 'Canonical Brand', 'StartDate': '2021-06-01', 'EndDate': None, 'Notes': ''},
    {'CanonicalID': 'CG-0002', 'GroupName': 'Virgin Media O2 Group', 'LegalEntity': 'VMED O2 UK Ltd', 'CompanyNo': '12580944', 'Alias': 'O2 UK', 'AliasType': 'Brand', 'StartDate': '2002-01-01', 'EndDate': None, 'Notes': 'Telefónica era'},
    {'CanonicalID': 'CG-0002', 'GroupName': 'Virgin Media O2 Group', 'LegalEntity': 'VMED O2 UK Ltd', 'CompanyNo': '12580944', 'Alias': 'BT Cellnet', 'AliasType': 'Historic', 'StartDate': '1985-01-01', 'EndDate': '2002-01-01', 'Notes': ''},
    {'CanonicalID': 'CG-0002', 'GroupName': 'Virgin Media O2 Group', 'LegalEntity': 'VMED O2 UK Ltd', 'CompanyNo': '12580944', 'Alias': 'Telefónica UK Ltd', 'AliasType': 'Legal Name', 'StartDate': '2006-01-01', 'EndDate': '2021-06-01', 'Notes': ''},
    {'CanonicalID': 'CG-0002', 'GroupName': 'Virgin Media O2 Group', 'LegalEntity': 'VMED O2 UK Ltd', 'CompanyNo': '12580944', 'Alias': 'Virgin Media Business Ltd', 'AliasType': 'Legal Entity', 'StartDate': '2023-08-01', 'EndDate': None, 'Notes': 'New VMOB sub'},
    {'CanonicalID': 'CG-0002', 'GroupName': 'Virgin Media O2 Group', 'LegalEntity': 'VMED O2 UK Ltd', 'CompanyNo': '12580944', 'Alias': 'Virgin Mobile UK', 'AliasType': 'Brand', 'StartDate': '2005-01-01', 'EndDate': None, 'Notes': ''},
    {'CanonicalID': 'CG-0002', 'GroupName': 'Virgin Media O2 Group', 'LegalEntity': 'VMED O2 UK Ltd', 'CompanyNo': '12580944', 'Alias': 'mmO2', 'AliasType': 'Historic', 'StartDate': '2002-01-01', 'EndDate': '2006-01-01', 'Notes': ''},
    {'CanonicalID': 'CG-0002', 'GroupName': 'Virgin Media O2 Group', 'LegalEntity': 'VMED O2 UK Ltd', 'CompanyNo': '12580944', 'Alias': 'NTL', 'AliasType': 'Predecessor', 'StartDate': '1990-01-01', 'EndDate': '2006-01-01', 'Notes': ''},
    {'CanonicalID': 'CG-0002', 'GroupName': 'Virgin Media O2 Group', 'LegalEntity': 'VMED O2 UK Ltd', 'CompanyNo': '12580944', 'Alias': 'Telewest', 'AliasType': 'Predecessor', 'StartDate': '1990-01-01', 'EndDate': '2006-01-01', 'Notes': ''},
]


def main():
    """Bootstrap canonical groups data"""
    print("=" * 80)
    print("BOOTSTRAPPING CANONICAL CUSTOMER GROUPS")
    print("=" * 80)
    print()

    # Track groups and aliases
    groups_created = {}
    aliases_added = 0
    errors = 0

    # Process data
    for row in CANONICAL_DATA:
        canonical_id = row['CanonicalID']
        group_name = row['GroupName']
        legal_entity = row['LegalEntity']
        company_no = row['CompanyNo']
        alias = row['Alias']
        alias_type = row['AliasType']
        start_date = row['StartDate']
        end_date = row['EndDate']
        notes = row['Notes']

        # Create group if not exists
        if canonical_id not in groups_created:
            print(f"Creating group: {canonical_id} - {group_name}")

            result = canonical_groups_manager.create_group(
                canonical_id=canonical_id,
                group_name=group_name,
                legal_entity=legal_entity,
                company_no=company_no,
                unlock_password=UNLOCK_PASSWORD,
                created_by='bootstrap_script'
            )

            if result['success']:
                groups_created[canonical_id] = True
                print(f"  ✅ Created group {canonical_id}")
            else:
                print(f"  ⚠️  {result['error']}")
                if 'already exists' not in result['error']:
                    errors += 1
                    continue
                else:
                    groups_created[canonical_id] = True

        # Add alias
        print(f"  Adding alias: {alias} ({alias_type})")

        result = canonical_groups_manager.add_alias(
            canonical_id=canonical_id,
            alias=alias,
            alias_type=alias_type,
            unlock_password=UNLOCK_PASSWORD,
            start_date=start_date,
            end_date=end_date,
            notes=notes,
            modified_by='bootstrap_script'
        )

        if result['success']:
            aliases_added += 1
            print(f"    ✅ Added alias")
        else:
            print(f"    ❌ Error: {result['error']}")
            errors += 1

        print()

    print("=" * 80)
    print("BOOTSTRAP COMPLETE")
    print("=" * 80)
    print()
    print(f"Groups created:   {len(groups_created)}")
    print(f"Aliases added:    {aliases_added}")
    print(f"Errors:           {errors}")
    print()
    print("🔒 ALL DATA IS LOCKED - Password 'luca' required to modify")
    print("=" * 80)


if __name__ == '__main__':
    main()
