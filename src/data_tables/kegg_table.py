"""
KEGG Table Section - Results Component.

Provides KEGG degradation pathway table with enhanced metadata,
database statistics, and on-demand rendering via accordion.

Functions
---------
create_kegg_section
    Create complete KEGG section with enhanced description and accordion
"""

from typing import Any, Dict, Optional

import dash_bootstrap_components as dbc
from dash import dcc, html

from src.presentation.components.composite import create_database_description


def _format_stat_value(value: Any) -> str:
    """Format stat values with fallback placeholder."""
    if value is None:
        return "--"
    if isinstance(value, bool):
        return str(value)
    if isinstance(value, int):
        return f"{value:,}"
    if isinstance(value, float):
        return f"{int(value):,}" if value.is_integer() else f"{value:,.2f}"
    return str(value)


def _get_stat_value(
    overview_stats: Optional[Dict[str, Dict[str, Any]]],
    metric_key: str,
    value_key: str,
) -> Any:
    """Safely get nested overview stat value."""
    if not overview_stats:
        return None
    metric = overview_stats.get(metric_key)
    if not isinstance(metric, dict):
        return None
    return metric.get(value_key)


def _create_reference_value_indicator(
    overview_stats: Optional[Dict[str, Dict[str, Any]]], metric_key: str
) -> html.Small:
    """Render compact database reference indicator (icon + value)."""
    return html.Small(
        [
            html.I(
                className="fas fa-database me-1",
                title="Refrence database value",
                style={"fontSize": "0.7rem"},
            ),
            _format_stat_value(_get_stat_value(overview_stats, metric_key, "global_value")),
        ],
        className="text-muted d-block",
    )


def create_kegg_section(
    overview_stats: Optional[Dict[str, Dict[str, Any]]] = None,
) -> html.Div:
    """
    Create KEGG pathway results table section with enhanced metadata.

    Returns
    -------
    html.Div
        Complete section with database description, statistics card,
        accordion with on-demand table rendering, and download component.
        Container ID: 'kegg-container', Accordion ID: 'kegg-accordion'
    """
    # Custom components for KEGG-specific information
    custom_components = [
        # Database statistics card
        dbc.Card(
            [
                dbc.CardHeader(
                    [
                        html.I(className="fas fa-database me-2"),
                        html.Strong("KEGG Degradation Database Overview"),
                    ],
                    className="bg-info text-white",
                ),
                dbc.CardBody(
                    [
                        dbc.Row(
                            [
                                dbc.Col(
                                    [
                                        html.Div(
                                            [
                                                html.H4(
                                                    _format_stat_value(
                                                        _get_stat_value(
                                                            overview_stats,
                                                            "gene_pathway_associations",
                                                            "input_value",
                                                        )
                                                    ),
                                                    className="text-info mb-0",
                                                ),
                                                html.Small(
                                                    "Gene-Pathway Associations",
                                                    className="text-muted",
                                                ),
                                            ],
                                            className="text-center",
                                        )
                                    ],
                                    md=4,
                                ),
                                dbc.Col(
                                    [
                                        html.Div(
                                            [
                                                html.H4(
                                                    _format_stat_value(
                                                        _get_stat_value(
                                                            overview_stats,
                                                            "unique_ko_numbers",
                                                            "input_value",
                                                        )
                                                    ),
                                                    className="text-primary mb-0",
                                                ),
                                                _create_reference_value_indicator(
                                                    overview_stats,
                                                    "unique_ko_numbers",
                                                ),
                                                html.Small(
                                                    "Unique KO Numbers",
                                                    className="text-muted",
                                                ),
                                            ],
                                            className="text-center",
                                        )
                                    ],
                                    md=4,
                                ),
                                dbc.Col(
                                    [
                                        html.Div(
                                            [
                                                html.H4(
                                                    _format_stat_value(
                                                        _get_stat_value(
                                                            overview_stats,
                                                            "degradation_pathways",
                                                            "input_value",
                                                        )
                                                    ),
                                                    className="text-success mb-0",
                                                ),
                                                _create_reference_value_indicator(
                                                    overview_stats,
                                                    "degradation_pathways",
                                                ),
                                                html.Small(
                                                    "Degradation Pathways",
                                                    className="text-muted",
                                                ),
                                            ],
                                            className="text-center",
                                        )
                                    ],
                                    md=4,
                                ),
                            ]
                        )
                    ]
                ),
            ],
            className="mb-3 shadow-sm",
        ),
    ]

    # Create download button for merged database
    from src.presentation.components.download_component import create_download_button

    download_button = create_download_button(
        use_case_id="kegg-db",
        button_id="kegg-db-download-btn",
        download_id="kegg-db-download",
        formats=["csv", "excel", "json"],
        button_text="Download Data",
        button_color="success",
        button_outline=True,
        show_spinner=True,
    )

    # Create Database Info button that opens schema page in new tab
    # Using html.A instead of dbc.Button to bypass Dash router and open in new tab
    info_button = html.A(
        [
            html.I(className="fas fa-info-circle me-2"),
            "Database Info",
        ],
        href="/schemas/kegg",
        target="_blank",
        rel="noopener noreferrer",
        className="btn btn-outline-info btn-sm",
    )

    # Enhanced database description
    description_component = create_database_description(
        title="KEGG Degradation Pathway Mapping",
        description=(
            "Integrates your data with the KEGG Degradation Database, mapping KO numbers "
            "to xenobiotic degradation pathways and gene symbols for metabolic context analysis."
        ),
        section_id="kegg-results-table",
        custom_components=custom_components,
        download_button=download_button,
        info_button=info_button,
    )

    # Accordion with on-demand table and enhanced title
    accordion = dbc.Accordion(
        [
            dbc.AccordionItem(
                [
                    # Info alert before table
                    dbc.Alert(
                        [
                            html.I(className="fas fa-info-circle me-2"),
                            html.Strong("Table Contents: "),
                            "This table shows the intersection of your input data with the KEGG degradation database. "
                            "Each row represents a gene-pathway-KO relationship found in your samples.",
                        ],
                        color="info",
                        className="mb-3",
                    ),
                    # Table container
                    html.Div(id="kegg-container", className="chart-container"),
                ],
                title="View KEGG Degradation Pathway Table",
            )
        ],
        start_collapsed=True,
        id="kegg-accordion",
    )

    # Download component
    download = dcc.Download(id="download-kegg-csv")

    # Complete section with enhanced styling
    section = html.Div(
        [description_component, accordion, download, html.Hr(className="my-4")],
        id="kegg-section",
    )

    return section
