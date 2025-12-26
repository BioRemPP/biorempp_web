"""
FAQ Page - BioRemPP v1.0.0.

Comprehensive Frequently Asked Questions page.

Functions
---------
create_faq_page
    Create complete FAQ page layout with all sections

Notes
-----
- Organized into logical categories
- Searchable content
- Quick navigation links
- Mobile responsive
"""

import dash_bootstrap_components as dbc
from dash import html

from ..components.base import create_footer, create_header
from ..components.composite.faq_item import (
    create_code_block,
    create_faq_item,
    create_faq_note,
)
from ..components.composite.faq_section import (
    create_faq_quick_links,
    create_faq_section,
)

# ==================== FAQ CONSTANTS ====================
# Version and contact information
FAQ_APP_VERSION = "1.0.0-beta"
FAQ_SUPPORT_EMAIL = "biorempp@gmail.com"
FAQ_CANONICAL_URL = "https://biorempp.cloud/"

# Technical limits
FAQ_SESSION_TIMEOUT_HOURS = 4
FAQ_MAX_SAMPLES = 100
FAQ_MAX_TOTAL_KOS = 500000

# Zenodo placeholders (to be updated when DOIs are assigned)
FAQ_ZENODO_WEB_SERVICE_DOI = "[Zenodo DOI pending]"
FAQ_ZENODO_DATABASE_DOI = "[Zenodo DOI pending]"


def create_faq_page() -> html.Div:
    """
    Create FAQ page layout.

    Returns
    -------
    html.Div
        Complete FAQ page with all sections

    Examples
    --------
    >>> faq_layout = create_faq_page()

    Notes
    -----
    Sections included:
    1. Getting Started
    2. File Upload & Validation
    3. Data Processing
    4. Results & Visualization
    5. Scientific Validity & Limitations
    6. Technical Questions
    7. Troubleshooting
    8. Data Privacy & Security
    9. Reproducibility, Versioning & Citation
    10. Licensing & Third-Party Data
    11. Export & Download
    """
    # Header
    header = create_header(show_nav=True, logo_size="60px")

    # Page title and intro
    page_intro = html.Div(
        [
            html.H1(
                [
                    html.I(className="fas fa-question-circle me-3 text-success"),
                    "Frequently Asked Questions",
                ],
                className="text-center mb-3",
            ),
            html.P(
                "Find answers to common questions about BioRemPP. "
                "Browse by category using the quick navigation.",
                className="text-center text-muted mb-4 lead",
            ),
            html.Hr(),
        ],
        className="mb-4",
    )

    # Quick navigation
    section_list = [
        {"title": "Getting Started", "id": "faq-getting-started"},
        {"title": "File Upload & Validation", "id": "faq-file-upload"},
        {"title": "Data Processing", "id": "faq-data-processing"},
        {"title": "Results & Visualization", "id": "faq-results"},
        {"title": "Scientific Validity & Limitations", "id": "faq-scientific-validity"},
        {"title": "Technical Questions", "id": "faq-technical"},
        {"title": "Troubleshooting", "id": "faq-troubleshooting"},
        {"title": "Data Privacy & Security", "id": "faq-privacy"},
        {"title": "Reproducibility, Versioning & Citation", "id": "faq-reproducibility"},
        {"title": "Licensing & Third-Party Data", "id": "faq-licensing"},
        {"title": "Export & Download", "id": "faq-export"},
    ]
    quick_links = create_faq_quick_links(section_list)

    # ==================== SECTION 1: Getting Started ====================
    getting_started_items = [
        create_faq_item(
            question="What is BioRemPP?",
            answer=html.Div(
                [
                    html.P(
                        "BioRemPP (Bioremediation Potential Profile) is a "
                        "comprehensive web service designed to analyze "
                        "bioremediation potential based on genomic "
                        "data."
                    ),
                    html.P(
                        "The system integrates multiple databases (KEGG, "
                        "HadegDB, toxCSM) to provide detailed insights into "
                        "degradation pathways, enzyme activities, and toxicity "
                        "profiles of environmental pollutants."
                    ),
                ]
            ),
            item_id="faq-what-is-biorempp",
        ),
        create_faq_item(
            question="What data do I need to start?",
            answer=html.Div(
                [
                    html.P("You need a TXT file containing:"),
                    html.Ul(
                        [
                            html.Li("Sample names preceded by '>' (one per line)"),
                            html.Li(
                                "KO (KEGG Orthology) numbers listed below each "
                                "sample (one per line)"
                            ),
                            html.Li(
                                "Proper formatting with each sample section "
                                "clearly separated"
                            ),
                        ]
                    ),
                    create_faq_note(
                        "KO annotations can be obtained from tools like "
                        "KEGG BlastKOALA, KofamKOALA, or eggNOG-mapper.",
                        note_type="info",
                    ),
                ]
            ),
            item_id="faq-what-data-needed",
        ),
        create_faq_item(
            question="Is BioRemPP free to use?",
            answer=html.Div(
                [
                    html.P(
                        "Yes. BioRemPP is freely accessible for academic and commercial use via the public web server. "
                        "No login is required, and users can run analyses directly in the browser using their own input tables."
                    ),
                    html.P(
                        "To ensure fair usage and stable availability for the community, the server may enforce practical limits "
                        "(e.g., request size, concurrency, and runtime). These limits are documented, and we recommend batching "
                        "large studies or using the local deployment option when appropriate."
                    ),
                    create_faq_note(
                        "For commercial usage, large-scale/high-throughput workloads, or institutional deployments, "
                        "please contact the team to discuss appropriate access and hosting options.",
                        note_type="info",
                    ),
                ]
            ),
            item_id="faq-is-free",
        ),
        create_faq_item(
            question="Do I need to create an account?",
            answer=(
                "No account creation is required! BioRemPP works with "
                "session-based storage. Your data is processed in real-time "
                "and stored temporarily for the duration of your session. "
                "Once you close your browser or the session expires, all "
                "data is automatically deleted."
            ),
            item_id="faq-need-account",
        ),
        create_faq_item(
            question="How long does analysis take?",
            answer=html.Div(
                [
                    html.P("Processing time depends on several factors, including: "),
                    html.Ul(
                        [
                            html.Li("Number of samples in your file"),
                            html.Li("Total KO annotations across samples"),
                            html.Li("Current server load and traffic"),
                        ]
                    ),
                ]
            ),
            item_id="faq-analysis-time",
        ),
        create_faq_item(
            question="What is the New User Guide?",
            answer=html.Div(
                [
                    html.P(
                        "The New User Guide is an interactive walkthrough designed "
                        "for first-time users. It provides a step-by-step tour of "
                        "BioRemPP's features and workflow."
                    ),
                    html.P("The guide covers:"),
                    html.Ul(
                        [
                            html.Li(
                                "Regulatory References - core principles and frameworks"
                            ),
                            html.Li("User Guide - platform layout and features"),
                            html.Li(
                                "Methods - 56 analytical use cases across 8 modules"
                            ),
                            html.Li(
                                "Official Documentation - technical details and API"
                            ),
                            html.Li("FAQ - common questions and troubleshooting"),
                            html.Li(
                                "Contact - support and collaboration opportunities"
                            ),
                        ]
                    ),
                    create_faq_note(
                        "Access the New User Guide from the homepage by clicking "
                        "'Start Guided Tour' below the 'Start Your Analysis' title.",
                        note_type="success",
                    ),
                ]
            ),
            item_id="faq-new-user-guide",
        ),
        create_faq_item(
            question="What are the 8 analytical modules?",
            answer=html.Div(
                [
                    html.P(
                        "BioRemPP provides 56 use cases organized into 8 specialized "
                        "analytical modules:"
                    ),
                    html.Ol(
                        [
                            html.Li(
                                [
                                    html.Strong("Module 1: "),
                                    "Comparative Assessment - databases, samples, and regulatory frameworks",
                                ]
                            ),
                            html.Li(
                                [
                                    html.Strong("Module 2: "),
                                    "Exploratory Analysis - ranking functional potential",
                                ]
                            ),
                            html.Li(
                                [
                                    html.Strong("Module 3: "),
                                    "System Structure - clustering, similarity, co-occurrence",
                                ]
                            ),
                            html.Li(
                                [
                                    html.Strong("Module 4: "),
                                    "Functional and Genetic Profiling",
                                ]
                            ),
                            html.Li(
                                [
                                    html.Strong("Module 5: "),
                                    "Modeling Interactions - samples, genes, compounds",
                                ]
                            ),
                            html.Li(
                                [html.Strong("Module 6: "), "KEGG Pathway Completeness"]
                            ),
                            html.Li(
                                [
                                    html.Strong("Module 7: "),
                                    "Toxicological Risk Assessment and Profiling",
                                ]
                            ),
                            html.Li(
                                [
                                    html.Strong("Module 8: "),
                                    "Assembly of Functional Consortia",
                                ]
                            ),
                        ]
                    ),
                    create_faq_note(
                        "Visit the Methods page for detailed descriptions of all "
                        "56 use cases and their workflows.",
                        note_type="info",
                    ),
                ]
            ),
            item_id="faq-eight-modules",
        ),
    ]

    section_getting_started = create_faq_section(
        title="Getting Started",
        items=getting_started_items,
        section_icon="fa-play-circle",
        section_id="faq-getting-started",
    )

    # ============== SECTION 2: File Upload & Validation ================
    upload_items = [
        create_faq_item(
            question="What file format is required?",
            answer=html.Div(
                [
                    html.P(
                        "BioRemPP accepts TXT files with the following " "structure:"
                    ),
                    html.Ul(
                        [
                            html.Li("File extension: .txt"),
                            html.Li("Sample names starting with '>' character"),
                            html.Li("KO numbers listed below each sample name"),
                            html.Li("Each KO on a new line (format: K#####)"),
                        ]
                    ),
                    html.P(html.Strong("Example of correct format:"), className="mt-3"),
                    create_code_block(
                        ">Sample1\n"
                        "K00031\n"
                        "K00032\n"
                        "K00090\n"
                        "K00042\n"
                        "K00052\n"
                        ">Sample2\n"
                        "K00031\n"
                        "K00032\n"
                        "K00090\n"
                        "K00042\n"
                        "K00052\n"
                        ">Sample3\n"
                        "K00031\n"
                        "K00032\n"
                        "K00090\n"
                        "K00042\n"
                        "K00052"
                    ),
                ]
            ),
            item_id="faq-file-format",
        ),
        create_faq_item(
            question="How should KO numbers be formatted?",
            answer=html.Div(
                [
                    html.P(
                        "KO numbers should be listed one per line below "
                        "each sample name:"
                    ),
                    html.P(html.Strong("Accepted format:")),
                    create_code_block(
                        ">Sample1\n"
                        "K00001\n"
                        "K00002\n"
                        "K00003\n"
                        ">Sample2\n"
                        "K00004\n"
                        "K00005"
                    ),
                    create_faq_note(
                        "Each KO number must start with 'K' followed by "
                        "5 digits (e.g., K00001). No prefixes like 'KO:' or "
                        "'KEGG:' needed.",
                        note_type="success",
                    ),
                ]
            ),
            item_id="faq-ko-format",
        ),
        create_faq_item(
            question="What is the maximum file size?",
            answer=html.Div(
                [
                    html.P(
                        [
                            "Maximum limits: ",
                            html.Strong(f"{FAQ_MAX_SAMPLES} samples"),
                            " or ",
                            html.Strong(f"{FAQ_MAX_TOTAL_KOS:,} KO numbers total"),
                            " (whichever comes first)",
                        ]
                    ),
                    html.P(
                        "These limits protect server stability and ensure responsive performance "
                        "for all users. Typical datasets are smaller and process quickly."
                    ),
                    create_faq_note(
                        "For larger projects, split inputs into batches or contact the team "
                        f"at {FAQ_SUPPORT_EMAIL} to discuss alternatives.",
                        note_type="warning",
                    ),
                ]
            ),
            item_id="faq-max-file-size",
        ),
        create_faq_item(
            question="Why is my file rejected during validation?",
            answer=html.Div(
                [
                    html.P("Common reasons for file rejection:"),
                    html.Ul(
                        [
                            html.Li(
                                [
                                    html.Strong("No KO numbers: "),
                                    "File must contain at least one valid KO number",
                                ]
                            ),
                            html.Li(
                                [
                                    html.Strong("Invalid format: "),
                                    "File is not in proper TXT format with sample "
                                    "sections",
                                ]
                            ),
                            html.Li(
                                [
                                    html.Strong("Empty samples: "),
                                    "Some samples have names but no KO numbers listed",
                                ]
                            ),
                            html.Li(
                                [
                                    html.Strong("Invalid KO format: "),
                                    "KO numbers not in K##### format (5 digits)",
                                ]
                            ),
                        ]
                    ),
                    create_faq_note(
                        "Check the validation error message for specific "
                        "issues. The system provides detailed feedback.",
                        note_type="info",
                    ),
                ]
            ),
            item_id="faq-file-rejected",
        ),
        create_faq_item(
            question="Can I upload multiple files at once?",
            answer=(
                "Currently, BioRemPP processes one file at a time. "
                "However, you can combine multiple sample sections into a "
                "single TXT file. Each sample (preceded by >) will be "
                "processed individually and results will be aggregated."
            ),
            item_id="faq-multiple-files",
        ),
        create_faq_item(
            question="What annotation tools can I use to generate KO numbers?",
            answer=html.Div(
                [
                    html.P(
                        "To obtain KO annotations from your genomic sequences, "
                        "use one of these recommended tools:"
                    ),
                    html.Ul(
                        [
                            html.Li(
                                [
                                    html.Strong("KEGG BlastKOALA: "),
                                    "Web-based tool for KO assignment using BLAST",
                                ]
                            ),
                            html.Li(
                                [
                                    html.Strong("KofamKOALA: "),
                                    "Profile HMM-based annotation (more sensitive)",
                                ]
                            ),
                            html.Li(
                                [
                                    html.Strong("eggNOG-mapper: "),
                                    "Fast orthology assignments and functional annotation",
                                ]
                            ),
                        ]
                    ),
                    html.P(html.Strong("Typical workflow:"), className="mt-3"),
                    html.Ol(
                        [
                            html.Li(
                                "Submit your protein/nucleotide sequences to annotation tool"
                            ),
                            html.Li("Download KO annotation results"),
                            html.Li("Extract KO numbers (K#####) from results"),
                            html.Li(
                                "Format as TXT file with sample names and KO lists"
                            ),
                            html.Li("Upload to BioRemPP"),
                        ]
                    ),
                    create_faq_note(
                        "All three tools are free for academic use. Choose based on "
                        "your data size and accuracy requirements.",
                        note_type="info",
                    ),
                ]
            ),
            item_id="faq-annotation-tools",
        ),
    ]

    section_upload = create_faq_section(
        title="File Upload & Validation",
        items=upload_items,
        section_icon="fa-upload",
        section_id="faq-file-upload",
    )

    # ================ SECTION 3: Data Processing ====================
    processing_items = [
        create_faq_item(
            question="What happens during data processing?",
            answer=html.Div(
                [
                    html.P("BioRemPP performs multiple integration steps:"),
                    html.Ol(
                        [
                            html.Li(
                                [
                                    html.Strong("KO Extraction: "),
                                    "Identifies all KO annotations from your file",
                                ]
                            ),
                            html.Li(
                                [
                                    html.Strong("KEGG Integration: "),
                                    "Queries KEGG database for pathway information, "
                                    "reactions, and compounds",
                                ]
                            ),
                            html.Li(
                                [
                                    html.Strong("HadegDB Matching: "),
                                    "Cross-references with hydrocarbon degradation "
                                    "database",
                                ]
                            ),
                            html.Li(
                                [
                                    html.Strong("toxCSM Analysis: "),
                                    "Retrieves toxicity predictions for identified "
                                    "compounds",
                                ]
                            ),
                        ]
                    ),
                    create_faq_note(
                        "All processing happens server-side. You don't need to "
                        "install any software.",
                        note_type="success",
                    ),
                ]
            ),
            item_id="faq-what-processing",
        ),
        create_faq_item(
            question="What databases does BioRemPP use?",
            answer=html.Div(
                [
                    html.Ul(
                        [
                            html.Li(
                                [
                                    html.Strong("KEGG: "),
                                    "Kyoto Encyclopedia of Genes and Genomes - "
                                    "metabolic pathways and enzyme functions",
                                ]
                            ),
                            html.Li(
                                [
                                    html.Strong("HADEG: "),
                                    "Hydrocarbon Degradation Database - specialized "
                                    "data on pollutant degradation",
                                ]
                            ),
                            html.Li(
                                [
                                    html.Strong("toxCSM: "),
                                    "Toxicity prediction database using machine "
                                    "learning models",
                                ]
                            ),
                        ]
                    ),
                ]
            ),
            item_id="faq-databases",
        ),
        create_faq_item(
            question="What if processing fails or gets stuck?",
            answer=html.Div(
                [
                    html.P("If processing fails or appears stuck:"),
                    html.Ol(
                        [
                            html.Li("Wait at least 5 minutes for large files"),
                            html.Li("Check your internet connection"),
                            html.Li("Refresh the page and try again"),
                            html.Li(
                                "If problem persists, try with a smaller file first"
                            ),
                        ]
                    ),
                    create_faq_note(
                        "Error messages will appear if something goes wrong. "
                        "Take a screenshot and contact support if needed.",
                        note_type="warning",
                    ),
                ]
            ),
            item_id="faq-processing-fails",
        ),
        create_faq_item(
            question="What are the integrated databases and their specific purposes?",
            answer=html.Div(
                [
                    html.P(
                        "BioRemPP integrates four specialized databases, each serving "
                        "a unique analytical purpose:"
                    ),
                    html.Ul(
                        [
                            html.Li(
                                [
                                    html.Strong("BioRemPP Database: "),
                                    "Curated bioremediation-specific data linking KO annotations "
                                    "to degradation compounds, enzyme activities, and regulatory "
                                    "classifications (IARC, EPA, ATSDR, WFD, PSL, EPC, CONAMA)",
                                ]
                            ),
                            html.Li(
                                [
                                    html.Strong("KEGG (Kyoto Encyclopedia): "),
                                    "Comprehensive metabolic pathway database providing reactions, "
                                    "compounds, and enzyme functions for pathway completeness analysis",
                                ]
                            ),
                            html.Li(
                                [
                                    html.Strong("HADEG (Hydrocarbon Degradation): "),
                                    "Specialized database focused on hydrocarbon and pollutant "
                                    "degradation pathways with detailed enzyme-substrate relationships",
                                ]
                            ),
                            html.Li(
                                [
                                    html.Strong("ToxCSM: "),
                                    "Machine learning-based toxicity prediction database with "
                                    "66 toxicity endpoints across 5 super-categories (Nuclear Response, "
                                    "Stress Response, Genotoxicity, Environmental, Organ Toxicity)",
                                ]
                            ),
                        ]
                    ),
                    create_faq_note(
                        "All databases are automatically queried during processing. "
                        "Results show only compounds that match your KO annotations.",
                        note_type="success",
                    ),
                ]
            ),
            item_id="faq-integrated-databases",
        ),
        create_faq_item(
            question="What is the difference between display data and raw data?",
            answer=html.Div(
                [
                    html.P(
                        "BioRemPP uses different data formats optimized for specific purposes:"
                    ),
                    html.P(html.Strong("Display Data (for visualizations):")),
                    html.Ul(
                        [
                            html.Li("Optimized format for charts and graphs"),
                            html.Li(
                                "Example: ToxCSM long format (5 columns) for heatmaps"
                            ),
                            html.Li(
                                "Columns: Sample, cpd, endpoint, value, super_category"
                            ),
                            html.Li("Easier to plot and analyze trends"),
                        ]
                    ),
                    html.P(html.Strong("Raw Data (for downloads):")),
                    html.Ul(
                        [
                            html.Li("Complete merged results with all database fields"),
                            html.Li(
                                "Example: ToxCSM wide format (67 columns) for analysis"
                            ),
                            html.Li("Includes Sample column for traceability"),
                            html.Li("Contains all value_* and label_* columns"),
                            html.Li(
                                "Suitable for external analysis (R, Python, Excel)"
                            ),
                        ]
                    ),
                    create_faq_note(
                        "Download buttons provide raw data. Tables and charts use "
                        "display-optimized formats.",
                        note_type="info",
                    ),
                ]
            ),
            item_id="faq-data-formats",
        ),
        create_faq_item(
            question="How does the Sample column work for traceability?",
            answer=html.Div(
                [
                    html.P(
                        "The Sample column is a key traceability feature that links "
                        "all results back to your original input samples."
                    ),
                    html.P(html.Strong("How it works:")),
                    html.Ol(
                        [
                            html.Li(
                                "Your input file contains sample names (e.g., >Sample1, >Sample2)"
                            ),
                            html.Li(
                                "Each KO is associated with its sample during processing"
                            ),
                            html.Li(
                                "When KOs match database entries, the Sample name is preserved"
                            ),
                            html.Li("All downloaded data includes the Sample column"),
                        ]
                    ),
                    html.P(html.Strong("Benefits:")),
                    html.Ul(
                        [
                            html.Li(
                                "Track which compounds/enzymes belong to which samples"
                            ),
                            html.Li("Compare bioremediation potential across samples"),
                            html.Li("Filter and analyze sample-specific results"),
                            html.Li("Maintain data provenance for publications"),
                        ]
                    ),
                    create_faq_note(
                        "The Sample column appears in all raw data downloads but may "
                        "be aggregated in some visualizations for clarity.",
                        note_type="success",
                    ),
                ]
            ),
            item_id="faq-sample-column",
        ),
    ]

    section_processing = create_faq_section(
        title="Data Processing",
        items=processing_items,
        section_icon="fa-cogs",
        section_id="faq-data-processing",
    )

    # ============== SECTION 4: Results & Visualization ===============
    results_items = [
        create_faq_item(
            question="How do I interpret the results?",
            answer=html.Div(
                [
                    html.P("Results are organized into 8 analytical modules:"),
                    html.Ul(
                        [
                            html.Li(
                                [
                                    html.Strong("Module 1: "),
                                    "Comparative Assessment of Databases, Samples, and Regulatory Frameworks",
                                ]
                            ),
                            html.Li(
                                [
                                    html.Strong("Module 2: "),
                                    "Exploratory Analysis: Ranking the Functional Potential of Samples and Compounds",
                                ]
                            ),
                            html.Li(
                                [
                                    html.Strong("Module 3: "),
                                    "System Structure: Clustering, Similarity, and Co-occurrence",
                                ]
                            ),
                            html.Li(
                                [
                                    html.Strong("Module 4: "),
                                    "Functional and Genetic Profiling",
                                ]
                            ),
                            html.Li(
                                [
                                    html.Strong("Module 5: "),
                                    "Modeling Interactions of Samples, Genes and Compounds",
                                ]
                            ),
                            html.Li(
                                [html.Strong("Module 6: "), "KEGG Pathway Completeness"]
                            ),
                            html.Li(
                                [
                                    html.Strong("Module 7: "),
                                    "Toxicological Risk Assessment and Profiling",
                                ]
                            ),
                            html.Li(
                                [
                                    html.Strong("Module 8: "),
                                    "Assembly of Functional Consortia",
                                ]
                            ),
                        ]
                    ),
                    html.P(
                        "Each module provides interactive visualizations and "
                        "downloadable data tables.",
                        className="mt-2",
                    ),
                ]
            ),
            item_id="faq-interpret-results",
        ),
        create_faq_item(
            question="What types of visualizations are available?",
            answer=html.Div(
                [
                    html.P(
                        "BioRemPP offers a wide range of interactive visualizations to explore results:"
                    ),
                    html.Ul(
                        [
                            html.Li(
                                "Heatmaps (including scored & faceted) - pathway and compound completeness, scored comparisons"
                            ),
                            html.Li(
                                "Bar charts & Stacked bar charts - frequency distributions and group comparisons"
                            ),
                            html.Li(
                                "Box & Scatter plots - distribution views and pairwise comparisons"
                            ),
                            html.Li(
                                "Dot plots & Density plots - point-level summaries and smoothed distributions"
                            ),
                            html.Li(
                                "Correlograms & PCA plots - correlation matrices and dimensionality reduction visualizations"
                            ),
                            html.Li(
                                "Treemaps & Sunburst charts - hierarchical enzyme / category breakdowns"
                            ),
                            html.Li(
                                "Network graphs & Sankey diagrams - pathway interactions and flow/transfer visualizations"
                            ),
                            html.Li(
                                "Chord diagrams - relationships between groups or categories"
                            ),
                            html.Li(
                                "Radar charts - multi-metric profile comparisons across samples or groups"
                            ),
                            html.Li(
                                "Hierarchical clustering & Dendrograms - cluster structure and sample grouping"
                            ),
                            html.Li(
                                "UpSet plots & Frozenset-style set views - set intersections and shared features across samples"
                            ),
                        ]
                    ),
                    create_faq_note(
                        "All charts are interactive: hover for details, zoom, pan, filter and download images or raw data.",
                        note_type="success",
                    ),
                ]
            ),
            item_id="faq-visualizations",
        ),
        create_faq_item(
            question="Can I customize the visualizations?",
            answer=html.Div(
                [
                    html.P(
                        [
                            "Yes! All visualizations use ",
                            html.Strong("Plotly's interactive features"),
                            ":",
                        ]
                    ),
                    html.Ul(
                        [
                            html.Li(
                                [
                                    html.Strong("Hover: "),
                                    "View detailed data points and values",
                                ]
                            ),
                            html.Li(
                                [
                                    html.Strong("Zoom: "),
                                    "Click and drag to zoom into specific areas",
                                ]
                            ),
                            html.Li(
                                [
                                    html.Strong("Pan: "),
                                    "Drag to move around zoomed charts",
                                ]
                            ),
                            html.Li(
                                [
                                    html.Strong("Reset: "),
                                    "Double-click to reset view to original",
                                ]
                            ),
                            html.Li(
                                [
                                    html.Strong("Export: "),
                                    "Use Plotly menu (top-right) to save chart images",
                                ]
                            ),
                        ]
                    ),
                    create_faq_note(
                        "Hover over the top-right corner of any chart to access "
                        "Plotly's interactive toolbar with download options.",
                        note_type="success",
                    ),
                ]
            ),
            item_id="faq-customize-viz",
        ),
        create_faq_item(
            question="How do I navigate between modules?",
            answer=html.Div(
                [
                    html.P("Use the navigation sidebar (left side):"),
                    html.Ul(
                        [
                            html.Li("Click module names to expand/collapse"),
                            html.Li("Each module shows available use cases"),
                            html.Li("Green highlights indicate active module"),
                            html.Li("Scroll within modules to see all options"),
                        ]
                    ),
                    create_faq_note(
                        "Tip: Use CTRL+F to search for specific analyses "
                        "across all modules.",
                        note_type="info",
                    ),
                ]
            ),
            item_id="faq-navigate-modules",
        ),
        create_faq_item(
            question="What is the Analysis Suggestions panel?",
            answer=html.Div(
                [
                    html.P(
                        "The Analysis Suggestions panel is a guided workflow feature "
                        "located in the bottom of the Results page."
                    ),
                    html.P("Key features:"),
                    html.Ul(
                        [
                            html.Li("Provides step-by-step analytical workflows"),
                            html.Li("Suggests next steps based on your data"),
                            html.Li("Links directly to relevant use cases"),
                            html.Li("Helps navigate the 56 available analyses"),
                        ]
                    ),
                    create_faq_note(
                        "Look for the floating panel in the bottom. "
                        "Click to expand and see suggested analyses for your dataset.",
                        note_type="success",
                    ),
                ]
            ),
            item_id="faq-analysis-suggestions",
        ),
        create_faq_item(
            question="How do I download complete database tables?",
            answer=html.Div(
                [
                    html.P(
                        "Each database section (BioRemPP, HADEG, KEGG, ToxCSM) has a "
                        "'Download Data' button in the header."
                    ),
                    html.P(html.Strong("To download:")),
                    html.Ol(
                        [
                            html.Li("Navigate to the database section in Results page"),
                            html.Li(
                                "Click 'Download Data' button (next to section title)"
                            ),
                            html.Li("Choose format: CSV, Excel (.xlsx), or JSON"),
                            html.Li("File downloads automatically"),
                        ]
                    ),
                    html.P(html.Strong("Downloaded data includes:")),
                    html.Ul(
                        [
                            html.Li("Your samples merged with database matches"),
                            html.Li("Sample column for traceability"),
                            html.Li(
                                "All database fields (e.g., 67 columns for ToxCSM)"
                            ),
                            html.Li("Only compounds that matched your input"),
                        ]
                    ),
                    create_faq_note(
                        "This is different from chart downloads. Database downloads "
                        "provide complete raw data for external analysis.",
                        note_type="info",
                    ),
                ]
            ),
            item_id="faq-database-downloads",
        ),
        create_faq_item(
            question="What are the regulatory frameworks referenced in results?",
            answer=html.Div(
                [
                    html.P(
                        "BioRemPP integrates seven major regulatory frameworks that "
                        "classify environmental pollutants:"
                    ),
                    html.Ul(
                        [
                            html.Li(
                                "IARC - International Agency for Research on Cancer"
                            ),
                            html.Li("EPA - U.S. Environmental Protection Agency"),
                            html.Li(
                                "ATSDR - Agency for Toxic Substances and Disease Registry"
                            ),
                            html.Li("WFD - Water Framework Directive (EU)"),
                            html.Li("PSL - Priority Substances List (Canada)"),
                            html.Li("EPC - Environmental Priority Chemicals"),
                            html.Li("CONAMA - National Environment Council (Brazil)"),
                        ]
                    ),
                    create_faq_note(
                        "Visit the Regulatory References page for detailed information "
                        "about each framework and their classification criteria.",
                        note_type="info",
                    ),
                ]
            ),
            item_id="faq-regulatory-frameworks",
        )
    ]

    section_results = create_faq_section(
        title="Results & Visualization",
        items=results_items,
        section_icon="fa-chart-bar",
        section_id="faq-results",
    )

    # ======= SECTION 5: Scientific Validity & Limitations ===========
    scientific_validity_items = [
        create_faq_item(
            question="What does 'bioremediation potential' mean in BioRemPP?",
            answer=html.Div(
                [
                    html.P(
                        "BioRemPP provides functional inference based on KO "
                        "(KEGG Orthology) annotation evidence and curated mappings "
                        "to bioremediation-relevant pathways and enzymes."
                    ),
                    html.P(html.Strong("Important clarifications:")),
                    html.Ul(
                        [
                            html.Li(
                                "Analysis are based on genomic potential (presence of genes)"
                            ),
                            html.Li(
                                "Do NOT prove actual in situ degradation activity"
                            ),
                            html.Li(
                                "Do NOT indicate gene expression levels or enzyme activity"
                            ),
                            html.Li(
                                "Do NOT account for environmental factors (pH, temperature, etc.)"
                            ),
                        ]
                    ),
                    create_faq_note(
                        "BioRemPP identifies genetic capacity for bioremediation, "
                        "not actual degradation performance. Wet-lab or field validation "
                        "is required to confirm functional activity.",
                        note_type="warning",
                    ),
                ]
            ),
            item_id="faq-what-is-bioremediation-potential",
        ),
        create_faq_item(
            question="Does BioRemPP experimentally validate degradation or enzyme activity?",
            answer=html.Div(
                [
                    html.P(
                        [
                            html.Strong("No."),
                            " BioRemPP is a computational inference tool that predicts "
                            "bioremediation potential based on genomic annotations.",
                        ]
                    ),
                    html.P("What BioRemPP does:"),
                    html.Ul(
                        [
                            html.Li(
                                "Identifies genes/enzymes potentially involved in degradation pathways"
                            ),
                            html.Li(
                                "Maps KO annotations to known bioremediation functions"
                            ),
                            html.Li(
                                "Assesses pathway completeness based on gene presence"
                            ),
                        ]
                    ),
                    html.P("What BioRemPP does NOT do:"),
                    html.Ul(
                        [
                            html.Li("Measure actual enzyme activity"),
                            html.Li("Confirm gene expression"),
                            html.Li("Validate degradation in laboratory or field conditions"),
                            html.Li("Account for regulatory mechanisms or metabolic flux"),
                        ]
                    ),
                    create_faq_note(
                        "All predictions require experimental validation through "
                        "wet-lab studies, field trials, or direct enzymatic assays.",
                        note_type="warning",
                    ),
                ]
            ),
            item_id="faq-experimental-validation",
        ),
        create_faq_item(
            question="What are common sources of false positives and false negatives?",
            answer=html.Div(
                [
                    html.P(
                        "Like all bioinformatics tools, BioRemPP predictions are subject "
                        "to several sources of error:"
                    ),
                    html.P(html.Strong("False Positives (over-prediction):")),
                    html.Ul(
                        [
                            html.Li(
                                [
                                    html.Strong("Annotation errors: "),
                                    "Incorrect KO assignments from annotation tools",
                                ]
                            ),
                            html.Li(
                                [
                                    html.Strong("Contamination: "),
                                    "Contaminant sequences in MAGs/metagenomes",
                                ]
                            ),
                            html.Li(
                                [
                                    html.Strong("Pathway redundancy: "),
                                    "Alternative pathways with overlapping KOs",
                                ]
                            ),
                            html.Li(
                                [
                                    html.Strong("Non-expressed genes: "),
                                    "Genes present but not expressed in specific conditions",
                                ]
                            ),
                        ]
                    ),
                    html.P(html.Strong("False Negatives (under-prediction):")),
                    html.Ul(
                        [
                            html.Li(
                                [
                                    html.Strong("Incomplete genomes/MAGs: "),
                                    "Missing genes due to assembly/binning gaps",
                                ]
                            ),
                            html.Li(
                                [
                                    html.Strong("Annotation sensitivity: "),
                                    "KO annotation tools miss divergent homologs",
                                ]
                            ),
                            html.Li(
                                [
                                    html.Strong("Novel enzymes: "),
                                    "Undiscovered or poorly characterized degradation pathways",
                                ]
                            ),
                            html.Li(
                                [
                                    html.Strong("Database coverage: "),
                                    "KEGG/HADEG may not cover all known pathways",
                                ]
                            ),
                        ]
                    ),
                    create_faq_note(
                        "Interpret results cautiously. Cross-validate predictions with "
                        "multiple annotation tools and literature evidence when possible.",
                        note_type="info",
                    ),
                ]
            ),
            item_id="faq-false-positives-negatives",
        ),
        create_faq_item(
            question="Can BioRemPP be used for metagenomes, MAGs, or incomplete assemblies?",
            answer=html.Div(
                [
                    html.P(
                        [
                            html.Strong("Yes, with important caveats."),
                            " BioRemPP accepts any KO annotations, regardless of source.",
                        ]
                    ),
                    html.P(html.Strong("Recommended practices:")),
                    html.Ul(
                        [
                            html.Li(
                                [
                                    html.Strong("Completeness assessment: "),
                                    "Check genome/MAG completeness (CheckM, BUSCO) before interpretation",
                                ]
                            ),
                            html.Li(
                                [
                                    html.Strong("Contamination filtering: "),
                                    "Remove contaminants to reduce false positives",
                                ]
                            ),
                            html.Li(
                                [
                                    html.Strong("Pathway completeness interpretation: "),
                                    "Incomplete genomes will show lower pathway completeness",
                                ]
                            ),
                            html.Li(
                                [
                                    html.Strong("Conservative thresholds: "),
                                    "Use higher confidence thresholds for incomplete data",
                                ]
                            ),
                        ]
                    ),
                    html.P(html.Strong("Quality guidelines:")),
                    html.Ul(
                        [
                            html.Li("MAGs: ≥70% completeness, <10% contamination recommended"),
                            html.Li("Metagenomes: Consider coverage and assembly quality"),
                            html.Li(
                                "Incomplete assemblies: Interpret pathway completeness with extreme caution"
                            ),
                        ]
                    ),
                    create_faq_note(
                        "Lower genome completeness = higher risk of false negatives. "
                        "Always report genome quality metrics alongside BioRemPP results.",
                        note_type="warning",
                    ),
                ]
            ),
            item_id="faq-metagenomes-mags",
        ),
        create_faq_item(
            question="How should toxCSM predictions be interpreted?",
            answer=html.Div(
                [
                    html.P(
                        "toxCSM provides machine learning-based toxicity predictions "
                        "for compounds. These are computational estimates, not experimental measurements."
                    ),
                    html.P(html.Strong("Key limitations:")),
                    html.Ul(
                        [
                            html.Li(
                                [
                                    html.Strong("Predictions vs. measurements: "),
                                    "toxCSM predicts toxicity; does not replace experimental assays",
                                ]
                            ),
                            html.Li(
                                [
                                    html.Strong("Endpoint specificity: "),
                                    "66 endpoints across 5 categories; each has different reliability",
                                ]
                            ),
                            html.Li(
                                [
                                    html.Strong("Model applicability domain: "),
                                    "Predictions less reliable for compounds outside training data",
                                ]
                            ),
                            html.Li(
                                [
                                    html.Strong("Species/context specificity: "),
                                    "Toxicity varies by organism, dose, exposure route",
                                ]
                            ),
                        ]
                    ),
                    html.P(html.Strong("Safe usage guidelines:")),
                    html.Ul(
                        [
                            html.Li("Use for prioritization and screening, not definitive assessment"),
                            html.Li("Cross-reference with experimental toxicity databases (EPA, ECHA)"),
                            html.Li("Consider multiple endpoints, not just one"),
                            html.Li("Report confidence scores and model versions"),
                        ]
                    ),
                    create_faq_note(
                        "NEVER use toxCSM predictions for clinical decisions, "
                        "regulatory submissions, or risk assessment without experimental validation.",
                        note_type="danger",
                    ),
                ]
            ),
            item_id="faq-toxcsm-interpretation",
        ),
        create_faq_item(
            question="How is pathway completeness defined and what are the caveats?",
            answer=html.Div(
                [
                    html.P(
                        "Pathway completeness in BioRemPP is calculated based on "
                        "presence/absence of KO annotations mapped to KEGG pathway definitions."
                    ),
                    html.P(html.Strong("Calculation method:")),
                    html.Ul(
                        [
                            html.Li("Identify required KOs for each pathway (from KEGG)"),
                            html.Li("Check which KOs are present in your sample"),
                            html.Li("Calculate: (KOs present / Total KOs required) × 100%"),
                        ]
                    ),
                    html.P(html.Strong("Important caveats:")),
                    html.Ul(
                        [
                            html.Li(
                                [
                                    html.Strong("Presence ≠ Activity: "),
                                    "Gene presence does not guarantee expression or enzymatic flux",
                                ]
                            ),
                            html.Li(
                                [
                                    html.Strong("Binary logic: "),
                                    "Does not account for gene copy number, expression levels, or regulation",
                                ]
                            ),
                            html.Li(
                                [
                                    html.Strong("KEGG pathway definitions: "),
                                    "May not reflect all biological pathway variants or alternatives",
                                ]
                            ),
                            html.Li(
                                [
                                    html.Strong("Essential vs. optional steps: "),
                                    "All KOs weighted equally; critical bottlenecks not distinguished",
                                ]
                            ),
                        ]
                    ),
                    html.P(html.Strong("Interpretation guidelines:")),
                    html.Ul(
                        [
                            html.Li("100% completeness: All genes present (potential capacity)"),
                            html.Li("70-99%: Likely functional, but missing steps may limit activity"),
                            html.Li("<70%: Incomplete; interpret with caution"),
                            html.Li("Consider alternative pathways and redundancy"),
                        ]
                    ),
                    create_faq_note(
                        "Pathway completeness indicates genetic potential, not metabolic flux. "
                        "Experimental validation (e.g., metabolomics, enzyme assays) required to "
                        "confirm functional activity.",
                        note_type="warning",
                    ),
                ]
            ),
            item_id="faq-pathway-completeness",
        ),
    ]

    section_scientific_validity = create_faq_section(
        title="Scientific Validity & Limitations",
        items=scientific_validity_items,
        section_icon="fa-flask",
        section_id="faq-scientific-validity",
    )

    # ================ SECTION 6: Technical Questions =================
    technical_items = [
        create_faq_item(
            question="What browsers are supported?",
            answer=html.Div(
                [
                    html.P(
                        "BioRemPP requires a modern browser with JavaScript enabled:"
                    ),
                    html.P(html.Strong("Fully Supported:")),
                    html.Ul(
                        [
                            html.Li(
                                [
                                    html.Strong("Google Chrome 90+: "),
                                    "Recommended - best performance and fully tested",
                                ]
                            ),
                            html.Li(
                                [
                                    html.Strong("Mozilla Firefox 88+: "),
                                    "Fully supported with excellent performance",
                                ]
                            ),
                            html.Li(
                                [
                                    html.Strong("Microsoft Edge 90+: "),
                                    "Chromium-based, fully supported",
                                ]
                            ),
                            html.Li(
                                [
                                    html.Strong("Safari 14+: "),
                                    "Supported with minor limitations on some visualizations",
                                ]
                            ),
                        ]
                    ),
                    html.P(html.Strong("Not Supported:")),
                    html.Ul(
                        [
                            html.Li("Internet Explorer (any version) - deprecated"),
                            html.Li("Browsers with JavaScript disabled"),
                            html.Li("Very old browser versions (pre-2020)"),
                        ]
                    ),
                    create_faq_note(
                        "For best experience: Chrome/Firefox latest version, "
                        "screen resolution ≥ 1366x768, JavaScript enabled.",
                        note_type="success",
                    ),
                ]
            ),
            item_id="faq-browsers",
        ),
        create_faq_item(
            question="Does BioRemPP work on mobile devices?",
            answer=html.Div(
                [
                    html.P(
                        "BioRemPP is responsive and technically works on mobile devices, "
                        "but the experience is optimized for desktop use."
                    ),
                    html.P(html.Strong("Limitations on mobile:")),
                    html.Ul(
                        [
                            html.Li(
                                "Complex visualizations difficult to interact with on small screens"
                            ),
                            html.Li(
                                "Heatmaps and network graphs require larger displays"
                            ),
                            html.Li("File upload may be cumbersome on mobile browsers"),
                            html.Li(
                                "Some interactive features have limited touch support"
                            ),
                            html.Li(
                                "Processing large datasets may strain mobile resources"
                            ),
                        ]
                    ),
                    html.P(html.Strong("Recommended setup:")),
                    html.Ul(
                        [
                            html.Li("Desktop or laptop computer"),
                            html.Li("Screen resolution: 1366x768 or higher"),
                            html.Li(
                                'Tablets (10"+ screen) acceptable for basic exploration'
                            ),
                            html.Li("Mouse/trackpad for best chart interaction"),
                        ]
                    ),
                    create_faq_note(
                        "Mobile browsers may work for viewing results, but we strongly "
                        "recommend desktop for data upload and analysis.",
                        note_type="warning",
                    ),
                ]
            ),
            item_id="faq-mobile",
        ),
        create_faq_item(
            question="Is my data processed locally or on a server?",
            answer=html.Div(
                [
                    html.P(
                        "All data processing happens server-side in a secure environment. "
                        "Your browser never processes or stores sensitive data."
                    ),
                    html.P(html.Strong("Data flow:")),
                    html.Ol(
                        [
                            html.Li(
                                [
                                    html.Strong("Upload: "),
                                    "File transmitted via HTTPS encryption to server",
                                ]
                            ),
                            html.Li(
                                [
                                    html.Strong("Processing: "),
                                    "Server-side analysis with integrated databases (BioRemPP, KEGG, HADEG, ToxCSM)",
                                ]
                            ),
                            html.Li(
                                [
                                    html.Strong("Caching: "),
                                    f"Results stored in Redis (in-memory cache) for {FAQ_SESSION_TIMEOUT_HOURS}-hour session",
                                ]
                            ),
                            html.Li(
                                [
                                    html.Strong("Display: "),
                                    "Results sent to browser via HTTPS for visualization",
                                ]
                            ),
                            html.Li(
                                [
                                    html.Strong("Deletion: "),
                                    "Automatic purge when session ends",
                                ]
                            ),
                        ]
                    ),
                    html.P(html.Strong("Why server-side processing?")),
                    html.Ul(
                        [
                            html.Li("Consistent performance across all devices"),
                            html.Li("No need to download/install software"),
                            html.Li("Centralized security and privacy controls"),
                        ]
                    ),
                    create_faq_note(
                        "Your browser only displays results - no genomic data is stored "
                        "client-side. All processing happens on secure servers.",
                        note_type="success",
                    ),
                ]
            ),
            item_id="faq-data-location",
        ),
        create_faq_item(
            question="Can I use BioRemPP via API or command line?",
            answer=html.Div(
                [
                    html.P(
                        "Currently, BioRemPP is available exclusively as a web application. "
                        "Programmatic access is under consideration for future releases."
                    ),
                    html.P(html.Strong("Current status:")),
                    html.Ul(
                        [
                            html.Li(
                                [
                                    html.Strong("Web Interface: "),
                                    "✅ Fully functional and production-ready",
                                ]
                            ),
                            html.Li(
                                [
                                    html.Strong("REST API: "),
                                    "❌ Not available (planned for future)",
                                ]
                            ),
                            html.Li(
                                [
                                    html.Strong("Command-line tool: "),
                                    "Under Development ",
                                ]
                            ),
                            html.Li(
                                [
                                    html.Strong("Python package: "),
                                    "Under Development",
                                ]
                            ),
                        ]
                    ),
                    html.P(html.Strong("Workarounds for automation:")),
                    html.Ul(
                        [
                            html.Li(
                                "Download database results (CSV/Excel/JSON) for external analysis"
                            ),
                            html.Li(
                                "Use browser automation tools (Selenium) for batch processing"
                            ),
                            html.Li(
                                "Export data tables and process with custom scripts"
                            ),
                        ]
                    ),
                ]
            ),
            item_id="faq-api",
        ),
        create_faq_item(
            question="What technology stack powers BioRemPP?",
            answer=html.Div(
                [
                    html.P("BioRemPP is built with modern, open-source technologies:"),
                    html.P(html.Strong("Core Technologies:")),
                    html.Ul(
                        [
                            html.Li(
                                [
                                    html.Strong("Python 3.12: "),
                                    "Core processing engine and business logic",
                                ]
                            ),
                            html.Li(
                                [
                                    html.Strong("Dash 2.x: "),
                                    "Interactive web framework (built on Flask)",
                                ]
                            ),
                            html.Li(
                                [
                                    html.Strong("Plotly: "),
                                    "Interactive visualizations and charts",
                                ]
                            ),
                            html.Li(
                                [
                                    html.Strong("Pandas/NumPy: "),
                                    "Data manipulation and numerical analysis",
                                ]
                            ),
                        ]
                    ),
                    html.P(html.Strong("Infrastructure:")),
                    html.Ul(
                        [
                            html.Li(
                                [
                                    html.Strong("Redis: "),
                                    "In-memory session caching (4-hour timeout)",
                                ]
                            ),
                            html.Li(
                                [
                                    html.Strong("Dash Bootstrap Components: "),
                                    "Responsive UI design",
                                ]
                            ),
                            html.Li(
                                [
                                    html.Strong("AG Grid: "),
                                    "High-performance data tables",
                                ]
                            ),
                        ]
                    ),
                ]
            ),
            item_id="faq-tech-stack",
        ),
    ]

    section_technical = create_faq_section(
        title="Technical Questions",
        items=technical_items,
        section_icon="fa-code",
        section_id="faq-technical",
    )

    # ================= SECTION 6: Troubleshooting ===================
    troubleshooting_items = [
        create_faq_item(
            question="The page won't load or is very slow",
            answer=html.Div(
                [
                    html.P("Performance issues can have several causes:"),
                    html.P(html.Strong("Quick fixes:")),
                    html.Ol(
                        [
                            html.Li("Clear browser cache and cookies (CTRL+SHIFT+DEL)"),
                            html.Li(
                                "Disable browser extensions/ad blockers temporarily"
                            ),
                            html.Li("Try a different browser (Chrome, Firefox, Edge)"),
                            html.Li("Check your internet connection speed"),
                            html.Li("Close unnecessary browser tabs"),
                        ]
                    ),
                    html.P(html.Strong("If still slow:")),
                    html.Ul(
                        [
                            html.Li(
                                "Server may be under heavy load - try during off-peak hours"
                            ),
                            html.Li(
                                "Large datasets take longer to process (be patient)"
                            ),
                            html.Li(
                                "Check if your firewall/antivirus is blocking connections"
                            ),
                        ]
                    ),
                    create_faq_note(
                        "Processing time depends on dataset size.",
                        note_type="info",
                    ),
                ]
            ),
            item_id="faq-slow-loading",
        ),
        create_faq_item(
            question="Charts are not displaying properly",
            answer=html.Div(
                [
                    html.P("Chart rendering issues are usually browser-related:"),
                    html.P(html.Strong("Essential checks:")),
                    html.Ul(
                        [
                            html.Li(
                                [
                                    html.Strong("JavaScript enabled: "),
                                    "Charts require JavaScript - check browser settings",
                                ]
                            ),
                            html.Li(
                                [
                                    html.Strong("Browser version: "),
                                    "Update to latest version (Chrome 90+, Firefox 88+, Edge 90+)",
                                ]
                            ),
                            html.Li(
                                [html.Strong("Zoom level: "), "Reset to 100% (CTRL+0)"]
                            ),
                        ]
                    ),
                    html.P(html.Strong("Advanced troubleshooting:")),
                    html.Ol(
                        [
                            html.Li("Open browser console (F12) and check for errors"),
                            html.Li("Try incognito/private mode"),
                            html.Li("Clear site data (Settings → Privacy → Site data)"),
                            html.Li("Test with a different browser"),
                        ]
                    ),
                    create_faq_note(
                        "Corporate networks may block WebGL or certain JavaScript features. "
                        "Contact your IT department if issues persist.",
                        note_type="warning",
                    ),
                ]
            ),
            item_id="faq-charts-not-displaying",
        ),
        create_faq_item(
            question="I lost my results after closing the browser",
            answer=html.Div(
                [
                    html.P(
                        "Results are session-based and automatically deleted for privacy. "
                        "This is by design, not a bug."
                    ),
                    html.P(html.Strong("Why this happens:")),
                    html.Ul(
                        [
                            html.Li(f"Session timeout: {FAQ_SESSION_TIMEOUT_HOURS} hours of inactivity"),
                            html.Li("Browser closed: Immediate deletion"),
                            html.Li("Session cleared: Manual or automatic cleanup"),
                            html.Li("Server restart: Rare, scheduled maintenance"),
                        ]
                    ),
                    html.P(html.Strong("Best practices to preserve results:")),
                    html.Ol(
                        [
                            html.Li(
                                [
                                    html.Strong("Download immediately: "),
                                    "Download database results (CSV/Excel/JSON) right after processing",
                                ]
                            ),
                            html.Li(
                                [
                                    html.Strong("Export charts: "),
                                    "Save important visualizations as PNG/SVG",
                                ]
                            ),
                            html.Li(
                                [
                                    html.Strong("Keep tab open: "),
                                    "Don't close browser during active analysis",
                                ]
                            ),
                            html.Li(
                                [
                                    html.Strong("Set reminders: "),
                                    f"{FAQ_SESSION_TIMEOUT_HOURS}-hour timeout - download before taking long breaks",
                                ]
                            ),
                        ]
                    ),
                    create_faq_note(
                        "Data cannot be recovered after session ends. Always download "
                        "important results before closing your browser.",
                        note_type="warning",
                    ),
                ]
            ),
            item_id="faq-lost-results",
        ),
        create_faq_item(
            question="Error: 'No KO annotations found'",
            answer=html.Div(
                [
                    html.P(
                        "This error means your file doesn't contain valid KO numbers in "
                        "the expected format."
                    ),
                    html.P(html.Strong("Common causes:")),
                    html.Ul(
                        [
                            html.Li("KO numbers missing the 'K' prefix"),
                            html.Li("Sample names don't start with '>' character"),
                            html.Li("File encoding issues (use UTF-8)"),
                            html.Li("Empty lines or incorrect formatting"),
                        ]
                    ),
                    html.P(html.Strong("Required format:")),
                    create_code_block(
                        ">Sample1\n"
                        "K00001\n"
                        "K00002\n"
                        "K00003\n"
                        ">Sample2\n"
                        "K00004\n"
                        "K00005"
                    ),
                    html.P(html.Strong("Troubleshooting steps:")),
                    html.Ol(
                        [
                            html.Li(
                                "Verify each KO follows K##### format (K + 5 digits)"
                            ),
                            html.Li("Ensure sample names start with '>'"),
                            html.Li("Check for extra spaces or special characters"),
                            html.Li(
                                "Save file as plain text (.txt) with UTF-8 encoding"
                            ),
                            html.Li(
                                "Try the example dataset to verify system is working"
                            ),
                        ]
                    ),
                    create_faq_note(
                        "Use KEGG BlastKOALA, KofamKOALA, or eggNOG-mapper to annotate "
                        "your sequences and obtain valid KO numbers.",
                        note_type="info",
                    ),
                ]
            ),
            item_id="faq-no-ko-error",
        ),
        create_faq_item(
            question="Download buttons are not working",
            answer=html.Div(
                [
                    html.P("Download issues are usually browser permission-related:"),
                    html.P(html.Strong("Browser settings:")),
                    html.Ul(
                        [
                            html.Li(
                                [
                                    html.Strong("Pop-up blocker: "),
                                    "Allow pop-ups from BioRemPP domain",
                                ]
                            ),
                            html.Li(
                                [
                                    html.Strong("Download permissions: "),
                                    "Enable automatic downloads in browser settings",
                                ]
                            ),
                            html.Li(
                                [
                                    html.Strong("Download location: "),
                                    "Ensure download folder exists and has write permissions",
                                ]
                            ),
                        ]
                    ),
                    html.P(html.Strong("System issues:")),
                    html.Ul(
                        [
                            html.Li("Insufficient disk space"),
                            html.Li("Antivirus software blocking downloads"),
                            html.Li("Corporate firewall restrictions"),
                            html.Li("File permissions in download folder"),
                        ]
                    ),
                    html.P(html.Strong("Solutions:")),
                    html.Ol(
                        [
                            html.Li("Check browser's download bar/notification"),
                            html.Li("Try different format (CSV instead of Excel)"),
                            html.Li("Right-click download button → 'Save link as'"),
                            html.Li("Temporarily disable antivirus"),
                            html.Li("Try incognito/private mode"),
                        ]
                    ),
                ]
            ),
            item_id="faq-download-not-working",
        ),
        create_faq_item(
            question="Charts show 'No data available for this configuration'",
            answer=html.Div(
                [
                    html.P(
                        "This message appears when your filter parameters are too "
                        "restrictive or no data matches the selected criteria."
                    ),
                    html.P(html.Strong("Common causes:")),
                    html.Ul(
                        [
                            html.Li(
                                "'Top N' value too low (e.g., Top 5 when you have 3 items)"
                            ),
                            html.Li(
                                "Threshold values too high (filtering out all data)"
                            ),
                            html.Li(
                                "Selected database has no matches for your samples"
                            ),
                            html.Li("Sample selection excludes all relevant data"),
                        ]
                    ),
                    html.P(html.Strong("Quick fixes:")),
                    html.Ol(
                        [
                            html.Li("Increase 'Top N' parameter (try 20 or 50)"),
                            html.Li("Lower threshold values"),
                            html.Li("Reset filters to default values"),
                            html.Li("Select 'All Samples' instead of specific subset"),
                            html.Li("Try a different database or use case"),
                        ]
                    ),
                    html.P(html.Strong("Understanding minimums:")),
                    html.Ul(
                        [
                            html.Li(
                                "Heatmaps: Need at least 2 samples and 2 compounds"
                            ),
                            html.Li("Network graphs: Need at least 3 nodes"),
                            html.Li("Clustering: Need at least 4 samples"),
                            html.Li("Statistical tests: Need at least 3 replicates"),
                        ]
                    ),
                    create_faq_note(
                        "If you have few samples or matches, start with simpler "
                        "visualizations (bar charts, tables) before trying complex ones.",
                        note_type="info",
                    ),
                ]
            ),
            item_id="faq-no-data-config",
        ),
        create_faq_item(
            question="Processing spinner stuck or taking too long",
            answer=html.Div(
                [
                    html.P(
                        "Processing time varies based on dataset size and server load."
                    ),
                    html.P(html.Strong("Expected processing times:")),
                    html.Ul(
                        [
                            html.Li(
                                "Small dataset (< 250.000 KOs): 10-30 seconds"
                            ),
                            html.Li(
                                "Medium dataset (> 250.000 KOs): 1 - 2 minutes"
                            ),
                        ]
                    ),
                    html.P(html.Strong("If stuck for > 5 minutes:")),
                    html.Ol(
                        [
                            html.Li("Check browser console (F12) for errors"),
                            html.Li("Verify internet connection is stable"),
                            html.Li("Refresh page and try again"),
                            html.Li("Try with example dataset to verify server status"),
                            html.Li("Contact support if issue persists"),
                        ]
                    ),
                    create_faq_note(
                        "Don't close the browser or navigate away during processing. "
                        "The spinner will disappear when complete.",
                        note_type="warning",
                    ),
                ]
            ),
            item_id="faq-processing-stuck",
        ),
        create_faq_item(
            question="Browser compatibility issues",
            answer=html.Div(
                [
                    html.P("BioRemPP works best with modern browsers:"),
                    html.P(html.Strong("Recommended browsers:")),
                    html.Ul(
                        [
                            html.Li(
                                [
                                    html.Strong("Google Chrome 90+: "),
                                    "Best performance, fully tested",
                                ]
                            ),
                            html.Li(
                                [
                                    html.Strong("Mozilla Firefox 88+: "),
                                    "Fully supported",
                                ]
                            ),
                            html.Li(
                                [html.Strong("Microsoft Edge 90+: "), "Fully supported"]
                            ),
                            html.Li(
                                [
                                    html.Strong("Safari 14+: "),
                                    "Supported with minor limitations",
                                ]
                            ),
                        ]
                    ),
                    html.P(html.Strong("Not supported:")),
                    html.Ul(
                        [
                            html.Li("Internet Explorer (any version)"),
                            html.Li("Browsers with JavaScript disabled"),
                            html.Li("Very old browser versions (pre-2020)"),
                        ]
                    ),
                    html.P(html.Strong("Mobile browsers:")),
                    html.P(
                        "BioRemPP is optimized for desktop use. Mobile browsers may have "
                        "limited functionality, especially for complex visualizations.",
                        className="text-muted",
                    ),
                    create_faq_note(
                        "For best experience, use latest version of Chrome or Firefox "
                        "on a desktop computer with screen resolution ≥ 1366x768.",
                        note_type="success",
                    ),
                ]
            ),
            item_id="faq-browser-compatibility",
        ),
        create_faq_item(
            question="General troubleshooting checklist",
            answer=html.Div(
                [
                    html.P(
                        "If you're experiencing issues not covered above, try this "
                        "systematic troubleshooting approach:"
                    ),
                    html.P(html.Strong("Level 1: Quick fixes (try first)")),
                    html.Ol(
                        [
                            html.Li("Refresh the page (CTRL+R or F5)"),
                            html.Li("Clear browser cache (CTRL+SHIFT+DEL)"),
                            html.Li("Try incognito/private mode"),
                            html.Li("Check internet connection"),
                        ]
                    ),
                    html.P(html.Strong("Level 2: Browser checks")),
                    html.Ol(
                        [
                            html.Li("Update browser to latest version"),
                            html.Li("Disable all extensions"),
                            html.Li("Check JavaScript is enabled"),
                            html.Li("Allow pop-ups and downloads"),
                            html.Li("Open browser console (F12) for error messages"),
                        ]
                    ),
                    html.P(html.Strong("Level 3: System checks")),
                    html.Ol(
                        [
                            html.Li("Try different browser"),
                            html.Li("Temporarily disable antivirus/firewall"),
                            html.Li("Check disk space"),
                            html.Li("Restart computer"),
                        ]
                    ),
                    html.P(html.Strong("Level 4: Contact support")),
                    html.P(
                        "If none of the above works, contact support with:",
                        className="mt-2",
                    ),
                    html.Ul(
                        [
                            html.Li("Screenshot of the error"),
                            html.Li("Browser console errors (F12 → Console tab)"),
                            html.Li("Browser name and version"),
                            html.Li("Operating system"),
                            html.Li("Steps to reproduce the issue"),
                        ]
                    ),
                    create_faq_note(
                        "Most issues are resolved at Level 1 or 2. Try these first "
                        "before contacting support.",
                        note_type="info",
                    ),
                ]
            ),
            item_id="faq-general-troubleshooting",
        ),
    ]

    section_troubleshooting = create_faq_section(
        title="Troubleshooting",
        items=troubleshooting_items,
        section_icon="fa-wrench",
        section_id="faq-troubleshooting",
    )

    # ============= SECTION 7: Data Privacy & Security ===============
    privacy_items = [
        create_faq_item(
            question="Is my genomic data secure?",
            answer=html.Div(
                [
                    html.P(
                        "Yes. BioRemPP implements multiple security layers to protect "
                        "your data:"
                    ),
                    html.P(html.Strong("Data Transmission:")),
                    html.Ul(
                        [
                            html.Li("HTTPS encryption for all data transmission"),
                            html.Li(
                                "Secure WebSocket connections for real-time updates"
                            ),
                            html.Li("No client-side storage of sensitive data"),
                        ]
                    ),
                    html.P(html.Strong("Session Management:")),
                    html.Ul(
                        [
                            html.Li("Redis-based session caching (in-memory storage)"),
                            html.Li("Unique session IDs for complete isolation"),
                            html.Li("Automatic 4-hour session timeout"),
                            html.Li("No cross-session data access"),
                        ]
                    ),
                    html.P(html.Strong("Data Handling:")),
                    html.Ul(
                        [
                            html.Li("Server-side processing only"),
                            html.Li("No permanent storage of uploaded files"),
                            html.Li("Automatic deletion after session ends"),
                            html.Li("No sharing with third parties"),
                        ]
                    ),
                    create_faq_note(
                        "Your data is processed in isolated sessions and immediately "
                        "discarded. We do not build databases from user uploads.",
                        note_type="success",
                    ),
                ]
            ),
            item_id="faq-data-secure",
        ),
        create_faq_item(
            question="How long is my data stored?",
            answer=html.Div(
                [
                    html.P(
                        "Your data is stored temporarily only during your active session:"
                    ),
                    html.P(html.Strong("Session Lifecycle:")),
                    html.Ol(
                        [
                            html.Li(
                                [
                                    html.Strong("Upload: "),
                                    "File is uploaded and validated",
                                ]
                            ),
                            html.Li(
                                [
                                    html.Strong("Processing: "),
                                    "Data is processed and results cached in Redis",
                                ]
                            ),
                            html.Li(
                                [
                                    html.Strong("Active Session: "),
                                    f"Results available for {FAQ_SESSION_TIMEOUT_HOURS} hours of activity",
                                ]
                            ),
                            html.Li(
                                [
                                    html.Strong("Session End: "),
                                    "All data automatically deleted",
                                ]
                            ),
                        ]
                    ),
                    html.P(html.Strong("Session ends when:")),
                    html.Ul(
                        [
                            html.Li("You close your browser"),
                            html.Li(f"{FAQ_SESSION_TIMEOUT_HOURS} hours of inactivity passes"),
                            html.Li("You explicitly clear your session"),
                            html.Li("Server restarts (rare, scheduled maintenance)"),
                        ]
                    ),
                    create_faq_note(
                        f"Session timeout: {FAQ_SESSION_TIMEOUT_HOURS} hours. Download important results before "
                        "closing your browser or taking long breaks.",
                        note_type="warning",
                    ),
                ]
            ),
            item_id="faq-data-storage-time",
        ),
        create_faq_item(
            question="What data do you collect?",
            answer=html.Div(
                [
                    html.P(
                        "We collect minimal data necessary for system operation and "
                        "improvement:"
                    ),
                    html.P(html.Strong("Data We DO Collect:")),
                    html.Ul(
                        [
                            html.Li(
                                [
                                    html.Strong("Anonymous Usage Statistics: "),
                                    "Page views, processing times, feature usage (no personal data)",
                                ]
                            ),
                            html.Li(
                                [
                                    html.Strong("Error Logs: "),
                                    "System errors for debugging (no user data included)",
                                ]
                            ),
                            html.Li(
                                [
                                    html.Strong("Session Metadata: "),
                                    "Session ID, timestamp, file size (not file contents)",
                                ]
                            ),
                        ]
                    ),
                    html.P(html.Strong("Data We DO NOT Collect:")),
                    html.Ul(
                        [
                            html.Li("Your uploaded files or their contents (not stored persistently)"),
                            html.Li("Analysis results or processed data (beyond session lifetime)"),
                            html.Li("Personal information (name, email, institution)"),
                            html.Li("Tracking cookies or persistent identifiers"),
                        ]
                    ),
                    create_faq_note(
                        "BioRemPP is designed to minimize personal data collection and "
                        "follows privacy-by-design principles. Operational logs may include "
                        "technical metadata for security and reliability. See Terms/Privacy "
                        "policy for details.",
                        note_type="success",
                    ),
                ]
            ),
            item_id="faq-data-collection",
        ),
        create_faq_item(
            question="Can other users see my results?",
            answer=html.Div(
                [
                    html.P(
                        "No. Complete session isolation ensures your data is private:"
                    ),
                    html.P(html.Strong("Isolation Mechanisms:")),
                    html.Ul(
                        [
                            html.Li(
                                [
                                    html.Strong("Unique Session IDs: "),
                                    "Each session has a unique identifier",
                                ]
                            ),
                            html.Li(
                                [
                                    html.Strong("Redis Namespacing: "),
                                    "Session data is stored in isolated Redis keys",
                                ]
                            ),
                            html.Li(
                                [
                                    html.Strong("No Cross-Session Access: "),
                                    "Server-side validation prevents accessing other sessions",
                                ]
                            ),
                            html.Li(
                                [
                                    html.Strong("No Public URLs: "),
                                    "Results are not accessible via shareable links",
                                ]
                            ),
                        ]
                    ),
                    html.P(
                        "Your results are only accessible to you during your session. "
                        "Even if someone knows your session ID, server-side validation "
                        "prevents unauthorized access.",
                        className="text-muted mt-2",
                    ),
                    create_faq_note(
                        "Session IDs are not shareable. Each browser session is "
                        "completely isolated from all others.",
                        note_type="info",
                    ),
                ]
            ),
            item_id="faq-session-isolation",
        ),
        create_faq_item(
            question="What happens to my data after I close my browser?",
            answer=html.Div(
                [
                    html.P(
                        "All session data is automatically and permanently deleted:"
                    ),
                    html.P(html.Strong("Deletion Process:")),
                    html.Ol(
                        [
                            html.Li(
                                [
                                    html.Strong("Uploaded TXT file: "),
                                    "Deleted from server memory",
                                ]
                            ),
                            html.Li(
                                [
                                    html.Strong("Processed results: "),
                                    "Removed from Redis cache",
                                ]
                            ),
                            html.Li(
                                [
                                    html.Strong("Generated visualizations: "),
                                    "Cleared from session storage",
                                ]
                            ),
                            html.Li(
                                [html.Strong("Session cache: "), "Purged from Redis"]
                            ),
                            html.Li(
                                [
                                    html.Strong("Temporary files: "),
                                    "Removed from server filesystem",
                                ]
                            ),
                        ]
                    ),
                    html.P(html.Strong("Important Notes:")),
                    html.Ul(
                        [
                            html.Li("Deletion is immediate and irreversible"),
                            html.Li("No backup copies are kept"),
                            html.Li("Data cannot be recovered after session ends"),
                            html.Li(
                                "Download results before closing if you want to keep them"
                            ),
                        ]
                    ),
                    create_faq_note(
                        "This ensures maximum privacy but means you must download "
                        "all important results before closing your browser.",
                        note_type="warning",
                    ),
                ]
            ),
            item_id="faq-data-after-close",
        ),
        create_faq_item(
            question="Is BioRemPP GDPR compliant?",
            answer=html.Div(
                [
                    html.P("BioRemPP is designed to minimize personal data collection and "
                           "support privacy-by-design principles:"),
                    html.P(html.Strong("Privacy Principles Implemented:")),
                    html.Ul(
                        [
                            html.Li(
                                [
                                    html.Strong("Data Minimization: "),
                                    "We only process data necessary for analysis",
                                ]
                            ),
                            html.Li(
                                [
                                    html.Strong("Purpose Limitation: "),
                                    "Data used only for bioremediation analysis",
                                ]
                            ),
                            html.Li(
                                [
                                    html.Strong("Storage Limitation: "),
                                    "Data deleted after 4-hour session timeout",
                                ]
                            ),
                            html.Li(
                                [
                                    html.Strong("No Personal Data: "),
                                    "No collection of identifiable information",
                                ]
                            ),
                            html.Li(
                                [
                                    html.Strong("User Control: "),
                                    "You control when to upload and delete data",
                                ]
                            ),
                        ]
                    ),
                    html.P(html.Strong("Your Rights:")),
                    html.Ul(
                        [
                            html.Li("Right to access: No personal data is stored"),
                            html.Li(
                                "Right to erasure: Automatic deletion after session"
                            ),
                            html.Li(
                                "Right to data portability: Download results anytime"
                            ),
                            html.Li(
                                "Right to object: Don't upload if you don't consent"
                            ),
                        ]
                    ),
                    create_faq_note(
                        "No account creation required. Personal data collection is minimized. "
                        "Session data deleted after timeout. See Terms/Privacy policy for complete details.",
                        note_type="success",
                    ),
                ]
            ),
            item_id="faq-gdpr-compliance",
        ),
    ]

    section_privacy = create_faq_section(
        title="Data Privacy & Security",
        items=privacy_items,
        section_icon="fa-shield-alt",
        section_id="faq-privacy",
    )

    # ===== SECTION 8: Reproducibility, Versioning & Citation ========
    reproducibility_items = [
        create_faq_item(
            question="How do I report BioRemPP in Methods (minimum required metadata)?",
            answer=html.Div(
                [
                    html.P(
                        "To ensure reproducibility, report the following information in your "
                        "Methods section when using BioRemPP:"
                    ),
                    html.P(html.Strong("Required metadata:")),
                    html.Ol(
                        [
                            html.Li(
                                [
                                    html.Strong("BioRemPP version: "),
                                    f"e.g., BioRemPP v{FAQ_APP_VERSION}",
                                ]
                            ),
                            html.Li(
                                [
                                    html.Strong("Access date: "),
                                    "Date when analysis was performed",
                                ]
                            ),
                            html.Li(
                                [
                                    html.Strong("Input type: "),
                                    "Genomes, MAGs, metagenomes, or mixed",
                                ]
                            ),
                            html.Li(
                                [
                                    html.Strong("Annotation pipeline: "),
                                    "Tool used for KO annotation (BlastKOALA, KofamKOALA, eggNOG-mapper, etc.)",
                                ]
                            ),
                            html.Li(
                                [
                                    html.Strong("Modules/use cases: "),
                                    "Specific analytical modules used (e.g., Module 2, UC-2.1)",
                                ]
                            ),
                            html.Li(
                                [
                                    html.Strong("Key parameters: "),
                                    "Any non-default thresholds, top N values, or filters applied",
                                ]
                            ),
                        ]
                    ),
                    html.P(html.Strong("Example Methods statement:")),
                    create_code_block(
                        f"Bioremediation potential was assessed using BioRemPP v{FAQ_APP_VERSION} "
                        "(accessed [DATE], {FAQ_CANONICAL_URL}). KO annotations were obtained "
                        "using eggNOG-mapper v2.1.12. We applied Module 2 (Exploratory Analysis) "
                        "with default parameters to rank degradation potential across samples.",
                        language="text",
                    ),
                    create_faq_note(
                        "Always report annotation tool and version, as KO assignment quality "
                        "directly impacts BioRemPP results.",
                        note_type="warning",
                    ),
                ]
            ),
            item_id="faq-methods-reporting",
        ),
        create_faq_item(
            question="Where can I find the exact BioRemPP version used?",
            answer=html.Div(
                [
                    html.P("BioRemPP version information is displayed in multiple locations:"),
                    html.Ul(
                        [
                            html.Li(
                                [
                                    html.Strong("Footer: "),
                                    f"Bottom of every page shows 'BioRemPP v{FAQ_APP_VERSION}'",
                                ]
                            ),
                            html.Li(
                                [
                                    html.Strong("About page: "),
                                    "Detailed version and build information",
                                ]
                            ),
                            html.Li(
                                [
                                    html.Strong("Documentation: "),
                                    "Technical documentation includes version history",
                                ]
                            ),
                        ]
                    ),
                    html.P(html.Strong(f"Current version: {FAQ_APP_VERSION}"), className="mt-3"),
                    create_faq_note(
                        "Screenshot the footer or About page during your analysis to preserve "
                        "version information for future reference.",
                        note_type="success",
                    ),
                ]
            ),
            item_id="faq-version-info",
        ),
        create_faq_item(
            question="Are databases versioned? What snapshot should I cite?",
            answer=html.Div(
                [
                    html.P(
                        "BioRemPP integrates multiple databases, each with different versioning practices:"
                    ),
                    html.P(html.Strong("Database versioning:")),
                    html.Ul(
                        [
                            html.Li(
                                [
                                    html.Strong("BioRemPP curated database: "),
                                    "Versioned with the web service; deposited on Zenodo",
                                ]
                            ),
                            html.Li(
                                [
                                    html.Strong("KEGG: "),
                                    "Updated regularly; cite access date",
                                ]
                            ),
                            html.Li(
                                [
                                    html.Strong("HADEG: "),
                                    "Cite original publication and BioRemPP integration version",
                                ]
                            ),
                            html.Li(
                                [
                                    html.Strong("toxCSM: "),
                                    "Cite original toxCSM publication",
                                ]
                            ),
                        ]
                    ),
                    html.P(html.Strong("Zenodo deposition:")),
                    html.P(
                        f"BioRemPP database and web service will be deposited on Zenodo with DOI: {FAQ_ZENODO_DATABASE_DOI}",
                        className="text-muted",
                    ),
                    create_faq_note(
                        "Until Zenodo DOI is assigned, cite BioRemPP version and access date. "
                        "Check 'How to Cite' page for updated citation information.",
                        note_type="info",
                    ),
                ]
            ),
            item_id="faq-database-versions",
        ),
        create_faq_item(
            question="How do I cite BioRemPP before DOI assignment?",
            answer=html.Div(
                [
                    html.P(
                        "Until formal publication and Zenodo DOI assignment, use the following "
                        "citation templates:"
                    ),
                    html.P(html.Strong("Web service citation (temporary):")),
                    create_code_block(
                        f"BioRemPP: Bioremediation Potential Profile Analysis Tool.\n"
                        f"Version {FAQ_APP_VERSION} (2025).\n"
                        f"Available at: {FAQ_CANONICAL_URL}\n"
                        "Accessed: [DATE]",
                        language="text",
                    ),
                    html.P(html.Strong("Database citation (temporary):")),
                    create_code_block(
                        f"BioRemPP Curated Database for Bioremediation Analysis.\n"
                        f"Version {FAQ_APP_VERSION} (2025).\n"
                        f"Zenodo DOI: {FAQ_ZENODO_DATABASE_DOI}",
                        language="text",
                    ),
                    html.P(html.Strong("Third-party databases (always cite):")),
                    html.Ul(
                        [
                            html.Li("KEGG: Kanehisa et al. (cite latest KEGG paper)"),
                            html.Li("HADEG: [HADEG original publication]"),
                            html.Li("toxCSM: [toxCSM original publication]"),
                        ]
                    ),
                    create_faq_note(
                        "A formal publication is in preparation. Check the 'How to Cite' page "
                        "regularly for updated citation information and assigned DOIs.",
                        note_type="warning",
                    ),
                ]
            ),
            item_id="faq-citation-templates",
        ),
        create_faq_item(
            question="Can I export parameters and analysis configuration for reproducibility?",
            answer=html.Div(
                [
                    html.P(
                        "Currently, BioRemPP does not automatically export a full configuration "
                        "file with all parameters used during analysis."
                    ),
                    html.P(html.Strong("Current reproducibility workflow:")),
                    html.Ol(
                        [
                            html.Li(
                                [
                                    html.Strong("Record parameters manually: "),
                                    "Note use case IDs, top N values, thresholds, filters",
                                ]
                            ),
                            html.Li(
                                [
                                    html.Strong("Download raw data: "),
                                    "Export database tables (CSV/Excel/JSON)",
                                ]
                            ),
                            html.Li(
                                [
                                    html.Strong("Save input file: "),
                                    "Keep original TXT file with KO annotations",
                                ]
                            ),
                        ]
                    ),
                    html.P(html.Strong("Recommended documentation:")),
                    html.Ul(
                        [
                            html.Li("BioRemPP version (from footer)"),
                            html.Li("Analysis date"),
                            html.Li("Module and use case IDs (e.g., UC-2.1, UC-7.3)"),
                            html.Li("Parameter values (top N, thresholds, filters)"),
                            html.Li("Downloaded data files with timestamps"),
                        ]
                    ),
                    create_faq_note(
                        "Future versions may include automated parameter export. For now, "
                        "maintain detailed lab notebooks or analysis logs.",
                        note_type="info",
                    ),
                ]
            ),
            item_id="faq-export-config",
        ),
    ]

    section_reproducibility = create_faq_section(
        title="Reproducibility, Versioning & Citation",
        items=reproducibility_items,
        section_icon="fa-file-alt",
        section_id="faq-reproducibility",
    )

    # ========= SECTION 9: Licensing & Third-Party Data =============
    licensing_items = [
        create_faq_item(
            question="How does BioRemPP use KEGG and what are licensing constraints?",
            answer=html.Div(
                [
                    html.P(
                        "BioRemPP uses KEGG Orthology (KO) identifiers and pathway metadata "
                        "to support bioremediation analysis."
                    ),
                    html.P(html.Strong("How KEGG is used:")),
                    html.Ul(
                        [
                            html.Li(
                                "KO identifiers serve as functional annotation standard for input data"
                            ),
                            html.Li(
                                "KEGG pathway definitions used for pathway completeness calculations"
                            ),
                            html.Li(
                                "KEGG compound IDs mapped to toxicity and regulatory databases"
                            ),
                            html.Li(
                                "Reaction and enzyme metadata support degradation pathway analysis"
                            ),
                        ]
                    ),
                    html.P(html.Strong("KEGG licensing constraints:")),
                    html.Ul(
                        [
                            html.Li(
                                [
                                    html.Strong("Academic/non-profit use: "),
                                    "KEGG data accessible for research purposes under KEGG terms",
                                ]
                            ),
                            html.Li(
                                [
                                    html.Strong("Commercial use: "),
                                    "Organizations using BioRemPP for commercial purposes may "
                                    "require a KEGG license from the KEGG organization",
                                ]
                            ),
                            html.Li(
                                [
                                    html.Strong("Redistribution: "),
                                    "BioRemPP does not redistribute KEGG database files; "
                                    "integrates curated mappings and references",
                                ]
                            ),
                        ]
                    ),
                    create_faq_note(
                        "Users are responsible for compliance with KEGG license terms. "
                        "For commercial use, contact KEGG directly: "
                        "https://www.kegg.jp/kegg/legal.html",
                        note_type="warning",
                    ),
                ]
            ),
            item_id="faq-kegg-licensing",
        ),
        create_faq_item(
            question="Do I need to cite HADEG and toxCSM separately?",
            answer=html.Div(
                [
                    html.P(
                        [
                            html.Strong("Yes."),
                            " BioRemPP integrates third-party databases, and proper attribution "
                            "is required for all data sources.",
                        ]
                    ),
                    html.P(html.Strong("Required citations:")),
                    html.Ul(
                        [
                            html.Li(
                                [
                                    html.Strong("BioRemPP: "),
                                    f"Cite the web service (v{FAQ_APP_VERSION}) and database",
                                ]
                            ),
                            html.Li(
                                [
                                    html.Strong("KEGG: "),
                                    "Cite the latest KEGG publication (Kanehisa et al.)",
                                ]
                            ),
                            html.Li(
                                [
                                    html.Strong("HADEG: "),
                                    "Cite the original HADEG publication",
                                ]
                            ),
                            html.Li(
                                [
                                    html.Strong("toxCSM: "),
                                    "Cite the original toxCSM publication",
                                ]
                            ),
                        ]
                    ),
                    html.P(html.Strong("Citation best practices:")),
                    html.Ul(
                        [
                            html.Li(
                                "Cite all databases used in your specific analysis"
                            ),
                            html.Li(
                                "If using Module 7 (toxicity), cite toxCSM"
                            ),
                            html.Li(
                                "If using HADEG-specific features, cite HADEG"
                            ),
                            html.Li(
                                "Always cite KEGG and BioRemPP"
                            ),
                        ]
                    ),
                    create_faq_note(
                        "See 'How to Cite' page for complete citation list with DOIs "
                        "and formatted references.",
                        note_type="info",
                    ),
                ]
            ),
            item_id="faq-cite-third-party",
        ),
        create_faq_item(
            question="Does BioRemPP redistribute third-party datasets?",
            answer=html.Div(
                [
                    html.P(
                        "No. BioRemPP does not redistribute complete third-party database files."
                    ),
                    html.P(html.Strong("What BioRemPP provides:")),
                    html.Ul(
                        [
                            html.Li(
                                [
                                    html.Strong("Curated mappings: "),
                                    "Relationships between KOs, compounds, and bioremediation functions",
                                ]
                            ),
                            html.Li(
                                [
                                    html.Strong("Integrated queries: "),
                                    "Server-side queries to reference databases",
                                ]
                            ),
                            html.Li(
                                [
                                    html.Strong("User-specific results: "),
                                    "Only data matching your input KO annotations",
                                ]
                            ),
                            html.Li(
                                [
                                    html.Strong("Value-added annotations: "),
                                    "BioRemPP-curated bioremediation-specific metadata",
                                ]
                            ),
                        ]
                    ),
                    html.P(html.Strong("Third-party data constraints:")),
                    html.Ul(
                        [
                            html.Li(
                                "KEGG: Used under KEGG terms; not redistributed"
                            ),
                            html.Li(
                                "HADEG: Cited and integrated; original data from publication"
                            ),
                            html.Li(
                                "toxCSM: Predictions accessed via integration; cite original tool"
                            ),
                        ]
                    ),
                    create_faq_note(
                        "Downloaded results contain only matched data for your samples, "
                        "not complete database dumps. All third-party terms apply.",
                        note_type="success",
                    ),
                ]
            ),
            item_id="faq-redistribution",
        ),
        create_faq_item(
            question="What is BioRemPP's software license?",
            answer=html.Div(
                [
                    html.P("BioRemPP components use open-source and permissive licenses:"),
                    html.P(html.Strong("Software license:")),
                    html.Ul(
                        [
                            html.Li(
                                [
                                    html.Strong("Web service code: "),
                                    "Apache License 2.0 (permissive, commercial-friendly)",
                                ]
                            ),
                            html.Li(
                                [
                                    html.Strong("BioRemPP curated database: "),
                                    "Creative Commons Attribution 4.0 (CC BY 4.0)",
                                ]
                            ),
                        ]
                    ),
                    html.P(html.Strong("What this means for users:")),
                    html.Ul(
                        [
                            html.Li(
                                [
                                    html.Strong("Academic use: "),
                                    "Free to use; cite BioRemPP and third-party databases",
                                ]
                            ),
                            html.Li(
                                [
                                    html.Strong("Commercial use: "),
                                    "Permitted under Apache 2.0, but verify third-party constraints (e.g., KEGG)",
                                ]
                            ),
                            html.Li(
                                [
                                    html.Strong("Redistribution: "),
                                    "Software can be modified/redistributed; database under CC BY 4.0",
                                ]
                            ),
                            html.Li(
                                [
                                    html.Strong("Attribution: "),
                                    "Always provide proper citations",
                                ]
                            ),
                        ]
                    ),
                    create_faq_note(
                        "BioRemPP is open for research and commercial use, but users must "
                        "comply with third-party database licenses (especially KEGG).",
                        note_type="info",
                    ),
                ]
            ),
            item_id="faq-biorempp-license",
        ),
    ]

    section_licensing = create_faq_section(
        title="Licensing & Third-Party Data",
        items=licensing_items,
        section_icon="fa-balance-scale",
        section_id="faq-licensing",
    )

    # ============== SECTION 10: Export & Download ===================
    export_items = [
        create_faq_item(
            question="What export formats are available?",
            answer=html.Div(
                [
                    html.P(
                        "BioRemPP provides multiple export options depending on what you want to download:"
                    ),
                    html.P(
                        html.Strong("1. Database Downloads (Complete Merged Data):")
                    ),
                    html.Ul(
                        [
                            html.Li(
                                [
                                    html.Strong("CSV: "),
                                    "Excel-compatible format, best for spreadsheet analysis",
                                ]
                            ),
                            html.Li(
                                [
                                    html.Strong("Excel (.xlsx): "),
                                    "Native Excel format with preserved formatting",
                                ]
                            ),
                            html.Li(
                                [
                                    html.Strong("JSON: "),
                                    "Structured data format for programmatic access (Python, R, JavaScript)",
                                ]
                            ),
                        ]
                    ),
                    html.P(html.Strong("2. Use Case Table Downloads:")),
                    html.Ul(
                        [
                            html.Li(
                                [
                                    html.Strong("CSV: "),
                                    "Excel-compatible format, best for spreadsheet analysis",
                                ]
                            ),
                            html.Li(
                                [
                                    html.Strong("Excel (.xlsx): "),
                                    "Native Excel format with preserved formatting",
                                ]
                            ),
                            html.Li(
                                [
                                    html.Strong("JSON: "),
                                    "Structured data format for programmatic access (Python, R, JavaScript)",
                                ]
                            ),
                        ]
                    ),
                    html.P(html.Strong("3. Chart Image Exports:")),
                    html.Ul(
                        [
                            html.Li(
                                [
                                    html.Strong("PNG/SVG/JPEG: "),
                                    "Via Plotly's interactive menu (hover over chart → camera icon)",
                                ]
                            )
                        ]
                    ),
                    create_faq_note(
                        "Database downloads include the Sample column for traceability. "
                        "Use case downloads provide data specific to that visualization.",
                        note_type="info",
                    ),
                ]
            ),
            item_id="faq-export-formats",
        ),
        create_faq_item(
            question="How do I download complete database results?",
            answer=html.Div(
                [
                    html.P(
                        "Each database section (BioRemPP, HADEG, KEGG, ToxCSM) has a "
                        "'Download Data' button that provides complete merged results."
                    ),
                    html.P(html.Strong("Step-by-step:")),
                    html.Ol(
                        [
                            html.Li(
                                "Navigate to Results page after processing your data"
                            ),
                            html.Li(
                                "Scroll to the database section you want (e.g., ToxCSM)"
                            ),
                            html.Li(
                                "Click 'Download Data' button in the section header"
                            ),
                            html.Li("Select your preferred format:"),
                            html.Ul(
                                [
                                    html.Li(
                                        "CSV - Opens in Excel, compatible with all tools"
                                    ),
                                    html.Li("Excel (.xlsx) - Native Excel format"),
                                    html.Li(
                                        "JSON - For Python, R, or JavaScript analysis"
                                    ),
                                ]
                            ),
                            html.Li(
                                "File downloads automatically with pattern: {database}_merged_data.{ext}"
                            ),
                        ]
                    ),
                    html.P(html.Strong("What's included:")),
                    html.Ul(
                        [
                            html.Li(
                                "Sample column - traces data back to your original samples"
                            ),
                            html.Li("All matched compounds/enzymes from your input"),
                            html.Li(
                                "Complete database fields (e.g., 67 columns for ToxCSM)"
                            ),
                            html.Li("Only data that matched your KO annotations"),
                        ]
                    ),
                    create_faq_note(
                        "Database downloads are merged data (your samples + database matches), "
                        "not the complete database. Empty downloads mean no matches were found.",
                        note_type="warning",
                    ),
                ]
            ),
            item_id="faq-download-database",
        ),
        create_faq_item(
            question="How do I download data from specific use cases?",
            answer=html.Div(
                [
                    html.P(
                        "Each use case (analytical module) provides downloadable data tables "
                    ),
                    html.P(html.Strong("To download:")),
                    html.Ol(
                        [
                            html.Li(
                                "Navigate to the use case you're interested in (e.g., UC-2.1)"
                            ),
                            html.Li("Generate the visualization by setting parameters"),
                            html.Li("Look for the data table below the chart"),
                            html.Li(
                                "Click the download button below the table"
                            ),
                        ]
                    ),
                    create_faq_note(
                        "Use case downloads contain the specific data used to generate "
                        "that particular visualization, not the complete database.",
                        note_type="info",
                    ),
                ]
            ),
            item_id="faq-download-use-case",
        ),
        create_faq_item(
            question="How do I export charts and visualizations?",
            answer=html.Div(
                [
                    html.P(
                        "All charts use Plotly's interactive export menu for saving images."
                    ),
                    html.P(html.Strong("To export a chart:")),
                    html.Ol(
                        [
                            html.Li("Hover your mouse over the chart"),
                            html.Li("Look for the toolbar in the top-right corner"),
                            html.Li("Click the camera icon (📷)"),
                            html.Li("Choose format: PNG, SVG, or JPEG"),
                            html.Li("Image downloads automatically"),
                        ]
                    ),
                    html.P(html.Strong("Format recommendations:")),
                    html.Ul(
                        [
                            html.Li(
                                [
                                    html.Strong("PNG: "),
                                    "Best for presentations and quick sharing (default)",
                                ]
                            ),
                            html.Li(
                                [
                                    html.Strong("SVG: "),
                                    "Vector format for publications, editable in Illustrator/Inkscape",
                                ]
                            ),
                            html.Li(
                                [
                                    html.Strong("JPEG: "),
                                    "Smaller file size, good for web use",
                                ]
                            ),
                        ]
                    ),
                    create_faq_note(
                        "For publication-quality figures, use SVG format. You can then "
                        "edit colors, fonts, and labels in vector graphics software.",
                        note_type="success",
                    ),
                ]
            ),
            item_id="faq-export-charts",
        ),
        create_faq_item(
            question="What's the difference between database downloads and use case downloads?",
            answer=html.Div(
                [
                    html.P(
                        "Understanding the difference helps you choose the right download "
                        "for your needs:"
                    ),
                    html.P(html.Strong("Database Downloads:")),
                    html.Ul(
                        [
                            html.Li("Complete merged results for entire database"),
                            html.Li("All matched compounds/enzymes with Sample column"),
                            html.Li(
                                "All database fields (e.g., 67 columns for ToxCSM)"
                            ),
                            html.Li("Found in database section headers"),
                            html.Li(
                                "Best for: Comprehensive external analysis, custom visualizations"
                            ),
                        ]
                    ),
                    html.P(html.Strong("Use Case Downloads:")),
                    html.Ul(
                        [
                            html.Li("Specific data for that particular visualization"),
                            html.Li(
                                "Filtered/processed according to use case parameters"
                            ),
                            html.Li("Subset of columns relevant to the analysis"),
                            html.Li("Found below data tables in use cases"),
                            html.Li(
                                "Best for: Reproducing specific charts, focused analysis"
                            ),
                        ]
                    ),
                    create_faq_note(
                        "Example: ToxCSM database download gives you all 67 columns for "
                        "all matched compounds. A UC-7.1 download gives you only the "
                        "toxicity endpoints used in that specific heatmap.",
                        note_type="info",
                    ),
                ]
            ),
            item_id="faq-database-vs-usecase",
        ),
        create_faq_item(
            question="Why is my database download empty?",
            answer=html.Div(
                [
                    html.P(
                        "Empty database downloads occur when no data from your samples "
                        "matched that particular database."
                    ),
                    html.P(html.Strong("Common causes by database:")),
                    html.Ul(
                        [
                            html.Li(
                                [
                                    html.Strong("ToxCSM: "),
                                    "Your KO annotations don't map to compounds in KEGG, or "
                                    "KEGG compounds aren't in ToxCSM database",
                                ]
                            ),
                            html.Li(
                                [
                                    html.Strong("HADEG: "),
                                    "No hydrocarbon degradation enzymes found in your samples",
                                ]
                            ),
                            html.Li(
                                [
                                    html.Strong("KEGG: "),
                                    "KO numbers don't match KEGG database (check KO format)",
                                ]
                            ),
                            html.Li(
                                [
                                    html.Strong("BioRemPP: "),
                                    "No bioremediation-relevant enzymes detected",
                                ]
                            ),
                        ]
                    ),
                    html.P(html.Strong("Troubleshooting steps:")),
                    html.Ol(
                        [
                            html.Li("Check if the corresponding table shows any data"),
                            html.Li(
                                "Verify your KO annotations are valid (K##### format)"
                            ),
                            html.Li(
                                "Try the example dataset to verify system functionality"
                            ),
                            html.Li("Check browser console (F12) for errors"),
                            html.Li(
                                "For ToxCSM: verify KEGG results have compound matches first"
                            ),
                        ]
                    ),
                    create_faq_note(
                        "Database downloads only include matched data. If a database "
                        "table is empty, the download will also be empty.",
                        note_type="warning",
                    ),
                ]
            ),
            item_id="faq-empty-download",
        ),
        create_faq_item(
            question="Can I download all results at once?",
            answer=html.Div(
                [
                    html.P(
                        "Currently, BioRemPP does not provide a single 'Download All' "
                        "button. You need to download each component separately:"
                    ),
                    html.P(html.Strong("Recommended download workflow:")),
                    html.Ol(
                        [
                            html.Li(
                                [
                                    html.Strong("Database Downloads: "),
                                    "Download each database (BioRemPP, HADEG, KEGG, ToxCSM) "
                                    "using 'Download Data' buttons",
                                ]
                            ),
                            html.Li(
                                [
                                    html.Strong("Use Case Data: "),
                                    "Download files from specific use cases you analyzed",
                                ]
                            ),
                            html.Li(
                                [
                                    html.Strong("Chart Images: "),
                                    "Export important visualizations via Plotly menu",
                                ]
                            ),
                        ]
                    ),
                    html.P(html.Strong("Organization tip:")),
                    html.P(
                        "Create a folder for your analysis and organize downloads by type: "
                        "databases/, use_cases/, charts/. This makes it easier to find "
                        "specific data later.",
                        className="text-muted",
                    ),
                    create_faq_note(
                        f"Session timeout is {FAQ_SESSION_TIMEOUT_HOURS} hours. Download all important results "
                        "before closing your browser or taking a long break.",
                        note_type="warning",
                    ),
                ]
            ),
            item_id="faq-download-all",
        ),
        create_faq_item(
            question="How do I cite BioRemPP in publications?",
            answer=html.Div(
                [
                    html.P("If you use BioRemPP in your research, please cite:"),
                    create_code_block(
                        f"BioRemPP: Bioremediation Potential Profile Analysis Tool.\n"
                        f"Version {FAQ_APP_VERSION} (2025).\n"
                        f"Available at: {FAQ_CANONICAL_URL}\n"
                        "Accessed: [Date]",
                        language="text",
                    ),
                    html.P(
                        html.Strong("What to include in methods section:"),
                        className="mt-3",
                    ),
                    html.Ul(
                        [
                            html.Li(f"BioRemPP version ({FAQ_APP_VERSION})"),
                            html.Li("Databases used (BioRemPP, KEGG, HADEG, toxCSM)"),
                            html.Li("Specific modules/use cases applied"),
                            html.Li("Date of analysis"),
                            html.Li("Annotation tool and version used"),
                            html.Li("Any non-default parameter modifications"),
                        ]
                    ),
                    create_faq_note(
                        "For detailed citation information, templates, and reproducibility "
                        "guidelines, see the 'Reproducibility, Versioning & Citation' section above.",
                        note_type="info",
                    ),
                ]
            ),
            item_id="faq-citation",
        ),
    ]

    section_export = create_faq_section(
        title="Export & Download",
        items=export_items,
        section_icon="fa-download",
        section_id="faq-export",
    )

    # Footer
    footer = create_footer(version=FAQ_APP_VERSION, year=2024)

    # Assemble complete layout
    layout = html.Div(
        [
            header,
            dbc.Container(
                [
                    page_intro,
                    dbc.Row(
                        [
                            # Main content (FAQ sections)
                            dbc.Col(
                                [
                                    section_getting_started,
                                    section_upload,
                                    section_processing,
                                    section_results,
                                    section_scientific_validity,
                                    section_technical,
                                    section_troubleshooting,
                                    section_privacy,
                                    section_reproducibility,
                                    section_licensing,
                                    section_export,
                                ],
                                md=8,
                            ),
                            # Sidebar (Quick navigation)
                            dbc.Col(
                                [
                                    html.Div(
                                        [quick_links],
                                        className="sticky-top",
                                        style={"top": "20px"},
                                    )
                                ],
                                md=4,
                            ),
                        ]
                    ),
                ],
                fluid=False,
                className="px-4 py-4",
            ),
            footer,
        ],
        id="faq-page",
    )

    return layout
