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


def _find_component_by_id(node: Any, target_id: str) -> Any:
    """Find first component by ID in Dash component tree."""
    found = None

    def visit(value: Any) -> None:
        nonlocal found
        if found is not None or value is None:
            return
        if isinstance(value, (list, tuple)):
            for item in value:
                visit(item)
            return
        if getattr(value, "id", None) == target_id:
            found = value
            return
        children = getattr(value, "children", None)
        if children is not None:
            visit(children)

    visit(node)
    return found


def _collect_text(node: Any) -> str:
    """Collect textual children recursively into a single string."""
    chunks: list[str] = []

    def visit(value: Any) -> None:
        if value is None:
            return
        if isinstance(value, str):
            chunks.append(value)
            return
        if isinstance(value, (list, tuple)):
            for item in value:
                visit(item)
            return
        children = getattr(value, "children", None)
        if children is not None:
            visit(children)

    visit(node)
    return " ".join(chunks)


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


def test_home_layout_resume_input_has_security_constraints():
    """Resume input should enforce length and format constraints in UI."""
    layout = create_home_layout()
    resume_input = _find_component_by_id(layout, "resume-job-id-input")

    assert resume_input is not None
    assert getattr(resume_input, "maxLength", None) == 26
    assert getattr(resume_input, "pattern", None) == r"BRP-\d{8}-\d{6}-[A-F0-9]{6}"


def test_home_layout_does_not_include_reviewer_disclaimer_components():
    """Homepage should not expose deprecated reviewer disclaimer UI IDs."""
    layout = create_home_layout()
    component_ids = _collect_component_ids(layout)
    removed_prefix = "reviewer"

    assert f"{removed_prefix}-disclaimer-btn" not in component_ids
    assert f"{removed_prefix}-disclaimer-modal" not in component_ids
    assert f"{removed_prefix}-disclaimer-close" not in component_ids


def test_home_layout_resume_panel_mentions_same_browser_and_ttl():
    """Resume panel should communicate same-browser and TTL constraints."""
    layout = create_home_layout()
    content = _collect_text(layout)

    assert "same browser profile" in content
    assert "available for up to" in content


def test_home_layout_includes_example_dataset_quick_actions():
    """Homepage should expose quick actions for sample data info and download."""
    layout = create_home_layout()
    component_ids = _collect_component_ids(layout)

    assert "sample-data-card" in component_ids
    assert "sample-data-download-btn" in component_ids
    assert "sample-data-modal" in component_ids


def test_home_layout_other_links_keeps_contact_and_publications_only():
    """Other Links section should no longer render the old example dataset tile."""
    layout = create_home_layout()
    content = _collect_text(layout)

    assert "Contact Support" in content
    assert "Publications and Awards" in content
    assert "Exemple Dataset" not in content
