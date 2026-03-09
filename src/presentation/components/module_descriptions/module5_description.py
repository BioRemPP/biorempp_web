"""
Module 5 Description - BioRemPP v1.0
====================================

Module 5: Modeling Interactions overview header configuration.

Functions
---------
create_module5_overview_header
    Create Module 5 overview header with context and guiding questions

Notes
-----
- Configured specifically for Module 5: Modeling Interactions of Samples,
  Genes and Compounds
- Defines 3 guiding questions (UC 5.1, 5.2, 5.3)
- Uses generic module_description component for rendering
"""

from dash import html

from ..composite.module_description import create_module_description


def create_module5_overview_header() -> html.Div:
    """
    Create Module 5 overview header with guiding questions.

    Returns
    -------
    html.Div
        Complete Module 5 overview header component

    Notes
    -----
    Module 5 Focus:
    - Shift from isolated profiles to co-annotation networks
    - Map the co-annotation landscape among samples, genes, and compounds
    - Identify hubs, modules, and motifs in the annotation data
    """
    # Module 5 configuration
    module_id = "5"
    title = "Modeling Interactions of Samples, Genes and Compounds"

    overview_text = (
        "This module shifts the focus from isolated annotation profiles to the "
        "web of co-annotations that connects samples, genes, and compounds. "
        "Having established which KOs and compounds are annotated per sample "
        "(Modules 2–4), we now ask how these annotation components are "
        "organized into co-occurrence networks that can reveal shared "
        "annotation patterns, potential redundancy, and co-annotation "
        "structure. By integrating information across multiple layers—samples, "
        "annotated genes, chemical classes, and regulatory frameworks—we aim "
        "to reconstruct a co-annotation landscape that may be informative for "
        "hypothesis generation and experimental prioritization."
    )

    # Guiding questions for Module 5
    guiding_questions = [
        {
            "id": "5.1",
            "subtitle": "Sample-level co-annotation structure",
            "question": (
                "What is the structure of sample-level co-annotations? We first "
                "examine the highest-level co-annotation patterns to understand "
                "how samples relate to each other and to their chemical and "
                "regulatory context. Chord diagrams are used to address three "
                "complementary questions: (i) how samples cluster based on "
                "shared compound annotation profiles; (ii) which samples are "
                "most co-annotated with particular chemical classes; and "
                "(iii) which samples are most relevant to specific regulatory "
                "agencies or frameworks. The result is a global co-annotation "
                "map that summarizes annotation patterns and shared compound "
                "coverage across samples, revealing broad and narrow annotation "
                "profiles and potential complementarity across the dataset."
            ),
        },
        {
            "id": "5.2",
            "subtitle": "Molecular co-annotation networks",
            "question": (
                "What are the underlying molecular co-annotation networks that "
                "define this landscape? To examine the annotation patterns "
                "driving the observed sample-level structure, we interrogate "
                "the molecular co-annotation layer by constructing networks "
                "whose nodes represent genes and compounds, and whose edges "
                "encode co-annotation relationships—such as shared compound "
                "co-annotations, co-occurrence across samples, or joint "
                "presence in annotated pathways. This perspective allows us "
                "to ask which genes are co-annotated through common compounds, "
                "and which compounds share annotated enzymatic associations. "
                "The resulting networks reveal co-annotation modules and "
                "chemically coherent groups that recur across samples."
            ),
        },
        {
            "id": "5.3",
            "subtitle": "Interaction hubs and annotation motifs",
            "question": (
                "Which co-annotation hubs and motifs are most prominent in "
                "the dataset? Finally, we integrate the sample-level and "
                "molecular-level co-annotation views to identify key elements "
                "within the annotation landscape that appear frequently. By "
                "analyzing network properties such as connectivity, "
                "redundancy, and shared neighbors across samples, genes, and "
                "compounds, we highlight co-annotation hubs (e.g., highly "
                "connected genes or compounds) and recurrent motifs (e.g., "
                "small gene–compound–sample triads) that may represent "
                "annotation patterns of interest. This synthesis enables the "
                "prioritization of candidate samples, annotated pathways, and "
                "chemical targets based on their centrality within the "
                "co-annotation network, providing an annotation-level basis "
                "for experimental hypothesis generation."
            ),
        },
    ]

    # Create module overview header using generic component
    return create_module_description(
        module_id=module_id,
        title=title,
        overview_text=overview_text,
        guiding_questions=guiding_questions,
        section_id="module5-overview-header",
        num_use_cases=6,
    )


# Alias for backward compatibility and consistency
create_module5_description = create_module5_overview_header
