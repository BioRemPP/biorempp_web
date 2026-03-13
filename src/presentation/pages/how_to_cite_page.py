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
- Both Zenodo DOIs assigned: web service (zenodo.18919675) and database (zenodo.18905195)
- APA and BibTeX records for both software and database
- Third-party resource citation guidelines
"""

import dash_bootstrap_components as dbc
from dash import html

from ..components.base import create_footer, create_header
from ..routing import app_path


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


def create_post_doi_section() -> html.Div:
    """
    Create section with citation instructions and key points.

    Returns
    -------
    html.Div
        Citation instruction section
    """
    return html.Div(
        [
            html.H2(
                [
                    html.I(className="fas fa-clipboard-check me-2 text-success"),
                    "Citation Instructions",
                ],
                className="mb-4",
            ),
            dbc.Card(
                [
                    dbc.CardBody(
                        [
                            html.P(
                                [
                                    "Use the citation records below as the baseline for manuscripts, reports, "
                                    "and supplementary materials. Update author/year/version/access-date fields before submission. "
                                    "The database DOI is already assigned.",
                                ],
                                className="mb-3",
                            ),
                            html.H5("Key Points:", className="mb-3"),
                            html.Ul(
                                [
                                    html.Li([
                                        "Keep ",
                                        html.Strong("separate records"),
                                        " for the web service and the database",
                                    ]),
                                    html.Li([
                                        "Always include the ",
                                        html.Strong("specific version"),
                                        " used in your analysis",
                                    ]),
                                    html.Li([
                                        "Always include the ",
                                        html.Strong("access date"),
                                        " when citing the live web service",
                                    ]),
                                    html.Li([
                                        "Database DOI: ",
                                        html.Code("10.5281/zenodo.18905195"),
                                        " (Zenodo, CC BY 4.0)",
                                    ]),
                                    html.Li([
                                        "Web Service DOI: ",
                                        html.Code("10.5281/zenodo.18919675"),
                                        " (Zenodo, v1.0.0)",
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
    Create BibTeX citation section.

    Returns
    -------
    html.Div
        BibTeX citation section
    """
    return html.Div(
        [
            html.H2(
                [
                    html.I(className="fas fa-code me-2 text-success"),
                    "BibTeX Records",
                ],
                className="mb-4",
            ),
            # Web service citations
            html.H4("Web Service", className="mb-3"),
            html.H6("APA", className="text-muted mb-2"),
            dbc.Card(
                dbc.CardBody(
                    html.Pre(
                        "Lima Silva, D. F., & Fassarella Agnez-Lima, L. (2026). BioRemPP: A Compound-Centric\n"
                        "Web Server for Bioremediation Potential Profiling (1.0.0). Zenodo.\n"
                        "https://doi.org/10.5281/zenodo.18919675",
                        style={
                            "backgroundColor": "#282c34",
                            "color": "#abb2bf",
                            "padding": "1.5rem",
                            "borderRadius": "0.5rem",
                            "fontFamily": "Consolas, Monaco, 'Courier New', monospace",
                            "fontSize": "0.85rem",
                            "overflowX": "auto",
                            "whiteSpace": "pre-wrap",
                        },
                    )
                ),
                className="shadow-sm mb-3",
            ),
            html.H6("BibTeX", className="text-muted mb-2"),
            dbc.Card(
                dbc.CardBody(
                    html.Pre(
                        "@software{limasilva2026biorempp_web,\n"
                        "  author    = {Lima Silva, D. F. and Fassarella Agnez-Lima, L.},\n"
                        "  title     = {BioRemPP: A Compound-Centric Web Server for\n"
                        "               Bioremediation Potential Profiling},\n"
                        "  year      = {2026},\n"
                        "  publisher = {Zenodo},\n"
                        "  version   = {1.0.0},\n"
                        "  doi       = {10.5281/zenodo.18919675},\n"
                        "  url       = {https://doi.org/10.5281/zenodo.18919675}\n"
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
                    )
                ),
                className="shadow-sm mb-4",
            ),
            # Database citations
            html.H4("Database", className="mb-3"),
            html.H6("APA", className="text-muted mb-2"),
            dbc.Card(
                dbc.CardBody(
                    html.Pre(
                        "Lima Silva, D. F., & Fassarella Agnez-Lima, L. (2025\u20132026). BioRemPP Database:\n"
                        "A Curated Compound-Centric Resource for Bioremediation Potential Profiling (1.0.0)\n"
                        "[Data set]. Zenodo. https://doi.org/10.5281/zenodo.18905195",
                        style={
                            "backgroundColor": "#282c34",
                            "color": "#abb2bf",
                            "padding": "1.5rem",
                            "borderRadius": "0.5rem",
                            "fontFamily": "Consolas, Monaco, 'Courier New', monospace",
                            "fontSize": "0.85rem",
                            "overflowX": "auto",
                            "whiteSpace": "pre-wrap",
                        },
                    )
                ),
                className="shadow-sm mb-3",
            ),
            html.H6("BibTeX", className="text-muted mb-2"),
            dbc.Card(
                dbc.CardBody(
                    html.Pre(
                        "@dataset{limasilva2025biorempp_db,\n"
                        "  author    = {Lima Silva, D. F. and Fassarella Agnez-Lima, L.},\n"
                        "  title     = {BioRemPP Database: A Curated Compound-Centric Resource\n"
                        "               for Bioremediation Potential Profiling},\n"
                        "  year      = {2025},\n"
                        "  publisher = {Zenodo},\n"
                        "  version   = {1.0.0},\n"
                        "  doi       = {10.5281/zenodo.18905195},\n"
                        "  url       = {https://doi.org/10.5281/zenodo.18905195}\n"
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
                    )
                ),
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
                    html.A("Contact page", href=app_path("/contact"), className="alert-link"),
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
    4. Citation instructions and key points
    5. BibTeX records
    6. Third-party resource citation
    7. Versioning and reproducibility
    8. Contact information
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
    footer = create_footer()

    # Assemble complete layout
    layout = html.Div(
        [
            header,
            dbc.Container(
                [
                    page_intro,
                    create_why_cite_section(),
                    create_citation_overview_section(),
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
