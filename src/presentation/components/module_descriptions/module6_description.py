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
    - Examine hierarchical organization of system components
    - Characterize flow of functional influence across levels
    - Integrate flow-based and hierarchical perspectives for strategy
    """
    # Module 6 configuration
    module_id = "6"
    title = "Hierarchical and Flow-based Functional Analysis"

    overview_text = (
        "While previous modules focus on ranking, clustering, and profiling "
        "individual entities (samples, genes, and compounds), here we "
        "explicitly examine how these components are organized into "
        "hierarchical structures and how information flows between them. By "
        "combining flow-based and hierarchical visualizations, we aim to "
        "reveal dominant routes of interaction, the internal composition of "
        "key categories, and the structural context in which "
        "bioremediation-relevant functions operate."
    )

    # Guiding questions for Module 6
    guiding_questions = [
        {
            "id": "6.1",
            "subtitle": "Pathways of functional influence",
            "question": (
                "What are the primary pathways of functional influence? We "
                "first employ alluvial diagrams to visualize the flow of "
                "functional influence and interaction across different "
                "organizational levels of the system. These diagrams trace "
                "connections from high-level categories—such as regulatory "
                "agencies, chemical classes, or samples—down to specific genes "
                "and compounds. This enables us to identify major routes by "
                "which regulatory priorities, sample capabilities, and "
                "molecular functions intersect, and to map where interactions "
                "concentrate, which categories act as main 'bridges', and which "
                "entities emerge as recurrent transition points along the flow."
            ),
        },
        {
            "id": "6.2",
            "subtitle": "Compositional hierarchy",
            "question": (
                "What is the internal composition of the most important "
                "functional and chemical categories? To deepen this structural "
                "perspective, we examine the internal composition of the "
                "system’s most relevant functional and chemical categories. "
                "Treemaps are used to decompose broad classes—such as compound "
                "families or enzymatic groups—into their constituent elements "
                "and subcategories. This allows us to visualize heterogeneity "
                "within each category, identify where diversity is greatest, "
                "and highlight subclasses that contribute disproportionately to "
                "the overall functional potential, providing detailed "
                "compositional context for the major interaction pathways."
            ),
        },
        {
            "id": "6.3",
            "subtitle": "Integrated strategic perspective",
            "question": (
                "How do flow-based and hierarchical views combine to support "
                "strategic interpretation? Finally, we integrate the "
                "flow-based and hierarchical perspectives to identify leverage "
                "points where influential flows intersect with highly diverse "
                "or enriched subgroups. This combined view helps to pinpoint "
                "specific compound classes, functional modules, or sample "
                "groups that are both structurally central and internally rich, "
                "highlighting natural candidates for prioritization in "
                "downstream analyses, experimental design, and planning of "
                "bioremediation interventions."
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
        num_use_cases=7,
    )


# Alias for backward compatibility and consistency
create_module6_description = create_module6_overview_header
