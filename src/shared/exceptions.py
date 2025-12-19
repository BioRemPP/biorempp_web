"""
Custom Exceptions

Custom exceptions for the BioRemPP domain.
"""


class BioRemPPException(Exception):
    """Base exception for all BioRemPP exceptions."""

    pass


class ValidationError(BioRemPPException):
    """Data validation error."""

    pass


class MergeError(BioRemPPException):
    """Error during a merge operation."""

    pass


class DatabaseNotFoundError(BioRemPPException):
    """Database not found."""

    pass


class InvalidFormatError(ValidationError):
    """Invalid data format."""

    pass


class EmptyDatasetError(ValidationError):
    """Empty dataset or no valid data."""

    pass


class FileSizeExceededError(ValidationError):
    """File size exceeds maximum allowed."""

    pass


class SampleLimitExceededError(ValidationError):
    """Number of samples exceeds maximum allowed."""

    pass


class KOLimitExceededError(ValidationError):
    """Number of KO entries exceeds maximum allowed."""

    pass


class InvalidSampleNameError(ValidationError):
    """Sample name contains invalid characters."""

    pass


class EncodingError(ValidationError):
    """File encoding is invalid or unsupported."""

    pass


class SanitizationError(BioRemPPException):
    """Input sanitization failed."""

    pass


class ProcessingError(BioRemPPException):
    """Error during data processing."""

    pass


class DataProcessingTimeoutError(ProcessingError):
    """Processing operation timed out."""

    pass


class EmptyDataFrameError(ProcessingError):
    """DataFrame is empty or has no valid data."""

    pass


class CircuitBreakerOpenError(ProcessingError):
    """Circuit breaker is open, operation not allowed."""

    pass


class RetryExhaustedError(ProcessingError):
    """All retry attempts exhausted."""

    pass


class StageProcessingError(ProcessingError):
    """Error during a specific processing stage."""

    def __init__(self, stage_name: str, original_error: Exception):
        """Initialize stage processing error."""
        self.stage_name = stage_name
        self.original_error = original_error
        super().__init__(f"Error in stage '{stage_name}': {str(original_error)}")
