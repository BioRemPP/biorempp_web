"""Smoke tests for Module 2 use case layout composition."""

from typing import Any, Callable

import dash_bootstrap_components as dbc
import pytest

from src.presentation.layouts.module2 import (
    create_uc_2_1_layout,
    create_uc_2_2_layout,
    create_uc_2_3_layout,
    create_uc_2_4_layout,
    create_uc_2_5_layout,
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
        (create_uc_2_1_layout, "uc-2-1"),
        (create_uc_2_2_layout, "uc-2-2"),
        (create_uc_2_3_layout, "uc-2-3"),
        (create_uc_2_4_layout, "uc-2-4"),
        (create_uc_2_5_layout, "uc-2-5"),
    ],
)
def test_module2_layout_places_info_panel_before_results(
    factory: Callable[[], dbc.Card], use_case_id: str
) -> None:
    """Each Module 2 card should keep the info panel before the results accordion."""
    layout = factory()
    body = _find_first_component(layout, dbc.CardBody)

    assert body is not None

    child_ids = [getattr(child, "id", None) for child in body.children]

    accordion_id = (
        f"{use_case_id}-accordion-group"
        if f"{use_case_id}-accordion-group" in child_ids
        else f"{use_case_id}-accordion"
    )

    assert f"{use_case_id}-info-panel" in child_ids
    assert accordion_id in child_ids
    assert child_ids.index(f"{use_case_id}-info-panel") < child_ids.index(
        accordion_id
    )
