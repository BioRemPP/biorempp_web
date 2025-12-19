"""
Module 6 Layout - BioRemPP v1.0
===============================

Module 6: Hierarchical and Flow-based Functional Analysis section layout.
"""

from dash import html

from src.presentation.components.module_descriptions import create_module6_description

# UC layouts
from src.presentation.layouts.module6 import (
    create_uc_6_1_layout,
    create_uc_6_2_layout,
    create_uc_6_3_layout,
    create_uc_6_4_layout,
    create_uc_6_5_layout,
)


def create_module6_section() -> html.Div:
    """
    Assembles the complete Module 6 section layout.

    Module 6 focuses on strategic analysis of functional architecture using
    flow diagrams and hierarchical composition analysis.

    Returns
    -------
    html.Div
        Complete Module 6 section containing the overview and all use cases.



    Functions
    ---------
    create_module6_section
        Creates the complete Module 6 section, including all use cases (UC-6.1 through UC-6.5).

    Notes
    -----
    This module orchestrates the Module 6 overview header and its five analysis components, focusing on strategic overview of functional architecture through flow diagrams and hierarchical composition analysis.
    """
    # Module description with scientific context
    description_component = create_module6_description()

    # Assemble use case cards (each from its own module)
    uc_6_1_card = create_uc_6_1_layout()
    uc_6_2_card = create_uc_6_2_layout()
    uc_6_3_card = create_uc_6_3_layout()
    uc_6_4_card = create_uc_6_4_layout()
    uc_6_5_card = create_uc_6_5_layout()

    # Horizontal rule separator for end of section
    hr = html.Hr(style={"margin": "3rem 0", "borderColor": "#dee2e6"})

    # Complete section assembly
    section = html.Div(
        [
            description_component,
            html.Hr(style={"margin": "2rem 0", "borderColor": "#dee2e6"}),
            # UC-6.1: Regulatory to Molecular Interaction Flow
            uc_6_1_card,
            # UC-6.2: Biological Interaction Flow
            uc_6_2_card,
            # UC-6.3: Chemical Hierarchy of Bioremediation
            uc_6_3_card,
            # UC-6.4: Overview of Enzymatic Activity and Substrate Scope
            uc_6_4_card,
            # UC-6.5: Chemical-Enzymatic Landscape by Substrate Scope
            uc_6_5_card,
            html.Hr(className="my-4"),
        ],
        id="module6-section",
        className="module-section",
    )

    return section
