"""
Module 8 Description - BioRemPP v1.0
====================================

Module 8: Assembly of Functional Consortia overview header configuration.

Functions
---------
create_module8_overview_header
    Create Module 8 overview header with context and guiding questions

Notes
-----
- Configured specifically for Module 8: Assembly of Functional Consortia
- Defines 4 guiding questions (UC 8.1, 8.2, 8.3, 8.4)
- Uses generic module_description component for rendering
"""

from dash import html

from ..composite.module_description import create_module_description


def create_module8_overview_header() -> html.Div:
    """
    Create Module 8 overview header with guiding questions.

    Returns
    -------
    html.Div
        Complete Module 8 overview header component

    Notes
    -----
    Module 8 Focus:
    - Rational design of functional consortia as a multi-objective problem
    - Integrate functional, toxicological, and regulatory insights
    - Balance coverage, completeness, and pathway integrity for applications

    Guiding Questions:
    - 8.1: Minimal coverage strategy (efficiency optimization)
    - 8.2: Specialist selection strategy (functional completeness)
    - 8.3: Pathway completion strategy (process integrity)
    - 8.4: Integration of strategies and trade-offs
    """
    # Module 8 configuration
    module_id = "8"
    title = "Assembly of Functional Consortia"

    overview_text = (
        "The rational design of a functional consortium in BioRemPP is "
        "explicitly framed as a multi-objective optimization problem. Rather "
        "than selecting individual samples in isolation, this module "
        "synthesizes all previous analyses into an integrated "
        "decision-support framework. Here, we use the functional, "
        "toxicological, and regulatory insights obtained in earlier modules "
        "to propose consortia that balance chemical coverage, functional "
        "completeness, and pathway completeness. The ultimate goal is to "
        "translate the analytical results into practical, scenario-aware "
        "strategies for assembling consortia suitable for bioremediation "
        "applications."
    )

    # Guiding questions for Module 8
    guiding_questions = [
        {
            "id": "8.1",
            "subtitle": "Minimal coverage strategy",
            "question": (
                "Optimizing for efficiency: how can we achieve the broadest "
                "possible chemical coverage using the smallest number of "
                "functional units? We begin by identifying non-redundant "
                "‘functional guilds’, defined as groups of samples with "
                "identical or highly similar chemical profiles. We then "
                "formulate and solve a set cover problem to determine the "
                "minimal set of guilds required to cover all compounds within "
                "a given chemical class or target list. The outcome is a "
                "parsimonious consortium blueprint that maximizes functional "
                "breadth while minimizing redundancy and implementation "
                "complexity."
            ),
        },
        {
            "id": "8.2",
            "subtitle": "Specialist selection strategy",
            "question": (
                "Optimizing for functional completeness: how can we maximize "
                "effectiveness against specific targets? For performance- and "
                "completeness-critical scenarios, we define a ‘Completeness "
                "Score’ that quantifies how fully a sample’s genetic toolkit "
                "covers the functions required for broad chemical classes and "
                "for individual high-priority compounds. By ranking samples "
                "according to this score, we identify ‘elite specialists’ that "
                "offer the most complete functional repertoire for a given "
                "task, supporting targeted selection where depth of "
                "capability is more important than breadth."
            ),
        },
        {
            "id": "8.3",
            "subtitle": "Pathway completion strategy",
            "question": (
                "Optimizing for process integrity: how can we ensure that "
                "complete multi-step biological processes can be executed by "
                "the consortium? We examine the distribution of all required "
                "KOs for a target metabolic pathway across the available "
                "samples. Rather than demanding that a single sample encode a "
                "complete pathway, we apply the principle of functional "
                "complementarity, designing consortia in which different "
                "samples contribute distinct segments of the pathway so that "
                "all enzymatic steps needed for complex transformations are "
                "collectively present."
            ),
        },
        {
            "id": "8.4",
            "subtitle": "Integrated consortium profiles and trade-offs",
            "question": (
                "How can these strategies be combined into practical "
                "consortium designs? Finally, we integrate the minimal "
                "coverage, specialist selection, and pathway completion "
                "strategies into coherent consortium profiles. By jointly "
                "considering coverage (breadth), completeness (depth), and "
                "process integrity (complementarity), we characterize each "
                "candidate consortium in terms of its strengths, limitations, "
                "and trade-offs. This integrated view enables users to choose "
                "between alternative designs according to practical criteria "
                "such as operational simplicity, targeted intervention needs, "
                "or robustness requirements for long-term deployments."
            ),
        },
    ]

    # Create module overview header using generic component
    return create_module_description(
        module_id=module_id,
        title=title,
        overview_text=overview_text,
        guiding_questions=guiding_questions,
        section_id="module8-overview-header",
        num_use_cases=7,
    )


# Alias for backward compatibility and consistency
create_module8_description = create_module8_overview_header
