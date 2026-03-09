# Methods & Methodology

This section documents the **scientific and technical methodology** underlying BioRemPP Web Service. It provides the foundation for understanding how functional annotations are processed, integrated, and interpreted for bioremediation potential inference.

---

## Analytical Use Cases

BioRemPP organizes analytical capabilities into **56 use cases across 8 thematic modules**. Each use case addresses a specific scientific question and produces reproducible, interpretable outputs.

For the complete catalog of analytical use cases, including scientific questions, visualization types, and interpretation guidelines, see:

**[Use Cases Catalog](../use_cases/index.md)** — Complete index of all analytical modules and use cases

| Module | Focus Area | Use Cases |
|--------|------------|-----------|
| Module 1 | Comparative Assessment (Databases, Samples, Regulatory) | UC 1.1 – 1.6 |
| Module 2 | Exploratory Analysis (Functional Potential Ranking) | UC 2.1 – 2.5 |
| Module 3 | System Structure (Clustering, Similarity, Co-occurrence) | UC 3.1 – 3.7 |
| Module 4 | Functional and Genetic Profiling | UC 4.1 – 4.13 |
| Module 5 | Modeling Interactions (Samples, Genes, Compounds) | UC 5.1 – 5.6 |
| Module 6 | Hierarchical and Flow-based Functional Analysis | UC 6.1 – 6.5 |
| Module 7 | Enzyme Activity & Functional Patterns | UC 7.1 – 7.7 |
| Module 8 | Assembly of Functional Consortia | UC 8.1 – 8.7 |

---

## Methodological Documentation

### Core Methodology

| Page | Description |
|------|-------------|
| [Methods Overview](methods-overview.md) | High-level framework for KO-based compound-centric functional inference |
| [Data Sources](data-sources.md) | Database inventory, provenance, coverage, and curation models |
| [Mapping Strategy](mapping-strategy.md) | Technical pipeline for identifier normalization and database integration |

### Regulatory & Interpretive Context

| Page | Description |
|------|-------------|
| [Regulatory Frameworks](regulatory-frameworks.md) | Integration of 7 international environmental agency classifications |
| [Limitations and Scope](limitations.md) | Complete documentation of constraints, boundaries, and usage restrictions |

### Configuration & Reproducibility

| Page | Description |
|------|-------------|
| [Use Case YAML Configuration](use-case-yaml.md) | Declarative YAML methodology for analytical use case definition |

---

## Integrated Databases

BioRemPP integrates four curated databases for multi-source functional context:

| Database | Records | Primary Focus |
|----------|---------|---------------|
| **BioRemPP Database** | 10,869 | Compound-enzyme-agency mapping for bioremediation |
| **KEGG Degradation** | 855 | Xenobiotic metabolism and degradation pathways |
| **HADEG** | 867 | Aerobic hydrocarbon degradation enzymes |
| **ToxCSM** | 370 | Computational toxicity predictions (31 endpoints) |

For detailed database documentation, see [Data Sources](data-sources.md).

---

## Regulatory Integration

BioRemPP contextualizes compounds using classifications from **7 international regulatory frameworks**:

| Agency | Jurisdiction | Focus |
|--------|--------------|-------|
| **IARC** | International (WHO) | Carcinogenicity classification |
| **EPA** | United States | Priority pollutants, Superfund sites |
| **ATSDR** | United States | Substance priority based on toxicity and prevalence |
| **WFD** | European Union | Aquatic environment protection |
| **PSL/CEPA** | Canada | Priority substances for environmental protection |
| **EPC** | European Union | REACH and priority chemicals |
| **CONAMA** | Brazil | Brazilian environmental standards |

For detailed framework documentation, see [Regulatory Frameworks](regulatory-frameworks.md).

---

## Interpretation Guidelines

### What Results Represent

| Aspect | Represents | Does NOT Represent |
|--------|------------|-------------------|
| Gene presence | Detection of KO identifiers | Confirmed gene expression |
| Functional capacity | Theoretical bioremediation ability | Actual enzymatic activity |
| Pathway coverage | Proportion of enzymes present | Metabolic flux or throughput |
| Toxicity predictions | Computational estimates | Experimental measurements |
| Regulatory context | Agency classifications | Compliance certification |

### Critical Boundaries

- **Genetic potential ≠ biological activity** — Results indicate capacity, not confirmed function
- **Computational predictions require validation** — All inferences need experimental confirmation
- **Database coverage is intentional** — Absence of results reflects curation scope, not absence of function

For complete interpretation guidance, see [Limitations and Scope](limitations.md).

---

## Related Documentation

### User Guides

- [Quickstart Guide](../getting-started/quickstart.md) — Getting started with BioRemPP
- [Input Format](../getting-started/input-format.md) — KO annotation file specification
- [Interpretation Guidelines](../user-guide/interpretation.md) — How to interpret results responsibly
- [Downloads](../user-guide/downloads.md) — Export and archive results

### Configuration

- [Configuration Overview](../config/index.md) — Runtime and deployment configuration
- [YAML Configuration](../config/yaml-configuration.md) — Declarative use case configuration

### Validation

- [Internal Validation](../validation/internal-validation.md) — QC rules and consistency checks
- [Unit Test Suite](../validation/test-suite.md) — Software validation documentation

### Legal

- [Terms of Use](../about/terms-of-use.md) — Usage restrictions and disclaimers
- [License](../about/license.md) — Software and database licensing
- [How to Cite](../about/how-to-cite.md) — Citation requirements

