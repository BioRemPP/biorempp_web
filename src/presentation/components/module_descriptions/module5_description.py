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
    - Shift from isolated profiles to interaction networks
    - Map the interaction landscape among samples, genes, and compounds
    - Identify hubs, modules, and motifs relevant to bioremediation
    """
    # Module 5 configuration
    module_id = "5"
    title = "Modeling Interactions of Samples, Genes and Compounds"

    overview_text = (
        "This module shifts the focus from isolated profiles to the web of "
        "interactions that connects samples, genes, and compounds. Having "
        "established which functions and pathways are present (Modules 2–4), "
        "we now ask how these components are organized into interaction "
        "networks that can reveal specialization, redundancy, and potential "
        "synergies. By integrating information across multiple layers—samples, "
        "functional genes, chemical classes, and regulatory frameworks—we aim "
        "to reconstruct an interaction landscape that is directly relevant to "
        "bioremediation decision-making."
    )

    # Guiding questions for Module 5
    guiding_questions = [
        {
            "id": "5.1",
            "subtitle": "Sample-level interaction structure",
            "question": (
                "What is the structure of sample-level interactions? We first "
                "examine the highest-level interaction patterns to understand "
                "how samples relate to each other and to their chemical and "
                "regulatory context. Chord diagrams are used to address three "
                "complementary questions: (i) how samples cluster based on "
                "shared chemical profiles; (ii) which samples are most "
                "strongly associated with particular chemical classes; and "
                "(iii) which samples are most relevant to specific regulatory "
                "agencies or frameworks. The result is a global interaction map "
                "that summarizes the functional roles and specializations of "
                "each sample, revealing generalists, specialists, and potential "
                "niche complementarity across the dataset."
            ),
        },
        {
            "id": "5.2",
            "subtitle": "Molecular networks and modules",
            "question": (
                "What are the underlying molecular networks that define this "
                "landscape? To uncover the mechanisms driving the observed "
                "sample-level patterns, we interrogate the molecular "
                "interaction layer by constructing networks whose nodes "
                "represent genes and compounds, and whose edges encode "
                "functional relationships—such as shared chemical targets, "
                "co-occurrence in degradation pathways, or joint participation "
                "in specific metabolic routes. This perspective allows us to "
                "ask which genes are functionally linked through common "
                "substrates, and which compounds are related through shared "
                "enzymatic machinery. The resulting networks reveal core "
                "metabolic modules and chemically coherent groups that act as "
                "the building blocks of the broader functional landscape."
            ),
        },
        {
            "id": "5.3",
            "subtitle": "Interaction hubs and bioremediation-relevant motifs",
            "question": (
                "Which interaction hubs and motifs are most relevant for "
                "bioremediation strategies? Finally, we integrate the "
                "sample-level and molecular-level views to identify key "
                "elements within the interaction landscape that are "
                "particularly relevant for practical applications. By "
                "analyzing network properties such as connectivity, "
                "redundancy, and shared neighbors across samples, genes, and "
                "compounds, we highlight interaction hubs (e.g., highly "
                "connected genes or compounds) and recurrent motifs (e.g., "
                "small gene–compound–sample triads) that may represent points "
                "of intervention. This synthesis enables the prioritization of "
                "candidate samples, pathways, and chemical targets not only "
                "based on their individual properties, but also on their "
                "centrality and role within the interaction network, providing "
                "a more informed basis for designing bioremediation consortia "
                "and deployment strategies."
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
        num_use_cases=7,
    )


# Alias for backward compatibility and consistency
create_module5_description = create_module5_overview_header
