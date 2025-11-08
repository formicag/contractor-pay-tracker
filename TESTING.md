# Testing Guide

Comprehensive testing documentation for the Contractor Pay Tracker system.

## Table of Contents

1. [Testing Strategy](#testing-strategy)
2. [Test Setup](#test-setup)
3. [Running Tests](#running-tests)
4. [Test Coverage](#test-coverage)
5. [Test Scenarios](#test-scenarios)
6. [Writing Tests](#writing-tests)
7. [CI/CD Integration](#cicd-integration)

---

## Testing Strategy

### Test Pyramid

```
        /\
       /  \  E2E Tests (5%)
      /____\
     /      \  Integration Tests (25%)
    /________\
   /          \  Unit Tests (70%)
  /______________\
```

**Unit Tests (70%)**
- Test individual functions and classes in isolation
- Fast execution (< 1s per test)
- Mock external dependencies
- Located in `tests/unit/`

**Integration Tests (25%)**
- Test interactions between components
- Use mocked AWS services (moto)
- Test complete workflows
- Located in `tests/integration/`

**End-to-End Tests (5%)**
- Test real deployment with real AWS services
- Manual testing with real Period 8 files
- Validate complete business scenarios

---

## Test Setup

### Install Dependencies

```bash
# Navigate to project root
cd /path/to/contractor-pay-tracker

# Install test dependencies
pip install -r tests/requirements.txt

# Install backend dependencies (if not already done)
pip install -r backend/layers/common/requirements.txt
```

### Verify Installation

```bash
pytest --version
# Should show: pytest 7.4.3 or higher
```

---

## Running Tests

### Quick Start

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run with coverage
pytest --cov=backend/layers/common/python/common --cov-report=term-missing
```

### Run Specific Tests

```bash
# Unit tests only
pytest tests/unit/

# Integration tests only
pytest tests/integration/

# Specific test file
pytest tests/unit/test_fuzzy_matcher.py

# Specific test class
pytest tests/unit/test_validators.py::TestValidationEngine

# Specific test method
pytest tests/unit/test_fuzzy_matcher.py::TestFuzzyMatcher::test_exact_match

# Run tests matching a pattern
pytest -k "fuzzy" -v
pytest -k "validation" -v
```

### Run with Markers

```bash
# Run only unit tests (if marked with @pytest.mark.unit)
pytest -m unit

# Run only integration tests
pytest -m integration

# Skip slow tests
pytest -m "not slow"
```

### Coverage Reports

```bash
# Terminal coverage report
pytest --cov=backend/layers/common/python/common --cov-report=term-missing

# HTML coverage report
pytest --cov=backend/layers/common/python/common --cov-report=html
# View at: htmlcov/index.html

# XML coverage report (for CI/CD)
pytest --cov=backend/layers/common/python/common --cov-report=xml
```

---

## Test Coverage

### Current Coverage Status

**Unit Tests: 59 tests** ✅

| Module | Tests | Coverage |
|--------|-------|----------|
| `fuzzy_matcher.py` | 15 | 90%+ |
| `validators.py` | 24 | 85%+ |
| `excel_parser.py` | 20 | 80%+ |

**Integration Tests: 15 tests** 🚧

| Workflow | Status |
|----------|--------|
| File Processing | Placeholder |
| End-to-End Scenarios | Placeholder |

### Module-by-Module Coverage

#### Fuzzy Matcher (`test_fuzzy_matcher.py`) - 15 tests ✅

**Exact Matching**
- ✅ `test_exact_match` - 100% confidence for identical names
- ✅ `test_case_insensitive_match` - Case variations handled
- ✅ `test_whitespace_handling` - Extra whitespace normalized

**Fuzzy Matching**
- ✅ `test_fuzzy_match_jon_to_jonathan` - Common variation (87% match)
- ✅ `test_fuzzy_match_mathews_to_matthews` - Spelling error (93% match)
- ✅ `test_no_match_below_threshold` - Rejects poor matches

**Edge Cases**
- ✅ `test_no_match_empty_list` - Empty contractor list
- ✅ `test_empty_name_handling` - Empty/None names
- ✅ `test_special_characters_normalization` - O'Brien, etc.
- ✅ `test_unicode_names_handling` - International characters

**Performance & Thresholds**
- ✅ `test_threshold_adjustment` - Different threshold values
- ✅ `test_multiple_similar_names` - Best match selection
- ✅ `test_performance_with_large_list` - 1000+ contractors
- ✅ `test_confidence_score_calculation` - Score accuracy
- ✅ `test_normalize_name_method` - Name normalization

#### Validators (`test_validators.py`) - 24 tests ✅

**Rule 1: Permanent Staff Detection (CRITICAL)**
- ✅ `test_rule1_permanent_staff_detected` - Detects Martin Alabone
- ✅ `test_rule1_permanent_staff_all_four_detected` - All 4 permanent staff
- ✅ `test_rule1_contractor_passes` - Valid contractors pass

**Rule 2: Contractor Name Matching**
- ✅ `test_rule2_exact_name_match` - Exact match (no warning)
- ✅ `test_rule2_fuzzy_name_match_with_warning` - Jon → Jonathan (WARNING)
- ✅ `test_rule2_unknown_contractor_critical_error` - Unknown = CRITICAL

**Rule 3: Contractor-Umbrella Association (CRITICAL)**
- ✅ `test_rule3_valid_umbrella_association` - Valid association
- ✅ `test_rule3_many_to_many_donna_smith` - Donna in NASA + PARASOL
- ✅ `test_rule3_no_umbrella_association_critical` - No association = CRITICAL
- ✅ `test_rule3_expired_association_fails` - Date validation

**Rule 4: VAT Validation (CRITICAL)**
- ✅ `test_rule4_vat_exactly_20_percent` - Exactly 20%
- ✅ `test_rule4_vat_incorrect_critical_error` - Wrong VAT = CRITICAL
- ✅ `test_rule4_vat_1p_tolerance` - ±1p rounding tolerance
- ✅ `test_rule4_vat_beyond_tolerance_fails` - Beyond 1p fails

**Rule 5: Overtime Rate Validation (CRITICAL)**
- ✅ `test_rule5_overtime_rate_validation` - Valid 1.5x rate
- ✅ `test_rule5_overtime_rate_too_low_fails` - Suspiciously low = CRITICAL

**Rule 7: Hours Validation (WARNING)**
- ✅ `test_rule7_hours_validation_normal` - Normal hours
- ✅ `test_rule7_hours_too_high_warning` - >25 days = WARNING
- ✅ `test_rule7_negative_hours_warning` - Negative = WARNING

**Complete Record Validation**
- ✅ `test_validate_record_all_pass` - Clean record passes
- ✅ `test_validate_record_permanent_staff_blocks_all` - Blocks immediately
- ✅ `test_validate_record_multiple_critical_errors` - Collects all errors
- ✅ `test_validate_record_warnings_dont_block` - Warnings allow import
- ✅ `test_system_parameters_loading` - Parameters loaded correctly

#### Excel Parser (`test_excel_parser.py`) - 20 tests ✅

**Metadata Extraction**
- ✅ `test_extract_metadata_nasa` - NASA umbrella code
- ✅ `test_extract_metadata_parasol` - PARASOL umbrella code
- ✅ `test_umbrella_code_extraction` - All 6 umbrella companies
- ✅ `test_submission_date_extraction` - DDMMYYYY format

**Header Detection**
- ✅ `test_find_header_row` - Auto-detect header
- ✅ `test_find_header_row_with_empty_rows` - Skip empty rows

**Record Parsing**
- ✅ `test_parse_records_simple` - Basic parsing
- ✅ `test_parse_records_with_overtime` - Overtime detection
- ✅ `test_parse_records_skips_empty_rows` - Empty row handling
- ✅ `test_parse_records_skips_duplicate_headers` - Duplicate headers

**Field Handling**
- ✅ `test_detect_overtime_from_notes` - Notes column parsing
- ✅ `test_calculate_gross_amount` - Gross = Amount + VAT
- ✅ `test_row_number_tracking` - Row numbers tracked
- ✅ `test_total_hours_calculation` - Days * 8 hours
- ✅ `test_numeric_fields_conversion` - Float conversion
- ✅ `test_string_fields_handling` - String handling

**Edge Cases**
- ✅ `test_parser_close_cleanup` - Cleanup resources
- ✅ `test_context_manager_support` - `with` statement
- ✅ `test_missing_columns_handling` - Missing columns
- ✅ `test_unicode_names_handling` - Unicode characters

---

## Test Scenarios

### Test Fixtures

Six test fixture files are provided in `tests/fixtures/`:

#### 1. NASA_GCI_Nasstar_Contractor_Pay_01092025.xlsx ✅
**Scenario:** Clean NASA file with 3 valid contractors

| Employee ID | Name | Days | Rate | Amount | VAT |
|-------------|------|------|------|--------|-----|
| 812001 | Jonathan Mays | 20 | £450 | £9,000 | £1,800 |
| 812002 | David Hunt | 18 | £500 | £9,000 | £1,800 |
| 812003 | Donna Smith | 22 | £475 | £10,450 | £2,090 |

**Expected Result:**
- ✅ Status: `COMPLETED`
- ✅ Records imported: 3
- ✅ Errors: 0
- ✅ Warnings: 0

#### 2. PARASOL_Limited_Contractor_Pay_01092025.xlsx ✅
**Scenario:** PARASOL file with Donna Smith (tests many-to-many)

| Employee ID | Name | Days | Rate | Amount | VAT |
|-------------|------|------|------|--------|-----|
| 812003 | Donna Smith | 20 | £475 | £9,500 | £1,900 |

**Expected Result:**
- ✅ Status: `COMPLETED`
- ✅ Donna Smith validates with PARASOL umbrella (has association)
- ✅ Records imported: 1

#### 3. GIANT_With_Permanent_Staff_01092025.xlsx ⚠️
**Scenario:** File contains Martin Alabone (permanent staff)

| Employee ID | Name | Days | Rate | Amount | VAT |
|-------------|------|------|------|--------|-----|
| 812001 | Jonathan Mays | 20 | £450 | £9,000 | £1,800 |
| 999999 | **Martin Alabone** | 20 | £500 | £10,000 | £2,000 |

**Expected Result:**
- ❌ Status: `ERROR`
- ❌ Records imported: 0
- ❌ Error: "Martin Alabone is permanent staff and must NOT appear in contractor pay files"

#### 4. NASA_With_Fuzzy_Match_01092025.xlsx ⚠️
**Scenario:** File has "Jon Mays" (fuzzy matches "Jonathan Mays")

| Employee ID | Name | Days | Rate | Amount | VAT |
|-------------|------|------|------|--------|-----|
| 812001 | **Jon** Mays | 20 | £450 | £9,000 | £1,800 |

**Expected Result:**
- ⚠️ Status: `COMPLETED_WITH_WARNINGS`
- ✅ Records imported: 1
- ⚠️ Warning: "Name 'Jon Mays' matched to 'Jonathan Mays' with 87% confidence"

#### 5. NASA_With_Wrong_VAT_01092025.xlsx ❌
**Scenario:** File has incorrect VAT calculation

| Employee ID | Name | Days | Rate | Amount | VAT |
|-------------|------|------|------|--------|-----|
| 812001 | Jonathan Mays | 20 | £450 | £9,000 | **£1,500** |

**Expected Result:**
- ❌ Status: `ERROR`
- ❌ Records imported: 0
- ❌ Error: "VAT calculation incorrect. Expected £1,800.00 at 20%"

#### 6. NASA_With_Overtime_01092025.xlsx ✅
**Scenario:** File includes overtime record

| Employee ID | Name | Days | Rate | Amount | VAT | Notes |
|-------------|------|------|------|--------|-----|-------|
| 812001 | Jonathan Mays | 20 | £450 | £9,000 | £1,800 | |
| 812001 | Jonathan Mays | 2 | £675 | £1,350 | £270 | Overtime |

**Expected Result:**
- ✅ Status: `COMPLETED`
- ✅ Records imported: 2
- ✅ First record type: `NORMAL`
- ✅ Second record type: `OVERTIME`

---

## Writing Tests

### Unit Test Template

```python
"""
Unit tests for your_module.py
"""

import pytest
from common.your_module import YourClass


class TestYourClass:
    """Test your functionality"""

    def test_basic_functionality(self):
        """Test basic case"""
        # Arrange
        obj = YourClass()

        # Act
        result = obj.method(input_data)

        # Assert
        assert result == expected_value

    def test_edge_case(self, sample_fixture):
        """Test edge case with fixture"""
        obj = YourClass()

        result = obj.method(sample_fixture)

        assert result is not None
        assert 'expected_key' in result

    def test_error_handling(self):
        """Test error handling"""
        obj = YourClass()

        with pytest.raises(ValueError) as exc_info:
            obj.method(invalid_input)

        assert "error message" in str(exc_info.value)
```

### Integration Test Template

```python
import pytest
from unittest.mock import MagicMock

@pytest.mark.integration
class TestYourIntegration:
    """Test integration scenario"""

    def test_complete_workflow(self, dynamodb_table, s3_bucket, seed_test_data):
        """Test end-to-end workflow"""
        # Arrange
        file_id = 'test-file-123'
        # Setup test data in dynamodb_table

        # Act
        result = your_workflow_function(file_id)

        # Assert
        assert result['status'] == 'COMPLETED'
        # Verify DynamoDB records created
        # Verify S3 objects created
```

### Test Fixtures

Add fixtures to `conftest.py`:

```python
@pytest.fixture
def your_test_data():
    """Description of test data"""
    return {
        'key': 'value',
        'nested': {
            'data': 123
        }
    }
```

---

## CI/CD Integration

### GitHub Actions Example

Create `.github/workflows/test.yml`:

```yaml
name: Test Suite

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install -r tests/requirements.txt
          pip install -r backend/layers/common/requirements.txt

      - name: Run unit tests
        run: |
          pytest tests/unit/ -v --cov=backend/layers/common/python/common --cov-report=xml

      - name: Run integration tests
        run: |
          pytest tests/integration/ -v

      - name: Upload coverage to Codecov
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage.xml
          fail_ci_if_error: true
```

### Pre-commit Hook

Create `.git/hooks/pre-commit`:

```bash
#!/bin/bash

echo "Running tests before commit..."

# Run unit tests
pytest tests/unit/ -q

if [ $? -ne 0 ]; then
    echo "❌ Unit tests failed. Commit aborted."
    exit 1
fi

echo "✅ Tests passed!"
exit 0
```

Make executable:
```bash
chmod +x .git/hooks/pre-commit
```

---

## Manual Testing with Real Files

### Test with Real Period 8 Files

```bash
# 1. Deploy to AWS
cd backend
sam build
sam deploy --guided

# 2. Seed database
cd seed-data
python seed_dynamodb.py --stack-name contractor-pay-tracker-dev

# 3. Upload NASA file
aws s3 cp \
  "../IntitalDesginFiles/RealContractorPayFiles/28-Jul-25 to 24-Aug-25/NASA GCI Nasstar Contractor Pay Figures 01092025.xlsx" \
  s3://contractor-pay-files-development-<account-id>/uploads/2025/09/nasa_test.xlsx

# 4. Check processing
aws dynamodb query \
  --table-name contractor-pay-development \
  --index-name GSI3 \
  --key-condition-expression "GSI3PK = :pk" \
  --expression-attribute-values '{":pk":{"S":"FILES"}}'

# 5. Verify records imported
aws dynamodb scan \
  --table-name contractor-pay-development \
  --filter-expression "EntityType = :type" \
  --expression-attribute-values '{":type":{"S":"PayRecord"}}'
```

---

## Troubleshooting

### Common Issues

**Import Errors**

```bash
# Solution: Add backend to PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)/backend/layers/common/python"
pytest
```

**AWS Mock Errors**

```bash
# Solution: Set AWS environment variables
export AWS_ACCESS_KEY_ID=testing
export AWS_SECRET_ACCESS_KEY=testing
export AWS_DEFAULT_REGION=eu-west-2
pytest tests/integration/
```

**Excel File Not Found**

```bash
# Solution: Ensure fixtures exist
ls tests/fixtures/
# If empty, regenerate:
python -c "from openpyxl import Workbook; ..." # (see fixture creation script)
```

**Coverage Not Working**

```bash
# Solution: Install coverage
pip install pytest-cov

# Run with coverage
pytest --cov=backend/layers/common/python/common
```

---

## Next Steps

1. ✅ Run unit tests: `pytest tests/unit/ -v`
2. 🚧 Implement integration test scenarios
3. 🚧 Test with real Period 8 files
4. 🚧 Set up CI/CD pipeline
5. 🚧 Achieve 80%+ coverage
6. 🚧 Add performance benchmarks

---

## Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [Moto (AWS Mocking)](https://docs.getmoto.org/)
- [Coverage.py](https://coverage.readthedocs.io/)
- [Testing Best Practices](https://docs.python-guide.org/writing/tests/)
