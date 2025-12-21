# UC-1.4 — Proportional Contribution of Samples Unique KO Pool

**Module:** 1 – Comparative Assessment of Databases, Samples, and Regulatory Frameworks  
**Visualization type:** 100% stacked bar chart (proportional contribution of KO diversity per sample)  
**Primary inputs:** BioRemPP results table with `sample` and `ko` columns  
**Primary outputs:** Proportional contribution of unique KO identifiers per sample

---

## Scientific Question and Rationale

**Question:** What is the relative functional diversity of each sample in comparison to the entire observed functional landscape?

This use case provides a high-level overview of the functional potential associated with each biological sample. The 100% stacked bar chart decomposes the global pool of unique KEGG Orthology (KO) identifiers into sample-specific contributions. By expressing each sample's unique KO richness as a fraction of the total, the visualization enables direct comparison of functional breadth across samples and can highlight which ones contribute most strongly to the overall functional landscape captured by BioRemPP.

---

## Data and Inputs

- **Primary data source:** `BioRemPP_Results.xlsx or BioRemPP_Results.csv`
- **Key columns:**
  - `sample` – identifier for each biological sample
  - `ko` – KEGG Orthology identifier associated with the annotated function
- **Accepted format:** semicolon-delimited text table (`.txt` or `.csv`)
- **Entity of interest:** unique KO identifiers associated with each sample

---

## Analytical Workflow

1. **Data Loading and Parsing**  
   The primary results table (`BioRemPP_Results.xlsx or BioRemPP_Results.csv`) is loaded and parsed from its semicolon-delimited format.

2. **Filtering and Standardization**  
   The dataset is filtered to retain only records containing valid `sample` and `ko` identifiers. Both fields are standardized (e.g., trimming whitespace, harmonizing case) to ensure consistency and prevent spurious duplication.

3. **Aggregation**  
   The filtered data is grouped by each unique `sample`. Within each group, the number of **distinct KO identifiers** is computed. This count reflects the functional richness (KO diversity) of that sample.

4. **Normalization and Rendering**  
   The per-sample counts of unique KOs are visualized as segments within a single bar using a 100% stacked bar chart. The counts are normalized so that:
   - the full bar corresponds to 100% of all unique KOs found across all samples, and  
   - each segment's length is proportional to that sample's percentage contribution to the global unique KO pool.

---

## How to Read the Plot

The 100% stacked bar chart can be interpreted as follows:

- **Single Bar (Global KO Pool)**  
  The chart consists of a single vertical (or horizontal) bar that represents 100% of the unique KOs detected across all samples in the dataset.

- **Colored Segments (Per-Sample Contributions)**  
  Each colored segment within the bar corresponds to a specific **Sample**.

- **Segment Length and Labels**  
  The length of each segment, together with its percentage label, may indicate that sample's **proportional contribution** to the total unique KO pool. Larger segments may denote samples associated with a broader functional repertoire.

---

## Interpretation and Key Messages

- **Functional Richness**  
  Larger segments can identify samples that contribute the most to the overall functional diversity of the dataset. These may be regarded as functionally rich or versatile candidates in terms of KO-based metabolic potential.

- **Comparative Diversity**  
  The chart can provide a rapid, at-a-glance comparison of the relative functional breadth of each sample. A sample with a noticeably larger segment possesses a more diverse set of unique metabolic functions than others, and could be prioritized for follow-up analyses or remediation trials, depending on the specific research or application context.

- **Niche Specialization**  
  Samples with smaller segments may exhibit a more specialized or focused functional profile. While less diverse, such samples may still be of high interest if their functions align with specific, targeted bioremediation tasks (e.g., degradation of a narrow class of pollutants).

---

## Reproducibility and Assumptions

- **Input Format**  
  The analysis assumes a semicolon-delimited table containing at least the columns `sample` and `ko`.

- **Uniqueness Definition**  
  Functional richness is defined as the count of **unique KO identifiers per sample**. If the same KO appears multiple times (e.g., linked to multiple genes or compounds) within a given sample, it is counted only once for that sample.

- **Normalization**  
  Percentages are computed relative to the **global union** of all unique KOs across all samples, ensuring that the full bar always corresponds to the complete KO diversity present in the dataset.
