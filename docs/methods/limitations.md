# Limitations and Scope Boundaries

This page consolidates all known limitations, scope boundaries, and usage restrictions of the BioRemPP Web Service. Understanding these constraints is essential for responsible scientific interpretation and appropriate use of results.

---

## Purpose of Limitations Documentation

BioRemPP is designed as an **exploratory research tool** for hypothesis generation and comparative functional profiling in bioremediation research. This documentation explicitly defines:

- **What BioRemPP does** and **what it does not do**
- **Scientific and methodological boundaries** of computational functional inference
- **Data coverage constraints** and their implications
- **Technical and operational limitations** of the web service
- **Interpretation boundaries** for responsible result interpretation
- **Regulatory and compliance disclaimers** to prevent misuse
- **Reproducibility constraints** and user responsibilities

**Audience:** Researchers, reviewers, and users who need to understand the scope and limitations of BioRemPP for scientific reporting, experimental design, or critical evaluation.

---

## 1. Scientific and Methodological Boundaries

### 1.1 Genetic Potential vs. Biological Activity

**Core Principle:**

BioRemPP infers **genetic potential** from the presence of functional orthologs (KO identifiers). Results indicate the **capacity** for bioremediation functions if genes are expressed and active under appropriate conditions.

**What BioRemPP Results DO Represent:**

- **Gene presence:** Detection of orthologous genes encoding specific enzymatic functions
- **Functional capacity:** Theoretical ability to perform bioremediation processes
- **Comparative profiling:** Relative functional differences across samples

**What BioRemPP Results DO NOT Represent:**

| Aspect | Limitation | Implication |
|--------|-----------|-------------|
| **Gene expression** | KO presence does not confirm transcriptional activity | Genes may be silenced, repressed, or not expressed under sampled conditions |
| **Protein abundance** | Genes may not be translated into functional enzymes | Translation may be blocked or proteins may be degraded |
| **Enzymatic activity** | Proteins may be post-translationally inactive | Cofactor limitation, inhibition, misfolding may prevent activity |
| **Metabolic flux** | Pathway completeness does not guarantee metabolic throughput | Competing pathways, substrate availability, or regulation may prevent flux |
| **In situ performance** | Laboratory or field degradation rates cannot be inferred | Environmental conditions (pH, temperature, toxicity) affect real-world performance |
| **Regulatory compliance** | Results are not validated for legal or clinical decisions | Requires formal risk assessment and experimental validation |

**The Gap Between Potential and Activity:**

Factors influencing the discrepancy between detected genetic potential and confirmed biological activity include:

- **Regulatory mechanisms:** Gene silencing, transcriptional repression, epigenetic modification
- **Environmental conditions:** pH, temperature, oxygen availability, salinity, pressure
- **Substrate bioavailability:** Sorption to soil, low solubility, physical barriers
- **Competing metabolic pathways:** Preference for alternative carbon sources
- **Post-translational modifications:** Phosphorylation, glycosylation, proteolytic cleavage
- **Enzyme inhibition:** Competitive inhibitors, allosteric regulation, product inhibition
- **Cofactor limitation:** NAD(P)H, FAD, metal ions (Fe, Cu, Mo) availability

**Implication for Interpretation:**

> Results indicate **functional potential** (presence of gene encoding a conserved biochemical role) but do not resolve finer enzymatic distinctions that may be biologically relevant under specific environmental conditions.

**All inferences require experimental validation** through wet-lab assays (e.g., RT-qPCR, RNA-seq, proteomics, substrate depletion assays, respirometry) or field monitoring prior to application in remediation scenarios.

---

### 1.2 Resolution Constraints: KO-Level Abstraction

**Input Contract:**

BioRemPP operates exclusively at the **KO identifier level**. This abstraction enables cross-organism functional comparability and reproducible integration but sacrifices finer-grained resolution.

**Trade-offs of KO-Level Resolution:**

| Gain | Loss |
|------|------|
| Cross-organism functional comparability | Strain-specific isoform variation |
| Deterministic mapping to reference databases | Substrate specificity differences within ortholog groups |
| Platform-independent annotation compatibility | Allelic polymorphisms affecting catalytic efficiency |
| Reproducible integration across studies | Context-dependent regulatory variation |

**What Is NOT Captured:**

- **Strain-level resolution:** KO identifiers represent orthologous groups, not individual genes. Sequence variants within a KO group (polymorphisms, isoforms, alleles) are indistinguishable.
- **Substrate specificity variation:** Enzymes within the same KO group may have different substrate preferences, kinetic parameters, or cofactor requirements.
- **Regulatory differences:** Gene expression regulation (promoters, enhancers, transcription factors) is not captured.
- **Catalytic efficiency variation:** Vmax, Km, kcat, turnover number differences between enzyme variants are not modeled.

**Accepted Input:**

- KO identifiers in format `K#####` (K + 5 digits)

**NOT Accepted:**

- Nucleotide or protein sequences
- Genome assemblies
- Gene expression matrices (RNA-seq, microarrays)
- Taxonomic identifiers
- EC numbers 
- Abundance data (gene counts, TPM, FPKM)

---

### 1.3 No Kinetic or Dynamic Modeling

#### 1.3.1 No Kinetic Modeling

**Limitation:**

BioRemPP mapping operates on gene presence/absence. It does **not** model:

- **Enzyme kinetics:** Vmax (maximum velocity), Km (Michaelis constant), kcat (catalytic rate constant)
- **Substrate concentrations:** Pollutant levels in environmental samples
- **Cofactor availability:** NAD(P)H, FAD, metal ions
- **Reaction thermodynamics:** ΔG, equilibrium constants
- **Metabolic flux:** Rate of substrate conversion through pathways

**Implication:**

Pathway completeness (100% of enzymes present) does **not** imply:

- Functional pathway activity under sampled conditions
- Measurable metabolite production
- In vivo catalytic competence
- Quantitative degradation rates

**Design Rationale:**

Kinetic modeling requires quantitative data (enzyme concentrations, substrate availability, environmental parameters) not captured by KO identifiers. Such modeling is outside the scope of this platform.

---

#### 1.3.2 No Expression Weighting

**Limitation:**

All KO identifiers are treated **equally** during mapping. BioRemPP does **not** integrate:

- **Gene expression levels:** RNA-seq TPM, FPKM, or transcript counts
- **Protein abundances:** Proteomics data
- **Metatranscriptomic data:** Active gene expression in microbial communities

**Implication:**

A KO with 1 transcript copy and a KO with 10,000 transcript copies receive **identical treatment** during mapping. Highly expressed genes and lowly expressed genes contribute equally to pathway completeness calculations.

**Workaround:**

Users with expression data must perform post-hoc filtering or weighting of BioRemPP results externally (e.g., intersecting BioRemPP results with RNA-seq data).

---

#### 1.3.3 No Temporal Dynamics

**Limitation:**

BioRemPP mapping represents a **static snapshot** of genetic potential at the time of sampling. It does **not** model:

- **Gene expression regulation over time:** Induction, repression, adaptation
- **Metabolic adaptation:** Upregulation of degradation genes upon substrate exposure
- **Microbial community succession:** Changes in community composition during bioremediation
- **Degradation kinetics:** Time-course of pollutant depletion

**Implication:**

Results indicate **capacity** (genes present) but not:

- **Induction time:** How long until enzymes are expressed after substrate exposure
- **Degradation rates:** Velocity of pollutant transformation
- **Temporal activity patterns:** Diurnal, seasonal, or succession-dependent changes

**Use Case:**

BioRemPP is suitable for comparing functional potential across samples at a single time point, not for modeling bioremediation dynamics.

---

### 1.4 Pathway Completeness Is Not Proof of Activity

**Common Misinterpretation:**

❌ **Incorrect:** "This sample has 100% completeness for the naphthalene degradation pathway, therefore it degrades naphthalene."

✅ **Correct:** "This sample encodes all enzymes required for naphthalene degradation. Experimental validation is needed to confirm degradation activity."

**Rationale:**

Pathway completeness (100% of enzymes present) reflects **gene presence**, not:

- Gene expression under the sampled conditions
- Catalytic activity of translated enzymes
- Metabolic flux through the pathway
- Net conversion of naphthalene to degradation products

**Recommended Workflow for Validation:**

1. **Identify functional potential** using BioRemPP pathway completeness
2. **Prioritize candidates** based on completeness scores
3. **Design experiments** to validate gene expression (RT-qPCR, RNA-seq)
4. **Confirm enzymatic activity** with substrate depletion assays (HPLC, GC-MS)
5. **Assess in situ performance** under environmentally relevant conditions (microcosm, pilot studies)
6. **Document assumptions and limitations** in scientific reports

---

## 2. Data Coverage and Curation Constraints

### 2.1 Database Scope Limitations

BioRemPP integrates four databases with **intentional curation boundaries**. Each database has defined scope and coverage constraints:

#### 2.1.1 BioRemPP Database

**Coverage:**

- **384 unique compounds** prioritized based on regulatory frameworks
- **1,541 unique KO groups** annotated for bioremediation-relevant enzymes

**Limitation:**

- **Not a universal xenobiotic database.** Coverage is limited to compounds of established regulatory or environmental significance.
- **Curation focus:** Priority pollutants listed by EPA, ATSDR, IARC, WFD, PSL, EPC, CONAMA.
- **Exclusions:** General metabolism, natural products, pharmaceuticals not listed as priority pollutants, emerging contaminants without regulatory classification.

**Implication:**

Absence of a compound in BioRemPP Database does **not** imply absence of biological degradation capacity. It may reflect:

- Compound is not yet classified as a priority pollutant
- Curation scope limitation
- Knowledge gap in bioremediation literature

---

#### 2.1.2 KEGG Degradation Subset - "1.11 Xenobiotics biodegradation and metabolism"

**Coverage:**

- **855 records** representing degradation and xenobiotic metabolism pathways
- **Subset of full KEGG database:** Contains only metabolism and degradation-relevant pathways

**Limitation:**

- **Intentional subsetting:** Not a complete KEGG export.
- **Pathways excluded:** Biosynthesis pathways, signaling pathways, disease pathways, organismal systems.
- **Pathway-level granularity:** Does not resolve individual reactions or metabolite intermediates within pathways.

**Included Pathway Examples:**

- Naphthalene degradation
- Chlorinated alkane and alkene degradation
- Toluene degradation
- Xylene degradation
- Cytochrome P450 xenobiotic metabolism
- Aromatic compound degradation

**Implication:**

KEGG Degradation results represent a **focused subset** for bioremediation research, not comprehensive pathway coverage.

---

#### 2.1.3 HADEG Database

**Coverage:**

- **867 records** linking KO identifiers to hydrocarbon degradation pathways
- **Focus:** Aerobic degradation mechanisms (terminal oxidation, biterminal oxidation, Finnerty pathway)
- **Compound classes:** Alkanes, alkenes, aromatics, polymers, biosurfactants.

**Limitation:**

- **Aerobic degradation only:** Does not cover anaerobic degradation pathways (e.g., methanogenesis, sulfate reduction, denitrification, fermentation).
- **Hydrocarbon focus:** Limited to hydrocarbons and structurally related xenobiotics, ploymers and biosurfactants.
- **No kinetic or environmental parameters:** Does not provide degradation rates, optimal conditions (pH, temperature), or substrate concentration ranges.

**Implication:**

HADEG is a **specialized database** for hydrocarbon bioremediation, not a comprehensive xenobiotic database.

---

#### 2.1.4 ToxCSM Toxicity Dataset

**Coverage:**

- **370 compounds** (all compounds from BioRemPP Database with available chemical structure data)
- **31 toxicity endpoints** across 5 categories: Nuclear Receptor, Stress Response, Genetic Toxicity, Environmental, Organ-level
- **66 columns total:** 4 identifiers + 62 prediction columns (31 values + 31 labels)

**Limitation:**

- **Computational predictions only:** Machine learning–based predictions, not experimental toxicity measurements. Models have inherent uncertainty.
- **Coverage dependent on BioRemPP Database:** Only compounds present in BioRemPP Database receive toxicity predictions.
- **No dose-response curves:** Provides classification labels (High/Medium/Low Toxicity) and scores (0–1), not quantitative dose thresholds, EC50, LD50, or NOAEL.
- **Model applicability domain:** Predictions may be less reliable for compounds structurally dissimilar from training data.
- **Not suitable for regulatory submissions:** Requires experimental validation for hazard classification, risk assessment, or regulatory compliance.

**Recommended Use:**

- Screening large compound sets for prioritization
- Identifying candidates for further experimental investigation
- Comparative hazard profiling across samples
- **NOT for:** Clinical decisions, regulatory submissions, definitive hazard determination

---

### 2.2 Absence of Annotation ≠ Absence of Function

**Critical Principle:**

Empty results or absence of database matches do **not** imply absence of biological function. They may reflect:

- **Database curation scope limitations:** Compound or pathway not within database focus
- **Database update lag:** Compound recently discovered or characterized
- **Knowledge gaps:** Insufficient scientific literature on specific degradation mechanisms
- **KO identifier assignment errors:** Upstream annotation tools (KAAS, eggNOG, BlastKOALA) may miss or misannotate genes

**Common Scenario:**

❌ **Incorrect Interpretation:** "No results were returned for the ToxCSM database, so this sample has no toxic compounds."

✅ **Correct Interpretation:** "No matches were found between user KOs and ToxCSM compound mappings. This does not exclude the presence of toxic metabolites not covered by the database."

**Implication:**

Negative results (no database matches) are **expected behavior** when:

- User KO identifiers do not map to bioremediation-relevant compounds (BioRemPP)
- Pathways detected are not xenobiotic degradation pathways (KEGG)
- Genes are not hydrocarbon degradation genes (HADEG)
- Compounds from BioRemPP are not in ToxCSM prediction set (ToxCSM)

**User Responsibility:**

Interpret empty results as **information about database coverage**, not definitive absence of bioremediation capacity. Consult primary literature and conduct experimental validation for comprehensive assessment.

---

### 2.3 Computational Predictions Only (ToxCSM)

**Nature of Predictions:**

ToxCSM provides **machine learning–based toxicity predictions** trained on experimental datasets. Predictions are in silico estimates with inherent model uncertainty.

**What ToxCSM Predictions ARE:**

- **Screening tools** for prioritizing compounds for experimental testing
- **Comparative metrics** for ranking samples by predicted toxicity profiles
- **Hypothesis generators** for identifying potentially hazardous metabolites

**What ToxCSM Predictions ARE NOT:**

- **Definitive hazard classifications:** Require validation with OECD test guidelines
- **Regulatory endpoints:** Not suitable for REACH, EPA, or other regulatory submissions without experimental confirmation

**Uncertainty Sources:**

- **Training data limitations:** Models trained on available experimental data, which may not cover all chemical space
- **Applicability domain:** Predictions less reliable for compounds outside training set chemical space
- **Endpoint-specific performance:** Model accuracy varies by toxicity endpoint

**Recommended Interpretation:**

Use toxicity predictions for **prioritization and screening**, not as definitive toxicological assessments. Always validate with experimental assays (e.g., Ames test, micronucleus assay, aquatic toxicity tests) before making safety or risk determinations.

---

## 3. Technical and Operational Limitations

### 3.1 Input Requirements and Restrictions

#### 3.1.1 KO Identifiers Only

**Accepted Input Format:**

- **KO identifiers** in format `K#####` (K + exactly 5 digits)
- **Plain text file** (`.txt`) with UTF-8 or Latin-1 encoding
- **Sample-organized structure:** Samples start with `>SampleName`, followed by KO identifiers (one per line)

**NOT Accepted:**

| Data Type | Why Not Accepted |
|-----------|------------------|
| **Raw sequencing reads** | BioRemPP does not perform read processing or assembly |
| **Assembled genomes or contigs** | No gene calling or annotation performed |
| **Protein or nucleotide sequences** | No BLAST or sequence alignment performed |
| **Gene expression data** | No RNA-seq, microarray, or qPCR data analysis |
| **Abundance tables** | No quantitative weighting or normalization |
| **Taxonomic identifiers** | No phylogenetic or taxonomic assignment |
| **EC numbers** | No direct EC-to-pathway mapping (use KO upstream tools) |

**Rationale:**

BioRemPP is a **functional analysis tool**, not an annotation pipeline. Users must obtain KO identifiers upstream using dedicated annotation tools:

- **KAAS** (KEGG Automatic Annotation Server)
- **eggNOG-mapper** (evolutionary genealogy of genes: Non-supervised Orthologous Groups)
- **BlastKOALA** or **GhostKOALA** (KEGG Orthology assignment)
- **Prokka** + **KofamScan** (prokaryotic genome annotation + KO assignment)

---

#### 3.1.2 Qualitative Analysis Only

**Limitation:**

BioRemPP performs **qualitative** (presence/absence) analysis of KO identifiers. Quantitative data are **not used**:

- **Gene counts:** Number of times a KO appears is ignored (deduplicated per sample)
- **Expression levels:** TPM, FPKM, RPKM, normalized counts are not accepted
- **Abundance:** Metagenomic coverage, read depth, or relative abundance are not integrated

**Implication:**

A KO present with 1 read and a KO present with 10,000 reads are treated **identically**. Pathway completeness and database matching are based on presence/absence only.

**Workaround:**

Users with quantitative data can:

1. Filter input to include only KOs above expression threshold (e.g., TPM > 10)
2. Perform post-hoc weighting of BioRemPP results using external expression data
3. Use complementary tools (e.g., WGCNA, limma, DESeq2) for expression-based analysis

---

### 3.2 Structural Constraints

**Upload Limits:**

| Constraint | Default Value | Configuration Variable | Enforcement Level |
|------------|---------------|------------------------|-------------------|
| **Maximum samples per upload** | 100 | `BIOREMPP_UPLOAD_SAMPLE_LIMIT` | Hard limit (rejection) |
| **Maximum total KO identifiers** | 500,000 | `BIOREMPP_UPLOAD_KO_LIMIT` | Hard limit (rejection) |
| **Maximum KOs per sample** | 10,000 | `BIOREMPP_PARSING_MAX_KOS_PER_SAMPLE` | Per-sample limit |
| **Maximum file size** | 5 MB | `BIOREMPP_UPLOAD_MAX_SIZE_MB` | Pre-upload validation |

**Sample Name Constraints:**

- **Pattern:** `[a-zA-Z0-9_\-\.]+` (alphanumeric, underscore, hyphen, period only)
- **No whitespace permitted**
- **Case-sensitive**
- **Non-empty required**

**Blank Lines:**

Not permitted. Any line that is neither a sample header (`>...`) nor a valid KO identifier triggers format validation error.

**Rationale:**

Limits ensure fair resource allocation, prevent denial-of-service scenarios, and maintain responsive user experience. For larger datasets, split into multiple files and process separately.

**Configurability:**

All numeric limits are configurable via `config/settings.py`. Values listed above reflect deployment defaults and may differ across installations.

---

### 3.3 Session-Based Data Retention

**Data Retention Policy:**

Results are **session-dependent** and **not persistent**:

- **Storage mechanism:** In-memory (Redis cache)
- **Lifetime:** 4 hours of inactivity or until browser closure
- **Deletion:** Automatic and irreversible upon session termination

**Session Management:**

- **No user accounts:** No authentication or registration required
- **No persistent storage:** Results are not saved to server disk
- **No retrieval from browser history:** Cannot recover results after session expires
- **No cloud backup:** Users must download results before closing browser

**Privacy Implications:**

- **Data privacy:** No biological data is stored server-side after session ends
- **Anonymity:** No user tracking or profiling
- **Ephemeral analysis:** Results exist only during active session

**User Responsibility:**

- **Keep browser tab open** during active analysis
- **Download results immediately** after analysis completes
- **Re-upload required** if session expires

**Session Timeout:**

- **4 hours of inactivity** triggers automatic session termination
- **Browser closure** immediately terminates session

---

### 3.4 No Probabilistic Inference

**Matching Strategy:**

BioRemPP uses **exact string matching** for database integration. It does **not**:

- **Infer missing mappings** based on sequence similarity
- **Use machine learning** to predict associations
- **Assign confidence scores** to mappings
- **Fill missing values** with defaults or imputed values
- **Perform fuzzy matching** or approximate string matching

**Join Type:**

- **Inner join** for all database merges (BioRemPP, KEGG, HADEG, ToxCSM)
- **Only exact matches** are retained
- **No partial matches** or probabilistic assignments

**Implication:**

- **Deterministic results:** Same input always produces same output (if databases unchanged)
- **No false positives:** Only validated database entries are included
- **Conservative approach:** Reduces noise but may miss edge cases

**Rationale:**

Exact matching ensures reproducibility and scientific rigor. Probabilistic methods introduce uncertainty and require validation, which is outside the scope of this platform.

---

## 4. Interpretation Boundaries and Common Misinterpretations

### 4.1 What Results Represent vs. Do Not Represent

**Quick Reference Table:**

| Aspect | What Results Represent | What Results Do NOT Represent |
|--------|----------------------|------------------------------|
| **Gene Presence** | ✅ Detection of KO identifiers matching database annotations | ❌ Confirmed gene expression, transcription, or translation |
| **Functional Capacity** | ✅ Theoretical ability to perform bioremediation if genes are expressed | ❌ Actual enzymatic activity or catalytic competence |
| **Pathway Coverage** | ✅ Proportion of enzymatic steps present in defined routes | ❌ Metabolic flux, throughput, or pathway activity |
| **Comparative Profiling** | ✅ Relative functional differences across samples | ❌ Quantitative degradation rates or kinetics |
| **Toxicity Predictions** | ✅ Computational estimates for prioritization | ❌ Experimental toxicity measurements or regulatory endpoints |
| **Regulatory Context** | ✅ Pollutant classification by environmental agencies | ❌ Regulatory compliance certification or risk assessment |

---

### 4.2 Common Misinterpretations

#### Misinterpretation 1: Pathway Completeness as Proof of Activity

❌ **Incorrect Interpretation:**

> "This sample has 100% completeness for the naphthalene degradation pathway, therefore it degrades naphthalene."

✅ **Correct Interpretation:**

> "This sample encodes all enzymes required for naphthalene degradation. Experimental validation is needed to confirm degradation activity."

**Rationale:** Pathway completeness reflects gene presence, not gene expression or catalytic activity.

---

#### Misinterpretation 2: Toxicity Predictions as Measured Endpoints

❌ **Incorrect Interpretation:**

> "toxCSM predicts LD50 of 250 mg/kg, so this compound is moderately toxic."

✅ **Correct Interpretation:**

> "toxCSM computational model predicts LD50 of 250 mg/kg. Experimental toxicity testing is required for hazard classification."

**Rationale:** Machine learning predictions have inherent uncertainty and are not substitutes for laboratory assays.

---

#### Misinterpretation 3: Database Agreement as Experimental Validation

❌ **Incorrect Interpretation:**

> "This KO appears in BioRemPP, KEGG, and HADEG, so the functional annotation is experimentally validated."

✅ **Correct Interpretation:**

> "This KO is consistently annotated across multiple databases, suggesting robust computational evidence. Experimental validation remains necessary."

**Rationale:** Database consensus reflects agreement among curation efforts, not experimental confirmation.

---

#### Misinterpretation 4: Quantitative Comparisons Across Databases

❌ **Incorrect Interpretation:**

> "Sample A has 500 KOs in KEGG but only 200 in BioRemPP, so KEGG is more comprehensive."

✅ **Correct Interpretation:**

> "Sample A has broader functional coverage in KEGG (500 KOs) than in the bioremediation-specific BioRemPP database (200 KOs), reflecting differences in database scope."

**Rationale:** Databases have different curation focuses. BioRemPP prioritizes bioremediation-relevant enzymes; KEGG covers xenobiotics biodegradation and metabolism.


---

#### Misinterpretation 5: Absence of Results as Absence of Function

❌ **Incorrect Interpretation:**

> "No results were returned for the ToxCSM database, so this sample has no potential for toxic metabolites."

✅ **Correct Interpretation:**

> "No matches were found between user KOs and ToxCSM compound mappings. This does not exclude the presence of toxic metabolites not covered by the database."

**Rationale:** Empty results reflect database coverage limitations, not definitive absence of function.

---

### 4.3 Supported vs. Unsupported Conclusions

**Supported Conclusions:**

- ✅ Identification of functional potential for specific bioremediation pathways
- ✅ Comparative functional profiling across samples or conditions
- ✅ Hypothesis generation for targeted experimental validation
- ✅ Prioritization of candidates for laboratory testing
- ✅ Assessment of database-specific coverage and complementarity
- ✅ Identification of samples with high regulatory pollutant coverage

**Unsupported Conclusions:**

- ❌ Definitive proof of degradation activity
- ❌ Quantitative degradation rates or kinetics (mg/L/day, half-life)
- ❌ In situ bioremediation performance under field conditions
- ❌ Regulatory compliance or safety assessments
- ❌ Clinical or toxicological decision-making
- ❌ Prediction of community-level ecological dynamics
- ❌ Cost-effectiveness or operational feasibility of bioremediation

---

### 4.4 Resolution Limitations

**Analytical Scope:**

BioRemPP is designed for **exploratory analysis**:

- Hypothesis generation
- Candidate prioritization for experimental validation
- Comparative functional profiling

**Not Designed For:**

- Definitive mechanistic conclusions
- Regulatory compliance submissions
- Clinical or risk-based decision-making
- Operational field recommendations without validation

**Use Cases Are Exploratory:**

All 56 use cases (Modules 1–8) provide **exploratory insights** to guide downstream experimental work, not definitive answers about bioremediation efficacy.

---

## 5. Regulatory and Compliance Boundaries

### 5.1 Not a Compliance or Risk Assessment Tool

**Critical Principle:**

Regulatory classifications in BioRemPP are provided **for contextual reference only**. They do **not** constitute compliance determinations, risk assessments, or legal advice.

**BioRemPP Does NOT:**

- ❌ Provide regulatory compliance assessments
- ❌ Certify bioremediation efficacy for regulatory purposes
- ❌ Recommend specific remediation actions based on regulatory status
- ❌ Interpret legal obligations or jurisdiction-specific regulations
- ❌ Conduct formal risk assessments for exposure, toxicity, or environmental impact
- ❌ Provide legal or regulatory advice on permitting, reporting, or compliance pathways

**BioRemPP DOES:**

- ✅ Identify which detected genetic capacities correspond to pollutants of regulatory concern
- ✅ Enable comparative profiling of samples based on priority pollutant coverage
- ✅ Contextualize functional potential within established environmental risk frameworks
- ✅ Support hypothesis generation for targeted experimental validation

**Example of Appropriate Use:**

✅ **Correct:** "Sample A contains genes encoding enzymes for the degradation of five EPA-listed priority pollutants, suggesting potential applicability for Superfund site bioremediation strategies pending experimental validation."

❌ **Incorrect:** "Sample A meets EPA requirements for site remediation based on the presence of degradation genes."

---

### 5.2 Regulatory Classifications Are Temporal Snapshots

**Temporal Limitation:**

BioRemPP regulatory data represents a **snapshot** of classifications as of the last database update.

**Database versions and checksums:**

| Database | Version | Snapshot Date | SHA256 Checksum |
|----------|---------|---------------|-----------------|
| **BioRemPP Database** | v1.0.0 | December 15, 2025 | `216cf113400161d6eee8d4eefb13bab23f60f9286874fa41ae8d00f3fc4637c0` |
| **KEGG Degradation** | Release 116.0+/12-19 | December 2025 | `f3df93d3bc5492043d2f6a9ea087b6687757e4757057ba1ab19c1a0d53fcd619` |
| **HADEG** | Commit 8f1ff8f | 2023 | `d546c01be1cf05866b18aa25fd1edb23e4d90f9ab4e65fb5e37911c1e57ce938` |
| **ToxCSM** | v1.0 | 2022 | `0d4616930b438964d9e007b20c9ffb9c414879b775a3b89d660bfc6278fe5f38` |

**Implications:**

- **Classifications may become outdated** if regulations are amended
- **New compounds may be added** to priority lists after database compilation
- **Compounds may be reclassified** (e.g., IARC group changes based on new evidence)

**User Responsibility:**

For applications requiring current regulatory status (e.g., regulatory submissions, legal compliance), users must verify classifications against the **most recent agency publications**:

- **IARC:** [IARC Monographs](https://monographs.iarc.who.int/)
- **EPA:** [Priority Pollutants List](https://www.epa.gov/eg/toxic-and-priority-pollutants-under-clean-water-act)
- **ATSDR:** [Substance Priority List](https://www.atsdr.cdc.gov/spl/)
- **WFD:** [EU Water Framework Directive](https://eur-lex.europa.eu/eli/dir/2000/60/oj)
- **PSL (CEPA):** [Canadian Priority Substances](https://www.canada.ca/en/environment-climate-change/services/canadian-environmental-protection-act-registry.html)
- **EPC:** [EU REACH](https://echa.europa.eu/)
- **CONAMA:** [Brazilian Environmental Regulations](http://www2.mma.gov.br/port/conama/)

**Recommended Practice:**

Document the BioRemPP Database version and regulatory data access date when reporting results to ensure reproducibility and transparent acknowledgment of temporal limitations.

---

### 5.3 Geographic Coverage Limitations

**Jurisdictions Covered:**

BioRemPP integrates frameworks from **seven sources** representing:

- **North America:** EPA, ATSDR (United States); PSL/CEPA (Canada)
- **South America:** CONAMA (Brazil)
- **Europe:** WFD, EPC (European Union)
- **International:** IARC (WHO)

**Jurisdictions NOT Covered yet:**

Regulatory priorities from **Asia, Africa, and Oceania** are not currently represented. Examples of missing frameworks:

- **China:** Ministry of Ecology and Environment (MEE) priority pollutants
- **Australia:** National Environment Protection Measures (NEPM)
- **Japan:** Chemical Substances Control Law (CSCL)
- **India:** Central Pollution Control Board (CPCB) priority pollutants
- **South Africa:** National Environmental Management Act (NEMA)

**Future Expansion:**

Integration of additional regulatory frameworks is under evaluation for future releases and will be prioritized when:

1. Source data are available in a structured and citable form
2. Framework can be mapped consistently to current BioRemPP compound identifiers
3. Integration does not break backward compatibility

---

### 5.4 Prohibited Uses

**BioRemPP outputs must NOT be used as the sole basis for:**

- ❌ **Clinical diagnostics or medical decisions**
- ❌ **Regulatory submissions or compliance determinations**
- ❌ **Environmental remediation decisions without independent validation**
- ❌ **Commercial product claims without experimental confirmation**
- ❌ **Risk assessments for exposure, toxicity, or site-specific hazards**
- ❌ **Occupational health and safety decisions**
- ❌ **Public health interventions**

**Appropriate Uses:**

- ✅ Academic research and hypothesis generation
- ✅ Educational purposes and training
- ✅ Exploratory analysis of functional genomic data
- ✅ Methodological development and validation
- ✅ Prioritization of candidates for experimental testing
- ✅ Comparative functional profiling across samples

**Legal Disclaimer:**

BioRemPP is provided "as is" without warranty of any kind. The authors and contributors shall not be liable for any claims, damages, or other liabilities arising from the use or misuse of this software or database. See [Terms of Use](../about/terms-of-use.md) for complete legal terms.

---

## 6. Reproducibility and Validation Constraints

### 6.1 Database Versioning Limitations

**Critical Limitation:**

BioRemPP databases are file-based CSV resources. Version and integrity metadata are tracked externally (repository history plus `data/databases/checksums.sha256`), not embedded in each row. Updates to any database file can change integration results for identical KO inputs.

**Reproducibility Table:**

| Aspect | Guaranteed | Not Guaranteed |
|--------|-----------|----------------|
| **Same input → same output** | ✅ Yes (if databases unchanged) | ❌ No (if databases updated) |
| **Order independence** | ✅ Yes (after cache normalization) | ❌ Row order may vary |
| **Platform independence** | ✅ Yes (deterministic merges) | ❌ Pandas version differences may affect edge cases |
| **Null handling** | ✅ Consistent (preserved, except toxCSM) | — |
| **Timestamps** | ❌ No (`created_at` fields use system time) | — |
| **Database versioning** | ❌ No (databases are file-based, no embedded version) | — |

**Implication:**

Reproducibility depends on preserving the same service version, database checksums, and execution time point. Database updates (e.g., KEGG refresh, regulatory framework amendments) can change outputs.

---

### 6.2 Reproducibility Requirements

**User Responsibility:**

To ensure reproducibility, users must document:

1. **BioRemPP version:** Service version (e.g., `1.0.6-beta`)
2. **Analysis date:** Date of analysis execution
3. **Input file:** Original KO annotations (preserve and archive)
4. **Annotation tool and version:** How KO identifiers were generated (e.g., eggNOG-mapper v2.1.12)
5. **Database snapshot date:** Date associated with the database files used
6. **Database file checksums:** SHA256 entries from `data/databases/checksums.sha256`
7. **Use case IDs analyzed:** Module and Use Case numbers (e.g., Module 2, UC-2.1)
8. **Non-default parameters:** Top N values, thresholds, filters (if modified)

**Reproducibility Checklist:**

- [ ] BioRemPP service version
- [ ] Analysis execution date
- [ ] Input file (KO annotations)
- [ ] Annotation tool and version
- [ ] Database snapshot date
- [ ] Database file checksums
- [ ] Use case IDs analyzed
- [ ] Non-default parameters (if any)

**Archival Best Practices:**

1. **Create analysis directory** with subdirectories:
   ```
   analysis_YYYYMMDD/
   ├── input/
   │   └── ko_annotations.txt
   ├── database_exports/
   │   ├── biorempp_db.csv
   │   ├── kegg_degradation_db.csv
   │   ├── hadeg_db.csv
   │   └── toxcsm_db.csv
   ├── use_case_outputs/
   │   ├── uc_2_1_table.csv
   │   └── uc_2_1_plot.svg
   └── metadata.txt
   ```

2. **Document parameters** in `metadata.txt`:
   ```
   BioRemPP version: 1.0.6-beta
   Analysis date: 2026-02-19
   Input samples: 12
   Input KOs: 4532
   Annotation tool: eggNOG-mapper v2.1.12
   Modules analyzed: 1, 2, 7
   Database checksums file: data/databases/checksums.sha256
   ```

3. **Deposit with publications:** Zenodo, Figshare, or institutional repository with DOI

---

### 6.3 No External Experimental Benchmarking

**Limitation:**

BioRemPP has **not been benchmarked against experimental bioremediation datasets** or competitive tools because:

1. **No equivalent tools exist:** No other platform provides a curated compound-centric database and bioremediation potential analysis integrating 4 databases + 7 regulatory frameworks.
2. **No gold standard dataset:** No curated benchmark dataset exists for "complete bioremediation annotation."
3. **Functional annotation is upstream:** BioRemPP assumes KO identifiers are correctly assigned by upstream tools.

**Validation Strategy:**

BioRemPP validation focuses on:

- **Internal consistency checks:** Schema validation, cross-database concordance, structural integrity
- **Biological plausibility:** Results for reference organisms align with known degradation capacities
- **Database curation quality:** BioRemPP Database entries are manually curated from authoritative sources (KEGG, EPA, ATSDR, IARC)

**Not Claimed:**

- ❌ Superior performance against other tools (no equivalent tools for direct comparison)
- ❌ Experimental validation of degradation predictions
- ❌ Benchmark metrics (precision, recall, F1-score) against experimental data

**Rationale:**

Validation is based on **internal consistency, data integrity, and biological plausibility** rather than competitive benchmarking. External validation requires community-driven experimental datasets, which are encouraged but outside the scope of this platform.

---

## Related Pages

- [Methods Overview](methods-overview.md) — High-level methodological framework and scope
- [Data Sources](data-sources.md) — Database inventory, provenance, and coverage
- [Mapping Strategy](mapping-strategy.md) — Technical mapping pipeline and join logic
- [Regulatory Frameworks](regulatory-frameworks.md) — Detailed descriptions of integrated environmental agencies
- [Interpretation Guidelines](../user-guide/interpretation.md) — How to interpret results responsibly
- [Results Page](../user-guide/results-page.md) — Understanding the analytical interface
- [Downloads](../user-guide/downloads.md) — Export results with proper documentation
- [FAQ](../getting-started/faq.md) — Common questions about scope and usage
- [Terms of Use](../about/terms-of-use.md) — Legal disclaimers and usage restrictions
- [How to Cite](../about/how-to-cite.md) — Citation requirements for publications
