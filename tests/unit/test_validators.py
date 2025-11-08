"""
Unit tests for validators.py
Tests all 7 business rules for contractor pay validation
"""

import pytest
from decimal import Decimal
from unittest.mock import MagicMock
from common.validators import ValidationEngine


class TestValidationEngine:
    """Test validation engine business rules"""

    def test_rule1_permanent_staff_detected(self, mock_dynamodb_client, sample_pay_record):
        """Rule 1: CRITICAL - Detects permanent staff and blocks import"""
        validator = ValidationEngine(mock_dynamodb_client)

        # Test with Martin Alabone (permanent staff)
        record = sample_pay_record.copy()
        record['forename'] = 'Martin'
        record['surname'] = 'Alabone'

        result = validator.check_permanent_staff(record)

        assert result['valid'] is False
        assert result['severity'] == 'CRITICAL'
        assert 'permanent staff' in result['error']['error_message'].lower()
        assert result['error']['error_type'] == 'PERMANENT_STAFF'

    def test_rule1_permanent_staff_all_four_detected(self, mock_dynamodb_client, sample_pay_record):
        """Rule 1: Verify all 4 permanent staff are detected"""
        validator = ValidationEngine(mock_dynamodb_client)

        permanent_staff = [
            ('Syed', 'Syed'),
            ('Victor', 'Cheung'),
            ('Gareth', 'Jones'),
            ('Martin', 'Alabone')
        ]

        for first_name, last_name in permanent_staff:
            record = sample_pay_record.copy()
            record['forename'] = first_name
            record['surname'] = last_name

            result = validator.check_permanent_staff(record)

            assert result['valid'] is False, f"{first_name} {last_name} should be detected as permanent staff"
            assert result['severity'] == 'CRITICAL'

    def test_rule1_contractor_passes(self, mock_dynamodb_client, sample_pay_record):
        """Rule 1: Valid contractor passes permanent staff check"""
        validator = ValidationEngine(mock_dynamodb_client)

        result = validator.check_permanent_staff(sample_pay_record)

        assert result['valid'] is True

    def test_rule2_exact_name_match(self, mock_dynamodb_client, sample_pay_record, sample_contractors):
        """Rule 2: Exact contractor name match (100% confidence)"""
        validator = ValidationEngine(mock_dynamodb_client)

        result = validator.find_contractor(sample_pay_record, {'C001': sample_contractors[0]})

        assert result['valid'] is True
        assert result['contractor_id'] == 'C001'
        assert 'warning' not in result  # No warning for exact match

    def test_rule2_fuzzy_name_match_with_warning(self, mock_dynamodb_client, sample_contractors):
        """Rule 2: Fuzzy name match returns WARNING (not CRITICAL)"""
        validator = ValidationEngine(mock_dynamodb_client)

        # Jon -> Jonathan (fuzzy match)
        record = {
            'forename': 'Jon',
            'surname': 'Mays',
            'row_number': 5
        }

        contractors_cache = {c['ContractorID']: c for c in sample_contractors}
        result = validator.find_contractor(record, contractors_cache)

        assert result['valid'] is True  # Still valid!
        assert result['severity'] == 'WARNING'
        assert result['warning']['warning_type'] == 'FUZZY_NAME_MATCH'
        assert 'confidence' in result['warning']['warning_message']

    def test_rule2_unknown_contractor_critical_error(self, mock_dynamodb_client):
        """Rule 2: Unknown contractor returns CRITICAL error"""
        validator = ValidationEngine(mock_dynamodb_client)

        record = {
            'forename': 'Unknown',
            'surname': 'Person',
            'row_number': 5,
            'employee_id': '999999'
        }

        result = validator.find_contractor(record, {})

        assert result['valid'] is False
        assert result['severity'] == 'CRITICAL'
        assert result['error']['error_type'] == 'UNKNOWN_CONTRACTOR'

    def test_rule3_valid_umbrella_association(self, mock_dynamodb_client, sample_period_data, sample_umbrella_associations):
        """Rule 3: Valid contractor-umbrella association passes"""
        validator = ValidationEngine(mock_dynamodb_client)

        # Mock the get_contractor_umbrella_associations method
        mock_dynamodb_client.get_contractor_umbrella_associations = MagicMock(
            return_value=sample_umbrella_associations
        )

        result = validator.validate_umbrella_association('C001', 'U001', sample_period_data)

        assert result['valid'] is True
        assert result['association']['AssociationID'] == 'A001'

    def test_rule3_many_to_many_donna_smith(self, mock_dynamodb_client, sample_period_data, sample_umbrella_associations):
        """Rule 3: Donna Smith has valid associations with both NASA and PARASOL"""
        validator = ValidationEngine(mock_dynamodb_client)

        mock_dynamodb_client.get_contractor_umbrella_associations = MagicMock(
            return_value=sample_umbrella_associations
        )

        # Test NASA association
        result_nasa = validator.validate_umbrella_association('C003', 'U001', sample_period_data)
        assert result_nasa['valid'] is True
        assert result_nasa['association']['UmbrellaCode'] == 'NASA'

        # Test PARASOL association
        result_parasol = validator.validate_umbrella_association('C003', 'U002', sample_period_data)
        assert result_parasol['valid'] is True
        assert result_parasol['association']['UmbrellaCode'] == 'PARASOL'

    def test_rule3_no_umbrella_association_critical(self, mock_dynamodb_client, sample_period_data):
        """Rule 3: No umbrella association returns CRITICAL error"""
        validator = ValidationEngine(mock_dynamodb_client)

        mock_dynamodb_client.get_contractor_umbrella_associations = MagicMock(return_value=[])

        result = validator.validate_umbrella_association('C001', 'U999', sample_period_data)

        assert result['valid'] is False
        assert result['error']['error_type'] == 'NO_UMBRELLA_ASSOCIATION'
        assert result['error']['severity'] == 'CRITICAL'

    def test_rule3_expired_association_fails(self, mock_dynamodb_client, sample_period_data):
        """Rule 3: Expired umbrella association fails validation"""
        validator = ValidationEngine(mock_dynamodb_client)

        # Association that expired before the period
        expired_association = [
            {
                'AssociationID': 'A999',
                'ContractorID': 'C001',
                'UmbrellaID': 'U001',
                'ValidFrom': '2024-01-01',
                'ValidTo': '2024-12-31'  # Expired before period starts (2025-07-28)
            }
        ]

        mock_dynamodb_client.get_contractor_umbrella_associations = MagicMock(
            return_value=expired_association
        )

        result = validator.validate_umbrella_association('C001', 'U001', sample_period_data)

        assert result['valid'] is False

    def test_rule4_vat_exactly_20_percent(self, mock_dynamodb_client, sample_pay_record):
        """Rule 4: VAT exactly 20% passes validation"""
        validator = ValidationEngine(mock_dynamodb_client)

        result = validator.validate_vat(sample_pay_record)

        assert result['valid'] is True

    def test_rule4_vat_incorrect_critical_error(self, mock_dynamodb_client, sample_pay_record):
        """Rule 4: Incorrect VAT returns CRITICAL error"""
        validator = ValidationEngine(mock_dynamodb_client)

        # Incorrect VAT (15% instead of 20%)
        record = sample_pay_record.copy()
        record['amount'] = 10000.00
        record['vat_amount'] = 1500.00  # Should be 2000.00

        result = validator.validate_vat(record)

        assert result['valid'] is False
        assert result['error']['error_type'] == 'INVALID_VAT'
        assert result['error']['severity'] == 'CRITICAL'
        assert 'expected' in result['error']['error_message'].lower()

    def test_rule4_vat_1p_tolerance(self, mock_dynamodb_client, sample_pay_record):
        """Rule 4: VAT allows 1p tolerance for rounding"""
        validator = ValidationEngine(mock_dynamodb_client)

        # VAT is 1p off due to rounding
        record = sample_pay_record.copy()
        record['amount'] = 9001.00
        record['vat_amount'] = 1800.00  # Should be 1800.20, but within 1p tolerance

        result = validator.validate_vat(record)

        assert result['valid'] is True

    def test_rule4_vat_beyond_tolerance_fails(self, mock_dynamodb_client, sample_pay_record):
        """Rule 4: VAT beyond 1p tolerance fails"""
        validator = ValidationEngine(mock_dynamodb_client)

        # VAT is 2p off (beyond tolerance)
        record = sample_pay_record.copy()
        record['amount'] = 9001.00
        record['vat_amount'] = 1798.00  # Should be 1800.20, off by 2.20p

        result = validator.validate_vat(record)

        assert result['valid'] is False

    def test_rule5_overtime_rate_validation(self, mock_dynamodb_client, sample_pay_record):
        """Rule 5: Overtime rate validation"""
        validator = ValidationEngine(mock_dynamodb_client)

        # Valid overtime rate (high day rate)
        record = sample_pay_record.copy()
        record['record_type'] = 'OVERTIME'
        record['day_rate'] = 675.00  # 1.5x of 450

        result = validator.validate_overtime_rate(record)

        assert result['valid'] is True

    def test_rule5_overtime_rate_too_low_fails(self, mock_dynamodb_client, sample_pay_record):
        """Rule 5: Suspiciously low overtime rate fails"""
        validator = ValidationEngine(mock_dynamodb_client)

        # Overtime rate too low
        record = sample_pay_record.copy()
        record['record_type'] = 'OVERTIME'
        record['day_rate'] = 250.00  # Too low for overtime

        result = validator.validate_overtime_rate(record)

        assert result['valid'] is False
        assert result['error']['error_type'] == 'INVALID_OVERTIME_RATE'

    def test_rule7_hours_validation_normal(self, mock_dynamodb_client, sample_pay_record):
        """Rule 7: Normal hours pass validation"""
        validator = ValidationEngine(mock_dynamodb_client)

        result = validator.validate_hours(sample_pay_record)

        assert result['warning'] is None

    def test_rule7_hours_too_high_warning(self, mock_dynamodb_client, sample_pay_record):
        """Rule 7: Excessive hours (>25 days) returns WARNING"""
        validator = ValidationEngine(mock_dynamodb_client)

        record = sample_pay_record.copy()
        record['unit_days'] = 30  # More than 25 days in 4-week period

        result = validator.validate_hours(record)

        assert result['warning'] is not None
        assert result['warning']['warning_type'] == 'UNUSUAL_HOURS'
        assert '30 days' in result['warning']['warning_message']

    def test_rule7_negative_hours_warning(self, mock_dynamodb_client, sample_pay_record):
        """Rule 7: Negative hours returns WARNING"""
        validator = ValidationEngine(mock_dynamodb_client)

        record = sample_pay_record.copy()
        record['unit_days'] = -5

        result = validator.validate_hours(record)

        assert result['warning'] is not None
        assert 'Negative' in result['warning']['warning_message']

    def test_validate_record_all_pass(self, mock_dynamodb_client, sample_pay_record, sample_contractors, sample_period_data, sample_umbrella_associations):
        """Complete record validation: all rules pass"""
        validator = ValidationEngine(mock_dynamodb_client)

        # Mock methods
        mock_dynamodb_client.get_contractor_umbrella_associations = MagicMock(
            return_value=sample_umbrella_associations
        )

        contractors_cache = {c['ContractorID']: c for c in sample_contractors}

        is_valid, errors, warnings = validator.validate_record(
            sample_pay_record,
            'U001',
            sample_period_data,
            contractors_cache
        )

        assert is_valid is True
        assert len(errors) == 0
        assert len(warnings) == 0

    def test_validate_record_permanent_staff_blocks_all(self, mock_dynamodb_client, sample_pay_record, sample_contractors, sample_period_data):
        """Complete validation: permanent staff blocks immediately"""
        validator = ValidationEngine(mock_dynamodb_client)

        # Martin Alabone (permanent staff)
        record = sample_pay_record.copy()
        record['forename'] = 'Martin'
        record['surname'] = 'Alabone'

        contractors_cache = {c['ContractorID']: c for c in sample_contractors}

        is_valid, errors, warnings = validator.validate_record(
            record,
            'U001',
            sample_period_data,
            contractors_cache
        )

        assert is_valid is False
        assert len(errors) == 1
        assert errors[0]['error_type'] == 'PERMANENT_STAFF'
        # Should stop validation immediately, not check other rules

    def test_validate_record_multiple_critical_errors(self, mock_dynamodb_client, sample_pay_record, sample_contractors, sample_period_data, sample_umbrella_associations):
        """Complete validation: multiple CRITICAL errors collected"""
        validator = ValidationEngine(mock_dynamodb_client)

        # Record with multiple errors
        record = sample_pay_record.copy()
        record['vat_amount'] = 1500.00  # Wrong VAT (CRITICAL)
        record['record_type'] = 'OVERTIME'
        record['day_rate'] = 200.00  # Wrong overtime rate (CRITICAL)

        mock_dynamodb_client.get_contractor_umbrella_associations = MagicMock(
            return_value=sample_umbrella_associations
        )

        contractors_cache = {c['ContractorID']: c for c in sample_contractors}

        is_valid, errors, warnings = validator.validate_record(
            record,
            'U001',
            sample_period_data,
            contractors_cache
        )

        assert is_valid is False
        assert len(errors) >= 2  # Multiple CRITICAL errors
        error_types = [e['error_type'] for e in errors]
        assert 'INVALID_VAT' in error_types
        assert 'INVALID_OVERTIME_RATE' in error_types

    def test_validate_record_warnings_dont_block(self, mock_dynamodb_client, sample_contractors, sample_period_data, sample_umbrella_associations):
        """Complete validation: WARNINGS don't block import"""
        validator = ValidationEngine(mock_dynamodb_client)

        # Record with warnings but no critical errors
        record = {
            'row_number': 10,
            'employee_id': '812001',
            'forename': 'Jon',  # Fuzzy match -> WARNING
            'surname': 'Mays',
            'unit_days': 30,  # Excessive hours -> WARNING
            'day_rate': 450.00,
            'amount': 13500.00,  # 30 days * 450
            'vat_amount': 2700.00,  # Correct VAT
            'gross_amount': 16200.00,
            'total_hours': 240,
            'record_type': 'NORMAL',
            'notes': ''
        }

        mock_dynamodb_client.get_contractor_umbrella_associations = MagicMock(
            return_value=sample_umbrella_associations
        )

        contractors_cache = {c['ContractorID']: c for c in sample_contractors}

        is_valid, errors, warnings = validator.validate_record(
            record,
            'U001',
            sample_period_data,
            contractors_cache
        )

        # Should be valid despite warnings
        assert is_valid is True
        assert len(errors) == 0
        assert len(warnings) >= 2  # Fuzzy match + excessive hours
        warning_types = [w['warning_type'] for w in warnings]
        assert 'FUZZY_NAME_MATCH' in warning_types
        assert 'UNUSUAL_HOURS' in warning_types

    def test_system_parameters_loading(self, mock_dynamodb_client):
        """Test that system parameters are loaded correctly"""
        validator = ValidationEngine(mock_dynamodb_client)

        assert validator.params['VAT_RATE'] == 0.20
        assert validator.params['OVERTIME_MULTIPLIER'] == 1.5
        assert validator.params['NAME_MATCH_THRESHOLD'] == 85
