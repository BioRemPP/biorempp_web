"""
Schema Page Renderer - Data-driven page generation from YAML configs.

This module provides functions to render database schema pages from YAML
configuration files, following a similar pattern to plot_configs.

Functions
---------
load_schema_config
    Load YAML configuration for a schema
render_schema_index_page
    Render the schemas index page
render_schema_page
    Render an individual schema page
"""

from pathlib import Path
from typing import Any

import dash_bootstrap_components as dbc
import yaml
from dash import html

from config.settings import DATABASE_VERSIONS

# Path to schema configuration files
CONFIGS_PATH = (
    Path(__file__).parent.parent.parent.parent
    / "infrastructure"
    / "schema_configs"
)


def load_schema_config(config_name: str) -> dict[str, Any]:
    """
    Load YAML configuration for a schema.

    Parameters
    ----------
    config_name : str
        Name of the config file (without extension), e.g., 'biorempp_schema'

    Returns
    -------
    dict
        Parsed YAML configuration
    """
    config_file = CONFIGS_PATH / f"{config_name}.yaml"
    with open(config_file, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def render_schema_index_page() -> html.Div:
    """
    Render the database schemas index page.

    Returns
    -------
    html.Div
        Complete index page layout
    """
    config = load_schema_config("index_config")

    return html.Div(
        [
            _render_index_header(config),
            dbc.Container(
                [
                    _render_quick_navigation(config),
                    _render_overview_section(config),
                    _render_database_cards(config),
                    _render_integration_section(config),
                    _render_file_format_section(config),
                    _render_contact_section(config),
                ],
                className="py-4",
            ),
        ]
    )


def render_schema_page(schema_id: str) -> html.Div:
    """
    Render an individual database schema page.

    Parameters
    ----------
    schema_id : str
        Schema identifier (biorempp, hadeg, kegg, toxcsm)

    Returns
    -------
    html.Div
        Complete schema page layout
    """
    config = load_schema_config(f"{schema_id}_schema")

    # Build base sections
    sections = [
        _render_breadcrumb(config),
        _render_overview(config),
        _render_schema_definition(config),
    ]

    # Add ToxCSM-specific sections if present
    if "column_organization" in config:
        sections.append(_render_column_organization(config))
    
    if "label_categories" in config:
        sections.append(_render_label_categories(config))

    # Standard columns section
    sections.append(_render_columns_section(config))

    # Add ToxCSM toxicity endpoints if present
    if "toxicity_endpoints" in config:
        sections.append(_render_toxicity_endpoints(config))
    
    if "value_columns_info" in config:
        sections.append(_render_value_columns_info(config))

    # Standard sections
    sections.extend([
        _render_constraints_section(config),
        _render_data_quality_section(config),
        _render_usage_examples_section(config),
        _render_schema_contact_section(config),
    ])

    return html.Div(
        [
            _render_schema_header(config),
            dbc.Container(sections, className="py-4"),
        ]
    )


# =============================================================================
# Index Page Render Functions
# =============================================================================


def _render_index_header(config: dict) -> html.Div:
    """Render index page header."""
    return html.Div(
        [
            html.H1(
                [
                    html.I(className=f"fas {config.get('icon', 'fa-database')} me-3 text-success"),
                    config["title"],
                ],
                className="text-center mb-3",
            ),
            html.P(
                config["subtitle"],
                className="text-center text-muted mb-4 lead",
            ),
            html.Hr(),
        ],
        className="mb-4 pt-4",
    )


def _render_quick_navigation(config: dict) -> dbc.Card:
    """Render quick navigation table."""
    databases = config["databases"]

    table_header = html.Thead(
        html.Tr(
            [
                html.Th("Database"),
                html.Th("Rows"),
                html.Th("Columns"),
                html.Th("Focus"),
                html.Th("Join Key"),
            ]
        )
    )

    table_body = html.Tbody(
        [
            html.Tr(
                [
                    html.Td(
                        html.A(
                            [
                                html.Strong(db["name"]),
                            ],
                            href=db["route"],
                            className=f"text-{db['color']} text-decoration-none",
                        )
                    ),
                    html.Td(f"{db['rows']:,}"),
                    html.Td(str(db["columns"])),
                    html.Td(db["focus"]),
                    html.Td(html.Code(db["join_key"])),
                ]
            )
            for db in databases
        ]
    )

    return dbc.Card(
        [
            dbc.CardHeader(
                "Quick Navigation",
                className="bg-primary text-white",
            ),
            dbc.CardBody(
                dbc.Table(
                    [table_header, table_body],
                    bordered=True,
                    hover=True,
                    responsive=True,
                    className="mb-0",
                )
            ),
        ],
        className="mb-4",
    )


def _render_overview_section(config: dict) -> dbc.Card:
    """Render overview section."""
    overview = config["overview"]

    items = [
        dbc.ListGroupItem(
            [
                html.I(className="fas fa-check-circle me-2 text-success"),
                html.Strong(f"{key.replace('_', ' ').title()}: "),
                value,
            ]
        )
        for key, value in overview.items()
    ]

    return dbc.Card(
        [
            dbc.CardHeader(
                "What Each Schema Contains",
                className="bg-success text-white",
            ),
            dbc.CardBody(dbc.ListGroup(items, flush=True)),
        ],
        className="mb-4",
    )


def _render_database_cards(config: dict) -> html.Div:
    """Render database summary cards."""
    databases = config["databases"]

    cards = []
    for db in databases:
        card = dbc.Col(
            dbc.Card(
                [
                    dbc.CardHeader(
                        db["name"],
                        className=f"bg-{db['color']} text-white",
                    ),
                    dbc.CardBody(
                        [
                            html.P(db["focus"], className="card-text"),
                            html.Hr(),
                            html.P(
                                [
                                    html.Strong(f"{db['rows']:,}"),
                                    " rows × ",
                                    html.Strong(str(db["columns"])),
                                    " columns",
                                ],
                                className="mb-2",
                            ),
                            html.P(
                                [
                                    "Join key: ",
                                    html.Code(db["join_key"]),
                                ],
                                className="mb-3",
                            ),
                            dbc.Button(
                                [
                                    "View Schema ",
                                    html.I(className="fas fa-arrow-right ms-1"),
                                ],
                                href=db["route"],
                                color=db["color"],
                                outline=True,
                                size="sm",
                            ),
                        ]
                    ),
                ],
                className="h-100",
            ),
            md=6,
            lg=3,
            className="mb-4",
        )
        cards.append(card)

    return html.Div(
        [
            html.H4(
                [
                    html.I(className="fas fa-layer-group me-2 text-primary"),
                    "Database Summaries",
                ],
                className="mb-3",
            ),
            dbc.Row(cards),
        ],
        className="mb-4",
    )


def _render_integration_section(config: dict) -> dbc.Card:
    """Render integration architecture section."""
    integration = config["integration"]

    join_items = [
        dbc.ListGroupItem(
            [
                html.Strong(", ".join(jp["databases"])),
                " → Join on ",
                html.Code(jp["key"]),
                f" ({jp['description']})",
            ]
        )
        for jp in integration["join_points"]
    ]

    return dbc.Card(
        [
            dbc.CardHeader(
                "Integration Architecture",
                className="bg-info text-white",
            ),
            dbc.CardBody(
                [
                    html.P(integration["description"], className="mb-3"),
                    html.H6("Join Relationships:", className="mb-2"),
                    dbc.ListGroup(join_items, flush=True),
                ]
            ),
        ],
        className="mb-4",
    )


def _render_file_format_section(config: dict) -> dbc.Card:
    """Render common file format section."""
    file_format = config["file_format"]

    rows = [
        html.Tr([html.Td(html.Strong(k.replace("_", " ").title())), html.Td(str(v))])
        for k, v in file_format.items()
    ]

    return dbc.Card(
        [
            dbc.CardHeader(
                "Common File Format",
                className="bg-secondary text-white",
            ),
            dbc.CardBody(
                dbc.Table(
                    html.Tbody(rows),
                    bordered=True,
                    size="sm",
                    className="mb-0",
                )
            ),
        ],
        className="mb-4",
    )


def _render_contact_section(config: dict) -> dbc.Alert:
    """Render contact section."""
    contact = config["contact"]

    return dbc.Alert(
        [
            html.I(className="fas fa-question-circle me-2"),
            html.Strong("Questions? "),
            html.A(
                "GitHub Issues",
                href=contact["github_issues"],
                target="_blank",
                className="alert-link",
            ),
            " | ",
            html.A(
                contact["email"],
                href=f"mailto:{contact['email']}",
                className="alert-link",
            ),
        ],
        color="light",
        className="mb-0",
    )


# =============================================================================
# Schema Page Render Functions
# =============================================================================


def _render_schema_header(config: dict) -> html.Div:
    """Render schema page header with version from settings.py."""
    schema_id = config["schema_id"]
    db_info = DATABASE_VERSIONS.get(schema_id, {})
    color = db_info.get("color", config.get("color", "primary"))
    version = db_info.get("version", config.get("version", "1.0.0"))

    return html.Div(
        [
            html.H1(
                [
                    html.I(className=f"fas fa-database me-3 text-{color}"),
                    config["title"],
                ],
                className="text-center mb-2",
            ),
            html.P(
                [
                    dbc.Badge(version, color=color, className="me-2"),
                    f"Last updated: {config['last_updated']}",
                ],
                className="text-center text-muted mb-4",
            ),
            html.Hr(),
        ],
        className="mb-4 pt-4",
    )


def _render_breadcrumb(config: dict) -> html.Div:
    """Render database navigation bar using versions from settings.py."""
    schema_id = config["schema_id"]
    
    # Database navigation links from settings
    databases = [
        {"id": db_id, "name": info["name"], "color": info["color"]}
        for db_id, info in DATABASE_VERSIONS.items()
    ]
    
    # Create database navigation buttons with better contrast
    nav_buttons = []
    for db in databases:
        is_active = db["id"] == schema_id
        nav_buttons.append(
            dbc.Button(
                db["name"],
                href=f"/schemas/{db['id']}",
                color=db["color"] if is_active else "secondary",
                outline=not is_active,
                size="sm",
                className="me-2 mb-2",
                active=is_active,
            )
        )
    
    return html.Div([
        # Database navigation bar only
        dbc.Card(
            dbc.CardBody([
                html.Strong("Navigate to: ", className="text-muted me-3"),
                html.Span(nav_buttons),
            ], className="py-2 d-flex align-items-center flex-wrap"),
            className="mb-4 bg-light border-0",
        ),
    ])


def _render_overview(config: dict) -> dbc.Card:
    """Render overview section."""
    overview = config["overview"]

    rationale_items = [
        dbc.ListGroupItem(
            [
                html.Strong(f"{r['title']}: "),
                r["description"],
            ]
        )
        for r in overview["design_rationale"]
    ]

    return dbc.Card(
        [
            dbc.CardHeader(
                "Overview",
                className="bg-primary text-white",
            ),
            dbc.CardBody(
                [
                    html.P(overview["description"], className="mb-3"),
                    html.H6("Design Rationale:", className="mb-2"),
                    dbc.ListGroup(rationale_items, flush=True),
                ]
            ),
        ],
        className="mb-4",
    )


def _render_schema_definition(config: dict) -> dbc.Card:
    """Render schema definition section."""
    schema_def = config["schema_definition"]

    rows = [
        html.Tr(
            [
                html.Td(html.Strong(k.replace("_", " ").title())),
                html.Td(str(v)),
            ]
        )
        for k, v in schema_def.items()
    ]

    return dbc.Card(
        [
            dbc.CardHeader(
                "Schema Definition",
                className="bg-success text-white",
            ),
            dbc.CardBody(
                dbc.Table(
                    html.Tbody(rows),
                    bordered=True,
                    hover=True,
                    size="sm",
                    className="mb-0",
                )
            ),
        ],
        className="mb-4",
    )


def _render_columns_section(config: dict) -> dbc.Card:
    """Render column specifications section."""
    columns = config["columns"]

    # Summary table
    table_header = html.Thead(
        html.Tr(
            [
                html.Th("#"),
                html.Th("Column"),
                html.Th("Type"),
                html.Th("Nullable"),
                html.Th("Example"),
            ]
        )
    )

    table_rows = [
        html.Tr(
            [
                html.Td(str(i + 1)),
                html.Td(html.Code(col["name"])),
                html.Td(col["type"]),
                html.Td("No" if not col["nullable"] else "Yes"),
                html.Td(html.Code(col["example"])),
            ]
        )
        for i, col in enumerate(columns)
    ]

    # Detail accordions
    accordion_items = [
        dbc.AccordionItem(
            _render_column_details(col),
            title=f"{col['name']} — {col['description']}",
        )
        for col in columns
    ]

    return dbc.Card(
        [
            dbc.CardHeader(
                "Column Specifications",
                className="bg-info text-white",
            ),
            dbc.CardBody(
                [
                    html.H6("Summary Table", className="mb-2"),
                    dbc.Table(
                        [table_header, html.Tbody(table_rows)],
                        bordered=True,
                        hover=True,
                        responsive=True,
                        size="sm",
                        className="mb-4",
                    ),
                    html.H6("Column Details", className="mb-2"),
                    dbc.Accordion(accordion_items, start_collapsed=True),
                ]
            ),
        ],
        className="mb-4",
    )


def _render_column_details(col: dict) -> html.Div:
    """Render detailed column information."""
    items = [
        html.P([html.Strong("Description: "), col["description"]]),
        html.P([html.Strong("Purpose: "), col.get("purpose", "N/A")]),
        html.P([html.Strong("Pattern: "), col.get("pattern", "N/A")]),
        html.P([html.Strong("Uniqueness: "), col.get("uniqueness", "N/A")]),
        html.P([html.Strong("Cardinality: "), str(col.get("cardinality", "N/A"))]),
    ]

    if "regex" in col:
        items.append(html.P([html.Strong("Regex: "), html.Code(col["regex"])]))

    if "valid_values" in col:
        values = col["valid_values"]
        if isinstance(values, list) and len(values) > 0:
            if isinstance(values[0], dict):
                # Handle dict format (e.g., referenceAG)
                key = "code" if "code" in values[0] else "class" if "class" in values[0] else "name"
                badges = [
                    dbc.Badge(v.get(key, str(v)), color="secondary", className="me-1 mb-1")
                    for v in values[:10]
                ]
                if len(values) > 10:
                    badges.append(dbc.Badge(f"+{len(values) - 10} more", color="light", className="me-1"))
                items.append(html.P([html.Strong("Valid Values: "), html.Span(badges)]))

    return html.Div(items)


def _render_constraints_section(config: dict) -> dbc.Card:
    """Render schema constraints section."""
    constraints = config["constraints"]

    content = []

    # Primary key
    pk = constraints.get("primary_key")
    if pk:
        content.append(html.P([html.Strong("Primary Key: "), html.Code(pk)]))
    else:
        content.append(
            html.P(
                [
                    html.Strong("Primary Key: "),
                    html.Em("None defined — "),
                    constraints.get("primary_key_note", "Flat structure"),
                ]
            )
        )

    # Conceptual key
    ck = constraints.get("conceptual_key")
    if ck:
        content.append(
            html.P(
                [
                    html.Strong("Conceptual Key: "),
                    html.Code(", ".join(ck)),
                ]
            )
        )

    # Foreign keys
    fks = constraints.get("foreign_keys", [])
    if fks:
        fk_items = [
            dbc.ListGroupItem(
                [
                    html.Code(fk["column"]),
                    " → ",
                    fk["references"],
                ]
            )
            for fk in fks
        ]
        content.append(html.H6("Foreign Keys:", className="mt-3 mb-2"))
        content.append(dbc.ListGroup(fk_items, flush=True))

    # Cardinality
    cards = constraints.get("cardinality_relationships", [])
    if cards:
        card_items = [
            dbc.ListGroupItem(
                [
                    html.Strong(f"{c['name']} ({c['type']}): "),
                    c["description"],
                ]
            )
            for c in cards
        ]
        content.append(html.H6("Cardinality Relationships:", className="mt-3 mb-2"))
        content.append(dbc.ListGroup(card_items, flush=True))

    return dbc.Card(
        [
            dbc.CardHeader(
                "Schema Constraints",
                className="bg-warning text-dark",
            ),
            dbc.CardBody(content),
        ],
        className="mb-4",
    )


def _render_data_quality_section(config: dict) -> dbc.Card:
    """Render data quality section."""
    quality = config["data_quality"]

    content = []

    # Completeness
    comp = quality.get("completeness", {})
    content.append(
        dbc.Alert(
            [
                html.I(className="fas fa-check-circle me-2"),
                html.Strong(f"Completeness: {comp.get('status', 'N/A')}"),
                html.Br(),
                html.Small(comp.get("description", "")),
            ],
            color="success",
            className="mb-3",
        )
    )

    # Consistency
    cons = quality.get("consistency", [])
    if cons:
        items = [dbc.ListGroupItem([html.I(className="fas fa-check me-2 text-success"), c]) for c in cons]
        content.append(html.H6("Consistency Checks:", className="mb-2"))
        content.append(dbc.ListGroup(items, flush=True, className="mb-3"))

    # Accuracy/Source
    acc = quality.get("accuracy", [])
    if acc:
        rows = [
            html.Tr([html.Td(html.Code(a["column"])), html.Td(a["source"])])
            for a in acc
        ]
        content.append(html.H6("Data Provenance:", className="mb-2"))
        content.append(
            dbc.Table(
                html.Tbody(rows),
                bordered=True,
                size="sm",
                className="mb-0",
            )
        )

    return dbc.Card(
        [
            dbc.CardHeader(
                "Data Quality",
                className="bg-success text-white",
            ),
            dbc.CardBody(content),
        ],
        className="mb-4",
    )


def _render_usage_examples_section(config: dict) -> dbc.Card:
    """Render usage examples section with R and Python tabs."""
    examples = config["usage_examples"]

    tabs = dbc.Tabs(
        [
            dbc.Tab(
                html.Pre(
                    html.Code(examples.get("r", "# No R example available")),
                    className="bg-dark text-light p-3 rounded",
                ),
                label="R",
                tab_id="tab-r",
            ),
            dbc.Tab(
                html.Pre(
                    html.Code(examples.get("python", "# No Python example available")),
                    className="bg-dark text-light p-3 rounded",
                ),
                label="Python",
                tab_id="tab-python",
            ),
        ],
        active_tab="tab-r",
        className="mb-3",
    )

    return dbc.Card(
        [
            dbc.CardHeader(
                "Usage Examples",
                className="bg-secondary text-white",
            ),
            dbc.CardBody(tabs),
        ],
        className="mb-4",
    )


def _render_schema_contact_section(config: dict) -> dbc.Alert:
    """Render contact section for schema page."""
    contact = config["contact"]

    return dbc.Alert(
        [
            html.I(className="fas fa-question-circle me-2"),
            html.Strong("Questions? "),
            html.A(
                "GitHub Issues",
                href=contact["github_issues"],
                target="_blank",
                className="alert-link",
            ),
            " | ",
            html.A(
                contact["email"],
                href=f"mailto:{contact['email']}",
                className="alert-link",
            ),
        ],
        color="light",
        className="mb-0",
    )


# =============================================================================
# ToxCSM-Specific Render Functions
# =============================================================================


def _render_column_organization(config: dict) -> dbc.Card:
    """Render column organization section for ToxCSM."""
    org = config["column_organization"]

    rows = [
        html.Tr([
            html.Td(html.Strong(item["category"])),
            html.Td(str(item["count"])),
            html.Td(", ".join(item.get("columns", [])) if "columns" in item else item.get("description", "")),
        ])
        for item in org
    ]

    return dbc.Card(
        [
            dbc.CardHeader(
                "Column Organization",
                className="bg-danger text-white",
            ),
            dbc.CardBody(
                dbc.Table(
                    [
                        html.Thead(
                            html.Tr([html.Th("Category"), html.Th("Count"), html.Th("Details")])
                        ),
                        html.Tbody(rows),
                    ],
                    bordered=True,
                    hover=True,
                    size="sm",
                    className="mb-0",
                )
            ),
        ],
        className="mb-4",
    )


def _render_label_categories(config: dict) -> dbc.Card:
    """Render toxicity label categories for ToxCSM."""
    categories = config["label_categories"]

    # Create colored badges for each label (3 levels)
    badge_colors = {
        "Safety": "success",
        "Moderate Risk": "warning",
        "High Risk": "danger",
    }

    items = [
        dbc.ListGroupItem(
            [
                dbc.Badge(cat["value"], color=badge_colors.get(cat["value"], "secondary"), className="me-2"),
                html.Span(cat["interpretation"]),
            ],
            className="d-flex align-items-center",
        )
        for cat in categories
    ]

    return dbc.Card(
        [
            dbc.CardHeader(
                "Toxicity Label Categories",
                className="bg-danger text-white",
            ),
            dbc.CardBody(
                [
                    html.P(
                        "All toxicity label columns use a 3-level categorical scale:",
                        className="mb-3",
                    ),
                    dbc.ListGroup(items, flush=True),
                ]
            ),
        ],
        className="mb-4",
    )


def _render_toxicity_endpoints(config: dict) -> dbc.Card:
    """Render toxicity endpoints section for ToxCSM."""
    endpoints = config["toxicity_endpoints"]

    # Category labels with icons and colors
    category_labels = {
        "environmental": ("Environmental", "globe", "info"),
        "genomic": ("Genomic", "dna", "danger"),
        "organic": ("Organic", "heart", "warning"),
        "nuclear_response": ("Nuclear Response", "atom", "primary"),
        "stress_response": ("Stress Response", "exclamation-triangle", "warning"),
        "dose_response": ("Dose Response", "chart-line", "secondary"),
    }

    accordion_items = []

    for category_key, endpoint_list in endpoints.items():
        label, icon, color = category_labels.get(category_key, (category_key.replace("_", " ").title(), "circle", "secondary"))

        # Create table for endpoints in this category
        rows = [
            html.Tr([
                html.Td(ep["endpoint"]),
                html.Td(html.Code(ep["label_column"])),
                html.Td(html.Code(ep["value_column"])),
                html.Td(ep["description"]),
                html.Td(ep.get("samples", "-")),
                html.Td(html.Small(ep.get("source", "-"))),
            ])
            for ep in endpoint_list
        ]

        table = dbc.Table(
            [
                html.Thead(
                    html.Tr([
                        html.Th("Endpoint"),
                        html.Th("Label Column"),
                        html.Th("Value Column"),
                        html.Th("Description"),
                        html.Th("Samples"),
                        html.Th("Source"),
                    ])
                ),
                html.Tbody(rows),
            ],
            bordered=True,
            hover=True,
            size="sm",
            responsive=True,
            className="mb-0",
        )

        accordion_items.append(
            dbc.AccordionItem(
                table,
                title=f"{label} ({len(endpoint_list)} endpoints)",
            )
        )

    return dbc.Card(
        [
            dbc.CardHeader(
                "Toxicological Endpoints (31 total)",
                className="bg-danger text-white",
            ),
            dbc.CardBody(
                dbc.Accordion(accordion_items, start_collapsed=True)
            ),
        ],
        className="mb-4",
    )


def _render_value_columns_info(config: dict) -> dbc.Card:
    """Render value columns info for ToxCSM."""
    info = config["value_columns_info"]

    rows = [
        html.Tr([html.Td(html.Strong(k.replace("_", " ").title())), html.Td(str(v))])
        for k, v in info.items()
    ]

    return dbc.Card(
        [
            dbc.CardHeader(
                "Numeric Value Columns",
                className="bg-secondary text-white",
            ),
            dbc.CardBody(
                [
                    html.P(
                        "All value columns contain numeric scores corresponding to each toxicity label:",
                        className="mb-3",
                    ),
                    dbc.Table(
                        html.Tbody(rows),
                        bordered=True,
                        size="sm",
                        className="mb-0",
                    ),
                ]
            ),
        ],
        className="mb-4",
    )

