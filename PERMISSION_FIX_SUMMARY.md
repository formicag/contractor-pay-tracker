# Lambda IAM Permissions - Quick Fix Summary

## Status: 🔴 CRITICAL ISSUES FOUND

Three critical permission gaps have been identified that will cause **runtime failures** when users upload files.

---

## The Problem

**File Upload Workflow:**
```
1. User uploads file via API
   ↓
2. file-upload-handler Lambda executes
   ├─ Uploads file to S3 ✓
   ├─ Stores metadata in DynamoDB ✓
   └─ Calls Step Functions to start workflow ❌ PERMISSION DENIED

   Error: AccessDeniedException - states:StartExecution permission missing
```

The Lambda function attempts to call `sfn_client.start_execution()` but the IAM role lacks the required permissions.

---

## Root Cause

**Current IAM Policy** only allows:
- ✓ DynamoDB: `dynamodb:*` (all actions)
- ✓ S3: `s3:*` (all actions)
- ✗ Step Functions: **NO PERMISSIONS**

The file-upload-handler code (line 57-58 of `/backend/functions/file_upload_handler/app.py`):
```python
sfn_client = boto3.client('stepfunctions')
# Line 334: sfn_client.start_execution(...)  ← Fails here
```

---

## Quick Fix (2 Steps)

### Step 1: Run the Fix Script

```bash
cd /Users/gianlucaformica/Projects/contractor-pay-tracker

# Option A: Automatic (recommended)
./fix-lambda-permissions.sh

# Option B: Manual with explicit parameters
./fix-lambda-permissions.sh AdministratorAccess-016164185850 016164185850 eu-west-2
```

**What it does:**
- Updates the IAM inline policy to add Step Functions permissions
- Implements least-privilege security (removes wildcards)
- Verifies the policy was applied correctly

### Step 2: Verify the Fix

```bash
# Test file upload
curl -X POST https://<your-api-endpoint>/api/v1/upload \
  -H "Content-Type: application/json" \
  -d '{
    "filename": "test.xlsx",
    "file_content_base64": "<base64-encoded-file>",
    "uploaded_by": "test-user"
  }'

# Verify Step Functions execution started
aws stepfunctions list-executions \
  --state-machine-arn arn:aws:states:eu-west-2:016164185850:stateMachine:contractor-pay-workflow-development \
  --status-filter RUNNING
```

---

## What Gets Fixed

### Before (Current)
```json
{
  "Statement": [
    {
      "Action": ["dynamodb:*"],
      "Resource": ["table/*"]
    },
    {
      "Action": ["s3:*"],
      "Resource": ["bucket/*"]
    }
  ]
}
```

### After (Fixed)
```json
{
  "Statement": [
    {
      "Sid": "DynamoDBAccess",
      "Action": [
        "dynamodb:GetItem",
        "dynamodb:PutItem",
        "dynamodb:UpdateItem",
        "dynamodb:Query",
        "dynamodb:Scan",
        "dynamodb:BatchWriteItem"
      ],
      "Resource": ["table/*"]
    },
    {
      "Sid": "S3Access",
      "Action": [
        "s3:GetObject",
        "s3:HeadObject",
        "s3:PutObject",
        "s3:ListBucket",
        "s3:DeleteObject"
      ],
      "Resource": ["bucket/*"]
    },
    {
      "Sid": "StepFunctionsAccess",
      "Action": [
        "states:StartExecution",
        "states:DescribeExecution"
      ],
      "Resource": ["stateMachine:contractor-pay-*"]
    }
  ]
}
```

**Security Improvements:**
- ✅ Removes dangerous wildcard `*` for DynamoDB (prevents table deletion)
- ✅ Removes dangerous wildcard `*` for S3 (prevents bucket deletion)
- ✅ Adds minimum Step Functions permissions needed
- ✅ Follows AWS least-privilege principle

---

## Issues Fixed

### 🔴 CRITICAL #1: Missing Step Functions Permission
- **Status:** WILL FAIL immediately
- **Error:** AccessDeniedException on states:StartExecution
- **Fix:** Added `states:StartExecution` and `states:DescribeExecution`

### 🔴 CRITICAL #2: Security Risk - DynamoDB Wildcard
- **Status:** Works but overly permissive
- **Risk:** Function can delete entire DynamoDB table
- **Fix:** Specific actions only (Get, Put, Update, Query, Scan, BatchWrite)

### 🔴 CRITICAL #3: Security Risk - S3 Wildcard
- **Status:** Works but overly permissive
- **Risk:** Function can delete S3 bucket
- **Fix:** Specific actions only (Get, Head, Put, List, Delete)

---

## Affected Lambda Functions

| Function | Issue | Current Status | Post-Fix |
|----------|-------|-----------------|----------|
| file-upload-handler | Missing Step Functions | ❌ FAILS | ✅ Works |
| file-processor | None (invoked by Step Functions) | ✓ Works | ✓ Works |
| validation-engine | None (DynamoDB only) | ✓ Works | ✓ Works |
| report-generator | None | ✓ Works | ✓ Works |
| cleanup-handler | None | ✓ Works | ✓ Works |

---

## Testing Checklist

After running the fix script:

- [ ] Script executed without errors
- [ ] "✅ All permissions applied successfully!" message displayed
- [ ] No timeout errors during policy application

Then test the actual workflow:

- [ ] Upload a test Excel file via API
- [ ] Check CloudWatch logs for file-upload-handler
- [ ] Verify file appears in S3 bucket
- [ ] Verify metadata in DynamoDB
- [ ] Check Step Functions execution started
- [ ] Verify file processing workflow runs to completion

---

## Manual Fix (If Script Fails)

If the automated script doesn't work, apply the policy manually:

```bash
# 1. Create policy file
cat > /tmp/lambda_policy.json <<'EOF'
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "DynamoDBAccess",
      "Effect": "Allow",
      "Action": [
        "dynamodb:GetItem",
        "dynamodb:PutItem",
        "dynamodb:UpdateItem",
        "dynamodb:Query",
        "dynamodb:Scan",
        "dynamodb:BatchWriteItem"
      ],
      "Resource": [
        "arn:aws:dynamodb:eu-west-2:016164185850:table/contractor-pay-development",
        "arn:aws:dynamodb:eu-west-2:016164185850:table/contractor-pay-development/index/*"
      ]
    },
    {
      "Sid": "S3Access",
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:GetObjectVersion",
        "s3:HeadObject",
        "s3:PutObject",
        "s3:ListBucket",
        "s3:DeleteObject"
      ],
      "Resource": [
        "arn:aws:s3:::contractor-pay-files-development-016164185850",
        "arn:aws:s3:::contractor-pay-files-development-016164185850/*"
      ]
    },
    {
      "Sid": "StepFunctionsAccess",
      "Effect": "Allow",
      "Action": [
        "states:StartExecution",
        "states:DescribeExecution"
      ],
      "Resource": [
        "arn:aws:states:eu-west-2:016164185850:stateMachine:contractor-pay-*"
      ]
    }
  ]
}
EOF

# 2. Apply policy
aws iam put-role-policy \
  --role-name contractor-pay-lambda-development \
  --policy-name contractor-pay-lambda-policy \
  --policy-document file:///tmp/lambda_policy.json \
  --profile AdministratorAccess-016164185850

# 3. Verify
aws iam get-role-policy \
  --role-name contractor-pay-lambda-development \
  --policy-name contractor-pay-lambda-policy \
  --profile AdministratorAccess-016164185850
```

---

## Files Generated

1. **LAMBDA_PERMISSIONS_AUDIT.md** - Full technical audit report
2. **fix-lambda-permissions.sh** - Automated fix script
3. **PERMISSION_FIX_SUMMARY.md** - This file (quick reference)

---

## Next Steps

1. ✅ Run `./fix-lambda-permissions.sh`
2. ✅ Test file upload workflow
3. ✅ Monitor logs for errors
4. ✅ Deploy to production when confident

---

## Questions?

See the detailed analysis in **LAMBDA_PERMISSIONS_AUDIT.md** for:
- Complete issue breakdown
- Security best practices
- Recommendations for each Lambda
- Production readiness checklist
