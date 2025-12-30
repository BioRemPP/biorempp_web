"""
Sample Parser - Convert raw input to domain entities.

This module provides functionality to parse raw input data (text format)
into domain entities (Dataset with Samples). It handles the transformation
from string content to structured domain objects.

Classes
-------
SampleParser
    Parses text-formatted input into Dataset entities
ParsingMetrics
    Stores parsing statistics and warnings

Examples
--------
>>> parser = SampleParser()
>>> content = ">Sample1\\nK00001\\nK00002\\n>Sample2\\nK00003"
>>> dataset, metrics = parser.parse(content)
"""

import logging
from dataclasses import dataclass, field
from typing import List, Optional, Set, Tuple

from config.settings import get_settings
from src.domain.entities.dataset import Dataset
from src.domain.entities.sample import Sample
from src.domain.services.sanitization_service import SanitizationService
from src.domain.value_objects.kegg_orthology import KO
from src.domain.value_objects.sample_id import SampleId
from src.shared.exceptions import (
    InvalidFormatError,
    KOLimitExceededError,
    SampleLimitExceededError,
)
from src.shared.logging import get_logger

logger = get_logger(__name__)
settings = get_settings()

# Get configuration from centralized settings
MAX_SAMPLES = settings.PARSING_MAX_SAMPLES
MAX_KOS_PER_SAMPLE = settings.PARSING_MAX_KOS_PER_SAMPLE
MAX_TOTAL_KOS = settings.PARSING_MAX_TOTAL_KOS


@dataclass
class ParsingMetrics:
    """
    Stores metrics and warnings from parsing operation.

    Attributes
    ----------
    total_samples : int
        Total samples successfully parsed
    total_kos : int
        Total KO IDs successfully parsed
    ignored_kos : int
        Number of invalid KO IDs ignored
    duplicate_samples : int
        Number of duplicate sample names found
    sanitized_names : int
        Number of sample names that were sanitized
    warnings : List[str]
        List of warning messages
    """

    total_samples: int = 0
    total_kos: int = 0
    ignored_kos: int = 0
    duplicate_samples: int = 0
    sanitized_names: int = 0
    warnings: List[str] = field(default_factory=list)


class SampleParser:
    """
    Parse raw text input into domain entities with robust error handling.

    This class converts text-formatted input into structured domain
    entities (Dataset containing Sample entities with KO value objects).
    Implements defensive programming with comprehensive validation and
    metrics tracking.

    Methods
    -------
    parse(content: str) -> Tuple[Dataset, ParsingMetrics]
        Parse content into Dataset with metrics
    parse_samples(content: str, metrics: ParsingMetrics) -> List[Sample]
        Parse content into list of Sample entities
    validate_format(content: str) -> Tuple[bool, str]
        Validate format structure

    Notes
    -----
    Expected format:
    >SampleID
    K00001
    K00002
    >AnotherSample
    K00003

    Limits (from config.settings):
    - Max samples: PARSING_MAX_SAMPLES (default: 100)
    - Max KOs per sample: PARSING_MAX_KOS_PER_SAMPLE (default: 10,000)
    - Max total KOs: PARSING_MAX_TOTAL_KOS (default: 500,000)

    Examples
    --------
    >>> parser = SampleParser()
    >>> content = ">Sample1\\nK00001\\nK00002"
    >>> dataset, metrics = parser.parse(content)
    """

    def __init__(self) -> None:
        """Initialize SampleParser."""
        self._seen_sample_names: Set[str] = set()
        logger.info("SampleParser initialized")

    def parse(self, content: str) -> Tuple[Dataset, ParsingMetrics]:
        """
        Parse text content into Dataset entity with metrics.

        Parameters
        ----------
        content : str
            Text-formatted input content

        Returns
        -------
        Tuple[Dataset, ParsingMetrics]
            Dataset and parsing metrics

        Raises
        ------
        ValueError
            If content is empty or format is invalid
        SampleLimitExceededError
            If number of samples exceeds limit
        KOLimitExceededError
            If number of KOs exceeds limit

        Examples
        --------
        >>> parser = SampleParser()
        >>> content = ">S1\\nK00001\\n>S2\\nK00002"
        >>> dataset, metrics = parser.parse(content)
        >>> dataset.total_samples
        2
        """
        logger.info("Starting content parsing")

        if not content or not content.strip():
            logger.error("Empty content provided for parsing")
            raise ValueError("Content cannot be empty")

        # Validate format first
        is_valid, error_msg = self.validate_format(content)
        if not is_valid:
            logger.error(
                f"Format validation failed: {error_msg}", extra={"error": error_msg}
            )
            raise InvalidFormatError(f"Invalid format: {error_msg}")

        # Initialize metrics
        metrics = ParsingMetrics()
        self._seen_sample_names.clear()

        # Parse samples
        try:
            samples = self.parse_samples(content, metrics)
            logger.info(
                f"Parsing completed: {len(samples)} samples, "
                f"{metrics.total_kos} KOs, "
                f"{metrics.ignored_kos} ignored KOs",
                extra={
                    "samples": len(samples),
                    "kos": metrics.total_kos,
                    "ignored_kos": metrics.ignored_kos,
                    "duplicates": metrics.duplicate_samples,
                    "sanitized": metrics.sanitized_names,
                },
            )
        except (SampleLimitExceededError, KOLimitExceededError) as e:
            logger.error(f"Parsing limit exceeded: {str(e)}")
            raise

        # Create and return dataset
        dataset = Dataset()
        for sample in samples:
            dataset.add_sample(sample)

        # Update metrics
        metrics.total_samples = len(samples)

        return dataset, metrics

    def parse_samples(self, content: str, metrics: ParsingMetrics) -> List[Sample]:
        """
        Parse content into list of Sample entities with validation.

        Parameters
        ----------
        content : str
            Text-formatted content
        metrics : ParsingMetrics
            Metrics object to track parsing statistics

        Returns
        -------
        List[Sample]
            List of parsed Sample entities

        Raises
        ------
        SampleLimitExceededError
            If sample limit exceeded
        KOLimitExceededError
            If KO limit exceeded

        Notes
        -----
        Lines starting with '>' are sample headers.
        Following lines are KO identifiers until next header.
        Invalid KOs are logged and counted but not added.

        Examples
        --------
        >>> parser = SampleParser()
        >>> metrics = ParsingMetrics()
        >>> samples = parser.parse_samples(">S1\\nK00001\\nK00002", metrics)
        >>> len(samples)
        1
        """
        samples: List[Sample] = []
        current_sample: Optional[Sample] = None
        line_number = 0
        total_ko_count = 0

        for line in content.splitlines():
            line_number += 1
            line = line.strip()

            # Skip empty lines
            if not line:
                continue

            # Sample header line
            if line.startswith(">"):
                # Check sample limit
                if len(samples) >= MAX_SAMPLES:
                    error_msg = (
                        f"Sample limit exceeded: {MAX_SAMPLES} max "
                        f"(found {len(samples) + 1})"
                    )
                    logger.error(error_msg, extra={"max_samples": MAX_SAMPLES})
                    raise SampleLimitExceededError(error_msg)

                # Save previous sample if exists
                if current_sample is not None:
                    samples.append(current_sample)

                # Extract and sanitize sample name
                sample_name = line[1:].strip()
                original_name = sample_name

                # Sanitize sample name
                is_valid, sanitized, error = SanitizationService.sanitize_sample_name(
                    sample_name
                )

                if not is_valid:
                    logger.warning(
                        f"Line {line_number}: Invalid sample name ignored",
                        extra={
                            "line": line_number,
                            "sample_name": original_name,
                            "error": error,
                        },
                    )
                    metrics.warnings.append(f"Line {line_number}: {error}")
                    current_sample = None
                    continue

                # Check for sanitization
                if sanitized != original_name:
                    metrics.sanitized_names += 1
                    logger.debug(
                        f"Sample name sanitized: '{original_name}' " f"→ '{sanitized}'"
                    )

                # Check for duplicates
                if sanitized in self._seen_sample_names:
                    metrics.duplicate_samples += 1
                    logger.warning(
                        f"Duplicate sample name: '{sanitized}'",
                        extra={"sample_name": sanitized},
                    )
                    metrics.warnings.append(f"Duplicate sample name: '{sanitized}'")
                    # Continue parsing but mark as duplicate
                else:
                    self._seen_sample_names.add(sanitized)

                # Create new sample
                try:
                    current_sample = Sample(id=SampleId(sanitized))
                except ValueError as e:
                    logger.warning(
                        f"Line {line_number}: Invalid sample ID: {e}",
                        extra={"line": line_number, "error": str(e)},
                    )
                    current_sample = None
                    continue

            # KO line
            elif current_sample is not None:
                # Check per-sample KO limit
                if current_sample.ko_count >= MAX_KOS_PER_SAMPLE:
                    logger.warning(
                        f"Sample '{current_sample.id}' exceeds KO limit "
                        f"({MAX_KOS_PER_SAMPLE}), skipping remaining KOs"
                    )
                    metrics.warnings.append(
                        f"Sample '{current_sample.id}' exceeded "
                        f"KO limit ({MAX_KOS_PER_SAMPLE})"
                    )
                    continue

                # Check total KO limit
                if total_ko_count >= MAX_TOTAL_KOS:
                    error_msg = f"Total KO limit exceeded: {MAX_TOTAL_KOS} max"
                    logger.error(error_msg)
                    raise KOLimitExceededError(error_msg)

                # Try to parse KO
                try:
                    ko = KO(line)
                    current_sample.add_ko(ko)
                    total_ko_count += 1
                    metrics.total_kos += 1
                except ValueError as e:
                    # Invalid KO - log and count but continue
                    metrics.ignored_kos += 1
                    logger.debug(
                        f"Line {line_number}: Invalid KO ignored: {line}",
                        extra={"line": line_number, "ko_value": line, "error": str(e)},
                    )

        # Add last sample
        if current_sample is not None:
            samples.append(current_sample)

        # Log summary warnings if significant issues found
        if metrics.ignored_kos > 0:
            logger.warning(
                f"Ignored {metrics.ignored_kos} invalid KO IDs during parsing"
            )
            metrics.warnings.append(
                f"{metrics.ignored_kos} invalid KO IDs were ignored"
            )

        if metrics.duplicate_samples > 0:
            logger.warning(f"Found {metrics.duplicate_samples} duplicate sample names")

        return samples

    def validate_format(self, content: str) -> Tuple[bool, str]:
        """
        Validate file format structure.

        Parameters
        ----------
        content : str
            Content to validate

        Returns
        -------
        Tuple[bool, str]
            (is_valid, error_message) - error_message empty if valid

        Notes
        -----
        Checks for:
        - At least one sample header (line starting with '>')
        - Content after headers

        Examples
        --------
        >>> parser = SampleParser()
        >>> is_valid, msg = parser.validate_format(">S1\\nK00001")
        >>> is_valid
        True

        >>> is_valid, msg = parser.validate_format("K00001")
        >>> is_valid
        False
        """
        if not content or not content.strip():
            return False, "Content is empty"

        lines = [line.strip() for line in content.splitlines() if line.strip()]

        # Check for at least one sample header
        has_header = any(line.startswith(">") for line in lines)
        if not has_header:
            return False, "No sample headers found (lines starting with '>')"

        # Check for content after headers
        non_header_lines = [line for line in lines if not line.startswith(">")]
        if not non_header_lines:
            return False, "No KO entries found after sample headers"

        return True, ""
