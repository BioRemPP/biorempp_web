"""Unit tests for Analysis entity."""

from datetime import datetime, timedelta

import pytest

from src.domain.entities.analysis import Analysis, AnalysisStatus


class TestAnalysis:
    """Tests for analysis lifecycle and validation."""

    def test_default_state_is_pending(self):
        analysis = Analysis(id="UC-2.1", name="Bar chart", category="charts")

        assert analysis.status == AnalysisStatus.PENDING
        assert analysis.started_at is None
        assert analysis.completed_at is None
        assert not analysis.is_completed
        assert not analysis.is_successful

    def test_start_sets_running_status_and_started_at(self):
        analysis = Analysis(id="UC-2.1", name="Bar chart", category="charts")
        analysis.start()

        assert analysis.status == AnalysisStatus.RUNNING
        assert analysis.started_at is not None
        assert analysis.completed_at is None

    def test_complete_sets_completed_status_and_updates_metadata(self):
        analysis = Analysis(id="UC-2.1", name="Bar chart", category="charts")
        analysis.start()
        analysis.complete(metadata={"rows": 123})

        assert analysis.status == AnalysisStatus.COMPLETED
        assert analysis.completed_at is not None
        assert analysis.result_metadata["rows"] == 123
        assert analysis.is_completed
        assert analysis.is_successful

    def test_fail_sets_failed_status_and_error_message(self):
        analysis = Analysis(id="UC-2.1", name="Bar chart", category="charts")
        analysis.start()
        analysis.fail("Database timeout")

        assert analysis.status == AnalysisStatus.FAILED
        assert analysis.error_message == "Database timeout"
        assert analysis.completed_at is not None
        assert analysis.is_completed
        assert not analysis.is_successful

    def test_mark_from_cache_sets_cached_status(self):
        analysis = Analysis(id="UC-2.1", name="Bar chart", category="charts")
        analysis.mark_from_cache()

        assert analysis.status == AnalysisStatus.CACHED
        assert analysis.completed_at is not None
        assert analysis.is_completed
        assert analysis.is_successful

    def test_duration_seconds_none_without_start_or_completion(self):
        analysis = Analysis(id="UC-2.1", name="Bar chart", category="charts")
        assert analysis.duration_seconds is None

    def test_duration_seconds_is_computed_when_started_and_completed(self):
        analysis = Analysis(id="UC-2.1", name="Bar chart", category="charts")
        analysis.started_at = datetime.now() - timedelta(seconds=8)
        analysis.completed_at = datetime.now() - timedelta(seconds=2)

        duration = analysis.duration_seconds

        assert duration is not None
        assert 5.0 <= duration <= 7.0

    @pytest.mark.parametrize(
        "field_name,value,error",
        [
            ("id", " ", "Analysis ID cannot be empty"),
            ("name", "", "Analysis name cannot be empty"),
            ("category", "\t", "Analysis category cannot be empty"),
        ],
    )
    def test_validate_rejects_empty_required_fields(self, field_name, value, error):
        kwargs = {"id": "UC-2.1", "name": "Bar chart", "category": "charts"}
        kwargs[field_name] = value
        analysis = Analysis(**kwargs)

        with pytest.raises(ValueError, match=error):
            analysis.validate()

    def test_str_and_repr_include_core_information(self):
        analysis = Analysis(id="UC-2.1", name="Bar chart", category="charts")

        text = str(analysis)
        rep = repr(analysis)

        assert "UC-2.1" in text
        assert "pending" in text
        assert "Analysis(id='UC-2.1'" in rep
