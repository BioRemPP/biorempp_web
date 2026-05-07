"""Unit tests for the use case panel component."""

from typing import Any

from dash import html

from src.presentation.components.base.use_case_panel import create_use_case_panel


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


def _collect_h6_texts(node: Any) -> list[str]:
    """Collect H6 heading texts in traversal order."""
    headings: list[str] = []

    def visit(value: Any) -> None:
        if value is None:
            return
        if isinstance(value, (list, tuple)):
            for item in value:
                visit(item)
            return
        if isinstance(value, html.H6):
            headings.append(" ".join(_flatten_text(value).split()))
        children = getattr(value, "children", None)
        if children is not None:
            visit(children)

    visit(node)
    return headings


def test_create_use_case_panel_renders_limitations_in_expected_order() -> None:
    """Panel should render Limitations as the fifth section when provided."""
    panel = create_use_case_panel(
        use_case_id="uc-test-1",
        scientific_question="What changed?",
        description="Panel description.",
        visual_elements=[{"label": "Axis", "description": "Axis description"}],
        interpretation_guidelines=["Interpretive context."],
        limitations=[
            "Methodological limitation: Example constraint.",
            "Visualization limitation: Example display caveat.",
            "Interpretive limitation: Example inference boundary.",
        ],
    )

    headings = _collect_h6_texts(panel)
    text = _flatten_text(panel)

    assert headings == [
        "Scientific Question",
        "Description",
        "Visual Elements",
        "Interpretation",
        "Limitations",
    ]
    assert "Methodological limitation: Example constraint." in text
    assert "Visualization limitation: Example display caveat." in text
    assert "Interpretive limitation: Example inference boundary." in text


def test_create_use_case_panel_omits_limitations_when_absent() -> None:
    """Panel should remain backward compatible when limitations are missing."""
    panel = create_use_case_panel(
        use_case_id="uc-test-2",
        scientific_question="What changed?",
        description="Panel description.",
        visual_elements=[{"label": "Axis", "description": "Axis description"}],
        interpretation_guidelines=["Interpretive context."],
    )

    headings = _collect_h6_texts(panel)
    text = _flatten_text(panel)

    assert headings == [
        "Scientific Question",
        "Description",
        "Visual Elements",
        "Interpretation",
    ]
    assert "Limitations" not in text
