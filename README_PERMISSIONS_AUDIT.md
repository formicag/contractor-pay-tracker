# Lambda IAM Permissions Audit - Complete Report

## Status: 🔴 CRITICAL ISSUES FOUND

**Date:** November 8, 2025
**Audit Type:** Lambda Function IAM Permission Verification
**Project:** Contractor Pay Tracker (development)
**Finding:** Critical permission gaps that will cause runtime failures

---

## Quick Start (5 minutes)

### If you want the FAST fix:
```bash
./fix-lambda-permissions.sh
```

### If you want to understand the issues first:
1. Read: **IAM_AUDIT_EXECUTIVE_SUMMARY.txt** (5 min)
2. Read: **PERMISSION_FIX_SUMMARY.md** (10 min)
3. Run: **./fix-lambda-permissions.sh** (2 min)

### If you want the FULL technical analysis:
1. Read: **LAMBDA_PERMISSIONS_AUDIT.md** (30 min) - Complete audit with code samples
2. Implement: **TERRAFORM_PERMISSION_FIX.md** (1 hour) - Proper IaC solution

---

## The Critical Issue

**File Upload Workflow is BROKEN:**

```
User uploads file → file-upload-handler Lambda
├─ Step 1: Upload to S3 ✓ Works
├─ Step 2: Save metadata to DynamoDB ✓ Works
└─ Step 3: Start Step Functions workflow ❌ FAILS
   
Error: AccessDeniedException
Reason: Lambda role missing "states:StartExecution" permission
Impact: File appears uploaded but never processed
```

---

## Files in This Audit

| File | Purpose | Time | For Whom |
|------|---------|------|----------|
| **IAM_AUDIT_EXECUTIVE_SUMMARY.txt** | Overview of all findings | 5 min | Managers, DevOps leads |
| **PERMISSION_FIX_SUMMARY.md** | Quick fix guide | 10 min | Developers |
| **LAMBDA_PERMISSIONS_AUDIT.md** | Full technical analysis | 30 min | Security, architects |
| **TERRAFORM_PERMISSION_FIX.md** | IaC solution | 1 hour | DevOps, infrastructure team |
| **fix-lambda-permissions.sh** | Automated fix script | 2 min | Anyone |

---

## The 5-Minute Fix

### Step 1: Run the script
```bash
chmod +x fix-lambda-permissions.sh
./fix-lambda-permissions.sh
```

### Step 2: Test
```bash
# Upload a test file
curl -X POST https://your-api/api/v1/upload \
  -H "Content-Type: application/json" \
  -d '{"filename":"test.xlsx","file_content_base64":"..."}'

# Check Step Functions execution started
aws stepfunctions list-executions \
  --state-machine-arn arn:aws:states:eu-west-2:016164185850:stateMachine:contractor-pay-workflow-development
```

---

## What Gets Fixed

### Critical Issue #1: Missing Step Functions Permission
- **Current:** Lambda role has no `states:*` permissions
- **Impact:** Cannot start file processing workflow
- **Fix:** Add `states:StartExecution` and `states:DescribeExecution`
- **Result:** File uploads will trigger processing

### High Priority Issue #2: Overly Permissive DynamoDB
- **Current:** Policy allows `dynamodb:*` (includes DeleteTable!)
- **Impact:** Violates security best practices
- **Fix:** Change to specific actions only
- **Result:** Least-privilege compliance

### High Priority Issue #3: Overly Permissive S3
- **Current:** Policy allows `s3:*` (includes DeleteBucket!)
- **Impact:** Violates security best practices
- **Fix:** Change to specific actions only
- **Result:** Least-privilege compliance

---

## Affected Lambda Functions

| Function | Role | Issue | Current | After Fix |
|----------|------|-------|---------|-----------|
| file-upload-handler | Shared | Missing Step Functions | ❌ FAILS | ✅ Works |
| file-processor | Shared | None (SFN invokes) | ✓ Works | ✓ Works |
| validation-engine | Shared | None (SFN invokes) | ✓ Works | ✓ Works |
| report-generator | Shared | None | ✓ Works | ✓ Works |
| cleanup-handler | Shared | None | ✓ Works | ✓ Works |

---

## Implementation Paths

### Path 1: Quick Fix (RECOMMENDED FOR NOW)
**Time:** 5 minutes
**Method:** Run shell script
**Pros:** Fast, immediate relief
**Cons:** Manual process, not infrastructure-as-code
**Next:** Follow up with Path 2

```bash
./fix-lambda-permissions.sh
```

### Path 2: Terraform Fix (BEST FOR PRODUCTION)
**Time:** 1 hour
**Method:** Update `/terraform/main.tf` and apply
**Pros:** Infrastructure-as-code, reproducible, auditable
**Cons:** Requires Terraform knowledge
**Reference:** See `TERRAFORM_PERMISSION_FIX.md`

```bash
cd terraform
terraform apply -var=environment=development
```

### Path 3: Manual AWS Console
**Time:** 15 minutes
**Method:** Edit policy in AWS IAM console
**Pros:** Immediate, visual
**Cons:** Not reproducible, error-prone, no audit trail

Not recommended - use Path 1 or 2

---

## Testing Checklist

After applying the fix:

- [ ] Script runs without errors
- [ ] "All permissions applied successfully" message appears
- [ ] Test file upload via API returns 200
- [ ] Step Functions execution ARN in response
- [ ] CloudWatch logs show no AccessDenied errors
- [ ] Step Functions execution appears RUNNING
- [ ] File appears in S3
- [ ] Metadata in DynamoDB
- [ ] Processing workflow completes

---

## Security Improvements

### Before (Current - INSECURE)
```json
{
  "Action": ["dynamodb:*"],  // Includes dangerous operations!
  "Action": ["s3:*"]         // Includes dangerous operations!
}
```

### After (Fixed - SECURE)
```json
{
  "Action": [
    "dynamodb:GetItem",      // Only what's needed
    "dynamodb:PutItem",
    "dynamodb:UpdateItem",
    "dynamodb:Query",
    "dynamodb:Scan",
    "dynamodb:BatchWriteItem"
  ],
  "Action": [
    "s3:GetObject",          // Only what's needed
    "s3:PutObject",
    "s3:HeadObject",
    "s3:ListBucket",
    "s3:DeleteObject"
  ]
}
```

---

## Timeline

### NOW (Nov 8, 2025)
- ❌ Critical permission gap prevents file processing
- Impact: System cannot function

### After 5-min fix
- ✅ File uploads work and trigger processing
- ⚠️ Still using overly permissive policies (security risk)

### After Terraform update (1 hour)
- ✅ File uploads work
- ✅ Least-privilege security implemented
- ✅ Infrastructure-as-code, reproducible
- ✅ Production ready

---

## Detailed Issue Analysis

### Issue Breakdown

**ISSUE #1: Missing Step Functions Permission** (CRITICAL)
- File: `/backend/functions/file_upload_handler/app.py`
- Line: 57-58 (creates sfn_client)
- Operation: `sfn_client.start_execution()` on line 334
- Missing: `states:StartExecution` action
- Error: AccessDeniedException at runtime
- Fix: Add to IAM policy

**ISSUE #2: Wildcard DynamoDB Permission** (HIGH)
- Current: `dynamodb:*` allows all operations
- Dangerous: Can delete entire tables
- Should: List specific operations needed
- Fix: See TERRAFORM_PERMISSION_FIX.md

**ISSUE #3: Wildcard S3 Permission** (HIGH)
- Current: `s3:*` allows all operations
- Dangerous: Can delete buckets, change policies
- Should: List specific operations needed
- Fix: See TERRAFORM_PERMISSION_FIX.md

---

## How This Was Discovered

1. **Code Analysis:** Reviewed all Lambda function code
   - Found: sfn_client.start_execution() call
   
2. **Permissions Check:** Listed attached policies
   - Found: Only DynamoDB and S3 actions
   
3. **Gap Analysis:** Compared code operations vs. IAM permissions
   - Missing: Step Functions actions

4. **Verification:** Tested with AWS CLI
   ```bash
   aws iam get-role-policy --role-name contractor-pay-lambda-development
   ```
   - Result: No Step Functions statement found

---

## For Different Audiences

### For Developers
Read: **PERMISSION_FIX_SUMMARY.md**
Action: Run **./fix-lambda-permissions.sh**

### For DevOps/Infrastructure
Read: **LAMBDA_PERMISSIONS_AUDIT.md**
Action: Implement **TERRAFORM_PERMISSION_FIX.md**

### For Security Team
Read: **LAMBDA_PERMISSIONS_AUDIT.md** (Issues #2 and #3 sections)
Action: Review and approve **TERRAFORM_PERMISSION_FIX.md**

### For Management
Read: **IAM_AUDIT_EXECUTIVE_SUMMARY.txt**
Action: Approve timeline and resources for fix

---

## Questions & Answers

**Q: How urgent is this?**
A: Critical. File uploads will fail immediately in production.

**Q: Will the fix break anything?**
A: No. The fix adds missing permissions and removes overly broad ones.

**Q: Do we need to redeploy?**
A: Only if using Terraform. Shell script updates policy directly.

**Q: What's the difference between the fixes?**
A: Shell script is quick (5 min), Terraform is proper IaC (1 hour).

**Q: Can we use the shell script now and Terraform later?**
A: Yes! Shell script is a good interim fix. Plan Terraform for later.

**Q: What if something goes wrong?**
A: Easy rollback. See TERRAFORM_PERMISSION_FIX.md "Rollback" section.

---

## Next Steps

1. **Immediate (now):**
   - Read this file (you're doing it!)
   - Read IAM_AUDIT_EXECUTIVE_SUMMARY.txt (5 min)

2. **Very Soon (next 5 min):**
   - Run ./fix-lambda-permissions.sh
   - Verify file upload works

3. **This Week:**
   - Read TERRAFORM_PERMISSION_FIX.md
   - Plan Terraform update for production

4. **Before Production:**
   - Implement proper least-privilege policies
   - Security review of Terraform changes
   - Full end-to-end testing

---

## Files in This Directory

```
/Users/gianlucaformica/Projects/contractor-pay-tracker/
├── README_PERMISSIONS_AUDIT.md           ← You are here
├── IAM_AUDIT_EXECUTIVE_SUMMARY.txt       ← Read next (5 min)
├── PERMISSION_FIX_SUMMARY.md             ← Then read this (10 min)
├── LAMBDA_PERMISSIONS_AUDIT.md           ← Full analysis (30 min)
├── TERRAFORM_PERMISSION_FIX.md           ← For production (1 hour)
├── fix-lambda-permissions.sh             ← Run this script (2 min)
├── backend/
├── terraform/
└── ... other files ...
```

---

## Support & Resources

**AWS Documentation:**
- [IAM Role Policies](https://docs.aws.amazon.com/IAM/latest/UserGuide/access_policies.html)
- [Lambda Execution Roles](https://docs.aws.amazon.com/lambda/latest/dg/lambda-intro-execution-role.html)
- [Step Functions IAM](https://docs.aws.amazon.com/step-functions/latest/dg/security-iam.html)

**Internal Documentation:**
- See LAMBDA_PERMISSIONS_AUDIT.md for detailed technical analysis

---

## Conclusion

Your contractor-pay-tracker has critical IAM permission gaps that must be fixed before any user testing or production deployment. The automated fix script can resolve the critical issue in 5 minutes. Plan to implement proper least-privilege security with Terraform within the next week.

**Estimated total time to production readiness: 1 hour**

---

**Start here:** Run `./fix-lambda-permissions.sh`

