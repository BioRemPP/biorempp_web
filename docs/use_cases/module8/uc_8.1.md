# UC-8.1 — Minimal Sample Grouping for Complete Compound Coverage

**Module:** 8 – Assembly of Functional Consortia  
**Visualization type:** Interactive faceted scatter plot (minimal non-redundant functional guilds)  
**Primary inputs:** `BioRemPP_Results.xlsx or BioRemPP_Results.csv` (sample–compound associations)  
**Primary outputs:** Minimal set of "functional guilds" providing complete compound coverage within a selected chemical class

---

## Scientific Question and Rationale

**Question:** What is the minimum number of distinct functional profiles (i.e., groups of samples with identical chemical targets) required to account for all observed compound interactions within a given chemical class?

This use case formalizes consortium design as a **set cover problem**. By clustering samples into **functional guilds** that share *identical* compound target sets within a specific chemical class, and then selecting the smallest subset of these guilds that collectively cover all compounds, the analysis may reveal the **minimal, non-redundant strategy** needed to achieve full chemical coverage. This can provide a principled foundation for designing parsimonious, yet functionally complete, bioremediation consortia.

---

## Data and Inputs

- **Primary data source:** `BioRemPP_Results.xlsx or BioRemPP_Results.csv` (semicolon-delimited)  
- **Key columns:**
  - `sample` – identifier for each biological sample  
  - `compoundclass` – chemical class to which a compound belongs  
  - `compoundname` – name of the chemical compound interacted with by the sample  

- **Core concept: Functional Guilds**  
  A **functional guild** is defined as a group of samples that share the **exact same set of target compounds** within a selected chemical class. Samples within the same guild are functionally equivalent with respect to that class.

---

## Analytical Workflow

1. **User Selection (Chemical Class)**  
   The user selects a **`compoundclass`** from an interactive dropdown menu (e.g., Aromatics, Chlorinated, Metals). This choice defines the chemical space to be analyzed.

2. **Dynamic Filtering**  
   The primary results table (`BioRemPP_Results.xlsx or BioRemPP_Results.csv`) is filtered to retain only rows where:
   - `compoundclass` equals the selected class, and  
   - both `sample` and `compoundname` are valid and non-missing.  

   This subset represents all observed interactions between samples and compounds in the chosen class.

3. **Sample Grouping into Functional Guilds**  
   For each `sample`, the set of associated `compoundname` values (within the selected class) is computed.  
   - Samples whose **compound sets are identical** are grouped into the same **functional guild**.  
   - Each guild is thus characterized by a unique compound profile and a list of member samples.

4. **Minimization via Set Cover (Greedy Heuristic)**  
   A **greedy set cover algorithm** is applied to the guilds:
   - Initialize the set of **uncovered compounds** as all unique `compoundname` values in the selected class.  
   - Iteratively select the guild that covers the largest number of currently uncovered compounds.  
   - Remove these compounds from the uncovered set and repeat until all compounds are covered.  

   The result is a **minimal (or near-minimal) subset of functional guilds** that collectively cover every compound in the selected class.

5. **Rendering**  
   The minimal guild set is visualized as a **faceted scatter plot**:
   - each facet (subplot) corresponds to one **selected functional guild**,  
   - within a facet, the x-axis lists member `sample`s and the y-axis lists `compoundname`s,  
   - points mark the presence of a sample–compound interaction, visually confirming the guild's profile.

---

## How to Read the Plot

- **Dropdown Menu**  
  Use the dropdown to choose the **Compound Class**. The full pipeline (filtering, guild detection, set cover, and plotting) is recomputed and the visualization is updated accordingly.

- **Subplots (Facets)**  
  Each subplot represents one **minimal required functional guild**:
  - the **number of subplots** equals the number of guilds selected by the set cover algorithm,  
  - each subplot can be interpreted as a distinct functional "strategy" for targeting the compounds in the selected class.

- **Y-axis (Compounds)**  
  Lists the **Compound Names** that define the chemical profile of that guild within the selected class.

- **X-axis (Samples)**  
  Lists the **Samples** that belong to that guild.  
  All samples within a subplot share the same compound interaction profile.

- **Points (Interactions)**  
  A point at the intersection of a sample and a compound indicates an **observed interaction** (i.e., the sample has at least one functional annotation linking it to that compound).

---

## Interpretation and Key Messages

- **Functional Redundancy**  
  The **number of subplots** (minimal guilds) can provide an immediate measure of redundancy:
  - **Few guilds** → high redundancy: many samples share similar compound profiles.  
  - **Many guilds** → low redundancy: compound coverage relies on multiple specialized strategies.

- **Core vs. Niche Profiles**  
  - A guild whose subplot contains **many samples** may represent a **core functional profile** that is widely distributed among samples; these could be robust, common strategies.  
  - A guild with **only one or two samples** may represent a **niche profile**, potentially encoding specialized capabilities that cannot be easily replaced.

- **Efficient Consortium Design**  
  This analysis can be particularly valuable for **designing minimal consortia**:
  - by selecting **one representative sample per guild** from the minimal set, one could theoretically achieve **complete coverage** of all compounds in the chosen class,  
  - this may minimize functional overlap while preserving full chemical coverage, which could be desirable in scenarios where the number of deployed samples must be limited.

- **Trade-offs and Extensions**  
  Although the minimal set emphasizes parsimony, additional samples from the same guilds can be added to introduce **redundancy and robustness** (e.g., to buffer against environmental variability or loss of specific members).

---

## Reproducibility and Assumptions

- **Input Format**  
  The analysis assumes a semicolon-delimited `BioRemPP_Results.xlsx or BioRemPP_Results.csv` table containing at least:
  - `sample`,  
  - `compoundclass`,  
  - `compoundname`.

- **Definition of Guilds**  
  Functional guilds are defined strictly by **identical compound sets** within the selected class. Even a single additional or missing compound differentiates two guilds.

- **Set Cover Approximation**  
  The minimization step uses a **greedy heuristic** for the set cover problem:
  - this approach is computationally efficient and typically near-optimal,  
  - however, it does not guarantee the absolute mathematically minimal number of guilds in all possible cases.



- **Functional Interpretation**  
  The analysis is based on **observed sample–compound associations**. It does not encode kinetic parameters, environmental abundance, or interaction strength; it answers a structural question: **Which distinct functional profiles are minimally required to cover all compounds in a given class?**


 
---

## Activity diagram of the use case

*Click on the image to enlarge and explore details.*

<a class="glightbox" href="../uc_8.1.png">
  <img src="../uc_8.1.png" alt="Activity diagram of the use case">
</a>


