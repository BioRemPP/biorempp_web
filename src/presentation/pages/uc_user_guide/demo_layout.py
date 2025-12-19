"""
User Guide Interactive Demo Layout - BioRemPP v1.0
===================================================

Complete demonstration of a BioRemPP module with real UI components:
- Module description with guiding questions
- Use case panel (collapsible description)
- Interactive controls (database selector, download button)
- Mock bar chart visualization
- Accordion for results

Author: BioRemPP Development Team
Date: 2025-12-05
"""

from pathlib import Path

import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import yaml
from dash import dcc, html

# Load demo configuration
DEMO_CONFIG_PATH = Path(__file__).parent / "demo_config.yaml"


def load_demo_config():
    """Load demo configuration from YAML."""
    with open(DEMO_CONFIG_PATH, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def create_demo_module_description(config: dict) -> html.Div:
    """
    Create module description header with guiding questions.

    Parameters
    ----------
    config : dict
        Configuration dictionary with module metadata

    Returns
    -------
    html.Div
        Module description component
    """
    module = config["module"]
    questions = config["guiding_questions"]

    # Overview Card
    overview_card = dbc.Card(
        [
            dbc.CardBody(
                [
                    html.H4(
                        f"Module {module['id']} — {module['title']}",
                        className="card-title",
                    ),
                    html.P(
                        module["overview"],
                        className="card-text",
                    ),
                ]
            )
        ],
        className="mb-3 shadow-sm",
    )

    # Guiding Questions Card
    question_columns = []
    for q in questions:
        col = dbc.Col(
            dbc.ListGroup(
                [
                    dbc.ListGroupItem(
                        [
                            html.H6(
                                f"{q['id']} {q['subtitle']}",
                                className="mb-1 fw-bold",
                            ),
                            html.P(
                                q["question"],
                                className="small mb-1",
                            ),
                        ]
                    )
                ],
                flush=True,
            ),
            md=4,
        )
        question_columns.append(col)

    questions_card = dbc.Card(
        [
            dbc.CardHeader("Guiding questions for the upcoming charts"),
            dbc.CardBody(
                [
                    dbc.Row(
                        question_columns,
                        className="g-3",
                    )
                ]
            ),
        ],
        className="mb-4 shadow-sm",
    )

    return html.Div([overview_card, questions_card], className="module-overview-header")


def create_demo_use_case_panel(config: dict) -> html.Div:
    """
    Create use case informative panel (collapsible).

    Parameters
    ----------
    config : dict
        Configuration with panel information

    Returns
    -------
    html.Div
        Collapsible panel component
    """
    panel_info = config["panel"]

    # Visual elements section
    visual_items = [
        html.Li([html.Strong(f"{elem['label']}: "), elem["description"]])
        for elem in panel_info["visual_elements"]
    ]

    visual_elements_content = [
        html.H6(
            [html.I(className="fas fa-eye me-2"), "Visual Elements"],
            className="mt-3 mb-2 text-primary",
        ),
        html.Ul(visual_items, className="mb-0"),
    ]

    # Interpretation guidelines
    interpretation_items = [
        html.Li(guideline) for guideline in panel_info["interpretation_guidelines"]
    ]

    interpretation_content = [
        html.H6(
            [html.I(className="fas fa-lightbulb me-2"), "Interpretation"],
            className="mt-3 mb-2 text-warning fw-bold",
        ),
        html.Ul(interpretation_items, className="mb-0"),
    ]

    # Main panel
    panel = html.Div(
        [
            # Collapse Button
            dbc.Button(
                [
                    html.I(className="fas fa-info-circle me-2"),
                    "View Use Case Description",
                ],
                id="demo-guide-collapse-button",
                color="success",
                outline=True,
                className="mb-3 w-100",
                n_clicks=0,
            ),
            # Collapsible Content
            dbc.Collapse(
                dbc.Card(
                    [
                        dbc.CardBody(
                            [
                                # Scientific Question
                                html.Div(
                                    [
                                        html.H6(
                                            [
                                                html.I(
                                                    className="fas fa-question-circle me-2"
                                                ),
                                                "Scientific Question",
                                            ],
                                            className="mb-2 text-success fw-bold",
                                        ),
                                        html.Blockquote(
                                            panel_info["scientific_question"],
                                            className=(
                                                "border-start border-4 border-success "
                                                "ps-3 mb-3 fst-italic"
                                            ),
                                        ),
                                    ]
                                ),
                                # Description
                                html.Div(
                                    [
                                        html.H6(
                                            [
                                                html.I(
                                                    className="fas fa-info-circle me-2"
                                                ),
                                                "Description",
                                            ],
                                            className="mb-2 text-info fw-bold",
                                        ),
                                        html.P(
                                            panel_info["description"],
                                            className="text-muted mb-3",
                                            style={"whiteSpace": "pre-line"},
                                        ),
                                    ]
                                ),
                                # Visual Elements
                                html.Div(visual_elements_content),
                                # Interpretation Guidelines
                                html.Div(interpretation_content),
                            ],
                            className="p-4",
                        )
                    ],
                    className="border-success shadow-sm",
                ),
                id="demo-guide-collapse",
                is_open=False,
            ),
        ],
        id="demo-guide-info-panel",
    )

    return panel


def create_mock_bar_chart(config: dict, selected_db: str = "BioRemPP") -> go.Figure:
    """
    Create mock bar chart for demonstration.

    Parameters
    ----------
    config : dict
        Configuration with mock data
    selected_db : str
        Selected database name for title

    Returns
    -------
    go.Figure
        Plotly bar chart figure
    """
    samples = config["mock_data"]["samples"]

    # Sort samples by KO count (descending)
    sorted_samples = sorted(samples, key=lambda x: x["ko_count"], reverse=True)

    # Extract data
    sample_names = [s["name"] for s in sorted_samples]
    ko_counts = [s["ko_count"] for s in sorted_samples]
    colors = [s["color"] for s in sorted_samples]

    # Create figure
    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            x=ko_counts,
            y=sample_names,
            orientation="h",
            marker=dict(color=colors, line=dict(color="rgba(0,0,0,0.3)", width=1)),
            text=ko_counts,
            textposition="outside",
            textfont=dict(size=12, color="black"),
            hovertemplate=("<b>%{y}</b><br>" "KO Count: %{x}<br>" "<extra></extra>"),
        )
    )

    # Update layout
    fig.update_layout(
        title={
            "text": f"Sample Ranking by KO Richness - {selected_db}",
            "x": 0.5,
            "xanchor": "center",
            "font": {"size": 16, "color": "#2C3E50"},
        },
        xaxis_title="Unique KO Count",
        yaxis_title="Samples",
        template="plotly_white",
        height=400,
        margin=dict(l=100, r=100, t=80, b=60),
        showlegend=False,
        hovermode="closest",
        xaxis=dict(showgrid=True, gridcolor="rgba(0,0,0,0.1)", zeroline=True),
        yaxis=dict(showgrid=False, categoryorder="total ascending"),
    )

    return fig


def create_demo_use_case_layout() -> dbc.Card:
    """
    Create complete demo use case layout matching real UC structure.

    Returns
    -------
    dbc.Card
        Complete use case card with all interactive elements
    """
    # Load configuration
    config = load_demo_config()

    # Create components
    info_panel = create_demo_use_case_panel(config)
    initial_chart = create_mock_bar_chart(config, "BioRemPP")

    # Database options from config
    databases = config["mock_data"]["databases"]

    return dbc.Card(
        [
            # ========================================
            # Card Header (Title + Download Button)
            # ========================================
            dbc.CardHeader(
                [
                    dbc.Row(
                        [
                            dbc.Col(
                                [
                                    html.H5(
                                        [
                                            html.I(className="fas fa-chart-bar me-2"),
                                            "UC-2.1: Ranking of Samples by KO Richness (Demo)",
                                        ],
                                        className="mb-0",
                                    )
                                ],
                                width="auto",
                            ),
                            dbc.Col(
                                [
                                    # Download dropdown (non-interactive for demo)
                                    dbc.DropdownMenu(
                                        [
                                            dbc.DropdownMenuItem(
                                                [
                                                    html.I(
                                                        className="fas fa-file-csv me-2"
                                                    ),
                                                    "CSV (.csv)",
                                                ],
                                                disabled=True,
                                            ),
                                            dbc.DropdownMenuItem(
                                                [
                                                    html.I(
                                                        className="fas fa-file-excel me-2"
                                                    ),
                                                    "Excel (.xlsx)",
                                                ],
                                                disabled=True,
                                            ),
                                            dbc.DropdownMenuItem(
                                                [
                                                    html.I(
                                                        className="fas fa-file-code me-2"
                                                    ),
                                                    "JSON (.json)",
                                                ],
                                                disabled=True,
                                            ),
                                        ],
                                        label=[
                                            html.I(className="fas fa-download me-2"),
                                            "Download Data",
                                        ],
                                        color="success",
                                        size="md",
                                        className="me-2",
                                    ),
                                    # Info badge
                                    dbc.Badge(
                                        "Demo Only", color="info", className="ms-2"
                                    ),
                                ],
                                width="auto",
                                className="ms-auto",
                            ),
                        ],
                        align="center",
                        className="g-0",
                    )
                ]
            ),
            # ========================================
            # Card Body
            # ========================================
            dbc.CardBody(
                [
                    # Informative panel
                    info_panel,
                    # Explanatory note
                    dbc.Alert(
                        [
                            html.I(className="fas fa-info-circle me-2"),
                            html.Strong("This is a demonstration: "),
                            "The components below show how a real use case works. ",
                            "Try selecting different databases and expanding the accordion to see the chart!",
                        ],
                        color="info",
                        className="mb-3",
                    ),
                    # ========================================
                    # Accordion: Interactive Controls
                    # ========================================
                    dbc.Accordion(
                        [
                            dbc.AccordionItem(
                                [
                                    # Database Selection
                                    html.Div(
                                        [
                                            html.Label(
                                                "Select Database:",
                                                className="fw-bold mb-2",
                                            ),
                                            html.Div(
                                                [
                                                    dbc.ButtonGroup(
                                                        [
                                                            dbc.Button(
                                                                db["name"],
                                                                id=f"demo-guide-db-{db['name'].lower()}",
                                                                color="primary",
                                                                outline=(
                                                                    i != 0
                                                                ),  # First button active
                                                                size="sm",
                                                                className="me-1",
                                                            )
                                                            for i, db in enumerate(
                                                                databases
                                                            )
                                                        ],
                                                        className="mb-2",
                                                    ),
                                                    # Database description
                                                    html.Div(
                                                        id="demo-guide-db-description",
                                                        children=dbc.Alert(
                                                            databases[0]["description"],
                                                            color="light",
                                                            className="mt-2 mb-0 small",
                                                        ),
                                                    ),
                                                ]
                                            ),
                                        ],
                                        className="mb-4",
                                    ),
                                    # ========================================
                                    # Chart Container
                                    # ========================================
                                    html.Div(
                                        [
                                            html.Hr(className="my-3"),
                                            html.H6(
                                                [
                                                    html.I(
                                                        className="fas fa-chart-bar me-2"
                                                    ),
                                                    "Visualization",
                                                ],
                                                className="mb-3",
                                            ),
                                            dcc.Graph(
                                                id="demo-guide-chart",
                                                figure=initial_chart,
                                                config={
                                                    "displayModeBar": True,
                                                    "displaylogo": False,
                                                    "modeBarButtonsToRemove": [
                                                        "select2d",
                                                        "lasso2d",
                                                        "autoScale2d",
                                                    ],
                                                },
                                            ),
                                        ]
                                    ),
                                ],
                                title="View Results",
                                item_id="demo-guide-item",
                            )
                        ],
                        id="demo-guide-accordion",
                        start_collapsed=False,
                    ),  # Open by default
                ],
                className="p-4",
            ),
        ],
        className="shadow-sm mb-4",
        id="demo-guide-card",
    )


def create_interactive_demo_section() -> html.Div:
    """
    Create complete interactive demo section for user guide.

    This section demonstrates the full structure of a BioRemPP module:
    1. Module description with guiding questions
    2. Use case with interactive components

    Returns
    -------
    html.Div
        Complete demo section
    """
    config = load_demo_config()

    # Section header
    section_header = html.Div(
        [
            html.H2(
                [
                    html.I(className="fas fa-laptop-code me-2 text-success"),
                    "Interactive Module Demo",
                ],
                className="mb-3",
            ),
            html.P(
                "Below is a live demonstration of how a BioRemPP module looks and works. "
                "This shows the actual UI components you'll interact with when analyzing your data.",
                className="lead text-muted mb-4",
            ),
        ]
    )

    # Create module components
    module_description = create_demo_module_description(config)
    use_case_layout = create_demo_use_case_layout()

    # Component explanation cards
    explanation_cards = dbc.Row(
        [
            dbc.Col(
                [
                    dbc.Card(
                        [
                            dbc.CardBody(
                                [
                                    html.H6(
                                        [
                                            html.I(
                                                className="fas fa-list-ul me-2 text-primary"
                                            ),
                                            "1. Module Header",
                                        ],
                                        className="card-title",
                                    ),
                                    html.P(
                                        "Shows the module title, overview, and guiding questions "
                                        "to help you understand what analyses are available.",
                                        className="small mb-0",
                                    ),
                                ]
                            )
                        ],
                        className="h-100 border-primary",
                    )
                ],
                md=4,
                className="mb-3",
            ),
            dbc.Col(
                [
                    dbc.Card(
                        [
                            dbc.CardBody(
                                [
                                    html.H6(
                                        [
                                            html.I(
                                                className="fas fa-info-circle me-2 text-success"
                                            ),
                                            "2. Use Case Description",
                                        ],
                                        className="card-title",
                                    ),
                                    html.P(
                                        "Collapsible panel with scientific context, visual elements guide, "
                                        "and interpretation guidelines for each analysis.",
                                        className="small mb-0",
                                    ),
                                ]
                            )
                        ],
                        className="h-100 border-success",
                    )
                ],
                md=4,
                className="mb-3",
            ),
            dbc.Col(
                [
                    dbc.Card(
                        [
                            dbc.CardBody(
                                [
                                    html.H6(
                                        [
                                            html.I(
                                                className="fas fa-sliders-h me-2 text-warning"
                                            ),
                                            "3. Interactive Controls",
                                        ],
                                        className="card-title",
                                    ),
                                    html.P(
                                        "Database selectors, filters, and download options. "
                                        "The accordion shows/hides the visualization on demand.",
                                        className="small mb-0",
                                    ),
                                ]
                            )
                        ],
                        className="h-100 border-warning",
                    )
                ],
                md=4,
                className="mb-3",
            ),
        ],
        className="mb-4",
    )

    return html.Div(
        [
            section_header,
            explanation_cards,
            html.Hr(className="my-4"),
            module_description,
            html.Hr(style={"margin": "2rem 0", "borderColor": "#dee2e6"}),
            use_case_layout,
        ],
        className="mb-5",
        id="interactive-demo-section",
    )
