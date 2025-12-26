# Changelog

All notable changes to BioRemPP will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.0.2-beta.] - 2025-12-25

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
- **Terms of Use**: Complete legal framework covering scope, permitted/prohibited uses, user responsibilities, privacy policy, service limitations, licensing (Apache 2.0 / CC BY 4.0), and warranty disclaimers

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

**Last Updated:** 2025 -  Migration to organization repository
