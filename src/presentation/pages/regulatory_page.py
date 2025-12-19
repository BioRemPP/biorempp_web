"""
Regulatory Reference Page - BioRemPP v1.0.

Comprehensive information about regulatory agencies and environmental
frameworks used in BioRemPP.

Functions
---------
create_regulatory_page
    Create complete regulatory reference page layout

Notes
-----
- Documents all regulatory sources
- Explains priority pollutants
- Provides reference links
- Mobile responsive design
"""

import dash_bootstrap_components as dbc
from dash import html

from ..components.base import create_footer, create_header
from ..components.composite.regulatory_card import (
    create_info_alert,
    create_pollutant_category_card,
    create_reference_table,
    create_regulatory_card,
)


def create_regulatory_page() -> html.Div:
    """
    Create regulatory reference page layout.

    Returns
    -------
    html.Div
        Complete regulatory page with all sections

    Examples
    --------
    >>> regulatory_layout = create_regulatory_page()

    Notes
    -----
    Sections included:
    1. Introduction
    2. Priority Environmental Pollutants
    3. Regulatory Agencies
    4. Reference Table
    5. IARC Classifications
    """
    # Header
    header = create_header(show_nav=True, logo_size="60px")

    # ==================== Page Title Section ====================
    page_intro = html.Div(
        [
            html.H1(
                [
                    html.I(className="fas fa-balance-scale me-3 text-success"),
                    "Regulatory Reference",
                ],
                className="text-center mb-3",
            ),
            html.P(
                "Comprehensive information about environmental regulatory "
                "agencies and frameworks that guide BioRemPP's priority "
                "pollutant database.",
                className="text-center text-muted mb-4 lead",
            ),
            html.Hr(),
        ],
        className="mb-5",
    )

    # ==================== Introduction Section ====================
    introduction_section = html.Div(
        [
            dbc.Row(
                [
                    dbc.Col(
                        [
                            html.H2(
                                [
                                    html.I(
                                        className="fas fa-book-open me-2 text-success"
                                    ),
                                    "About BioRemPP Database",
                                ],
                                className="mb-4",
                            ),
                            html.P(
                                "BioRemPP provides a comprehensive database that includes "
                                "compounds identified as priority environmental pollutants. "
                                "These compounds are recognized by global regulatory "
                                "agencies or entities due to their environmental and human "
                                "health impacts.",
                                className="lead",
                            ),
                            html.P(
                                "Our database integrates information from multiple "
                                "authoritative sources to ensure comprehensive coverage "
                                "of priority pollutants across different regulatory "
                                "frameworks and geographical regions.",
                                className="mb-4",
                            ),
                            create_info_alert(
                                "All regulatory references were last reviewed and "
                                "updated on August 25, 2025.",
                                alert_type="info",
                                icon="fa-calendar-check",
                            ),
                        ],
                        md=12,
                    )
                ]
            )
        ],
        className="mb-5",
    )

    # ============ Priority Environmental Pollutants Section ============
    priority_pollutants_section = html.Div(
        [
            html.H2(
                [
                    html.I(className="fas fa-exclamation-triangle me-2 text-warning"),
                    "Priority Environmental Pollutants",
                ],
                className="mb-4",
            ),
            dbc.Row(
                [
                    dbc.Col(
                        [
                            html.P(
                                "Priority pollutants are compounds that pose significant "
                                "risks to environmental and human health. These substances "
                                "are targeted for monitoring and remediation efforts due "
                                "to their:",
                                className="mb-3",
                            ),
                            html.Ul(
                                [
                                    html.Li(
                                        [
                                            html.Strong("Persistence: "),
                                            "Resistance to degradation in the environment",
                                        ]
                                    ),
                                    html.Li(
                                        [
                                            html.Strong("Toxicity: "),
                                            "Harmful effects on living organisms and ecosystems",
                                        ]
                                    ),
                                    html.Li(
                                        [
                                            html.Strong("Bioaccumulation: "),
                                            "Tendency to accumulate in organisms and food chains",
                                        ]
                                    ),
                                    html.Li(
                                        [
                                            html.Strong("Mobility: "),
                                            "Capacity to spread through environmental media",
                                        ]
                                    ),
                                ],
                                className="mb-4",
                            ),
                        ],
                        md=12,
                    )
                ]
            ),
            # Pollutant Categories
            html.H4("Common Categories of Priority Pollutants", className="mb-3"),
            dbc.Row(
                [
                    dbc.Col(
                        [
                            create_pollutant_category_card(
                                category="Organic Compounds",
                                description="Persistent organic pollutants (POPs) including "
                                "polycyclic aromatic hydrocarbons (PAHs) and "
                                "polychlorinated biphenyls (PCBs).",
                                examples=[
                                    "Benzene, Toluene, Xylene (BTX)",
                                    "Polycyclic Aromatic Hydrocarbons",
                                    "Chlorinated Solvents",
                                    "Petroleum Hydrocarbons",
                                ],
                                icon="fa-oil-can",
                            )
                        ],
                        md=6,
                        className="mb-4",
                    ),
                    dbc.Col(
                        [
                            create_pollutant_category_card(
                                category="Heavy Metals",
                                description="Toxic metallic elements that persist in the "
                                "environment and accumulate in living organisms.",
                                examples=[
                                    "Lead (Pb)",
                                    "Mercury (Hg)",
                                    "Cadmium (Cd)",
                                    "Chromium (Cr)",
                                ],
                                icon="fa-atom",
                            )
                        ],
                        md=6,
                        className="mb-4",
                    ),
                    dbc.Col(
                        [
                            create_pollutant_category_card(
                                category="Pesticides",
                                description="Agricultural and industrial chemicals designed "
                                "to control pests but with environmental impacts.",
                                examples=[
                                    "Organophosphates",
                                    "Organochlorines",
                                    "Herbicides",
                                    "Fungicides",
                                ],
                                icon="fa-seedling",
                            )
                        ],
                        md=6,
                        className="mb-4",
                    ),
                    dbc.Col(
                        [
                            create_pollutant_category_card(
                                category="Industrial Chemicals",
                                description="Synthetic compounds used in manufacturing "
                                "processes with potential environmental hazards.",
                                examples=[
                                    "Phthalates",
                                    "Dioxins and Furans",
                                    "Brominated Flame Retardants",
                                    "Per- and Polyfluoroalkyl Substances (PFAS)",
                                ],
                                icon="fa-industry",
                            )
                        ],
                        md=6,
                        className="mb-4",
                    ),
                ]
            ),
        ],
        className="mb-5",
    )

    # ================ Regulatory Agencies Section ==================
    regulatory_agencies_section = html.Div(
        [
            html.H2(
                [
                    html.I(className="fas fa-landmark me-2 text-primary"),
                    "Key Environmental Regulatory Agencies",
                ],
                className="mb-4",
            ),
            html.P(
                "BioRemPP integrates priority pollutant lists from leading "
                "international regulatory agencies and environmental frameworks:",
                className="lead mb-4",
            ),
            dbc.Row(
                [
                    # ATSDR
                    dbc.Col(
                        [
                            create_regulatory_card(
                                title="Agency for Toxic Substances and Disease Registry",
                                acronym="ATSDR",
                                description="The ATSDR identifies hazardous substances and "
                                "assesses their health effects. Its priority "
                                "substance list guides environmental cleanup and "
                                "regulatory actions in the USA.",
                                country="USA",
                                icon="fa-hospital",
                                color="primary",
                            )
                        ],
                        lg=4,
                        md=6,
                        className="mb-4",
                    ),
                    # CONAMA
                    dbc.Col(
                        [
                            create_regulatory_card(
                                title="National Environmental Council",
                                acronym="CONAMA",
                                description="CONAMA establishes guidelines for pollution "
                                "control, water quality, and the regulation of "
                                "hazardous substances in Brazil. It prioritizes "
                                "pollutants based on environmental impact and "
                                "public health risks.",
                                country="Brazil",
                                icon="fa-flag",
                                color="success",
                            )
                        ],
                        lg=4,
                        md=6,
                        className="mb-4",
                    ),
                    # EPA
                    dbc.Col(
                        [
                            create_regulatory_card(
                                title="Environmental Protection Agency",
                                acronym="US EPA",
                                description="The EPA regulates pollutants through programs "
                                "like the National Priority List and CERCLA "
                                "(Superfund), focusing on mitigating environmental "
                                "contamination and promoting sustainability.",
                                country="USA",
                                icon="fa-shield-alt",
                                color="info",
                            )
                        ],
                        lg=4,
                        md=6,
                        className="mb-4",
                    ),
                    # European Parliament
                    dbc.Col(
                        [
                            create_regulatory_card(
                                title="European Parliament",
                                acronym="EP",
                                description="The EP enforces directives like the REACH "
                                "regulation and the Water Framework Directive, "
                                "which aim to protect the environment and human "
                                "health by monitoring and regulating pollutants "
                                "across Europe.",
                                country="European Union",
                                icon="fa-euro-sign",
                                color="warning",
                            )
                        ],
                        lg=4,
                        md=6,
                        className="mb-4",
                    ),
                    # IARC
                    dbc.Col(
                        [
                            create_regulatory_card(
                                title="International Agency for Research on Cancer",
                                acronym="IARC",
                                description="The IARC classifies compounds based on their "
                                "carcinogenic potential (Groups 1, 2A, and 2B). "
                                "This classification informs regulatory actions "
                                "and prioritization for monitoring.",
                                country="International (WHO)",
                                icon="fa-globe",
                                color="danger",
                            )
                        ],
                        lg=4,
                        md=6,
                        className="mb-4",
                    ),
                    # CEPA
                    dbc.Col(
                        [
                            create_regulatory_card(
                                title="Canadian Environmental Protection Act",
                                acronym="CEPA",
                                description="The CEPA prioritizes substances based on their "
                                "toxicity, persistence, and bioaccumulation. "
                                "PSL1 and PSL2 guide environmental management "
                                "actions in Canada.",
                                country="Canada",
                                icon="fa-maple-leaf",
                                color="secondary",
                            )
                        ],
                        lg=4,
                        md=6,
                        className="mb-4",
                    ),
                ]
            ),
        ],
        className="mb-5",
    )

    # ============= Water Framework Directive Section ================
    wfd_section = html.Div(
        [
            dbc.Card(
                [
                    dbc.CardBody(
                        [
                            html.H4(
                                [
                                    html.I(className="fas fa-tint me-2 text-info"),
                                    "Water Framework Directive (WFD)",
                                ],
                                className="mb-3",
                            ),
                            html.P(
                                "The Water Framework Directive (2000/60/EC) is a key "
                                "European Union directive that aims to achieve good "
                                "water quality in surface and groundwater across Europe.",
                                className="mb-3",
                            ),
                            html.P(
                                [
                                    html.Strong("Key Objectives:"),
                                ]
                            ),
                            html.Ul(
                                [
                                    html.Li(
                                        "Prevent deterioration of aquatic ecosystems"
                                    ),
                                    html.Li("Promote sustainable water use"),
                                    html.Li("Reduce pollution of priority substances"),
                                    html.Li(
                                        "Ensure progressive reduction of priority hazardous "
                                        "substances"
                                    ),
                                ]
                            ),
                            html.P(
                                "The WFD provides a comprehensive framework for monitoring "
                                "and remediation efforts, targeting priority pollutants "
                                "that pose risks to aquatic environments.",
                                className="mb-0",
                            ),
                        ]
                    )
                ],
                className="shadow-sm border-info border-start border-5",
            )
        ],
        className="mb-5",
    )

    # =============== IARC Classification Section ===================
    iarc_section = html.Div(
        [
            html.H3(
                [
                    html.I(className="fas fa-microscope me-2 text-danger"),
                    "IARC Carcinogenicity Classifications",
                ],
                className="mb-4",
            ),
            html.P(
                "The International Agency for Research on Cancer (IARC) "
                "classifies compounds into groups based on the strength of "
                "evidence for their carcinogenic potential:",
                className="mb-3",
            ),
            dbc.Row(
                [
                    dbc.Col(
                        [
                            dbc.Card(
                                [
                                    dbc.CardHeader(
                                        html.H5("Group 1", className="mb-0 text-white"),
                                        className="bg-danger",
                                    ),
                                    dbc.CardBody(
                                        [
                                            html.P(
                                                [
                                                    html.Strong(
                                                        "Carcinogenic to humans"
                                                    ),
                                                    html.Br(),
                                                    "Sufficient evidence of carcinogenicity in humans.",
                                                ],
                                                className="mb-0",
                                            )
                                        ]
                                    ),
                                ],
                                className="mb-3",
                            )
                        ],
                        md=4,
                    ),
                    dbc.Col(
                        [
                            dbc.Card(
                                [
                                    dbc.CardHeader(
                                        html.H5(
                                            "Group 2A", className="mb-0 text-white"
                                        ),
                                        className="bg-warning",
                                    ),
                                    dbc.CardBody(
                                        [
                                            html.P(
                                                [
                                                    html.Strong(
                                                        "Probably carcinogenic to humans"
                                                    ),
                                                    html.Br(),
                                                    "Limited evidence in humans, sufficient evidence "
                                                    "in experimental animals.",
                                                ],
                                                className="mb-0",
                                            )
                                        ]
                                    ),
                                ],
                                className="mb-3",
                            )
                        ],
                        md=4,
                    ),
                    dbc.Col(
                        [
                            dbc.Card(
                                [
                                    dbc.CardHeader(
                                        html.H5(
                                            "Group 2B", className="mb-0 text-white"
                                        ),
                                        className="bg-info",
                                    ),
                                    dbc.CardBody(
                                        [
                                            html.P(
                                                [
                                                    html.Strong(
                                                        "Possibly carcinogenic to humans"
                                                    ),
                                                    html.Br(),
                                                    "Limited evidence in humans, less than sufficient "
                                                    "evidence in experimental animals.",
                                                ],
                                                className="mb-0",
                                            )
                                        ]
                                    ),
                                ],
                                className="mb-3",
                            )
                        ],
                        md=4,
                    ),
                ]
            ),
        ],
        className="mb-5",
    )

    # ================= Reference Table Section =====================
    reference_section = html.Div(
        [
            html.H2(
                [
                    html.I(className="fas fa-link me-2 text-success"),
                    "Regulatory Sources and References",
                ],
                className="mb-4",
            ),
            html.P(
                "The following table provides direct links to all regulatory "
                "sources used to compile the BioRemPP priority pollutant database:",
                className="mb-3",
            ),
            dbc.Card(
                [
                    dbc.CardBody(
                        [
                            create_reference_table(
                                [
                                    {
                                        "agency": "ATSDR — Substance Priority List",
                                        "url": "https://www.atsdr.cdc.gov/programs/substance-priority-list.html?CDC_AAref_Val=https://www.atsdr.cdc.gov/spl/index.html",
                                    },
                                    {
                                        "agency": "CEPA — Priority Substances Lists (PSL1 & PSL2)",
                                        "url": "https://www.canada.ca/en/environment-climate-change/services/canadian-environmental-protection-act-registry/substances-list",
                                    },
                                    {
                                        "agency": "US EPA — National Priorities List (CERCLA/Superfund)",
                                        "url": "https://www.epa.gov/superfund/superfund-national-priorities-list-npl",
                                    },
                                    {
                                        "agency": "IARC — Carcinogenicity Classifications",
                                        "url": "https://monographs.iarc.who.int/list-of-classifications/",
                                    },
                                    {
                                        "agency": "CONAMA — Brazilian Environmental Regulations",
                                        "url": "https://conama.mma.gov.br/",
                                    },
                                    {
                                        "agency": "EU — Water Framework Directive (2000/60/EC)",
                                        "url": "https://eur-lex.europa.eu/eli/dir/2000/60/oj",
                                    },
                                ]
                            ),
                            html.Small(
                                "All links were last reviewed and verified on December, 2025.",
                                className="text-muted mt-3 d-block",
                            ),
                        ]
                    )
                ],
                className="shadow-sm",
            ),
        ],
        className="mb-5",
    )

    # Footer
    footer = create_footer(version="1.0.0", year=2025)

    # =================== Assemble Layout ===========================
    layout = html.Div(
        [
            header,
            dbc.Container(
                [
                    page_intro,
                    introduction_section,
                    priority_pollutants_section,
                    regulatory_agencies_section,
                    wfd_section,
                    iarc_section,
                    reference_section,
                ],
                fluid=False,
                className="px-4 py-4",
            ),
            footer,
        ],
        id="regulatory-page",
    )

    return layout
