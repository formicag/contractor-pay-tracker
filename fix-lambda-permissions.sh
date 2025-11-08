#!/bin/bash

# Lambda IAM Permissions Fix Script
# Fixes critical permission gaps identified in LAMBDA_PERMISSIONS_AUDIT.md
#
# Usage: ./fix-lambda-permissions.sh <aws-profile> <account-id> <region>
# Example: ./fix-lambda-permissions.sh AdministratorAccess-016164185850 016164185850 eu-west-2

set -e

# Configuration
AWS_PROFILE="${1:-AdministratorAccess-016164185850}"
ACCOUNT_ID="${2:-016164185850}"
REGION="${3:-eu-west-2}"
ROLE_NAME="contractor-pay-lambda-development"
POLICY_NAME="contractor-pay-lambda-policy"
STATE_MACHINE_ARN="arn:aws:states:${REGION}:${ACCOUNT_ID}:stateMachine:contractor-pay-*"
S3_BUCKET="contractor-pay-files-development-${ACCOUNT_ID}"
DYNAMODB_TABLE="contractor-pay-development"

echo "========================================"
echo "Lambda IAM Permissions Fix Script"
echo "========================================"
echo "AWS Profile: $AWS_PROFILE"
echo "Account ID: $ACCOUNT_ID"
echo "Region: $REGION"
echo "Role: $ROLE_NAME"
echo "========================================"
echo ""

# Verify role exists
echo "✓ Verifying role exists..."
if ! aws iam get-role --role-name "$ROLE_NAME" --profile "$AWS_PROFILE" &>/dev/null; then
    echo "❌ ERROR: Role '$ROLE_NAME' not found!"
    exit 1
fi
echo "✓ Role found"
echo ""

# Create updated policy document
echo "✓ Creating updated IAM policy..."
cat > /tmp/lambda_policy.json <<EOF
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
        "arn:aws:dynamodb:${REGION}:${ACCOUNT_ID}:table/${DYNAMODB_TABLE}",
        "arn:aws:dynamodb:${REGION}:${ACCOUNT_ID}:table/${DYNAMODB_TABLE}/index/*"
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
        "arn:aws:s3:::${S3_BUCKET}",
        "arn:aws:s3:::${S3_BUCKET}/*"
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
        "${STATE_MACHINE_ARN}"
      ]
    }
  ]
}
EOF

echo "✓ Policy document created at /tmp/lambda_policy.json"
echo ""

# Display policy before applying
echo "📋 Updated Policy Content:"
echo "========================================"
cat /tmp/lambda_policy.json | jq '.'
echo "========================================"
echo ""

# Ask for confirmation
read -p "Apply this policy to role '$ROLE_NAME'? (yes/no): " CONFIRM
if [ "$CONFIRM" != "yes" ]; then
    echo "❌ Cancelled"
    exit 1
fi
echo ""

# Apply the policy
echo "⏳ Applying policy to role..."
aws iam put-role-policy \
    --role-name "$ROLE_NAME" \
    --policy-name "$POLICY_NAME" \
    --policy-document file:///tmp/lambda_policy.json \
    --profile "$AWS_PROFILE"

echo "✓ Policy applied successfully!"
echo ""

# Verify the policy was applied
echo "✓ Verifying policy..."
APPLIED_POLICY=$(aws iam get-role-policy \
    --role-name "$ROLE_NAME" \
    --policy-name "$POLICY_NAME" \
    --profile "$AWS_PROFILE" \
    --query 'PolicyDocument' \
    --output json)

if echo "$APPLIED_POLICY" | jq -e '.Statement[] | select(.Sid == "StepFunctionsAccess")' &>/dev/null; then
    echo "✅ Step Functions permissions verified!"
else
    echo "❌ Step Functions permissions NOT found!"
    exit 1
fi

if echo "$APPLIED_POLICY" | jq -e '.Statement[] | select(.Sid == "DynamoDBAccess")' &>/dev/null; then
    echo "✅ DynamoDB permissions verified!"
else
    echo "❌ DynamoDB permissions NOT found!"
    exit 1
fi

if echo "$APPLIED_POLICY" | jq -e '.Statement[] | select(.Sid == "S3Access")' &>/dev/null; then
    echo "✅ S3 permissions verified!"
else
    echo "❌ S3 permissions NOT found!"
    exit 1
fi

echo ""
echo "========================================"
echo "✅ All permissions applied successfully!"
echo "========================================"
echo ""
echo "Next steps:"
echo "1. Test file upload: curl -X POST http://api-endpoint/api/v1/upload"
echo "2. Verify Step Functions: aws stepfunctions list-executions --state-machine-arn <arn>"
echo "3. Check processing logs: aws logs tail /aws/lambda/contractor-pay-file-upload-handler-development"
echo ""
echo "For detailed analysis, see: LAMBDA_PERMISSIONS_AUDIT.md"
