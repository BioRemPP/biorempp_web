# UC-4.6 — Functional Potential by Chemical Compound

**Module:** 4 – Functional and Genetic Profiling  
**Visualization type:** Interactive scatter (sample–compound matrix with KO-based intensity)  
**Primary inputs:** `BioRemPP_Results.xlsx or BioRemPP_Results.csv` (sample–compound–KO associations, with chemical class)  
**Primary outputs:** Sample–compound functional potential map for a selected chemical class

---

## Scientific Question and Rationale

**Question:** For a given class of chemical compounds, which samples exhibit the strongest functional potential—measured by KO diversity—towards which specific compounds?

Instead of asking only **whether** a sample can interact with a compound, this use case quantifies **how strongly** it is equipped to do so, using the **number of unique KEGG Orthology (KO) identifiers** as a proxy for the **complexity and breadth of the underlying genetic machinery**.

By filtering on a **chemical class** and summarizing **unique KO counts** for each `(sample, compound)` pair, the visualization creates a two-dimensional **functional potential landscape**, where "hotspots" (large, bright points) may identify combinations of samples and compounds that are particularly promising targets for applied bioremediation strategies.

---

## Data and Inputs

- **Primary data source:** `BioRemPP_Results.xlsx or BioRemPP_Results.csv` (semicolon-delimited)  
- **Key columns:**
  - `sample` – identifier for each biological sample  
  - `compoundclass` – chemical class for each compound  
  - `compoundname` – individual compound names  
  - `ko` – KEGG Orthology identifier(s) associated with each sample–compound interaction

- **User control:**
  - A **dropdown menu** to select the **Compound Class** (`compoundclass`) to be analyzed.

- **Output structure:**
  - **X-axis:** samples  
  - **Y-axis:** compounds (within the selected class)  
  - **Point size/color:** unique KO count for each `(sample, compound)` pair (functional potential)

---

## Analytical Workflow

1. **Compound Class Selection (User Input)**  
   The user selects a **chemical class** (`compoundclass`) from an interactive dropdown menu.  
   - All subsequent filtering and aggregation are restricted to compounds belonging to this class.

2. **Dynamic Filtering**  
   - The results table `BioRemPP_Results.xlsx or BioRemPP_Results.csv` is loaded.  
   - The dataset is filtered to retain only rows where:
     - `compoundclass` equals the selected class, and  
     - `sample`, `compoundname`, and `ko` are valid and non-missing.

3. **Aggregation of Functional Potential**  
   - The filtered data is grouped by `(sample, compoundname)`.  
   - For each `(sample, compoundname)` pair, the **number of distinct KO identifiers** is computed (e.g., `nunique()` on `ko`).  
   - This yields a table where each row encodes:
     - `sample`,  
     - `compoundname`,  
     - `unique_ko_count` (the functional potential metric).

4. **Rendering as Sample–Compound Scatter Map**  
   - The aggregated table is rendered as a **scatter (dot) plot** where:
     - **X-axis:** `sample`,  
     - **Y-axis:** `compoundname`,  
     - **Marker size and color:** proportional to `unique_ko_count`.  
   - A continuous color bar provides a quantitative legend for the KO-based functional potential.

---

## How to Read the Plot

- **Dropdown Menu (Chemical Class Selection)**  
  - Use the menu to select the **Compound Class** of interest (e.g., aromatics, chlorinated compounds).  
  - The plot automatically updates to show only compounds and interactions within that class.

- **Y-axis – Compound Names**  
  - Each horizontal position corresponds to an individual **Compound** (`compoundname`) within the selected class.  
  - Reading along the row reveals which samples interact with that compound and with what KO diversity.

- **X-axis – Samples**  
  - Each vertical position corresponds to a **Sample**.  
  - Reading down the column reveals which compounds of the selected class are targeted by that sample and with what level of functional potential.

- **Marker Size and Color – Functional Potential**  
  - Each point represents a **sample–compound** interaction.  
  - **Marker size** and **color intensity** are both mapped to the **count of unique KOs** (`unique_ko_count`) for that interaction:
    - larger, brighter markers indicate higher KO diversity and thus higher functional potential  
    - smaller, paler markers indicate more limited KO diversity

---

## Interpretation and Key Messages

- **Functional Hotspots**  
  - Large, brightly colored points may mark **hotspots of genetic investment**, where a sample deploys a rich and diverse KO repertoire against a specific compound.  
  - These hotspots could highlight **high-priority sample–compound pairs** for targeted bioremediation experiments.

- **Sample-Level Specialization and Breadth**  
  - A sample whose column contains **many large, bright markers** could be interpreted as a **strong degrader** for that chemical class, with broad or intense functional capacity across multiple compounds.  
  - Columns dominated by smaller markers or sparse points may indicate weaker or more limited functionality within that class.

- **Compound-Level Complexity and Challenge**  
  - A compound row with **large, bright markers for several different samples** may suggest that:
    - the compound is a **complex or challenging substrate**, potentially requiring a diverse enzymatic toolkit.  
  - Conversely, compounds with only a few small markers may be either simple to degrade (requiring fewer KOs) or underrepresented in the dataset.

- **Consortium Design Implications**  
  - By visually inspecting which samples cover which compounds with high KO diversity, users can:
    - identify **complementary sample sets** that together provide broad coverage of high-risk compounds within a class  
    - choose **elite candidate samples** for focused studies on particularly problematic compounds

---

## Reproducibility and Assumptions

- **Input Format**  
  The analysis requires a semicolon-delimited table containing at least:
  - `sample`,  
  - `compoundclass`,  
  - `compoundname`,  
  - `ko`.

- **Definition of Functional Potential**  
  - For each `(sample, compoundname)` pair, **functional potential** is defined as the **count of unique KO identifiers** associated with that interaction.  
  - Multiple rows with the same `(sample, compoundname, ko)` combination do not increase the KO count; KOs are considered unique per pair.

- **Scope and Limitations**  
  - The metric captures **annotated genetic potential**, not expression or kinetic performance.  
  - Interpretation assumes that higher KO diversity is a reasonable proxy for:
    - more robust or versatile degradation capacity, and/or  
    - more complex enzymatic strategies for acting on that compound.
 