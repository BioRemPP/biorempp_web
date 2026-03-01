"""
Job Resume Panel - Composite UI component.

Provides a simple `job_id` input + action button to restore cached results.
"""

import dash_bootstrap_components as dbc
from dash import html

from config.settings import get_settings


def _format_resume_ttl(ttl_seconds: int) -> str:
    """Convert TTL seconds into a short, user-facing duration string."""
    ttl = max(int(ttl_seconds), 60)
    if ttl % 3600 == 0:
        hours = ttl // 3600
        return f"{hours} hour{'s' if hours != 1 else ''}"
    if ttl % 60 == 0:
        minutes = ttl // 60
        return f"{minutes} minute{'s' if minutes != 1 else ''}"
    return f"{ttl} seconds"


def create_job_resume_panel() -> dbc.Card:
    """Create resume-by-job-id panel for homepage workflow."""
    ttl_label = _format_resume_ttl(get_settings().RESUME_TTL_SECONDS)

    return dbc.Card(
        [
            dbc.CardHeader(
                [
                    html.I(className="fas fa-rotate-left me-2"),
                    html.Span(
                        "Resume Analysis by Job ID",
                        className="font-weight-bold",
                    ),
                ],
                className="bg-success text-white",
            ),
            dbc.CardBody(
                [
                    html.P(
                        "Already processed a file? Enter your Job ID to restore results "
                        "without reprocessing.",
                        className="text-muted mb-2",
                    ),
                    html.P(
                        [
                            "Resume works only in the same browser profile and remains "
                            f"available for up to {ttl_label} after processing.",
                        ],
                        className="text-muted mb-3",
                        style={"fontSize": "0.9rem"},
                    ),
                    dbc.Row(
                        [
                            dbc.Col(
                                dbc.Input(
                                    id="resume-job-id-input",
                                    type="text",
                                    placeholder="BRP-YYYYMMDD-HHMMSS-XXXXXX",
                                    debounce=True,
                                    maxLength=26,
                                    pattern=r"BRP-\d{8}-\d{6}-[A-F0-9]{6}",
                                    autoComplete="off",
                                    inputMode="text",
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
                    html.P(
                        [
                            "This identifier lets you return to analysis without reprocessing.",
                            html.Br(),
                            "In the results page, you can copy it for later use.",
                        ],
                        className="text-muted mt-2 mb-0",
                        style={"fontSize": "0.85rem"},
                    ),
                    html.Div(id="resume-job-status", className="mt-3"),
                ]
            ),
        ],
        id="job-resume-panel",
        className="mb-3",
    )
