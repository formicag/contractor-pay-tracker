"""
Validation rules engine for contractor pay records
Implements all business rules from Gemini improvements
"""

print("[VALIDATORS_MODULE] Starting validators.py module load")

from datetime import datetime
from decimal import Decimal
from typing import Dict, List, Optional, Tuple

print("[VALIDATORS_MODULE] Imported datetime, Decimal, and typing modules")


class ValidationEngine:
    """Validate contractor pay records against business rules"""

    def __init__(self, dynamodb_client, system_params: Dict = None):
        """
        Initialize validation engine

        Args:
            dynamodb_client: DynamoDB client instance
            system_params: System parameters (VAT rate, thresholds, etc.)
        """
        print("[VALIDATION_ENGINE_INIT] Starting ValidationEngine initialization")

        self.db = dynamodb_client
        print(f"[VALIDATION_ENGINE_INIT] Assigned dynamodb_client to self.db: {self.db}")

        self.params = system_params or {}
        print(f"[VALIDATION_ENGINE_INIT] Assigned system_params to self.params: {self.params}")

        # Load system parameters if not provided
        if not self.params:
            print("[VALIDATION_ENGINE_INIT] system_params is empty, calling _load_system_parameters()")
            self._load_system_parameters()
        else:
            print("[VALIDATION_ENGINE_INIT] system_params is populated, skipping _load_system_parameters()")

        print("[VALIDATION_ENGINE_INIT] ValidationEngine initialization complete")

    def _load_system_parameters(self):
        """Load system parameters from DynamoDB"""
        print("[LOAD_SYSTEM_PARAMETERS] Starting _load_system_parameters()")

        params = [
            'VAT_RATE',
            'OVERTIME_MULTIPLIER',
            'OVERTIME_TOLERANCE_PERCENT',
            'RATE_CHANGE_ALERT_PERCENT',
            'NAME_MATCH_THRESHOLD'
        ]
        print(f"[LOAD_SYSTEM_PARAMETERS] Created params list: {params}")

        print(f"[LOAD_SYSTEM_PARAMETERS] Iterating through {len(params)} parameters")
        for param in params:
            print(f"[LOAD_SYSTEM_PARAMETERS] Processing parameter: {param}")

            value = self.db.get_system_parameter(param)
            print(f"[LOAD_SYSTEM_PARAMETERS] Retrieved value for {param}: {value}")

            if value:
                print(f"[LOAD_SYSTEM_PARAMETERS] Value is truthy, converting to appropriate type")

                # Convert to appropriate type
                if param.endswith('_PERCENT'):
                    print(f"[LOAD_SYSTEM_PARAMETERS] Parameter ends with _PERCENT, converting to float")
                    self.params[param] = float(value)
                    print(f"[LOAD_SYSTEM_PARAMETERS] {param} = {self.params[param]}")
                elif param == 'NAME_MATCH_THRESHOLD':
                    print(f"[LOAD_SYSTEM_PARAMETERS] Parameter is NAME_MATCH_THRESHOLD, converting to int")
                    self.params[param] = int(value)
                    print(f"[LOAD_SYSTEM_PARAMETERS] {param} = {self.params[param]}")
                else:
                    print(f"[LOAD_SYSTEM_PARAMETERS] Default conversion to float")
                    self.params[param] = float(value)
                    print(f"[LOAD_SYSTEM_PARAMETERS] {param} = {self.params[param]}")
            else:
                print(f"[LOAD_SYSTEM_PARAMETERS] Value is falsy, skipping {param}")

        print(f"[LOAD_SYSTEM_PARAMETERS] _load_system_parameters() complete. Final params: {self.params}")

    def validate_record(
        self,
        record: Dict,
        umbrella_id: str,
        period_data: Dict,
        contractors_cache: Dict = None,
        rates_cache: Dict = None
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
        print(f"[VALIDATE_RECORD] Called with record={record}, umbrella_id={umbrella_id}, period_data={period_data}")

        errors = []
        print("[VALIDATE_RECORD] Initialized errors list: []")

        warnings = []
        print("[VALIDATE_RECORD] Initialized warnings list: []")

        # Rule 1: Find and validate contractor
        print("[VALIDATE_RECORD] Rule 1: Calling find_contractor()")
        contractor_result = self.find_contractor(record, contractors_cache)
        print(f"[VALIDATE_RECORD] find_contractor returned: {contractor_result}")

        if not contractor_result['valid']:
            print("[VALIDATE_RECORD] Contractor lookup failed (valid=False)")
            severity = contractor_result.get('severity')
            print(f"[VALIDATE_RECORD] Contractor error severity: {severity}")

            if severity == 'CRITICAL':
                print("[VALIDATE_RECORD] Severity is CRITICAL, returning early")
                errors.append(contractor_result['error'])
                print(f"[VALIDATE_RECORD] Added error to errors list. Errors count: {len(errors)}")
                return False, errors, warnings
            else:
                print("[VALIDATE_RECORD] Severity is not CRITICAL, adding to warnings")
                warnings.append(contractor_result['warning'])
                print(f"[VALIDATE_RECORD] Added warning to warnings list. Warnings count: {len(warnings)}")
        else:
            print("[VALIDATE_RECORD] Contractor lookup passed (valid=True)")

        contractor_id = contractor_result.get('contractor_id')
        print(f"[VALIDATE_RECORD] Extracted contractor_id: {contractor_id}")

        contractor_data = contractor_result.get('contractor')
        print(f"[VALIDATE_RECORD] Extracted contractor_data: {contractor_data}")

        # Rule 3: Validate contractor-umbrella association (CRITICAL)
        print("[VALIDATE_RECORD] Rule 3: Calling validate_umbrella_association()")
        assoc_result = self.validate_umbrella_association(
            contractor_id,
            umbrella_id,
            period_data
        )
        print(f"[VALIDATE_RECORD] validate_umbrella_association returned: {assoc_result}")

        if not assoc_result['valid']:
            print("[VALIDATE_RECORD] Umbrella association validation failed (valid=False)")
            errors.append(assoc_result['error'])
            print(f"[VALIDATE_RECORD] Added error to errors list. Errors count: {len(errors)}")
            print("[VALIDATE_RECORD] Returning early due to umbrella association error")
            return False, errors, warnings
        else:
            print("[VALIDATE_RECORD] Umbrella association validation passed (valid=True)")

        # Rule 4: Validate VAT calculation (CRITICAL) - skip for expense records
        print("[VALIDATE_RECORD] Rule 4: Checking if VAT validation needed")
        record_type = record.get('record_type')

        if record_type != 'EXPENSE':
            print("[VALIDATE_RECORD] Record type is not EXPENSE, calling validate_vat()")
            vat_result = self.validate_vat(record)
            print(f"[VALIDATE_RECORD] validate_vat returned: {vat_result}")

            if not vat_result['valid']:
                print("[VALIDATE_RECORD] VAT validation failed (valid=False)")
                errors.append(vat_result['error'])
                print(f"[VALIDATE_RECORD] Added error to errors list. Errors count: {len(errors)}")
                print("[VALIDATE_RECORD] Not returning - collecting all errors")
            else:
                print("[VALIDATE_RECORD] VAT validation passed (valid=True)")
        else:
            print("[VALIDATE_RECORD] Record type is EXPENSE, skipping VAT validation")

        # Rule 5: Validate overtime rate if applicable (CRITICAL)
        # DISABLED: Overtime rate validation disabled per user request
        # print(f"[VALIDATE_RECORD] Rule 5: Checking if record_type is OVERTIME")
        # record_type = record.get('record_type')
        # print(f"[VALIDATE_RECORD] record_type: {record_type}")

        # if record_type == 'OVERTIME':
        #     print("[VALIDATE_RECORD] record_type is OVERTIME, calling validate_overtime_rate()")
        #     overtime_result = self.validate_overtime_rate(
        #         record,
        #         contractor_id,
        #         period_data,
        #         rates_cache
        #     )
        #     print(f"[VALIDATE_RECORD] validate_overtime_rate returned: {overtime_result}")

        #     if not overtime_result['valid']:
        #         print("[VALIDATE_RECORD] Overtime validation failed (valid=False)")
        #         errors.append(overtime_result['error'])
        #         print(f"[VALIDATE_RECORD] Added error to errors list. Errors count: {len(errors)}")
        #     else:
        #         print("[VALIDATE_RECORD] Overtime validation passed (valid=True)")
        #         if 'warning' in overtime_result:
        #             print("[VALIDATE_RECORD] Overtime validation has warning, adding to warnings list")
        #             warnings.append(overtime_result['warning'])
        #             print(f"[VALIDATE_RECORD] Added warning to warnings list. Warnings count: {len(warnings)}")
        # else:
        #     print("[VALIDATE_RECORD] record_type is not OVERTIME, skipping overtime validation")
        print("[VALIDATE_RECORD] Rule 5: Overtime rate validation DISABLED")

        # Rule 6: Check rate changes (WARNING)
        print("[VALIDATE_RECORD] Rule 6: Checking for rate changes")
        print(f"[VALIDATE_RECORD] contractor_id is truthy: {bool(contractor_id)}")

        if contractor_id:
            print("[VALIDATE_RECORD] contractor_id is set, calling check_rate_change()")
            day_rate = record.get('day_rate')
            print(f"[VALIDATE_RECORD] day_rate: {day_rate}")

            rate_change_result = self.check_rate_change(
                contractor_id,
                day_rate,
                period_data
            )
            print(f"[VALIDATE_RECORD] check_rate_change returned: {rate_change_result}")

            if rate_change_result['warning']:
                print("[VALIDATE_RECORD] Rate change warning present")
                warnings.append(rate_change_result['warning'])
                print(f"[VALIDATE_RECORD] Added warning to warnings list. Warnings count: {len(warnings)}")
            else:
                print("[VALIDATE_RECORD] No rate change warning")
        else:
            print("[VALIDATE_RECORD] contractor_id is not set, skipping rate change check")

        # Rule 7: Validate hours (WARNING)
        print("[VALIDATE_RECORD] Rule 7: Calling validate_hours()")
        hours_result = self.validate_hours(record)
        print(f"[VALIDATE_RECORD] validate_hours returned: {hours_result}")

        if hours_result['warning']:
            print("[VALIDATE_RECORD] Hours warning present")
            warnings.append(hours_result['warning'])
            print(f"[VALIDATE_RECORD] Added warning to warnings list. Warnings count: {len(warnings)}")
        else:
            print("[VALIDATE_RECORD] No hours warning")

        # Record is invalid if any CRITICAL errors found
        is_valid = len(errors) == 0
        print(f"[VALIDATE_RECORD] Calculated is_valid (len(errors) == 0): {is_valid}")

        print(f"[VALIDATE_RECORD] Final result: is_valid={is_valid}, errors_count={len(errors)}, warnings_count={len(warnings)}")
        return is_valid, errors, warnings

    def find_contractor(self, record: Dict, contractors_cache: Dict = None) -> Dict:
        """
        Rule 1: Find contractor using fuzzy matching
        CRITICAL if not found after fuzzy match
        WARNING if fuzzy matched (confidence < 100%)
        """
        print("[FIND_CONTRACTOR] Starting find_contractor()")

        print("[FIND_CONTRACTOR] Importing FuzzyMatcher from fuzzy_matcher module")
        from .fuzzy_matcher import FuzzyMatcher
        print("[FIND_CONTRACTOR] FuzzyMatcher imported successfully")

        first_name = record['forename']
        print(f"[FIND_CONTRACTOR] Extracted first_name: {first_name}")

        last_name = record['surname']
        print(f"[FIND_CONTRACTOR] Extracted last_name: {last_name}")

        # Get contractors from cache or database
        print(f"[FIND_CONTRACTOR] contractors_cache is provided: {contractors_cache is not None}")

        if contractors_cache:
            print("[FIND_CONTRACTOR] Using contractors_cache")
            contractors = list(contractors_cache.values())
            print(f"[FIND_CONTRACTOR] Extracted {len(contractors)} contractors from cache")
        else:
            print("[FIND_CONTRACTOR] Cache not provided, calling db.get_contractor_by_name()")
            contractors = self.db.get_contractor_by_name(first_name, last_name)
            print(f"[FIND_CONTRACTOR] Retrieved {len(contractors)} contractors from database")

        # Fuzzy match
        threshold = int(self.params.get('NAME_MATCH_THRESHOLD', 75))
        print(f"[FIND_CONTRACTOR] NAME_MATCH_THRESHOLD: {threshold}")

        print("[FIND_CONTRACTOR] Creating FuzzyMatcher instance")
        matcher = FuzzyMatcher(threshold=threshold)
        print("[FIND_CONTRACTOR] FuzzyMatcher instance created")

        print(f"[FIND_CONTRACTOR] Calling matcher.match_contractor_name({first_name}, {last_name}, ...)")
        match_result = matcher.match_contractor_name(first_name, last_name, contractors)
        print(f"[FIND_CONTRACTOR] match_contractor_name returned: {match_result}")

        if not match_result:
            print("[FIND_CONTRACTOR] No match found - returning CRITICAL error")
            full_name = f"{first_name} {last_name}"
            error_dict = {
                'valid': False,
                'severity': 'CRITICAL',
                'error': {
                    'error_type': 'UNKNOWN_CONTRACTOR',
                    'severity': 'CRITICAL',
                    'row_number': record.get('row_number'),
                    'employee_id': record.get('employee_id'),
                    'contractor_name': full_name,
                    'error_message': f"CRITICAL: Contractor '{full_name}' not found in golden reference data (after fuzzy matching)",
                    'suggested_fix': "Add this contractor to the system or check for spelling errors"
                }
            }
            print(f"[FIND_CONTRACTOR] Returning: {error_dict}")
            return error_dict

        print("[FIND_CONTRACTOR] Match found")
        contractor = match_result['contractor']
        print(f"[FIND_CONTRACTOR] Extracted contractor: {contractor}")

        contractor_id = contractor.get('ContractorID')
        print(f"[FIND_CONTRACTOR] Extracted contractor_id: {contractor_id}")

        # If fuzzy matched, add warning
        match_type = match_result.get('match_type')
        print(f"[FIND_CONTRACTOR] match_type: {match_type}")

        if match_type == 'FUZZY':
            print("[FIND_CONTRACTOR] Match type is FUZZY - returning with warning")
            confidence = match_result.get('confidence')
            contractor_full_name = f"{contractor['FirstName']} {contractor['LastName']}"
            searched_name = match_result.get('searched_name')
            matched_name = match_result.get('matched_name')

            fuzzy_result = {
                'valid': True,
                'severity': 'WARNING',
                'contractor_id': contractor_id,
                'contractor': contractor,
                'warning': {
                    'warning_type': 'FUZZY_NAME_MATCH',
                    'row_number': record.get('row_number'),
                    'warning_message': f"Name '{first_name} {last_name}' matched to '{contractor_full_name}' with {confidence}% confidence",
                    'auto_resolved': True,
                    'resolution_notes': f"Fuzzy matched: {searched_name} → {matched_name}"
                }
            }
            print(f"[FIND_CONTRACTOR] Returning fuzzy match result: {fuzzy_result}")
            return fuzzy_result

        # Exact match - all good
        print("[FIND_CONTRACTOR] Match type is EXACT - returning valid result")
        exact_result = {
            'valid': True,
            'contractor_id': contractor_id,
            'contractor': contractor
        }
        print(f"[FIND_CONTRACTOR] Returning exact match result: {exact_result}")
        return exact_result

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

        Note: umbrella_id can be either shortcode (e.g., 'CLARITY') or UUID
        """
        print("[VALIDATE_UMBRELLA_ASSOCIATION] Starting validate_umbrella_association()")
        print(f"[VALIDATE_UMBRELLA_ASSOCIATION] contractor_id={contractor_id}, umbrella_id={umbrella_id}")

        if not contractor_id:
            print("[VALIDATE_UMBRELLA_ASSOCIATION] contractor_id is empty - returning error")
            return {'valid': False, 'error': {'error_type': 'NO_CONTRACTOR_ID'}}

        # Convert shortcode to UUID if needed
        actual_umbrella_id = umbrella_id
        if '-' not in umbrella_id:  # It's a shortcode, not a UUID
            print(f"[VALIDATE_UMBRELLA_ASSOCIATION] umbrella_id looks like shortcode, looking up UUID")
            umbrella_record = self.db.get_umbrella_by_code(umbrella_id)
            if umbrella_record:
                actual_umbrella_id = umbrella_record.get('UmbrellaID')
                print(f"[VALIDATE_UMBRELLA_ASSOCIATION] Converted shortcode '{umbrella_id}' to UUID '{actual_umbrella_id}'")
            else:
                print(f"[VALIDATE_UMBRELLA_ASSOCIATION] Could not find umbrella with shortcode '{umbrella_id}'")
                return {
                    'valid': False,
                    'error': {
                        'error_type': 'UMBRELLA_NOT_FOUND',
                        'severity': 'CRITICAL',
                        'umbrella_code': umbrella_id,
                        'error_message': f"CRITICAL: Umbrella company '{umbrella_id}' not found in system",
                        'suggested_fix': f"Verify umbrella company code '{umbrella_id}' exists in the system"
                    }
                }

        print(f"[VALIDATE_UMBRELLA_ASSOCIATION] Using umbrella_id: {actual_umbrella_id}")

        # Get all associations for contractor
        print(f"[VALIDATE_UMBRELLA_ASSOCIATION] Calling db.get_contractor_umbrella_associations({contractor_id})")
        associations = self.db.get_contractor_umbrella_associations(contractor_id)
        print(f"[VALIDATE_UMBRELLA_ASSOCIATION] Retrieved {len(associations)} associations")

        period_start = period_data.get('WorkStartDate')
        print(f"[VALIDATE_UMBRELLA_ASSOCIATION] period_start: {period_start}")

        period_end = period_data.get('WorkEndDate')
        print(f"[VALIDATE_UMBRELLA_ASSOCIATION] period_end: {period_end}")

        # Find matching umbrella association
        valid_association = None
        print(f"[VALIDATE_UMBRELLA_ASSOCIATION] Iterating through {len(associations)} associations to find match")

        for idx, assoc in enumerate(associations):
            print(f"[VALIDATE_UMBRELLA_ASSOCIATION] Processing association {idx+1}/{len(associations)}: {assoc}")

            assoc_umbrella_id = assoc.get('UmbrellaID')
            print(f"[VALIDATE_UMBRELLA_ASSOCIATION] Association UmbrellaID: {assoc_umbrella_id}")

            if assoc_umbrella_id != actual_umbrella_id:
                print(f"[VALIDATE_UMBRELLA_ASSOCIATION] UmbrellaID mismatch ({assoc_umbrella_id} != {actual_umbrella_id}), skipping")
                continue

            print("[VALIDATE_UMBRELLA_ASSOCIATION] UmbrellaID matches, checking date validity")

            # Check date validity
            valid_from = assoc.get('ValidFrom')
            print(f"[VALIDATE_UMBRELLA_ASSOCIATION] valid_from: {valid_from}")

            valid_to = assoc.get('ValidTo')
            print(f"[VALIDATE_UMBRELLA_ASSOCIATION] valid_to: {valid_to}")

            if valid_from and valid_from > period_start:
                print(f"[VALIDATE_UMBRELLA_ASSOCIATION] valid_from ({valid_from}) > period_start ({period_start}) - not valid yet, skipping")
                continue  # Not valid yet

            if valid_to and valid_to < period_end:
                print(f"[VALIDATE_UMBRELLA_ASSOCIATION] valid_to ({valid_to}) < period_end ({period_end}) - expired, skipping")
                continue  # Expired

            print("[VALIDATE_UMBRELLA_ASSOCIATION] Association is valid for period")
            valid_association = assoc
            print(f"[VALIDATE_UMBRELLA_ASSOCIATION] Set valid_association: {valid_association}")
            break

        if not valid_association:
            print("[VALIDATE_UMBRELLA_ASSOCIATION] No valid association found - returning error")
            error_dict = {
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
            print(f"[VALIDATE_UMBRELLA_ASSOCIATION] Returning: {error_dict}")
            return error_dict

        print("[VALIDATE_UMBRELLA_ASSOCIATION] Valid association found - returning success")
        result = {
            'valid': True,
            'association': valid_association
        }
        print(f"[VALIDATE_UMBRELLA_ASSOCIATION] Returning: {result}")
        return result

    def validate_vat(self, record: Dict) -> Dict:
        """
        Rule 4: Validate VAT is exactly 20%
        CRITICAL error if incorrect
        """
        print("[VALIDATE_VAT] Starting validate_vat()")

        amount_str = record['amount']
        print(f"[VALIDATE_VAT] Retrieved amount string: {amount_str}")

        amount = Decimal(str(amount_str))
        print(f"[VALIDATE_VAT] Converted amount to Decimal: {amount}")

        vat_amount_str = record['vat_amount']
        print(f"[VALIDATE_VAT] Retrieved vat_amount string: {vat_amount_str}")

        vat_amount = Decimal(str(vat_amount_str))
        print(f"[VALIDATE_VAT] Converted vat_amount to Decimal: {vat_amount}")

        vat_rate_value = self.params.get('VAT_RATE', 0.20)
        print(f"[VALIDATE_VAT] Retrieved VAT_RATE from params: {vat_rate_value}")

        vat_rate = Decimal(str(vat_rate_value))
        print(f"[VALIDATE_VAT] Converted vat_rate to Decimal: {vat_rate}")

        expected_vat = amount * vat_rate
        print(f"[VALIDATE_VAT] Calculated expected_vat: {amount} * {vat_rate} = {expected_vat}")

        # Allow 1p tolerance for rounding
        tolerance = Decimal('0.01')
        print(f"[VALIDATE_VAT] Set tolerance to: {tolerance}")

        difference = abs(vat_amount - expected_vat)
        print(f"[VALIDATE_VAT] Calculated difference: abs({vat_amount} - {expected_vat}) = {difference}")

        if difference > tolerance:
            print(f"[VALIDATE_VAT] Difference ({difference}) exceeds tolerance ({tolerance}) - returning error")
            error_dict = {
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
            print(f"[VALIDATE_VAT] Returning error: {error_dict}")
            return error_dict

        print("[VALIDATE_VAT] VAT validation passed - returning valid=True")
        return {'valid': True}

    def validate_overtime_rate(
        self,
        record: Dict,
        contractor_id: str,
        period_data: Dict,
        rates_cache: Dict = None
    ) -> Dict:
        """
        Rule 5: Validate overtime rate is 1.5x normal rate
        CRITICAL error if incorrect (with tolerance)

        Args:
            record: Pay record dict with overtime day_rate
            contractor_id: Contractor UUID
            period_data: Pay period information

        Returns:
            Dict with 'valid' bool and optional 'error' dict
        """
        print("[VALIDATE_OVERTIME_RATE] Starting validate_overtime_rate()")
        print(f"[VALIDATE_OVERTIME_RATE] contractor_id={contractor_id}, period_id={period_data.get('PeriodNumber')}")

        print("[VALIDATE_OVERTIME_RATE] About to execute: Extract overtime day_rate from record")
        day_rate_str = record['day_rate']
        print(f"[VALIDATE_OVERTIME_RATE] Retrieved day_rate string: {day_rate_str}")

        overtime_rate = Decimal(str(day_rate_str))
        print(f"[VALIDATE_OVERTIME_RATE] Converted overtime_rate to Decimal: {overtime_rate}")

        print("[VALIDATE_OVERTIME_RATE] About to execute: Get overtime multiplier from system params")
        multiplier_value = self.params.get('OVERTIME_MULTIPLIER', 1.5)
        print(f"[VALIDATE_OVERTIME_RATE] Retrieved OVERTIME_MULTIPLIER from params: {multiplier_value}")

        multiplier = Decimal(str(multiplier_value))
        print(f"[VALIDATE_OVERTIME_RATE] Converted multiplier to Decimal: {multiplier}")

        print("[VALIDATE_OVERTIME_RATE] About to execute: Get tolerance percent from system params")
        tolerance_percent_value = self.params.get('OVERTIME_TOLERANCE_PERCENT', 2.0)
        print(f"[VALIDATE_OVERTIME_RATE] Retrieved OVERTIME_TOLERANCE_PERCENT from params: {tolerance_percent_value}")

        tolerance_percent = Decimal(str(tolerance_percent_value))
        print(f"[VALIDATE_OVERTIME_RATE] Converted tolerance_percent to Decimal: {tolerance_percent}")

        # Check current batch first (rates_cache)
        normal_rate = None
        if rates_cache and contractor_id in rates_cache:
            normal_rate = rates_cache[contractor_id]
            print(f"[VALIDATE_OVERTIME_RATE] Found normal_rate in current batch: {normal_rate}")

        # If not in current batch, lookup contractor's normal rate from database
        if not normal_rate:
            print("[VALIDATE_OVERTIME_RATE] About to execute: Query contractor's normal rate for current period")
            period_id = str(period_data.get('PeriodNumber'))
            print(f"[VALIDATE_OVERTIME_RATE] period_id={period_id}")

            print(f"[VALIDATE_OVERTIME_RATE] About to execute: db.get_contractor_rate_in_period({contractor_id}, {period_id})")
            normal_rate = self.db.get_contractor_rate_in_period(contractor_id, period_id)
            print(f"[VALIDATE_OVERTIME_RATE] Retrieved normal_rate from current period: {normal_rate}")

        # If not found in current period, try to get from recent pay history
        if not normal_rate:
            print("[VALIDATE_OVERTIME_RATE] Normal rate not found in current period, checking recent pay history")
            print(f"[VALIDATE_OVERTIME_RATE] About to execute: db.get_contractor_pay_records({contractor_id}, limit=5)")
            recent_records = self.db.get_contractor_pay_records(contractor_id, limit=5)
            print(f"[VALIDATE_OVERTIME_RATE] Retrieved {len(recent_records)} recent records")

            if recent_records:
                print("[VALIDATE_OVERTIME_RATE] About to execute: Extract DayRate from most recent STANDARD record")
                normal_rate = recent_records[0].get('DayRate')
                print(f"[VALIDATE_OVERTIME_RATE] Extracted normal_rate from most recent record: {normal_rate}")
            else:
                print("[VALIDATE_OVERTIME_RATE] No recent pay records found for contractor")

        # If we still don't have normal rate, we cannot validate
        if not normal_rate:
            print("[VALIDATE_OVERTIME_RATE] Cannot validate overtime rate - no normal rate found in system")
            print("[VALIDATE_OVERTIME_RATE] Returning WARNING - unable to determine normal rate")
            warning_dict = {
                'valid': True,
                'warning': {
                    'warning_type': 'INVALID_OVERTIME_RATE',
                    'severity': 'WARNING',
                    'row_number': record.get('row_number'),
                    'employee_id': record.get('employee_id'),
                    'warning_message': f"WARNING: Cannot validate overtime rate £{overtime_rate:.2f} - no normal rate found for contractor in system",
                    'suggested_action': "Verify contractor has a STANDARD record in this period or previous periods, or verify overtime rate manually"
                }
            }
            print(f"[VALIDATE_OVERTIME_RATE] Returning warning: {warning_dict}")
            return warning_dict

        print("[VALIDATE_OVERTIME_RATE] About to execute: Convert normal_rate to Decimal for calculation")
        normal_rate = Decimal(str(normal_rate))
        print(f"[VALIDATE_OVERTIME_RATE] Converted normal_rate to Decimal: {normal_rate}")

        print("[VALIDATE_OVERTIME_RATE] About to execute: Calculate expected overtime rate")
        expected_overtime_rate = normal_rate * multiplier
        print(f"[VALIDATE_OVERTIME_RATE] Calculated expected_overtime_rate: {normal_rate} * {multiplier} = {expected_overtime_rate}")

        print("[VALIDATE_OVERTIME_RATE] About to execute: Calculate tolerance amount")
        tolerance_amount = expected_overtime_rate * (tolerance_percent / Decimal('100'))
        print(f"[VALIDATE_OVERTIME_RATE] Calculated tolerance_amount: {expected_overtime_rate} * ({tolerance_percent}/100) = {tolerance_amount}")

        print("[VALIDATE_OVERTIME_RATE] About to execute: Calculate min and max acceptable overtime rates")
        min_acceptable_rate = expected_overtime_rate - tolerance_amount
        max_acceptable_rate = expected_overtime_rate + tolerance_amount
        print(f"[VALIDATE_OVERTIME_RATE] Acceptable range: {min_acceptable_rate:.2f} to {max_acceptable_rate:.2f}")

        print("[VALIDATE_OVERTIME_RATE] About to execute: Calculate actual difference")
        difference = abs(overtime_rate - expected_overtime_rate)
        print(f"[VALIDATE_OVERTIME_RATE] Calculated difference: abs({overtime_rate} - {expected_overtime_rate}) = {difference}")

        print(f"[VALIDATE_OVERTIME_RATE] About to execute: Check if overtime_rate {overtime_rate} is within acceptable range")
        if overtime_rate < min_acceptable_rate or overtime_rate > max_acceptable_rate:
            print(f"[VALIDATE_OVERTIME_RATE] Overtime rate {overtime_rate} is OUTSIDE acceptable range - returning error")

            percent_diff = (difference / expected_overtime_rate) * Decimal('100')
            print(f"[VALIDATE_OVERTIME_RATE] Calculated percent_diff: {percent_diff:.2f}%")

            error_dict = {
                'valid': False,
                'error': {
                    'error_type': 'INVALID_OVERTIME_RATE',
                    'severity': 'CRITICAL',
                    'row_number': record.get('row_number'),
                    'employee_id': record.get('employee_id'),
                    'error_message': f"CRITICAL: Overtime rate £{overtime_rate:.2f} is incorrect. Normal rate: £{normal_rate:.2f}, Expected overtime (1.5x): £{expected_overtime_rate:.2f} (±{tolerance_percent}% tolerance)",
                    'suggested_fix': f"Correct overtime rate should be £{expected_overtime_rate:.2f} (actual difference: {percent_diff:.2f}%)"
                }
            }
            print(f"[VALIDATE_OVERTIME_RATE] Returning error: {error_dict}")
            return error_dict

        print(f"[VALIDATE_OVERTIME_RATE] Overtime rate {overtime_rate} is within acceptable range - validation passed")
        print("[VALIDATE_OVERTIME_RATE] Returning valid=True")
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

        Args:
            contractor_id: Contractor UUID
            new_rate: Current day rate from record
            period_data: Current pay period information

        Returns:
            Dict with optional 'warning' dict (None if no warning)
        """
        print("[CHECK_RATE_CHANGE] Starting check_rate_change()")
        print(f"[CHECK_RATE_CHANGE] contractor_id={contractor_id}, new_rate={new_rate}")

        print("[CHECK_RATE_CHANGE] About to execute: Get current period number")
        current_period_num = period_data.get('PeriodNumber')
        print(f"[CHECK_RATE_CHANGE] current_period_num={current_period_num}")

        print("[CHECK_RATE_CHANGE] About to execute: Check if current_period_num is valid")
        if not current_period_num or current_period_num <= 1:
            print(f"[CHECK_RATE_CHANGE] Period {current_period_num} is first period or invalid, no previous period to compare")
            print("[CHECK_RATE_CHANGE] Returning no warning (warning=None)")
            return {'warning': None}

        print("[CHECK_RATE_CHANGE] About to execute: Calculate previous period number")
        previous_period_num = current_period_num - 1
        print(f"[CHECK_RATE_CHANGE] previous_period_num={previous_period_num}")

        print("[CHECK_RATE_CHANGE] About to execute: Query contractor's rate from previous period")
        print(f"[CHECK_RATE_CHANGE] Calling db.get_contractor_rate_in_period({contractor_id}, {previous_period_num})")
        previous_rate = self.db.get_contractor_rate_in_period(contractor_id, str(previous_period_num))
        print(f"[CHECK_RATE_CHANGE] Retrieved previous_rate from period {previous_period_num}: {previous_rate}")

        print("[CHECK_RATE_CHANGE] About to execute: Check if previous_rate exists")
        if not previous_rate:
            print(f"[CHECK_RATE_CHANGE] No previous rate found for period {previous_period_num}")
            print("[CHECK_RATE_CHANGE] This might be contractor's first period, checking further back")

            print("[CHECK_RATE_CHANGE] About to execute: Query recent pay records as fallback")
            print(f"[CHECK_RATE_CHANGE] Calling db.get_contractor_pay_records({contractor_id}, limit=5)")
            recent_records = self.db.get_contractor_pay_records(contractor_id, limit=5)
            print(f"[CHECK_RATE_CHANGE] Retrieved {len(recent_records)} recent records")

            if recent_records:
                print("[CHECK_RATE_CHANGE] About to execute: Extract DayRate from most recent record")
                previous_rate = recent_records[0].get('DayRate')
                print(f"[CHECK_RATE_CHANGE] Extracted previous_rate from most recent record: {previous_rate}")
            else:
                print("[CHECK_RATE_CHANGE] No previous pay records found - this is contractor's first payment")
                print("[CHECK_RATE_CHANGE] Returning no warning (warning=None)")
                return {'warning': None}

        print("[CHECK_RATE_CHANGE] About to execute: Convert rates to Decimal for comparison")
        new_rate_decimal = Decimal(str(new_rate))
        print(f"[CHECK_RATE_CHANGE] new_rate_decimal={new_rate_decimal}")

        previous_rate_decimal = Decimal(str(previous_rate))
        print(f"[CHECK_RATE_CHANGE] previous_rate_decimal={previous_rate_decimal}")

        print("[CHECK_RATE_CHANGE] About to execute: Calculate rate change amount and percentage")
        rate_change_amount = new_rate_decimal - previous_rate_decimal
        print(f"[CHECK_RATE_CHANGE] rate_change_amount={new_rate_decimal} - {previous_rate_decimal} = {rate_change_amount}")

        print("[CHECK_RATE_CHANGE] About to execute: Check if previous_rate is zero to avoid division by zero")
        if previous_rate_decimal == 0:
            print("[CHECK_RATE_CHANGE] previous_rate is zero, cannot calculate percentage change")
            print("[CHECK_RATE_CHANGE] Returning no warning (warning=None)")
            return {'warning': None}

        print("[CHECK_RATE_CHANGE] About to execute: Calculate percentage change")
        rate_change_percent = (rate_change_amount / previous_rate_decimal) * Decimal('100')
        print(f"[CHECK_RATE_CHANGE] rate_change_percent=({rate_change_amount}/{previous_rate_decimal}) * 100 = {rate_change_percent:.2f}%")

        print("[CHECK_RATE_CHANGE] About to execute: Get alert threshold from system params")
        alert_threshold = Decimal(str(self.params.get('RATE_CHANGE_ALERT_PERCENT', 5.0)))
        print(f"[CHECK_RATE_CHANGE] alert_threshold={alert_threshold}%")

        print("[CHECK_RATE_CHANGE] About to execute: Check if absolute rate change exceeds threshold")
        abs_change_percent = abs(rate_change_percent)
        print(f"[CHECK_RATE_CHANGE] abs_change_percent={abs_change_percent:.2f}%")

        print(f"[CHECK_RATE_CHANGE] About to execute: Compare {abs_change_percent:.2f}% > {alert_threshold}%")
        if abs_change_percent > alert_threshold:
            print(f"[CHECK_RATE_CHANGE] Rate change {abs_change_percent:.2f}% EXCEEDS threshold {alert_threshold}% - generating warning")

            print("[CHECK_RATE_CHANGE] About to execute: Determine change direction (increase/decrease)")
            change_direction = "increased" if rate_change_amount > 0 else "decreased"
            print(f"[CHECK_RATE_CHANGE] change_direction={change_direction}")

            print("[CHECK_RATE_CHANGE] About to execute: Build warning message")
            warning_message = f"Day rate {change_direction} from £{previous_rate_decimal:.2f} to £{new_rate_decimal:.2f} ({rate_change_percent:+.2f}% change, threshold: {alert_threshold}%)"
            print(f"[CHECK_RATE_CHANGE] warning_message={warning_message}")

            warning_dict = {
                'warning': {
                    'warning_type': 'RATE_CHANGE',
                    'row_number': None,  # Will be set by caller if needed
                    'warning_message': warning_message,
                    'auto_resolved': False,
                    'resolution_notes': f"Previous rate: £{previous_rate_decimal:.2f} (period {previous_period_num}), New rate: £{new_rate_decimal:.2f} (period {current_period_num})"
                }
            }
            print(f"[CHECK_RATE_CHANGE] Returning warning: {warning_dict}")
            return warning_dict

        print(f"[CHECK_RATE_CHANGE] Rate change {abs_change_percent:.2f}% is within threshold {alert_threshold}% - no warning")
        print("[CHECK_RATE_CHANGE] Returning no warning (warning=None)")
        return {'warning': None}

    def validate_hours(self, record: Dict) -> Dict:
        """
        Rule 7: Validate hours are reasonable
        WARNING if unusual hours detected
        """
        print("[VALIDATE_HOURS] Starting validate_hours()")

        unit_days = record['unit_days']
        print(f"[VALIDATE_HOURS] Retrieved unit_days: {unit_days}")

        total_hours = record.get('total_hours', 0)
        print(f"[VALIDATE_HOURS] Retrieved total_hours: {total_hours}")

        # Check for unusual values
        max_days_threshold = 25
        print(f"[VALIDATE_HOURS] Maximum days threshold: {max_days_threshold}")

        if unit_days > max_days_threshold:
            print(f"[VALIDATE_HOURS] unit_days ({unit_days}) > maximum ({max_days_threshold}) - returning warning")
            warning_dict = {
                'warning': {
                    'warning_type': 'UNUSUAL_HOURS',
                    'row_number': record.get('row_number'),
                    'warning_message': f"Unusual number of days worked: {unit_days} days (>25 days in 4-week period)",
                    'auto_resolved': False
                }
            }
            print(f"[VALIDATE_HOURS] Returning warning: {warning_dict}")
            return warning_dict

        if unit_days < 0:
            print(f"[VALIDATE_HOURS] unit_days ({unit_days}) is negative - returning warning")
            warning_dict = {
                'warning': {
                    'warning_type': 'UNUSUAL_HOURS',
                    'row_number': record.get('row_number'),
                    'warning_message': f"Negative days worked: {unit_days} days",
                    'auto_resolved': False
                }
            }
            print(f"[VALIDATE_HOURS] Returning warning: {warning_dict}")
            return warning_dict

        print("[VALIDATE_HOURS] Hours validation passed - returning no warning (warning=None)")
        return {'warning': None}

print("[VALIDATORS_MODULE] validators.py module load complete")
