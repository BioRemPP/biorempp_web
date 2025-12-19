"""
Module 1 Layout - BioRemPP v1.0
===============================

Module 1: Comparative Assessment of Databases, Samples, and Regulatory Frameworks section layout.
"""

from dash import html

from ...components.module_descriptions.module1_description import (
    create_module1_description,
)
from ..module1 import (
    create_uc_1_1_layout,
    create_uc_1_2_layout,
    create_uc_1_3_layout,
    create_uc_1_4_layout,
    create_uc_1_5_layout,
    create_uc_1_6_layout,
)


def create_module1_section() -> html.Div:
    """
    Assembles the complete Module 1 section layout.

    Module 1 serves as the foundation for subsequent analyses by performing database
    validation, quality assurance, regulatory framework integration, and sample
    prioritization.

    Returns
    -------
    html.Div
        Complete Module 1 section containing the overview and all use cases.

    Functions
    ---------
    create_module1_section
        Creates the complete Module 1 section, including all use cases.

    Notes
    -----
    This module orchestrates the Module 1 overview header and its six analysis
    components (UC 1.1 through 1.6), primarily focusing on database validation and
    regulatory assessment within the BioRemPP framework.
    """
    # Module 1 overview header
    module1_description = create_module1_description()

    # Use Case Layouts
    uc_1_1 = create_uc_1_1_layout()
    uc_1_2 = create_uc_1_2_layout()
    uc_1_3 = create_uc_1_3_layout()
    uc_1_4 = create_uc_1_4_layout()
    uc_1_5 = create_uc_1_5_layout()
    uc_1_6 = create_uc_1_6_layout()

    # Horizontal rule separator for end of section
    hr = html.Hr(style={"margin": "3rem 0", "borderColor": "#dee2e6"})

    # Assemble complete Module 1 section
    return html.Div(
        [
            module1_description,
            html.Hr(style={"margin": "2rem 0", "borderColor": "#dee2e6"}),
            uc_1_1,
            uc_1_2,
            uc_1_3,
            uc_1_4,
            uc_1_5,
            uc_1_6,
            hr,
        ],
        id="module1-section",
        className="module-section",
    )
