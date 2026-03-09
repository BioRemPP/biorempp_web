import time
from typing import Optional

from src.application.dto.processing_progress_dto import ProcessingProgressDTO


class ProgressTracker:
    """
    Simplified progress tracker for multi-stage processing.

    This class tracks progress across 8 weighted processing stages without
    threading complexity, designed specifically for single-threaded Dash.

    Parameters
    ----------
    session_id : str
        Unique session identifier for tracking

    Attributes
    ----------
    session_id : str
        Session identifier
    _stages : Dict[int, str]
        Stage number to description mapping
    _stage_weights : Dict[int, float]
        Stage number to weight mapping (sums to 100.0)
    _current_stage : int
        Current stage number (1-8)
    _current_message : str
        Current processing message
    _start_time : float
        Timestamp when processing started
    _error : Optional[str]
        Error message if processing failed

    Methods
    -------
    start_stage(stage: int, stage_name: str, message: str)
        Start a new processing stage
    update_progress(progress: float, message: Optional[str])
        Update progress within current stage
    complete()
        Mark processing as complete
    set_error(error: str)
        Set error message and halt progress
    get_progress() -> ProcessingProgressDTO
        Get current progress as DTO
    calculate_overall_progress() -> float
        Calculate weighted overall progress

    Notes
    -----
    **8 Processing Stages with Weights:**
    1. Input Validation (5%)
    2. Data Parsing (10%)
    3. BioRemPP Merge (30%)
    4. KEGG Merge (20%)
    5. HADEG Merge (15%)
    6. ToxCSM Merge (10%)
    7. Result Preparation (5%)
    8. Finalization (5%)

    **Simplifications from Legacy:**
    - NO threading.Lock (single-threaded Dash)
    - NO callback notifications (handled externally)
    - Simple dict storage instead of complex state machine
    - Weighted progress calculation preserved

    Examples
    --------
    >>> tracker = ProgressTracker("session_1")
    >>> tracker.start_stage(1, "Validation", "Validating input")
    >>> tracker.update_progress(50.0, "Checked 3/5 samples")
    >>> progress = tracker.get_progress()
    'Validation'
    """

    # Stage definitions (8 stages)
    STAGES = {
        1: "Input Validation",
        2: "Data Parsing",
        3: "BioRemPP Database Merge",
        4: "KEGG Database Merge",
        5: "HADEG Database Merge",
        6: "ToxCSM Database Merge",
        7: "Result Preparation",
        8: "Finalization",
    }

    # Stage weights (must sum to 100.0)
    STAGE_WEIGHTS = {
        1: 5.0,  # Validation - fast
        2: 10.0,  # Parsing - fast
        3: 30.0,  # BioRemPP - largest database
        4: 20.0,  # KEGG - medium
        5: 15.0,  # HADEG - medium
        6: 10.0,  # ToxCSM - smaller
        7: 5.0,  # Preparation - fast
        8: 5.0,  # Finalization - fast
    }

    TOTAL_STAGES = 8

    def __init__(self, session_id: str) -> None:
        """
        Initialize simplified progress tracker.

        Parameters
        ----------
        session_id : str
            Unique session identifier
        """
        self.session_id = session_id
        self._stages = self.STAGES
        self._stage_weights = self.STAGE_WEIGHTS
        self._current_stage = 0
        self._current_message = ""
        self._stage_progress = 0.0  # Progress within current stage (0-100)
        self._start_time = time.time()
        self._error: Optional[str] = None

    def start_stage(self, stage: int, stage_name: str, message: str = "") -> None:
        """
        Start a new processing stage.

        Parameters
        ----------
        stage : int
            Stage number (1-8)
        stage_name : str
            Stage description (optional, uses default if empty)
        message : str, default=""
            Initial stage message

        Raises
        ------
        ValueError
            If stage number is invalid

        Examples
        --------
        >>> tracker = ProgressTracker("session_1")
        >>> tracker.start_stage(1, "Validation", "Starting validation")
        """
        if stage < 1 or stage > self.TOTAL_STAGES:
            raise ValueError(
                f"Invalid stage number: {stage} (must be 1-{self.TOTAL_STAGES})"
            )

        self._current_stage = stage
        self._current_message = message
        self._stage_progress = 0.0

    def update_progress(self, progress: float, message: Optional[str] = None) -> None:
        """
        Update progress within current stage.

        Parameters
        ----------
        progress : float
            Progress percentage within stage (0.0-100.0)
        message : Optional[str]
            Optional progress message

        Raises
        ------
        ValueError
            If progress is out of range

        Examples
        --------
        >>> tracker.start_stage(3, "Merge", "Merging data")
        >>> tracker.update_progress(50.0, "Processed 500/1000 records")
        """
        if not 0.0 <= progress <= 100.0:
            raise ValueError("Progress must be between 0.0 and 100.0")

        self._stage_progress = progress
        if message is not None:
            self._current_message = message

    def complete(self) -> None:
        """
        Mark processing as complete (100%).

        Examples
        --------
        >>> tracker.complete()
        >>> tracker.get_progress().is_complete()
        True
        """
        self._current_stage = self.TOTAL_STAGES
        self._stage_progress = 100.0
        self._current_message = "Processing complete"

    def set_error(self, error: str) -> None:
        """
        Set error message and halt progress.

        Parameters
        ----------
        error : str
            Error description

        Examples
        --------
        >>> tracker.set_error("Database connection failed")
        >>> tracker.get_progress().has_error()
        True
        """
        self._error = error
        self._current_message = f"Error: {error}"

    def get_progress(self) -> ProcessingProgressDTO:
        """
        Get current progress as DTO.

        Returns
        -------
        ProcessingProgressDTO
            Current progress information

        Examples
        --------
        >>> tracker.start_stage(3, "Merge", "Processing")
        >>> tracker.update_progress(50.0)
        >>> dto = tracker.get_progress()
        >>> dto.current_stage
        'BioRemPP Database Merge'
        """
        overall_progress = self.calculate_overall_progress()
        estimated_time = self._calculate_estimated_time(overall_progress)

        stage_name = (
            self._stages.get(self._current_stage, "Unknown")
            if self._current_stage > 0
            else "Not Started"
        )

        return ProcessingProgressDTO(
            current_stage=stage_name,
            stage_number=max(1, self._current_stage),
            total_stages=self.TOTAL_STAGES,
            progress_percentage=overall_progress,
            message=self._current_message,
            estimated_time_remaining=estimated_time,
            error=self._error,
        )

    def calculate_overall_progress(self) -> float:
        """
        Calculate weighted overall progress across all stages.

        Returns
        -------
        float
            Overall progress percentage (0.0-100.0)

        Notes
        -----
        Formula: Σ(completed_stages_weights) + (current_stage_weight * stage_progress%)

        Examples
        --------
        >>> tracker.start_stage(3, "Merge", "Processing")
        >>> tracker.update_progress(50.0)  # 50% of stage 3
        >>> overall = tracker.calculate_overall_progress()
        >>> # Stages 1-2 complete (15%) + 50% of stage 3 (15% of 30%)
        >>> round(overall, 1)
        30.0
        """
        if self._current_stage == 0:
            return 0.0

        # Sum weights of completed stages
        completed_weight = sum(
            self._stage_weights[s]
            for s in range(1, self._current_stage)
            if s in self._stage_weights
        )

        # Add progress of current stage
        current_stage_weight = self._stage_weights.get(self._current_stage, 0.0)
        current_contribution = current_stage_weight * self._stage_progress / 100.0

        total_progress = completed_weight + current_contribution

        return min(100.0, total_progress)  # Cap at 100%

    def _calculate_estimated_time(self, current_progress: float) -> Optional[float]:
        """
        Calculate estimated time remaining.

        Parameters
        ----------
        current_progress : float
            Current progress percentage

        Returns
        -------
        Optional[float]
            Estimated seconds remaining (None if cannot estimate)
        """
        if current_progress <= 0.0:
            return None

        elapsed = time.time() - self._start_time
        if elapsed < 1.0:  # Too early to estimate
            return None

        # Linear extrapolation
        estimated_total = elapsed / (current_progress / 100.0)
        remaining = estimated_total - elapsed

        return max(0.0, remaining)
