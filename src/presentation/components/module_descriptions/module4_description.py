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
    - Bridge system-level structure with annotation detail
    - Characterize KO annotation profiles of individual samples
    - Enable annotation-based candidate selection and gene-level profiling

    Guiding Questions:
    - 4.1: Comprehensive KO annotation coverage per sample
    - 4.2: Annotation-based best candidate samples per function
    - 4.3: Gene and hierarchical annotation architecture of key functions
    """
    # Module 4 configuration
    module_id = "4"
    title = "Functional and Genetic Profiling"

    overview_text = (
        "This module bridges the gap between system-level annotation structure "
        "and mechanistic detail. After identifying how samples cluster and rank "
        "in terms of their KO annotation counts and compound co-annotation "
        "breadth, we now focus on the annotation profile of each sample at a "
        "finer resolution and how these annotations are organized at the gene "
        "level. The analyses in this section are organized to support a "
        "researcher exploring which samples show the broadest annotation "
        "coverage for a given function, pathway, or compound class—from "
        "broad KO annotation profiles, to targeted candidate selection, down "
        "to gene-level annotation architecture. The goal is to provide "
        "annotation-level profiles that support hypothesis-driven "
        "experimentation and the design of targeted experimental validations."
    )

    # Guiding questions for Module 4
    guiding_questions = [
        {
            "id": "4.1",
            "subtitle": "Sample annotation profiles",
            "question": (
                "What is the KO annotation coverage of each individual sample? "
                "We first construct a detailed annotation "
                "profile for every sample. This involves "
                "characterizing its full repertoire of annotated KOs across "
                "pathways and ranking its most represented annotation "
                "categories, typically using KO counts and associated gene "
                "annotations as key indicators. Through this lens, we "
                "obtain a descriptive overview of each sample's primary "
                "annotation strengths. Samples can then be compared along a "
                "continuum from those with broad and diverse KO annotation "
                "coverage to those with annotation concentrated in a narrower "
                "set of pathways or functions."
            ),
        },
        {
            "id": "4.2",
            "subtitle": "Annotation-based candidate selection",
            "question": (
                "For a specific function, which samples show the broadest "
                "annotation coverage? Once individual profiles are established, "
                "the analysis shifts to a task-oriented, comparative "
                "perspective. Instead of asking 'what is each sample annotated "
                "with?', we ask: for a given metabolic pathway, functional "
                "category, or chemical class of interest, which samples have "
                "the highest annotation counts for the corresponding KOs? "
                "We address this by ranking samples "
                "according to annotation-specific metrics such as the number "
                "of unique KOs, gene counts, or annotated pathway components "
                "associated with the selected function. The result is a "
                "data-driven procedure for identifying candidate samples with "
                "broad annotation coverage for predefined functions—such as "
                "KOs co-annotated with a particular compound class."
            ),
        },
        {
            "id": "4.3",
            "subtitle": "Gene annotation architecture",
            "question": (
                "What is the underlying gene annotation structure of these "
                "key functions? To achieve a more detailed understanding "
                "of the observed annotation patterns, we examine the gene "
                "and structural basis of high-priority KO annotations. We map "
                "gene inventories associated with selected pathways to "
                "distinguish KO annotations consistently present "
                "across samples from those present only in subsets. In "
                "parallel, we explore the "
                "hierarchical organization of these annotations—from genes and "
                "reactions to modules and full annotated routes—and provide "
                "tools to query specific gene–sample and gene–compound "
                "co-annotations. This level of resolution enables the "
                "construction of detailed annotation profiles for each "
                "function and sample, supporting hypothesis generation "
                "and the design of targeted experimental validations."
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
