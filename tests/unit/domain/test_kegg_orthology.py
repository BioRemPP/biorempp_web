"""
Unit Tests for KEGG Orthology Value Object
"""

import pytest

from biorempp_web.src.domain.value_objects.kegg_orthology import KO


class TestKO:
    """Tests for the KO Value Object."""

    def test_create_valid_ko(self, valid_ko_ids):
        """Tests creating a valid KO with real data."""
        # Use first real KO from database
        ko = KO(valid_ko_ids[0])
        assert ko.id == valid_ko_ids[0]
        assert ko.id.startswith('K')
        assert len(ko.id) == 6

    def test_ko_str_representation(self, sample_ko):
        """Tests the KO's string representation."""
        ko_str = str(sample_ko)
        assert ko_str.startswith('K')
        assert len(ko_str) == 6

    def test_ko_repr_representation(self, sample_ko):
        """Tests the KO's debug representation."""
        ko_repr = repr(sample_ko)
        assert ko_repr.startswith("KO('K")
        assert ko_repr.endswith("')")

    def test_ko_is_immutable(self, sample_ko):
        """Tests the KO's immutability."""
        with pytest.raises(Exception):  # frozen dataclass
            sample_ko.id = "K99999"

    def test_ko_equality(self, valid_ko_ids):
        """Tests equality between KOs using real data."""
        ko1 = KO(valid_ko_ids[0])
        ko2 = KO(valid_ko_ids[0])  # Same as ko1
        ko3 = KO(valid_ko_ids[1])  # Different

        assert ko1 == ko2
        assert ko1 != ko3

    def test_ko_hashable(self, valid_ko_ids):
        """Tests that KO can be used in a set/dict."""
        ko1 = KO(valid_ko_ids[0])
        ko2 = KO(valid_ko_ids[0])  # Duplicate
        ko3 = KO(valid_ko_ids[1])  # Different

        ko_set = {ko1, ko2, ko3}
        assert len(ko_set) == 2  # ko1 and ko2 are equal

    def test_invalid_ko_empty(self, edge_case_empty_string_ko):
        """Tests an empty KO using fixture."""
        with pytest.raises(ValueError, match="cannot be empty"):
            KO(edge_case_empty_string_ko)

    def test_invalid_ko_no_k_prefix(self, invalid_ko_ids):
        """Tests KO without 'K' prefix using invalid fixtures."""
        # Find invalid KO without K prefix
        no_k_prefix = [ko for ko in invalid_ko_ids if ko and not str(ko).startswith('K')][0]
        with pytest.raises(ValueError, match="Must start with 'K'"):
            KO(no_k_prefix)

    def test_invalid_ko_wrong_length(self, invalid_ko_ids):
        """Tests KO with incorrect length."""
        # Too short
        too_short = [ko for ko in invalid_ko_ids if ko and len(str(ko)) < 6 and str(ko).startswith('K')][0]
        with pytest.raises(ValueError, match="6 characters"):
            KO(too_short)

        # Too long
        too_long = [ko for ko in invalid_ko_ids if ko and len(str(ko)) > 6 and str(ko).startswith('K')][0]
        with pytest.raises(ValueError, match="6 characters"):
            KO(too_long)

    def test_invalid_ko_non_numeric(self, invalid_ko_ids):
        """Tests KO with non-numeric characters."""
        # Find KO with non-numeric suffix
        non_numeric = [ko for ko in invalid_ko_ids if ko and str(ko).startswith('K') and len(str(ko)) == 6][0]
        with pytest.raises(ValueError, match="must be digits"):
            KO(non_numeric)

    def test_ko_valid_range(self, valid_ko_ids):
        """Tests KOs in different valid ranges using real data."""
        # Test first 5 real KOs from database
        for ko_id in valid_ko_ids[:5]:
            ko = KO(ko_id)
            assert ko.id == ko_id
            assert ko.id.startswith('K')
            assert len(ko.id) == 6


class TestKOUseCases:
    """Tests use cases with KO."""

    def test_ko_in_list(self, sample_ko_list, valid_ko_ids):
        """Tests using KO in lists with real data."""
        # Verify list has exactly 5 items
        assert len(sample_ko_list) == 5
        
        # First KO in list should be findable
        first_ko = sample_ko_list[0]
        assert first_ko in sample_ko_list
        
        # Creating new KO with same ID should match
        # This tests equality implementation
        ko_ids_in_list = [ko.id for ko in sample_ko_list]
        assert valid_ko_ids[0] in ko_ids_in_list

    def test_ko_as_dict_key(self, valid_ko_ids):
        """Tests using KO as a dictionary key with real data."""
        # Use first 3 KOs from the 5 available
        ko_map = {
            KO(valid_ko_ids[0]): "Gene A",
            KO(valid_ko_ids[1]): "Gene B"
        }

        assert ko_map[KO(valid_ko_ids[0])] == "Gene A"
        
        # Use 3rd KO (not in map) to verify key not found
        other_ko = KO(valid_ko_ids[2])
        assert other_ko not in ko_map
