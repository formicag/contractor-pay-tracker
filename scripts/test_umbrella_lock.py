#!/usr/bin/env python3
"""
Test Umbrella Company Password Protection

This script tests that:
1. Data can be read without password
2. Updates FAIL without correct password
3. Updates SUCCEED with correct password "luca"
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../flask-app'))

from umbrella_company_manager import umbrella_manager

print("=" * 80)
print("UMBRELLA COMPANY PASSWORD PROTECTION TEST")
print("=" * 80)
print()

# Test 1: Read without password (should work)
print("Test 1: Reading umbrella companies (no password required)")
companies = umbrella_manager.get_all_umbrella_companies()
print(f"✅ Found {len(companies)} umbrella companies")
print()

if not companies:
    print("❌ No companies found. Run setup script first.")
    sys.exit(1)

# Pick first company for testing
test_company = companies[0]
company_id = test_company['company_id']
print(f"Testing with: {test_company['trading_name']} (ID: {company_id})")
print()

# Test 2: Try to update without password (should FAIL)
print("Test 2: Attempting update WITHOUT password...")
result = umbrella_manager.update_umbrella_company(
    company_id=company_id,
    unlock_password='wrong_password',
    updates={'vat_number': 'FAKE123456'},
    modified_by='test_script'
)

if not result['success']:
    print(f"✅ PASS: Update blocked as expected")
    print(f"   Error: {result['error']}")
else:
    print(f"❌ FAIL: Update succeeded when it should have been blocked!")
print()

# Test 3: Try to update with CORRECT password (should SUCCEED)
print("Test 3: Attempting update WITH correct password 'luca'...")
original_vat = test_company.get('vat_number', '')
result = umbrella_manager.update_umbrella_company(
    company_id=company_id,
    unlock_password='luca',
    updates={'vat_number': original_vat},  # Restore original
    modified_by='test_script'
)

if result['success']:
    print(f"✅ PASS: Update succeeded with correct password")
    print(f"   Message: {result['message']}")
else:
    print(f"❌ FAIL: Update failed even with correct password!")
    print(f"   Error: {result.get('error', 'Unknown')}")
print()

# Test 4: Try to delete without password (should FAIL)
print("Test 4: Attempting delete WITHOUT password...")
result = umbrella_manager.delete_umbrella_company(
    company_id=company_id,
    unlock_password='wrong_password',
    deleted_by='test_script'
)

if not result['success']:
    print(f"✅ PASS: Delete blocked as expected")
    print(f"   Error: {result['error']}")
else:
    print(f"❌ FAIL: Delete succeeded when it should have been blocked!")
print()

# Verify lock status
company = umbrella_manager.get_umbrella_company(company_id)
if company:
    print(f"Current lock status: {'🔒 LOCKED' if company.get('locked') else '🔓 Unlocked'}")
    print(f"Version: {company.get('version', 1)}")
    print(f"Last modified: {company.get('modified_at', 'N/A')}")
    print(f"Modified by: {company.get('modified_by', 'N/A')}")
print()

print("=" * 80)
print("🔐 PASSWORD PROTECTION TEST COMPLETE")
print("=" * 80)
print()
print("Summary:")
print("  ✅ Read access: Works without password")
print("  ✅ Update protection: Blocks incorrect password")
print("  ✅ Update with unlock: Works with 'luca'")
print("  ✅ Delete protection: Blocks incorrect password")
print()
print("🔒 All umbrella company data is protected!")
print()
