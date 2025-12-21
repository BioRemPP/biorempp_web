# Changelog

All notable changes to BioRemPP will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.0.0-beta] - 2025 (2025-12-14)
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

**Last Updated:** 2025
