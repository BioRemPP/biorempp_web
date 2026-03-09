"""Unit tests for results page dynamic database overview rendering."""

from typing import Any

from src.presentation.pages.results_page import create_results_layout


def _flatten_text(node: Any) -> str:
    """Extract plain text recursively from Dash component trees."""
    fragments = []

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


def _collect_titles(node: Any) -> list[str]:
    """Collect `title` attributes recursively from Dash component trees."""
    titles = []

    def visit(value: Any) -> None:
        if value is None:
            return
        if isinstance(value, (list, tuple)):
            for item in value:
                visit(item)
            return
        title = getattr(value, "title", None)
        if isinstance(title, str):
            titles.append(title)
        children = getattr(value, "children", None)
        if children is not None:
            visit(children)

    visit(node)
    return titles


def _collect_ids(node: Any) -> set[str]:
    """Collect component ids recursively from Dash component trees."""
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


def _build_overview_payload() -> dict:
    """Build complete overview payload used by the four database cards."""
    return {
        "biorempp": {
            "enzyme_compound_relations": {"input_value": 1, "global_value": 10},
            "environmental_compounds": {"input_value": 2, "global_value": 11},
            "compound_classes": {"input_value": 3, "global_value": 12},
            "regulatory_frameworks": {"input_value": 4, "global_value": 13},
        },
        "hadeg": {
            "gene_pathway_relations": {"input_value": 5, "global_value": 14},
            "unique_ko_numbers": {"input_value": 6, "global_value": 15},
            "degradation_pathways": {"input_value": 7, "global_value": 16},
            "compound_categories": {"input_value": 8, "global_value": 17},
        },
        "toxcsm": {
            "environmental_compounds": {"input_value": 9, "global_value": 18},
            "toxicity_endpoints": {"input_value": 10, "global_value": 19},
            "toxicity_categories": {"input_value": 11, "global_value": 20},
        },
        "kegg": {
            "gene_pathway_associations": {"input_value": 12, "global_value": 21},
            "unique_ko_numbers": {"input_value": 13, "global_value": 22},
            "degradation_pathways": {"input_value": 14, "global_value": 23},
        },
    }


def _build_aggregate_payload() -> dict:
    """Build aggregate overview payload for top results card."""
    return {
        "total_relations_input": 27,
        "active_databases": 3,
        "total_databases": 4,
        "ko_match_rate_pct": 66.67,
        "matched_kos": 2,
        "total_kos": 3,
        "per_database": {
            "biorempp": {"input_relations": 5, "share_pct": 18.52},
            "hadeg": {"input_relations": 6, "share_pct": 22.22},
            "toxcsm": {"input_relations": 7, "share_pct": 25.93},
            "kegg": {"input_relations": 9, "share_pct": 33.33},
        },
    }


def _build_merged_data(metadata: dict) -> dict:
    """Build minimal merged_data payload accepted by `create_results_layout`."""
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


def test_results_page_renders_global_values_from_database_overview():
    """Results page should render per-database cards and top aggregate metrics."""
    metadata = {
        "sample_count": 2,
        "ko_count": 3,
        "processing_time": 0.25,
        "job_id": "BRP-20260225-101010-ABCDEF",
        "database_overview": _build_overview_payload(),
        "database_aggregate_overview": _build_aggregate_payload(),
    }
    layout = create_results_layout(merged_data=_build_merged_data(metadata))

    text = _flatten_text(layout)
    titles = _collect_titles(layout)

    assert "KO-Compound Relations" in text
    assert "Job ID" in text
    assert "BRP-20260225-101010-ABCDEF" in text
    assert "Integrated Relations" in text
    assert "Databases with Matches" in text
    assert "KO Match Rate" in text
    assert "27" in text
    assert "3/4" in text
    assert "66.67%" in text
    assert "BioRemPP: 5 (18.5%)" in text
    assert "HADEG: 6 (22.2%)" in text
    assert "ToxCSM: 7 (25.9%)" in text
    assert "KEGG: 9 (33.3%)" in text
    assert "Database reference value:" not in text
    assert titles.count("Refrence database value") == 10


def test_results_page_fallback_renders_placeholder_when_overview_missing():
    """Results page should keep cards stable with placeholders on old sessions."""
    metadata = {
        "sample_count": 2,
        "ko_count": 3,
        "processing_time": 0.25,
    }
    layout = create_results_layout(merged_data=_build_merged_data(metadata))

    text = _flatten_text(layout)
    titles = _collect_titles(layout)

    assert "--" in text
    assert "Integrated Relations" in text
    assert "Databases with Matches" in text
    assert "KO Match Rate" in text
    assert "BioRemPP: --" in text
    assert "HADEG: --" in text
    assert "ToxCSM: --" in text
    assert "KEGG: --" in text
    assert titles.count("Refrence database value") == 10


def test_results_page_fallback_builds_aggregate_from_database_overview():
    """When aggregate key is missing, top card should derive values from overview."""
    metadata = {
        "sample_count": 2,
        "ko_count": 3,
        "processing_time": 0.25,
        "matched_kos": 2,
        "total_kos": 3,
        "database_overview": _build_overview_payload(),
    }
    layout = create_results_layout(merged_data=_build_merged_data(metadata))

    text = _flatten_text(layout)

    assert "Integrated Relations" in text
    assert "27" in text
    assert "4/4" in text
    assert "66.67%" in text
    assert "BioRemPP: 1 (3.7%)" in text
    assert "HADEG: 5 (18.5%)" in text
    assert "ToxCSM: 9 (33.3%)" in text
    assert "KEGG: 12 (44.4%)" in text


def test_results_page_shows_job_id_placeholder_when_missing():
    """Results page should render Job ID placeholder for legacy sessions."""
    metadata = {
        "sample_count": 2,
        "ko_count": 3,
        "processing_time": 0.25,
        "database_overview": _build_overview_payload(),
        "database_aggregate_overview": _build_aggregate_payload(),
    }
    layout = create_results_layout(merged_data=_build_merged_data(metadata))
    text = _flatten_text(layout)

    assert "Job ID" in text
    assert "--" in text


def test_results_page_includes_global_workflow_modal_ids():
    """Results layout should include single global workflow modal components."""
    metadata = {"sample_count": 1, "ko_count": 1, "processing_time": 0.1}
    layout = create_results_layout(merged_data=_build_merged_data(metadata))
    ids = _collect_ids(layout)

    assert "results-workflow-modal" in ids
    assert "results-workflow-modal-title" in ids
    assert "results-workflow-modal-body" in ids
    assert "results-workflow-modal-close" in ids
