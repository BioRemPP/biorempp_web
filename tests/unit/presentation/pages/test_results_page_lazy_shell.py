"""Unit tests for /results shell + lazy module rendering."""

from typing import Any

from src.presentation.pages.results_page import (
    get_results_module_layout,
    get_results_shell_layout,
)


def _collect_ids(node: Any) -> set[str]:
    """Collect component ids recursively from Dash component tree."""
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


def _build_merged_data(metadata: dict[str, Any]) -> dict[str, Any]:
    """Build minimal merged_data payload accepted by results layout."""
    return {
        "biorempp_df": [],
        "biorempp_raw_df": [],
        "hadeg_df": [],
        "hadeg_raw_df": [],
        "toxcsm_df": [],
        "toxcsm_raw_df": [],
        "kegg_df": [],
        "kegg_raw_df": [],
        "metadata": metadata,
    }


def test_results_shell_renders_selector_and_dynamic_container_only():
    """Shell mode should expose selector/container and skip eager module mount."""
    metadata = {
        "sample_count": 2,
        "ko_count": 3,
        "processing_time": 0.25,
        "database_overview": {},
    }
    layout = get_results_shell_layout(merged_data=_build_merged_data(metadata))
    ids = _collect_ids(layout)

    assert "results-module-selector" in ids
    assert "results-module-container" in ids
    assert "results-module-spinner" not in ids
    assert "module1-section" not in ids
    assert "module8-section" not in ids


def test_get_results_module_layout_maps_requested_module():
    """Dynamic module factory should return selected module root section."""
    module4 = get_results_module_layout(4)
    module8 = get_results_module_layout(8)

    assert getattr(module4, "id", None) == "module4-section"
    assert getattr(module8, "id", None) == "module8-section"


def test_get_results_module_layout_fallbacks_to_module1_when_invalid():
    """Invalid module values should fallback to module 1 to keep behavior stable."""
    fallback = get_results_module_layout("invalid")
    assert getattr(fallback, "id", None) == "module1-section"
