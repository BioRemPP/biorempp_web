"""
Job Resume Panel - Composite UI component.

Provides a simple `job_id` input + action button to restore cached results.
"""

import dash_bootstrap_components as dbc
from dash import html


def create_job_resume_panel() -> dbc.Card:
    """Create resume-by-job-id panel for homepage workflow."""
    return dbc.Card(
        [
            dbc.CardHeader(
                [
                    html.I(className="fas fa-rotate-left me-2"),
                    html.Span("Resume Analysis by Job ID", className="font-weight-bold"),
                ],
                className="bg-light",
            ),
            dbc.CardBody(
                [
                    html.P(
                        "Already processed a file? Enter your Job ID to restore results "
                        "without reprocessing.",
                        className="text-muted mb-3",
                    ),
                    dbc.Row(
                        [
                            dbc.Col(
                                dbc.Input(
                                    id="resume-job-id-input",
                                    type="text",
                                    placeholder="BRP-YYYYMMDD-HHMMSS-XXXXXX",
                                    debounce=True,
                                ),
                                md=8,
                            ),
                            dbc.Col(
                                dbc.Button(
                                    [
                                        html.I(className="fas fa-play-circle me-2"),
                                        "Resume",
                                    ],
                                    id="resume-job-btn",
                                    color="primary",
                                    className="w-100",
                                ),
                                md=4,
                            ),
                        ],
                        className="g-2",
                    ),
                    html.Div(id="resume-job-status", className="mt-3"),
                ]
            ),
        ],
        id="job-resume-panel",
        className="mb-3",
    )

