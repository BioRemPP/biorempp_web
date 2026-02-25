"""Unit tests for resume-by-job-id elements on homepage layout."""

from typing import Any

from src.presentation.pages.home_page import create_home_layout


def _collect_component_ids(node: Any) -> set[str]:
    """Collect string IDs recursively from Dash component tree."""
    ids: set[str] = set()

    def visit(value: Any) -> None:
        if value is None:
            return
        if isinstance(value, (list, tuple)):
            for item in value:
                visit(item)
            return
        component_id = getattr(value, "id", None)
        if isinstance(component_id, str):
            ids.add(component_id)
        children = getattr(value, "children", None)
        if children is not None:
            visit(children)

    visit(node)
    return ids


def test_home_layout_includes_resume_browser_token_store():
    """Homepage should expose local store for browser ownership token."""
    layout = create_home_layout()
    component_ids = _collect_component_ids(layout)

    assert "resume-browser-token-store" in component_ids


def test_home_layout_includes_resume_panel_components():
    """Homepage should expose resume input, action button, and feedback area."""
    layout = create_home_layout()
    component_ids = _collect_component_ids(layout)

    assert "resume-job-id-input" in component_ids
    assert "resume-job-btn" in component_ids
    assert "resume-job-status" in component_ids

