# Internal Validation

This page describes the internal validation strategy employed by BioRemPP to ensure analytical coherence, structural plausibility, and reproducibility of results.

---

## 1. Purpose of Internal Validation

- **Integrated data behave coherently** across resources with complementary scopes
- **Analytical outputs are structurally plausible** given the input annotations and database coverage
- **Results are reproducible** under identical input conditions and database versions
- **Scientific claims remain bounded** by the nature of computational inference

### Internal Validation vs. Competitive Benchmarking

BioRemPP employs **internal validation**, which assesses the coherence and plausibility of integrated data and analytical outputs within the platform's defined scope.

**Internal validation focuses on:**

- Cross-database consistency (identifier mappings, compound linkages, pathway associations)
- Structural invariants (subset relationships, expected overlap/divergence patterns)
- Deterministic reproducibility (same input + same databases → same output)
- Traceability of analytical transformations (transparency of mapping logic and parameters)

**External competitive benchmarking**, by contrast, compares platform performance against alternative tools using shared test datasets or ground-truth references.

### Why External Benchmarking Is Not Claimed

#### Absence of Comparable Platforms

BioRemPP provides **compound-centric bioremediation potential inference** by integrating:

- Functional annotations (KO identifiers)
- Regulatory classifications (EPA, ATSDR, IARC, WFD, PSL, EPC, CONAMA)
- Toxicological predictions (toxCSM)
- Specialized degradation pathways (HADEG)

No existing platform integrates these dimensions for bioremediation-focused analysis.

**Closest alternatives operate at different levels:**

| Tool/Platform | Scope | Why Not Comparable |
|---------------|-------|-------------------|
| **KEGG Mapper, BlastKOALA, GhostKOALA** | Upstream KO annotation from sequences | Do not integrate regulatory context, toxicity, or compound-centric prioritization |
| **KEGG Pathway Database** | General metabolism and pathway mapping | Not focused on bioremediation; lacks regulatory classifications and toxicity predictions |
| **HADEG** | Hydrocarbon aerobic degradation genes | Specialized subset; does not integrate multiple databases or provide comparative profiling |
| **MetaCyc, BioCyc** | Metabolic pathway databases | Broad metabolic coverage; not prioritized for environmental pollutants or regulatory context |
| **ToxCSM** | Toxicity prediction for compounds | Standalone tool; does not link toxicity to functional genomic annotations |

**Implication:**

External benchmarking requires shared test datasets and ground-truth references. For BioRemPP:

- **No standard test dataset exists** for compound-centric bioremediation inference.
- **No ground-truth reference** defines "correct" bioremediation potential for arbitrary KO sets.
- **Organism-specific validation** would require wet-lab experiments confirming degradation activity, which is beyond the scope of a computational inference platform.

**BioRemPP's validation strategy therefore focuses on:**

- **Internal coherence:** Cross-database consistency, structural plausibility, deterministic mapping.
- **Reproducibility:** Version control, parameter transparency, traceability.
- **Bounded claims:** Genetic potential (not confirmed activity), exploratory analysis (not regulatory compliance).

---

## 2. Cross-Resource Coherence and Expected Overlap

BioRemPP integrates four databases with distinct but complementary scopes. Understanding expected overlap and divergence patterns is essential for interpreting validation outcomes.

### BioRemPP Database: Bioremediation-Focused Subset

**Scope:** BioRemPP Database is a **specialized subset** relative to broader metabolic pathway resources. Compounds absent from BioRemPP Database may still be present in KEGG if they participate in general metabolism or hydrocarbon degradation pathways not classified as priority pollutants.

**Expected pattern:** BioRemPP KO matches represent a subset of KEGG matches.

---

### KEGG Degradation Subset: Metabolic Pathway Context

**Scope:** KEGG provides **pathway-level context** for degradation processes. KOs may appear in KEGG without appearing in BioRemPP Database if they participate in degradation pathways not linked to priority pollutants.

**Expected pattern:** Partial overlap with BioRemPP Database. KEGG's broader pathway coverage includes general metabolism and microbial degradation routes that extend beyond BioRemPP's regulatory focus.

---

### HADEG: Specialized Hydrocarbon Degradation


**Scope:** HADEG provides **specialized overlap** for hydrocarbon degradation. KOs involved in hydrocarbon metabolism are expected to appear in HADEG even if they do not map to regulatory priority pollutants in BioRemPP Database.

**Expected pattern:** HADEG matches represent a specialized functional subset. Overlap with BioRemPP Database is expected for aromatic hydrocarbons (e.g., benzene, naphthalene, PAHs) that appear in regulatory frameworks. Divergence is expected for hydrocarbon intermediates or aerobic oxidation pathways not classified as priority pollutants.

---

### toxCSM: Compound-Level Toxicity Predictions


**Join key:** Compound identifier (`cpd`), not KO identifier.

**Scope:** ToxCSM integration is **compound-dependent**, not KO-dependent. Toxicity predictions are available only for compounds matched via BioRemPP Database. Empty ToxCSM results occur when KOs do not map to BioRemPP compounds..

**Expected pattern:** ToxCSM matches are a subset of BioRemPP Database matches. Coverage reflects availability of chemical structure annotations, not absence of toxicity.

---

### Coherence Summary

| Database | Scope | Expected Relationship to BioRemPP Database |
|----------|-------|--------------------------------------------|
| **BioRemPP** | Regulatory priority pollutants | Core resource (reference set) |
| **KEGG** | Degradation and xenobiotic metabolism pathways | Broader coverage; partial overlap |
| **HADEG** | Aerobic hydrocarbon degradation | Specialized overlap; divergence for non-hydrocarbon pollutants |
| **toxCSM** | Toxicity predictions for BioRemPP compounds | Subset of BioRemPP Database (structure-dependent) |

These relationships are **scientifically expected** given curation scopes and integration logic. Overlap/divergence patterns validate database integration coherence rather than indicating errors.

---

## 3. Structural Plausibility Checks

Internal validation assesses structural plausibility of integrated data at the level of **identifier behavior**, **mapping cardinality**, and **cross-database linkages**.

### 3.1 Identifier Consistency Across Resources

**KO-level integration:**

- BioRemPP Database, KEGG, and HADEG use KO identifiers as join keys.
- Expected behavior: Same KO identifier retrieves consistent functional annotations across databases.

**Compound-level integration:**

- ToxCSM uses compound identifiers (`cpd`) derived from BioRemPP Database.
- Expected behavior: Toxicity predictions link to compounds, not KOs.

**Validation check:** Cross-database joins preserve identifier uniqueness. No identifier format corruption (e.g., whitespace, case mismatches) occurs during integration.

---

### 3.2 One-to-Many Mappings

**Observed cardinality:**

- One KO identifier may map to **multiple compounds** (enzyme promiscuity, multiple substrates).
- One KO identifier may map to **multiple pathways** (multifunctional enzymes, pathway redundancy).
- One compound may be classified by **multiple regulatory agencies** (international priority pollutant consensus).

**Scientific rationale:**

- Enzyme promiscuity: Many enzymes exhibit broad substrate specificity (e.g., cytochrome P450 monooxygenases).
- Pathway redundancy: Metabolic routes may converge or diverge across degradation mechanisms.
- Multi-agency classification: Compounds like benzene, trichloroethylene, and polycyclic aromatic hydrocarbons (PAHs) appear in multiple regulatory frameworks (IARC, EPA, ATSDR, WFD).

**Validation check:** One-to-many relationships are preserved in output tables (no automatic aggregation). Users receive all associations for downstream interpretation.

---

### 3.3 Absence of Matches as Expected Outcome

**Empty results occur when:**

- KO identifiers do not match database-specific coverage (e.g., KO for general metabolism not in BioRemPP Database).
- Compounds lack toxicity predictions (e.g., inorganic ions, metals without SMILES representations).
- Pathway associations are incomplete (e.g., partial pathway coverage in KEGG subset).

**Scientific interpretation:**

Absence of database match does **not** imply absence of biological function. It reflects:

- **Curation scope limitation:** Databases prioritize specific compound classes or pathway types.
- **Knowledge gaps:** Compounds or pathways not yet characterized in bioremediation literature.
- **Structural constraints:** ToxCSM requires SMILES; inorganic compounds may lack chemical structure annotations.

**Validation check:** Empty results are scientifically plausible and documented as expected behavior, not errors.

---

### 3.4 Coherence of Chemical Classes and Regulatory Labels

**Chemical classes:**

- BioRemPP Database assigns compounds to 12 standardized classes (Metal, Aromatic, Organic, Chlorinated, etc.).
- Expected behavior: Chemical classes partition compounds logically. Compounds do not appear in contradictory classes (e.g., "Metal" and "Aromatic" simultaneously unless explicitly curated as organometallic).

**Regulatory labels:**

- Regulatory agency codes (`referenceAG`) act as compound-level metadata.
- Expected behavior: Regulatory classifications are independent of enzymatic function. A single compound may be classified by multiple agencies without contradicting functional annotations.

**Validation check:** Chemical class assignments and regulatory labels behave as contextual layers that do not conflict with KO-level functional annotations.

---

## 4. Representative Coherence Patterns Observed in Practice

The following patterns illustrate structural coherence of integrated data without making organism-specific or experimental performance claims.

### Pattern 1: Specialized Degradation Sets Within Broader Pathway Context

**Observation:**

KO identifiers annotated in BioRemPP (hydrocarbon aerobic degradation) also appear in KEGG Degradation Subset under related pathways (e.g., "Naphthalene degradation," "Toluene degradation").

**Interpretation:**

Specialized degradation databases (BioRemPP) provide focused annotations that overlap with broader pathway resources (KEGG) where curation scopes intersect. This pattern validates that BioRemPP is a **refinement** of KEGG coverage for specific degradation mechanisms, not a contradictory resource.

---

### Pattern 2: Compound-to-Enzyme Promiscuity

**Observation:**

Single compounds (e.g., benzene, toluene) map to multiple KO identifiers representing distinct enzymatic activities (e.g., monooxygenases, dioxygenases, dehydrogenases).

**Interpretation:**

Xenobiotic degradation involves multiple enzymatic steps and alternative degradation routes. One compound may undergo transformation by diverse enzymes depending on organism, pathway context, or environmental conditions. This pattern reflects **biochemical promiscuity** and **pathway redundancy**, not data duplication errors.

---

### Pattern 3: Toxicity Predictions as Compound-Layer Annotations

**Observation:**

Multiple KO identifiers mapping to the same compound (e.g., catechol) share identical toxicity predictions (e.g., AMES mutagenesis, LD50).

**Interpretation:**

Toxicity is a **compound property**, not a gene property. Multiple enzymes producing or degrading the same compound inherit the compound's toxicity profile. This pattern validates the compound-centric integration logic: toxicity predictions propagate to all KOs linked to a given compound.

---

### Pattern 4: Regulatory Labels as Cross-Cutting Metadata

**Observation:**

Compounds classified by multiple regulatory agencies (e.g., benzene: IARC Group 1, EPA Priority Pollutant, ATSDR Substance Priority List) appear as separate rows in BioRemPP Database with distinct `referenceAG` values but identical compound identifiers.

**Interpretation:**

Regulatory frameworks serve complementary purposes (carcinogenicity assessment, environmental monitoring, priority ranking). Multi-agency classification reflects **regulatory consensus** on environmental or health significance. This pattern validates that regulatory labels are metadata layers, not functional annotations.

---

### Pattern 5: Subset Relationships Across Database Scopes

**Observation:**

KO identifiers appearing in BioRemPP Database (regulatory priority pollutants) represent a subset of KO identifiers appearing in KEGG.

**Interpretation:**

BioRemPP Database prioritizes compounds of established regulatory significance. KEGG provides broader metabolic coverage, including intermediates, natural products, and microbial metabolism not classified as priority pollutants. This subset relationship validates intentional curation focus rather than indicating incomplete data.

---

## 5. Reproducibility and Stability Guarantees

### 5.1 Deterministic Mapping Logic

**Principle:**

All database integrations use **exact identifier matching** via inner joins. No probabilistic inference, fuzzy matching, or machine learning–based assignments occur during integration.

**Implication:**

Given identical KO input and unchanged database versions:

- Same KO identifiers retrieve same database records.
- Same compounds map to same toxicity predictions.
- Same pathways associate with same KO groups.

**Reproducibility guarantee:**

Same input + same databases → same merged data → same analytical outputs.

---

### 5.2 Versioned Resources and Provenance

**Database versioning:**

All outputs are linked to specific database versions with documented checksums for integrity verification:

| Database | Version | Snapshot Date | SHA256 Checksum |
|----------|---------|---------------|-----------------|
| **BioRemPP Database** | v1.0.0 | December 15, 2025 | `216cf113400161d6eee8d4eefb13bab23f60f9286874fa41ae8d00f3fc4637c0` |
| **KEGG Degradation** | Release 116.0+/12-19 | December 2025 | `20fff1041ec3c0ccc9510a1c1c27d4d5e3dff2c36dcba37427ef602673af5921` |
| **HADEG** | Commit 8f1ff8f | 2023 | `b588099bb19e123c2384a710b532dfe4fd0413ea80da9f238c0b11e433442a42` |
| **ToxCSM** | v1.0 | 2022 | `0d4616930b438964d9e007b20c9ffb9c414879b775a3b89d660bfc6278fe5f38` |

**Versioning policy:**

- **BioRemPP Database:** Major version changes indicate schema modifications; minor versions indicate content updates.
- **KEGG:** Updated regularly by KEGG consortium. Users must cite **access date** and release version for reproducibility.
- **HADEG, toxCSM:** Static snapshots. Cite original publications and commit/version identifiers.

**Metadata documentation:**

- Database versions documented in release notes and metadata files.
- File checksums (SHA256) provided in `data/databases/checksums.sha256` for integrity verification.
- Curation dates and external source access dates recorded.

**User responsibility:**

To ensure reproducibility, users must report:

- BioRemPP version (e.g., v1.0.0)
- Database snapshot date (e.g., December 2025)
- Database checksums (if integrity verification required)
- Analysis date
- Annotation tool and version used upstream (e.g., eggNOG-mapper v2.1.12)

---

### 5.3 Configuration-Driven Analyses (Declarative YAML Framework)

**Declarative parameter transparency**

All BioRemPP analytical use cases are defined through **declarative YAML configuration files**.
These files explicitly encode **all analytical parameters, data transformations, and visualization logic** used by each use case.

**Examples of YAML-controlled parameters**

Typical parameters defined in the YAML layer include:

* Ranking constraints (e.g., `top_n: 20` samples, `top_n: 10` pathways)
* Pathway completeness thresholds (e.g., `min_coverage: 0.5`)
* Chemical class inclusion or exclusion filters
* Regulatory agency scopes (e.g., EPA, IARC, ATSDR, CONAMA)
* Database selection and weighting rules

These parameters are not embedded in code, but are declared in structured configuration files that are versioned and human-readable.

**Implications for reproducibility**

Because each analysis is driven by an explicit YAML specification:

* Every analytical output can be traced to a **precise configuration state**
* Identical YAML files applied to identical data yield **identical results**
* Parameter changes produce **predictable and reproducible** changes in analytical outputs

This declarative design ensures full **auditability**, **transparency**, and **scientific reproducibility** of BioRemPP analyses.

---

### 5.4 Stability Across Sessions

**Session-based processing:**

Results are not cached across users. Each upload executes the full integration pipeline independently.

**Implication:**

No cross-user contamination. Results are session-isolated and deterministic within session scope.

**Temporal stability:**

Within a single database release:

- Same KO input produces same output regardless of upload time.
- Row order may vary (pandas merge does not guarantee order), but **content** (which rows, which values) is identical.

---

## 6. Limitations of Internal Validation

Internal validation ensures analytical coherence and reproducibility but does **not** constitute experimental validation or competitive performance claims.

**What internal validation does NOT demonstrate:**

- **Sensitivity or specificity:** No ground-truth dataset exists for bioremediation potential inference; therefore, standard benchmark metrics cannot be computed.
- **Biological degradation activity:** Gene presence does not confirm gene expression, enzymatic activity, or in situ degradation performance. All inferences require wet-lab or field validation.
- **Regulatory compliance or approval:** Results provide contextual information only; they do not certify compliance with environmental regulations or safety standards.
- **Superiority over alternative methods:** Absence of comparable platforms precludes competitive benchmarking claims.

**User responsibility:**

Interpretation of results, experimental validation design, and regulatory compliance assessments remain the sole responsibility of the user.

For complete documentation of scope boundaries, methodological constraints, interpretation guidelines, and usage restrictions, see **[Limitations and Scope Boundaries](../methods/limitations.md)**.

---

## Related Pages

- [Mapping Strategy](../methods/mapping-strategy.md) — Identifier normalization and deterministic join logic
- [Data Sources](../methods/data-sources.md) — Database scope, provenance, and coverage
- [Methods Overview](../methods/methods-overview.md) — High-level scientific methodology
- [Limitations](../methods/limitations.md) — Comprehensive scope boundaries and usage restrictions
- [Interpretation Guidelines](../user-guide/interpretation.md) — How to interpret results responsibly
- [Downloads](../user-guide/downloads.md) — Reproducibility requirements for exported data
