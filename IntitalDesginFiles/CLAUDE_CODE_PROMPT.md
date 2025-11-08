# CLAUDE CODE BUILD PROMPT - Contractor Pay File Management System

## MISSION

You are tasked with building a complete, enterprise-grade contractor pay file management system for Colibri Digital. This system ingests, validates, and tracks pay files sent to umbrella companies, with comprehensive audit trails for compliance.

## CONTEXT

**User**: Gianluca Formica, Consultancy/Delivery Manager at Colibri Digital  
**Company**: Colibri Digital (subsidiary of Nasstar Group)  
**Purpose**: Track contractor payments to 6 umbrella companies every 4 weeks  
**Budget**: <£5/month AWS costs  
**Compliance**: Must be audit-ready with extensive metadata and validation

## YOUR TASK

Build the complete system following the attached design document (`ENTERPRISE_SOLUTION_DESIGN.md`). You have sample pay files that demonstrate the exact Excel format you'll be processing.

## DELIVERABLES

### 1. AWS Infrastructure (SAM/CloudFormation)
- Complete `backend/template.yaml` with all resources:
  - Aurora Serverless v2 PostgreSQL database
  - S3 bucket with versioning
  - Lambda functions (5 functions as specified)
  - Step Functions state machine
  - API Gateway REST API
  - CloudWatch alarms and dashboards
  - Secrets Manager for database credentials
  - IAM roles and policies

### 2. Database Schema
- Complete PostgreSQL schema with all tables
- Database triggers for audit logging
- Indexes for performance
- Seed data script with:
  - 23 contractors (as specified in design doc)
  - 6 umbrella companies
  - 4 permanent staff to reject
  - 13 pay periods for 2025-2026
  - System parameters

### 3. Lambda Functions (Python 3.11)
All Lambda functions with proper error handling, structured logging, and comprehensive validation:

#### a) file-upload-handler
- Receive file uploads from Flask UI
- Upload to S3 with metadata
- Calculate SHA256 hash
- Insert into pay_files_metadata table
- Return file_id and status

#### b) file-processor
- Download Excel from S3
- Parse using openpyxl/pandas
- Extract umbrella company and period
- Handle duplicate period detection (prompt user for replacement)
- For each row:
  - Clean and normalize data
  - Validate contractor (fuzzy name matching with 85% threshold)
  - Validate umbrella company association
  - Validate rates (normal vs 1.5x overtime, ±2% tolerance)
  - Validate VAT (20% calculation)
  - Check not permanent staff
  - Check employee ID consistency
- Store validation errors/warnings
- Import valid records
- Update file metadata
- Log everything

#### c) validation-engine
- Implement all validation rules from design doc
- Fuzzy name matching using Levenshtein distance
- Rate validation with historical comparison
- Overtime rate validation (1.5x with ±2% tolerance)
- VAT validation (must be 20%)
- Return detailed validation results

#### d) report-generator
- Summary statistics by period
- Spend by umbrella company
- Top contractors by pay
- Contractor detail view with pay history
- Rate change detection
- Export to JSON (future: CSV/Excel)

#### e) cleanup-handler
- Daily maintenance tasks
- Archive old logs
- Move old S3 files to Glacier
- Database vacuum

### 4. Flask Web UI
Complete local development web application:

#### Pages:
- **Dashboard** (`index.html`):
  - Summary cards (total spend, contractors, recent uploads)
  - Quick actions
  - Recent activity feed

- **Upload** (`upload.html`):
  - Drag-and-drop file upload (multiple files)
  - Progress bars
  - Metadata form (uploaded_by, notes)
  - Real-time validation feedback

- **Files Management** (`files.html`) - **CRITICAL FOR TESTING**:
  - **Main Table**: All uploaded files with columns:
    - Filename (clickable to view details)
    - Umbrella company (badge with color)
    - Pay period (e.g., "Period 8: 28-Jul to 24-Aug")
    - Upload date/time (relative, e.g., "2 hours ago")
    - Status (badge: SUCCESS, ERROR, PROCESSING)
    - Records (count of contractor records)
    - Total amount (formatted: £127,456.50)
    - Actions: [View] [Delete] [Reprocess]
  
  - **Filter Bar**:
    - Filter by umbrella (dropdown: ALL, NASA, PAYSTREAM, etc.)
    - Filter by period (dropdown: ALL, Period 8, Period 9, etc.)
    - Filter by status (dropdown: ALL, COMPLETED, ERROR)
    - Search by filename
  
  - **DELETE Action** (ESSENTIAL):
    - Click DELETE → Modal confirmation appears:
      ```
      ⚠️ Delete NASA_GCI_Nasstar_Contractor_Pay_Figures_01092025.xlsx?
      
      This will permanently remove:
      • 14 contractor pay records
      • £127,456.50 in payments
      • All validation results for this file
      
      Period: Period 8 (28-Jul-25 to 24-Aug-25)
      Umbrella: NASA
      
      This action cannot be undone.
      
      [Cancel] [Confirm Delete]
      ```
    - On confirm:
      - Show loading spinner
      - Call DELETE /api/v1/files/{file_id}
      - Backend soft-deletes all records (sets is_active=FALSE)
      - Logs deletion in audit_log
      - Refreshes table
      - Shows success toast: "✓ Deleted 14 records for NASA Period 8"
  
  - **Period Overview Tab**:
    - Grid view showing all pay periods
    - For each period, show which umbrellas have files:
      ```
      Period 8 (28-Jul to 24-Aug)  Total: £456,789.00
      ✓ NASA        (14 records, £127,456.50)  [View] [Delete]
      ✓ PAYSTREAM   (5 records, £57,890.00)    [View] [Delete]
      ✓ PARASOL     (6 records, £34,567.00)    [View] [Delete]
      ✓ GIANT       (1 record, £9,965.12)       [View] [Delete]
      ✗ CLARITY     Missing
      ✓ WORKWELL    (2 records, £13,149.56)    [View] [Delete]
      ```
    - Click umbrella row → drill down to contractor list
    - Delete button per umbrella → removes ALL records for that umbrella+period
  
  - **Bulk Actions**:
    - Checkbox per row
    - "Delete Selected" button (confirms before deleting multiple)
    - Useful for clearing test data

  - **Development Tools** (only visible when ENVIRONMENT=development):
    - **Danger Zone** section at bottom:
      - Button: "🗑️ Flush All Data"
      - Click → Modal: "Type 'DELETE ALL' to confirm"
      - Truncates all pay_records, pay_files_metadata, validation_errors
      - Keeps contractors, umbrellas, periods (reference data)
      - Shows success: "✓ All operational data deleted. Ready for fresh import."

- **Validation** (`validation.html`):
  - Display errors, warnings, success
  - Drill-down to specific row issues
  - Action buttons (approve, reject)

- **Reports** (`reports.html`):
  - Period selector
  - Summary statistics
  - Charts (spend by umbrella pie chart, spend over time line chart)
  - Top contractors table
  - Drill-down to contractor details

- **Contractor Detail** (`contractor.html`):
  - Contractor profile
  - Pay history table
  - Rate change history
  - Overtime analysis

#### Features:
- Bootstrap 5 for styling
- JavaScript for AJAX calls to API Gateway
- Real-time status polling during processing
- Client-side file validation (file type, size)
- Responsive design (works on laptop)

### 5. CI/CD Pipeline
Complete GitHub Actions workflows:

- **deploy.yml**: Main deployment pipeline
  - Run tests (pytest with coverage)
  - Lint with ruff
  - SAM build and deploy
  - Deploy seed data
  - Output API Gateway URL

- **test.yml**: Run tests on PR
  - Unit tests
  - Integration tests
  - Code coverage report

### 6. Comprehensive Testing
- Unit tests for all validation rules
- Integration tests for Lambda functions
- Test fixtures (sample Excel files)
- Mocked AWS services for local testing

### 7. Documentation
- README.md with setup instructions
- API.md with endpoint documentation
- DEPLOYMENT.md with step-by-step deployment guide
- USER_GUIDE.md for end users

## CRITICAL REQUIREMENTS

### Development & Testing Requirements (ESSENTIAL)
**Context**: Gianluca will be actively testing, importing files repeatedly, and fixing bugs during development. The system MUST be designed for rapid iteration and easy debugging.

1. **Fast Deployment**: 
   - SAM deploy must complete in <5 minutes
   - Changes to Lambda code deploy in <2 minutes
   - Database schema changes via migrations (no manual SQL)
   - Hot reload for Flask UI during local dev

2. **Bug Prevention**:
   - Extensive input validation (fail fast, fail loud)
   - Type hints on all Python functions
   - Comprehensive error messages (tell user exactly what's wrong)
   - Database constraints prevent bad data
   - Rollback capabilities for failed imports

3. **Bug Fixing Speed**:
   - Verbose structured logging (DEBUG level during development)
   - Every function logs: inputs, outputs, execution time
   - CloudWatch Logs Insights queries provided
   - Error traces include full context
   - Test fixtures for every scenario

4. **Data Management Dashboard** (CRITICAL FOR TESTING):
   - **Overview Table**: Shows ALL imported files with:
     - File name
     - Umbrella company
     - Pay period
     - Upload date/time
     - Status (UPLOADED, PROCESSING, COMPLETED, ERROR)
     - Record count
     - Total amount
     - **DELETE button** (with confirmation)
   
   - **Delete File Action** (MUST IMPLEMENT):
     ```
     When user clicks DELETE on NASA file from Period 8:
     1. Show confirmation: 
        "Delete NASA_..._01092025.xlsx?
         This will remove:
         - 14 contractor records
         - £127,456.50 in pay records
         - All validation results
         This cannot be undone. Continue?"
     
     2. If confirmed:
        - Mark file_metadata as DELETED
        - Set all pay_records.is_active = FALSE (soft delete)
        - Log deletion in audit_log
        - Show success: "Deleted 14 records for NASA Period 8"
     
     3. Allow immediate re-import of same file
     ```

   - **Period Overview**: 
     - Group files by pay period
     - Show which umbrellas have files for each period
     - Highlight missing umbrellas (e.g., "Period 8: Missing Clarity")
     - Total spend per period
     - Drill-down to see all contractors in that period

   - **Flush Database** (DEVELOPMENT ONLY):
     - Button: "Delete ALL Data" (requires typing "DELETE ALL" to confirm)
     - Truncates all operational tables (keeps reference data)
     - Useful for testing clean imports
     - Only visible when `ENVIRONMENT=development`

5. **Re-import Testing Flow**:
   ```
   Common testing scenario:
   1. Import NASA file → spot error in validation logic
   2. Click DELETE on NASA file → removes all records
   3. Fix validation code → deploy in 2 minutes
   4. Re-import NASA file → test fix
   5. Check logs to verify fix worked
   ```

6. **Testing Tools Required**:
   - **Seed Data Reset**: Script to restore golden reference data
   - **Sample Data Generator**: Create test files with known errors
   - **Validation Report**: Export all validation errors to CSV
   - **Audit Trail Viewer**: Search audit_log by file, contractor, date

### Data Validation Rules (MUST IMPLEMENT)
1. **Contractor Name Matching**: Use fuzzy matching (85% threshold) to handle typos like "Jon" vs "Jonathan", "Mathews" vs "Matthews"
2. **Permanent Staff Check**: Reject any file containing Syed Syed, Victor Cheung, Gareth Jones, or Martin Alabone (they're permanent staff, not contractors)
3. **Umbrella Validation**: Each contractor MUST be in their assigned umbrella company's file
4. **Overtime Rate**: Must be 1.5x normal rate (±2% tolerance for rounding)
5. **VAT Calculation**: Must be exactly 20% of amount (±£0.01 tolerance)
6. **Duplicate Period**: Detect existing data for umbrella+period, prompt user to replace or cancel
7. **Rate Change Detection**: Flag if rate changes >5% from last period

### Metadata Requirements (CRITICAL FOR AUDIT)
Every file and record must track:
- File: name, S3 key, version, hash, size, upload timestamp, processed timestamp, uploaded_by
- Record: file_id, contractor, umbrella, period, amounts, rates, VAT, record_type
- Audit: Every INSERT/UPDATE/DELETE with old/new values, user, timestamp
- Processing: Detailed logs with request_id, execution time, validation results

### Logging Requirements
Use structured JSON logging:
```python
{
  "timestamp": "2025-09-01T15:23:45Z",
  "level": "INFO",
  "lambda_name": "file-processor",
  "request_id": "abc-123",
  "message": "Processing file",
  "context": {
    "file_id": "...",
    "s3_key": "...",
    "records": 14
  }
}
```

### Error Handling
- Graceful degradation (one file failure doesn't stop others)
- Detailed error messages for users
- Automatic retry for transient failures
- Dead letter queue for failed messages

## FILE FORMAT SPECIFICATION

You have 6 sample Excel files (NASA, PAYSTREAM, GIANT, Parasol, Clarity, WORKWELL). All follow this structure:

**Columns:**
- `employee id`: Umbrella's ID for contractor (string or numeric)
- `surname`: Last name
- `forename`: First name  
- `unit`: Days worked (decimal, e.g., 20.00, 0.5 for half day)
- `rate`: Day rate in GBP (decimal)
- `per`: Always "day"
- `amount`: unit × rate (decimal)
- `vat`: 20% of amount (decimal)
- `total hours per period`: unit × 7.5 hours (decimal)
- `company`: Full umbrella company name (varies by file)
- `notes`: "Overtime" or "Expense" or blank

**Data Quirks to Handle:**
- Empty rows (skip)
- Repeated header rows mid-file (skip)
- Missing employee_id in some rows (error if data exists)
- Overtime indicated by "Overtime" in notes OR rate = 1.5x
- Some names have spelling variations
- Company names vary (e.g., "NASA GROUP" vs "Nasa Umbrella Ltd")

**Filename Pattern** (not guaranteed, don't rely on it):
`{PREFIX}_{UMBRELLA}_{GCI_Nasstar}_Contractor_Pay_Figures_{DDMMYYYY}.xlsx`

## GOLDEN REFERENCE DATA

### Contractors (23)
```
Gary Mandaracas → PayStream My Max 3 Limited
Graeme Oldroyd → PayStream My Max 3 Limited
Barry Breden → Nasa Umbrella Ltd
James Matthews → Nasa Umbrella Ltd
Chris Halfpenny → Parasol Limited
Neil Pomfret → Workwell People Solutions Limited
Venu Adluru → Parasol Limited
Kevin Kayes → Nasa Umbrella Ltd
David Hunt → Nasa Umbrella Ltd
Diogo Diogo → Nasa Umbrella Ltd
Sheela Adesara → PayStream My Max 3 Limited
Craig Conkerton → Parasol Limited
Julie Barton → Parasol Limited
Parag Maniar → PayStream My Max 3 Limited
Vijetha Dayyala → Parasol Limited
Nik Coultas → Clarity Umbrella Ltd
Donna Smith → Parasol Limited
Richard Williams → Nasa Umbrella Ltd
Jonathan Mays → Giant Professional Limited
Basavaraj Puttagangaiah → PayStream My Max 3 Limited
Duncan Macadam → Nasa Umbrella Ltd
Bilgun Yildirim → Nasa Umbrella Ltd
Matthew Garrety → Workwell People Solutions Limited
```

### Umbrella Companies (6)
```
NASA → Nasa Umbrella Ltd → "NASA GROUP" (in files)
PAYSTREAM → PayStream My Max 3 Limited → "PAYSTREAM MYMAX"
PARASOL → Parasol Limited → "PARASOL"
CLARITY → Clarity Umbrella Ltd → "CLARITY"
GIANT → Giant Professional Limited → "GIANT PROFESSIONAL LIMITED (PRG)"
WORKWELL → Workwell People Solutions Limited → "WORKWELL (JSA SERVICES)"
```

### Permanent Staff (Reject if Found)
```
Syed Syed
Victor Cheung
Gareth Jones
Martin Alabone
```

## TECHNICAL SPECIFICATIONS

### Technology Stack
- **Backend**: Python 3.11, AWS Lambda
- **Database**: Aurora Serverless v2 (PostgreSQL 15)
- **Storage**: S3 with versioning
- **API**: API Gateway REST
- **IaC**: AWS SAM (CloudFormation)
- **CI/CD**: GitHub Actions
- **Frontend**: Flask 3.0, Bootstrap 5, jQuery
- **Excel**: openpyxl, pandas
- **Testing**: pytest

### AWS Region
`eu-west-2` (London)

### Cost Constraints
Must stay under £5/month:
- Aurora: 0.5-2 ACU, ~10 hours/month = £2.50
- Lambda: 200 invocations/month = £0.05
- S3: 500 files × 50KB = £0.01
- CloudWatch: 1GB logs = £0.50
- API Gateway: 1000 requests = £0.04
- Total: ~£3.80/month ✅

## PROJECT STRUCTURE

Create this exact directory structure:

```
contractor-pay-tracker/
├── .github/
│   └── workflows/
│       ├── deploy.yml
│       └── test.yml
├── backend/
│   ├── template.yaml              # SAM template (IaC)
│   ├── functions/
│   │   ├── file_upload_handler/
│   │   │   ├── app.py
│   │   │   ├── requirements.txt
│   │   │   └── tests/
│   │   ├── file_processor/
│   │   │   ├── app.py
│   │   │   ├── validator.py
│   │   │   ├── parser.py
│   │   │   ├── requirements.txt
│   │   │   └── tests/
│   │   ├── validation_engine/
│   │   │   ├── app.py
│   │   │   ├── rules.py
│   │   │   ├── requirements.txt
│   │   │   └── tests/
│   │   ├── report_generator/
│   │   │   ├── app.py
│   │   │   ├── requirements.txt
│   │   │   └── tests/
│   │   └── cleanup_handler/
│   │       ├── app.py
│   │       └── requirements.txt
│   ├── layers/
│   │   └── common/
│   │       ├── python/
│   │       │   └── common/
│   │       │       ├── __init__.py
│   │       │       ├── db.py
│   │       │       ├── s3.py
│   │       │       └── logger.py
│   │       └── requirements.txt
│   └── seed-data/
│       ├── seed.sql
│       └── seed.py
├── frontend/
│   ├── app.py
│   ├── config.py
│   ├── requirements.txt
│   ├── static/
│   │   ├── css/
│   │   │   └── styles.css
│   │   ├── js/
│   │   │   ├── upload.js
│   │   │   ├── validation.js
│   │   │   └── reports.js
│   │   └── img/
│   ├── templates/
│   │   ├── base.html
│   │   ├── index.html
│   │   ├── upload.html
│   │   ├── files.html
│   │   ├── validation.html
│   │   ├── reports.html
│   │   └── contractor.html
│   └── utils/
│       ├── api_client.py
│       └── formatters.py
├── tests/
│   ├── fixtures/              # Sample Excel files
│   ├── unit/
│   └── integration/
├── docs/
│   ├── API.md
│   ├── DEPLOYMENT.md
│   └── USER_GUIDE.md
├── .gitignore
├── README.md
├── Makefile
└── pytest.ini
```

## STEP-BY-STEP BUILD PLAN

### Phase 1: Infrastructure & Database (Week 1)
1. Create SAM template with Aurora, S3, basic Lambda, API Gateway
2. Create database schema (all tables, indexes, triggers)
3. Create seed data script
4. Deploy to AWS
5. Verify database connections

### Phase 2: Core Processing (Week 1-2)
1. Implement file_upload_handler Lambda
2. Implement file_processor Lambda:
   - Excel parsing logic
   - Row-by-row processing
   - Error collection
3. Implement validation_engine Lambda:
   - All validation rules
   - Fuzzy name matching
   - Rate validation
   - VAT validation
4. Implement Step Functions orchestration
5. Write comprehensive tests

### Phase 3: Flask UI (Week 2)
1. Create base Flask app with routes
2. Implement upload page with drag-and-drop
3. Implement files list page
4. Implement validation results page
5. Implement dashboard with summary stats
6. Implement reports page with charts

### Phase 4: Reporting & Polish (Week 2-3)
1. Implement report_generator Lambda
2. Create SQL queries for reports
3. Add charts to reports page (Chart.js)
4. Implement contractor detail view
5. Add export functionality

### Phase 5: CI/CD & Documentation (Week 3)
1. Create GitHub Actions workflows
2. Set up automated testing
3. Write comprehensive documentation
4. Create deployment guide
5. Test full deployment from scratch

## CODE QUALITY REQUIREMENTS

### Python Style
- Follow PEP 8
- Type hints for all functions
- Docstrings for all functions/classes
- Max line length: 100 characters
- Use f-strings for formatting

### Error Handling
```python
try:
    result = process_file(file_id)
except FileNotFoundError as e:
    logger.error("File not found", file_id=file_id, error=str(e))
    raise
except ValidationError as e:
    logger.warning("Validation failed", file_id=file_id, errors=e.errors)
    return {"status": "validation_failed", "errors": e.errors}
except Exception as e:
    logger.error("Unexpected error", file_id=file_id, error=str(e), traceback=traceback.format_exc())
    raise
```

### Testing
- Minimum 80% code coverage
- Unit tests for all validation rules
- Integration tests for Lambda functions
- Mocked AWS services (boto3 mocking)
- Test fixtures for all scenarios

## VALIDATION RULE EXAMPLES

### Fuzzy Name Matching
```python
from fuzzywuzzy import fuzz

def find_matching_contractor(surname, forename, golden_data):
    # Try exact match first
    exact_match = golden_data.get(f"{forename} {surname}")
    if exact_match:
        return {"match_type": "EXACT", "contractor": exact_match, "confidence": 100}
    
    # Fuzzy match
    best_match = None
    best_score = 0
    
    for contractor in golden_data.contractors:
        score = fuzz.ratio(
            f"{surname} {forename}".lower(),
            f"{contractor.surname} {contractor.forename}".lower()
        )
        if score > best_score:
            best_score = score
            best_match = contractor
    
    if best_score >= 85:  # Threshold
        return {"match_type": "FUZZY", "contractor": best_match, "confidence": best_score}
    
    return {"match_type": "NOT_FOUND", "contractor": None, "confidence": 0}
```

### Overtime Validation
```python
def validate_overtime_rate(normal_rate, overtime_rate, tolerance_percent=2.0):
    expected_overtime = normal_rate * 1.5
    tolerance = expected_overtime * (tolerance_percent / 100)
    
    if abs(overtime_rate - expected_overtime) <= tolerance:
        return {"valid": True}
    
    return {
        "valid": False,
        "error": f"Overtime rate {overtime_rate:.2f} should be {expected_overtime:.2f} (1.5x {normal_rate:.2f})"
    }
```

### VAT Validation
```python
def validate_vat(amount, vat_amount, vat_rate=0.20):
    expected_vat = amount * vat_rate
    
    if abs(vat_amount - expected_vat) <= 0.01:  # 1p tolerance
        return {"valid": True}
    
    return {
        "valid": False,
        "error": f"VAT {vat_amount:.2f} should be {expected_vat:.2f} (20% of {amount:.2f})"
    }
```

## COMMON DATABASE QUERIES

### Get Pay Summary by Period
```sql
SELECT 
    pp.period_number,
    pp.work_start_date,
    pp.work_end_date,
    uc.short_code as umbrella,
    COUNT(DISTINCT pr.contractor_id) as contractor_count,
    SUM(pr.amount) as total_amount,
    SUM(pr.vat_amount) as total_vat,
    SUM(pr.gross_amount) as total_gross,
    SUM(CASE WHEN pr.record_type = 'OVERTIME' THEN pr.amount ELSE 0 END) as overtime_amount
FROM pay_records pr
JOIN pay_periods pp ON pr.period_id = pp.period_id
JOIN umbrella_companies uc ON pr.umbrella_id = uc.umbrella_id
WHERE pr.is_active = TRUE
  AND pp.period_id = $1
GROUP BY pp.period_number, pp.work_start_date, pp.work_end_date, uc.short_code
ORDER BY uc.short_code;
```

### Get Contractor Pay History
```sql
SELECT 
    pp.period_number,
    pp.work_start_date,
    pp.work_end_date,
    SUM(pr.unit_days) as days_worked,
    AVG(pr.day_rate) as average_rate,
    SUM(pr.amount) as total_pay,
    SUM(CASE WHEN pr.record_type = 'OVERTIME' THEN pr.amount ELSE 0 END) as overtime_pay
FROM pay_records pr
JOIN pay_periods pp ON pr.period_id = pp.period_id
WHERE pr.contractor_id = $1
  AND pr.is_active = TRUE
GROUP BY pp.period_number, pp.work_start_date, pp.work_end_date
ORDER BY pp.work_start_date DESC;
```

### Detect Rate Changes
```sql
SELECT 
    c.first_name,
    c.last_name,
    uc.short_code as umbrella,
    pp.period_number,
    LAG(pr.day_rate) OVER (PARTITION BY pr.contractor_id ORDER BY pp.work_start_date) as previous_rate,
    pr.day_rate as current_rate,
    ROUND(((pr.day_rate - LAG(pr.day_rate) OVER (PARTITION BY pr.contractor_id ORDER BY pp.work_start_date)) 
           / LAG(pr.day_rate) OVER (PARTITION BY pr.contractor_id ORDER BY pp.work_start_date) * 100), 2) as change_percent
FROM pay_records pr
JOIN contractors c ON pr.contractor_id = c.contractor_id
JOIN umbrella_companies uc ON pr.umbrella_id = uc.umbrella_id
JOIN pay_periods pp ON pr.period_id = pp.period_id
WHERE pr.is_active = TRUE
  AND pr.record_type = 'STANDARD'
ORDER BY pp.work_start_date DESC;
```

## SAMPLE FILES PROVIDED

You have these files to test with:
1. `1762530836118_NASA_GCI_Nasstar_Contractor_Pay_Figures_01092025.xlsx` (14 contractors, 20 rows with overtime)
2. `1762530836118_PAYSTREAM_GCI_Nasstar_Contractor_Pay_Figures_01092025.xlsx` (5 contractors)
3. `1762530836119_Clarity_GCI_Nasstar_Contractor_Pay_Figures_01092025.xlsx` (1 contractor)
4. `1762530836119_GIANT_GCI_Nasstar_Contractor_Pay_Figures_01092025.xlsx` (1 contractor, 2 rows with overtime)
5. `1762530836119_Parasol_GCI_Nasstar_Contractor_Pay_Figures_01092025.xlsx` (6 contractors)
6. `1762530836119_WORKWELL_GCI_Nasstar_Contractor_Pay_Figures_01092025.xlsx` (2 contractors)

These are for **Period 8: 28-Jul-25 to 24-Aug-25**, submitted **01-Sep-25**.

Use these files to:
- Test Excel parsing
- Validate fuzzy name matching
- Test overtime detection
- Verify VAT calculations
- Test duplicate period detection (upload twice)
- Create test fixtures

## FINAL NOTES

### What Success Looks Like
1. ✅ User drags 6 Excel files to Flask UI
2. ✅ Files upload to S3 with metadata
3. ✅ Processing begins automatically (or on button click)
4. ✅ System validates all records against golden data
5. ✅ Fuzzy matching catches "Jon Mays" → "Jonathan Mays"
6. ✅ System detects overtime rates are 1.5x
7. ✅ VAT calculated correctly at 20%
8. ✅ If duplicate period detected, user prompted to replace
9. ✅ All valid records imported to database
10. ✅ Dashboard shows summary statistics
11. ✅ Reports show spend by umbrella, top contractors
12. ✅ Full audit trail in database
13. ✅ Comprehensive logs in CloudWatch
14. ✅ Total AWS cost <£5/month

### What to Avoid
- ❌ Hard-coding filenames or formats
- ❌ Assuming employee_id is always numeric
- ❌ Missing validation errors (permissive validation)
- ❌ Inadequate logging
- ❌ Missing audit trail
- ❌ No error handling
- ❌ Expensive AWS resources (large Aurora instances)

### Priority Order
1. **CRITICAL**: Data validation (no bad data enters system)
2. **CRITICAL**: Audit trail (every action logged)
3. **HIGH**: Duplicate detection (prevent double payments)
4. **HIGH**: Processing reliability (retries, error handling)
5. **MEDIUM**: Reporting (can be basic initially)
6. **LOW**: UI polish (functional > beautiful)

## GET STARTED

1. Read the full design document (`ENTERPRISE_SOLUTION_DESIGN.md`)
2. Examine the sample Excel files to understand data format
3. Start with Phase 1: Create SAM template and database schema
4. Test locally with SAM CLI
5. Deploy to AWS
6. Build incrementally, testing each component
7. Write tests as you go (not after)
8. Document your work

**You have everything you need. Build an amazing system! 🚀**
