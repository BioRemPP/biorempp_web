"""
KEGG Orthology Value Object

Represents an immutable KEGG Orthology (KO) identifier.
"""

from dataclasses import dataclass

from src.shared.logging import get_logger

# Logger for this module
logger = get_logger(__name__)


@dataclass(frozen=True)
class KO:
    """
    Immutable Value Object for KEGG Orthology.

    Parameters
    ----------
    id : str
        KO identifier in format 'KXXXXX' where X are digits
        Example: 'K00001', 'K12345'

    Raises
    ------
    ValueError
        If ID does not start with 'K' or does not have exactly 6 characters

    Notes
    -----
    This object is immutable (frozen=True) ensuring that once created
    it cannot be modified, respecting the DDD Value Object principle.
    """

    id: str

    def __post_init__(self):
        """
        Validates KO ID format after initialization.

        Raises
        ------
        ValueError
            If ID is invalid (does not start with 'K' or length != 6).
        """
        if not self.id:
            logger.warning("KO validation failed: Empty ID")
            raise ValueError("KO ID cannot be empty")

        if not self.id.startswith("K"):
            logger.warning(
                "KO validation failed: Invalid prefix", extra={"ko_id": self.id}
            )
            raise ValueError(f"Invalid KO ID: {self.id}. Must start with 'K'")

        if len(self.id) != 6:
            logger.warning(
                "KO validation failed: Invalid length",
                extra={"ko_id": self.id, "length": len(self.id)},
            )
            raise ValueError(
                f"Invalid KO ID: {self.id}. Must have exactly 6 characters"
            )

        # Verifica se os 5 últimos caracteres são dígitos
        if not self.id[1:].isdigit():
            logger.warning(
                "KO validation failed: Non-numeric suffix", extra={"ko_id": self.id}
            )
            raise ValueError(
                f"Invalid KO ID: {self.id}. Last 5 characters must be digits"
            )

        logger.debug("KO created successfully", extra={"ko_id": self.id})

    def __str__(self) -> str:
        """
        Returns string representation of KO.

        Returns
        -------
        str
            The KO ID.
        """
        return self.id

    def __repr__(self) -> str:
        """
        Returns debug representation of KO.

        Returns
        -------
        str
            Representation in format "KO('KXXXXX')".
        """
        return f"KO('{self.id}')"

    def __hash__(self) -> int:
        """
        Allows using KO as dictionary key or in sets.

        Returns
        -------
        int
            Hash of the ID.
        """
        return hash(self.id)
