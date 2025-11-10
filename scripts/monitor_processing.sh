#!/bin/bash

###############################################################################
# Monitor Processing Script
#
# Real-time monitoring dashboard for file processing
###############################################################################

PROFILE="AdministratorAccess-016164185850"
REGION="eu-west-2"
TABLE_NAME="contractor-pay-development"
STATE_MACHINE_ARN="arn:aws:states:${REGION}:016164185850:stateMachine:contractor-pay-workflow-development"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

clear

while true; do
    clear
    echo -e "${BLUE}╔════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║         📊 Contractor Pay Tracker - Processing Monitor         ║${NC}"
    echo -e "${BLUE}║                  $(date '+%Y-%m-%d %H:%M:%S')                              ║${NC}"
    echo -e "${BLUE}╚════════════════════════════════════════════════════════════════╝${NC}"
    echo ""

    # Get DynamoDB file counts
    echo -e "${CYAN}📁 DynamoDB File Status:${NC}"
    echo ""

    TOTAL=$(aws dynamodb scan \
        --table-name "$TABLE_NAME" \
        --filter-expression "EntityType = :et" \
        --expression-attribute-values '{":et":{"S":"File"}}' \
        --select COUNT \
        --profile "$PROFILE" \
        --region "$REGION" \
        --output json 2>/dev/null | jq -r '.Count // 0')

    COMPLETED=$(aws dynamodb scan \
        --table-name "$TABLE_NAME" \
        --filter-expression "EntityType = :et AND #status = :st" \
        --expression-attribute-names '{"#status":"Status"}' \
        --expression-attribute-values '{":et":{"S":"File"},":st":{"S":"COMPLETED"}}' \
        --select COUNT \
        --profile "$PROFILE" \
        --region "$REGION" \
        --output json 2>/dev/null | jq -r '.Count // 0')

    ERROR=$(aws dynamodb scan \
        --table-name "$TABLE_NAME" \
        --filter-expression "EntityType = :et AND #status = :st" \
        --expression-attribute-names '{"#status":"Status"}' \
        --expression-attribute-values '{":et":{"S":"File"},":st":{"S":"ERROR"}}' \
        --select COUNT \
        --profile "$PROFILE" \
        --region "$REGION" \
        --output json 2>/dev/null | jq -r '.Count // 0')

    UPLOADED=$(aws dynamodb scan \
        --table-name "$TABLE_NAME" \
        --filter-expression "EntityType = :et AND #status = :st" \
        --expression-attribute-names '{"#status":"Status"}' \
        --expression-attribute-values '{":et":{"S":"File"},":st":{"S":"UPLOADED"}}' \
        --select COUNT \
        --profile "$PROFILE" \
        --region "$REGION" \
        --output json 2>/dev/null | jq -r '.Count // 0')

    PROCESSING=$(aws dynamodb scan \
        --table-name "$TABLE_NAME" \
        --filter-expression "EntityType = :et AND #status = :st" \
        --expression-attribute-names '{"#status":"Status"}' \
        --expression-attribute-values '{":et":{"S":"File"},":st":{"S":"PROCESSING"}}' \
        --select COUNT \
        --profile "$PROFILE" \
        --region "$REGION" \
        --output json 2>/dev/null | jq -r '.Count // 0')

    echo -e "  ${BLUE}Total Files:${NC}      ${TOTAL}"
    echo -e "  ${GREEN}✅ Completed:${NC}     ${COMPLETED}"
    echo -e "  ${YELLOW}⏳ Processing:${NC}    ${PROCESSING}"
    echo -e "  ${CYAN}📤 Uploaded:${NC}      ${UPLOADED}"
    echo -e "  ${RED}❌ Errors:${NC}        ${ERROR}"

    # Calculate progress
    if [ "$TOTAL" -gt 0 ]; then
        PERCENT=$(( (COMPLETED * 100) / TOTAL ))
        BARS=$(( PERCENT / 2 ))
        EMPTY=$(( 50 - BARS ))

        echo ""
        echo -e "  ${CYAN}Progress:${NC} ["
        printf "  "
        for i in $(seq 1 $BARS); do printf "${GREEN}█${NC}"; done
        for i in $(seq 1 $EMPTY); do printf "░"; done
        echo -e " ] ${PERCENT}%"
    fi

    echo ""
    echo -e "${CYAN}🔄 Recent Step Functions Executions:${NC}"
    echo ""

    aws stepfunctions list-executions \
        --state-machine-arn "$STATE_MACHINE_ARN" \
        --max-results 10 \
        --profile "$PROFILE" \
        --region "$REGION" \
        --output json 2>/dev/null | jq -r '
        .executions[] |
        "  " +
        (if .status == "SUCCEEDED" then "✅"
         elif .status == "RUNNING" then "⏳"
         elif .status == "FAILED" then "❌"
         else "❓" end) +
        " " + (.name | split(":") | last | split("-") | .[0:3] | join(" ")) +
        " (" + .status + ")"
    ' | head -10

    echo ""
    echo -e "${YELLOW}Press Ctrl+C to exit. Refreshing every 5 seconds...${NC}"

    sleep 5
done
