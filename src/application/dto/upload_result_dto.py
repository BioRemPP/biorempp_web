"""
Upload Result Data Transfer Object.

Defines the UploadResultDTO, an immutable data transfer object that
encapsulates the results of file upload operations. Provides a clean
contract for communicating upload outcomes between application layers.

Classes
-------
UploadResultDTO
    Immutable DTO containing upload operation results
"""

from dataclasses import dataclass
from typing import Optional

from src.domain.entities.dataset import Dataset


@dataclass(frozen=True)
class UploadResultDTO:
    """
    Immutable DTO for upload operation results.

    Encapsulates all relevant information from a file upload operation,
    including success status, parsed dataset, and metadata.

    Parameters
    ----------
    success : bool
        Whether the upload operation succeeded
    dataset : Optional[Dataset]
        The parsed dataset entity (None if upload failed)
    filename : str
        Name of the uploaded file
    sample_count : int
        Number of samples parsed
    ko_count : int
        Total number of KOs across all samples
    message : str
        User-friendly message about the upload result
    errors : Optional[list[str]]
        List of validation or parsing errors (None if no errors)

    Attributes
    ----------
    success : bool
        Upload success status
    dataset : Optional[Dataset]
        Parsed dataset or None
    filename : str
        Uploaded filename
    sample_count : int
        Sample count
    ko_count : int
        KO count
    message : str
        Result message
    errors : Optional[list[str]]
        Error messages if any

    Notes
    -----
    - This DTO is immutable (frozen) to ensure data integrity
    - All validation should occur before DTO creation
    """

    success: bool
    dataset: Optional[Dataset]
    filename: str
    sample_count: int
    ko_count: int
    message: str
    errors: Optional[list[str]] = None

    def __post_init__(self) -> None:
        """
        Validate DTO consistency after initialization.

        Raises
        ------
        ValueError
            If success=True but dataset is None, or if counts are negative

        Notes
        -----
        This method is called automatically by dataclass after __init__.
        It ensures logical consistency of the DTO state.
        """
        if self.success and self.dataset is None:
            raise ValueError("Success=True requires a valid dataset")

        if self.sample_count < 0 or self.ko_count < 0:
            raise ValueError("Counts cannot be negative")

    def has_errors(self) -> bool:
        """
        Check if upload had any errors.

        Returns
        -------
        bool
            True if errors list is not empty, False otherwise
        """
        return self.errors is not None and len(self.errors) > 0
