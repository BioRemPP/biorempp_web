"""
Upload Handler - Process file uploads with validation.

This module provides functionality to handle file upload operations,
including content validation, parsing, and result packaging. It acts
as the entry point for user data processing.

Classes
-------
UploadHandler
    Handles file upload validation and processing

Examples
--------
>>> handler = UploadHandler()
>>> result = handler.process_upload(
...     content="data:text/plain;base64,..base64_content..",
...     filename="samples.txt"
... )
>>> if result.success:
...     print(f"Uploaded {result.sample_count} samples")
"""

import base64
from typing import Optional

from src.application.core.sample_parser import SampleParser
from src.application.dto.upload_result_dto import UploadResultDTO
from src.domain.services.validation_service import ValidationService


class UploadHandler:
    """
    Handle file upload operations with validation.

    This class coordinates file upload processing including content
    decoding, format validation, parsing, and result packaging.

    Parameters
    ----------
    parser : Optional[SampleParser]
        Parser instance (injected for testing, creates default if None)
    validation_service : Optional[ValidationService]
        Validation service (injected for testing, uses default if None)

    Attributes
    ----------
    _parser : SampleParser
        Parser for converting content to entities
    _validation_service : ValidationService
        Service for validation logic

    Methods
    -------
    process_upload(content: str, filename: str) -> UploadResultDTO
        Process uploaded file and return result DTO
    decode_content(content: str) -> str
        Decode base64 content from Dash upload
    validate_and_parse(content: str) -> Tuple[bool, Dataset, List[str]]
        Validate content and parse into dataset

    Notes
    -----
    Uses dependency injection for parser and validation service,
    following SOLID principles (Dependency Inversion Principle).

    Examples
    --------
    >>> handler = UploadHandler()
    >>> content = "data:text/plain;base64,PlNhbXBsZTEKSzAwMDAx"
    >>> result = handler.process_upload(content, "test.txt")
    >>> result.success
    True
    """

    def __init__(
        self,
        parser: Optional[SampleParser] = None,
        validation_service: Optional[ValidationService] = None,
    ) -> None:
        """
        Initialize UploadHandler with dependencies.

        Parameters
        ----------
        parser : Optional[SampleParser]
            Parser instance (creates default if None)
        validation_service : Optional[ValidationService]
            Validation service (uses class methods if None)
        """
        self._parser = parser if parser is not None else SampleParser()
        self._validation_service = (
            validation_service if validation_service is not None else ValidationService
        )

    def process_upload(self, content: str, filename: str) -> UploadResultDTO:
        """
        Process uploaded file and return result DTO.

        Parameters
        ----------
        content : str
            Base64-encoded content from Dash upload component
        filename : str
            Name of uploaded file

        Returns
        -------
        UploadResultDTO
            Result DTO with success status and parsed data or errors

        Examples
        --------
        >>> handler = UploadHandler()
        >>> result = handler.process_upload(content_b64, "data.txt")
        >>> if result.success:
        ...     print(f"Uploaded {result.filename}")
        """
        try:
            # Decode content
            decoded_content = self.decode_content(content)

            # Validate and parse
            is_valid, dataset, metrics, errors = self.validate_and_parse(
                decoded_content
            )

            if not is_valid:
                return UploadResultDTO(
                    success=False,
                    dataset=None,
                    filename=filename,
                    sample_count=0,
                    ko_count=0,
                    message="Upload failed validation",
                    errors=errors,
                )

            # Success
            return UploadResultDTO(
                success=True,
                dataset=dataset,
                filename=filename,
                sample_count=dataset.total_samples,
                ko_count=dataset.total_kos,
                message=f"Successfully uploaded {dataset.total_samples} samples "
                f"with {dataset.total_kos} KOs",
                errors=None,
            )

        except Exception as e:
            return UploadResultDTO(
                success=False,
                dataset=None,
                filename=filename,
                sample_count=0,
                ko_count=0,
                message="Upload processing error",
                errors=[str(e)],
            )

    def decode_content(self, content: str) -> str:
        """
        Decode base64 content from Dash upload component.

        Parameters
        ----------
        content : str
            Base64-encoded content with data URI prefix

        Returns
        -------
        str
            Decoded text content

        Raises
        ------
        ValueError
            If content format is invalid or decoding fails

        Notes
        -----
        Expected format: "data:text/plain;base64,<base64_content>"
        This is the standard format from Dash dcc.Upload component.

        Examples
        --------
        >>> handler = UploadHandler()
        >>> encoded = "data:text/plain;base64,SGVsbG8="
        >>> handler.decode_content(encoded)
        'Hello'
        """
        if not content:
            raise ValueError("Content is empty")

        # Remove data URI prefix if present
        if "base64," in content:
            content = content.split("base64,")[1]

        try:
            decoded_bytes = base64.b64decode(content)
            decoded_str = decoded_bytes.decode("utf-8")
            return decoded_str
        except Exception as e:
            raise ValueError(f"Failed to decode content: {str(e)}")

    def validate_and_parse(self, content: str) -> tuple:
        """
        Validate content and parse into dataset.

        Parameters
        ----------
        content : str
            Raw text content to validate and parse

        Returns
        -------
        tuple
            (is_valid: bool, dataset: Dataset|None, metrics: ParsingMetrics|None, errors: List[str])

        Notes
        -----
        Validation steps:
        1. Format validation (file structure)
        2. Content validation (non-empty samples, valid KOs)
        3. Domain validation (Dataset.validate())

        Examples
        --------
        >>> handler = UploadHandler()
        >>> content = ">Sample1\\nK00001"
        >>> is_valid, dataset, metrics, errors = handler.validate_and_parse(content)
        >>> is_valid
        True
        """
        errors = []

        # Step 1: Validate raw input format
        is_valid, error_msg = self._validation_service.validate_raw_input(content)
        if not is_valid:
            return False, None, None, [error_msg]

        # Step 2: Parse into entities
        try:
            dataset, metrics = self._parser.parse(content)
        except ValueError as e:
            return False, None, None, [f"Parsing error: {str(e)}"]

        # Step 3: Domain-level validation
        try:
            dataset.validate()
        except ValueError as e:
            return False, None, None, [f"Validation error: {str(e)}"]

        return True, dataset, metrics, []
