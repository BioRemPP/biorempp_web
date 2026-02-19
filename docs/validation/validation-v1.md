# Internal Validation Results (v1.0)

## Executive Summary

This document reports the outcome of the **BioRemPP Internal Validation Suite** execution and provides evidence that the released data resources and analytical transformations behave **consistently**, remain **traceable to a defined data snapshot**, and support **reproducible** analyses.

- **Validation Date:** 2026-02-18
- **Run ID:** `20260218T220038Z`
- **Checkpoint:** `biorempp_full_validation`
- **Output Version:** `v2.0.0-gx-first`
- **Overall Status:** **All validation components passed successfully**.

> Scope note: these checks evaluate **internal consistency and analytical coherence** of database integration and derived outputs. They do **not** establish biological activity, in situ degradation performance, predictive accuracy, or regulatory compliance.

---

## 1. Provenance Snapshot

### Validation Results

The provenance snapshot successfully characterized all four integrated databases:

| Database | Records | Columns | Data Completeness |
| -------- | ------- | ------- | ----------------- |
| BioRemPP | 10,869  | 8       | 100% (0 nulls)    |
| KEGG     | 855     | 3       | 100% (0 nulls)    |
| HADEG    | 867     | 4       | 100% (0 nulls)    |
| toxCSM   | 370     | 66      | 100% (0 nulls)    |

| Database | SHA256 Checksum | Size (bytes) |
|----------|------------------|--------------|
| **BioRemPP** | `216cf113400161d6eee8d4eefb13bab23f60f9286874fa41ae8d00f3fc4637c0` | 1,125,913 |
| **KEGG** | `f3df93d3bc5492043d2f6a9ea087b6687757e4757057ba1ab19c1a0d53fcd619` | 21,612 |
| **HADEG** | `d546c01be1cf05866b18aa25fd1edb23e4d90f9ab4e65fb5e37911c1e57ce938` | 35,380 |
| **toxCSM** | `0d4616930b438964d9e007b20c9ffb9c414879b775a3b89d660bfc6278fe5f38` | 224,997 |

**Key Findings:**

- All databases exhibit complete data coverage with zero null values across all fields.
- Cryptographic checksums were computed for each database, enabling detection of any future modifications.
- Schema structures were documented, including column names and data types.

### Interpretation

- The zero-null snapshot supports downstream joins without imputation.
- Archived checksums provide a verifiable reference for subsequent releases and for reproducing published analyses.

---

## 2. Schema Integrity

### Validation Results

Schema integrity validation passed for all four databases:

| Schema Suite | Expectations Evaluated | Passed | Failed | Status |
| -------- | ------------------ | ------ | ------ | ------ |
| `biorempp_db_schema_integrity_suite` | 23 | 23 | 0 | PASS |
| `kegg_degradation_db_schema_integrity_suite` | 10 | 10 | 0 | PASS |
| `hadeg_db_schema_integrity_suite` | 12 | 12 | 0 | PASS |
| `toxcsm_db_schema_integrity_suite` | 10 | 10 | 0 | PASS |

**Schema Totals:**

- Evaluated expectations: **55**
- Successful expectations: **55**
- Unsuccessful expectations: **0**

### Interpretation

- Required structural constraints were satisfied for all validated assets.
- No schema-level regression was detected in this execution.

---

## 3. Cross-Database Overlap

### Validation Results

**Database Coverage:**

| Database | Unique KO Identifiers |
| -------- | --------------------- |
| BioRemPP | 1,541                 |
| KEGG     | 517                   |
| HADEG    | 337                   |

**Pairwise Overlap Analysis:**

| Database Pair    | Shared KOs | Jaccard Index | Coverage A | Coverage B |
| ---------------- | ---------- | ------------- | ---------- | ---------- |
| BioRemPP & KEGG  | 269        | 0.1504        | 17.46%     | 52.03%     |
| BioRemPP & HADEG | 128        | 0.0731        | 8.31%      | 37.98%     |
| KEGG & HADEG     | 169        | 0.2467        | 32.69%     | 50.15%     |

**Core Enzymes:**

- 102 KO identifiers are shared across all three databases.

**Exclusive Content:**

| Database | Exclusive KOs | Percentage |
| -------- | ------------- | ---------- |
| BioRemPP | 1,246         | 80.9%      |
| KEGG     | 181           | 35.0%      |
| HADEG    | 142           | 42.1%      |

### Interpretation

- The overlap structure is consistent with partial concordance across resources and meaningful unique contributions by each source.
- The shared core set provides a stability anchor for cross-resource comparisons.

---

## 4. Mapping Consistency

### Validation Results

Mapping consistency validations passed for both mapping suites:

| Mapping Suite | Expectations Evaluated | Passed | Failed | Status |
| -------- | ------------------ | ------ | ------ | ------ |
| `biorempp_mapping_consistency_suite` | 3 | 3 | 0 | PASS |
| `toxcsm_mapping_linkage_suite` | 3 | 3 | 0 | PASS |

**Mapping Totals:**

- Evaluated expectations: **6**
- Successful expectations: **6**
- Unsuccessful expectations: **0**

### Interpretation

- KO-compound and compound-toxicity linkage constraints remained stable in this run.
- No mapping expectation failure was observed.

---

## 5. Example Roundtrip Regression

### Validation Results

**Status:** PASS

**Datasets Processed:** 5 standardized example datasets

| Dataset   | Input KOs | Unique KOs | BioRemPP Matches | KEGG Matches | HADEG Matches | toxCSM Matches |
| --------- | --------- | ---------- | ---------------- | ------------ | ------------- | -------------- |
| Example_A | 15        | 15         | 199              | 34           | 35            | 199            |
| Example_B | 12        | 12         | 94               | 19           | 0             | 94             |
| Example_C | 12        | 12         | 65               | 0            | 38            | 65             |
| Example_D | 12        | 12         | 13               | 0            | 0             | 0              |
| Example_E | 13        | 13         | 106              | 19           | 34            | 103            |

**Key Findings:**

- All 5 datasets were processed successfully through the complete analytical pipeline.
- Cryptographic checksums (SHA256) were generated for each input and output file.
- Content hashes were computed independently of file ordering to verify logical equivalence.
- Output checksums are archived for future regression testing.

### Interpretation

- Across-database variation in match counts is expected under differential coverage and is consistent with overlap behavior.
- Archived checksums provide a concrete reference for verifying that subsequent releases preserve expected behavior on the example suite.

---

## 6. Use Case Invariants

### Validation Results

**Status:** PASS

**Checks Validated:** 10/10 (all passed with empty fail reasons)

| Dataset   | Output Type     | Total Rows | Invariant Status |
| --------- | --------------- | ---------- | ---------------- |
| Example_A | merged_biorempp | 199        | PASS |
| Example_A | merged_toxcsm   | 199        | PASS |
| Example_B | merged_biorempp | 94         | PASS |
| Example_B | merged_toxcsm   | 94         | PASS |
| Example_C | merged_biorempp | 65         | PASS |
| Example_C | merged_toxcsm   | 65         | PASS |
| Example_D | merged_biorempp | 13         | PASS |
| Example_D | merged_toxcsm   | 0          | PASS |
| Example_E | merged_biorempp | 106        | PASS |
| Example_E | merged_toxcsm   | 103        | PASS |

### Interpretation

These invariants provide a final consistency check over representative merged outputs used in documentation and regression testing.

---

## 7. Controlled Vocabulary Audit

### Validation Results

**Compound Class Distribution:**

| Class               | Records | Percentage |
| ------------------- | ------- | ---------- |
| Aromatic            | 2,249   | 20.69%     |
| Nitrogen-containing | 2,161   | 19.88%     |
| Chlorinated         | 1,816   | 16.71%     |
| Aliphatic           | 1,693   | 15.58%     |
| Polyaromatic        | 1,471   | 13.53%     |
| Inorganic           | 356     | 3.28%      |
| Metal               | 340     | 3.13%      |
| Organophosphorus    | 269     | 2.47%      |
| Sulfur-containing   | 209     | 1.92%      |
| Organometallic      | 171     | 1.57%      |
| Halogenated         | 130     | 1.20%      |
| Organosulfur        | 4       | 0.04%      |

**Total unique compound classes:** 12

**Regulatory Agency Distribution:**

| Agency  | Records | Percentage |
| ------- | ------- | ---------- |
| ATSDR   | 2,459   | 22.62%     |
| IARC2B  | 1,855   | 17.07%     |
| EPC     | 1,349   | 12.41%     |
| PSL     | 1,308   | 12.03%     |
| WFD     | 1,074   | 9.88%      |
| IARC1   | 1,039   | 9.56%      |
| EPA     | 912     | 8.39%      |
| CONAMA  | 536     | 4.93%      |
| IARC2A  | 337     | 3.10%      |

**Total unique regulatory agencies:** 9

**Enzyme Activity Distribution:**

- **Total unique enzyme activities:** 205
- **Most frequent:** cytochrome P450 (19.93%), dioxygenase (10.06%), monooxygenase (8.02%)
- **Zero null values** across all vocabulary fields

### Interpretation

- This audit provides a stable reference for how controlled terms are used in the current snapshot.
- Future releases can compare against these baselines to identify reclassification or expansion.

---

## Summary of Validation Status

| Component | Status | Key Metric |
| ---------------------------- | ------ | ------------------------------------------------------ |
| Provenance Snapshot          | PASS   | 4 databases, 100% data completeness                    |
| Schema Integrity             | PASS   | 55/55 schema expectations passed                       |
| Cross-Database Overlap       | PASS   | 102 core shared KOs                                    |
| Mapping Consistency          | PASS   | 6/6 mapping expectations passed                        |
| Example Roundtrip Regression | PASS   | 5 datasets, checksums archived                         |
| Use Case Invariants          | PASS   | 10/10 checks passed                                    |
| Controlled Vocabulary Audit  | PASS   | 12 compound classes, 9 agencies, 205 enzyme activities |

**Global GX Execution Totals (Checkpoint):**

- Validation definitions executed: **9**
- Expectations evaluated: **102**
- Expectations successful: **102**
- Expectations unsuccessful: **0**

---

## Limitations

These results support internal consistency and reproducible behavior for the validated snapshot, but they do not imply:

- **Biological activity or in situ degradation** (gene presence and database linkage are not evidence of activity).
- **Predictive accuracy** (no gold-standard dataset exists for bioremediation potential).
- **Regulatory compliance or approval** (regulatory annotations are provided for contextualization).

Results are **snapshot-based** and may change as curated resources are updated; provenance checksums and suite versioning are therefore reported alongside this document.
