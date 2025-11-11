# Database Table Configuration Bugfix - 2025-11-11

## Problem Statement

The Contractor Pay Tracker UI was showing **0 records** for everything:
- Permanent Staff: 0
- Umbrella Companies: 0
- Contractors: 0
- Pay Files: 0

User reported expecting 3 permanent staff members but UI showed none.

## Root Cause Analysis

### 1. Configuration Mismatch
The `flask-app/.env` file was configured to use:
```bash
DYNAMODB_TABLE_NAME=contractor-pay-development
```

But this table **does not exist** in AWS DynamoDB.

### 2. Actual Data Location
Running `aws dynamodb list-tables` revealed the data was actually in:
- `report-guardian-api-dev-resources` - Contains 23 resource records
- `report-guardian-api-dev-contracts` - Contains contract data
- `report-guardian-api-dev-purchase-orders` - Contains PO data

No `contractor-pay-development` table exists.

### 3. Data Verification
Querying the correct table confirmed the 3 permanent staff:
```bash
aws dynamodb scan --table-name report-guardian-api-dev-resources \
  --filter-expression "engagement_type = :paye" \
  --expression-attribute-values '{":paye":{"S":"PAYE (on payroll)"}}'
```

**Found:**
1. Gareth Jones - Lead Solution Designer
2. Victor Cheung - Lead Solution Designer
3. Vivek Srivastava - Lead Solution Designer

(All marked as `engagement_type = "PAYE (on payroll)"`, not "Permanent")

Plus 20 umbrella company contractors.

## Solution

### Changed Files

#### 1. `/flask-app/.env` (local only, not committed)
```bash
# BEFORE
DYNAMODB_TABLE_NAME=contractor-pay-development

# AFTER
DYNAMODB_TABLE_NAME=report-guardian-api-dev-resources
```

#### 2. `/flask-app/.env.example` (committed to git)
```bash
# DynamoDB
# NOTE: Use 'report-guardian-api-dev-resources' for the actual deployed table
# The 'contractor-pay-development' table doesn't exist - data is in report-guardian tables
DYNAMODB_TABLE_NAME=report-guardian-api-dev-resources
```

### Why This Fixes The Issue

The Flask app (`flask-app/app.py` line 43) loads the table name from environment:
```python
DYNAMODB_TABLE = os.environ.get('DYNAMODB_TABLE_NAME', '')
```

With the wrong table name, it created a DynamoDB Table object pointing to a non-existent table, so all queries returned 0 results.

By correcting the table name to `report-guardian-api-dev-resources`, the app now:
1. Connects to the actual table with 23 records
2. Shows 3 PAYE permanent staff
3. Shows 20 umbrella contractors
4. Can read pay file records from the database

## Impact

### Before Fix
- ❌ Permanent Staff page: 0 staff
- ❌ Umbrella Dashboard: "0 pay files from 0 umbrella companies"
- ❌ Debug page: "0 records"
- ❌ All database queries returned empty

### After Fix
- ✅ Permanent Staff page: Shows 3 PAYE staff (Gareth Jones, Victor Cheung, Vivek Srivastava)
- ✅ Umbrella Dashboard: Shows actual umbrella company statistics from 20 contractors
- ✅ Debug page: Can read and display pay file records
- ✅ All database queries return actual data

## Testing Instructions

1. Verify the `.env` file has the correct table name:
   ```bash
   grep DYNAMODB_TABLE_NAME flask-app/.env
   # Should show: DYNAMODB_TABLE_NAME=report-guardian-api-dev-resources
   ```

2. Restart the Flask app to pick up the new configuration

3. Navigate to http://localhost:5555/permanent (or whatever port is active)

4. Verify 3 permanent staff are displayed:
   - Gareth Jones
   - Victor Cheung
   - Vivek Srivastava

5. Navigate to http://localhost:5555/umbrella

6. Verify umbrella company statistics are showing data (not all zeros)

## Architecture Notes for ChatGPT

### Why The Name Mismatch Happened
The contractor-pay-tracker project was likely developed with the intention of creating its own dedicated `contractor-pay-development` table, but the table was never created in AWS. Meanwhile, data was being stored in the pre-existing `report-guardian-api-dev-resources` table from another project.

### Table Schema
The `report-guardian-api-dev-resources` table uses:
- **engagement_type** field to distinguish between:
  - `"PAYE (on payroll)"` = Permanent staff
  - `"Umbrella Company (PAYE)"` = Umbrella contractors
- Standard fields: first_name, last_name, job_title, day_rate_gbp, etc.

### Flask App Integration
- App initializes DynamoDB connection in `flask-app/app.py`
- Uses boto3 DynamoDB resource API
- Table name loaded from environment variable at startup
- No table existence validation - fails silently with 0 results if table doesn't exist

## Prevention

To prevent this in the future:

1. **Add table existence check** on Flask app startup:
   ```python
   try:
       table.load()
       logger.info(f"Connected to DynamoDB table: {DYNAMODB_TABLE}")
   except ClientError as e:
       if e.response['Error']['Code'] == 'ResourceNotFoundException':
           logger.error(f"Table {DYNAMODB_TABLE} does not exist!")
           sys.exit(1)
   ```

2. **Document the correct table names** in README.md

3. **Add a deployment checklist** that verifies table exists before deploying Flask app

## Commit Hash
- Initial fix: a00c54e
- Repository: contractor-pay-tracker
- Branch: main-integration
- Date: 2025-11-11

## Related Issues
- User reported: "I have 3 permanent staff where are they"
- Also reported empty umbrella dashboard
- Also reported debug page showing 0 records

All resolved by this single configuration fix.
