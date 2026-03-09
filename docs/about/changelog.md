# Changelog

All notable changes to BioRemPP will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### To-Do

- Structure and document Profiling Suite scripts for public release

---

## [1.0.9-beta] - 2026-03-07
##### The application will remain in beta until the article is officially released.

### Added

#### Results Runtime Modularization and Observability Toolkit

- **Lazy modular shell for `/results`** with on-demand module rendering and lightweight context loading.
- **Collapsible navigation groups by analysis module** to reduce scroll depth and improve navigation efficiency.
- **Observability toolkit for performance tracking**
- **Client/server transition telemetry integration**


### Changed

#### Results UX, Navigation, and Loading Consistency

- **Cross-module hash navigation behavior** updated to synchronize module selection and canonical anchor scrolling (`#uc-x-y-card`).
- **Analysis suggestions link standardization** to compact `View UC x-x` labels and consistent `Relevant Use Cases` blocks.

### Fixed

#### Results Runtime Regressions and Data Consistency

- **Internal navigation regression** that could trigger white-screen/global-spinner behavior during in-page interactions.
- **Workflow modal auto-open regression** on initial `/results` render.
- **Top-scroll behavior regression** when transitioning to `/results`.

---

## [1.0.8-beta] - 2026-03-04
##### The application will remain in beta until the article is officially released.

### Added

#### HTTP Error Pages and Centralized Error Catalog

- **Centralized HTTP error catalog** with typed specifications (`HttpErrorSpec`) for `400` and `500`, including stable titles, user-facing guidance, and JSON-safe message contracts.
- **Custom browser-facing error pages** for bad requests and internal failures, aligned with BioRemPP visual shell and support actions (`Back to Home`, `Contact Support`).
- **Flask-level HTTP error handlers** with content negotiation to preserve Dash protocol compatibility on internal JSON requests.

### Changed

#### Error Routing, Response Semantics, and App Integration

- **Application routing expanded** with explicit error paths (`/error/400`, `/error/500`) for direct navigation and operational validation.
- **Centralized error-handler registration** in app bootstrap, keeping real HTTP status codes in browser responses while returning compact JSON payloads for Dash/internal endpoints.
- **Public file download error consistency** by reusing shared file-not-found payload contract in allowlisted static-data routes.

#### Methods Access in Use-Case Panels

- **Methods modal access embedded in use-case headers** across analytical modules, adding a direct `Methods` action in panel controls (adjacent to `Download Data` where available).
- **Pattern-matching modal integration standardized** in use-case layouts, reusing existing `link/modal/modal-close` callback IDs for unified behavior with the Methods page.

### Fixed

#### Error Handling Compatibility and Safety

- **Dash callback compatibility during HTTP errors** by preventing HTML fallback on internal JSON/Dash requests.
- **Safer client-visible failure messaging** for `500` responses, avoiding exposure of internal exception details while preserving structured server logs.

---

## [1.0.7-beta] - 2026-02-27
##### The application will remain in beta until the article is officially released.

### Added

#### Resume by Job ID + Production Observability

- **Resume Analysis by Job ID (same-browser)** with temporary payload persistence and recovery flow from homepage to `/results`.
- **Dual backend support for resume persistence** (`diskcache` baseline and `redis` for multi-worker scale), including backend resolution by environment.
- **Prometheus/Grafana observability stack** with instrumentation for processing, resume flow, cache behavior, and callback execution.
- **Operational telemetry and alerting** for resume outcomes (`not_found`, `token_mismatch`, `save_failed`, `rate_limited`) and worker health.

### Changed

#### Security, Deployment, and Routing

- **Production hardening policy** with fail-fast validation for required secrets and safer production defaults.
- **Nginx-first production topology** with internal app exposure, metrics protection, and institutional edge-TLS alignment.
- **Configurable base path support** via `BIOREMPP_URL_BASE_PATH`, preserving root compatibility while enabling subpath deployments.
- **Incremental deployment model** using environment overlays for baseline (`prod`) and full stack (`prod + cache + observability`) activation.

#### UI and Editorial Alignment

- **Homepage workflow refinement** based on editorial feedback (input onboarding flow, resume panel positioning, and cleaner action hierarchy).
- **Deprecated reviewer disclaimer removed** (UI, callback registration, and related page module).
- **Job ID UX improvements** in processing/results flow, with clearer recovery messaging and copy-oriented interaction.

### Fixed

#### Reliability and Runtime Consistency

- **Results navigation stability** under production proxy/base-path scenarios.
- **Nginx and app integration issues** affecting request routing, health behavior, and payload handling.
- **UpSet rendering consistency** by centralizing dimension behavior in the shared strategy path.

---

## [1.0.6-beta] - 2026-02-19
##### The application will remain in beta until the article is officially released.

### Added

#### Internal Validation (GX)

- **Official Internal Validation Suite in Root Directory**
  - Added complete `internal_validation/` structure with configuration, scripts, suites, context, outputs, and operational docs.
  - Added GX orchestration scripts:
    - `internal_validation/scripts/run_all_gx.py`
    - `internal_validation/scripts/ci_validation.py`
    - `internal_validation/scripts/init_gx_context.py`
    - `internal_validation/scripts/configure_data_sources.py`
    - `internal_validation/scripts/verify_gx_setup.py`
  - Added hybrid task modules for provenance, overlap, roundtrip, and parity support in:
    - `internal_validation/scripts/tasks/`

- **GX Validation Definitions and Checkpoints**
  - Added schema, mapping, invariants, and vocabulary suites with persisted GX artifacts under:
    - `internal_validation/gx_context/expectations/`
    - `internal_validation/gx_context/validation_definitions/`
    - `internal_validation/gx_context/checkpoints/`

- **CI Workflow for Internal Validation**
  - Added workflow:
    - `.github/workflows/internal_validation_gx.yml`

### Changed

#### Validation Strictness and Contracts

- **Strict Fixed Expectations for Consolidated Snapshot**
  - Replaced range/tolerance expectations with fixed-value constraints in GX suites.
  - Added fixed row-count contract per asset in:
    - `internal_validation/config/validation_config.yaml` (`expected_row_counts`)
  - Updated suite logic to enforce strict row counts and strict non-null checks.
  - Replaced toxCSM `value_*` range checks with fixed discrete domain checks (`0.00` to `1.00`, step `0.01`).

- **Output Ignore Rule for Roundtrip Summary**
  - Updated `.gitignore` to ignore dated roundtrip summary JSON files:
    - `internal_validation/outputs/*/05_example_roundtrip_regression/summary.json`

- **Dependency Scope**
  - Moved `great_expectations>=1.12,<2.0` to `dev` optional dependencies in `pyproject.toml`.

#### Validation Documentation

- Rewrote official validation documentation pages to reflect the GX implementation and current operational flow:
  - `docs/validation/index.md`
  - `docs/validation/internal-validation.md`
  - `docs/validation/validation-suite.md`
  - `docs/validation/validation-v1.md`

### Fixed

#### Checksum Consistency and Validation Reporting

- Updated `docs/validation/validation-v1.md` with real execution metrics from:
  - `internal_validation/outputs/2026-02-18/`
- Aligned checksum references in documentation with current dataset hashes.
- Updated `data/databases/checksums.sha256` to match current CSV files:
  - `biorempp_db.csv`: `216cf113400161d6eee8d4eefb13bab23f60f9286874fa41ae8d00f3fc4637c0`
  - `hadeg_db.csv`: `d546c01be1cf05866b18aa25fd1edb23e4d90f9ab4e65fb5e37911c1e57ce938`
  - `kegg_degradation_db.csv`: `f3df93d3bc5492043d2f6a9ea087b6687757e4757057ba1ab19c1a0d53fcd619`
  - `toxcsm_db.csv`: `0d4616930b438964d9e007b20c9ffb9c414879b775a3b89d660bfc6278fe5f38`

---

## [1.0.5-beta] - 2026-02-19
##### The application will remain in beta until the article is officially released.

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
