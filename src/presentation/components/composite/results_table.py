"""
Results Table Component - Interactive Data Table.

Creates interactive DataTable with export functionality.

Functions
---------
create_results_table
    Create interactive table with sort, filter, pagination

Notes
-----
- dash_table.DataTable with Bootstrap styling
- Sortable and filterable columns
- Pagination (50 rows/page)
- CSV export functionality
"""

from typing import Any, Dict, List, Optional

import dash_bootstrap_components as dbc
import pandas as pd
from dash import dash_table, dcc, html


def create_results_table(
    table_id: str,
    data: Optional[pd.DataFrame] = None,
    title: str = "Results",
    download_filename: str = "results.csv",
    alert_component: Optional[html.Div] = None,
    conditional_styles: Optional[List[Dict]] = None,
) -> dbc.Card:
    """
    Create results table component.

    Parameters
    ----------
    table_id : str
        Unique ID for the DataTable component
    data : Optional[pd.DataFrame], optional
        DataFrame with table data, by default None
    title : str, optional
        Table title, by default "Results"
    download_filename : str, optional
        Filename for CSV export, by default "results.csv"
    alert_component : Optional[html.Div], optional
        Alert to display above table, by default None
    conditional_styles : Optional[List[Dict]], optional
        Conditional formatting rules for cells, by default None

    Returns
    -------
    dbc.Card
        Card containing interactive DataTable

    Examples
    --------
    >>> import pandas as pd
    >>> df = pd.DataFrame({
    ...     'Sample': ['S1', 'S2'],
    ...     'KO': ['K00001', 'K00002'],
    ...     'Compound': ['Benzene', 'Toluene']
    ... })
    >>> table = create_results_table(
    ...     table_id='biorempp-table',
    ...     data=df,
    ...     title='BioRemPP Results'
    ... )

    Notes
    -----
    - Built-in sort (click column headers)
    - Built-in filter (type in column filter boxes)
    - Pagination (50 rows per page)
    - Export CSV button
    - Bootstrap striped/hover styling
    """
    if data is None:
        data = pd.DataFrame()

    # Prepare table data
    table_data = data.to_dict("records") if not data.empty else []
    table_columns = (
        [
            {"name": col, "id": col, "deletable": False, "selectable": True}
            for col in data.columns
        ]
        if not data.empty
        else []
    )

    # Alert section
    alert_section = html.Div()
    if alert_component is not None:
        alert_section = html.Div(alert_component, className="mb-3")

    # Search/Filter info
    filter_info = html.Div(
        [
            html.Small(
                [
                    html.I(className="fas fa-info-circle me-1"),
                    "Click column headers to sort. " "Type in filter boxes to search.",
                ],
                className="text-muted",
            )
        ],
        className="mb-2",
    )

    # DataTable
    data_table = dash_table.DataTable(
        id=table_id,
        data=table_data,
        columns=table_columns,
        filter_action="native",
        sort_action="native",
        sort_mode="multi",
        page_action="native",
        page_current=0,
        page_size=50,
        style_table={"overflowX": "auto", "border": "1px solid #dee2e6"},
        style_header={
            "backgroundColor": "#28a745",
            "color": "white",
            "fontWeight": "bold",
            "textAlign": "left",
            "border": "1px solid white",
        },
        style_cell={
            "textAlign": "left",
            "padding": "10px",
            "border": "1px solid #dee2e6",
            "fontSize": "14px",
        },
        style_data_conditional=(conditional_styles if conditional_styles else []),
        style_as_list_view=False,
        export_format="csv",
        export_headers="display",
    )

    # Export buttons
    export_section = html.Div(
        [
            dbc.Button(
                [html.I(className="fas fa-download me-1"), "Export CSV"],
                id=f"{table_id}-export-csv",
                color="success",
                outline=True,
                size="sm",
                className="me-2",
            ),
            dbc.Button(
                [html.I(className="fas fa-file-excel me-1"), "Export Excel"],
                id=f"{table_id}-export-excel",
                color="success",
                outline=True,
                size="sm",
            ),
            dcc.Download(id=f"{table_id}-download"),
        ],
        className="mt-3",
    )

    # Row count footer
    row_count = len(data) if not data.empty else 0
    footer = html.Div(
        [
            html.Small(
                [html.I(className="fas fa-table me-1"), f"Total rows: {row_count}"],
                className="text-muted",
            )
        ]
    )

    return dbc.Card(
        [
            dbc.CardHeader(
                [
                    html.Div(
                        [
                            html.I(className="fas fa-table me-2"),
                            html.Span(title, className="font-weight-bold"),
                        ],
                        className="d-inline-block",
                    ),
                    html.Div(
                        [
                            dbc.Button(
                                [html.I(className="fas fa-download")],
                                id=f"{table_id}-header-download",
                                color="light",
                                size="sm",
                                className="float-end",
                            )
                        ],
                        className="d-inline-block float-end",
                    ),
                ],
                className="bg-info text-white",
            ),
            dbc.CardBody([alert_section, filter_info, data_table, export_section]),
            dbc.CardFooter(footer, className="bg-light"),
        ],
        className="mb-4",
    )
