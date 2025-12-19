"""
Scientific Methods Overview Layout - BioRemPP v1.0.

Creates comprehensive scientific methods overview page with 4 main sections:
1. Scientific Foundations (KO richness, Compound richness, Functional guilds)
2. Data Science & Feature Engineering
3. FAIR Principles & Databases
4. Multi-omics Integration

Functions
---------
create_scientific_overview_layout
    Create complete overview page layout
_create_hero_section
    Hero section with page introduction
_create_scientific_section
    Section 1: Core scientific metrics
_create_datascience_section
    Section 2: Data science methods and visualization
_create_fair_section
    Section 3: FAIR principles and integrated databases
_create_multiomics_section
    Section 4: Multi-omics integration strategies
_create_cta_section
    Call-to-action to detailed workflow methods

Notes
-----
- Uses Dash Bootstrap Components for responsive layout
- Font Awesome icons for visual hierarchy
- English content throughout
- Follows SOLID and DRY principles
"""

from typing import Dict

import dash_bootstrap_components as dbc
from dash import html

from .overview_service import get_all_overview_data


def create_scientific_overview_layout() -> html.Div:
    """
    Create complete scientific methods overview page layout.

    Returns
    -------
    html.Div
        Complete page layout with header, 4 sections, CTA, and footer.

    Examples
    --------
    >>> layout = create_scientific_overview_layout()
    >>> # Use in Dash app routing

    Notes
    -----
    - Loads all YAML data via overview_service
    - Creates 4 main content sections
    - Includes hero section and call-to-action
    - Responsive design with Bootstrap grid
    """
    # Load all data
    data = get_all_overview_data()

    # Import header and footer
    from ...components.base import create_footer, create_header

    # Build layout
    layout = html.Div(
        [
            create_header(show_nav=True, logo_size="60px"),
            _create_hero_section(),
            _create_scientific_section(data.get("scientific", {})),
            _create_datascience_section(data.get("datascience", {})),
            _create_fair_section(data.get("bioremediation", {})),
            _create_multiomics_section(data.get("multiomics", {})),
            _create_cta_section(),
            create_footer(version="1.0.0", year=2024),
            # Reference Modals
            _create_reference_modals(data.get("scientific", {})),
        ]
    )

    return layout


def _create_hero_section() -> dbc.Container:
    """
    Create hero section with page introduction.

    Returns
    -------
    dbc.Container
        Hero section container with title and description.

    Notes
    -----
    - Large heading with icon
    - Descriptive subtitle
    - Light background for visual separation
    """
    return dbc.Container(
        [
            html.Div(
                [
                    html.H1(
                        [
                            html.I(className="fas fa-microscope me-3"),
                            "Scientific Foundations of BioRemPP",
                        ],
                        className="display-4 mb-3 text-success",
                        style={"fontWeight": "600"},
                    ),
                    html.P(
                        "Understanding the methodological rigor and scientific principles "
                        "behind our bioremediation potential analyses",
                        className="lead text-muted mb-4",
                    ),
                    html.Hr(),
                ],
                className="text-center py-5",
            )
        ],
        fluid=True,
        className="bg-light",
    )


def _create_scientific_section(data: Dict) -> dbc.Container:
    """
    Create Section 1: Core Scientific Metrics.

    Parameters
    ----------
    data : Dict
        Scientific foundations data from scientific.yaml

    Returns
    -------
    dbc.Container
        Section with KO richness, compound richness, and functional guilds.

    Notes
    -----
    - Three-column layout for metrics
    - Each metric has definition, application, and References
    - Collapsible reference lists
    """
    if "error" in data:
        return dbc.Container(
            [dbc.Alert(data["error"], color="warning")], className="my-5"
        )

    terms = data.get("terms", {})

    return dbc.Container(
        [
            html.H2(
                [html.I(className="fas fa-flask me-3"), "Core Scientific Metrics"],
                className="mb-4 mt-5 text-primary",
            ),
            html.P(
                "Foundational metrics used throughout BioRemPP to quantify functional "
                "diversity and bioremediation potential",
                className="lead mb-4",
            ),
            dbc.Row(
                [
                    # KO Richness
                    dbc.Col(
                        [
                            dbc.Card(
                                [
                                    dbc.CardHeader(
                                        [
                                            html.I(
                                                className=f"fas {terms.get('ko_richness', {}).get('icon', 'fa-dna')} me-2"
                                            ),
                                            html.Strong(
                                                terms.get("ko_richness", {}).get(
                                                    "label", "KO Richness"
                                                )
                                            ),
                                        ],
                                        className="bg-primary text-white",
                                    ),
                                    dbc.CardBody(
                                        [
                                            html.H6(
                                                "Definition",
                                                className="text-muted mb-2",
                                            ),
                                            html.P(
                                                terms.get("ko_richness", {}).get(
                                                    "definition", ""
                                                ),
                                                className="small",
                                            ),
                                            html.H6(
                                                "BioRemPP Application",
                                                className="text-muted mb-2 mt-3",
                                            ),
                                            html.P(
                                                terms.get("ko_richness", {}).get(
                                                    "biorempp_application", ""
                                                ),
                                                className="small",
                                            ),
                                            html.Div(
                                                [
                                                    dbc.Button(
                                                        [
                                                            html.I(
                                                                className="fas fa-lightbulb me-2"
                                                            ),
                                                            "Use Cases and References",
                                                        ],
                                                        id="ko-refs-modal-open",
                                                        color="primary",
                                                        size="sm",
                                                        outline=True,
                                                        className="mt-3 w-100",
                                                    )
                                                ],
                                                className="text-center",
                                            ),
                                        ]
                                    ),
                                ],
                                className="h-100 shadow-sm",
                            )
                        ],
                        md=4,
                        className="mb-4",
                    ),
                    # Compound Richness
                    dbc.Col(
                        [
                            dbc.Card(
                                [
                                    dbc.CardHeader(
                                        [
                                            html.I(
                                                className=f"fas {terms.get('compound_richness', {}).get('icon', 'fa-vial')} me-2"
                                            ),
                                            html.Strong(
                                                terms.get("compound_richness", {}).get(
                                                    "label", "Compound Richness"
                                                )
                                            ),
                                        ],
                                        className="bg-success text-white",
                                    ),
                                    dbc.CardBody(
                                        [
                                            html.H6(
                                                "Definition",
                                                className="text-muted mb-2",
                                            ),
                                            html.P(
                                                terms.get("compound_richness", {}).get(
                                                    "definition", ""
                                                ),
                                                className="small",
                                            ),
                                            html.H6(
                                                "BioRemPP Application",
                                                className="text-muted mb-2 mt-3",
                                            ),
                                            html.P(
                                                terms.get("compound_richness", {}).get(
                                                    "biorempp_application", ""
                                                ),
                                                className="small",
                                            ),
                                            html.Div(
                                                [
                                                    dbc.Button(
                                                        [
                                                            html.I(
                                                                className="fas fa-lightbulb me-2"
                                                            ),
                                                            "Use Cases and References",
                                                        ],
                                                        id="compound-refs-modal-open",
                                                        color="success",
                                                        size="sm",
                                                        outline=True,
                                                        className="mt-3 w-100",
                                                    )
                                                ],
                                                className="text-center",
                                            ),
                                        ]
                                    ),
                                ],
                                className="h-100 shadow-sm",
                            )
                        ],
                        md=4,
                        className="mb-4",
                    ),
                    # Functional Guilds
                    dbc.Col(
                        [
                            dbc.Card(
                                [
                                    dbc.CardHeader(
                                        [
                                            html.I(
                                                className=f"fas {terms.get('metabolic_functional_guilds', {}).get('icon', 'fa-project-diagram')} me-2"
                                            ),
                                            html.Strong(
                                                terms.get(
                                                    "metabolic_functional_guilds", {}
                                                ).get("label", "Functional Guilds")
                                            ),
                                        ],
                                        className="bg-info text-white",
                                    ),
                                    dbc.CardBody(
                                        [
                                            html.H6(
                                                "Definition",
                                                className="text-muted mb-2",
                                            ),
                                            html.P(
                                                terms.get(
                                                    "metabolic_functional_guilds", {}
                                                ).get("definition", ""),
                                                className="small",
                                            ),
                                            html.H6(
                                                "BioRemPP Application",
                                                className="text-muted mb-2 mt-3",
                                            ),
                                            html.P(
                                                terms.get(
                                                    "metabolic_functional_guilds", {}
                                                ).get("biorempp_application", ""),
                                                className="small",
                                            ),
                                            html.Div(
                                                [
                                                    dbc.Button(
                                                        [
                                                            html.I(
                                                                className="fas fa-lightbulb me-2"
                                                            ),
                                                            "Use Cases and References",
                                                        ],
                                                        id="guilds-refs-modal-open",
                                                        color="info",
                                                        size="sm",
                                                        outline=True,
                                                        className="mt-3 w-100",
                                                    )
                                                ],
                                                className="text-center",
                                            ),
                                        ]
                                    ),
                                ],
                                className="h-100 shadow-sm",
                            )
                        ],
                        md=4,
                        className="mb-4",
                    ),
                ]
            ),
        ],
        className="my-5",
    )


def _create_reference_list(references: list) -> html.Div:
    """
    Create formatted reference list.

    Parameters
    ----------
    references : list
        List of reference dictionaries with authors, year, title, etc.

    Returns
    -------
    html.Div
        Formatted reference list with links.
    """
    if not references:
        return html.Div("No references available", className="text-muted small")

    ref_items = []
    for ref in references:
        ref_items.append(
            html.Li(
                [
                    html.Strong(
                        f"{ref.get('authors', 'Unknown')} ({ref.get('year', 'N/A')}). "
                    ),
                    html.Em(ref.get("title", "No title")),
                    ". ",
                    ref.get("journal", ""),
                    ". " if ref.get("journal") else "",
                    (
                        html.A(
                            [html.I(className="fas fa-external-link-alt ms-2")],
                            href=ref.get("url", "#"),
                            target="_blank",
                            className="small",
                        )
                        if ref.get("url")
                        else ""
                    ),
                ],
                className="small mb-2",
            )
        )

    return html.Div(
        [
            html.Hr(),
            html.H6("References", className="text-muted mb-2"),
            html.Ul(ref_items, className="small"),
        ]
    )


def _create_reference_modals(data: Dict) -> html.Div:
    """
    Create reference modals for scientific metrics.

    Parameters
    ----------
    data : Dict
        Scientific data with terms and references

    Returns
    -------
    html.Div
        Container with all reference modals
    """
    if "error" in data:
        return html.Div()

    terms = data.get("terms", {})

    # Helper function to create modal content
    def create_modal_content(use_cases, references):
        content = []

        # Use Cases Section
        if use_cases:
            content.append(
                html.Div(
                    [
                        html.H5(
                            [
                                html.I(className="fas fa-lightbulb me-2 text-warning"),
                                "Use Cases in BioRemPP",
                            ],
                            className="mb-3",
                        ),
                        html.Ul(
                            [
                                html.Li(use_case, className="mb-2")
                                for use_case in use_cases
                            ],
                            className="text-dark",
                            style={"lineHeight": "1.6"},
                        ),
                    ],
                    className="mb-4 pb-4 border-bottom",
                )
            )

        # References Section
        if not references:
            content.append(html.P("No references available", className="text-muted"))
        else:
            content.append(
                html.H5(
                    [
                        html.I(className="fas fa-book-open me-2 text-primary"),
                        "Key References",
                    ],
                    className="mb-3",
                )
            )

            ref_cards = []
            for idx, ref in enumerate(references, 1):
                ref_url = ref.get("url", "")
                if not ref_url and ref.get("doi"):
                    ref_url = f"https://doi.org/{ref.get('doi')}"

                ref_cards.append(
                    dbc.Card(
                        [
                            dbc.CardBody(
                                [
                                    html.Div(
                                        [
                                            dbc.Badge(
                                                f"#{idx}",
                                                color="primary",
                                                className="me-2",
                                            ),
                                            html.Strong(
                                                ref.get("title", "No title"),
                                                className="text-dark",
                                            ),
                                        ],
                                        className="mb-3",
                                    ),
                                    html.P(
                                        [
                                            html.I(
                                                className="fas fa-users me-2 text-muted"
                                            ),
                                            html.Strong("Authors: "),
                                            ref.get("authors", "Unknown"),
                                        ],
                                        className="small mb-2",
                                    ),
                                    html.P(
                                        [
                                            html.I(
                                                className="fas fa-book me-2 text-muted"
                                            ),
                                            html.Strong("Journal: "),
                                            html.Em(ref.get("journal", "N/A")),
                                        ],
                                        className="small mb-2",
                                    ),
                                    html.P(
                                        [
                                            html.I(
                                                className="fas fa-calendar me-2 text-muted"
                                            ),
                                            html.Strong("Year: "),
                                            ref.get("year", "N/A"),
                                        ],
                                        className="small mb-3",
                                    ),
                                    (
                                        dbc.Button(
                                            [
                                                html.I(
                                                    className="fas fa-external-link-alt me-2"
                                                ),
                                                "View Publication",
                                            ],
                                            href=ref_url,
                                            target="_blank",
                                            color="primary",
                                            size="sm",
                                            outline=True,
                                        )
                                        if ref_url
                                        else html.Div(
                                            "No link available",
                                            className="text-muted small",
                                        )
                                    ),
                                ]
                            )
                        ],
                        className="mb-3 shadow-sm",
                    )
                )

            content.append(html.Div(ref_cards))

        return html.Div(content)

    # Create modals
    modals = html.Div(
        [
            # KO Richness Modal
            dbc.Modal(
                [
                    dbc.ModalHeader(
                        dbc.ModalTitle(
                            [
                                html.I(className="fas fa-dna me-2 text-primary"),
                                "KO Richness - Use Cases and References",
                            ]
                        )
                    ),
                    dbc.ModalBody(
                        create_modal_content(
                            terms.get("ko_richness", {}).get("use_cases", []),
                            terms.get("ko_richness", {}).get("key_references", []),
                        ),
                        style={"maxHeight": "70vh", "overflowY": "auto"},
                    ),
                    dbc.ModalFooter(
                        dbc.Button(
                            "Close",
                            id="ko-refs-modal-close",
                            className="ms-auto",
                            color="secondary",
                        )
                    ),
                ],
                id="ko-refs-modal",
                size="lg",
                is_open=False,
                centered=True,
                backdrop=True,
            ),
            # Compound Richness Modal
            dbc.Modal(
                [
                    dbc.ModalHeader(
                        dbc.ModalTitle(
                            [
                                html.I(className="fas fa-vial me-2 text-success"),
                                "Compound Richness - Use Cases and References",
                            ]
                        )
                    ),
                    dbc.ModalBody(
                        create_modal_content(
                            terms.get("compound_richness", {}).get("use_cases", []),
                            terms.get("compound_richness", {}).get(
                                "key_references", []
                            ),
                        ),
                        style={"maxHeight": "70vh", "overflowY": "auto"},
                    ),
                    dbc.ModalFooter(
                        dbc.Button(
                            "Close",
                            id="compound-refs-modal-close",
                            className="ms-auto",
                            color="secondary",
                        )
                    ),
                ],
                id="compound-refs-modal",
                size="lg",
                is_open=False,
                centered=True,
                backdrop=True,
            ),
            # Functional Guilds Modal
            dbc.Modal(
                [
                    dbc.ModalHeader(
                        dbc.ModalTitle(
                            [
                                html.I(
                                    className="fas fa-project-diagram me-2 text-info"
                                ),
                                "Metabolic Functional Guilds - Use Cases and References",
                            ]
                        )
                    ),
                    dbc.ModalBody(
                        create_modal_content(
                            terms.get("metabolic_functional_guilds", {}).get(
                                "use_cases", []
                            ),
                            terms.get("metabolic_functional_guilds", {}).get(
                                "key_references", []
                            ),
                        ),
                        style={"maxHeight": "70vh", "overflowY": "auto"},
                    ),
                    dbc.ModalFooter(
                        dbc.Button(
                            "Close",
                            id="guilds-refs-modal-close",
                            className="ms-auto",
                            color="secondary",
                        )
                    ),
                ],
                id="guilds-refs-modal",
                size="lg",
                is_open=False,
                centered=True,
                backdrop=True,
            ),
        ]
    )

    return modals


def _create_datascience_section(data: Dict) -> dbc.Container:
    """
    Create Section 2: Data Science & Feature Engineering.

    Parameters
    ----------
    data : Dict
        Data science methods data from datascience.yaml

    Returns
    -------
    dbc.Container
        Section with feature engineering, visualization, and bioremediation DS.

    Notes
    -----
    - Accordion layout for three categories
    - Each category has methods, applications, and references
    """
    if "error" in data:
        return dbc.Container(
            [dbc.Alert(data["error"], color="warning")], className="my-5"
        )

    categories = data.get("categories", {})

    accordion_items = []

    # Feature Engineering
    fe_data = categories.get("feature_engineering", {})
    accordion_items.append(
        dbc.AccordionItem(
            [
                html.P(fe_data.get("description", ""), className="mb-3"),
                html.H6("BioRemPP Applications", className="text-muted mb-2"),
                html.Ul(
                    [
                        html.Li(app, className="small")
                        for app in fe_data.get("biorempp_applications", [])
                    ]
                ),
                html.H6("References", className="text-muted mb-2 mt-3"),
                _create_ds_reference_cards(fe_data.get("references", [])),
            ],
            title=[
                html.I(className=f"fas {fe_data.get('icon', 'fa-cogs')} me-2"),
                fe_data.get("title", "Feature Engineering"),
            ],
        )
    )

    # Visualization
    viz_data = categories.get("visualization", {})
    accordion_items.append(
        dbc.AccordionItem(
            [
                html.P(viz_data.get("description", ""), className="mb-3"),
                html.H6("BioRemPP Applications", className="text-muted mb-2"),
                html.Ul(
                    [
                        html.Li(app, className="small")
                        for app in viz_data.get("biorempp_applications", [])
                    ]
                ),
                html.H6("References", className="text-muted mb-2 mt-3"),
                _create_ds_reference_cards(viz_data.get("references", [])),
            ],
            title=[
                html.I(className=f"fas {viz_data.get('icon', 'fa-chart-bar')} me-2"),
                viz_data.get("title", "Visualization"),
            ],
        )
    )

    # Bioremediation Data Science
    bio_ds_data = categories.get("bioremediation_datascience", {})
    accordion_items.append(
        dbc.AccordionItem(
            [
                html.P(bio_ds_data.get("description", ""), className="mb-3"),
                html.H6("BioRemPP Applications", className="text-muted mb-2"),
                html.Ul(
                    [
                        html.Li(app, className="small")
                        for app in bio_ds_data.get("biorempp_applications", [])
                    ]
                ),
                html.H6("References", className="text-muted mb-2 mt-3"),
                _create_ds_reference_cards(bio_ds_data.get("references", [])),
            ],
            title=[
                html.I(className=f"fas {bio_ds_data.get('icon', 'fa-leaf')} me-2"),
                bio_ds_data.get("title", "Bioremediation Data Science"),
            ],
        )
    )

    return dbc.Container(
        [
            html.H2(
                [
                    html.I(className="fas fa-chart-line me-3"),
                    "Data Science & Feature Engineering",
                ],
                className="mb-4 mt-5 text-primary",
            ),
            html.P(
                "Computational methods and visualization techniques applied to multi-omics "
                "bioremediation data",
                className="lead mb-4",
            ),
            dbc.Accordion(accordion_items, start_collapsed=True, always_open=True),
        ],
        className="my-5",
    )


def _create_ds_reference_cards(references: list) -> dbc.Row:
    """Create reference cards for data science section."""
    if not references:
        return html.Div("No references available", className="text-muted small")

    cards = []
    for ref in references[:3]:  # Show first 3
        cards.append(
            dbc.Col(
                [
                    dbc.Card(
                        [
                            dbc.CardBody(
                                [
                                    html.H6(
                                        ref.get("title", "No title"),
                                        className="card-title small",
                                    ),
                                    html.P(
                                        f"{ref.get('authors', 'Unknown')} ({ref.get('year', 'N/A')})",
                                        className="card-text small text-muted mb-2",
                                    ),
                                    html.P(
                                        ref.get("relevance_to_biorempp", ""),
                                        className="small",
                                    ),
                                    (
                                        dbc.Button(
                                            [
                                                html.I(
                                                    className="fas fa-external-link-alt me-2"
                                                ),
                                                "View",
                                            ],
                                            href=ref.get("url", "#"),
                                            target="_blank",
                                            size="sm",
                                            color="primary",
                                            outline=True,
                                        )
                                        if ref.get("url")
                                        else ""
                                    ),
                                ]
                            )
                        ],
                        className="h-100 shadow-sm",
                    )
                ],
                md=4,
                className="mb-3",
            )
        )

    return dbc.Row(cards)


def _create_fair_section(data: Dict) -> dbc.Container:
    """
    Create Section 3: FAIR Principles & Databases.

    Parameters
    ----------
    data : Dict
        FAIR and bioremediation data from bioremediation.yaml

    Returns
    -------
    dbc.Container
        Section with FAIR principles and integrated databases.
    """
    if "error" in data:
        return dbc.Container(
            [dbc.Alert(data["error"], color="warning")], className="my-5"
        )

    fair = data.get("fair_principles", {})
    databases = data.get("integrated_databases", {})

    # FAIR Principles Cards
    principles = fair.get("principles", {})
    fair_cards = []

    for key in ["findable", "accessible", "interoperable", "reusable"]:
        principle = principles.get(key, {})
        fair_cards.append(
            dbc.Col(
                [
                    dbc.Card(
                        [
                            dbc.CardHeader(
                                [
                                    html.I(
                                        className=f"fas {principle.get('icon', 'fa-check')} me-2"
                                    ),
                                    html.Strong(
                                        principle.get("label", key.capitalize())
                                    ),
                                ],
                                className="bg-success text-white",
                            ),
                            dbc.CardBody(
                                [
                                    html.P(
                                        principle.get("description", ""),
                                        className="small mb-3",
                                    ),
                                    html.H6(
                                        "Implementation",
                                        className="text-muted small mb-2",
                                    ),
                                    html.Ul(
                                        [
                                            html.Li(impl, className="small")
                                            for impl in principle.get(
                                                "biorempp_implementation", []
                                            )[:3]
                                        ]
                                    ),
                                ]
                            ),
                        ],
                        className="h-100 shadow-sm",
                    )
                ],
                md=3,
                className="mb-4",
            )
        )

    # Database Cards
    db_cards = []
    for db in databases.get("databases", []):
        db_cards.append(
            dbc.Col(
                [
                    dbc.Card(
                        [
                            dbc.CardHeader(
                                [
                                    html.I(
                                        className=f"fas {db.get('icon', 'fa-database')} me-2"
                                    ),
                                    html.Strong(db.get("name", "Database")),
                                ]
                            ),
                            dbc.CardBody(
                                [
                                    dbc.Badge(
                                        db.get("type", "Reference"),
                                        color="info",
                                        className="mb-2",
                                    ),
                                    html.P(
                                        db.get("description", ""), className="small"
                                    ),
                                ]
                            ),
                        ],
                        className="h-100 shadow-sm",
                    )
                ],
                md=3,
                className="mb-3",
            )
        )

    return dbc.Container(
        [
            html.H2(
                [
                    html.I(className="fas fa-database me-3"),
                    "FAIR Principles & Integrated Databases",
                ],
                className="mb-4 mt-5 text-primary",
            ),
            html.P(
                "Data interoperability and reproducibility through FAIR principles and "
                "multi-database integration",
                className="lead mb-4",
            ),
            html.H4("FAIR Data Principles", className="mb-3 mt-4"),
            dbc.Row(fair_cards),
            html.H4("Integrated Databases", className="mb-3 mt-5"),
            dbc.Row(db_cards),
        ],
        className="my-5",
    )


def _create_multiomics_section(data: Dict) -> dbc.Container:
    """
    Create Section 4: Multi-omics Integration & Interoperability.

    Parameters
    ----------
    data : Dict
        Multi-omics data from multiomics.yaml

    Returns
    -------
    dbc.Container
        Section with BioRemPP framework and interoperability catalog.

    Notes
    -----
    - Two main subsections: BioRemPP Framework and Interoperability Catalog
    - Displays core identifiers, omics layers, and external tool compatibility
    """
    if "error" in data:
        return dbc.Container(
            [dbc.Alert(data["error"], color="warning")], className="my-5"
        )

    framework = data.get("biorempp_framework", {})
    interop = data.get("interoperability_catalog", {})

    return dbc.Container(
        [
            # Main Title
            html.H2(
                [
                    html.I(className="fas fa-layer-group me-3"),
                    "Multi-omics Integration & Interoperability",
                ],
                className="mb-4 mt-5 text-primary",
            ),
            html.P(framework.get("description", ""), className="lead mb-5"),
            # ============================================================
            # SECTION 1: BIOREMPP FRAMEWORK
            # ============================================================
            html.Div(
                [
                    html.H3(
                        [
                            html.I(className="fas fa-dna me-2"),
                            framework.get("title", "BioRemPP Multi-omics Framework"),
                        ],
                        className="mb-3 text-success",
                    ),
                    html.P(
                        framework.get("subtitle", ""),
                        className="text-muted mb-4",
                        style={"fontSize": "1.1rem"},
                    ),
                    # Core Identifiers
                    html.H4(
                        [
                            html.I(className="fas fa-fingerprint me-2"),
                            "Core Interoperable Identifiers",
                        ],
                        className="mb-3 mt-4",
                    ),
                    dbc.Row(
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
                                                                className="fas fa-tag me-2 text-primary"
                                                            ),
                                                            identifier.get("label", ""),
                                                        ],
                                                        className="mb-2",
                                                    ),
                                                    html.P(
                                                        identifier.get(
                                                            "description", ""
                                                        ),
                                                        className="small text-muted mb-2",
                                                    ),
                                                    html.Code(
                                                        identifier.get("example", ""),
                                                        className="small",
                                                    ),
                                                    html.Div(
                                                        [
                                                            dbc.Badge(
                                                                db,
                                                                color="light",
                                                                className="me-1 text-dark",
                                                            )
                                                            for db in identifier.get(
                                                                "databases", []
                                                            )
                                                        ],
                                                        className="mt-2",
                                                    ),
                                                ]
                                            )
                                        ],
                                        className="h-100 shadow-sm border-primary",
                                    )
                                ],
                                md=4,
                                lg=2,
                                className="mb-3",
                            )
                            for identifier in framework.get("core_identifiers", {}).get(
                                "identifiers", []
                            )
                        ]
                    ),
                    # Omics Layers
                    html.H4(
                        [html.I(className="fas fa-layer-group me-2"), "Omics Layers"],
                        className="mb-3 mt-5",
                    ),
                    dbc.Row(
                        [
                            dbc.Col(
                                [
                                    dbc.Card(
                                        [
                                            dbc.CardHeader(
                                                [
                                                    html.I(
                                                        className=f"fas {layer.get('icon', 'fa-dna')} me-2"
                                                    ),
                                                    html.Strong(layer.get("label", "")),
                                                ],
                                                className=f"bg-{layer.get('color', 'primary')} text-white",
                                            ),
                                            dbc.CardBody(
                                                [
                                                    html.P(
                                                        layer.get("description", ""),
                                                        className="small mb-3",
                                                    ),
                                                    dbc.Badge(
                                                        (
                                                            "Future Features"
                                                            if layer.get(
                                                                "future_integration"
                                                            )
                                                            else "Implemented"
                                                        ),
                                                        color=(
                                                            "info"
                                                            if layer.get(
                                                                "future_integration"
                                                            )
                                                            else "success"
                                                        ),
                                                        className="mb-2",
                                                    ),
                                                    html.H6(
                                                        "Key Identifiers",
                                                        className="small text-muted mt-3 mb-2",
                                                    ),
                                                    html.Div(
                                                        [
                                                            dbc.Badge(
                                                                kid.upper(),
                                                                color="light",
                                                                className="me-1 text-dark small",
                                                            )
                                                            for kid in layer.get(
                                                                "key_identifiers", []
                                                            )
                                                        ]
                                                    ),
                                                ]
                                            ),
                                        ],
                                        className="h-100 shadow-sm",
                                    )
                                ],
                                md=6,
                                lg=4,
                                className="mb-3",
                            )
                            for key, layer in framework.get("omics_layers", {}).items()
                        ]
                    ),
                ],
                className="mb-5 pb-4 border-bottom",
            ),
            # ============================================================
            # SECTION 2: INTEROPERABILITY CATALOG
            # ============================================================
            html.Div(
                [
                    html.H3(
                        [
                            html.I(className="fas fa-plug me-2"),
                            interop.get(
                                "title",
                                "Interoperability with Multi-omics Technologies",
                            ),
                        ],
                        className="mb-3 text-info",
                    ),
                    html.P(
                        interop.get("subtitle", ""),
                        className="text-muted mb-2",
                        style={"fontSize": "1.1rem"},
                    ),
                    html.P(interop.get("description", ""), className="mb-4"),
                    # Genomics & Metagenomics Tools
                    _create_tool_category_section(
                        interop.get("genomics_metagenomics", {}),
                        "Genomics & Metagenomics Tools",
                    ),
                    # Transcriptomics Tools
                    _create_tool_category_section(
                        interop.get("transcriptomics", {}), "Transcriptomics Tools"
                    ),
                    # Metabolomics Tools
                    _create_tool_category_section(
                        interop.get("metabolomics", {}), "Metabolomics Tools"
                    ),
                    # Proteomics Tools
                    _create_tool_category_section(
                        interop.get("proteomics", {}), "Proteomics Tools"
                    ),
                    # Integrative Frameworks
                    _create_tool_category_section(
                        interop.get("integrative_frameworks", {}),
                        "Integrative Multi-omics Frameworks",
                    ),
                ]
            ),
        ],
        className="my-5",
    )


def _create_tool_category_section(
    category_data: Dict, title_override: str = None
) -> html.Div:
    """
    Create a tool category section for interoperability catalog.

    Parameters
    ----------
    category_data : Dict
        Category data with tools list
    title_override : str, optional
        Override title if provided

    Returns
    -------
    html.Div
        Formatted tool category section
    """
    if not category_data or not category_data.get("tools"):
        return html.Div()

    title = title_override or category_data.get("title", "Tools")
    icon = category_data.get("icon", "fa-tools")
    color = category_data.get("color", "primary")
    description = category_data.get("description", "")

    tool_cards = []
    for tool in category_data.get("tools", []):
        # Interoperable IDs badges
        interop_ids = tool.get("interoperable_ids", {})
        id_badges = []
        for id_type, id_desc in interop_ids.items():
            if "native" in id_desc.lower() or "direct" in id_desc.lower():
                badge_color = "success"
            elif "indirect" in id_desc.lower():
                badge_color = "warning"
            else:
                badge_color = "secondary"

            id_badges.append(
                dbc.Badge(
                    [
                        (
                            html.I(className="fas fa-check-circle me-1")
                            if badge_color == "success"
                            else ""
                        ),
                        id_type.upper(),
                    ],
                    color=badge_color,
                    className="me-1 mb-1",
                    pill=True,
                )
            )

        # Reference section
        ref = tool.get("reference", {})
        ref_url = ref.get("url") or ref.get("doi", "")
        if ref_url and not ref_url.startswith("http"):
            ref_url = (
                f"https://doi.org/{ref_url}"
                if "doi.org" not in ref_url
                else f"https://{ref_url}"
            )

        tool_cards.append(
            dbc.Col(
                [
                    dbc.Card(
                        [
                            dbc.Row(
                                [
                                    # Left column: Tool info
                                    dbc.Col(
                                        [
                                            dbc.CardHeader(
                                                [
                                                    html.I(
                                                        className=f"fas fa-cube me-2"
                                                    ),
                                                    html.Strong(
                                                        tool.get("name", "Tool")
                                                    ),
                                                ],
                                                className=f"bg-{color} text-white",
                                            ),
                                            dbc.CardBody(
                                                [
                                                    html.P(
                                                        tool.get("description", ""),
                                                        className="small mb-3",
                                                    ),
                                                    html.H6(
                                                        "Interoperable IDs",
                                                        className="small text-muted mb-2",
                                                    ),
                                                    html.Div(
                                                        id_badges, className="mb-3"
                                                    ),
                                                    html.H6(
                                                        "Integration Example",
                                                        className="small text-muted mb-1",
                                                    ),
                                                    html.P(
                                                        tool.get(
                                                            "integration_example", ""
                                                        ),
                                                        className="small text-success mb-0",
                                                        style={"fontStyle": "italic"},
                                                    ),
                                                ]
                                            ),
                                        ],
                                        md=8,
                                    ),
                                    # Right column: Reference
                                    dbc.Col(
                                        [
                                            dbc.CardBody(
                                                [
                                                    html.Div(
                                                        [
                                                            html.I(
                                                                className="fas fa-book-open me-2 text-muted"
                                                            ),
                                                            html.Strong(
                                                                "Reference",
                                                                className="text-muted small",
                                                            ),
                                                        ],
                                                        className="mb-3",
                                                    ),
                                                    html.H6(
                                                        ref.get("title", "No title"),
                                                        className="small mb-2",
                                                        style={"lineHeight": "1.4"},
                                                    ),
                                                    html.P(
                                                        [
                                                            html.Strong(
                                                                ref.get(
                                                                    "authors", "Unknown"
                                                                )
                                                            ),
                                                            html.Br(),
                                                            html.Em(
                                                                ref.get("journal", "")
                                                            ),
                                                            (
                                                                f" ({ref.get('year', 'N/A')})"
                                                                if ref.get("year")
                                                                else ""
                                                            ),
                                                        ],
                                                        className="small text-muted mb-3",
                                                    ),
                                                    (
                                                        dbc.Button(
                                                            [
                                                                html.I(
                                                                    className="fas fa-external-link-alt me-2"
                                                                ),
                                                                "View Publication",
                                                            ],
                                                            href=ref_url,
                                                            target="_blank",
                                                            color=color,
                                                            size="sm",
                                                            outline=True,
                                                            className="w-100",
                                                        )
                                                        if ref_url
                                                        else html.Div(
                                                            "No link available",
                                                            className="text-muted small text-center",
                                                        )
                                                    ),
                                                ],
                                                className="bg-light",
                                            )
                                        ],
                                        md=4,
                                        className="border-start",
                                    ),
                                ],
                                className="g-0",
                            )
                        ],
                        className="shadow-sm mb-3",
                    )
                ],
                md=12,
            )
        )

    return html.Div(
        [
            html.H4(
                [html.I(className=f"fas {icon} me-2 text-{color}"), title],
                className="mb-2 mt-5",
            ),
            html.P(description, className="text-muted mb-3"),
            dbc.Row(tool_cards),
        ]
    )


def _create_cta_section() -> dbc.Container:
    """
    Create call-to-action section.

    Returns
    -------
    dbc.Container
        CTA section with button to detailed workflow methods.
    """
    return dbc.Container(
        [
            dbc.Card(
                [
                    dbc.CardBody(
                        [
                            html.H3(
                                "Ready to Explore Detailed Analytical Methods?",
                                className="text-center mb-4",
                            ),
                            html.P(
                                "Discover step-by-step methodologies for each of the 56 use cases "
                                "with interactive examples and comprehensive documentation",
                                className="text-center text-muted mb-4",
                            ),
                            html.Div(
                                [
                                    dbc.Button(
                                        [
                                            html.I(className="fas fa-arrow-right me-2"),
                                            "View 56 Analytical Workflows",
                                        ],
                                        href="/methods",
                                        color="success",
                                        size="lg",
                                        className="px-5",
                                    )
                                ],
                                className="text-center",
                            ),
                        ],
                        className="py-5",
                    )
                ],
                className="shadow-lg border-success",
            )
        ],
        className="my-5",
    )
