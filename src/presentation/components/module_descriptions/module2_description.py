"""
Module 2 Description - BioRemPP v1.0
====================================

Module 2: Exploratory Analysis overview header configuration.

Functions
---------
create_module2_overview_header
    Create Module 2 overview header with context and guiding questions

Notes
-----
- Configured specifically for Module 2: Exploratory Analysis
- Defines 3 guiding questions (UC 2.1, 2.2, 2.3)
- Uses generic module_description component for rendering
"""

from dash import html

from ..composite.module_description import create_module_description


def create_module2_overview_header() -> html.Div:
    """
    Create Module 2 overview header with guiding questions.

    Returns
    -------
    html.Div
        Complete Module 2 overview header component

    Notes
    -----
    Module 2 Focus:
    - Quantitative overview of the KO annotation landscape
    - Ranking by annotation coverage of samples and compounds
    - Baseline characterization of system-wide KO annotation distribution

    Guiding Questions:
    - 2.1: Key annotation characteristics of input samples
    - 2.2: Compounds with broadest sample and gene co-annotation
    - 2.3: System-wide distribution of KO annotation counts
    """
    # Module 2 configuration
    module_id = "2"
    title = "Exploratory Analysis: Ranking the KO Annotation Coverage of Samples and Compounds"

    overview_text = (
        "This module provides a quantitative overview of the annotation "
        "landscape captured by BioRemPP. Before interrogating higher-order "
        "relationships, it is necessary to characterize how KO annotation "
        "counts are distributed across samples and chemical compounds. Here, "
        "we focus on ranking and describing both sides of the system: the "
        "input samples (by their KO annotation counts) and the compounds "
        "(by the number of samples and genes co-annotated with them in the "
        "database). Together, these analyses define a baseline from which "
        "more complex network- and pathway-level interpretations can be "
        "derived."
    )

    # Guiding questions for Module 2
    guiding_questions = [
        {
            "id": "2.1",
            "subtitle": "Sample annotation coverage",
            "question": (
                "What are the key annotation characteristics of the input "
                "samples? We begin by profiling and ranking each sample using "
                "two core metrics: (i) the count of unique KO identifiers "
                "annotated per sample and (ii) the breadth of compound "
                "co-annotations in the database. These metrics "
                "jointly capture the annotation coverage of a sample—the "
                "range of KO identifiers and compounds co-annotated with it "
                "in BioRemPP. The resulting ranking highlights samples with "
                "broad annotation coverage and compound co-annotation, "
                "which may represent useful starting points for deeper "
                "computational or experimental follow-up."
            ),
        },
        {
            "id": "2.2",
            "subtitle": "Compound co-annotation breadth",
            "question": (
                "Which compounds show the broadest co-annotation with samples "
                "and genes in the dataset? In parallel, we invert the "
                "perspective and focus on the chemical scope. We rank "
                "compounds according to the number of unique samples and genes "
                "co-annotated with each compound in the database. "
                "This procedure distinguishes compounds that are widely "
                "co-annotated across many samples from those that appear "
                "in fewer co-annotations. High-ranking compounds in this "
                "dimension may represent well-annotated targets in BioRemPP "
                "and could be prioritized for further investigation."
            ),
        },
        {
            "id": "2.3",
            "subtitle": "System-wide distribution",
            "question": (
                "What is the overall distribution of KO annotation counts? "
                "Finally, we examine the statistical distribution of these "
                "annotation metrics across the full dataset. By visualizing "
                "the variance, skewness, and range of KO annotation counts and "
                "compound co-annotation breadth, we move beyond individual "
                "rankings to characterize global dataset properties—for "
                "example, whether KO annotation counts are concentrated in a "
                "few samples or more evenly distributed. This baseline "
                "characterization is essential for interpreting downstream "
                "analyses of annotation networks and pathways."
            ),
        },
    ]

    # Create module overview header using generic component
    return create_module_description(
        module_id=module_id,
        title=title,
        overview_text=overview_text,
        guiding_questions=guiding_questions,
        section_id="module2-overview-header",
        num_use_cases=5,
    )


# Alias for backward compatibility and consistency
create_module2_description = create_module2_overview_header
