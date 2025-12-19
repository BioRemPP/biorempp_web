"""
UC-3.3 Layout - Interactive Hierarchical Clustering of Samples.

Provides layout for dendrogram visualization showing hierarchical
relationships between samples with interactive metric and method selection.

Notes
-----
- See official documentation for detailed use case description
"""

import dash_bootstrap_components as dbc
from dash import dcc, html

from src.presentation.components.composite.use_cases import create_panel_by_id
from src.presentation.components.download_component import (
    create_download_button,
    create_download_toast,
)


def create_uc_3_3_layout() -> dbc.Card:
    """
    Create UC-3.3 layout for interactive hierarchical clustering.

    Returns
    -------
    dbc.Card
        Card component with distance metric and clustering method selection.

    Notes
    -----
    - See official documentation for use case details
    """
    # Informative panel with scientific context
    info_panel = create_panel_by_id("uc-3-3")

    return dbc.Card(
        [
            # ========================================
            # Card Header
            # ========================================
            dbc.CardHeader(
                [
                    dbc.Row(
                        [
                            dbc.Col(
                                [
                                    html.H5(
                                        [
                                            html.I(className="fas fa-chart-area me-2"),
                                            "UC-3.3: Interactive Hierarchical Clustering of Samples",
                                        ],
                                        className="mb-0",
                                    )
                                ],
                                width="auto",
                            ),
                            dbc.Col(
                                [
                                    html.Span(
                                        [
                                            html.I(
                                                className="fas fa-exclamation-triangle text-warning",
                                                id="uc-3-3-info-icon",
                                            ),
                                            dbc.Tooltip(
                                                "⚠️ Currently unavailable",
                                                target="uc-3-3-info-icon",
                                                placement="left",
                                            ),
                                        ]
                                    )
                                ],
                                width="auto",
                                className="ms-auto",
                            ),
                        ],
                        align="center",
                        className="g-0",
                    )
                ]
            ),
            # ========================================
            # Card Body
            # ========================================
            dbc.CardBody(
                [
                    # Informative panel (scientific context)
                    info_panel,
                    # Toast notification for download feedback
                    create_download_toast("uc-3-3-download-toast"),
                    # ========================================
                    # Accordion: Interactive Controls
                    # ========================================
                    dbc.Accordion(
                        [
                            dbc.AccordionItem(
                                [
                                    # Distance Metric and Clustering Method Selection (Side by Side)
                                    dbc.Row(
                                        [
                                            dbc.Col(
                                                [
                                                    html.Label(
                                                        "Select Distance Metric:",
                                                        className="fw-bold mb-2",
                                                    ),
                                                    dcc.Dropdown(
                                                        id="uc-3-3-metric-dropdown",
                                                        options=[
                                                            {
                                                                "label": "Jaccard",
                                                                "value": "jaccard",
                                                            },
                                                            {
                                                                "label": "Euclidean",
                                                                "value": "euclidean",
                                                            },
                                                            {
                                                                "label": "Cosine",
                                                                "value": "cosine",
                                                            },
                                                            {
                                                                "label": "Hamming",
                                                                "value": "hamming",
                                                            },
                                                            {
                                                                "label": "Dice",
                                                                "value": "dice",
                                                            },
                                                        ],
                                                        placeholder="Choose a distance metric...",
                                                        clearable=False,
                                                        className="mb-3",
                                                    ),
                                                ],
                                                width=6,
                                            ),
                                            dbc.Col(
                                                [
                                                    html.Label(
                                                        "Select Clustering Method:",
                                                        className="fw-bold mb-2",
                                                    ),
                                                    dcc.Dropdown(
                                                        id="uc-3-3-method-dropdown",
                                                        options=[
                                                            {
                                                                "label": "Average (UPGMA)",
                                                                "value": "average",
                                                            },
                                                            {
                                                                "label": "Complete",
                                                                "value": "complete",
                                                            },
                                                            {
                                                                "label": "Single",
                                                                "value": "single",
                                                            },
                                                            {
                                                                "label": "Ward",
                                                                "value": "ward",
                                                            },
                                                        ],
                                                        placeholder="Choose a clustering method...",
                                                        clearable=False,
                                                        className="mb-3",
                                                    ),
                                                ],
                                                width=6,
                                            ),
                                        ],
                                        className="mb-4",
                                    ),
                                    # ========================================
                                    # Chart Container (Rendered on Demand)
                                    # ========================================
                                    html.Div(
                                        id="uc-3-3-chart-container", className="mt-4"
                                    ),
                                ],
                                title="View Results",
                                item_id="uc-3-3-item",
                            )
                        ],
                        id="uc-3-3-accordion",
                        start_collapsed=True,
                    ),
                ],
                className="p-4",
            ),
        ],
        className="shadow-sm mb-4",
        id="uc-3-3-card",
    )
