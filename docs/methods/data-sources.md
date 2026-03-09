# Data Sources

This page documents the data inventory and provenance of BioRemPP, detailing the databases integrated into the web service, their scientific roles, coverage scope, curation models, and acknowledged limitations.

---

## 1. Purpose of Data Integration

BioRemPP integrates four primary databases to provide multi-source functional context for bioremediation potential inference. This integration addresses complementary scientific dimensions:

**Functional annotation:** Mapping KEGG Orthology (KO) identifiers to enzyme-compound associations relevant to environmental pollutant biotransformation (BioRemPP Database).

**Metabolic pathway coverage:** Contextualizing enzymatic functions within degradation and metabolism pathways (KEGG Degradation Subset).

**Hydrocarbon degradation specialization:** Providing focused annotations for aerobic hydrocarbon degradation enzymes and pathways (HADEG).

**Toxicological context:** Integrating computational toxicity predictions to support compound prioritization and hazard screening (toxCSM).

**Regulatory classification:** Embedding environmental agency classifications at the compound level to contextualize pollutant significance (stored within BioRemPP Database).

### Integration Principle

Database integration enables compound-centric functional reasoning:
 
**KO identifiers → enzymes → compounds → pathways → toxicity/regulatory context**
 
This abstraction facilitates comparative profiling and hypothesis generation across samples, databases, and knowledge domains.

### Critical Constraint

Integration does **not** constitute experimental validation. Results represent genetic potential based on annotation presence, not confirmed biological activity, gene expression, or degradation performance. All computational inferences require wet-lab or field validation prior to application in remediation scenarios.

---

## 2. Data Inventory (Release Snapshot)

**Release snapshot:** December 2025
**Application version:** 1.0.0-beta
**Database version:** 1.0.0

| Database | Scientific Role | Records | File Size | Primary Identifier |
|----------|----------------|---------|-----------|-------------------|
| **BioRemPP Database** | Compound-enzyme-agency mapping (core bioremediation focus) | 10,869 | 1.1 MB | `ko` (KO identifier) |
| **KEGG Degradation Subset** | Metabolism and degradation pathway annotations | 855 | 22 KB | `ko` (KO identifier) |
| **HADEG** | Hydrocarbon aerobic degradation enzymes | 867 | 45 KB | `ko` (KO identifier) |
| **ToxCSM** | Computational toxicity predictions (31 endpoints) | 370 | 186 KB | `cpd` (Compound ID) |

**Total records (this release):** 12,961

**Total data footprint:** 1.39 MB

**Schema integrity:** All expected columns load without schema errors for this release snapshot.

**File format:** UTF-8 encoded CSV with semicolon (`;`) field delimiter for all databases.

**Provenance metadata:** Versioning details, checksums, and schema definitions are documented in [Database Schemas](../database_schemas/biorempp-schema.md)


---

## 3. Primary Databases

### 3.1 BioRemPP Database

**Scientific role:**

BioRemPP Database is the core compound-centric knowledge resource, mapping KO identifiers to environmental pollutants, enzymes, and regulatory classifications. It prioritizes compounds of established environmental and human health significance based on international regulatory frameworks.

**Content:**

| Field | Description | Examples |
|-------|-------------|----------|
| `ko` | KEGG Orthology identifier | K00001, K00128 |
| `cpd` | KEGG Compound identifier | C00038, C06790 |
| `compoundname` | Human-readable compound name | Zinc cation, Trichloroethene |
| `compoundclass` | Standardized chemical class (12 categories) | Metal, Aromatic, Organic, Chlorinated |
| `genesymbol` | Gene or enzyme symbol | E1.1.1.1, ADH1 |
| `genename` | Full gene/enzyme name | alcohol dehydrogenase |
| `enzyme_activity` | Standardized activity term (205 unique) | dehydrogenase, monooxygenase, cytochrome P450 |
| `referenceAG` | Environmental agency code | EPA, ATSDR, IARC1, IARC2A, IARC2B, PSL, EPC, WFD, CONAMA |

> **📄 Full schema specification:** See [BioRemPP Database Schema](../database_schemas/biorempp-schema.md) for complete column definitions, validation rules, and cardinality details.

**Coverage scope:**

- **384 unique compounds** of regulatory and environmental relevance
- **1,541 unique KO groups** annotated for bioremediation-related enzymes
- **12 standardized compound classes** (Metal, Aromatic, Organic, Chlorinated, etc.)
- **205 standardized enzyme activity terms**
- **7 international regulatory frameworks**

**Curation model:**

- **Source integration:** KEGG Orthology API, environmental agency priority pollutant lists
- **Normalization:** Curation to standardize compound classes and enzyme activity terms
- **Inclusion criteria:** Compounds must appear in at least one of the seven integrated regulatory frameworks 
- **Maintenance:** Updates align with major BioRemPP releases (breaking changes in major versions only)

**Cardinality characteristics:**

- **Many-to-many relationships:** One KO may map to multiple compounds; one compound may associate with multiple KO groups.
- **Multi-agency classification:** A single compound may appear in multiple regulatory frameworks, represented as separate rows with distinct `referenceAG` values.

**Example:** Trichloroethene (C06790) maps to 37 distinct KO groups and is classified by five agencies (EPA, ATSDR, IARC1, PSL, WFD).

**Key limitations:**

- **Coverage constraint:** Limited to compounds of established regulatory or environmental significance. Not a universal xenobiotic database.
- **Absence of annotation:** Does not imply absence of biological function; may reflect curation scope, database update lag, or knowledge gaps.
- **No kinetic data:** Does not provide degradation rates, substrate affinity, or catalytic efficiency.
- **No expression data:** Gene presence does not confirm transcription, translation, or post-translational activation.

---

### 3.2 KEGG Degradation Subset

**Scientific role:**

The KEGG Degradation Subset provides pathway-level context for metabolism and xenobiotic degradation. It links KO identifiers to named degradation processes and metabolic routes relevant to environmental biotransformation.

**Content:**

| Field | Description | Examples |
|-------|-------------|----------|
| `ko` | KEGG Orthology identifier | K00001, K00128 |
| `pathname` | Pathway or degradation process name | Naphthalene degradation, Cytochrome P450, Aromatic compound degradation |
| `genesymbol` | Gene or enzyme symbol | E1.1.1.1 |

> **📄 Full schema specification:** See [KEGG Degradation Schema](../database_schemas/kegg-schema.md)

**Coverage scope:**

- **Focused subset:** Contains only metabolism and xenobiotic degradation pathways (not the complete KEGG database)
- **855 records** representing degradation-relevant pathway associations
- **Pathway examples:** Naphthalene degradation, Chlorinated alkane/alkene degradation, Toluene degradation, Xylene degradation, Cytochrome P450 metabolism

**Curation model:**

- **Source:** KEGG Pathway Database
- **Subsetting criteria:** Manual curation to retain pathways explicitly related to xenobiotic metabolism
- **Exclusion:** General metabolism pathways not related to bioremediation or environmental pollutant biotransformation were excluded

**Key limitations:**

- **Intentional subsetting:** Not a complete KEGG export. Covers bioremediation-relevant pathways only.
- **Pathway-level granularity:** Does not resolve individual reactions or metabolite intermediates within pathways.
- **No flux modeling:** Pathway presence does not quantify metabolic throughput or pathway activity.

---

### 3.3 HADEG Database

**Scientific role:**

HADEG (Hydrocarbon Aerobic Degrading Enzymes Database) specializes in aerobic hydrocarbon degradation pathways. It links genes to specific degradation mechanisms for alkanes, aromatics, and related xenobiotics.

**Content:**

| Field | Description | Examples |
|-------|-------------|----------|
| `Gene` | Gene name | ahpC, alkB, dmpN |
| `ko` | KEGG Orthology identifier | K24119, K03386, K00496 |
| `Pathway` | Degradation pathway classification | A_Finnerty_pathway, A_Terminal/biterminal_oxidation |
| `compound_pathway` | Compound class for pathway | Alkanes, Aromatics |

> **📄 Full schema specification:** See [HADEG Database Schema](../database_schemas/hadeg-schema.md)

**Coverage scope:**

- **867 records** linking KO identifiers to hydrocarbon degradation pathways
- **Focus:** Aerobic degradation mechanisms (terminal oxidation, biterminal oxidation, Finnerty pathway)
- **Compound classes:** Alkanes, aromatics, and xenobiotics

**Curation model:**


- **Sequence-level annotation:**  
  Nucleotide and protein sequences associated with hydrocarbon degradation were subjected to functional annotation using **BlastKOALA** and **eggNOG**, enabling standardized assignment of KEGG Orthology (KO) identifiers and orthology-based functional inference.


**Key limitations:**

- **Aerobic degradation only:** Does not cover anaerobic degradation pathways (e.g., methanogenesis, sulfate reduction, denitrification).
- **Hydrocarbon focus:** Limited to hydrocarbon and related xenobiotic classes. Does not comprehensively cover metal biotransformation, nutrient cycling, or non-hydrocarbon organics.
- **No kinetic or environmental parameters:** Does not provide degradation rates, optimal conditions, or substrate concentration ranges.

---

### 3.4 ToxCSM Toxicity Dataset

**Scientific role:**

ToxCSM provides machine learning–based toxicity predictions for compounds identified in the BioRemPP Database. It enables in silico hazard screening and prioritization based on predicted toxicological endpoints.

**Content:**

| Category | Endpoints | Example Endpoints |
|----------|-----------|-------------------|
| **Core identifiers** | 4 fields | SMILES, `cpd` (Compound ID), ChEBI, compoundname |
| **Nuclear Receptor (NR)** | 9 endpoints | Androgen Receptor, Estrogen Receptor, Aryl Hydrocarbon Receptor |
| **Stress Response (SR)** | 5 endpoints | Antioxidant Response Element, p53, Heat Shock Element |
| **Genetic Toxicity (Gen)** | 3 endpoints | AMES Mutagenesis, Carcinogenesis, Micronucleus |
| **Environmental (Env)** | 6 endpoints | Fathead Minnow, Biodegradation, Crustacean toxicity |
| **Organ-level (Org)** | 8 endpoints | Liver Injury, Skin Sensitization, hERG Inhibition |

**Total:** 31 toxicity endpoints, each with two columns (`value_[endpoint]`: numerical score 0–1; `label_[endpoint]`: classification label)

**Coverage scope:**

- **370 compounds** (all compounds from BioRemPP Database with toxCSM predictions)
- **66 columns total** (4 identifiers + 62 prediction columns)
- **Join key:** `cpd` (Compound ID), not `ko` (differs from other databases)

> **📄 Full schema specification:** See [ToxCSM Database Schema](../database_schemas/toxcsm-schema.md)

**Curation model:**

- **Computational predictions:** Machine learning models trained on experimental toxicity data
- **Compound integration:** Predictions generated for all BioRemPP Database compounds with SMILES structural data

**Key limitations:**

- **Computational predictions only:** Not experimental toxicity measurements. Models have inherent uncertainty.
- **Coverage dependent on BioRemPP Database:** Only compounds in BioRemPP Database receive toxicity predictions.
- **No dose-response curves:** Provides classification labels and scores, not quantitative dose thresholds or EC50/LD50 measurements.
- **Model applicability domain:** Predictions may be less reliable for compounds structurally dissimilar from training data.
- **Not suitable for regulatory submissions:** Requires experimental validation for hazard classification or risk assessment.

---

## 4. Regulatory Classification Sources (Overview Only)

BioRemPP integrates priority pollutant classifications from **seven international environmental and health regulatory frameworks**. These classifications are stored at the **compound level** within the `referenceAG` field of the BioRemPP Database.

**Integrated frameworks:**

- **IARC** (International Agency for Research on Cancer, WHO) — Groups 1, 2A, 2B
- **EPA** (U.S. Environmental Protection Agency)
- **ATSDR** (Agency for Toxic Substances and Disease Registry, U.S.)
- **WFD** (Water Framework Directive, European Union)
- **PSL** (Priority Substances List, Canada - CEPA)
- **EPC** (European Parliament Commission - Priority Chemicals)
- **CONAMA** (National Environmental Council, Brazil)

**Purpose:**

Regulatory classifications provide **scientific context** for prioritizing compounds based on established environmental and health significance. They do **not** constitute compliance determinations, legal assessments, or risk certifications.

**Granularity:**

Classifications are stored at the compound level. A single compound may be classified by multiple agencies, represented as multiple rows in the BioRemPP Database with distinct `referenceAG` values.

**Detailed documentation:**

For comprehensive descriptions of each framework, classification criteria, jurisdictional scope, and interpretation boundaries, see [Regulatory Frameworks](regulatory-frameworks.md).

---

## 5. Licensing & Usage Constraints

### BioRemPP Components

**BioRemPP Database:**

- **License:** Creative Commons Attribution 4.0 International (CC BY 4.0)
- **Permitted uses:** Academic, commercial, and derivative works with proper attribution
- **Citation requirement:** Mandatory for publications and reports

**Web Service Source Code:**

- **License:** Apache License 2.0
- **Permitted uses:** Academic, commercial, modification, and redistribution with attribution

### Third-Party Dependencies

**KEGG:**

- **Academic use:** Permitted under KEGG academic license
- **Commercial use:** Requires separate commercial license from KEGG
- **User responsibility:** Users must ensure compliance with KEGG licensing terms

**HADEG:**

- **License:** Open access
- **Citation:** See HADEG original publication

**ToxCSM:**

- **License:** Open access for academic use
- **Citation:** See toxCSM original publication and web service

**Compliance obligation:**

Users are solely responsible for ensuring their use of BioRemPP complies with all applicable third-party licenses. BioRemPP does not redistribute proprietary data beyond what is permitted by respective licenses.

**Complete licensing documentation:**

See [License](../about/license.md) and [Terms of Use](../about/terms-of-use.md) for comprehensive legal terms, disclaimers, and usage restrictions.

---

## 6. Versioning, Provenance & Update Policy

### Current Version

- **Database version:** 1.0.0
- **Application version:** 1.0.0 (status: under peer review until official article publication)
- **Release date:** December 15, 2025
- **Database snapshot date:** December 2025

### Schema Stability

- **Stable in v1.x.x:** Column names and data types remain consistent across minor versions
- **Non-breaking changes permitted in minor versions:**
  - Addition of new compounds or KO groups
  - Expansion of controlled vocabularies (enzyme activity terms, compound classes)
  - Updates to KEGG pathway references
- **Breaking changes only in major versions (v2.0.0+):**
  - Column renames or removals
  - Data type changes
  - Schema restructuring

### Provenance Documentation

**Schema documentation:** [Database Schemas Documentation](../database_schemas/biorempp-schema.md)

**Traceability:**

- **File checksums (SHA256):** Documented in metadata for integrity verification
- **Curation dates:** Documented in release notes
- **External source access dates:** Documented for KEGG and regulatory agency data

### Update Policy

**Database updates:**

- **Major updates:** Aligned with major application releases (v2.0.0+)
- **Minor updates:** Bug fixes, compound additions, agency updates (v1.x.0)
- **Backward compatibility:** Ensured for all v1.x.x versions

**KEGG refresh:**

- **Frequency:** Annually or as needed for major KEGG releases
- **Access date documentation:** Critical for reproducibility (KEGG updates regularly)

### Reproducibility Requirements

Users reporting results derived from BioRemPP must document:

- **Database version:** 1.0.0 (or version used)
- **Application version:** 1.0.0-beta (or version used)
- **Analysis date:** Date of analysis execution
- **Database access date:** Especially for KEGG (subject to updates)

---

## 7. Scope and Limitations

BioRemPP provides **exploratory functional inference** of bioremediation potential based on genetic annotations. Results represent **genetic capacity**, not confirmed biological activity, gene expression, or degradation rates.

**Critical boundaries:**

- Genetic potential ≠ biological activity
- No kinetic modeling or expression weighting
- Computational predictions require experimental validation
- Not suitable for regulatory compliance or clinical decisions

For complete documentation of scope boundaries, methodological constraints, interpretation guidelines, and usage restrictions, see **[Limitations and Scope Boundaries](limitations.md)**.

---

## Related Pages

- [Mapping Strategy](mapping-strategy.md) — Identifier normalization and database integration logic
- [Regulatory Frameworks](regulatory-frameworks.md) — Detailed descriptions of integrated environmental agencies
- [Methods Overview](methods-overview.md) — High-level methodological framework
- [License](../about/license.md) — Legal terms for software and database content
- [Terms of Use](../about/terms-of-use.md) — Usage restrictions and disclaimers
- [Interpretation Guidelines](../user-guide/interpretation.md) — How to interpret database results responsibly
