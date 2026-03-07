"""Unit tests for global /results workflow modal callback logic."""

from typing import Any

import pytest
from dash import no_update
from dash.exceptions import PreventUpdate

from src.presentation.callbacks import results_workflow_modal_callbacks as workflow_cb


def _flatten_text(node: Any) -> str:
    """Extract plain text recursively from Dash component trees."""
    fragments: list[str] = []

    def visit(value: Any) -> None:
        if value is None:
            return
        if isinstance(value, (str, int, float)):
            fragments.append(str(value))
            return
        if isinstance(value, (list, tuple)):
            for item in value:
                visit(item)
            return
        children = getattr(value, "children", None)
        if children is not None:
            visit(children)

    visit(node)
    return " ".join(fragments)


def test_is_results_path_accepts_plain_and_base_prefixed_path():
    """Route guard should match /results and reject non-results routes."""
    assert workflow_cb._is_results_path("/results") is True
    assert workflow_cb._is_results_path("/methods") is False


def test_resolve_results_workflow_modal_close_returns_closed_state():
    """Close trigger should close modal and preserve title/body."""
    is_open, title, body = workflow_cb.resolve_results_workflow_modal_update(
        trigger="results-workflow-modal-close",
        trigger_value=None,
        close_n_clicks=1,
        pathname="/results",
    )

    assert is_open is False
    assert title is no_update
    assert body is no_update


def test_resolve_results_workflow_modal_close_without_click_raises():
    """Close trigger without clicks should not update."""
    with pytest.raises(PreventUpdate):
        workflow_cb.resolve_results_workflow_modal_update(
            trigger="results-workflow-modal-close",
            trigger_value=None,
            close_n_clicks=0,
            pathname="/results",
        )


def test_resolve_results_workflow_modal_requires_results_route():
    """Methods clicks outside /results should be ignored."""
    with pytest.raises(PreventUpdate):
        workflow_cb.resolve_results_workflow_modal_update(
            trigger={"type": "results-methods-link", "index": "UC-2.1"},
            trigger_value=1,
            close_n_clicks=None,
            pathname="/methods",
        )


def test_resolve_results_workflow_modal_fallback_when_workflow_missing(monkeypatch):
    """Missing workflow should show user-facing warning in modal body."""

    class _Service:
        @staticmethod
        def get_workflow(_):
            return None

    monkeypatch.setattr(workflow_cb, "get_methods_service", lambda: _Service())

    is_open, title, body = workflow_cb.resolve_results_workflow_modal_update(
        trigger={"type": "results-methods-link", "index": "UC-9.9"},
        trigger_value=1,
        close_n_clicks=None,
        pathname="/results",
    )

    assert is_open is True
    assert "UC-9.9" in _flatten_text(title)
    assert "not available" in _flatten_text(body).lower()


def test_resolve_results_workflow_modal_opens_for_valid_workflow(monkeypatch):
    """Valid workflow payload should render global modal title/body content."""

    class _Service:
        @staticmethod
        def get_workflow(_):
            return {
                "use_case_id": "UC-2.1",
                "title": "KO Richness",
                "steps": [
                    {
                        "step_number": 1,
                        "name": "Load data",
                        "description": "Open sample table and prepare inputs.",
                        "keywords": ["KO", "Sample"],
                    }
                ],
            }

    monkeypatch.setattr(workflow_cb, "get_methods_service", lambda: _Service())

    is_open, title, body = workflow_cb.resolve_results_workflow_modal_update(
        trigger={"type": "results-methods-link", "index": "UC-2.1"},
        trigger_value=1,
        close_n_clicks=None,
        pathname="/results",
    )

    body_text = _flatten_text(body)
    assert is_open is True
    assert "UC-2.1" in _flatten_text(title)
    assert "KO Richness" in _flatten_text(title)
    assert "Load data" in body_text
    assert "analytical steps" in body_text


def test_resolve_results_workflow_modal_ignores_non_clicked_trigger():
    """Mount/hydration triggers with n_clicks=0/None should be ignored."""
    with pytest.raises(PreventUpdate):
        workflow_cb.resolve_results_workflow_modal_update(
            trigger={"type": "results-methods-link", "index": "UC-1.1"},
            trigger_value=0,
            close_n_clicks=None,
            pathname="/results",
        )
