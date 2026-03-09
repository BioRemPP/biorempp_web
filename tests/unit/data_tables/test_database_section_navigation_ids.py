"""Ensure database sections expose stable navigation anchor IDs."""

from __future__ import annotations

from typing import Any

from src.data_tables.biorempp_table import create_biorempp_section
from src.data_tables.hadeg_table import create_hadeg_section
from src.data_tables.kegg_table import create_kegg_section
from src.data_tables.toxcsm_table import create_toxcsm_section


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


def test_database_sections_expose_navigation_anchor_ids() -> None:
    component_ids = set()
    component_ids.update(_collect_ids(create_biorempp_section()))
    component_ids.update(_collect_ids(create_hadeg_section()))
    component_ids.update(_collect_ids(create_toxcsm_section()))
    component_ids.update(_collect_ids(create_kegg_section()))

    assert "biorempp-section" in component_ids
    assert "hadeg-section" in component_ids
    assert "toxcsm-section" in component_ids
    assert "kegg-section" in component_ids
