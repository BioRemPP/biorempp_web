"""
Module 3 Layout - BioRemPP v1.0
===============================

Module 3: System Structure: Clustering, Similarity, Co-occurrence section layout.
"""

from dash import html

from src.presentation.components.module_descriptions import create_module3_description

# UC layouts
from src.presentation.layouts.module3 import (
    create_uc_3_1_layout,
    create_uc_3_2_layout,
    create_uc_3_3_layout,
    create_uc_3_4_layout,
    create_uc_3_5_layout,
    create_uc_3_6_layout,
    create_uc_3_7_layout,
)


def create_module3_section() -> html.Div:
    """
    Assembles the complete Module 3 section layout.

    Module 3 performs statistical analysis to identify sample relationships,
    functional similarities, and molecular co-occurrence networks.

    Returns
    -------
    html.Div
        Complete Module 3 section containing the overview and all use cases.

    Functions
    ---------
    create_module3_section
        Creates the complete Module 3 section, including all use cases (UC-3.1 through UC-3.7).

    Notes
    -----
    This module orchestrates the Module 3 overview header and its seven analysis components, focusing on uncovering emergent system structure through advanced statistical and graph-based analysis.
    """
    # Module overview header
    description_component = create_module3_description()

    # Use Case Layouts
    uc_3_1_card = create_uc_3_1_layout()
    uc_3_2_card = create_uc_3_2_layout()
    uc_3_3_card = create_uc_3_3_layout()
    uc_3_4_card = create_uc_3_4_layout()
    uc_3_5_card = create_uc_3_5_layout()
    uc_3_6_card = create_uc_3_6_layout()
    uc_3_7_card = create_uc_3_7_layout()

    # Horizontal rule separator for end of section
    hr = html.Hr(style={"margin": "3rem 0", "borderColor": "#dee2e6"})

    # Assemble complete Module 3 section
    section = html.Div(
        [
            description_component,
            html.Hr(style={"margin": "2rem 0", "borderColor": "#dee2e6"}),
            uc_3_1_card,
            uc_3_2_card,
            uc_3_3_card,
            uc_3_4_card,
            uc_3_5_card,
            uc_3_6_card,
            uc_3_7_card,
            hr,
        ],
        id="module3-section",
        className="module-section",
    )

    return section
