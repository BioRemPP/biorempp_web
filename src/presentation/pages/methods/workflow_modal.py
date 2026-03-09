"""
Workflow Modal Component.

Creates local and global workflow modals with shared content builders.
"""

from typing import Dict, List

import dash_bootstrap_components as dbc
from dash import dcc, html


def _build_workflow_title_children(workflow: Dict) -> html.Div:
    """Build modal title section from workflow payload."""
    uc_id = workflow.get("use_case_id", "Unknown")
    title = workflow.get("title", "Untitled Workflow")
    return html.Div(
        [html.Strong(f"{uc_id}: ", className="text-primary"), html.Span(title)]
    )


def _build_workflow_body_children(workflow: Dict) -> html.Div:
    """Build modal body section from workflow payload."""
    steps = workflow.get("steps", [])

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

    return html.Div(
        [
            html.P(
                f"{len(steps)} analytical steps",
                className="text-muted mb-3",
                style={"fontSize": "0.9rem", "fontStyle": "italic"},
            ),
            html.Div(step_elements),
        ]
    )


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
    modal_header = dbc.ModalHeader(
        dbc.ModalTitle(_build_workflow_title_children(workflow)),
        close_button=True,
    )
    modal_body = dbc.ModalBody(
        [_build_workflow_body_children(workflow)],
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


def create_results_workflow_modal() -> dbc.Modal:
    """Create a single global workflow modal for /results page."""
    return dbc.Modal(
        [
            dbc.ModalHeader(
                dbc.ModalTitle(id="results-workflow-modal-title"),
                close_button=True,
            ),
            dbc.ModalBody(
                id="results-workflow-modal-body",
                style={"maxHeight": "70vh", "overflowY": "auto"},
            ),
            dbc.ModalFooter(
                dbc.Button(
                    "Close",
                    id="results-workflow-modal-close",
                    className="btn-secondary",
                    n_clicks=0,
                )
            ),
        ],
        id="results-workflow-modal",
        size="lg",
        centered=True,
        backdrop=True,
        is_open=False,
        scrollable=True,
    )


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
