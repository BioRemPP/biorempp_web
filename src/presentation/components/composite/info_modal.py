import dash_bootstrap_components as dbc
from dash import html


def create_info_modal() -> dbc.Modal:
    """
    Create the "More Info" modal with platform overview and database information.

    Returns
    -------
    dbc.Modal
        A Bootstrap modal component with platform and database details.

    Notes
    -----
    - Modal is extra-large (size="xl") and vertically centered
    - Body is scrollable for long content
    - Can be closed via X button or clicking outside (backdrop=True)
    """
    # Platform Overview Section
    platform_overview = html.Div(
        [
            html.H4("🌍 Bioremediation Framework", className="text-success mb-3"),
            html.P(
                [
                    html.Strong("BioRemPP"),
                    " is a ",
                    html.Strong("free web servce"),
                    " designed to  perform genomic data analysis for environmental bioremediation. "
                    "Accessible to all users without login requirements, BioRemPP addresses the global challenge "
                    "of environmental pollution",
                ],
                className="mb-3",
            ),
            # SDG Alignment
            dbc.Alert(
                [
                    html.Div(
                        [
                            html.I(className="fas fa-globe me-2"),
                            html.Strong(
                                "Aligned with UN Sustainable Development Goals"
                            ),
                        ],
                        className="mb-2",
                    ),
                    html.Ul(
                        [
                            html.Li(
                                [
                                    html.Strong("SDG 3:"),
                                    " Good Health and Well-being - Reducing pollutant exposure",
                                ]
                            ),
                            html.Li(
                                [
                                    html.Strong("SDG 6:"),
                                    " Clean Water and Sanitation - Water quality restoration",
                                ]
                            ),
                            html.Li(
                                [
                                    html.Strong("SDG 13:"),
                                    " Climate Action - Sustainable environmental solutions",
                                ]
                            ),
                            html.Li(
                                [
                                    html.Strong("SDG 14:"),
                                    " Life Below Water - Aquatic ecosystem protection",
                                ]
                            ),
                            html.Li(
                                [
                                    html.Strong("SDG 15:"),
                                    " Life on Land - Terrestrial ecosystem restoration",
                                ]
                            ),
                        ],
                        className="mb-0",
                    ),
                ],
                color="info",
                className="mb-3",
            ),
            # Framework Architecture
            html.H5("🔬 Framework Architecture", className="text-primary mb-2 mt-3"),
            html.P(
                [
                    "BioRemPP integrates ",
                    html.Strong("8 analytical modules"),
                    " covering ",
                    html.Strong("56 use cases"),
                    " for comprehensive bioremediation assessment:",
                ],
                className="mb-2",
            ),
            dbc.Row(
                [
                    dbc.Col(
                        [
                            html.Ul(
                                [
                                    html.Li(
                                        "Module 1: Comparative Assessment of Databases, Samples, and Regulatory Frameworks (7 use cases)"
                                    ),
                                    html.Li(
                                        "Module 2: Exploratory Analysis: Ranking the Functional Potential of Samples and Compounds (7 use cases)"
                                    ),
                                    html.Li(
                                        "Module 3: System Structure: Clustering, Similarity, and Co-occurrence (7 use cases)"
                                    ),
                                    html.Li(
                                        "Module 4: Functional and Genetic Profiling (7 use cases)"
                                    ),
                                ],
                                className="small",
                            )
                        ],
                        md=6,
                    ),
                    dbc.Col(
                        [
                            html.Ul(
                                [
                                    html.Li(
                                        "Module 5: Modeling Interactions among Samples, Genes, and Compounds (7 use cases)"
                                    ),
                                    html.Li(
                                        "Module 6: Hierarchical and Flow-based Functional Analysis (7 use cases)"
                                    ),
                                    html.Li(
                                        "Module 7: Toxicological Risk Assessment and Profiling (7 use cases)"
                                    ),
                                    html.Li(
                                        "Module 8: Assembly of Functional Consortia (7 use cases)"
                                    ),
                                ],
                                className="small",
                            )
                        ],
                        md=6,
                    ),
                ],
                className="mb-3",
            ),
            # Data Integration
            html.H5("🗄️ Integrated Databases", className="text-primary mb-2 mt-3"),
            html.P("BioRemPP integrates four specialized databases:", className="mb-2"),
            dbc.ListGroup(
                [
                    dbc.ListGroupItem(
                        [
                            html.Strong("BioRemPP Database: "),
                            "Compound-centric, regulatory-based database (384 compounds, 1,541 KOs, 10,869 relations)",
                        ],
                        className="border-0 ps-0 py-1",
                    ),
                    dbc.ListGroupItem(
                        [
                            html.Strong("HADEG: "),
                            html.A(
                                "Hydrocarbon Aerobic Degrading Enzymes",
                                href="https://github.com/jarojasva/HADEG",
                                target="_blank",
                                className="text-primary",
                            ),
                            " (1,168 gene-pathway relations)",
                        ],
                        className="border-0 ps-0 py-1",
                    ),
                    dbc.ListGroupItem(
                        [
                            html.Strong("KEGG: "),
                            html.A(
                                "Degradation Pathway Database",
                                href="https://www.genome.jp/kegg/pathway.html",
                                target="_blank",
                                className="text-primary",
                            ),
                            " (871 pathway records)",
                        ],
                        className="border-0 ps-0 py-1",
                    ),
                    dbc.ListGroupItem(
                        [
                            html.Strong("toxCSM: "),
                            html.A(
                                "Toxicity Prediction via Machine Learning",
                                href="https://biosig.lab.uq.edu.au/toxcsm/",
                                target="_blank",
                                className="text-primary",
                            ),
                            " (323 compounds, 34 endpoints)",
                        ],
                        className="border-0 ps-0 py-1",
                    ),
                ],
                flush=True,
                className="mb-3",
            ),
            # Technical Stack
            html.P(
                [
                    "Built with Python (Pandas, NumPy, scikit-learn), visualization powered by Plotly, "
                    "and delivered through an intuitive Dash interface with ",
                    html.Strong("20+ interactive chart types"),
                    ".",
                ],
                className="text-muted small",
            ),
        ]
    )

    # Database Information Section - Optimized
    database_info = html.Div(
        [
            html.H4(
                "BioRemPP Database: Compound-Centric & Regulatory-Based",
                className="text-success mb-3 mt-4",
            ),
            # Key Characteristics
            dbc.Alert(
                [
                    html.Div(
                        [
                            html.I(className="fas fa-database me-2"),
                            html.Strong("Database Characteristics"),
                        ],
                        className="mb-2",
                    ),
                    html.Ul(
                        [
                            html.Li(
                                [
                                    html.Strong("Compound-Centric: "),
                                    "Organized around 384 priority environmental pollutants",
                                ]
                            ),
                            html.Li(
                                [
                                    html.Strong("Regulatory-Based: "),
                                    "Classified by 9 international frameworks (IARC, EPA, ATSDR, WFD, PSL, EPC, CONAMA, and others)",
                                ]
                            ),
                            html.Li(
                                [
                                    html.Strong("Enzyme-Linked: "),
                                    "1,541 KEGG Orthologs mapped to degradation mechanisms",
                                ]
                            ),
                            html.Li(
                                [
                                    html.Strong("Multi-Dimensional: "),
                                    "Integrates chemical classes, enzyme activities, and regulatory status",
                                ]
                            ),
                        ],
                        className="mb-0",
                    ),
                ],
                color="success",
                className="mb-3",
            ),
            # Database Statistics - Compact
            html.H5("📊 Database Statistics", className="text-primary mb-2"),
            dbc.Row(
                [
                    dbc.Col(
                        [
                            dbc.Card(
                                [
                                    dbc.CardBody(
                                        [
                                            html.H3(
                                                "1,541", className="text-success mb-0"
                                            ),
                                            html.Small(
                                                "KO Identifiers", className="text-muted"
                                            ),
                                        ],
                                        className="text-center py-2",
                                    )
                                ],
                                className="shadow-sm",
                            )
                        ],
                        md=3,
                        className="mb-2",
                    ),
                    dbc.Col(
                        [
                            dbc.Card(
                                [
                                    dbc.CardBody(
                                        [
                                            html.H3(
                                                "384", className="text-primary mb-0"
                                            ),
                                            html.Small(
                                                "Compounds", className="text-muted"
                                            ),
                                        ],
                                        className="text-center py-2",
                                    )
                                ],
                                className="shadow-sm",
                            )
                        ],
                        md=3,
                        className="mb-2",
                    ),
                    dbc.Col(
                        [
                            dbc.Card(
                                [
                                    dbc.CardBody(
                                        [
                                            html.H3("12", className="text-info mb-0"),
                                            html.Small(
                                                "Compound Classes",
                                                className="text-muted",
                                            ),
                                        ],
                                        className="text-center py-2",
                                    )
                                ],
                                className="shadow-sm",
                            )
                        ],
                        md=3,
                        className="mb-2",
                    ),
                    dbc.Col(
                        [
                            dbc.Card(
                                [
                                    dbc.CardBody(
                                        [
                                            html.H3(
                                                "205", className="text-warning mb-0"
                                            ),
                                            html.Small(
                                                "Enzyme Activities",
                                                className="text-muted",
                                            ),
                                        ],
                                        className="text-center py-2",
                                    )
                                ],
                                className="shadow-sm",
                            )
                        ],
                        md=3,
                        className="mb-2",
                    ),
                ],
                className="mb-3",
            ),
            # Compound Classes - Compact
            html.H5("🧪 Compound Classes", className="text-primary mb-2"),
            html.Div(
                [
                    html.Span("Aromatic", className="badge bg-secondary me-1 mb-1"),
                    html.Span("Aliphatic", className="badge bg-secondary me-1 mb-1"),
                    html.Span("Chlorinated", className="badge bg-secondary me-1 mb-1"),
                    html.Span("Halogenated", className="badge bg-secondary me-1 mb-1"),
                    html.Span("Polyaromatic", className="badge bg-secondary me-1 mb-1"),
                    html.Span("Inorganic", className="badge bg-secondary me-1 mb-1"),
                    html.Span(
                        "Organometallic", className="badge bg-secondary me-1 mb-1"
                    ),
                    html.Span(
                        "Organophosphorus", className="badge bg-secondary me-1 mb-1"
                    ),
                    html.Span("Organosulfur", className="badge bg-secondary me-1 mb-1"),
                    html.Span(
                        "Sulfur-containing", className="badge bg-secondary me-1 mb-1"
                    ),
                    html.Span("Metal", className="badge bg-secondary me-1 mb-1"),
                    html.Span(
                        "Nitrogen-containing", className="badge bg-secondary me-1 mb-1"
                    ),
                ],
                style={"display": "flex", "flexWrap": "wrap", "alignItems": "center"},
                className="mb-3",
            ),
            # Regulatory Frameworks - Compact
            html.H5("⚖️ Regulatory Frameworks", className="text-primary mb-2"),
            html.Div(
                [
                    html.Span(
                        "IARC (1, 2A, 2B)", className="badge bg-danger me-1 mb-1"
                    ),
                    html.Span("EPA", className="badge bg-warning text-dark me-1 mb-1"),
                    html.Span("ATSDR", className="badge bg-info me-1 mb-1"),
                    html.Span("WFD", className="badge bg-primary me-1 mb-1"),
                    html.Span("PSL", className="badge bg-success me-1 mb-1"),
                    html.Span("EPC", className="badge bg-secondary me-1 mb-1"),
                    html.Span("CONAMA", className="badge bg-dark me-1 mb-1"),
                ],
                className="mb-3",
            ),
        ]
    )

    # Use Cases Documentation Section
    use_cases_section = html.Div(
        [
            html.H4("📚 Use Cases Documentation", className="text-success mb-3 mt-4"),
            html.P(
                [
                    "Explore detailed documentation for all 56 analytical use cases across 8 modules, "
                    "including step-by-step workflows, interpretation guidelines, and application examples."
                ],
                className="mb-3",
            ),
            dbc.Button(
                [
                    html.I(className="fas fa-book me-2"),
                    "View Complete Use Cases Documentation",
                ],
                color="primary",
                outline=True,
                href="/methods",  # Link to methods page
                className="mb-2",
            ),
            html.P(
                [
                    html.Small(
                        [
                            html.I(className="fas fa-info-circle me-1"),
                            "Navigate to the Methods page to explore all analytical workflows",
                        ],
                        className="text-muted fst-italic",
                    )
                ]
            ),
        ]
    )

    # Assemble modal
    modal = dbc.Modal(
        [
            dbc.ModalHeader(
                dbc.ModalTitle(
                    [
                        html.I(className="fas fa-info-circle me-2"),
                        "About BioRemPP Platform",
                    ]
                ),
                close_button=True,
            ),
            dbc.ModalBody(
                [
                    platform_overview,
                    html.Hr(),
                    database_info,
                    html.Hr(),
                    use_cases_section,
                ],
                style={"maxHeight": "70vh", "overflowY": "auto"},
            ),
            dbc.ModalFooter(
                dbc.Button(
                    "Close",
                    id="info-modal-close-button",
                    className="ms-auto",
                    color="secondary",
                    n_clicks=0,
                )
            ),
        ],
        id="info-modal",
        size="xl",
        is_open=False,
        centered=True,
        backdrop=True,  # Allows closing by clicking outside
        scrollable=True,
    )

    return modal
