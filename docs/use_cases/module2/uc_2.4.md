# UC-2.4 — Ranking of Compounds Richness by Gene Count per Chemical Classes 

**Module:** 2 – Exploratory Analysis: Ranking the Functional Potential of Samples and Compounds  
**Visualization type:** Interactive bar chart (unique gene count per compound, by chemical class)  
**Primary inputs:** BioRemPP results table with `compoundclass`, `compoundname`, and `genesymbol` columns  
**Primary outputs:** Ranked list of compounds by number of unique genes, within a selected chemical class

---

## Scientific Question and Rationale

**Question:** Within a specific chemical class, which compounds are associated with the greatest diversity of unique genes, and what might this pattern suggest about their degradation complexity?

This use case ranks compounds according to the diversity of **unique genes** associated with them, within a user-selected **chemical class**. The focus here is on the **compound-centric genetic demand**: which compounds elicit the most diverse genetic response. Compounds linked to many distinct genes may require complex, multi-step degradation pathways, whereas those associated with few genes may be handled by simpler enzymatic systems. This perspective complements sample-based analyses by potentially highlighting challenging or biochemically rich targets.

---

## Data and Inputs

- **Primary data source:** `BioRemPP_Results.xlsx or BioRemPP_Results.csv`  
- **Key columns:**
  - `compoundclass` – categorical label defining the chemical class (e.g., Aromatics, Aliphatics, Chlorinated)
  - `compoundname` – name of the chemical compound
  - `genesymbol` – gene symbol or identifier associated with the interaction
- **Accepted format:** semicolon-delimited text table (`.txt` or `.csv`)
- **Entities of interest:** compounds, grouped by chemical class, with counts of unique associated genes

---

## Analytical Workflow

1. **User Selection**  
   The user selects a `compoundclass` from an interactive dropdown menu.

2. **Dynamic Filtering**  
   The primary results table (`BioRemPP_Results.xlsx or BioRemPP_Results.csv`) is filtered to retain only rows corresponding to the selected `compoundclass`. All further calculations are performed on this subset.

3. **Aggregation**  
   The filtered data is grouped by each unique `compoundname`. Within each group, the number of **distinct gene symbols** is computed (e.g., using `nunique()` on the `genesymbol` column). This yields a per-compound measure of **genetic diversity** associated with its degradation or transformation.

4. **Sorting and Rendering**  
   The aggregated results (compound vs. unique gene count) are sorted in descending order and rendered as a bar chart:
   - one axis lists **Compounds** within the selected class,  
   - the other axis represents the **count of unique genes** associated with each compound, and  
   - bar height/length is proportional to the unique gene count.

---

## How to Read the Plot

- **Dropdown Menu**  
  Use the dropdown to select the **Chemical Class** (`compoundclass`) of interest. The plot updates automatically to show only compounds belonging to that class.

- **Compound Axis**  
  One axis (typically the X-axis) lists the individual **Compounds** within the selected class.

- **Gene Count Axis**  
  The other axis (typically the Y-axis) represents the **count of unique genes** (`genesymbol`) associated with each compound.

- **Bar Height and Labels**  
  The height (or length) of each bar, along with optional numeric labels, indicates the total number of unique genes linked to that compound. Taller bars correspond to compounds that require a more diverse genetic toolkit.

---

## Interpretation and Key Messages

- **Complex Degradation Targets**  
  Compounds with taller bars are associated with a larger and more diverse set of genes. This pattern may suggest **complex degradation targets**, potentially involving:
  - multi-step pathways,  
  - multiple enzyme families, transporters, or regulators, or  
  - contributions from several different samples in a consortium.

- **Simple Degradation Targets**  
  Compounds with shorter bars—especially those with a unique gene count of 1—appear to be handled by a smaller, more specific genetic repertoire. These may rely on a single dominant pathway or a limited set of enzymes, and could be considered **simpler** targets in terms of genetic requirements.

- **Comparing Chemical Classes**  
  By switching between chemical classes in the dropdown, users can compare genetic interaction patterns across classes. For example, one can ask whether compounds in the "Aromatics" class generally require a greater diversity of genetic machinery than those in the "Aliphatics" class, which may offer insights into class-level biochemical complexity.

---

## Reproducibility and Assumptions

- **Input Format**  
  The analysis assumes a semicolon-delimited table containing at least the columns `compoundclass`, `compoundname`, and `genesymbol`.

- **Uniqueness Definition**  
  The ranking is based on the **count of unique genes per compound**. If a single gene is associated multiple times with the same compound (e.g., across different samples or conditions), it is counted only once for that compound.

- **Gene-Level Interpretation**  
  Gene counts are used as a proxy for **genetic complexity**; the visualization does not directly incorporate expression level, gene copy number, or kinetic parameters. These aspects would require additional layers of analysis.

- **Class-Specific Context**  
  All rankings and interpretations are conditional on the selected chemical class. A compound may be genetically complex in one class but absent in another simply because it is not annotated there.


 
---

## Activity diagram of the use case

![Activity diagram of the use case](uc_2.4.png)


