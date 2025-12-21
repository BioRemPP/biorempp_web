# UC-4.7 — Gene–Compound Association Explorer

**Module:** 4 – Functional and Genetic Profiling  
**Visualization type:** Interactive scatter (gene–compound matrix with sample-level details via hover)  
**Primary inputs:** `BioRemPP_Results.xlsx or BioRemPP_Results.csv` (sample–compound–gene–KO associations)  
**Primary outputs:** Filterable map of gene–compound associations, with links back to contributing samples

---

## Scientific Question and Rationale

**Question:** What are the specific associations between individual genes and chemical compounds, and which samples mediate these interactions?

In the context of bioremediation, understanding **which genes act on which compounds**, and **in which samples these links occur**, is central for moving from high-level functional potential to mechanistic insight. This use case can provide an **exploratory query interface** over the BioRemPP interaction table, enabling users to interrogate:

- all genes associated with a given compound (compound-centric view),
- all compounds associated with a given gene (gene-centric view), and
- the subset of samples that realize a specific gene–compound link.

By exposing gene–compound associations at full resolution, UC-4.7 and UC-4.8 can support **hypothesis generation**, **candidate target validation**, and the identification of promising gene–compound pairs for downstream experimental work.

---

## Data and Inputs

- **Primary data source:** `BioRemPP_Results.xlsx or BioRemPP_Results.csv` (semicolon-delimited)  
- **Key columns:**
  - `sample` – identifier for each biological sample  
  - `compoundname` – individual chemical compound names  
  - `genesymbol` – gene symbols associated with the interaction  
  - `ko` – KEGG Orthology identifier(s) mapped to the gene in that context

- **User controls:**
  - **Dropdown – Compound Name:** `compoundname` (optional filter)  
  - **Dropdown – Gene Symbol:** `genesymbol` (optional filter)

- **Output structure:**
  - **X-axis:** gene symbols  
  - **Y-axis:** compound names  
  - **Points:** observed gene–compound associations, with hover metadata exposing the underlying samples and KOs

---

## Analytical Workflow

1. **Data Loading**  
   - The results table `BioRemPP_Results.xlsx or BioRemPP_Results.csv` is loaded from a semicolon-delimited text file.  
   - Only rows with non-missing `compoundname`, `genesymbol`, and `sample` are retained.

2. **Widget Initialization (Query Controls)**  
   - Two interactive dropdown menus are created and populated with:
     - all unique `compoundname` values, and  
     - all unique `genesymbol` values.  
   - Both menus support:
     - **no selection** (returns all values along that dimension), and  
     - selection of a **single compound** and/or a **single gene**.

3. **Conditional Data Filtering**  
   Based on the user's choices, the table is filtered as follows:
   - **Compound-only selection:**  
     - If only `compoundname` is selected, the data is filtered to all rows matching that compound, across all genes and samples.
   - **Gene-only selection:**  
     - If only `genesymbol` is selected, the data is filtered to all rows matching that gene, across all compounds and samples.
   - **Compound + gene selection:**  
     - If both are selected, the data is filtered to rows matching that exact `(compoundname, genesymbol)` pair.


4. **Association Extraction and Rendering**  
   - From the filtered table, unique combinations of:
     - `compoundname`,  
     - `genesymbol`,  
     - associated `sample` (and optionally `ko`),
     are extracted.  
   - A scatter-like matrix is rendered:
     - **X-axis:** `genesymbol`,  
     - **Y-axis:** `compoundname`,  
     - each point representing at least one observed association between that gene and compound.  

---

## How to Read the Plot

- **Dropdown Menus (Query Interface)**  
  - **Select Compound Name:** filters the visualization to interactions involving that compound.  
  - **Select Gene Symbol:** filters the visualization to interactions involving that gene.  
  - Selecting **both** returns only the intersection for that gene–compound pair.  
  - The scatter updates immediately after each change.

- **Y-axis – Compound Names**  
  - Each position on the vertical axis corresponds to a **Compound** (`compoundname`).  
  - Multiple points along that row indicate different genes associated with the same compound.

- **X-axis – Gene Symbols**  
  - Each position on the horizontal axis corresponds to a **Gene Symbol** (`genesymbol`).  
  - Multiple points along that column indicate different compounds associated with the same gene.

- **Points – Gene–Compound Associations**  
  - Each point at the intersection of a gene and a compound indicates that **at least one association** between them exists in the BioRemPP dataset.  


---

## Interpretation and Key Messages

- **Compound-Centric View (Substrate Perspective)**  
  - Selecting a single compound in the **Compound Name** dropdown may reveal its **genetic interaction profile**:
    - the complete set of genes that have been annotated as acting on, or associated with, that compound, across all samples.  


- **Gene-Centric View (Enzyme Perspective)**  
  - Selecting a single gene in the **Gene Symbol** dropdown may reveal its **chemical substrate profile**:
    - all compounds to which that gene has been linked in the dataset.  
  - This can help to identify:
    - **broad-specificity genes** associated with many compounds, and  
    - **narrow-specificity genes** with highly restricted substrate ranges.

- **Dual-Filter View (Targeted Hypothesis Testing)**  
  - Selecting both a gene and a compound tests a **specific mechanistic hypothesis**:
    - "Does this gene act on this compound in any of the samples?"  

- **Consortium-Level Insight**  
  - By exploring which key gene–compound associations, one can:
    - identify **keystone samples** carrying unique or rare associations  
    - detect **shared enzymatic strategies** across multiple samples, and  
    - design consortia that combine complementary gene–compound profiles

---

## Reproducibility and Assumptions

- **Input Format**  
  The analysis requires a semicolon-delimited table containing at least:
  - `sample`,  
  - `compoundname`,  
  - `genesymbol`,  
  - `ko`.

- **Association Definition**  
  - A gene–compound association is defined by the presence of **at least one row** in the BioRemPP results where the same `genesymbol` and `compoundname` co-occur.  
  - The visualization displays **presence/absence** of associations, not their frequency or expression level.

- **Scope and Limitations**  
  - The approach reflects **annotated potential**, not measured activity or kinetics.  
  - Multiple `ko` entries per `(sample, genesymbol, compoundname)` reflect additional functional detail but do not alter the presence of the point itself.

 