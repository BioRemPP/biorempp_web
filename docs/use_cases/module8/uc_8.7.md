# UC-8.7 — Sample-Sample KO Intersection Profile

**Module:** 8 – Assembly of Functional Consortia  
**Visualization type:** Interactive UpSet plot (KO set intersections across user-selected samples)  
**Primary inputs:** `BioRemPP_Results.xlsx or BioRemPP_Results.csv` (sample–KO associations)  
**Primary outputs:** Intersection statistics for KEGG Orthology (KO) sets across selected samples

---

## Scientific Question and Rationale

**Question:** How many orthologous genes (KOs) are shared across the selected samples, and which samples exhibit unique or highly specific genetic inventories?

The goal is to quantify and visualize how KEGG Orthology (KO) identifiers are distributed across samples, potentially identifying:

- a **core KO repertoire** shared by many or all samples, and  
- **unique or rare KOs** that may define specialized, niche capabilities.

Instead of relying on Venn diagrams—which become unreadable as the number of sets increases—the analysis employs an **UpSet plot**, a scalable approach that enumerates and ranks all relevant set intersections. This can provide a rigorous foundation for reasoning about **functional redundancy**, **complementarity**, and potential **functional guilds** within the collection of samples.

---

## Data and Inputs

- **Primary data source:** `BioRemPP_Results.xlsx or BioRemPP_Results.csv` (semicolon-delimited)  
- **Key columns:**
  - `sample` – identifier for each biological sample  
  - `ko` – KEGG Orthology (KO) identifier associated with that sample  

- **Set definition:**
  - **Sets:** Individual `sample`s (each represented by its KO repertoire)  
  - **Elements:** Unique **KO identifiers** (`ko`) observed in the selected subset of samples  

- **User control:**
  - A **multi-select dropdown** allowing selection of **two or more samples** to include in the intersection analysis.

---

## Analytical Workflow

1. **Sample Selection (User Input)**  
   The user selects **two or more samples** from a multi-select dropdown control.  
   - A minimum of two samples is required to generate meaningful intersections.  
   - The downstream analysis is dynamically restricted to this subset.

2. **Data Loading and Filtering**  
   - The results table `BioRemPP_Results.xlsx or BioRemPP_Results.csv` is loaded.  
   - The dataset is filtered to retain only rows whose `sample` appears in the user's selection and for which both `sample` and `ko` are valid and non-missing.

3. **Set Construction (Per-Sample KO Repertoires)**  
   - The filtered data is grouped by `sample`.  
   - For each `sample`, a **set of unique KOs** is constructed.  
   - These sets encode the **functional inventories** (KO repertoires) of the selected samples.

4. **Intersection Computation and Ranking**  
   - From the per-sample KO sets, all relevant **set intersections** are computed.  
   - For each intersection (i.e., a specific combination of samples), the **intersection size** (number of shared KOs) is calculated.  
   - Intersections are ranked by **cardinality**, so the most informative overlaps appear prominently in the UpSet plot.

5. **Rendering as UpSet Plot**  
   The processed set and intersection statistics are rendered as an **UpSet plot**, comprising:
   - a **set size bar chart** (left),  
   - an **intersection matrix** (bottom), and  
   - an **intersection size bar chart** (top).

---

## How to Read the Plot

- **Sample Multi-Select Dropdown**  
  - Use the dropdown to choose **two or more samples** for analysis.  
  - The UpSet plot recomputes and updates automatically whenever the selection changes.

- **Set Size (Left Bar Chart)**  
  - Each horizontal bar corresponds to a **single sample**.  
  - Bar length indicates the **total number of unique KOs** present in that sample.  
  - Taller bars represent samples with higher KO richness, suggestive of broader metabolic potential.

- **Intersection Matrix (Bottom Panel)**  
  - Each **row** corresponds to one of the selected samples.  
  - Each **column** corresponds to one intersection pattern (a particular combination of samples).  
  - **Dots** indicate membership: a dot in a row means that sample is part of that intersection.  
  - A **vertical line connecting dots** in multiple rows indicates that the bar above represents KOs shared **only** by those specific samples.  
  - A column with a **single dot and no connections** represents KOs **unique** to that sample.

- **Intersection Size (Top Bar Chart)**  
  - Each vertical bar directly above a column in the matrix represents the **number of KOs** in that specific intersection.  
  - Taller bars correspond to **larger shared KO sets**, highlighting prominent patterns of gene sharing or uniqueness.

---

## Interpretation and Key Messages

- **Core Functional Repertoire (Core Genome Analogue)**  
  - A **large bar** associated with the intersection involving **all selected samples** may reflect the **core KO set** shared across the group.  
  - These KOs could correspond to essential metabolic functions or broadly conserved degradation pathways that are common to the sampled community.

- **Unique Functional Potential**  
  - Bars above columns with a **single dot (no connections)** may reveal **sample-specific KOs**.  
  - These unique genes could be strong candidates for explaining **specialized degradation capabilities**, **niche adaptations**, or rare metabolic traits.  
  - Such samples may be valuable in targeted bioremediation scenarios where specific pollutants or conditions are present.

- **Functional Redundancy and Overlap**  
  - Intersections with **large bars spanning multiple connected dots** may reveal **functional redundancy**: several samples carry the same KO subset.  
  - High redundancy may suggest potential **niche overlap** or **backup capacity**, enhancing system robustness but potentially increasing competition.

- **Pairwise Similarity and Potential Partnerships**  
  - Bars over columns with **exactly two connected dots** quantify KOs shared exclusively by those two samples.  
  - These patterns may indicate:
    - high **metabolic similarity** between specific sample pairs,  
    - possible **functional partnerships**, or  
    - evolutionary relationships such as horizontal gene transfer events.

- **Multi-Sample Intersections and Functional Guilds**  
  - More complex intersection patterns (multiple connected dots involving subsets of samples) may correspond to **functional guilds**:  
    - groups of samples that share specific KO modules,  
    - potentially cooperating in particular metabolic processes or occupying related ecological roles.  

  These guilds can guide the design of **composite consortia** that exploit complementary capabilities while maintaining some redundancy for resilience.

---

## Reproducibility and Assumptions

- **Input Format**  
  The analysis requires a semicolon-delimited BioRemPP results table containing at least:
  - `sample` (sample identifier),  
  - `ko` (KO identifier).

- **Set Definition and De-duplication**  
  - Each sample's KO repertoire is treated as a **set of unique KOs**.  
  - Multiple occurrences of the same `(sample, ko)` pair in the raw data do **not** increase set size.

- **Selection Constraints**  
  - At least **two samples** must be selected to compute informative intersections.  
  - Interpretation should consider that different sample subsets will yield different core and unique KO patterns.

- **Scope of Inference**  
  - The UpSet plot encodes **presence/absence relationships** only; it does not account for KO copy number, expression, or regulation.  
  - Results should be interpreted as a **structural map of genetic potential**, to be integrated with other BioRemPP modules (e.g., pathway completeness, toxicological profiling, regulatory relevance) for comprehensive bioremediation design.


 
---

## Activity diagram of the use case

*Click on the image to enlarge and explore details.*

<a class="glightbox" href="../uc_8.7.png">
  <img src="../uc_8.7.png" alt="Activity diagram of the use case">
</a>


