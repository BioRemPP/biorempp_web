"""
How to Cite Page - BioRemPP v1.0.

Citation guidelines for BioRemPP web service and database following
scientific publication best practices.

Functions
---------
create_how_to_cite_page
    Create complete citation guide page layout

Notes
-----
- Static informational page (no callbacks)
- Pre-DOI citation templates with placeholders
- BibTeX templates for both software and database
- Third-party resource citation guidelines
"""

import dash_bootstrap_components as dbc
from dash import html

from ..components.base import create_footer, create_header


def create_why_cite_section() -> html.Div:
    """
    Create section explaining importance of proper citation.

    Returns
    -------
    html.Div
        Section explaining citation importance
    """
    return html.Div(
        [
            html.H2(
                [
                    html.I(className="fas fa-question-circle me-2 text-success"),
                    "Why Cite BioRemPP?",
                ],
                className="mb-4",
            ),
            dbc.Card(
                [
                    dbc.CardBody(
                        [
                            html.P(
                                [
                                    "Proper citation of BioRemPP ensures ",
                                    html.Strong("scientific reproducibility"),
                                    " and supports the ",
                                    html.Strong("sustainability"),
                                    " of this open-access research platform.",
                                ],
                                className="lead",
                            ),
                            html.Hr(),
                            html.Ul(
                                [
                                    html.Li([
                                        html.Strong("Reproducibility: "),
                                        "Citations enable other researchers to replicate your analyses "
                                        "using the same tools and database versions.",
                                    ]),
                                    html.Li([
                                        html.Strong("Project Sustainability: "),
                                        "Tracking usage through citations helps demonstrate impact "
                                        "and secure funding for continued development.",
                                    ]),
                                    html.Li([
                                        html.Strong("Scientific Transparency: "),
                                        "Proper attribution acknowledges the computational methods "
                                        "and curated data underlying your results.",
                                    ]),
                                ],
                                className="mb-0",
                            ),
                        ]
                    )
                ],
                className="shadow-sm",
            ),
        ],
        className="mb-5",
    )


def create_citation_overview_section() -> html.Div:
    """
    Create overview of BioRemPP citation components.

    Returns
    -------
    html.Div
        Citation components overview section
    """
    return html.Div(
        [
            html.H2(
                [
                    html.I(className="fas fa-list-alt me-2 text-success"),
                    "Citation Overview",
                ],
                className="mb-4",
            ),
            dbc.Alert(
                [
                    html.I(className="fas fa-info-circle me-2"),
                    html.Strong("Important: "),
                    "BioRemPP comprises ",
                    html.Strong("distinct artifacts"),
                    " that must be cited ",
                    html.Strong("separately"),
                    " depending on your use case.",
                ],
                color="info",
                className="mb-3 text-dark",
            ),
            dbc.ListGroup(
                [
                    dbc.ListGroupItem(
                        [
                            html.Div(
                                [
                                    html.I(className="fas fa-globe me-2 text-primary"),
                                    html.Strong("BioRemPP Web Service"),
                                ],
                                className="mb-2",
                            ),
                            html.Small(
                                "Cite when using the interactive web platform for analysis",
                                className="text-muted",
                            ),
                        ]
                    ),
                    dbc.ListGroupItem(
                        [
                            html.Div(
                                [
                                    html.I(className="fas fa-database me-2 text-success"),
                                    html.Strong("BioRemPP Database"),
                                ],
                                className="mb-2",
                            ),
                            html.Small(
                                "Cite when referencing curated enzyme-compound associations "
                                "from the database",
                                className="text-muted",
                            ),
                        ]
                    ),
                    dbc.ListGroupItem(
                        [
                            html.Div(
                                [
                                    html.I(className="fas fa-file-alt me-2 text-warning"),
                                    html.Strong("Scientific Article"),
                                ],
                                className="mb-2",
                            ),
                            html.Small(
                                "(Future) Cite when referencing methodology or validation results",
                                className="text-muted",
                            ),
                        ]
                    ),
                ],
                flush=True,
            ),
        ],
        className="mb-5",
    )


def create_pre_doi_section() -> html.Div:
    """
    Create section with pre-DOI citation templates.

    Returns
    -------
    html.Div
        Pre-DOI citation templates section
    """
    return html.Div(
        [
            html.H2(
                [
                    html.I(className="fas fa-exclamation-triangle me-2 text-warning"),
                    "Citation Before DOI Assignment",
                ],
                className="mb-4",
            ),
            dbc.Alert(
                [
                    html.I(className="fas fa-hourglass-half me-2"),
                    html.Strong("Pending Publication: "),
                    "The BioRemPP manuscript is currently under review. "
                    "DOIs will be assigned upon formal publication via ",
                    html.A(
                        "Zenodo",
                        href="https://zenodo.org",
                        target="_blank",
                        className="alert-link",
                    ),
                    ". Until then, please use the provisional citation formats below.",
                ],
                color="warning",
                className="mb-4 text-dark",
            ),
            # Web Service pre-DOI
            html.H4("BioRemPP Web Service (Provisional Citation)", className="mb-3"),
            dbc.Card(
                [
                    dbc.CardHeader(
                        "Recommended Format",
                        className="bg-light",
                    ),
                    dbc.CardBody(
                        [
                            html.Pre(
                                "[Author Names]. BioRemPP Web Service: an interactive platform for "
                                "bioremediation potential profiling. [Year]. Available at: "
                                "[https://biorempp.org] (accessed [DD Month YYYY]).",
                                style={
                                    "backgroundColor": "#f8f9fa",
                                    "padding": "1rem",
                                    "borderRadius": "0.25rem",
                                    "border": "1px solid #dee2e6",
                                    "fontFamily": "monospace",
                                    "fontSize": "0.9rem",
                                },
                            ),
                            html.Small(
                                [
                                    html.I(className="fas fa-lightbulb me-1"),
                                    "Replace placeholders with your access information",
                                ],
                                className="text-muted",
                            ),
                        ]
                    ),
                ],
                className="shadow-sm mb-4",
            ),
            # Database pre-DOI
            html.H4("BioRemPP Database (Provisional Citation)", className="mb-3"),
            dbc.Card(
                [
                    dbc.CardHeader(
                        "Recommended Format",
                        className="bg-light",
                    ),
                    dbc.CardBody(
                        [
                            html.Pre(
                                "[Author Names / Consortium]. BioRemPP Database (version [X.Y.Z]): "
                                "curated enzyme-compound associations for bioremediation research. "
                                "[Year]. License: CC BY 4.0. Available at: [https://biorempp.org/database] "
                                "(accessed [DD Month YYYY]).",
                                style={
                                    "backgroundColor": "#f8f9fa",
                                    "padding": "1rem",
                                    "borderRadius": "0.25rem",
                                    "border": "1px solid #dee2e6",
                                    "fontFamily": "monospace",
                                    "fontSize": "0.9rem",
                                },
                            ),
                            dbc.Alert(
                                [
                                    html.I(className="fas fa-code-branch me-2"),
                                    html.Strong("Version Tracking: "),
                                    "Always cite the specific database version used in your analysis "
                                    "(check footer or /version endpoint)",
                                ],
                                color="info",
                                className="mb-0 mt-3 text-dark",
                            ),
                        ]
                    ),
                ],
                className="shadow-sm mb-4",
            ),
        ],
        className="mb-5",
    )


def create_post_doi_section() -> html.Div:
    """
    Create section explaining post-DOI citation.

    Returns
    -------
    html.Div
        Post-DOI citation explanation section
    """
    return html.Div(
        [
            html.H2(
                [
                    html.I(className="fas fa-link me-2 text-success"),
                    "Citation After DOI Assignment",
                ],
                className="mb-4",
            ),
            dbc.Card(
                [
                    dbc.CardBody(
                        [
                            html.P(
                                [
                                    "Upon formal publication, both the BioRemPP Web Service and Database "
                                    "will be archived on ",
                                    html.Strong("Zenodo"),
                                    " with persistent ",
                                    html.Strong("DOIs"),
                                    ".",
                                ],
                                className="mb-3",
                            ),
                            html.H5("Key Points:", className="mb-3"),
                            html.Ul(
                                [
                                    html.Li([
                                        "Software and database will have ",
                                        html.Strong("separate DOIs"),
                                    ]),
                                    html.Li([
                                        "Cite the ",
                                        html.Strong("specific version"),
                                        " used in your analysis",
                                    ]),
                                    html.Li([
                                        "Update your manuscript references once DOIs are available",
                                    ]),
                                    html.Li([
                                        "DOI-based citations supersede provisional formats",
                                    ]),
                                ],
                                className="mb-0",
                            ),
                        ]
                    )
                ],
                className="shadow-sm",
            ),
        ],
        className="mb-5",
    )


def create_bibtex_section() -> html.Div:
    """
    Create BibTeX templates section.

    Returns
    -------
    html.Div
        BibTeX citation templates section
    """
    return html.Div(
        [
            html.H2(
                [
                    html.I(className="fas fa-code me-2 text-success"),
                    "BibTeX Templates",
                ],
                className="mb-4",
            ),
            # Web service BibTeX
            html.H4("Web Service BibTeX (Provisional)", className="mb-3"),
            dbc.Card(
                [
                    dbc.CardBody(
                        [
                            html.Pre(
                                "@misc{biorempp_web_[YEAR],\n"
                                "  author       = {[Author Names]},\n"
                                "  title        = {BioRemPP Web Service: Bioremediation Potential Profile},\n"
                                "  year         = {[YEAR]},\n"
                                "  howpublished = {\\url{https://biorempp.org}},\n"
                                "  note         = {Accessed: [DD-Month-YEAR]. Zenodo DOI pending}\n"
                                "}",
                                style={
                                    "backgroundColor": "#282c34",
                                    "color": "#abb2bf",
                                    "padding": "1.5rem",
                                    "borderRadius": "0.5rem",
                                    "fontFamily": "Consolas, Monaco, 'Courier New', monospace",
                                    "fontSize": "0.85rem",
                                    "overflowX": "auto",
                                },
                            ),
                        ]
                    )
                ],
                className="shadow-sm mb-4",
            ),
            # Database BibTeX
            html.H4("Database BibTeX (Provisional)", className="mb-3"),
            dbc.Card(
                [
                    dbc.CardBody(
                        [
                            html.Pre(
                                "@misc{biorempp_db_[YEAR],\n"
                                "  author       = {[Author Names]},\n"
                                "  title        = {BioRemPP Database: Curated enzyme-compound associations "
                                "for bioremediation research},\n"
                                "  year         = {[YEAR]},\n"
                                "  version      = {[X.Y.Z]},\n"
                                "  license      = {CC BY 4.0},\n"
                                "  howpublished = {\\url{https://biorempp.org/database}},\n"
                                "  note         = {Accessed: [DD-Month-YEAR]. Zenodo DOI pending}\n"
                                "}",
                                style={
                                    "backgroundColor": "#282c34",
                                    "color": "#abb2bf",
                                    "padding": "1.5rem",
                                    "borderRadius": "0.5rem",
                                    "fontFamily": "Consolas, Monaco, 'Courier New', monospace",
                                    "fontSize": "0.85rem",
                                    "overflowX": "auto",
                                },
                            ),
                        ]
                    )
                ],
                className="shadow-sm mb-4",
            ),
        ],
        className="mb-5",
    )


def create_third_party_section() -> html.Div:
    """
    Create third-party resources citation section.

    Returns
    -------
    html.Div
        Third-party citation requirements section
    """
    return html.Div(
        [
            html.H2(
                [
                    html.I(className="fas fa-link me-2 text-success"),
                    "Citation of Integrated Resources",
                ],
                className="mb-4",
            ),
            dbc.Alert(
                [
                    html.I(className="fas fa-exclamation-circle me-2"),
                    html.Strong("Important: "),
                    "BioRemPP integrates data from third-party resources. ",
                    html.Strong("Citing BioRemPP does NOT replace"),
                    " citation of the original data sources.",
                ],
                color="danger",
                className="mb-4 text-dark",
            ),
            dbc.Card(
                [
                    dbc.CardBody(
                        [
                            html.H5("Integrated Resources:", className="mb-3"),
                            html.Ul(
                                [
                                    html.Li([
                                        html.Strong("KEGG: "),
                                        html.A(
                                            "https://www.genome.jp/kegg/",
                                            href="https://www.genome.jp/kegg/",
                                            target="_blank",
                                        ),
                                        " - KEGG Orthology and pathway data",
                                    ]),
                                    html.Li([
                                        html.Strong("HADEG: "),
                                        html.A(
                                            "https://github.com/jarojasva/HADEG",
                                            href="https://github.com/jarojasva/HADEG",
                                            target="_blank",
                                        ),
                                        " - Hydrocarbon and xenobiotic degradation genes",
                                    ]),
                                    html.Li([
                                        html.Strong("toxCSM: "),
                                        html.A(
                                            "https://biosig.lab.uq.edu.au/toxcsm/",
                                            href="https://biosig.lab.uq.edu.au/toxcsm/",
                                            target="_blank",
                                        ),
                                        " - Computational toxicity predictions",
                                    ]),
                                ],
                                className="mb-3",
                            ),
                            html.P(
                                [
                                    "Please consult each resource's citation guidelines and cite them ",
                                    html.Strong("in addition to"),
                                    " BioRemPP when publishing your results.",
                                ],
                                className="mb-0 text-muted",
                            ),
                        ]
                    )
                ],
                className="shadow-sm",
            ),
        ],
        className="mb-5",
    )


def create_versioning_section() -> html.Div:
    """
    Create versioning and reproducibility section.

    Returns
    -------
    html.Div
        Versioning best practices section
    """
    return html.Div(
        [
            html.H2(
                [
                    html.I(className="fas fa-history me-2 text-success"),
                    "Versioning and Reproducibility",
                ],
                className="mb-4",
            ),
            dbc.Card(
                [
                    dbc.CardBody(
                        [
                            html.P(
                                [
                                    "Following ",
                                    html.A(
                                        "FAIR principles",
                                        href="https://www.go-fair.org/fair-principles/",
                                        target="_blank",
                                        className="fw-bold",
                                    ),
                                    " ensures your research is Findable, Accessible, "
                                    "Interoperable, and Reusable.",
                                ],
                                className="lead mb-3",
                            ),
                            html.Hr(),
                            html.H5("Best Practices:", className="mb-3"),
                            html.Ul(
                                [
                                    html.Li([
                                        html.Strong("Cite specific versions: "),
                                        "Always include the BioRemPP version number (e.g., v1.0.0)",
                                    ]),
                                    html.Li([
                                        html.Strong("Report access dates: "),
                                        "Databases evolve; specify when you accessed the service",
                                    ]),
                                    html.Li([
                                        html.Strong("Document database versions: "),
                                        "Note KEGG release, HADEG commit, and toxCSM version used",
                                    ]),
                                    html.Li([
                                        html.Strong("Archive input data: "),
                                        "Deposit your KO annotation files in repositories like Zenodo or OSF",
                                    ]),
                                    html.Li([
                                        html.Strong("Report parameters: "),
                                        "Document any custom filtering or analysis parameters used",
                                    ]),
                                ],
                                className="mb-0",
                            ),
                        ]
                    )
                ],
                className="shadow-sm",
            ),
        ],
        className="mb-5",
    )


def create_contact_section() -> html.Div:
    """
    Create questions and contact section.

    Returns
    -------
    html.Div
        Citation support contact section
    """
    return html.Div(
        [
            html.Hr(style={"margin": "3rem 0", "borderColor": "#dee2e6"}),
            dbc.Alert(
                [
                    html.I(className="fas fa-envelope me-2"),
                    html.Strong("Citation Questions? "),
                    "For clarification regarding citation practices or attribution requirements, "
                    "please contact the BioRemPP team via the institutional email listed on the ",
                    html.A("Contact page", href="/contact", className="alert-link"),
                    ".",
                ],
                color="info",
                className="text-center text-dark",
            ),
        ],
        className="mb-3",
    )


def create_how_to_cite_page() -> html.Div:
    """
    Create complete How to Cite page layout.

    Returns
    -------
    html.Div
        Complete citation guide page with all sections

    Examples
    --------
    >>> cite_layout = create_how_to_cite_page()

    Notes
    -----
    Sections included:
    1. Page header and title
    2. Why cite BioRemPP
    3. Citation overview (distinct artifacts)
    4. Pre-DOI citation templates
    5. Post-DOI explanation
    6. BibTeX templates
    7. Third-party resource citation
    8. Versioning and reproducibility
    9. Contact information
    """
    # Header
    header = create_header(show_nav=True, logo_size="60px")

    # Page title and intro
    page_intro = html.Div(
        [
            html.H1(
                [
                    html.I(className="fas fa-quote-right me-3 text-success"),
                    "How to Cite BioRemPP",
                ],
                className="text-center mb-3",
            ),
            html.P(
                "Citation guidelines for the BioRemPP web service and database",
                className="text-center text-muted mb-4 lead",
            ),
            html.Hr(),
        ],
        className="mb-5",
    )

    # Footer
    footer = create_footer(version="2.0.0", year=2024)

    # Assemble complete layout
    layout = html.Div(
        [
            header,
            dbc.Container(
                [
                    page_intro,
                    create_why_cite_section(),
                    create_citation_overview_section(),
                    create_pre_doi_section(),
                    create_post_doi_section(),
                    create_bibtex_section(),
                    create_third_party_section(),
                    create_versioning_section(),
                    create_contact_section(),
                ],
                fluid=False,
                className="px-4 py-4",
            ),
            footer,
        ],
        id="how-to-cite-page",
    )

    return layout


def get_layout() -> html.Div:
    """
    Get How to Cite page layout (alias for create_how_to_cite_page).

    Returns
    -------
    html.Div
        How to Cite page layout

    Notes
    -----
    This function is called by Dash when rendering the citation page.
    """
    return create_how_to_cite_page()
