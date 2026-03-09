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
    - Identify annotation-based groups and shared co-annotation patterns
    - Reveal molecular and chemical co-occurrence modules

    Guiding Questions:
    - 3.1: KO and compound annotation clustering of samples
    - 3.2: Quantitative similarity between samples
    - 3.3: Molecular and chemical co-occurrence patterns
    """
    # Module 3 configuration
    module_id = "3"
    title = "System Structure: Clustering, Similarity, and Co-occurrence"

    overview_text = (
        "This module moves from describing individual entities to "
        "characterizing the emergent organization of the system as a whole. "
        "After ranking samples and compounds by their KO annotation counts and "
        "co-annotation breadth, the next step is to understand how these "
        "entities group, relate, and co-vary in a higher-dimensional space. "
        "Here, we adopt a systems-level perspective to reveal clusters, "
        "similarity gradients, and co-occurrence patterns that define the "
        "annotation structure of the dataset. These structural insights are "
        "essential for identifying annotation-based sample groups, shared "
        "co-annotation patterns, and recurring molecular co-occurrence "
        "patterns that may be worth investigating experimentally."
    )

    # Guiding questions for Module 3
    guiding_questions = [
        {
            "id": "3.1",
            "subtitle": "KO and compound annotation clusters",
            "question": (
                "How do the samples organize into KO annotation and compound "
                "co-annotation clusters? We first address the global "
                "organization of the samples in both KO and compound "
                "annotation terms by applying multivariate "
                "dimensionality-reduction and clustering methods. "
                "Principal Component Analysis (PCA) is used on KO-based "
                "and compound-based annotation profiles to "
                "visualize dominant axes of variation and to highlight groups "
                "of samples with similar annotation patterns. This is "
                "complemented by hierarchical clustering, generating "
                "dendrograms that reveal nested, fine-grained relationships "
                "among sample groups. Together, these approaches enable the "
                "identification of distinct sample clusters—"
                "groups of samples that appear to share comparable KO "
                "annotation profiles or compound co-annotation repertoires."
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
                "KO annotations (KO Richness) and another based on "
                "shared compound co-annotations (Compound Richness). The "
                "resulting similarity matrices provide statistical support for "
                "the sample groups identified in the clustering step, while "
                "also revealing intermediate degrees of relatedness that may "
                "not be immediately apparent from visual inspection alone."
            ),
        },
        {
            "id": "3.3",
            "subtitle": "Molecular and chemical patterns",
            "question": (
                "What are the underlying molecular and chemical co-occurrence "
                "patterns that drive these sample similarities? To examine "
                "the annotation basis of the observed sample groups, we "
                "investigate co-occurrence patterns among the core molecular "
                "and chemical features. "
                "Using correlograms and related association metrics, we ask "
                "which genes tend to co-occur across samples and which "
                "compounds are frequently co-annotated together. From this, "
                "we characterize potential co-occurrence clusters (sets of "
                "correlated genes or KOs) and compound co-annotation sets "
                "(sets of co-annotated compounds) that recur across samples, "
                "providing an annotation-level rationale for the sample "
                "groupings observed in this module."
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
