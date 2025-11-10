# DynamoDB Cleanup Report

**Date:** 2025-11-09
**Table:** contractor-pay-development
**Region:** eu-west-2

## Summary

Successfully cleaned up DynamoDB database by removing duplicate file records, old FAILED records, and stale data. Only the most recent COMPLETED version of each file for each umbrella company and period combination was retained.

## Cleanup Results

### Before Cleanup
- **Total files:** 48
- **Umbrella+Period groups:** 6
- **Files per group:** 8 (7 duplicates + 1 to keep)

### Files Deleted
- **Duplicate COMPLETED files:** 40
- **ERROR status files:** 2
- **FAILED status files:** 0
- **SUPERSEDED status files:** 0
- **Old UPLOADED/PROCESSING files:** 0

### Total Deletions
- **Files deleted:** 42
- **Pay records deleted:** 216 (including associated records)
- **Total database items deleted:** 216

### After Cleanup
- **Total files:** 6
- **Umbrella+Period groups:** 6
- **Files per group:** 1 (most recent COMPLETED only)

## Files Kept (Most Recent COMPLETED)

| Umbrella Company | Period | File ID | Status | Upload Date |
|------------------|--------|---------|--------|-------------|
| WORKWELL | UNKNOWN | c856937d... | COMPLETED | 2025-11-09T22:46:16Z |
| PAYSTREAM | UNKNOWN | 20db685f... | COMPLETED | 2025-11-09T22:46:21Z |
| GIANT | UNKNOWN | 800c23cc... | COMPLETED | 2025-11-09T22:46:21Z |
| NASA | UNKNOWN | 5380976f... | COMPLETED | 2025-11-09T22:46:18Z |
| CLARITY | UNKNOWN | 03967888... | COMPLETED | 2025-11-09T22:46:30Z |
| PARASOL | UNKNOWN | 19227ebd... | COMPLETED | 2025-11-09T22:46:30Z |

## Cleanup Strategy

The cleanup script (`scripts/cleanup_dynamodb.py`) implements the following logic:

1. **Scan all file metadata records** from DynamoDB
2. **Group files by umbrella company + period** combination
3. **Within each group:**
   - Sort by upload timestamp (most recent first)
   - Keep the most recent COMPLETED or COMPLETED_WITH_WARNINGS file
   - Mark all other files for deletion:
     - Older COMPLETED files (duplicates)
     - FAILED status files
     - ERROR status files
     - SUPERSEDED files
     - Old UPLOADED/PROCESSING files
4. **Delete files and associated pay records** in batches

## Script Usage

```bash
# Dry run (no actual deletions)
python scripts/cleanup_dynamodb.py

# Execute actual cleanup
python scripts/cleanup_dynamodb.py --execute
```

## Verification

Post-cleanup verification confirms:
- Only 6 files remain (one per umbrella+period combination)
- All remaining files have COMPLETED status
- Each file is the most recent upload for its group
- No duplicate, failed, or stale records remain

## Script Location

**Script:** `/Users/gianlucaformica/Projects/contractor-pay-tracker/scripts/cleanup_dynamodb.py`

The script is reusable and can be run anytime to clean up duplicates and stale data in the future.
