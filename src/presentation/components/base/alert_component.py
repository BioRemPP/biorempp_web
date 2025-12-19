"""
Alert Component - Atomic UI Component.

Creates styled alerts for feedback messages.

Functions
---------
create_alert
    Create alert component with message and type

Notes
-----
- Atomic component
- Supports 4 variants: success, error, warning, info
- Dismissable option
"""

from typing import Literal, Optional

import dash_bootstrap_components as dbc
from dash import html

AlertType = Literal["success", "error", "warning", "info"]


def create_alert(
    message: str,
    alert_type: AlertType = "info",
    component_id: Optional[str] = None,
    dismissable: bool = False,
    icon: bool = True,
) -> dbc.Alert:
    """
    Create alert component.

    Parameters
    ----------
    message : str
        Alert message text
    alert_type : AlertType, optional
        Type of alert, by default "info"
        Options: "success", "error", "warning", "info"
    component_id : Optional[str], optional
        ID for the alert component, by default None
    dismissable : bool, optional
        Allow user to dismiss alert, by default False
    icon : bool, optional
        Show icon before message, by default True

    Returns
    -------
    dbc.Alert
        Styled alert component

    Examples
    --------
    >>> alert = create_alert("Upload successful!", "success")
    >>> alert = create_alert("Error processing file", "error", dismissable=True)
    >>> alert = create_alert("Please select a file", "warning", icon=False)

    Notes
    -----
    - Success: green (#28a745)
    - Error: red (danger)
    - Warning: yellow (warning)
    - Info: blue (info)
    - Icons: check, times, exclamation, info-circle
    """
    color_map = {
        "success": "success",
        "error": "danger",
        "warning": "warning",
        "info": "info",
    }

    icon_map = {
        "success": "fas fa-check-circle",
        "error": "fas fa-times-circle",
        "warning": "fas fa-exclamation-triangle",
        "info": "fas fa-info-circle",
    }

    alert_color = color_map.get(alert_type, "info")
    icon_class = icon_map.get(alert_type, "fas fa-info-circle")

    alert_content = message
    if icon:
        alert_content = html.Div(
            [html.I(className=f"{icon_class} me-2"), html.Span(message)],
            className="d-flex align-items-center",
        )

    return dbc.Alert(
        alert_content,
        id=component_id,
        color=alert_color,
        dismissable=dismissable,
        className="mb-3",
    )
