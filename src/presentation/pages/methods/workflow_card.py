"""
Workflow Card Component

Creates Bootstrap cards to display individual workflow information
with collapsible step details.
"""

from typing import Dict, List

import dash_bootstrap_components as dbc
from dash import dcc, html

from .module_metadata import get_module_color, get_module_icon


def create_workflow_card(workflow: Dict) -> dbc.Card:
    """
    Create a Bootstrap card for displaying a workflow.

    Args:
        workflow: Workflow dictionary containing:
            - use_case_id: UC identifier (e.g., "UC-1.1")
            - title: Workflow title
            - module: Module number
            - steps: List of step dictionaries

    Returns:
        dbc.Card component with workflow information.
    """
    uc_id = workflow.get("use_case_id", "Unknown")
    title = workflow.get("title", "Untitled Workflow")
    module = workflow.get("module", 1)
    steps = workflow.get("steps", [])

    # Use green color for all cards (consistent theme)
    card_color = "#2ecc71"  # Green

    # Create card header (without emoji)
    card_header = dbc.CardHeader(
        html.Div([html.Strong(f"{uc_id}: ", className="me-1"), html.Span(title)]),
        style={"backgroundColor": card_color, "color": "white", "fontWeight": "500"},
    )

    # Create step accordion items
    accordion_items = []
    for step in steps:
        step_num = step.get("step_number", 0)
        step_name = step.get("name", "Unnamed Step")
        step_desc = step.get("description", "")

        # Create accordion item without emoji
        accordion_item = dbc.AccordionItem(
            html.Div(
                [
                    dcc.Markdown(
                        step_desc, className="mb-0", style={"fontSize": "0.9rem"}
                    )
                ]
            ),
            title=f"Step {step_num}: {step_name}",
            item_id=f"{uc_id}-step-{step_num}",
        )
        accordion_items.append(accordion_item)

    # Create accordion
    accordion = dbc.Accordion(
        accordion_items, id=f"accordion-{uc_id}", start_collapsed=True, flush=True
    )

    # Create card body
    card_body = dbc.CardBody(
        [
            html.P(
                f"{len(steps)} analytical steps",
                className="text-muted mb-3",
                style={"fontSize": "0.85rem"},
            ),
            accordion,
        ]
    )

    # Create complete card
    card = dbc.Card(
        [card_header, card_body],
        className="mb-3 shadow-sm",
        style={
            "borderLeft": f"4px solid {card_color}",
            "transition": "transform 0.2s, box-shadow 0.2s",
        },
    )

    return card


def create_workflow_cards_grid(workflows: List[Dict]) -> html.Div:
    """
    Create a responsive grid of workflow cards.

    Args:
        workflows: List of workflow dictionaries

    Returns:
        html.Div containing responsive grid of cards.
    """
    if not workflows:
        return html.Div(
            dbc.Alert(
                "No workflows found for this module.",
                color="info",
                className="text-center",
            ),
            className="mt-4",
        )

    # Create cards
    cards = [create_workflow_card(wf) for wf in workflows]

    # Organize into rows (3 cards per row on desktop)
    rows = []
    for i in range(0, len(cards), 3):
        row_cards = cards[i : i + 3]

        cols = [
            dbc.Col(
                card,
                xs=12,  # Full width on mobile
                md=6,  # Half width on tablet
                lg=4,  # Third width on desktop
                className="mb-3",
            )
            for card in row_cards
        ]

        rows.append(dbc.Row(cols, className="g-3"))

    return html.Div(rows)
