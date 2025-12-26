# UC-4.13 — Genetic Profile by Compound Class

**Module:** 4 – Functional and Genetic Profiling  
**Visualization type:** Heatmap (Genes × Samples)  
**Primary inputs:** `HADEG_Results.xlsx or HADEG_Results.csv` (sample–KO–Gene–compound_pathway)  
**Primary outputs:** Gene-level functional richness matrix per compound pathway

---

## Scientific Question and Rationale

**Question:** For a given class of degradation pathways (e.g., *Alkanes*), which genes are present in which samples, and how diverse is their KO annotation?

The same **compound pathway** can be implemented through different **genetic strategies** across samples. By quantifying, for each gene and sample, how many distinct KOs are associated with that gene, UC-4.13 may reveal:

- which **genes** act as core players within a pathway  
- which **samples** are genetically best equipped for that compound class, and  
- how **functional diversity** (KO richness) is distributed across the consortium

---

## Data and Inputs

- **Primary data source:** `HADEG_Results.xlsx or HADEG_Results.csv` (semicolon-delimited)

- **Key columns:**
  - `sample` – identifier of the analyzed biological sample  
  - `Gene` – gene identifier used in the HADEG mapping  
  - `ko` – KEGG Orthology identifier linked to the gene  
  - `compound_pathway` – broader degradation pathway / compound class (e.g., *Alkanes*, *Aromatics*)

- **Pre-processing rules:**
  - Discard rows with missing `sample`, `Gene`, `ko`, or `compound_pathway`  
  - Optionally standardize string fields (trim, case normalization) to avoid artificial duplicates

- **Output structure:**
  - 2D matrix for a **selected compound_pathway**:
    - Rows: `Gene`  
    - Columns: `sample`  
    - Cell value: count of **unique KOs** per gene–sample pair

---

## Analytical Workflow

1. **User Selection**  
   - The user selects a target `compound_pathway` (e.g., *Alkanes*, *Aromatics*) from an interactive dropdown menu.  
   - All downstream computations are scoped to this selected compound class.

2. **Dynamic Filtering**  
   - Filter `HADEG_Results.xlsx or HADEG_Results.csv` to retain only rows where:
     - `compound_pathway == selected_compound_pathway`.  
   - Ensure `sample`, `Gene`, and `ko` are valid (non-missing, non-placeholder).

3. **Aggregation and Functional Richness Calculation**  
   - Group the filtered data by `(Gene, sample)`.  
   - For each pair, compute:
     - `unique_ko_count = nunique(ko)`  
   - This yields a table summarizing, for the chosen compound_pathway, the **KO diversity** associated with each gene in each sample.

4. **Matrix Construction**  
   - Pivot the aggregated table into a 2D matrix:
     - **Rows:** `Gene`,  
     - **Columns:** `sample`,  
     - **Values:** `unique_ko_count` (fill missing combinations with 0).

5. **Rendering the Heatmap**  
   - Render the matrix as an interactive heatmap where:
     - each cell's **color intensity** encodes the KO count for that gene–sample pair  
     - optional annotations can display the numeric KO counts  
     - hover tooltips expose `Gene`, `sample`, and `unique_ko_count`

---

## How to Read the Plot

- **Dropdown Menu (Compound Pathway Selector)**  
  - Select the **Compound Pathway** of interest.  
  - The heatmap recomputes for the chosen pathway, showing only the relevant genes and samples.

- **Y-axis (Rows)**  
  - Each row corresponds to a **Gene** associated with the selected compound_pathway.  
  - Rows can be ordered alphabetically or by total KO richness across samples.

- **X-axis (Columns)**  
  - Each column represents a **Sample** in the dataset.  
  - Columns can be ordered by overall KO richness or kept in a fixed order.

- **Cell Color (Heat Intensity)**  
  - The color of each cell indicates the **count of unique KOs** annotated for that Gene in that Sample within the selected compound_pathway.  
  - Darker/warmer cells indicate higher functional richness for that gene–sample pair.


---

## Interpretation and Key Messages

- **Functional Hotspots**  
  - Brightly colored cells ("hotspots") may identify **gene–sample combinations** with high KO diversity.  
  - These hotspots could suggest genes that play a **central or complex role** in degrading the selected compound class within a specific sample.

- **Key Genetic Players (Core Genes)**  
  - Rows with consistently high values across many samples may point to **core genes**.

- **Sample Specialization**  
  - Columns with many bright cells may highlight **samples that are strongly equipped** for the selected compound_pathway.  
  - Such samples could be interpreted as **functional specialists** for that chemical class.

- **Consortium-Level Strategies**  
  - Comparing patterns of hotspots across samples may reveal:
    - whether multiple samples share similar genetic strategies (redundancy), or  
    - whether different samples contribute different sets of high-diversity genes (complementarity).  
  - This can be directly useful for designing **multi-sample consortia** where genes (and associated KOs) are distributed across different members.

---

## Reproducibility and Assumptions

- **Input Format Requirements**  
  - The analysis assumes a semicolon-delimited HADEG results file containing:
    - `sample`,  
    - `ko`,  
    - `Gene`,  
    - `compound_pathway`.

- **Counting Rules**  
  - **Functional richness** is defined as the number of **unique KOs** per `(Gene, sample)` for the selected compound_pathway.  
  - Multiple rows involving the same `ko` for the same `(Gene, sample)` pair do **not** increase the count.

- **Scope and Limitations**  
  - The heatmap quantifies **annotated genetic potential**, not expression levels or in situ activity.  
  - Observed patterns depend on the completeness and curation of the HADEG mapping and KO annotations.


 
---

## Activity diagram of the use case

*Click on the image to enlarge and explore details.*

<a class="glightbox" href="../uc_4.13.png">
  <img src="../uc_4.13.png" alt="Activity diagram of the use case">
</a>



 