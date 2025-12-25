# UC-4.8 —  Gene Inventory Explorer

**Module:** 4 – Functional and Genetic Profiling  
**Visualization type:** Interactive scatter (sample–gene matrix with contextual metadata via hover)  
**Primary inputs:** `BioRemPP_Results.xlsx or BioRemPP_Results.csv` (sample–gene–compound–KO associations)  
**Primary outputs:** Filterable map of gene presence across samples

---

## Scientific Question and Rationale

**Question:** What is the specific genetic inventory (`genesymbols`) of each sample, and which samples possess a particular gene of interest?

Understanding **which genes are present in which samples** is essential for assessing functional potential, detecting redundancy, and identifying unique capabilities.  

UC-4.8 can provide an **exploratory interface** to the gene-level composition of the system. It may enable users to:

- list all genes present in a given sample (sample-centric view),
- identify which samples carry a specific gene of interest (gene-centric view), and
- inspect the compounds and KOs associated with each sample–gene pair.

This use case can support **comparative genomics**, **candidate gene tracking**, and **hypothesis-driven exploration** of the BioRemPP dataset.

---

## Data and Inputs

- **Primary data source:** `BioRemPP_Results.xlsx or BioRemPP_Results.csv` (semicolon-delimited)  
- **Key columns:**
  - `sample` – identifier for each biological sample  
  - `genesymbol` – gene symbols detected and functionally annotated  
  - `compoundname` – compounds associated with that gene in a given sample  
  - `ko` – KEGG Orthology identifier(s) mapped to the gene in that context

- **User controls:**
  - **Dropdown – Sample:** all unique `sample` identifiers  
  - **Dropdown – Gene Symbol:** all unique `genesymbol` entries

- **Output structure:**
  - **Y-axis:** samples  
  - **X-axis:** gene symbols  
  - **Points:** confirmed presence of a given gene in a given sample, with hover metadata exposing associated compounds and KOs

---

## Analytical Workflow

1. **Data Loading**  
   - The BioRemPP results table `BioRemPP_Results.xlsx or BioRemPP_Results.csv` is loaded from a semicolon-delimited file.  
   - Rows with missing `sample` or `genesymbol` are discarded to ensure valid associations.

2. **Widget Initialization (Query Controls)**  
   - Two interactive dropdown menus are constructed and populated with:
     - all unique `sample` identifiers, and  
     - all unique `genesymbol` values.  
   - Each dropdown supports:
     - **no selection** (no filter on that dimension), and  
     - selection of a **single sample** or **single gene**.

3. **Conditional Data Filtering**  
   Depending on the user's choices, the dataset is filtered as follows:

   - **Sample-only selection:**  
     - If only a `sample` is selected, the table is filtered to rows matching that sample, returning all genes present in that sample.

   - **Gene-only selection:**  
     - If only a `genesymbol` is selected, the table is filtered to rows matching that gene, returning all samples that carry it.

   - **Sample + gene selection:**  
     - If both a `sample` and a `genesymbol` are selected, the table is filtered to the rows matching that exact pair.  
     - This confirms the presence of the gene in that sample and retrieves associated `compoundname` and `ko` information.

   - **No selection:**  
     - If neither filter is set, the full sample–gene association space is visualized (optionally restricted for performance, depending on implementation).

4. **Association Extraction and Rendering**  
   - From the filtered table, unique `(sample, genesymbol)` pairs are extracted, with their associated `compoundname` and `ko` carried as hover metadata.  
   - A scatter-like matrix is rendered where:
     - **Y-axis:** `sample`,  
     - **X-axis:** `genesymbol`,  
     - each point marks the presence of that gene in that sample.  

---

## How to Read the Plot

- **Dropdown Menus (Query Interface)**  
  - **Select Sample:** filters the visualization to genes present in that sample.  
  - **Select Gene Symbol:** filters the visualization to samples that carry that gene.  
  - Selecting **both** restricts the view to that specific sample–gene association.  

- **Y-axis – Samples**  
  - Each horizontal position corresponds to a **Sample**.  
  - Multiple points along that row indicate different genes present in that sample.

- **X-axis – Gene Symbols**  
  - Each vertical position corresponds to a **Gene Symbol**.  
  - Multiple points along that column indicate different samples that carry that gene.

- **Points – Sample–Gene Presence**  
  - A point at the intersection of a `sample` and a `genesymbol` signifies that the gene has been detected and functionally annotated in that sample.  


---

## Interpretation and Key Messages

- **Sample-Centric View (Genetic Inventory)**  
  - Selecting a **single sample** produces its **genetic inventory** within the BioRemPP dataset:
    - the complete set of annotated gene symbols present in that sample.  
  - This can help characterize:
    - the **functional potential** of that sample, and  
    - the breadth of its encoded metabolic capabilities.

- **Gene-Centric View (Distribution Across Samples)**  
  - Selecting a **single gene** produces its **distribution across samples**:
    - all samples where that gene is present.  
  - This can be useful for:
    - tracking **key functional genes** (e.g., markers of specific degradation pathways)  
    - identifying **widely distributed** vs. **rare** genes, and  
    - assessing possible functional redundancy across samples

- **Dual-Filter View (Targeted Queries)**  
  - Selecting both a **sample** and a **gene** confirms whether that gene is present in that sample and, via hover metadata, may reveal:
    - the compounds (`compoundname`) to which it has been linked, and  
    - the underlying KOs (`ko`).  
  - This can support **targeted hypothesis testing**, such as verifying whether a candidate sample carries a gene of interest for a particular bioremediation strategy.

- **Consortium Design and Comparative Genomics**  
  - By exploring patterns of shared and unique genes across samples, UC-4.8 can aid in:
    - identifying **shared functional cores** vs. **unique capabilities**  
    - selecting complementary samples for consortium design, and  
    - prioritizing samples that carry rare but functionally important genes

---

## Reproducibility and Assumptions

- **Input Format**  
  The analysis requires a semicolon-delimited table containing at least:
  - `sample`,  
  - `genesymbol`,  
  - `compoundname`,  
  - `ko`.

- **Presence Definition**  
  - A sample–gene association (a point in the plot) is defined by the existence of **at least one row** in the input table where that `sample` and `genesymbol` co-occur.  
  - The visualization captures **presence/absence**, not copy number, expression level, or interaction frequency.

- **Scope and Limitations**  
  - Results reflect **annotated genetic potential** derived from the BioRemPP workflow, not direct experimental measurements of gene expression or enzyme activity.  


 
---

## Activity diagram of the use case

![Activity diagram of the use case](uc_4.8.png)


 