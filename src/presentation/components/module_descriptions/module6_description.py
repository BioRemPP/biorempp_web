"""
Module 6 Description - BioRemPP v1.0
====================================

Module 6: Hierarchical and Flow-based Functional Analysis configuration.

Functions
---------
create_module6_overview_header
    Create Module 6 overview header with context and guiding questions

Notes
-----
- Configured specifically for Module 6: Hierarchical and Flow-based
  Functional Analysis
- Defines 3 guiding questions (UC 6.1, 6.2, 6.3)
- Uses generic module_description component for rendering
"""

from dash import html

from ..composite.module_description import create_module_description


def create_module6_overview_header() -> html.Div:
    """
    Create Module 6 overview header with guiding questions.

    Returns
    -------
    html.Div
        Complete Module 6 overview header component

    Notes
    -----
    Module 6 Focus:
    - Examine hierarchical organization of annotation components
    - Characterize flow of co-annotations across organizational levels
    - Integrate flow-based and hierarchical perspectives for exploration
    """
    # Module 6 configuration
    module_id = "6"
    title = "Hierarchical and Flow-based Functional Analysis"

    overview_text = (
        "While previous modules focus on ranking, clustering, and profiling "
        "individual entities (samples, genes, and compounds), here we "
        "explicitly examine how these components are organized into "
        "hierarchical structures and how co-annotation flows between them. By "
        "combining flow-based and hierarchical visualizations, we aim to "
        "reveal dominant routes of co-annotation, the internal composition of "
        "key annotation categories, and the structural context in which "
        "annotated functions are distributed across the dataset."
    )

    # Guiding questions for Module 6
    guiding_questions = [
        {
            "id": "6.1",
            "subtitle": "Pathways of co-annotation flow",
            "question": (
                "What are the primary pathways of co-annotation flow? We "
                "first employ alluvial diagrams to visualize how co-annotations "
                "are distributed across different organizational levels of the "
                "system. These diagrams trace connections from high-level "
                "categories—such as regulatory agencies, chemical classes, or "
                "samples—down to specific genes and compounds. This enables us "
                "to identify major routes by which regulatory priorities, sample "
                "annotation profiles, and molecular co-annotations intersect, "
                "and to map where co-annotations concentrate, which categories "
                "act as main 'bridges', and which entities emerge as recurrent "
                "transition points along the flow."
            ),
        },
        {
            "id": "6.2",
            "subtitle": "Compositional hierarchy",
            "question": (
                "What is the internal composition of the most important "
                "annotation and chemical categories? To deepen this structural "
                "perspective, we examine the internal composition of the "
                "system's most relevant annotation and chemical categories. "
                "Treemaps are used to decompose broad classes—such as compound "
                "families or annotated enzymatic groups—into their constituent "
                "elements and subcategories. This allows us to visualize "
                "heterogeneity within each category, identify where diversity "
                "is greatest, and highlight subclasses that contribute "
                "disproportionately to overall annotation counts, providing "
                "detailed compositional context for the major co-annotation "
                "pathways."
            ),
        },
        {
            "id": "6.3",
            "subtitle": "Integrated structural perspective",
            "question": (
                "How do flow-based and hierarchical views combine to support "
                "structural interpretation? Finally, we integrate the "
                "flow-based and hierarchical perspectives to identify leverage "
                "points where prominent co-annotation flows intersect with "
                "highly diverse or enriched annotation subgroups. This combined "
                "view helps to pinpoint specific compound classes, annotation "
                "modules, or sample groups that are both structurally central "
                "and internally rich in annotation, highlighting natural "
                "candidates for prioritization in downstream analyses and "
                "experimental design."
            ),
        },
    ]

    # Create module overview header using generic component
    return create_module_description(
        module_id=module_id,
        title=title,
        overview_text=overview_text,
        guiding_questions=guiding_questions,
        section_id="module6-overview-header",
        num_use_cases=5,
    )


# Alias for backward compatibility and consistency
create_module6_description = create_module6_overview_header
