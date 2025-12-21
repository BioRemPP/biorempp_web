# UC-4.12 —  Pathway Funcional Map by Sample

**Module:** 4 – Functional and Genetic Profiling  
**Visualization type:** Heatmap (2D pathway vs. compound class)  
**Primary inputs:** `HADEG_Results.xlsx or HADEG_Results.csv` (sample–KO–Pathway–compound_pathway)  
**Primary outputs:** Sample-specific matrix of functional richness per Pathway × compound_pathway

---

## Scientific Question and Rationale

**Question:** For a given sample, how are its specific metabolic pathways (`Pathway`) functionally distributed across the broader chemical families (`compound_pathway`) they address?

A single sample can simultaneously encode pathways for multiple **compound classes** (e.g., alkanes, aromatics, chlorinated compounds). Quantifying the **unique KO diversity** at each intersection of `Pathway` and `compound_pathway` may reveal:

- which specific pathways are major contributors within each chemical class, and  
- how a sample's metabolic capacity is structurally organized across different pollutant families.


---

## Data and Inputs

- **Primary data source:** `HADEG_Results.xlsx or HADEG_Results.csv` (semicolon-delimited)

- **Key columns:**
  - `sample` – identifier of the analyzed biological sample  
  - `ko` – KEGG Orthology identifier associated with HADEG  
  - `Pathway` – specific HADEG/KEGG-like metabolic pathway  
  - `compound_pathway` – broader compound class (e.g., *Aromatics*, *Alkanes*)

- **Pre-processing rules:**
  - Remove rows with missing `sample`, `ko`, `Pathway`, or `compound_pathway`  
  - Optionally standardize string fields (trim, harmonize case) to avoid spurious duplicates

- **Output structure:**
  - 2D matrix for a **single selected sample**:  
    - Rows: specific `Pathway`  
    - Columns: `compound_pathway`  
    - Cell value: count of **unique KOs**

---

## Analytical Workflow

1. **User Selection**  
   - The user selects a target `sample` from an interactive dropdown menu.  
   - All subsequent steps are recomputed dynamically for this selected sample.

2. **Dynamic Filtering**  
   - Filter `HADEG_Results.xlsx or HADEG_Results.csv` to retain only rows where:
     - `sample == selected_sample`.  
   - Ensure that `Pathway`, `compound_pathway`, and `ko` are present and valid.

3. **Aggregation of Functional Richness**  
   - Group the filtered data by `(Pathway, compound_pathway)`.  
   - For each pair, compute:
     - `unique_ko_count = nunique(ko)`  
   - This yields a table summarizing the **KO diversity** for each Pathway within each compound class, for the selected sample.

4. **Matrix Construction**  
   - Pivot the aggregated table into a 2D matrix:
     - **Rows:** `Pathway`,  
     - **Columns:** `compound_pathway`,  
     - **Values:** `unique_ko_count` (fill missing combinations with 0).

5. **Rendering the Heatmap**  
   - Render the matrix as an interactive heatmap where:
     - each cell's **color intensity** encodes the KO count  
     - optional annotations can display the numeric values  
     - tooltips can expose the exact `(Pathway, compound_pathway, KO count)` triplet

---

## How to Read the Plot

- **Dropdown Menu (Sample Selector)**  
  - Select a **Sample** to analyze.  
  - The heatmap recomputes in real time for the chosen sample.

- **Y-axis (Rows)**  
  - Each row represents a specific **Pathway** present in the selected sample.  

- **X-axis (Columns)**  
  - Each column corresponds to a broader **compound_pathway** (compound class).  
  - Together, columns define the chemical "domains" where the sample is active.

- **Cell Color (Heat Intensity)**  
  - The color of each cell encodes the **count of unique KOs** at that Pathway × compound_pathway intersection.  
  - Darker/warmer colors indicate higher functional richness (more distinct KOs).

---

## Interpretation and Key Messages

- **Functional Hotspots**  
  - Cells with intense color ("hotspots") may highlight **pathways with high KO diversity** within a given compound class.  
  - These could represent **major functional modules** that the sample deploys against a particular chemical family.

- **Sample's Metabolic Strategy**  
  - The pattern of hotspots across columns may reveal the sample's **preferred chemical domains**:
    - concentration of hotspots in one column (e.g., "Aromatics") may suggest **specialization**  
    - a more balanced spread across many columns could suggest a **broad-spectrum degrader**

- **Pathway-Level Importance**  
  - Rows with consistently high values across multiple compound classes may indicate **multi-context pathways** that contribute to several degradation strategies.  
  - Conversely, pathways with a single strong cell could be **highly specific** to one compound class.

- **Comparative Profiling Across Samples**  
  - By switching samples in the dropdown, one can:
    - compare **which chemical classes** each sample is best suited for  
    - identify candidates with complementary hotspot patterns  
    - support **consortium design** by combining samples whose heatmaps occupy different sectors of the matrix

---

## Reproducibility and Assumptions

- **Input Format Requirements**  
  - The analysis assumes a semicolon-delimited HADEG results file containing:
    - `sample`,  
    - `ko`,  
    - `Pathway`,  
    - `compound_pathway`.

- **Counting Rules**  
  - **Functional richness** is defined as the number of **unique KOs** per `(Pathway, compound_pathway)` for the selected sample.  
  - Multiple rows with the same KO in the same intersection do **not** increase the count.

- **Scope and Limitations**  
  - The heatmap describes **genetic potential**, not pathway expression or activity.  
  - Differences in annotation depth or KO mapping across pathways or compound classes may influence the observed counts.

 