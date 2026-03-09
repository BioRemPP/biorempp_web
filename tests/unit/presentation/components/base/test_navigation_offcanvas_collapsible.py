"""Unit tests for collapsible navigation offcanvas component."""

from typing import Any

from src.presentation.components.base.navigation_offcanvas import (
    create_navigation_offcanvas,
)


def _collect_ids(node: Any) -> set[str]:
    ids: set[str] = set()

    def visit(value: Any) -> None:
        if value is None:
            return
        if isinstance(value, (list, tuple)):
            for item in value:
                visit(item)
            return
        node_id = getattr(value, "id", None)
        if isinstance(node_id, str):
            ids.add(node_id)
        children = getattr(value, "children", None)
        if children is not None:
            visit(children)

    visit(node)
    return ids


def test_navigation_offcanvas_uses_collapsible_module_accordion() -> None:
    offcanvas = create_navigation_offcanvas()
    ids = _collect_ids(offcanvas)

    assert "navigation-offcanvas" in ids
    assert "navigation-modules-accordion" in ids


def test_navigation_offcanvas_keeps_core_nav_link_ids() -> None:
    offcanvas = create_navigation_offcanvas()
    ids = _collect_ids(offcanvas)

    assert "nav-biorempp" in ids
    assert "nav-kegg" in ids
    assert "nav-module1" in ids
    assert "nav-module8" in ids
    assert "nav-uc-1-1" in ids
    assert "nav-uc-4-13" in ids
    assert "nav-uc-8-7" in ids

