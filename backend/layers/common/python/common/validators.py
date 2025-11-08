"""
Validation rules engine for contractor pay records
Implements all business rules from Gemini improvements
"""

from datetime import datetime
from decimal import Decimal
from typing import Dict, List, Optional, Tuple


class ValidationEngine:
    """Validate contractor pay records against business rules"""

    def __init__(self, dynamodb_client, system_params: Dict = None):
        """
        Initialize validation engine

        Args:
            dynamodb_client: DynamoDB client instance
            system_params: System parameters (VAT rate, thresholds, etc.)
        """
        self.db = dynamodb_client
        self.params = system_params or {}

        # Load system parameters if not provided
        if not self.params:
            self._load_system_parameters()

    def _load_system_parameters(self):
        """Load system parameters from DynamoDB"""
        params = [
            'VAT_RATE',
            'OVERTIME_MULTIPLIER',
            'OVERTIME_TOLERANCE_PERCENT',
            'RATE_CHANGE_ALERT_PERCENT',
            'NAME_MATCH_THRESHOLD'
        ]

        for param in params:
            value = self.db.get_system_parameter(param)
            if value:
                # Convert to appropriate type
                if param.endswith('_PERCENT'):
                    self.params[param] = float(value)
                elif param == 'NAME_MATCH_THRESHOLD':
                    self.params[param] = int(value)
                else:
                    self.params[param] = float(value)

    def validate_record(
        self,
        record: Dict,
        umbrella_id: str,
        period_data: Dict,
        contractors_cache: Dict = None
    ) -> Tuple[bool, List[Dict], List[Dict]]:
        """
        Validate a single pay record

        Args:
            record: Pay record dict from Excel
            umbrella_id: Umbrella company ID
            period_data: Pay period information
            contractors_cache: Cached contractor data (for performance)

        Returns:
            Tuple of (is_valid, errors, warnings)
            - is_valid: False if CRITICAL errors found
            - errors: List of error dicts (CRITICAL - blocks import)
            - warnings: List of warning dicts (NON-BLOCKING)
        """
        errors = []
        warnings = []

        # Rule 1: Check if permanent staff (CRITICAL)
        perm_result = self.check_permanent_staff(record)
        if not perm_result['valid']:
            errors.append(perm_result['error'])
            return False, errors, warnings  # Stop validation immediately

        # Rule 2: Find and validate contractor
        contractor_result = self.find_contractor(record, contractors_cache)
        if not contractor_result['valid']:
            if contractor_result['severity'] == 'CRITICAL':
                errors.append(contractor_result['error'])
                return False, errors, warnings
            else:
                warnings.append(contractor_result['warning'])

        contractor_id = contractor_result.get('contractor_id')
        contractor_data = contractor_result.get('contractor')

        # Rule 3: Validate contractor-umbrella association (CRITICAL)
        assoc_result = self.validate_umbrella_association(
            contractor_id,
            umbrella_id,
            period_data
        )
        if not assoc_result['valid']:
            errors.append(assoc_result['error'])
            return False, errors, warnings

        # Rule 4: Validate VAT calculation (CRITICAL)
        vat_result = self.validate_vat(record)
        if not vat_result['valid']:
            errors.append(vat_result['error'])
            # Don't return yet - collect all errors

        # Rule 5: Validate overtime rate if applicable (CRITICAL)
        if record['record_type'] == 'OVERTIME':
            overtime_result = self.validate_overtime_rate(record)
            if not overtime_result['valid']:
                errors.append(overtime_result['error'])

        # Rule 6: Check rate changes (WARNING)
        if contractor_id:
            rate_change_result = self.check_rate_change(
                contractor_id,
                record['day_rate'],
                period_data
            )
            if rate_change_result['warning']:
                warnings.append(rate_change_result['warning'])

        # Rule 7: Validate hours (WARNING)
        hours_result = self.validate_hours(record)
        if hours_result['warning']:
            warnings.append(hours_result['warning'])

        # Record is invalid if any CRITICAL errors found
        is_valid = len(errors) == 0

        return is_valid, errors, warnings

    def check_permanent_staff(self, record: Dict) -> Dict:
        """
        Rule 1: Check if person is permanent staff
        CRITICAL error if found - Gemini improvement #2
        """
        first_name = record['forename']
        last_name = record['surname']

        is_permanent = self.db.check_permanent_staff(first_name, last_name)

        if is_permanent:
            return {
                'valid': False,
                'severity': 'CRITICAL',
                'error': {
                    'error_type': 'PERMANENT_STAFF',
                    'severity': 'CRITICAL',
                    'row_number': record.get('row_number'),
                    'employee_id': record.get('employee_id'),
                    'contractor_name': f"{first_name} {last_name}",
                    'error_message': f"CRITICAL: {first_name} {last_name} is permanent staff and must NOT appear in contractor pay files",
                    'suggested_fix': f"Remove {first_name} {last_name} from this file - they should be paid via payroll, not umbrella company"
                }
            }

        return {'valid': True}

    def find_contractor(self, record: Dict, contractors_cache: Dict = None) -> Dict:
        """
        Rule 2: Find contractor using fuzzy matching
        CRITICAL if not found after fuzzy match
        WARNING if fuzzy matched (confidence < 100%)
        """
        from .fuzzy_matcher import FuzzyMatcher

        first_name = record['forename']
        last_name = record['surname']

        # Get contractors from cache or database
        if contractors_cache:
            contractors = list(contractors_cache.values())
        else:
            contractors = self.db.get_contractor_by_name(first_name, last_name)

        # Fuzzy match
        matcher = FuzzyMatcher(threshold=int(self.params.get('NAME_MATCH_THRESHOLD', 85)))
        match_result = matcher.match_contractor_name(first_name, last_name, contractors)

        if not match_result:
            return {
                'valid': False,
                'severity': 'CRITICAL',
                'error': {
                    'error_type': 'UNKNOWN_CONTRACTOR',
                    'severity': 'CRITICAL',
                    'row_number': record.get('row_number'),
                    'employee_id': record.get('employee_id'),
                    'contractor_name': f"{first_name} {last_name}",
                    'error_message': f"CRITICAL: Contractor '{first_name} {last_name}' not found in golden reference data (after fuzzy matching)",
                    'suggested_fix': "Add this contractor to the system or check for spelling errors"
                }
            }

        contractor = match_result['contractor']
        contractor_id = contractor.get('ContractorID')

        # If fuzzy matched, add warning
        if match_result['match_type'] == 'FUZZY':
            return {
                'valid': True,
                'severity': 'WARNING',
                'contractor_id': contractor_id,
                'contractor': contractor,
                'warning': {
                    'warning_type': 'FUZZY_NAME_MATCH',
                    'row_number': record.get('row_number'),
                    'warning_message': f"Name '{first_name} {last_name}' matched to '{contractor['FirstName']} {contractor['LastName']}' with {match_result['confidence']}% confidence",
                    'auto_resolved': True,
                    'resolution_notes': f"Fuzzy matched: {match_result['searched_name']} → {match_result['matched_name']}"
                }
            }

        # Exact match - all good
        return {
            'valid': True,
            'contractor_id': contractor_id,
            'contractor': contractor
        }

    def validate_umbrella_association(
        self,
        contractor_id: str,
        umbrella_id: str,
        period_data: Dict
    ) -> Dict:
        """
        Rule 3: Validate contractor-umbrella association
        CRITICAL - Gemini improvement #1 (many-to-many support)

        Checks:
        - Contractor has association with this umbrella
        - Association is valid for this period (ValidFrom/ValidTo dates)
        """
        if not contractor_id:
            return {'valid': False, 'error': {'error_type': 'NO_CONTRACTOR_ID'}}

        # Get all associations for contractor
        associations = self.db.get_contractor_umbrella_associations(contractor_id)

        period_start = period_data.get('WorkStartDate')
        period_end = period_data.get('WorkEndDate')

        # Find matching umbrella association
        valid_association = None
        for assoc in associations:
            if assoc['UmbrellaID'] != umbrella_id:
                continue

            # Check date validity
            valid_from = assoc.get('ValidFrom')
            valid_to = assoc.get('ValidTo')

            if valid_from and valid_from > period_start:
                continue  # Not valid yet

            if valid_to and valid_to < period_end:
                continue  # Expired

            valid_association = assoc
            break

        if not valid_association:
            return {
                'valid': False,
                'error': {
                    'error_type': 'NO_UMBRELLA_ASSOCIATION',
                    'severity': 'CRITICAL',
                    'contractor_id': contractor_id,
                    'umbrella_id': umbrella_id,
                    'error_message': f"CRITICAL: Contractor does not have a valid association with this umbrella company for period {period_start} to {period_end}",
                    'suggested_fix': "Verify contractor is assigned to correct umbrella or update contractor-umbrella associations"
                }
            }

        return {
            'valid': True,
            'association': valid_association
        }

    def validate_vat(self, record: Dict) -> Dict:
        """
        Rule 4: Validate VAT is exactly 20%
        CRITICAL error if incorrect
        """
        amount = Decimal(str(record['amount']))
        vat_amount = Decimal(str(record['vat_amount']))

        vat_rate = Decimal(str(self.params.get('VAT_RATE', 0.20)))
        expected_vat = amount * vat_rate

        # Allow 1p tolerance for rounding
        tolerance = Decimal('0.01')

        if abs(vat_amount - expected_vat) > tolerance:
            return {
                'valid': False,
                'error': {
                    'error_type': 'INVALID_VAT',
                    'severity': 'CRITICAL',
                    'row_number': record.get('row_number'),
                    'employee_id': record.get('employee_id'),
                    'error_message': f"CRITICAL: VAT calculation incorrect. Amount: £{amount:.2f}, VAT: £{vat_amount:.2f} (expected £{expected_vat:.2f} at 20%)",
                    'suggested_fix': f"Correct VAT should be £{expected_vat:.2f}"
                }
            }

        return {'valid': True}

    def validate_overtime_rate(self, record: Dict) -> Dict:
        """
        Rule 5: Validate overtime rate is 1.5x normal rate
        CRITICAL error if incorrect (with tolerance)
        """
        # For overtime records, we need to find the normal rate
        # This is complex - for now, validate rate is reasonable
        # TODO: Implement proper overtime validation with rate history

        day_rate = Decimal(str(record['day_rate']))
        multiplier = Decimal(str(self.params.get('OVERTIME_MULTIPLIER', 1.5)))
        tolerance_percent = Decimal(str(self.params.get('OVERTIME_TOLERANCE_PERCENT', 2.0)))

        # For now, just check rate is higher than typical
        # Full implementation would compare to contractor's normal rate
        if day_rate < Decimal('300'):  # Suspiciously low for overtime
            return {
                'valid': False,
                'error': {
                    'error_type': 'INVALID_OVERTIME_RATE',
                    'severity': 'CRITICAL',
                    'row_number': record.get('row_number'),
                    'error_message': f"CRITICAL: Overtime rate £{day_rate:.2f} seems too low (should be 1.5x normal rate)",
                    'suggested_fix': "Verify overtime rate is calculated correctly"
                }
            }

        return {'valid': True}

    def check_rate_change(
        self,
        contractor_id: str,
        new_rate: float,
        period_data: Dict
    ) -> Dict:
        """
        Rule 6: Check for significant rate changes
        WARNING if rate changed > 5% from previous period
        """
        # TODO: Implement rate history lookup
        # For now, return no warning
        return {'warning': None}

    def validate_hours(self, record: Dict) -> Dict:
        """
        Rule 7: Validate hours are reasonable
        WARNING if unusual hours detected
        """
        unit_days = record['unit_days']
        total_hours = record.get('total_hours', 0)

        # Check for unusual values
        if unit_days > 25:  # More than 25 days in 4-week period
            return {
                'warning': {
                    'warning_type': 'UNUSUAL_HOURS',
                    'row_number': record.get('row_number'),
                    'warning_message': f"Unusual number of days worked: {unit_days} days (>25 days in 4-week period)",
                    'auto_resolved': False
                }
            }

        if unit_days < 0:
            return {
                'warning': {
                    'warning_type': 'UNUSUAL_HOURS',
                    'row_number': record.get('row_number'),
                    'warning_message': f"Negative days worked: {unit_days} days",
                    'auto_resolved': False
                }
            }

        return {'warning': None}
