"""
Module 4 Description - BioRemPP v1.0
====================================

Module 4: Functional and Genetic Profiling overview header configuration.

Functions
---------
create_module4_overview_header
    Create Module 4 overview header with context and guiding questions

Notes
-----
- Configured specifically for Module 4: Functional and Genetic Profiling
- Defines 3 guiding questions (UC 4.1, 4.2, 4.3)
- Uses generic module_description component for rendering
"""

from dash import html

from ..composite.module_description import create_module_description


def create_module4_overview_header() -> html.Div:
    """
    Create Module 4 overview header with guiding questions.

    Returns
    -------
    html.Div
        Complete Module 4 overview header component

    Notes
    -----
    Module 4 Focus:
    - Bridge system-level structure with mechanistic detail
    - Characterize functional fingerprints of individual samples
    - Enable function-specific candidate selection and gene-level profiling

    Guiding Questions:
    - 4.1: Comprehensive functional potential per sample
    - 4.2: Function-specific best candidate samples
    - 4.3: Genetic and hierarchical architecture of key functions
    """
    # Module 4 configuration
    module_id = "4"
    title = "Functional and Genetic Profiling"

    overview_text = (
        "This module bridges the gap between system-level structure and "
        "mechanisms. After identifying how samples cluster and rank in terms "
        "of their functional and chemical potential, we now focus on what each "
        "sample can do at a finer resolution and how these capabilities are "
        "encoded at the genetic level. The analyses in this section are "
        "organized to mirror the decision-making process of a researcher or "
        "engineer selecting candidates for specific bioremediation tasks: from "
        "broad functional fingerprints, to targeted candidate selection, down "
        "to gene-level architecture. The goal is to provide actionable, "
        "biologically interpretable profiles that support both practical "
        "solutions and hypothesis-driven experimentation."
    )

    # Guiding questions for Module 4
    guiding_questions = [
        {
            "id": "4.1",
            "subtitle": "Sample functional capabilities",
            "question": (
                "What is the comprehensive functional potential of each "
                "individual sample? We first construct a detailed functional "
                "profile—or 'fingerprint'—for every sample. This involves "
                "characterizing its full repertoire of metabolic pathways and "
                "ranking its most prominent enzymatic activities, typically "
                "using the diversity and abundance of associated genes "
                "(e.g., KO richness) as key indicators. Through this lens, we "
                "obtain a nuanced understanding of each sample's primary "
                "metabolic strengths and specializations. Samples can then be "
                "classified along a continuum from versatile 'generalists', "
                "which encode broad and diverse functional repertoires, to "
                "'specialists', which concentrate their capacity on a narrower "
                "set of highly developed pathways."
            ),
        },
        {
            "id": "4.2",
            "subtitle": "Function-specific candidate selection",
            "question": (
                "For a specific function, which samples are the most capable "
                "candidates? Once individual profiles are established, the "
                "analysis shifts to a task-oriented, comparative perspective. "
                "Instead of asking 'what can each sample do?', we ask: for a "
                "given metabolic pathway, functional category, or chemical "
                "class of interest, which samples are best equipped to perform "
                "the corresponding task? We address this by ranking samples "
                "according to function-specific metrics such as the number of "
                "unique KOs, gene counts, or pathway completeness associated "
                "with the selected function. The result is a direct, "
                "data-driven procedure for identifying elite candidate samples "
                "tailored to predefined bioremediation challenges, such as the "
                "degradation of a particular pollutant or class of compounds."
            ),
        },
        {
            "id": "4.3",
            "subtitle": "Genetic architecture profiling",
            "question": (
                "What is the underlying genetic and hierarchical architecture "
                "of these key functions? To achieve a mechanistic understanding "
                "of the observed potential, we decompose the genetic and "
                "structural basis of high-priority functions. We map detailed "
                "gene inventories associated with selected pathways to "
                "distinguish core genetic components (consistently present "
                "across samples) from accessory or auxiliary elements (present "
                "only in subsets of samples). In parallel, we explore the "
                "hierarchical organization of these pathways—from genes and "
                "reactions to modules and full metabolic routes—and provide "
                "tools to query specific gene–sample and gene–compound "
                "associations. This level of resolution enables the "
                "construction of detailed mechanistic profiles for each "
                "function and sample, supporting hypothesis generation, strain "
                "engineering strategies, and the design of targeted "
                "experimental validations."
            ),
        },
    ]

    # Create module overview header using generic component
    return create_module_description(
        module_id=module_id,
        title=title,
        overview_text=overview_text,
        guiding_questions=guiding_questions,
        section_id="module4-overview-header",
        num_use_cases=13,
    )


# Alias for backward compatibility and consistency
create_module4_description = create_module4_overview_header
