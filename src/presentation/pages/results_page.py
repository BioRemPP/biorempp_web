"""
Results Page Layout - BioRemPP v1.0.

Display analysis results with feed-style accordion layout.

Functions
---------
create_results_layout
    Create complete results page layout with accordions

Notes
-----
- Feed-style layout with sections
- Accordion-based table rendering
- Overview card with general information
- 4 database results: BioRemPP, HADEG, ToxCSM, KEGG
- Module 1: Comparative Assessment (Databases, Samples, Regulatory Frameworks)
- Module 2: Exploratory Analysis (Gene Counts and Distributions)
- Module 3: System Structure (Clustering, Similarity, Co-occurrence)
- Module 4: Functional and Genetic Profiling
- Module 5: Modeling Interactions (Samples, Genes, Compounds)
- Module 6: Hierarchical and Flow-based Functional Analysis
- Module 7: Toxicological Risk Assessment and Profiling
- Module 8: Assembly of Functional Consortia
- Modular components for maintainability
"""

from typing import Any, Dict, Optional

import dash_bootstrap_components as dbc
from dash import dcc, html

from src.data_tables import (
    create_biorempp_section,
    create_hadeg_section,
    create_kegg_section,
    create_toxcsm_section,
)

from ..components.base import (
    create_footer,
    create_header,
    create_navigation_button,
    create_navigation_offcanvas,
)
from ..components.composite.analysis_suggestions import (
    create_suggestions_offcanvas,
    create_suggestions_trigger_button,
)
from ..layouts.module_layouts import (
    create_module1_section,
    create_module2_section,
    create_module3_section,
    create_module4_section,
    create_module5_section,
    create_module6_section,
    create_module7_section,
    create_module8_section,
)


def create_results_layout(merged_data: Optional[Dict[str, Any]] = None) -> html.Div:
    """
    Create results page layout with feed-style accordions.

    Parameters
    ----------
    merged_data : Optional[Dict[str, Any]], optional
        Merged data from processing
        Expected keys: biorempp_df, biorempp_raw_df, hadeg_df, hadeg_raw_df,
        toxcsm_df (processed), toxcsm_raw_df (complete 66 columns),
        kegg_df, kegg_raw_df, metadata

    Returns
    -------
    html.Div
        Complete results page layout

    Notes
    -----
    Page Structure:
      - Header (with logo)
      - Overview card (general information)
      - Modular database sections (4 databases)
        Each section is self-contained with:
        - Title and description
        - Download button
        - Analytical highlight
        - Accordion with on-demand table
      - Module 2 overview header (guiding questions)
      - Module 2 exploratory analysis section
      - Module 3 overview header (guiding questions)
      - Module 3 system structure analysis section
      - Module 4 overview header (guiding questions)
      - Module 4 functional and genetic profiling section
      - Module 5 overview header (guiding questions)
      - Module 5 interaction modeling section
      - Module 6 overview header (guiding questions)
      - Module 6 hierarchical and flow-based analysis section
      - Module 7 overview header (guiding questions)
      - Module 7 toxicological risk assessment section
    """
    # Default empty data
    if merged_data is None:
        merged_data = {
            "biorempp_df": [],  # Processed for display
            "biorempp_raw_df": [],  # Complete database for download
            "hadeg_df": [],  # Processed for display
            "hadeg_raw_df": [],  # Complete database for download
            "toxcsm_df": [],  # Processed for graphs (5 columns)
            "toxcsm_raw_df": [],  # Complete database for table (66 columns)
            "kegg_df": [],  # Processed for display
            "kegg_raw_df": [],  # Complete database for download
            "metadata": {},
        }

    metadata = merged_data.get("metadata", {})

    # Header
    header = create_header(show_nav=True, logo_size="80px")

    # Overview Card - Enhanced Design
    overview_card = dbc.Card(
        [
            dbc.CardHeader(
                [
                    dbc.Row(
                        [
                            dbc.Col(
                                [
                                    html.I(className="fas fa-table me-2 text-success"),
                                    html.H4(
                                        "Data Tables and Database Integration",
                                        className="d-inline mb-0",
                                    ),
                                ],
                                width="auto",
                            ),
                            dbc.Col(
                                [
                                    dbc.Badge(
                                        [
                                            html.I(className="fas fa-database me-1"),
                                            "4 Databases",
                                        ],
                                        color="success",
                                        className="me-2",
                                    ),
                                    dbc.Badge(
                                        [
                                            html.I(className="fas fa-chart-line me-1"),
                                            "8 Analysis Modules",
                                        ],
                                        color="info",
                                    ),
                                ],
                                width="auto",
                                className="ms-auto d-none d-md-block",
                            ),
                        ],
                        align="center",
                        className="g-0",
                    )
                ],
                className="bg-light border-bottom",
            ),
            dbc.CardBody(
                [
                    # Overview description
                    html.P(
                        "Comprehensive overview of integrated data across BioRemPP, HADEG, ToxCSM, and KEGG databases",
                        className="text-muted mb-3",
                        style={"lineHeight": "1.6"},
                    ),
                    # Processing statistics
                    dbc.Row(
                        [
                            dbc.Col(
                                [
                                    html.Div(
                                        [
                                            html.I(
                                                className="fas fa-flask text-success mb-2",
                                                style={"fontSize": "1.5rem"},
                                            ),
                                            html.H5(
                                                str(metadata.get("sample_count", 0)),
                                                className="mb-0 text-success",
                                            ),
                                            html.Small(
                                                "Samples Processed",
                                                className="text-muted",
                                            ),
                                        ],
                                        className="text-center",
                                    )
                                ],
                                md=4,
                                className="mb-3 mb-md-0",
                            ),
                            dbc.Col(
                                [
                                    html.Div(
                                        [
                                            html.I(
                                                className="fas fa-dna text-primary mb-2",
                                                style={"fontSize": "1.5rem"},
                                            ),
                                            html.H5(
                                                str(metadata.get("ko_count", 0)),
                                                className="mb-0 text-primary",
                                            ),
                                            html.Small(
                                                "KO Identifiers", className="text-muted"
                                            ),
                                        ],
                                        className="text-center",
                                    )
                                ],
                                md=4,
                                className="mb-3 mb-md-0",
                            ),
                            dbc.Col(
                                [
                                    html.Div(
                                        [
                                            html.I(
                                                className="fas fa-clock text-info mb-2",
                                                style={"fontSize": "1.5rem"},
                                            ),
                                            html.H5(
                                                f"{metadata.get('processing_time', 0):.2f}s",
                                                className="mb-0 text-info",
                                            ),
                                            html.Small(
                                                "Processing Time", className="text-muted"
                                            ),
                                        ],
                                        className="text-center",
                                    )
                                ],
                                md=4,
                            ),
                        ],
                        className="mt-2",
                    ),
                ]
            ),
        ],
        className="mb-4 shadow-sm border-top border-success border-3",
    )

    # Modular Database Sections
    biorempp_section = create_biorempp_section()
    hadeg_section = create_hadeg_section()
    toxcsm_section = create_toxcsm_section()
    kegg_section = create_kegg_section()

    # Module 1: Comparative Assessment
    module1_section = create_module1_section()

    # Module 2: Exploratory Analysis
    module2_section = create_module2_section()

    # Module 3: System Structure
    module3_section = create_module3_section()

    # Module 4: Functional and Genetic Profiling
    module4_section = create_module4_section()

    # Module 5: Modeling Interactions
    module5_section = create_module5_section()

    # Module 6: Hierarchical and Flow-based Analysis
    module6_section = create_module6_section()

    # Module 7: Toxicological Risk Assessment
    module7_section = create_module7_section()

    # Module 8: Assembly of Functional Consortia
    module8_section = create_module8_section()

    # Main Content Container
    main_content = dbc.Container(
        [
            overview_card,
            biorempp_section,
            hadeg_section,
            toxcsm_section,
            kegg_section,
            module1_section,
            module2_section,
            module3_section,
            module4_section,
            module5_section,
            module6_section,
            module7_section,
            module8_section,
        ],
        fluid=False,
        className="my-4",
    )

    # Footer
    footer = create_footer(version="1.0.0", year=2025)

    # Navigation components
    nav_button = create_navigation_button()
    nav_offcanvas = create_navigation_offcanvas()

    # Analytical Suggestions components
    suggestions_button = create_suggestions_trigger_button()
    suggestions_offcanvas = create_suggestions_offcanvas()

    # Complete Layout (NO dcc.Location here - already in main app)
    return html.Div(
        [
            header,
            main_content,
            footer,
            suggestions_button,  # Left side
            nav_button,  # Right side
            suggestions_offcanvas,
            nav_offcanvas,
        ]
    )


def get_results_layout(merged_data: Optional[Dict[str, Any]] = None):
    """
    Get results layout (alias for create_results_layout).

    Parameters
    ----------
    merged_data : Optional[Dict[str, Any]], optional
        Merged data from processing

    Returns
    -------
    html.Div
        Complete results page layout
    """
    return create_results_layout(merged_data)
