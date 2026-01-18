# Methodological Framework

This page describes the **methodological framework** of the BioRemPP Web Service: a KO-based, compound-centric approach for **exploratory functional inference of bioremediation potential** from genomic and metagenomic annotations.

---

## Purpose and Scope

BioRemPP supports **systematic interpretation of functional annotations** in bioremediation-oriented studies by integrating standardized identifiers with curated knowledge resources.

BioRemPP is a **research-only, exploratory** framework intended for:

* hypothesis generation and candidate prioritization;
* comparative functional profiling across samples, datasets, and knowledge sources;
* transparent, reproducible mapping between functional identifiers and bioremediation-relevant contexts.

BioRemPP is **not intended for** regulatory compliance determinations, clinical or risk-based decision-making, prediction of degradation kinetics, or operational field recommendations without independent experimental validation.

---

## Scope and Limitations

BioRemPP provides **exploratory functional inference** of bioremediation potential based on genetic annotations. Results represent **genetic capacity**, not confirmed biological activity, gene expression, or degradation rates.

**Critical boundaries:**

- Genetic potential ≠ biological activity
- No kinetic modeling or expression weighting
- Computational predictions require experimental validation
- Not suitable for regulatory compliance or clinical decisions

For complete documentation of scope boundaries, methodological constraints, interpretation guidelines, and usage restrictions, see **[Limitations and Scope Boundaries](limitations.md)**.

---

## Conceptual Analytical Model

### KO as a standardized functional language

BioRemPP uses **KEGG Orthology (KO) identifiers** as a phylogeny-independent functional representation of samples. KO identifiers provide a stable, interoperable unit of analysis across genomes, metagenomes, MAGs, isolates, and transcriptome-derived annotations.

### Compound-centric functional reasoning

BioRemPP adopts a compound-centric perspective that links functional identifiers to regulatory context:

**KO identifiers → enzymatic function → mapped compounds → pathway context → toxicity/regulatory context**

This abstraction enables questions such as:

* which pollutant compounds are *functionally addressable* given observed enzyme orthologs;
* whether inferred functional coverage aligns with known compound classes and degradation contexts;
* how toxicological and regulatory metadata can support **prioritization** (not certification).

---

## High-level Methodological Stages

BioRemPP’s framework can be understood as three methodological stages.

### Stage 1 — Input abstraction

User inputs are treated as **sets of KO identifiers per sample**, representing functional annotations generated upstream. BioRemPP does not perform assembly, gene calling, or functional annotation.

### Stage 2 — Deterministic knowledge integration

KO sets are mapped to curated reference knowledge using **exact identifier matching** and deterministic joins. The mapping is designed to preserve sample-level traceability across all derived tables and summaries.

### Stage 3 — Independent analytical units

Analyses are organized into **independent use cases** grouped into thematic modules. Each use case addresses a distinct scientific question (e.g., coverage, similarity, enrichment, completeness, relationships), and can be interpreted and reported independently.

---

## Representative Analytical Concepts

BioRemPP applies recurring analytical concepts across modules. These concepts are **illustrative**, not an exhaustive inventory.

* **KO Richness:** characterization of samples by the diversity and composition of detected KO groups.
* **Compound coverage:** characterization of samples by the breadth of mapped compounds associated with detected enzymatic functions.
* **Similarity and complementarity:** assessment of overlap versus complementarity across samples based on shared KO and compound profiles.
* **Pathway-oriented completeness (contextual):** approximation of coverage of multi-step functional routes based on presence/absence of required functional units.
* **System-level organization:** identification of recurring functional patterns (e.g., guild-like clusters) emerging from shared functional/chemical profiles.

---

## Interpretation Boundaries

### Genetic potential vs biological activity

BioRemPP outputs represent **functional potential** inferred from annotations. Presence of a KO identifier does not demonstrate:

* transcription, translation, or regulation under the studied conditions;
* enzyme activity, substrate availability, or environmental feasibility;
* net conversion of pollutants or measurable remediation outcomes.

Interpret results as **candidate evidence** to guide downstream validation and experimental design.

### Toxicology and regulatory metadata are contextual

Toxicological predictions and regulatory classifications are provided for **informational context and prioritization**. They do not constitute:

* legal compliance judgments;
* formal risk assessments;
* exposure limit or hazard determinations;
* regulatory approval or certification.

---

## Reproducibility Principles

BioRemPP is designed to support reproducible scientific reporting through:

* **Versioned knowledge resources:** curated data snapshots aligned with service releases.
* **Deterministic mapping:** exact identifier-based integration with no probabilistic assignments.
* **Transparent, declarative analysis definitions:** analyses are parameterized and version-controlled to enable independent inspection and replication.


---

## Related Pages

This page intentionally remains high-level and non-operational. For detailed methodological components, see:

- [Data Sources](data-sources.md) — Scope, provenance, and coverage of integrated databases
- [Mapping Strategy](mapping-strategy.md) — Identifier normalization and KO-to-context mapping rules
- [Regulatory Frameworks](regulatory-frameworks.md) — Definitions and agency-specific compound categories
- [Limitations and Scope Boundaries](limitations.md) — Complete documentation of constraints and interpretation guidelines
- [Use Case YAML Configuration](use-case-yaml.md) — Declarative configuration methodology
- [Internal Validation](../validation/internal-validation.md) — QC rules, consistency checks, and validation scope
- [Interpretation Guidelines](../user-guide/interpretation.md) — How to interpret BioRemPP results responsibly
- [Quickstart Guide](../getting-started/quickstart.md) — Getting started with BioRemPP
