"""
Workflow Links Component

Creates a clean list of clickable links for workflows.
Each link opens a modal with the workflow details.
"""

from typing import Dict, List

import dash_bootstrap_components as dbc
from dash import html


def create_workflow_link(workflow: Dict) -> html.Li:
    """
    Create a single workflow link item.

    Args:
        workflow: Workflow dictionary containing:
            - use_case_id: UC identifier (e.g., "UC-1.1")
            - title: Workflow title

    Returns:
        html.Li containing a clickable link.
    """
    uc_id = workflow.get("use_case_id", "Unknown")
    title = workflow.get("title", "Untitled Workflow")

    # Create link button with pattern-matching ID
    link = dbc.Button(
        [
            html.I(className="fas fa-flask me-2", style={"color": "#2ecc71"}),
            html.Strong(f"{uc_id}: ", className="text-primary"),
            html.Span(title, className="text-dark"),
        ],
        id={"type": "link", "index": uc_id},
        color="link",
        className="text-start p-2 w-100",
        style={
            "textDecoration": "none",
            "transition": "all 0.2s",
            "borderRadius": "0.25rem",
        },
        n_clicks=0,
    )

    # Wrap in list item
    list_item = html.Li(
        link,
        className="mb-2",
        style={
            "listStyle": "none",
            "borderBottom": "1px solid #e9ecef",
            "paddingBottom": "0.5rem",
        },
    )

    return list_item


def create_workflow_links_list(workflows: List[Dict]) -> html.Div:
    """
    Create a list of workflow links.

    Args:
        workflows: List of workflow dictionaries

    Returns:
        html.Div containing a clean list of clickable links.
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

    # Create link items
    link_items = [create_workflow_link(wf) for wf in workflows]

    # Create list container
    links_list = html.Div(
        [html.Ul(link_items, className="ps-0 mb-0")],
        className="workflow-links-container",
    )

    return links_list
