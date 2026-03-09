"""
Database Schemas Pages - Route handlers for schema documentation.

This module provides page creation functions for the database schemas section,
using the schema_renderer to generate pages from YAML configurations.

Functions
---------
create_schemas_index_page
    Create the schemas index page
create_biorempp_schema_page
    Create BioRemPP schema page
create_hadeg_schema_page
    Create HADEG schema page
create_kegg_schema_page
    Create KEGG schema page
create_toxcsm_schema_page
    Create ToxCSM schema page
"""

from dash import html

from ...components.base import create_footer, create_header
from .schema_renderer import render_schema_index_page, render_schema_page


def create_schemas_index_page() -> html.Div:
    """
    Create the database schemas index page.

    Returns
    -------
    html.Div
        Complete index page with header, content, and footer
    """
    return html.Div(
        [
            create_header(show_nav=True, logo_size="60px"),
            render_schema_index_page(),
            create_footer(),
        ]
    )


def create_biorempp_schema_page() -> html.Div:
    """
    Create BioRemPP database schema page.

    Returns
    -------
    html.Div
        Complete schema page with header, content, and footer
    """
    return html.Div(
        [
            create_header(show_nav=True, logo_size="60px"),
            render_schema_page("biorempp"),
            create_footer(),
        ]
    )


def create_hadeg_schema_page() -> html.Div:
    """
    Create HADEG database schema page.

    Returns
    -------
    html.Div
        Complete schema page with header, content, and footer
    """
    return html.Div(
        [
            create_header(show_nav=True, logo_size="60px"),
            render_schema_page("hadeg"),
            create_footer(),
        ]
    )


def create_kegg_schema_page() -> html.Div:
    """
    Create KEGG degradation database schema page.

    Returns
    -------
    html.Div
        Complete schema page with header, content, and footer
    """
    return html.Div(
        [
            create_header(show_nav=True, logo_size="60px"),
            render_schema_page("kegg"),
            create_footer(),
        ]
    )


def create_toxcsm_schema_page() -> html.Div:
    """
    Create ToxCSM database schema page.

    Returns
    -------
    html.Div
        Complete schema page with header, content, and footer
    """
    return html.Div(
        [
            create_header(show_nav=True, logo_size="60px"),
            render_schema_page("toxcsm"),
            create_footer(),
        ]
    )
