"""
Current Trends Tab - Analysis Suggestions
==========================================

Showcase emerging research trends in bioremediation with scientific context.

Author: BioRemPP Development Team
Date: 2025-12-05
"""

from pathlib import Path

import dash_bootstrap_components as dbc
import yaml
from dash import html

from .guiding_questions import create_uc_link

# Load Current Trends config from local directory
CONFIG_PATH = Path(__file__).parent / "practical_applications_config.yaml"


def load_trends_config():
    """Load current trends configuration from YAML."""
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def create_reference_link(ref_data: dict) -> html.Li:
    """
    Create reference link item.

    Parameters
    ----------
    ref_data : dict
        Reference data with title, citation, url

    Returns
    -------
    html.Li
        List item with formatted reference
    """
    return html.Li(
        [
            html.A(
                [html.I(className="fas fa-external-link-alt me-2"), ref_data["title"]],
                href=ref_data["url"],
                target="_blank",
                className="text-decoration-none",
            ),
            html.Br(),
            html.Small(ref_data["citation"], className="text-muted"),
        ],
        className="mb-2",
    )


def create_trend_accordion_item(trend_data: dict, index: int) -> dbc.AccordionItem:
    """
    Create accordion item for a research trend.

    Parameters
    ----------
    trend_data : dict
        Trend data from YAML
    index : int
        Index for unique item ID

    Returns
    -------
    dbc.AccordionItem
        Accordion item with trend details
    """
    # Create UC links
    uc_links = []
    for uc_id in trend_data.get("relevant_use_cases", []):
        uc_links.append(
            create_uc_link(uc_id, f"View {uc_id.upper()}", "fas fa-chart-bar")
        )

    # Create reference links
    references = [
        create_reference_link(ref) for ref in trend_data.get("references", [])
    ]

    return dbc.AccordionItem(
        [
            # Summary
            html.H6(
                [html.I(className="fas fa-book-open me-2 text-primary"), "Overview:"],
                className="mb-2",
            ),
            html.P(
                trend_data["summary"],
                className="text-muted mb-3",
                style={"fontSize": "0.95rem"},
            ),
            # Why Relevant
            html.H6(
                [
                    html.I(className="fas fa-lightbulb me-2 text-warning"),
                    "Why It Matters for BioRemPP:",
                ],
                className="mb-2",
            ),
            html.P(
                trend_data["why_relevant"],
                className="text-muted mb-3",
                style={"fontSize": "0.95rem"},
            ),
            # Suggested Questions
            html.H6(
                [
                    html.I(className="fas fa-question-circle me-2 text-info"),
                    "Key Research Questions:",
                ],
                className="mb-2",
            ),
            html.Ul(
                [
                    html.Li(question, className="text-muted small")
                    for question in trend_data.get("suggested_questions", [])
                ],
                className="mb-3",
            ),
            # Relevant Use Cases
            html.H6(
                [
                    html.I(className="fas fa-link me-2 text-success"),
                    f"Relevant Use Cases ({len(uc_links)}):",
                ],
                className="mb-2",
            ),
            (
                dbc.ListGroup(uc_links, flush=True, className="mb-3")
                if uc_links
                else html.P(
                    "No use cases mapped yet.", className="text-muted small mb-3"
                )
            ),
            # References
            html.H6(
                [
                    html.I(className="fas fa-graduation-cap me-2 text-danger"),
                    f"Scientific References ({len(references)}):",
                ],
                className="mb-2",
            ),
            (
                html.Ul(references, className="list-unstyled")
                if references
                else html.P("No references available.", className="text-muted small")
            ),
        ],
        title=[
            html.I(
                className=f"{trend_data.get('icon', 'fas fa-flask')} me-2 text-{trend_data.get('color', 'info')}"
            ),
            html.Span(
                trend_data["title"],
                className=f"text-{trend_data.get('color', 'info')} fw-bold",
            ),
        ],
        item_id=f"trend-{index}",
    )


def create_current_trends_content() -> html.Div:
    """
    Create current trends tab content.

    Showcases 6 emerging research areas in bioremediation with
    scientific context, relevant use cases, and peer-reviewed references.

    Returns
    -------
    html.Div
        Tab content with trend accordion
    """
    config = load_trends_config()
    trends = config.get("current_trends", [])

    return html.Div(
        [
            dbc.Alert(
                [
                    html.I(className="fas fa-microscope me-2"),
                    html.Strong("Current Research Trends: "),
                    "Explore cutting-edge research areas in bioremediation. "
                    "Click each trend to expand and view scientific context, use cases, and references.",
                ],
                color="info",
                className="mb-3",
            ),
            # Trend Accordion
            dbc.Accordion(
                [
                    create_trend_accordion_item(trend_data, idx)
                    for idx, trend_data in enumerate(trends)
                ],
                start_collapsed=True,
                always_open=False,
                flush=True,
            ),
            # Summary footer
            html.Hr(className="my-3"),
            dbc.Alert(
                [
                    html.I(className="fas fa-atom me-2"),
                    html.Strong("Stay Current: "),
                    f"{len(trends)} emerging research trends with peer-reviewed references. "
                    "Click reference links to access full publications.",
                ],
                color="success",
                className="mb-0",
            ),
        ]
    )
