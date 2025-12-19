"""
Validation Result Data Transfer Object.

Defines the ValidationResultDTO, an immutable data transfer object that
encapsulates validation results. Provides detailed validation outcomes with
error messages and severity levels.

Classes
-------
ValidationResultDTO
    Immutable DTO containing validation results
"""

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class ValidationResultDTO:
    """
    Immutable DTO for validation operation results.

    Encapsulates validation outcomes including success status, error messages,
    warnings, and metadata about validated items.

    Parameters
    ----------
    is_valid : bool
        Whether validation passed (no errors)
    errors : Optional[list[str]]
        List of validation error messages (None if no errors)
    warnings : Optional[list[str]]
        List of validation warnings (None if no warnings)
    validated_items : int
        Number of items validated
    message : str, default=""
        Summary message about validation result

    Attributes
    ----------
    is_valid : bool
        Validation success status
    errors : Optional[list[str]]
        Error messages
    warnings : Optional[list[str]]
        Warning messages
    validated_items : int
        Count of validated items
    message : str
        Summary message

    Notes
    -----
    - This DTO is immutable (frozen) to ensure data integrity
    - Errors prevent processing, warnings allow processing but flag issues
    """

    is_valid: bool
    errors: Optional[list[str]]
    warnings: Optional[list[str]]
    validated_items: int
    message: str = ""

    def __post_init__(self) -> None:
        """
        Validate DTO consistency.

        Raises
        ------
        ValueError
            If is_valid=False but no errors, or validated_items is negative
        """
        if not self.is_valid and (self.errors is None or len(self.errors) == 0):
            raise ValueError("is_valid=False requires error messages")

        if self.validated_items < 0:
            raise ValueError("validated_items cannot be negative")

    def has_errors(self) -> bool:
        """
        Check if validation has errors.

        Returns
        -------
        bool
            True if errors exist
        """
        return self.errors is not None and len(self.errors) > 0

    def has_warnings(self) -> bool:
        """
        Check if validation has warnings.

        Returns
        -------
        bool
            True if warnings exist
        """
        return self.warnings is not None and len(self.warnings) > 0

    def error_count(self) -> int:
        """
        Get count of errors.

        Returns
        -------
        int
            Number of errors
        """
        return len(self.errors) if self.errors else 0

    def warning_count(self) -> int:
        """
        Get count of warnings.

        Returns
        -------
        int
            Number of warnings
        """
        return len(self.warnings) if self.warnings else 0
