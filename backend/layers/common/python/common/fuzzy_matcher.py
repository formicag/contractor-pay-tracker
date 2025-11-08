"""
Fuzzy name matching for contractor validation
Uses Levenshtein distance to handle typos and variations
"""

from typing import Dict, List, Optional, Tuple

from fuzzywuzzy import fuzz


class FuzzyMatcher:
    """Fuzzy string matching for contractor names"""

    def __init__(self, threshold: int = 85):
        """
        Initialize fuzzy matcher

        Args:
            threshold: Minimum similarity score (0-100) to consider a match
        """
        self.threshold = threshold

    def find_best_match(
        self,
        search_name: str,
        candidate_names: List[Dict],
        name_field: str = 'NormalizedName'
    ) -> Optional[Dict]:
        """
        Find best matching contractor from candidates

        Args:
            search_name: Name to search for (will be normalized)
            candidate_names: List of contractor dicts with name fields
            name_field: Field name containing the normalized name

        Returns:
            Dict with match info or None if no match found
        """
        if not candidate_names:
            return None

        search_normalized = self._normalize_name(search_name)

        best_match = None
        best_score = 0

        for candidate in candidate_names:
            candidate_name = candidate.get(name_field, '')

            # Try exact match first
            if search_normalized == candidate_name.lower():
                return {
                    'match_type': 'EXACT',
                    'contractor': candidate,
                    'confidence': 100,
                    'searched_name': search_name,
                    'matched_name': candidate_name
                }

            # Calculate fuzzy score
            score = fuzz.ratio(search_normalized, candidate_name.lower())

            if score > best_score:
                best_score = score
                best_match = candidate

        # Check if best match exceeds threshold
        if best_score >= self.threshold:
            return {
                'match_type': 'FUZZY',
                'contractor': best_match,
                'confidence': best_score,
                'searched_name': search_name,
                'matched_name': best_match.get(name_field, '')
            }

        return None

    def match_contractor_name(
        self,
        first_name: str,
        last_name: str,
        contractors: List[Dict]
    ) -> Optional[Dict]:
        """
        Match contractor by first and last name

        Args:
            first_name: First name from Excel file
            last_name: Last name from Excel file
            contractors: List of contractor dicts from DynamoDB

        Returns:
            Match result dict or None
        """
        search_name = f"{first_name} {last_name}"
        return self.find_best_match(search_name, contractors)

    @staticmethod
    def _normalize_name(name: str) -> str:
        """
        Normalize name for comparison

        - Convert to lowercase
        - Remove extra whitespace
        - Remove special characters except spaces
        """
        import re

        # Lowercase and strip
        normalized = name.lower().strip()

        # Remove special characters except spaces
        normalized = re.sub(r'[^a-z0-9\s]', '', normalized)

        # Collapse multiple spaces
        normalized = re.sub(r'\s+', ' ', normalized)

        return normalized

    def calculate_similarity(self, name1: str, name2: str) -> int:
        """
        Calculate similarity score between two names

        Args:
            name1: First name
            name2: Second name

        Returns:
            Similarity score (0-100)
        """
        normalized1 = self._normalize_name(name1)
        normalized2 = self._normalize_name(name2)

        return fuzz.ratio(normalized1, normalized2)
