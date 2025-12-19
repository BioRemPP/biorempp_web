"""
Data Type Exploration Tab - Analysis Suggestions
=================================================

Organize use cases by primary data entity type for systematic exploration.

Author: BioRemPP Development Team
Date: 2025-12-05
"""

from pathlib import Path

import dash_bootstrap_components as dbc
import yaml
from dash import html

from .guiding_questions import create_uc_link

# Load UC mapping from local directory
CONFIG_PATH = Path(__file__).parent / "uc_suggestions_map.yaml"


def load_uc_config():
    """Load UC suggestions mapping from YAML."""
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def filter_by_data_type(config: dict, data_type: str) -> list:
    """
    Filter use cases by data type.

    Parameters
    ----------
    config : dict
        Full configuration dictionary
    data_type : str
        Data type to filter by (genes, pathways, compounds, samples, interactions)

    Returns
    -------
    list
        List of tuples (uc_id, title, icon)
    """
    ucs = []
    for uc_id, uc_data in config["use_cases"].items():
        if uc_data.get("data_type") == data_type:
            ucs.append(
                (uc_id, uc_data["title"], uc_data.get("icon", "fas fa-chart-bar"))
            )
    return ucs


def create_entity_accordion_item(
    entity_id: str, entity_name: str, ucs: list, color: str, description: str, icon: str
) -> dbc.AccordionItem:
    """
    Create accordion item for entity category.

    Parameters
    ----------
    entity_id : str
        Unique ID for accordion item
    entity_name : str
        Display name of entity category
    ucs : list
        List of (uc_id, title, icon) tuples
    color : str
        Bootstrap color name
    description : str
        Category description
    icon : str
        FontAwesome icon class

    Returns
    -------
    dbc.AccordionItem
        Accordion item with UC links
    """
    # Create UC links - force all icons to fa-chart-bar for consistency
    uc_links = [
        create_uc_link(uc_id, title, "fas fa-chart-bar")
        for uc_id, title, uc_icon in ucs
    ]

    return dbc.AccordionItem(
        [
            html.P(description, className="text-muted small mb-3"),
            html.P(
                [
                    html.I(className="fas fa-chart-bar me-2 text-muted"),
                    html.Strong(f"{len(ucs)} use cases", className="text-muted"),
                ],
                className="small mb-3",
            ),
            (
                dbc.ListGroup(uc_links, flush=True)
                if uc_links
                else html.P(
                    "No use cases available for this category.",
                    className="text-muted small",
                )
            ),
        ],
        title=[
            html.I(className=f"{icon} me-2 text-{color}"),
            html.Span(entity_name, className=f"text-{color} fw-bold"),
        ],
        item_id=entity_id,
    )


def create_data_type_exploration_content() -> html.Div:
    """
    Create data type exploration tab content.

    Organizes all 56 use cases by primary data entity:
    - Genes (15 UCs)
    - Metabolic Pathways (12 UCs)
    - Compounds (14 UCs)
    - Samples (13 UCs)
    - Associations & Interactions (8 UCs)

    Returns
    -------
    html.Div
        Tab content with entity-organized use cases in accordion
    """
    config = load_uc_config()
    data_types_config = config.get("data_types", {})

    # Filter UCs by data type
    genes_ucs = filter_by_data_type(config, "genes")
    pathways_ucs = filter_by_data_type(config, "pathways")
    compounds_ucs = filter_by_data_type(config, "compounds")
    samples_ucs = filter_by_data_type(config, "samples")
    interactions_ucs = filter_by_data_type(config, "interactions")

    return html.Div(
        [
            dbc.Alert(
                [
                    html.I(className="fas fa-info-circle me-2"),
                    html.Strong("Explore by Data Type: "),
                    "Use cases organized by the primary data entity they analyze. "
                    "Click each category to expand and view relevant use cases.",
                ],
                color="info",
                className="mb-3",
            ),
            # Accordion with all entity categories
            dbc.Accordion(
                [
                    # Genes Section
                    create_entity_accordion_item(
                        entity_id="datatype-genes",
                        entity_name=data_types_config.get("genes", {}).get(
                            "name", "Genes"
                        ),
                        ucs=genes_ucs,
                        color=data_types_config.get("genes", {}).get(
                            "color", "primary"
                        ),
                        description=data_types_config.get("genes", {}).get(
                            "description", "Genetic and KO-based functional analyses"
                        ),
                        icon=data_types_config.get("genes", {}).get(
                            "icon", "fas fa-dna"
                        ),
                    ),
                    # Metabolic Pathways Section
                    create_entity_accordion_item(
                        entity_id="datatype-pathways",
                        entity_name=data_types_config.get("pathways", {}).get(
                            "name", "Metabolic Pathways"
                        ),
                        ucs=pathways_ucs,
                        color=data_types_config.get("pathways", {}).get(
                            "color", "success"
                        ),
                        description=data_types_config.get("pathways", {}).get(
                            "description", "Pathway-centric metabolic profiling"
                        ),
                        icon=data_types_config.get("pathways", {}).get(
                            "icon", "fas fa-project-diagram"
                        ),
                    ),
                    # Compounds Section
                    create_entity_accordion_item(
                        entity_id="datatype-compounds",
                        entity_name=data_types_config.get("compounds", {}).get(
                            "name", "Compounds"
                        ),
                        ucs=compounds_ucs,
                        color=data_types_config.get("compounds", {}).get(
                            "color", "danger"
                        ),
                        description=data_types_config.get("compounds", {}).get(
                            "description", "Chemical diversity and toxicity analyses"
                        ),
                        icon=data_types_config.get("compounds", {}).get(
                            "icon", "fas fa-flask"
                        ),
                    ),
                    # Samples Section
                    create_entity_accordion_item(
                        entity_id="datatype-samples",
                        entity_name=data_types_config.get("samples", {}).get(
                            "name", "Samples"
                        ),
                        ucs=samples_ucs,
                        color=data_types_config.get("samples", {}).get("color", "info"),
                        description=data_types_config.get("samples", {}).get(
                            "description", "Sample comparison and clustering"
                        ),
                        icon=data_types_config.get("samples", {}).get(
                            "icon", "fas fa-vial"
                        ),
                    ),
                    # Associations & Interactions Section
                    create_entity_accordion_item(
                        entity_id="datatype-interactions",
                        entity_name=data_types_config.get("interactions", {}).get(
                            "name", "Associations & Interactions"
                        ),
                        ucs=interactions_ucs,
                        color=data_types_config.get("interactions", {}).get(
                            "color", "warning"
                        ),
                        description=data_types_config.get("interactions", {}).get(
                            "description", "Network and interaction analyses"
                        ),
                        icon=data_types_config.get("interactions", {}).get(
                            "icon", "fas fa-network-wired"
                        ),
                    ),
                ],
                start_collapsed=True,
                always_open=False,
                flush=True,
            ),
            # Summary footer
            html.Hr(className="my-3"),
            dbc.Alert(
                [
                    html.I(className="fas fa-lightbulb me-2"),
                    html.Strong("Tip: "),
                    f"Total of {len(genes_ucs) + len(pathways_ucs) + len(compounds_ucs) + len(samples_ucs) + len(interactions_ucs)} "
                    "use cases available across all data types. Click any use case to navigate directly to the visualization.",
                ],
                color="success",
                className="mb-0",
            ),
        ]
    )
