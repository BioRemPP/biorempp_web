# UC-4.1 — Functional Profiling of Samples by Metabolic Pathway

**Module:** 4 – Functional and Genetic Profiling  
**Visualization type:** Interactive horizontal bar chart (pathway-level KO richness for a selected sample)  
**Primary inputs:** `KEGG_Results.xlsx or KEGG_Results.csv` (sample–KO–KEGG pathway associations)  
**Primary outputs:** Ranked list of KEGG pathways by unique KO count for a selected sample

---

## Scientific Question and Rationale

**Question:** What is the specific functional profile of each sample, as defined by the richness of its annotated metabolic pathways?

The goal is to characterize, for a given sample, **which KEGG metabolic pathways are present and how functionally rich they are**, as approximated by the diversity of KEGG Orthology (KO) identifiers mapped to each pathway. This can yield a **pathway-level functional fingerprint** for each sample and may provide a direct, interpretable view of its dominant metabolic capabilities, potential specializations, and overall functional breadth within the KEGG framework.

---

## Data and Inputs

- **Primary data source:** `KEGG_Results.xlsx or KEGG_Results.csv` (semicolon-delimited)  
- **Key columns:**
  - `sample` – identifier for each biological sample  
  - `pathname` – KEGG pathway name or identifier  
  - `ko` – KEGG Orthology (KO) identifier associated with that sample and pathway  

- **User control:**
  - A **dropdown menu** allowing selection of a single `sample` to be profiled.

- **Output structure:**
  - **Bars:** KEGG pathways present in the selected sample  
  - **Bar value:** count of **unique KOs** per `(sample, pathname)` pair (pathway-level KO richness)

---

## Analytical Workflow

1. **Sample Selection (User Input)**  
   The user selects a **single sample** from an interactive dropdown menu.  
   - All subsequent steps are restricted to this selected `sample`.

2. **Dynamic Filtering**  
   The KEGG results table `KEGG_Results.xlsx or KEGG_Results.csv` is loaded and filtered to retain only rows where:
   - `sample` equals the selected sample, and  
   - `pathname` and `ko` are valid and non-missing.

3. **Aggregation of Pathway-Level KO Richness**  
   - The filtered data is grouped by `pathname`.  
   - For each pathway, the **number of distinct KO identifiers** is computed (e.g., via `nunique()` on `ko`).  
   - This unique KO count is used as a proxy for the **functional richness** or complexity of that pathway in the selected sample.

4. **Sorting and Rendering**  
   - The resulting `(pathname, unique_ko_count)` pairs are sorted (typically from lowest to highest or vice versa) to produce an intuitive ranking.  
   - The aggregated data is rendered as a **horizontal bar chart**, with:
     - one bar per KEGG pathway,  
     - bar length proportional to the unique KO count.

---

## How to Read the Plot

- **Dropdown Menu**  
  - Use the menu to choose the **Sample** whose functional profile you wish to inspect.  
  - The bar chart updates automatically when a different sample is selected.

- **Y-axis (Pathways)**  
  - Each entry on the y-axis corresponds to a **KEGG Pathway** (`pathname`) present in the selected sample.  
  - The set of labels provides a **catalogue of pathways** encoded in that sample's genome (or metagenome).

- **X-axis (KO Richness)**  
  - The x-axis represents the **count of unique KOs** associated with each pathway for the selected sample.  
  - Larger values indicate a greater diversity of functions contributing to that pathway.

- **Bars (Length and Optional Labels)**  
  - The **length** of each bar is proportional to the unique KO count for that pathway.  
  - Optional numeric labels on bars can display the exact KO count, making it straightforward to compare pathway richness quantitatively.

---

## Interpretation and Key Messages

- **Dominant Pathways and Core Capabilities**  
  - The **longest bars** may identify the **most functionally rich pathways** for the selected sample.  
  - These could correspond to the organism's **primary metabolic capabilities**, such as central carbon metabolism, key environmental response pathways, or major degradation routes relevant to bioremediation.

- **Functional Specialization**  
  - A sample whose top-ranked pathways are strongly associated with specific compound classes (e.g., hydrocarbons, aromatics, xenobiotics) could be **specialized for those substrates**.  
  - Comparing the profile of different samples may reveal which entities are enriched for **bioremediation-relevant functions** versus more generic metabolic processes.

- **Comparative Profiling Across Samples**  
  - By switching the selected sample in the dropdown, users can **compare functional fingerprints**.  
  - These comparisons can support **rational candidate selection** for specific environmental contexts or pollutant types.

---

## Reproducibility and Assumptions

- **Input Format**  
  The analysis requires a semicolon-delimited KEGG results table with at least:
  - `sample`,  
  - `pathname`,  
  - `ko`.

- **Definition of Pathway Richness**  
  - Pathway "richness" is quantified as the **count of unique KOs** mapped to that pathway for a given sample.  
  - This metric is interpreted as a proxy for **pathway completeness or complexity**, not an absolute measure of biochemical flux or activity.

- **De-duplication and Data Consistency**  
  - Multiple occurrences of the same `(sample, pathname, ko)` triplet in the raw data do **not** increase the richness value; KOs are counted **once per pathway per sample**.  
  - Accurate interpretation assumes consistent naming of `sample`, `pathname`, and `ko` across the dataset.

- **Scope of Inference**  
  - The visualization reflects **genetic potential** (presence of annotated KOs), not expression, regulation, or kinetic performance.  
  - It should be integrated with other BioRemPP layers (e.g., toxicology, regulatory mapping, network analyses) when designing bioremediation experiments or consortia.


 
---

## Activity diagram of the use case

*Click on the image to enlarge and explore details.*

<a class="glightbox" href="../uc_4.1.png">
  <img src="../uc_4.1.png" alt="Activity diagram of the use case">
</a>


