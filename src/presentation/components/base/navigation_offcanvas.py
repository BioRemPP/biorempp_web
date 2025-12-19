"""
Navigation Offcanvas Component - BioRemPP v1.0
===============================================

Offcanvas navigation panel with hierarchical module and use case navigation.

Functions
---------
create_navigation_offcanvas
    Create offcanvas panel with navigation tree for all modules

Notes
-----
- Right-to-left slide animation
- Scrollable content for long lists
- Hierarchical structure: Modules → Use Cases
- Bootstrap ListGroup components
- 350px width for comfortable reading
"""

import dash_bootstrap_components as dbc
from dash import html


def create_navigation_offcanvas() -> dbc.Offcanvas:
    """
    Create navigation offcanvas panel.

    Returns
    -------
    dbc.Offcanvas
        Offcanvas component with complete navigation tree

    Notes
    -----
    Navigation Structure:
    - Database Tables (4 sections)
    - Module 1: Comparative Assessment (overview only)
    - Module 2: Exploratory Analysis (5 use cases)
    - Modules 3-8: Overview navigation (UCs pending implementation)

    Component Properties:
    - ID: 'navigation-offcanvas'
    - Placement: end (right-to-left)
    - Width: 350px
    - Scrollable: True
    - Initial state: Closed

    Interaction:
    - Opens via navigation button click
    - List items trigger scroll navigation
    - Stays open until manually closed (X button or ESC key)
    - Button auto-hides when offcanvas is open (via CSS)

    Examples
    --------
    >>> offcanvas = create_navigation_offcanvas()
    >>> # Add to results page layout

    See Also
    --------
    create_navigation_button : Floating button component
    navigation_callbacks : Navigation interaction callbacks
    """
    navigation_content = [
        html.H5("Navigation", className="mb-4 fw-bold text-primary"),
        # ========================================
        # Database Tables Section
        # ========================================
        html.Div(
            [
                html.H6(
                    [html.I(className="fas fa-database me-2"), "Database Tables"],
                    className="mb-2 text-muted",
                ),
                dbc.ListGroup(
                    [
                        dbc.ListGroupItem(
                            [html.I(className="fas fa-table me-2"), "BioRemPP Results"],
                            id="nav-biorempp",
                            action=True,
                            className="border-0 py-2",
                            href="#biorempp-section",
                        ),
                        dbc.ListGroupItem(
                            [html.I(className="fas fa-table me-2"), "HADEG Database"],
                            id="nav-hadeg",
                            action=True,
                            className="border-0 py-2",
                            href="#hadeg-section",
                        ),
                        dbc.ListGroupItem(
                            [html.I(className="fas fa-table me-2"), "ToxCSM Database"],
                            id="nav-toxcsm",
                            action=True,
                            className="border-0 py-2",
                            href="#toxcsm-section",
                        ),
                        dbc.ListGroupItem(
                            [html.I(className="fas fa-table me-2"), "KEGG Pathways"],
                            id="nav-kegg",
                            action=True,
                            className="border-0 py-2",
                            href="#kegg-section",
                        ),
                    ],
                    flush=True,
                    className="mb-4",
                ),
            ]
        ),
        # ========================================
        # Module 1: Comparative Assessment
        # ========================================
        html.Div(
            [
                html.H6(
                    "Module 1: Comparative Assessment", className="mb-2 text-muted"
                ),
                dbc.ListGroup(
                    [
                        dbc.ListGroupItem(
                            [html.I(className="fas fa-book-open me-2"), "Overview"],
                            id="nav-module1",
                            action=True,
                            className="border-0 py-2",
                            href="#module1-section",
                        ),
                        dbc.ListGroupItem(
                            "UC-1.1: Database Overlap",
                            id="nav-uc-1-1",
                            action=True,
                            className="border-0 py-2 ps-4",
                            href="#uc-1-1-card",
                        ),
                        dbc.ListGroupItem(
                            "UC-1.2: Agency Overlap",
                            id="nav-uc-1-2",
                            action=True,
                            className="border-0 py-2 ps-4",
                            href="#uc-1-2-card",
                        ),
                        dbc.ListGroupItem(
                            "UC-1.3: Reference Contribution",
                            id="nav-uc-1-3",
                            action=True,
                            className="border-0 py-2 ps-4",
                            href="#uc-1-3-card",
                        ),
                        dbc.ListGroupItem(
                            "UC-1.4: Sample Diversity",
                            id="nav-uc-1-4",
                            action=True,
                            className="border-0 py-2 ps-4",
                            href="#uc-1-4-card",
                        ),
                        dbc.ListGroupItem(
                            "UC-1.5: Compliance Scorecard",
                            id="nav-uc-1-5",
                            action=True,
                            className="border-0 py-2 ps-4",
                            href="#uc-1-5-card",
                        ),
                        dbc.ListGroupItem(
                            "UC-1.6: Functional Heatmap",
                            id="nav-uc-1-6",
                            action=True,
                            className="border-0 py-2 ps-4",
                            href="#uc-1-6-card",
                        ),
                    ],
                    flush=True,
                    className="mb-4",
                ),
            ]
        ),
        # ========================================
        # Module 2: Exploratory Analysis
        # ========================================
        html.Div(
            [
                html.H6("Module 2: Exploratory Analysis", className="mb-2 text-muted"),
                dbc.ListGroup(
                    [
                        dbc.ListGroupItem(
                            [html.I(className="fas fa-book-open me-2"), "Overview"],
                            id="nav-module2",
                            action=True,
                            className="border-0 py-2",
                            href="#module2-section",
                        ),
                        dbc.ListGroupItem(
                            "UC-2.1: KO Richness",
                            id="nav-uc-2-1",
                            action=True,
                            className="border-0 py-2 ps-4",
                            href="#uc-2-1-card",
                        ),
                        dbc.ListGroupItem(
                            "UC-2.2: Compound Richness",
                            id="nav-uc-2-2",
                            action=True,
                            className="border-0 py-2 ps-4",
                            href="#uc-2-2-card",
                        ),
                        dbc.ListGroupItem(
                            "UC-2.3: Sample Diversity",
                            id="nav-uc-2-3",
                            action=True,
                            className="border-0 py-2 ps-4",
                            href="#uc-2-3-card",
                        ),
                        dbc.ListGroupItem(
                            "UC-2.4: Genetic Interaction",
                            id="nav-uc-2-4",
                            action=True,
                            className="border-0 py-2 ps-4",
                            href="#uc-2-4-card",
                        ),
                        dbc.ListGroupItem(
                            "UC-2.5: KO Distribution",
                            id="nav-uc-2-5",
                            action=True,
                            className="border-0 py-2 ps-4",
                            href="#uc-2-5-card",
                        ),
                    ],
                    flush=True,
                    className="mb-4",
                ),
            ]
        ),
        # ========================================
        # Module 3: System Structure
        # ========================================
        html.Div(
            [
                html.H6("Module 3: System Structure", className="mb-2 text-muted"),
                dbc.ListGroup(
                    [
                        dbc.ListGroupItem(
                            [html.I(className="fas fa-book-open me-2"), "Overview"],
                            id="nav-module3",
                            action=True,
                            className="border-0 py-2",
                            href="#module3-section",
                        ),
                        dbc.ListGroupItem(
                            "UC-3.1: Sample Relationships by KO (PCA)",
                            id="nav-uc-3-1",
                            action=True,
                            className="border-0 py-2 ps-4",
                            href="#uc-3-1-card",
                        ),
                        dbc.ListGroupItem(
                            "UC-3.2: Sample Relationships by Chemical (PCA)",
                            id="nav-uc-3-2",
                            action=True,
                            className="border-0 py-2 ps-4",
                            href="#uc-3-2-card",
                        ),
                        dbc.ListGroupItem(
                            "UC-3.4: Sample Similarity (KO)",
                            id="nav-uc-3-4",
                            action=True,
                            className="border-0 py-2 ps-4",
                            href="#uc-3-4-card",
                        ),
                        dbc.ListGroupItem(
                            "UC-3.5: Sample Similarity (Chem)",
                            id="nav-uc-3-5",
                            action=True,
                            className="border-0 py-2 ps-4",
                            href="#uc-3-5-card",
                        ),
                        dbc.ListGroupItem(
                            "UC-3.6: Gene Co-occurrence",
                            id="nav-uc-3-6",
                            action=True,
                            className="border-0 py-2 ps-4",
                            href="#uc-3-6-card",
                        ),
                        dbc.ListGroupItem(
                            "UC-3.7: Compound Co-occurrence",
                            id="nav-uc-3-7",
                            action=True,
                            className="border-0 py-2 ps-4",
                            href="#uc-3-7-card",
                        ),
                    ],
                    flush=True,
                    className="mb-4",
                ),
            ]
        ),
        # ========================================
        # Module 4: Functional Profiling
        # ========================================
        html.Div(
            [
                html.H6(
                    [html.I(className="fas me-2"), "Module 4: Functional Profiling"],
                    className="mb-2 text-muted",
                ),
                dbc.ListGroup(
                    [
                        dbc.ListGroupItem(
                            [html.I(className="fas fa-book-open me-2"), "Overview"],
                            id="nav-module4",
                            action=True,
                            className="border-0 py-2",
                            href="#module4-section",
                        ),
                        dbc.ListGroupItem(
                            "UC-4.1: Functional Profiling by Pathway",
                            id="nav-uc-4-1",
                            action=True,
                            className="border-0 py-2 ps-4",
                            href="#uc-4-1-card",
                        ),
                        dbc.ListGroupItem(
                            "UC-4.2: Sample Ranking by Pathway Richness",
                            id="nav-uc-4-2",
                            action=True,
                            className="border-0 py-2 ps-4",
                            href="#uc-4-2-card",
                        ),
                        dbc.ListGroupItem(
                            "UC-4.3: Sample Comparison by Pathway",
                            id="nav-uc-4-3",
                            action=True,
                            className="border-0 py-2 ps-4",
                            href="#uc-4-3-card",
                        ),
                        dbc.ListGroupItem(
                            "UC-4.4: Functional Fingerprint by Sample",
                            id="nav-uc-4-4",
                            action=True,
                            className="border-0 py-2 ps-4",
                            href="#uc-4-4-card",
                        ),
                        dbc.ListGroupItem(
                            "UC-4.5: Gene Presence Map by Pathway",
                            id="nav-uc-4-5",
                            action=True,
                            className="border-0 py-2 ps-4",
                            href="#uc-4-5-card",
                        ),
                        dbc.ListGroupItem(
                            "UC-4.6: Functional Potential by Compound",
                            id="nav-uc-4-6",
                            action=True,
                            className="border-0 py-2 ps-4",
                            href="#uc-4-6-card",
                        ),
                        dbc.ListGroupItem(
                            "UC-4.7: Gene-Compound Association Explorer",
                            id="nav-uc-4-7",
                            action=True,
                            className="border-0 py-2 ps-4",
                            href="#uc-4-7-card",
                        ),
                        dbc.ListGroupItem(
                            "UC-4.8: Gene Inventory Explorer by Sample",
                            id="nav-uc-4-8",
                            action=True,
                            className="border-0 py-2 ps-4",
                            href="#uc-4-8-card",
                        ),
                        dbc.ListGroupItem(
                            "UC-4.9: Enzymatic Activity Profiling",
                            id="nav-uc-4-9",
                            action=True,
                            className="border-0 py-2 ps-4",
                            href="#uc-4-9-card",
                        ),
                        dbc.ListGroupItem(
                            "UC-4.10: Genetic Diversity by Enzyme Activity",
                            id="nav-uc-4-10",
                            action=True,
                            className="border-0 py-2 ps-4",
                            href="#uc-4-10-card",
                        ),
                        dbc.ListGroupItem(
                            "UC-4.11: Global Genetic Diversity Hierarchy",
                            id="nav-uc-4-11",
                            action=True,
                            className="border-0 py-2 ps-4",
                            href="#uc-4-11-card",
                        ),
                        dbc.ListGroupItem(
                            "UC-4.12: Pathway Relationships by Sample",
                            id="nav-uc-4-12",
                            action=True,
                            className="border-0 py-2 ps-4",
                            href="#uc-4-12-card",
                        ),
                        dbc.ListGroupItem(
                            "UC-4.13: Genetic Profile by Compound Pathway",
                            id="nav-uc-4-13",
                            action=True,
                            className="border-0 py-2 ps-4",
                            href="#uc-4-13-card",
                        ),
                    ],
                    flush=True,
                    className="mb-4",
                ),
            ]
        ),
        # ========================================
        # Module 5: Interaction Modeling
        # ========================================
        html.Div(
            [
                html.H6("Module 5: Interaction Modeling", className="mb-2 text-muted"),
                dbc.ListGroup(
                    [
                        dbc.ListGroupItem(
                            [html.I(className="fas fa-book-open me-2"), "Overview"],
                            id="nav-module5",
                            action=True,
                            className="border-0 py-2",
                            href="#module5-section",
                        ),
                        dbc.ListGroupItem(
                            "UC-5.1: Sample-Compound Interaction Strength",
                            id="nav-uc-5-1",
                            action=True,
                            className="border-0 py-2 ps-4",
                            href="#uc-5-1-card",
                        ),
                        dbc.ListGroupItem(
                            "UC-5.2: Sample Similarity via Shared Compounds",
                            id="nav-uc-5-2",
                            action=True,
                            className="border-0 py-2 ps-4",
                            href="#uc-5-2-card",
                        ),
                        dbc.ListGroupItem(
                            "UC-5.3: Regulatory Relevance of Samples",
                            id="nav-uc-5-3",
                            action=True,
                            className="border-0 py-2 ps-4",
                            href="#uc-5-3-card",
                        ),
                        dbc.ListGroupItem(
                            "UC-5.4: Gene-Compound Interaction Network",
                            id="nav-uc-5-4",
                            action=True,
                            className="border-0 py-2 ps-4",
                            href="#uc-5-4-card",
                        ),
                        dbc.ListGroupItem(
                            "UC-5.5: Gene-Gene Functional Interaction",
                            id="nav-uc-5-5",
                            action=True,
                            className="border-0 py-2 ps-4",
                            href="#uc-5-5-card",
                        ),
                        dbc.ListGroupItem(
                            "UC-5.6: Compound-Compound Similarity Network",
                            id="nav-uc-5-6",
                            action=True,
                            className="border-0 py-2 ps-4",
                            href="#uc-5-6-card",
                        ),
                    ],
                    flush=True,
                    className="mb-4",
                ),
            ]
        ),
        # ========================================
        # Module 6: Hierarchical Analysis
        # ========================================
        html.Div(
            [
                html.H6("Module 6: Hierarchical Analysis", className="mb-2 text-muted"),
                dbc.ListGroup(
                    [
                        dbc.ListGroupItem(
                            [html.I(className="fas fa-book-open me-2"), "Overview"],
                            id="nav-module6",
                            action=True,
                            className="border-0 py-2",
                            href="#module6-section",
                        ),
                        dbc.ListGroupItem(
                            "UC-6.1: Regulatory to Molecular Flow",
                            id="nav-uc-6-1",
                            action=True,
                            className="border-0 py-2 ps-4",
                            href="#uc-6-1-card",
                        ),
                        dbc.ListGroupItem(
                            "UC-6.2: Biological Interaction Flow",
                            id="nav-uc-6-2",
                            action=True,
                            className="border-0 py-2 ps-4",
                            href="#uc-6-2-card",
                        ),
                        dbc.ListGroupItem(
                            "UC-6.3: Chemical Hierarchy",
                            id="nav-uc-6-3",
                            action=True,
                            className="border-0 py-2 ps-4",
                            href="#uc-6-3-card",
                        ),
                        dbc.ListGroupItem(
                            "UC-6.4: Enzymatic Activity",
                            id="nav-uc-6-4",
                            action=True,
                            className="border-0 py-2 ps-4",
                            href="#uc-6-4-card",
                        ),
                        dbc.ListGroupItem(
                            "UC-6.5: Substrate Scope",
                            id="nav-uc-6-5",
                            action=True,
                            className="border-0 py-2 ps-4",
                            href="#uc-6-5-card",
                        ),
                    ],
                    flush=True,
                    className="mb-4",
                ),
            ]
        ),
        # ========================================
        # Module 7: Toxicological Assessment
        # ========================================
        html.Div(
            [
                html.H6(
                    "Module 7: Toxicological Assessment", className="mb-2 text-muted"
                ),
                dbc.ListGroup(
                    [
                        dbc.ListGroupItem(
                            [html.I(className="fas fa-book-open me-2"), "Overview"],
                            id="nav-module7",
                            action=True,
                            className="border-0 py-2",
                            href="#module7-section",
                        ),
                        dbc.ListGroupItem(
                            "UC-7.1: Toxicity Profiles",
                            id="nav-uc-7-1",
                            action=True,
                            className="border-0 py-2 ps-4",
                            href="#uc-7-1-card",
                        ),
                        dbc.ListGroupItem(
                            "UC-7.2: Concordance Risk vs Regulatory Focus",
                            id="nav-uc-7-2",
                            action=True,
                            className="border-0 py-2 ps-4",
                            href="#uc-7-2-card",
                        ),
                        dbc.ListGroupItem(
                            "UC-7.3: Genetic Response Map",
                            id="nav-uc-7-3",
                            action=True,
                            className="border-0 py-2 ps-4",
                            href="#uc-7-3-card",
                        ),
                        dbc.ListGroupItem(
                            "UC-7.4: Score Distribution",
                            id="nav-uc-7-4",
                            action=True,
                            className="border-0 py-2 ps-4",
                            href="#uc-7-4-card",
                        ),
                        dbc.ListGroupItem(
                            "UC-7.5: Toxicity Distribution by Endpoint",
                            id="nav-uc-7-5",
                            action=True,
                            className="border-0 py-2 ps-4",
                            href="#uc-7-5-card",
                        ),
                        dbc.ListGroupItem(
                            "UC-7.6: Mitigation Breadth",
                            id="nav-uc-7-6",
                            action=True,
                            className="border-0 py-2 ps-4",
                            href="#uc-7-6-card",
                        ),
                        dbc.ListGroupItem(
                            "UC-7.7: Mitigation Depth",
                            id="nav-uc-7-7",
                            action=True,
                            className="border-0 py-2 ps-4",
                            href="#uc-7-7-card",
                        ),
                    ],
                    flush=True,
                    className="mb-4",
                ),
            ]
        ),
        # ========================================
        # Module 8: Consortium Assembly
        # ========================================
        html.Div(
            [
                html.H6("Module 8: Consortium Assembly", className="mb-2 text-muted"),
                dbc.ListGroup(
                    [
                        dbc.ListGroupItem(
                            [html.I(className="fas fa-book-open me-2"), "Overview"],
                            id="nav-module8",
                            action=True,
                            className="border-0 py-2",
                            href="#module8-section",
                        ),
                        dbc.ListGroupItem(
                            "UC-8.1: Minimal Sample Grouping",
                            id="nav-uc-8-1",
                            action=True,
                            className="border-0 py-2 ps-4",
                            href="#uc-8-1-card",
                        ),
                        dbc.ListGroupItem(
                            "UC-8.2: Class Completeness",
                            id="nav-uc-8-2",
                            action=True,
                            className="border-0 py-2 ps-4",
                            href="#uc-8-2-card",
                        ),
                        dbc.ListGroupItem(
                            "UC-8.3: Pathway Completeness",
                            id="nav-uc-8-3",
                            action=True,
                            className="border-0 py-2 ps-4",
                            href="#uc-8-3-card",
                        ),
                        dbc.ListGroupItem(
                            "UC-8.4: Compound Completeness",
                            id="nav-uc-8-4",
                            action=True,
                            className="border-0 py-2 ps-4",
                            href="#uc-8-4-card",
                        ),
                        dbc.ListGroupItem(
                            "UC-8.5: Enzyme Completeness",
                            id="nav-uc-8-5",
                            action=True,
                            className="border-0 py-2 ps-4",
                            href="#uc-8-5-card",
                        ),
                        dbc.ListGroupItem(
                            "UC-8.6: Pathway Consortium",
                            id="nav-uc-8-6",
                            action=True,
                            className="border-0 py-2 ps-4",
                            href="#uc-8-6-card",
                        ),
                        dbc.ListGroupItem(
                            "UC-8.7: Gene Intersection",
                            id="nav-uc-8-7",
                            action=True,
                            className="border-0 py-2 ps-4",
                            href="#uc-8-7-card",
                        ),
                    ],
                    flush=True,
                    className="mb-4",
                ),
            ]
        ),
    ]

    offcanvas = dbc.Offcanvas(
        navigation_content,
        id="navigation-offcanvas",
        title="BioRemPP v1.0 - Navigation",
        is_open=False,
        placement="end",  # Right-to-left
        scrollable=True,
        backdrop=True,  # Show backdrop for better UX
        keyboard=True,  # Allow ESC key to close
        close_button=True,  # Show close button
        style={"width": "350px"},
    )

    return offcanvas
