#!/bin/bash

# Flush and Re-import Script
# Clears DynamoDB and re-uploads all files to collect enterprise validation metadata

set -e

AWS_PROFILE="AdministratorAccess-016164185850"
AWS_REGION="eu-west-2"
TABLE_NAME="contractor-pay-development"
S3_BUCKET="contractor-pay-files-development-016164185850"
INPUT_DIR="/Users/gianlucaformica/Projects/contractor-pay-tracker/InputData"

echo "================================================================================"
echo "FLUSH AND RE-IMPORT - ENTERPRISE VALIDATION METADATA COLLECTION"
echo "================================================================================"
echo ""

# Step 1: Count current items
echo "[1/5] Counting current DynamoDB items..."
CURRENT_COUNT=$(aws dynamodb scan --table-name "$TABLE_NAME" --select COUNT --profile "$AWS_PROFILE" --region "$AWS_REGION" | jq -r '.Count')
echo "      Current items: $CURRENT_COUNT"
echo ""

# Step 2: Flush DynamoDB
echo "[2/5] Flushing DynamoDB table..."
echo "      Scanning all items..."
aws dynamodb scan \
  --table-name "$TABLE_NAME" \
  --attributes-to-get PK SK \
  --profile "$AWS_PROFILE" \
  --region "$AWS_REGION" \
  --output json | \
jq -r '.Items[] | @json' | \
while read -r item; do
  PK=$(echo "$item" | jq -r '.PK.S')
  SK=$(echo "$item" | jq -r '.SK.S')

  aws dynamodb delete-item \
    --table-name "$TABLE_NAME" \
    --key "{\"PK\": {\"S\": \"$PK\"}, \"SK\": {\"S\": \"$SK\"}}" \
    --profile "$AWS_PROFILE" \
    --region "$AWS_REGION" > /dev/null

  echo "      Deleted: $PK | $SK"
done

echo "      ✓ Database flushed"
echo ""

# Step 3: Clear S3 bucket
echo "[3/5] Clearing S3 bucket..."
aws s3 rm "s3://$S3_BUCKET/" --recursive --profile "$AWS_PROFILE" --region "$AWS_REGION"
echo "      ✓ S3 bucket cleared"
echo ""

# Step 4: Count files to upload
echo "[4/5] Counting files to re-import..."
FILE_COUNT=$(ls -1 "$INPUT_DIR"/*.xlsx 2>/dev/null | wc -l | tr -d ' ')
echo "      Found $FILE_COUNT Excel files"
echo ""

# Step 5: Upload all files
echo "[5/5] Uploading files to trigger enterprise validation..."
UPLOADED=0

for file in "$INPUT_DIR"/*.xlsx; do
  if [ -f "$file" ]; then
    FILENAME=$(basename "$file")
    echo "      [$((UPLOADED+1))/$FILE_COUNT] Uploading: $FILENAME"

    aws s3 cp "$file" "s3://$S3_BUCKET/uploads/$FILENAME" \
      --profile "$AWS_PROFILE" \
      --region "$AWS_REGION" > /dev/null

    UPLOADED=$((UPLOADED+1))

    # Small delay to avoid overwhelming the system
    sleep 0.5
  fi
done

echo ""
echo "================================================================================"
echo "✓ FLUSH AND RE-IMPORT COMPLETE"
echo "================================================================================"
echo ""
echo "Summary:"
echo "  - Deleted: $CURRENT_COUNT items from DynamoDB"
echo "  - Uploaded: $UPLOADED files"
echo "  - Status: Step Functions will now process files with enterprise validation"
echo ""
echo "Next steps:"
echo "  - Monitor executions: aws stepfunctions list-executions --state-machine-arn <arn>"
echo "  - View validation metadata in debug UI: http://localhost:5559/debug"
echo ""
