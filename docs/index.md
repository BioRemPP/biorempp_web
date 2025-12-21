# BioRemPP Web Service

*Scientific Web Service* | Version 1.0.0-beta | Last Updated: December 2025

**Type:** Scientific Web Service
**Version:** v1.0.0-beta
**Last Updated:** 2025-12-20

---

## Overview

BioRemPP (Bioremediation Potential Profile) is an open-access scientific web service for exploratory, integrative functional analysis of bioremediation potential based on KEGG Orthology (KO) identifiers. The platform integrates four curated databases (BioRemPP Database, KEGG, HADEG, toxCSM) with seven international regulatory frameworks to enable comprehensive assessment of functional capabilities relevant to environmental remediation contexts. BioRemPP addresses the analytical gap in bioremediation research by providing a compound-centric functional mapping approach that links genetic potential to specific environmental pollutants and toxicological profiles.  The service provides modular analytical outputs including comparative cross-database assessments, functional profiling, hierarchical pathway visualization, and toxicological risk evaluation. It is **not** designed for clinical diagnostics, regulatory compliance assessments, or direct remediation decision-making without independent experimental validation.

---

## Target Audience

BioRemPP is designed for:

- Bioinformatics researchers developing or evaluating analytical pipelines for metagenomics and functional annotation
- Bioinformatics researchers developing bioremediation-oriented analytical workflows
- Computational and environmental biologists conducting functional genomics research
- Scientific reviewers evaluating functional annotation pipelines and integrative database platforms
- Scientific reviewers assessing bioremediation-oriented data analysis workflows

---

## Core Capabilities

### 4.1 Inputs

BioRemPP accepts functional annotation identifiers as input, specifically **KEGG Orthology (KO)** codes organized by sample. Input data represents gene functional annotations derived from metagenomic or genomic datasets, not raw nucleotide or protein sequences. Each sample is conceptually a collection of biological functions (represented as KO identifiers) present in an environmental sample, pure culture, or genome assembly. The platform does not perform sequence assembly, gene calling, or functional annotation; these upstream analyses must be completed prior to BioRemPP submission. Users must perform upstream functional annotation (e.g., via KEGG KAAS, KOfamScan, or similar tools) before submitting data to BioRemPP. Each submission represents a dataset containing one or more samples, where each sample is associated with a list of KO identifiers representing the functional potential of that sample.

### 4.2 Outputs

BioRemPP generates four categories of outputs:

1.  **Integrated Result Tables**: Merged data combining user-uploaded KO identifiers with annotations from BioRemPP Database, HADEG, KEGG, and toxCSM, including enzymatic activities, pathway assignments, compound associations, and regulatory classifications
2. **Interactive Visualizations**: Eight analytical modules containing 56 use cases with Plotly-based charts (e.g., heatmaps, network diagrams, hierarchical clustering, UpSet plots, sunburst diagrams), each addressing specific scientific questions
3. **Toxicological profiles** derived from in silico predictions (toxCSM), including organ-specific toxicity, environmental endpoints, and genotoxicity assessments
4. **Downloadable datasets** in multiple formats (CSV, TSV, JSON) for downstream computational analyses
5.  **Comparative Analytics**: Cross-database consistency assessments, sample similarity analyses, and functional overlap evaluations

Results emphasize functional potential, chemical target coverage, regulatory alignment, and toxicological context. All outputs are session-based and temporary.

### 4.3 Integrated Resources

BioRemPP integrates the following resources:

- **BioRemPP Database (v1.0):** Manually curated database linking KO identifiers to bioremediation-relevant compounds, genes, enzymatic activities, and regulatory agency classifications. This database represents the platform's novel contribution by providing compound-centric functional mappings.

- **Database (Release 116.0+/12-19):** Metabolic pathway annotations and KO definitions providing functional context. ([KEGG](https://www.kegg.jp/kegg/legal.html))

- **HADEG Database (Commit 8f1ff8f):** Gene and pathway annotations focused on hydrocarbon and xenobiotic degradation pathways. ([HADEG Database](https://github.com/jarojasva/HADEG))


- **toxCSM Database:** Computational toxicity predictions for chemical compounds, including 50+ toxicological endpoints covering nuclear receptor binding, stress response pathways, genotoxicity, organ-specific toxicity, and environmental impact.  
([toxCSM Prediction Tool](https://biosig.lab.uq.edu.au/toxcsm/))

- **Regulatory Frameworks:** International and national priority pollutant classifications from IARC (International Agency for Research on Cancer), EPA (United States Environmental Protection Agency), ATSDR (Agency for Toxic Substances and Disease Registry), WFD (Water Framework Directive, EU), PSL (Priority Substances List, Canada), EPC (European Parliament Commission), and CONAMA (National Environmental Council, Brazil).



---

## High-Level Workflow

The BioRemPP analytical workflow consists of five conceptual stages:

1. **Data Submission:** Users upload plain-text files containing KO identifiers organized by sample in a FASTA-like header format (sample headers prefixed with `>`).

2. **Validation and Preprocessing:** Input files are validated for format compliance, KO identifier accuracy, and structural constraints (sample count, identifier count, encoding). Validated data is parsed into internal domain entities. 

3. **Database Integration:** Submitted KO identifiers are mapped through cascading joins across the four integrated databases. This multi-stage merge process links functional annotations to compounds, pathways, toxicological endpoints, and regulatory classifications. Validated KO identifiers are mapped to curated databases through exact identifier matching and cross-referencing across biological layers (KO → Compound → Pathway → Gene → Toxicity)

4. **Modular Analysis Execution:** Users select from 8 analytical modules and 56 use cases, each implementing distinct analytical strategies (clustering, network analysis, toxicological profiling, consortium assembly). Analysis execution is configuration-driven and leverages cached intermediate results where applicable.

5. **Results Visualization and Export:** Results are presented as interactive visualizations (19 distinct chart types) with accompanying plot ready data tables. All outputs are downloadable in standard formats (CSV, Excel, JSON) and visualizations can be exported as static images.

---

## Data Policy & Privacy

BioRemPP operates with a strict session-based processing model designed to minimize privacy risks:

- **No user accounts required:** The service operates without authentication, user registration, or persistent user profiles.

- **No persistent storage of uploaded data:** All uploaded files are processed exclusively in-memory during the active session. Data is automatically discarded when the browser session ends or after 6 hours of inactivity, whichever occurs first.

- **Session-based processing:** Each analysis session is isolated. No cross-session data sharing or aggregation occurs.

- **Logging policy:** The service logs only technical metadata required for service operation and abuse prevention:
  - IP addresses (rate limiting and abuse detection)
  - User-agent strings (browser compatibility monitoring)
  - Error stack traces (debugging and stability improvement)
  - **Uploaded data content is never logged.**

- **No third-party data sharing:** Uploaded data and analysis results are never transmitted to external services or third parties.

- **Security measures:** Production deployments enforce HTTPS/TLS encryption. Uploaded files are subject to format validation, size limits (5 MB maximum), and content sanitization before processing.

---

## Reproducibility & Availability

BioRemPP supports scientific reproducibility through multiple mechanisms:

- **Open-access web service:** The platform is freely accessible without registration or institutional affiliation requirements. Access URL: [https://biorempp.org](https://biorempp.org) (placeholder).

- **Public source code:** Complete source code is available under Apache License 2.0 at [https://github.com/BioRemPP/biorempp_web](https://github.com/BioRemPP/biorempp_web).

- **Database versioning:** All integrated databases are version-controlled and distributed with the source code. Specific versions are documented in analysis outputs to ensure reproducibility.

- **Local execution capability:** BioRemPP can be deployed locally via Docker containers, enabling offline analysis, institutional deployments, and custom database integration. Containerized deployment ensures environment consistency across platforms.

- **Configuration-driven analyses:** All analytical workflows are defined in YAML configuration files, enabling transparent inspection of analysis parameters and facilitating customization.

---

## Limitations & Scope

BioRemPP is a research tool subject to the following limitations:

- **Research-only usage:** BioRemPP is designed exclusively for exploratory scientific research and hypothesis generation. It is not validated for clinical diagnostics, regulatory submissions, or direct remediation decision-making. All outputs require independent experimental validation before application in operational contexts.

- **Database coverage dependence:** Results are constrained by the completeness and accuracy of integrated databases. The absence of an annotation does not imply the absence of biological function; it may reflect incomplete database coverage, evolving nomenclature, or knowledge gaps in bioremediation research.

- **Functional resolution limits:** KEGG Orthology identifiers represent functional groups and may not capture fine-grained enzymatic specificity, substrate preference, or isoform-level variation. Functional potential inferred from KO presence does not guarantee enzymatic activity under specific environmental conditions.

- **In silico toxicity predictions:** Toxicological assessments derived from toxCSM are computational predictions based on machine learning models trained on experimental data. These predictions provide probabilistic estimates and require experimental validation before use in risk assessment or regulatory contexts.

- **Quantitative limitations:** BioRemPP operates on presence/absence data (binary functional potential). Quantitative expression levels, transcript abundances, protein concentrations, and metabolic flux rates are not incorporated.
---

## Citation

### Web Service

If you use BioRemPP in your research, please cite:

```
BioRemPP Development Team (2025). BioRemPP: Bioremediation Potential Profile Web Service (v1.0.0-beta). Available at: https://biorempp.org
```

**BibTeX format:**

```bibtex
@misc{biorempp2025,
  title={BioRemPP: Bioremediation Potential Profile Web Service},
  author={BioRemPP Development Team},
  year={2025},
  url={https://biorempp.org},
  note={Version 1.0.0-beta}
}
```

### Manuscript Reference

placeholder
---

## License Summary

### Database Content

**License:** Creative Commons Attribution 4.0 International (CC BY 4.0)

The BioRemPP Database (compound-gene-pathway mappings, regulatory classifications, and annotations) is licensed under CC BY 4.0. Users are free to share, adapt, and build upon the database for any purpose, including commercial applications, provided appropriate attribution is given as specified in the [Citation](#citation) section.

**Full license:** [https://creativecommons.org/licenses/by/4.0/](https://creativecommons.org/licenses/by/4.0/)

### Web Service Source Code

**License:** Apache License 2.0

The BioRemPP web service source code (Python application, Docker configuration, tests, documentation) is licensed under Apache 2.0. This license permits commercial use, modification, distribution, and patent use, subject to the terms specified in the LICENSE file distributed with the source code.

Users must retain copyright notices and provide attribution.

**Full license:** [https://www.apache.org/licenses/LICENSE-2.0](https://www.apache.org/licenses/LICENSE-2.0)

### Third-Party Databases

BioRemPP integrates data from external sources, each governed by independent licenses:

- **KEGG:** Academic use is free; commercial use requires a separate license from Kanehisa Laboratories ([KEGG License Terms](https://www.kegg.jp/kegg/legal.html)).
- **HADEG:** Open access under permissive license ([GitHub Repository](https://github.com/jarojasva/HADEG)).
- **toxCSM:** Open access for academic research ([toxCSM License](https://biosig.lab.uq.edu.au/toxcsm/)).

Users are responsible for ensuring compliance with all applicable third-party licenses when using BioRemPP outputs derived from these resources.

---

## Contact & Support

### Institutional Contact

**Email:** biorempp@gmail.com

**Response Expectations:** Inquiries are addressed on a best-effort basis. We aim to respond within 5 business days. For urgent technical issues affecting service availability, please indicate "URGENT" in the subject line.

### Bug Reports and Feature Requests

**Issue Tracking:** [https://github.com/BioRemPP/biorempp_web/issues](https://github.com/BioRemPP/biorempp_web/issues)

When reporting issues, please include:

1. BioRemPP version (available in application footer or `/version` endpoint)
2. Browser type and version
3. Operating system
4. Steps to reproduce the issue
5. Expected behavior vs. observed behavior
6. Example input file (if applicable and non-confidential)
7. Screenshots or error messages

Feature requests should include scientific justification, proposed functionality, expected input/output formats, and potential impact on existing analytical workflows.

### Support Limitations

BioRemPP is provided without warranty of any kind. User support is offered on a best-effort basis by the development team.  
Institutional users requiring service-level agreements (SLAs) or prioritized support may contact the project team through the official institutional email **biorempp@gmail.com** , clearly describing the intended service scope.

Requests of this nature will be reviewed and responded to within **five (5) business days**.


---

## Acknowledgments

BioRemPP development is supported by:

- **Institutional Affiliation:** Federal University of Rio Grande do Norte (UFRN) — Graduate Program in Bioinformatics (PPg-Bioinfo) and Instituto Metrópole Digital (IMD)
- **Research Group / Laboratory:** Laboratory of Molecular Biology and Genomics (LBMG–UFRN) and associated collaborative research groups within UFRN
- **Funding and Institutional Support:** Institutional and academic support from UFRN and research and innovation programs in Brazil, CNPq and CAPES.
We acknowledge the developers and curators of **KEGG**, **HADEG**, and **toxCSM** for making their resources available to the scientific community. We also thank the open-source software communities behind **Python**, **Dash**, **Plotly**, **Pandas**, and related libraries that provide the technical foundation for BioRemPP.


---

**Last Documentation Update:** 2025-12-20

**Application Version:** 1.0.0-beta
