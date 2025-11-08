"""
Excel file parser for contractor pay files
Handles the specific format from umbrella companies
"""

import re
from datetime import datetime
from decimal import Decimal
from typing import Dict, List, Optional

import openpyxl
from openpyxl.worksheet.worksheet import Worksheet


class PayFileParser:
    """Parse contractor pay Excel files"""

    def __init__(self, file_path: str):
        self.file_path = file_path
        self.workbook = openpyxl.load_workbook(file_path, data_only=True)
        self.worksheet = self.workbook.active

    def extract_metadata(self) -> Dict:
        """Extract metadata from filename and file content"""
        filename = self.file_path.split('/')[-1]

        # Try to extract umbrella company from filename
        umbrella_patterns = {
            'NASA': r'NASA',
            'PAYSTREAM': r'PAYSTREAM',
            'PARASOL': r'Parasol',
            'CLARITY': r'Clarity',
            'GIANT': r'GIANT',
            'WORKWELL': r'WORKWELL'
        }

        umbrella_code = None
        for code, pattern in umbrella_patterns.items():
            if re.search(pattern, filename, re.IGNORECASE):
                umbrella_code = code
                break

        # Try to extract date from filename (DDMMYYYY format)
        date_match = re.search(r'(\d{8})', filename)
        submission_date = None
        if date_match:
            date_str = date_match.group(1)
            submission_date = datetime.strptime(date_str, '%d%m%Y').strftime('%Y-%m-%d')

        return {
            'filename': filename,
            'umbrella_code': umbrella_code,
            'submission_date': submission_date
        }

    def find_header_row(self) -> int:
        """Find the row containing column headers"""
        # Common header variations
        header_indicators = ['employee id', 'surname', 'forename', 'unit', 'rate', 'amount']

        for row_idx, row in enumerate(self.worksheet.iter_rows(min_row=1, max_row=20), start=1):
            row_text = ' '.join([str(cell.value or '').lower() for cell in row])

            # Check if this row contains most header indicators
            matches = sum(1 for indicator in header_indicators if indicator in row_text)
            if matches >= 4:
                return row_idx

        return 1  # Default to first row

    def parse_records(self) -> List[Dict]:
        """Parse all pay records from the Excel file"""
        header_row = self.find_header_row()

        # Get column mapping
        column_map = self._get_column_mapping(header_row)

        records = []
        row_number = 0

        for row_idx, row in enumerate(self.worksheet.iter_rows(min_row=header_row + 1), start=header_row + 1):
            row_number += 1

            # Skip empty rows
            if all(cell.value is None or str(cell.value).strip() == '' for cell in row):
                continue

            # Check if this is a duplicate header row
            first_cell = str(row[0].value or '').lower()
            if 'employee' in first_cell or 'surname' in first_cell:
                continue

            try:
                record = self._parse_row(row, column_map, row_number, row_idx)
                if record:
                    records.append(record)
            except Exception as e:
                # Log parsing error but continue
                print(f"Error parsing row {row_idx}: {e}")
                continue

        return records

    def _get_column_mapping(self, header_row: int) -> Dict[str, int]:
        """Map column names to their indices"""
        headers = []
        for cell in self.worksheet[header_row]:
            header_text = str(cell.value or '').lower().strip()
            headers.append(header_text)

        # Map common variations to standard names
        column_map = {}

        for idx, header in enumerate(headers):
            if 'employee' in header and 'id' in header:
                column_map['employee_id'] = idx
            elif 'surname' in header or 'last' in header:
                column_map['surname'] = idx
            elif 'forename' in header or 'first' in header:
                column_map['forename'] = idx
            elif header == 'unit' or 'days' in header:
                column_map['unit'] = idx
            elif header == 'rate' and 'day' in header:
                column_map['rate'] = idx
            elif header == 'per':
                column_map['per'] = idx
            elif header == 'amount' and 'vat' not in header:
                column_map['amount'] = idx
            elif 'vat' in header and 'amount' not in header:
                column_map['vat'] = idx
            elif 'total' in header and 'hours' in header:
                column_map['total_hours'] = idx
            elif 'company' in header:
                column_map['company'] = idx
            elif 'notes' in header or 'description' in header:
                column_map['notes'] = idx

        return column_map

    def _parse_row(self, row, column_map: Dict[str, int], row_number: int, row_idx: int) -> Optional[Dict]:
        """Parse a single row into a pay record"""

        def get_cell_value(col_name: str, default=None):
            """Safely get cell value"""
            if col_name not in column_map:
                return default
            idx = column_map[col_name]
            if idx >= len(row):
                return default
            value = row[idx].value
            return value if value is not None else default

        # Get basic fields
        employee_id = str(get_cell_value('employee_id', '')).strip()
        surname = str(get_cell_value('surname', '')).strip()
        forename = str(get_cell_value('forename', '')).strip()

        # Skip rows without essential data
        if not surname or not forename:
            return None

        # Get numeric fields
        unit_days = self._parse_decimal(get_cell_value('unit', 0))
        day_rate = self._parse_decimal(get_cell_value('rate', 0))
        amount = self._parse_decimal(get_cell_value('amount', 0))
        vat_amount = self._parse_decimal(get_cell_value('vat', 0))
        total_hours = self._parse_decimal(get_cell_value('total_hours', 0))

        # Get other fields
        notes = str(get_cell_value('notes', '')).strip()
        company = str(get_cell_value('company', '')).strip()

        # Calculate gross amount (amount + vat)
        gross_amount = amount + vat_amount

        # Determine record type
        record_type = 'STANDARD'
        if 'overtime' in notes.lower():
            record_type = 'OVERTIME'
        elif 'expense' in notes.lower():
            record_type = 'EXPENSE'

        return {
            'row_number': row_number,
            'row_idx': row_idx,
            'employee_id': employee_id,
            'surname': surname,
            'forename': forename,
            'unit_days': float(unit_days),
            'day_rate': float(day_rate),
            'amount': float(amount),
            'vat_amount': float(vat_amount),
            'gross_amount': float(gross_amount),
            'total_hours': float(total_hours) if total_hours else float(unit_days * Decimal('7.5')),
            'record_type': record_type,
            'notes': notes,
            'company': company
        }

    @staticmethod
    def _parse_decimal(value) -> Decimal:
        """Parse value to Decimal, handling various formats"""
        if value is None:
            return Decimal('0')

        if isinstance(value, (int, float)):
            return Decimal(str(value))

        # Handle string values
        str_value = str(value).strip().replace(',', '').replace('£', '')
        if not str_value or str_value == '-':
            return Decimal('0')

        try:
            return Decimal(str_value)
        except:
            return Decimal('0')

    def close(self):
        """Close the workbook"""
        self.workbook.close()
