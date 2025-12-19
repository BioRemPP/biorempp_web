"""
Data Processor - Orchestrate Data Processing and Merge Operations.

Provides the main orchestrator for processing user data, coordinating dataset
merging with multiple databases, and preparing results. Acts as the central
coordinator for the entire processing pipeline.

Implements defensive programming with try/except per stage, circuit breaker,
DataFrame validation, timeout handling, retry logic, and structured logging.
All settings are loaded from config.settings and can be overridden via
environment variables.

Classes
-------
DataProcessor
    Orchestrates multi-stage data processing workflow
CircuitBreaker
    Simple circuit breaker for fault tolerance
"""

import signal
import time
from contextlib import contextmanager
from typing import Any, Callable, Dict, Optional

import pandas as pd

from config.settings import get_settings
from src.application.dto.merged_data_dto import MergedDataDTO
from src.application.services.cache_service import CacheService
from src.application.services.progress_tracker import ProgressTracker
from src.domain.entities.dataset import Dataset
from src.domain.services.merge_service import MergeService
from src.shared.exceptions import (
    CircuitBreakerOpenError,
    DataProcessingTimeoutError,
    EmptyDataFrameError,
    RetryExhaustedError,
    StageProcessingError,
)
from src.shared.logging import get_logger, log_performance

logger = get_logger(__name__)
settings = get_settings()

# Get configuration from centralized settings
DEFAULT_TIMEOUT_SECONDS = settings.PROCESSING_TIMEOUT_SECONDS
MAX_RETRIES = settings.PROCESSING_MAX_RETRIES
RETRY_DELAY_SECONDS = settings.PROCESSING_RETRY_DELAY_SECONDS
CIRCUIT_BREAKER_THRESHOLD = settings.PROCESSING_CIRCUIT_BREAKER_THRESHOLD
CIRCUIT_BREAKER_TIMEOUT = settings.PROCESSING_CIRCUIT_BREAKER_TIMEOUT


class CircuitBreaker:
    """
    Simple circuit breaker to prevent cascading failures.

    Attributes
    ----------
    failure_threshold : int
        Number of failures before opening circuit
    timeout : int
        Seconds before attempting to close circuit
    failures : int
        Current failure count
    last_failure_time : float
        Timestamp of last failure
    is_open : bool
        Whether circuit is currently open
    """

    def __init__(
        self,
        failure_threshold: int = CIRCUIT_BREAKER_THRESHOLD,
        timeout: int = CIRCUIT_BREAKER_TIMEOUT,
    ):
        """Initialize circuit breaker."""
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failures = 0
        self.last_failure_time: Optional[float] = None
        self._is_open = False

    @property
    def is_open(self) -> bool:
        """Check if circuit is open."""
        if self._is_open:
            # Check if timeout has passed
            if (
                self.last_failure_time
                and time.time() - self.last_failure_time > self.timeout
            ):
                logger.info("Circuit breaker timeout elapsed, attempting reset")
                self._is_open = False
                self.failures = 0
                return False
            return True
        return False

    def record_failure(self) -> None:
        """Record a failure."""
        self.failures += 1
        self.last_failure_time = time.time()

        if self.failures >= self.failure_threshold:
            self._is_open = True
            logger.error(
                f"Circuit breaker opened after {self.failures} failures",
                extra={"failures": self.failures},
            )

    def record_success(self) -> None:
        """Record a success."""
        self.failures = 0
        self._is_open = False


@contextmanager
def timeout_handler(seconds: int = DEFAULT_TIMEOUT_SECONDS):
    """
    Context manager for timeout handling.

    Parameters
    ----------
    seconds : int
        Timeout in seconds

    Raises
    ------
    DataProcessingTimeoutError
        If operation exceeds timeout

    Notes
    -----
    - Uses signal.alarm for Unix-like systems
    - For Windows, timeout is advisory only
    """

    def timeout_signal_handler(signum, frame):
        raise DataProcessingTimeoutError(f"Operation timed out after {seconds} seconds")

    # Set timeout (Unix-like systems only)
    try:
        old_handler = signal.signal(signal.SIGALRM, timeout_signal_handler)
        signal.alarm(seconds)
    except (AttributeError, ValueError):
        # Windows or signal not available - log warning
        logger.warning("Signal-based timeout not available on this platform")
        old_handler = None

    try:
        yield
    finally:
        # Cancel alarm
        try:
            signal.alarm(0)
            if old_handler:
                signal.signal(signal.SIGALRM, old_handler)
        except (AttributeError, ValueError):
            pass


class DataProcessor:
    """
    Orchestrate data processing with robust error handling.

    Coordinates the entire processing pipeline including cache checking,
    progress tracking, database merging, and result preparation with
    defensive programming practices.

    Parameters
    ----------
    cache_service : CacheService
        Service for caching merge results
    progress_tracker : ProgressTracker
        Tracker for progress updates
    merge_service : Optional[MergeService]
        Domain merge service (uses default if None)
    timeout_seconds : int
        Timeout for processing operations (default: 60)

    Attributes
    ----------
    _cache : CacheService
        Cache service instance
    _tracker : ProgressTracker
        Progress tracker instance
    _merge_service : MergeService
        Domain merge service
    _timeout_seconds : int
        Timeout for operations
    _circuit_breakers : dict
        Circuit breakers for each database

    Methods
    -------
    process(dataset, session_id)
        Process dataset through full pipeline
    _merge_with_retry(merge_func, **kwargs)
        Execute merge with retry logic
    _validate_dataframe(df, name)
        Validate DataFrame is not empty

    Notes
    -----
    Processing pipeline with error handling:
    1. Cache check
    2. BioRemPP merge (with retry + circuit breaker)
    3. KEGG merge (with retry + circuit breaker)
    4. HADEG merge (with retry + circuit breaker)
    5. ToxCSM merge (with retry + circuit breaker)
    6. Result preparation + validation
    7. Cache storage

    Uses dependency injection for testability.
    """

    def __init__(
        self,
        cache_service: CacheService,
        progress_tracker: ProgressTracker,
        merge_service: Optional[MergeService] = None,
        timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS,
    ) -> None:
        """
        Initialize DataProcessor with dependencies.

        Parameters
        ----------
        cache_service : CacheService
            Cache service for merge results
        progress_tracker : ProgressTracker
            Progress tracker for UI updates
        merge_service : Optional[MergeService]
            Merge service (uses default if None)
        timeout_seconds : int
            Timeout for operations
        """
        self._cache = cache_service
        self._tracker = progress_tracker
        self._merge_service = (
            merge_service if merge_service is not None else MergeService
        )
        self._timeout_seconds = timeout_seconds

        # Circuit breakers for each database
        self._circuit_breakers = {
            "biorempp": CircuitBreaker(),
            "kegg": CircuitBreaker(),
            "hadeg": CircuitBreaker(),
            "toxcsm": CircuitBreaker(),
        }

        logger.info("DataProcessor initialized", extra={"timeout": timeout_seconds})

    @log_performance()
    def process(self, dataset: Dataset, session_id: str) -> MergedDataDTO:
        """
        Process dataset through complete pipeline with error handling.

        Parameters
        ----------
        dataset : Dataset
            Validated dataset to process
        session_id : str
            Session identifier for tracking

        Returns
        -------
        MergedDataDTO
            Result DTO with merged data

        Raises
        ------
        DataProcessingTimeoutError
            If processing exceeds timeout
        StageProcessingError
            If a critical stage fails

        Notes
        -----
        Pipeline stages with error handling:
        1. Check cache
        2. BioRemPP merge (critical - with retry)
        3. KEGG merge (with retry)
        4. HADEG merge (with retry)
        5. ToxCSM merge (with retry)
        6. Result preparation + validation
        7. Cache storage
        """
        logger.info(
            f"Starting processing for session: {session_id}",
            extra={"session_id": session_id},
        )
        start_time = time.time()

        try:
            # Use timeout context
            with timeout_handler(self._timeout_seconds):
                # Generate cache key
                cache_key = self._generate_cache_key(dataset)

                # Check cache
                cached_result = self._cache.get(cache_key)
                if cached_result is not None:
                    logger.info(
                        "Cache hit - returning cached result",
                        extra={"cache_key": str(cache_key)[:16]},
                    )
                    self._tracker.complete()
                    return cached_result

                logger.info("Cache miss - proceeding with processing")

                # Initialize result dictionary
                merge_results = {}

                # Stage 3: BioRemPP Merge (CRITICAL)
                merge_results["biorempp_df"] = self._process_stage(
                    stage_num=3,
                    stage_name="BioRemPP Database Merge",
                    stage_desc="Merging with main database",
                    merge_func=self._merge_biorempp,
                    dataset=dataset,
                    breaker_key="biorempp",
                )

                # Stage 4: KEGG Merge
                merge_results["kegg_df"] = self._process_stage(
                    stage_num=4,
                    stage_name="KEGG Database Merge",
                    stage_desc="Merging with KEGG pathways",
                    merge_func=self._merge_kegg,
                    biorempp_df=merge_results["biorempp_df"],
                    breaker_key="kegg",
                )

                # Stage 5: HADEG Merge
                merge_results["hadeg_df"] = self._process_stage(
                    stage_num=5,
                    stage_name="HADEG Database Merge",
                    stage_desc="Merging with HADEG",
                    merge_func=self._merge_hadeg,
                    dataset=dataset,
                    breaker_key="hadeg",
                )

                # Stage 6: ToxCSM Merge
                merge_results["toxcsm_df"] = self._process_stage(
                    stage_num=6,
                    stage_name="ToxCSM Database Merge",
                    stage_desc="Merging with ToxCSM",
                    merge_func=self._merge_toxcsm,
                    biorempp_df=merge_results["biorempp_df"],
                    breaker_key="toxcsm",
                )

                # Stage 7: Result Preparation
                logger.info("Starting result preparation")
                self._tracker.start_stage(7, "Result Preparation", "Preparing results")
                self._tracker.update_progress(50.0)

                processing_time = time.time() - start_time
                result_dto = self.prepare_result(
                    merge_results, cache_key, processing_time
                )

                self._tracker.update_progress(100.0)

                # Stage 8: Finalization
                logger.info("Finalizing and caching results")
                self._tracker.start_stage(8, "Finalization", "Caching results")
                self._cache.set(cache_key, result_dto, ttl_seconds=3600)
                self._tracker.complete()

                logger.info(
                    f"Processing completed successfully in {processing_time:.2f}s",
                    extra={
                        "session_id": session_id,
                        "processing_time": processing_time,
                        "match_count": result_dto.match_count,
                    },
                )

                return result_dto

        except DataProcessingTimeoutError as e:
            logger.error(
                f"Processing timeout: {str(e)}", extra={"session_id": session_id}
            )
            self._tracker.complete()
            raise

        except StageProcessingError as e:
            logger.error(
                f"Stage processing failed: {e.stage_name}",
                extra={
                    "session_id": session_id,
                    "stage": e.stage_name,
                    "error": str(e.original_error),
                },
            )
            self._tracker.complete()
            raise

        except Exception as e:
            logger.exception(
                "Unexpected error during processing",
                exc_info=True,
                extra={"session_id": session_id},
            )
            self._tracker.complete()
            raise

    def _process_stage(
        self,
        stage_num: int,
        stage_name: str,
        stage_desc: str,
        merge_func,
        breaker_key: str,
        **kwargs,
    ):
        """
        Process a single stage with error handling.

        Parameters
        ----------
        stage_num : int
            Stage number
        stage_name : str
            Stage name
        stage_desc : str
            Stage description
        merge_func : callable
            Merge function to execute
        breaker_key : str
            Circuit breaker key
        **kwargs
            Arguments for merge function

        Returns
        -------
        pd.DataFrame
            Merge result

        Raises
        ------
        StageProcessingError
            If stage fails after retries
        """
        logger.info(f"Starting stage {stage_num}: {stage_name}")
        self._tracker.start_stage(stage_num, stage_name, stage_desc)

        # Check circuit breaker
        breaker = self._circuit_breakers[breaker_key]
        if breaker.is_open:
            error_msg = f"Circuit breaker open for {breaker_key}, " "skipping stage"
            logger.error(error_msg)
            raise CircuitBreakerOpenError(error_msg)

        try:
            # Execute with retry
            self._tracker.update_progress(10.0, f"Loading {breaker_key} database")
            result = self._merge_with_retry(merge_func, **kwargs)

            # Validate result
            self._validate_dataframe(result, stage_name)

            self._tracker.update_progress(100.0, f"{stage_name} complete")

            # Record success
            breaker.record_success()

            logger.info(
                f"Stage {stage_num} completed",
                extra={"stage": stage_name, "rows": len(result)},
            )

            return result

        except Exception as e:
            # Record failure
            breaker.record_failure()

            logger.error(
                f"Stage {stage_num} failed: {str(e)}",
                extra={"stage": stage_name, "error_type": type(e).__name__},
            )
            raise StageProcessingError(stage_name, e)

    def _merge_with_retry(self, merge_func, **kwargs):
        """
        Execute merge function with retry logic.

        Parameters
        ----------
        merge_func : callable
            Merge function to execute
        **kwargs
            Arguments for merge function

        Returns
        -------
        Any
            Merge result

        Raises
        ------
        RetryExhaustedError
            If all retries fail
        """
        last_exception = None

        for attempt in range(MAX_RETRIES + 1):
            try:
                logger.debug(f"Merge attempt {attempt + 1}/{MAX_RETRIES + 1}")
                result = merge_func(**kwargs)
                return result

            except Exception as e:
                last_exception = e
                logger.warning(
                    f"Merge attempt {attempt + 1} failed: {str(e)}",
                    extra={"attempt": attempt + 1, "error_type": type(e).__name__},
                )

                # Don't retry on last attempt
                if attempt < MAX_RETRIES:
                    logger.info(f"Retrying in {RETRY_DELAY_SECONDS}s...")
                    time.sleep(RETRY_DELAY_SECONDS)

        # All retries exhausted
        logger.error(
            f"All {MAX_RETRIES + 1} retry attempts exhausted",
            extra={"last_error": str(last_exception)},
        )
        raise RetryExhaustedError(
            f"Failed after {MAX_RETRIES + 1} attempts: {last_exception}"
        )

    def _validate_dataframe(self, df: pd.DataFrame, name: str) -> None:
        """
        Validate DataFrame is not empty and has valid data.

        Parameters
        ----------
        df : pd.DataFrame
            DataFrame to validate
        name : str
            Name for error messages

        Raises
        ------
        EmptyDataFrameError
            If DataFrame is empty or invalid
        """
        if df is None:
            raise EmptyDataFrameError(f"{name}: DataFrame is None")

        if not isinstance(df, pd.DataFrame):
            raise EmptyDataFrameError(f"{name}: Result is not a DataFrame")

        if df.empty:
            logger.warning(f"{name}: DataFrame is empty", extra={"stage": name})
            raise EmptyDataFrameError(f"{name}: No data in result")

        if len(df) == 0:
            raise EmptyDataFrameError(f"{name}: Zero rows in DataFrame")

        logger.debug(
            f"{name}: Validation passed",
            extra={"rows": len(df), "columns": len(df.columns)},
        )

    def _merge_biorempp(self, dataset: Dataset) -> pd.DataFrame:
        """Merge with BioRemPP database."""
        input_df = self._dataset_to_dataframe(dataset)
        return self._merge_service.merge_with_biorempp(input_df)

    def _merge_kegg(self, biorempp_df: pd.DataFrame) -> pd.DataFrame:
        """Merge with KEGG database."""
        return self._merge_service.merge_with_kegg(biorempp_df)

    def _merge_hadeg(self, dataset: Dataset) -> pd.DataFrame:
        """Merge with HADEG database."""
        input_df = self._dataset_to_dataframe(dataset)
        return self._merge_service.merge_with_hadeg(input_df)

    def _merge_toxcsm(self, biorempp_df: pd.DataFrame) -> pd.DataFrame:
        """Merge with ToxCSM database."""
        return self._merge_service.merge_with_toxcsm(biorempp_df)

    def prepare_result(
        self, merge_results: dict, cache_key: str, processing_time: float
    ) -> MergedDataDTO:
        """
        Prepare final result DTO from merge results.

        Parameters
        ----------
        merge_results : dict
            Dictionary with merge results
        cache_key : str
            Cache key for this result
        processing_time : float
            Time taken for processing

        Returns
        -------
        MergedDataDTO
            Final result DTO
        """
        biorempp_df = merge_results["biorempp_df"]
        match_count = len(biorempp_df)
        total_records = len(biorempp_df)  # After merge, these are matched records

        return MergedDataDTO(
            biorempp_data=biorempp_df,
            hadeg_data=merge_results.get("hadeg_df"),
            toxcsm_data=merge_results.get("toxcsm_df"),
            match_count=match_count,
            total_records=total_records,
            cache_key=cache_key,
            processing_time_seconds=processing_time,
        )

    def _dataset_to_dataframe(self, dataset: Dataset) -> pd.DataFrame:
        """
        Convert Dataset entity to DataFrame for legacy merge compatibility.

        Parameters
        ----------
        dataset : Dataset
            Dataset entity

        Returns
        -------
        pd.DataFrame
            DataFrame with columns: sample, ko

        Notes
        -----
        Temporary conversion for compatibility with legacy merge functions.
        Will be replaced with entity-based merging in future iterations.
        """
        data = []
        for sample in dataset.samples:
            for ko in sample.ko_list:
                data.append({"sample": str(sample.id), "ko": str(ko)})

        return pd.DataFrame(data, columns=["sample", "ko"])

    def _generate_cache_key(self, dataset: Dataset) -> str:
        """
        Generate cache key from dataset.

        Parameters
        ----------
        dataset : Dataset
            Dataset to hash

        Returns
        -------
        str
            Cache key (hash)

        Notes
        -----
        Uses deterministic hash based on dataset content.
        """
        # Create deterministic string representation
        content_parts = []
        for sample in sorted(dataset.samples, key=lambda s: str(s.id)):
            content_parts.append(f">{sample.id}")
            for ko in sorted(sample.ko_list, key=lambda k: str(k)):
                content_parts.append(str(ko))

        content = "\n".join(content_parts)
        return self._cache.generate_hash_key(content)
