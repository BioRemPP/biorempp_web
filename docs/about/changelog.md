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

---

## [1.0.3-beta] - 2026-01-17

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

## [1.0.1-beta] - 2025-12-20

> **Note on Tag Versioning:** The previous tag `v1.0.1` was incorrectly versioned and should have been `v1.0.1-beta` per semantic versioning guidelines. The application remains in beta status until official article publication.

### Added

#### DevOps & CI/CD

- **GitHub Actions Workflow for Documentation** ([#001])
  - Automated MkDocs build validation on push/PR to `main` and `dev` branches
  - Path-based triggering for documentation-related files
  - Build artifact upload with 7-day retention
  - Comprehensive error reporting and logging
  - Dependencies installed via `pyproject.toml[docs]`

- **ReadTheDocs Multi-Version Deployment**
  - Configured automatic deployment for `main` (stable) and `dev` (latest) branches  
  - Webhook integration for automatic builds on push
  - Multi-format export: HTML, PDF, EPUB
  - Version switcher for accessing different documentation versions
  - Documentation URLs:
    - Development (latest): https://biorempp.readthedocs.io/en/latest/
    - Production (stable): https://biorempp.readthedocs.io/en/stable/

### Fixed

- **API Documentation Module References**
  - Corrected mkdocstrings import paths for cache module classes
  - Changed from submodule paths to package-level exports
  - Resolved `src.infrastructure.cache` import errors in API docs

- **ReadTheDocs Configuration**
  - Fixed `.readthedocs.yml` syntax: `extra_requires` → `extra_requirements`
  - Removed `cache/` from `.gitignore` to allow proper module documentation

- **GitHub Actions Permissions**
  - Added `.github/workflows/docs-ci.yml` to repository (was blocked by gitignore)
  - Configured proper workflow permissions for actions execution

### Technical Details

- **Python Version:** 3.11
- **CI Actions:** `checkout@v4`, `setup-python@v5`, `upload-artifact@v4`
- **Build Command:** `mkdocs build --verbose`
- **Dependencies:** Managed via `pyproject.toml[docs]` optional dependency group

---

## [1.0.0-beta] - 2025-12-14

##### The application will remain in beta (v1.0.0-beta) until the article is officially released.

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

- REST API for programmatic access
- Batch processing capabilities
- Additional visualization types
- Performance optimizations
- Mobile app (iOS/Android)
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

**Last Updated:** 2026-01-17

[unreleased]: https://github.com/BioRemPP/biorempp_web/compare/v1.0.3-beta...HEAD
[1.0.3-beta]: https://github.com/BioRemPP/biorempp_web/compare/v1.0.1-beta...v1.0.3-beta
[1.0.1-beta]: https://github.com/BioRemPP/biorempp_web/compare/v1.0.0-beta...v1.0.1-beta
[1.0.0-beta]: https://github.com/BioRemPP/biorempp_web/releases/tag/v1.0.0-beta

