#!/bin/bash

###############################################################################
# Flush and Reload Script (AUTO-CONFIRM VERSION)
#
# DANGER ZONE: This script will:
# 1. Delete ALL data from DynamoDB
# 2. Delete ALL files from S3
# 3. Re-upload all files from InputData/
#
# Use only in DEVELOPMENT environments!
###############################################################################

set -e  # Exit on any error

# Configuration
PROFILE="AdministratorAccess-016164185850"
REGION="eu-west-2"
TABLE_NAME="contractor-pay-development"
BUCKET_NAME="contractor-pay-files-development-016164185850"
INPUT_DIR="/Users/gianlucaformica/Projects/contractor-pay-tracker/InputData"
S3_PREFIX="production"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo ""
echo -e "${RED}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${RED}║           🚀 AUTO-FLUSH STARTING (NO CONFIRMATION)         ║${NC}"
echo -e "${RED}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

echo ""
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}Step 1: Creating backup export (just in case)${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"

BACKUP_FILE="/tmp/dynamodb_backup_$(date +%Y%m%d_%H%M%S).json"
echo -e "${YELLOW}📦 Exporting DynamoDB to ${BACKUP_FILE}...${NC}"

aws dynamodb scan \
    --table-name "$TABLE_NAME" \
    --profile "$PROFILE" \
    --region "$REGION" \
    --output json > "$BACKUP_FILE" 2>&1

BACKUP_COUNT=$(cat "$BACKUP_FILE" | jq '.Items | length' 2>/dev/null || echo "0")
echo -e "${GREEN}✅ Backed up ${BACKUP_COUNT} items to ${BACKUP_FILE}${NC}"

echo ""
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}Step 2: Deleting all DynamoDB records${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"

echo -e "${YELLOW}🗑️  Scanning for all items...${NC}"

# Get all keys
aws dynamodb scan \
    --table-name "$TABLE_NAME" \
    --attributes-to-get PK SK \
    --profile "$PROFILE" \
    --region "$REGION" \
    --output json > /tmp/keys_to_delete.json 2>&1

TOTAL_ITEMS=$(cat /tmp/keys_to_delete.json | jq '.Items | length' 2>/dev/null || echo "0")
echo -e "${YELLOW}Found ${TOTAL_ITEMS} items to delete${NC}"

if [ "$TOTAL_ITEMS" -gt 0 ]; then
    echo -e "${YELLOW}Deleting in batches...${NC}"

    # Delete items in parallel (simple version for compatibility)
    DELETE_COUNT=0
    cat /tmp/keys_to_delete.json | jq -c '.Items[] | {PK: .PK, SK: .SK}' | while IFS= read -r item; do
        aws dynamodb delete-item \
            --table-name "$TABLE_NAME" \
            --key "$item" \
            --profile "$PROFILE" \
            --region "$REGION" > /dev/null 2>&1 &

        DELETE_COUNT=$((DELETE_COUNT + 1))

        # Wait every 25 items to avoid too many concurrent requests
        if [ $((DELETE_COUNT % 25)) -eq 0 ]; then
            wait
        fi
    done

    wait  # Wait for all remaining deletes to complete
    echo -e "${GREEN}✅ Deleted ${TOTAL_ITEMS} items from DynamoDB${NC}"
else
    echo -e "${GREEN}✅ DynamoDB table already empty${NC}"
fi

echo ""
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}Step 3: Clearing S3 bucket${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"

echo -e "${YELLOW}🗑️  Deleting all S3 objects...${NC}"

aws s3 rm "s3://${BUCKET_NAME}/" \
    --recursive \
    --profile "$PROFILE" \
    --region "$REGION" 2>&1

echo -e "${GREEN}✅ S3 bucket cleared${NC}"

echo ""
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}Step 4: Uploading fresh files from InputData/${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"

FILE_COUNT=0
SUCCESS_COUNT=0
FAIL_COUNT=0

for file in "${INPUT_DIR}"/*.xlsx; do
    if [ -f "$file" ]; then
        FILE_COUNT=$((FILE_COUNT + 1))
        FILENAME=$(basename "$file")

        echo -e "${YELLOW}📤 [$FILE_COUNT] Uploading: ${FILENAME}${NC}"

        if aws s3 cp "$file" "s3://${BUCKET_NAME}/${S3_PREFIX}/${FILENAME}" \
            --profile "$PROFILE" \
            --region "$REGION" > /dev/null 2>&1; then

            SUCCESS_COUNT=$((SUCCESS_COUNT + 1))
            echo -e "${GREEN}   ✅ Uploaded successfully${NC}"
        else
            FAIL_COUNT=$((FAIL_COUNT + 1))
            echo -e "${RED}   ❌ Upload failed${NC}"
        fi

        # Small delay to avoid overwhelming the system
        sleep 0.5
    fi
done

echo ""
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}Upload Summary${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}✅ Successful uploads: ${SUCCESS_COUNT}${NC}"
if [ $FAIL_COUNT -gt 0 ]; then
    echo -e "${RED}❌ Failed uploads: ${FAIL_COUNT}${NC}"
fi
echo -e "${BLUE}📊 Total processed: ${FILE_COUNT}${NC}"

echo ""
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}Step 5: Monitoring Step Functions executions${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"

echo -e "${YELLOW}⏳ Waiting 5 seconds for Step Functions to start...${NC}"
sleep 5

STATE_MACHINE_ARN="arn:aws:states:${REGION}:016164185850:stateMachine:contractor-pay-workflow-development"

echo -e "${YELLOW}📊 Checking execution status...${NC}"

aws stepfunctions list-executions \
    --state-machine-arn "$STATE_MACHINE_ARN" \
    --max-results 10 \
    --profile "$PROFILE" \
    --region "$REGION" \
    --output table 2>&1 || echo "Step Functions check completed"

echo ""
echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║                    ✅ FLUSH COMPLETE ✅                     ║${NC}"
echo -e "${GREEN}║                                                            ║${NC}"
echo -e "${GREEN}║  Files uploaded: ${SUCCESS_COUNT}/48                                    ║${NC}"
echo -e "${GREEN}║  Backup saved: ${BACKUP_FILE}        ║${NC}"
echo -e "${GREEN}║                                                            ║${NC}"
echo -e "${GREEN}║  Next: Monitor at http://localhost:5556/files              ║${NC}"
echo -e "${GREEN}║                                                            ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

echo -e "${YELLOW}💡 Run this in another terminal to watch processing:${NC}"
echo ""
echo -e "${BLUE}   ./scripts/monitor_processing.sh${NC}"
echo ""
