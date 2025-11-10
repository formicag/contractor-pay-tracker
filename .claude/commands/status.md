# Status Command

Quick health check of the contractor-pay-tracker system.

## Instructions

Check the current status of all system components and provide a concise summary.

1. **Lambda Functions Status**:
   - List all 5 Lambda functions with their state
   - Verify they're all Active
   - Show which Lambda Layer version each is using

2. **Recent Step Functions Executions**:
   - Show last 5 executions with their status
   - Calculate success rate from recent executions
   - Show any currently running executions

3. **DynamoDB Quick Stats**:
   - Total items count
   - PayRecords count (EntityType = 'PayRecord')
   - Files count (EntityType = 'File')

4. **S3 Bucket**:
   - Verify bucket exists and is accessible
   - Show total number of files in bucket

5. **Summary**:
   - Overall system health (Healthy/Degraded/Down)
   - Any issues detected
   - Recent activity summary

Use the AWS credentials:
- Profile: AdministratorAccess-016164185850
- Region: eu-west-2

Keep the output concise and focused on actionable information.
