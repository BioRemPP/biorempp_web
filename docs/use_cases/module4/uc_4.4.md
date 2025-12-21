# UC-4.4 - Functional Fingerprint of Samples by Pathway

**Module:** 4 – Functional and Genetic Profiling  
**Visualization type:** Interactive radar (polar) plot (pathway-level KO richness for a selected sample)  
**Primary inputs:** `KEGG_Results.xlsx or KEGG_Results.csv` (sample–KO–KEGG pathway associations)  
**Primary outputs:** Pathway-level "functional fingerprint" of a selected sample

---

## Scientific Question and Rationale

**Question:** What is the specific functional fingerprint of each sample, as defined by the distribution and richness of its annotated metabolic pathways?

Rather than comparing samples for a single pathway, this use case focuses on **characterizing one sample across all its KEGG pathways**.  

By summarizing, for a selected sample, the **unique KO richness** per pathway and representing it on a **radar (polar) plot**, the visualization can provide an intuitive, shape-based **functional fingerprint**. This may reveal:

- which pathways are particularly **enriched or dominant** for that sample, and  
- whether the sample may behave as a **specialist** (skewed profile) or **generalist** (more balanced profile) within the KEGG metabolic space.

---

## Data and Inputs

- **Primary data source:** `KEGG_Results.xlsx or KEGG_Results.csv` (semicolon-delimited)  
- **Key columns:**
  - `sample` – identifier for each biological sample  
  - `pathname` – KEGG pathway name or identifier  
  - `ko` – KEGG Orthology (KO) identifier associated with that sample and pathway  

- **User control:**
  - A **dropdown menu** allowing selection of a single **Sample** (`sample`) for detailed profiling.

- **Output structure:**
  - **Axes (θ):** one axis per KEGG pathway (`pathname`) present in the selected sample  
  - **Radius (r):** unique KO count for each `(sample, pathway)` pair  
  - **Polygon:** a closed shape connecting all pathway points, representing the sample's functional fingerprint

---

## Analytical Workflow

1. **Sample Selection (User Input)**  
   The user selects a **single sample** from an interactive dropdown menu.  
   - All subsequent filtering and aggregation are restricted to this selected `sample`.

2. **Dynamic Filtering**  
   - The KEGG results table `KEGG_Results.xlsx or KEGG_Results.csv` is loaded.  
   - The dataset is filtered to retain only rows where:
     - `sample` equals the selected sample, and  
     - both `pathname` and `ko` are valid and non-missing.

3. **Aggregation of Pathway-Level KO Richness**  
   - The filtered data is grouped by `pathname`.  
   - For each pathway, the **number of distinct KO identifiers** is computed (e.g., via `nunique()` on `ko`).  
   - This produces a set of `(pathname, unique_ko_count)` pairs representing the **pathway-level KO richness** for that sample.

4. **Rendering as Radar (Polar) Plot**  
   - Each `pathname` is mapped to an angular coordinate (θ) around the circle.  
   - The corresponding **radius (r)** is the unique KO count for that pathway.  
   - A closed polygon is drawn by connecting these points, optionally with markers at each vertex:
     - axes: metabolic pathways  
     - radius: KO richness for the selected sample in each pathway

---

## How to Read the Plot

- **Dropdown Menu (Sample Selection)**  
  - Use the menu to select the **Sample** whose functional fingerprint you want to inspect.  
  - The radar plot recomputes and updates automatically.

- **Axes (θ – Metabolic Pathways)**  
  - Each radial axis represents a **KEGG Pathway** (`pathname`) for which the selected sample has at least one associated KO.  
  - The set of axes forms an inventory of the pathway space encoded in that sample.

- **Radius (r – Pathway KO Richness)**  
  - The **distance from the center** along each axis is proportional to the **count of unique KOs** mapped to that pathway in the selected sample.  
  - Higher values indicate stronger representation or greater complexity of that pathway in the sample.

- **Polygon Shape (Functional Fingerprint)**  
  - The polygon connecting all axes encodes the **overall distribution of functional richness**:
    - pronounced "spikes" along specific axes may indicate **strong specialization** in those pathways  
    - a more rounded, balanced shape may indicate a **broad and relatively even metabolic repertoire**

---

## Interpretation and Key Messages

- **Functional Specialization**  
  - A radar shape heavily skewed toward a subset of related pathways (e.g., several hydrocarbon or xenobiotic degradation pathways) may indicate that the sample is a **functional specialist** in those domains.  
  - Such samples could be best suited for **targeted bioremediation tasks** where those pathways are critical.

- **Metabolic Breadth and Generalist Profiles**  
  - A more circular or evenly expanded polygon may suggest a **generalist** profile, where the sample maintains **moderate to high richness across many different pathways**.  
  - These samples could be valuable in scenarios that require **robust, multi-functional performance** under variable environmental conditions.

- **Comparative Profiling Across Samples**  
  - By switching between samples in the dropdown, users can **compare fingerprints** directly.  
  - This can help identify **complementary candidates** for consortium design and may hint at their potential ecological roles.

- **Link to Other BioRemPP Modules**  
  - When interpreted together with completeness scorecards, toxicity mapping, and regulatory alignment analyses, the functional fingerprint can help bridge **genomic potential** with **applied bioremediation design**, supporting hypothesis generation and experimental planning.

---

## Reproducibility and Assumptions

- **Input Format**  
  The analysis requires a semicolon-delimited KEGG results table containing at least:
  - `sample`,  
  - `pathname`,  
  - `ko`.

- **Definition of Pathway Richness**  
  - For each `(sample, pathway)` pair, pathway richness is defined as the **count of unique KO identifiers** mapped to that pathway.  
  - Multiple occurrences of the same `(sample, pathname, ko)` combination do **not** increase the value; KOs are counted once per pathway per sample.

- **Scope and Limitations**  
  - The metric captures **genetic potential** (annotated KO presence) rather than expression, regulation, or actual metabolic flux.  
  - Radar plots are most interpretable when the number of pathways shown is moderate; in cases with very many low-richness pathways, pre-filtering (e.g., minimum KO count threshold) may be applied for clarity.

 