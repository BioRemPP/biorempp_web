"""
Sample ID Value Object

Represents a unique identifier for a biological sample.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class SampleId:
    """
    Value Object for sample identifier.

    Parameters
    ----------
    value : str
        Sample identifier name (cannot be empty)

    Raises
    ------
    ValueError
        If value is empty or contains only spaces

    Notes
    -----
    This object is immutable ensuring identifier consistency
    throughout the application lifecycle.
    """

    value: str

    def __post_init__(self):
        """
        Validates the identifier after initialization.

        Raises
        ------
        ValueError
            If value is empty or None.
        """
        if not self.value or not self.value.strip():
            raise ValueError("Sample ID cannot be empty")

    def __str__(self) -> str:
        """
        Returns string representation of Sample ID.

        Returns
        -------
        str
            The identifier value.
        """
        return self.value

    def __repr__(self) -> str:
        """
        Returns debug representation of Sample ID.

        Returns
        -------
        str
            Representation in format "SampleId('value')".
        """
        return f"SampleId('{self.value}')"

    def __hash__(self) -> int:
        """
        Allows using SampleId as dictionary key.

        Returns
        -------
        int
            Hash of the value.
        """
        return hash(self.value)
