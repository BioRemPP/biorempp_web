"""Smoke tests for Module 4 use case layout composition."""

from typing import Any, Callable

import dash_bootstrap_components as dbc
import pytest

from src.presentation.layouts.module4 import (
    create_uc_4_1_layout,
    create_uc_4_2_layout,
    create_uc_4_3_layout,
    create_uc_4_4_layout,
    create_uc_4_5_layout,
    create_uc_4_6_layout,
    create_uc_4_7_layout,
    create_uc_4_8_layout,
    create_uc_4_9_layout,
    create_uc_4_10_layout,
    create_uc_4_11_layout,
    create_uc_4_12_layout,
    create_uc_4_13_layout,
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
        (create_uc_4_1_layout, "uc-4-1"),
        (create_uc_4_2_layout, "uc-4-2"),
        (create_uc_4_3_layout, "uc-4-3"),
        (create_uc_4_4_layout, "uc-4-4"),
        (create_uc_4_5_layout, "uc-4-5"),
        (create_uc_4_6_layout, "uc-4-6"),
        (create_uc_4_7_layout, "uc-4-7"),
        (create_uc_4_8_layout, "uc-4-8"),
        (create_uc_4_9_layout, "uc-4-9"),
        (create_uc_4_10_layout, "uc-4-10"),
        (create_uc_4_11_layout, "uc-4-11"),
        (create_uc_4_12_layout, "uc-4-12"),
        (create_uc_4_13_layout, "uc-4-13"),
    ],
)
def test_module4_layout_places_info_panel_before_results(
    factory: Callable[[], dbc.Card], use_case_id: str
) -> None:
    """Each Module 4 card should keep the info panel before the results accordion."""
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
