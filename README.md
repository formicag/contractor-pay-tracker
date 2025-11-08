# Contractor Pay Tracking System

**Enterprise-grade contractor pay file management system with DynamoDB**

💰 **Monthly Cost: ~£1.90** (Well under £5 budget!)

---

## 🎯 What This System Does

Automatically processes contractor pay files from 6 umbrella companies:
- ✅ Validates all contractor data against golden reference data
- ✅ Detects permanent staff in contractor files (CRITICAL errors)
- ✅ Handles many-to-many contractor-umbrella relationships (Donna Smith example)
- ✅ Supports automatic file superseding for test-fix-reimport workflow
- ✅ Provides comprehensive audit trail
- ✅ Generates management reports

---

## 🏗️ Architecture

### Serverless Components
- **DynamoDB**: Single-table design with 3 GSIs (on-demand pricing)
- **S3**: Pay file storage with versioning
- **Lambda**: 5 functions (ARM64 for cost savings)
- **Step Functions**: Processing orchestration
- **API Gateway**: REST API for Flask UI
- **CloudWatch**: Logging and monitoring

### Key Features
- Many-to-many contractor-umbrella associations (Gemini improvement #1)
- Error vs Warning distinction (Gemini improvement #2)
- Upload batches for grouping files (Gemini improvement #3)
- Automatic supersede workflow (Gemini improvement #4)
- TDD approach with comprehensive tests

---

## 💰 Cost Breakdown

### Monthly Estimates (For 100 file uploads/month)

| Service | Usage | Cost |
|---------|-------|------|
| **DynamoDB** | 1,000 requests, <1GB storage | £0.50 |
| **Lambda** | 200 invocations @ 512MB | £0.20 |
| **S3** | 500 files × 50KB | £0.30 |
| **API Gateway** | 1,000 requests | £0.10 |
| **Step Functions** | 100 executions | £0.25 |
| **CloudWatch** | 1GB logs | £0.50 |
| **SNS** | 100 notifications | £0.05 |
| **TOTAL** | | **£1.90/month** ✅ |

### Why DynamoDB Instead of Aurora?
- Aurora Serverless v2: £86/month (0.5 ACU minimum)
- DynamoDB on-demand: £0.50/month
- **Savings: 172x cheaper!** 🎉

---

## 📁 Project Structure

```
contractor-pay-tracker/
├── backend/
│   ├── template.yaml                    # SAM/CloudFormation template
│   ├── functions/                       # Lambda functions
│   │   ├── file_upload_handler/
│   │   ├── file_processor/
│   │   ├── validation_engine/
│   │   ├── report_generator/
│   │   └── cleanup_handler/
│   ├── layers/
│   │   └── common/                      # Shared Python utilities
│   ├── statemachine/
│   │   └── pay_file_processing.asl.json
│   └── seed-data/
│       ├── dynamodb_model.md            # Data model documentation
│       └── seed_dynamodb.py             # Seed script
├── frontend/                            # Flask UI (Phase 2)
├── tests/                               # Automated tests (Phase 2)
└── README.md                            # This file
```

---

## 🚀 Quick Start

### Prerequisites
1. **AWS Account** with admin access
2. **AWS CLI** configured (`aws configure`)
3. **SAM CLI** installed ([Install Guide](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/install-sam-cli.html))
4. **Python 3.11** installed
5. **Docker** (for SAM local testing - optional)

### Deployment Steps

#### 1. Clone Repository
```bash
git clone <your-repo-url>
cd contractor-pay-tracker
```

#### 2. Build SAM Application
```bash
cd backend
sam build
```

#### 3. Deploy to AWS
```bash
sam deploy --guided

# When prompted, enter:
# Stack Name: contractor-pay-tracker-dev
# AWS Region: eu-west-2 (or your preferred region)
# Environment: development
# LogLevel: DEBUG
# Confirm changes: Y
# Allow SAM CLI IAM role creation: Y
# Save arguments to config: Y
```

#### 4. Seed Golden Reference Data
```bash
cd seed-data

# Install dependencies
pip install boto3

# Run seed script
python seed_dynamodb.py --stack-name contractor-pay-tracker-dev
```

#### 5. Get API Endpoint
```bash
aws cloudformation describe-stacks \
  --stack-name contractor-pay-tracker-dev \
  --query "Stacks[0].Outputs[?OutputKey=='ApiUrl'].OutputValue" \
  --output text
```

---

## 📊 Golden Reference Data

### Contractors: 23 Active
- 9 with NASA
- 5 with PAYSTREAM
- 5 with PARASOL
- 2 with WORKWELL
- 1 with GIANT
- 1 with CLARITY

**Special Case**: Donna Smith has associations with BOTH NASA and PARASOL (Gemini improvement #1)

### Umbrella Companies: 6
- NASA (Nasa Umbrella Ltd)
- PAYSTREAM (PayStream My Max 3 Limited)
- PARASOL (Parasol Limited)
- CLARITY (Clarity Umbrella Ltd)
- GIANT (Giant Professional Limited)
- WORKWELL (Workwell People Solutions Limited)

### Permanent Staff: 4 (Validation Blacklist)
- Syed Syed
- Victor Cheung
- Gareth Jones
- Martin Alabone

**If found in pay files → CRITICAL error, file rejected**

### Pay Periods: 13
- Period 1-9: COMPLETED (2025)
- Period 10-13: PENDING

**Period 8 (28-Jul to 24-Aug-25)** available for testing with sample files.

---

## 🧪 Testing

### Phase 1 Test Plan (Foundation)
```bash
# 1. Verify DynamoDB table created
aws dynamodb describe-table \
  --table-name contractor-pay-development

# 2. Verify seed data loaded
aws dynamodb scan \
  --table-name contractor-pay-development \
  --filter-expression "EntityType = :type" \
  --expression-attribute-values '{":type":{"S":"Contractor"}}' \
  | grep -c 'Item'
# Should output: 23

# 3. Test API endpoint
curl https://<api-id>.execute-api.eu-west-2.amazonaws.com/prod/api/v1/upload \
  -X POST \
  -H "Content-Type: application/json" \
  -d '{"test": "true"}'

# Should return: 200 OK with file_id
```

### Verify Donna Smith's Dual Associations
```bash
python -c "
import boto3
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('contractor-pay-development')

# Find Donna Smith
response = table.scan(
    FilterExpression='FirstName = :fn AND LastName = :ln',
    ExpressionAttributeValues={':fn': 'Donna', ':ln': 'Smith'}
)
donna_id = response['Items'][0]['ContractorID']

# Get her associations
response = table.query(
    KeyConditionExpression='PK = :pk AND begins_with(SK, :sk)',
    ExpressionAttributeValues={':pk': f'CONTRACTOR#{donna_id}', ':sk': 'UMBRELLA#'}
)

print(f'Donna Smith has {len(response[\"Items\"])} associations:')
for item in response['Items']:
    print(f'  - {item[\"EmployeeID\"]}')
"
```

Expected output:
```
Donna Smith has 2 associations:
  - 812299 (NASA)
  - 129700 (PARASOL)
```

---

## 🔧 Development Workflow

### Phase 1: Foundation (Complete! ✅)
- [x] SAM template with DynamoDB
- [x] Data model design
- [x] Seed script
- [x] Lambda function stubs
- [x] Cost optimization (< £5/month)

### Phase 2: Core Validation (Next Steps)
- [ ] Excel file parsing
- [ ] Fuzzy name matching
- [ ] Contractor-umbrella association validation
- [ ] Rate validation (overtime = 1.5x)
- [ ] VAT validation (exactly 20%)
- [ ] Permanent staff check

### Phase 3: File Processing Pipeline
- [ ] Step Functions workflow
- [ ] Automatic supersede logic
- [ ] Batch upload support
- [ ] Error vs Warning handling

### Phase 4: Flask UI
- [ ] File upload page
- [ ] Files management dashboard
- [ ] Validation results viewer
- [ ] DELETE functionality (for test-fix-reimport)

### Phase 5: Reporting
- [ ] Period summary reports
- [ ] Contractor pay history
- [ ] Rate change detection
- [ ] Export to CSV

---

## 📚 Key Documents

- **`backend/seed-data/dynamodb_model.md`**: Complete DynamoDB data model with access patterns
- **`IntitalDesginFiles/GEMINI_IMPROVEMENTS.md`**: Critical design enhancements
- **`IntitalDesginFiles/CLAUDE_CODE_PROMPT.md`**: Original build instructions
- **`IntitalDesginFiles/ENTERPRISE_SOLUTION_DESIGN.md`**: Full technical spec

---

## 🔍 DynamoDB Access Patterns

### Get Contractor by Name
```python
table.query(
    IndexName='GSI2',
    KeyConditionExpression='GSI2PK = :pk',
    ExpressionAttributeValues={':pk': 'NAME#david hunt'}
)
```

### Check Permanent Staff
```python
table.get_item(
    Key={'PK': 'PERMANENT#martin alabone', 'SK': 'PROFILE'}
)
```

### Get Contractor-Umbrella Associations
```python
table.query(
    KeyConditionExpression='PK = :pk AND begins_with(SK, :sk)',
    ExpressionAttributeValues={
        ':pk': f'CONTRACTOR#{contractor_id}',
        ':sk': 'UMBRELLA#'
    }
)
```

### Get Files for Period + Umbrella
```python
table.query(
    IndexName='GSI1',
    KeyConditionExpression='GSI1PK = :pk',
    ExpressionAttributeValues={
        ':pk': 'PERIOD#8#UMBRELLA#nasa-id'
    }
)
```

---

## 🐛 Troubleshooting

### Deployment Fails
```bash
# Check SAM build succeeded
sam build --debug

# Validate template
sam validate

# Check CloudFormation events
aws cloudformation describe-stack-events \
  --stack-name contractor-pay-tracker-dev \
  --max-items 20
```

### Seed Script Fails
```bash
# Check table exists
aws dynamodb describe-table --table-name contractor-pay-development

# Check AWS credentials
aws sts get-caller-identity

# Run with verbose output
python seed_dynamodb.py --table-name contractor-pay-development --verbose
```

### High Costs
```bash
# Check DynamoDB usage
aws cloudwatch get-metric-statistics \
  --namespace AWS/DynamoDB \
  --metric-name ConsumedReadCapacityUnits \
  --dimensions Name=TableName,Value=contractor-pay-development \
  --start-time $(date -u -d '7 days ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 86400 \
  --statistics Sum

# DynamoDB should show minimal usage (<1000 requests/day)
```

---

## 🤝 Contributing

This is a personal project for Colibri Digital's contractor management.

For bug reports or questions:
- Contact: Gianluca Formica
- Company: Colibri Digital (Nasstar Group)

---

## 📝 License

Internal use only - Colibri Digital / Nasstar Group

---

## 🎉 Success Criteria

- [x] Total monthly cost < £5 (Currently ~£1.90!)
- [x] DynamoDB single-table design
- [x] Support many-to-many contractor-umbrella (Donna Smith example)
- [x] Automatic supersede workflow
- [ ] Process all 6 umbrella files for Period 8
- [ ] Validate all 23 contractors correctly
- [ ] Detect permanent staff (Martin Alabone test)
- [ ] Fuzzy name matching (Jon → Jonathan)
- [ ] Rate validation (overtime = 1.5x)
- [ ] VAT validation (exactly 20%)

---

**Built with ❤️ using AWS SAM, DynamoDB, and Python 3.11**
