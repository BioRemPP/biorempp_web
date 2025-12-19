"""
Guiding Questions Tab - Analysis Suggestions
============================================

Scientific questions to guide user exploration of results.

Author: BioRemPP Development Team
Date: 2025-12-05
"""

from pathlib import Path

import dash_bootstrap_components as dbc
import yaml
from dash import html

# Load UC mapping from local directory
CONFIG_PATH = Path(__file__).parent / "uc_suggestions_map.yaml"


def load_uc_config():
    """Load UC suggestions mapping from YAML."""
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def create_uc_link(
    uc_id: str, label: str, icon: str = "fas fa-chart-bar"
) -> dbc.ListGroupItem:
    """
    Create clickable link to use case.

    Parameters
    ----------
    uc_id : str
        Use case ID (e.g., "uc-2-1")
    label : str
        Display label
    icon : str
        FontAwesome icon class

    Returns
    -------
    dbc.ListGroupItem
        Clickable list item
    """
    return dbc.ListGroupItem(
        [html.I(className=f"{icon} me-2 text-primary"), label],
        id={"type": "suggestion-uc-link", "index": uc_id},
        href=f"#{uc_id}-info-panel",  # Add href for JavaScript navigation
        action=True,
        className="suggestion-uc-link",
        n_clicks=0,
        style={"cursor": "pointer"},
    )


def create_guiding_questions_content() -> html.Div:
    """
    Create guiding questions tab content.

    Returns
    -------
    html.Div
        Tab content with scientific questions organized in accordion
    """
    config = load_uc_config()

    # Extract guiding questions from UCs
    questions = [
        {
            "question": "Which samples show more genes associated with biodegradation?",
            "description": "Higher gene counts may indicate richer metabolic potential in specific samples.",
            "ucs": [
                ("uc-2-1", "Gene Counts Across Samples", "fas fa-chart-bar"),
                ("uc-2-2", "Chemical Diversity Ranking", "fas fa-chart-bar"),
            ],
        },
        {
            "question": "Are gene distributions balanced across samples or are there outliers?",
            "description": "Outliers may represent highly specialized or unusually diverse samples.",
            "ucs": [("uc-2-5", "Descriptive Statistics", "fas fa-chart-bar")],
        },
        {
            "question": "Which pathways are most active across samples?",
            "description": "Identify dominant metabolic routes in your dataset.",
            "ucs": [
                ("uc-4-1", "Pathway Profiling by Sample", "fas fa-chart-bar"),
                ("uc-4-2", "Pathway Richness Ranking", "fas fa-chart-bar"),
            ],
        },
        {
            "question": "How many entries are matched in the BioRemPP and HADEG databases?",
            "description": "Understand consensus and unique contributions from each database.",
            "ucs": [("uc-1-1", "Database Intersections", "fas fa-chart-bar")],
        },
        {
            "question": "Are there any compounds predicted as toxic?",
            "description": "Toxicity predictions can help prioritize compounds for closer inspection.",
            "ucs": [
                ("uc-7-1", "Toxicity Prediction Heatmap", "fas fa-chart-bar"),
                ("uc-7-4", "Toxicity Score Distributions", "fas fa-chart-bar"),
            ],
        },
        {
            "question": "How complete are degradation pathways in my samples?",
            "description": "Assess pathway completeness to identify gaps or strong candidates.",
            "ucs": [("uc-8-2", "Completeness Scorecard", "fas fa-chart-bar")],
        },
        {
            "question": "Which genes are associated with specific compounds?",
            "description": "Explore gene-compound relationships for targeted analysis.",
            "ucs": [
                ("uc-4-7", "Gene-Compound Explorer", "fas fa-chart-bar"),
                ("uc-4-8", "Gene Inventory", "fas fa-chart-bar"),
            ],
        },
        {
            "question": "How do samples group based on their functional profiles?",
            "description": "Clustering reveals samples with similar metabolic capabilities.",
            "ucs": [
                ("uc-3-3", "Hierarchical Clustering", "fas fa-chart-bar"),
                ("uc-3-6", "Gene Co-occurrence", "fas fa-chart-bar"),
            ],
        },
    ]

    # Build accordion items
    accordion_items = []
    for idx, q in enumerate(questions, 1):
        uc_links = [
            create_uc_link(uc_id, label, icon) for uc_id, label, icon in q["ucs"]
        ]

        accordion_items.append(
            dbc.AccordionItem(
                [
                    html.P(q["description"], className="text-muted mb-3"),
                    dbc.ListGroup(uc_links, flush=True),
                    html.Small(
                        f"Related UCs: {', '.join([uc[0].upper() for uc in q['ucs']])}",
                        className="text-muted mt-3 d-block",
                    ),
                ],
                title=f"{idx}. {q['question']}",
            )
        )

    return html.Div(
        [
            dbc.Alert(
                [
                    html.I(className="fas fa-info-circle me-2"),
                    html.Strong("Tip: "),
                    "Click on any use case below to navigate directly to the visualization.",
                ],
                color="info",
                className="mb-3",
            ),
            dbc.Accordion(
                accordion_items,
                id="guiding-questions-accordion",
                start_collapsed=False,
                always_open=True,
            ),
        ]
    )
