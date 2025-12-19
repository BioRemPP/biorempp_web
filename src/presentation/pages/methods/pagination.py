"""
Pagination Component

Creates module-based pagination controls for navigating between modules.
"""

import dash_bootstrap_components as dbc
from dash import html

from .module_metadata import get_module_metadata


def create_pagination(current_module: int, total_modules: int = 8) -> html.Div:
    """
    Create pagination controls for module navigation.

    Args:
        current_module: Currently displayed module (1-8)
        total_modules: Total number of modules (default: 8)

    Returns:
        html.Div containing pagination controls.
    """
    # Create pagination items
    items = []

    # Previous button
    items.append(
        dbc.Button(
            "Previous",
            id="methods-pagination-prev",
            disabled=(current_module == 1),
            color="secondary",
            outline=True,
            size="sm",
            className="me-2",
            n_clicks=0,
        )
    )

    # Module number buttons
    for module_num in range(1, total_modules + 1):
        metadata = get_module_metadata(module_num)

        items.append(
            dbc.Button(
                f"M{module_num}",
                id=f"methods-pagination-{module_num}",
                color="primary" if module_num == current_module else "secondary",
                outline=(module_num != current_module),
                size="sm",
                className="me-2",
                n_clicks=0,
            )
        )

    # Next button
    items.append(
        dbc.Button(
            "Next",
            id="methods-pagination-next",
            disabled=(current_module == total_modules),
            color="secondary",
            outline=True,
            size="sm",
            n_clicks=0,
        )
    )

    # Create button group
    button_group = dbc.ButtonGroup(
        items, className="d-flex justify-content-center flex-wrap mb-3"
    )

    # Add module info below pagination
    current_metadata = get_module_metadata(current_module)
    module_info = html.Div(
        html.Small(
            f"Viewing: {current_metadata['short_title']} ({current_metadata['use_case_count']} use cases)",
            className="text-muted text-center d-block",
        ),
        className="mb-3",
    )

    return html.Div([button_group, module_info])
