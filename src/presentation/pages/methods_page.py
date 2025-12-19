"""
Methods Page - Analytical Workflows Display

This page displays comprehensive analytical workflows for all 56 use cases
organized by module with pagination.
"""

from dash import html

from .methods.layout import create_methods_layout


def create_methods_page() -> html.Div:
    """
    Create the Methods page layout.

    Returns:
        html.Div containing the complete Methods page.
    """
    return create_methods_layout()
