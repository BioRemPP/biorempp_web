"""Unit tests for MergedData entity."""

import pytest

from src.domain.entities.dataset import Dataset
from src.domain.entities.merged_data import MergedData
from src.domain.entities.sample import Sample
from src.domain.value_objects.kegg_orthology import KO
from src.domain.value_objects.sample_id import SampleId


def _build_dataset() -> Dataset:
    sample = Sample(id=SampleId("S1"))
    sample.add_ko(KO("K00001"))
    return Dataset(samples=[sample])


class TestMergedData:
    """Tests for merged-data status and validation."""

    def test_is_biorempp_merged_true_when_data_present(self):
        merged = MergedData(original_dataset=_build_dataset(), biorempp_data={"rows": 1})
        assert merged.is_biorempp_merged

    def test_is_biorempp_merged_false_when_data_empty(self):
        merged = MergedData(original_dataset=_build_dataset(), biorempp_data={})
        assert not merged.is_biorempp_merged

    def test_is_fully_merged_requires_all_mandatory_databases(self):
        merged = MergedData(
            original_dataset=_build_dataset(),
            biorempp_data={"rows": 1},
            kegg_data={"rows": 1},
            hadeg_data={"rows": 1},
        )
        assert merged.is_fully_merged

    def test_get_merge_status_returns_expected_flags(self):
        merged = MergedData(
            original_dataset=_build_dataset(),
            biorempp_data={"rows": 1},
            kegg_data={},
            hadeg_data={"rows": 1},
            toxcsm_data={},
        )

        status = merged.get_merge_status()

        assert status == {
            "biorempp": True,
            "kegg": False,
            "hadeg": True,
            "toxcsm": False,
        }

    def test_validate_raises_when_biorempp_not_merged(self):
        merged = MergedData(original_dataset=_build_dataset(), biorempp_data=None)

        with pytest.raises(ValueError, match="BioRemPP merge is required"):
            merged.validate()

    def test_validate_passes_when_biorempp_is_merged(self):
        merged = MergedData(
            original_dataset=_build_dataset(),
            biorempp_data={"rows": 1},
        )

        merged.validate()
        assert merged.is_biorempp_merged

    def test_str_representation_includes_merged_count(self):
        merged = MergedData(
            original_dataset=_build_dataset(),
            biorempp_data={"rows": 1},
            kegg_data={"rows": 1},
        )

        text = str(merged)

        assert "MergedData" in text
        assert "2/4 databases merged" in text

    def test_repr_representation_lists_merge_flags(self):
        merged = MergedData(
            original_dataset=_build_dataset(),
            biorempp_data={"rows": 1},
            kegg_data={},
            hadeg_data={"rows": 1},
            toxcsm_data={},
        )

        rep = repr(merged)

        assert "biorempp=True" in rep
        assert "kegg=False" in rep
        assert "hadeg=True" in rep
        assert "toxcsm=False" in rep
