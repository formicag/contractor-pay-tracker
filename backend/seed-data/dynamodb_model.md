# DynamoDB Single-Table Design

## Cost Estimate: ~£0.50/month ✅

With **on-demand pricing**:
- First 2.5M reads FREE, then £1.25 per million
- First 1M writes FREE, then £1.56 per million
- Storage: £0.25/GB (you'll use < 100MB)
- **Your usage**: ~1000 operations/month = **£0.002** 😄

## Table Structure

**Table Name**: `contractor-pay-{environment}`

### Primary Keys
- **PK** (Partition Key): Entity type + ID
- **SK** (Sort Key): Related entity or timestamp

### Global Secondary Indexes
- **GSI1**: Reverse lookups (umbrella→contractors, period+umbrella→files)
- **GSI2**: Name-based lookups (fuzzy matching)
- **GSI3**: Time-based queries (recent uploads, date ranges)

---

## Entity Patterns

### 1. Contractors
```json
{
  "PK": "CONTRACTOR#550e8400-e29b-41d4-a716-446655440000",
  "SK": "PROFILE",
  "EntityType": "Contractor",
  "ContractorID": "550e8400-e29b-41d4-a716-446655440000",
  "FirstName": "David",
  "LastName": "Hunt",
  "NormalizedName": "david hunt",
  "JobTitle": "Solution Designer",
  "IsActive": true,
  "CreatedAt": "2025-01-01T00:00:00Z",

  "GSI2PK": "NAME#david hunt",
  "GSI2SK": "CONTRACTOR#550e8400-e29b-41d4-a716-446655440000"
}
```

**Access Patterns**:
- Get contractor by ID: `Query PK=CONTRACTOR#{id} AND SK=PROFILE`
- Find contractor by name: `Query GSI2 WHERE GSI2PK=NAME#{normalized_name}`

---

### 2. Contractor-Umbrella Associations (MANY-TO-MANY)
```json
{
  "PK": "CONTRACTOR#550e8400...",
  "SK": "UMBRELLA#660f9511-f30c-52e5-b827-557766551111",
  "EntityType": "Association",
  "ContractorID": "550e8400...",
  "UmbrellaID": "660f9511...",
  "EmployeeID": "801234",
  "ValidFrom": "2025-01-01",
  "ValidTo": null,
  "IsActive": true,

  "GSI1PK": "UMBRELLA#660f9511...",
  "GSI1SK": "CONTRACTOR#550e8400..."
}
```

**CRITICAL** - Donna Smith example:
```json
// Association 1: NASA
{
  "PK": "CONTRACTOR#donna-smith-id",
  "SK": "UMBRELLA#nasa-id",
  "EmployeeID": "812299",
  "ValidFrom": "2025-01-01"
}

// Association 2: PARASOL
{
  "PK": "CONTRACTOR#donna-smith-id",
  "SK": "UMBRELLA#parasol-id",
  "EmployeeID": "129700",
  "ValidFrom": "2025-01-01"
}
```

**Access Patterns**:
- Get all umbrellas for contractor: `Query PK=CONTRACTOR#{id} AND SK BEGINS_WITH "UMBRELLA#"`
- Get all contractors for umbrella: `Query GSI1 WHERE GSI1PK=UMBRELLA#{id} AND GSI1SK BEGINS_WITH "CONTRACTOR#"`
- Validate contractor-umbrella for period: Check if association exists and `ValidFrom <= period_start` and (`ValidTo IS NULL` or `ValidTo >= period_end`)

---

### 3. Umbrella Companies
```json
{
  "PK": "UMBRELLA#660f9511-f30c-52e5-b827-557766551111",
  "SK": "PROFILE",
  "EntityType": "Umbrella",
  "UmbrellaID": "660f9511...",
  "ShortCode": "NASA",
  "LegalName": "Nasa Umbrella Ltd",
  "FileNameVariation": "NASA GROUP",
  "IsActive": true,

  "GSI2PK": "UMBRELLA_CODE#NASA",
  "GSI2SK": "PROFILE"
}
```

**Access Patterns**:
- Get umbrella by ID: `Query PK=UMBRELLA#{id} AND SK=PROFILE`
- Find umbrella by code: `Query GSI2 WHERE GSI2PK=UMBRELLA_CODE#{code}`

---

### 4. Pay Periods
```json
{
  "PK": "PERIOD#8",
  "SK": "PROFILE",
  "EntityType": "Period",
  "PeriodNumber": 8,
  "PeriodYear": 2025,
  "WorkStartDate": "2025-07-28",
  "WorkEndDate": "2025-08-24",
  "SubmissionDate": "2025-09-01",
  "PaymentDate": "2025-09-05",
  "Status": "COMPLETED"
}
```

**Access Patterns**:
- Get period by number: `Query PK=PERIOD#{number} AND SK=PROFILE`
- Get all periods: `Scan` (only 13 items, very cheap)

---

### 5. Permanent Staff (Validation Blacklist)
```json
{
  "PK": "PERMANENT#martin alabone",
  "SK": "PROFILE",
  "EntityType": "PermanentStaff",
  "FirstName": "Martin",
  "LastName": "Alabone",
  "NormalizedName": "martin alabone",

  "GSI2PK": "PERMANENT_CHECK",
  "GSI2SK": "NAME#martin alabone"
}
```

**Access Patterns**:
- Check if permanent staff: `GetItem PK=PERMANENT#{normalized_name} AND SK=PROFILE`
- Get all permanent staff: `Query GSI2 WHERE GSI2PK=PERMANENT_CHECK`

---

### 6. System Parameters
```json
{
  "PK": "PARAM#VAT_RATE",
  "SK": "VALUE",
  "EntityType": "Parameter",
  "ParamKey": "VAT_RATE",
  "ParamValue": "0.20",
  "DataType": "DECIMAL",
  "Description": "UK VAT rate (20%)",
  "IsEditable": false,
  "UpdatedAt": "2025-01-01T00:00:00Z"
}
```

**Access Patterns**:
- Get parameter: `GetItem PK=PARAM#{key} AND SK=VALUE`
- Get all parameters: `Query PK BEGINS_WITH "PARAM#"`

---

### 7. Upload Batches (Gemini Improvement #3)
```json
{
  "PK": "BATCH#770g0622-g41d-63f6-c938-668877662222",
  "SK": "METADATA",
  "EntityType": "Batch",
  "BatchID": "770g0622...",
  "BatchName": "Period 8 - All Umbrellas",
  "PeriodID": "8",
  "Status": "COMPLETED",
  "TotalFiles": 6,
  "CompletedFiles": 5,
  "ErrorFiles": 1,
  "WarningFiles": 2,
  "UploadedBy": "gianluca.formica@colibridigital.co.uk",
  "CreatedAt": "2025-09-01T14:00:00Z",

  "GSI3PK": "BATCHES",
  "GSI3SK": "2025-09-01T14:00:00Z"
}
```

**Access Patterns**:
- Get batch by ID: `Query PK=BATCH#{id} AND SK=METADATA`
- Get recent batches: `Query GSI3 WHERE GSI3PK=BATCHES ORDER BY GSI3SK DESC`

---

### 8. Pay File Metadata
```json
{
  "PK": "FILE#550e8400-e29b-41d4-a716-446655440000",
  "SK": "METADATA",
  "EntityType": "File",
  "FileID": "550e8400...",
  "BatchID": "770g0622...",
  "UmbrellaID": "nasa-id",
  "PeriodID": "8",
  "OriginalFilename": "NASA_GCI_Nasstar_Contractor_Pay_Figures_01092025.xlsx",
  "S3Bucket": "contractor-pay-files-prod-123456789",
  "S3Key": "uploads/2025/09/nasa_abc123.xlsx",
  "S3VersionID": "v1234",
  "FileSizeBytes": 57344,
  "FileHashSHA256": "abc123...",
  "Status": "COMPLETED",
  "UploadedAt": "2025-09-01T15:23:12Z",
  "ProcessingStartedAt": "2025-09-01T15:23:15Z",
  "ProcessingCompletedAt": "2025-09-01T15:23:45Z",
  "UploadedBy": "gianluca.formica@colibridigital.co.uk",
  "TotalRecords": 14,
  "ValidRecords": 14,
  "ErrorRecords": 0,
  "WarningRecords": 1,
  "TotalAmount": 127456.50,
  "TotalVAT": 25491.30,
  "TotalGross": 152947.80,
  "IsCurrentVersion": true,
  "Version": 1,

  "GSI1PK": "PERIOD#8#UMBRELLA#nasa-id",
  "GSI1SK": "FILE#550e8400...",
  "GSI3PK": "FILES",
  "GSI3SK": "2025-09-01T15:23:12Z"
}
```

**Access Patterns**:
- Get file by ID: `Query PK=FILE#{id} AND SK=METADATA`
- Get files for period+umbrella: `Query GSI1 WHERE GSI1PK=PERIOD#{period}#UMBRELLA#{umbrella}`
- Get recent files: `Query GSI3 WHERE GSI3PK=FILES ORDER BY GSI3SK DESC`
- Check duplicate: Query GSI1 for existing file with same period+umbrella where `IsCurrentVersion=true`

---

### 9. Pay Records
```json
{
  "PK": "FILE#550e8400...",
  "SK": "RECORD#001",
  "EntityType": "PayRecord",
  "RecordID": "880h1733-h52e-74g7-d049-779988773333",
  "FileID": "550e8400...",
  "ContractorID": "david-hunt-id",
  "UmbrellaID": "nasa-id",
  "PeriodID": "8",
  "AssociationID": "assoc-id",
  "EmployeeID": "801234",
  "UnitDays": 20.00,
  "DayRate": 472.03,
  "Amount": 9440.60,
  "VATAmount": 1888.12,
  "GrossAmount": 11328.72,
  "TotalHours": 150.0,
  "RecordType": "STANDARD",
  "Notes": "",
  "IsActive": true,
  "CreatedAt": "2025-09-01T15:23:45Z",

  "GSI1PK": "CONTRACTOR#david-hunt-id",
  "GSI1SK": "RECORD#2025-09-01T15:23:45Z",
  "GSI2PK": "PERIOD#8",
  "GSI2SK": "CONTRACTOR#david-hunt-id"
}
```

**Access Patterns**:
- Get all records for file: `Query PK=FILE#{id} AND SK BEGINS_WITH "RECORD#"`
- Get pay history for contractor: `Query GSI1 WHERE GSI1PK=CONTRACTOR#{id} AND GSI1SK BEGINS_WITH "RECORD#"`
- Get all contractors paid in period: `Query GSI2 WHERE GSI2PK=PERIOD#{number}`

---

### 10. Validation Errors (CRITICAL - block import)
```json
{
  "PK": "FILE#550e8400...",
  "SK": "ERROR#001",
  "EntityType": "ValidationError",
  "ErrorID": "990i2844-i63f-85h8-e150-880099884444",
  "FileID": "550e8400...",
  "ErrorType": "PERMANENT_STAFF",
  "Severity": "CRITICAL",
  "RowNumber": 5,
  "EmployeeID": "999999",
  "ContractorName": "Martin Alabone",
  "ErrorMessage": "CRITICAL: Martin Alabone is permanent staff and should not be in contractor pay file",
  "SuggestedFix": "Remove Martin Alabone from file",
  "CreatedAt": "2025-09-01T15:23:25Z",

  "GSI1PK": "ERRORS",
  "GSI1SK": "2025-09-01T15:23:25Z"
}
```

**Access Patterns**:
- Get errors for file: `Query PK=FILE#{id} AND SK BEGINS_WITH "ERROR#"`
- Get recent errors: `Query GSI1 WHERE GSI1PK=ERRORS ORDER BY GSI1SK DESC`

---

### 11. Validation Warnings (NON-BLOCKING)
```json
{
  "PK": "FILE#550e8400...",
  "SK": "WARNING#001",
  "EntityType": "ValidationWarning",
  "WarningID": "aa0j3955-j74g-96i9-f261-991100995555",
  "FileID": "550e8400...",
  "RecordID": "880h1733...",
  "WarningType": "RATE_CHANGE",
  "WarningMessage": "David Hunt rate changed from £472.00 to £472.03 (0.06%)",
  "AutoResolved": false,
  "ResolutionNotes": null,
  "CreatedAt": "2025-09-01T15:23:30Z",

  "GSI1PK": "WARNINGS",
  "GSI1SK": "2025-09-01T15:23:30Z"
}
```

**Access Patterns**:
- Get warnings for file: `Query PK=FILE#{id} AND SK BEGINS_WITH "WARNING#"`
- Get recent warnings: `Query GSI1 WHERE GSI1PK=WARNINGS ORDER BY GSI1SK DESC`

---

### 12. Audit Log
```json
{
  "PK": "AUDIT#2025-09-01",
  "SK": "2025-09-01T15:23:45.123Z#FILE#550e8400...",
  "EntityType": "AuditLog",
  "AuditID": "bb0k4066-k85h-07j0-g372-002211006666",
  "TableName": "PayFileMetadata",
  "RecordID": "550e8400...",
  "Action": "DELETE",
  "OldValues": {...},
  "NewValues": null,
  "ChangedFields": ["Status", "IsActive", "DeletedAt"],
  "UserEmail": "gianluca.formica@colibridigital.co.uk",
  "Reason": "Testing - re-importing with validation fixes",
  "IPAddress": "203.0.113.0",
  "CreatedAt": "2025-09-01T15:23:45Z"
}
```

**Access Patterns**:
- Get audit trail for date: `Query PK=AUDIT#{date} ORDER BY SK`
- Get audit for specific record: `Query` then filter by RecordID (or use GSI)

---

## Query Examples

### Validation: Check if contractor can be paid by umbrella
```python
# Step 1: Get contractor-umbrella associations
response = table.query(
    KeyConditionExpression='PK = :pk AND begins_with(SK, :sk)',
    ExpressionAttributeValues={
        ':pk': f'CONTRACTOR#{contractor_id}',
        ':sk': 'UMBRELLA#'
    }
)

# Step 2: Check if umbrella_id is in results and dates are valid
for item in response['Items']:
    if item['UmbrellaID'] == umbrella_id:
        valid_from = item['ValidFrom']
        valid_to = item.get('ValidTo')

        if valid_from <= period_start and (valid_to is None or valid_to >= period_end):
            return True  # Valid!

return False  # CRITICAL ERROR: No association found
```

### Find files that need processing
```python
response = table.query(
    IndexName='GSI3',
    KeyConditionExpression='GSI3PK = :pk',
    FilterExpression='#status = :status',
    ExpressionAttributeNames={'#status': 'Status'},
    ExpressionAttributeValues={
        ':pk': 'FILES',
        ':status': 'UPLOADED'
    }
)
```

### Get Period 8 summary (all contractors, all umbrellas)
```python
response = table.query(
    IndexName='GSI2',
    KeyConditionExpression='GSI2PK = :pk',
    ExpressionAttributeValues={
        ':pk': 'PERIOD#8'
    }
)

# Aggregate in application code
total_amount = sum(item['Amount'] for item in response['Items'])
contractor_count = len(set(item['ContractorID'] for item in response['Items']))
```

---

## Cost Analysis

### Monthly Estimates (Low Volume)

**Writes** (seeding + 100 file uploads):
- Seed data: 50 writes (one-time)
- Per file upload: 20 writes (metadata, records, batch)
- 100 files × 20 = 2,000 writes/month
- Cost: **FREE** (under 1M free tier)

**Reads** (validation + reporting):
- Per file validation: 50 reads (check contractors, umbrellas, associations)
- 100 files × 50 = 5,000 reads/month
- Reports/dashboards: 500 reads/month
- Total: 5,500 reads/month
- Cost: **FREE** (under 2.5M free tier)

**Storage**:
- ~100KB per file × 1000 files = 100MB
- Cost: £0.025/month

**Total DynamoDB cost: £0.03/month** 🎉

---

## Benefits Over Aurora

1. **Cost**: £0.03/month vs £86/month (2,867x cheaper!)
2. **Serverless**: True pay-per-request, scales to zero
3. **Performance**: Single-digit millisecond latency
4. **Backups**: Point-in-time recovery included
5. **Streams**: Built-in audit trail via DynamoDB Streams
6. **No VPC**: Simpler architecture, no NAT Gateway needed

---

## Trade-offs

1. **No SQL**: Must design access patterns upfront
2. **No Joins**: Denormalize data or query multiple times
3. **Limited Transactions**: BatchWriteItem for related writes
4. **Learning Curve**: Single-table design requires planning

**Verdict**: For your use case (23 contractors, low volume), DynamoDB is perfect! ✅
