"""
Workflow Modal Component

Creates large, centered modals to display workflow steps.
Steps are displayed sequentially without accordion.
"""

from typing import Dict, List

import dash_bootstrap_components as dbc
from dash import dcc, html


def create_workflow_modal(workflow: Dict) -> dbc.Modal:
    """
    Create a large, centered modal for displaying workflow steps.

    Args:
        workflow: Workflow dictionary containing:
            - use_case_id: UC identifier (e.g., "UC-1.1")
            - title: Workflow title
            - steps: List of step dictionaries

    Returns:
        dbc.Modal component with workflow steps displayed sequentially.
    """
    uc_id = workflow.get("use_case_id", "Unknown")
    title = workflow.get("title", "Untitled Workflow")
    steps = workflow.get("steps", [])

    # Create modal header
    modal_header = dbc.ModalHeader(
        dbc.ModalTitle(
            html.Div(
                [html.Strong(f"{uc_id}: ", className="text-primary"), html.Span(title)]
            )
        ),
        close_button=True,
    )

    # Create sequential step list
    step_elements = []
    for step in steps:
        step_num = step.get("step_number", 0)
        step_name = step.get("name", "Unnamed Step")
        step_desc = step.get("description", "")

        # Create step card
        step_card = dbc.Card(
            [
                dbc.CardHeader(
                    html.Div(
                        [
                            html.Strong(
                                f"Step {step_num}: ", className="text-success me-1"
                            ),
                            html.Span(step_name),
                        ]
                    ),
                    className="bg-light",
                ),
                dbc.CardBody(
                    [
                        dcc.Markdown(
                            step_desc, className="mb-0", style={"fontSize": "0.95rem"}
                        )
                    ]
                ),
            ],
            className="mb-3 shadow-sm",
        )

        step_elements.append(step_card)

    # Create modal body
    modal_body = dbc.ModalBody(
        [
            html.Div(
                [
                    html.P(
                        f"{len(steps)} analytical steps",
                        className="text-muted mb-3",
                        style={"fontSize": "0.9rem", "fontStyle": "italic"},
                    ),
                    html.Div(step_elements),
                ]
            )
        ],
        style={"maxHeight": "70vh", "overflowY": "auto"},
    )

    # Create modal footer with close button
    modal_footer = dbc.ModalFooter(
        dbc.Button(
            "Close",
            id={"type": "modal-close", "index": uc_id},
            className="btn-secondary",
            n_clicks=0,
        )
    )

    # Create complete modal
    modal = dbc.Modal(
        [modal_header, modal_body, modal_footer],
        id={"type": "modal", "index": uc_id},
        size="lg",
        centered=True,
        backdrop=True,  # Click outside to close
        is_open=False,
        scrollable=True,
    )

    return modal


def create_all_modals(workflows: List[Dict]) -> html.Div:
    """
    Create all modals for a list of workflows.

    Args:
        workflows: List of workflow dictionaries

    Returns:
        html.Div containing all modals (hidden by default).
    """
    modals = []

    for workflow in workflows:
        modal = create_workflow_modal(workflow)
        modals.append(modal)

    return html.Div(modals)
