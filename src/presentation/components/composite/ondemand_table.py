"""
On-Demand Table Component - BioRemPP v1.0
==========================================

Reusable component for on-demand table rendering with trigger button.
"""

from typing import Optional

import dash_bootstrap_components as dbc
import pandas as pd
from dash import dash_table, html


def create_ondemand_table(
    table_id: str,
    button_id: str,
    container_id: str,
    title: str,
    description: Optional[str] = None,
    icon: str = "fas fa-table",
) -> dbc.Card:
    """
    Create on-demand table component with trigger button.

    Parameters
    ----------
    table_id : str
        ID for the DataTable component
    button_id : str
        ID for the trigger button
    container_id : str
        ID for the table container div
    title : str
        Table card title
    description : Optional[str]
        Optional description text
    icon : str
        FontAwesome icon class

    Returns
    -------
    dbc.Card
        Card component with button and empty container

    Examples
    --------
    >>> table = create_ondemand_table(
    ...     table_id="biorempp-table",
    ...     button_id="view-biorempp-btn",
    ...     container_id="biorempp-container",
    ...     title="BioRemPP Results"
    ... )

    Notes
    -----
    - Container is initially empty
    - Callback populates container when button clicked
    - Reusable for both tables and charts
    """
    return dbc.Card(
        [
            dbc.CardHeader(
                [html.I(className=f"{icon} me-2"), title],
                className="bg-success text-white",
            ),
            dbc.CardBody(
                [
                    # Description
                    (
                        html.P(
                            description or f"Click below to view {title}",
                            className="text-muted mb-3",
                        )
                        if description
                        else html.Div()
                    ),
                    # Trigger Button
                    html.Div(
                        [
                            dbc.Button(
                                [html.I(className="fas fa-eye me-2"), f"View {title}"],
                                id=button_id,
                                color="success",
                                className="mb-3",
                            )
                        ]
                    ),
                    # Table Container (initially empty)
                    html.Div(id=container_id, children=[]),
                ]
            ),
        ],
        className="mb-4",
    )


def create_data_table(
    data: pd.DataFrame, table_id: str, page_size: int = 5
) -> dash_table.DataTable:
    """
    Create DataTable component from DataFrame.

    Parameters
    ----------
    data : pd.DataFrame
        Data to display
    table_id : str
        Table ID
    page_size : int
        Rows per page (default: 5)

    Returns
    -------
    dash_table.DataTable
        Configured DataTable
    """
    if data.empty:
        return html.Div(
            [
                dbc.Alert(
                    [html.I(className="fas fa-info-circle me-2"), "No data available"],
                    color="info",
                )
            ]
        )

    return dash_table.DataTable(
        id=table_id,
        data=data.to_dict("records"),
        columns=[{"name": col, "id": col} for col in data.columns],
        page_size=page_size,
        page_action="native",
        sort_action="native",
        filter_action="native",
        style_table={"overflowX": "auto"},
        style_cell={
            "textAlign": "left",
            "padding": "10px",
            "fontFamily": "Arial, sans-serif",
            "fontSize": "14px",
        },
        style_header={
            "backgroundColor": "#198754",
            "color": "white",
            "fontWeight": "bold",
        },
        style_data_conditional=[
            {"if": {"row_index": "odd"}, "backgroundColor": "#f8f9fa"}
        ],
    )
