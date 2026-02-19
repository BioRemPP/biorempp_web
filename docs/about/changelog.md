# Changelog

All notable changes to BioRemPP will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### To-Do

- Structure and document Profiling Suite scripts for public release
- Structure and document Internal Validation Suite scripts for public release
- Publish validation results as supplementary materials

### Added

#### Results Overview Aggregation

- **Hybrid Aggregate Metrics in Top Results Panel** - Added a second compact metrics row in `/results` overview card
  - New KPIs: `Integrated Relations`, `Databases with Matches`, `KO Match Rate`
  - Added per-database contribution badges (BioRemPP, HADEG, ToxCSM, KEGG) with input relation totals and share percentages
  - Added compact tooltip for aggregation semantics (sum of first relation metric per database; overlap may exist)

- **Metadata Contract Extension** - Added optional aggregate payload generated during processing
  - New key: `metadata["database_aggregate_overview"]`
  - Fields: `total_relations_input`, `active_databases`, `total_databases`, `ko_match_rate_pct`, `matched_kos`, `total_kos`, `per_database`

### Changed

#### Dynamic Database Overview Cards (4 Databases)

- **Database Cards Refactor** - Replaced hardcoded overview values with dynamic values from processing metadata
  - BioRemPP: dynamic `enzyme_compound_relations`, `environmental_compounds`, `compound_classes`, `regulatory_frameworks`
  - HADEG: dynamic `gene_pathway_relations`, `unique_ko_numbers`, `degradation_pathways`, `compound_categories`
  - ToxCSM: dynamic `environmental_compounds`, `toxicity_endpoints`, `toxicity_categories`
  - KEGG: dynamic `gene_pathway_associations`, `unique_ko_numbers`, `degradation_pathways`

- **Input-vs-Reference Presentation Rule** - Updated KPI display behavior for readability and tidy-data consistency
  - First metric in each database card now shows **input value only**
  - Remaining metrics keep input value with compact reference indicator (database icon + value)
  - Replaced explicit "Global" text with a small icon hover label (`Refrence database value`) to reduce visual noise

- **ToxCSM Label Update** - Renamed first ToxCSM KPI label to `KO-Compound Relations`

#### Processing Pipeline and Compatibility

- **Service-Layer Aggregation Builders** - Added dedicated builders for database overview and aggregate overview in `DataProcessingService`
- **Server-Side Rendering Integration** - Kept existing architecture (`DataProcessingService -> merged-result-store -> /results`) without introducing new callbacks
- **Backward Compatibility Fallbacks** - Added resilient fallback logic when `database_overview` or `database_aggregate_overview` is missing (older sessions)

### Fixed

- **Overview Data Accuracy** - Ensured top-panel aggregate volume uses input-derived relations only, avoiding misleading comparisons with global table size for tidy datasets
- **ToxCSM Endpoint Semantics** - Kept endpoint counting dynamic and column-driven (`value_*`) for both input and reference contexts
- **Regression Coverage** - Added/updated unit tests for:
  - `database_overview` and `database_aggregate_overview` metadata structure and formulas
  - Top results panel rendering with aggregate payload
  - Fallback rendering for sessions missing new metadata keys

---

## [1.0.4-beta] - 2026-01-30
##### The application will remain in beta until the article is officially released.

### Added

#### Database Schema Documentation

- **Database Schema Pages** - Comprehensive schema documentation for all 4 integrated databases
  - Each schema includes: column specifications, data types, controlled vocabularies, cross-references, usage examples (R/Python)

#### CI/CD & Infrastructure

- **Docker Build Cache Optimization**
  - Implemented BuildKit cache mounts for pip installations (`--mount=type=cache,target=/root/.cache/pip`)
  - Reordered COPY commands to preserve dependency cache when only source code changes
  - Removed `PIP_NO_CACHE_DIR=1` environment variable to enable pip caching
  - Created minimal package structure before pip install to satisfy setuptools requirements
  - **Impact**: Rebuild time reduced to ~15 seconds for code-only changes

### Changed

#### User Interface

- **Navigation Header** - Reordered and renamed navigation links for improved UX
  - New order: Home → User Guide → **Databases** (renamed from "Schemas") → Regulatory → Methods → Documentation → FAQ → Contact
  - File: `src/presentation/components/base/header_component.py`

#### Database Schema Corrections

- **Column Descriptions** - Enhanced accuracy and clarity
  - **BioRemPP Schema**:
    - `cpd`: Clarified as unique KEGG Compound identifier
    - `referenceAG`: Updated to indicate regulatory framework references
    - `compoundname`: Specified IUPAC nomenclature
    - `genesymbol`: Clarified KEGG annotation origin
    - `enzyme_activity`: Corrected source attribution to IUBMB/IUPAC Biochemical Nomenclature Committee
  - **KEGG Schema**:
    - `genesymbol`: Updated to reflect KEGG annotation and origin

- **Usage Examples** - Standardized file path placeholders
  - Changed hardcoded paths (e.g., `"data/databases/biorempp_db.csv"`) to generic `"path/"` placeholder
  - Improved portability and clarity of R and Python code examples
  - Files: All 4 schema YAML configuration files

### Removed

- **UI Component Redundancy**
  - Removed "Top Pathways" card from KEGG table section
  - Removed redundant sections from `database_description.py` component

### Fixed

- **Session Continuity** - Database Info buttons now open in new tabs without disrupting active analysis sessions
- **Schema Rendering** - Corrected toxicity endpoint category labels to match actual database values

---

## [1.0.3-beta] - 2026-01-17
##### The application will remain in beta until the article is officially released.

### Added

#### Documentation Structure

- **Comprehensive Index Pages** - Added index.md for all major documentation sections
  - `docs/getting-started/index.md` - Quick navigation, workflow overview, FAQ summary (107 lines)
  - `docs/user-guide/index.md` - Results, interpretation, downloads, troubleshooting overview (79 lines)
  - `docs/database_schemas/index.md` - 4 database schemas with integration architecture diagram (196 lines)
  - `docs/validation/index.md` - 3-pillar validation framework overview (235 lines)

#### Validation & Quality Assurance

- **Computational Profiling Suite (v1.0)** - Performance characterization and reproducibility
  - `docs/validation/profiling-biorempp.md` - Consolidated profiling documentation (280 lines)
  - 5 profiling targets: database_load, biorempp_operations, io_operations, batch_export, data_transforms
  - Total execution time: 12.50 seconds, Total memory: 167.3 MB
  - Instrumentation: cProfile, tracemalloc, psutil

- **Unit Test Suite Documentation**
  - `docs/validation/test-suite.md` - 53 unit test modules across 3 architectural layers (378 lines)
  - Coverage: Domain (entities, value objects, strategies), Application (services, DTOs, mappers), Infrastructure (cache, config, repositories)
  - Test design principles: Determinism, Isolation, Dependency Substitution, Fast Execution

- **Internal Validation Suite**
  - 7 validation components: Provenance Snapshot, Schema Integrity, Cross-Database Overlap, Mapping Consistency, Roundtrip Regression, Use Case Invariants, Controlled Vocabulary Audit

### Changed

#### Documentation Improvements

- **MkDocs Navigation** - Updated `mkdocs.yml` with index entries for all sections
  - Added index pages to: Getting Started, User Guide, Database Schemas, Validation & QC
  - Reordered Validation & QC entries for logical flow

- **Use Cases Index** - Fixed markdown list rendering for proper MkDocs display
  - Added blank lines after numbered items with sub-content
  - Improved visual separation of list items in rendered output


- **Version Numbering** - Updated application version
  - Changed from `v1.0.0-beta` to `v1.0.3-beta` in `docs/index.md`
  - Reflects documentation consolidation milestone

### Removed

- **Redundant UI Components**
  - Database Documentation card from documentation page (consolidated into single webservice card)

### Fixed

- **Markdown Rendering** - Fixed numbered list display in use_cases/index.md
- **Schema Examples** - Corrected file paths in R and Python code snippets
- **Regex Patterns** - Fixed escape sequences in hadeg-schema.md and kegg-schema.md (`\\\\d` → `\\\\\\\\d`)

---

## [1.0.2-beta] - 2025-12-25
##### The application will remain in beta until the article is officially released.

### Added

#### Documentation Infrastructure
- Complete use case documentation for all 56 analytical use cases organized into 8 modules
  - Module 1 (6 cases): Comparative Assessment of Databases, Samples, and Regulatory Frameworks
  - Module 2 (5 cases): Exploratory Analysis - Ranking Functional Potential
  - Module 3 (7 cases): System Structure - Clustering, Similarity, Co-occurrence
  - Module 4 (13 cases): Functional and Genetic Profiling 
  - Module 5 (6 cases): Modeling Interactions among Samples, Genes, and Compounds
  - Module 6 (5 cases): Hierarchical and Flow-based Functional Analysis
  - Module 7 (7 cases): Toxicological Risk Assessment and Profiling
  - Module 8 (7 cases): Assembly of Functional Consortia
- Each use case includes scientific rationale, analytical workflow, interpretation guidelines, and activity diagrams

#### Legal and Citation Pages
- **How to Cite page**: Comprehensive citation guidelines with:
  - Pre-DOI provisional citation formats
  - Post-DOI citation instructions
  - BibTeX templates for academic references
  - Third-party resource attribution (KEGG, HADEG, toxCSM)
  - FAIR principles and versioning best practices
- **Terms of Use page**: Complete legal framework in documentation (`docs/about/terms-of-use.md`) covering:
  - Scope and purpose of BioRemPP as academic research tool
  - Permitted uses (research, education) and prohibited uses (clinical, regulatory)
  - User responsibilities (data ownership, citation, third-party license compliance)
  - Privacy-by-design philosophy (no accounts, no persistent storage, session-based processing)
  - Service limitations and availability (best-effort, no SLA)
  - Licensing details (Apache 2.0 for code, CC BY 4.0 for database)
  - Warranty disclaimers and liability limitations
  - Contact information for institutional support

#### Documentation Site Enhancements
- MkDocs navigation structure for 65+ documentation pages
- ReadTheDocs integration configuration (`.readthedocs.yml`)
- Enhanced `docs/index.md` homepage with detailed service overview
- GLightbox integration for lightbox viewing of activity diagrams
  - `docs/javascripts/glightbox.min.js`: Core library
  - `docs/javascripts/lightbox-init.js`: Initialization script with timeout
  - `docs/stylesheets/glightbox.min.css`: Styling

### Changed
- Updated FAQ with cross-references to new citation and terms pages
- Enhanced home page navigation to include citation and terms links
- Improved page registration system for new pages

---

## [1.0.0-beta] - 2025 (2025-12-14)
##### The application will remain in beta until the article is officially released.
### Added

#### Architecture & Design

- Implemented Clean Architecture with 4 distinct layers (Domain, Application, Infrastructure, Presentation)
- Added Strategy Pattern for plot generation (19 chart strategies)
- Implemented Factory Pattern for dynamic info panel generation
- Added YAML-based configuration system for use cases and info panels
- Implemented multi-layer caching system (Memory, DataFrame, Graph)

#### Modules & Use Cases

- **Module 1:** 6 use cases - Comparative Assessment of Databases, Samples, and Regulatory Frameworks
- **Module 2:** 5 use cases - Exploratory Analysis: Ranking the Functional Potential
- **Module 3:** 7 use cases - System Structure: Clustering, Similarity, and Co-occurrence
- **Module 4:** 13 use cases - Functional and Genetic Profiling
- **Module 5:** 5 use cases - Modeling Interactions among Samples, Genes, and Compounds
- **Module 6:** 5 use cases - Hierarchical and Flow-based Functional Analysis
- **Module 7:** 7 use cases - Toxicological Risk Assessment and Profiling
- **Module 8:** 7 use cases - Assembly of Functional Consortia
- **Total:** 56 analytical use cases across 8 specialized modules

#### Visualizations

- Heatmaps (standard, scored, faceted)
- Bar charts and Stacked bar charts
- Box & Scatter plots
- Dot plots and Density plots
- Correlograms and PCA plots
- Treemaps and Sunburst charts
- Network graphs and Sankey diagrams
- Chord diagrams
- Radar charts
- Hierarchical clustering and Dendrograms
- UpSet plots and Frozenset-style set views

#### Databases & Integration

- Integrated BioRemPP curated database
- Integrated KEGG (Kyoto Encyclopedia of Genes and Genomes)
- Integrated HADEG (Hydrocarbon Degradation Database)
- Integrated toxCSM (Toxicity prediction database)
- Added 7 regulatory framework classifications (IARC, EPA, ATSDR, WFD, PSL, EPC, CONAMA)

#### User Experience

- User interface with Bootstrap components
- Interactive Plotly visualizations with zoom, pan, and export
- Progress tracking during data processing
- Session-based storage with automatic cleanup
- Analysis Suggestions panel for guided workflows
- Quick navigation sidebar for modules
- Comprehensive data tables with AG Grid

#### Data Export

- CSV export for all database results
- Excel (.xlsx) export with formatting
- JSON export for programmatic access
- PNG/SVG/JPEG export for charts via Plotly

#### Documentation

- Comprehensive FAQ page with 8 sections
- Complete API reference with auto-generated docs
- User guide with step-by-step instructions
- Scientific documentation for methodologies
- Regulatory references documentation
- 56 use case documentation pages

---

## Upcoming Features

### Under Consideration
- Additional visualization types
- Performance optimizations
- Python package (pip installable)
- Command-line interface (CLI)
- Integration with additional databases
- User accounts and saved analyses
- Collaboration features

---

## Contributing

We welcome contributions! Please see our [GitHub repository](https://github.com/BioRemPP/biorempp_web) for contribution guidelines.

---

## Support

For questions, bug reports, or feature requests:

- **GitHub Issues:** [BioRemPP Issues](https://github.com/BioRemPP/biorempp_web/issues)
- **Email:** biorempp@gmail.com
---

**Last Updated:** 2026 -  Migration to organization repository
