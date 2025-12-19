"""
AG Grid Table Component - Enterprise-Grade Data Tables.

Creates interactive AG Grid tables with built-in filtering, sorting,
and pagination functionality.

Functions
---------
create_ag_grid_table
    Create AG Grid table component with all features enabled

Notes
-----
- Uses dash_ag_grid for advanced table features
- Built-in column filtering (text, number, date)
- Multi-column sorting
- Row selection
- Pagination with configurable page size
- Responsive design
"""

from typing import Any, Dict, List, Literal, Optional

import dash_ag_grid as dag
import dash_bootstrap_components as dbc
import pandas as pd
from dash import html


def create_ag_grid_table(
    table_id: str,
    data: Optional[pd.DataFrame] = None,
    title: Optional[str] = None,
    page_size: int = 50,
    enable_selection: bool = False,
    selection_mode: Literal["single", "multiple"] = "multiple",
    custom_column_defs: Optional[List[Dict[str, Any]]] = None,
    default_col_def: Optional[Dict[str, Any]] = None,
    style_header: Optional[Dict[str, str]] = None,
    card_wrapper: bool = True,
) -> dbc.Card | dag.AgGrid:
    """
    Create AG Grid table with enterprise features.

    Parameters
    ----------
    table_id : str
        Unique ID for the AG Grid component
    data : Optional[pd.DataFrame], optional
        DataFrame with table data, by default None
    title : Optional[str], optional
        Table title (only used if card_wrapper=True), by default None
    page_size : int, optional
        Rows per page, by default 50
    enable_selection : bool, optional
        Enable row selection, by default False
    selection_mode : Literal['single', 'multiple'], optional
        Row selection mode, by default 'multiple'
    custom_column_defs : Optional[List[Dict[str, Any]]], optional
        Custom column definitions (overrides auto-generation), by default None
    default_col_def : Optional[Dict[str, Any]], optional
        Default column definition properties, by default None
    style_header : Optional[Dict[str, str]], optional
        Custom header styling, by default None
    card_wrapper : bool, optional
        Wrap table in Bootstrap card, by default True

    Returns
    -------
    dbc.Card | dag.AgGrid
        AG Grid component (wrapped in card if card_wrapper=True)

    Examples
    --------
    >>> import pandas as pd
    >>> df = pd.DataFrame({
    ...     'Sample': ['S1', 'S2', 'S3'],
    ...     'KO_Count': [150, 200, 175],
    ...     'Database': ['BioRemPP', 'HADEG', 'KEGG']
    ... })
    >>> table = create_ag_grid_table(
    ...     table_id='biorempp-grid',
    ...     data=df,
    ...     title='BioRemPP Results',
    ...     page_size=50
    ... )

    Notes
    -----
    Built-in Features:
    - Column Filters: Click filter icon in column header
    - Sorting: Click column header to sort (Shift+Click for multi-sort)
    - Pagination: Navigate using bottom controls
    - Responsive: Automatically adjusts to container width

    Column Types:
    - Text columns: Contains text filter
    - Number columns: Number range filter
    - Date columns: Date range filter
    """
    # Handle empty data
    if data is None or data.empty:
        empty_message = dbc.Alert(
            [
                html.I(className="fas fa-info-circle me-2"),
                "No data available to display.",
            ],
            color="info",
            className="mb-0",
        )
        if card_wrapper and title:
            return dbc.Card(
                [
                    dbc.CardHeader(
                        [html.I(className="fas fa-table me-2"), title],
                        className="bg-success text-white fw-bold",
                    ),
                    dbc.CardBody(empty_message),
                ],
                className="shadow-sm mb-4",
            )
        return empty_message

    # Auto-generate column definitions if not provided
    if custom_column_defs is None:
        column_defs = _auto_generate_column_defs(data)
    else:
        column_defs = custom_column_defs

    # Default column definition (applies to all columns)
    if default_col_def is None:
        default_col_def = {
            "resizable": True,
            "sortable": True,
            "filter": True,
            "floatingFilter": True,
            "minWidth": 100,
            "menuTabs": ["filterMenuTab", "generalMenuTab"],
        }

    # Dashboard configuration with pagination settings
    dashboard_config = {
        "pagination": True,
        "paginationPageSize": page_size,
        "paginationPageSizeSelector": [10, 25, 50, 100, 200],
        "animateRows": True,
        "rowHeight": 40,
        "defaultColDef": default_col_def,
    }

    # Add selection-specific config if enabled
    if enable_selection:
        dashboard_config["rowSelection"] = selection_mode
        dashboard_config["statusBar"] = {
            "statusPanels": [
                {"statusPanel": "agTotalRowCountComponent", "align": "left"},
                {"statusPanel": "agFilteredRowCountComponent"},
                {"statusPanel": "agSelectedRowCountComponent"},
            ]
        }

    # AG Grid component
    ag_grid = dag.AgGrid(
        id=table_id,
        rowData=data.to_dict("records"),
        columnDefs=column_defs,
        className="ag-theme-alpine",
        style={"height": "600px", "width": "100%"},
        dashGridOptions=dashboard_config,
    )

    # Info text with filtering and sorting instructions
    info_text = html.Div(
        [
            html.Small(
                [
                    html.I(className="fas fa-info-circle me-1"),
                    "Click column headers to sort. ",
                    "Use filter boxes to search. ",
                    "Shift+Click for multi-column sorting.",
                ],
                className="text-muted",
            )
        ],
        className="mb-2",
    )

    # Wrap in card if requested
    if card_wrapper:
        if title:
            return dbc.Card(
                [
                    dbc.CardHeader(
                        [html.I(className="fas fa-table me-2"), title],
                        className="bg-success text-white fw-bold",
                    ),
                    dbc.CardBody([info_text, ag_grid]),
                ],
                className="shadow-sm mb-4",
            )
        else:
            return dbc.Card(
                [dbc.CardBody([info_text, ag_grid])], className="shadow-sm mb-4"
            )

    # Return bare AG Grid
    return ag_grid


def _auto_generate_column_defs(df: pd.DataFrame) -> List[Dict[str, Any]]:
    """
    Auto-generate column definitions from DataFrame.

    Parameters
    ----------
    df : pd.DataFrame
        Input DataFrame

    Returns
    -------
    List[Dict[str, Any]]
        Column definitions for AG Grid

    Notes
    -----
    Automatically detects:
    - Numeric columns → number filter
    - Date columns → date filter
    - Text columns → text filter
    - Sets appropriate column widths
    """
    column_defs = []

    for col in df.columns:
        col_def = {"field": col, "headerName": col, "filter": True}

        # Detect column type and set appropriate filter
        dtype = df[col].dtype

        if pd.api.types.is_numeric_dtype(dtype):
            col_def["filter"] = "agNumberColumnFilter"
            col_def["type"] = "numericColumn"
        elif pd.api.types.is_datetime64_any_dtype(dtype):
            col_def["filter"] = "agDateColumnFilter"
        else:
            col_def["filter"] = "agTextColumnFilter"

        # Set column width based on content
        max_len = df[col].astype(str).str.len().max()
        if max_len < 10:
            col_def["width"] = 120
        elif max_len < 30:
            col_def["width"] = 200
        else:
            col_def["width"] = 300

        column_defs.append(col_def)

    return column_defs


def create_ondemand_ag_grid(
    table_id: str,
    button_id: str,
    container_id: str,
    title: str,
    description: Optional[str] = None,
    icon: str = "fas fa-table",
) -> dbc.Card:
    """
    Create on-demand AG Grid table with trigger button.

    Parameters
    ----------
    table_id : str
        ID for the AG Grid component
    button_id : str
        ID for the trigger button
    container_id : str
        ID for the table container div
    title : str
        Table card title
    description : Optional[str], optional
        Optional description text, by default None
    icon : str, optional
        FontAwesome icon class, by default "fas fa-table"

    Returns
    -------
    dbc.Card
        Card component with button and empty container

    Examples
    --------
    >>> table = create_ondemand_ag_grid(
    ...     table_id="biorempp-grid",
    ...     button_id="view-biorempp-btn",
    ...     container_id="biorempp-container",
    ...     title="BioRemPP Results"
    ... )

    Notes
    -----
    - Container is initially empty
    - Callback populates container when button clicked
    - Designed for large datasets that shouldn't load immediately
    """
    return dbc.Card(
        [
            dbc.CardHeader(
                [html.I(className=f"{icon} me-2"), title],
                className="bg-success text-white fw-bold",
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
        className="shadow-sm mb-4",
    )
