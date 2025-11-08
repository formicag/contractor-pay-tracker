# Contractor Pay Tracker

Professional contractor payment tracking system with Terraform + GitHub Actions CI/CD.

## Quick Start

```bash
# Deploy infrastructure
cd terraform
terraform init
terraform apply

# Run Flask app
cd ../flask-app
python app.py
```

## Architecture

- **Infrastructure**: Terraform (NO CloudFormation!)
- **CI/CD**: GitHub Actions automated pipeline
- **Backend**: Python 3.12 Lambda functions
- **Database**: DynamoDB single-table design
- **Storage**: S3 encrypted file storage
- **Logging**: Ultra-verbose logging on EVERY line

## Lambda Functions

All deployed via Terraform:
- `contractor-pay-file-upload-handler-development`
- `contractor-pay-file-processor-development`
- `contractor-pay-validation-engine-development`
- `contractor-pay-cleanup-handler-development`

## CI/CD Pipeline

**Location**: `.github/workflows/deploy.yml`

**Every push to main automatically:**
1. Runs Terraform validation
2. Plans infrastructure changes
3. Applies to AWS
4. Tests Lambda functions
5. Reports status

**NO MANUAL DEPLOYMENT NEEDED!**

## Logging

Ultra-verbose logging everywhere:
```
[CLEANUP_HANDLER] ==================== MODULE LOAD START ====================
[CLEANUP_HANDLER] Importing json module
[CLEANUP_HANDLER] json module imported: <module 'json'>
```

View logs:
```bash
aws logs tail /aws/lambda/{function-name} --region eu-west-2 --follow
```

## Cost

~£1.50/month total

## Status

✅ Terraform infrastructure
✅ GitHub Actions CI/CD
✅ Ultra-verbose logging
✅ All Lambda functions deployed
✅ PRODUCTION READY
