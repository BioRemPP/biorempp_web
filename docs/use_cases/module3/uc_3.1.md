# UC-3.1 — Principal Component Analysis of Samples by Functional Profile

**Module:** 3 – System Structure: Clustering, Similarity, and Co-occurrence  
**Visualization type:** PCA scatter plot (samples in KO-based functional space)  
**Primary inputs:** BioRemPP results table with `sample` and `ko` columns  
**Primary outputs:** Sample coordinates on principal components (PC1, PC2)

---

## Scientific Question and Rationale

**Question:** How do the samples cluster or separate based on their overall functional (KO) profiles, and which samples are the most functionally similar or distinct?

This use case applies **Principal Component Analysis (PCA)** to visualize high-dimensional functional relationships among biological samples. Each sample is characterized by its KEGG Orthology (KO) repertoire. PCA projects these high-dimensional KO profiles into a two-dimensional space defined by the first two principal components, which capture the major axes of functional variation. This can facilitate the identification of functional clusters, gradients, and outliers in a compact and interpretable way.

---

## Data and Inputs

- **Primary data source:** `BioRemPP_Results.xlsx or BioRemPP_Results.csv`  
- **Key columns:**
  - `sample` – identifier for each biological sample
  - `ko` – KEGG Orthology identifier associated with the sample
- **Accepted format:** semicolon-delimited text table (`.txt` or `.csv`)
- **Derived structure:** binary presence/absence matrix with:
  - rows = samples  
  - columns = unique KOs  
  - cell = 1 if the sample has the KO, 0 otherwise

---

## Analytical Workflow

1. **Data Loading**  
   The primary results table (`BioRemPP_Results.xlsx or BioRemPP_Results.csv`) is loaded into memory.

2. **Matrix Construction**  
   A **binary presence/absence matrix** is constructed where:
   - rows correspond to **Samples**,  
   - columns correspond to **unique KOs**, and  
   - each cell is set to `1` if the sample possesses that KO and `0` otherwise.  
   This step converts categorical functional data into a numerical matrix suitable for PCA.

3. **Data Scaling**  
   The binary matrix is standardized using a `StandardScaler` (mean-centering and scaling to unit variance). This ensures that all KO features contribute comparably to the PCA, regardless of their overall frequency.

4. **PCA Computation**  
   PCA is performed on the scaled matrix to reduce dimensionality. The first two principal components (PC1 and PC2), which explain the largest fractions of variance in the KO space, are retained for visualization.

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
  Axis labels typically include the percentage of total variance explained by each component (e.g., "PC1 (35% variance)").

- **Proximity and Distance**  
  The distance between two points may reflect their **functional similarity**:
  - samples that lie close together may have more similar KO profiles,  
  - samples far apart may differ more strongly in the presence/absence of KOs that load heavily on PC1 and/or PC2.

---

## Interpretation and Key Messages

- **Functional Clusters**  
  Groups of points that cluster together may indicate sets of samples with similar KO-based functional profiles. These patterns could correspond to samples that share comparable metabolic capabilities, ecological roles, or degradation strategies.

- **Functional Divergence and Axes of Variation**  
  Separation of samples along PC1 or PC2 may indicate the main directions of functional divergence in the dataset. For example:
  - separation along PC1 may suggest that the KOs with high loadings on PC1 are key discriminators between those sample groups,  
  - similar reasoning applies to PC2.

- **Outliers**  
  Samples positioned far from the main clusters might be considered **functional outliers**, carrying unusually distinct KO repertoires. These may represent highly specialized or unusually rich functional profiles and could warrant focused investigation.

---

## Reproducibility and Assumptions

- **Input Format**  
  The analysis assumes a semicolon-delimited table containing at least the columns `sample` and `ko`.

- **Binary Representation**  
  Each `(sample, ko)` combination is treated as a **presence/absence** event. Multiple occurrences of the same KO within a sample (e.g., multiple genes encoding the same KO) are collapsed into a single presence (`1`).

- **Standardization**  
  The PCA is performed on a **standardized** version of the presence/absence matrix (mean-centered and scaled to unit variance). This is a standard prerequisite for PCA when features differ in frequency or scale.

- **Variance-Based Interpretation**  
  PCA captures **linear** combinations of KOs that explain variance in the dataset. It does not directly model nonlinear relationships or interaction effects, which may be addressed by complementary methods in other use cases.
