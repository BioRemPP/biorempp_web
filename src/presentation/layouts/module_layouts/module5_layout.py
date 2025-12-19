"""
Module 5 Layout - BioRemPP v1.0
===============================

Module 5: Modeling Interactions of Samples, Genes and Compounds section layout.
"""

from dash import html

from src.presentation.components.module_descriptions import create_module5_description

# UC layouts
from src.presentation.layouts.module5 import (
    create_uc_5_1_layout,
    create_uc_5_2_layout,
    create_uc_5_3_layout,
    create_uc_5_4_layout,
    create_uc_5_5_layout,
    create_uc_5_6_layout,
)


def create_module5_section() -> html.Div:
    """
    Assembles the complete Module 5 section layout.

    Module 5 focuses on mapping the interaction landscape between samples,
    genes, and compounds using advanced network and visualization techniques.

    Returns
    -------
    html.Div
        Complete Module 5 section containing the overview and all use cases.



    Functions
    ---------
    create_module5_section
        Creates the complete Module 5 section, including all use cases (UC-5.1 through UC-5.6).

    Notes
    -----
    This module orchestrates the Module 5 overview header and its six analysis components, focusing on mapping the interaction landscape between samples, genes, and compounds through network analysis and chord diagrams.
    """
    # Module overview header
    description_component = create_module5_description()

    # Use Case Layouts
    uc_5_1_card = create_uc_5_1_layout()
    uc_5_2_card = create_uc_5_2_layout()
    uc_5_3_card = create_uc_5_3_layout()
    uc_5_4_card = create_uc_5_4_layout()
    uc_5_5_card = create_uc_5_5_layout()
    uc_5_6_card = create_uc_5_6_layout()

    # Horizontal rule separator for end of section
    hr = html.Hr(style={"margin": "3rem 0", "borderColor": "#dee2e6"})

    # Assemble complete Module 5 section
    section = html.Div(
        [
            description_component,
            html.Hr(style={"margin": "2rem 0", "borderColor": "#dee2e6"}),
            uc_5_1_card,
            uc_5_2_card,
            uc_5_3_card,
            uc_5_4_card,
            uc_5_5_card,
            uc_5_6_card,
            hr,
        ],
        id="module5-section",
        className="module-section",
    )

    return section
