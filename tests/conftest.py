"""
Pytest configuration and shared fixtures
"""

import os
import sys
from decimal import Decimal
from unittest.mock import MagicMock

import pytest

# Add backend layers to Python path
backend_path = os.path.join(os.path.dirname(__file__), '..', 'backend', 'layers', 'common', 'python')
sys.path.insert(0, backend_path)


@pytest.fixture
def mock_dynamodb_client():
    """Mock DynamoDB client for testing"""
    mock_client = MagicMock()

    # Mock table
    mock_client.table = MagicMock()

    # Mock system parameters
    def mock_get_system_parameter(param_name):
        params = {
            'VAT_RATE': '0.20',
            'OVERTIME_MULTIPLIER': '1.5',
            'OVERTIME_TOLERANCE_PERCENT': '2.0',
            'RATE_CHANGE_ALERT_PERCENT': '5.0',
            'NAME_MATCH_THRESHOLD': '85'
        }
        return params.get(param_name)

    mock_client.get_system_parameter = mock_get_system_parameter

    return mock_client


@pytest.fixture
def sample_contractors():
    """Sample contractor data for testing"""
    return [
        {
            'ContractorID': 'C001',
            'FirstName': 'Jonathan',
            'LastName': 'Mays',
            'EmployeeID': '812001',
            'NormalizedName': 'jonathan mays'
        },
        {
            'ContractorID': 'C002',
            'FirstName': 'David',
            'LastName': 'Hunt',
            'EmployeeID': '812002',
            'NormalizedName': 'david hunt'
        },
        {
            'ContractorID': 'C003',
            'FirstName': 'Donna',
            'LastName': 'Smith',
            'EmployeeID': '812003',
            'NormalizedName': 'donna smith'
        },
        {
            'ContractorID': 'C004',
            'FirstName': 'Stephen',
            'LastName': 'Matthews',
            'EmployeeID': '812004',
            'NormalizedName': 'stephen matthews'
        }
    ]


@pytest.fixture
def sample_pay_record():
    """Sample pay record for validation testing"""
    return {
        'row_number': 5,
        'employee_id': '812001',
        'forename': 'Jonathan',
        'surname': 'Mays',
        'unit_days': 20,
        'day_rate': 450.00,
        'amount': 9000.00,
        'vat_amount': 1800.00,
        'gross_amount': 10800.00,
        'total_hours': 160,
        'record_type': 'NORMAL',
        'notes': ''
    }


@pytest.fixture
def sample_period_data():
    """Sample period data for testing"""
    return {
        'PeriodID': '8',
        'PeriodNumber': 8,
        'WorkStartDate': '2025-07-28',
        'WorkEndDate': '2025-08-24',
        'SubmissionDeadline': '2025-09-01'
    }


@pytest.fixture
def sample_umbrella_associations():
    """Sample contractor-umbrella associations"""
    return [
        {
            'AssociationID': 'A001',
            'ContractorID': 'C001',
            'UmbrellaID': 'U001',
            'UmbrellaCode': 'NASA',
            'ValidFrom': '2025-01-01',
            'ValidTo': None
        },
        {
            'AssociationID': 'A002',
            'ContractorID': 'C003',
            'UmbrellaID': 'U001',
            'UmbrellaCode': 'NASA',
            'ValidFrom': '2025-01-01',
            'ValidTo': None
        },
        {
            'AssociationID': 'A003',
            'ContractorID': 'C003',
            'UmbrellaID': 'U002',
            'UmbrellaCode': 'PARASOL',
            'ValidFrom': '2025-01-01',
            'ValidTo': None
        }
    ]
