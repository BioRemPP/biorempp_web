"""
User Guide Page - BioRemPP v1.0.

Comprehensive user guide for BioRemPP workflow and analysis.

Functions
---------
create_user_guide_page
    Create complete user guide page layout with workflow instructions

Notes
-----
- Overview of 8 analytical modules
- Step-by-step workflow guidance
- Upload, validation, and processing instructions
- Results navigation and analysis tips
"""

import dash_bootstrap_components as dbc
from dash import html

from ..components.base import create_footer, create_header
from .uc_user_guide import create_interactive_demo_section


def create_intro_section() -> html.Div:
    """
    Create introduction section about BioRemPP.

    Returns
    -------
    html.Div
        Introduction section with framework overview
    """
    return html.Div(
        [
            html.H2(
                [
                    html.I(className="fas fa-info-circle me-2 text-success"),
                    "What is BioRemPP?",
                ],
                className="mb-4",
            ),
            dbc.Card(
                [
                    dbc.CardBody(
                        [
                            html.P(
                                [
                                    html.Strong(
                                        "BioRemPP (Bioremediation Potential Profile)"
                                    ),
                                    " is a comprehensive web-based framework for analyzing genomic potential "
                                    "for bioremediation based on ",
                                    html.Strong("KEGG Orthology (KO) identifiers"),
                                    ".",
                                ],
                                className="lead",
                            ),
                            html.Hr(),
                            html.H5("Framework Capabilities", className="mt-3 mb-3"),
                            html.P(
                                "BioRemPP integrates genomic, biochemical, and toxicological data "
                                "to provide detailed insights into biodegradation pathways, enzyme activities, "
                                "and toxicity profiles of environmental pollutants."
                            ),
                            html.H5("8 Analytical Modules", className="mt-4 mb-3"),
                            html.Ul(
                                [
                                    html.Li(
                                        [
                                            html.Strong("Module 1: "),
                                            "Comparative Assessment of Databases, Samples, and Regulatory Frameworks",
                                        ]
                                    ),
                                    html.Li(
                                        [
                                            html.Strong("Module 2: "),
                                            "Exploratory Analysis - Ranking the Functional Potential of Samples and Compounds",
                                        ]
                                    ),
                                    html.Li(
                                        [
                                            html.Strong("Module 3: "),
                                            "System Structure - Clustering, Similarity, and Co-occurrence",
                                        ]
                                    ),
                                    html.Li(
                                        [
                                            html.Strong("Module 4: "),
                                            "Functional and Genetic Profiling",
                                        ]
                                    ),
                                    html.Li(
                                        [
                                            html.Strong("Module 5: "),
                                            "Modeling Interactions among Samples, Genes, and Compounds",
                                        ]
                                    ),
                                    html.Li(
                                        [
                                            html.Strong("Module 6: "),
                                            "KEGG Pathway Completeness",
                                        ]
                                    ),
                                    html.Li(
                                        [
                                            html.Strong("Module 7: "),
                                            "Toxicological Risk Assessment and Profiling",
                                        ]
                                    ),
                                    html.Li(
                                        [
                                            html.Strong("Module 8: "),
                                            "Assembly of Functional Consortia",
                                        ]
                                    ),
                                ],
                                className="mb-3",
                            ),
                            dbc.Alert(
                                [
                                    html.I(className="fas fa-chart-line me-2"),
                                    html.Strong("56 Use Cases"),
                                    " implemented across all modules for comprehensive bioremediation analysis",
                                ],
                                color="info",
                                className="mt-3",
                            ),
                        ]
                    )
                ],
                className="shadow-sm",
            ),
        ],
        className="mb-5",
    )


def create_workflow_step(
    step_number: int,
    title: str,
    description: str,
    icon: str,
    details: list = None,
    alert_message: str = None,
    alert_type: str = "info",
) -> dbc.Card:
    """
    Create a workflow step card.

    Parameters
    ----------
    step_number : int
        Step number in workflow
    title : str
        Step title
    description : str
        Step description
    icon : str
        FontAwesome icon class
    details : list, optional
        List of detail points
    alert_message : str, optional
        Alert/warning message
    alert_type : str, optional
        Type of alert (info, warning, success, danger)

    Returns
    -------
    dbc.Card
        Workflow step card component
    """
    card_content = [
        dbc.CardHeader(
            [
                html.Div(
                    [
                        html.Span(
                            f"Step {step_number}",
                            className="badge bg-success me-2",
                            style={"fontSize": "1rem"},
                        ),
                        html.I(className=f"{icon} me-2 text-success"),
                        html.Strong(title),
                    ],
                    style={"fontSize": "1.2rem"},
                )
            ],
            className="bg-light",
        ),
        dbc.CardBody(
            [
                html.P(description, className="mb-3"),
                (
                    html.Ul([html.Li(detail) for detail in (details or [])])
                    if details
                    else html.Div()
                ),
                (
                    dbc.Alert(
                        [
                            html.I(
                                className=f"fas fa-{'exclamation-triangle' if alert_type == 'warning' else 'info-circle'} me-2"
                            ),
                            alert_message,
                        ],
                        color=alert_type,
                        className="mb-0 mt-3",
                    )
                    if alert_message
                    else html.Div()
                ),
            ]
        ),
    ]

    return dbc.Card(card_content, className="mb-4 shadow-sm")


def create_workflow_section() -> html.Div:
    """
    Create complete workflow section with all steps.

    Returns
    -------
    html.Div
        Workflow section with step-by-step instructions
    """
    return html.Div(
        [
            html.H2(
                [
                    html.I(className="fas fa-route me-2 text-success"),
                    "How to Perform Your Analysis",
                ],
                className="mb-4",
            ),
            # Step 1: Upload Data
            create_workflow_step(
                step_number=1,
                title="Upload Your Data",
                description="Begin by uploading your KO annotation file in the correct format.",
                icon="fas fa-upload",
                details=[
                    "File format: Plain text (.txt)",
                    "Sample names must start with '>' character",
                    "KO numbers listed below each sample (one per line)",
                    "Format: K##### (K followed by 5 digits)",
                    "Maximum: 100 samples or 500,000 KO numbers",
                ],
                alert_message=(
                    "Proper file formatting is CRITICAL for data integrity and application security. "
                    "Invalid formats will be rejected during validation to ensure reliable analysis results."
                ),
                alert_type="warning",
            ),
            # Example format card
            dbc.Card(
                [
                    dbc.CardHeader("Example File Format", className="bg-light"),
                    dbc.CardBody(
                        [
                            html.Pre(
                                ">Sample1\n"
                                "K00031\n"
                                "K00032\n"
                                "K00090\n"
                                ">Sample2\n"
                                "K00031\n"
                                "K00042\n"
                                "K00052",
                                style={
                                    "backgroundColor": "#f8f9fa",
                                    "padding": "1rem",
                                    "borderRadius": "0.25rem",
                                    "border": "1px solid #dee2e6",
                                },
                            )
                        ]
                    ),
                ],
                className="mb-4 shadow-sm",
            ),
            # Step 2: File Validation
            create_workflow_step(
                step_number=2,
                title="File Validation",
                description=(
                    "After uploading, BioRemPP automatically validates your file to ensure data integrity "
                    "and security compliance."
                ),
                icon="fas fa-check-circle",
                details=[
                    "Format validation: Checks file structure and syntax",
                    "Sample detection: Identifies all samples in your file",
                    "KO validation: Verifies KO number format (K#####)",
                    "Size limits: Ensures file is within processing limits",
                    "Security check: Prevents malicious file uploads",
                ],
                alert_message=(
                    "Validation is a security measure that protects the application and ensures "
                    "your analysis results are based on correctly formatted data. "
                    "If validation fails, check the error message for specific issues."
                ),
                alert_type="info",
            ),
            # Validation feedback illustration
            dbc.Card(
                [
                    dbc.CardHeader("Validation Feedback", className="bg-light"),
                    dbc.CardBody(
                        [
                            dbc.Alert(
                                [
                                    html.I(className="fas fa-check-circle me-2"),
                                    html.Strong("Success: "),
                                    "File validated successfully! Found 3 samples with 150 KO annotations.",
                                ],
                                color="success",
                                className="mb-2",
                            ),
                            dbc.Alert(
                                [
                                    html.I(
                                        className="fas fa-exclamation-triangle me-2"
                                    ),
                                    html.Strong("Error: "),
                                    "Invalid KO format detected on line 15. Expected format: K##### (e.g., K00001)",
                                ],
                                color="danger",
                                className="mb-0",
                            ),
                        ]
                    ),
                ],
                className="mb-4 shadow-sm",
            ),
            # Step 3: Process Data
            create_workflow_step(
                step_number=3,
                title="Process Your Data",
                description=(
                    "Once validation succeeds, click the 'Process Data' button to begin analysis."
                ),
                icon="fas fa-cogs",
                details=[
                    "KO extraction: Identifies all unique KO annotations",
                    "KEGG integration: Queries KEGG database for pathway information",
                    "HadegDB matching: Cross-references hydrocarbon degradation data",
                    "toxCSM analysis: Retrieves toxicity predictions for compounds",
                    "Data merging: Combines all databases into unified dataset",
                ],
                alert_message=(
                    "Processing time varies based on file size (typically 30 seconds to 3 minutes). "
                    "Do not close your browser during processing."
                ),
                alert_type="info",
            ),
            # Step 4: Processing Feedback
            dbc.Card(
                [
                    dbc.CardHeader(
                        "Processing Progress Feedback", className="bg-light"
                    ),
                    dbc.CardBody(
                        [
                            html.P(
                                "Real-time feedback keeps you informed during processing:",
                                className="mb-4",
                            ),
                            # Processing spinner illustration
                            html.Div(
                                [
                                    dbc.Spinner(
                                        color="success",
                                        size="lg",
                                        spinner_style={
                                            "width": "3rem",
                                            "height": "3rem",
                                        },
                                    ),
                                    html.Div(
                                        "Processing your data...",
                                        className="mt-3 fw-bold text-success",
                                        style={"fontSize": "1.1rem"},
                                    ),
                                    html.Div(
                                        "Elapsed time: 2.5s",
                                        className="mt-2 text-muted",
                                        style={"fontSize": "0.9rem"},
                                    ),
                                ],
                                className="text-center py-3 mb-4",
                                style={
                                    "backgroundColor": "#f8f9fa",
                                    "borderRadius": "0.5rem",
                                },
                            ),
                            html.Hr(),
                            # Success feedback
                            html.H6(
                                "Success Feedback:", className="text-success mt-3 mb-2"
                            ),
                            dbc.Alert(
                                [
                                    html.I(className="fas fa-check-circle me-2"),
                                    html.Strong("Processing completed successfully! "),
                                    "Your data is ready for analysis.",
                                ],
                                color="success",
                                className="mb-3",
                            ),
                            # Error feedback
                            html.H6(
                                "Error Feedback:", className="text-danger mt-3 mb-2"
                            ),
                            dbc.Alert(
                                [
                                    html.I(className="fas fa-times-circle me-2"),
                                    html.Strong("Processing failed: "),
                                    "Unable to connect to database. Please try again or contact support.",
                                ],
                                color="danger",
                                className="mb-0",
                            ),
                        ]
                    ),
                ],
                className="mb-4 shadow-sm",
            ),
            # Step 5: View Results
            create_workflow_step(
                step_number=5,
                title="View Results & Navigate Modules",
                description=(
                    "After processing completes, click 'View Results' to access your analysis dashboard "
                    "with all 8 modules and 56 use cases."
                ),
                icon="fas fa-chart-bar",
                details=[
                    "Navigation sidebar: Browse all modules and use cases",
                    "Interactive visualizations: Explore data with Plotly charts",
                    "Downloadable tables: Export data in TSV format",
                    "Module filtering: Focus on specific analysis types",
                    "Custom parameters: Adjust visualizations per use case",
                ],
                alert_message=(
                    "Results are session-based and will be deleted when you close your browser. "
                    "Download important data before ending your session!"
                ),
                alert_type="warning",
            ),
        ],
        className="mb-5",
    )


def create_tips_section() -> html.Div:
    """
    Create tips and best practices section.

    Returns
    -------
    html.Div
        Tips section with recommendations
    """
    return html.Div(
        [
            html.H2(
                [
                    html.I(className="fas fa-lightbulb me-2 text-success"),
                    "Tips & Best Practices",
                ],
                className="mb-4",
            ),
            dbc.Row(
                [
                    dbc.Col(
                        [
                            dbc.Card(
                                [
                                    dbc.CardBody(
                                        [
                                            html.H5(
                                                [
                                                    html.I(
                                                        className="fas fa-file-alt me-2 text-primary"
                                                    ),
                                                    "Data Preparation",
                                                ],
                                                className="card-title",
                                            ),
                                            html.Ul(
                                                [
                                                    html.Li(
                                                        "Use KEGG BlastKOALA, KofamKOALA, or eggNOG-mapper for KO annotation"
                                                    ),
                                                    html.Li(
                                                        "Verify KO format before uploading (K#####)"
                                                    ),
                                                    html.Li(
                                                        "Remove duplicate KO numbers within same sample"
                                                    ),
                                                    html.Li(
                                                        "Use descriptive sample names for clarity"
                                                    ),
                                                    html.Li(
                                                        "Check file encoding is UTF-8 for special characters"
                                                    ),
                                                ],
                                                className="small mb-0",
                                            ),
                                        ]
                                    )
                                ],
                                className="h-100 shadow-sm",
                            )
                        ],
                        md=6,
                        className="mb-3",
                    ),
                    dbc.Col(
                        [
                            dbc.Card(
                                [
                                    dbc.CardBody(
                                        [
                                            html.H5(
                                                [
                                                    html.I(
                                                        className="fas fa-question-circle me-2 text-danger"
                                                    ),
                                                    "Troubleshooting",
                                                ],
                                                className="card-title",
                                            ),
                                            html.Ul(
                                                [
                                                    html.Li(
                                                        "Clear browser cache if charts don't display"
                                                    ),
                                                    html.Li(
                                                        "Check FAQ page for common error solutions"
                                                    ),
                                                    html.Li(
                                                        "Verify internet connection during processing"
                                                    ),
                                                    html.Li(
                                                        "Contact support if issues persist"
                                                    ),
                                                    html.Li(
                                                        "Try different browser if problems continue"
                                                    ),
                                                ],
                                                className="small mb-0",
                                            ),
                                        ]
                                    )
                                ],
                                className="h-100 shadow-sm",
                            )
                        ],
                        md=6,
                        className="mb-3",
                    ),
                ]
            ),
        ],
        className="mb-5",
    )


def create_user_guide_page() -> html.Div:
    """
    Create user guide page layout.

    Returns
    -------
    html.Div
        Complete user guide page with all sections

    Examples
    --------
    >>> guide_layout = create_user_guide_page()

    Notes
    -----
    Sections included:
    1. Page header and title
    2. Framework introduction (8 modules overview)
    3. Step-by-step workflow (upload → validation → processing → results)
    4. Tips and best practices
    """
    # Header
    header = create_header(show_nav=True, logo_size="60px")

    # Page title and intro
    page_intro = html.Div(
        [
            html.H1(
                [html.I(className="fas fa-book-open me-3 text-success"), "User Guide"],
                className="text-center mb-3",
            ),
            html.P(
                "Complete guide to performing bioremediation potential analysis with BioRemPP",
                className="text-center text-muted mb-4 lead",
            ),
            html.Hr(),
        ],
        className="mb-5",
    )

    # Quick start alert
    quick_start = dbc.Alert(
        [
            html.H4(
                [html.I(className="fas fa-rocket me-2"), "Quick Start"],
                className="alert-heading mb-3",
            ),
            html.P(
                [
                    "New to BioRemPP? Follow these steps: ",
                    html.Strong("Upload Data"),
                    " → ",
                    html.Strong("Validate"),
                    " → ",
                    html.Strong("Process"),
                    " → ",
                    html.Strong("Analyze Results"),
                ]
            ),
            html.Hr(),
            html.P(
                [
                    "For detailed examples, check our ",
                    html.A("FAQ page", href="/faq", className="danger-link"),
                    " or ",
                    html.A(
                        "Contact Support", href="/help/contact", className="danger-link"
                    ),
                    ".",
                ],
                className="mb-0",
            ),
        ],
        color="success",
        className="mb-5",
    )

    # Footer
    footer = create_footer(version="2.0.0", year=2024)

    # Assemble complete layout
    layout = html.Div(
        [
            header,
            dbc.Container(
                [
                    page_intro,
                    quick_start,
                    create_intro_section(),
                    create_workflow_section(),
                    # Interactive Demo Section (after Step 5)
                    html.Hr(
                        style={
                            "margin": "3rem 0",
                            "borderColor": "#28a745",
                            "borderWidth": "2px",
                        }
                    ),
                    create_interactive_demo_section(),
                    # Tips section at the end
                    html.Hr(style={"margin": "3rem 0", "borderColor": "#dee2e6"}),
                    create_tips_section(),
                ],
                fluid=False,
                className="px-4 py-4",
            ),
            footer,
        ],
        id="user-guide-page",
    )

    return layout


def get_layout() -> html.Div:
    """
    Get user guide page layout (alias for create_user_guide_page).

    Returns
    -------
    html.Div
        User guide page layout

    Notes
    -----
    This function is called by Dash when rendering the user guide page.
    """
    return create_user_guide_page()
