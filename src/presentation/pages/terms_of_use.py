"""
Terms of Use Modal Component.

Provides legally conservative terms of use for BioRemPP scientific web service,
following best practices for open-access research platforms.
"""

import dash_bootstrap_components as dbc
from dash import html


def create_terms_button():
    """
    Create terms of use button with warning styling.

    Returns
    -------
    dbc.Card
        Card containing button to open terms modal
    """
    return dbc.Card(
        [
            dbc.CardBody(
                [
                    html.Div(
                        [
                            dbc.Button(
                                [
                                    html.I(className="fas fa-exclamation-triangle me-2"),
                                    "Terms of Use",
                                    html.I(className="fas fa-exclamation-triangle ms-2"),
                                ],
                                id="terms-btn",
                                color="warning",
                                size="lg",
                                className="shadow-sm",
                            )
                        ],
                        className="d-grid",
                    ),
                ]
            )
        ],
        className="shadow-sm mb-4",
    )


def create_terms_modal():
    """
    Create terms of use modal with comprehensive legal sections.

    Returns
    -------
    dbc.Modal
        Modal containing 11 terms of use sections
    """
    return dbc.Modal(
        [
            dbc.ModalHeader(
                [
                    html.I(className="fas fa-file-contract me-2"),
                    "BioRemPP Terms of Use",
                ],
                close_button=True,
            ),
            dbc.ModalBody(
                [
                    # Introduction
                    dbc.Alert(
                        [
                            html.I(className="fas fa-info-circle me-2"),
                            html.Strong("Important Notice: "),
                            "By using the BioRemPP web service, you acknowledge and agree "
                            "to the following terms. Please read carefully before proceeding.",
                        ],
                        color="warning",
                        className="mb-4",
                    ),
                    # Section 1: Scope and Purpose
                    html.Div(
                        [
                            html.H5(
                                [
                                    html.Span("1", className="badge bg-primary me-2"),
                                    "Scope and Purpose",
                                ],
                                className="mb-3",
                            ),
                            html.P(
                                [
                                    "BioRemPP (Bioremediation Potential Profile) is a ",
                                    html.Strong("scientific research tool"),
                                    " designed exclusively for exploratory functional analysis "
                                    "of bioremediation-related data. The platform integrates curated "
                                    "databases (BioRemPP, KEGG, HADEG, toxCSM) with regulatory frameworks "
                                    "to support hypothesis generation and methodological development in "
                                    "environmental bioinformatics.",
                                ],
                                className="text-muted mb-2",
                            ),
                            html.P(
                                [
                                    "BioRemPP is an ",
                                    html.Strong("academic web service"),
                                    " provided on a best-effort basis without performance guarantees "
                                    "or service level agreements.",
                                ],
                                className="text-muted mb-2",
                            ),
                        ]
                    ),
                    html.Hr(),
                    # Section 2: Intended Use
                    html.Div(
                        [
                            html.H5(
                                [
                                    html.Span("2", className="badge bg-success me-2"),
                                    "Intended Use",
                                ],
                                className="mb-3",
                            ),
                            html.P(
                                html.Strong("Permitted Uses:"),
                                className="mb-2",
                            ),
                            html.Ul(
                                [
                                    html.Li("Academic research and hypothesis generation"),
                                    html.Li("Educational purposes and training"),
                                    html.Li(
                                        "Exploratory analysis of functional genomic data"
                                    ),
                                    html.Li("Methodological development and validation"),
                                ],
                                className="text-muted mb-3",
                            ),
                            dbc.Alert(
                                [
                                    html.I(className="fas fa-ban me-2"),
                                    html.Strong("Prohibited Uses:"),
                                    html.Br(),
                                    "BioRemPP outputs must ",
                                    html.Strong("NOT"),
                                    " be used as the sole basis for:",
                                    html.Ul(
                                        [
                                            html.Li("Clinical diagnostics or medical decisions"),
                                            html.Li("Regulatory submissions or compliance"),
                                            html.Li(
                                                "Environmental remediation decisions without "
                                                "independent validation"
                                            ),
                                            html.Li(
                                                "Commercial product claims without experimental "
                                                "confirmation"
                                            ),
                                        ],
                                        className="mb-0 mt-2",
                                    ),
                                ],
                                color="danger",
                                className="mb-2",
                            ),
                        ]
                    ),
                    html.Hr(),
                    # Section 3: User Responsibilities
                    html.Div(
                        [
                            html.H5(
                                [
                                    html.Span("3", className="badge bg-info me-2"),
                                    "User Responsibilities",
                                ],
                                className="mb-3",
                            ),
                            html.P(
                                "Users are solely responsible for:",
                                className="mb-2",
                            ),
                            html.Ul(
                                [
                                    html.Li([
                                        html.Strong("Data ownership and legitimacy: "),
                                        "Ensuring uploaded data does not violate third-party "
                                        "rights or confidentiality agreements.",
                                    ]),
                                    html.Li([
                                        html.Strong("Scientific interpretation: "),
                                        "Results must be critically evaluated within appropriate "
                                        "biological and methodological context.",
                                    ]),
                                    html.Li([
                                        html.Strong("Citation and attribution: "),
                                        "Properly citing BioRemPP web service and database in "
                                        "publications and reports (see https://github.com/BioRemPP)",
                                    ]),
                                    html.Li([
                                        html.Strong("Compliance with third-party licenses: "),
                                        "Respecting KEGG, HADEG, and toxCSM licensing terms.",
                                    ]),
                                ],
                                className="text-muted mb-2",
                            ),
                        ]
                    ),
                    html.Hr(),
                    # Section 4: Data Submission and Privacy
                    html.Div(
                        [
                            html.H5(
                                [
                                    html.Span("4", className="badge bg-secondary me-2"),
                                    "Data Submission and Privacy",
                                ],
                                className="mb-3",
                            ),
                            html.P(
                                [
                                    "BioRemPP operates under a ",
                                    html.Strong("privacy-by-design philosophy"),
                                    ":",
                                ],
                                className="mb-2",
                            ),
                            html.Ul(
                                [
                                    html.Li([
                                        html.Strong("No user accounts: "),
                                        "The service requires no authentication or registration.",
                                    ]),
                                    html.Li([
                                        html.Strong("No persistent storage: "),
                                        "Uploaded data is processed in-memory only during the "
                                        "active session.",
                                    ]),
                                    html.Li([
                                        html.Strong("Session-based processing: "),
                                        "Data and results are automatically deleted when the "
                                        "browser session ends or after 6 hours of inactivity.",
                                    ]),
                                    html.Li([
                                        html.Strong("Minimal technical logging: "),
                                        "Server logs contain only IP addresses (rate limiting), "
                                        "user-agent strings (compatibility), and error messages "
                                        "(debugging). ",
                                        html.Strong("No biological data is logged."),
                                    ]),
                                ],
                                className="text-muted mb-2",
                            ),
                        ]
                    ),
                    html.Hr(),
                    # Section 5: Availability and Service Limitations
                    html.Div(
                        [
                            html.H5(
                                [
                                    html.Span("5", className="badge bg-warning me-2"),
                                    "Availability and Service Limitations",
                                ],
                                className="mb-3",
                            ),
                            html.P(
                                [
                                    "BioRemPP is provided as a ",
                                    html.Strong("best-effort service"),
                                    " without guaranteed uptime or performance commitments:",
                                ],
                                className="mb-2",
                            ),
                            html.Ul(
                                [
                                    html.Li([
                                        html.Strong("No Service Level Agreement (SLA): "),
                                        "Availability, response time, and throughput are not "
                                        "guaranteed.",
                                    ]),
                                    html.Li([
                                        html.Strong("Maintenance windows: "),
                                        "Service may be temporarily unavailable for updates, "
                                        "database refreshes, or infrastructure maintenance.",
                                    ]),
                                    html.Li([
                                        html.Strong("Resource constraints: "),
                                        "Upload limits (100 samples, 500K KO entries, 5 MB file "
                                        "size) are enforced to ensure fair access.",
                                    ]),
                                ],
                                className="text-muted mb-2",
                            ),
                            dbc.Alert(
                                [
                                    html.I(className="fas fa-envelope me-2"),
                                    html.Strong("Support and Custom SLA: "),
                                    "For institutional deployments, high-throughput analyses, "
                                    "or customized service agreements, contact ",
                                    html.A(
                                        "biorempp@gmail.com",
                                        href="mailto:biorempp@gmail.com",
                                        className="success-link",
                                    ),
                                    " with a detailed description of your requirements. "
                                    "Response time: up to 5 business days.",
                                ],
                                color="info",
                                className="mb-2",
                            ),
                        ]
                    ),
                    html.Hr(),
                    # Section 6: Licensing and Intellectual Property
                    html.Div(
                        [
                            html.H5(
                                [
                                    html.Span("6", className="badge bg-dark me-2"),
                                    "Licensing and Intellectual Property",
                                ],
                                className="mb-3",
                            ),
                            html.P(
                                html.Strong("BioRemPP Components:"),
                                className="mb-2",
                            ),
                            html.Ul(
                                [
                                    html.Li(
                                        [
                                            html.Strong("Web Service Source Code: "),
                                            html.A(
                                                "Apache License 2.0",
                                                href="https://opensource.org/licenses/Apache-2.0",
                                                target="_blank",
                                                className="text-decoration-none",
                                            ),
                                            " — Commercial and private use permitted with "
                                            "attribution.",
                                        ]
                                    ),
                                    html.Li(
                                        [
                                            html.Strong("BioRemPP Database Content: "),
                                            html.A(
                                                "CC BY 4.0",
                                                href="https://creativecommons.org/licenses/by/4.0/",
                                                target="_blank",
                                                className="text-decoration-none",
                                            ),
                                            " — Free to share and adapt with proper citation.",
                                        ]
                                    ),
                                ],
                                className="text-muted mb-3",
                            ),
                            html.P(
                                html.Strong("Third-Party Resources:"),
                                className="mb-2",
                            ),
                            html.Ul(
                                [
                                    html.Li(
                                        [
                                            html.Strong("KEGG: "),
                                            "Academic use free; commercial use requires license (",
                                            html.A(
                                                "KEGG License",
                                                href="https://www.kegg.jp/kegg/legal.html",
                                                target="_blank",
                                                className="text-decoration-none",
                                            ),
                                            ").",
                                        ]
                                    ),
                                    html.Li(
                                        [
                                            html.Strong("HADEG: "),
                                            "Open access (",
                                            html.A(
                                                "GitHub",
                                                href="https://github.com/jarojasva/HADEG",
                                                target="_blank",
                                                className="text-decoration-none",
                                            ),
                                            ").",
                                        ]
                                    ),
                                    html.Li(
                                        [
                                            html.Strong("toxCSM: "),
                                            "Open access for academic use (",
                                            html.A(
                                                "toxCSM License",
                                                href="https://biosig.lab.uq.edu.au/toxcsm/",
                                                target="_blank",
                                                className="text-decoration-none",
                                            ),
                                            ").",
                                        ]
                                    ),
                                ],
                                className="text-muted mb-2",
                            ),
                            dbc.Alert(
                                [
                                    html.I(className="fas fa-gavel me-2"),
                                    html.Strong("User Compliance Obligation: "),
                                    "Users are responsible for ensuring their use complies with "
                                    "all applicable third-party licenses.",
                                ],
                                color="warning",
                                className="mb-2",
                            ),
                        ]
                    ),
                    html.Hr(),
                    # Section 7: Citation and Attribution
                    html.Div(
                        [
                            html.H5(
                                [
                                    html.Span("7", className="badge bg-primary me-2"),
                                    "Citation and Attribution",
                                ],
                                className="mb-3",
                            ),
                            html.P(
                                [
                                    "Use of BioRemPP in academic publications, reports, or "
                                    "presentations ",
                                    html.Strong("requires proper citation"),
                                    " of both the web service and the BioRemPP database.",
                                ],
                                className="text-muted mb-2",
                            ),
                            html.P(
                                [
                                    "Please refer to the ",
                                    html.A(
                                        "How to Cite",
                                        href="/how-to-cite",
                                        className="fw-bold",
                                    ),
                                    " page for detailed citation guidelines, including provisional "
                                    "formats (pending DOI assignment via Zenodo) and recommended "
                                    "language for Methods sections.",
                                ],
                                className="text-muted mb-2",
                            ),
                        ]
                    ),
                    html.Hr(),
                    # Section 8: Disclaimer of Warranty
                    html.Div(
                        [
                            html.H5(
                                [
                                    html.Span("8", className="badge bg-danger me-2"),
                                    "Disclaimer of Warranty",
                                ],
                                className="mb-3",
                            ),
                            dbc.Alert(
                                [
                                    html.I(className="fas fa-exclamation-triangle me-2"),
                                    html.Strong('"AS IS" Provision: '),
                                    html.Br(),
                                    "BioRemPP is provided ",
                                    html.Strong('"as is" and "as available"'),
                                    " without warranty of any kind, either express or implied, "
                                    "including but not limited to warranties of merchantability, "
                                    "fitness for a particular purpose, or non-infringement.",
                                    html.Br(),
                                    html.Br(),
                                    "The authors and contributors make no representations regarding "
                                    "the accuracy, reliability, completeness, or timeliness of the "
                                    "service, database content, or analytical results.",
                                ],
                                color="danger",
                                className="mb-2",
                            ),
                        ]
                    ),
                    html.Hr(),
                    # Section 9: Limitation of Liability
                    html.Div(
                        [
                            html.H5(
                                [
                                    html.Span("9", className="badge bg-warning me-2"),
                                    "Limitation of Liability",
                                ],
                                className="mb-3",
                            ),
                            html.P(
                                [
                                    "The authors, contributors, and hosting institutions ",
                                    html.Strong("shall not be liable"),
                                    " for any direct, indirect, incidental, special, consequential, "
                                    "or exemplary damages arising from:",
                                ],
                                className="text-muted mb-2",
                            ),
                            html.Ul(
                                [
                                    html.Li("Use or inability to use the service"),
                                    html.Li(
                                        "Errors, omissions, or inaccuracies in results or database "
                                        "content"
                                    ),
                                    html.Li(
                                        "Decisions or actions taken based on service outputs"
                                    ),
                                    html.Li("Data loss or service interruptions"),
                                    html.Li(
                                        "Reliance on third-party database annotations (KEGG, HADEG, "
                                        "toxCSM)"
                                    ),
                                ],
                                className="text-muted mb-2",
                            ),
                            html.P(
                                [
                                    html.Strong("User Acknowledgment: "),
                                    "By using BioRemPP, you acknowledge that interpretation and "
                                    "application of results are solely your responsibility.",
                                ],
                                className="text-muted mb-2",
                            ),
                        ]
                    ),
                    html.Hr(),
                    # Section 10: Modifications to Terms
                    html.Div(
                        [
                            html.H5(
                                [
                                    html.Span("10", className="badge bg-secondary me-2"),
                                    "Modifications to the Terms",
                                ],
                                className="mb-3",
                            ),
                            html.P(
                                [
                                    "We reserve the right to modify these Terms of Use at any time. "
                                    "Changes will be posted on this page with an updated revision date.",
                                ],
                                className="text-muted mb-2",
                            ),
                            html.P(
                                [
                                    html.Strong("Continued use"),
                                    " of the service after modifications constitutes acceptance of "
                                    "the updated terms. Users are encouraged to review this page "
                                    "periodically.",
                                ],
                                className="text-muted mb-2",
                            ),
                        ]
                    ),
                    html.Hr(),
                    # Section 11: Contact Information
                    html.Div(
                        [
                            html.H5(
                                [
                                    html.Span("11", className="badge bg-info me-2"),
                                    "Contact Information",
                                ],
                                className="mb-3",
                            ),
                            html.P(
                                [
                                    "For questions, clarifications, or institutional support "
                                    "requests regarding these Terms of Use:",
                                ],
                                className="text-muted mb-2",
                            ),
                            html.Ul(
                                [
                                    html.Li(
                                        [
                                            html.Strong("Email: "),
                                            html.A(
                                                "biorempp@gmail.com",
                                                href="mailto:biorempp@gmail.com",
                                            ),
                                        ]
                                    ),
                                    html.Li(
                                        [
                                            html.Strong("GitHub Repository: "),
                                            html.A(
                                                "github.com/biorempp/biorempp_web",
                                                href="https://github.com/biorempp/biorempp_web",
                                                target="_blank",
                                            ),
                                        ]
                                    ),
                                    html.Li(
                                        [
                                            html.Strong("Response Time: "),
                                            "Up to 5 business days",
                                        ]
                                    ),
                                ],
                                className="text-muted mb-2",
                            ),
                        ]
                    ),
                    # Footer
                    html.Hr(),
                    dbc.Alert(
                        [
                            html.I(className="fas fa-check-circle me-2"),
                            html.Strong("Thank you for using BioRemPP responsibly. "),
                            "Your adherence to these terms ensures the continued availability "
                            "of this resource for the scientific community.",
                        ],
                        color="success",
                        className="mb-0",
                    ),
                ],
                style={"maxHeight": "70vh", "overflowY": "auto"},
            ),
            dbc.ModalFooter(
                [
                    dbc.Button(
                        "Close",
                        id="terms-close",
                        color="secondary",
                        outline=True,
                    )
                ]
            ),
        ],
        id="terms-modal",
        size="lg",
        centered=True,
        scrollable=True,
        is_open=False,
    )
