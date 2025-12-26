# UC-1.3 — Proportional Contribution of Regulatory References

**Module:** 1 – Comparative Assessment of Databases, Samples, and Regulatory Frameworks  
**Visualization type:** 100% stacked bar chart (proportional contribution of KO diversity)  
**Primary inputs:** BioRemPP results table with `referenceAG` and `ko` columns  
**Primary outputs:** Proportional contribution of unique KO identifiers per regulatory agency

---

## Scientific Question and Rationale

**Question:** What is the relative contribution of each regulatory agency's associated functional potential to the total unique KO diversity observed across the entire dataset?

This use case provides a high-level overview of the functional landscape by partitioning the complete set of unique KEGG Orthology (KO) identifiers according to the regulatory context in which they appear. Specifically, it quantifies how much of the total KO diversity can be attributed to compounds linked to each regulatory or scientific agency (`referenceAG`). The resulting 100% stacked bar chart summarizes the **relative functional breadth** associated with each regulatory framework, enabling rapid comparison of how different agencies map onto the underlying metabolic potential captured by BioRemPP.

---

## Data and Inputs

- **Primary data source:** BioRemPP results table  
- **Key columns:**
  - `referenceAG` – identifier for the regulatory or scientific agency (e.g., WFD, CONAMA, EPC)
  - `ko` – KEGG Orthology identifier associated with the annotated function
- **Accepted format:** semicolon-delimited text table (`.txt` or `.csv`)
- **Entity of interest:** unique KO identifiers associated with each agency

---

## Analytical Workflow

1. **Data Loading**  
   The primary results table produced by the BioRemPP analysis is loaded into memory.

2. **Filtering**  
   The dataset is filtered to retain only records containing both a non-empty `referenceAG` and a valid `ko` identifier. This ensures that each retained row can be unambiguously assigned to a regulatory context and a functional annotation.

3. **Aggregation**  
   The filtered data is grouped by each unique `referenceAG`. Within each group, the total number of **distinct KO identifiers** is computed. Each count reflects the functional diversity (in terms of KO richness) associated with that agency.

4. **Normalization and Rendering**  
   The per-agency counts of unique KOs are visualized as segments within a single bar using a 100% stacked bar chart. The `barnorm='percent'` setting normalizes these counts such that:
   - the full bar corresponds to 100% of all unique KOs in the dataset, and  
   - each segment's length is proportional to the percentage contribution of that agency's KO diversity.

---

## How to Read the Plot

The 100% stacked bar chart can be interpreted as follows:

- **Single Bar (Global KO Pool)**  
  The chart consists of a single vertical (or horizontal) bar representing 100% of the unique KOs identified in the dataset across all regulatory contexts.

- **Colored Segments (Per-Agency Contributions)**  
  Each colored segment within the bar corresponds to one **Reference Agency** (`referenceAG`). The color distinguishes each agency's contribution.

- **Segment Length and Labels**  
  The length of each segment, together with its percentage label, may indicate that agency's **proportional contribution** to the total pool of unique KOs. Larger segments may correspond to agencies associated with a broader functional repertoire.

---

## Interpretation and Key Messages

- **Dominant Contributions**  
  Larger segments can highlight regulatory agencies whose associated compounds are linked to a greater diversity of metabolic functions (KOs). These agencies may oversee chemical spaces that are particularly rich in bioremediation-relevant activities or that are more extensively represented in the dataset.

- **Specialized Scope**  
  Smaller segments may correspond to agencies with a more specialized or narrow regulatory scope, whose target compounds are associated with a limited or less common set of metabolic pathways.

- **Comparative Functional Overview**  
  By summarizing KO diversity in a single normalized bar, the chart can provide an at-a-glance comparison of the **functional breadth** associated with each regulatory context, which can aid in the identification of agencies that align with broader versus more focused functional spaces.

---

## Reproducibility and Assumptions

- **Input Format**  
  The analysis assumes a semicolon-delimited table containing at least the columns `referenceAG` and `ko`.

- **Uniqueness Definition**  
  Counts are based on **unique KO identifiers per agency**. If the same KO is linked to multiple compounds under the same `referenceAG`, it is still counted only once for that agency.

- **Normalization**  
  Percentages are computed relative to the **global union** of all unique KOs across all agencies, ensuring that the full bar always corresponds to 100% of the KO diversity represented in the dataset.


 
---

## Activity diagram of the use case


  *Click on the image to enlarge and explore details.*

<a class="glightbox" href="../uc_1.3.png">
    <img src="../uc_1.3.png" alt="Activity diagram of the use case">
  </a>



