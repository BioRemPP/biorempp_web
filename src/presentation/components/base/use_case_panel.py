"""
Use Case Panel Component - Informative Description Panel.

Creates atomic informative panels for use cases with scientific context,
interpretation guidelines, and visual element descriptions.

Functions
---------
create_use_case_panel
    Create informative collapsible panel for a specific use case
load_use_case_config
    Load use case configuration from YAML file

Notes
-----
- Uses Dash Bootstrap Components for consistent styling
- Fully atomic and reusable component
- Configuration loaded from YAML files
- Collapsible panel for better UX and space management

Individual Use Case Panels
--------------------------
Individual panel creation functions have been moved to:
presentation/components/composite/use_cases/

Import pattern:
>>> from src.presentation.components.composite.use_cases import create_uc_2_1_panel

Author: BioRemPP Development Team
Date: 2025-11-17
"""

from pathlib import Path
from typing import Any, Dict, List, Optional

import dash_bootstrap_components as dbc
import yaml
from dash import html


def load_use_case_config(config_path: str) -> Dict[str, Any]:
    """
    Load use case configuration from YAML file.

    Parameters
    ----------
    config_path : str
        Path to YAML configuration file

    Returns
    -------
    Dict[str, Any]
        Use case configuration dictionary

    Examples
    --------
    >>> config = load_use_case_config('configs/uc_2_1.yaml')
    >>> panel = create_use_case_panel(**config)
    """
    config_file = Path(config_path)
    if not config_file.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")

    with open(config_file, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    return config


def create_use_case_panel(
    use_case_id: str,
    scientific_question: str,
    description: str,
    visual_elements: Optional[List[Dict[str, str]]] = None,
    interpretation_guidelines: Optional[List[str]] = None,
    color_scheme: str = "info",
) -> html.Div:
    """
    Create collapsible informative panel for use case description.

    Parameters
    ----------
    use_case_id : str
        Unique identifier for the use case (e.g., 'uc-2-1')
    scientific_question : str
        The main scientific question being addressed
    description : str
        Detailed description (plain text, supports line breaks)
    visual_elements : Optional[List[Dict[str, str]]], optional
        List of visual element descriptions
        Example: [{'label': 'Y-axis', 'description': 'Samples'}]
    interpretation_guidelines : Optional[List[str]], optional
        List of interpretation guidelines (plain text)
    color_scheme : str, optional
        Bootstrap color (info, primary, success, warning),
        by default "info"

    Returns
    -------
    html.Div
        Collapsible informative panel with button

    Examples
    --------
    >>> panel = create_use_case_panel(
    ...     use_case_id='uc-2-1',
    ...     scientific_question='How does ranking change?',
    ...     description='Compare functional richness.',
    ...     visual_elements=[
    ...         {'label': 'Y-axis', 'description': 'Samples'},
    ...         {'label': 'X-axis', 'description': 'KO counts'}
    ...     ],
    ...     interpretation_guidelines=[
    ...         'Ranking: Observe changes',
    ...         'Generalists: High ranks'
    ...     ]
    ... )

    Notes
    -----
    - Collapsible with button for better UX
    - Plain text rendering (no markdown processing)
    - Color-coded borders for visual hierarchy
    - Can be configured via YAML using load_use_case_config()
    """
    # Visual elements section
    visual_elements_content = []
    if visual_elements:
        visual_items = [
            html.Li([html.Strong(f"{elem['label']}: "), elem["description"]])
            for elem in visual_elements
        ]
        visual_elements_content = [
            html.H6(
                [html.I(className="fas fa-eye me-2"), "Visual Elements"],
                className="mt-3 mb-2 text-primary",
            ),
            html.Ul(visual_items, className="mb-0"),
        ]

    # Interpretation guidelines section
    interpretation_content = []
    if interpretation_guidelines:
        interpretation_items = [
            html.Li(guideline) for guideline in interpretation_guidelines
        ]
        interpretation_content = [
            html.H6(
                [html.I(className="fas fa-lightbulb me-2"), "Interpretation"],
                className="mt-3 mb-2 text-warning fw-bold",
            ),
            html.Ul(interpretation_items, className="mb-0"),
        ]

    # Main panel with collapse button
    collapse_id = f"{use_case_id}-collapse"
    button_id = f"{use_case_id}-collapse-button"

    panel = html.Div(
        [
            # Collapse Button
            dbc.Button(
                [
                    html.I(className="fas fa-info-circle me-2"),
                    "View Use Case Description",
                ],
                id=button_id,
                color=color_scheme,
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
                                # Scientific Question Header
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
                                            scientific_question,
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
                                            description,
                                            className="text-muted mb-3",
                                            style={"whiteSpace": "pre-line"},
                                        ),
                                    ]
                                ),
                                # Visual Elements
                                (
                                    html.Div(visual_elements_content)
                                    if visual_elements
                                    else html.Div()
                                ),
                                # Interpretation Guidelines
                                (
                                    html.Div(interpretation_content)
                                    if interpretation_guidelines
                                    else html.Div()
                                ),
                            ],
                            className="p-4",
                        )
                    ],
                    className=f"border-{color_scheme} shadow-sm",
                ),
                id=collapse_id,
                is_open=False,
            ),
        ],
        id=f"{use_case_id}-info-panel",
    )

    return panel
