"""Unit tests for module description accordion defaults."""

from typing import Any

import dash_bootstrap_components as dbc

from src.presentation.components.module_descriptions.module1_description import (
    create_module1_description,
)


def _find_first_accordion(node: Any) -> dbc.Accordion | None:
    """Recursively find first dbc.Accordion in component tree."""
    if node is None:
        return None
    if isinstance(node, dbc.Accordion):
        return node
    if isinstance(node, (list, tuple)):
        for item in node:
            found = _find_first_accordion(item)
            if found is not None:
                return found
        return None

    children = getattr(node, "children", None)
    if children is None:
        return None
    return _find_first_accordion(children)


def test_module_description_questions_start_collapsed() -> None:
    """Guiding questions accordion should start fully collapsed."""
    layout = create_module1_description()
    accordion = _find_first_accordion(layout)

    assert accordion is not None
    assert getattr(accordion, "start_collapsed", None) is True
    assert getattr(accordion, "active_item", None) == []
