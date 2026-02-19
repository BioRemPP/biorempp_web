# Internal Validation Suite

BioRemPP includes an **Internal Validation Suite** that is executed to document whether the platform's **data integration and analytical behavior** remain structurally consistent, biologically plausible at the level of *functional potential inference*, and reproducible under a fixed data snapshot.

This page summarizes the **scientific intent** of the validation suite and the **types of artifacts** it produces.

---

## 1. Purpose of the Internal Validation Suite

BioRemPP integrates heterogeneous, curated resources (BioRemPP database, KEGG degradation subset, HADEG, toxCSM) to support **compound-centric interpretation** of user-provided KO profiles. Multi-source integration introduces two reviewer-relevant risks:

- **Integration drift:** changes in underlying data (content, schema, controlled vocabularies) can alter analytical outputs.
- **Mapping incoherence:** inconsistent linkage patterns (e.g., KO->compound->toxicity) can generate outputs that are difficult to interpret scientifically.

The Internal Validation Suite is designed to provide **auditable evidence** that:

- the integrated datasets remain **traceable and structurally stable**;
- cross-database relationships exhibit **expected concordance/complementarity** given their scopes;
- key mapping and output properties satisfy **logical invariants** required for defensible interpretation;
- repeated execution over an identical snapshot yields **consistent results**.

**Why internal validation (rather than competitive benchmarking)?**  
BioRemPP's compound-centric integration of functional annotations with toxicity and regulatory context does not have a direct, like-for-like comparator. Generic KO/pathway tools (e.g., KO assignment or pathway viewers) address upstream annotation or generic metabolism visualization and do not evaluate the same integrated outputs. Consequently, BioRemPP emphasizes **internal consistency, plausibility, and reproducibility** as the appropriate validation targets.

---

## 2. Scope of Validation

The suite evaluates three domains:

1. **Provenance and data stability**

   - evidence that the database snapshot used by the service is identifiable and traceable.

2. **Integration and mapping coherence**

   - evidence that cross-database overlaps and linkage cardinalities are consistent with expected database scopes and biological realities (e.g., enzyme promiscuity; redundancy of enzymatic routes).

3. **Analytical output invariants and regression stability**

   - evidence that representative outputs remain logically well-formed and stable across repeated runs given identical inputs and the same database snapshot.

### Explicit Non-Claims

The Internal Validation Suite does **not** claim:

- experimental confirmation of degradation or biological activity;
- predictive accuracy (sensitivity/specificity) against a gold-standard dataset;
- regulatory compliance, endorsement, or risk assessment.

BioRemPP outputs should be interpreted as **hypothesis-generating functional potential** that requires experimental validation for real-world bioremediation conclusions.

---

## 3. Overview of the Executed Suite

The validation suite is implemented through a **GX-driven execution layer** plus **hybrid analytical tasks**, generating:

- a **human-readable report** for each validation component; and
- machine-readable summaries suitable for tracking changes across versions.

When executed, the suite produces a consolidated run summary with checkpoint status, hybrid task status, timestamps, and output contracts.

**Validation components (7):**

| Component | Primary domain | What it provides (evidence) |
| --- | --- | --- |
| Provenance snapshot | Provenance and stability | Snapshot fingerprinting of integrated datasets |
| Schema integrity | Data integrity | Required-field presence and structural consistency |
| Cross-database overlap | Integration coherence | Expected concordance/complementarity across KO universes |
| Mapping consistency | Mapping coherence | KO-compound and compound-toxicity linkage patterns |
| Example roundtrip regression | Reproducibility | Stable outputs for standardized example inputs |
| Use case invariants | Output correctness | Logical constraints preserved in representative outputs |
| Controlled vocabulary audit | Semantic stability | Drift monitoring for controlled terms used in interpretation |

---

## 4. Execution Model and Artifacts

### 4.1 Validation Engine

The official stack combines:

- **Great Expectations** suites and checkpoints for declarative constraints
- **Hybrid Python tasks** for provenance, overlap, and roundtrip analyses

### 4.2 Main Commands

```bash
python internal_validation/scripts/run_all_gx.py --checkpoint biorempp_full_validation
python internal_validation/scripts/run_all_gx.py --schema-only
python internal_validation/scripts/run_all_gx.py --ci
python internal_validation/scripts/ci_validation.py
```

### 4.3 Output Contracts

- Versioned outputs: `internal_validation/outputs/YYYY-MM-DD/`
- Latest outputs: `internal_validation/outputs_latest/`
- Consolidated summary: `internal_validation/outputs_latest/index.json`
- Human summary: `internal_validation/outputs_latest/index.md`
- Data Docs: `internal_validation/gx_context/uncommitted/data_docs/local_site/`

### 4.4 CI Exit Semantics

- `0`: all critical checks passed
- `1`: one or more validations failed
- `2`: execution/runtime error

---

## 5. Description of Validation Components

### 5.1 Provenance Snapshot

**Scientific purpose.** Enable readers to identify the exact data state underlying a set of results.

**Evidence produced.** File fingerprints (SHA256), metadata, schema descriptors, and missingness profile for each integrated database.

**What it detects.** Any unintended modification, corruption, or untracked update of database content.

**Why it matters.** Links reported analyses to a specific database snapshot with audit-ready traceability.

---

### 5.2 Schema Integrity

**Scientific purpose.** Ensure required fields and structural assumptions remain valid for deterministic joins and downstream analyses.

**Evidence produced.** Required-column checks, KO format checks, null-threshold checks, and suite-level expectation statistics.

**What it detects.** Missing/renamed fields, abnormal null density, and structural drift that can invalidate interpretation.

**Why it matters.** Distinguishes genuine coverage limits from malformed data artifacts.

---

### 5.3 Cross-Database Overlap

**Scientific purpose.** Characterize expected overlap/divergence among resources with different curation scopes.

**Evidence produced.** Pairwise intersections, Jaccard indices, shared cores, and exclusive KO counts.

**What it detects.** Unexpected disjointness or overlap shifts suggesting curation or integration issues.

**Why it matters.** Supports interpretation when input KOs map in one resource but not in others.

---

### 5.4 Mapping Consistency

**Scientific purpose.** Verify coherent KO->compound and compound->toxicity relationships.

**Evidence produced.** Cardinality distributions, linkage coverage, and mapping-level expectations.

**What it detects.** Systematic linkage breaks or implausible mapping patterns.

**Why it matters.** Preserves scientifically defensible interpretation of one-to-many associations.

---

### 5.5 Example Roundtrip Regression

**Scientific purpose.** Demonstrate deterministic behavior for fixed example datasets.

**Evidence produced.** Input checksums, merged output checksums, and content hashes by dataset.

**What it detects.** Unintended changes in mapping behavior across runs with unchanged inputs and snapshot.

**Why it matters.** Provides an auditable regression baseline.

---

### 5.6 Use Case Invariants

**Scientific purpose.** Ensure representative merged outputs remain logically well-formed.

**Evidence produced.** Invariant pass/fail checks per merged artifact.

**What it detects.** Impossible ranges, missing mandatory values, invalid identifiers.

**Why it matters.** Adds a final sanity layer for downstream interpretation.

---

### 5.7 Controlled Vocabulary Audit

**Scientific purpose.** Ensure semantic stability of controlled fields used in filtering and interpretation.

**Evidence produced.** Frequency distributions for controlled vocabularies and unique value counts.

**What it detects.** Untracked additions/removals/renames with potential interpretability impact.

**Why it matters.** Supports stable longitudinal comparisons.

---

## 6. Determinism and Reproducibility

Within a fixed database snapshot, BioRemPP mapping and downstream analyses are deterministic:

- identical KO inputs applied to the same snapshot yield the same merged results;
- roundtrip fingerprints on standardized example datasets provide a reproducibility baseline;
- provenance fingerprints document the exact snapshot used to generate results.

Because analyses and validation parameters are defined via declarative YAML configuration, analytical state remains explicit and auditable.

---

## 7. Limitations

The Internal Validation Suite provides evidence of **internal coherence and reproducibility**, but it does not establish external validity:

- It does not confirm real-world biodegradation outcomes.
- It does not quantify predictive accuracy due to the lack of a field-wide gold-standard dataset for compound-centric bioremediation potential.
- It does not constitute experimental validation.
- It does not imply regulatory approval or compliance.

Accordingly, BioRemPP results should be used for **comparative profiling and hypothesis generation** with subsequent experimental validation where required.
