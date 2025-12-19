"""
Module Description Component - BioRemPP v1.0 (Enhanced)
=======================================================

Enhanced composite component for module overview headers with modern UI.

Functions
---------
create_module_description
    Create enhanced module overview header with collapsible sections and visual hierarchy

Notes
-----
- Phase 1 & 2 Implementation: Core restructuring + Visual enhancements
- Collapsible sections (default: open)
- Module-specific color coding
- Responsive design (mobile-first)
- Icons, badges, and improved typography
"""

from typing import Dict, List, Optional

import dash_bootstrap_components as dbc
from dash import html


# Module color configuration - ALL MODULES USE SAME GREEN COLOR
MODULE_COLORS = {
    "1": {"primary": "success", "icon": "fa-database", "name": "Database Assessment"},
    "2": {"primary": "success", "icon": "fa-database", "name": "Exploratory Analysis"},
    "3": {"primary": "success", "icon": "fa-database", "name": "System Structure"},
    "4": {"primary": "success", "icon": "fa-database", "name": "Functional Profiling"},
    "5": {"primary": "success", "icon": "fa-database", "name": "Interaction Modeling"},
    "6": {"primary": "success", "icon": "fa-database", "name": "Hierarchical Analysis"},
    "7": {"primary": "success", "icon": "fa-database", "name": "Toxicological Assessment"},
    "8": {"primary": "success", "icon": "fa-database", "name": "Consortium Assembly"},
}


def create_module_description(
    module_id: str,
    title: str,
    overview_text: str,
    guiding_questions: List[Dict[str, str]],
    section_id: Optional[str] = None,
    num_use_cases: Optional[int] = None,
) -> html.Div:
    """
    Create enhanced module overview header with modern UI.

    Parameters
    ----------
    module_id : str
        Module identifier (e.g., "1", "2", "3")
    title : str
        Module title
    overview_text : str
        Overview description explaining module's purpose
    guiding_questions : List[Dict[str, str]]
        List of guiding questions. Each dict must contain:
        - 'id': Question ID (e.g., "1.1", "1.2")
        - 'subtitle': Question subtitle
        - 'question': Main question text
    section_id : Optional[str], default=None
        Optional ID for the section div
    num_use_cases : Optional[int], default=None
        Number of use cases in this module

    Returns
    -------
    html.Div
        Enhanced module overview header component

    Notes
    -----
    Phase 1 & 2 Features:
    - Collapsible overview (default: open)
    - Accordion questions (default: open)
    - Module-specific icons and colors
    - Badges for metadata
    - Responsive grid layout
    - Hover effects and animations
    """
    # Get module configuration
    module_config = MODULE_COLORS.get(module_id, MODULE_COLORS["1"])
    color = module_config["primary"]
    icon = module_config["icon"]

    # Count use cases from questions if not provided
    if num_use_cases is None:
        num_use_cases = len(guiding_questions)

    # ========================================
    # Module Header Card
    # ========================================
    header_card = dbc.Card(
        [
            dbc.CardHeader(
                [
                    dbc.Row(
                        [
                            dbc.Col(
                                [
                                    html.I(className=f"fas {icon} me-2 text-{color}"),
                                    html.Span(
                                        f"Module {module_id}",
                                        className=f"badge bg-{color} me-2",
                                    ),
                                    html.H4(title, className="d-inline mb-0"),
                                ],
                                width="auto",
                            ),
                            dbc.Col(
                                [
                                    dbc.Badge(
                                        [
                                            html.I(className="fas fa-chart-line me-1"),
                                            f"{num_use_cases} Use Cases",
                                        ],
                                        color="light",
                                        text_color="dark",
                                        className="ms-2",
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
                    # Collapsible Overview Section
                    html.Div(
                        [
                            dbc.Button(
                                [
                                    html.I(
                                        className="fas fa-chevron-down me-2",
                                        id=f"module-{module_id}-overview-icon",
                                    ),
                                    html.Strong("Overview & Context"),
                                ],
                                id=f"module-{module_id}-overview-toggle",
                                color="link",
                                className="text-start w-100 p-0 mb-2 text-decoration-none",
                                style={"border": "none"},
                            ),
                            dbc.Collapse(
                                [
                                    html.Div(
                                        [
                                            html.I(
                                                className=f"fas fa-book-open me-2 text-{color}"
                                            ),
                                            html.Strong("Module Purpose"),
                                        ],
                                        className="mb-2",
                                    ),
                                    html.P(
                                        overview_text,
                                        className="text-muted ms-4",
                                        style={"lineHeight": "1.6"},
                                    ),
                                ],
                                id=f"module-{module_id}-overview-collapse",
                                is_open=True,  # Default: OPEN
                            ),
                        ],
                        className="mb-3",
                    ),
                ]
            ),
        ],
        className=f"mb-4 shadow-sm border-top border-{color} border-3 module-header-card",
        id=f"module-{module_id}-header",
    )

    # ========================================
    # Analytical Questions Card
    # ========================================
    questions_card = dbc.Card(
        [
            dbc.CardHeader(
                [
                    html.I(className="fas fa-lightbulb me-2 text-warning"),
                    html.Strong("Analytical Questions"),
                    html.Small(
                        " — Guiding questions for the upcoming charts",
                        className="text-muted ms-2 d-none d-md-inline",
                    ),
                ],
                className="bg-light",
            ),
            dbc.CardBody(
                [
                    dbc.Accordion(
                        [
                            dbc.AccordionItem(
                                [
                                    html.P(
                                        question_data["question"],
                                        className="mb-0",
                                        style={"lineHeight": "1.6"},
                                    ),
                                ],
                                title=[
                                    html.Span(
                                        question_data["id"],
                                        className=f"badge bg-{color} me-2",
                                    ),
                                    html.Span(
                                        question_data["subtitle"], className="fw-bold"
                                    ),
                                ],
                                item_id=f"question-{question_data['id']}",
                            )
                            for question_data in guiding_questions
                        ],
                        id=f"module-{module_id}-questions-accordion",
                        start_collapsed=False,  # Default: OPEN (all items)
                        flush=True,
                        always_open=True,  # Allow multiple items open
                    )
                ],
                className="p-0",
            ),
        ],
        className="mb-4 shadow-sm",
        id=f"module-{module_id}-questions",
    )

    # ========================================
    # Complete Module Header
    # ========================================
    component = html.Div(
        [header_card, questions_card],
        className="module-overview-header",
        id=section_id,
    )

    return component
