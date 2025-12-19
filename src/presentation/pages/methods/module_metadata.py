"""
Module Metadata - Titles and Descriptions for Each Module

This module contains metadata for all 8 analytical modules in BioRemPP.
"""

MODULE_METADATA = {
    1: {
        "title": "Comparative Assessment of Databases, Samples, and Regulatory Frameworks",
        "short_title": "Database Analysis",
        "description": "Comparative analysis of functional annotations across BioRemPP, HADEG, and KEGG databases, "
        "including regulatory framework compliance and sample diversity assessment.",
        "icon": "📊",
        "color": "#3498db",  # Blue
        "use_case_count": 6,
    },
    2: {
        "title": "Comparative Functional Profiling",
        "short_title": "Functional Profiling",
        "description": "Ranking and statistical analysis of samples based on functional richness, chemical diversity, "
        "and compound-gene associations across different databases.",
        "icon": "📈",
        "color": "#2ecc71",  # Green
        "use_case_count": 5,
    },
    3: {
        "title": "System Structure - Clustering, Similarity, and Co-occurrence",
        "short_title": "System Structure",
        "description": "Multivariate analysis including PCA, hierarchical clustering, and correlation-based similarity "
        "assessments of samples, genes, and compounds.",
        "icon": "🔬",
        "color": "#9b59b6",  # Purple
        "use_case_count": 7,
    },
    4: {
        "title": "Functional and Genetic Profiling",
        "short_title": "Genetic Profiling",
        "description": "KO-centric analysis of metabolic pathways, enzymatic activities, and genetic diversity across "
        "samples using KEGG and HADEG databases.",
        "icon": "🧬",
        "color": "#e74c3c",  # Red
        "use_case_count": 13,
    },
    5: {
        "title": "Network Analysis and Interaction Mapping",
        "short_title": "Network Analysis",
        "description": "Graph-based visualization of gene-compound interactions, sample-compound relationships, "
        "and regulatory relevance using chord diagrams and network layouts.",
        "icon": "🕸️",
        "color": "#f39c12",  # Orange
        "use_case_count": 6,
    },
    6: {
        "title": "Hierarchical and Flow Visualizations",
        "short_title": "Hierarchical Viz",
        "description": "Sankey diagrams and treemaps for visualizing multi-level hierarchies in chemical, enzymatic, "
        "and regulatory-to-molecular interaction flows.",
        "icon": "🌳",
        "color": "#1abc9c",  # Teal
        "use_case_count": 5,
    },
    7: {
        "title": "Toxicological Risk Assessment",
        "short_title": "Toxicology",
        "description": "Integration of ToxCSM predictions with functional data to assess compound toxicity profiles, "
        "regulatory concordance, and sample risk mitigation capacity.",
        "icon": "⚠️",
        "color": "#e67e22",  # Dark Orange
        "use_case_count": 7,
    },
    8: {
        "title": "Functional Completeness and Consortium Design",
        "short_title": "Completeness",
        "description": "Set cover algorithms and completeness scorecards for optimal sample selection and "
        "consortium design based on KO coverage and pathway representation.",
        "icon": "🎯",
        "color": "#34495e",  # Dark Gray
        "use_case_count": 7,
    },
}


def get_module_metadata(module: int) -> dict:
    """
    Get metadata for a specific module.

    Args:
        module: Module number (1-8)

    Returns:
        Dictionary with module metadata.

    Raises:
        ValueError: If module number is invalid.
    """
    if module not in MODULE_METADATA:
        raise ValueError(f"Invalid module number: {module}. Must be 1-8.")

    return MODULE_METADATA[module]


def get_all_modules_metadata() -> dict:
    """
    Get metadata for all modules.

    Returns:
        Dictionary mapping module numbers to metadata.
    """
    return MODULE_METADATA.copy()


def get_module_color(module: int) -> str:
    """
    Get color hex code for a module.

    Args:
        module: Module number (1-8)

    Returns:
        Hex color code string.
    """
    return MODULE_METADATA.get(module, {}).get("color", "#6c757d")


def get_module_icon(module: int) -> str:
    """
    Get emoji icon for a module.

    Args:
        module: Module number (1-8)

    Returns:
        Emoji string.
    """
    return MODULE_METADATA.get(module, {}).get("icon", "📄")
