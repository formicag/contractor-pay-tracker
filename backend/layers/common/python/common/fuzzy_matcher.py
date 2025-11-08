"""
Fuzzy name matching for contractor validation
Uses Levenshtein distance to handle typos and variations
"""

print("[FUZZY_MATCHER_MODULE] Starting fuzzy_matcher.py module load")

from typing import Dict, List, Optional, Tuple

print("[FUZZY_MATCHER_MODULE] Imported typing modules")

from fuzzywuzzy import fuzz

print("[FUZZY_MATCHER_MODULE] Imported fuzzywuzzy")


class FuzzyMatcher:
    """Fuzzy string matching for contractor names"""

    def __init__(self, threshold: int = 85):
        """
        Initialize fuzzy matcher

        Args:
            threshold: Minimum similarity score (0-100) to consider a match
        """
        print(f"[FUZZYMATCHER_INIT] Starting FuzzyMatcher initialization with threshold={threshold}")
        self.threshold = threshold
        print(f"[FUZZYMATCHER_INIT] Set self.threshold={self.threshold}")
        print(f"[FUZZYMATCHER_INIT] FuzzyMatcher initialization complete")

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
        print(f"[FIND_BEST_MATCH] Called with search_name={search_name}, name_field={name_field}, {len(candidate_names)} candidates")

        if not candidate_names:
            print(f"[FIND_BEST_MATCH] No candidate_names provided, returning None")
            return None

        print(f"[FIND_BEST_MATCH] Normalizing search_name")
        search_normalized = self._normalize_name(search_name)
        print(f"[FIND_BEST_MATCH] Normalized search_name: {search_normalized}")

        best_match = None
        best_score = 0
        print(f"[FIND_BEST_MATCH] Initialized best_match=None, best_score=0")

        print(f"[FIND_BEST_MATCH] Iterating through {len(candidate_names)} candidates")
        for idx, candidate in enumerate(candidate_names):
            print(f"[FIND_BEST_MATCH] Processing candidate {idx+1}/{len(candidate_names)}: {candidate}")

            candidate_name = candidate.get(name_field, '')
            print(f"[FIND_BEST_MATCH] Candidate name from field '{name_field}': {candidate_name}")

            # Try exact match first
            print(f"[FIND_BEST_MATCH] Checking for exact match")
            if search_normalized == candidate_name.lower():
                print(f"[FIND_BEST_MATCH] EXACT MATCH FOUND!")
                result = {
                    'match_type': 'EXACT',
                    'contractor': candidate,
                    'confidence': 100,
                    'searched_name': search_name,
                    'matched_name': candidate_name
                }
                print(f"[FIND_BEST_MATCH] Returning exact match result: {result}")
                return result

            # Calculate fuzzy score
            print(f"[FIND_BEST_MATCH] Calculating fuzzy score for '{search_normalized}' vs '{candidate_name.lower()}'")
            score = fuzz.ratio(search_normalized, candidate_name.lower())
            print(f"[FIND_BEST_MATCH] Fuzzy score: {score}")

            if score > best_score:
                print(f"[FIND_BEST_MATCH] New best score! {score} > {best_score}")
                best_score = score
                best_match = candidate
                print(f"[FIND_BEST_MATCH] Updated best_match and best_score")
            else:
                print(f"[FIND_BEST_MATCH] Score {score} not better than best_score {best_score}")

        # Check if best match exceeds threshold
        print(f"[FIND_BEST_MATCH] Finished iterating. best_score={best_score}, threshold={self.threshold}")
        if best_score >= self.threshold:
            print(f"[FIND_BEST_MATCH] best_score ({best_score}) >= threshold ({self.threshold}), FUZZY MATCH FOUND")
            result = {
                'match_type': 'FUZZY',
                'contractor': best_match,
                'confidence': best_score,
                'searched_name': search_name,
                'matched_name': best_match.get(name_field, '')
            }
            print(f"[FIND_BEST_MATCH] Returning fuzzy match result: {result}")
            return result

        print(f"[FIND_BEST_MATCH] best_score ({best_score}) < threshold ({self.threshold}), NO MATCH")
        print(f"[FIND_BEST_MATCH] Returning None")
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
        print(f"[MATCH_CONTRACTOR_NAME] Called with first_name={first_name}, last_name={last_name}, {len(contractors)} contractors")

        search_name = f"{first_name} {last_name}"
        print(f"[MATCH_CONTRACTOR_NAME] Combined search_name: {search_name}")

        print(f"[MATCH_CONTRACTOR_NAME] Calling find_best_match")
        result = self.find_best_match(search_name, contractors)
        print(f"[MATCH_CONTRACTOR_NAME] find_best_match returned: {result}")

        return result

    @staticmethod
    def _normalize_name(name: str) -> str:
        """
        Normalize name for comparison

        - Convert to lowercase
        - Remove extra whitespace
        - Remove special characters except spaces
        """
        print(f"[NORMALIZE_NAME] Normalizing name: {name}")

        import re
        print(f"[NORMALIZE_NAME] Imported re module")

        # Lowercase and strip
        normalized = name.lower().strip()
        print(f"[NORMALIZE_NAME] After lowercase and strip: {normalized}")

        # Remove special characters except spaces
        normalized = re.sub(r'[^a-z0-9\s]', '', normalized)
        print(f"[NORMALIZE_NAME] After removing special chars: {normalized}")

        # Collapse multiple spaces
        normalized = re.sub(r'\s+', ' ', normalized)
        print(f"[NORMALIZE_NAME] After collapsing spaces: {normalized}")

        print(f"[NORMALIZE_NAME] Final normalized name: {normalized}")
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
        print(f"[CALCULATE_SIMILARITY] Called with name1={name1}, name2={name2}")

        print(f"[CALCULATE_SIMILARITY] Normalizing name1")
        normalized1 = self._normalize_name(name1)
        print(f"[CALCULATE_SIMILARITY] normalized1={normalized1}")

        print(f"[CALCULATE_SIMILARITY] Normalizing name2")
        normalized2 = self._normalize_name(name2)
        print(f"[CALCULATE_SIMILARITY] normalized2={normalized2}")

        print(f"[CALCULATE_SIMILARITY] Calculating fuzz.ratio")
        score = fuzz.ratio(normalized1, normalized2)
        print(f"[CALCULATE_SIMILARITY] Similarity score: {score}")

        return score

print("[FUZZY_MATCHER_MODULE] fuzzy_matcher.py module load complete")
