# Deployment Guide

Complete guide to deploying the Contractor Pay Tracker to AWS.

## Prerequisites

1. **AWS CLI configured**
   ```bash
   aws configure
   # Or for SSO:
   aws sso login --profile your-profile
   ```

2. **AWS SAM CLI installed**
   ```bash
   # macOS
   brew install aws-sam-cli

   # Verify
   sam --version
   ```

3. **Python 3.12** installed
   ```bash
   python3 --version
   ```

---

## Quick Deploy (First Time)

### Step 1: Login to AWS

```bash
# For SSO
aws sso login

# Or for standard credentials
aws configure
```

### Step 2: Build SAM Application

```bash
cd backend
sam build
```

Expected output:
```
Build Succeeded

Built Artifacts  : .aws-sam/build
Built Template   : .aws-sam/build/template.yaml
```

### Step 3: Deploy with Guided Setup

```bash
sam deploy --guided
```

**Answer the prompts:**
```
Stack Name []: contractor-pay-tracker-dev
AWS Region []: eu-west-2
Parameter Environment [development]: development
Parameter LogLevel [INFO]: INFO
Confirm changes before deploy [Y/n]: Y
Allow SAM CLI IAM role creation [Y/n]: Y
Disable rollback [y/N]: N
Save arguments to configuration file [Y/n]: Y
SAM configuration file [samconfig.toml]: samconfig.toml
SAM configuration environment [default]: default
```

### Step 4: Wait for Deployment

This will take **5-10 minutes** for the first deployment.

You'll see:
```
CloudFormation stack changeset
-----------------------------------------------------------------
Operation    LogicalResourceId              ResourceType
-----------------------------------------------------------------
+ Add        ContractorPayTable             AWS::DynamoDB::Table
+ Add        PayFilesBucket                 AWS::S3::Bucket
+ Add        FileUploadHandlerFunction      AWS::Lambda::Function
...
-----------------------------------------------------------------

Deploy this changeset? [y/N]: y

Deploying with following values
Stack name                   : contractor-pay-tracker-dev
Region                       : eu-west-2
...

CloudFormation outputs from deployed stack
-----------------------------------------------------------------
Outputs
-----------------------------------------------------------------
Key                 ApiEndpoint
Description         API Gateway endpoint URL
Value               https://abc123.execute-api.eu-west-2.amazonaws.com/Prod

Key                 DynamoDBTableName
Description         DynamoDB table name
Value               contractor-pay-development

Key                 S3BucketName
Description         S3 bucket for file storage
Value               contractor-pay-files-development-123456789012
-----------------------------------------------------------------

Successfully created/updated stack - contractor-pay-tracker-dev in eu-west-2
```

---

## Step 5: Seed the Database

```bash
cd seed-data

# Install dependencies (if not already installed)
pip install boto3

# Run seed script
python seed_dynamodb.py --stack-name contractor-pay-tracker-dev
```

Expected output:
```
✅ Seeding DynamoDB table: contractor-pay-development

📊 Seeding 23 contractors...
✅ Seeded 23 contractors

🏢 Seeding 6 umbrella companies...
✅ Seeded 6 umbrella companies

👔 Seeding 4 permanent staff members...
✅ Seeded 4 permanent staff

📅 Seeding 13 pay periods...
✅ Seeded 13 periods

🔗 Seeding contractor-umbrella associations...
✅ Including Donna Smith in both NASA (812299) and PARASOL (129700)
✅ Seeded 27 associations

⚙️  Seeding system parameters...
✅ Seeded 5 parameters

✅ Database seeding complete!
```

---

## Step 6: Get Stack Outputs

```bash
cd backend

aws cloudformation describe-stacks \
  --stack-name contractor-pay-tracker-dev \
  --query 'Stacks[0].Outputs' \
  --output table
```

Save these values for your Flask app!

---

## Update Flask App Configuration

### Create .env file

```bash
cd flask-app
cp .env.example .env
```

### Edit .env with your stack outputs

```env
# Flask Configuration
FLASK_ENV=development
SECRET_KEY=your-random-secret-key-here

# AWS Configuration
AWS_REGION=eu-west-2
AWS_PROFILE=default

# From CloudFormation Outputs:
DYNAMODB_TABLE_NAME=contractor-pay-development
S3_BUCKET_NAME=contractor-pay-files-development-123456789012
API_GATEWAY_URL=https://abc123.execute-api.eu-west-2.amazonaws.com/Prod
```

---

## Subsequent Deployments

After the first deployment, you can use:

```bash
cd backend
sam build && sam deploy
```

No need for `--guided` - it will use `samconfig.toml`

---

## Deploy to Production

```bash
cd backend

# Build
sam build

# Deploy to production
sam deploy \
  --stack-name contractor-pay-tracker-prod \
  --parameter-overrides Environment=production LogLevel=WARNING \
  --no-confirm-changeset

# Seed production database
cd seed-data
python seed_dynamodb.py --stack-name contractor-pay-tracker-prod
```

---

## CI/CD with GitHub Actions

### Setup AWS Credentials for GitHub

1. **Create IAM OIDC Provider for GitHub**
   ```bash
   aws iam create-open-id-connect-provider \
     --url https://token.actions.githubusercontent.com \
     --client-id-list sts.amazonaws.com \
     --thumbprint-list 6938fd4d98bab03faadb97b34396831e3780aea1
   ```

2. **Create IAM Role for GitHub Actions**

   Create `github-actions-role.json`:
   ```json
   {
     "Version": "2012-10-17",
     "Statement": [
       {
         "Effect": "Allow",
         "Principal": {
           "Federated": "arn:aws:iam::YOUR_ACCOUNT_ID:oidc-provider/token.actions.githubusercontent.com"
         },
         "Action": "sts:AssumeRoleWithWebIdentity",
         "Condition": {
           "StringEquals": {
             "token.actions.githubusercontent.com:aud": "sts.amazonaws.com"
           },
           "StringLike": {
             "token.actions.githubusercontent.com:sub": "repo:YOUR_GITHUB_USERNAME/contractor-pay-tracker:*"
           }
         }
       }
     ]
   }
   ```

   ```bash
   # Create role
   aws iam create-role \
     --role-name GitHubActionsDeployRole \
     --assume-role-policy-document file://github-actions-role.json

   # Attach policies
   aws iam attach-role-policy \
     --role-name GitHubActionsDeployRole \
     --policy-arn arn:aws:iam::aws:policy/AdministratorAccess
   ```

3. **Add GitHub Secret**

   Go to: `https://github.com/YOUR_USERNAME/contractor-pay-tracker/settings/secrets/actions`

   Add secret:
   - Name: `AWS_ROLE_ARN`
   - Value: `arn:aws:iam::YOUR_ACCOUNT_ID:role/GitHubActionsDeployRole`

### Trigger Deployment

**Automatic (on push to main):**
```bash
git add -A
git commit -m "Deploy to AWS"
git push origin main
```

**Manual (via GitHub UI):**
1. Go to Actions tab
2. Select "Deploy to AWS"
3. Click "Run workflow"
4. Choose environment (development/production)
5. Click "Run workflow"

---

## Monitoring Deployments

### View Logs

```bash
# View Lambda logs
sam logs --stack-name contractor-pay-tracker-dev --tail

# View specific function logs
aws logs tail /aws/lambda/contractor-pay-file-upload-handler-dev --follow
```

### View CloudFormation Events

```bash
aws cloudformation describe-stack-events \
  --stack-name contractor-pay-tracker-dev \
  --max-items 10
```

### View Stack Resources

```bash
aws cloudformation describe-stack-resources \
  --stack-name contractor-pay-tracker-dev
```

---

## Troubleshooting

### Build Fails

**Error: Python version mismatch**
```
Error: Binary validation failed for python
```

**Solution:**
Install Python 3.12:
```bash
brew install python@3.12
```

### Deploy Fails

**Error: Stack already exists**
```bash
# Delete stack and redeploy
aws cloudformation delete-stack --stack-name contractor-pay-tracker-dev
aws cloudformation wait stack-delete-complete --stack-name contractor-pay-tracker-dev
sam build && sam deploy --guided
```

**Error: Insufficient permissions**

Check your AWS credentials:
```bash
aws sts get-caller-identity
```

### Seed Fails

**Error: Table not found**

Wait for stack to complete:
```bash
aws cloudformation wait stack-create-complete --stack-name contractor-pay-tracker-dev
```

---

## Cost Monitoring

### View Current Costs

```bash
# DynamoDB table cost
aws dynamodb describe-table \
  --table-name contractor-pay-development \
  --query 'Table.TableSizeBytes' \
  --output text

# S3 bucket size
aws s3 ls s3://contractor-pay-files-development-ACCOUNT_ID --recursive --summarize
```

### Set Up Billing Alerts

1. Go to AWS Budgets: https://console.aws.amazon.com/billing/home#/budgets
2. Create budget
3. Set amount: £5.00
4. Alert threshold: 80%
5. Email: your@email.com

---

## Rollback

### To Previous Version

```bash
# View stack history
aws cloudformation list-stack-resources \
  --stack-name contractor-pay-tracker-dev

# Rollback to previous version
aws cloudformation cancel-update-stack \
  --stack-name contractor-pay-tracker-dev
```

### Complete Teardown

```bash
# Delete stack (keeps S3 bucket by default)
aws cloudformation delete-stack --stack-name contractor-pay-tracker-dev

# Wait for deletion
aws cloudformation wait stack-delete-complete --stack-name contractor-pay-tracker-dev

# Manually delete S3 bucket if needed
aws s3 rb s3://contractor-pay-files-development-ACCOUNT_ID --force
```

---

## Next Steps

1. ✅ Deploy infrastructure
2. ✅ Seed database
3. ✅ Update Flask app .env
4. 🚀 Test file upload
5. 📊 Monitor costs
6. 🔄 Set up GitHub Actions

---

## Quick Commands Reference

```bash
# Build
cd backend && sam build

# Deploy
sam deploy

# Logs
sam logs --stack-name contractor-pay-tracker-dev --tail

# Outputs
aws cloudformation describe-stacks \
  --stack-name contractor-pay-tracker-dev \
  --query 'Stacks[0].Outputs'

# Seed
cd seed-data && python seed_dynamodb.py --stack-name contractor-pay-tracker-dev

# Delete
aws cloudformation delete-stack --stack-name contractor-pay-tracker-dev
```
