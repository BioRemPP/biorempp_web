"""
Module 1 Description - BioRemPP v1.0 (Enhanced)
===============================================

Module 1: Comparative Assessment of Databases, Samples, and Regulatory Frameworks
overview header configuration with enhanced UI.

Functions
---------
create_module1_overview_header
    Create Module 1 overview header with enhanced visual design

Notes
-----
- Enhanced with Phase 1 & 2 features
- Collapsible overview (default: open)
- Accordion questions (default: open)
- Module-specific icon and color
- Improved typography and spacing
"""

from dash import html

from ..composite.module_description import create_module_description


def create_module1_overview_header() -> html.Div:
    """
    Create Module 1 overview header with enhanced visual design.

    Returns
    -------
    html.Div
        Complete Module 1 overview header component with modern UI

    Notes
    -----
    Module 1 Focus:
    - Database reliability and complementarity assessment
    - Regulatory landscape characterization
    - Sample positioning within a validated, regulation-aware context

    Guiding Questions:
    - 1.1: Data source reliability (BioRemPP validation vs. HADEG and KEGG)
    - 1.2: Regulatory relevance landscape (compound list overlaps)
    - 1.3: Sample annotation overlap with regulatory compound lists
    """
    # Module 1 configuration
    module_id = "1"
    title = "Comparative Assessment of Databases, Samples, and Regulatory Frameworks"

    overview_text = (
        "This module establishes the analytical and methodological foundation "
        "of the entire BioRemPP workflow. Before exploring higher-level "
        "biological or ecological inferences, it is essential to: (i) evaluate "
        "the reliability and complementarity of the reference databases; "
        "(ii) align the resulting annotations with environmentally relevant "
        "regulatory frameworks; and (iii) characterize the input samples within "
        "this validated and regulation-aware landscape. Together, these "
        "analyses can help ensure that subsequent results are biologically "
        "plausible and interpretable within regulatory and annotation contexts."
    )

    # Guiding questions for Module 1
    guiding_questions = [
        {
            "id": "1.1",
            "subtitle": "Data source reliability",
            "question": (
                "What is the reliability of the data sources? We begin by "
                "validating the BioRemPP pipeline against established reference "
                "resources. By systematically comparing its annotations to those "
                "from the HADEG and Degradation pathways from KEGG databases, "
                "we quantify both the agreement between sources and the unique "
                "contribution of the BioRemPP compound-centric approach. This "
                "comparative assessment can enable us to identify shared and "
                "exclusive signals, highlighting how much novel or refined "
                "information is gained by our strategy. The impact of this step "
                "is twofold: it may reinforce the robustness of the pipeline and "
                "can support the originality of the resulting bioremediation-focused "
                "database and analyses."
            ),
        },
        {
            "id": "1.2",
            "subtitle": "Regulatory relevance landscape",
            "question": (
                "What is the landscape of regulatory relevance? Next, we "
                "characterize the regulatory landscape associated with the "
                "annotated compounds. We do so by examining the overlap and "
                "coverage between compound lists from key environmental agencies "
                "and regulatory frameworks. This provides a structured view of "
                "which compounds appear across multiple regulatory lists and "
                "which are unique to specific agencies. In practice, this step "
                "can direct the analytical focus toward compounds with broader "
                "regulatory recognition and monitoring requirements."
            ),
        },
        {
            "id": "1.3",
            "subtitle": "Sample annotation overlap with regulatory compound lists",
            "question": (
                "Which input samples show the broadest annotation overlap with "
                "regulatory compound lists? Finally, we situate each input sample "
                "within this validated and regulation-aware context. We assess "
                "both their KO annotation richness and compound annotation "
                "richness, and compute an annotation-level overlap score that "
                "reflects the percentage of an agency's listed compounds "
                "associated with KOs present in each sample's annotation. "
                "Rather than implying operational readiness, this step "
                "characterizes samples according to their annotation-level "
                "representation within regulatory compound spaces, providing a "
                "basis for prioritizing samples for further exploration and "
                "hypothesis generation."
            ),
        },
    ]

    # Create enhanced module overview header
    return create_module_description(
        module_id=module_id,
        title=title,
        overview_text=overview_text,
        guiding_questions=guiding_questions,
        section_id="module1-overview-header",
        num_use_cases=6,  # Module 1 has 6 use cases
    )


# Alias for backward compatibility and consistency
create_module1_description = create_module1_overview_header
