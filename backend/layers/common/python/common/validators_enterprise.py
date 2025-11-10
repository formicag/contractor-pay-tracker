"""
Enterprise-Grade Validation Engine
Implements comprehensive data quality checks for contractor pay records
Provides full audit trail for compliance and tracking
"""

from datetime import datetime
from decimal import Decimal, InvalidOperation
from typing import Dict, List, Optional, Tuple
import re


class ValidationCheck:
    """Represents a single validation check with full audit trail"""

    def __init__(self, check_id: str, check_name: str, check_type: str, severity: str = "CRITICAL"):
        self.check_id = check_id
        self.check_name = check_name
        self.check_type = check_type  # FILE, CONTRACTOR, RATE, HOURS, PERIOD, FINANCIAL, DATA_QUALITY
        self.severity = severity  # CRITICAL, WARNING, INFO
        self.passed = None
        self.expected = None
        self.actual = None
        self.message = None
        self.metadata = {}

    def pass_check(self, actual=None, expected=None, message=None, **metadata):
        """Mark check as passed"""
        self.passed = True
        self.actual = actual
        self.expected = expected
        self.message = message or f"{self.check_name}: PASSED"
        self.metadata = metadata
        return self

    def fail_check(self, actual=None, expected=None, message=None, **metadata):
        """Mark check as failed"""
        self.passed = False
        self.actual = actual
        self.expected = expected
        self.message = message or f"{self.check_name}: FAILED"
        self.metadata = metadata
        return self

    def to_dict(self):
        """Convert to dictionary for storage"""
        return {
            'check_id': self.check_id,
            'check_name': self.check_name,
            'check_type': self.check_type,
            'severity': self.severity,
            'passed': self.passed,
            'expected': str(self.expected) if self.expected is not None else None,
            'actual': str(self.actual) if self.actual is not None else None,
            'message': self.message,
            'metadata': self.metadata
        }


class EnterpriseValidationEngine:
    """
    Enterprise-grade validation engine with comprehensive data quality checks
    Records every check with expected vs actual for full audit trail
    """

    # System parameter defaults
    DEFAULT_PARAMS = {
        'VAT_RATE': Decimal('0.20'),
        'OVERTIME_MULTIPLIER': Decimal('1.5'),
        'MAX_DAY_RATE': Decimal('2000'),
        'MIN_DAY_RATE': Decimal('50'),
        'MAX_DAILY_HOURS': Decimal('24'),
        'MAX_WEEKLY_HOURS': Decimal('80'),
        'WARNING_WEEKLY_HOURS': Decimal('60'),
        'RATE_TOLERANCE_PERCENT': Decimal('10'),
        'VAT_TOLERANCE': Decimal('0.01')
    }

    def __init__(self, dynamodb_client, system_params: Dict = None):
        """Initialize validation engine"""
        self.db = dynamodb_client
        self.params = {**self.DEFAULT_PARAMS}
        if system_params:
            self.params.update(system_params)

        # Load contractors and umbrellas cache
        self.contractors_cache = {}
        self.umbrellas_cache = {}
        self._load_reference_data()

    def _load_reference_data(self):
        """Load contractor and umbrella reference data for validation"""
        try:
            # Load contractors
            contractors = self.db.table.query(
                IndexName='GSI1',
                KeyConditionExpression='GSI1PK = :pk',
                ExpressionAttributeValues={':pk': 'CONTRACTORS'}
            ).get('Items', [])

            for contractor in contractors:
                email = contractor.get('Email', '').lower()
                self.contractors_cache[email] = contractor

            # Load umbrellas
            umbrellas = self.db.table.query(
                IndexName='GSI1',
                KeyConditionExpression='GSI1PK = :pk',
                ExpressionAttributeValues={':pk': 'UMBRELLAS'}
            ).get('Items', [])

            for umbrella in umbrellas:
                code = umbrella.get('UmbrellaCode', '')
                self.umbrellas_cache[code] = umbrella

        except Exception as e:
            print(f"Error loading reference data: {e}")

    def validate_record(
        self,
        record: Dict,
        umbrella_id: str,
        period_data: Dict,
        file_name: str = None
    ) -> Tuple[bool, List[ValidationCheck]]:
        """
        Validate a single pay record with comprehensive checks

        Returns:
            Tuple of (is_valid, checks_list)
            - is_valid: False if any CRITICAL checks failed
            - checks_list: List of all validation checks performed
        """
        checks = []

        # ============ DATA TYPE & PRESENCE CHECKS ============
        checks.extend(self._validate_required_fields(record))
        checks.extend(self._validate_data_types(record))

        # ============ CONTRACTOR VALIDATION ============
        checks.extend(self._validate_contractor(record))
        checks.extend(self._validate_umbrella_association(record, umbrella_id))

        # ============ RATE VALIDATION ============
        checks.extend(self._validate_day_rate(record))
        checks.extend(self._validate_rate_range(record))
        checks.extend(self._validate_rate_vs_reference(record))
        checks.extend(self._validate_overtime_rate(record))
        checks.extend(self._validate_margin(record))

        # ============ HOURS VALIDATION ============
        checks.extend(self._validate_hours_non_negative(record))
        checks.extend(self._validate_daily_hours(record))
        checks.extend(self._validate_weekly_hours(record))
        checks.extend(self._validate_hours_total(record))

        # ============ PERIOD VALIDATION ============
        checks.extend(self._validate_period(period_data))

        # ============ FINANCIAL VALIDATION ============
        checks.extend(self._validate_vat(record))
        checks.extend(self._validate_gross_calculation(record))
        checks.extend(self._validate_net_calculation(record))

        # ============ DATA QUALITY CHECKS ============
        checks.extend(self._validate_no_obvious_errors(record))

        # Determine if record is valid (no critical failures)
        critical_failures = [c for c in checks if not c.passed and c.severity == 'CRITICAL']
        is_valid = len(critical_failures) == 0

        return is_valid, checks

    # ============ REQUIRED FIELDS ============

    def _validate_required_fields(self, record: Dict) -> List[ValidationCheck]:
        """Check all required fields are present"""
        required_fields = [
            'contractor_name', 'employee_id', 'day_rate', 'hours_worked',
            'gross_pay', 'vat_amount', 'net_pay', 'record_type'
        ]

        checks = []
        for field in required_fields:
            check = ValidationCheck(
                f"REQUIRED_{field.upper()}",
                f"Required Field: {field}",
                "DATA_QUALITY",
                "CRITICAL"
            )

            if field in record and record[field] is not None:
                check.pass_check(
                    actual="Present",
                    expected="Required",
                    message=f"Field '{field}' is present"
                )
            else:
                check.fail_check(
                    actual="Missing",
                    expected="Required",
                    message=f"Required field '{field}' is missing"
                )
            checks.append(check)

        return checks

    # ============ DATA TYPE VALIDATION ============

    def _validate_data_types(self, record: Dict) -> List[ValidationCheck]:
        """Validate data types of numeric fields"""
        numeric_fields = ['day_rate', 'hours_worked', 'gross_pay', 'vat_amount', 'net_pay', 'buy_rate', 'sell_rate']
        checks = []

        for field in numeric_fields:
            if field not in record:
                continue

            check = ValidationCheck(
                f"DATATYPE_{field.upper()}",
                f"Data Type: {field}",
                "DATA_QUALITY",
                "CRITICAL"
            )

            value = record[field]
            try:
                Decimal(str(value))
                check.pass_check(
                    actual=f"Numeric ({value})",
                    expected="Numeric",
                    message=f"Field '{field}' is valid numeric"
                )
            except (InvalidOperation, TypeError, ValueError):
                check.fail_check(
                    actual=f"Invalid ({value})",
                    expected="Numeric",
                    message=f"Field '{field}' must be numeric, got: {value}"
                )
            checks.append(check)

        return checks

    # ============ CONTRACTOR VALIDATION ============

    def _validate_contractor(self, record: Dict) -> List[ValidationCheck]:
        """Validate contractor exists in system"""
        checks = []
        contractor_name = record.get('contractor_name', '')
        employee_id = record.get('employee_id', '')

        # Check contractor exists
        check = ValidationCheck(
            "CONTRACTOR_EXISTS",
            "Contractor Exists in System",
            "CONTRACTOR",
            "CRITICAL"
        )

        # Try to find contractor by email or name
        contractor_email = record.get('email', '').lower()
        contractor_found = None

        if contractor_email and contractor_email in self.contractors_cache:
            contractor_found = self.contractors_cache[contractor_email]

        if contractor_found:
            check.pass_check(
                actual=contractor_name,
                expected="Valid Contractor",
                message=f"Contractor '{contractor_name}' found in system"
            )
        else:
            check.fail_check(
                actual=contractor_name,
                expected="Valid Contractor",
                message=f"Contractor '{contractor_name}' not found in system"
            )
        checks.append(check)

        # Check employee ID matches if contractor found
        if contractor_found:
            check_emp = ValidationCheck(
                "EMPLOYEE_ID_MATCH",
                "Employee ID Matches Contractor",
                "CONTRACTOR",
                "WARNING"
            )

            expected_emp_id = contractor_found.get('EmployeeID', '')
            if str(employee_id) == str(expected_emp_id):
                check_emp.pass_check(
                    actual=employee_id,
                    expected=expected_emp_id,
                    message=f"Employee ID matches: {employee_id}"
                )
            else:
                check_emp.fail_check(
                    actual=employee_id,
                    expected=expected_emp_id,
                    message=f"Employee ID mismatch: got {employee_id}, expected {expected_emp_id}"
                )
            checks.append(check_emp)

        return checks

    def _validate_umbrella_association(self, record: Dict, umbrella_id: str) -> List[ValidationCheck]:
        """Validate umbrella company is valid"""
        checks = []

        check = ValidationCheck(
            "UMBRELLA_VALID",
            "Umbrella Company Valid",
            "CONTRACTOR",
            "CRITICAL"
        )

        if umbrella_id in self.umbrellas_cache:
            umbrella_name = self.umbrellas_cache[umbrella_id].get('Name', umbrella_id)
            check.pass_check(
                actual=umbrella_id,
                expected="Valid Umbrella",
                message=f"Umbrella '{umbrella_name}' is valid"
            )
        else:
            check.fail_check(
                actual=umbrella_id,
                expected="Valid Umbrella",
                message=f"Umbrella '{umbrella_id}' not found in system"
            )
        checks.append(check)

        return checks

    # ============ RATE VALIDATION ============

    def _validate_day_rate(self, record: Dict) -> List[ValidationCheck]:
        """Validate day rate is positive"""
        checks = []
        day_rate = record.get('day_rate')

        check = ValidationCheck(
            "RATE_POSITIVE",
            "Day Rate Must Be Positive",
            "RATE",
            "CRITICAL"
        )

        try:
            rate = Decimal(str(day_rate))
            if rate > 0:
                check.pass_check(
                    actual=f"£{rate}",
                    expected="> £0",
                    message=f"Day rate is positive: £{rate}"
                )
            else:
                check.fail_check(
                    actual=f"£{rate}",
                    expected="> £0",
                    message=f"Day rate must be positive, got: £{rate}"
                )
        except:
            check.fail_check(
                actual=day_rate,
                expected="> £0",
                message=f"Day rate is invalid: {day_rate}"
            )
        checks.append(check)

        return checks

    def _validate_rate_range(self, record: Dict) -> List[ValidationCheck]:
        """Validate rate is in reasonable range (not yearly rate)"""
        checks = []
        day_rate = record.get('day_rate')

        check = ValidationCheck(
            "RATE_RANGE",
            "Day Rate in Valid Range",
            "RATE",
            "CRITICAL"
        )

        try:
            rate = Decimal(str(day_rate))
            min_rate = self.params['MIN_DAY_RATE']
            max_rate = self.params['MAX_DAY_RATE']

            if min_rate <= rate <= max_rate:
                check.pass_check(
                    actual=f"£{rate}",
                    expected=f"£{min_rate} - £{max_rate}",
                    message=f"Day rate in valid range: £{rate}"
                )
            else:
                check.fail_check(
                    actual=f"£{rate}",
                    expected=f"£{min_rate} - £{max_rate}",
                    message=f"Day rate outside valid range: £{rate} (looks like yearly rate?)"
                )
        except:
            check.fail_check(
                actual=day_rate,
                expected=f"£{self.params['MIN_DAY_RATE']} - £{self.params['MAX_DAY_RATE']}",
                message=f"Day rate is invalid: {day_rate}"
            )
        checks.append(check)

        return checks

    def _validate_rate_vs_reference(self, record: Dict) -> List[ValidationCheck]:
        """Validate rate matches contractor's registered rate"""
        checks = []
        day_rate = record.get('day_rate')
        contractor_email = record.get('email', '').lower()

        check = ValidationCheck(
            "RATE_MATCHES_REFERENCE",
            "Day Rate Matches Contractor Reference",
            "RATE",
            "WARNING"
        )

        if contractor_email in self.contractors_cache:
            contractor = self.contractors_cache[contractor_email]
            expected_rate = contractor.get('DayRate')

            if expected_rate:
                try:
                    actual_rate = Decimal(str(day_rate))
                    expected_rate = Decimal(str(expected_rate))
                    tolerance = expected_rate * self.params['RATE_TOLERANCE_PERCENT'] / 100

                    if abs(actual_rate - expected_rate) <= tolerance:
                        check.pass_check(
                            actual=f"£{actual_rate}",
                            expected=f"£{expected_rate} (±{self.params['RATE_TOLERANCE_PERCENT']}%)",
                            message=f"Day rate matches reference: £{actual_rate}"
                        )
                    else:
                        check.fail_check(
                            actual=f"£{actual_rate}",
                            expected=f"£{expected_rate} (±{self.params['RATE_TOLERANCE_PERCENT']}%)",
                            message=f"Day rate differs from reference: £{actual_rate} vs £{expected_rate}"
                        )
                except:
                    check.fail_check(
                        actual=day_rate,
                        expected=expected_rate,
                        message="Rate comparison failed"
                    )
            else:
                check.pass_check(
                    actual=day_rate,
                    expected="No reference rate",
                    message="No reference rate to compare"
                )
        else:
            check.pass_check(
                actual=day_rate,
                expected="Contractor not found",
                message="Cannot compare - contractor not in system"
            )
        checks.append(check)

        return checks

    def _validate_overtime_rate(self, record: Dict) -> List[ValidationCheck]:
        """Validate overtime rate = standard rate × 1.5"""
        checks = []

        if record.get('record_type') != 'OVERTIME':
            return checks

        check = ValidationCheck(
            "OVERTIME_RATE_MULTIPLIER",
            "Overtime Rate = Standard Rate × 1.5",
            "RATE",
            "CRITICAL"
        )

        buy_rate = record.get('buy_rate')
        contractor_email = record.get('email', '').lower()

        if contractor_email in self.contractors_cache:
            contractor = self.contractors_cache[contractor_email]
            standard_buy_rate = contractor.get('BuyRate')

            if standard_buy_rate and buy_rate:
                try:
                    actual_buy_rate = Decimal(str(buy_rate))
                    expected_buy_rate = Decimal(str(standard_buy_rate)) * self.params['OVERTIME_MULTIPLIER']
                    tolerance = expected_buy_rate * Decimal('0.01')  # 1% tolerance

                    if abs(actual_buy_rate - expected_buy_rate) <= tolerance:
                        check.pass_check(
                            actual=f"£{actual_buy_rate}",
                            expected=f"£{expected_buy_rate} (£{standard_buy_rate} × 1.5)",
                            message=f"Overtime rate correct: £{actual_buy_rate}"
                        )
                    else:
                        check.fail_check(
                            actual=f"£{actual_buy_rate}",
                            expected=f"£{expected_buy_rate} (£{standard_buy_rate} × 1.5)",
                            message=f"Overtime rate incorrect: £{actual_buy_rate}, expected £{expected_buy_rate}"
                        )
                except:
                    check.fail_check(
                        actual=buy_rate,
                        expected=f"{standard_buy_rate} × 1.5",
                        message="Overtime rate calculation failed"
                    )
        checks.append(check)

        return checks

    def _validate_margin(self, record: Dict) -> List[ValidationCheck]:
        """Validate sell rate > buy rate (positive margin)"""
        checks = []
        sell_rate = record.get('sell_rate')
        buy_rate = record.get('buy_rate')

        if not sell_rate or not buy_rate:
            return checks

        check = ValidationCheck(
            "POSITIVE_MARGIN",
            "Sell Rate > Buy Rate",
            "RATE",
            "CRITICAL"
        )

        try:
            sell = Decimal(str(sell_rate))
            buy = Decimal(str(buy_rate))

            if sell > buy:
                margin = sell - buy
                margin_pct = (margin / sell * 100).quantize(Decimal('0.01'))
                check.pass_check(
                    actual=f"Margin: £{margin} ({margin_pct}%)",
                    expected="Sell > Buy",
                    message=f"Positive margin: £{margin} ({margin_pct}%)"
                )
            else:
                check.fail_check(
                    actual=f"Sell: £{sell}, Buy: £{buy}",
                    expected="Sell > Buy",
                    message=f"Negative margin: sell £{sell} <= buy £{buy}"
                )
        except:
            check.fail_check(
                actual=f"Sell: {sell_rate}, Buy: {buy_rate}",
                expected="Sell > Buy",
                message="Margin calculation failed"
            )
        checks.append(check)

        return checks

    # ============ HOURS VALIDATION ============

    def _validate_hours_non_negative(self, record: Dict) -> List[ValidationCheck]:
        """Validate hours cannot be negative"""
        checks = []
        hours = record.get('hours_worked')

        check = ValidationCheck(
            "HOURS_NON_NEGATIVE",
            "Hours Cannot Be Negative",
            "HOURS",
            "CRITICAL"
        )

        try:
            hrs = Decimal(str(hours))
            if hrs >= 0:
                check.pass_check(
                    actual=f"{hrs}h",
                    expected=">= 0h",
                    message=f"Hours are non-negative: {hrs}h"
                )
            else:
                check.fail_check(
                    actual=f"{hrs}h",
                    expected=">= 0h",
                    message=f"Hours cannot be negative: {hrs}h"
                )
        except:
            check.fail_check(
                actual=hours,
                expected=">= 0h",
                message=f"Hours value invalid: {hours}"
            )
        checks.append(check)

        return checks

    def _validate_daily_hours(self, record: Dict) -> List[ValidationCheck]:
        """Validate daily hours <= 24"""
        checks = []

        # Check individual day hours if present
        days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']

        for day in days:
            day_hours = record.get(f'{day}_hours')
            if day_hours is None:
                continue

            check = ValidationCheck(
                f"DAILY_HOURS_{day.upper()}",
                f"{day.title()} Hours <= 24",
                "HOURS",
                "CRITICAL"
            )

            try:
                hrs = Decimal(str(day_hours))
                max_hrs = self.params['MAX_DAILY_HOURS']

                if 0 <= hrs <= max_hrs:
                    check.pass_check(
                        actual=f"{hrs}h",
                        expected=f"0-{max_hrs}h",
                        message=f"{day.title()}: {hrs}h valid"
                    )
                else:
                    check.fail_check(
                        actual=f"{hrs}h",
                        expected=f"0-{max_hrs}h",
                        message=f"{day.title()}: {hrs}h exceeds maximum"
                    )
            except:
                check.fail_check(
                    actual=day_hours,
                    expected=f"0-{max_hrs}h",
                    message=f"{day.title()}: invalid hours value"
                )
            checks.append(check)

        return checks

    def _validate_weekly_hours(self, record: Dict) -> List[ValidationCheck]:
        """Validate weekly hours reasonable"""
        checks = []
        hours = record.get('hours_worked')

        if not hours:
            return checks

        # Critical check: <= 80 hours
        check_max = ValidationCheck(
            "WEEKLY_HOURS_MAX",
            "Weekly Hours <= 80",
            "HOURS",
            "CRITICAL"
        )

        try:
            hrs = Decimal(str(hours))
            max_hrs = self.params['MAX_WEEKLY_HOURS']

            if hrs <= max_hrs:
                check_max.pass_check(
                    actual=f"{hrs}h",
                    expected=f"<= {max_hrs}h",
                    message=f"Weekly hours within limit: {hrs}h"
                )
            else:
                check_max.fail_check(
                    actual=f"{hrs}h",
                    expected=f"<= {max_hrs}h",
                    message=f"Weekly hours exceed maximum: {hrs}h"
                )
        except:
            check_max.fail_check(
                actual=hours,
                expected=f"<= {max_hrs}h",
                message="Weekly hours invalid"
            )
        checks.append(check_max)

        # Warning check: > 60 hours
        check_warn = ValidationCheck(
            "WEEKLY_HOURS_WARNING",
            "Weekly Hours <= 60 (Recommended)",
            "HOURS",
            "WARNING"
        )

        try:
            hrs = Decimal(str(hours))
            warn_hrs = self.params['WARNING_WEEKLY_HOURS']

            if hrs <= warn_hrs:
                check_warn.pass_check(
                    actual=f"{hrs}h",
                    expected=f"<= {warn_hrs}h",
                    message=f"Weekly hours reasonable: {hrs}h"
                )
            else:
                check_warn.fail_check(
                    actual=f"{hrs}h",
                    expected=f"<= {warn_hrs}h",
                    message=f"Weekly hours high: {hrs}h (verify with contractor)"
                )
        except:
            pass
        checks.append(check_warn)

        return checks

    def _validate_hours_total(self, record: Dict) -> List[ValidationCheck]:
        """Validate total hours = sum of daily hours"""
        checks = []

        total_hours = record.get('hours_worked')
        if not total_hours:
            return checks

        # Calculate sum of daily hours
        days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
        daily_sum = Decimal('0')
        has_daily_breakdown = False

        for day in days:
            day_hours = record.get(f'{day}_hours')
            if day_hours is not None:
                has_daily_breakdown = True
                try:
                    daily_sum += Decimal(str(day_hours))
                except:
                    pass

        if not has_daily_breakdown:
            return checks

        check = ValidationCheck(
            "HOURS_SUM_MATCHES",
            "Total Hours = Sum of Daily Hours",
            "HOURS",
            "CRITICAL"
        )

        try:
            total = Decimal(str(total_hours))
            tolerance = Decimal('0.01')

            if abs(total - daily_sum) <= tolerance:
                check.pass_check(
                    actual=f"{total}h",
                    expected=f"{daily_sum}h",
                    message=f"Hours total matches daily sum: {total}h"
                )
            else:
                check.fail_check(
                    actual=f"{total}h",
                    expected=f"{daily_sum}h",
                    message=f"Hours mismatch: total {total}h != daily sum {daily_sum}h"
                )
        except:
            check.fail_check(
                actual=total_hours,
                expected=f"{daily_sum}h",
                message="Hours calculation failed"
            )
        checks.append(check)

        return checks

    # ============ PERIOD VALIDATION ============

    def _validate_period(self, period_data: Dict) -> List[ValidationCheck]:
        """Validate period is valid and not in future"""
        checks = []

        # Check period name format
        period_name = period_data.get('period_name', '')
        check_format = ValidationCheck(
            "PERIOD_FORMAT",
            "Period Name Format Valid",
            "PERIOD",
            "WARNING"
        )

        # Expected format: "Month Year" or "Month YYYY"
        if re.match(r'^[A-Za-z]+ \d{4}$', period_name):
            check_format.pass_check(
                actual=period_name,
                expected="Month YYYY",
                message=f"Period format valid: {period_name}"
            )
        else:
            check_format.fail_check(
                actual=period_name,
                expected="Month YYYY",
                message=f"Period format unusual: {period_name}"
            )
        checks.append(check_format)

        # Check period not in future
        check_future = ValidationCheck(
            "PERIOD_NOT_FUTURE",
            "Period Not in Future",
            "PERIOD",
            "CRITICAL"
        )

        period_end = period_data.get('end_date')
        if period_end:
            try:
                if isinstance(period_end, str):
                    end_dt = datetime.fromisoformat(period_end.replace('Z', '+00:00'))
                else:
                    end_dt = period_end

                now = datetime.now(end_dt.tzinfo)

                if end_dt <= now:
                    check_future.pass_check(
                        actual=period_end,
                        expected=f"<= {now.date()}",
                        message=f"Period not in future: {period_end}"
                    )
                else:
                    check_future.fail_check(
                        actual=period_end,
                        expected=f"<= {now.date()}",
                        message=f"Period is in future: {period_end}"
                    )
            except:
                check_future.fail_check(
                    actual=period_end,
                    expected="Valid past date",
                    message="Period date validation failed"
                )
        checks.append(check_future)

        return checks

    # ============ FINANCIAL VALIDATION ============

    def _validate_vat(self, record: Dict) -> List[ValidationCheck]:
        """Validate VAT calculation (20%)"""
        checks = []

        gross_pay = record.get('gross_pay')
        vat_amount = record.get('vat_amount')

        if not gross_pay or not vat_amount:
            return checks

        check = ValidationCheck(
            "VAT_CALCULATION",
            "VAT = Gross × 20%",
            "FINANCIAL",
            "CRITICAL"
        )

        try:
            gross = Decimal(str(gross_pay))
            vat = Decimal(str(vat_amount))
            expected_vat = gross * self.params['VAT_RATE']
            tolerance = self.params['VAT_TOLERANCE']

            if abs(vat - expected_vat) <= tolerance:
                check.pass_check(
                    actual=f"£{vat}",
                    expected=f"£{expected_vat} (£{gross} × 20%)",
                    message=f"VAT correct: £{vat}"
                )
            else:
                check.fail_check(
                    actual=f"£{vat}",
                    expected=f"£{expected_vat} (£{gross} × 20%)",
                    message=f"VAT incorrect: £{vat}, expected £{expected_vat}"
                )
        except:
            check.fail_check(
                actual=vat_amount,
                expected=f"{gross_pay} × 20%",
                message="VAT calculation failed"
            )
        checks.append(check)

        return checks

    def _validate_gross_calculation(self, record: Dict) -> List[ValidationCheck]:
        """Validate gross = rate × hours"""
        checks = []

        day_rate = record.get('day_rate')
        hours = record.get('hours_worked')
        gross = record.get('gross_pay')

        if not all([day_rate, hours, gross]):
            return checks

        check = ValidationCheck(
            "GROSS_CALCULATION",
            "Gross = Rate × Hours",
            "FINANCIAL",
            "CRITICAL"
        )

        try:
            rate = Decimal(str(day_rate))
            hrs = Decimal(str(hours))
            actual_gross = Decimal(str(gross))
            expected_gross = rate * hrs / Decimal('7.5')  # Assuming 7.5 hours = 1 day
            tolerance = Decimal('0.01')

            if abs(actual_gross - expected_gross) <= tolerance:
                check.pass_check(
                    actual=f"£{actual_gross}",
                    expected=f"£{expected_gross} (£{rate} × {hrs}h)",
                    message=f"Gross pay correct: £{actual_gross}"
                )
            else:
                check.fail_check(
                    actual=f"£{actual_gross}",
                    expected=f"£{expected_gross} (£{rate} × {hrs}h)",
                    message=f"Gross pay incorrect: £{actual_gross}, expected £{expected_gross}"
                )
        except:
            check.fail_check(
                actual=gross,
                expected=f"{day_rate} × {hours}",
                message="Gross calculation failed"
            )
        checks.append(check)

        return checks

    def _validate_net_calculation(self, record: Dict) -> List[ValidationCheck]:
        """Validate net = gross + VAT"""
        checks = []

        gross = record.get('gross_pay')
        vat = record.get('vat_amount')
        net = record.get('net_pay')

        if not all([gross, vat, net]):
            return checks

        check = ValidationCheck(
            "NET_CALCULATION",
            "Net = Gross + VAT",
            "FINANCIAL",
            "CRITICAL"
        )

        try:
            gross_amt = Decimal(str(gross))
            vat_amt = Decimal(str(vat))
            actual_net = Decimal(str(net))
            expected_net = gross_amt + vat_amt
            tolerance = Decimal('0.01')

            if abs(actual_net - expected_net) <= tolerance:
                check.pass_check(
                    actual=f"£{actual_net}",
                    expected=f"£{expected_net} (£{gross_amt} + £{vat_amt})",
                    message=f"Net pay correct: £{actual_net}"
                )
            else:
                check.fail_check(
                    actual=f"£{actual_net}",
                    expected=f"£{expected_net} (£{gross_amt} + £{vat_amt})",
                    message=f"Net pay incorrect: £{actual_net}, expected £{expected_net}"
                )
        except:
            check.fail_check(
                actual=net,
                expected=f"{gross} + {vat}",
                message="Net calculation failed"
            )
        checks.append(check)

        return checks

    # ============ DATA QUALITY ============

    def _validate_no_obvious_errors(self, record: Dict) -> List[ValidationCheck]:
        """Check for obvious data entry errors"""
        checks = []

        # Check for suspiciously round numbers that might be placeholders
        day_rate = record.get('day_rate')
        if day_rate:
            check = ValidationCheck(
                "RATE_NOT_PLACEHOLDER",
                "Rate Not Obviously Wrong",
                "DATA_QUALITY",
                "WARNING"
            )

            try:
                rate = Decimal(str(day_rate))
                suspicious_values = [Decimal('99999'), Decimal('0'), Decimal('1'), Decimal('9999')]

                if rate in suspicious_values:
                    check.fail_check(
                        actual=f"£{rate}",
                        expected="Realistic rate",
                        message=f"Rate looks like placeholder: £{rate}"
                    )
                else:
                    check.pass_check(
                        actual=f"£{rate}",
                        expected="Realistic rate",
                        message=f"Rate looks valid: £{rate}"
                    )
            except:
                pass
            checks.append(check)

        return checks
