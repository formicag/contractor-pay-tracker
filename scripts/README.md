# 🚀 Flush and Reload Scripts

## Overview

These scripts provide a safe way to **completely reset** your development environment and re-process all contractor pay files with the latest code.

## Scripts

### 1. `flush_and_reload.sh`

**The Nuclear Option** - Completely resets your development environment.

```bash
./scripts/flush_and_reload.sh
```

**What it does:**
1. ✅ Creates a backup of current DynamoDB data to `/tmp/dynamodb_backup_TIMESTAMP.json`
2. 🗑️ Deletes ALL records from DynamoDB table
3. 🗑️ Deletes ALL files from S3 bucket
4. 📤 Uploads all 48 files from `InputData/` to S3
5. 📊 Shows initial execution status

**Safety features:**
- Requires typing `FLUSH` to confirm (prevents accidents)
- Creates backup before deletion
- Only works in DEVELOPMENT environment
- Shows progress for each step

**Expected duration:** ~2-3 minutes

---

### 2. `monitor_processing.sh`

**Real-time Dashboard** - Monitors file processing progress.

```bash
./scripts/monitor_processing.sh
```

**What it shows:**
- 📊 File status counts (Total, Completed, Processing, Uploaded, Errors)
- 📈 Progress bar with percentage
- 🔄 Recent Step Functions executions
- ⏱️ Auto-refreshes every 5 seconds

**Use cases:**
- After running flush_and_reload.sh
- Debugging processing issues
- Watching batch uploads complete

Press `Ctrl+C` to exit.

---

## Complete Workflow

### Step 1: Run the flush
```bash
cd /Users/gianlucaformica/Projects/contractor-pay-tracker
./scripts/flush_and_reload.sh
```

When prompted, type `FLUSH` and press Enter.

### Step 2: Monitor progress
In a **separate terminal**:
```bash
cd /Users/gianlucaformica/Projects/contractor-pay-tracker
./scripts/monitor_processing.sh
```

### Step 3: Check the Flask app
Open browser to: http://localhost:5556/files

**Expected results:**
- ✅ All files show correct UmbrellaCode (NASA, GIANT, WORKWELL, etc.)
- ✅ No "Unknown" umbrella companies
- ✅ Files grouped by umbrella company
- ✅ Clean, professional data

---

## What to Watch For

### ✅ Good Signs
- Files upload successfully (green checkmarks)
- Step Functions executions show SUCCEEDED
- DynamoDB file count matches uploaded count (48)
- Flask app shows umbrella codes for all files

### ⚠️ Warning Signs
- Upload failures (red X marks)
- Step Functions showing FAILED
- Files stuck in UPLOADED status for >2 minutes
- ERROR status with critical validation failures

### 🔧 Troubleshooting

**Files stuck in UPLOADED status:**
```bash
# Check CloudWatch logs
aws logs tail /aws/lambda/contractor-pay-file-upload-handler-development --follow \
  --profile AdministratorAccess-016164185850 --region eu-west-2
```

**Step Functions failures:**
```bash
# Get recent failed executions
aws stepfunctions list-executions \
  --state-machine-arn arn:aws:states:eu-west-2:016164185850:stateMachine:contractor-pay-workflow-development \
  --status-filter FAILED \
  --max-results 5 \
  --profile AdministratorAccess-016164185850 \
  --region eu-west-2
```

**Restore from backup:**
```bash
# Find your backup
ls -lt /tmp/dynamodb_backup*.json | head -1

# Restore items (you'll need to write restoration script)
# Or just re-run flush_and_reload.sh
```

---

## After Successful Reload

### Verify Everything Works

1. **Check Files page:**
   - http://localhost:5556/files
   - All files have correct umbrella codes
   - No "Unknown" entries

2. **Check Contractors page:**
   - http://localhost:5556/contractors
   - 24 contractors visible
   - All have correct data

3. **Spot Check Data:**
   ```bash
   # Check a random file's umbrella code
   aws dynamodb get-item \
     --table-name contractor-pay-development \
     --key '{"PK":{"S":"FILE#<some-file-id>"},"SK":{"S":"METADATA"}}' \
     --profile AdministratorAccess-016164185850 \
     --region eu-west-2 | jq '.Item.UmbrellaCode'
   ```

   Should return: `{"S":"NASA"}` or similar (NOT missing!)

---

## Important Notes

⚠️ **DEVELOPMENT ONLY**: These scripts are ONLY for development environments. Never run on production data!

💾 **Backups**: Each run creates a backup in `/tmp/`. These are temporary and will be lost on reboot.

🔄 **Idempotent**: You can run `flush_and_reload.sh` multiple times safely.

⏱️ **Processing Time**: 48 files typically process in 5-10 minutes depending on:
- File sizes
- Lambda cold starts
- Validation complexity

📊 **Expected Final State**:
- 48 files in S3
- 48 File records in DynamoDB (Status=COMPLETED or ERROR)
- 200-300 PayRecord items in DynamoDB
- 24 Contractor records
- 12 Period records
- 48 Step Functions executions (SUCCEEDED or FAILED)

---

## Quick Reference

```bash
# Flush everything and reload
./scripts/flush_and_reload.sh

# Monitor in real-time (separate terminal)
./scripts/monitor_processing.sh

# Check Flask app
open http://localhost:5556/files

# View Step Functions in AWS Console
open https://eu-west-2.console.aws.amazon.com/states/home?region=eu-west-2#/statemachines/view/arn:aws:states:eu-west-2:016164185850:stateMachine:contractor-pay-workflow-development

# Check DynamoDB in AWS Console
open https://eu-west-2.console.aws.amazon.com/dynamodbv2/home?region=eu-west-2#item-explorer?table=contractor-pay-development
```

---

## Success Criteria

After flush and reload, you should see:

✅ **All files have UmbrellaCode**
- NASA files: `UmbrellaCode: "NASA"`
- GIANT files: `UmbrellaCode: "GIANT"`
- WORKWELL files: `UmbrellaCode: "WORKWELL"`
- etc.

✅ **Zero "Unknown" umbrella companies**

✅ **Files page groups by umbrella correctly**

✅ **Enterprise-quality data**

---

**Questions?** Check the main project README or CloudWatch logs.
