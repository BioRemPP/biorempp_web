# Internal Validation Suite

BioRemPP includes an **Internal Validation Suite** that is executed to document whether the platform’s **data integration and analytical behavior** remain structurally consistent, biologically plausible at the level of *functional potential inference*, and reproducible under a fixed data snapshot.

This page summarizes the **scientific intent** of the validation suite and the **types of artifacts** it produces.

---

## 1. Purpose of the internal validation suite

BioRemPP integrates heterogeneous, curated resources (BioRemPP database, KEGG degradation subset, HADEG, toxCSM) to support **compound-centric interpretation** of user-provided KO profiles. Multi-source integration introduces two reviewer-relevant risks:

* **Integration drift:** changes in underlying data (content, schema, controlled vocabularies) can alter analytical outputs.
* **Mapping incoherence:** inconsistent linkage patterns (e.g., KO→compound→toxicity) can generate outputs that are difficult to interpret scientifically.

The Internal Validation Suite is designed to provide **auditable evidence** that:

* the integrated datasets remain **traceable and structurally stable**;
* cross-database relationships exhibit **expected concordance/complementarity** given their scopes;
* key mapping and output properties satisfy **logical invariants** required for defensible interpretation;
* repeated execution over an identical snapshot yields **consistent results**.

**Why internal validation (rather than competitive benchmarking)?**
BioRemPP’s compound-centric integration of functional annotations with toxicity and regulatory context does not have a direct, like-for-like comparator. Generic KO/pathway tools (e.g., KO assignment or pathway viewers) address upstream annotation or generic metabolism visualization and do not evaluate the same integrated outputs. Consequently, BioRemPP emphasizes **internal consistency, plausibility, and reproducibility** as the appropriate validation targets.

---

## 2. Scope of validation

The suite evaluates three domains:

1. **Provenance and data stability**

   * evidence that the database snapshot used by the service is identifiable and traceable.

2. **Integration and mapping coherence**

   * evidence that cross-database overlaps and linkage cardinalities are consistent with expected database scopes and biological realities (e.g., enzyme promiscuity; redundancy of enzymatic routes).

3. **Analytical output invariants and regression stability**

   * evidence that representative outputs remain logically well-formed and stable across repeated runs given identical inputs and the same database snapshot.

### Explicit non-claims

The Internal Validation Suite does **not** claim:

* experimental confirmation of degradation or biological activity;
* predictive accuracy (sensitivity/specificity) against a gold-standard dataset;
* regulatory compliance, endorsement, or risk assessment.

BioRemPP outputs should be interpreted as **hypothesis-generating functional potential** that requires experimental validation for real-world bioremediation conclusions.

---

## 3. Overview of the executed suite

The validation suite is implemented as a set of **seven scripted checks** that generate:

* a **human-readable report** for each validation component; and
* machine-readable summaries suitable for tracking changes across versions.

When executed, the suite produces an execution summary (pass/fail per script) with a timestamp and suite version identifier.

**Validation components (7):**

| Component                    | Primary domain         | What it provides (evidence)                                  |
| ---------------------------- | ---------------------- | ------------------------------------------------------------ |
| Provenance snapshot          | Provenance & stability | Snapshot fingerprinting of integrated datasets               |
| Schema integrity             | Data integrity         | Required-field presence and structural consistency           |
| Cross-database overlap       | Integration coherence  | Expected concordance/complementarity across KO universes     |
| Mapping consistency          | Mapping coherence      | KO–compound and compound–toxicity linkage patterns           |
| Example roundtrip regression | Reproducibility        | Stable outputs for standardized example inputs               |
| Use case invariants          | Output correctness     | Logical constraints preserved in representative outputs      |
| Controlled vocabulary audit  | Semantic stability     | Drift monitoring for controlled terms used in interpretation |

---

## 4. Description of validation components

### 4.1 Provenance snapshot

**Scientific purpose.** Enable readers to identify the *exact data state* underlying a set of results.

**Evidence produced.** The suite records a fingerprint of each integrated database file (e.g., checksums) plus basic snapshot descriptors (e.g., file metadata and schema signatures).

**What it detects.** Any unintended modification, corruption, or untracked update of database content is detectable as a change in the snapshot fingerprint.

**Why it matters.** This provides a defensible mechanism for linking reported analyses to a specific database snapshot, enabling temporal traceability.

---

### 4.2 Schema integrity

**Scientific purpose.** Integration and downstream analyses assume the presence of specific identifier fields and controlled columns. Schema drift can silently alter results.

**Evidence produced.** The suite verifies the availability of required columns and performs structural sanity checks (e.g., missingness patterns; duplicate pressure in fields expected to be stable).

**What it detects.** Missing/renamed fields, abnormal null density, or unexpected structural changes that can invalidate joins or distort interpretation.

**Why it matters.** It supports the claim that observed non-matches or coverage differences are consistent with database scope/coverage rather than malformed data.

---

### 4.3 Cross-database overlap

**Scientific purpose.** BioRemPP combines databases with different curation scopes. Interpreting partial mappings requires understanding expected overlap.

**Evidence produced.** The suite computes overlap summaries for KO identifier sets across BioRemPP, KEGG subset, and HADEG (and links to compound-level coverage for toxCSM where applicable).

**What it detects.** Unexpected disjointness or unexpectedly high/low overlap suggest scope drift, curation errors, or integration mistakes.

**Why it matters.** Establishes baseline expectations for why an input KO may map in one source but not in another.

---

### 4.4 Mapping consistency

**Scientific purpose.** Compound-centric inference relies on coherent relationships across layers (KO→compound and compound→toxicity). Many-to-many mappings are biologically plausible and must be preserved consistently.

**Evidence produced.** The suite audits linkage patterns such as:

* distribution of compounds per KO (capturing expected promiscuity and redundancy);
* coverage of compounds that have toxCSM predictions;
* missingness patterns across toxicity endpoints.

**What it detects.** Broken linkages (e.g., compounds expected to connect to toxicity predictions but failing systematically) or implausible cardinality distributions that indicate integration issues.

**Why it matters.** Supports scientifically defensible interpretation of why some compounds carry toxicity context while others do not, and why multiple compounds may be associated with a single KO.

---

### 4.5 Example roundtrip regression

**Scientific purpose.** Demonstrate that identical inputs evaluated against the same snapshot yield consistent merged outputs.

**Evidence produced.** The suite reprocesses standardized example KO datasets and records stable fingerprints of the resulting merged tables.

**What it detects.** Any unintended change in mapping behavior across releases or database snapshots that would alter merged outputs for unchanged example inputs.

**Why it matters.** Provides an auditable regression baseline for reproducibility over time.

---

### 4.6 Use case invariants

**Scientific purpose.** Independent analytical use cases should preserve basic logical constraints required for interpretation (e.g., non-negative counts; required identifiers present where defined).

**Evidence produced.** The suite evaluates invariant checks on representative merged outputs and/or derived summary tables.

**What it detects.** Violations that would indicate incoherent analytical outputs (e.g., impossible ranges, invalid identifiers in output fields, empty mandatory descriptors).

**Why it matters.** Adds a final scientific-sanity layer that outputs remain interpretable as structured analytical results.

---

### 4.7 Controlled vocabulary audit

**Scientific purpose.** BioRemPP relies on controlled terms (e.g., compound classes; regulatory framework labels) that are used downstream for filtering and interpretation. Vocabulary drift can invalidate comparisons.

**Evidence produced.** The suite enumerates controlled vocabulary values and their frequencies, producing version-comparable summaries.

**What it detects.** Untracked additions/removals/renames that would change interpretation layers or break reproducibility across releases.

**Why it matters.** Preserves semantic stability and supports longitudinal comparisons.

---

## 5. Determinism and reproducibility

Within a fixed database snapshot, BioRemPP’s mapping and downstream analyses are designed to be **deterministic**:

* identical KO inputs applied to the same snapshot yield the same merged results;
* regression fingerprints on standardized example datasets provide an auditable stability check;
* provenance fingerprints document the exact snapshot used to generate results.

Because BioRemPP analyses are defined using **declarative YAML configuration** (parameters, transformations, visualization logic), the analytical state can be traced to explicit configuration versions rather than implicit code defaults.

---

## 6. Limitations

The Internal Validation Suite provides evidence of **internal coherence and reproducibility**, but it does not establish external validity:

* It does not confirm real-world biodegradation outcomes.
* It does not quantify predictive accuracy due to the lack of a field-wide gold-standard dataset for compound-centric bioremediation potential.
* It does not replace experimental validation.
* It does not imply regulatory approval or compliance.

Accordingly, BioRemPP results should be used for **comparative profiling and hypothesis generation** with subsequent experimental validation where required.
