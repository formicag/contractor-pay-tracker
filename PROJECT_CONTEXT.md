# Contractor Pay Tracker - Project Context

**Last Updated**: 2025-11-11
**Status**: ⚠️ INFRASTRUCTURE FIXED - Pipeline operational, blocked on data seeding

---

## System Overview

AWS serverless application for processing contractor pay Excel files using SQS event-driven architecture, Lambda, and DynamoDB.

### Architecture (NEW: SQS-Based Pipeline)
- **S3**: File storage (bucket: `contractor-pay-files-development-016164185850`)
- **EventBridge**: S3 upload events trigger processing
- **SQS Queues**: 3 queues (upload, validation, import) + 3 DLQs
- **Lambda Functions**: 3 processing functions (extract-metadata, validate-data, import-records)
- **DynamoDB**: Single-table design (`contractor-pay-development`)
- **Terraform**: Infrastructure as Code (in `/terraform` directory)

**IMPORTANT**: System migrated from Step Functions to SQS event-driven architecture

---

## Current System State (2025-11-11)

### Infrastructure Status ✅
- **SQS Queues**: 6 queues operational (3 main + 3 DLQs)
- **Lambda Functions**: 3 functions deployed with layer v36 ✅
- **EventBridge Rules**: S3 upload rule active and enabled ✅
- **Event Source Mappings**: All 3 Lambda-SQS connections configured ✅
- **Lambda Layer v36**: Correctly structured with `python/` at root ✅
- **Environment Variables**: Fixed TABLE_NAME on all 3 functions ✅

### Data Status ⚠️
- **Total DynamoDB Items**: ~18 (Umbrella companies only)
- **PayRecords Created**: 0 ❌ (blocked on validation)
- **TimeRecords Created**: 0 ❌ (blocked on validation)
- **Contractor PROFILE Records**: 0 ❌ (BLOCKER - need to fix seeding)
- **Contractor Associations**: ~50+ ✅ (exist in GSI1)

### What's Working ✅
1. S3 file upload triggers EventBridge → SQS ✅
2. Extract-metadata Lambda processes upload queue ✅
3. Excel parsing and file metadata extraction ✅
4. SQS message passing between stages ✅
5. Detailed logging in validation stage ✅

### What's Blocked ❌
1. **Contractor validation fails** - No PROFILE records in DynamoDB
2. **Import stage never runs** - Validation fails first
3. **Dashboard shows no data** - No PayRecords created + Flask API field name bug
4. **End-to-end testing** - Blocked on validation issue

---

## Recent Critical Fixes (2025-11-11)

### BUG #1: Lambda Environment Variable Configuration - ✅ FIXED
- **Issue**: All 3 Lambda functions had `TABLE_NAME` set to literal string `"$(terraform output -raw dynamodb_table_name)"`
- **Impact**: DynamoDB operations failed with validation error
- **Root Cause**: Manual environment variable override caused drift from IaC
- **Fix**: Updated all 3 Lambda functions with correct `TABLE_NAME=contractor-pay-development`
- **Functions Fixed**:
  - `contractor-pay-extract-metadata-development`
  - `contractor-pay-validate-data-development`
  - `contractor-pay-import-records-development`
- **Status**: ✅ DEPLOYED and verified

### BUG #2: Lambda Layer Directory Structure - ✅ FIXED
- **Issue**: Layer had incorrect directory structure `common/python/` instead of `python/` at root
- **Impact**: `Runtime.ImportModuleError: Unable to import module 'app': No module named 'common'`
- **Root Cause**: AWS Lambda requires `python/` directory at zip root for imports to work
- **Fix**: Rebuilt layer with correct structure and published as v36
- **Structure**: `python/common/{excel_parser.py, validators.py, dynamodb.py, ...}`
- **Status**: ✅ Layer v36 deployed to all 3 functions

### BUG #3: GSI Index Bug in Contractor Validation - ✅ FIXED
- **Location**: `backend/layers/common/python/common/validators.py:890`
- **Issue**: Querying GSI3 (for FILES) instead of GSI1 (for contractor associations)
- **Impact**: "No contractors found for umbrella company" for 100% of files
- **Fix**: Changed `IndexName='GSI3'` to `IndexName='GSI1'`
- **Commit**: bc7f51c
- **Status**: ✅ FIXED and deployed

### BUG #4: Excel Parser Field Mapping - ✅ FIXED
- **Location**: `backend/layers/common/python/common/excel_parser.py:315-360`
- **Issue**: Parser not returning fields in format expected by validator
- **Missing Fields**: `contractor_name`, proper mapping of `pay_rate`/`units`/`pay_amount`
- **Fix**:
  - Construct `contractor_name` from `forename + surname`
  - Map `day_rate` → `pay_rate`
  - Map `unit_days` → `units`
  - Map `amount` → `pay_amount`
- **Status**: ✅ FIXED and deployed in layer v36

### BUG #5: Missing Contractor PROFILE Records - ❌ NOT FIXED (BLOCKER)
- **Issue**: DynamoDB has ContractorUmbrellaAssociation records but no corresponding contractor PROFILE records
- **Impact**: Validation fails at contractor name matching stage
- **Evidence**:
  ```bash
  # GSI1 query succeeds:
  Found 9 contractor associations

  # get_item fails for all:
  Loaded 0 contractor profiles (No 'Item' in response)
  ```
- **Root Cause**: `seed_dynamodb.py` creates associations but not PROFILE records
- **Location**: `/Users/gianlucaformica/Projects/contractor-pay-tracker/backend/seed-data/seed_dynamodb.py`
- **Status**: ❌ IDENTIFIED but not yet fixed - blocks all validation

### BUG #6: Flask API Field Name Mismatch - ❌ NOT FIXED
- **Location**: `flask-app/app.py:~2487` (umbrella-stats endpoint)
- **Issue**: API queries `item.get('CompanyName')` but database has `LegalName` field
- **Impact**: Umbrella dashboard shows "No umbrella company data found"
- **Database Schema**: `{'ShortCode': 'PARASOL', 'LegalName': 'Parasol Limited', 'CompanyName': null}`
- **Fix Required**: Change to `item.get('LegalName', item.get('CompanyName', umbrella_code))`
- **Status**: ❌ IDENTIFIED but not yet fixed - user explicitly asked about this

### AWS Tagging & Cost Allocation - ✅ IMPLEMENTED (2025-11-10)
- **Scope**: All 17 AWS resources across 6 service types
- **Implementation**: Standardized tagging with 7 tag keys
- **Status**: ✅ Deployed and active

---

## Key Files and Locations

### SQS Pipeline Lambda Functions (NEW)
- `backend/functions/extract_metadata/app.py` - Processes upload queue
  - Extracts file metadata and Excel data
  - Publishes to validation queue
- `backend/functions/validate_data/app.py` - Processes validation queue
  - Validates contractor names, pay rates, units
  - Publishes to import queue if valid
- `backend/functions/import_records/app.py` - Processes import queue
  - Creates TimeRecord/PayRecord entities
  - Marks file processing complete

### Lambda Layer (v36 - Current)
- `backend/layers/common/python/common/` - Shared libraries
  - `excel_parser.py` - Excel file parsing with field mapping fixes
  - `fuzzy_matcher.py` - Contractor/umbrella matching
  - `dynamodb.py` - DynamoDB client wrapper
  - `validators.py` - Validation rules with detailed logging (lines 904-933)
- **Structure**: `python/` at root (fixed in v36)
- **Deployment**: Layer ARN attached to all 3 Lambda functions

### Infrastructure
- `terraform/main.tf` - SQS queues, Lambda functions, EventBridge rules
- `terraform/lambda.tf` - Lambda function definitions
- `terraform/sqs.tf` - SQS queue and DLQ definitions
- `terraform/eventbridge.tf` - S3 upload event rules
- `terraform/variables.tf` - Variables (includes tagging variables)
- `terraform/outputs.tf` - Outputs
- `terraform/locals.tf` - Centralized tag definitions

### Database Seeding
- `backend/seed-data/seed_dynamodb.py` - ⚠️ NEEDS FIX - missing contractor PROFILE creation
- `backend/seed-data/seed.py` - Alternative seeding script

### Flask Dashboard
- `flask-app/app.py` - ⚠️ Line ~2487 has field name bug (CompanyName→LegalName)
- `flask-app/templates/umbrella_dashboard.html` - Dashboard UI
- `flask-app/excel_processor.py` - Excel utilities for reprocessing

### Test Data
- `InputData/` - 48 production Excel files (user's complete dataset)

---

## DynamoDB Schema (Single Table Design)

### Entity Types
1. **Umbrella** - Umbrella company reference data
   - `PK`: `UMBRELLA#{UmbrellaID}`
   - `SK`: `PROFILE`
   - Fields: `ShortCode`, `LegalName`, `FileNameVariation`, `IsActive`
   - GSI2: `UMBRELLA_CODE#{ShortCode}` for lookup by code

2. **Contractor** - ⚠️ MISSING (BLOCKER)
   - `PK`: `CONTRACTOR#{ContractorID}`
   - `SK`: `PROFILE`
   - Fields: `FirstName`, `LastName`, `Email`, etc.
   - **Status**: Associations exist, but PROFILE records don't exist

3. **ContractorUmbrellaAssociation** - Links contractors to umbrella companies
   - `PK`: `CONTRACTOR#{ContractorID}`
   - `SK`: `UMBRELLA#{UmbrellaID}`
   - GSI1PK: `UMBRELLA#{UmbrellaID}` (for reverse lookup)
   - **Status**: ~50+ exist, but corresponding contractor PROFILEs don't

4. **FileMetadata** - Uploaded file information
   - `PK`: `FILE#{FileID}`
   - `SK`: `METADATA`
   - Created by extract-metadata Lambda

5. **TimeRecord** / **PayRecord** - Individual pay line items
   - `PK`: `FILE#{FileID}`
   - `SK`: `RECORD#{RecordNumber}`
   - Created by import-records Lambda (when validation passes)
   - **Status**: Currently 0 records (validation blocked)

---

## AWS Credentials

**Profile**: `AdministratorAccess-016164185850`
**Region**: `eu-west-2`

All AWS CLI commands use:
```bash
export AWS_PROFILE=AdministratorAccess-016164185850
export AWS_DEFAULT_REGION=eu-west-2
```

---

## Common Operations

### Deploy Infrastructure Changes
```bash
cd terraform
AWS_PROFILE=AdministratorAccess-016164185850 AWS_DEFAULT_REGION=eu-west-2 terraform plan
AWS_PROFILE=AdministratorAccess-016164185850 AWS_DEFAULT_REGION=eu-west-2 terraform apply
```

### Upload Test File (Triggers SQS Pipeline)
```bash
AWS_PROFILE=AdministratorAccess-016164185850 AWS_DEFAULT_REGION=eu-west-2 \
  aws s3 cp "InputData/FILENAME.xlsx" \
  s3://contractor-pay-files-development-016164185850/production/FILENAME.xlsx
```

### Check SQS Queue Status
```bash
# Check message counts
AWS_PROFILE=AdministratorAccess-016164185850 AWS_DEFAULT_REGION=eu-west-2 \
  aws sqs get-queue-attributes \
  --queue-url https://sqs.eu-west-2.amazonaws.com/016164185850/contractor-pay-upload-queue-development \
  --attribute-names ApproximateNumberOfMessages ApproximateNumberOfMessagesNotVisible
```

### Query DynamoDB
```bash
# Count entities by type
AWS_PROFILE=AdministratorAccess-016164185850 AWS_DEFAULT_REGION=eu-west-2 \
  aws dynamodb scan --table-name contractor-pay-development \
  --filter-expression "EntityType = :et" \
  --expression-attribute-values '{":et":{"S":"Umbrella"}}' \
  --select COUNT

# Get contractor PROFILE (for debugging)
AWS_PROFILE=AdministratorAccess-016164185850 AWS_DEFAULT_REGION=eu-west-2 \
  aws dynamodb get-item --table-name contractor-pay-development \
  --key '{"PK":{"S":"CONTRACTOR#<id>"},"SK":{"S":"PROFILE"}}'
```

### Check Lambda Logs
```bash
# Extract Metadata
AWS_PROFILE=AdministratorAccess-016164185850 AWS_DEFAULT_REGION=eu-west-2 \
  aws logs tail /aws/lambda/contractor-pay-extract-metadata-development --since 10m --follow

# Validate Data
AWS_PROFILE=AdministratorAccess-016164185850 AWS_DEFAULT_REGION=eu-west-2 \
  aws logs tail /aws/lambda/contractor-pay-validate-data-development --since 10m --follow

# Import Records
AWS_PROFILE=AdministratorAccess-016164185850 AWS_DEFAULT_REGION=eu-west-2 \
  aws logs tail /aws/lambda/contractor-pay-import-records-development --since 10m --follow
```

### Seed Database with Contractor Profiles
```bash
cd backend/seed-data
AWS_PROFILE=AdministratorAccess-016164185850 AWS_DEFAULT_REGION=eu-west-2 \
  python3 seed_dynamodb.py --table-name contractor-pay-development
```

---

## Known Issues (Priority Order)

### P0: BLOCKERS
1. **Missing Contractor PROFILE Records** - ❌ NOT FIXED
   - Validation fails because contractor profiles don't exist
   - Need to fix `seed_dynamodb.py` to create PROFILE records
   - Blocks: All file processing, dashboard data

2. **Flask API Field Name Bug** - ❌ NOT FIXED
   - Dashboard queries wrong field name (`CompanyName` vs `LegalName`)
   - Blocks: Umbrella dashboard display
   - User explicitly asked about this issue

### P1: Infrastructure Debt
1. Clean up background Bash processes from debugging
2. Review Lambda memory/timeout settings for optimization
3. Add CloudWatch alarms for SQS DLQ messages

### P2: Future Enhancements
1. Add error recovery in SQS pipeline
2. Implement comprehensive monitoring dashboard
3. Build web UI for file upload

---

## Investigation History

### SQS Pipeline Migration (2025-11-11)
- Migrated from Step Functions to event-driven SQS architecture
- Fixed Lambda environment variable configuration
- Fixed Lambda layer directory structure
- Added detailed logging to validation stage
- Identified contractor PROFILE seeding bug as root blocker

### Previous Work (2025-11-10)
- AWS resource tagging implementation
- Excel parser bug fixes (8 bugs)
- Fuzzy matcher improvements (4 enhancements)

---

## Quick Start After Restart

When you restart Claude Code:

1. **Read this file**: `PROJECT_CONTEXT.md`
2. **Read TODO list**: `TODO.md`
3. **Check system status**:
   ```bash
   # Check Lambda functions
   AWS_PROFILE=AdministratorAccess-016164185850 AWS_DEFAULT_REGION=eu-west-2 \
     aws lambda list-functions --query 'Functions[?starts_with(FunctionName, `contractor-pay`)].FunctionName'

   # Check SQS queue status
   AWS_PROFILE=AdministratorAccess-016164185850 AWS_DEFAULT_REGION=eu-west-2 \
     aws sqs list-queues --queue-name-prefix contractor-pay
   ```

4. **Continue from TODO.md**

---

## Critical Reminders

1. **System uses SQS pipeline, not Step Functions** - EventBridge → SQS → Lambda
2. **Contractor PROFILE records are missing** - This blocks all validation
3. **Flask API has field name bug** - Queries CompanyName but database has LegalName
4. **All AWS operations require profile** - `AWS_PROFILE=AdministratorAccess-016164185850`
5. **Lambda layer v36 is current** - Contains all parser fixes and detailed logging
6. **Region is eu-west-2** - Don't forget `AWS_DEFAULT_REGION=eu-west-2`

---

**System Status**: ⚠️ INFRASTRUCTURE OPERATIONAL - Pipeline ready, blocked on data seeding
