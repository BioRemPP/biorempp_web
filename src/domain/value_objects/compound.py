"""
Compound Value Object

Represents a chemical compound in the system.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class Compound:
    """
    Value Object for chemical compound.

    Parameters
    ----------
    cpd : str
        Compound identifier code (e.g., 'C00001')
    name : str
        Compound name (e.g., 'H2O', 'Water')
    smiles : Optional[str], default=None
        SMILES notation of the compound
    chebi : Optional[str], default=None
        ChEBI identifier

    Raises
    ------
    ValueError
        If cpd or name are empty

    Notes
    -----
    Compounds are uniquely identified by cpd code.
    SMILES and ChEBI are optional for data enrichment.
    """

    cpd: str
    name: str
    smiles: Optional[str] = None
    chebi: Optional[str] = None

    def __post_init__(self):
        """
        Validates required compound fields.

        Raises
        ------
        ValueError
            If cpd or name are invalid.
        """
        if not self.cpd or not self.cpd.strip():
            raise ValueError("Compound code (cpd) cannot be empty")

        if not self.name or not self.name.strip():
            raise ValueError("Compound name cannot be empty")

    def __str__(self) -> str:
        """
        Returns string representation of compound.

        Returns
        -------
        str
            Compound name.
        """
        return self.name

    def __repr__(self) -> str:
        """
        Returns debug representation of compound.

        Returns
        -------
        str
            Representation with cpd and name.
        """
        return f"Compound('{self.cpd}', '{self.name}')"

    def __hash__(self) -> int:
        """
        Hash based on compound code.

        Returns
        -------
        int
            Hash of cpd.
        """
        return hash(self.cpd)

    def has_structure(self) -> bool:
        """
        Checks if compound has structural information (SMILES).

        Returns
        -------
        bool
            True if SMILES is defined.
        """
        return self.smiles is not None and len(self.smiles.strip()) > 0

    def has_chebi(self) -> bool:
        """
        Checks if compound has ChEBI reference.

        Returns
        -------
        bool
            True if ChEBI is defined.
        """
        return self.chebi is not None and len(self.chebi.strip()) > 0
