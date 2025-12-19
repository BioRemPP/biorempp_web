"""
Practical Applications Tab - Analysis Suggestions
==================================================

Demonstrate real-world bioremediation applications supported by BioRemPP.

Author: BioRemPP Development Team
Date: 2025-12-05
"""

from pathlib import Path

import dash_bootstrap_components as dbc
import yaml
from dash import html

from .guiding_questions import create_uc_link

# Load Practical Applications config from local directory
CONFIG_PATH = Path(__file__).parent / "practical_applications_config.yaml"


def load_practical_config():
    """Load practical applications configuration from YAML."""
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def create_application_accordion_item(app_data: dict, index: int) -> dbc.AccordionItem:
    """
    Create accordion item for a practical application.

    Parameters
    ----------
    app_data : dict
        Application data from YAML
    index : int
        Index for unique item ID

    Returns
    -------
    dbc.AccordionItem
        Accordion item with application details
    """
    # Create UC links
    uc_links = []
    for uc_id in app_data.get("relevant_use_cases", []):
        uc_links.append(
            create_uc_link(uc_id, f"View {uc_id.upper()}", "fas fa-chart-bar")
        )

    return dbc.AccordionItem(
        [
            # Description
            html.P(
                app_data["description"],
                className="text-muted mb-3",
                style={"fontSize": "0.95rem"},
            ),
            # Guiding Questions
            html.H6(
                [
                    html.I(className="fas fa-question-circle me-2 text-info"),
                    "Key Questions:",
                ],
                className="mb-2",
            ),
            html.Ul(
                [
                    html.Li(question, className="text-muted small")
                    for question in app_data.get("guiding_questions", [])
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
                dbc.ListGroup(uc_links, flush=True)
                if uc_links
                else html.P("No use cases mapped yet.", className="text-muted small")
            ),
        ],
        title=[
            html.I(
                className=f"{app_data.get('icon', 'fas fa-lightbulb')} me-2 text-{app_data.get('color', 'primary')}"
            ),
            html.Span(
                app_data["title"],
                className=f"text-{app_data.get('color', 'primary')} fw-bold",
            ),
        ],
        item_id=f"practical-app-{index}",
    )


def create_practical_applications_content() -> html.Div:
    """
    Create practical applications tab content.

    Organizes 10 real-world bioremediation applications showing how
    BioRemPP supports practical decision-making.

    Returns
    -------
    html.Div
        Tab content with application accordion
    """
    config = load_practical_config()
    applications = config.get("practical_applications", [])

    return html.Div(
        [
            dbc.Alert(
                [
                    html.I(className="fas fa-industry me-2"),
                    html.Strong("Practical Applications: "),
                    "Discover how BioRemPP supports real-world bioremediation decisions. "
                    "Click each application to expand and view details.",
                ],
                color="success",
                className="mb-3",
            ),
            # Application Accordion
            dbc.Accordion(
                [
                    create_application_accordion_item(app_data, idx)
                    for idx, app_data in enumerate(applications)
                ],
                start_collapsed=True,
                always_open=False,
                flush=True,
            ),
            # Summary footer
            html.Hr(className="my-3"),
            dbc.Alert(
                [
                    html.I(className="fas fa-check-circle me-2"),
                    html.Strong("Ready to Apply: "),
                    f"{len(applications)} practical applications demonstrating how BioRemPP's analytical "
                    "capabilities translate into actionable insights for bioremediation projects.",
                ],
                color="info",
                className="mb-0",
            ),
        ]
    )
