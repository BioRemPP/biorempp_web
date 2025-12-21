# UC-4.11 —  Hierarchical View of Genetic Diversity in HADEG Pathways

**Module:** 4 – Functional and Genetic Profiling  
**Visualization type:** Sunburst chart (hierarchical gene diversity)  
**Primary inputs:** `HADEG_Results.xlsx or HADEG_Results.csv` (compound_pathway–pathway–gene associations)  
**Primary outputs:** Hierarchical map of genetic diversity across HADEG pathways

---

## Scientific Question and Rationale

**Question:** What is the overall hierarchical structure of genetic diversity within the HADEG dataset, and how is this diversity distributed among compound pathway classes and their specific metabolic routes?

**Compound pathway classes** (e.g., alkanes, aromatics) are often decomposed into more specific **metabolic pathways**, each implemented by multiple genes. Quantifying the **number of distinct genes** at each level of this hierarchy may reveal:

- which compound classes are genetically most complex or diversified, and  
- which specific pathways carry the largest **gene repertoires**, potentially suggesting high robustness, redundancy, or evolutionary importance.



---

## Data and Inputs

- **Primary data source:** `HADEG_Results.xlsx or HADEG_Results.csv` (semicolon-delimited)

- **Key columns:**
  - `compound_pathway` – broad degradation class (e.g., *Alkanes*, *Aromatics*)  
  - `Pathway` – specific metabolic pathway within that compound class  
  - `Gene` – gene identifier (or symbol) associated with that pathway

- **Pre-processing rules:**
  - Remove rows with missing `compound_pathway`, `Pathway`, or `Gene`  
  - Optionally standardize identifiers (trim whitespace, harmonize case) to avoid artificial duplicates

- **Output structure (hierarchy):**
  - Root node: **All Pathways**  
  - Inner ring: **compound_pathway**  
  - Outer ring: **Pathway** (children of each compound_pathway)  
  - Slice size: number of **unique genes**

---

## Analytical Workflow

1. **Data Loading**  
   - Import `HADEG_Results.xlsx or HADEG_Results.csv` as a semicolon-delimited table.  
   - Ensure that `compound_pathway`, `Pathway`, and `Gene` are correctly parsed as categorical/string fields.

2. **Aggregation of Genetic Diversity**  
   - Group the data by `(compound_pathway, Pathway)`.  
   - For each pair, compute the number of **distinct genes**:
     - `unique_gene_count = nunique(Gene)`  
   - This yields a summary table with:
     - `compound_pathway`, `Pathway`, `unique_gene_count`.

3. **Hierarchy Construction**  
   - Add a synthetic root node (e.g., `"All Pathways"`) to serve as the center of the sunburst.  
   - Define the hierarchical path as:
     - `["All Pathways" → compound_pathway → Pathway]`  
   - Associate `unique_gene_count` as the **value** used to size slices.

4. **Rendering the Sunburst**  
   - Render a sunburst chart where:
     - the **center** is `"All Pathways"`,  
     - the **first ring** corresponds to `compound_pathway`,  
     - the **second ring** corresponds to specific `Pathway` entries,  
     - the **slice size** and **color** encode `unique_gene_count`.

---

## How to Read the Plot

- **Concentric Rings (Hierarchy)**  
  - **Center:** `"All Pathways"` – total genetic diversity in the HADEG dataset.  
  - **Inner ring:** individual **compound_pathways**.  
  - **Outer ring:** specific **Pathways** belonging to each compound_pathway.

- **Slice Size (`values`)**  
  - The **angular width** of each slice is proportional to its **unique gene count**.  
  - Larger slices = more distinct genes contributing to that class or pathway.

- **Color Encoding**  
  - Slice color also reflects `unique_gene_count`, typically with brighter/warmer colors representing higher gene diversity.  
  - The color scale provides a quick visual cue to locate the most complex regions.

- **Interactivity**  
  - Clicking a slice "zooms in" on that branch:
    - focusing on one compound_pathway and its constituent pathways,  
    - or further isolating a single pathway to see its relative contribution.

---

## Interpretation and Key Messages

- **Dominant Compound Classes**  
  - In the **inner ring**, the largest and brightest slices may mark the compound_pathways (e.g., *Aromatics*, *Alkanes*) that carry the highest **total genetic diversity**.  
  - These classes could represent **major targets** in hydrocarbon or pollutant degradation.

- **Key Metabolic Pathways**  
  - In the **outer ring**, large slices may reveal specific pathways that are especially gene-rich, possibly indicating:
    - complex multi-step transformations  
    - substantial redundancy (multiple genes for similar roles), or  
    - strong historical selection pressure

- **Hierarchical Structure of Complexity**  
  - The sunburst can support a **top-down exploration**:
    - start at compound classes to identify which broad chemistries dominate the functional landscape  
    - then inspect their child pathways to see how this diversity is partitioned

- **Prioritization for Curation or Experimental Work**  
  - Gene-rich pathways could be:
    - good candidates for **deeper curation** or mechanistic modeling  
    - potential targets for **synthetic pathway reconstruction**  
    - areas where additional **sample-level analyses** (from other UCs) could be most informative

---

## Reproducibility and Assumptions

- **Input Format Requirements**  
  - The analysis assumes a semicolon-delimited HADEG results file with at least:
    - `compound_pathway`,  
    - `Pathway`,  
    - `Gene`.

- **Counting Rules**  
  - **Genetic diversity** is defined as the **number of unique genes** associated with each `(compound_pathway, Pathway)` pair.  
  - Multiple rows for the same gene in the same pathway do **not** increase the count.

- **Hierarchical Aggregation**  
  - The value for a **parent slice** (e.g., a compound_pathway) is the sum of the unique gene counts of its **child pathways**.  
  - The root `"All Pathways"` represents the sum over all pathways in the input file.

- **Scope and Limitations**  
  - The sunburst reflects **annotated gene diversity in HADEG**, not pathway expression, flux, or kinetic capacity.  
  - Any biases in HADEG curation or gene labeling (e.g., synonyms not merged) will directly influence slice sizes.

 