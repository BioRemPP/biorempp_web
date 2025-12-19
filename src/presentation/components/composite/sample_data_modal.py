import dash_bootstrap_components as dbc
from dash import html


def create_sample_data_modal() -> dbc.Modal:
    """
    Create the "Sample Data" modal with example dataset and organism information.

    Returns
    -------
    dbc.Modal
        A Bootstrap modal component with sample data details.

    Notes
    -----
    - Modal is extra-large (size="xl") and vertically centered
    - Body is scrollable for long content
    - Can be closed via X button or clicking outside (backdrop=True)
    """
    # Example Dataset Section
    example_dataset = html.Div(
        [
            html.H4("Example Dataset", className="text-success mb-3"),
            html.P(
                [
                    "For demonstration purposes, BioRemPP includes an example dataset to illustrate the "
                    "expected input structure:"
                ],
                className="mb-3",
            ),
            # Code block with example data
            dbc.Card(
                [
                    dbc.CardBody(
                        [
                            html.Pre(
                                [
                                    html.Code(
                                        [
                                            ">Sample1\n",
                                            "K00031\n",
                                            "K00032\n",
                                            "K00090\n",
                                            "K00042\n",
                                            "K00052\n",
                                            ">Sample2\n",
                                            "K00031\n",
                                            "K00032\n",
                                            "K00090\n",
                                            "K00042\n",
                                            "K00052",
                                        ],
                                        style={
                                            "fontSize": "0.9rem",
                                            "color": "#2c3e50",
                                            "fontFamily": "monospace",
                                        },
                                    )
                                ],
                                style={
                                    "backgroundColor": "#f8f9fa",
                                    "padding": "1rem",
                                    "borderRadius": "4px",
                                    "margin": "0",
                                },
                            )
                        ],
                        style={"padding": "0.5rem"},
                    )
                ],
                className="mb-4",
                style={"backgroundColor": "#ffffff", "border": "1px solid #dee2e6"},
            ),
        ]
    )

    # Selected Organisms Section
    selected_organisms = html.Div(
        [
            html.H4("Selected Organisms", className="text-success mb-3 mt-4"),
            html.P(
                [
                    "For the published demonstration, BioRemPP uses ",
                    html.Strong("nine representative organisms"),
                    " spanning three principal groups in bioremediation:",
                ],
                className="mb-3",
            ),
            # Bacteria
            dbc.Card(
                [
                    dbc.CardHeader(
                        [
                            html.I(className="fas fa-bacterium me-2 text-primary"),
                            html.Strong("Bacteria"),
                        ],
                        className="bg-light",
                    ),
                    dbc.CardBody(
                        [
                            html.Ul(
                                [
                                    html.Li(
                                        [
                                            html.Em("Acinetobacter baumannii"),
                                            " — ",
                                            html.Code(
                                                "acb",
                                                style={
                                                    "fontSize": "0.85rem",
                                                    "color": "#6c757d",
                                                },
                                            ),
                                        ]
                                    ),
                                    html.Li(
                                        [
                                            html.Em("Enterobacter asburiae"),
                                            " — ",
                                            html.Code(
                                                "eau",
                                                style={
                                                    "fontSize": "0.85rem",
                                                    "color": "#6c757d",
                                                },
                                            ),
                                        ]
                                    ),
                                    html.Li(
                                        [
                                            html.Em("Pseudomonas aeruginosa"),
                                            " — ",
                                            html.Code(
                                                "pae",
                                                style={
                                                    "fontSize": "0.85rem",
                                                    "color": "#6c757d",
                                                },
                                            ),
                                        ]
                                    ),
                                ],
                                className="mb-0",
                            )
                        ]
                    ),
                ],
                className="mb-3",
            ),
            # Fungi
            dbc.Card(
                [
                    dbc.CardHeader(
                        [
                            html.I(className="fas fa-leaf me-2 text-success"),
                            html.Strong("Fungi"),
                        ],
                        className="bg-light",
                    ),
                    dbc.CardBody(
                        [
                            html.Ul(
                                [
                                    html.Li(
                                        [
                                            html.Em("Aspergillus nidulans"),
                                            " — ",
                                            html.Code(
                                                "ani",
                                                style={
                                                    "fontSize": "0.85rem",
                                                    "color": "#6c757d",
                                                },
                                            ),
                                        ]
                                    ),
                                    html.Li(
                                        [
                                            html.Em("Fusarium graminearum"),
                                            " — ",
                                            html.Code(
                                                "fgr",
                                                style={
                                                    "fontSize": "0.85rem",
                                                    "color": "#6c757d",
                                                },
                                            ),
                                        ]
                                    ),
                                    html.Li(
                                        [
                                            html.Em("Cryptococcus gattii"),
                                            " — ",
                                            html.Code(
                                                "cgi",
                                                style={
                                                    "fontSize": "0.85rem",
                                                    "color": "#6c757d",
                                                },
                                            ),
                                        ]
                                    ),
                                ],
                                className="mb-0",
                            )
                        ]
                    ),
                ],
                className="mb-3",
            ),
            # Microalgae / Cyanobacteria
            dbc.Card(
                [
                    dbc.CardHeader(
                        [
                            html.I(className="fas fa-water me-2 text-info"),
                            html.Strong("Microalgae / Cyanobacteria"),
                        ],
                        className="bg-light",
                    ),
                    dbc.CardBody(
                        [
                            html.Ul(
                                [
                                    html.Li(
                                        [
                                            html.Em("Chlorella variabilis"),
                                            " — ",
                                            html.Code(
                                                "cvr",
                                                style={
                                                    "fontSize": "0.85rem",
                                                    "color": "#6c757d",
                                                },
                                            ),
                                        ]
                                    ),
                                    html.Li(
                                        [
                                            html.Em("Nannochloropsis gaditana"),
                                            " — ",
                                            html.Code(
                                                "ngd",
                                                style={
                                                    "fontSize": "0.85rem",
                                                    "color": "#6c757d",
                                                },
                                            ),
                                        ]
                                    ),
                                    html.Li(
                                        [
                                            html.Em("Synechocystis sp."),
                                            " — ",
                                            html.Code(
                                                "syn",
                                                style={
                                                    "fontSize": "0.85rem",
                                                    "color": "#6c757d",
                                                },
                                            ),
                                        ]
                                    ),
                                ],
                                className="mb-0",
                            )
                        ]
                    ),
                ],
                className="mb-3",
            ),
            # Reference
            dbc.Alert(
                [
                    html.I(className="fas fa-book-open me-2"),
                    html.Strong("Reference: "),
                    "These organisms were selected based on their relevance in hydrocarbon bioremediation studies, as highlighted in: ",
                    html.Em(
                        "Bacteria, Fungi and Microalgae for the Bioremediation of Marine Sediments Contaminated by Petroleum Hydrocarbons in the Omics Era"
                    ),
                    " — Microorganisms 2021, 9, 1695. ",
                    html.A(
                        "https://doi.org/10.3390/microorganisms9081695",
                        href="https://doi.org/10.3390/microorganisms9081695",
                        target="_blank",
                        className="alert-link",
                    ),
                ],
                color="info",
                className="mt-4",
            ),
        ]
    )

    # Assemble modal
    modal = dbc.Modal(
        [
            dbc.ModalHeader(
                dbc.ModalTitle("Sample Data Information"),
                close_button=True,
            ),
            dbc.ModalBody(
                [
                    example_dataset,
                    html.Hr(),
                    selected_organisms,
                ],
                style={"maxHeight": "70vh", "overflowY": "auto"},
            ),
            dbc.ModalFooter(
                dbc.Button(
                    "Close",
                    id="sample-data-modal-close-button",
                    className="ms-auto",
                    color="secondary",
                    n_clicks=0,
                )
            ),
        ],
        id="sample-data-modal",
        size="xl",
        is_open=False,
        centered=True,
        backdrop=True,  # Allows closing by clicking outside
        scrollable=True,
    )

    return modal
