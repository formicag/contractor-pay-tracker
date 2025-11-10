#!/bin/bash

# Monitor validation executions in real-time

AWS_PROFILE="AdministratorAccess-016164185850"
AWS_REGION="eu-west-2"
SF_ARN="arn:aws:states:eu-west-2:016164185850:stateMachine:contractor-pay-workflow-development"

echo "================================================================================"
echo "MONITORING ENTERPRISE VALIDATION - LIVE UPDATES"
echo "================================================================================"
echo ""
echo "Watching Step Functions executions..."
echo "Press Ctrl+C to stop"
echo ""

while true; do
  clear
  echo "================================================================================"
  echo "ENTERPRISE VALIDATION MONITOR - $(date '+%H:%M:%S')"
  echo "================================================================================"
  echo ""

  # Get recent executions
  EXECUTIONS=$(aws stepfunctions list-executions \
    --state-machine-arn "$SF_ARN" \
    --max-results 20 \
    --profile "$AWS_PROFILE" \
    --region "$AWS_REGION" \
    --output json)

  # Count by status
  RUNNING=$(echo "$EXECUTIONS" | jq '[.executions[] | select(.status=="RUNNING")] | length')
  SUCCEEDED=$(echo "$EXECUTIONS" | jq '[.executions[] | select(.status=="SUCCEEDED")] | length')
  FAILED=$(echo "$EXECUTIONS" | jq '[.executions[] | select(.status=="FAILED")] | length')

  echo "Status Summary (Last 20 executions):"
  echo "  ⏳ RUNNING:   $RUNNING"
  echo "  ✓ SUCCEEDED: $SUCCEEDED"
  echo "  ✗ FAILED:    $FAILED"
  echo ""

  # Show recent executions
  echo "Recent Executions:"
  echo "$EXECUTIONS" | jq -r '.executions[] |
    "  [\(.status)] \(.name) - \(.startDate)"' | head -10

  echo ""
  echo "Press Ctrl+C to stop monitoring..."

  sleep 3
done
