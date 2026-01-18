# Internal Validation Results (v1.0)

## Executive Summary

This document reports the outcome of the **BioRemPP Internal Validation Suite** execution and provides evidence that the released data resources and analytical transformations behave **consistently**, remain **traceable to a defined data snapshot**, and support **reproducible** analyses.

* **Validation Date:** 2026-01-16
* **Suite Version:** v1.0
* **Overall Status:** **All validation components passed successfully**.

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
| ToxCSM   | 370     | 66      | 100% (0 nulls)    |

| Database | Version | Snapshot Date | SHA256 Checksum |
|----------|---------|---------------|-----------------|
| **BioRemPP Database** | v1.0.0 | December 15, 2025 | `216cf113400161d6eee8d4eefb13bab23f60f9286874fa41ae8d00f3fc4637c0` |
| **KEGG Degradation** | Release 116.0+/12-19 | December 2025 | `20fff1041ec3c0ccc9510a1c1c27d4d5e3dff2c36dcba37427ef602673af5921` |
| **HADEG** | Commit 8f1ff8f | 2023 | `b588099bb19e123c2384a710b532dfe4fd0413ea80da9f238c0b11e433442a42` |
| **ToxCSM** | v1.0 | 2022 | `0d4616930b438964d9e007b20c9ffb9c414879b775a3b89d660bfc6278fe5f38` |

**Key Findings:**

* All databases exhibit complete data coverage with zero null values across all fields.
* Cryptographic checksums were computed for each database, enabling detection of any future modifications.
* Schema structures were documented, including column names and data types.

### Interpretation

* The zero-null snapshot supports downstream joins without imputation.
* Archived checksums provide a verifiable reference for subsequent releases and for reproducing published analyses.

---

## 2. Schema Integrity

### Validation Results

Schema integrity validation passed for all four databases:

| Database | Required Columns | KO Format    | Duplicates | Null Density    | Status |
| -------- | ---------------- | ------------ | ---------- | --------------- | ------ |
| BioRemPP | 8/8 present      | 10,869 valid | None       | Below threshold | PASS   |
| KEGG     | 3/3 present      | 855 valid    | None       | Below threshold | PASS   |
| HADEG    | 4/4 present      | 867 valid    | None       | Below threshold | PASS   |
| ToxCSM   | 4/4 present      | N/A          | None       | Below threshold | PASS   |

**BioRemPP-Specific Validations:**

* Compound identifiers: All 10,869 records contain valid, non-empty compound IDs.
* Regulatory agencies: All values conform to the controlled vocabulary.
* Compound classes: All records have non-empty compound class assignments.

### Interpretation

* Identifier format checks reduce false non-matches attributable to formatting.
* Controlled-field checks ensure consistent downstream grouping/stratification by compound class and regulatory scope.

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
| BioRemPP ∩ KEGG  | 269        | 0.15          | 17.5%      | 52.0%      |
| BioRemPP ∩ HADEG | 128        | 0.07          | 8.3%       | 38.0%      |
| KEGG ∩ HADEG     | 169        | 0.25          | 32.7%      | 50.2%      |

**Core Enzymes:**

* 102 KO identifiers are shared across all three databases.

**Exclusive Content:**

| Database | Exclusive KOs | Percentage |
| -------- | ------------- | ---------- |
| BioRemPP | 1,246         | 80.9%      |
| KEGG     | 181           | 35.0%      |
| HADEG    | 142           | 42.1%      |

### Interpretation

* The overlap structure is consistent with partial concordance across resources and meaningful unique contributions by each source.
* The shared core set provides a stability anchor for cross-resource comparisons.

---

## 4. Mapping Consistency

### Validation Results

**KO-to-Compound Cardinality:**

| Metric                | Value |
| --------------------- | ----- |
| Total KOs             | 1,541 |
| Mean compounds per KO | 2.22  |
| Median                | 1     |
| Range                 | 1–27  |

The maximum observed cardinality (27 compounds associated with a single KO) is consistent with broad substrate associations commonly observed for large enzyme families.

**Compound-to-KO Cardinality:**

| Metric                | Value |
| --------------------- | ----- |
| Total Compounds       | 384   |
| Mean KOs per compound | 8.9   |
| Median                | 4     |
| Range                 | 1–333 |

The highest redundancy (333 KOs associated with a single compound) reflects the behavior of widely connected metabolites in biochemical knowledge bases.

**ToxCSM Linkage:**

| Metric             | Value  |
| ------------------ | ------ |
| BioRemPP compounds | 384    |
| ToxCSM compounds   | 370    |
| Matched compounds  | 370    |
| Coverage           | 96.35% |

* 14 compounds in BioRemPP lack corresponding toxicity predictions in ToxCSM.
* Zero endpoint-level missingness was observed for matched compounds.

### Interpretation

* Documented linkage coverage supports consistent availability of toxicity endpoints for the majority of curated compounds in this snapshot.
* Reported cardinality ranges inform interpretation of output multiplicity (multiple rows per KO or per compound) as a property of the underlying knowledge integration.

---

## 5. Example Roundtrip Regression

### Validation Results

**Status:** PASS

**Datasets Processed:** 5 standardized example datasets

| Dataset   | Input KOs | BioRemPP Matches | KEGG Matches | HADEG Matches | ToxCSM Matches |
| --------- | --------- | ---------------- | ------------ | ------------- | -------------- |
| Example_A | 15        | 199              | 34           | 35            | 199            |
| Example_B | 12        | 94               | 19           | 0             | 94             |
| Example_C | 12        | 65               | 0            | 38            | 65             |
| Example_D | 12        | 13               | 0            | 0             | 0              |
| Example_E | 13        | 106              | 19           | 34            | 103            |

**Key Findings:**

* All 5 datasets were processed successfully through the complete analytical pipeline.
* Cryptographic checksums (SHA256) were generated for each input and output file.
* Content hashes were computed independently of file ordering to verify logical equivalence.
* Output checksums are archived for future regression testing.

### Interpretation

* The across-database variation in match counts is expected under differential coverage and is consistent with the overlap patterns reported above.
* Archived checksums provide a concrete reference for verifying that subsequent releases preserve expected behavior on the example suite.

---

## 6. Use Case Invariants

### Validation Results

**Status:** PASS

**Datasets Validated:** 10 merged outputs (5 datasets × 2 outputs each)

| Dataset   | Output Type     | Total Rows | Invariants | Status |
| --------- | --------------- | ---------- | ---------- | ------ |
| Example_A | merged_biorempp | 199        | 5/5        | PASS   |
| Example_A | merged_toxcsm   | 199        | 5/5        | PASS   |
| Example_B | merged_biorempp | 94         | 5/5        | PASS   |
| Example_B | merged_toxcsm   | 94         | 5/5        | PASS   |
| Example_C | merged_biorempp | 65         | 5/5        | PASS   |
| Example_C | merged_toxcsm   | 65         | 5/5        | PASS   |
| Example_D | merged_biorempp | 13         | 5/5        | PASS   |
| Example_D | merged_toxcsm   | 13         | 5/5        | PASS   |
| Example_E | merged_biorempp | 106        | 5/5        | PASS   |
| Example_E | merged_toxcsm   | 106        | 5/5        | PASS   |

**Invariants Verified:**

* No negative values in numeric columns
* Valid KO format (K followed by 5 digits)
* No empty sample names
* No invalid regulatory agencies (controlled vocabulary compliance)
* No null compounds when ToxCSM join exists

### Interpretation

These invariants provide a final consistency check over representative merged outputs used in documentation and regression testing.

---

## 7. Controlled Vocabulary Audit

### Validation Results

**Compound Class Distribution:**

| Class               | Records | Percentage |
| ------------------- | ------- | ---------- |
| Aromatic            | 2,249   | 20.7%      |
| Nitrogen-containing | 2,161   | 19.9%      |
| Chlorinated         | 1,816   | 16.7%      |
| Aliphatic           | 1,693   | 15.6%      |
| Polyaromatic        | 1,471   | 13.5%      |
| Inorganic           | 356     | 3.3%       |
| Metal               | 340     | 3.1%       |
| Organophosphorus    | 269     | 2.5%       |
| Sulfur-containing   | 209     | 1.9%       |
| Organometallic      | 171     | 1.6%       |
| Halogenated         | 130     | 1.2%       |
| Organosulfur        | 4       | 0.04%      |

**Total unique compound classes:** 12

**Regulatory Agency Distribution:**

| Agency  | Records | Percentage |
| ------- | ------- | ---------- |
| ATSDR   | 2,459   | 22.6%      |
| IARC 2B | 1,855   | 17.1%      |
| EPC     | 1,349   | 12.4%      |
| PSL     | 1,308   | 12.0%      |
| WFD     | 1,074   | 9.9%       |
| IARC 1  | 1,039   | 9.6%       |
| EPA     | 912     | 8.4%       |
| CONAMA  | 536     | 4.9%       |
| IARC 2A | 337     | 3.1%       |

**Total unique regulatory agencies:** 9

**Enzyme Activity Distribution:**

* **Total unique enzyme activities:** 205
* **Most frequent:** Cytochrome P450 (19.9%), Dioxygenase (10.1%), Monooxygenase (8.0%)
* **Zero null values** across all vocabulary fields.

### Interpretation

* This audit provides a stable reference for how controlled terms are used in the current snapshot.
* Future releases can compare against these baselines to identify reclassification or expansion.

---

## Summary of Validation Status

| Component                    | Status | Key Metric                                             |
| ---------------------------- | ------ | ------------------------------------------------------ |
| Provenance Snapshot          | PASS   | 4 databases, 100% data completeness                    |
| Schema Integrity             | PASS   | 4/4 databases validated                                |
| Cross-Database Overlap       | PASS   | 102 core shared KOs                                    |
| Mapping Consistency          | PASS   | 96.35% ToxCSM coverage                                 |
| Example Roundtrip Regression | PASS   | 5 datasets, checksums archived                         |
| Use Case Invariants          | PASS   | 10/10 outputs, 5/5 invariants each                     |
| Controlled Vocabulary Audit  | PASS   | 12 compound classes, 9 agencies, 205 enzyme activities |

---

## Limitations

These results support internal consistency and reproducible behavior for the validated snapshot, but they do not imply:

* **Biological activity or in situ degradation** (gene presence and database linkage are not evidence of activity).
* **Predictive accuracy** (no gold-standard dataset exists for bioremediation potential).
* **Regulatory compliance or approval** (regulatory annotations are provided for contextualization).

Results are **snapshot-based** and may change as curated resources are updated; provenance checksums and suite versioning are therefore reported alongside this document.
