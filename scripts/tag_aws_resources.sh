#!/bin/bash

# AWS Tagging Script for Contractor Pay Tracker
# This script tags all AWS resources that are not managed by Terraform

set -e

AWS_PROFILE="AdministratorAccess-016164185850"
AWS_REGION="eu-west-2"

# Define common tags
PROJECT="contractor-pay-tracker"
ENVIRONMENT="development"
OWNER="engineering-team"
PURPOSE="contractor-payroll-processing"
MANAGED_BY="manual"
COST_CENTER="finance-operations"

echo "=========================================="
echo "AWS Resource Tagging Script"
echo "=========================================="
echo ""

# Function to tag S3 buckets
tag_s3_bucket() {
    local bucket=$1
    local service=$2
    echo "Tagging S3 bucket: $bucket"

    aws s3api put-bucket-tagging \
        --bucket "$bucket" \
        --tagging "TagSet=[
            {Key=Project,Value=$PROJECT},
            {Key=Environment,Value=$ENVIRONMENT},
            {Key=Owner,Value=$OWNER},
            {Key=Purpose,Value=$PURPOSE},
            {Key=ManagedBy,Value=$MANAGED_BY},
            {Key=CostCenter,Value=$COST_CENTER},
            {Key=Service,Value=$service},
            {Key=Name,Value=$bucket}
        ]" \
        --profile "$AWS_PROFILE" \
        --region "$AWS_REGION" 2>&1 && echo "  ✓ Tagged successfully" || echo "  ✗ Failed to tag"
}

# Function to tag CloudWatch Log Groups
tag_log_group() {
    local log_group=$1
    echo "Tagging CloudWatch log group: $log_group"

    aws logs tag-log-group \
        --log-group-name "$log_group" \
        --tags "Project=$PROJECT,Environment=$ENVIRONMENT,Owner=$OWNER,Purpose=$PURPOSE,ManagedBy=aws-auto-created,CostCenter=$COST_CENTER,Service=cloudwatch" \
        --profile "$AWS_PROFILE" \
        --region "$AWS_REGION" 2>&1 && echo "  ✓ Tagged successfully" || echo "  ✗ Failed to tag"
}

# Function to tag Lambda functions
tag_lambda_function() {
    local function_name=$1
    local function_desc=$2
    local function_arn

    function_arn=$(aws lambda get-function --function-name "$function_name" --query 'Configuration.FunctionArn' --output text --profile "$AWS_PROFILE" --region "$AWS_REGION")

    echo "Tagging Lambda function: $function_name"

    aws lambda tag-resource \
        --resource "$function_arn" \
        --tags "Project=$PROJECT,Environment=$ENVIRONMENT,Owner=$OWNER,Purpose=$PURPOSE,ManagedBy=terraform,CostCenter=$COST_CENTER,Service=lambda,Description=$function_desc" \
        --profile "$AWS_PROFILE" \
        --region "$AWS_REGION" 2>&1 && echo "  ✓ Tagged successfully" || echo "  ✗ Failed to tag"
}

echo "1. Tagging S3 Buckets"
echo "----------------------"
tag_s3_bucket "contractor-pay-terraform-state" "s3-terraform-state"
echo ""

echo "2. Tagging CloudWatch Log Groups"
echo "----------------------------------"
tag_log_group "/aws/lambda/contractor-pay-cleanup-handler-development"
tag_log_group "/aws/lambda/contractor-pay-file-processor-development"
tag_log_group "/aws/lambda/contractor-pay-file-upload-handler-development"
tag_log_group "/aws/lambda/contractor-pay-report-generator-development"
tag_log_group "/aws/lambda/contractor-pay-validation-engine-development"
echo ""

echo "3. Supplemental Lambda Function Tagging"
echo "----------------------------------------"
# Note: Terraform will manage primary tags, these are supplemental
tag_lambda_function "contractor-pay-cleanup-handler-development" "Manages-data-retention-and-cleanup"
tag_lambda_function "contractor-pay-file-processor-development" "Processes-Excel-files-and-extracts-data"
tag_lambda_function "contractor-pay-file-upload-handler-development" "Handles-S3-upload-events"
tag_lambda_function "contractor-pay-report-generator-development" "Generates-contractor-pay-reports"
tag_lambda_function "contractor-pay-validation-engine-development" "Validates-contractor-pay-records"
echo ""

echo "=========================================="
echo "Tagging Complete!"
echo "=========================================="
