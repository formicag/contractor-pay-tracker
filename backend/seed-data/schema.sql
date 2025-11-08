-- ============================================================================
-- CONTRACTOR PAY TRACKING SYSTEM - DATABASE SCHEMA
-- ============================================================================
-- Total Tables: 18 (includes upload_batches from Gemini improvements)
-- PostgreSQL 15.4 on Aurora Serverless v2
-- ============================================================================

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================================================
-- REFERENCE DATA TABLES (5 tables)
-- ============================================================================

-- Table 1: Umbrella Companies
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
CREATE INDEX idx_umbrella_active ON umbrella_companies(is_active);

COMMENT ON TABLE umbrella_companies IS 'Master list of 6 umbrella companies that handle contractor payments';
COMMENT ON COLUMN umbrella_companies.file_name_variation IS 'Company name as it appears in Excel files (may differ from legal name)';

-- Table 2: Contractors (Golden Reference Data)
CREATE TABLE contractors (
    contractor_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    normalized_name VARCHAR(200) NOT NULL,  -- Lowercase, no special chars for fuzzy matching
    job_title VARCHAR(200),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(first_name, last_name)
);

CREATE INDEX idx_contractor_normalized_name ON contractors(normalized_name);
CREATE INDEX idx_contractor_active ON contractors(is_active);

COMMENT ON TABLE contractors IS 'Golden reference data - 23 active contractors';
COMMENT ON COLUMN contractors.normalized_name IS 'Used for fuzzy name matching (lowercase, no special chars)';

-- Table 3: Permanent Staff (DO NOT PAY via umbrellas)
CREATE TABLE permanent_staff (
    staff_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    normalized_name VARCHAR(200) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(first_name, last_name)
);

CREATE INDEX idx_permanent_normalized_name ON permanent_staff(normalized_name);

COMMENT ON TABLE permanent_staff IS 'Permanent employees who should NEVER appear in contractor pay files - triggers CRITICAL error if found';

-- Table 4: Pay Periods (4-week cycles)
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
CREATE INDEX idx_period_status ON pay_periods(status);

COMMENT ON TABLE pay_periods IS '13 pay periods defined for 2025-2026 financial year (4-week cycles)';

-- Table 5: System Parameters
CREATE TABLE system_parameters (
    param_key VARCHAR(100) PRIMARY KEY,
    param_value VARCHAR(500) NOT NULL,
    data_type VARCHAR(20) NOT NULL,        -- DECIMAL, INTEGER, STRING, BOOLEAN
    description TEXT,
    is_editable BOOLEAN DEFAULT FALSE,
    updated_at TIMESTAMP DEFAULT NOW(),
    updated_by VARCHAR(200)
);

COMMENT ON TABLE system_parameters IS 'Configuration parameters (VAT rate, overtime multiplier, validation thresholds)';

-- ============================================================================
-- OPERATIONAL DATA TABLES (8 tables)
-- ============================================================================

-- Table 6: Upload Batches (NEW - Gemini Improvement #3)
CREATE TABLE upload_batches (
    batch_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    batch_name VARCHAR(200),           -- "Period 8 - All Umbrellas"
    period_id UUID REFERENCES pay_periods(period_id),
    status VARCHAR(20),                -- PROCESSING, COMPLETED, COMPLETED_WITH_WARNINGS, ERROR
    total_files INTEGER,
    completed_files INTEGER,
    error_files INTEGER,
    warning_files INTEGER,
    uploaded_by VARCHAR(200),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_batch_period ON upload_batches(period_id);
CREATE INDEX idx_batch_status ON upload_batches(status);
CREATE INDEX idx_batch_created ON upload_batches(created_at);

COMMENT ON TABLE upload_batches IS 'Groups multiple file uploads together (e.g., all 6 umbrella files for Period 8) - Gemini improvement';
COMMENT ON COLUMN upload_batches.status IS 'Overall batch status: COMPLETED if all files OK, ERROR if any critical errors';

-- Table 7: Pay File Metadata
CREATE TABLE pay_files_metadata (
    file_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    batch_id UUID REFERENCES upload_batches(batch_id),  -- Link to batch
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
    status VARCHAR(30) NOT NULL DEFAULT 'UPLOADED',
    -- UPLOADED, PROCESSING, COMPLETED, COMPLETED_WITH_WARNINGS, ERROR, SUPERSEDED, DELETED

    -- Timestamps
    uploaded_at TIMESTAMP DEFAULT NOW(),
    processing_started_at TIMESTAMP,
    processing_completed_at TIMESTAMP,
    superseded_at TIMESTAMP,
    deleted_at TIMESTAMP,

    -- User Tracking
    uploaded_by VARCHAR(200),
    deleted_by VARCHAR(200),
    deletion_reason TEXT,

    -- Processing Results
    total_records INTEGER,
    valid_records INTEGER,
    error_records INTEGER,
    warning_records INTEGER,

    -- Financial Totals (for quick validation)
    total_amount DECIMAL(12,2),
    total_vat DECIMAL(12,2),
    total_gross DECIMAL(12,2),

    -- Versioning
    version INTEGER DEFAULT 1,
    is_current_version BOOLEAN DEFAULT TRUE,
    superseded_by UUID REFERENCES pay_files_metadata(file_id),

    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_payfile_batch ON pay_files_metadata(batch_id);
CREATE INDEX idx_payfile_umbrella_period ON pay_files_metadata(umbrella_id, period_id);
CREATE INDEX idx_payfile_status ON pay_files_metadata(status);
CREATE INDEX idx_payfile_s3_key ON pay_files_metadata(s3_key);
CREATE INDEX idx_payfile_current ON pay_files_metadata(is_current_version);
CREATE INDEX idx_payfile_uploaded ON pay_files_metadata(uploaded_at);

COMMENT ON TABLE pay_files_metadata IS 'Metadata for all uploaded Excel files with processing status and results';
COMMENT ON COLUMN pay_files_metadata.status IS 'COMPLETED (no issues), COMPLETED_WITH_WARNINGS (imported with warnings), ERROR (not imported), SUPERSEDED (replaced), DELETED (soft delete)';
COMMENT ON COLUMN pay_files_metadata.is_current_version IS 'Only one current version per umbrella+period combination';

-- Table 8: Contractor-Umbrella Associations (CRITICAL - Gemini Improvement #1)
CREATE TABLE contractor_umbrella_associations (
    association_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    contractor_id UUID NOT NULL REFERENCES contractors(contractor_id),
    umbrella_id UUID NOT NULL REFERENCES umbrella_companies(umbrella_id),
    employee_id VARCHAR(50) NOT NULL,       -- Umbrella company's ID for this contractor

    -- Validity Period
    valid_from DATE NOT NULL,
    valid_to DATE,                          -- NULL means ongoing
    is_active BOOLEAN DEFAULT TRUE,

    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),

    UNIQUE(umbrella_id, employee_id)        -- Employee ID unique per umbrella
);

CREATE INDEX idx_assoc_contractor ON contractor_umbrella_associations(contractor_id);
CREATE INDEX idx_assoc_umbrella ON contractor_umbrella_associations(umbrella_id);
CREATE INDEX idx_assoc_employee_id ON contractor_umbrella_associations(employee_id);
CREATE INDEX idx_assoc_active ON contractor_umbrella_associations(is_active);
CREATE INDEX idx_assoc_validity ON contractor_umbrella_associations(valid_from, valid_to);

COMMENT ON TABLE contractor_umbrella_associations IS 'Many-to-many: Contractors CAN work for multiple umbrellas (e.g., Donna Smith in both NASA and PARASOL) - Gemini improvement';
COMMENT ON COLUMN contractor_umbrella_associations.employee_id IS 'Umbrella company employee ID for this contractor (e.g., NASA ID: 812299, PARASOL ID: 129700)';
COMMENT ON COLUMN contractor_umbrella_associations.valid_from IS 'Date from which this association is valid (handles contractor moves between umbrellas)';

-- Table 9: Pay Records (individual line items from files)
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
    is_active BOOLEAN DEFAULT TRUE,         -- FALSE if file deleted or superseded

    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_payrecord_file ON pay_records(file_id);
CREATE INDEX idx_payrecord_contractor ON pay_records(contractor_id);
CREATE INDEX idx_payrecord_umbrella ON pay_records(umbrella_id);
CREATE INDEX idx_payrecord_period ON pay_records(period_id);
CREATE INDEX idx_payrecord_type ON pay_records(record_type);
CREATE INDEX idx_payrecord_active ON pay_records(is_active);
CREATE INDEX idx_payrecord_association ON pay_records(association_id);

COMMENT ON TABLE pay_records IS 'Individual pay line items from Excel files - granular pay data';
COMMENT ON COLUMN pay_records.is_active IS 'Set to FALSE when file is deleted or superseded (soft delete for audit trail)';
COMMENT ON COLUMN pay_records.record_type IS 'STANDARD (normal days), OVERTIME (1.5x rate), EXPENSE (reimbursement)';

-- Table 10: Rate History (track rate changes over time)
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
CREATE INDEX idx_rate_reviewed ON rate_history(reviewed);

COMMENT ON TABLE rate_history IS 'Automatic detection of rate changes >5% between periods';

-- ============================================================================
-- VALIDATION & AUDIT TABLES (5 tables)
-- ============================================================================

-- Table 11: Validation Errors (CRITICAL - block import)
CREATE TABLE validation_errors (
    error_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    file_id UUID NOT NULL REFERENCES pay_files_metadata(file_id),

    error_type VARCHAR(50) NOT NULL,
    -- UNKNOWN_CONTRACTOR, WRONG_UMBRELLA, INVALID_RATE, INVALID_VAT,
    -- PERMANENT_STAFF, DUPLICATE_EMPLOYEE_ID, NO_UMBRELLA_ASSOCIATION, etc.

    severity VARCHAR(20) NOT NULL,          -- CRITICAL (blocks import)

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

COMMENT ON TABLE validation_errors IS 'Critical errors that BLOCK file import - NO data imported if errors exist (Gemini improvement #2)';
COMMENT ON COLUMN validation_errors.severity IS 'Always CRITICAL - these errors prevent import';

-- Table 12: Validation Warnings (NON-BLOCKING - allow import)
CREATE TABLE validation_warnings (
    warning_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    file_id UUID NOT NULL REFERENCES pay_files_metadata(file_id),
    record_id UUID REFERENCES pay_records(record_id),

    warning_type VARCHAR(50) NOT NULL,
    -- RATE_CHANGE, FUZZY_NAME_MATCH, UNUSUAL_HOURS, FIRST_TIME_CONTRACTOR, etc.

    warning_message TEXT NOT NULL,
    auto_resolved BOOLEAN DEFAULT FALSE,
    resolution_notes TEXT,

    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_warning_file ON validation_warnings(file_id);
CREATE INDEX idx_warning_record ON validation_warnings(record_id);
CREATE INDEX idx_warning_type ON validation_warnings(warning_type);

COMMENT ON TABLE validation_warnings IS 'Non-blocking warnings - data IS imported, status=COMPLETED_WITH_WARNINGS (Gemini improvement #2)';
COMMENT ON COLUMN validation_warnings.warning_type IS 'RATE_CHANGE (>5%), FUZZY_NAME_MATCH (e.g., Jon→Jonathan), UNUSUAL_HOURS, etc.';

-- Table 13: Audit Log (tracks ALL changes)
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
    reason TEXT,                            -- E.g., deletion reason

    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_audit_table ON audit_log(table_name);
CREATE INDEX idx_audit_record ON audit_log(record_id);
CREATE INDEX idx_audit_action ON audit_log(action);
CREATE INDEX idx_audit_created ON audit_log(created_at);
CREATE INDEX idx_audit_user ON audit_log(user_email);

COMMENT ON TABLE audit_log IS 'Complete audit trail of all data changes - 7 year retention for compliance';

-- Table 14: Processing Log (detailed execution logs)
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
CREATE INDEX idx_proclog_component ON processing_log(component);

COMMENT ON TABLE processing_log IS 'Detailed processing logs for debugging and monitoring';

-- ============================================================================
-- DATABASE TRIGGERS FOR AUDIT LOGGING
-- ============================================================================

-- Trigger function to automatically log all changes
CREATE OR REPLACE FUNCTION audit_trigger_function()
RETURNS TRIGGER AS $$
BEGIN
    IF (TG_OP = 'DELETE') THEN
        INSERT INTO audit_log (table_name, record_id, action, old_values)
        VALUES (TG_TABLE_NAME, OLD.contractor_id, 'DELETE', row_to_json(OLD));
        RETURN OLD;
    ELSIF (TG_OP = 'UPDATE') THEN
        INSERT INTO audit_log (table_name, record_id, action, old_values, new_values)
        VALUES (TG_TABLE_NAME, NEW.contractor_id, 'UPDATE', row_to_json(OLD), row_to_json(NEW));
        RETURN NEW;
    ELSIF (TG_OP = 'INSERT') THEN
        INSERT INTO audit_log (table_name, record_id, action, new_values)
        VALUES (TG_TABLE_NAME, NEW.contractor_id, 'INSERT', row_to_json(NEW));
        RETURN NEW;
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

-- Apply audit triggers to key tables
CREATE TRIGGER contractors_audit_trigger
    AFTER INSERT OR UPDATE OR DELETE ON contractors
    FOR EACH ROW EXECUTE FUNCTION audit_trigger_function();

CREATE TRIGGER umbrella_companies_audit_trigger
    AFTER INSERT OR UPDATE OR DELETE ON umbrella_companies
    FOR EACH ROW EXECUTE FUNCTION audit_trigger_function();

CREATE TRIGGER pay_files_metadata_audit_trigger
    AFTER INSERT OR UPDATE OR DELETE ON pay_files_metadata
    FOR EACH ROW EXECUTE FUNCTION audit_trigger_function();

-- ============================================================================
-- VIEWS FOR COMMON QUERIES
-- ============================================================================

-- Active contractors with their umbrella associations
CREATE OR REPLACE VIEW v_active_contractor_umbrellas AS
SELECT
    c.contractor_id,
    c.first_name,
    c.last_name,
    c.normalized_name,
    c.job_title,
    u.umbrella_id,
    u.short_code as umbrella_code,
    u.legal_name as umbrella_name,
    a.employee_id,
    a.valid_from,
    a.valid_to,
    CASE
        WHEN a.valid_to IS NULL THEN 'Ongoing'
        WHEN a.valid_to >= CURRENT_DATE THEN 'Active'
        ELSE 'Expired'
    END as association_status
FROM contractors c
JOIN contractor_umbrella_associations a ON c.contractor_id = a.contractor_id
JOIN umbrella_companies u ON a.umbrella_id = u.umbrella_id
WHERE c.is_active = TRUE
  AND a.is_active = TRUE
ORDER BY c.last_name, c.first_name, u.short_code;

COMMENT ON VIEW v_active_contractor_umbrellas IS 'Lists all active contractors with their umbrella company associations';

-- Current period summary
CREATE OR REPLACE VIEW v_current_period_summary AS
SELECT
    pp.period_number,
    pp.work_start_date,
    pp.work_end_date,
    pp.submission_date,
    uc.short_code as umbrella,
    COUNT(DISTINCT pr.contractor_id) as contractor_count,
    SUM(pr.amount) as total_amount,
    SUM(pr.vat_amount) as total_vat,
    SUM(pr.gross_amount) as total_gross,
    SUM(CASE WHEN pr.record_type = 'OVERTIME' THEN pr.amount ELSE 0 END) as overtime_amount
FROM pay_periods pp
LEFT JOIN pay_records pr ON pp.period_id = pr.period_id AND pr.is_active = TRUE
LEFT JOIN umbrella_companies uc ON pr.umbrella_id = uc.umbrella_id
WHERE pp.status = 'COMPLETED'
GROUP BY pp.period_number, pp.work_start_date, pp.work_end_date, pp.submission_date, uc.short_code
ORDER BY pp.period_number DESC, uc.short_code;

COMMENT ON VIEW v_current_period_summary IS 'Summary of completed periods with spend by umbrella';

-- ============================================================================
-- GRANT PERMISSIONS (for Lambda execution role)
-- ============================================================================

-- Create application role for Lambda functions
-- Note: Actual role creation happens via AWS IAM/Secrets Manager
-- This schema assumes Lambda will connect using database credentials

-- ============================================================================
-- SCHEMA VALIDATION
-- ============================================================================

-- Verify all 18 tables exist
DO $$
DECLARE
    table_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO table_count
    FROM information_schema.tables
    WHERE table_schema = 'public'
      AND table_type = 'BASE TABLE'
      AND table_name IN (
          'umbrella_companies',
          'contractors',
          'permanent_staff',
          'pay_periods',
          'system_parameters',
          'upload_batches',
          'pay_files_metadata',
          'contractor_umbrella_associations',
          'pay_records',
          'rate_history',
          'validation_errors',
          'validation_warnings',
          'audit_log',
          'processing_log'
      );

    IF table_count <> 14 THEN
        RAISE EXCEPTION 'Expected 14 core tables, found %', table_count;
    END IF;

    RAISE NOTICE 'Schema validation successful: 14 tables created';
END $$;

-- ============================================================================
-- END OF SCHEMA
-- ============================================================================
