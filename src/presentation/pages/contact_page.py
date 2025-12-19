"""
Contact Page - BioRemPP v1.0.

Help and contact information page with team details and laboratory info.

Functions
---------
create_contact_page
    Create complete contact page layout with team and lab information

Notes
-----
- Includes laboratory introduction
- Developer and supervisor profiles
- Contact methods and social media links
- Responsive Bootstrap design
"""

import dash_bootstrap_components as dbc
from dash import html

from ..components.base import create_footer, create_header


def create_team_card(
    name: str,
    role: str,
    description: str,
    image_path: str,
    additional_info: str = None,
    badge_text: str = None,
) -> dbc.Card:
    """
    Create team member profile card.

    Parameters
    ----------
    name : str
        Team member name
    role : str
        Professional role/title
    description : str
        Brief description of expertise
    image_path : str
        Path to profile image
    additional_info : str, optional
        Additional information (institution, department, etc.)
    badge_text : str, optional
        Badge text to display (e.g., "CNPq Research Fellow")

    Returns
    -------
    dbc.Card
        Styled profile card component

    Examples
    --------
    >>> card = create_team_card(
    ...     name="Dr. John Doe",
    ...     role="PhD Advisor",
    ...     description="Expert in bioinformatics...",
    ...     image_path="/assets/photo.jpg"
    ... )
    """
    card_content = [
        html.Div(
            className="team-photo-container",
            style={
                "position": "relative",
                "width": "100%",
                "paddingBottom": "75%",  # 4:3 aspect ratio (responsive)
                "overflow": "hidden",
                "backgroundColor": "#f8f9fa",
            },
            children=[
                html.Img(
                    src=image_path,
                    style={
                        "position": "absolute",
                        "top": "0",
                        "left": "0",
                        "width": "100%",
                        "height": "100%",
                        "objectFit": "cover",
                        "objectPosition": "center top",
                    },
                    alt=f"{name} profile photo",
                )
            ],
        ),
        dbc.CardBody(
            [
                html.H4(name, className="card-title text-center mb-2"),
                html.H6(role, className="text-muted text-center mb-3"),
                # Optional badge
                (
                    html.Div(
                        [dbc.Badge(badge_text, color="success", className="mb-3")],
                        className="text-center",
                    )
                    if badge_text
                    else html.Div()
                ),
                html.P(
                    description,
                    className="card-text text-justify",
                    style={"fontSize": "0.95rem"},
                ),
                # Additional info
                (
                    html.P(additional_info, className="text-muted small mt-3")
                    if additional_info
                    else html.Div()
                ),
            ]
        ),
    ]

    return dbc.Card(
        card_content,
        className="h-100 shadow-sm team-card",
        style={"border": "1px solid #e9ecef"},
    )


def create_lab_info_card() -> dbc.Card:
    """
    Create laboratory information card.

    Returns
    -------
    dbc.Card
        Styled card with laboratory details
    """
    return dbc.Card(
        [
            dbc.CardHeader(
                [
                    html.H4(
                        [
                            html.I(className="fas fa-flask me-2 text-success"),
                            "About LBMG",
                        ],
                        className="mb-0",
                    )
                ],
                className="bg-light",
            ),
            dbc.CardBody(
                [
                    dbc.Row(
                        [
                            dbc.Col(
                                [
                                    html.Img(
                                        src="/assets/lbmg_logo.png",
                                        style={
                                            "maxWidth": "100%",
                                            "height": "auto",
                                            "maxHeight": "200px",
                                        },
                                        alt="LBMG Logo",
                                        className="mb-3",
                                    )
                                ],
                                width=12,
                                md=4,
                                className="d-flex align-items-center justify-content-center",
                            ),
                            dbc.Col(
                                [
                                    html.H5(
                                        "Laboratory of Molecular Biology and Genomics (LBMG)",
                                        className="mb-3",
                                    ),
                                    html.P(
                                        [
                                            "The Laboratory of Molecular Biology and Genomics (LBMG) at the ",
                                            html.Strong(
                                                "Federal University of Rio Grande do Norte (UFRN)"
                                            ),
                                            " began its work in 1996 with the establishment of the research base in Genetics and Molecular Biology.",
                                        ],
                                        className="text-justify",
                                    ),
                                    html.P(
                                        [
                                            "In 2003, under the coordination of Professors ",
                                            html.Strong(
                                                "Lucymara Fassarella Agnez-Lima"
                                            ),
                                            " and ",
                                            html.Strong(
                                                "Silvia Regina Batistuzzo de Medeiros"
                                            ),
                                            ", a new laboratory was inaugurated, expanding its facilities.",
                                        ],
                                        className="text-justify",
                                    ),
                                    html.P(
                                        [
                                            "The lab is affiliated with the ",
                                            html.Strong(
                                                "Department of Cell Biology and Genetics"
                                            ),
                                            " at the ",
                                            html.Strong("Biosciences Center of UFRN"),
                                            ". Today, LBMG brings together approximately ",
                                            html.Strong(
                                                "70 undergraduate, master's, and doctoral students"
                                            ),
                                            ".",
                                        ],
                                        className="text-justify",
                                    ),
                                ],
                                width=12,
                                md=8,
                            ),
                        ]
                    )
                ]
            ),
        ],
        className="shadow-sm mb-4",
    )


def create_contact_methods() -> dbc.Card:
    """
    Create contact methods card with email and social media links.

    Returns
    -------
    dbc.Card
        Card with contact information
    """
    return dbc.Card(
        [
            dbc.CardHeader(
                [
                    html.H4(
                        [
                            html.I(className="fas fa-paper-plane me-2 text-success"),
                            "Get in Touch",
                        ],
                        className="mb-0",
                    )
                ],
                className="bg-light",
            ),
            dbc.CardBody(
                [
                    html.P(
                        "Feel free to reach out via email for collaboration or inquiries",
                        className="text-center mb-3",
                        style={"fontSize": "1.1rem"},
                    ),
                    # Email link
                    html.Div(
                        [
                            html.A(
                                "biorempp@gmail.com",
                                href="mailto:biorempp@gmail.com",
                                className="text-success",
                                style={
                                    "fontSize": "1.3rem",
                                    "fontWeight": "500",
                                    "textDecoration": "none",
                                },
                            )
                        ],
                        className="text-center mb-4",
                    ),
                    html.Hr(className="my-4"),
                    # Social Media Icons Section
                    html.H5("Connect on Social Media", className="text-center mb-4"),
                    html.Div(
                        [
                            # GitHub
                            html.A(
                                html.I(className="fab fa-github"),
                                href="https://github.com/BioRemPP",
                                target="_blank",
                                style={
                                    "color": "#24292e",
                                    "fontSize": "3rem",
                                    "margin": "0 1rem",
                                    "display": "inline-block",
                                    "transition": "all 0.3s ease",
                                },
                                title="GitHub - DougFelipe",
                            ),
                            # LinkedIn
                            html.A(
                                html.I(className="fab fa-linkedin"),
                                href="https://www.linkedin.com/in/douglas-feliipe/",
                                target="_blank",
                                style={
                                    "color": "#0077b5",
                                    "fontSize": "3rem",
                                    "margin": "0 1rem",
                                    "display": "inline-block",
                                    "transition": "all 0.3s ease",
                                },
                                title="LinkedIn - Douglas Felipe",
                            ),
                            # Instagram
                            html.A(
                                html.I(className="fab fa-instagram"),
                                href="https://www.instagram.com/pesquisadoug/",
                                target="_blank",
                                style={
                                    "color": "#E4405F",
                                    "fontSize": "3rem",
                                    "margin": "0 1rem",
                                    "display": "inline-block",
                                    "transition": "all 0.3s ease",
                                },
                                title="Instagram - @pesquisadoug",
                            ),
                            # Email Icon
                            html.A(
                                html.I(className="fas fa-envelope"),
                                href="mailto:biorempp@gmail.com",
                                target="_blank",
                                style={
                                    "color": "#28a745",
                                    "fontSize": "3rem",
                                    "margin": "0 1rem",
                                    "display": "inline-block",
                                    "transition": "all 0.3s ease",
                                },
                                title="Email - biorempp@gmail.com",
                            ),
                        ],
                        className="text-center",
                        style={"padding": "1rem 0"},
                    ),
                ]
            ),
        ],
        className="shadow-sm",
    )


def create_contact_page() -> html.Div:
    """
    Create contact page layout.

    Returns
    -------
    html.Div
        Complete contact page with all sections

    Examples
    --------
    >>> contact_layout = create_contact_page()

    Notes
    -----
    Sections included:
    1. Page header and title
    2. Laboratory information
    3. Team profiles (Developer and PhD Advisor)
    4. Contact methods and social media
    """
    # Header
    header = create_header(show_nav=True, logo_size="60px")

    # Page title and intro
    page_intro = html.Div(
        [
            html.H1(
                [html.I(className="fas fa-users me-3 text-success"), "Help & Contact"],
                className="text-center mb-3",
            ),
            html.P(
                "Learn more about our team and get in touch with us",
                className="text-center text-muted mb-4 lead",
            ),
            html.Hr(),
        ],
        className="mb-5",
    )

    # Laboratory Info Section
    lab_section = html.Div(
        [
            html.H2(
                [
                    html.I(className="fas fa-building me-2 text-success"),
                    "Our Laboratory",
                ],
                className="mb-4",
            ),
            create_lab_info_card(),
        ],
        className="mb-5",
    )

    # Team Section
    team_section = html.Div(
        [
            html.H2(
                [
                    html.I(className="fas fa-user-friends me-2 text-success"),
                    "Meet the Team",
                ],
                className="mb-4",
            ),
            dbc.Row(
                [
                    # Developer Card
                    dbc.Col(
                        [
                            create_team_card(
                                name="Douglas Felipe",
                                role="Biomedical Scientist, MSc. in Bioinformatics",
                                description=(
                                    "PhD student in Bioinformatics at UFRN, specializing in biotechnological "
                                    "solutions using microbiology to mitigate environmental pollution through "
                                    "bioremediation. Expertise in molecular biology, microbiology, bioinformatics, "
                                    "and software engineering with focus on Data Science, Artificial Intelligence, "
                                    "and Computational Intelligence for integrated data science and machine learning workflows."
                                ),
                                image_path="/assets/developer.jpeg",
                                additional_info="BioRemPP Developer",
                            )
                        ],
                        width=12,
                        md=6,
                        className="mb-4",
                    ),
                    # PhD Advisor Card
                    dbc.Col(
                        [
                            create_team_card(
                                name="Dr. Lucymara Fassarella Agnez-Lima",
                                role="Full Professor",
                                description=(
                                    "Full Professor at the Federal University of Rio Grande do Norte (UFRN). "
                                    "Holds a BSc in Biological Sciences from the Federal University of Espírito Santo, "
                                    "MSc and PhD in Biological Sciences (Biology/Genetics) from the University of São Paulo, "
                                    "and postdoctoral fellowship from the University of Barcelona. Permanent advisor in the "
                                    "graduate programs in Biochemistry, RENORBIO, and Bioinformatics, with research focused "
                                    "on genetics, molecular biology, biotechnology, and environmental genomics."
                                ),
                                image_path="/assets/supervisor.png",
                                additional_info="Department of Cell Biology and Genetics - UFRN",
                                badge_text="CNPq Research Fellow",
                            )
                        ],
                        width=12,
                        md=6,
                        className="mb-4",
                    ),
                ]
            ),
        ],
        className="mb-5",
    )

    # Contact Section
    contact_section = html.Div(
        [
            html.H2(
                [
                    html.I(className="fas fa-paper-plane me-2 text-success"),
                    "Contact Information",
                ],
                className="mb-4",
            ),
            create_contact_methods(),
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
                [page_intro, lab_section, team_section, contact_section],
                fluid=False,
                className="px-4 py-4",
            ),
            footer,
        ],
        id="contact-page",
    )

    return layout


def get_layout() -> html.Div:
    """
    Get contact page layout (alias for create_contact_page).

    Returns
    -------
    html.Div
        Contact page layout

    Notes
    -----
    This function is called by Dash when rendering the contact page.
    """
    return create_contact_page()
