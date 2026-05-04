"""Smoke tests for Module 1 use case layout composition."""

from typing import Any, Callable

import dash_bootstrap_components as dbc
import pytest

from src.presentation.layouts.module1 import (
    create_uc_1_1_layout,
    create_uc_1_2_layout,
    create_uc_1_3_layout,
    create_uc_1_4_layout,
    create_uc_1_5_layout,
    create_uc_1_6_layout,
)


def _find_first_component(node: Any, component_type: type) -> Any | None:
    """Recursively find first component instance of the requested type."""
    if node is None:
        return None
    if isinstance(node, component_type):
        return node
    if isinstance(node, (list, tuple)):
        for item in node:
            found = _find_first_component(item, component_type)
            if found is not None:
                return found
        return None

    children = getattr(node, "children", None)
    if children is None:
        return None
    return _find_first_component(children, component_type)


@pytest.mark.parametrize(
    ("factory", "use_case_id"),
    [
        (create_uc_1_1_layout, "uc-1-1"),
        (create_uc_1_2_layout, "uc-1-2"),
        (create_uc_1_3_layout, "uc-1-3"),
        (create_uc_1_4_layout, "uc-1-4"),
        (create_uc_1_5_layout, "uc-1-5"),
        (create_uc_1_6_layout, "uc-1-6"),
    ],
)
def test_module1_layout_places_info_panel_before_results(
    factory: Callable[[], dbc.Card], use_case_id: str
) -> None:
    """Each Module 1 card should keep the info panel before the results accordion."""
    layout = factory()
    body = _find_first_component(layout, dbc.CardBody)

    assert body is not None

    child_ids = [getattr(child, "id", None) for child in body.children]

    assert f"{use_case_id}-info-panel" in child_ids
    assert f"{use_case_id}-accordion-group" in child_ids
    assert child_ids.index(f"{use_case_id}-info-panel") < child_ids.index(
        f"{use_case_id}-accordion-group"
    )
