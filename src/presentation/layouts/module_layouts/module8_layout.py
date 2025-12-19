"""
Module 8 Layout - BioRemPP v1.0
================================

Module 8: Assembly of Functional Consortia section layout.
"""

from dash import html

from src.presentation.components.module_descriptions import create_module8_description
from src.presentation.layouts.module8 import (
    create_uc_8_1_layout,
    create_uc_8_2_layout,
    create_uc_8_3_layout,
    create_uc_8_4_layout,
    create_uc_8_5_layout,
    create_uc_8_6_layout,
    create_uc_8_7_layout,
)


def create_module8_section() -> html.Div:
    """
    Assembles the complete Module 8 section layout.

    Module 8 focuses on multi-objective optimization for consortium design,
    providing actionable blueprints for bioremediation system assembly.

    Returns
    -------
    html.Div
        Complete Module 8 section with overview and use cases.

    Functions
    ---------
    create_module8_section
        Creates the complete Module 8 section, including all use cases (UC-8.1 through UC-8.7).

    Notes
    -----
    This module orchestrates the Module 8 overview header and its seven analysis components, focusing on consortium design and optimization strategies.
    """
    # Module 8 overview header
    description_component = create_module8_description()

    # Use Cases
    uc_8_1 = create_uc_8_1_layout()
    uc_8_2 = create_uc_8_2_layout()
    uc_8_3 = create_uc_8_3_layout()
    uc_8_4 = create_uc_8_4_layout()
    uc_8_5 = create_uc_8_5_layout()
    uc_8_6 = create_uc_8_6_layout()
    uc_8_7 = create_uc_8_7_layout()

    # Horizontal rule separator
    hr = html.Hr(style={"margin": "3rem 0", "borderColor": "#dee2e6"})

    # Assemble complete Module 8 section
    return html.Div(
        [
            description_component,
            html.Hr(style={"margin": "2rem 0", "borderColor": "#dee2e6"}),
            uc_8_1,
            uc_8_2,
            uc_8_3,
            uc_8_4,
            uc_8_5,
            uc_8_6,
            uc_8_7,
            hr,
        ],
        id="module8-section",
        className="module-section",
    )
