"""
Module 7 Description - BioRemPP v1.0
====================================

Module 7: Toxicological Risk Assessment and Profiling configuration.

Functions
---------
create_module7_overview_header
    Create Module 7 overview header with context and guiding questions

Notes
-----
- Configured specifically for Module 7: Toxicological Risk Assessment
  and Profiling
- Defines 4 guiding questions (UC 7.1, 7.2, 7.3, 7.4)
- Uses generic module_description component for rendering
"""

from dash import html

from ..composite.module_description import create_module_description


def create_module7_overview_header() -> html.Div:
    """
    Create Module 7 overview header with guiding questions.

    Returns
    -------
    html.Div
        Complete Module 7 overview header component

    Notes
    -----
    Module 7 Focus:
    - Toxicology-aware, application-oriented analysis
    - Systematic toxicological risk evaluation of compounds
    - Mapping sample mitigation capabilities against hazards
    - Support for consortium design and deployment strategies

    Guiding Questions:
    - 7.1: Comprehensive toxicological landscape
    - 7.2: Regulatory priority alignment
    - 7.3: Genetic response to high-priority threats
    - 7.4: Characterization of mitigation strategies
    """
    # Module 7 configuration
    module_id = "7"
    title = "Toxicological Risk Assessment and Profiling"

    overview_text = (
        "This module transitions from purely functional annotation to an "
        "application-oriented perspective centered on chemical safety and "
        "risk mitigation. Using toxicity predictions from the toxCSM model, "
        "we systematically evaluate the hazard profile of the compounds "
        "present in the system and relate these risks to the mitigation "
        "capabilities encoded in the input samples. The analyses are "
        "structured as a logical sequence of questions that progress from a "
        "broad characterization of the toxicological landscape to a detailed, "
        "sample-specific profiling of the biological response. The objective "
        "is to provide a toxicology-aware framework for guiding consortium "
        "design and deployment in realistic environmental scenarios."
    )

    # Guiding questions for Module 7
    guiding_questions = [
        {
            "id": "7.1",
            "subtitle": "Toxicological landscape",
            "question": (
                "What is the comprehensive toxicological landscape? We first "
                "establish a 'risk fingerprint' for each compound across a "
                "broad panel of toxicological endpoints predicted by toxCSM. "
                "This comprehensive profiling reveals the full spectrum of "
                "potential adverse effects, enabling the identification of "
                "multi-faceted threats that span several biological and "
                "environmental categories (e.g., genomic damage, "
                "organism-level toxicity, environmental persistence). The "
                "impact of this step is the construction of a global "
                "toxicological landscape that highlights which compounds are "
                "merely of localized concern and which represent systemic, "
                "high-priority hazards, forming the foundational layer for "
                "all subsequent risk-aware analyses."
            ),
        },
        {
            "id": "7.2",
            "subtitle": "Regulatory priority alignment",
            "question": (
                "How do these predicted risks align with established "
                "regulatory priorities? To anchor the predictive toxicity data "
                "in real-world decision-making contexts, we evaluate the "
                "concordance between high-risk compounds and those monitored "
                "or flagged by key environmental and regulatory agencies. This "
                "step addresses which predicted hazards are also recognized as "
                "priorities in existing regulatory frameworks, resulting in a "
                "refined set of 'consensus priority compounds' that are "
                "important from both toxicological and compliance standpoints. "
                "Focusing on this consensus set provides a more targeted and "
                "impactful basis for downstream assessments and "
                "policy-relevant discussions."
            ),
        },
        {
            "id": "7.3",
            "subtitle": "Elite specialist identification",
            "question": (
                "Which samples possess the most potent genetic response to "
                "high-priority threats? Once the most critical chemical "
                "threats have been identified, we shift our attention to the "
                "biological response capacity encoded in the input samples. "
                "For each sample, we quantify the diversity and richness of "
                "genetic functions associated with the degradation or "
                "transformation of consensus priority compounds. This allows "
                "us to identify 'elite specialist' samples that exhibit "
                "particularly strong, focused mitigation potential against "
                "specific high-risk compounds, providing a direct mapping "
                "between high-priority threats and the samples best equipped "
                "to counter them."
            ),
        },
        {
            "id": "7.4",
            "subtitle": "Mitigation strategy profiling",
            "question": (
                "How can the broader mitigation strategies of the samples be "
                "characterized? We develop a view of each sample’s mitigation "
                "profile to inform consortium-level design by characterizing "
                "their capabilities along two complementary axes: breadth, "
                "defined as the variety of distinct high-risk compounds that a "
                "sample can target, and depth, defined as the magnitude and "
                "redundancy of the genetic investment directed toward those "
                "targets. By integrating these dimensions, we generate a "
                "strategic mitigation profile for each candidate sample, "
                "enabling the rational design of microbial consortia that "
                "combine high potency against specific threats with "
                "versatility and functional redundancy for robust performance "
                "under diverse environmental conditions."
            ),
        },
    ]

    # Create module overview header using generic component
    return create_module_description(
        module_id=module_id,
        title=title,
        overview_text=overview_text,
        guiding_questions=guiding_questions,
        section_id="module7-overview-header",
        num_use_cases=7,
    )


# Alias for backward compatibility and consistency
create_module7_description = create_module7_overview_header
