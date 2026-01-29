# BioRemPP Web Service

**Bioremediation Potential Profile — Scientific Web Application**

[![Documentation](https://img.shields.io/badge/docs-Read%20the%20Docs-blue)](https://biormepp-web.readthedocs.io/en/latest/)
[![Docker](https://img.shields.io/badge/docker-ready-brightgreen)](https://hub.docker.com/r/biorempp/biorempp-web)
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![Database: CC BY 4.0](https://img.shields.io/badge/Database-CC%20BY%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by/4.0/)

---

## Overview

BioRemPP is a scientific web service for bioremediation-oriented functional analysis. It integrates curated databases (BioRemPP, KEGG, HADEG, toxCSM) with international regulatory frameworks to assess functional potential for environmental remediation from KEGG Orthology (KO) annotations.

**Live Application:** [https://biorempp.cloud](https://biorempp.cloud)

---

## Quick Start

### Docker (Recommended)

```bash
docker run -p 8050:8050 biorempp/biorempp-web:latest
```

Open: **http://localhost:8050**

### Local Development

```bash
git clone https://github.com/BioRemPP/biorempp_web.git
cd biorempp_web
python -m venv venv && source venv/bin/activate
pip install -e ".[dev]"
python biorempp_app.py
```

> For detailed setup options, see [Quickstart Guide](https://biormepp-web.readthedocs.io/en/latest/getting-started/quickstart/).

---

## Input Format

Plain text file with KO identifiers organized by sample:

```
>Sample_1
K00001
K00002
>Sample_2
K00003
K00004
```

**Limits:** 100 samples, 500,000 KOs, 5 MB max file size.

> Full specification: [Input Format](https://biormepp-web.readthedocs.io/en/latest/getting-started/input-format/)

---

## Analytical Modules

BioRemPP provides **56 use cases** across **8 thematic modules**:

| Module | Focus |
|--------|-------|
| **1** | Comparative assessment (databases, samples, regulatory) |
| **2** | Exploratory analysis (functional potential ranking) |
| **3** | System structure (clustering, similarity, co-occurrence) |
| **4** | Functional and genetic profiling |
| **5** | Modeling interactions (samples, genes, compounds) |
| **6** | Hierarchical and flow-based functional analysis |
| **7** | Toxicological risk assessment |
| **8** | Assembly of functional consortia |

> Complete catalog: [Use Cases](https://biormepp-web.readthedocs.io/en/latest/use_cases/)

---

## Integrated Databases

| Database | Focus |
|----------|-------|
| **BioRemPP** | Compound-enzyme-agency mapping for bioremediation |
| **KEGG** | Xenobiotic metabolism and degradation pathways |
| **HADEG** | Aerobic hydrocarbon degradation enzymes |
| **toxCSM** | Computational toxicity predictions (31 endpoints) |

Regulatory frameworks: IARC, EPA, ATSDR, WFD, PSL, EPC, CONAMA.

> Details: [Data Sources](https://biormepp-web.readthedocs.io/en/latest/methods/data-sources/) | [Database Schemas](https://biormepp-web.readthedocs.io/en/latest/database_schemas/biorempp-schema/)

---

## Documentation

| Section | Description |
|---------|-------------|
| [Getting Started](https://biormepp-web.readthedocs.io/en/latest/getting-started/) | Quickstart, input format, example datasets |
| [User Guide](https://biormepp-web.readthedocs.io/en/latest/user-guide/) | Results interpretation, downloads, troubleshooting |
| [Use Cases](https://biormepp-web.readthedocs.io/en/latest/use_cases/) | Complete analytical catalog (56 use cases) |
| [Methods](https://biormepp-web.readthedocs.io/en/latest/methods/) | Data sources, mapping strategy, limitations |
| [Configuration](https://biormepp-web.readthedocs.io/en/latest/config/) | Environment variables, Docker, deployment |
| [API Reference](https://biormepp-web.readthedocs.io/en/latest/api/) | Technical documentation |

---

## Citation

When using BioRemPP, please cite:

> BioRemPP Web Service v1.0.3-beta. Available at: https://biorempp.cloud (accessed [DATE]).

> Full citation guidelines: [How to Cite](https://biormepp-web.readthedocs.io/en/latest/about/how-to-cite/)

---

## License

- **Source Code:** [Apache License 2.0](LICENSE)
- **Database Content:** [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)
- **Third-party:** KEGG (academic license), HADEG (open access), toxCSM (open access)

> Details: [License](https://biormepp-web.readthedocs.io/en/latest/about/license/) | [Terms of Use](https://biormepp-web.readthedocs.io/en/latest/about/terms-of-use/)

---

## Limitations

BioRemPP is a research tool for hypothesis generation. Results represent **genetic potential**, not confirmed biological activity. Not intended for clinical, regulatory, or remediation decisions without experimental validation.

> Complete limitations: [Limitations and Scope](https://biormepp-web.readthedocs.io/en/latest/methods/limitations/)

---

## Support

- **Documentation:** [biorempp-web.readthedocs.io](https://biormepp-web.readthedocs.io/en/latest/)
- **Issues:** [GitHub Issues](https://github.com/BioRemPP/biorempp_web/issues)
- **Email:** biorempp@gmail.com

---

**BioRemPP v1.0.3-beta** | [Documentation](https://biormepp-web.readthedocs.io/en/latest/) | [GitHub](https://github.com/BioRemPP/biorempp_web)
