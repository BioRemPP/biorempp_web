"""
Action Button Component - Atomic UI Component.

Creates styled buttons for user actions.

Functions
---------
create_button
    Create button component with label and variant

Notes
-----
- Atomic component
- Supports multiple Bootstrap variants
- Size options: sm, md, lg
"""

from typing import Literal, Optional

import dash_bootstrap_components as dbc
from dash import html

ButtonVariant = Literal[
    "primary",
    "success",
    "secondary",
    "danger",
    "warning",
    "info",
    "light",
    "dark",
    "link",
]
ButtonSize = Literal["sm", "md", "lg"]


def create_button(
    component_id: str,
    label: str,
    variant: ButtonVariant = "primary",
    size: ButtonSize = "md",
    outline: bool = False,
    disabled: bool = False,
    icon: Optional[str] = None,
    href: Optional[str] = None,
) -> dbc.Button:
    """
    Create action button component.

    Parameters
    ----------
    component_id : str
        ID for the button component
    label : str
        Button text label
    variant : ButtonVariant, optional
        Bootstrap color variant, by default "primary"
        Options: primary, success, secondary, danger, warning, info, light, dark, link
    size : ButtonSize, optional
        Button size, by default "md"
        Options: sm, md, lg
    outline : bool, optional
        Use outline style instead of solid, by default False
    disabled : bool, optional
        Disable button interaction, by default False
    icon : Optional[str], optional
        FontAwesome icon class (e.g., "fas fa-upload"), by default None
    href : Optional[str], optional
        Link URL if button is a link, by default None

    Returns
    -------
    dbc.Button
        Styled button component

    Examples
    --------
    >>> btn = create_button("submit-btn", "Submit", variant="success")
    >>> btn = create_button("cancel-btn", "Cancel", variant="secondary", outline=True)
    >>> btn = create_button("upload-btn", "Upload", icon="fas fa-upload", size="lg")
    >>> btn = create_button("help-btn", "Help", variant="link", href="/help")

    Notes
    -----
    - Default variant: primary (blue)
    - Success variant: green (#28a745)
    - Icon placed before label
    - Size classes: btn-sm, btn-md (default), btn-lg
    """
    button_children = label
    if icon:
        button_children = [html.I(className=f"{icon} me-2"), html.Span(label)]

    size_class = None if size == "md" else size

    return dbc.Button(
        button_children,
        id=component_id,
        color=variant,
        outline=outline,
        size=size_class,
        disabled=disabled,
        href=href,
        className="me-2",
    )
