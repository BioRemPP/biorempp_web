"""Unit tests for ProcessingProgressDTO."""

import pytest

from src.application.dto.processing_progress_dto import ProcessingProgressDTO


class TestProcessingProgressDTOValidation:
    """Validation rules for ProcessingProgressDTO."""

    def test_valid_dto_creation(self):
        """A valid DTO should be created successfully."""
        dto = ProcessingProgressDTO(
            current_stage="BioRemPP Database Merge",
            stage_number=3,
            total_stages=8,
            progress_percentage=42.5,
            message="Processing...",
            estimated_time_remaining=12.3,
            error=None,
        )

        assert dto.stage_number == 3
        assert dto.total_stages == 8
        assert dto.progress_percentage == 42.5

    @pytest.mark.parametrize("stage_number,total_stages", [(0, 8), (9, 8), (-1, 8)])
    def test_stage_number_must_be_within_bounds(self, stage_number, total_stages):
        """Stage number must be between 1 and total_stages."""
        with pytest.raises(ValueError, match="stage_number must be between"):
            ProcessingProgressDTO(
                current_stage="Stage",
                stage_number=stage_number,
                total_stages=total_stages,
                progress_percentage=10.0,
            )

    @pytest.mark.parametrize("progress", [-0.1, 100.1])
    def test_progress_percentage_must_be_between_0_and_100(self, progress):
        """Progress percentage must be inside [0, 100]."""
        with pytest.raises(ValueError, match="progress_percentage must be between"):
            ProcessingProgressDTO(
                current_stage="Stage",
                stage_number=1,
                total_stages=8,
                progress_percentage=progress,
            )

    def test_total_stages_must_be_at_least_one(self):
        """total_stages cannot be zero or negative."""
        with pytest.raises(ValueError, match="total_stages must be at least 1"):
            ProcessingProgressDTO(
                current_stage="Stage",
                stage_number=1,
                total_stages=0,
                progress_percentage=0.0,
            )

    def test_estimated_time_cannot_be_negative(self):
        """estimated_time_remaining must not be negative."""
        with pytest.raises(ValueError, match="estimated_time_remaining cannot be negative"):
            ProcessingProgressDTO(
                current_stage="Stage",
                stage_number=1,
                total_stages=8,
                progress_percentage=10.0,
                estimated_time_remaining=-1.0,
            )


class TestProcessingProgressDTOHelpers:
    """Helper method behavior for ProcessingProgressDTO."""

    def test_is_complete_true_when_progress_is_100(self):
        """is_complete should return True at 100%."""
        dto = ProcessingProgressDTO(
            current_stage="Finalization",
            stage_number=8,
            total_stages=8,
            progress_percentage=100.0,
        )

        assert dto.is_complete() is True

    def test_has_error_true_when_error_is_present(self):
        """has_error should return True when error text exists."""
        dto = ProcessingProgressDTO(
            current_stage="Data Parsing",
            stage_number=2,
            total_stages=8,
            progress_percentage=15.0,
            error="Parsing failed",
        )

        assert dto.has_error() is True

    def test_is_final_stage_true_on_last_stage(self):
        """is_final_stage should return True on final stage number."""
        dto = ProcessingProgressDTO(
            current_stage="Finalization",
            stage_number=8,
            total_stages=8,
            progress_percentage=90.0,
        )

        assert dto.is_final_stage() is True
