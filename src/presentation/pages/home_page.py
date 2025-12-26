"""
Home Page Layout - BioRemPP v1.0.

Main landing page with upload workflow.

Functions
---------
create_home_layout
    Create complete homepage layout

Notes
-----
- 5 sections: Header, Intro, Upload Workflow, Help, Footer
- State managed via 4 dcc.Stores
- Clean separation from results page
"""

from typing import Optional

import dash_bootstrap_components as dbc
from dash import dcc, html

from ..components.base import create_footer, create_header, create_help_links
from ..components.composite import (
    create_completion_panel,
    create_intro_card,
    create_progress_panel,
    create_upload_panel,
    create_validation_panel,
)
from ..pages.new_user import (
    create_new_user_guide_button,
    create_new_user_guide_modal,
)
from ..pages.terms_of_use import create_terms_button, create_terms_modal


def create_home_layout(session_id: Optional[str] = None) -> html.Div:
    """
    Create homepage layout.

    Parameters
    ----------
    session_id : Optional[str], optional
        Session ID for tracking user session, by default None

    Returns
    -------
    html.Div
        Complete homepage layout with all sections

    Examples
    --------
    >>> layout = create_home_layout()
    >>> layout = create_home_layout(session_id="abc123")

    Notes
    -----
    Layout Structure:
    - Section 1: Header (logo, title, navigation)
    - Section 2: Intro Card (collapsible system description)
    - Section 3: Upload Workflow (3-step process)
      - Upload Panel (Step 1)
      - Validation Panel (Step 1 results)
      - Progress Panel (Step 2)
      - Completion Panel (Step 3)
    - Section 4: Help & Guidance
    - Section 5: Footer

    State Management (4 dcc.Stores):
    - upload-result: UploadResultDTO
    - processing-progress: ProcessingProgressDTO
    - processing-complete: bool flag
    - merged-result: MergedDataDTO

    Workflow:
    1. User uploads file → upload-result populated
    2. User clicks Process → processing-progress updates
    3. Processing completes → processing-complete = True
    4. User clicks View Results → navigate to /results
    """
    # Section 1: Header
    header = create_header(show_nav=True, logo_size="80px")

    # Section 2: Intro Card
    intro = create_intro_card()

    # Section 3: Upload Workflow (3 steps)
    upload_workflow = dbc.Container(
        [
            html.H1(
                "Start Your Analysis", className="text-center text-success mb-4 mt-4"
            ),
            # New User Guide Card
            dbc.Row(
                [
                    dbc.Col(
                        [create_new_user_guide_button()],
                        md=8,
                        lg=6,
                        className="mx-auto mb-2",
                    )
                ]
            ),
            # Terms of Use Card
            dbc.Row(
                [
                    dbc.Col(
                        [create_terms_button()],
                        md=8,
                        lg=6,
                        className="mx-auto mb-4",
                    )
                ]
            ),
            # Step 1: Upload
            create_upload_panel(),
            # Validation feedback (appears after upload)
            create_validation_panel(),
            # Step 2: Processing (appears after clicking "Process Data")
            create_progress_panel(),
            # Step 3: Completion (appears when processing finishes)
            create_completion_panel(),
        ],
        className="mb-5",
    )

    # Section 4: Help & Guidance
    help_section = dbc.Container([create_help_links()], className="mb-5")

    # Section 5: Footer
    footer = create_footer(version="2.0.0", year=2024)

    # State Management Stores (Legacy stores only)
    stores = html.Div(
        [
            # Upload result (UploadResultDTO) - Legacy
            dcc.Store(id="upload-result-store", storage_type="session"),
            # Processing progress (ProcessingProgressDTO)
            dcc.Store(id="processing-progress-store", storage_type="session"),
            # Processing completion flag
            dcc.Store(
                id="processing-complete-store", storage_type="session", data=False
            ),
            # Session ID
            dcc.Store(id="session-id-store", storage_type="session", data=session_id),
        ]
    )

    # Assemble complete layout (no Location - it's in main app layout)
    layout = html.Div(
        [
            stores,
            header,
            dbc.Container(
                [intro, upload_workflow, help_section], fluid=False, className="px-4"
            ),
            footer,
            create_new_user_guide_modal(),  # Guided tour modal
            create_terms_modal(),  # Terms of use modal
        ]
    )

    return layout


def get_layout(session_id: Optional[str] = None) -> html.Div:
    """
    Get homepage layout (alias for create_home_layout).

    Parameters
    ----------
    session_id : Optional[str], optional
        Session ID for tracking, by default None

    Returns
    -------
    html.Div
        Homepage layout

    Notes
    -----
    This function is called by Dash when rendering the homepage.
    """
    return create_home_layout(session_id=session_id)
