# BioRemPP Web Service (v1.0.0-beta)

**Bioremediation Potential Profile - Scientific Web Application**

[![Documentation](https://img.shields.io/badge/docs-Read%20the%20Docs-blue)](placeholder)
[![Docker](https://img.shields.io/badge/docker-ready-brightgreen)](https://hub.docker.com/r/biorempp/biorempp-web)
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Database: CC BY 4.0](https://img.shields.io/badge/Database-CC%20BY%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by/4.0/)

## Quick Links

- **🌐 Live Application:** [https://biorempp.org](https://biorempp.org) *(placeholder)*
- **📚 Documentation:** [https://biorempp.readthedocs.io](https://biorempp.readthedocs.io) *(placeholder)*
- **📖 Methods:** [Article DOI](https://doi.org/placeholder) *(pending publication)*
- **📘 User Guide:** [Getting Started](https://biorempp.readthedocs.io/en/latest/user-guide/) *(placeholder)*
- **🐛 Issue Tracker:** [GitHub Issues](https://github.com/BioRemPP/biorempp_web/issues) *(placeholder)*
- **📝 How to Cite:** [See Citation](#citation)

---

## Scope

BioRemPP (Bioremediation Potential Profile) is a scientific web service for bioremediation-oriented functional analysis. It integrates curated databases (BioRemPP Database, KEGG, HADEG, toxCSM) with regulatory frameworks to enable comprehensive assessment of functional potential for environmental remediation. 

**Target Audience**: Computational and environmental biologists, bioinformatics researchers, and scientific reviewers interested in data-driven assessment of bioremediation potential and functional annotation pipelines.

## Core Capabilities

- **Inputs**  
  Tab-separated sample–KO lists in plain text format. Each sample header must be prefixed with `>`, followed by KEGG Orthology identifiers (`K#####`).  
  **Limits:** up to 100 samples and 10,000 KO identifiers per upload.  
  **Encoding:** UTF-8.

- **Outputs**  
  Integrated result tables available for download (CSV, TSV, JSON), eight modular analysis sections with 56 use cases, interactive visualizations, comparative cross-database assessments, functional profiling, toxicological risk evaluation, and guidance for interpreting potential bioremediation consortia.

- **Integrations**  
  - **BioRemPP Database** – Curated orthology–compound associations relevant to bioremediation  
  - **HADEG Database** – Hydrocarbon and xenobiotic degradation pathways and genes  
  - **toxCSM** – In silico toxicity predictions  
  - **KEGG** – Functional orthology and pathway mapping  
  - **Regulatory Frameworks** – Priority pollutant classifications from international and national agencies (IARC, EPA, ATSDR, WFD, PSL, EPC, CONAMA)


---

## Data Policy

**Privacy and Data Handling:**

- **No user accounts:** The service operates without authentication or user registration
- **No persistent storage:** Uploaded data is processed in-memory during the session only
- **Session-based processing:** Each analysis session is isolated and temporary
- **Data retention:** Uploaded files and results are automatically deleted when the browser session ends or after 6 hours of inactivity, whichever comes first
- **Logging:** The service logs only:
  - IP addresses (for rate limiting and abuse prevention)
  - User-agent strings (for compatibility monitoring)
  - Error messages (for debugging and service improvement)
  - **No uploaded data content is logged**
- **Security assumptions:**
  - HTTPS/TLS encryption is enforced in production deployments
  - File uploads are validated for format, size, and content before processing
  - Maximum upload size: 5 MB
  - Maximum samples per upload: 100
  - Maximum KO entries per upload: 500,000

---

## Quick Start

### Docker Deployment (Recommended)

### Prerequisites

- Docker and Docker Compose (recommended for reproducibility)
- Python 3.11+ (for local development)
- 4 GB RAM minimum (8 GB recommended for larger datasets)

**Development Mode:**
```bash
# Clone repository
git clone https://github.com/BioRemPP/biorempp_web.git
cd biorempp_web

# Copy environment template
cp .env/env.development .env/env.local

# Start service
docker compose --env-file .env/env.local --profile dev up

# Access application
# Open browser: http://localhost:8050
```

**Production Mode:**
```bash
# Copy production environment template
cp .env/env.production .env/env.local

# Edit .env/env.local and set:
# - SECRET_KEY (generate with: openssl rand -hex 32)
# - DOMAIN (your domain name)
# - Other production settings as needed

# Start production service with nginx
docker compose --env-file .env/env.local --profile prod --profile nginx up -d

# Access application
# Open browser: http://localhost (or https://yourdomain.com if SSL configured)
```

**Health Check:**
```bash
# Verify service is running
curl http://localhost:8050/health  # Development
curl http://localhost/health        # Production (via nginx)
```

**Expected response:**
```json
{
  "status": "healthy",
  "version": "1.0.0-beta",
  "environment": "production"
}
```

### Local Development (Without Docker)

**Prerequisites:** Python 3.11+

```bash
# Clone repository
git clone https://github.com/BioRemPP/biorempp_web.git
cd biorempp_web

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -e ".[dev]"

# Set environment variables (optional)
export BIOREMPP_ENV=development
export BIOREMPP_DEBUG=True
export BIOREMPP_PORT=8050

# Run application
python biorempp_app.py

# Access application
# Open browser: http://127.0.0.1:8050
```

**Note:** Docker deployment is strongly recommended for reproducibility and to ensure all dependencies are correctly configured.

---

## Input Format

BioRemPP accepts plain text files containing KO (KEGG Orthology) identifiers organized by sample.

### Format Specification

```
>Sample_Name_1
K00001
K00002
K00003
>Sample_Name_2
K00001
K00004
K00005
```

### Requirements

- **File encoding:** UTF-8 (no BOM)
- **File extension:** `.txt`
- **Sample Headers**: Lines starting with `>` denote sample names. Sample names should follow this pattern: `^[A-Za-z0-9_\-\.]+$` (alphanumeric, underscores, hyphens, dots).
- **KO Identifiers**: One KO per line after the sample header. KO format: `^K\d{5}$` (e.g., `K00001`, `K12345`).
- **One KO per line:** No additional text or whitespace after KO identifier
- **Line Endings**: Unix (`\n`) or Windows (`\r\n`) line endings accepted.

### Constraints

| Parameter | Limit | Configurable via |
|-----------|-------|------------------|
| Maximum file size | 5 MB | `BIOREMPP_UPLOAD_MAX_SIZE_MB` |
| Maximum samples | 100 | `BIOREMPP_UPLOAD_SAMPLE_LIMIT` |
| Maximum KO entries (total) | 500,000 | `BIOREMPP_UPLOAD_KO_LIMIT` |
| Maximum KOs per sample | 10,000 | `BIOREMPP_PARSING_MAX_KOS_PER_SAMPLE` |

### Example File

See [`data/exemple_dataset.txt`](data/exemple_dataset.txt) for a complete example with real data.

### Common Validation Errors

- **Invalid KO format:** KO identifiers must be exactly 5 digits (e.g., `K00001`, not `K1` or `K000001`)
- **Missing sample header:** Each KO list must be preceded by a `>Sample_Name` line
- **Invalid characters in sample name:** Only alphanumeric characters, underscores, hyphens, and dots are allowed
- **File too large:** Reduce number of samples or KO entries
- **Encoding issues:** Ensure file is saved as UTF-8

---

## Outputs and Downloads


### Results Page Structure

After successful data upload and processing, BioRemPP generates a structured results page composed of the following elements:

Results are first contextualized through integration with multiple reference databases:

1. **BioRemPP Database** – Curated enzyme–compound associations supporting bioremediation-relevant pathways  
2. **HADEG Database** – Gene and pathway annotations related to hydrocarbon and xenobiotic degradation  
3. **ToxCSM Database** – In silico toxicity predictions (e.g., LD₅₀, hepatotoxicity, AMES mutagenicity)  
4. **KEGG Database** – Functional orthology assignments and pathway mapping

#### Analytical Modules and Use Cases

Analytical results are further organized into:

- **Module Selection** – Eight specialized analytical modules covering complementary aspects of bioremediation potential  
- **Use Case Panels** – A total of 56 interactive use cases, each providing:
  - Clearly defined scientific questions and interpretation guidelines  
  - Interactive visualizations (Plotly-based)  
  - Tabular result views (AG Grid with sorting, filtering, and pagination)  
  - Download options for underlying raw and processed data


### Available Modules

| Module | Use Cases | Focus |
|--------|-----------|-------|
| **Module 1** | 6 | Comparative assessment of databases, samples, regulatory frameworks |
| **Module 2** | 5 | Exploratory analysis: ranking functional potential |
| **Module 3** | 7 | System structure: clustering, similarity, co-occurrence |
| **Module 4** | 13 | Functional and genetic profiling |
| **Module 5** | 5 | Modeling interactions among samples, genes, compounds |
| **Module 6** | 5 | Hierarchical and flow-based functional analysis |
| **Module 7** | 7 | Toxicological risk assessment and profiling |
| **Module 8** | 7 | Assembly of functional consortia |

### Download Formats

All data tables can be exported in:

- **CSV** (`.csv`) - Comma-separated values, UTF-8 encoded
- **Excel** (`.xlsx`) - Microsoft Excel format with formatting
- **JSON** (`.json`) - Structured data for programmatic access

Charts can be exported as:

- **PNG** - Raster image (default: 1200x800px)

### Key Output Fields

Common fields across output tables:

- `Sample`: Sample identifier from input file
- `KO`: KEGG Orthology identifier
- `Pathway`: KEGG pathway name
- `Compound_Class`: Chemical compound class (from BioRemPP database)
- `Compound_Name`: Specific compound name
- `Gene_Symbol`: Gene symbol associated with KO
- `Enzyme_Activity`: Enzyme activity description
- `Regulatory_Status`: Classification according to regulatory frameworks
- `Toxicity_Prediction`: toxCSM-based toxicity predictions (when available)

### Database Versioning

All outputs are linked to specific database versions:

- **BioRemPP Database:** v1.0 (2025)
- **KEGG:** Release 116.0+/12-19 (December 2025)
- **HADEG:** Commit 8f1ff8f (2023)
- **toxCSM:** v1.0 (2022)

---

## Methods

**Note:** Full methodological details are provided in the official documentation. The following is a high-level overview.

### Data Sources

- **BioRemPP Database:** Curated database linking KO identifiers to bioremediation-relevant compounds, genes, and enzymatic activities
- **KEGG:** Metabolic pathway annotations and KO definitions
- **HADEG:** Hydrocarbon degradation gene database
- **toxCSM:** Computational toxicity predictions for chemical compounds
- **Regulatory Frameworks:** IARC, EPA, ATSDR, WFD, PSL, EPC, CONAMA classifications

### Mapping Strategy

The BioRemPP mapping strategy follows a structured, multi-stage integration workflow designed to ensure consistency, traceability, and biological relevance:

- **Input Validation**  
  Enforcement of KEGG Orthology (KO) identifier format (`K#####`), removal of duplicate entries, and verification of sample and identifier count constraints.

- **KO Validation**  
  Submitted KO identifiers are validated against reference KEGG resources to ensure identifier consistency and current nomenclature.

- **Database Integration**  
  Validated KOs are mapped through exact identifier matching against locally maintained copies of the BioRemPP, HADEG, and toxCSM databases.

- **Cross-Referencing and Annotation**  
  Cascading joins are performed across multiple biological layers (KO → EC → Compound → Pathway → Toxicity), enabling functional annotation of genes, enzymatic activities, metabolic pathways, and associated compounds.

- **Regulatory Classification**  
  Identified compounds are classified according to seven international regulatory frameworks, providing contextual relevance for environmental and toxicological assessment.

- **Toxicity Assessment**  
  Compound-level toxicological properties are evaluated using toxCSM predictions, including endpoints relevant to environmental and human health risk.


### Quality Control

- Input validation (format, encoding, KO pattern matching)
- Database consistency checks (referential integrity)
- Missing data handling (explicit reporting of unavailable annotations)

### Computational Approach

- **Architecture:** Clean Architecture with 4 layers (Domain, Application, Infrastructure, Presentation)
- **Caching:** Multi-layer caching system (memory, DataFrame, graph) for performance optimization
- **Visualization:** Strategy Pattern for dynamic chart generation (19 chart types)
- **Configuration:** YAML-based configuration for use cases and info panels

**For detailed methods, see:** [Official Use Case Documentation](https://doi.org/placeholder) *(pending publication)*

---

## Architecture Overview

BioRemPP follows **Clean Architecture** principles with clear separation of concerns:

### Architectural Layers

```
┌─────────────────────────────────────────────────┐
│         Presentation Layer (Dash/Flask)         │
│   - Web pages (homepage, results, user guide)   │
│   - Callbacks (upload, navigation, downloads)   │
│   - Components (charts, tables, accordions)     │
└─────────────────────────────────────────────────┘
                       ↓
┌─────────────────────────────────────────────────┐
│          Application Layer (Services)           │
│   - Data processing orchestration               │
│   - DTO mappers (domain ↔ presentation)         │
│   - Plot services (visualization generation)    │
│   - Cache management                            │
└─────────────────────────────────────────────────┘
                       ↓
┌─────────────────────────────────────────────────┐
│            Domain Layer (Business Logic)        │
│   - Entities: Sample, Dataset, MergedData       │
│   - Value Objects: KO, SampleName               │
│   - Domain Services: Validation, aggregation    │
│   - Plot Strategies (module-specific logic)     │
└─────────────────────────────────────────────────┘
                       ↓
┌─────────────────────────────────────────────────┐
│       Infrastructure Layer (Data Access)        │
│   - CSV/TSV repositories (database loaders)     │
│   - File parsers (upload processing)            │
│   - Logging and configuration management        │
└─────────────────────────────────────────────────┘
```

### Technology Stack

**Backend**:
- **Python 3.11+**: Core language
- **Dash 3.3**: Reactive web framework
- **Flask 3.0**: WSGI server foundation
- **Pandas 2.x**: Data manipulation
- **Plotly 5.x**: Interactive visualizations
- **Gunicorn**: WSGI HTTP server (production)

**Frontend**:
- **Dash Bootstrap Components**: UI framework (Bootstrap 5)
- **Dash AG Grid**: Advanced data tables
- **Font Awesome**: Icons
- **Custom CSS**: Branding and theming

**Data Processing**:
- **NumPy, SciPy**: Numerical computing
- **scikit-learn**: Clustering and distance metrics
- **NetworkX**: Graph analysis
- **UpSetPlot**: Set visualization

**Infrastructure**:
- **Docker & Docker Compose**: Containerization
- **Nginx** (optional): Reverse proxy and SSL termination
- **diskcache**: Session-based caching
- **Redis** (optional): Distributed caching for multi-worker setups

**Development Tools**:
- **pytest**: Unit and integration testing
- **black, isort, flake8**: Code formatting
- **MkDocs**: Documentation generation

### Directory Structure

```
biorempp_web/
├── src/                          # Source code (Clean Architecture)
│   ├── domain/                   # Business entities and logic
│   │   ├── entities/             # Sample, Dataset, MergedData
│   │   ├── value_objects/        # KO, SampleName, CompoundClass
│   │   ├── services/             # Domain services (validation, etc.)
│   │   └── plot_strategies/      # Module-specific plot generation
│   ├── application/              # Application services
│   │   ├── services/             # Orchestration, caching, progress
│   │   ├── dto/                  # Data Transfer Objects
│   │   ├── mappers/              # DTO ↔ Entity conversion
│   │   └── plot_services/        # Plot generation coordination
│   ├── infrastructure/           # Data access and external systems
│   │   ├── repositories/         # CSV/TSV loaders
│   ├── presentation/             # Web UI (Dash)
│   │   ├── pages/                # Homepage, results, user guide, FAQ
│   │   ├── components/           # Reusable UI components
│   │   ├── callbacks/            # Dash callback handlers
│   │   └── layouts/              # Module-specific layouts
│   └── shared/                   # Cross-cutting utilities
│       └── logging/              # Logging configuration
├── data/                         # Databases and examples
│   ├── databases/                # BioRemPP, HADEG, ToxCSM, KEGG DBs
│   └── exemple_dataset.txt       # Sample input file
├── config/                       # Configuration
│   ├── settings.py               # Environment-based settings
│   ├── logging_dev.yaml          # Development logging config
│   └── logging_prod.yaml         # Production logging config
├── docs/                         # MkDocs documentation
│   ├── scientific/               # Methods, validation
│   ├── user-guide/               # User tutorials
│   ├── api/                      # API reference (auto-generated)
│   └── use_cases/                # Module-specific use cases
├── tests/                        # Test suite
│   ├── unit/                     # Unit tests (domain, services)
├── .docker/                      # Docker configuration
│   ├── Dockerfile                # Multi-stage build
│   └── healthcheck.sh            # Container health probe
├── biorempp_app.py               # Main application entry point
├── wsgi.py                       # WSGI entry for Gunicorn
├── gunicorn_config.py            # Gunicorn production settings
├── docker-compose.yml            # Multi-environment orchestration
├── pyproject.toml                # Python project metadata + deps
├── pytest.ini                    # Test configuration
├── mkdocs.yml                    # Documentation site config
└── README.md                     # (This file, once finalized)
```

### Key Design Patterns

- **Repository Pattern**: Abstracts database access (CSV files treated as repositories)
- **Strategy Pattern**: Plot generation varies by module (Module2PlotStrategy, Module3PlotStrategy, etc.)
- **Singleton Pattern**: PlotService instance shared across callbacks
- **DTO Pattern**: Decouples domain entities from presentation layer
- **Dependency Injection**: Services receive dependencies via constructor (testability)

---

## System Requirements & Deployment Notes

### Minimum Requirements

**Development:**
- CPU: 2 cores
- RAM: 4 GB
- Disk: 2 GB free space
- Docker: 20.10+ and Docker Compose 2.0+

**Production (Recommended):**
- CPU: 4 cores
- RAM: 8 GB
- Disk: 20 GB free space (for logs and caching)
- Docker: 20.10+ and Docker Compose 2.0+
- Reverse proxy: nginx (included in Docker Compose)

### Resource Limits (Docker)

Production deployment includes resource limits:

```yaml
limits:
  cpus: '4.0'
  memory: 8G
reservations:
  cpus: '2.0'
  memory: 4G
```

### Caching

- **Memory cache:** In-memory caching for frequently accessed data
- **DataFrame cache:** Disk-based caching for processed DataFrames
- **Graph cache:** Disk-based caching for visualizations
- **Optional Redis:** Can be enabled for distributed caching (see `docker-compose.yml` profile `cache`)

### Upload/Payload Limits

- Maximum file upload: 5 MB
- Maximum request timeout: 60 seconds 
- Maximum samples: 100
- Maximum KO entries: 500,000

### Scalability Notes

- **Horizontal Scaling**  
  Not currently supported due to stateful session-based processing. Horizontal scalability will be re-evaluated based on real-world usage patterns observed after public release.

- **Vertical Scaling**  
  Resource allocation (CPU and RAM) can be increased via Docker Compose configuration to accommodate higher workloads.

- **Performance**  
  Typical analyses (up to 50 samples and 10,000 KO identifiers) complete in under 30 seconds under standard deployment conditions.

- **Concurrency**  
  The service is deployed using Gunicorn with gevent workers (default configuration: 4 workers, up to 1,000 concurrent connections per worker).

- **Post-release Monitoring**  
  Infrastructure performance and usage metrics will be monitored following publication to inform iterative optimization, capacity planning, and potential architectural adjustments.


**Note:** No SLA or performance guarantees are provided. For high-throughput or production-critical deployments, contact the development team.

---

## API Availability

**BioRemPP is currently provided as an interactive web application; no stable public API is guaranteed.**

The following endpoints are available for monitoring and health checks:

### Health Check

```bash
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0-beta",
  "environment": "production",
}
```

### Version Information

```bash
GET /version
```

**Response:**
```json
{
  "version": "1.0.0-beta",
  "build_date": "2025-12-14",
  "python_version": "3.11"
}
```

**Note:** Programmatic access to analysis functions is not currently supported. The provision of a stable public API is under consideration for future releases


---

## Citation

### Web Service

If you use BioRemPP in your research, please cite:

```bibtex
@misc{biorempp2025,
  title={BioRemPP: Bioremediation Potential Profile Web Service},
  author={BioRemPP Development Team},
  year={2025},
  url={https://biorempp.org},
  note={Version 1.0.0-beta}
}
```

### Database

```bibtex
@dataset{biorempp_db2025,
  title={BioRemPP Database: Curated Bioremediation Functional Annotations},
  author={BioRemPP Development Team},
  year={2025},
  version={1.0},
  license={CC BY 4.0},
  url={https://biorempp.org/database}
}
```

### Article (Pending Publication)

```bibtex
@article{biorempp_article2025,
  title={BioRemPP: A Comprehensive Web Service for Bioremediation-Oriented Functional Analysis},
  author={[Authors]},
  journal={[Journal Name]},
  year={2025},
  doi={[DOI]},
  note={Manuscript in preparation}
}
```

**Provisional Citation (until article is published):**

> BioRemPP Development Team (2025). BioRemPP: Bioremediation Potential Profile Web Service (v1.0.0-beta). Available at: PLACEHOLDER

---

## Licensing

### Database Content

**License:** Creative Commons Attribution 4.0 International (CC BY 4.0)

The BioRemPP curated database (including compound-gene-pathway mappings, regulatory classifications, and annotations) is licensed under CC BY 4.0. You are free to:

- Share: Copy and redistribute the material
- Adapt: Remix, transform, and build upon the material

**Attribution:** Please cite the BioRemPP database as specified in the [Citation](#citation) section.

### Web Service Source Code

**License:** Apache License 2.0

The BioRemPP web service source code (Python application, Docker configuration, documentation) is licensed under Apache 2.0. You are free to:

- Use: Commercial and private use
- Modify: Modify and distribute
- Patent use: Grant of patent rights

**See:** [`LICENSE`](LICENSE) file for full terms.

### Third-Party Databases

BioRemPP integrates data from third-party sources, each with their own licenses:

- **KEGG:** Academic use free, commercial use requires license ([KEGG License](https://www.kegg.jp/kegg/legal.html))
- **HADEG:** Open access ([HADEG License](https://github.com/jarojasva/HADEG))
- **toxCSM:** Open access for academic use ([toxCSM License](https://biosig.lab.uq.edu.au/toxcsm/))

All dependencies listed in [pyproject.toml](pyproject.toml) are governed by their respective licenses


**Users are responsible for complying with all applicable third-party licenses.**

---

## Limitations  

BioRemPP is a research-oriented platform designed to support exploratory functional analyses related to bioremediation. The following limitations should be considered when interpreting results:

- **Not for Clinical or Regulatory Decision-Making**  
  BioRemPP outputs are intended exclusively for research and hypothesis generation. They must not be used as the sole basis for clinical diagnostics, regulatory submissions, or environmental remediation decisions without independent experimental and regulatory validation.

- **Database Scope and Coverage**  
  Results depend on the completeness and accuracy of the integrated reference resources (BioRemPP Database, HADEG, ToxCSM, KEGG). The absence of an annotation does not imply the absence of biological function; it may reflect incomplete or evolving database coverage.

- **Annotation Quality and Propagation Effects**  
  Although BioRemPP Database entries undergo manual curation, propagated inaccuracies from upstream sources (e.g., KEGG, UniProt) may persist. HADEG and ToxCSM annotations are computationally derived and may include false positives or context-dependent predictions.

- **Input Resolution Dependency**  
  Analyses are limited by the resolution of the input data. KEGG Orthology (KO) identifiers represent functional groups and may mask fine-grained differences such as substrate specificity or isoform-level variation.

- **No Quantitative Expression Modeling**  
  BioRemPP operates on presence/absence data only. Quantitative gene expression levels, transcript abundances, protein concentrations, or metabolic fluxes are not incorporated yet.

- **Toxicity Predictions**  
  Toxicological assessments derived from ToxCSM are in silico estimates based on machine learning models. These predictions require experimental confirmation before being used in safety or regulatory contexts.

- **Internal Validation and Benchmarking Scope**  
  The platform has been internally validated through consistency checks and reference-based comparisons using curated KEGG annotations and well-characterized bioremediation-related pathways and organisms (see Methods). As no directly comparable tools or frameworks are currently available, external benchmarking against alternative platforms is not claimed at this stage.


- **Database Versioning and Update Frequency**  
  Integrated databases are provided as versioned snapshots at deployment. Users are encouraged to consult release dates and re-run analyses when updated database versions become available.

- **Disclaimer**  
  BioRemPP is provided “as is,” without warranty of any kind. The authors and contributors assume no liability for interpretations or decisions derived from the use of this platform. Responsibility for result interpretation and downstream application lies solely with the user.


---

## Reproducibility & Versioning

### Web Service Version

- **Current Version:** 1.0.0-beta
- **Release Date:** 2025-12-14
- **Status:** Beta (pending article publication)

### Changelog

See [`CHANGELOG.md`](CHANGELOG.md) for detailed version history.

### Last Updated

**Documentation:** 2025-12-19  
**Application:** 2025-12-14

---

## Support, Contact, and Contributing

### Institutional Contact

**Email:** biorempp@gmail.com

**Response Time:** We aim to respond to inquiries within 5 business days. For urgent issues, please indicate "URGENT" in the subject line.

### Bug Reporting

**GitHub Issues:** [https://github.com/BioRemPP/biorempp_web/issues](https://github.com/BioRemPP/biorempp_web/issues) 

When reporting bugs, please include:

1. BioRemPP version (from `/version` endpoint or application footer)
2. Browser and OS information
3. Steps to reproduce the issue
4. Expected vs. actual behavior
5. Example input file (if applicable)
6. Screenshots or error messages

### Feature Requests

Feature requests are welcome via GitHub Issues. Please describe:

1. Use case and scientific motivation
2. Proposed functionality
3. Expected input/output
4. Potential impact on existing features

## Contributing

Community contributions are welcome and encouraged. A comprehensive contribution manual is currently under development and will provide detailed guidance for extending the BioRemPP framework with additional use cases, analytical modules, and integrations across other omics domains.

Future updates to the contribution guidelines will explicitly address the incorporation of new biological domains, multi-omics data types, and cross-domain analytical workflows within the BioRemPP platform.


### Community

- **Discussions:** [GitHub Discussions](https://github.com/BioRemPP/biorempp_web/discussions) *(placeholder)*

---

**BioRemPP v1.0.0-beta** | [Documentation](https://biorempp.readthedocs.io) | [GitHub](https://github.com/BioRemPP/biorempp_web) | [License](LICENSE)

