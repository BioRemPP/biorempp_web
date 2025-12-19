"""
Module Section Component

Creates a section container for displaying all workflows in a module.
Now uses link list with modals instead of card grid.
"""

from typing import Dict, List

import dash_bootstrap_components as dbc
from dash import html

from .module_metadata import get_module_metadata
from .workflow_links import create_workflow_links_list
from .workflow_modal import create_all_modals


def create_module_section(module: int, workflows: List[Dict]) -> dbc.Container:
    """
    Create a section displaying all workflows for a module.

    Args:
        module: Module number (1-8)
        workflows: List of workflow dictionaries for this module

    Returns:
        dbc.Container with module header, workflow links, and modals.
    """
    # Get module metadata
    metadata = get_module_metadata(module)

    # Create module header
    header = html.Div(
        [
            html.Div(
                [
                    html.Div(
                        [
                            html.H2(
                                f"Module {module}",
                                className="mb-1",
                                style={"color": metadata["color"]},
                            ),
                            html.H4(metadata["title"], className="mb-2 text-muted"),
                            html.P(
                                metadata["description"],
                                className="mb-0 text-secondary",
                                style={"fontSize": "0.95rem"},
                            ),
                        ],
                        style={"flex": "1"},
                    )
                ],
                style={
                    "display": "flex",
                    "alignItems": "center",
                    "padding": "1.5rem",
                    "backgroundColor": "#f8f9fa",
                    "borderRadius": "0.5rem",
                    "borderLeft": f"6px solid {metadata['color']}",
                    "marginBottom": "2rem",
                },
            ),
            html.Div(
                [
                    html.Span(
                        f"{len(workflows)} Use Cases",
                        className="badge bg-secondary",
                        style={"fontSize": "0.9rem"},
                    )
                ],
                className="text-end mt-2",
            ),
        ]
    )

    # Create workflow links list
    links_list = create_workflow_links_list(workflows)

    # Create all modals for this module
    modals = create_all_modals(workflows)

    # Create complete section
    section = dbc.Container(
        [
            header,
            dbc.Row([dbc.Col([links_list], md=12)]),
            modals,  # Add modals container
        ],
        fluid=True,
        className="py-4",
    )

    return section
