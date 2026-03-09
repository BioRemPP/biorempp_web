"""Unit tests for Compound value object."""

import pytest

from src.domain.value_objects.compound import Compound


class TestCompound:
    """Tests for compound value semantics and validation."""

    def test_create_valid_compound(self):
        compound = Compound(cpd="C00001", name="Water", smiles="O", chebi="CHEBI:15377")

        assert compound.cpd == "C00001"
        assert compound.name == "Water"
        assert compound.has_structure()
        assert compound.has_chebi()

    def test_empty_cpd_raises(self):
        with pytest.raises(ValueError, match="cannot be empty"):
            Compound(cpd="", name="Water")

    def test_empty_name_raises(self):
        with pytest.raises(ValueError, match="cannot be empty"):
            Compound(cpd="C00001", name=" ")

    def test_str_and_repr(self):
        compound = Compound(cpd="C00001", name="Water")

        assert str(compound) == "Water"
        assert repr(compound) == "Compound('C00001', 'Water')"

    def test_has_structure_false_when_smiles_missing_or_blank(self):
        assert not Compound(cpd="C00001", name="Water", smiles=None).has_structure()
        assert not Compound(cpd="C00001", name="Water", smiles="   ").has_structure()

    def test_has_chebi_false_when_chebi_missing_or_blank(self):
        assert not Compound(cpd="C00001", name="Water", chebi=None).has_chebi()
        assert not Compound(cpd="C00001", name="Water", chebi=" ").has_chebi()

    def test_hash_uses_compound_code(self):
        c1 = Compound(cpd="C00001", name="Water")
        c2 = Compound(cpd="C00001", name="Aqua")

        assert hash(c1) == hash(c2)
