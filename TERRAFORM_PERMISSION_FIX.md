# Terraform Fix for Lambda IAM Permissions

## How to Fix via Terraform

If you prefer to fix permissions through Infrastructure as Code (recommended for long-term), update your Terraform configuration.

---

## Files to Update

**File:** `/terraform/main.tf`

---

## Change 1: Update Lambda Policy (Lines 211-240)

### Current Code (BROKEN)
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
          "dynamodb:*"
        ]
        Resource = [
          aws_dynamodb_table.contractor_pay.arn,
          "${aws_dynamodb_table.contractor_pay.arn}/*"
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "s3:*"
        ]
        Resource = [
          aws_s3_bucket.pay_files.arn,
          "${aws_s3_bucket.pay_files.arn}/*"
        ]
      }
    ]
  })
}
```

**Problems:**
- ❌ Missing Step Functions permissions
- ❌ Overly permissive DynamoDB (`dynamodb:*` includes deletion)
- ❌ Overly permissive S3 (`s3:*` includes bucket deletion)

### Fixed Code
```hcl
resource "aws_iam_role_policy" "lambda_policy" {
  name = "contractor-pay-lambda-policy"
  role = aws_iam_role.lambda_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "DynamoDBAccess"
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
        Sid    = "S3Access"
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
        Sid    = "StepFunctionsAccess"
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

**Improvements:**
- ✅ Added Step Functions permissions (CRITICAL FIX)
- ✅ Replaced wildcard DynamoDB with specific actions
- ✅ Replaced wildcard S3 with specific actions
- ✅ Follows AWS security best practices (least privilege)

---

## Change 2: Add Lambda-to-Lambda Permission (NEW RESOURCE)

### Add This New Resource (After line 814)

```hcl
# Lambda policy to allow Lambda functions to invoke each other (future-proofing)
resource "aws_iam_role_policy" "lambda_invoke_policy" {
  name = "contractor-pay-lambda-invoke-policy"
  role = aws_iam_role.lambda_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "LambdaInvocation"
        Effect = "Allow"
        Action = [
          "lambda:InvokeFunction"
        ]
        Resource = [
          "arn:aws:lambda:${var.aws_region}:${data.aws_caller_identity.current.account_id}:function:contractor-pay-*"
        ]
      }
    ]
  })
}
```

**Why:**
- Future-proofing if Lambda functions need to invoke each other
- Consistent with Step Functions' ability to invoke Lambda

---

## Deployment Instructions

### Step 1: Update the Terraform File

Edit `/terraform/main.tf`:

1. Find the `aws_iam_role_policy "lambda_policy"` resource (around line 211)
2. Replace the entire resource with the fixed code above
3. Add the new `aws_iam_role_policy "lambda_invoke_policy"` resource

### Step 2: Validate Terraform

```bash
cd /Users/gianlucaformica/Projects/contractor-pay-tracker/terraform

# Validate syntax
terraform validate
# Output: Success! The configuration is valid.

# Preview changes
terraform plan -var=environment=development

# Expected output:
# - aws_iam_role_policy.lambda_policy will be updated
# - aws_iam_role_policy.lambda_invoke_policy will be created
```

### Step 3: Apply Changes

```bash
# Apply with auto-approve (or remove -auto-approve to review)
terraform apply -var=environment=development -auto-approve

# Expected output:
# ✓ aws_iam_role_policy.lambda_policy: Modifications complete after Xs
# ✓ aws_iam_role_policy.lambda_invoke_policy: Creation complete after Xs
```

### Step 4: Verify

```bash
# Check the applied policy
aws iam get-role-policy \
  --role-name contractor-pay-lambda-development \
  --policy-name contractor-pay-lambda-policy \
  --profile AdministratorAccess-016164185850

# Should show the updated policy with StepFunctionsAccess statement
```

---

## Complete Diff (For Reference)

```diff
resource "aws_iam_role_policy" "lambda_policy" {
  name = "contractor-pay-lambda-policy"
  role = aws_iam_role.lambda_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
+       Sid    = "DynamoDBAccess"
        Effect = "Allow"
        Action = [
-         "dynamodb:*"
+         "dynamodb:GetItem",
+         "dynamodb:PutItem",
+         "dynamodb:UpdateItem",
+         "dynamodb:Query",
+         "dynamodb:Scan",
+         "dynamodb:BatchWriteItem"
        ]
        Resource = [
          aws_dynamodb_table.contractor_pay.arn,
-         "${aws_dynamodb_table.contractor_pay.arn}/*"
+         "${aws_dynamodb_table.contractor_pay.arn}/index/*"
        ]
      },
      {
+       Sid    = "S3Access"
        Effect = "Allow"
        Action = [
-         "s3:*"
+         "s3:GetObject",
+         "s3:GetObjectVersion",
+         "s3:HeadObject",
+         "s3:PutObject",
+         "s3:ListBucket",
+         "s3:DeleteObject"
        ]
        Resource = [
          aws_s3_bucket.pay_files.arn,
          "${aws_s3_bucket.pay_files.arn}/*"
        ]
      },
+     {
+       Sid    = "StepFunctionsAccess"
+       Effect = "Allow"
+       Action = [
+         "states:StartExecution",
+         "states:DescribeExecution"
+       ]
+       Resource = [
+         aws_sfn_state_machine.contractor_pay_workflow.arn,
+         "${aws_sfn_state_machine.contractor_pay_workflow.arn}:*"
+       ]
+     }
    ]
  })
}

+ # Lambda policy to allow Lambda functions to invoke each other (future-proofing)
+ resource "aws_iam_role_policy" "lambda_invoke_policy" {
+   name = "contractor-pay-lambda-invoke-policy"
+   role = aws_iam_role.lambda_role.id
+
+   policy = jsonencode({
+     Version = "2012-10-17"
+     Statement = [
+       {
+         Sid    = "LambdaInvocation"
+         Effect = "Allow"
+         Action = [
+           "lambda:InvokeFunction"
+         ]
+         Resource = [
+           "arn:aws:lambda:${var.aws_region}:${data.aws_caller_identity.current.account_id}:function:contractor-pay-*"
+         ]
+       }
+     ]
+   })
+ }
```

---

## Variables Already Available

The Terraform configuration already has these variables defined:

```hcl
# From variables.tf
variable "aws_region" {
  default = "eu-west-2"
}

variable "environment" {
  default = "development"
}

# From data sources in main.tf
data "aws_caller_identity" "current" {}  # Provides account ID
```

So no additional variables need to be added.

---

## Pre-Deployment Checklist

Before applying:

- [ ] Read the diff above
- [ ] Understand each permission change
- [ ] Verify variable values: `aws_region`, account ID
- [ ] Have AWS credentials set up
- [ ] Can access Terraform state

---

## Post-Deployment Testing

After Terraform apply:

```bash
# 1. Test file upload
curl -X POST https://your-api-endpoint/api/v1/upload \
  -H "Content-Type: application/json" \
  -d '{
    "filename": "test.xlsx",
    "file_content_base64": "...",
    "uploaded_by": "test"
  }'

# 2. Check Step Functions execution
aws stepfunctions list-executions \
  --state-machine-arn arn:aws:states:eu-west-2:016164185850:stateMachine:contractor-pay-workflow-development \
  --status-filter RUNNING \
  --profile AdministratorAccess-016164185850

# 3. Watch Lambda logs
aws logs tail /aws/lambda/contractor-pay-file-upload-handler-development \
  --follow \
  --profile AdministratorAccess-016164185850
```

---

## Rollback (If Needed)

If something goes wrong:

```bash
# See previous version
terraform plan -var=environment=development

# Revert to previous code in git
git checkout HEAD~ terraform/main.tf

# Re-apply
terraform apply -var=environment=development -auto-approve
```

---

## Why Use Terraform for This?

1. **Infrastructure as Code** - Changes are tracked in version control
2. **Repeatable** - Same configuration works across environments (dev, prod)
3. **Documented** - Policy logic is clear and reviewable
4. **Reversible** - Easy to rollback if issues found
5. **Consistent** - No manual AWS console mistakes

---

## Alternative: SAM Template Fix

If you prefer to use the SAM template instead (`backend/template.yaml`):

Find the `FileUploadHandlerFunction` resource and update its `Policies` section:

```yaml
FileUploadHandlerFunction:
  Type: AWS::Serverless::Function
  Properties:
    # ... existing properties ...
    Policies:
      - S3CrudPolicy:
          BucketName: !Ref PayFilesBucket
      - DynamoDBCrudPolicy:
          TableName: !Ref ContractorPayTable
      - Statement:
          - Effect: Allow
            Action:
              - states:StartExecution
              - states:DescribeExecution
            Resource: !Sub "arn:aws:states:${AWS::Region}:${AWS::AccountId}:stateMachine:contractor-pay-*"
```

Then redeploy:

```bash
sam build
sam deploy
```

---

## Comparison: Manual vs Terraform vs SAM

| Method | Speed | Repeatability | Auditability | Recommended |
|--------|-------|--------------|--------------|-------------|
| Manual (AWS Console) | Slow | ❌ No | ❌ No | ❌ No |
| Shell Script | Fast | ✓ Yes | ⚠️ Partial | ⚠️ Quick fix only |
| Terraform | Medium | ✓ Yes | ✓ Yes | ✅ Best |
| SAM Template | Medium | ✓ Yes | ✓ Yes | ✅ Also good |

**Recommendation:** Use Terraform or SAM for long-term maintainability, but use the shell script for immediate fix.

---

## Questions?

See related files:
- **LAMBDA_PERMISSIONS_AUDIT.md** - Detailed technical analysis
- **PERMISSION_FIX_SUMMARY.md** - Quick reference guide
- **fix-lambda-permissions.sh** - Automated shell script fix
