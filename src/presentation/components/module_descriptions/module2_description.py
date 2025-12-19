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
    - Quantitative overview of the functional landscape
    - Ranking of samples and compounds by functional potential
    - Baseline characterization of system-wide functional distribution

    Guiding Questions:
    - 2.1: Key performance characteristics of input samples
    - 2.2: Biological definition of high-priority chemical targets
    - 2.3: System-wide distribution of functional potential
    """
    # Module 2 configuration
    module_id = "2"
    title = "Exploratory Analysis: Ranking the Functional Potential of Samples and Compounds"

    overview_text = (
        "This module provides a quantitative overview of the functional "
        "landscape captured by BioRemPP. Before interrogating higher-order "
        "relationships, it is necessary to characterize how functional "
        "potential is distributed across samples and chemical targets. Here, "
        "we focus on ranking and describing both sides of the system: the "
        "input samples (as biological sources of functions) and the compounds "
        "(as substrates, pollutants, or intermediates that drive selective "
        "pressure). Together, these analyses define a baseline from which "
        "more complex network- and pathway-level interpretations can be "
        "derived."
    )

    # Guiding questions for Module 2
    guiding_questions = [
        {
            "id": "2.1",
            "subtitle": "Sample performance",
            "question": (
                "What are the key performance characteristics of the input "
                "samples? We begin by profiling and ranking each sample using "
                "two core metrics: (i) the diversity of unique functional "
                "identifiers (KOs) and (ii) the breadth of compound "
                "interactions inferred from those functions. These metrics "
                "jointly capture the versatility of a sample—its potential to "
                "encode and express a wide range of bioremediation-relevant "
                "activities. The resulting ranking highlights the most "
                "functionally potent 'generalist' samples, which combine high "
                "functional richness with broad compound coverage and "
                "therefore represent prime candidates for deeper experimental "
                "or computational follow-up."
            ),
        },
        {
            "id": "2.2",
            "subtitle": "High-priority chemical targets",
            "question": (
                "What defines a high-priority chemical target from a "
                "biological perspective? In parallel, we invert the "
                "perspective and focus on the chemical scope. We rank "
                "compounds according to the breadth and intensity of the "
                "biological response they elicit, quantified by the number of "
                "unique samples and genes that interact with each compound. "
                "This procedure distinguishes compounds that function as "
                "widely accessible substrates from those that pose more "
                "stringent or complex metabolic challenges. High-ranking "
                "compounds in this dimension may represent critical "
                "bottlenecks, key pollutants of concern, or central hubs in "
                "the bioremediation landscape."
            ),
        },
        {
            "id": "2.3",
            "subtitle": "System-wide distribution",
            "question": (
                "What is the overall distribution of functional potential? "
                "Finally, we examine the statistical distribution of these "
                "performance metrics across the full dataset. By visualizing "
                "the variance, skewness, and range of functional diversity and "
                "compound coverage, we move beyond individual rankings to "
                "characterize global system properties—for example, whether "
                "functional potential is concentrated in a few highly "
                "versatile samples or more evenly distributed. This baseline "
                "characterization is essential for interpreting downstream "
                "analyses of metabolic networks and pathways."
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
        num_use_cases=7,
    )


# Alias for backward compatibility and consistency
create_module2_description = create_module2_overview_header
