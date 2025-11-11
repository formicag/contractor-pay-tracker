"""
Canonical Customer Groups Manager

Manages canonical customer group data with entity resolution and matching.
All modifications require password "luca".
"""

import boto3
import os
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timezone
from difflib import SequenceMatcher
import re

# AWS Configuration
AWS_REGION = os.getenv('AWS_REGION', 'eu-west-1')
TABLE_NAME = os.getenv('PAYFILES_TABLE_NAME', 'contractor-pay-files-metadata')

# Unlock password
UNLOCK_PASSWORD = 'luca'


class CanonicalGroupsManager:
    """Manager for canonical customer groups with entity resolution."""

    def __init__(self):
        self.dynamodb = boto3.resource('dynamodb', region_name=AWS_REGION)
        self.table = self.dynamodb.Table(TABLE_NAME)

    def verify_password(self, password: str) -> bool:
        """Verify unlock password."""
        return password == UNLOCK_PASSWORD

    def normalize_name(self, name: str) -> str:
        """
        Normalize company name for matching.

        Args:
            name: Company name to normalize

        Returns:
            Normalized name (lowercase, no extra whitespace, no punctuation)
        """
        if not name:
            return ""

        # Convert to lowercase
        normalized = name.lower()

        # Remove common legal suffixes for better matching
        legal_suffixes = [
            'limited', 'ltd', 'plc', 'llc', 'inc', 'incorporated',
            'corporation', 'corp', 'company', 'co'
        ]

        for suffix in legal_suffixes:
            # Remove suffix with word boundary
            normalized = re.sub(rf'\b{suffix}\b\.?', '', normalized)

        # Remove punctuation except hyphens
        normalized = re.sub(r'[^\w\s-]', '', normalized)

        # Collapse multiple spaces
        normalized = re.sub(r'\s+', ' ', normalized).strip()

        return normalized

    def calculate_similarity(self, str1: str, str2: str) -> float:
        """
        Calculate similarity score between two strings.

        Args:
            str1: First string
            str2: Second string

        Returns:
            Similarity score between 0.0 and 1.0
        """
        return SequenceMatcher(None, str1.lower(), str2.lower()).ratio()

    def get_all_groups(self) -> List[Dict]:
        """Get all canonical customer groups."""
        try:
            response = self.table.scan(
                FilterExpression='begins_with(file_id, :prefix)',
                ExpressionAttributeValues={
                    ':prefix': 'CANONICAL_GROUP#'
                }
            )

            groups = response.get('Items', [])

            # Handle pagination
            while 'LastEvaluatedKey' in response:
                response = self.table.scan(
                    ExclusiveStartKey=response['LastEvaluatedKey'],
                    FilterExpression='begins_with(file_id, :prefix)',
                    ExpressionAttributeValues={
                        ':prefix': 'CANONICAL_GROUP#'
                    }
                )
                groups.extend(response.get('Items', []))

            return groups

        except Exception as e:
            print(f"Error fetching canonical groups: {str(e)}")
            return []

    def get_group(self, canonical_id: str) -> Optional[Dict]:
        """Get a specific canonical group by ID."""
        try:
            response = self.table.get_item(
                Key={'file_id': f'CANONICAL_GROUP#{canonical_id}'}
            )
            return response.get('Item')
        except Exception as e:
            print(f"Error fetching group {canonical_id}: {str(e)}")
            return None

    def create_group(
        self,
        canonical_id: str,
        group_name: str,
        legal_entity: str,
        company_no: str,
        unlock_password: str,
        created_by: str = 'api'
    ) -> Dict:
        """
        Create a new canonical customer group.

        Args:
            canonical_id: Unique ID for the group (e.g., CG-0001)
            group_name: Display name (e.g., "Nasstar Group")
            legal_entity: Primary legal entity name
            company_no: Company registration number
            unlock_password: Password to unlock (must be "luca")
            created_by: Who created the group

        Returns:
            Dict with success status and message
        """
        # Verify password
        if not self.verify_password(unlock_password):
            return {
                'success': False,
                'error': 'Invalid unlock password. Canonical groups are locked.'
            }

        # Check if group already exists
        existing = self.get_group(canonical_id)
        if existing:
            return {
                'success': False,
                'error': f'Group {canonical_id} already exists'
            }

        try:
            timestamp = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')

            group_data = {
                'file_id': f'CANONICAL_GROUP#{canonical_id}',
                'canonical_id': canonical_id,
                'group_name': group_name,
                'legal_entity': legal_entity,
                'company_no': company_no,
                'aliases': [],  # Will store list of alias dicts
                'created_at': timestamp,
                'created_by': created_by,
                'modified_at': timestamp,
                'modified_by': created_by,
                'version': 1
            }

            self.table.put_item(Item=group_data)

            return {
                'success': True,
                'message': f'Canonical group {canonical_id} created successfully',
                'group': group_data
            }

        except Exception as e:
            return {
                'success': False,
                'error': f'Failed to create group: {str(e)}'
            }

    def add_alias(
        self,
        canonical_id: str,
        alias: str,
        alias_type: str,
        unlock_password: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        notes: Optional[str] = None,
        modified_by: str = 'api'
    ) -> Dict:
        """
        Add an alias to a canonical group.

        Args:
            canonical_id: Group ID
            alias: Company name alias
            alias_type: Type (e.g., "Brand", "Legal Name", "Former Name", "Acquired Unit")
            unlock_password: Password to unlock
            start_date: When alias became valid (ISO format)
            end_date: When alias became invalid (ISO format, None if still valid)
            notes: Additional notes
            modified_by: Who made the modification

        Returns:
            Dict with success status and message
        """
        # Verify password
        if not self.verify_password(unlock_password):
            return {
                'success': False,
                'error': 'Invalid unlock password. Canonical groups are locked.'
            }

        # Get existing group
        group = self.get_group(canonical_id)
        if not group:
            return {
                'success': False,
                'error': f'Group {canonical_id} not found'
            }

        try:
            # Get current aliases
            aliases = group.get('aliases', [])

            # Add new alias
            alias_data = {
                'alias': alias,
                'alias_type': alias_type,
                'normalized': self.normalize_name(alias),
                'start_date': start_date or datetime.now(timezone.utc).strftime('%Y-%m-%d'),
                'end_date': end_date,
                'notes': notes,
                'added_at': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
                'added_by': modified_by
            }

            aliases.append(alias_data)

            # Update group
            timestamp = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')

            self.table.update_item(
                Key={'file_id': f'CANONICAL_GROUP#{canonical_id}'},
                UpdateExpression='SET aliases = :aliases, modified_at = :modified_at, modified_by = :modified_by, version = version + :inc',
                ExpressionAttributeValues={
                    ':aliases': aliases,
                    ':modified_at': timestamp,
                    ':modified_by': modified_by,
                    ':inc': 1
                }
            )

            return {
                'success': True,
                'message': f'Alias "{alias}" added to group {canonical_id}',
                'alias': alias_data
            }

        except Exception as e:
            return {
                'success': False,
                'error': f'Failed to add alias: {str(e)}'
            }

    def match_entity(
        self,
        entity_name: str,
        active_only: bool = True,
        min_score: float = 0.75
    ) -> List[Dict]:
        """
        Match an entity name against canonical groups.

        Args:
            entity_name: Company name to match
            active_only: Only match active (non-expired) aliases
            min_score: Minimum similarity score (0.0 to 1.0)

        Returns:
            List of matches sorted by score (highest first)
        """
        if not entity_name:
            return []

        normalized_input = self.normalize_name(entity_name)
        matches = []

        # Get all groups
        groups = self.get_all_groups()

        today = datetime.now(timezone.utc).strftime('%Y-%m-%d')

        for group in groups:
            canonical_id = group.get('canonical_id')
            group_name = group.get('group_name')
            legal_entity = group.get('legal_entity')
            aliases = group.get('aliases', [])

            # Check group name
            score = self.calculate_similarity(normalized_input, self.normalize_name(group_name))
            if score >= min_score:
                matches.append({
                    'canonical_id': canonical_id,
                    'group_name': group_name,
                    'matched_text': group_name,
                    'match_type': 'group_name',
                    'score': score,
                    'active': True
                })

            # Check legal entity
            score = self.calculate_similarity(normalized_input, self.normalize_name(legal_entity))
            if score >= min_score:
                matches.append({
                    'canonical_id': canonical_id,
                    'group_name': group_name,
                    'matched_text': legal_entity,
                    'match_type': 'legal_entity',
                    'score': score,
                    'active': True
                })

            # Check aliases
            for alias_data in aliases:
                alias = alias_data.get('alias', '')
                alias_type = alias_data.get('alias_type', '')
                start_date = alias_data.get('start_date', '')
                end_date = alias_data.get('end_date')

                # Check if alias is active
                is_active = True
                if start_date and start_date > today:
                    is_active = False
                if end_date and end_date < today:
                    is_active = False

                # Skip inactive if requested
                if active_only and not is_active:
                    continue

                # Calculate score
                score = self.calculate_similarity(normalized_input, self.normalize_name(alias))

                # Also check partial match (does normalized input contain alias or vice versa)
                if normalized_input in self.normalize_name(alias) or self.normalize_name(alias) in normalized_input:
                    score = max(score, 0.85)  # Boost score for partial matches

                if score >= min_score:
                    matches.append({
                        'canonical_id': canonical_id,
                        'group_name': group_name,
                        'matched_text': alias,
                        'match_type': f'alias_{alias_type}',
                        'score': score,
                        'active': is_active,
                        'start_date': start_date,
                        'end_date': end_date
                    })

        # Sort by score (highest first)
        matches.sort(key=lambda x: x['score'], reverse=True)

        return matches

    def delete_group(
        self,
        canonical_id: str,
        unlock_password: str,
        deleted_by: str = 'api'
    ) -> Dict:
        """
        Delete a canonical group.

        Args:
            canonical_id: Group ID to delete
            unlock_password: Password to unlock
            deleted_by: Who deleted the group

        Returns:
            Dict with success status and message
        """
        # Verify password
        if not self.verify_password(unlock_password):
            return {
                'success': False,
                'error': 'Invalid unlock password. Canonical groups are locked.'
            }

        # Check if group exists
        group = self.get_group(canonical_id)
        if not group:
            return {
                'success': False,
                'error': f'Group {canonical_id} not found'
            }

        try:
            self.table.delete_item(
                Key={'file_id': f'CANONICAL_GROUP#{canonical_id}'}
            )

            return {
                'success': True,
                'message': f'Canonical group {canonical_id} deleted successfully'
            }

        except Exception as e:
            return {
                'success': False,
                'error': f'Failed to delete group: {str(e)}'
            }


# Global instance
canonical_groups_manager = CanonicalGroupsManager()
