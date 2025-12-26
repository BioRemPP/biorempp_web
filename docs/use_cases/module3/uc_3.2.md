# UC-3.2 — Principal Component Analysis of Samples by Chemical Profile

**Module:** 3 – System Structure: Clustering, Similarity, and Co-occurrence  
**Visualization type:** PCA scatter plot (samples in compound-interaction space)  
**Primary inputs:** BioRemPP results table with `sample` and `cpd` (compound) columns  
**Primary outputs:** Sample coordinates on principal components (PC1, PC2) based on chemical interaction profiles

---

## Scientific Question and Rationale

**Question:** How do the samples cluster or separate based on their chemical interaction profiles (the compounds they are associated with), and which samples have the most similar or distinct degradation capabilities?

This use case applies **Principal Component Analysis (PCA)** to characterize relationships among biological samples based on their **compound interaction profiles** rather than their KO repertoires. Each sample is represented by the set of compounds (`cpd`) with which it is associated. PCA projects these high-dimensional compound presence/absence patterns into a two-dimensional space defined by the first two principal components. This can provide an interpretable map of chemical similarity, potentially revealing groups of samples that target similar substrates, as well as "chemical specialists" with unique compound profiles.

---

## Data and Inputs

- **Primary data source:** `BioRemPP_Results.xlsx or BioRemPP_Results.csv`  
- **Key columns:**
  - `sample` – identifier for each biological sample
  - `cpd` – identifier or name of the chemical compound associated with that sample
- **Accepted format:** semicolon-delimited text table (`.txt` or `.csv`)
- **Derived structure:** binary presence/absence matrix with:
  - rows = samples  
  - columns = unique compounds (`cpd`)  
  - cell = `1` if the sample is associated with the compound, `0` otherwise

---

## Analytical Workflow

1. **Data Loading**  
   The primary results table (`BioRemPP_Results.xlsx or BioRemPP_Results.csv`) is loaded into memory.

2. **Matrix Construction**  
   A **binary presence/absence matrix** is constructed where:
   - rows correspond to **Samples**,  
   - columns correspond to **unique compounds (`cpd`)**, and  
   - each cell is set to `1` if the sample is associated with that compound and `0` otherwise.  
   This converts the categorical compound interaction data into a numerical format suitable for PCA.

3. **Data Scaling**  
   The binary matrix is standardized using a `StandardScaler` (mean-centering and scaling to unit variance). This ensures that all compound features contribute comparably to the PCA, regardless of overall frequency.

4. **PCA Computation**  
   PCA is applied to the scaled matrix to reduce dimensionality. The first two principal components (PC1 and PC2), which explain the largest fractions of variance in the compound interaction space, are retained for visualization.

5. **Rendering**  
   The samples are plotted as a scatter plot in the PC1–PC2 plane:
   - each point represents a **Sample**, and  
   - its coordinates correspond to the sample's scores on PC1 (X-axis) and PC2 (Y-axis).

---

## How to Read the Plot

- **Points (Samples)**  
  Each point in the scatter plot represents an individual **Sample**.

- **Axes (Principal Components)**  
  - The **X-axis** corresponds to **Principal Component 1 (PC1)**.  
  - The **Y-axis** corresponds to **Principal Component 2 (PC2)**.  
  Axis labels typically include the percentage of total variance explained by each component (e.g., "PC1 (28% variance)").

- **Proximity and Distance**  
  The distance between points may reflect **similarity in chemical interaction profiles**:
  - samples that lie close together may interact with a more similar set of compounds,  
  - samples that are far apart may differ strongly in the compounds that load heavily on PC1 and/or PC2.

---

## Interpretation and Key Messages

- **Chemical Guilds / Clusters**  
  Groups of points that cluster together could form **chemical guilds**: sets of samples with similar degradation or interaction profiles across the compound space. These guilds may represent samples that target analogous substrates or share overlapping ecological niches.

- **Chemical Divergence and Axes of Variation**  
  Separation of samples or clusters along PC1 or PC2 may indicate the main directions of chemical divergence in the dataset:
  - separation along PC1 may reflect differences driven by compounds with high loadings on PC1,  
  - separation along PC2 may reflect analogous patterns for compounds with high loadings on PC2.

- **Chemical Specialists and Outliers**  
  Samples that are positioned far from the main cluster(s) might be interpreted as **chemical specialists**, possessing unique or rare compound interaction profiles. These could be particularly valuable for targeting specific pollutants or underrepresented chemical classes.

---

## Reproducibility and Assumptions

- **Input Format**  
  The analysis assumes a semicolon-delimited table containing at least the columns `sample` and `cpd`.

- **Binary Representation**  
  Each `(sample, cpd)` combination is treated as a **presence/absence** event. Multiple occurrences of the same compound for a sample (e.g., via different genes or pathways) are collapsed into a single presence (`1`).

- **Standardization**  
  The PCA is performed on a **standardized** version of the presence/absence matrix (mean-centered and scaled to unit variance), which is standard practice to prevent features with higher prevalence from dominating the analysis.

- **Variance-Based Interpretation**  
  PCA captures **linear** combinations of compounds that explain variance in the data. It does not explicitly model nonlinear relationships or interaction effects between compounds, which may be explored using complementary methods in other use cases.


 
---

## Activity diagram of the use case

*Click on the image to enlarge and explore details.*

<a class="glightbox" href="../uc_3.2.png">
  <img src="../uc_3.2.png" alt="Activity diagram of the use case">
</a>


