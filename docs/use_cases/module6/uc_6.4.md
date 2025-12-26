# UC-6.4 — Enzymatic Hierarchy

**Module:** 6 – Hierarchical and Flow-based Functional Analysis  
**Visualization type:** Treemap (three-level hierarchical composition)  
**Primary inputs:** BioRemPP results table with `enzyme_activity`, `compoundclass`, `genesymbol`, and `compoundname`  
**Primary outputs:** Hierarchical partitioning of substrate scope across enzyme activities → chemical classes → genes

---

## Scientific Question and Rationale

**Question:** Which enzymatic functions are the most versatile (i.e., act on the widest range of unique compounds), how is this versatility distributed across different chemical classes, and which specific genes are the primary drivers of these activities?

This use case provides a **top-down functional overview** of the **enzymatic landscape** involved in bioremediation. It organizes the system into three levels—**enzyme activities**, **compound classes**, and **genes**—and quantifies for each branch how many **unique compounds** are associated with it. The resulting treemap may highlight **broadly active enzymatic functions**, which chemical classes are their main targets, and which genes serve as **key contributors** to this substrate scope.

---

## Data and Inputs

- **Primary data source:** `BioRemPP_Results.xlsx or BioRemPP_Results.csv`  
- **Key columns:**
  - `enzyme_activity` – functional category/label of the enzymatic activity  
  - `compoundclass` – chemical class/category of the substrates  
  - `genesymbol` – gene symbol or identifier implementing that activity in at least one sample  
  - `compoundname` – specific compound name or identifier
- **Accepted format:** semicolon-delimited text table (`.txt` or `.csv`)

- **Hierarchical structure:**
  1. **Enzyme Activity** (`enzyme_activity`)  
  2. **Compound Class** (`compoundclass`)  
  3. **Gene Symbol** (`genesymbol`)

---

## Analytical Workflow

1. **Data Loading**  
   The primary results table (`BioRemPP_Results.xlsx or BioRemPP_Results.csv`) is loaded from its semicolon-delimited format.

2. **Hierarchy Definition**  
   A three-level hierarchy is defined:
   - **Level 1:** `enzyme_activity`  
   - **Level 2:** `compoundclass` (nested within each enzyme activity)  
   - **Level 3:** `genesymbol` (nested within each compound class)

3. **Aggregation of Substrate Scope**  
   The data is grouped by each unique `(enzyme_activity, compoundclass, genesymbol)` path:
   - for each group, the number of **distinct `compoundname`** entries is computed (e.g., via `nunique()`),  
   - this count represents the **substrate scope** (number of unique compounds) associated with that gene within that functional and chemical context.

4. **Value Propagation for Treemap**  
   The unique compound counts at the lowest level (per gene) are used as the basic **values**:
   - higher-level values for `compoundclass` and `enzyme_activity` nodes are obtained by **summing** the values of all nested nodes,  
   - this yields total substrate scope at each level of the hierarchy.

5. **Rendering**  
   The aggregated data is rendered as an **interactive treemap**:
   - each rectangle represents a node in the hierarchy (enzyme activity, compound class, gene),  
   - the **area** of the rectangle is proportional to its total unique compound count,  
   - **color** is also mapped to the unique compound count to reinforce the visual encoding.

---

## How to Read the Plot

- **Nested Rectangles (Hierarchy)**  
  The treemap uses nested rectangles to represent the hierarchy:
  - **Outer rectangles** represent **enzyme activities** (`enzyme_activity`),  
  - within each activity, **inner rectangles** represent **compound classes** (`compoundclass`),  
  - within each class, the smallest rectangles represent **genes** (`genesymbol`).

- **Area (Values)**  
  The **area** of each rectangle is proportional to the **total number of unique compounds**:
  - for a **gene node**, area reflects how many distinct compounds that gene is associated with under that activity–class context,  
  - for a **compound class node**, area reflects the sum of unique compounds handled by all genes and activities contributing to that class,  
  - for an **enzyme activity node**, area reflects the full substrate scope of that activity across classes and genes.

- **Color Encoding**  
  Rectangle color also encodes the unique compound count:
  - brighter or warmer colors indicate **broader substrate scope**,  
  - cooler colors indicate more limited sets of compounds.

- **Interactivity**  
  In the interactive view:
  - clicking on a rectangle **zooms in** to that part of the hierarchy,  
  - hovering displays labels (enzyme activity, compound class, gene) and their associated **unique compound counts**.

---

## Interpretation and Key Messages

- **Most Versatile Enzyme Functions**  
  The largest and most intensely colored top-level rectangles may identify **enzyme activities** with the **widest substrate scope**:
  - these could correspond to broad functional classes such as oxidoreductases, transferases, or hydrolases that participate in many different transformation reactions,  
  - they may represent **central functional pillars** of the bioremediation system.

- **Substrate Specificity within Activities**  
  Within a given enzyme activity, the largest **compound class** rectangles may reveal:
  - which chemical classes are the **primary targets** of that activity (e.g., whether a hydrolase class acts mainly on esters, amides, or other subclasses),  
  - how enzymatic versatility is distributed across chemical space.

- **Key Genetic Contributors (Genes)**  
  At the lowest level, large **gene** rectangles may identify **key genetic contributors**:
  - genes that are associated with many distinct compounds under a given activity–class context,  
  - potential **genes** whose broad substrate scope could be crucial for versatile bioremediation strategies.

- **System-Level Functional Architecture**  
  Taken together, the treemap can offer a **compact functional overview**:
  - it may show where enzymatic versatility is concentrated,  
  - how chemical classes partition across different activities,  
  - and which genes sit at the core of these functional architectures.

---

## Reproducibility and Assumptions

- **Input Format**  
  The analysis assumes a semicolon-delimited table containing:
  - `enzyme_activity`, `compoundclass`, `genesymbol`, and `compoundname`.

- **Value Definition**  
  - The fundamental value driving the visualization is the **count of unique compound names** per `(enzyme_activity, compoundclass, genesymbol)` group.  
  - Higher-level values are computed as **sums** of these counts across nested nodes.

- **Interpretation Scope**  
  - Unique-compound count is used as a **proxy for functional versatility or substrate scope**; it does not encode enzyme kinetics, expression levels, or in situ activity.  
  - The treemap should therefore be interpreted as a **structural and comparative map** of where enzymatic breadth is concentrated, guiding more detailed mechanistic or experimental studies rather than replacing them.


 
---

## Activity diagram of the use case

*Click on the image to enlarge and explore details.*

<a class="glightbox" href="../uc_6.4.png">
  <img src="../uc_6.4.png" alt="Activity diagram of the use case">
</a>


