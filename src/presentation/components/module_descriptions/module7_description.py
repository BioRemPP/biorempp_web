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
    - Systematic toxicological risk profiling of compounds (toxCSM predictions)
    - Mapping sample KO annotation coverage against toxicologically relevant compounds
    - Support for prioritization and hypothesis generation

    Guiding Questions:
    - 7.1: Comprehensive toxicological prediction landscape
    - 7.2: Regulatory priority alignment
    - 7.3: KO annotation coverage for high-priority compounds
    - 7.4: Annotation-based profiling of sample coverage per compound
    """
    # Module 7 configuration
    module_id = "7"
    title = "Toxicological Risk Assessment and Profiling"

    overview_text = (
        "This module transitions from purely annotation-based analysis to an "
        "application-oriented perspective centered on chemical safety and "
        "toxicological prioritization. Using toxicity predictions from the "
        "toxCSM model, we systematically evaluate the predicted hazard profile "
        "of the compounds present in the system and relate these computational "
        "predictions to the KO annotation coverage of the input samples. The "
        "analyses are structured as a logical sequence of questions that "
        "progress from a broad characterization of the predicted toxicological "
        "landscape to annotation-level profiling of sample coverage per "
        "compound. The objective is to provide a toxicology-aware framework "
        "for guiding hypothesis generation and experimental prioritization."
    )

    # Guiding questions for Module 7
    guiding_questions = [
        {
            "id": "7.1",
            "subtitle": "Toxicological prediction landscape",
            "question": (
                "What is the predicted toxicological landscape? We first "
                "establish a toxicity prediction profile for each compound "
                "across a broad panel of toxicological endpoints predicted by "
                "toxCSM. This comprehensive profiling reveals the predicted "
                "spectrum of potential adverse effects, enabling the "
                "identification of compounds with multi-faceted predicted "
                "toxicity spanning several biological and environmental "
                "categories (e.g., genomic damage, organism-level toxicity, "
                "environmental persistence). The result is a global "
                "toxicological prediction landscape that highlights which "
                "compounds are predicted to pose localized concern and which "
                "are predicted to represent broader hazards, forming the "
                "foundational layer for all subsequent risk-aware analyses. "
                "Note that these are computational predictions and require "
                "experimental validation."
            ),
        },
        {
            "id": "7.2",
            "subtitle": "Regulatory priority alignment",
            "question": (
                "How do these predicted risks align with established "
                "regulatory priorities? To anchor the predictive toxicity data "
                "in real-world decision-making contexts, we evaluate the "
                "concordance between high-risk compounds (as predicted by "
                "toxCSM) and those monitored or flagged by key environmental "
                "and regulatory agencies. This step addresses which predicted "
                "hazards are also recognized as priorities in existing "
                "regulatory frameworks, resulting in a refined set of "
                "'shared regulatory priority compounds' that appear important "
                "from both toxicological prediction and compliance standpoints. "
                "Focusing on this consensus set provides a more targeted basis "
                "for downstream assessments and policy-relevant discussions."
            ),
        },
        {
            "id": "7.3",
            "subtitle": "KO annotation coverage for priority compounds",
            "question": (
                "Which samples show the broadest KO annotation coverage for "
                "high-priority compounds? Once the most critically predicted "
                "compounds have been identified, we examine the KO annotation "
                "coverage of the input samples for those compounds. "
                "For each sample, we quantify the count of unique KO "
                "identifiers co-annotated with priority compounds in the "
                "database. This allows us to identify samples with high "
                "annotation counts for specific high-priority compounds, "
                "providing a direct annotation-level mapping between predicted "
                "high-risk compounds and the samples with the broadest "
                "co-annotation coverage for them."
            ),
        },
        {
            "id": "7.4",
            "subtitle": "Sample annotation profile per compound",
            "question": (
                "How can the annotation profiles of the samples be "
                "characterized relative to priority compounds? We develop a "
                "view of each sample's annotation profile to inform "
                "prioritization by characterizing their KO annotation "
                "coverage along two complementary axes: breadth, "
                "defined as the variety of distinct high-priority compounds "
                "co-annotated with a sample, and depth, defined as the count "
                "and diversity of KO annotations associated with those "
                "compounds. By examining these dimensions, we generate a "
                "descriptive annotation profile for each candidate sample, "
                "supporting the identification of samples with broad or "
                "deep annotation coverage for further experimental "
                "investigation."
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
