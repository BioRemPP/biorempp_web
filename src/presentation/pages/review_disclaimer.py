"""
Reviewer Disclaimer Modal Component.

Provides important performance disclaimer for reviewers during initial submission period.

This is a temporary feature for the initial submission review period.
All components and callbacks are self-contained in this module for easy removal later.
"""

import dash_bootstrap_components as dbc
from dash import Input, Output, State, html


def create_reviewer_disclaimer_button():
    """
    Create reviewer disclaimer button with info styling.

    Returns
    -------
    dbc.Card
        Card containing button to open reviewer disclaimer modal
    """
    return dbc.Card(
        [
            dbc.CardBody(
                [
                    html.Div(
                        [
                            dbc.Button(
                                [
                                    html.I(className="fas fa-info-circle me-2"),
                                    "Disclaimer for Reviewers - Please Read Before Proceeding",
                                    html.I(className="fas fa-info-circle ms-2"),
                                ],
                                id="reviewer-disclaimer-btn",
                                color="info",
                                size="lg",
                                className="shadow-sm",
                            )
                        ],
                        className="d-grid",
                    ),
                ]
            )
        ],
        className="shadow-sm mb-4",
    )


def create_reviewer_disclaimer_modal():
    """
    Create reviewer disclaimer modal with performance notice.

    Returns
    -------
    dbc.Modal
        Modal containing disclaimer about current deployment limitations
    """
    return dbc.Modal(
        [
            dbc.ModalHeader(
                [
                    html.I(className="fas fa-server me-2"),
                    "Important Notice for Reviewers - Temporary Infrastructure Limitations",
                ],
                close_button=True,
            ),
            dbc.ModalBody(
                [
                    # Introduction Alert
                    dbc.Alert(
                        [
                            html.I(className="fas fa-exclamation-triangle me-2"),
                            html.Strong("Performance Advisory: "),
                            "Please read this important information about the current deployment status of BioRemPP.",
                        ],
                        color="warning",
                        className="mb-4",
                    ),

                    # Main Content
                    html.Div(
                        [
                            html.P(
                                "Dear Reviewers,",
                                className="mb-3 text-dark",
                                style={"fontSize": "1.05rem"},
                            ),

                            html.P(
                                [
                                    "We want to be transparent about the current infrastructure situation for this initial submission. "
                                    "Due to the submission deadline coinciding with the holiday season (Christmas and New Year), "
                                    "the IT department staff at ",
                                    html.Strong("Universidade Federal do Rio Grande do Norte (UFRN)"),
                                    " are on vacation and unavailable to perform the deployment on the university's production server infrastructure.",
                                ],
                                className="text-dark mb-3",
                            ),

                            html.H6(
                                [
                                    html.I(className="fas fa-cloud me-2"),
                                    "Current Deployment Status",
                                ],
                                className="mb-3 text-primary",
                            ),

                            html.P(
                                [
                                    "To ensure the application remains accessible for review during this period, BioRemPP is temporarily hosted on a ",
                                    html.Strong("DigitalOcean droplet"),
                                    " with costs being ",
                                    html.Strong("personally covered"),
                                    " by the development team. However, this VM has ",
                                    html.Strong("significantly limited computational resources"),
                                    " compared to the production environment where the application has been tested.",
                                ],
                                className="text-dark mb-3",
                            ),

                            dbc.Alert(
                                [
                                    html.I(className="fas fa-server me-2"),
                                    html.Strong("Current VM Resources: "),
                                    html.Br(),
                                    html.Br(),
                                    "• ",
                                    html.Strong("1 vCPU"),
                                    " (DigitalOcean Basic Droplet)",
                                    html.Br(),
                                    "• ",
                                    html.Strong("2 GB RAM"),
                                    html.Br(),
                                    "• ",
                                    html.Strong("25 GB Disk"),
                                    html.Br(),
                                    "• Location: NYC3 - Ubuntu 24.04 (LTS) x64",
                                    html.Br(),
                                    html.Br(),
                                    html.Strong("Recommended Production Resources:"),
                                    html.Br(),
                                    "• ",
                                    html.Strong("6.0 CPUs / 8 GB RAM"),
                                    html.Br(),
                                    html.Br(),
                                    html.Em("The current configuration is running below 25% CPU capacity and below 25% RAM capacity of the recommended production specifications."),
                                ],
                                color="danger",
                                className="mb-3",
                            ),

                            html.H6(
                                [
                                    html.I(className="fas fa-exclamation-circle me-2"),
                                    "Expected Performance Issues",
                                ],
                                className="mb-3 text-warning",
                            ),

                            html.P(
                                "Due to these infrastructure limitations, you may experience the following performance degradations:",
                                className="mb-2 text-dark",
                            ),

                            html.Ul(
                                [
                                    html.Li([
                                        html.Strong("Extended upload times: "),
                                        "Processing the example dataset or user-provided data files may take longer than expected.",
                                    ]),
                                    html.Li([
                                        html.Strong("Slow table rendering: "),
                                        "Large result tables may take additional time to render and display.",
                                    ]),
                                    html.Li([
                                        html.Strong("Graph generation delays: "),
                                        "Complex plots and visualizations may experience increased rendering times.",
                                    ]),
                                    html.Li([
                                        html.Strong("General responsiveness: "),
                                        "Overall application responsiveness may be slower than in the properly resourced environment.",
                                    ]),
                                ],
                                className="text-dark mb-3",
                            ),

                            html.H6(
                                [
                                    html.I(className="fas fa-shield-alt me-2"),
                                    "Application Reliability Assurance",
                                ],
                                className="mb-3 text-success",
                            ),

                            dbc.Alert(
                                [
                                    html.I(className="fas fa-check-circle me-2"),
                                    html.Strong("Important: "),
                                    "These performance issues are ",
                                    html.Strong("purely infrastructure-related"),
                                    " and do not reflect the application's actual capabilities or reliability. "
                                    "BioRemPP has been extensively tested and validated across multiple environments: ",
                                    html.Strong("development, staging, and full production infrastructure"),
                                    ", where it performs as designed with optimal response times and throughput.",
                                ],
                                color="success",
                                className="mb-3",
                            ),

                            html.H6(
                                [
                                    html.I(className="fas fa-video me-2"),
                                    "Reference Video Demonstration",
                                ],
                                className="mb-3 text-info",
                            ),

                            html.P(
                                [
                                    "To demonstrate BioRemPP's performance in a properly resourced local environment, "
                                    "we have prepared a comprehensive video walkthrough showing the application running "
                                    "with optimal specifications. This video showcases the expected user experience, "
                                    "response times, and functionality as it will operate once deployed on UFRN's production infrastructure.",
                                ],
                                className="text-dark mb-3",
                            ),

                            dbc.Alert(
                                [
                                    html.I(className="fas fa-play-circle me-2"),
                                    html.Strong("Video Demonstration: "),
                                    html.Br(),
                                    html.A(
                                        "Click here to view BioRemPP running in optimal local environment",
                                        href="https://placeholder-video-url.com",  # PLACEHOLDER for actual video URL
                                        target="_blank",
                                        className="fw-bold",
                                        style={"color": "#0d6efd", "textDecoration": "underline"},
                                    ),
                                    html.Br(),
                                    html.Small(
                                        "We recommend watching this video if you experience performance issues during your review.",
                                        className="text-dark",
                                    ),
                                ],
                                color="info",
                                className="mb-3",
                            ),

                            html.H6(
                                [
                                    html.I(className="fas fa-docker me-2"),
                                    "Local Deployment Option",
                                ],
                                className="mb-3 text-secondary",
                            ),

                            html.P(
                                [
                                    "If you prefer to evaluate BioRemPP with optimal performance on your own infrastructure, "
                                    "we provide full Docker Compose support for easy local deployment in development mode. "
                                    "This allows you to run the application with adequate resources and experience the intended performance.",
                                ],
                                className="text-dark mb-3",
                            ),

                            dbc.Card(
                                [
                                    dbc.CardBody(
                                        [
                                            html.H6(
                                                [
                                                    html.I(className="fas fa-terminal me-2"),
                                                    "Quick Local Deployment Instructions",
                                                ],
                                                className="mb-3",
                                            ),
                                            html.P(
                                                "Follow these steps to run BioRemPP locally using Docker Compose:",
                                                className="mb-2",
                                            ),
                                            html.Pre(
                                                html.Code(
                                                    """# 1. Clone the repository
git clone https://github.com/biorempp/biorempp_web.git
cd biorempp_web

# 2. Run in development mode
docker compose --env-file .env/env.development --profile dev up

# 3. Access the application
# Open your browser at: http://localhost:8050""",
                                                    className="language-bash",
                                                ),
                                                className="bg-dark text-light p-3 rounded",
                                                style={"fontSize": "0.9rem"},
                                            ),
                                            dbc.Alert(
                                                [
                                                    html.I(className="fas fa-info-circle me-2"),
                                                    html.Strong("Note: "),
                                                    "Ensure Docker and Docker Compose are installed on your system. "
                                                    "The development mode includes hot-reload capabilities and detailed logging.",
                                                ],
                                                color="light",
                                                className="mb-0 mt-3",
                                            ),
                                        ]
                                    )
                                ],
                                className="mb-3 border-secondary",
                            ),

                            html.H6(
                                [
                                    html.I(className="fas fa-calendar-check me-2"),
                                    "Resolution Timeline",
                                ],
                                className="mb-3 text-primary",
                            ),

                            html.P(
                                [
                                    "This infrastructure limitation is ",
                                    html.Strong("temporary and will be resolved"),
                                    " as soon as the UFRN IT department staff return from their holiday vacation. "
                                    "At that time, BioRemPP will be deployed on the university's production infrastructure "
                                    "with full computational resources, delivering the optimal performance demonstrated in our "
                                    "development, staging, and production testing environments.",
                                ],
                                className="text-dark mb-3",
                            ),

                            html.Hr(),

                            html.P(
                                [
                                    "We sincerely appreciate your understanding regarding this temporary situation. "
                                    "We are committed to transparency and wanted to ensure you are aware of the current "
                                    "deployment context. Should you have any questions or concerns, please do not hesitate "
                                    "to contact us at ",
                                    html.A(
                                        "biorempp@gmail.com",
                                        href="mailto:biorempp@gmail.com",
                                        className="fw-bold",
                                    ),
                                    ".",
                                ],
                                className="text-dark mb-3",
                            ),

                            html.P(
                                [
                                    "Best regards,",
                                    html.Br(),
                                    html.Strong("The BioRemPP Development Team"),
                                ],
                                className="mb-0 text-dark",
                                style={"fontSize": "1.05rem"},
                            ),
                        ]
                    ),
                ],
                style={"maxHeight": "70vh", "overflowY": "auto"},
            ),
            dbc.ModalFooter(
                [
                    dbc.Button(
                        "I Understand",
                        id="reviewer-disclaimer-close",
                        color="primary",
                        className="px-4",
                    )
                ]
            ),
        ],
        id="reviewer-disclaimer-modal",
        size="xl",
        centered=True,
        scrollable=True,
        is_open=False,
    )


def register_reviewer_disclaimer_callbacks(app):
    """
    Register callbacks for reviewer disclaimer modal.

    This function should be called once during app initialization.
    All callbacks are self-contained within this module for easy removal.

    Parameters
    ----------
    app : Dash
        Dash application instance

    Notes
    -----
    This is a temporary feature. To remove it completely:
    1. Delete this file (review_disclaimer.py)
    2. Remove import and function calls from home_page.py
    3. Remove this callback registration from app initialization
    """

    @app.callback(
        Output("reviewer-disclaimer-modal", "is_open"),
        [
            Input("reviewer-disclaimer-btn", "n_clicks"),
            Input("reviewer-disclaimer-close", "n_clicks"),
        ],
        [State("reviewer-disclaimer-modal", "is_open")],
        prevent_initial_call=True,
    )
    def toggle_reviewer_disclaimer_modal(open_clicks, close_clicks, is_open):
        """
        Toggle reviewer disclaimer modal open/close.

        Parameters
        ----------
        open_clicks : int
            Number of clicks on open button
        close_clicks : int
            Number of clicks on close button
        is_open : bool
            Current modal state

        Returns
        -------
        bool
            New modal state (toggled)
        """
        return not is_open
