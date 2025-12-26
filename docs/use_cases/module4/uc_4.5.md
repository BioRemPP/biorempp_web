# UC-4.5 — Gene Presence Map by Metabolic Pathway

**Module:** 4 – Functional and Genetic Profiling  
**Visualization type:** Interactive dot (scatter) matrix (gene-by-sample presence for a selected pathway)  
**Primary inputs:** `KEGG_Results.xlsx or KEGG_Results.csv` (sample–gene–KO–pathway associations)  
**Primary outputs:** Gene presence/absence map across samples for a selected KEGG pathway

---

## Scientific Question and Rationale

**Question:** For a given metabolic pathway, which specific genes are present in which samples, and how do these patterns distinguish core from accessory genetic components across the consortium?

This use case focuses on a **gene-level view** of a single KEGG pathway across all samples, treating the pathway as a functional unit and asking:

- which genes may be broadly conserved (**core genes**) across many or all samples, and  
- which genes are restricted to a few samples (**accessory genes**), potentially encoding niche specializations.

By mapping **gene symbols vs. samples** as a presence/absence dot matrix, the visualization can provide a high-resolution overview of **pathway completeness and variability** at the genetic level, directly supporting comparative and consortium-oriented analyses.

---

## Data and Inputs

- **Primary data source:** `KEGG_Results.xlsx or KEGG_Results.csv` (semicolon-delimited)  
- **Key columns:**
  - `sample` – identifier for each biological sample  
  - `pathname` – KEGG pathway name or identifier  
  - `genesymbol` – gene symbol associated with the KO(s) for that pathway  
  - `ko` – KEGG Orthology identifier(s) linked to the gene and pathway

- **User control:**
  - A **dropdown menu** to select a single **Metabolic Pathway** (`pathname`) for inspection.

- **Output structure:**
  - **X-axis:** samples  
  - **Y-axis:** gene symbols associated with the selected pathway  
  - **Dots:** presence of a given gene in a given sample for that pathway, optionally with KO-based summaries in hover

---

## Analytical Workflow

1. **Pathway Selection (User Input)**  
   The user selects a **metabolic pathway** (`pathname`) from an interactive dropdown menu.  
   - All subsequent computations are restricted to this selected pathway.

2. **Dynamic Filtering**  
   - The KEGG results table `KEGG_Results.xlsx or KEGG_Results.csv` is loaded.  
   - The dataset is filtered to retain only rows where:
     - `pathname` equals the selected pathway, and  
     - `sample`, `genesymbol`, and `ko` are valid and non-missing.

3. **Extraction of Sample–Gene Pairs**  
   - From the filtered data, the script derives the set of **unique (`sample`, `genesymbol`) pairs**, representing **presence** of that gene in that sample for the selected pathway.  
   - Optionally, for each pair, a **summary count of distinct KOs** can be calculated to enrich hover information.

4. **Rendering as Gene Presence Map**  
   - A dot (scatter) matrix is constructed where:
     - the **X-axis** lists samples  
     - the **Y-axis** lists gene symbols associated with the pathway  
     - each **point** indicates that the corresponding sample encodes that gene in the context of the selected pathway  
   - Points may carry additional hover metadata (e.g., number of distinct KOs per sample–gene pair).

---

## How to Read the Plot

- **Dropdown Menu (Pathway Selection)**  
  - Use the menu to choose the **Metabolic Pathway** of interest.  
  - The gene–sample matrix updates automatically for the selected pathway.

- **Y-axis – Gene Symbols**  
  - Each horizontal row corresponds to a **Gene Symbol** associated with the selected pathway.  
  - The set of rows collectively defines the gene inventory for that pathway in the dataset.

- **X-axis – Samples**  
  - Each vertical column represents a **Sample**.  
  - All samples that encode at least one gene for the selected pathway are shown.

- **Dots (Presence Events)**  
  - A dot at the intersection of a gene row and a sample column indicates that the sample encodes that **gene** for the selected pathway.  
  - **Hover information** can include:
    - sample identifier  
    - gene symbol  
    - number of distinct KOs mapped to that gene in that sample for this pathway

---

## Interpretation and Key Messages

- **Core vs. Accessory Genes**  
  - Genes forming **nearly continuous horizontal rows** of dots across many samples could be interpreted as **core genes** for that pathway in this consortium—likely essential steps or structural components of the metabolic route.  
  - Genes with only a few dots (restricted to one or a small subset of samples) may behave as **accessory genes**, highlighting specialized or strain-specific functions.

- **Pathway Completeness per Sample**  
  - The **vertical density of dots** in a given sample column may reflect how completely the pathway is represented in that sample.  
  - Columns with many genes present may indicate higher **pathway completeness** (more steps potentially encoded), while sparse columns could suggest partial or truncated pathways.

- **Comparative Genomics at Pathway Scale**  
  - By inspecting patterns of shared and unique gene presence, one can:
    - identify **redundant** samples with very similar gene sets  
    - recognize **complementary** samples whose gene inventories cover different parts of the pathway, and  
    - detect **keystone samples** that carry rare but functionally critical genes

- **Consortium Design Implications**  
  - Combining samples that together cover **all (or most) genes** in the pathway can support **pathway-complete consortia**.  
  - Accessory genes restricted to certain samples may indicate **bottlenecks** or **specialized steps** that require those specific samples to be included in any consortium design.

---

## Reproducibility and Assumptions

- **Input Format**  
  The analysis requires a semicolon-delimited table with at least:
  - `sample`,  
  - `pathname`,  
  - `genesymbol`,  
  - `ko`.

- **Definition of Presence**  
  - A gene is considered **present** in a sample for the selected pathway if there is at least one row in the filtered data linking that `sample`, `genesymbol`, and `pathname` via one or more `ko` identifiers.  


- **Scope and Limitations**  
  - The visualization captures **structural genetic potential**, not expression or regulation.  
  - The set of genes and KOs is determined entirely by the input file; it does not incorporate external knowledge about canonical pathway completeness beyond what is represented in the dataset.


 
---

## Activity diagram of the use case

*Click on the image to enlarge and explore details.*

<a class="glightbox" href="../uc_4.5.png">
  <img src="../uc_4.5.png" alt="Activity diagram of the use case">
</a>



 