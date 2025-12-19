"""
Module 2 Layout - BioRemPP v1.0
===============================

Module 2: Exploratory Analysis - Gene Counts and Distributions section layout.
"""

from dash import html

from src.presentation.components.module_descriptions import create_module2_description
from src.presentation.layouts.module2 import (
    create_uc_2_1_layout,
    create_uc_2_2_layout,
    create_uc_2_3_layout,
    create_uc_2_4_layout,
    create_uc_2_5_layout,
)


def create_module2_section() -> html.Div:
    """
    Assembles the complete Module 2 section layout.

    Module 2 focuses on exploratory analysis, ranking samples and compounds
    by functional and chemical richness.

    Returns
    -------
    html.Div
        Complete Module 2 section containing the overview and all use cases.

    Functions
    ---------
    create_module2_section
        Creates the complete Module 2 section, including all use cases.

    Notes
    -----
    This module orchestrates the Module 2 overview header and its five analysis components (UC 2.1 through 2.5), primarily focusing on ranking samples and compounds by functional and chemical richness.
    """
    # Module description with scientific context
    description_component = create_module2_description()

    # Use Case Layouts
    uc_2_1_card = create_uc_2_1_layout()
    uc_2_2_card = create_uc_2_2_layout()
    uc_2_3_card = create_uc_2_3_layout()
    uc_2_4_card = create_uc_2_4_layout()
    uc_2_5_card = create_uc_2_5_layout()

    # Horizontal rule separator for end of section
    hr = html.Hr(style={"margin": "3rem 0", "borderColor": "#dee2e6"})

    # Assemble complete Module 2 section
    section = html.Div(
        [
            description_component,
            html.Hr(style={"margin": "2rem 0", "borderColor": "#dee2e6"}),
            uc_2_1_card,
            uc_2_2_card,
            uc_2_3_card,
            uc_2_4_card,
            uc_2_5_card,
            hr,
        ],
        id="module2-section",
        className="module-section",
    )

    return section
