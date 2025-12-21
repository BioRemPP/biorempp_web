# UC-8.4 — HADEG Pathways Completeness Scorecard

**Module:** 8 – Assembly of Functional Consortia  
**Visualization type:** Interactive heatmap (Pathway Completeness Score per sample–pathway pair)  
**Primary inputs:** `HADEG_Results.xlsx or HADEG_Results.csv` (sample–KO–pathway associations)  
**Primary outputs:** Matrix of per-sample **Pathway Completeness Scores** for HADEG degradation pathways

---

## Scientific Question and Rationale

**Question:** Which samples possess the most "complete" genetic toolkit for a given degradation pathway, and how can this be used to identify elite functional specialists?

This use case focuses on **pathway-level completeness** using degradation pathways curated in the HADEG database. For each HADEG pathway, the analysis quantifies how many of the **KEGG Orthology (KO) identifiers** associated with that pathway are present in a given sample. The resulting **Pathway Completeness Score** (expressed as a percentage) may allow the identification of **elite pathway specialists**, comparison of pathway coverage across samples, and assessment of which pathways are likely to require **multi-sample consortia** for full functional realization.

---

## Data and Inputs

- **Primary data source:** `HADEG_Results.xlsx or HADEG_Results.csv` (semicolon-delimited)  
- **Key columns:**
  - `sample` – identifier for each biological sample  
  - `ko` – KEGG Orthology (KO) identifier annotated for that sample  
  - `compound_pathway` – HADEG pathway label associated with the KO  

- **Scorecard structure:**
  - **Rows:** Samples  
  - **Columns:** HADEG degradation pathways (`compound_pathway`)  
  - **Cell value:** Pathway Completeness Score (%) for each `(sample, pathway)` pair  

---

## Analytical Workflow

1. **Data Loading**  
   The HADEG analysis results table `HADEG_Results.xlsx or HADEG_Results.csv` is loaded from its semicolon-delimited format.

2. **Feature Engineering – Pathway Completeness Score**  
   For each HADEG pathway, a three-step calculation is performed:

   1. **KO Universe per Pathway**  
      For each `compound_pathway`, determine the **universe of unique KOs** observed for that pathway across all samples.

   2. **Sample-Specific KO Count**  
      For each `(sample, compound_pathway)` pair, count the **number of unique KOs** that the sample possesses for that pathway.

   3. **Score Calculation**  
      Compute the **Pathway Completeness Score (%)** as:  
      `Pathway Completeness Score = (unique KOs in sample for that pathway / total unique KOs for that pathway) × 100`.

3. **Matrix Construction**  
   The per-pair scores are reshaped into a **2D matrix**:
   - **rows** represent `sample`,  
   - **columns** represent `compound_pathway`,  
   - **cell values** store the Pathway Completeness Score (%).

4. **Rendering as Heatmap**  
   The matrix is rendered as an **interactive heatmap**:
   - cell color intensity is proportional to the Pathway Completeness Score,  
   - optional numeric labels can display the exact percentage value inside each cell.

---

## How to Read the Plot

- **Y-axis (Rows)**  
  Each row corresponds to a single **Sample**.

- **X-axis (Columns)**  
  Each column corresponds to a **HADEG Compound Pathway** (`compound_pathway`).

- **Cells (Color and Label)**  
  - The **color intensity** of each cell encodes the **Pathway Completeness Score (%)** for the corresponding sample–pathway pair.  
  - Brighter or warmer colors indicate **higher pathway completeness**, while darker or cooler colors indicate **lower completeness**.  
  - If enabled, the numeric label within a cell shows the exact percentage.

---

## Interpretation and Key Messages

- **Identifying Elite Pathway Specialists**  
  Brightly colored cells ("hotspots") may highlight samples that are **elite specialists** for specific pathways:
  - a **100% score** indicates that the sample contains **all KOs** associated with the pathway in the dataset,  
  - such samples could be strong candidates for single-sample deployment where a particular HADEG degradation pathway is central to the remediation strategy.

- **Comparing Functional Potential Across Pathways**  
  Reading **across a row** (left to right) may reveal the **range of pathway capabilities** for a sample:
  - multiple high-scoring cells may indicate a **versatile degrader** that is functionally effective across several pathways,  
  - one or two isolated hotspots may indicate a more **pathway-focused specialist**.

- **Assessing Pathway Difficulty and Fragmentation**  
  Reading **down a column** (top to bottom) may reveal how well a pathway is covered across all samples:
  - if no sample achieves a high completeness score, the pathway could be **complex or fragmented**,  
  - such pathways may require **consortia**, combining multiple samples to assemble a fully complete KO set.

- **Guiding Consortium Design with HADEG Pathways**  
  This scorecard can support pathway-centric design of consortia:
  - samples with high completeness for **different pathways** can be combined to produce a **multi-pathway-capable** consortium,  
  - or multiple samples with partially overlapping coverage of a **single difficult pathway** can be combined to achieve near-complete or complete functional coverage.

---

## Reproducibility and Assumptions

- **Input Format**  
  The analysis requires a semicolon-delimited HADEG results table containing at least:
  - `sample`,  
  - `ko`,  
  - `compound_pathway`.

- **Definition of KO Universe per Pathway**  
  For each `compound_pathway`, the **"total universe"** of KOs is defined **by the dataset**:
  - it includes all unique KOs observed for that pathway across all samples in `HADEG_Results.xlsx or HADEG_Results.csv`,  
  - no external canonical pathway definition is imported or enforced.

- **Normalization**  
  The Pathway Completeness Score is expressed as a **percentage**, enabling fair comparison:
  - between pathways with different total KO counts, and  
  - between samples with variable annotation density.


- **Interpretation Scope**  
  As with other completeness metrics in Module 8, the Pathway Completeness Score measures **genetic potential**, not kinetic performance, expression, or regulation. It should be interpreted as a **structural capacity indicator** to be integrated with other functional, toxicological, and network-level analyses in BioRemPP.
