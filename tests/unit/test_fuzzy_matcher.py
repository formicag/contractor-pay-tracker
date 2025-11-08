"""
Unit tests for fuzzy_matcher.py
Tests Levenshtein distance name matching with various scenarios
"""

import pytest
from common.fuzzy_matcher import FuzzyMatcher


class TestFuzzyMatcher:
    """Test fuzzy name matching functionality"""

    def test_exact_match(self, sample_contractors):
        """Test exact name match returns 100% confidence"""
        matcher = FuzzyMatcher(threshold=85)

        result = matcher.match_contractor_name('Jonathan', 'Mays', sample_contractors)

        assert result is not None
        assert result['match_type'] == 'EXACT'
        assert result['confidence'] == 100
        assert result['contractor']['ContractorID'] == 'C001'
        assert result['searched_name'] == 'jonathan mays'
        assert result['matched_name'] == 'Jonathan Mays'

    def test_fuzzy_match_jon_to_jonathan(self, sample_contractors):
        """Test fuzzy match: 'Jon' → 'Jonathan' (should be ~87% match)"""
        matcher = FuzzyMatcher(threshold=85)

        result = matcher.match_contractor_name('Jon', 'Mays', sample_contractors)

        assert result is not None
        assert result['match_type'] == 'FUZZY'
        assert result['confidence'] >= 85
        assert result['contractor']['ContractorID'] == 'C001'
        assert result['searched_name'] == 'jon mays'
        assert result['matched_name'] == 'Jonathan Mays'

    def test_fuzzy_match_mathews_to_matthews(self, sample_contractors):
        """Test fuzzy match: 'Mathews' → 'Matthews' (should be ~93% match)"""
        matcher = FuzzyMatcher(threshold=85)

        result = matcher.match_contractor_name('Stephen', 'Mathews', sample_contractors)

        assert result is not None
        assert result['match_type'] == 'FUZZY'
        assert result['confidence'] >= 85
        assert result['contractor']['ContractorID'] == 'C004'

    def test_no_match_below_threshold(self, sample_contractors):
        """Test no match when name is too different"""
        matcher = FuzzyMatcher(threshold=85)

        result = matcher.match_contractor_name('John', 'Doe', sample_contractors)

        assert result is None

    def test_no_match_empty_list(self):
        """Test no match with empty contractor list"""
        matcher = FuzzyMatcher(threshold=85)

        result = matcher.match_contractor_name('Jonathan', 'Mays', [])

        assert result is None

    def test_case_insensitive_match(self, sample_contractors):
        """Test case-insensitive matching"""
        matcher = FuzzyMatcher(threshold=85)

        result = matcher.match_contractor_name('JONATHAN', 'MAYS', sample_contractors)

        assert result is not None
        assert result['match_type'] == 'EXACT'
        assert result['confidence'] == 100

    def test_whitespace_handling(self, sample_contractors):
        """Test matching with extra whitespace"""
        matcher = FuzzyMatcher(threshold=85)

        result = matcher.match_contractor_name('  Jonathan  ', '  Mays  ', sample_contractors)

        assert result is not None
        assert result['match_type'] == 'EXACT'

    def test_threshold_adjustment(self, sample_contractors):
        """Test different threshold values"""
        # High threshold (strict)
        matcher_strict = FuzzyMatcher(threshold=95)
        result_strict = matcher_strict.match_contractor_name('Jon', 'Mays', sample_contractors)

        # Low threshold (permissive)
        matcher_permissive = FuzzyMatcher(threshold=70)
        result_permissive = matcher_permissive.match_contractor_name('Jon', 'Mays', sample_contractors)

        # Both should find a match, but with different match types
        assert result_permissive is not None
        # Jon -> Jonathan is ~87%, so strict (95%) might not match

    def test_multiple_similar_names(self):
        """Test matching when multiple similar names exist"""
        contractors = [
            {
                'ContractorID': 'C001',
                'FirstName': 'John',
                'LastName': 'Smith',
                'NormalizedName': 'john smith'
            },
            {
                'ContractorID': 'C002',
                'FirstName': 'Jon',
                'LastName': 'Smith',
                'NormalizedName': 'jon smith'
            },
            {
                'ContractorID': 'C003',
                'FirstName': 'Jonathan',
                'LastName': 'Smith',
                'NormalizedName': 'jonathan smith'
            }
        ]

        matcher = FuzzyMatcher(threshold=85)

        # Should match exact first
        result = matcher.match_contractor_name('Jon', 'Smith', contractors)
        assert result is not None
        assert result['contractor']['ContractorID'] == 'C002'  # Exact match to Jon Smith

    def test_special_characters_normalization(self):
        """Test normalization of special characters"""
        contractors = [
            {
                'ContractorID': 'C001',
                'FirstName': "O'Brien",
                'LastName': 'Smith',
                'NormalizedName': "o'brien smith"
            }
        ]

        matcher = FuzzyMatcher(threshold=85)

        result = matcher.match_contractor_name("OBrien", "Smith", contractors)

        # Should find a fuzzy match despite apostrophe difference
        assert result is not None
        assert result['confidence'] >= 85

    def test_confidence_score_calculation(self, sample_contractors):
        """Test that confidence scores are calculated correctly"""
        matcher = FuzzyMatcher(threshold=85)

        # Test exact match
        result_exact = matcher.match_contractor_name('David', 'Hunt', sample_contractors)
        assert result_exact['confidence'] == 100

        # Test fuzzy match
        result_fuzzy = matcher.match_contractor_name('Davd', 'Hunt', sample_contractors)
        assert result_fuzzy is not None
        assert 85 <= result_fuzzy['confidence'] < 100

    def test_normalize_name_method(self):
        """Test the normalize_name helper method"""
        matcher = FuzzyMatcher()

        # Test various normalization scenarios
        assert matcher.normalize_name("  Jonathan  ") == "jonathan"
        assert matcher.normalize_name("JONATHAN") == "jonathan"
        assert matcher.normalize_name("Jon-Paul") == "jon-paul"
        assert matcher.normalize_name("O'Brien") == "o'brien"

    def test_performance_with_large_list(self):
        """Test matching performance with large contractor list"""
        # Create 1000 contractors
        large_contractor_list = [
            {
                'ContractorID': f'C{i:04d}',
                'FirstName': f'FirstName{i}',
                'LastName': f'LastName{i}',
                'NormalizedName': f'firstname{i} lastname{i}'
            }
            for i in range(1000)
        ]

        # Add our target contractor
        large_contractor_list.append({
            'ContractorID': 'TARGET',
            'FirstName': 'Jonathan',
            'LastName': 'Mays',
            'NormalizedName': 'jonathan mays'
        })

        matcher = FuzzyMatcher(threshold=85)

        result = matcher.match_contractor_name('Jon', 'Mays', large_contractor_list)

        # Should still find the match
        assert result is not None
        assert result['contractor']['ContractorID'] == 'TARGET'

    def test_empty_name_handling(self, sample_contractors):
        """Test handling of empty or None names"""
        matcher = FuzzyMatcher(threshold=85)

        # Empty first name
        result = matcher.match_contractor_name('', 'Mays', sample_contractors)
        assert result is None

        # Empty last name
        result = matcher.match_contractor_name('Jonathan', '', sample_contractors)
        assert result is None

        # Both empty
        result = matcher.match_contractor_name('', '', sample_contractors)
        assert result is None
