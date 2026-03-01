"""
Results Page Layout - BioRemPP v1.0.

Display analysis results with feed-style accordion layout.

Functions
---------
create_results_layout
    Create complete results page layout with accordions
"""

from typing import Any, Dict, Optional

import dash_bootstrap_components as dbc
from dash import dcc, html

from src.data_tables import (
    create_biorempp_section,
    create_hadeg_section,
    create_kegg_section,
    create_toxcsm_section,
)

from ..components.base import (
    create_footer,
    create_header,
    create_navigation_button,
    create_navigation_offcanvas,
)
from ..components.composite.analysis_suggestions import (
    create_suggestions_offcanvas,
    create_suggestions_trigger_button,
)
from ..layouts.module_layouts import (
    create_module1_section,
    create_module2_section,
    create_module3_section,
    create_module4_section,
    create_module5_section,
    create_module6_section,
    create_module7_section,
    create_module8_section,
)


DATABASE_RELATION_METRIC_MAP = {
    "biorempp": "enzyme_compound_relations",
    "hadeg": "gene_pathway_relations",
    "toxcsm": "environmental_compounds",
    "kegg": "gene_pathway_associations",
}

DATABASE_LABELS = {
    "biorempp": "BioRemPP",
    "hadeg": "HADEG",
    "toxcsm": "ToxCSM",
    "kegg": "KEGG",
}


def _safe_int(value: Any) -> Optional[int]:
    """Safely parse int values with None fallback."""
    if value is None:
        return None
    if isinstance(value, bool):
        return int(value)
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _safe_float(value: Any) -> Optional[float]:
    """Safely parse float values with None fallback."""
    if value is None:
        return None
    if isinstance(value, bool):
        return float(int(value))
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _extract_input_relation(
    database_overview: Dict[str, Any], db_name: str, metric_name: str
) -> Optional[int]:
    """Extract relation metric from database_overview payload."""
    metric = database_overview.get(db_name, {}).get(metric_name, {})
    if not isinstance(metric, dict):
        return None
    return _safe_int(metric.get("input_value"))


def _build_database_aggregate_overview_fallback(
    database_overview: Dict[str, Any],
    matched_kos: Any,
    total_kos: Any,
) -> Dict[str, Any]:
    """Build aggregate overview from existing metadata when key is missing."""
    per_database: Dict[str, Dict[str, Any]] = {}
    relation_values = []

    for db_name, metric_name in DATABASE_RELATION_METRIC_MAP.items():
        input_relations = _extract_input_relation(database_overview, db_name, metric_name)
        per_database[db_name] = {"input_relations": input_relations, "share_pct": None}
        if input_relations is not None:
            relation_values.append(input_relations)

    total_relations_input = sum(relation_values) if relation_values else None
    active_databases = (
        sum(1 for value in relation_values if value > 0) if relation_values else None
    )
    total_databases = len(DATABASE_RELATION_METRIC_MAP)

    if total_relations_input and total_relations_input > 0:
        for db_name, stats in per_database.items():
            input_relations = stats.get("input_relations")
            if input_relations is None:
                continue
            stats["share_pct"] = round((input_relations / total_relations_input) * 100, 2)

    matched = _safe_int(matched_kos)
    total = _safe_int(total_kos)
    ko_match_rate_pct = None
    if matched is not None and total is not None and total > 0:
        ko_match_rate_pct = round((matched / total) * 100, 2)

    return {
        "total_relations_input": total_relations_input,
        "active_databases": active_databases,
        "total_databases": total_databases,
        "ko_match_rate_pct": ko_match_rate_pct,
        "matched_kos": matched,
        "total_kos": total,
        "per_database": per_database,
    }


def _resolve_database_aggregate_overview(
    metadata: Dict[str, Any], database_overview: Dict[str, Any]
) -> Dict[str, Any]:
    """Resolve aggregate overview from metadata with resilient fallback."""
    fallback = _build_database_aggregate_overview_fallback(
        database_overview=database_overview,
        matched_kos=metadata.get("matched_kos"),
        total_kos=metadata.get("total_kos"),
    )
    aggregate = metadata.get("database_aggregate_overview")
    if not isinstance(aggregate, dict):
        return fallback

    result = {
        "total_relations_input": fallback["total_relations_input"],
        "active_databases": fallback["active_databases"],
        "total_databases": fallback["total_databases"],
        "ko_match_rate_pct": fallback["ko_match_rate_pct"],
        "matched_kos": fallback["matched_kos"],
        "total_kos": fallback["total_kos"],
        "per_database": {
            db_name: {
                "input_relations": stats.get("input_relations"),
                "share_pct": stats.get("share_pct"),
            }
            for db_name, stats in fallback["per_database"].items()
        },
    }

    total_relations_input = _safe_int(aggregate.get("total_relations_input"))
    active_databases = _safe_int(aggregate.get("active_databases"))
    total_databases = _safe_int(aggregate.get("total_databases"))
    ko_match_rate_pct = _safe_float(aggregate.get("ko_match_rate_pct"))
    matched_kos = _safe_int(aggregate.get("matched_kos"))
    total_kos = _safe_int(aggregate.get("total_kos"))

    if total_relations_input is not None:
        result["total_relations_input"] = total_relations_input
    if active_databases is not None:
        result["active_databases"] = active_databases
    if total_databases is not None:
        result["total_databases"] = total_databases
    if ko_match_rate_pct is not None:
        result["ko_match_rate_pct"] = round(ko_match_rate_pct, 2)
    if matched_kos is not None:
        result["matched_kos"] = matched_kos
    if total_kos is not None:
        result["total_kos"] = total_kos

    aggregate_per_database = aggregate.get("per_database", {})
    if isinstance(aggregate_per_database, dict):
        for db_name in DATABASE_RELATION_METRIC_MAP:
            db_stats = aggregate_per_database.get(db_name, {})
            if not isinstance(db_stats, dict):
                continue
            input_relations = _safe_int(db_stats.get("input_relations"))
            share_pct = _safe_float(db_stats.get("share_pct"))
            if input_relations is not None:
                result["per_database"][db_name]["input_relations"] = input_relations
            if share_pct is not None:
                result["per_database"][db_name]["share_pct"] = round(share_pct, 2)

    if result["active_databases"] is None:
        relations = [
            stats.get("input_relations")
            for stats in result["per_database"].values()
            if stats.get("input_relations") is not None
        ]
        if relations:
            result["active_databases"] = sum(1 for value in relations if value > 0)

    if result["total_relations_input"] is None:
        relations = [
            stats.get("input_relations")
            for stats in result["per_database"].values()
            if stats.get("input_relations") is not None
        ]
        if relations:
            result["total_relations_input"] = sum(relations)

    total_relations = result.get("total_relations_input")
    if total_relations and total_relations > 0:
        for db_name in DATABASE_RELATION_METRIC_MAP:
            db_stats = result["per_database"].get(db_name, {})
            input_relations = db_stats.get("input_relations")
            if input_relations is None:
                continue
            if db_stats.get("share_pct") is None:
                db_stats["share_pct"] = round((input_relations / total_relations) * 100, 2)

    if result["ko_match_rate_pct"] is None:
        matched = result.get("matched_kos")
        total = result.get("total_kos")
        if matched is not None and total is not None and total > 0:
            result["ko_match_rate_pct"] = round((matched / total) * 100, 2)

    return result


def _format_integer(value: Optional[int]) -> str:
    """Format integer metrics with placeholder."""
    if value is None:
        return "--"
    return f"{value:,}"


def _format_ratio(numerator: Optional[int], denominator: Optional[int]) -> str:
    """Format ratio metrics with placeholder."""
    if numerator is None or denominator is None:
        return "--"
    return f"{numerator:,}/{denominator:,}"


def _format_percentage(value: Optional[float]) -> str:
    """Format percentage metrics with placeholder."""
    if value is None:
        return "--"
    return f"{value:.2f}%"


def create_results_layout(merged_data: Optional[Dict[str, Any]] = None) -> html.Div:
    """
    Create results page layout with feed-style accordions.

    Parameters
    ----------
    merged_data : Optional[Dict[str, Any]], optional
        Merged data from processing
        Expected keys: biorempp_df, biorempp_raw_df, hadeg_df, hadeg_raw_df,
        toxcsm_df (processed), toxcsm_raw_df (complete 66 columns),
        kegg_df, kegg_raw_df, metadata

    Returns
    -------
    html.Div
        Complete results page layout

    Notes
    -----
    Page Structure:
      - Header (with logo)
      - Overview card (general information)
      - Modular database sections (4 databases)
        Each section is self-contained with:
        - Title and description
        - Download button
        - Analytical highlight
        - Accordion with on-demand table
        - Analytical Modules (8 modules)
    """
    # Default empty data
    if merged_data is None:
        merged_data = {
            "biorempp_df": [],  # Processed for display
            "biorempp_raw_df": [],  # Complete database for download
            "hadeg_df": [],  # Processed for display
            "hadeg_raw_df": [],  # Complete database for download
            "toxcsm_df": [],  # Processed for graphs (5 columns)
            "toxcsm_raw_df": [],  # Complete database for table (66 columns)
            "kegg_df": [],  # Processed for display
            "kegg_raw_df": [],  # Complete database for download
            "metadata": {},
        }

    metadata = merged_data.get("metadata", {})
    job_id = metadata.get("job_id")
    if not isinstance(job_id, str) or not job_id.strip():
        job_id = "--"
    database_overview = metadata.get("database_overview", {})
    if not isinstance(database_overview, dict):
        database_overview = {}
    aggregate_overview = _resolve_database_aggregate_overview(
        metadata=metadata,
        database_overview=database_overview,
    )

    contributions = []
    for db_name, db_label in DATABASE_LABELS.items():
        db_stats = aggregate_overview.get("per_database", {}).get(db_name, {})
        input_relations = _safe_int(db_stats.get("input_relations"))
        share_pct = _safe_float(db_stats.get("share_pct"))

        if input_relations is None:
            badge_text = f"{db_label}: --"
        elif share_pct is None:
            badge_text = f"{db_label}: {input_relations:,}"
        else:
            badge_text = f"{db_label}: {input_relations:,} ({share_pct:.1f}%)"

        contributions.append(
            dbc.Badge(
                badge_text,
                color="light",
                text_color="dark",
                className="border me-2 mb-2",
            )
        )

    # Header
    header = create_header(show_nav=True, logo_size="80px")

    # Overview Card - Enhanced Design
    overview_card = dbc.Card(
        [
            dbc.CardHeader(
                [
                    dbc.Row(
                        [
                            dbc.Col(
                                [
                                    html.I(className="fas fa-table me-2 text-success"),
                                    html.H4(
                                        "Data Tables and Database Integration",
                                        className="d-inline mb-0",
                                    ),
                                ],
                                width="auto",
                            ),
                            dbc.Col(
                                [
                                    dbc.Badge(
                                        [
                                            html.I(className="fas fa-database me-1"),
                                            "4 Databases",
                                        ],
                                        color="success",
                                        className="me-2",
                                    ),
                                    dbc.Badge(
                                        [
                                            html.I(className="fas fa-chart-line me-1"),
                                            "8 Analysis Modules",
                                        ],
                                        color="info",
                                    ),
                                ],
                                width="auto",
                                className="ms-auto d-none d-md-block",
                            ),
                        ],
                        align="center",
                        className="g-0",
                    )
                ],
                className="bg-light border-bottom",
            ),
            dbc.CardBody(
                [
                    # Overview description
                    html.P(
                        "Comprehensive overview of integrated data across BioRemPP, HADEG, ToxCSM, and KEGG databases",
                        className="text-muted mb-3",
                        style={"lineHeight": "1.6"},
                    ),
                    # Processing statistics
                    dbc.Row(
                        [
                            dbc.Col(
                                [
                                    html.Div(
                                        [
                                            html.I(
                                                className="fas fa-flask text-success mb-2",
                                                style={"fontSize": "1.5rem"},
                                            ),
                                            html.H5(
                                                str(metadata.get("sample_count", 0)),
                                                className="mb-0 text-success",
                                            ),
                                            html.Small(
                                                "Samples Processed",
                                                className="text-muted",
                                            ),
                                        ],
                                        className="text-center",
                                    )
                                ],
                                md=4,
                                className="mb-3 mb-md-0",
                            ),
                            dbc.Col(
                                [
                                    html.Div(
                                        [
                                            html.I(
                                                className="fas fa-dna text-primary mb-2",
                                                style={"fontSize": "1.5rem"},
                                            ),
                                            html.H5(
                                                str(metadata.get("ko_count", 0)),
                                                className="mb-0 text-primary",
                                            ),
                                            html.Small(
                                                "KO Identifiers", className="text-muted"
                                            ),
                                        ],
                                        className="text-center",
                                    )
                                ],
                                md=4,
                                className="mb-3 mb-md-0",
                            ),
                            dbc.Col(
                                [
                                    html.Div(
                                        [
                                            html.I(
                                                className="fas fa-clock text-info mb-2",
                                                style={"fontSize": "1.5rem"},
                                            ),
                                            html.H5(
                                                f"{metadata.get('processing_time', 0):.2f}s",
                                                className="mb-0 text-info",
                                            ),
                                            html.Small(
                                                "Processing Time", className="text-muted"
                                            ),
                                        ],
                                        className="text-center",
                                    )
                                ],
                                md=4,
                            ),
                        ],
                        className="mt-2",
                    ),
                    dbc.Row(
                        [
                            dbc.Col(
                                html.Div(
                                    [
                                        html.Small(
                                            [
                                                html.I(
                                                    className="fas fa-fingerprint text-secondary me-2"
                                                ),
                                                "Job ID",
                                            ],
                                            className="text-muted d-block",
                                        ),
                                        html.Div(
                                            [
                                                html.Code(
                                                    job_id,
                                                    id="results-job-id-copy-target",
                                                    className="text-dark",
                                                    style={
                                                        "fontSize": "0.9rem",
                                                        "cursor": "pointer",
                                                    },
                                                ),
                                                (
                                                    dcc.Clipboard(
                                                        target_id="results-job-id-copy-target",
                                                        title="Copy Job ID",
                                                        className="ms-2",
                                                        style={
                                                            "display": "inline-flex",
                                                            "alignItems": "center",
                                                            "cursor": "pointer",
                                                            "color": "#6c757d",
                                                            "fontSize": "1rem",
                                                        },
                                                    )
                                                    if job_id != "--"
                                                    else html.Span()
                                                ),
                                            ],
                                            className="d-inline-flex align-items-center justify-content-center",
                                        ),
                                    ],
                                    className="text-center mt-3",
                                ),
                                width=12,
                            )
                        ]
                    ),
                    dbc.Row(
                        [
                            dbc.Col(
                                html.Hr(className="my-3"),
                                width=12,
                            )
                        ]
                    ),
                    dbc.Row(
                        [
                            dbc.Col(
                                html.Div(
                                    [
                                        html.Small(
                                            [
                                                html.I(
                                                    className="fas fa-link text-success me-2"
                                                ),
                                                "Integrated Relations",
                                                html.I(
                                                    className="fas fa-info-circle ms-2 text-muted",
                                                    title=(
                                                        "Sum of input relations across the first metric "
                                                        "of each database; overlap may exist."
                                                    ),
                                                    style={"fontSize": "0.75rem"},
                                                ),
                                            ],
                                            className="text-muted d-block",
                                        ),
                                        html.H5(
                                            _format_integer(
                                                _safe_int(
                                                    aggregate_overview.get(
                                                        "total_relations_input"
                                                    )
                                                )
                                            ),
                                            className="mb-0 text-dark",
                                        ),
                                    ],
                                    className="text-center",
                                ),
                                md=4,
                                className="mb-3 mb-md-0",
                            ),
                            dbc.Col(
                                html.Div(
                                    [
                                        html.Small(
                                            [
                                                html.I(
                                                    className="fas fa-database text-primary me-2"
                                                ),
                                                "Databases with Matches",
                                            ],
                                            className="text-muted d-block",
                                        ),
                                        html.H5(
                                            _format_ratio(
                                                _safe_int(
                                                    aggregate_overview.get(
                                                        "active_databases"
                                                    )
                                                ),
                                                _safe_int(
                                                    aggregate_overview.get("total_databases")
                                                ),
                                            ),
                                            className="mb-0 text-dark",
                                        ),
                                    ],
                                    className="text-center",
                                ),
                                md=4,
                                className="mb-3 mb-md-0",
                            ),
                            dbc.Col(
                                html.Div(
                                    [
                                        html.Small(
                                            [
                                                html.I(
                                                    className="fas fa-percentage text-info me-2"
                                                ),
                                                "KO Match Rate",
                                            ],
                                            className="text-muted d-block",
                                        ),
                                        html.H5(
                                            _format_percentage(
                                                _safe_float(
                                                    aggregate_overview.get("ko_match_rate_pct")
                                                )
                                            ),
                                            className="mb-0 text-dark",
                                        ),
                                    ],
                                    className="text-center",
                                ),
                                md=4,
                            ),
                        ]
                    ),
                    dbc.Row(
                        [
                            dbc.Col(
                                [
                                    html.Small(
                                        [
                                            html.I(
                                                className="fas fa-layer-group me-2 text-muted"
                                            ),
                                            "Per-database contribution",
                                        ],
                                        className="text-muted d-block mt-3 mb-2 text-center",
                                    ),
                                    html.Div(
                                        contributions,
                                        className=(
                                            "d-flex flex-wrap justify-content-center "
                                            "align-items-center"
                                        ),
                                    ),
                                ],
                                width=12,
                            )
                        ]
                    ),
                ]
            ),
        ],
        className="mb-4 shadow-sm border-top border-success border-3",
    )

    # Modular Database Sections
    biorempp_section = create_biorempp_section(
        overview_stats=database_overview.get("biorempp", {})
    )
    hadeg_section = create_hadeg_section(
        overview_stats=database_overview.get("hadeg", {})
    )
    toxcsm_section = create_toxcsm_section(
        overview_stats=database_overview.get("toxcsm", {})
    )
    kegg_section = create_kegg_section(
        overview_stats=database_overview.get("kegg", {})
    )

    # Module 1: Comparative Assessment
    module1_section = create_module1_section()

    # Module 2: Exploratory Analysis
    module2_section = create_module2_section()

    # Module 3: System Structure
    module3_section = create_module3_section()

    # Module 4: Functional and Genetic Profiling
    module4_section = create_module4_section()

    # Module 5: Modeling Interactions
    module5_section = create_module5_section()

    # Module 6: Hierarchical and Flow-based Analysis
    module6_section = create_module6_section()

    # Module 7: Toxicological Risk Assessment
    module7_section = create_module7_section()

    # Module 8: Assembly of Functional Consortia
    module8_section = create_module8_section()

    # Main Content Container
    main_content = dbc.Container(
        [
            overview_card,
            biorempp_section,
            hadeg_section,
            toxcsm_section,
            kegg_section,
            module1_section,
            module2_section,
            module3_section,
            module4_section,
            module5_section,
            module6_section,
            module7_section,
            module8_section,
        ],
        fluid=False,
        className="my-4",
    )

    # Footer
    footer = create_footer()

    # Navigation components
    nav_button = create_navigation_button()
    nav_offcanvas = create_navigation_offcanvas()

    # Analytical Suggestions components
    suggestions_button = create_suggestions_trigger_button()
    suggestions_offcanvas = create_suggestions_offcanvas()

    # Complete Layout (NO dcc.Location here - already in main app)
    return html.Div(
        [
            header,
            main_content,
            footer,
            suggestions_button,  # Left side
            nav_button,  # Right side
            suggestions_offcanvas,
            nav_offcanvas,
        ]
    )


def get_results_layout(merged_data: Optional[Dict[str, Any]] = None):
    """
    Get results layout (alias for create_results_layout).

    Parameters
    ----------
    merged_data : Optional[Dict[str, Any]], optional
        Merged data from processing

    Returns
    -------
    html.Div
        Complete results page layout
    """
    return create_results_layout(merged_data)
