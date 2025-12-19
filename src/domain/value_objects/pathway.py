"""
Pathway Value Object

Represents a KEGG metabolic pathway.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Pathway:
    """
    Value Object for KEGG metabolic pathway.

    Parameters
    ----------
    id : str
        Pathway identifier (e.g., 'map00010')
    name : str
        Descriptive pathway name (e.g., 'Glycolysis / Gluconeogenesis')

    Raises
    ------
    ValueError
        If ID or name are empty

    Notes
    -----
    Pathways are immutable and uniquely identified by ID.
    """

    id: str
    name: str

    def __post_init__(self):
        """
        Validates pathway fields.

        Raises
        ------
        ValueError
            If ID or name are invalid.
        """
        if not self.id or not self.id.strip():
            raise ValueError("Pathway ID cannot be empty")

        if not self.name or not self.name.strip():
            raise ValueError("Pathway name cannot be empty")

    def __str__(self) -> str:
        """
        Returns string representation of pathway.

        Returns
        -------
        str
            Pathway name.
        """
        return self.name

    def __repr__(self) -> str:
        """
        Returns debug representation of pathway.

        Returns
        -------
        str
            Representation in format "Pathway('id', 'name')".
        """
        return f"Pathway('{self.id}', '{self.name}')"

    def __hash__(self) -> int:
        """
        Hash based on pathway ID.

        Returns
        -------
        int
            Hash of the ID.
        """
        return hash(self.id)
