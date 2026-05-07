"""Unit tests for workflow modal content helpers."""

from pathlib import Path

from typing import Any

from src.presentation.pages.methods.methods_service import get_methods_service
from src.presentation.pages.methods.workflow_docs import (
    USE_CASE_DOCS_BASE_URL,
    build_use_case_docs_url,
)
from src.presentation.pages.methods.workflow_modal import _build_workflow_body_children


def _find_first_href(node: Any) -> str | None:
    """Recursively find the first component href in a Dash component tree."""
    if node is None:
        return None
    if isinstance(node, (list, tuple)):
        for item in node:
            href = _find_first_href(item)
            if href is not None:
                return href
        return None

    href = getattr(node, "href", None)
    if isinstance(href, str):
        return href

    children = getattr(node, "children", None)
    if children is None:
        return None
    return _find_first_href(children)


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


def test_build_use_case_docs_url_supports_dotted_and_hyphenated_ids() -> None:
    """Documentation URLs should follow the shared Read the Docs pattern."""
    assert (
        build_use_case_docs_url("UC-1.1")
        == "https://biorempp-web.readthedocs.io/en/stable/use_cases/module1/uc_1.1/"
    )
    assert (
        build_use_case_docs_url("uc-2-5")
        == "https://biorempp-web.readthedocs.io/en/stable/use_cases/module2/uc_2.5/"
    )
    assert build_use_case_docs_url("invalid-id") is None


def test_build_workflow_body_children_appends_official_docs_link() -> None:
    """Workflow modal body should include the official use case docs link."""
    body = _build_workflow_body_children(
        {
            "use_case_id": "UC-2.1",
            "title": "Example Workflow",
            "steps": [
                {
                    "step_number": 1,
                    "name": "Load data",
                    "description": "Open inputs.",
                }
            ],
        }
    )

    assert (
        _find_first_href(body)
        == "https://biorempp-web.readthedocs.io/en/stable/use_cases/module2/uc_2.1/"
    )
    assert "View complete Use Case documentation" in _flatten_text(body)


def test_all_configured_workflows_render_valid_official_docs_links() -> None:
    """Every configured workflow should resolve to an official docs page."""
    repo_root = Path(__file__).resolve().parents[4]
    docs_root = repo_root / "docs" / "use_cases"
    workflows = get_methods_service().load_workflows()

    assert len(workflows) == 56

    for workflow in workflows.values():
        use_case_id = workflow.get("use_case_id")
        expected_url = build_use_case_docs_url(use_case_id)

        assert expected_url is not None, f"Missing docs URL for {use_case_id}"

        body = _build_workflow_body_children(workflow)
        assert _find_first_href(body) == expected_url
        assert "View complete Use Case documentation" in _flatten_text(body)

        relative_path = expected_url.removeprefix(f"{USE_CASE_DOCS_BASE_URL}/").strip(
            "/"
        )
        module_name, use_case_slug = relative_path.split("/")
        docs_path = docs_root / module_name / f"{use_case_slug}.md"
        assert docs_path.exists(), f"Missing docs file for {use_case_id}: {docs_path}"
