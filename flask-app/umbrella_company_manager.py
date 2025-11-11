"""
Umbrella Company Manager - Password-Protected Reference Data Management

This module provides secure access to umbrella company data with password protection.
All modifications to umbrella companies require password verification.
"""

import boto3
import bcrypt
import os
from typing import Dict, List, Optional
from datetime import datetime, timezone
from botocore.exceptions import ClientError

# AWS Configuration
AWS_REGION = os.getenv('AWS_REGION', 'eu-west-1')
TABLE_NAME = os.getenv('PAYFILES_TABLE_NAME', 'contractor-pay-files-metadata')

# Unlock password (must type "luca" to modify any umbrella company data)
UNLOCK_PASSWORD = 'luca'


class UmbrellaCompanyManager:
    """Manager for password-protected umbrella company reference data."""

    def __init__(self):
        self.dynamodb = boto3.resource('dynamodb', region_name=AWS_REGION)
        self.table = self.dynamodb.Table(TABLE_NAME)

    def verify_password(self, password: str, password_hash: str) -> bool:
        """Verify password against bcrypt hash."""
        try:
            return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))
        except Exception:
            return False

    def get_all_umbrella_companies(self) -> List[Dict]:
        """Get all umbrella companies from database."""
        try:
            response = self.table.scan(
                FilterExpression='begins_with(file_id, :prefix)',
                ExpressionAttributeValues={
                    ':prefix': 'UMBRELLA#'
                }
            )
            return response.get('Items', [])
        except Exception as e:
            print(f"Error fetching umbrella companies: {str(e)}")
            return []

    def get_umbrella_company(self, company_id: str) -> Optional[Dict]:
        """Get a specific umbrella company by ID."""
        try:
            response = self.table.get_item(
                Key={'file_id': f'UMBRELLA#{company_id}'}
            )
            return response.get('Item')
        except Exception as e:
            print(f"Error fetching umbrella company {company_id}: {str(e)}")
            return None

    def update_umbrella_company(
        self,
        company_id: str,
        unlock_password: str,
        updates: Dict,
        modified_by: str = 'api'
    ) -> Dict:
        """
        Update umbrella company data (requires password).

        Args:
            company_id: Company identifier
            unlock_password: Password to unlock (must be "luca")
            updates: Dictionary of fields to update
            modified_by: Who is making the modification

        Returns:
            Dict with success status and message

        Raises:
            ValueError: If password is incorrect or company is locked
        """

        # Get current company data
        company = self.get_umbrella_company(company_id)

        if not company:
            return {
                'success': False,
                'error': f'Umbrella company {company_id} not found'
            }

        # Check if locked
        if company.get('locked', False):
            # Verify password
            password_hash = company.get('password_hash', '')

            if not self.verify_password(unlock_password, password_hash):
                return {
                    'success': False,
                    'error': 'Invalid unlock password. This data is locked.'
                }

        # Password verified or not locked - proceed with update
        try:
            # Build update expression
            update_expr = 'SET '
            expr_attr_values = {}
            expr_attr_names = {}

            for key, value in updates.items():
                # Don't allow updating lock status or password hash
                if key in ['locked', 'password_hash', 'file_id', 'company_id']:
                    continue

                safe_key = f'#{key}'
                value_key = f':{key}'

                update_expr += f'{safe_key} = {value_key}, '
                expr_attr_names[safe_key] = key
                expr_attr_values[value_key] = value

            # Add modification metadata
            update_expr += '#modified_at = :modified_at, #modified_by = :modified_by, #version = #version + :inc'

            expr_attr_names['#modified_at'] = 'modified_at'
            expr_attr_names['#modified_by'] = 'modified_by'
            expr_attr_names['#version'] = 'version'

            expr_attr_values[':modified_at'] = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
            expr_attr_values[':modified_by'] = modified_by
            expr_attr_values[':inc'] = 1

            # Execute update
            self.table.update_item(
                Key={'file_id': f'UMBRELLA#{company_id}'},
                UpdateExpression=update_expr,
                ExpressionAttributeNames=expr_attr_names,
                ExpressionAttributeValues=expr_attr_values
            )

            return {
                'success': True,
                'message': f'Umbrella company {company_id} updated successfully'
            }

        except Exception as e:
            return {
                'success': False,
                'error': f'Failed to update: {str(e)}'
            }

    def delete_umbrella_company(
        self,
        company_id: str,
        unlock_password: str,
        deleted_by: str = 'api'
    ) -> Dict:
        """
        Delete umbrella company (requires password).

        Args:
            company_id: Company identifier
            unlock_password: Password to unlock (must be "luca")
            deleted_by: Who is deleting

        Returns:
            Dict with success status and message
        """

        # Get current company data
        company = self.get_umbrella_company(company_id)

        if not company:
            return {
                'success': False,
                'error': f'Umbrella company {company_id} not found'
            }

        # Check if locked
        if company.get('locked', False):
            # Verify password
            password_hash = company.get('password_hash', '')

            if not self.verify_password(unlock_password, password_hash):
                return {
                    'success': False,
                    'error': 'Invalid unlock password. This data is locked.'
                }

        # Password verified - proceed with deletion
        try:
            self.table.delete_item(
                Key={'file_id': f'UMBRELLA#{company_id}'}
            )

            return {
                'success': True,
                'message': f'Umbrella company {company_id} deleted successfully'
            }

        except Exception as e:
            return {
                'success': False,
                'error': f'Failed to delete: {str(e)}'
            }


# Global instance
umbrella_manager = UmbrellaCompanyManager()


def get_umbrella_companies_for_ui() -> List[Dict]:
    """Get umbrella companies formatted for UI display."""
    companies = umbrella_manager.get_all_umbrella_companies()

    # Format for UI
    formatted = []
    for company in companies:
        formatted.append({
            'id': company.get('company_id', ''),
            'trading_name': company.get('trading_name', ''),
            'legal_name': company.get('legal_name', ''),
            'company_number': company.get('company_number', ''),
            'vat_number': company.get('vat_number', ''),
            'registered_address': company.get('registered_address', ''),
            'locked': company.get('locked', False),
            'created_at': company.get('created_at', ''),
            'modified_at': company.get('modified_at', ''),
            'version': company.get('version', 1)
        })

    # Sort by trading name
    formatted.sort(key=lambda x: x['trading_name'])

    return formatted
