# UC-6.3 — Chemical Hierarchy

**Module:** 6 – Hierarchical and Flow-based Functional Analysis  
**Visualization type:** Treemap (three-level hierarchical composition)  
**Primary inputs:** BioRemPP results table with `compoundclass`, `compoundname`, `sample`, and `genesymbol`  
**Primary outputs:** Hierarchical partitioning of genetic diversity across classes → compounds → samples

---

## Scientific Question and Rationale

**Question:** Which chemical classes and specific compounds require the most diverse genetic toolkit for their degradation, and which samples are the primary contributors to this diversity?

This use case provides a **top-down, hierarchical view** of the **genetic investment in bioremediation**. It organizes the system into three levels—**chemical classes**, **individual compounds**, and **biological samples**—and quantifies for each branch how many **unique genes** are involved. The resulting treemap can expose which parts of chemical space may be **genetically demanding**, which compounds might require particularly **complex or varied enzymatic machinery**, and which samples contribute the most to this genetic diversity.

---

## Data and Inputs

- **Primary data source:** `BioRemPP_Results.xlsx or BioRemPP_Results.csv`  
- **Key columns:**
  - `compoundclass` – high-level chemical class or category  
  - `compoundname` – specific compound or pollutant name  
  - `sample` – identifier for each biological sample  
  - `genesymbol` – gene symbol or identifier associated with that sample–compound pair
- **Accepted format:** semicolon-delimited text table (`.txt` or `.csv`)

- **Hierarchical structure:**
  1. **Compound Class** (`compoundclass`)  
  2. **Compound Name** (`compoundname`)  
  3. **Sample** (`sample`)

---

## Analytical Workflow

1. **Data Loading**  
   The primary results table (`BioRemPP_Results.xlsx or BioRemPP_Results.csv`) is loaded from its semicolon-delimited format.

2. **Hierarchy Definition**  
   A three-level hierarchy is defined:
   - **Level 1:** `compoundclass`  
   - **Level 2:** `compoundname` (nested within each class)  
   - **Level 3:** `sample` (nested within each compound)

3. **Aggregation of Genetic Diversity**  
   The data is grouped by each unique `(compoundclass, compoundname, sample)` path:
   - for each group, the number of **distinct gene symbols** (`genesymbol`) is computed (e.g., via `nunique()`),  
   - this count represents the **genetic diversity** contributed by that sample to that specific compound within that class.

4. **Value Propagation for Treemap**  
   The unique gene counts at the lowest level (per sample) are used as the basic **values**:
   - higher-level values for `compoundname` and `compoundclass` nodes are obtained by summing the values of all nested nodes,  
   - this yields gene-diversity totals at each level.

5. **Rendering**  
   The aggregated data is rendered as an **interactive treemap**:
   - each rectangle represents a node in the hierarchy (class, compound, or sample),  
   - the **area** of the rectangle is proportional to its total unique gene count,  
   - **color** is also mapped to the unique gene count to reinforce the visual encoding.

---

## How to Read the Plot

- **Nested Rectangles (Hierarchy)**  
  The treemap uses nested rectangles to represent the hierarchy:
  - **Outer rectangles** represent **compound classes** (`compoundclass`),  
  - within each class, **inner rectangles** represent **compounds** (`compoundname`),  
  - within each compound, the smallest rectangles represent **samples** (`sample`).

- **Area (Values)**  
  The **area** of each rectangle is proportional to the **total unique gene count**:
  - for a **sample node**, area reflects the number of distinct genes that sample deploys against a given compound,  
  - for a **compound node**, area reflects the total unique genes involved in degrading that compound across all samples,  
  - for a **class node**, area reflects the sum of unique genes associated with all compounds and samples within that class.

- **Color Encoding**  
  Rectangle color also encodes the unique gene count:
  - brighter or warmer colors indicate **higher genetic diversity**,  
  - cooler colors indicate fewer unique genes.

- **Interactivity**  
  The interactive treemap allows:
  - clicking on a rectangle to **zoom in** and focus on a specific class, compound, or sample subset,  
  - hovering to display labels (class, compound, sample) and the associated **unique gene count**.

---

## Interpretation and Key Messages

- **Genetically Demanding Chemical Classes**  
  The largest and most intensely colored top-level rectangles may identify **compound classes** that:
  - require a broad and diverse genetic toolkit for their degradation,  
  - may represent chemically complex or environmentally challenging regions of chemical space.

- **Complex Compounds within Classes**  
  Within a given class, the largest **compound** rectangles may highlight:
  - specific pollutants that could require particularly high genetic diversity,  
  - candidates for focusing detailed pathway analysis or targeted bioremediation strategies.

- **Key Biological Contributors (Samples)**  
  At the lowest level, large **sample** rectangles may identify:
  - which samples contribute the greatest number of unique genes to the degradation of a particular compound,  
  - potential **elite contributors** to consortia designed to handle certain compounds or classes.

- **Comparative View across the System**  
  The treemap can provide a compact, comparative snapshot of:
  - where genetic resources may be most heavily invested,  
  - which parts of the chemical hierarchy are **broadly supported** vs. **sparsely covered**,  
  - and how different samples partition their genetic potential across chemical space.

---

## Reproducibility and Assumptions

- **Input Format**  
  The analysis assumes a semicolon-delimited table containing:
  - `compoundclass`, `compoundname`, `sample`, and `genesymbol`.

- **Value Definition**  
  - The fundamental value driving the visualization is the **count of unique gene symbols** within each `(compoundclass, compoundname, sample)` group.  
  - Higher-level values are derived by **summing** these counts across nested levels.

- **Interpretation Scope**  
  - Unique-gene count is used as a **proxy for genetic diversity and metabolic complexity**; it does not directly encode gene expression levels, kinetic parameters, or regulatory effects.  
  - The treemap is therefore best interpreted as a **structural and comparative map of genetic investment**, informing where more detailed functional or experimental analyses may be most impactful.


 
---

## Activity diagram of the use case

*Click on the image to enlarge and explore details.*

<a class="glightbox" href="../uc_6.3.png">
  <img src="../uc_6.3.png" alt="Activity diagram of the use case">
</a>


