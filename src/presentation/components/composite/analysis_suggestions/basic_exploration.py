"""
Basic Exploration Tab - Analysis Suggestions
============================================

Essential exploratory analyses organized by data entity.

Author: BioRemPP Development Team
Date: 2025-12-05
"""

import dash_bootstrap_components as dbc
from dash import html

from .guiding_questions import create_uc_link


def create_basic_exploration_content() -> html.Div:
    """
    Create basic exploration tab content.

    Returns
    -------
    html.Div
        Tab content with analyses organized by entity (Genes, Pathways, Compounds)
    """
    return html.Div(
        [
            dbc.Alert(
                [
                    html.I(className="fas fa-compass me-2"),
                    html.Strong("Start here: "),
                    "These fundamental analyses help you understand your data before diving into advanced visualizations.",
                ],
                color="success",
                className="mb-4",
            ),
            # Genes Section
            dbc.Card(
                [
                    dbc.CardHeader(
                        [
                            html.I(className="fas fa-dna me-2 text-primary"),
                            html.Strong("Genes", className="text-primary"),
                        ],
                        className="bg-light",
                    ),
                    dbc.CardBody(
                        [
                            html.P(
                                "Explore gene diversity, distribution, and relationships across your samples.",
                                className="text-muted small mb-3",
                            ),
                            html.H6(
                                [
                                    html.I(className="fas fa-link me-2 text-success"),
                                    "Relevant Use Cases (4):",
                                ],
                                className="mb-2",
                            ),
                            dbc.ListGroup(
                                [
                                    create_uc_link(
                                        "uc-2-1",
                                    ),
                                    create_uc_link(
                                        "uc-2-5",
                                    ),
                                    create_uc_link(
                                        "uc-1-1",
                                    ),
                                    create_uc_link(
                                        "uc-3-6",
                                    ),
                                ],
                                flush=True,
                            ),
                        ]
                    ),
                ],
                className="mb-3 shadow-sm",
            ),
            # Metabolic Pathways Section
            dbc.Card(
                [
                    dbc.CardHeader(
                        [
                            html.I(
                                className="fas fa-project-diagram me-2 text-success"
                            ),
                            html.Strong("Metabolic Pathways", className="text-success"),
                        ],
                        className="bg-light",
                    ),
                    dbc.CardBody(
                        [
                            html.P(
                                "Understand which metabolic routes are active and how they vary across samples.",
                                className="text-muted small mb-3",
                            ),
                            html.H6(
                                [
                                    html.I(className="fas fa-link me-2 text-success"),
                                    "Relevant Use Cases (3):",
                                ],
                                className="mb-2",
                            ),
                            dbc.ListGroup(
                                [
                                    create_uc_link(
                                        "uc-4-1",
                                    ),
                                    create_uc_link(
                                        "uc-4-2",
                                    ),
                                    create_uc_link(
                                        "uc-8-2",
                                    ),
                                ],
                                flush=True,
                            ),
                        ]
                    ),
                ],
                className="mb-3 shadow-sm",
            ),
            # Compounds Section
            dbc.Card(
                [
                    dbc.CardHeader(
                        [
                            html.I(className="fas fa-flask me-2 text-danger"),
                            html.Strong("Compounds", className="text-danger"),
                        ],
                        className="bg-light",
                    ),
                    dbc.CardBody(
                        [
                            html.P(
                                "Analyze chemical diversity and toxicity predictions for target compounds.",
                                className="text-muted small mb-3",
                            ),
                            html.H6(
                                [
                                    html.I(className="fas fa-link me-2 text-success"),
                                    "Relevant Use Cases (3):",
                                ],
                                className="mb-2",
                            ),
                            dbc.ListGroup(
                                [
                                    create_uc_link(
                                        "uc-7-1",
                                    ),
                                    create_uc_link(
                                        "uc-4-7",
                                    ),
                                    create_uc_link(
                                        "uc-2-2",
                                    ),
                                ],
                                flush=True,
                            ),
                        ]
                    ),
                ],
                className="mb-3 shadow-sm",
            ),
            # Samples Section
            dbc.Card(
                [
                    dbc.CardHeader(
                        [
                            html.I(className="fas fa-vial me-2 text-info"),
                            html.Strong("Samples", className="text-info"),
                        ],
                        className="bg-light",
                    ),
                    dbc.CardBody(
                        [
                            html.P(
                                "Compare samples and identify those with unique or complementary profiles.",
                                className="text-muted small mb-3",
                            ),
                            html.H6(
                                [
                                    html.I(className="fas fa-link me-2 text-success"),
                                    "Relevant Use Cases (3):",
                                ],
                                className="mb-2",
                            ),
                            dbc.ListGroup(
                                [
                                    create_uc_link(
                                        "uc-3-3",
                                    ),
                                    create_uc_link(
                                        "uc-8-1",
                                    ),
                                    create_uc_link(
                                        "uc-1-5",
                                    ),
                                ],
                                flush=True,
                            ),
                        ]
                    ),
                ],
                className="mb-3 shadow-sm",
            ),
        ]
    )
