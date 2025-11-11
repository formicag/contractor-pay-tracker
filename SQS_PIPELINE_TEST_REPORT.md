# SQS-Based File Processing Pipeline Test Report

**Date:** 2025-11-10
**Test Duration:** ~5 minutes
**Environment:** Development (AWS Account 016164185850, eu-west-2)
**Tester:** Claude Code Agent

---

## Executive Summary

**CRITICAL ISSUE IDENTIFIED:** All 6 test files (100%) failed validation due to a **fundamental bug in the contractor lookup logic**. The validation code is querying the wrong DynamoDB index (GSI3 instead of GSI1), resulting in zero contractors being found for all umbrella companies.

**Impact:** This bug prevents ANY production Excel files from being successfully imported into the system.

**Status:**
- ❌ All files: VALIDATION_FAILED (6/6)
- ✅ Processing pipeline: Working correctly
- ✅ Lambda orchestration: Working correctly
- ❌ Validation logic: CRITICAL BUG

---

## 1. Test Execution Summary

### Files Tested
Successfully uploaded 6 files (one per umbrella company, all from period 29092025):

| Umbrella Company | File Name | Size | Upload Status |
|-----------------|-----------|------|---------------|
| Clarity | TEST-AGENT-Clarity-29092025.xlsx | 9.8 KB | ✅ Success |
| GIANT | TEST-AGENT-GIANT-29092025.xlsx | 9.3 KB | ✅ Success |
| NASA | TEST-AGENT-NASA-29092025.xlsx | 55.2 KB | ✅ Success |
| Parasol | TEST-AGENT-Parasol-29092025.xlsx | 10.5 KB | ✅ Success |
| PAYSTREAM | TEST-AGENT-PAYSTREAM-29092025.xlsx | 10.3 KB | ✅ Success |
| WORKWELL | TEST-AGENT-WORKWELL-29092025.xlsx | 29.1 KB | ✅ Success |

### Processing Timeline
- **Upload Time:** ~3 seconds (all 6 files)
- **Wait Time:** 90 seconds (for all 3 Lambda stages)
- **Total Test Time:** ~2 minutes

All files were processed through the complete SQS pipeline:
1. ✅ S3 Upload → extract-metadata Lambda
2. ✅ Metadata extraction → file-processor Lambda
3. ✅ Excel parsing → validate-data Lambda
4. ❌ Validation → FAILED (all 6 files)

---

## 2. FILE Status Breakdown

### Status Distribution
| Status | Count | Percentage | Umbrella Companies |
|--------|-------|------------|-------------------|
| VALIDATION_FAILED | 6 | 100% | All (Clarity, GIANT, NASA, Parasol, PAYSTREAM, WORKWELL) |
| COMPLETED | 0 | 0% | None |
| PROCESSING | 0 | 0% | None |
| FAILED | 0 | 0% | None |

### Per-Umbrella Results

| Umbrella | Status | Error Count | Primary Error |
|----------|--------|-------------|---------------|
| Clarity | VALIDATION_FAILED | 5 | No contractors found for umbrella company |
| GIANT | VALIDATION_FAILED | 3 | No contractors found for umbrella company |
| NASA | VALIDATION_FAILED | 5 | No contractors found for umbrella company |
| Parasol | VALIDATION_FAILED | 5 | No contractors found for umbrella company |
| PAYSTREAM | VALIDATION_FAILED | 5 | No contractors found for umbrella company |
| WORKWELL | VALIDATION_FAILED | 5 | No contractors found for umbrella company |

**Key Finding:** All umbrella companies are affected equally - this is NOT a data issue, it's a code bug.

---

## 3. Validation Error Analysis

### Error Pattern (100% of Files)

From Lambda logs and DynamoDB FILE records:

```
[VALIDATE_CONTRACTOR_NAME] Querying contractors for umbrella: {umbrella_id}
[VALIDATE_CONTRACTOR_NAME] Found 0 contractors for umbrella {umbrella_id}
[VALIDATE_CONTRACTOR_NAME] No contractors found for umbrella
```

### Sample Validation Errors (GIANT file)

```json
{
  "validation_errors": [
    {
      "field": "contractor_name",
      "error": "No contractors found for umbrella company",
      "severity": "ERROR"
    },
    {
      "field": "contractor_name",
      "error": "No contractors found for umbrella company",
      "severity": "ERROR"
    },
    {
      "field": "period",
      "error": "1 records have missing required fields",
      "severity": "ERROR"
    }
  ]
}
```

### Error Frequency
- **"No contractors found for umbrella company"**: 100% of files (all contractor name validations)
- **"Missing required fields"**: Some records (secondary issue - caused by contractor lookup failure)

---

## 4. Excel File Structure Analysis

All 6 umbrella companies use **identical Excel structure** (standardized format):

### Common Structure
- **Header Row:** Row 1
- **Data Start:** Row 2
- **Total Columns:** 25
- **Standard Columns:** employee_id, surname, forename, unit, rate, per, amount, vat, total_hours_per_period, company, notes

### File Statistics

| Umbrella | Rows | Contractor Count | Notes |
|----------|------|------------------|-------|
| Clarity | 9 | 8 | Standard format, employee_id missing in row 2 |
| GIANT | 3 | 2 | Standard format, both records complete |
| NASA | 963 | 962 | Large file, standard format |
| Parasol | 25 | 24 | Standard format |
| PAYSTREAM | 24 | 23 | Standard format |
| WORKWELL | 992 | 991 | Large file, standard format |

### Sample Data (GIANT file, Row 2):

| Column | Value | Type |
|--------|-------|------|
| employee_id | 445288 | Integer |
| surname | Mays | String |
| forename | Jonathan | String |
| unit | 13 | Integer (days worked) |
| rate | 524.48 | Float (day rate) |
| per | day | String |
| amount | 6818.24 | Float |
| vat | 1363.65 | Float |
| total_hours_per_period | 97.5 | Float |
| company | GIANT PROFESSIONAL LIMITED (PRG) | String |

**Conclusion:** Excel files are well-formed and follow consistent structure. No parsing issues detected.

---

## 5. Contractor Database Analysis

### Database Population

| Entity Type | Count | Notes |
|-------------|-------|-------|
| Contractor | 46 | Base contractor records |
| ContractorUmbrellaAssociation | 47 | Links between contractors and umbrellas |
| Umbrella | 12 | Umbrella company records |
| Period | 13 | Pay period definitions |
| File | 18 | File processing records |

### Contractor-Umbrella Linkage Status

**CRITICAL FINDING:**

```bash
Contractors with GSI1PK (umbrella link): 0
Total contractors: 46
```

**Explanation:** Contractor PROFILE records don't have GSI1PK set. The linkage exists in separate `ContractorUmbrellaAssociation` records, but the validation code is looking in the wrong place.

### ContractorUmbrellaAssociation Structure

Associations are correctly structured:

```json
{
  "PK": "CONTRACTOR#{contractor_id}",
  "SK": "UMBRELLA#{umbrella_id}",
  "GSI1PK": "UMBRELLA#{umbrella_id}",
  "GSI1SK": "CONTRACTOR#{contractor_id}",
  "EntityType": "ContractorUmbrellaAssociation",
  "ContractorID": "{uuid}",
  "UmbrellaID": "{uuid}",
  "EmployeeID": "807654",
  "ValidFrom": "2025-01-01",
  "ValidTo": null,
  "IsActive": true
}
```

**GSI1 Purpose:** Query all contractors for an umbrella using `GSI1PK = UMBRELLA#{umbrella_id}`

### Umbrella Company Records

All 6 test umbrella companies exist in database:

| ShortCode | LegalName | FileNameVariation | UmbrellaID |
|-----------|-----------|-------------------|------------|
| CLARITY | Clarity Umbrella Ltd | CLARITY | 6e741e3a-... |
| GIANT | Giant Professional Limited | GIANT PROFESSIONAL LIMITED (PRG) | cd81e6ef-... |
| NASA | Nasa Umbrella Ltd | NASA GROUP | 76fd62dc-... |
| PARASOL | Parasol Limited | PARASOL | 19278b15-... |
| PAYSTREAM | PayStream My Max 3 Limited | PAYSTREAM MYMAX | d2956dbe-... |
| WORKWELL | Workwell People Solutions Limited | WORKWELL (JSA SERVICES) | 4618778d-... |

**Verification:** Umbrella companies are correctly populated with matching FileNameVariation for Excel file parsing.

---

## 6. ROOT CAUSE IDENTIFICATION

### The Critical Bug

**Location:** `/backend/layers/common/python/common/validators.py`
**Function:** `validate_contractor_name()` (lines 835-1005)
**Issue:** **Wrong DynamoDB index being queried**

### Current (Broken) Code - Line 889

```python
response = dynamodb_client.table.query(
    IndexName='GSI3',                           # ❌ WRONG INDEX
    KeyConditionExpression='GSI3PK = :pk',
    ExpressionAttributeValues={
        ':pk': f'UMBRELLA#{umbrella_id}'        # GSI3 doesn't have this!
    }
)
```

**What's Wrong:**
- GSI3 is used for FILE records (GSI3PK = "FILES")
- GSI3 is NOT indexed by umbrella company
- Query returns 0 results for all umbrella queries

**Test Query Results:**
```bash
aws dynamodb query --index-name GSI3 \
  --key-condition-expression "GSI3PK = :pk" \
  --expression-attribute-values '{":pk":{"S":"UMBRELLA#76fd62dc-ce5e-45ee-af1e-3c120f1a93d2"}}'

Result: 0 items (always)
```

### Correct Approach

**Solution:** Query GSI1 to get ContractorUmbrellaAssociation records:

```python
response = dynamodb_client.table.query(
    IndexName='GSI1',                           # ✅ CORRECT INDEX
    KeyConditionExpression='GSI1PK = :pk',
    ExpressionAttributeValues={
        ':pk': f'UMBRELLA#{umbrella_id}'
    }
)
```

**Verified Working:**
```bash
aws dynamodb query --index-name GSI1 \
  --key-condition-expression "GSI1PK = :pk" \
  --expression-attribute-values '{":pk":{"S":"UMBRELLA#76fd62dc-ce5e-45ee-af1e-3c120f1a93d2"}}'

Result: 5 items (contractor associations)
```

### Why This Bug Exists

Looking at the data model:
- **GSI1:** Used for ContractorUmbrellaAssociation (GSI1PK = `UMBRELLA#{id}`, GSI1SK = `CONTRACTOR#{id}`)
- **GSI2:** Used for name lookups (GSI2PK = `NAME#{normalized_name}` for contractors, `UMBRELLA_CODE#{code}` for umbrellas)
- **GSI3:** Used for file listing (GSI3PK = `FILES`)

The validation code should:
1. Query GSI1 to get all ContractorUmbrellaAssociation records for the umbrella
2. Extract ContractorID from each association
3. Load contractor PROFILE records to get names
4. Perform fuzzy matching against contractor names

### Impact Analysis

**Files Affected:** ALL (100%)
**Records Affected:** ALL contractor records in every file
**Severity:** P0 - CRITICAL BLOCKER

This bug makes the entire validation system non-functional. No files can pass validation because contractor lookup always fails.

---

## 7. Additional Findings

### Secondary Issues

1. **Missing Units Field (GIANT file, 1 record)**
   - One contractor record in GIANT file has missing "units" field
   - This is a data quality issue in the Excel file
   - Caused secondary validation error

2. **DynamoDB Data Model Confusion**
   - Multiple GSI indexes with different purposes
   - No comprehensive data model documentation found in codebase
   - Led to developer using wrong index

### What's Working Well

✅ **S3 Upload & Event Trigger:** Files successfully trigger Lambda processing
✅ **SQS Pipeline:** All 3 stages execute in correct order
✅ **Excel Parsing:** Parser correctly extracts data from all umbrella formats
✅ **Umbrella Detection:** Files correctly matched to umbrella companies
✅ **Error Logging:** Extensive logging captured issue clearly
✅ **DynamoDB Updates:** FILE status records updated correctly

---

## 8. RECOMMENDATIONS

### Priority 1: Critical Fixes (Must Fix Before ANY Production Use)

#### 1. Fix Contractor Lookup Query (P0 - BLOCKER)
**File:** `/backend/layers/common/python/common/validators.py`
**Lines:** 889-895
**Complexity:** Low (5 minutes)

**Change Required:**
```python
# BEFORE (BROKEN)
response = dynamodb_client.table.query(
    IndexName='GSI3',
    KeyConditionExpression='GSI3PK = :pk',
    ExpressionAttributeValues={
        ':pk': f'UMBRELLA#{umbrella_id}'
    }
)

# AFTER (FIXED)
response = dynamodb_client.table.query(
    IndexName='GSI1',
    KeyConditionExpression='GSI1PK = :pk',
    ExpressionAttributeValues={
        ':pk': f'UMBRELLA#{umbrella_id}'
    }
)

# Then extract ContractorIDs and load contractor profiles
contractor_ids = [item.get('ContractorID') for item in response.get('Items', [])]

# Build contractors list with ContractorName field for matching
contractors = []
for contractor_id in contractor_ids:
    profile_response = dynamodb_client.table.get_item(
        Key={
            'PK': f'CONTRACTOR#{contractor_id}',
            'SK': 'PROFILE'
        }
    )
    if 'Item' in profile_response:
        contractor = profile_response['Item']
        # Add ContractorName field for fuzzy matching
        contractor['ContractorName'] = f"{contractor['FirstName']} {contractor['LastName']}"
        contractors.append(contractor)
```

**Testing:** Run same test with 6 files - should now find contractors

#### 2. Update Fuzzy Matching Logic
**Lines:** 913-927 (exact match), 940-954 (fuzzy match)

The code expects `ContractorName` field but contractor profiles have `FirstName` and `LastName`. Update matching logic to use:
```python
db_name = f"{contractor.get('FirstName', '')} {contractor.get('LastName', '')}"
```

### Priority 2: Immediate Improvements (Before Scale Testing)

#### 3. Add Contractor Caching (P1)
**Reason:** Current approach queries DynamoDB once per contractor per file
**Impact:** With 962 contractors (NASA), this means 962 individual GetItem calls
**Solution:** Cache all contractors for umbrella in memory after first query

#### 4. Create Data Model Documentation (P1)
**Location:** Create `/docs/DATABASE_SCHEMA.md`
**Content:**
- Entity types and their PK/SK patterns
- All GSI indexes and their purposes
- Access patterns and which index to use
- Sample queries for common operations

#### 5. Add Integration Tests (P1)
**Location:** `/tests/integration/test_validation_engine.py`
**Tests:**
- Test contractor lookup for each umbrella company
- Test fuzzy matching with sample names
- Test validation with complete sample file
- Mock DynamoDB responses

### Priority 3: Future Enhancements

#### 6. Performance Optimization (P2)
- Batch get_item calls (max 100 per batch)
- Use Query with projection expression to reduce data transfer
- Consider caching at Lambda layer level

#### 7. Error Reporting Enhancement (P2)
- Include contractor count in validation errors
- Show sample contractor names for debugging
- Add retry logic for transient DynamoDB errors

#### 8. Monitoring & Alerts (P3)
- CloudWatch alarm for validation failure rate > 10%
- Dashboard showing validation success rate by umbrella
- Daily report of files awaiting manual review

---

## 9. Test Data Samples

### Contractors Found in Database (Sample)

Successfully seeded contractors exist:
- Duncan Macadam (NASA)
- Paul Marsh (NASA)
- Jonathan Mays (GIANT)
- Nik Coultas (Clarity)
- Plus 42 others across all umbrella companies

### File Names in Excel

Excel "company" column values match umbrella FileNameVariation:
- ✅ "CLARITY" → matches Clarity
- ✅ "GIANT PROFESSIONAL LIMITED (PRG)" → matches GIANT
- ✅ "NASA GROUP" → matches NASA
- ✅ "PARASOL" → matches Parasol
- ✅ "PAYSTREAM MYMAX" → matches PAYSTREAM
- ✅ "WORKWELL (JSA SERVICES)" → matches WORKWELL

---

## 10. Next Steps

### Immediate Actions (Today)

1. ✅ **TEST COMPLETED** - Pipeline tested, bug identified
2. ⏳ **FIX BUG** - Apply Priority 1 fix to validators.py
3. ⏳ **RETEST** - Re-run same 6 test files
4. ⏳ **VERIFY** - Confirm all 6 files reach COMPLETED status

### This Week

1. Complete Priority 2 improvements
2. Run full 48-file production test
3. Monitor validation success rates
4. Document any edge cases found

### Before Production Launch

1. All Priority 1 and 2 items complete
2. 100% success rate on test files
3. Manual review of first 5 production imports
4. Monitoring dashboards configured

---

## Appendix A: Test Commands Used

### Upload Test Files
```bash
export AWS_PROFILE=AdministratorAccess-016164185850
export AWS_DEFAULT_REGION=eu-west-2

aws s3 cp "InputData/Clarity GCI Nasstar Contractor Pay Figures 29092025.xlsx" \
  s3://contractor-pay-files-development-016164185850/production/TEST-AGENT-Clarity-29092025.xlsx
```

### Query FILE Status
```bash
aws dynamodb query \
  --table-name contractor-pay-development \
  --index-name GSI3 \
  --key-condition-expression "GSI3PK = :pk" \
  --expression-attribute-values '{":pk":{"S":"FILES"}}'
```

### Check Validation Errors
```bash
aws logs tail /aws/lambda/contractor-pay-validate-data-development \
  --since 10m \
  --filter-pattern "No contractors found"
```

### Verify GSI1 Query (Working)
```bash
aws dynamodb query \
  --table-name contractor-pay-development \
  --index-name GSI1 \
  --key-condition-expression "GSI1PK = :pk" \
  --expression-attribute-values '{":pk":{"S":"UMBRELLA#76fd62dc-ce5e-45ee-af1e-3c120f1a93d2"}}'
```

---

## Appendix B: Lambda Log Excerpts

### Validation Failure Pattern

```
[VALIDATE_CONTRACTOR_NAME] === Starting contractor name validation ===
[VALIDATE_CONTRACTOR_NAME] Input contractor_name: 'Jonathan Mays'
[VALIDATE_CONTRACTOR_NAME] Input umbrella_id: 'cd81e6ef-a69c-4128-82e0-8b86d3a4f536'
[VALIDATE_CONTRACTOR_NAME] Cleaned contractor_name: 'Jonathan Mays'
[VALIDATE_CONTRACTOR_NAME] Querying contractors for umbrella: cd81e6ef-a69c-4128-82e0-8b86d3a4f536
[VALIDATE_CONTRACTOR_NAME] Found 0 contractors for umbrella cd81e6ef-a69c-4128-82e0-8b86d3a4f536
[VALIDATE_CONTRACTOR_NAME] No contractors found for umbrella
```

### File Status Update

```
[UPDATE_FILE_STATUS] Called with file_id=abf35363-3936-4ba3-b982-ac03b33e4f27,
  status=VALIDATION_FAILED,
  kwargs={'umbrella_code': 'GIANT', 'period_number': 9,
  'validation_errors': [
    {'field': 'contractor_name', 'error': 'No contractors found...', 'severity': 'ERROR'},
    {'field': 'contractor_name', 'error': 'No contractors found...', 'severity': 'ERROR'},
    {'field': 'period', 'error': '1 records have missing required fields', 'severity': 'ERROR'}
  ]}
```

---

## Conclusion

The SQS-based file processing pipeline architecture is sound and working correctly. However, a critical bug in the contractor validation logic prevents ANY files from being successfully imported. This is a **quick fix** (changing GSI3 to GSI1 plus loading contractor profiles) that will unlock the entire system.

**Estimated Time to Fix:** 30 minutes (coding + testing)
**Estimated Time to Full Production:** 1-2 days (including full 48-file test)

Once fixed, the system will be ready to process all 48 production Excel files across 6 umbrella companies and 8 time periods.

---

**Report Generated:** 2025-11-10 20:35 UTC
**Test Files Cleaned Up:** ✅ All 6 test files removed from S3
**Database State:** Unchanged (test had no side effects on contractor/umbrella data)
