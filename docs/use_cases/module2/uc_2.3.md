# UC-2.3 — Ranking of Compound Richness by Sample per Chemical Class

**Module:** 2 – Exploratory Analysis: Ranking the Functional Potential of Samples and Compounds  
**Visualization type:** Interactive bar chart (unique sample count per compound, by chemical class)  
**Primary inputs:** BioRemPP results table with `sample`, `compoundclass`, and `compoundname` columns  
**Primary outputs:** Ranked list of compounds by number of interacting samples, within a selected chemical class

---

## Scientific Question and Rationale

**Question:** Within a specific chemical class, which compounds are targeted by the widest range of samples, and what might this pattern suggest about their bioavailability or degradation potential?

This use case ranks compounds according to how many distinct biological samples interact with them, within a user-selected **chemical class**. By focusing on the **number of unique samples per compound**, the visualization can highlight compounds that are widely accessible to the biological system (potentially common substrates or ubiquitous pollutants), as well as those that may require more specialized metabolic capabilities.

---

## Data and Inputs

- **Primary data source:** `BioRemPP_Results.xlsx or BioRemPP_Results.csv`  
- **Key columns:**
  - `sample` – identifier for each biological sample
  - `compoundclass` – categorical label defining the chemical class (e.g., Aromatics, Chlorinated, Alkanes)
  - `compoundname` – name of the chemical compound
- **Accepted format:** semicolon-delimited text table (`.txt` or `.csv`)
- **Entities of interest:** compounds, grouped by chemical class, with counts of unique interacting samples

---

## Analytical Workflow

1. **User Selection**  
   The user selects a specific `compoundclass` from an interactive dropdown menu.

2. **Dynamic Filtering**  
   The primary results table (`BioRemPP_Results.xlsx or BioRemPP_Results.csv`) is filtered to retain only rows corresponding to the selected `compoundclass`. All downstream calculations are performed on this subset.

3. **Aggregation**  
   The filtered data is grouped by each unique `compoundname`. Within each group, the number of **distinct samples** associated with that compound is computed (e.g., using `nunique()` on the `sample` column). This yields a per-compound measure of how broadly the compound is targeted across the sample set.

4. **Sorting and Rendering**  
   The aggregated results (compound vs. unique sample count) are sorted in descending order and rendered as a bar chart:
   - one axis lists **Compounds** within the selected class,  
   - the other axis represents the **count of unique samples** that interact with each compound, and  
   - bar height/length is proportional to the unique sample count.

---

## How to Read the Plot

- **Dropdown Menu**  
  Use the dropdown to select the **Chemical Class** (`compoundclass`) to analyze. The plot updates automatically to show only compounds within that class.

- **Compound Axis**  
  One axis  lists individual **Compounds** belonging to the selected chemical class.

- **Sample Count Axis**  
  The other axis represents the **count of unique samples** associated with each compound.

- **Bar Height and Labels**  
  The height (or length) of each bar, along with optional numeric labels, indicates the total number of unique samples that interact with that compound. Taller bars correspond to compounds targeted by a larger fraction of the sampled biological diversity.

---

## Interpretation and Key Messages

- **High-Interaction Compounds**  
  Compounds with taller bars are associated with a more diverse set of samples. These patterns could suggest:
  - common or environmentally widespread substrates

- **Specialized Targets**  
  Compounds with shorter bars—especially those with a unique sample count of 1—are targeted by only a few, or a single, sample. This pattern may indicate **specialized** or rare metabolic capabilities that could be of interest for targeted or niche bioremediation strategies.

- **Comparing Chemical Classes**  
  By switching the selected `compoundclass` in the dropdown, users can compare interaction patterns across different chemical classes. For example, one can assess whether compounds in the "Aromatics" class are generally targeted by more diverse sets of samples than those in the "Chlorinated" class, which may provide insights into class-specific accessibility or metabolic difficulty.

---

## Reproducibility and Assumptions

- **Input Format**  
  The analysis assumes a semicolon-delimited table containing at least the columns `sample`, `compoundclass`, and `compoundname`.

- **Uniqueness Definition**  
  The ranking is based on the **count of unique samples per compound**. If a single sample interacts with a compound multiple times (e.g., through different genes, pathways, or reactions), it is still counted only once for that compound.

- **Class-Specific Context**  
  All rankings and interpretations are **conditional** on the selected chemical class. A compound may appear highly interactive within one class but absent in another simply because it is not annotated under that class.

- **Sampling and Annotation Bias**  
  The observed diversity of interacting samples for a given compound is constrained by the composition of the dataset and the completeness of the annotations in BioRemPP.


 
---

## Activity diagram of the use case

*Click on the image to enlarge and explore details.*

<a class="glightbox" href="../uc_2.3.png">
  <img src="../uc_2.3.png" alt="Activity diagram of the use case">
</a>


