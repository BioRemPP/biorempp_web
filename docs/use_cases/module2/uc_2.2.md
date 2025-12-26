# UC-2.2 — Ranking of Samples by Chemical Diversity

**Module:** 2 – Exploratory Analysis: Ranking the Functional Potential of Samples and Compounds  
**Visualization type:** Bar chart (ranking by unique compound diversity per sample)  
**Primary inputs:** BioRemPP results table with `sample` and `compoundname` columns  
**Primary outputs:** Ranked list of samples by unique compound count ("chemical diversity")

---

## Scientific Question and Rationale

**Question:** Which samples interact with the widest variety of unique chemical compounds?

This use case ranks each biological sample according to the total number of **unique compounds** with which it is associated. The resulting bar chart provides a direct assessment of the **chemical diversity** or **chemical versatility** of each sample. By focusing on the breadth of distinct compounds rather than on functional annotations, this visualization can highlight which samples have the broadest interaction capacity across the chemical space represented in the dataset.

---

## Data and Inputs

- **Primary data source:** `BioRemPP_Results.xlsx or BioRemPP_Results.csv`  
- **Key columns:**
  - `sample` – identifier for each biological sample
  - `compoundname` – name of the chemical compound associated with that sample
- **Accepted format:** semicolon-delimited text table (`.txt` or `.csv`)
- **Entity of interest:** unique compound names associated with each sample

---

## Analytical Workflow

1. **Data Loading**  
   The primary results table (`BioRemPP_Results.xlsx or BioRemPP_Results.csv`) is loaded from its semicolon-delimited format.

2. **Filtering**  
   The dataset is filtered to retain only complete entries containing both a valid `sample` and a `compoundname`. Rows missing either field are discarded.

3. **Aggregation**  
   The filtered data is grouped by each unique `sample`. Within each group, the number of **distinct compound names** is computed (e.g., using `nunique()`), yielding a per-sample measure of chemical diversity.

4. **Sorting and Rendering**  
   The aggregated results are sorted (typically in descending order of unique compound count) and rendered as a bar chart:
   - one axis represents **Samples**,  
   - the other axis represents the **count of unique compounds**, and  
   - bar length/height is proportional to the unique compound count for each sample.

---

## How to Read the Plot

- **Sample Axis**  
  One axis (X or Y, depending on orientation) lists the individual **Samples**, each represented by a single bar.

- **Compound Count Axis**  
  The other axis represents the **absolute count of unique compounds** (`compoundname`) associated with each sample.

- **Bar Size and Labels**  
  The bar length (for a horizontal chart) or height (for a vertical chart), together with optional numeric labels, explicitly indicates the total unique compound count for that sample. Taller/longer bars correspond to higher chemical diversity.

---

## Interpretation and Key Messages

- **Chemical Versatility**  
  Samples with taller/longer bars may exhibit greater **chemical versatility**, suggesting an ability to interact with a broader and more diverse repertoire of compounds. These could be considered potential candidates for **generalist** roles in bioremediation scenarios that require broad substrate coverage.

- **Direct Comparative Ranking**  
  The chart provides a straightforward ranking of samples by chemical diversity, which can facilitate rapid identification of top-performing candidates for applications where broad degradative capacity may be advantageous.

- **Specialized Potential**  
  Samples with shorter bars may have more specialized chemical targets or a narrower metabolic scope within the set of compounds analyzed. Such **specialists** may still be strategically valuable when targeting specific pollutants or chemical classes.

---

## Reproducibility and Assumptions

- **Input Format**  
  The analysis assumes a semicolon-delimited table containing at least the columns `sample` and `compoundname`.

- **Uniqueness Definition**  
  Chemical diversity (compound richness) is defined as the **count of unique compounds per sample**. Multiple occurrences of the same `compoundname` for a given sample (e.g., across different reactions or genes) are counted only once.

- **Scope of Interpretation**  
  The interpretation is directly dependent on the compounds present in `BioRemPP_Results.xlsx or BioRemPP_Results.csv`. Samples may appear less diverse simply because certain compound classes or environmental conditions are not represented in the underlying dataset.


 
---

## Activity diagram of the use case

*Click on the image to enlarge and explore details.*

<a class="glightbox" href="../uc_2.2.png">
  <img src="../uc_2.2.png" alt="Activity diagram of the use case">
</a>


