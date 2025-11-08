# Test Suite

Comprehensive test suite for the Contractor Pay Tracker system.

## Test Structure

```
tests/
├── conftest.py                       # Shared pytest fixtures
├── pytest.ini                        # Pytest configuration (in project root)
├── requirements.txt                  # Test dependencies
├── unit/                            # Unit tests
│   ├── test_fuzzy_matcher.py        # Fuzzy name matching tests
│   ├── test_validators.py           # Business rule validation tests
│   └── test_excel_parser.py         # Excel parsing tests
├── integration/                     # Integration tests
│   └── test_file_processing.py      # End-to-end workflow tests
└── fixtures/                        # Test data files
    └── (Excel test files)
```

## Setup

### Install Dependencies

```bash
# Install test dependencies
pip install -r tests/requirements.txt

# Or install with backend dependencies
pip install -r backend/layers/common/requirements.txt
pip install -r tests/requirements.txt
```

### Required Packages

- `pytest` - Test framework
- `pytest-cov` - Coverage reporting
- `pytest-mock` - Mocking support
- `moto` - AWS service mocking
- `boto3` - AWS SDK
- `openpyxl` - Excel file handling
- `fuzzywuzzy` - Fuzzy string matching
- `python-Levenshtein` - Fast string comparison

## Running Tests

### Run All Tests

```bash
# From project root
pytest

# With coverage
pytest --cov=backend/layers/common/python/common --cov-report=term-missing

# With HTML coverage report
pytest --cov=backend/layers/common/python/common --cov-report=html
```

### Run Specific Test Categories

```bash
# Unit tests only
pytest tests/unit/

# Integration tests only
pytest tests/integration/

# Specific test file
pytest tests/unit/test_fuzzy_matcher.py

# Specific test class
pytest tests/unit/test_validators.py::TestValidationEngine

# Specific test function
pytest tests/unit/test_fuzzy_matcher.py::TestFuzzyMatcher::test_exact_match
```

### Run Tests by Marker

```bash
# Run only unit tests (if marked)
pytest -m unit

# Run only integration tests (if marked)
pytest -m integration

# Skip slow tests
pytest -m "not slow"
```

## Test Coverage

### Unit Tests Coverage

**Fuzzy Matcher (`test_fuzzy_matcher.py`)** - 15 tests
- ✅ Exact name matching (100% confidence)
- ✅ Fuzzy matching (Jon → Jonathan, ~87% confidence)
- ✅ Threshold enforcement (85% default)
- ✅ Case insensitive matching
- ✅ Whitespace normalization
- ✅ Special character handling
- ✅ Multiple similar names
- ✅ Large dataset performance
- ✅ Empty name handling

**Validators (`test_validators.py`)** - 24 tests

**Rule 1: Permanent Staff Detection**
- ✅ Detects all 4 permanent staff (Syed Syed, Victor Cheung, Gareth Jones, Martin Alabone)
- ✅ CRITICAL error blocks import
- ✅ Valid contractors pass

**Rule 2: Contractor Name Matching**
- ✅ Exact match (100% confidence)
- ✅ Fuzzy match returns WARNING (not CRITICAL)
- ✅ Unknown contractor returns CRITICAL error

**Rule 3: Contractor-Umbrella Association**
- ✅ Valid association passes
- ✅ Many-to-many support (Donna Smith in both NASA and PARASOL)
- ✅ No association returns CRITICAL error
- ✅ Expired association fails
- ✅ Date range validation (ValidFrom/ValidTo)

**Rule 4: VAT Validation**
- ✅ Exactly 20% passes
- ✅ Incorrect VAT returns CRITICAL error
- ✅ 1p tolerance for rounding
- ✅ Beyond tolerance fails

**Rule 5: Overtime Rate Validation**
- ✅ Valid overtime rate (1.5x)
- ✅ Suspiciously low rate fails

**Rule 7: Hours Validation**
- ✅ Normal hours pass
- ✅ Excessive hours (>25 days) returns WARNING
- ✅ Negative hours returns WARNING

**Complete Record Validation**
- ✅ All rules pass
- ✅ Permanent staff blocks all validation
- ✅ Multiple CRITICAL errors collected
- ✅ WARNINGS don't block import
- ✅ System parameters loading

**Excel Parser (`test_excel_parser.py`)** - 20 tests
- ✅ Metadata extraction (umbrella code, submission date)
- ✅ Automatic header row detection
- ✅ Empty row handling
- ✅ Duplicate header skipping
- ✅ Overtime detection from notes
- ✅ Gross amount calculation
- ✅ Row number tracking
- ✅ Umbrella code extraction (6 companies)
- ✅ Submission date extraction
- ✅ Total hours calculation
- ✅ Numeric/string field conversion
- ✅ Parser cleanup
- ✅ Context manager support
- ✅ Missing columns handling
- ✅ Unicode character support

### Integration Tests

**File Processing Workflow (`test_file_processing.py`)**
- 🚧 Extract metadata
- 🚧 Match period
- 🚧 Check duplicates
- 🚧 Automatic supersede
- 🚧 Validation workflows
- 🚧 Import records
- 🚧 Status marking

**End-to-End Scenarios**
- 🚧 Clean NASA file (14 contractors)
- 🚧 PARASOL with Donna Smith
- 🚧 File with permanent staff
- 🚧 Duplicate file supersede
- 🚧 Fuzzy match warnings

Legend: ✅ Implemented | 🚧 Placeholder

## Test Data

### Fixtures

Test fixtures are provided in `conftest.py`:

- `mock_dynamodb_client` - Mock DynamoDB client
- `sample_contractors` - 4 test contractors
- `sample_pay_record` - Valid pay record
- `sample_period_data` - Period 8 data
- `sample_umbrella_associations` - Including Donna Smith's dual associations

### Integration Test Data

Integration tests use `moto` to mock AWS services:
- DynamoDB table with test data
- S3 bucket for file storage
- Pre-seeded golden reference data

## Writing New Tests

### Unit Test Template

```python
import pytest
from common.your_module import YourClass

class TestYourClass:
    """Test your functionality"""

    def test_basic_case(self):
        """Test basic functionality"""
        obj = YourClass()
        result = obj.method()
        assert result == expected_value

    def test_edge_case(self):
        """Test edge case"""
        # Test implementation
        pass
```

### Integration Test Template

```python
import pytest

@pytest.mark.integration
class TestYourIntegration:
    """Test integration scenario"""

    def test_scenario(self, dynamodb_table, s3_bucket, seed_test_data):
        """Test complete workflow"""
        # Setup
        # Execute
        # Assert
        pass
```

## Continuous Integration

### GitHub Actions (Future)

```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          pip install -r tests/requirements.txt
      - name: Run tests
        run: pytest --cov --cov-report=xml
      - name: Upload coverage
        uses: codecov/codecov-action@v2
```

## Troubleshooting

### Import Errors

If you see import errors, ensure the backend path is in PYTHONPATH:

```bash
export PYTHONPATH="${PYTHONPATH}:$(pwd)/backend/layers/common/python"
pytest
```

### AWS Mock Errors

If moto tests fail, ensure AWS credentials are set (even fake ones):

```bash
export AWS_ACCESS_KEY_ID=testing
export AWS_SECRET_ACCESS_KEY=testing
export AWS_DEFAULT_REGION=eu-west-2
pytest tests/integration/
```

### Excel File Errors

Ensure openpyxl is installed:

```bash
pip install openpyxl
```

## Coverage Goals

- **Unit Tests**: 80%+ coverage of common layer
- **Integration Tests**: All critical workflows covered
- **End-to-End**: All Phase 2 scenarios tested

## Next Steps

1. ✅ Complete unit tests for all common layer modules
2. 🚧 Implement integration test scenarios
3. 🚧 Add test fixtures from real Period 8 files
4. 🚧 Set up CI/CD pipeline
5. 🚧 Add performance benchmarks
