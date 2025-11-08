# Contractor Pay File Management System - Enterprise Solution Design

## Executive Summary

**Project Name**: Colibri Contractor Pay Tracking System (CPTS)  
**Owner**: Gianluca Formica, Consultancy/Delivery Manager, Colibri Digital  
**Purpose**: Enterprise-grade system to ingest, validate, track, and report on contractor pay files sent to umbrella companies  
**Compliance Focus**: Audit-ready with comprehensive metadata, validation, and audit trails  
**Budget**: <£5/month AWS costs  
**Timeline**: MVP in 2-3 weeks

---

## 1. BUSINESS CONTEXT

### 1.1 The Problem
Colibri Digital pays contractors through 6 umbrella companies every 4 weeks. Currently:
- Manual tracking via Excel spreadsheets
- No validation of contractor names, rates, or umbrella company associations
- Risk of duplicate submissions
- Difficult to generate management reports
- Poor audit trail for compliance

### 1.2 The Solution
Automated pay file ingestion system with:
- Drag-and-drop web UI for file uploads
- Automated validation against golden reference data
- Duplicate detection with replacement workflow
- Comprehensive audit trail
- Management reporting dashboard
- Enterprise-grade metadata tracking

### 1.3 Success Criteria
- ✅ Zero duplicate payments
- ✅ 100% contractor-umbrella validation
- ✅ Audit trail for every file and record
- ✅ Management reports in <5 seconds
- ✅ <£5/month running costs
- ✅ Deployment via single command (CI/CD)

---

## 2. BUSINESS RULES & VALIDATION

### 2.1 Golden Reference Data

#### Contractors (23 Active)
```
First Name, Last Name, Umbrella Company
Gary, Mandaracas, PayStream My Max 3 Limited
Graeme, Oldroyd, PayStream My Max 3 Limited
Barry, Breden, Nasa Umbrella Ltd
James, Matthews, Nasa Umbrella Ltd
Chris, Halfpenny, Parasol Limited
Neil, Pomfret, Workwell People Solutions Limited
Venu, Adluru, Parasol Limited
Kevin, Kayes, Nasa Umbrella Ltd
David, Hunt, Nasa Umbrella Ltd
Diogo, Diogo, Nasa Umbrella Ltd
Sheela, Adesara, PayStream My Max 3 Limited
Craig, Conkerton, Parasol Limited
Julie, Barton, Parasol Limited
Parag, Maniar, PayStream My Max 3 Limited
Vijetha, Dayyala, Parasol Limited
Nik, Coultas, Clarity Umbrella Ltd
Donna, Smith, Parasol Limited
Richard, Williams, Nasa Umbrella Ltd
Jonathan, Mays, Giant Professional Limited
Basavaraj, Puttagangaiah, PayStream My Max 3 Limited
Duncan, Macadam, Nasa Umbrella Ltd
Bilgun, Yildirim, Nasa Umbrella Ltd
Matthew, Garrety, Workwell People Solutions Limited
```

#### Permanent Staff (Reject if found in pay files)
```
Syed, Syed
Victor, Cheung
Gareth, Jones
Martin, Alabone
```

#### Umbrella Companies (6 Active)
```
Short Code, Legal Name, File Company Name Variation
NASA, Nasa Umbrella Ltd, "NASA GROUP"
PAYSTREAM, PayStream My Max 3 Limited, "PAYSTREAM MYMAX"
PARASOL, Parasol Limited, "PARASOL"
CLARITY, Clarity Umbrella Ltd, "CLARITY"
GIANT, Giant Professional Limited, "GIANT PROFESSIONAL LIMITED (PRG)"
WORKWELL, Workwell People Solutions Limited, "WORKWELL (JSA SERVICES)"
```

### 2.2 Pay Schedule (2025-2026)

| Period | Work Start | Work End | Submission Date | Payment Date | Status |
|--------|-----------|----------|----------------|--------------|--------|
| 1 | 13-Jan-25 | 09-Feb-25 | 10-Feb-25 | 21-Feb-25 | Completed |
| 2 | 10-Feb-25 | 09-Mar-25 | 10-Mar-25 | 21-Mar-25 | Completed |
| 3 | 10-Mar-25 | 06-Apr-25 | 07-Apr-25 | 18-Apr-25 | Completed |
| 4 | 07-Apr-25 | 04-May-25 | 06-May-25 | 16-May-25 | Completed |
| 5 | 05-May-25 | 01-Jun-25 | 02-Jun-25 | 13-Jun-25 | Completed |
| 6 | 02-Jun-25 | 29-Jun-25 | 07-Jul-25 | 11-Jul-25 | Completed |
| 7 | 30-Jun-25 | 27-Jul-25 | 04-Aug-25 | 08-Aug-25 | Completed |
| 8 | 28-Jul-25 | 24-Aug-25 | 01-Sep-25 | 05-Sep-25 | Completed |
| 9 | 25-Aug-25 | 21-Sep-25 | 29-Sep-25 | 03-Oct-25 | Completed |
| 10 | 22-Sep-25 | 19-Oct-25 | 27-Oct-25 | 31-Oct-25 | Pending |
| 11 | 20-Oct-25 | 16-Nov-25 | 24-Nov-25 | 28-Nov-25 | Pending |
| 12 | 17-Nov-25 | 14-Dec-25 | TBD | 24-Dec-25 | Pending |
| 13 | 15-Dec-25 | 11-Jan-26 | 19-Jan-26 | 23-Jan-26 | Future |

### 2.3 System Parameters

```python
SYSTEM_PARAMETERS = {
    "VAT_RATE": 0.20,  # Fixed 20% UK VAT
    "HOURS_PER_DAY": 7.5,  # Standard working day
    "OVERTIME_MULTIPLIER": 1.5,  # Overtime = 1.5x normal rate
    "OVERTIME_TOLERANCE_PERCENT": 2.0,  # Allow ±2% rounding errors
    "RATE_CHANGE_ALERT_PERCENT": 5.0,  # Flag if rate changes >5%
    "NAME_MATCH_THRESHOLD": 85,  # Fuzzy match confidence %
    "SUBMISSION_DATE_TOLERANCE_DAYS": 3,  # Accept files ±3 days
    "CURRENCY": "GBP",
    "LOCALE": "en_GB"
}
```

### 2.4 Validation Rules

#### Rule 1: Contractor Existence Check
```
IF contractor (firstname, lastname) NOT IN golden_data:
  IF similarity_score >= 85%:
    FLAG as "POSSIBLE_MATCH" with suggestions
  ELSE:
    ERROR: "Unknown contractor"
```

#### Rule 2: Permanent Staff Check
```
IF contractor IN permanent_staff_list:
  ERROR: "CRITICAL - Permanent staff in contractor file"
  REJECT entire file
```

#### Rule 3: Umbrella Company Validation
```
IF contractor.umbrella != file.umbrella:
  ERROR: "Contractor assigned to wrong umbrella company"
  Expected: {correct_umbrella}
  Found: {file_umbrella}
```

#### Rule 4: Rate Validation
```
IF is_overtime:
  expected_rate = base_rate * 1.5
  tolerance = expected_rate * 0.02
  IF abs(actual_rate - expected_rate) > tolerance:
    ERROR: "Invalid overtime rate"
ELSE:
  IF abs(actual_rate - known_rate) / known_rate > 0.05:
    WARNING: "Rate changed by >5%"
    LOG rate change for review
```

#### Rule 5: VAT Validation
```
expected_vat = amount * 0.20
IF abs(vat_amount - expected_vat) > 0.01:
  ERROR: "VAT calculation incorrect"
```

#### Rule 6: Employee ID Consistency
```
IF employee_id EXISTS in database:
  IF employee_id.contractor != current_contractor:
    ERROR: "Employee ID reused for different person"
```

#### Rule 7: Duplicate Period Detection
```
IF pay_file_exists(umbrella_id, period_id):
  PROMPT: "Replace existing data or cancel?"
  IF replace:
    MARK old records as superseded
    IMPORT new file
  ELSE:
    CANCEL import
```

---

## 3. TECHNICAL ARCHITECTURE

### 3.1 Technology Stack

#### Infrastructure
- **Cloud Provider**: AWS (London eu-west-2 region)
- **IaC Tool**: AWS SAM (Serverless Application Model)
- **Version Control**: GitHub
- **CI/CD**: GitHub Actions

#### Backend
- **API**: AWS API Gateway (REST)
- **Compute**: AWS Lambda (Python 3.11)
- **Orchestration**: AWS Step Functions
- **Database**: Amazon Aurora Serverless v2 (PostgreSQL 15)
- **File Storage**: Amazon S3 (versioning enabled)
- **Secrets**: AWS Secrets Manager
- **Logging**: CloudWatch Logs (JSON structured)
- **Monitoring**: CloudWatch Metrics + Alarms

#### Frontend
- **Local Dev**: Flask 3.0 + Bootstrap 5
- **File Upload**: Drag-and-drop with progress bars
- **Environment**: Python venv for local development

#### Development
- **Language**: Python 3.11
- **Package Manager**: pip
- **Linting**: ruff
- **Testing**: pytest
- **Excel Processing**: openpyxl, pandas

### 3.2 System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    FLASK WEB UI (Local)                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ File Upload  │  │  Validation  │  │   Reports    │      │
│  │ (Drag/Drop)  │  │   Status     │  │  Dashboard   │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                            │ HTTPS
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    AWS API GATEWAY                           │
│  /upload, /process, /status, /reports                       │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    AWS LAMBDA FUNCTIONS                      │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │ File Upload  │  │  Processor   │  │   Reports    │     │
│  │   Handler    │  │  Validator   │  │   Generator  │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
│         │                 │                  │              │
└─────────┼─────────────────┼──────────────────┼──────────────┘
          │                 │                  │
          ▼                 ▼                  ▼
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│   Amazon S3     │  │  Step Functions │  │ Aurora Postgres │
│  (Pay Files)    │  │  (Orchestrate)  │  │   (Metadata)    │
└─────────────────┘  └─────────────────┘  └─────────────────┘
          │                                       │
          └───────────────┬───────────────────────┘
                          ▼
                ┌─────────────────┐
                │  CloudWatch     │
                │  Logs & Metrics │
                └─────────────────┘
```

### 3.3 Data Flow

#### Upload Flow
```
1. User drags files to Flask UI
2. Flask uploads to /upload API endpoint
3. Lambda writes to S3 with metadata
4. S3 event triggers Step Function
5. Step Function orchestrates validation
6. Validation results stored in DB
7. UI polls /status endpoint for progress
8. User sees validation report
```

#### Processing Flow
```
1. User clicks "Process Approved Files"
2. Lambda reads Excel from S3
3. Parse rows into structured data
4. For each row:
   a. Validate contractor name (fuzzy match)
   b. Validate umbrella company
   c. Validate rates (normal vs overtime)
   d. Validate VAT calculation
   e. Check for duplicates
5. If errors: Store in validation_errors table
6. If warnings: Store in validation_warnings table
7. If OK: Insert into pay_records table
8. Update file_metadata status
9. Return summary to user
```

---

## 4. DATABASE SCHEMA

### 4.1 PostgreSQL Schema

```sql
-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================================================
-- REFERENCE DATA TABLES
-- ============================================================================

-- Umbrella Companies
CREATE TABLE umbrella_companies (
    umbrella_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    short_code VARCHAR(20) UNIQUE NOT NULL,  -- NASA, PAYSTREAM, etc.
    legal_name VARCHAR(200) NOT NULL,        -- Nasa Umbrella Ltd
    file_name_variation VARCHAR(200),        -- NASA GROUP (as appears in files)
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_umbrella_short_code ON umbrella_companies(short_code);

-- Contractors (Golden Reference Data)
CREATE TABLE contractors (
    contractor_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    normalized_name VARCHAR(200) NOT NULL,  -- Lowercase, no special chars
    primary_umbrella_id UUID REFERENCES umbrella_companies(umbrella_id),
    job_title VARCHAR(200),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(first_name, last_name)
);

CREATE INDEX idx_contractor_normalized_name ON contractors(normalized_name);
CREATE INDEX idx_contractor_umbrella ON contractors(primary_umbrella_id);

-- Permanent Staff (DO NOT PAY via umbrellas)
CREATE TABLE permanent_staff (
    staff_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    normalized_name VARCHAR(200) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(first_name, last_name)
);

-- Pay Periods (4-week cycles)
CREATE TABLE pay_periods (
    period_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    period_number INTEGER NOT NULL,         -- 1, 2, 3...
    period_year INTEGER NOT NULL,           -- 2025, 2026...
    work_start_date DATE NOT NULL,
    work_end_date DATE NOT NULL,
    submission_date DATE NOT NULL,
    payment_date DATE NOT NULL,
    status VARCHAR(20) NOT NULL,            -- PENDING, COMPLETED, CANCELLED
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(period_number, period_year)
);

CREATE INDEX idx_period_dates ON pay_periods(work_start_date, work_end_date);
CREATE INDEX idx_period_submission ON pay_periods(submission_date);

-- System Parameters
CREATE TABLE system_parameters (
    param_key VARCHAR(100) PRIMARY KEY,
    param_value VARCHAR(500) NOT NULL,
    data_type VARCHAR(20) NOT NULL,        -- DECIMAL, INTEGER, STRING, BOOLEAN
    description TEXT,
    is_editable BOOLEAN DEFAULT FALSE,
    updated_at TIMESTAMP DEFAULT NOW(),
    updated_by VARCHAR(200)
);

-- ============================================================================
-- OPERATIONAL DATA TABLES
-- ============================================================================

-- Pay File Metadata
CREATE TABLE pay_files_metadata (
    file_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    umbrella_id UUID NOT NULL REFERENCES umbrella_companies(umbrella_id),
    period_id UUID NOT NULL REFERENCES pay_periods(period_id),
    
    -- File Information
    original_filename VARCHAR(500) NOT NULL,
    s3_bucket VARCHAR(200) NOT NULL,
    s3_key VARCHAR(500) NOT NULL,
    s3_version_id VARCHAR(200),
    file_size_bytes BIGINT,
    file_hash_sha256 VARCHAR(64),
    
    -- Processing Status
    status VARCHAR(20) NOT NULL DEFAULT 'UPLOADED',  
    -- UPLOADED, PROCESSING, VALIDATED, COMPLETED, ERROR, SUPERSEDED
    
    -- Timestamps
    uploaded_at TIMESTAMP DEFAULT NOW(),
    processing_started_at TIMESTAMP,
    processing_completed_at TIMESTAMP,
    superseded_at TIMESTAMP,
    
    -- User Tracking
    uploaded_by VARCHAR(200),
    
    -- Processing Results
    total_records INTEGER,
    valid_records INTEGER,
    error_records INTEGER,
    warning_records INTEGER,
    
    -- Financial Totals (for quick validation)
    total_amount DECIMAL(12,2),
    total_vat DECIMAL(12,2),
    total_gross DECIMAL(12,2),
    
    -- Metadata
    version INTEGER DEFAULT 1,
    is_current_version BOOLEAN DEFAULT TRUE,
    superseded_by UUID REFERENCES pay_files_metadata(file_id),
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    UNIQUE(umbrella_id, period_id, is_current_version)  -- Only 1 current version per umbrella+period
);

CREATE INDEX idx_payfile_umbrella_period ON pay_files_metadata(umbrella_id, period_id);
CREATE INDEX idx_payfile_status ON pay_files_metadata(status);
CREATE INDEX idx_payfile_s3_key ON pay_files_metadata(s3_key);

-- Contractor-Umbrella Associations (track employee IDs)
CREATE TABLE contractor_umbrella_associations (
    association_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    contractor_id UUID NOT NULL REFERENCES contractors(contractor_id),
    umbrella_id UUID NOT NULL REFERENCES umbrella_companies(umbrella_id),
    employee_id VARCHAR(50) NOT NULL,       -- Umbrella company's ID for this contractor
    
    -- Validity Period
    valid_from DATE NOT NULL,
    valid_to DATE,
    is_active BOOLEAN DEFAULT TRUE,
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    UNIQUE(umbrella_id, employee_id)        -- Employee ID unique per umbrella
);

CREATE INDEX idx_assoc_contractor ON contractor_umbrella_associations(contractor_id);
CREATE INDEX idx_assoc_umbrella ON contractor_umbrella_associations(umbrella_id);
CREATE INDEX idx_assoc_employee_id ON contractor_umbrella_associations(employee_id);

-- Pay Records (individual line items from files)
CREATE TABLE pay_records (
    record_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    file_id UUID NOT NULL REFERENCES pay_files_metadata(file_id),
    contractor_id UUID NOT NULL REFERENCES contractors(contractor_id),
    umbrella_id UUID NOT NULL REFERENCES umbrella_companies(umbrella_id),
    period_id UUID NOT NULL REFERENCES pay_periods(period_id),
    association_id UUID REFERENCES contractor_umbrella_associations(association_id),
    
    -- Pay Details
    employee_id VARCHAR(50) NOT NULL,
    unit_days DECIMAL(5,2) NOT NULL,
    day_rate DECIMAL(10,2) NOT NULL,
    amount DECIMAL(12,2) NOT NULL,
    vat_amount DECIMAL(12,2) NOT NULL,
    gross_amount DECIMAL(12,2) NOT NULL,
    total_hours DECIMAL(6,2),
    
    -- Record Type
    record_type VARCHAR(20) NOT NULL,       -- STANDARD, OVERTIME, EXPENSE
    notes TEXT,
    
    -- Status
    is_active BOOLEAN DEFAULT TRUE,         -- FALSE if superseded
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_payrecord_file ON pay_records(file_id);
CREATE INDEX idx_payrecord_contractor ON pay_records(contractor_id);
CREATE INDEX idx_payrecord_period ON pay_records(period_id);
CREATE INDEX idx_payrecord_type ON pay_records(record_type);
CREATE INDEX idx_payrecord_active ON pay_records(is_active);

-- Rate History (track rate changes over time)
CREATE TABLE rate_history (
    rate_history_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    contractor_id UUID NOT NULL REFERENCES contractors(contractor_id),
    umbrella_id UUID NOT NULL REFERENCES umbrella_companies(umbrella_id),
    period_id UUID NOT NULL REFERENCES pay_periods(period_id),
    
    previous_rate DECIMAL(10,2),
    new_rate DECIMAL(10,2) NOT NULL,
    rate_change_percent DECIMAL(5,2),
    
    detected_at TIMESTAMP DEFAULT NOW(),
    reviewed BOOLEAN DEFAULT FALSE,
    reviewed_by VARCHAR(200),
    reviewed_at TIMESTAMP,
    notes TEXT
);

CREATE INDEX idx_rate_contractor ON rate_history(contractor_id);
CREATE INDEX idx_rate_period ON rate_history(period_id);

-- ============================================================================
-- VALIDATION & AUDIT TABLES
-- ============================================================================

-- Validation Errors
CREATE TABLE validation_errors (
    error_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    file_id UUID NOT NULL REFERENCES pay_files_metadata(file_id),
    
    error_type VARCHAR(50) NOT NULL,
    -- UNKNOWN_CONTRACTOR, WRONG_UMBRELLA, INVALID_RATE, 
    -- INVALID_VAT, PERMANENT_STAFF, DUPLICATE_EMPLOYEE_ID, etc.
    
    severity VARCHAR(20) NOT NULL,          -- CRITICAL, ERROR, WARNING
    
    row_number INTEGER,
    employee_id VARCHAR(50),
    contractor_name VARCHAR(200),
    
    error_message TEXT NOT NULL,
    suggested_fix TEXT,
    
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_error_file ON validation_errors(file_id);
CREATE INDEX idx_error_type ON validation_errors(error_type);
CREATE INDEX idx_error_severity ON validation_errors(severity);

-- Validation Warnings
CREATE TABLE validation_warnings (
    warning_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    file_id UUID NOT NULL REFERENCES pay_files_metadata(file_id),
    record_id UUID REFERENCES pay_records(record_id),
    
    warning_type VARCHAR(50) NOT NULL,
    -- RATE_CHANGE, FUZZY_NAME_MATCH, UNUSUAL_HOURS, etc.
    
    warning_message TEXT NOT NULL,
    auto_resolved BOOLEAN DEFAULT FALSE,
    resolution_notes TEXT,
    
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_warning_file ON validation_warnings(file_id);
CREATE INDEX idx_warning_type ON validation_warnings(warning_type);

-- Audit Log (tracks ALL changes)
CREATE TABLE audit_log (
    audit_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    table_name VARCHAR(100) NOT NULL,
    record_id UUID NOT NULL,
    action VARCHAR(20) NOT NULL,            -- INSERT, UPDATE, DELETE
    
    old_values JSONB,
    new_values JSONB,
    changed_fields TEXT[],
    
    user_email VARCHAR(200),
    ip_address VARCHAR(50),
    
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_audit_table ON audit_log(table_name);
CREATE INDEX idx_audit_record ON audit_log(record_id);
CREATE INDEX idx_audit_action ON audit_log(action);
CREATE INDEX idx_audit_created ON audit_log(created_at);

-- Processing Log (detailed execution logs)
CREATE TABLE processing_log (
    log_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    file_id UUID REFERENCES pay_files_metadata(file_id),
    lambda_request_id VARCHAR(200),
    step_function_execution_arn VARCHAR(500),
    
    log_level VARCHAR(20) NOT NULL,         -- DEBUG, INFO, WARNING, ERROR, CRITICAL
    component VARCHAR(100),                 -- validator, parser, importer, etc.
    
    message TEXT NOT NULL,
    context JSONB,
    
    execution_time_ms INTEGER,
    
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_proclog_file ON processing_log(file_id);
CREATE INDEX idx_proclog_level ON processing_log(log_level);
CREATE INDEX idx_proclog_created ON processing_log(created_at);

```

### 4.2 Seed Data SQL

```sql
-- Insert System Parameters
INSERT INTO system_parameters (param_key, param_value, data_type, description, is_editable) VALUES
('VAT_RATE', '0.20', 'DECIMAL', 'UK VAT rate (20%)', FALSE),
('HOURS_PER_DAY', '7.5', 'DECIMAL', 'Standard working hours per day', TRUE),
('OVERTIME_MULTIPLIER', '1.5', 'DECIMAL', 'Overtime rate multiplier', FALSE),
('OVERTIME_TOLERANCE_PERCENT', '2.0', 'DECIMAL', 'Allowed variance in overtime rate (%)', TRUE),
('RATE_CHANGE_ALERT_PERCENT', '5.0', 'DECIMAL', 'Alert if rate changes by more than this %', TRUE),
('NAME_MATCH_THRESHOLD', '85', 'INTEGER', 'Fuzzy name matching threshold (0-100)', TRUE);

-- Insert Umbrella Companies
INSERT INTO umbrella_companies (short_code, legal_name, file_name_variation) VALUES
('NASA', 'Nasa Umbrella Ltd', 'NASA GROUP'),
('PAYSTREAM', 'PayStream My Max 3 Limited', 'PAYSTREAM MYMAX'),
('PARASOL', 'Parasol Limited', 'PARASOL'),
('CLARITY', 'Clarity Umbrella Ltd', 'CLARITY'),
('GIANT', 'Giant Professional Limited', 'GIANT PROFESSIONAL LIMITED (PRG)'),
('WORKWELL', 'Workwell People Solutions Limited', 'WORKWELL (JSA SERVICES)');

-- Insert Permanent Staff (to reject if found in pay files)
INSERT INTO permanent_staff (first_name, last_name, normalized_name) VALUES
('Syed', 'Syed', 'syed syed'),
('Victor', 'Cheung', 'victor cheung'),
('Gareth', 'Jones', 'gareth jones'),
('Martin', 'Alabone', 'martin alabone');

-- Insert Pay Periods
INSERT INTO pay_periods (period_number, period_year, work_start_date, work_end_date, submission_date, payment_date, status) VALUES
(1, 2025, '2025-01-13', '2025-02-09', '2025-02-10', '2025-02-21', 'COMPLETED'),
(2, 2025, '2025-02-10', '2025-03-09', '2025-03-10', '2025-03-21', 'COMPLETED'),
(3, 2025, '2025-03-10', '2025-04-06', '2025-04-07', '2025-04-18', 'COMPLETED'),
(4, 2025, '2025-04-07', '2025-05-04', '2025-05-06', '2025-05-16', 'COMPLETED'),
(5, 2025, '2025-05-05', '2025-06-01', '2025-06-02', '2025-06-13', 'COMPLETED'),
(6, 2025, '2025-06-02', '2025-06-29', '2025-07-07', '2025-07-11', 'COMPLETED'),
(7, 2025, '2025-06-30', '2025-07-27', '2025-08-04', '2025-08-08', 'COMPLETED'),
(8, 2025, '2025-07-28', '2025-08-24', '2025-09-01', '2025-09-05', 'COMPLETED'),
(9, 2025, '2025-08-25', '2025-09-21', '2025-09-29', '2025-10-03', 'COMPLETED'),
(10, 2025, '2025-09-22', '2025-10-19', '2025-10-27', '2025-10-31', 'PENDING'),
(11, 2025, '2025-10-20', '2025-11-16', '2025-11-24', '2025-11-28', 'PENDING'),
(12, 2025, '2025-11-17', '2025-12-14', '2025-12-15', '2025-12-24', 'PENDING'),
(13, 2025, '2025-12-15', '2026-01-11', '2026-01-19', '2026-01-23', 'PENDING');

-- Insert Contractors (with umbrella associations)
-- Note: umbrella_id will be filled via lookup in actual seed script
-- This is pseudo-SQL for demonstration

-- NASA contractors
INSERT INTO contractors (first_name, last_name, normalized_name, job_title) VALUES
('Barry', 'Breden', 'barry breden', 'Solution Designer'),
('James', 'Matthews', 'james matthews', 'Solution Designer'),
('Kevin', 'Kayes', 'kevin kayes', 'Lead Solution Designer'),
('David', 'Hunt', 'david hunt', 'Solution Designer'),
('Diogo', 'Diogo', 'diogo diogo', 'Solution Designer'),
('Donna', 'Smith', 'donna smith', 'Junior Reference Engineer'),
('Richard', 'Williams', 'richard williams', 'Solution Designer'),
('Bilgun', 'Yildirim', 'bilgun yildirim', 'Solution Designer'),
('Duncan', 'Macadam', 'duncan macadam', 'Solution Designer');

-- PAYSTREAM contractors
INSERT INTO contractors (first_name, last_name, normalized_name, job_title) VALUES
('Gary', 'Mandaracas', 'gary mandaracas', 'Solution Designer'),
('Graeme', 'Oldroyd', 'graeme oldroyd', 'Lead Solution Designer'),
('Sheela', 'Adesara', 'sheela adesara', 'Lead Solution Designer'),
('Parag', 'Maniar', 'parag maniar', 'Lead Solution Designer'),
('Basavaraj', 'Puttagangaiah', 'basavaraj puttagangaiah', 'Solution Designer');

-- PARASOL contractors
INSERT INTO contractors (first_name, last_name, normalized_name, job_title) VALUES
('Chris', 'Halfpenny', 'chris halfpenny', 'Junior Reference Engineer'),
('Venu', 'Adluru', 'venu adluru', 'Reference Engineer'),
('Craig', 'Conkerton', 'craig conkerton', 'Senior Reference Engineer'),
('Julie', 'Barton', 'julie barton', 'Reference Engineer'),
('Vijetha', 'Dayyala', 'vijetha dayyala', 'Junior Reference Engineer');

-- WORKWELL contractors
INSERT INTO contractors (first_name, last_name, normalized_name, job_title) VALUES
('Neil', 'Pomfret', 'neil pomfret', 'Solution Designer'),
('Matthew', 'Garrety', 'matthew garrety', 'Solution Designer');

-- GIANT contractors
INSERT INTO contractors (first_name, last_name, normalized_name, job_title) VALUES
('Jonathan', 'Mays', 'jonathan mays', 'Solution Designer');

-- CLARITY contractors
INSERT INTO contractors (first_name, last_name, normalized_name, job_title) VALUES
('Nik', 'Coultas', 'nik coultas', 'Programme Manager');
```

---

## 5. API ENDPOINTS

### 5.1 REST API Specification

#### Base URL
```
Local Dev: http://localhost:5000/api/v1
Production: https://{api-id}.execute-api.eu-west-2.amazonaws.com/prod/api/v1
```

#### Authentication
- Local Dev: No auth (trusted network)
- Production: IAM-based auth (future: Cognito for multi-user)

### 5.2 Endpoint Details

#### POST /upload
Upload pay files to S3 for processing.

**Request (multipart/form-data)**
```json
{
  "files": [FileObject, FileObject, ...],
  "uploaded_by": "gianluca.formica@colibridigital.co.uk",
  "notes": "Period 8 files - corrected NASA file"
}
```

**Response (200 OK)**
```json
{
  "status": "success",
  "files_uploaded": 6,
  "results": [
    {
      "filename": "NASA_GCI_Nasstar_Contractor_Pay_Figures_01092025.xlsx",
      "file_id": "550e8400-e29b-41d4-a716-446655440000",
      "s3_key": "uploads/2025/09/NASA_01092025_abc123.xlsx",
      "size_bytes": 57344,
      "status": "UPLOADED"
    }
  ]
}
```

#### POST /process
Trigger processing of uploaded files.

**Request**
```json
{
  "file_ids": [
    "550e8400-e29b-41d4-a716-446655440000",
    "660f9511-f30c-52e5-b827-557766551111"
  ],
  "processing_options": {
    "auto_resolve_warnings": false,
    "strict_validation": true
  }
}
```

**Response (202 Accepted)**
```json
{
  "status": "processing_started",
  "job_id": "770g0622-g41d-63f6-c938-668877662222",
  "step_function_arn": "arn:aws:states:...",
  "check_status_url": "/api/v1/status/770g0622..."
}
```

#### GET /status/{job_id}
Check processing status.

**Response (200 OK)**
```json
{
  "job_id": "770g0622-g41d-63f6-c938-668877662222",
  "status": "COMPLETED",
  "files_processed": 6,
  "total_records": 42,
  "valid_records": 40,
  "warnings": 2,
  "errors": 0,
  "started_at": "2025-09-01T15:23:12Z",
  "completed_at": "2025-09-01T15:23:45Z",
  "execution_time_seconds": 33,
  "details": [
    {
      "file_id": "550e8400-e29b-41d4-a716-446655440000",
      "filename": "NASA_GCI_Nasstar_Contractor_Pay_Figures_01092025.xlsx",
      "status": "COMPLETED",
      "records": 14,
      "errors": 0,
      "warnings": 1,
      "warnings_detail": [
        {
          "type": "RATE_CHANGE",
          "message": "David Hunt rate changed from £472.00 to £472.03 (0.06%)"
        }
      ]
    }
  ]
}
```

#### GET /files
List all uploaded files with filters.

**Query Parameters**
- `period_id` (UUID): Filter by pay period
- `umbrella_id` (UUID): Filter by umbrella company
- `status` (string): UPLOADED, PROCESSING, COMPLETED, ERROR, SUPERSEDED
- `from_date` (date): Filter files uploaded after this date
- `to_date` (date): Filter files uploaded before this date
- `limit` (int): Max results (default 50)
- `offset` (int): Pagination offset

**Response (200 OK)**
```json
{
  "total": 156,
  "limit": 50,
  "offset": 0,
  "files": [
    {
      "file_id": "550e8400-e29b-41d4-a716-446655440000",
      "filename": "NASA_GCI_Nasstar_Contractor_Pay_Figures_01092025.xlsx",
      "umbrella": "NASA",
      "period": "Period 8 (28-Jul-25 to 24-Aug-25)",
      "status": "COMPLETED",
      "total_amount": 127456.50,
      "total_vat": 25491.30,
      "uploaded_at": "2025-09-01T15:23:12Z",
      "processed_at": "2025-09-01T15:23:45Z"
    }
  ]
}
```

#### DELETE /files/{file_id}
Delete a file and all associated records (soft delete for audit trail). **CRITICAL FOR TESTING WORKFLOW**.

**Request**
```json
{
  "confirm": true,
  "reason": "Testing - re-importing with validation fixes"
}
```

**Response (200 OK)**
```json
{
  "status": "deleted",
  "file_id": "550e8400-e29b-41d4-a716-446655440000",
  "filename": "NASA_GCI_Nasstar_Contractor_Pay_Figures_01092025.xlsx",
  "umbrella": "NASA",
  "period": "Period 8 (28-Jul-25 to 24-Aug-25)",
  "records_deleted": 14,
  "total_amount_removed": 127456.50,
  "total_vat_removed": 25491.30,
  "contractors_affected": [
    "David Hunt",
    "Barry Breden",
    "James Matthews"
  ],
  "message": "File and all associated records marked as deleted",
  "audit_log_id": "abc-123-def-456",
  "can_reimport": true
}
```

**What it does**:
1. Updates `pay_files_metadata.status = 'DELETED'`
2. Sets `pay_files_metadata.is_current_version = FALSE`
3. Sets `pay_records.is_active = FALSE` for all records from this file
4. Sets `validation_errors/warnings` as resolved
5. Logs deletion in `audit_log` with user, timestamp, reason
6. Does NOT physically delete data (maintains audit trail)
7. Allows same file to be re-imported immediately

**Use case**: 
```
Testing workflow:
1. Import NASA file → validation error detected
2. DELETE file → removes all 14 records
3. Fix validation code → deploy in 2 minutes
4. Re-import NASA file → validation passes
5. All records fresh and correct
```

#### POST /files/bulk-delete
Delete multiple files at once (useful for clearing test data).

**Request**
```json
{
  "file_ids": [
    "550e8400-e29b-41d4-a716-446655440000",
    "660f9511-f30c-52e5-b827-557766551111"
  ],
  "confirm": true,
  "reason": "Clearing Period 8 test data"
}
```

**Response (200 OK)**
```json
{
  "status": "deleted",
  "files_deleted": 2,
  "total_records_deleted": 20,
  "total_amount_removed": 184345.50,
  "details": [
    {
      "file_id": "550e8400...",
      "filename": "NASA_...",
      "records_deleted": 14
    },
    {
      "file_id": "660f9511...",
      "filename": "PAYSTREAM_...",
      "records_deleted": 6
    }
  ]
}
```

#### DELETE /periods/{period_id}/umbrella/{umbrella_id}
Delete ALL files for specific umbrella + period combination.

**Response (200 OK)**
```json
{
  "status": "deleted",
  "period": "Period 8 (28-Jul-25 to 24-Aug-25)",
  "umbrella": "NASA",
  "files_deleted": 1,
  "records_deleted": 14,
  "contractors_affected": 9,
  "message": "All NASA data for Period 8 removed"
}
```

#### POST /dev/flush-data (DEVELOPMENT ONLY)
**DANGER ZONE**: Truncate all operational data. Only available when `ENVIRONMENT=development`.

**Request**
```json
{
  "confirmation": "DELETE ALL",
  "keep_reference_data": true
}
```

**Response (200 OK)**
```json
{
  "status": "flushed",
  "environment": "development",
  "tables_truncated": [
    "pay_records",
    "pay_files_metadata",
    "contractor_umbrella_associations", 
    "validation_errors",
    "validation_warnings",
    "rate_history",
    "processing_log"
  ],
  "reference_data_preserved": [
    "contractors (23 records)",
    "umbrella_companies (6 records)",
    "permanent_staff (4 records)",
    "pay_periods (13 records)",
    "system_parameters (6 records)"
  ],
  "message": "Database ready for fresh imports"
}
```

**Safety**: 
- Only works if `ENVIRONMENT=development`
- Returns 403 Forbidden in production
- Requires exact confirmation string
- Logs the flush action with timestamp and user

#### GET /reports/summary
Get high-level summary statistics.

**Query Parameters**
- `period_ids` (UUID[]): Filter by specific periods
- `from_date` (date): Start of date range
- `to_date` (date): End of date range

**Response (200 OK)**
```json
{
  "period": "2025-Q3",
  "total_spend": 1245678.90,
  "total_vat": 249135.78,
  "contractor_count": 23,
  "by_umbrella": [
    {
      "umbrella": "NASA",
      "spend": 567890.12,
      "vat": 113578.02,
      "contractor_count": 9
    }
  ],
  "top_contractors": [
    {
      "name": "Duncan Macadam",
      "umbrella": "NASA",
      "total_pay": 48000.00,
      "periods_worked": 8
    }
  ],
  "overtime_total": 45678.90,
  "expense_total": 0.00
}
```

#### GET /reports/contractor/{contractor_id}
Get detailed contractor pay history.

**Response (200 OK)**
```json
{
  "contractor": {
    "name": "David Hunt",
    "umbrella": "NASA",
    "job_title": "Solution Designer",
    "is_active": true
  },
  "summary": {
    "total_periods_worked": 9,
    "total_days_worked": 171.5,
    "total_pay": 80956.35,
    "average_daily_rate": 472.03,
    "overtime_days": 7.5,
    "overtime_pay": 5310.45
  },
  "rate_history": [
    {
      "period": "Period 1 (13-Jan-25 to 09-Feb-25)",
      "rate": 470.00,
      "days": 20
    },
    {
      "period": "Period 2 (10-Feb-25 to 09-Mar-25)",
      "rate": 472.03,
      "days": 18.5
    }
  ],
  "recent_payments": [...]
}
```

#### GET /validation/errors
Get validation errors for review.

**Query Parameters**
- `file_id` (UUID): Filter by file
- `severity` (string): CRITICAL, ERROR, WARNING
- `error_type` (string): Filter by specific error type

**Response (200 OK)**
```json
{
  "total_errors": 3,
  "errors": [
    {
      "error_id": "...",
      "file_id": "...",
      "filename": "NASA_...",
      "error_type": "WRONG_UMBRELLA",
      "severity": "ERROR",
      "row_number": 5,
      "contractor_name": "Donna Smith",
      "message": "Donna Smith assigned to PARASOL, found in NASA file",
      "suggested_fix": "Move to PARASOL file or update contractor umbrella",
      "created_at": "2025-09-01T15:23:35Z"
    }
  ]
}
```

---

## 6. AWS LAMBDA FUNCTIONS

### 6.1 Lambda Architecture

#### Function 1: file-upload-handler
**Trigger**: API Gateway POST /upload  
**Runtime**: Python 3.11  
**Memory**: 512 MB  
**Timeout**: 30 seconds

**Responsibilities**:
1. Receive file upload request
2. Validate file format (must be .xlsx)
3. Generate unique S3 key with timestamp
4. Upload to S3 with metadata
5. Calculate SHA256 hash
6. Insert record into pay_files_metadata table
7. Return file_id and S3 details

**Environment Variables**:
- `S3_BUCKET_NAME`
- `DB_SECRET_ARN`
- `LOG_LEVEL=INFO`

#### Function 2: file-processor
**Trigger**: Step Functions (orchestrated)  
**Runtime**: Python 3.11  
**Memory**: 1024 MB  
**Timeout**: 5 minutes

**Responsibilities**:
1. Download file from S3
2. Parse Excel using openpyxl/pandas
3. Extract umbrella company and period from filename/content
4. Validate against pay_periods table
5. For each row:
   - Parse and clean data
   - Validate contractor name (fuzzy match)
   - Validate umbrella company
   - Validate rates
   - Validate VAT
   - Check for permanent staff
6. Store validation results
7. If valid, insert into pay_records
8. Update file_metadata status
9. Return processing summary

**Environment Variables**:
- `S3_BUCKET_NAME`
- `DB_SECRET_ARN`
- `NAME_MATCH_THRESHOLD=85`
- `LOG_LEVEL=DEBUG`

#### Function 3: validation-engine
**Trigger**: Step Functions (called by file-processor)  
**Runtime**: Python 3.11  
**Memory**: 512 MB  
**Timeout**: 2 minutes

**Responsibilities**:
1. Receive parsed records
2. Load golden reference data (contractors, umbrellas, params)
3. Apply validation rules
4. Return validation results with errors/warnings
5. Log all validation decisions

#### Function 4: report-generator
**Trigger**: API Gateway GET /reports/*  
**Runtime**: Python 3.11  
**Memory**: 512 MB  
**Timeout**: 30 seconds

**Responsibilities**:
1. Execute SQL queries for reports
2. Aggregate data
3. Format response as JSON
4. Cache results for performance

#### Function 5: cleanup-handler
**Trigger**: CloudWatch Events (daily)  
**Runtime**: Python 3.11  
**Memory**: 256 MB  
**Timeout**: 5 minutes

**Responsibilities**:
1. Archive old CloudWatch logs
2. Clean up superseded S3 files (move to glacier)
3. Vacuum database tables
4. Generate daily health report

### 6.2 Step Functions Workflow

**State Machine**: PayFileProcessingOrchestrator

```json
{
  "Comment": "Orchestrates pay file processing with validation",
  "StartAt": "ExtractMetadata",
  "States": {
    "ExtractMetadata": {
      "Type": "Task",
      "Resource": "arn:aws:lambda:...file-processor",
      "Parameters": {
        "file_id.$": "$.file_id",
        "action": "extract_metadata"
      },
      "Next": "MatchPeriod",
      "Catch": [{
        "ErrorEquals": ["States.ALL"],
        "Next": "ProcessingFailed"
      }]
    },
    "MatchPeriod": {
      "Type": "Task",
      "Resource": "arn:aws:lambda:...file-processor",
      "Parameters": {
        "file_id.$": "$.file_id",
        "metadata.$": "$.metadata",
        "action": "match_period"
      },
      "Next": "CheckDuplicates",
      "Catch": [{
        "ErrorEquals": ["States.ALL"],
        "Next": "ProcessingFailed"
      }]
    },
    "CheckDuplicates": {
      "Type": "Task",
      "Resource": "arn:aws:lambda:...file-processor",
      "Parameters": {
        "file_id.$": "$.file_id",
        "umbrella_id.$": "$.umbrella_id",
        "period_id.$": "$.period_id"
      },
      "Next": "DuplicateChoice",
      "Catch": [{
        "ErrorEquals": ["States.ALL"],
        "Next": "ProcessingFailed"
      }]
    },
    "DuplicateChoice": {
      "Type": "Choice",
      "Choices": [{
        "Variable": "$.duplicate_found",
        "BooleanEquals": true,
        "Next": "HandleDuplicate"
      }],
      "Default": "ParseRecords"
    },
    "HandleDuplicate": {
      "Type": "Task",
      "Resource": "arn:aws:lambda:...file-processor",
      "Parameters": {
        "file_id.$": "$.file_id",
        "existing_file_id.$": "$.existing_file_id",
        "action": "supersede_existing"
      },
      "Next": "ParseRecords"
    },
    "ParseRecords": {
      "Type": "Task",
      "Resource": "arn:aws:lambda:...file-processor",
      "Parameters": {
        "file_id.$": "$.file_id",
        "action": "parse_records"
      },
      "Next": "ValidateRecords",
      "Catch": [{
        "ErrorEquals": ["States.ALL"],
        "Next": "ProcessingFailed"
      }]
    },
    "ValidateRecords": {
      "Type": "Task",
      "Resource": "arn:aws:lambda:...validation-engine",
      "Parameters": {
        "file_id.$": "$.file_id",
        "records.$": "$.records"
      },
      "Next": "ValidationChoice",
      "Catch": [{
        "ErrorEquals": ["States.ALL"],
        "Next": "ProcessingFailed"
      }]
    },
    "ValidationChoice": {
      "Type": "Choice",
      "Choices": [{
        "Variable": "$.validation_result.has_critical_errors",
        "BooleanEquals": true,
        "Next": "ProcessingFailed"
      }],
      "Default": "ImportRecords"
    },
    "ImportRecords": {
      "Type": "Task",
      "Resource": "arn:aws:lambda:...file-processor",
      "Parameters": {
        "file_id.$": "$.file_id",
        "validated_records.$": "$.validation_result.valid_records",
        "action": "import_records"
      },
      "Next": "ProcessingComplete"
    },
    "ProcessingComplete": {
      "Type": "Task",
      "Resource": "arn:aws:lambda:...file-processor",
      "Parameters": {
        "file_id.$": "$.file_id",
        "action": "mark_complete"
      },
      "End": true
    },
    "ProcessingFailed": {
      "Type": "Task",
      "Resource": "arn:aws:lambda:...file-processor",
      "Parameters": {
        "file_id.$": "$.file_id",
        "error.$": "$.error",
        "action": "mark_failed"
      },
      "End": true
    }
  }
}
```

---

## 7. FLASK WEB UI

### 7.1 Application Structure

```
contractor-pay-tracker/
├── frontend/
│   ├── app.py                 # Flask application entry point
│   ├── config.py              # Configuration (dev vs prod)
│   ├── requirements.txt       # Python dependencies
│   ├── static/
│   │   ├── css/
│   │   │   └── styles.css
│   │   ├── js/
│   │   │   ├── upload.js      # File upload logic
│   │   │   ├── validation.js  # Validation results display
│   │   │   └── reports.js     # Charts and tables
│   │   └── img/
│   ├── templates/
│   │   ├── base.html          # Base template
│   │   ├── index.html         # Dashboard
│   │   ├── upload.html        # File upload page
│   │   ├── files.html         # File list view
│   │   ├── validation.html    # Validation results
│   │   ├── reports.html       # Reports dashboard
│   │   └── contractor.html    # Contractor detail view
│   └── utils/
│       ├── api_client.py      # API Gateway client
│       └── formatters.py      # Data formatting helpers
```

### 7.2 Key Pages

#### Dashboard (index.html)
- Summary statistics cards
- Recent uploads
- Pending validations
- Quick actions (Upload, View Reports)

#### Upload Page (upload.html)
- Drag-and-drop file upload zone
- Multiple file selection
- Progress bars per file
- Upload metadata form (uploaded_by, notes)

#### Files Page (files.html)
- Searchable/filterable table
- Columns: Filename, Umbrella, Period, Status, Uploaded, Actions
- Actions: View, Reprocess, Delete

#### Validation Page (validation.html)
- Display validation results by file
- Tabs: Errors, Warnings, Success
- Drill-down to specific row issues

#### Reports Page (reports.html)
- Period selector
- Summary cards (Total Spend, Contractors, Overtime)
- Charts: Spend by Umbrella (pie), Spend over Time (line)
- Top Contractors table
- Export to CSV/Excel

---

## 8. CI/CD PIPELINE

### 8.1 GitHub Repository Structure

```
contractor-pay-tracker/
├── .github/
│   └── workflows/
│       ├── deploy.yml          # Main deployment workflow
│       ├── test.yml            # Run tests on PR
│       └── seed-data.yml       # Deploy seed data
├── backend/
│   ├── template.yaml           # SAM template (IaC)
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
│   │   └── report_generator/
│   │       ├── app.py
│   │       ├── requirements.txt
│   │       └── tests/
│   ├── layers/
│   │   └── common/             # Shared libraries
│   │       ├── python/
│   │       │   └── common/
│   │       │       ├── db.py
│   │       │       ├── s3.py
│   │       │       └── logger.py
│   │       └── requirements.txt
│   └── seed-data/
│       ├── seed.sql            # Database seed data
│       └── seed.py             # Python seed script
├── frontend/
│   └── (Flask app as above)
├── docs/
│   ├── API.md
│   ├── DEPLOYMENT.md
│   └── USER_GUIDE.md
├── tests/
│   ├── integration/
│   └── e2e/
├── .gitignore
├── README.md
└── Makefile                    # Shortcuts for common commands
```

### 8.2 GitHub Actions Workflow

**File: .github/workflows/deploy.yml**

```yaml
name: Deploy Contractor Pay Tracker

on:
  push:
    branches:
      - main
  pull_request:
    branches:
      - main
  workflow_dispatch:

env:
  AWS_REGION: eu-west-2
  PYTHON_VERSION: '3.11'

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: ${{ env.PYTHON_VERSION }}
      
      - name: Install dependencies
        run: |
          pip install pytest pytest-cov ruff
          cd backend/functions/file_processor
          pip install -r requirements.txt
      
      - name: Lint with ruff
        run: |
          ruff check backend/
      
      - name: Run tests
        run: |
          pytest tests/ --cov=backend --cov-report=xml
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          files: ./coverage.xml

  build:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: ${{ env.PYTHON_VERSION }}
      
      - name: Set up AWS SAM
        uses: aws-actions/setup-sam@v2
      
      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v2
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: ${{ env.AWS_REGION }}
      
      - name: SAM build
        run: |
          cd backend
          sam build --use-container
      
      - name: SAM deploy
        run: |
          cd backend
          sam deploy \
            --stack-name contractor-pay-tracker-prod \
            --capabilities CAPABILITY_IAM \
            --no-fail-on-empty-changeset \
            --parameter-overrides \
              Environment=production \
              LogLevel=INFO
      
      - name: Get API Gateway URL
        run: |
          aws cloudformation describe-stacks \
            --stack-name contractor-pay-tracker-prod \
            --query "Stacks[0].Outputs[?OutputKey=='ApiUrl'].OutputValue" \
            --output text

  seed-database:
    needs: build
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
      - uses: actions/checkout@v3
      
      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v2
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: ${{ env.AWS_REGION }}
      
      - name: Run seed script
        run: |
          cd backend/seed-data
          pip install psycopg2-binary boto3
          python seed.py --stack-name contractor-pay-tracker-prod
```

---

## 9. LOGGING & MONITORING

### 9.1 Structured Logging Format

All Lambda functions use structured JSON logging:

```python
import json
import logging
from datetime import datetime

class StructuredLogger:
    def __init__(self, lambda_name, request_id):
        self.lambda_name = lambda_name
        self.request_id = request_id
        self.logger = logging.getLogger()
        self.logger.setLevel(logging.INFO)
    
    def log(self, level, message, **context):
        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": level,
            "lambda_name": self.lambda_name,
            "request_id": self.request_id,
            "message": message,
            "context": context
        }
        self.logger.log(
            getattr(logging, level),
            json.dumps(log_entry)
        )
    
    def info(self, message, **context):
        self.log("INFO", message, **context)
    
    def error(self, message, **context):
        self.log("ERROR", message, **context)
    
    def debug(self, message, **context):
        self.log("DEBUG", message, **context)

# Usage in Lambda
def lambda_handler(event, context):
    logger = StructuredLogger("file-processor", context.request_id)
    
    logger.info("Starting file processing", 
                file_id=event['file_id'],
                s3_key=event['s3_key'])
    
    try:
        # Process file
        result = process_file(event['file_id'])
        
        logger.info("File processed successfully",
                    file_id=event['file_id'],
                    records_imported=result['record_count'],
                    execution_time_ms=result['execution_time'])
        
        return result
    
    except Exception as e:
        logger.error("File processing failed",
                     file_id=event['file_id'],
                     error_type=type(e).__name__,
                     error_message=str(e),
                     traceback=traceback.format_exc())
        raise
```

### 9.2 CloudWatch Metrics

Custom metrics to track:

```python
import boto3

cloudwatch = boto3.client('cloudwatch')

def put_metric(metric_name, value, unit='Count', dimensions=None):
    cloudwatch.put_metric_data(
        Namespace='ContractorPayTracker',
        MetricData=[{
            'MetricName': metric_name,
            'Value': value,
            'Unit': unit,
            'Dimensions': dimensions or []
        }]
    )

# Examples:
put_metric('FilesProcessed', 1)
put_metric('ValidationErrors', error_count)
put_metric('ProcessingTimeMs', execution_time, unit='Milliseconds')
put_metric('RecordsImported', record_count, 
           dimensions=[{'Name': 'Umbrella', 'Value': umbrella_code}])
```

**Key Metrics**:
- FilesUploaded (Count)
- FilesProcessed (Count)
- ValidationErrors (Count)
- ValidationWarnings (Count)
- RecordsImported (Count)
- ProcessingTimeMs (Milliseconds)
- DatabaseConnections (Count)
- S3GetObject (Count)

### 9.3 CloudWatch Alarms

```yaml
# In SAM template.yaml
ProcessingErrorAlarm:
  Type: AWS::CloudWatch::Alarm
  Properties:
    AlarmName: contractor-pay-tracker-processing-errors
    AlarmDescription: Alert when file processing fails
    MetricName: Errors
    Namespace: AWS/Lambda
    Statistic: Sum
    Period: 300
    EvaluationPeriods: 1
    Threshold: 1
    ComparisonOperator: GreaterThanOrEqualToThreshold
    Dimensions:
      - Name: FunctionName
        Value: !Ref FileProcessorFunction
    AlarmActions:
      - !Ref AlertTopic

ValidationErrorAlarm:
  Type: AWS::CloudWatch::Alarm
  Properties:
    AlarmName: contractor-pay-tracker-validation-errors
    AlarmDescription: Alert when validation errors exceed threshold
    MetricName: ValidationErrors
    Namespace: ContractorPayTracker
    Statistic: Sum
    Period: 3600
    EvaluationPeriods: 1
    Threshold: 10
    ComparisonOperator: GreaterThanThreshold
    AlarmActions:
      - !Ref AlertTopic

DatabaseConnectionAlarm:
  Type: AWS::CloudWatch::Alarm
  Properties:
    AlarmName: contractor-pay-tracker-db-connections
    AlarmDescription: Alert when Aurora connections are high
    MetricName: DatabaseConnections
    Namespace: AWS/RDS
    Statistic: Average
    Period: 300
    EvaluationPeriods: 2
    Threshold: 80
    ComparisonOperator: GreaterThanThreshold
    Dimensions:
      - Name: DBClusterIdentifier
        Value: !Ref AuroraCluster
    AlarmActions:
      - !Ref AlertTopic
```

---

## 10. SECURITY & COMPLIANCE

### 10.1 Data Encryption

- **At Rest**:
  - S3: Server-side encryption (SSE-S3 or SSE-KMS)
  - RDS Aurora: Encryption enabled
  - Secrets Manager: Encrypted by default

- **In Transit**:
  - API Gateway: HTTPS only (TLS 1.2+)
  - Database: SSL/TLS connections enforced

### 10.2 IAM Roles & Policies

#### Lambda Execution Role
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:PutObject",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::contractor-pay-files/*",
        "arn:aws:s3:::contractor-pay-files"
      ]
    },
    {
      "Effect": "Allow",
      "Action": [
        "secretsmanager:GetSecretValue"
      ],
      "Resource": "arn:aws:secretsmanager:*:*:secret:contractor-pay-tracker/db-*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ],
      "Resource": "arn:aws:logs:*:*:*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "cloudwatch:PutMetricData"
      ],
      "Resource": "*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "states:StartExecution"
      ],
      "Resource": "arn:aws:states:*:*:stateMachine:PayFileProcessing*"
    }
  ]
}
```

### 10.3 Audit Compliance

All actions are logged for audit purposes:

1. **File Operations**: Every upload, process, delete logged in audit_log
2. **Data Changes**: All INSERT/UPDATE/DELETE captured via database triggers
3. **User Actions**: API calls include user_email in logs
4. **Validation Results**: Complete trail of validation decisions
5. **Rate Changes**: Automatic detection and flagging

**Retention Policy**:
- CloudWatch Logs: 90 days
- Database audit_log: 7 years (compliance requirement)
- S3 files: Move to Glacier after 2 years

---

## 11. DEPLOYMENT INSTRUCTIONS

### 11.1 Prerequisites

1. **AWS Account** with admin access
2. **AWS CLI** installed and configured
3. **SAM CLI** installed
4. **Python 3.11** installed
5. **Git** and **GitHub** account
6. **Docker** (for SAM local testing)

### 11.2 Initial Setup

```bash
# Clone repository
git clone https://github.com/colibri-digital/contractor-pay-tracker.git
cd contractor-pay-tracker

# Set up Python virtual environment (for local Flask dev)
cd frontend
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Configure AWS credentials
aws configure
# Enter: Access Key ID, Secret Access Key, Region (eu-west-2), Output format (json)

# Deploy infrastructure
cd ../backend
sam build
sam deploy --guided
# Follow prompts:
#   Stack Name: contractor-pay-tracker-prod
#   AWS Region: eu-west-2
#   Confirm changes: Y
#   Allow SAM CLI IAM role creation: Y
#   Save arguments to config: Y

# Deploy seed data
cd seed-data
pip install psycopg2-binary boto3
python seed.py --stack-name contractor-pay-tracker-prod

# Get API Gateway URL
aws cloudformation describe-stacks \
  --stack-name contractor-pay-tracker-prod \
  --query "Stacks[0].Outputs[?OutputKey=='ApiUrl'].OutputValue" \
  --output text
```

### 11.3 Local Development

```bash
# Start Flask UI
cd frontend
source venv/bin/activate
export API_GATEWAY_URL="https://xxxx.execute-api.eu-west-2.amazonaws.com/prod"
python app.py

# Access at http://localhost:5000

# Run tests
cd ../backend
pytest tests/ -v

# SAM local testing (requires Docker)
sam local start-api
sam local invoke FileProcessorFunction -e events/test-event.json
```

### 11.4 CI/CD Setup

1. **Create GitHub Repository**:
```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/colibri-digital/contractor-pay-tracker.git
git push -u origin main
```

2. **Add GitHub Secrets**:
   - Go to repo Settings → Secrets → Actions
   - Add secrets:
     - `AWS_ACCESS_KEY_ID`
     - `AWS_SECRET_ACCESS_KEY`

3. **Push to trigger deployment**:
```bash
git push origin main
# GitHub Actions will automatically deploy
```

---

## 12. TESTING STRATEGY

### 12.1 Unit Tests

Test individual functions in isolation.

**Example: Test fuzzy name matching**
```python
# tests/test_validator.py
import pytest
from backend.functions.validation_engine.rules import find_matching_contractor

def test_exact_name_match():
    result = find_matching_contractor("David", "Hunt", golden_data)
    assert result['match_type'] == 'EXACT'
    assert result['contractor_id'] is not None

def test_fuzzy_name_match():
    result = find_matching_contractor("Jon", "Mays", golden_data)
    assert result['match_type'] == 'FUZZY'
    assert result['confidence'] >= 85
    assert result['contractor']['first_name'] == 'Jonathan'

def test_unknown_contractor():
    result = find_matching_contractor("Unknown", "Person", golden_data)
    assert result['match_type'] == 'NOT_FOUND'
    assert result['contractor_id'] is None
```

### 12.2 Integration Tests

Test Lambda functions with real AWS services (dev environment).

```python
# tests/integration/test_file_processor.py
import boto3
import json

def test_file_processing_end_to_end():
    # Upload test file to S3
    s3 = boto3.client('s3')
    s3.upload_file(
        'tests/fixtures/NASA_test.xlsx',
        'contractor-pay-files-dev',
        'test/NASA_test.xlsx'
    )
    
    # Invoke Lambda
    lambda_client = boto3.client('lambda')
    response = lambda_client.invoke(
        FunctionName='contractor-pay-tracker-dev-file-processor',
        Payload=json.dumps({
            'file_id': 'test-file-id',
            's3_key': 'test/NASA_test.xlsx'
        })
    )
    
    result = json.loads(response['Payload'].read())
    
    assert result['status'] == 'success'
    assert result['records_imported'] > 0
```

### 12.3 Test Data

**Sample Test Files**:
- `tests/fixtures/NASA_valid.xlsx` - Clean file, no errors
- `tests/fixtures/NASA_with_errors.xlsx` - Contains validation errors
- `tests/fixtures/NASA_duplicate_period.xlsx` - Tests duplicate detection
- `tests/fixtures/PAYSTREAM_valid.xlsx` - Different umbrella

---

## 13. COST OPTIMIZATION

### 13.1 Aurora Serverless Scaling

```yaml
# In SAM template
AuroraCluster:
  Type: AWS::RDS::DBCluster
  Properties:
    Engine: aurora-postgresql
    EngineMode: provisioned
    EngineVersion: '15.4'
    ServerlessV2ScalingConfiguration:
      MinCapacity: 0.5  # Scale down to 0.5 ACU when idle
      MaxCapacity: 2    # Max 2 ACU (rarely needed)
```

**Cost**: ~£0.12/hour × 10 hours/month = £1.20/month

### 13.2 S3 Lifecycle Policy

```json
{
  "Rules": [{
    "Id": "ArchiveOldFiles",
    "Status": "Enabled",
    "Transitions": [{
      "Days": 730,
      "StorageClass": "GLACIER"
    }],
    "NoncurrentVersionTransitions": [{
      "NoncurrentDays": 90,
      "StorageClass": "GLACIER"
    }]
  }]
}
```

### 13.3 Lambda Optimization

- Use ARM64 architecture (20% cheaper)
- Right-size memory (512MB-1024MB based on profiling)
- Enable Lambda SnapStart for faster cold starts

---

## 14. FUTURE ENHANCEMENTS

### Phase 2 (Month 3-6)
- Multi-user support with Cognito authentication
- Email notifications for validation errors
- Scheduled reports sent to stakeholders
- Rate approval workflow
- Mobile-responsive UI

### Phase 3 (Month 6-12)
- Machine learning for anomaly detection
- Predictive analytics (forecast contractor costs)
- Integration with accounting system (Xero/QuickBooks)
- Contractor onboarding/offboarding workflow
- Time tracking integration

---

## 15. SUPPORT & MAINTENANCE

### 15.1 Troubleshooting

**Common Issues**:

1. **File upload fails**:
   - Check S3 bucket permissions
   - Verify API Gateway URL is correct
   - Check CloudWatch logs for Lambda errors

2. **Validation errors**:
   - Review validation_errors table
   - Check golden reference data is seeded
   - Verify contractor names match exactly

3. **Database connection issues**:
   - Check Aurora cluster is running
   - Verify security group allows Lambda access
   - Check Secrets Manager has correct credentials

### 15.2 Monitoring Dashboard

Create CloudWatch Dashboard with:
- Lambda invocation count and duration
- API Gateway request count and latency
- Aurora CPU/memory utilization
- S3 bucket size
- Validation error rate

---

## 16. SUCCESS METRICS

Track these KPIs to measure system effectiveness:

1. **Operational Efficiency**:
   - Time to process pay period: Target <5 minutes
   - Manual intervention rate: Target <5%
   - File resubmission rate: Target <10%

2. **Data Quality**:
   - Validation error rate: Target <2%
   - Duplicate detection accuracy: Target 100%
   - Name matching accuracy: Target >95%

3. **Compliance**:
   - Audit trail completeness: 100%
   - Rate validation coverage: 100%
   - Data retention compliance: 100%

4. **Cost**:
   - Monthly AWS spend: Target <£5
   - Cost per pay period processed: Target <£0.50

---

## 17. GLOSSARY

- **Umbrella Company**: Third-party payroll provider that handles contractor payments
- **Pay Period**: 4-week cycle for contractor payments
- **Employee ID**: Umbrella company's unique identifier for a contractor
- **Day Rate**: Contractor's daily charge rate (excluding VAT)
- **Overtime**: Work beyond standard hours, typically paid at 1.5x normal rate
- **Golden Reference Data**: Authoritative source of contractor-umbrella associations
- **Superseded File**: Previous version of pay file replaced by newer upload
- **Validation Engine**: Component that checks pay records against business rules

---

**END OF DESIGN DOCUMENT**

**Document Version**: 1.0  
**Last Updated**: 2025-11-07  
**Author**: Claude (Anthropic)  
**For**: Gianluca Formica, Colibri Digital
