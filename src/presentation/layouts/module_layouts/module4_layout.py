"""
Module 4 Layout - BioRemPP v1.0
===============================

Module 4: Functional and Genetic Profiling section layout.
"""

from dash import html

from src.presentation.components.module_descriptions import create_module4_description

# UC layouts
from src.presentation.layouts.module4 import (
    create_uc_4_1_layout,
    create_uc_4_2_layout,
    create_uc_4_3_layout,
    create_uc_4_4_layout,
    create_uc_4_5_layout,
    create_uc_4_6_layout,
    create_uc_4_7_layout,
    create_uc_4_8_layout,
    create_uc_4_9_layout,
    create_uc_4_10_layout,
    create_uc_4_11_layout,
    create_uc_4_12_layout,
    create_uc_4_13_layout,
)


def create_module4_section() -> html.Div:
    """
    Assembles the complete Module 4 section layout.

    Module 4 focuses on functional and genetic profiling to provide actionable
    insights for practical bioremediation applications.

    Returns
    -------
    html.Div
        Complete Module 4 section containing the overview and all use cases.

    Functions
    ---------
    create_module4_section
        Creates the complete Module 4 section, including all use cases (UC-4.1 through UC-4.13).

    Notes
    -----
    This module orchestrates the Module 4 overview header and its thirteen analysis components, focusing on providing actionable insights for practical bioremediation through detailed functional and genetic profiling.
    """
    # Module overview header
    description_component = create_module4_description()

    # Use Case Layouts
    uc_4_1_card = create_uc_4_1_layout()
    uc_4_2_card = create_uc_4_2_layout()
    uc_4_3_card = create_uc_4_3_layout()
    uc_4_4_card = create_uc_4_4_layout()
    uc_4_5_card = create_uc_4_5_layout()
    uc_4_6_card = create_uc_4_6_layout()
    uc_4_7_card = create_uc_4_7_layout()
    uc_4_8_card = create_uc_4_8_layout()
    uc_4_9_card = create_uc_4_9_layout()
    uc_4_10_card = create_uc_4_10_layout()
    uc_4_11_card = create_uc_4_11_layout()
    uc_4_12_card = create_uc_4_12_layout()
    uc_4_13_card = create_uc_4_13_layout()

    # Horizontal rule separator for end of section
    hr = html.Hr(style={"margin": "3rem 0", "borderColor": "#dee2e6"})

    # Assemble complete Module 4 section
    section = html.Div(
        [
            description_component,
            html.Hr(style={"margin": "2rem 0", "borderColor": "#dee2e6"}),
            uc_4_1_card,
            uc_4_2_card,
            uc_4_3_card,
            uc_4_4_card,
            uc_4_5_card,
            uc_4_6_card,
            uc_4_7_card,
            uc_4_8_card,
            uc_4_9_card,
            uc_4_10_card,
            uc_4_11_card,
            uc_4_12_card,
            uc_4_13_card,
            hr,
        ],
        id="module4-section",
        className="module-section",
    )

    return section
