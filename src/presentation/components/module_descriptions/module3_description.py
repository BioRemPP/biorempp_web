"""
Module 3 Description - BioRemPP v1.0
====================================

Module 3: System Structure overview header configuration.

Functions
---------
create_module3_overview_header
    Create Module 3 overview header with context and guiding questions

Notes
-----
- Configured specifically for Module 3: Clustering, Similarity,
  and Co-occurrence
- Defines 3 guiding questions (UC 3.1, 3.2, 3.3)
- Uses generic module_description component for rendering
"""

from dash import html

from ..composite.module_description import create_module_description


def create_module3_overview_header() -> html.Div:
    """
    Create Module 3 overview header with guiding questions.

    Returns
    -------
    html.Div
        Complete Module 3 overview header component

    Notes
    -----
    Module 3 Focus:
    - Characterize emergent system-wide organization
    - Identify functional guilds and shared degradation strategies
    - Reveal molecular and chemical co-occurrence modules

    Guiding Questions:
    - 3.1: Functional and chemical clustering of samples
    - 3.2: Quantitative similarity between samples
    - 3.3: Molecular and chemical co-occurrence patterns
    """
    # Module 3 configuration
    module_id = "3"
    title = "System Structure: Clustering, Similarity, and Co-occurrence"

    overview_text = (
        "This module moves from describing individual entities to "
        "characterizing the emergent organization of the system as a whole. "
        "After ranking samples and compounds by their functional and chemical "
        "potential, the next step is to understand how these entities group, "
        "relate, and co-vary in a higher-dimensional space. Here, we adopt a "
        "systems-level perspective to reveal clusters, similarity gradients, "
        "and co-occurrence patterns that define the functional architecture of "
        "the dataset. These structural insights are essential for identifying "
        "functional guilds, shared degradation strategies, and recurring "
        "molecular 'modules' that may underpin robust bioremediation responses."
    )

    # Guiding questions for Module 3
    guiding_questions = [
        {
            "id": "3.1",
            "subtitle": "Functional and chemical clusters",
            "question": (
                "How do the samples organize into functional and chemical "
                "clusters? We first address the global organization of the "
                "samples in both functional and chemical terms by applying "
                "multivariate dimensionality-reduction and clustering methods. "
                "Principal Component Analysis (PCA) is used on functional "
                "(KO-based) and chemical (compound-based) profiles to "
                "visualize dominant axes of variation and to highlight groups "
                "of samples with similar response patterns. This is "
                "complemented by hierarchical clustering, generating "
                "dendrograms that reveal nested, fine-grained relationships "
                "among sample groups. Together, these approaches enable the "
                "robust identification of distinct 'functional guilds'—"
                "clusters of samples that appear to share comparable metabolic "
                "strategies or chemical degradation repertoires."
            ),
        },
        {
            "id": "3.2",
            "subtitle": "Quantitative sample similarity",
            "question": (
                "What is the quantitative similarity between any two samples? "
                "Once distinct clusters have been defined, we quantify the "
                "strength and structure of these relationships by constructing "
                "correlograms that assign numerical similarity scores to all "
                "pairwise combinations of samples. This analysis is carried "
                "out from two complementary perspectives: one based on shared "
                "functional repertoires (KO Richness) and another based on "
                "shared chemical targets (Compound Richness). The resulting "
                "similarity matrices provide statistical support for the "
                "functional guilds identified in the clustering step, while "
                "also revealing intermediate degrees of relatedness that may "
                "not be immediately apparent from visual inspection alone."
            ),
        },
        {
            "id": "3.3",
            "subtitle": "Molecular and chemical patterns",
            "question": (
                "What are the underlying molecular and chemical patterns that "
                "drive these sample similarities? To elucidate the mechanistic "
                "basis of the observed sample guilds, we examine co-occurrence "
                "patterns among the core molecular and chemical features. "
                "Using correlograms and related association metrics, we ask "
                "which genes tend to co-occur across samples and which "
                "compounds are frequently targeted together. From this, we "
                "infer potential 'metabolic modules' (sets of correlated genes "
                "or functions) and 'chemical suites' (sets of co-targeted "
                "compounds) that likely act as recurrent building blocks "
                "within the system, providing a functional and chemical "
                "rationale for the sample groupings."
            ),
        },
    ]

    # Create module overview header using generic component
    return create_module_description(
        module_id=module_id,
        title=title,
        overview_text=overview_text,
        guiding_questions=guiding_questions,
        section_id="module3-overview-header",
        num_use_cases=7,
    )


# Alias for backward compatibility and consistency
create_module3_description = create_module3_overview_header
