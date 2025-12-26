# UC-4.9 — Profiling of Sample Enzymatic Activity

**Module:** 4 – Functional and Genetic Profiling  
**Visualization type:** Interactive bar chart (enzyme activity vs. gene diversity)  
**Primary inputs:** `BioRemPP_Results.xlsx or BioRemPP_Results.csv` (sample–enzyme–gene associations)  
**Primary outputs:** Ranked enzymatic activity profile per sample

---

## Scientific Question and Rationale

**Question:** For any given sample, which enzymatic functions are the most prominent, as measured by the diversity of unique genes associated with them?

The same high-level enzymatic activity (e.g., *oxidoreductase*, *hydrolase*) can be implemented by many distinct genes. Quantifying **how many unique genes support each enzymatic function** can provide a proxy for:

- how strongly a sample invests in that activity, and  
- which catalytic functions are likely central to its bioremediation potential.


---

## Data and Inputs

- **Primary data source:** `BioRemPP_Results.xlsx or BioRemPP_Results.csv` (semicolon-delimited)

- **Key columns:**
  - `sample` – identifier for each biological sample  
  - `enzyme_activity` – functional label for enzymatic activity (e.g., *oxidoreductase*, *transferase*)  
  - `genesymbol` – gene symbols mapped to that enzymatic activity in a given sample

- **User control:**
  - **Dropdown – Sample:** all unique `sample` identifiers available in the dataset.

- **Output structure:**
  - **X-axis:** enzymatic activities (`enzyme_activity`)  
  - **Y-axis:** number of distinct `genesymbol` values per activity for the selected sample  
  - **Bars:** one bar per enzymatic activity, ranked by gene diversity

---

## Analytical Workflow

1. **User Selection**  
   - The user selects a **sample** from the interactive dropdown menu.  
   - This choice defines the focal organism or consortium for profiling.

2. **Dynamic Filtering**  
   - The `BioRemPP_Results.xlsx or BioRemPP_Results.csv` table is filtered to retain only rows matching the selected `sample`.  
   - Rows with missing `enzyme_activity` or `genesymbol` are discarded to ensure valid associations.

3. **Aggregation**  
   - The filtered data is grouped by `enzyme_activity`.  
   - For each enzymatic activity, the number of **distinct gene symbols** is computed (e.g., using `nunique()` on `genesymbol`).  
   - The result is a summary table:
     - one row per `enzyme_activity`,  
     - one value: `unique_gene_count`.

4. **Sorting and Rendering**  
   - Enzymatic activities are sorted in **descending order** of `unique_gene_count`.  
   - A bar chart is rendered:
     - **X-axis:** `enzyme_activity`,  
     - **Y-axis:** `unique_gene_count`,  
     - bars labelled with their exact counts for clarity.

---

## How to Read the Plot

- **Dropdown Menu – Sample Selection**  
  - Choose a **Sample** to analyze.  
  - The bar chart updates to show the enzymatic activity profile for that specific sample.

- **X-axis – Enzymatic Activities**  
  - Each tick corresponds to a distinct `enzyme_activity` annotated in the selected sample.  
  - Examples might include *hydrolase*, *monooxygenase*, *transferase*, *oxidoreductase*, etc.

- **Y-axis – Gene Diversity per Activity**  
  - The vertical value for each bar is the **count of unique genes** (`genesymbol`) mapped to that activity in the chosen sample.

- **Bars – Genetic Support for Each Activity**  
  - The **height** and **numeric label** of each bar indicate how many distinct genes support that activity.  
  - Taller bars represent enzymatic functions backed by a more diverse gene set.

---

## Interpretation and Key Messages

- **Genetic Investment in Enzymatic Functions**  
  - Enzymatic activities with **tall bars** may represent functions with substantial **genetic investment**:
    - many different genes can carry out or modulate that activity.

- **Functional Specialization**  
  - A profile dominated by a small set of activities (e.g., many genes in *oxidoreductase* and *monooxygenase*) may indicate **specialization**.

- **Metabolic Breadth vs. Depth**  
  - A wide spread of activities with moderate gene counts may suggest **broad metabolic breadth**.  
  - A few activities with very high gene counts may indicate **depth** in those specific functions (strong redundancy and flexibility within that functional class).

- **Comparative Profiling Across Samples**  
  - By switching the selected sample:
    - one can compare **which activities dominate** in different organisms  
    - identify complementary profiles (e.g., one sample rich in hydrolases, another rich in monooxygenases), and  
    - design consortia that combine distinct enzymatic strengths

---

## Reproducibility and Assumptions

- **Input Format**  
  The analysis requires a semicolon-delimited table with at least:
  - `sample`,  
  - `enzyme_activity`,  
  - `genesymbol`.

- **Presence and Counting Rules**  
  - Each bar's value is the **number of unique gene symbols** associated with that activity **for the selected sample**.  
  - Multiple occurrences of the same `(sample, enzyme_activity, genesymbol)` combination do **not** increase the count; they are treated as a single gene providing that activity.

- **Scope and Limitations**  
  - The chart reflects **annotated enzymatic potential**, not measured expression or activity levels.  
  - `enzyme_activity` labels depend on upstream annotation pipelines; misannotations or incomplete mappings will affect the profile.


 
---

## Activity diagram of the use case

*Click on the image to enlarge and explore details.*

<a class="glightbox" href="../uc_4.9.png">
  <img src="../uc_4.9.png" alt="Activity diagram of the use case">
</a>



 