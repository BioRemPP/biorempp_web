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
    - 1.2: Regulatory relevance landscape (priority targets)
    - 1.3: Functional candidate identification (regulatory compliance scoring)
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
        "regulatory frameworks; and (iii) position the input samples within "
        "this validated and regulation-aware landscape. Together, these "
        "analyses ensure that subsequent results are not only biologically "
        "plausible but also interpretable in terms of compliance, priority, "
        "and practical applicability to bioremediation scenarios."
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
                "comparative assessment enables us to identify shared and "
                "exclusive signals, highlighting how much novel or refined "
                "information is gained by our strategy. The impact of this step "
                "is twofold: it reinforces the robustness of the pipeline and "
                "supports the originality of the resulting bioremediation-focused "
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
                "and regulatory frameworks. This transforms raw lists of "
                "compounds into a structured set of 'priority targets', defined "
                "by their regulatory status, environmental concern, or monitoring "
                "requirements. In practice, this step directs the analytical "
                "focus toward compounds with the greatest potential impact on "
                "environmental policy, risk assessment, and regulatory "
                "decision-making."
            ),
        },
        {
            "id": "1.3",
            "subtitle": "Functional candidate identification",
            "question": (
                "Which input samples represent the most valuable functional "
                "candidates? Finally, we situate each input sample within this "
                "validated and regulation-aware context. We assess both their "
                "functional repertoire — measured by KO Richness and Compound "
                "Richness — and their composite 'regulatory compliance score', "
                "derived from the presence and relevance of compounds tied to "
                "environmental regulations. Rather than merely describing the "
                "samples, this step ranks them according to their potential to "
                "address real-world bioremediation challenges and regulatory "
                "demands, thereby identifying the most promising candidates for "
                "follow-up studies, pilot interventions, and environmental "
                "compliance strategies."
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
        num_use_cases=7,  # Module 1 has 7 use cases (UC 1.1 - 1.6, plus regulatory)
    )


# Alias for backward compatibility and consistency
create_module1_description = create_module1_overview_header
