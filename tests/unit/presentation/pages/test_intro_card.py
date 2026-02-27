"""Unit tests for homepage intro card content and deprecated UI cleanup."""

from typing import Any

from src.presentation.components.composite.intro_card import create_intro_card


CLAIM_LINES = (
    "This web service is free and open to all users and does not require login.",
    "It is not usable for commercial product claims without experimental confirmation.",
    "See the license page for detailed terms of use.",
)


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


def test_intro_card_has_updated_claim():
    """Intro card should display the updated public claim split by sentence."""
    intro_card = create_intro_card()
    content = _collect_text(intro_card)

    for claim_line in CLAIM_LINES:
        assert claim_line in content


def test_intro_card_does_not_include_reviewer_disclaimer_button():
    """Intro card should not include deprecated reviewer disclaimer button ID."""
    intro_card = create_intro_card()
    component_ids = _collect_component_ids(intro_card)
    removed_prefix = "reviewer"

    assert f"{removed_prefix}-disclaimer-btn" not in component_ids
