import dash_bootstrap_components as dbc
from dash import html


def create_publications_modal() -> dbc.Modal:
    """
    Create the "Publications and Awards" modal with scientific publications and awards.

    Returns
    -------
    dbc.Modal
        A Bootstrap modal component with publications and awards details.

    Notes
    -----
    - Modal is extra-large (size="xl") and vertically centered
    - Body is scrollable for long content
    - Can be closed via X button or clicking outside (backdrop=True)
    """
    # Publications Section
    publications_section = html.Div(
        [
            html.H4(
                [
                    html.I(className="fas fa-book-open me-2 text-success"),
                    "Publications",
                ],
                className="text-success mb-4",
            ),
            # Publication 1
            dbc.Card(
                [
                    dbc.CardBody(
                        [
                            html.H5(
                                [
                                    html.I(
                                        className="fas fa-file-alt me-2 text-primary"
                                    ),
                                    "Unlocking the transcriptional profiles of an oily waste-degrading bacterial consortium",
                                ],
                                className="mb-3",
                            ),
                            html.P(
                                [
                                    html.Strong("Authors: "),
                                    "Silva-Portela, Rita de Cássia Barreto; Minnicelli, Carolina Fonseca; Freitas, Júlia Firme; "
                                    "Fonseca, Marbella Maria Bernardes; Lima Silva, Douglas Felipe de; Silva-Barbalho, Kamila Karla; "
                                    "Falcão, Raul Maia; Bruce, Thiago; Cavalcante, João Vitor Ferreira; Dalmolin, Rodrigo Juliani Siqueira; "
                                    "Agnez-Lima, Lucymara Fassarella",
                                ],
                                className="mb-2",
                                style={"fontSize": "0.9rem"},
                            ),
                            html.P(
                                [
                                    html.I(className="fas fa-journal-whills me-2"),
                                    html.Strong("Journal: "),
                                    html.Em("Journal of Hazardous Materials"),
                                    ", 2024, Pages 136866",
                                ],
                                className="mb-2",
                            ),
                            html.P(
                                [
                                    html.I(className="fas fa-link me-2"),
                                    html.Strong("DOI: "),
                                    html.A(
                                        "https://doi.org/10.1016/j.jhazmat.2024.136866",
                                        href="https://doi.org/10.1016/j.jhazmat.2024.136866",
                                        target="_blank",
                                        className="text-primary",
                                    ),
                                ],
                                className="mb-0",
                            ),
                        ]
                    )
                ],
                className="mb-3",
                style={"backgroundColor": "#f8f9fa"},
            ),
            # Publication 2
            dbc.Card(
                [
                    dbc.CardBody(
                        [
                            html.H5(
                                [
                                    html.I(
                                        className="fas fa-file-alt me-2 text-primary"
                                    ),
                                    "Genomic and phenotypic characterization of novel Ochrobactrum species isolated from Brazilian oil reservoirs: "
                                    "Genomic diversity and bioremediation potential",
                                ],
                                className="mb-3",
                            ),
                            html.P(
                                [
                                    html.Strong("Authors: "),
                                    "Freitas, Júlia Firme; Lima Silva, Douglas Felipe de; Castro, Jenielly Noronha Ferreira; "
                                    "Agnez-Lima, Lucymara Fassarella",
                                ],
                                className="mb-2",
                                style={"fontSize": "0.9rem"},
                            ),
                            html.P(
                                [
                                    html.I(className="fas fa-journal-whills me-2"),
                                    html.Strong("Journal: "),
                                    html.Em("Process Biochemistry"),
                                    ", Volume 149, Pages 74-84, 2025",
                                ],
                                className="mb-2",
                            ),
                            html.P(
                                [
                                    html.I(className="fas fa-link me-2"),
                                    html.Strong("DOI: "),
                                    html.A(
                                        "https://www.sciencedirect.com/science/article/abs/pii/S1359511324003970",
                                        href="https://www.sciencedirect.com/science/article/abs/pii/S1359511324003970",
                                        target="_blank",
                                        className="text-primary",
                                    ),
                                ],
                                className="mb-0",
                            ),
                        ]
                    )
                ],
                className="mb-3",
                style={"backgroundColor": "#f8f9fa"},
            ),
            # Publication 3
            dbc.Card(
                [
                    dbc.CardBody(
                        [
                            html.H5(
                                [
                                    html.I(
                                        className="fas fa-file-alt me-2 text-primary"
                                    ),
                                    "Genomic and phenotypic features of Acinetobacter baumannii isolated from oil reservoirs reveal a novel "
                                    "subspecies specialized in degrading hazardous hydrocarbons",
                                ],
                                className="mb-3",
                            ),
                            html.P(
                                [
                                    html.Strong("Authors: "),
                                    "Freitas, Júlia Firme; Silva, Douglas Felipe de Lima; Silva, Beatriz Soares; "
                                    "Castro, Jenielly Noronha Ferreira; Felipe, Marcus Bruno Mendonça Chaves; "
                                    "Silva-Portela, Renata Cláudia Brito; Minnicelli, Carolina Farah; Agnez-Lima, Lucymara Fassarella",
                                ],
                                className="mb-2",
                                style={"fontSize": "0.9rem"},
                            ),
                            html.P(
                                [
                                    html.I(className="fas fa-journal-whills me-2"),
                                    html.Strong("Journal: "),
                                    html.Em("Microbiological Research"),
                                    ", Volume 273, 127420, August 2023",
                                ],
                                className="mb-2",
                            ),
                            html.P(
                                [
                                    html.I(className="fas fa-link me-2"),
                                    html.Strong("DOI: "),
                                    html.A(
                                        "https://doi.org/10.1016/j.micres.2023.127420",
                                        href="https://doi.org/10.1016/j.micres.2023.127420",
                                        target="_blank",
                                        className="text-primary",
                                    ),
                                ],
                                className="mb-0",
                            ),
                        ]
                    )
                ],
                className="mb-3",
                style={"backgroundColor": "#f8f9fa"},
            ),
        ]
    )

    # Awards Section
    awards_section = html.Div(
        [
            html.H4(
                [html.I(className="fas fa-trophy me-2 text-warning"), "Awards"],
                className="text-success mb-4 mt-5",
            ),
            # Local Awards
            dbc.Card(
                [
                    dbc.CardHeader(
                        [
                            html.I(className="fas fa-map-marker-alt me-2 text-info"),
                            html.Strong("Local"),
                        ],
                        className="bg-light",
                    ),
                    dbc.CardBody(
                        [
                            html.H6(
                                [
                                    html.I(className="fas fa-award me-2 text-warning"),
                                    "BioRemPP: Exploring the genomic potential for bioremediation of priority pollutant compounds",
                                ],
                                className="mb-3",
                            ),
                            html.P(
                                [
                                    html.Strong("Authors: "),
                                    "Silva, Douglas Felipe de Lima; Agnez-Lima, Lucymara Fassarella",
                                ],
                                className="mb-2",
                                style={"fontSize": "0.9rem"},
                            ),
                            html.P(
                                [
                                    html.I(className="fas fa-calendar-alt me-2"),
                                    "Presented at the ",
                                    html.Strong("Annual Workshop of PPGBIONF"),
                                    " Postgraduate Program in Bioinformatics, Federal University of Rio Grande do Norte (UFRN), Natal, Brazil, 2024",
                                ],
                                className="mb-2",
                            ),
                            dbc.Alert(
                                [
                                    html.I(className="fas fa-star me-2"),
                                    html.Strong("Winner of Oral Presentation Award"),
                                ],
                                color="success",
                                className="mb-0",
                            ),
                        ]
                    ),
                ],
                className="mb-3",
            ),
            # Regional Awards
            dbc.Card(
                [
                    dbc.CardHeader(
                        [
                            html.I(className="fas fa-map me-2 text-success"),
                            html.Strong("Regional"),
                        ],
                        className="bg-light",
                    ),
                    dbc.CardBody(
                        [
                            html.H6(
                                [
                                    html.I(className="fas fa-award me-2 text-warning"),
                                    "MicroBioReToxiC (MicroBRTC) - A bioinformatics pipeline for analyzing the bioremediation potential "
                                    "of environmental pollutants in microorganisms",
                                ],
                                className="mb-3",
                            ),
                            html.P(
                                [
                                    html.Strong("Authors: "),
                                    "Silva, Douglas Felipe de Lima; Agnez-Lima, Lucymara Fassarella",
                                ],
                                className="mb-2",
                                style={"fontSize": "0.9rem"},
                            ),
                            html.P(
                                [
                                    html.I(className="fas fa-calendar-alt me-2"),
                                    "Presented at the ",
                                    html.Strong(
                                        "XXIV Encontro de Genética do Nordeste (XXIV ENGENE)"
                                    ),
                                    ", 2023",
                                ],
                                className="mb-2",
                            ),
                            dbc.Alert(
                                [
                                    html.I(className="fas fa-star me-2"),
                                    html.Strong("Winner of Oral Presentation Award"),
                                ],
                                color="success",
                                className="mb-0",
                            ),
                        ]
                    ),
                ],
                className="mb-3",
            ),
            # National Awards
            dbc.Card(
                [
                    dbc.CardHeader(
                        [
                            html.I(className="fas fa-flag me-2 text-primary"),
                            html.Strong("National"),
                        ],
                        className="bg-light",
                    ),
                    dbc.CardBody(
                        [
                            html.H6(
                                [
                                    html.I(className="fas fa-award me-2 text-warning"),
                                    "BioRemPP: A Genomic Platform for Bioremediation Potential Analysis of Priority Pollutant Compounds",
                                ],
                                className="mb-3",
                            ),
                            html.P(
                                [
                                    html.Strong("Authors: "),
                                    "Silva, Douglas Felipe de Lima; Agnez-Lima, Lucymara Fassarella",
                                ],
                                className="mb-2",
                                style={"fontSize": "0.9rem"},
                            ),
                            html.P(
                                [
                                    html.I(className="fas fa-calendar-alt me-2"),
                                    "Presented at the ",
                                    html.Strong(
                                        "Bioinformatics and Computational Biology 21st Brazilian Conference (X-Meeting 2025)"
                                    ),
                                    ", in the area Database and Software Development",
                                ],
                                className="mb-2",
                            ),
                            dbc.Alert(
                                [
                                    html.I(className="fas fa-certificate me-2"),
                                    html.Strong(
                                        "Honorable Mention - Qiagen Digital Insights Excellence Award"
                                    ),
                                ],
                                color="success",
                                className="mb-0",
                            ),
                        ]
                    ),
                ],
                className="mb-3",
            ),
        ]
    )

    # Assemble modal
    modal = dbc.Modal(
        [
            dbc.ModalHeader(
                dbc.ModalTitle("Publications and Awards"),
                close_button=True,
            ),
            dbc.ModalBody(
                [
                    publications_section,
                    html.Hr(),
                    awards_section,
                ],
                style={"maxHeight": "70vh", "overflowY": "auto"},
            ),
            dbc.ModalFooter(
                dbc.Button(
                    "Close",
                    id="publications-modal-close-button",
                    className="ms-auto",
                    color="secondary",
                    n_clicks=0,
                )
            ),
        ],
        id="publications-modal",
        size="xl",
        is_open=False,
        centered=True,
        backdrop=True,
        scrollable=True,
    )

    return modal
