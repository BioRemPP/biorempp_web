"""
Navigation Offcanvas Component - BioRemPP v1.0.

Collapsible offcanvas navigation optimized for long module/use-case lists.
"""

from __future__ import annotations

import dash_bootstrap_components as dbc
from dash import html


def _create_nav_item(
    *,
    item_id: str,
    label: str,
    href: str,
    icon_class: str | None = None,
    indent: bool = False,
) -> dbc.ListGroupItem:
    """Build one clickable navigation item preserving stable IDs."""
    children = (
        [html.I(className=f"{icon_class} me-2"), label] if icon_class else label
    )
    class_name = "border-0 py-2 ps-4" if indent else "border-0 py-2"
    return dbc.ListGroupItem(
        children,
        id=item_id,
        action=True,
        className=class_name,
        href=href,
    )


def _build_module_item(module: dict[str, object]) -> dbc.AccordionItem:
    """Create one collapsible module section with overview + UC links."""
    module_id = str(module["id"])
    module_title = str(module["title"])
    use_cases: list[tuple[str, str, str]] = list(module["use_cases"])  # (id, label, href)

    links = [
        _create_nav_item(
            item_id=f"nav-module{module_id}",
            label="Overview",
            href=f"#module{module_id}-section",
            icon_class="fas fa-book-open",
            indent=False,
        )
    ]
    links.extend(
        _create_nav_item(
            item_id=uc_id,
            label=uc_label,
            href=uc_href,
            indent=True,
        )
        for uc_id, uc_label, uc_href in use_cases
    )

    return dbc.AccordionItem(
        dbc.ListGroup(links, flush=True),
        title=[
            html.I(className="fas fa-layer-group me-2 text-muted"),
            html.Span(module_title, className="text-muted fw-bold"),
        ],
        item_id=f"nav-module-group-{module_id}",
    )


def create_navigation_offcanvas() -> dbc.Offcanvas:
    """Create right-side offcanvas with compact collapsible module navigation."""
    database_links = dbc.ListGroup(
        [
            _create_nav_item(
                item_id="nav-biorempp",
                label="BioRemPP Results",
                href="#biorempp-section",
                icon_class="fas fa-table",
            ),
            _create_nav_item(
                item_id="nav-hadeg",
                label="HADEG Database",
                href="#hadeg-section",
                icon_class="fas fa-table",
            ),
            _create_nav_item(
                item_id="nav-toxcsm",
                label="ToxCSM Database",
                href="#toxcsm-section",
                icon_class="fas fa-table",
            ),
            _create_nav_item(
                item_id="nav-kegg",
                label="KEGG Pathways",
                href="#kegg-section",
                icon_class="fas fa-table",
            ),
        ],
        flush=True,
        className="mb-4",
    )

    modules: list[dict[str, object]] = [
        {
            "id": "1",
            "title": "Module 1: Comparative Assessment",
            "use_cases": [
                ("nav-uc-1-1", "UC-1.1: Database Overlap", "#uc-1-1-card"),
                ("nav-uc-1-2", "UC-1.2: Agency Overlap", "#uc-1-2-card"),
                ("nav-uc-1-3", "UC-1.3: Reference Contribution", "#uc-1-3-card"),
                ("nav-uc-1-4", "UC-1.4: Sample Diversity", "#uc-1-4-card"),
                ("nav-uc-1-5", "UC-1.5: Compliance Scorecard", "#uc-1-5-card"),
                ("nav-uc-1-6", "UC-1.6: Functional Heatmap", "#uc-1-6-card"),
            ],
        },
        {
            "id": "2",
            "title": "Module 2: Exploratory Analysis",
            "use_cases": [
                ("nav-uc-2-1", "UC-2.1: KO Richness", "#uc-2-1-card"),
                ("nav-uc-2-2", "UC-2.2: Compound Richness", "#uc-2-2-card"),
                ("nav-uc-2-3", "UC-2.3: Sample Diversity", "#uc-2-3-card"),
                ("nav-uc-2-4", "UC-2.4: Genetic Interaction", "#uc-2-4-card"),
                ("nav-uc-2-5", "UC-2.5: KO Distribution", "#uc-2-5-card"),
            ],
        },
        {
            "id": "3",
            "title": "Module 3: System Structure",
            "use_cases": [
                ("nav-uc-3-1", "UC-3.1: Sample Relationships by KO (PCA)", "#uc-3-1-card"),
                ("nav-uc-3-2", "UC-3.2: Sample Relationships by Chemical (PCA)", "#uc-3-2-card"),
                ("nav-uc-3-4", "UC-3.4: Sample Similarity (KO)", "#uc-3-4-card"),
                ("nav-uc-3-5", "UC-3.5: Sample Similarity (Chem)", "#uc-3-5-card"),
                ("nav-uc-3-6", "UC-3.6: Gene Co-occurrence", "#uc-3-6-card"),
                ("nav-uc-3-7", "UC-3.7: Compound Co-occurrence", "#uc-3-7-card"),
            ],
        },
        {
            "id": "4",
            "title": "Module 4: Functional Profiling",
            "use_cases": [
                ("nav-uc-4-1", "UC-4.1: Functional Profiling by Pathway", "#uc-4-1-card"),
                ("nav-uc-4-2", "UC-4.2: Sample Ranking by Pathway Richness", "#uc-4-2-card"),
                ("nav-uc-4-3", "UC-4.3: Sample Comparison by Pathway", "#uc-4-3-card"),
                ("nav-uc-4-4", "UC-4.4: Functional Fingerprint by Sample", "#uc-4-4-card"),
                ("nav-uc-4-5", "UC-4.5: Gene Presence Map by Pathway", "#uc-4-5-card"),
                ("nav-uc-4-6", "UC-4.6: Functional Potential by Compound", "#uc-4-6-card"),
                ("nav-uc-4-7", "UC-4.7: Gene-Compound Association Explorer", "#uc-4-7-card"),
                ("nav-uc-4-8", "UC-4.8: Gene Inventory Explorer by Sample", "#uc-4-8-card"),
                ("nav-uc-4-9", "UC-4.9: Enzymatic Activity Profiling", "#uc-4-9-card"),
                ("nav-uc-4-10", "UC-4.10: Genetic Diversity by Enzyme Activity", "#uc-4-10-card"),
                ("nav-uc-4-11", "UC-4.11: Global Genetic Diversity Hierarchy", "#uc-4-11-card"),
                ("nav-uc-4-12", "UC-4.12: Pathway Relationships by Sample", "#uc-4-12-card"),
                ("nav-uc-4-13", "UC-4.13: Genetic Profile by Compound Pathway", "#uc-4-13-card"),
            ],
        },
        {
            "id": "5",
            "title": "Module 5: Interaction Modeling",
            "use_cases": [
                ("nav-uc-5-1", "UC-5.1: Sample-Compound Interaction Strength", "#uc-5-1-card"),
                ("nav-uc-5-2", "UC-5.2: Sample Similarity via Shared Compounds", "#uc-5-2-card"),
                ("nav-uc-5-3", "UC-5.3: Regulatory Relevance of Samples", "#uc-5-3-card"),
                ("nav-uc-5-4", "UC-5.4: Gene-Compound Interaction Network", "#uc-5-4-card"),
                ("nav-uc-5-5", "UC-5.5: Gene-Gene Functional Interaction", "#uc-5-5-card"),
                ("nav-uc-5-6", "UC-5.6: Compound-Compound Similarity Network", "#uc-5-6-card"),
            ],
        },
        {
            "id": "6",
            "title": "Module 6: Hierarchical Analysis",
            "use_cases": [
                ("nav-uc-6-1", "UC-6.1: Regulatory to Molecular Flow", "#uc-6-1-card"),
                ("nav-uc-6-2", "UC-6.2: Biological Interaction Flow", "#uc-6-2-card"),
                ("nav-uc-6-3", "UC-6.3: Chemical Hierarchy", "#uc-6-3-card"),
                ("nav-uc-6-4", "UC-6.4: Enzymatic Activity", "#uc-6-4-card"),
                ("nav-uc-6-5", "UC-6.5: Substrate Scope", "#uc-6-5-card"),
            ],
        },
        {
            "id": "7",
            "title": "Module 7: Toxicological Assessment",
            "use_cases": [
                ("nav-uc-7-1", "UC-7.1: Toxicity Profiles", "#uc-7-1-card"),
                ("nav-uc-7-2", "UC-7.2: Concordance Risk vs Regulatory Focus", "#uc-7-2-card"),
                ("nav-uc-7-3", "UC-7.3: Genetic Response Map", "#uc-7-3-card"),
                ("nav-uc-7-4", "UC-7.4: Score Distribution", "#uc-7-4-card"),
                ("nav-uc-7-5", "UC-7.5: Toxicity Distribution by Endpoint", "#uc-7-5-card"),
                ("nav-uc-7-6", "UC-7.6: Mitigation Breadth", "#uc-7-6-card"),
                ("nav-uc-7-7", "UC-7.7: Mitigation Depth", "#uc-7-7-card"),
            ],
        },
        {
            "id": "8",
            "title": "Module 8: Consortium Assembly",
            "use_cases": [
                ("nav-uc-8-1", "UC-8.1: Minimal Sample Grouping", "#uc-8-1-card"),
                ("nav-uc-8-2", "UC-8.2: Class Completeness", "#uc-8-2-card"),
                ("nav-uc-8-3", "UC-8.3: Pathway Completeness", "#uc-8-3-card"),
                ("nav-uc-8-4", "UC-8.4: Compound Completeness", "#uc-8-4-card"),
                ("nav-uc-8-5", "UC-8.5: Enzyme Completeness", "#uc-8-5-card"),
                ("nav-uc-8-6", "UC-8.6: Pathway Consortium", "#uc-8-6-card"),
                ("nav-uc-8-7", "UC-8.7: Gene Intersection", "#uc-8-7-card"),
            ],
        },
    ]

    module_accordion = dbc.Accordion(
        [_build_module_item(module) for module in modules],
        id="navigation-modules-accordion",
        start_collapsed=True,
        always_open=False,
        flush=True,
        className="mb-2",
    )

    navigation_content = [
        html.H5("Navigation", className="mb-3 fw-bold text-primary"),
        html.Div(
            [
                html.H6(
                    [html.I(className="fas fa-database me-2"), "Database Tables"],
                    className="mb-2 text-muted",
                ),
                database_links,
            ]
        ),
        html.Div(
            [
                html.H6(
                    [html.I(className="fas fa-layer-group me-2"), "Analysis Modules"],
                    className="mb-2 text-muted",
                ),
                module_accordion,
            ]
        ),
    ]

    return dbc.Offcanvas(
        navigation_content,
        id="navigation-offcanvas",
        title="BioRemPP v1.0 - Navigation",
        is_open=False,
        placement="end",
        scrollable=True,
        backdrop=True,
        keyboard=True,
        close_button=True,
        style={"width": "350px"},
    )

