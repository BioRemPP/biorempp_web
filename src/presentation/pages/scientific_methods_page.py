"""
Scientific Methods Overview Page - Entry Point.

Main entry point for the scientific methods overview page that precedes
the detailed workflow methods page.

Functions
---------
create_scientific_methods_page
    Create scientific methods overview page layout

Notes
-----
- Entry point for /methods/overview route
- Loads data via overview_service
- Uses overview_layout for UI components
"""

from dash import html

from .methods.overview_layout import create_scientific_overview_layout


def create_scientific_methods_page() -> html.Div:
    """
    Create scientific methods overview page.

    Returns
    -------
    html.Div
        Complete scientific methods overview page layout.

    Examples
    --------
    >>> from src.presentation.pages import scientific_methods_page
    >>> layout = scientific_methods_page.create_scientific_methods_page()

    Notes
    -----
    - This page provides scientific foundations before users access detailed workflows
    - Covers 4 main sections: Scientific Metrics, Data Science, FAIR Principles, Multi-omics
    - Includes call-to-action to detailed methods page
    """
    return create_scientific_overview_layout()
