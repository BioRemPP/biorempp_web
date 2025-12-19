"""
Module 7 Layout - BioRemPP v1.0
===============================

Module 7: Toxicological Risk Assessment and Profiling section layout.
"""

from dash import html

from src.presentation.components.module_descriptions import create_module7_description

# UC layouts
from src.presentation.layouts.module7 import (
    create_uc_7_1_layout,
    create_uc_7_2_layout,
    create_uc_7_3_layout,
    create_uc_7_4_layout,
    create_uc_7_5_layout,
    create_uc_7_6_layout,
    create_uc_7_7_layout,
)


def create_module7_section() -> html.Div:
    """
    Assembles the complete Module 7 section layout.

    Module 7 performs toxicological risk assessment and profiling to identify
    and map sample mitigation capabilities.

    Returns
    -------
    html.Div
        Complete Module 7 section containing the overview and all use cases.


    Functions
    ---------
    create_module7_section
        Creates the complete Module 7 section, including all use cases (UC-7.1 through UC-7.7).

    Notes
    -----
    This module orchestrates the Module 7 overview header and its seven analysis components, focusing on systematic toxicological risk evaluation and mapping sample mitigation capabilities for application-oriented consortium design.
    """
    # Module description with scientific context
    description_component = create_module7_description()

    # Assemble use case cards (each from its own module)
    uc_7_1_card = create_uc_7_1_layout()
    uc_7_2_card = create_uc_7_2_layout()
    uc_7_3_card = create_uc_7_3_layout()
    uc_7_4_card = create_uc_7_4_layout()
    uc_7_5_card = create_uc_7_5_layout()
    uc_7_6_card = create_uc_7_6_layout()
    uc_7_7_card = create_uc_7_7_layout()

    # Complete section assembly
    section = html.Div(
        [
            description_component,
            html.Hr(style={"margin": "2rem 0", "borderColor": "#dee2e6"}),
            # UC-7.1: Faceted Heatmap of Predicted Compound Toxicity Profiles
            uc_7_1_card,
            # UC-7.2: Concordance Between Predicted Risk and Regulatory Focus
            uc_7_2_card,
            # UC-7.3: Elite Specialist Identification (Genetic Response Mapping)
            uc_7_3_card,
            # UC-7.4: Toxicity Score Distribution
            uc_7_4_card,
            # UC-7.5: Interactive Distribution of Toxicity Scores by Endpoint Category
            uc_7_5_card,
            # UC-7.6: Sample Risk Mitigation Breadth by Compound Variety
            uc_7_6_card,
            # UC-7.7: Sample Risk Mitigation Depth Profile by Genetic Investment
            uc_7_7_card,
            html.Hr(className="my-4"),
        ],
        id="module7-section",
        className="module-section",
    )

    return section
