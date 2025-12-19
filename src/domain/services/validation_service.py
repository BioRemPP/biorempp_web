"""
Validation Service.

Domain service for complex business validations.

Classes
-------
ValidationService
    Static methods for validating datasets, samples, and file inputs
"""

import logging
from typing import List, Tuple

from src.shared.logging import get_logger, log_execution

from ..entities.dataset import Dataset
from ..value_objects.kegg_orthology import KO

# Logger for this module
logger = get_logger(__name__)


class ValidationService:
    """
    Domain service for complex validations.

    Implements validation rules that involve multiple entities
    or business logic that does not belong to a specific entity.

    Notes
    -----
    This is a Domain Service that encapsulates complex validation
    logic, keeping the entities simple and focused. All methods are
    static and stateless.
    """

    @staticmethod
    @log_execution(level=logging.INFO)
    def validate_raw_input(content: str) -> Tuple[bool, str]:
        """
        Validate raw content from sample upload.

        Parameters
        ----------
        content : str
            Content of the samples file in BioRemPP format

        Returns
        -------
        Tuple[bool, str]
            Tuple (is_valid, error_message) where is_valid is True if
            the content is valid, and error_message contains the
            error description if any

        Notes
        -----
        Expected format:
        - Lines starting with '>' indicate the start of a new sample
        - Lines starting with 'K' are KO entries
        """
        if not content or not content.strip():
            logger.warning("Validation failed: Empty file content")
            return False, "Empty file content"

        lines = content.strip().split("\n")

        # Must have at least 1 sample and 1 KO
        if len(lines) < 2:
            logger.warning(
                "Validation failed: Insufficient content",
                extra={"line_count": len(lines)},
            )
            return (
                False,
                "File must contain at least one sample and one KO",
            )

        # First line must be a sample (starts with '>')
        first_line = lines[0].strip()
        if not first_line.startswith(">"):
            logger.warning(
                "Validation failed: Invalid first line format",
                extra={"first_line": first_line[:50]},
            )
            return (
                False,
                "File must start with sample identifier (>SampleName)",
            )

        # Validate structure line by line
        sample_count = 0
        ko_count = 0
        line_number = 0

        for line in lines:
            line_number += 1
            line = line.strip()

            if not line:
                continue

            if line.startswith(">"):
                sample_count += 1
                # Check if sample name is not empty
                sample_name = line[1:].strip()
                if not sample_name:
                    error_msg = f"Line {line_number}: Sample name cannot be empty"
                    logger.warning(
                        "Validation failed: Empty sample name",
                        extra={"line_number": line_number},
                    )
                    return (
                        False,
                        error_msg,
                    )

            elif line.startswith("K"):
                ko_count += 1
                # Validate KO format
                try:
                    KO(line.strip())
                except ValueError as e:
                    error_msg = f"Line {line_number}: {str(e)}"
                    logger.warning(
                        "Validation failed: Invalid KO format",
                        extra={
                            "line_number": line_number,
                            "ko_value": line.strip(),
                            "error": str(e),
                        },
                    )
                    return (
                        False,
                        error_msg,
                    )

            else:
                error_msg = f"Line {line_number}: Invalid line format: {line}"
                logger.warning(
                    "Validation failed: Invalid line format",
                    extra={"line_number": line_number, "line_content": line[:50]},
                )
                return (
                    False,
                    error_msg,
                )

        if sample_count == 0:
            logger.warning("Validation failed: No samples found in file")
            return False, "No samples found in file"

        if ko_count == 0:
            logger.warning("Validation failed: No KO entries found in file")
            return False, "No KO entries found in file"

        logger.info(
            "Raw input validation successful",
            extra={
                "sample_count": sample_count,
                "ko_count": ko_count,
                "total_lines": len(lines),
            },
        )
        return True, ""

    @staticmethod
    @log_execution(level=logging.INFO)
    def validate_dataset(dataset: Dataset) -> Tuple[bool, str]:
        """
        Validate a complete dataset.

        Parameters
        ----------
        dataset : Dataset
            Dataset to be validated

        Returns
        -------
        Tuple[bool, str]
            Tuple (is_valid, error_message)

        Notes
        -----
        Validates both the dataset structure and each sample
        individually, ensuring complete consistency.
        """
        if dataset.total_samples == 0:
            logger.warning("Dataset validation failed: No samples in dataset")
            return False, "Dataset has no samples"

        logger.debug(
            "Validating dataset", extra={"sample_count": dataset.total_samples}
        )

        # Validate each sample
        for sample in dataset.samples:
            try:
                sample.validate()
            except ValueError as e:
                logger.warning(
                    "Dataset validation failed: Invalid sample",
                    extra={"sample_id": str(sample.id), "error": str(e)},
                )
                return False, str(e)

        logger.info(
            "Dataset validation successful",
            extra={
                "sample_count": dataset.total_samples,
                "total_ko_count": sum(len(s.ko_list) for s in dataset.samples),
            },
        )
        return True, ""

    @staticmethod
    @log_execution(level=logging.DEBUG)
    def validate_ko_list(ko_list: List[str]) -> Tuple[bool, str, List[KO]]:
        """
        Validate and convert a list of strings to a list of KOs.

        Parameters
        ----------
        ko_list : List[str]
            List of strings representing KOs

        Returns
        -------
        Tuple[bool, str, List[KO]]
            Tuple (is_valid, error_message, ko_objects) where ko_objects
            contains the validated KOs if successful

        Notes
        -----
        This method is useful for validating user inputs
        before creating domain entities.
        """
        if not ko_list:
            logger.warning("KO list validation failed: Empty list")
            return False, "KO list cannot be empty", []

        logger.debug("Validating KO list", extra={"ko_count": len(ko_list)})

        validated_kos = []
        for idx, ko_str in enumerate(ko_list):
            try:
                ko = KO(ko_str.strip())
                validated_kos.append(ko)
            except ValueError as e:
                logger.warning(
                    "KO list validation failed: Invalid KO",
                    extra={"index": idx, "ko_value": ko_str, "error": str(e)},
                )
                return False, str(e), []

        logger.info(
            "KO list validation successful",
            extra={"validated_count": len(validated_kos)},
        )
        return True, "", validated_kos

    @staticmethod
    @log_execution(level=logging.DEBUG)
    def check_duplicate_samples(dataset: Dataset) -> Tuple[bool, List[str]]:
        """
        Check for duplicate samples in the dataset.

        Parameters
        ----------
        dataset : Dataset
            Dataset to be checked

        Returns
        -------
        Tuple[bool, List[str]]
            Tuple (has_duplicates, duplicate_ids) where has_duplicates
            is True if there are duplicates, and duplicate_ids contains
            the duplicate IDs

        Notes
        -----
        Duplicate samples may indicate an error in the input file
        or incorrect processing.
        """
        logger.debug(
            "Checking for duplicate samples",
            extra={"total_samples": dataset.total_samples},
        )

        seen_ids = set()
        duplicates = []

        for sample in dataset.samples:
            sample_id_str = str(sample.id)
            if sample_id_str in seen_ids:
                duplicates.append(sample_id_str)
            seen_ids.add(sample_id_str)

        has_duplicates = len(duplicates) > 0

        if has_duplicates:
            logger.warning(
                "Duplicate samples found",
                extra={"duplicate_count": len(duplicates), "duplicate_ids": duplicates},
            )
        else:
            logger.debug("No duplicate samples found")

        return has_duplicates, duplicates

    @staticmethod
    @log_execution(level=logging.DEBUG)
    def validate_file_size(size_bytes: int, max_bytes: int) -> Tuple[bool, str]:
        """
        Validate file size against maximum limit.

        Parameters
        ----------
        size_bytes : int
            File size in bytes
        max_bytes : int
            Maximum allowed size in bytes

        Returns
        -------
        Tuple[bool, str]
            Tuple (is_valid, error_message)

        Notes
        -----
        Provides user-friendly error messages with sizes in MB.
        Logs validation failures with detailed context.
        """
        if size_bytes > max_bytes:
            size_mb = size_bytes / (1024 * 1024)
            max_mb = max_bytes / (1024 * 1024)
            error_msg = (
                f"File size ({size_mb:.2f} MB) exceeds maximum "
                f"allowed size ({max_mb:.0f} MB)"
            )
            logger.warning(
                "File size validation failed",
                extra={
                    "size_bytes": size_bytes,
                    "size_mb": size_mb,
                    "max_bytes": max_bytes,
                    "max_mb": max_mb,
                },
            )
            return False, error_msg

        logger.debug(
            "File size validation passed",
            extra={"size_bytes": size_bytes, "max_bytes": max_bytes},
        )
        return True, ""

    @staticmethod
    @log_execution(level=logging.DEBUG)
    def validate_sample_count(sample_count: int, max_samples: int) -> Tuple[bool, str]:
        """
        Validate number of samples against maximum limit.

        Parameters
        ----------
        sample_count : int
            Number of samples in dataset
        max_samples : int
            Maximum allowed samples

        Returns
        -------
        Tuple[bool, str]
            Tuple (is_valid, error_message)

        Notes
        -----
        Provides clear error messages when limit is exceeded.
        Logs validation context for debugging.
        """
        if sample_count > max_samples:
            error_msg = (
                f"Number of samples ({sample_count}) exceeds maximum "
                f"allowed ({max_samples})"
            )
            logger.warning(
                "Sample count validation failed",
                extra={"sample_count": sample_count, "max_samples": max_samples},
            )
            return False, error_msg

        logger.debug(
            "Sample count validation passed",
            extra={"sample_count": sample_count, "max_samples": max_samples},
        )
        return True, ""

    @staticmethod
    @log_execution(level=logging.DEBUG)
    def validate_ko_count(ko_count: int, max_kos: int) -> Tuple[bool, str]:
        """
        Validate number of KO entries against maximum limit.

        Parameters
        ----------
        ko_count : int
            Number of KO entries in dataset
        max_kos : int
            Maximum allowed KO entries

        Returns
        -------
        Tuple[bool, str]
            Tuple (is_valid, error_message)

        Notes
        -----
        Formats large numbers with commas for readability.
        Logs detailed context for validation failures.
        """
        if ko_count > max_kos:
            error_msg = (
                f"Number of KO entries ({ko_count:,}) exceeds maximum "
                f"allowed ({max_kos:,})"
            )
            logger.warning(
                "KO count validation failed",
                extra={"ko_count": ko_count, "max_kos": max_kos},
            )
            return False, error_msg

        logger.debug(
            "KO count validation passed",
            extra={"ko_count": ko_count, "max_kos": max_kos},
        )
        return True, ""

    @staticmethod
    @log_execution(level=logging.DEBUG)
    def validate_encoding(content_bytes: bytes) -> Tuple[bool, str, str]:
        """
        Validate and decode file content encoding.

        Attempts UTF-8 decoding first, falls back to latin-1 if needed.

        Parameters
        ----------
        content_bytes : bytes
            Raw file content

        Returns
        -------
        Tuple[bool, str, str]
            Tuple (is_valid, decoded_content, error_message)
            - is_valid: True if decoding succeeded
            - decoded_content: Decoded string (empty if failed)
            - error_message: Error description (empty if successful)

        Notes
        -----
        Encoding priority:
        1. UTF-8 (preferred)
        2. Latin-1 (fallback)

        Logs warnings when fallback encoding is used.
        Returns user-friendly error messages.
        """
        # Try UTF-8 first
        try:
            decoded = content_bytes.decode("utf-8")
            logger.debug("Content decoded as UTF-8")
            return True, decoded, ""
        except UnicodeDecodeError as e:
            logger.warning(f"UTF-8 decoding failed: {e}", extra={"error": str(e)})

        # Try latin-1 as fallback
        try:
            decoded = content_bytes.decode("latin-1")
            logger.warning(
                "Content decoded as latin-1 (not UTF-8)", extra={"encoding": "latin-1"}
            )
            return True, decoded, ""
        except UnicodeDecodeError as e:
            error_msg = "Unable to decode file. Please ensure file is UTF-8 encoded."
            logger.error(f"All encoding attempts failed: {e}", extra={"error": str(e)})
            return False, "", error_msg
