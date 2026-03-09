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
    - Annotation-based consortium assembly as a multi-objective problem
    - Integrate KO annotation, toxicological prediction, and regulatory insights
    - Balance annotation coverage, KO overlap scores, and pathway annotation
      for hypothesis generation (experimental validation required)

    Guiding Questions:
    - 8.1: Minimal annotation coverage strategy (efficiency)
    - 8.2: High annotation overlap score selection (depth)
    - 8.3: Pathway annotation completion strategy (annotation complementarity)
    - 8.4: Integration of strategies and trade-offs
    """
    # Module 8 configuration
    module_id = "8"
    title = "Assembly of Functional Consortia"

    overview_text = (
        "The annotation-based assembly of candidate consortia in BioRemPP is "
        "explicitly framed as a multi-objective optimization problem at the "
        "annotation level. Rather than selecting individual samples in "
        "isolation, this module synthesizes all previous analyses into an "
        "integrated decision-support framework. Here, we use the KO annotation "
        "counts, toxicological predictions, and regulatory information obtained "
        "in earlier modules to propose candidate consortia that balance "
        "compound annotation coverage, KO annotation overlap scores, and "
        "annotated pathway completeness. These are annotation-level profiles "
        "that require experimental validation before any biological conclusions "
        "can be drawn."
    )

    # Guiding questions for Module 8
    guiding_questions = [
        {
            "id": "8.1",
            "subtitle": "Minimal annotation coverage strategy",
            "question": (
                "Optimizing for annotation efficiency: how can we achieve the "
                "broadest possible compound co-annotation coverage using the "
                "smallest number of samples? We begin by identifying "
                "non-redundant sample groups, defined as samples with identical "
                "or highly similar compound annotation profiles. We then "
                "formulate and solve a set cover problem to determine the "
                "minimal set of sample groups required to cover all compounds "
                "within a given chemical class or target list. The outcome is a "
                "parsimonious candidate consortium that maximizes annotation "
                "breadth while minimizing redundancy."
            ),
        },
        {
            "id": "8.2",
            "subtitle": "High annotation overlap score selection",
            "question": (
                "Optimizing for annotation depth: how can we identify samples "
                "with the highest KO annotation overlap for specific targets? "
                "For annotation-depth-critical scenarios, we define a 'KO "
                "Annotation Overlap Score' that quantifies what percentage of "
                "the KOs annotated for a compound class in the database are "
                "also annotated in a given sample. By ranking samples "
                "according to this score, we identify candidates with the "
                "highest annotation overlap for a given target—supporting "
                "prioritization where depth of annotation is more important "
                "than breadth. Note that annotation overlap does not confirm "
                "functional capacity."
            ),
        },
        {
            "id": "8.3",
            "subtitle": "Pathway annotation completion strategy",
            "question": (
                "Optimizing for annotation complementarity: how can we ensure "
                "that all annotated KOs for a target metabolic pathway are "
                "collectively covered by the candidate consortium? We examine "
                "the distribution of annotated KOs for a target pathway across "
                "the available samples. Rather than requiring a single sample "
                "to be annotated with all pathway KOs, we apply the principle "
                "of annotation complementarity, identifying candidate consortia "
                "in which different samples together cover distinct annotated "
                "KO segments of the pathway so that full pathway KO annotation "
                "is collectively represented."
            ),
        },
        {
            "id": "8.4",
            "subtitle": "Integrated annotation profiles and trade-offs",
            "question": (
                "How can these annotation-based strategies be combined into "
                "candidate consortium profiles? Finally, we integrate the "
                "minimal annotation coverage, high overlap score selection, "
                "and pathway annotation complementarity strategies into "
                "coherent candidate profiles. By jointly considering annotation "
                "breadth, annotation depth, and annotated pathway complementarity, "
                "we characterize each candidate consortium in terms of its "
                "annotation strengths, limitations, and trade-offs. This "
                "integrated view enables users to compare alternative "
                "annotation-level designs according to criteria such as "
                "annotation simplicity, targeted annotation depth, or "
                "pathway annotation completeness. All identified candidates "
                "require experimental validation."
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
