# UC-4.2 — Ranking of Samples by Pathway Richness

**Module:** 4 – Functional and Genetic Profiling  
**Visualization type:** Interactive vertical bar chart (sample-level KO richness for a selected pathway)  
**Primary inputs:** `KEGG_Results.xlsx or KEGG_Results.csv` (sample–KO–KEGG pathway associations)  
**Primary outputs:** Ranked list of samples by unique KO count for a selected KEGG pathway

---

## Scientific Question and Rationale

**Question:** For any given metabolic pathway, which samples possess the highest functional richness or completeness, as measured by their unique KO count?

Instead of asking which pathways dominate a single sample, this analysis inverts the perspective: for a **selected KEGG pathway**, it compares **all samples** in terms of how many distinct KEGG Orthology (KO) identifiers they encode for that pathway.  

The result is a **pathway-centric ranking** of samples that:

- may identify **elite functional specialists** for specific degradation routes, and  
- can help distinguish **versatile generalists** that are strongly represented across many pathways from more **niche specialists**.

This may be directly useful for pathway-oriented candidate selection and consortium design.

---

## Data and Inputs

- **Primary data source:** `KEGG_Results.xlsx or KEGG_Results.csv` (semicolon-delimited)  
- **Key columns:**
  - `sample` – identifier for each biological sample  
  - `pathname` – KEGG pathway name or identifier  
  - `ko` – KEGG Orthology (KO) identifier associated with that sample and pathway  

- **User control:**
  - A **dropdown menu** allowing selection of a single **metabolic pathway** (`pathname`) to analyze.

- **Output structure:**
  - **Bars:** samples associated with the selected pathway  
  - **Bar value:** pathway-level KO richness per sample (count of unique KOs for that `sample`–`pathname` pair)

---

## Analytical Workflow

1. **Pathway Selection (User Input)**  
   The user selects a **metabolic pathway** from an interactive dropdown menu.  
   - Internally, this corresponds to choosing one `pathname` value.

2. **Dynamic Filtering**  
   - The KEGG results table `KEGG_Results.xlsx or KEGG_Results.csv` is loaded.  
   - The dataset is filtered to retain only rows where:
     - `pathname` equals the selected pathway, and  
     - `sample` and `ko` are valid and non-missing.

3. **Aggregation of KO Richness per Sample**  
   - The filtered data is grouped by `sample`.  
   - For each sample, the **number of distinct KO identifiers** is computed (e.g., via `nunique()` on `ko`).  
   - This count represents the **pathway-specific KO richness** of that sample.

4. **Sorting and Rendering**  
   - The resulting `(sample, unique_ko_count)` pairs are sorted in **descending** order of KO count.  
   - The aggregated data is rendered as a **vertical bar chart**, where:
     - the x-axis lists samples, and  
     - the y-axis encodes the unique KO count.  

   Optionally, numeric labels can be added on top of each bar to show the exact KO count.

---

## How to Read the Plot

- **Dropdown Menu (Pathway Selection)**  
  - Use the menu to select the **Metabolic Pathway** (`pathname`) of interest.  
  - The bar chart recomputes and updates automatically for the selected pathway.

- **X-axis (Samples)**  
  - Each tick on the x-axis corresponds to an individual **Sample** that has at least one KO annotated for the selected pathway.  
  - The set of samples displayed represents all entities contributing at least partially to that pathway.

- **Y-axis (KO Richness)**  
  - The y-axis represents the **count of unique KOs** associated with the selected pathway for each sample.  
  - Higher values reflect more extensive KO coverage and, by proxy, potentially more complete or complex functional capacity for that pathway.

- **Bars (Height and Optional Labels)**  
  - The **height** of each bar is proportional to the number of unique KOs that sample contributes to the selected pathway.  
  - Optional labels on each bar can display the exact KO count, making it easier to compare samples quantitatively.

---

## Interpretation and Key Messages

- **Pathway Richness and Functional Completeness**  
  - **Taller bars** may indicate samples with higher pathway-specific KO richness.  
  - These samples could be **candidates for near-complete or complex execution** of that pathway, especially when they approach the pathway's total KO universe (as quantified in UC-8.x completeness scorecards).

- **Identifying Functional Specialists**  
  - For a pathway of interest (e.g., a specific xenobiotic or hydrocarbon degradation pathway), the top-ranked samples in this chart could be considered **functional specialists** for that pathway.  
  - Such samples may be natural starting points for targeted bioremediation strategies focused on that particular metabolic function.

- **Comparative Functional Genomics Across Pathways**  
  - By cycling through different `pathname` values in the dropdown, users can see **how the ranking of samples changes** from one pathway to another:  
    - A sample that is highly ranked for several degradation pathways could be a **versatile generalist**,  
    - whereas a sample that ranks highly only for one or two pathways may be a **niche specialist**.

- **Link to Higher-Level Design**  
  - This visualization can complement pathway completeness matrices (e.g., UC-8.5) and KO-based UpSet analyses by providing a straightforward **per-pathway ranking** of candidate samples.  
  - It may be particularly useful for filtering and prioritizing samples before proceeding to more complex consortium-level modeling.

---

## Reproducibility and Assumptions

- **Input Format**  
  The analysis requires a semicolon-delimited KEGG results table containing at least:
  - `sample`,  
  - `pathname`,  
  - `ko`.

- **Definition of Richness**  
  - Pathway "richness" for a sample is defined as the **count of unique KO identifiers** mapped to the selected pathway for that sample.  
  - Duplicate `(sample, pathname, ko)` entries in the raw data are collapsed so that each KO is counted **once per sample per pathway**.

- **Scope of Inference**  
  - The metric captures **genetic potential** (KO presence), not expression, regulation, or flux.  
  - A high KO count suggests a rich repertoire, but does not alone guarantee full pathway function under specific environmental conditions.

- **Comparability Across Pathways**  
  - KO counts are not normalized by the total possible KOs in each pathway in this use case; they should therefore be interpreted **within a pathway** (comparing samples to each other) rather than directly across very different pathways.  
  - For normalized comparisons across pathways, the pathway completeness scorecards (e.g., UC-8.5) provide a complementary view.
