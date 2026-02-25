"""Unit tests for Pathway value object."""

import pytest

from src.domain.value_objects.pathway import Pathway


class TestPathway:
    """Tests for pathway value semantics and validation."""

    def test_create_valid_pathway(self):
        pathway = Pathway(id="map00010", name="Glycolysis / Gluconeogenesis")

        assert pathway.id == "map00010"
        assert pathway.name == "Glycolysis / Gluconeogenesis"

    def test_empty_id_raises(self):
        with pytest.raises(ValueError, match="Pathway ID cannot be empty"):
            Pathway(id="", name="Glycolysis")

    def test_empty_name_raises(self):
        with pytest.raises(ValueError, match="Pathway name cannot be empty"):
            Pathway(id="map00010", name=" ")

    def test_str_and_repr(self):
        pathway = Pathway(id="map00010", name="Glycolysis")

        assert str(pathway) == "Glycolysis"
        assert repr(pathway) == "Pathway('map00010', 'Glycolysis')"

    def test_hash_uses_pathway_id(self):
        p1 = Pathway(id="map00010", name="Glycolysis")
        p2 = Pathway(id="map00010", name="Alternative name")

        assert hash(p1) == hash(p2)
