# Lambda Function IAM Permissions Audit Report

**Date:** 2025-11-08
**Environment:** development
**AWS Account:** 016164185850
**Region:** eu-west-2
**Status:** CRITICAL PERMISSION GAPS DETECTED

---

## Executive Summary

The contractor-pay-tracker system has **CRITICAL PERMISSION GAPS** that will cause runtime failures. All Lambda functions use a single shared IAM role (`contractor-pay-lambda-development`) with insufficient permissions for several operations.

**Critical Issues Found: 3**
**High Risk Issues Found: 2**
**Moderate Issues Found: 1**

---

## Shared IAM Role Configuration

**Role Name:** `contractor-pay-lambda-development`
**Account ID:** 016164185850

### Attached Policies

1. **AWSLambdaBasicExecutionRole** (AWS Managed)
   - Allows CloudWatch Logs operations
   - Permissions: `logs:CreateLogGroup`, `logs:CreateLogStream`, `logs:PutLogEvents`

2. **contractor-pay-lambda-policy** (Inline)
   - **Status:** EXISTS with narrowly scoped permissions
   - **Coverage:** Only DynamoDB and S3

### Inline Policy Content

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": ["dynamodb:*"],
      "Resource": [
        "arn:aws:dynamodb:eu-west-2:016164185850:table/contractor-pay-development",
        "arn:aws:dynamodb:eu-west-2:016164185850:table/contractor-pay-development/*"
      ]
    },
    {
      "Effect": "Allow",
      "Action": ["s3:*"],
      "Resource": [
        "arn:aws:s3:::contractor-pay-files-development-016164185850",
        "arn:aws:s3:::contractor-pay-files-development-016164185850/*"
      ]
    }
  ]
}
```

---

## Lambda Functions Analysis

### 1. File Upload Handler
- **Function Name:** `contractor-pay-file-upload-handler-development`
- **Role:** `contractor-pay-lambda-development`
- **Timeout:** 30s
- **Memory:** 512MB

#### Code Dependencies (from app.py)
```python
s3_client = boto3.client('s3')  # S3 operations ✓
sfn_client = boto3.client('stepfunctions')  # Step Functions ✗
dynamodb_client = DynamoDBClient()  # DynamoDB ✓
```

#### Operations Performed
- `s3_client.put_object()` - Upload file to S3 ✓
- `s3_client.head_object()` - Get S3 object metadata ✓
- `s3_client.get_object()` - Read S3 object ✓
- `sfn_client.start_execution()` - **START WORKFLOW** ✗ MISSING PERMISSION
- `dynamodb_client.put_item()` - Create file metadata ✓

#### Missing Permissions
```
❌ states:StartExecution
❌ states:DescribeExecution
```

**Impact:** Step Functions workflow will NOT start. File uploads will succeed but processing workflow will fail silently.

---

### 2. File Processor
- **Function Name:** `contractor-pay-file-processor-development`
- **Role:** `contractor-pay-lambda-development`
- **Timeout:** 300s (5 minutes)
- **Memory:** 1024MB

#### Code Dependencies (from app.py)
```python
s3_client = boto3.client('s3')  # S3 operations ✓
dynamodb_client = DynamoDBClient()  # DynamoDB ✓
```

#### Operations Performed
- `s3_client.download_file()` - Download files from S3 ✓
- `s3_client.get_object()` - Read S3 object ✓
- `s3_client.head_object()` - Get object metadata ✓
- `dynamodb_client.table.query()` - Query DynamoDB ✓
- `dynamodb_client.table.update_item()` - Update DynamoDB ✓
- `dynamodb_client.table.scan()` - Scan DynamoDB ✓
- `dynamodb_client.batch_writer()` - Batch write records ✓

**Status:** ✓ All permissions present (works via Step Functions invocation)

---

### 3. Validation Engine
- **Function Name:** `contractor-pay-validation-engine-development`
- **Role:** `contractor-pay-lambda-development`
- **Timeout:** 120s (2 minutes)
- **Memory:** 512MB

#### Code Dependencies (from app.py)
```python
dynamodb_client = DynamoDBClient()  # DynamoDB ✓
```

#### Operations Performed
- `dynamodb_client.table.get_item()` - Get items from DynamoDB ✓
- `dynamodb_client.table.query()` - Query DynamoDB ✓
- `dynamodb_client.table.scan()` - Scan DynamoDB ✓

**Status:** ✓ All permissions present

---

### 4. Report Generator
- **Function Name:** `contractor-pay-report-generator-development`
- **Role:** `contractor-pay-lambda-development`
- **Timeout:** 120s (2 minutes)
- **Memory:** 512MB

#### Code Dependencies (from app.py)
```python
s3_client = boto3.client('s3')  # S3 operations ✓
dynamodb_client = DynamoDBClient()  # DynamoDB ✓
```

#### Operations Performed
- `s3_client.put_object()` - Upload reports to S3 ✓
- `dynamodb_client.table.query()` - Query DynamoDB ✓
- `dynamodb_client.table.scan()` - Scan DynamoDB ✓

**Status:** ✓ All permissions present for current operations

---

### 5. Cleanup Handler
- **Function Name:** `contractor-pay-cleanup-handler-development`
- **Role:** `contractor-pay-lambda-development`
- **Timeout:** 300s (5 minutes)
- **Memory:** 256MB

#### Code Dependencies (from app.py)
```python
s3_client = boto3.client('s3')  # S3 operations ✓
dynamodb_client = DynamoDBClient()  # DynamoDB ✓
dynamodb_resource = boto3.resource('dynamodb')  # Direct table access ✓
```

#### Operations Performed
- `s3_client.list_objects_v2()` - List S3 objects (implied from code)
- `s3_client.delete_object()` - Delete S3 objects (implied from cleanup logic)
- `dynamodb_client.table.query()` - Query DynamoDB ✓
- `dynamodb_client.table.update_item()` - Update items ✓
- `table.batch_writer()` - Batch write operations ✓

**Status:** ✓ All permissions present (uses wildcard s3:* and dynamodb:*)

---

## Step Functions Integration

### Role Configuration
- **Role Name:** `contractor-pay-step-functions-development`
- **Inline Policy:** `contractor-pay-step-functions-policy`

### Permissions
```json
{
  "Effect": "Allow",
  "Action": ["lambda:InvokeFunction"],
  "Resource": ["arn:aws:lambda:eu-west-2:016164185850:function:contractor-pay-*"]
}
```

**Status:** ✓ Step Functions can invoke Lambda functions correctly

---

## Critical Issues

### ❌ ISSUE #1: FILE_UPLOAD_HANDLER - Missing Step Functions Permissions

**Severity:** CRITICAL
**Impact:** File processing workflow will not start

**Affected Function:**
- `contractor-pay-file-upload-handler-development`

**Root Cause:**
The Lambda function calls:
```python
sfn_client.start_execution(
    stateMachineArn=STATE_MACHINE_ARN,
    name=execution_name,
    input=json.dumps(sfn_input)
)
```

But the IAM role has NO permissions for Step Functions actions:
- Missing: `states:StartExecution`
- Missing: `states:DescribeExecution` (optional but recommended)

**Error Expected at Runtime:**
```
ClientError: An error occurred (AccessDenied) when calling the StartExecution
operation: User: arn:aws:iam::016164185850:role/contractor-pay-lambda-development
is not authorized to perform: states:StartExecution on resource:
arn:aws:states:eu-west-2:016164185850:stateMachine:contractor-pay-processing-development
```

**Fix Required:**
Add to `contractor-pay-lambda-policy` inline policy:
```json
{
  "Effect": "Allow",
  "Action": [
    "states:StartExecution",
    "states:DescribeExecution"
  ],
  "Resource": [
    "arn:aws:states:eu-west-2:016164185850:stateMachine:contractor-pay-*"
  ]
}
```

---

### ❌ ISSUE #2: FILE_UPLOAD_HANDLER - Missing S3 HeadObject Permission (Implicit Risk)

**Severity:** CRITICAL (Potential)
**Impact:** S3 event trigger handler may fail

**Affected Function:**
- `contractor-pay-file-upload-handler-development`

**Analysis:**
The current policy uses wildcard `s3:*` which covers all S3 permissions including:
- `s3:GetObject`
- `s3:PutObject`
- `s3:HeadObject`

**Status:** Currently protected by wildcard, but overly permissive

**Recommendation:**
Tighten to specific actions needed:
```json
{
  "Effect": "Allow",
  "Action": [
    "s3:GetObject",
    "s3:GetObjectVersion",
    "s3:HeadObject",
    "s3:PutObject"
  ],
  "Resource": "arn:aws:s3:::contractor-pay-files-development-016164185850/*"
}
```

---

### ❌ ISSUE #3: Missing Lambda-to-Lambda Invocation Permissions

**Severity:** HIGH (Future Risk)
**Impact:** If Lambda functions call each other directly, it will fail

**Current Code Analysis:**
Functions are currently invoked only by:
1. Step Functions (has proper permissions)
2. S3 events (no Lambda invocation needed)
3. API Gateway (implicit Lambda invocation)

**Future Risk:**
If any Lambda function attempts to invoke another Lambda function:
```python
lambda_client = boto3.client('lambda')
lambda_client.invoke(FunctionName='contractor-pay-*', ...)  # Will fail
```

**Fix Required (Preemptive):**
```json
{
  "Effect": "Allow",
  "Action": [
    "lambda:InvokeFunction"
  ],
  "Resource": [
    "arn:aws:lambda:eu-west-2:016164185850:function:contractor-pay-*"
  ]
}
```

---

## High Priority Issues

### ⚠️ ISSUE #4: Overly Permissive DynamoDB Policy

**Severity:** HIGH (Security)
**Impact:** Violates principle of least privilege

**Current Policy:**
```json
"Action": ["dynamodb:*"]
```

**Problem:**
This grants ALL DynamoDB actions including:
- `dynamodb:DeleteTable` ✗
- `dynamodb:DescribeBackup` ✗
- `dynamodb:UpdateTable` ✗
- And 100+ other dangerous operations

**Current Usage:** Only needs:
- `dynamodb:GetItem`
- `dynamodb:PutItem`
- `dynamodb:UpdateItem`
- `dynamodb:Query`
- `dynamodb:Scan`
- `dynamodb:BatchWriteItem`

**Recommended Fix:**
```json
{
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
}
```

---

### ⚠️ ISSUE #5: Overly Permissive S3 Policy

**Severity:** HIGH (Security)
**Impact:** Violates principle of least privilege

**Current Policy:**
```json
"Action": ["s3:*"]
```

**Problem:**
This grants ALL S3 actions including:
- `s3:DeleteBucket` ✗
- `s3:DeleteBucketPolicy` ✗
- `s3:PutBucketAcl` ✗
- And 100+ other dangerous operations

**Current Usage:** Only needs:
- `s3:GetObject`
- `s3:PutObject`
- `s3:HeadObject`

**Recommended Fix:**
```json
{
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
}
```

---

## Moderate Issues

### ⚠️ ISSUE #6: CloudWatch Logs Retention Policy Missing

**Severity:** MODERATE
**Impact:** Cleanup handler cannot manage log retention

**Code Observation:**
Template.yaml shows attempt to manage logs:
```yaml
- Statement:
    - Effect: Allow
      Action:
        - logs:PutRetentionPolicy
      Resource: '*'
```

**Actual Status:** NOT applied to Lambda role
**Affected Function:** `cleanup-handler` (if feature is enabled)

**Current Risk:** Low (feature may not be used)

---

## Permission Gap Summary Table

| Function | DynamoDB | S3 | Step Functions | Lambda-to-Lambda | Status |
|----------|----------|----|-----------------|--------------------|--------|
| file-upload-handler | ✓ | ✓ | ❌ **MISSING** | ✗ Implicit | 🔴 **FAIL** |
| file-processor | ✓ | ✓ | N/A (invoked by SFN) | ✗ Implicit | ✓ Pass |
| validation-engine | ✓ | N/A | N/A (invoked by SFN) | ✗ Implicit | ✓ Pass |
| report-generator | ✓ | ✓ | N/A (invoked by API) | ✗ Implicit | ✓ Pass |
| cleanup-handler | ✓ | ✓ | N/A (invoked by CloudWatch) | ✗ Implicit | ✓ Pass |

---

## Runtime Failure Scenarios

### Scenario 1: User Uploads File via API (WILL FAIL)

**Steps:**
1. User calls POST `/api/v1/upload`
2. file-upload-handler receives request
3. File uploaded to S3 ✓
4. Metadata stored in DynamoDB ✓
5. **FAIL:** Attempts to call `sfn_client.start_execution()` → AccessDenied

**Error Message:**
```
ClientError: An error occurred (AccessDeniedException) when calling the
StartExecution operation: User: arn:aws:iam::016164185850:role/
contractor-pay-lambda-development is not authorized to perform:
states:StartExecution on resource: arn:aws:states:eu-west-2:...
```

**User Impact:** File appears uploaded but processing never starts

---

### Scenario 2: File Uploaded Directly to S3 (PARTIAL FAILURE)

**Steps:**
1. File uploaded to S3 bucket
2. S3 event triggers file-upload-handler ✓
3. File metadata created in DynamoDB ✓
4. **FAIL:** Attempts to start Step Functions workflow → AccessDenied

**User Impact:** File metadata exists but never processed

---

### Scenario 3: Step Functions Workflow Execution

When Step Functions attempts to invoke Lambda functions:

**Result:** ✓ Works correctly
- Step Functions role has proper permissions
- Can invoke file-processor and validation-engine

---

## Recommended Fixes (Priority Order)

### 🔴 CRITICAL - Must Fix Before Production

**Add Step Functions Permissions to Lambda Role:**

```bash
# Option 1: Update inline policy programmatically
aws iam put-role-policy \
  --role-name contractor-pay-lambda-development \
  --policy-name contractor-pay-lambda-policy \
  --policy-document file://updated-policy.json
```

**updated-policy.json:**
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
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
```

**Option 2: Use Terraform (Recommended)**

Update `/terraform/main.tf` line 211-240:
```hcl
resource "aws_iam_role_policy" "lambda_policy" {
  name = "contractor-pay-lambda-policy"
  role = aws_iam_role.lambda_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "dynamodb:GetItem",
          "dynamodb:PutItem",
          "dynamodb:UpdateItem",
          "dynamodb:Query",
          "dynamodb:Scan",
          "dynamodb:BatchWriteItem"
        ]
        Resource = [
          aws_dynamodb_table.contractor_pay.arn,
          "${aws_dynamodb_table.contractor_pay.arn}/index/*"
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:GetObjectVersion",
          "s3:HeadObject",
          "s3:PutObject",
          "s3:ListBucket",
          "s3:DeleteObject"
        ]
        Resource = [
          aws_s3_bucket.pay_files.arn,
          "${aws_s3_bucket.pay_files.arn}/*"
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "states:StartExecution",
          "states:DescribeExecution"
        ]
        Resource = aws_sfn_state_machine.contractor_pay_workflow.arn
      }
    ]
  })
}
```

Then add the Step Functions execution policy (already partially correct):
```hcl
resource "aws_iam_role_policy" "lambda_step_functions_policy" {
  name = "contractor-pay-lambda-step-functions-policy"
  role = aws_iam_role.lambda_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "states:StartExecution",
          "states:DescribeExecution"
        ]
        Resource = [
          aws_sfn_state_machine.contractor_pay_workflow.arn,
          "${aws_sfn_state_machine.contractor_pay_workflow.arn}:*"
        ]
      }
    ]
  })
}
```

### 🟡 HIGH - Recommended Before Production

**Implement Least Privilege DynamoDB/S3 Permissions**

Replace wildcard `*` actions with specific needed actions (shown above).

---

## Testing Recommendations

### Test Case 1: Verify Step Functions Permission
```bash
aws lambda invoke \
  --function-name contractor-pay-file-upload-handler-development \
  --payload '{"test": true}' \
  response.json
```

**Expected:** File metadata created and Step Functions execution started

---

### Test Case 2: Verify End-to-End Workflow
```bash
# 1. Upload file via API
curl -X POST http://api-endpoint/api/v1/upload \
  -H "Content-Type: application/json" \
  -d @test-file.json

# 2. Verify Step Functions execution started
aws stepfunctions list-executions \
  --state-machine-arn arn:aws:states:eu-west-2:016164185850:stateMachine:contractor-pay-processing-development

# 3. Verify file processing completed
aws dynamodb get-item \
  --table-name contractor-pay-development \
  --key '{"PK":{"S":"FILE#<file-id>"},"SK":{"S":"METADATA"}}'
```

---

## Deployment Impact

### Current State
- ❌ **Production Ready:** NO
- 🔴 **Critical Blocker:** Step Functions invocation will fail

### After CRITICAL Fix
- ✓ **Production Ready:** MAYBE (with HIGH priority fixes recommended)
- Requires: Security policy review (least privilege)

### After ALL Fixes
- ✓ **Production Ready:** YES
- Security: Best practices implemented

---

## Additional Notes

### Policy Comparison: Expected vs Actual

**Expected (from template.yaml):**
```yaml
Policies:
  - S3CrudPolicy:
      BucketName: !Ref PayFilesBucket
  - DynamoDBCrudPolicy:
      TableName: !Ref ContractorPayTable
  - Statement:
      - Effect: Allow
        Action:
          - states:StartExecution
        Resource: !Sub "arn:aws:states:${AWS::Region}:${AWS::AccountId}:stateMachine:contractor-pay-processing-${Environment}"
```

**Actual (in Terraform):**
```hcl
# Missing states:StartExecution in lambda_policy
# Has it in separate lambda_step_functions_policy but that policy may not be applied
```

### File Locations

- **SAM Template:** `/Users/gianlucaformica/Projects/contractor-pay-tracker/backend/template.yaml`
- **Terraform Config:** `/Users/gianlucaformica/Projects/contractor-pay-tracker/terraform/main.tf`
- **Lambda Functions:** `/Users/gianlucaformica/Projects/contractor-pay-tracker/backend/functions/`

---

## Conclusion

The contractor-pay-tracker Lambda functions have **CRITICAL permission gaps** that will cause immediate runtime failures when attempting to start Step Functions workflows. The file-upload-handler cannot trigger the processing pipeline due to missing `states:StartExecution` permissions.

**Immediate Action Required:**
1. Add Step Functions permissions to Lambda IAM role
2. Test end-to-end workflow
3. Implement least-privilege security improvements

**Timeline:** Fix before any file upload testing or production deployment.
