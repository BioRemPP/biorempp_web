# UC-3.5 — Sample Similarity (Based on Chemical Profiles)

**Module:** 3 – System Structure: Clustering, Similarity, and Co-occurrence  
**Visualization type:** Correlogram (sample × sample similarity heatmap in compound space)  
**Primary inputs:** BioRemPP results table with `sample` and `compoundname` columns  
**Primary outputs:** Pairwise similarity matrix of samples based on compound interaction profiles

---

## Scientific Question and Rationale

**Question:** How similar are the samples to one another, based on the shared repertoire of chemical compounds they interact with?

This use case quantifies **pairwise similarity** between all biological samples using their chemical interaction profiles as a proxy for **degradative capabilities**. A correlogram (heatmap of a correlation matrix) is constructed from binary presence/absence profiles of compounds for each sample. The resulting visualization provides a compact, quantitative overview of how alike any two samples may be in terms of the compounds they can interact with, which can help identify chemical "guilds", distinct degradative strategies, and unique specialists within the dataset.

---

## Data and Inputs

- **Primary data source:** `BioRemPP_Results.xlsx or BioRemPP_Results.csv`  
- **Key columns:**
  - `sample` – identifier for each biological sample
  - `compoundname` – name (or identifier) of the chemical compound associated with the sample
- **Accepted format:** semicolon-delimited text table (`.txt` or `.csv`)
- **Derived structure:** binary presence/absence matrix with:
  - rows = samples  
  - columns = unique compound names  
  - cell = `1` if the sample is associated with that compound, `0` otherwise

---

## Analytical Workflow

1. **Data Loading**  
   The primary results table (`BioRemPP_Results.xlsx or BioRemPP_Results.csv`) is loaded into memory.

2. **Matrix Construction**  
   A **binary presence/absence matrix** is constructed where:
   - rows correspond to **Samples**,  
   - columns correspond to **unique compound names**, and  
   - each cell is `1` if the sample is associated with that compound and `0` otherwise.

3. **Correlation Calculation**  
   A **pairwise similarity matrix** is computed by correlating the compound presence/absence vectors (rows) for every pair of samples. Typically:
   - the **Pearson correlation coefficient** is calculated between each pair of sample vectors,  
   - this yields a square matrix where each cell `(i, j)` represents the similarity score between Sample *i* and Sample *j* based on their compound profiles.

4. **Rendering**  
   The resulting sample-by-sample correlation matrix is rendered as a **heatmap (correlogram)**:
   - both axes list the same set of samples,  
   - cell colors encode correlation values, and  
   - a color bar indicates the numerical range of correlation coefficients.

---

## How to Read the Plot

- **X-axis and Y-axis (Samples)**  
  Both axes represent the same set of **Samples**. The cell at row *i*, column *j* shows the similarity between those two samples.

- **Cell Color**  
  The color at each cell encodes the **correlation coefficient** between the compound presence/absence profiles of the two samples:
  - warm colors (e.g., reds) indicate **high positive similarity** (samples interact with very similar sets of compounds),  
  - cooler or neutral colors indicate lower similarity.

- **Color Scale**  
  A diverging color scale is typically used:
  - warm colors highlight strong similarity,  
  - neutral or cool colors indicate weaker similarity.  
  The main diagonal is always at the maximum value, as each sample is perfectly correlated with itself.

---

## Interpretation and Key Messages

- **Functional Guilds (Chemical Guilds)**  
  Brightly colored blocks or patches off the main diagonal may identify **clusters of samples with highly similar chemical degradation profiles**. These clusters might be interpreted as "functional guilds": groups of samples that may compete for, or collaboratively process, similar sets of chemical substrates.

- **Distinct Degradative Strategies**  
  The overall structure of the heat map can reveal **distinct groups of samples** that may specialize in different parts of the chemical space:
  - separate warm-colored regions could indicate sets of samples that primarily target different compound subsets or classes,  
  - transitions between regions may suggest shifts in degradative strategy or substrate preference.

- **Unique Chemical Specialists**  
  Samples whose row/column is dominated by neutral or cool colors (low correlations with most other samples) could be **chemical specialists**, exhibiting unique or rare compound interaction profiles within the dataset. These may be particularly relevant for targeted remediation of specific pollutants.

---

## Reproducibility and Assumptions

- **Input Format**  
  The analysis assumes a semicolon-delimited table containing at least the columns `sample` and `compoundname`.

- **Binary Representation**  
  The similarity calculation is based on **binary presence/absence** of compounds. Multiple occurrences of the same compound for a given sample (e.g., through different genes or pathways) are collapsed into a single presence (`1`).

- **Similarity Metric**  
  Similarity is quantified using the **Pearson correlation coefficient** applied to binary vectors. This metric captures linear co-variation in compound repertoires; while widely used, alternative metrics (e.g., Jaccard similarity) may be explored in complementary analyses.

- **Interpretation Scope**  
  The correlogram reflects similarity in **chemical interaction repertoires**, not interaction strength, kinetic efficiency, or environmental abundance of compounds. These aspects require additional data and analyses beyond the presence/absence of `compoundname`.


 
---

## Activity diagram of the use case

*Click on the image to enlarge and explore details.*

<a class="glightbox" href="../uc_3.5.png">
  <img src="../uc_3.5.png" alt="Activity diagram of the use case">
</a>


