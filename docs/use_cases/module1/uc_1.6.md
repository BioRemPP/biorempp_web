# UC-1.6 — Functional Potential of Samples Across Regulatory References

**Module:** 1 – Comparative Assessment of Databases, Samples, and Regulatory Frameworks  
**Visualization type:** Heatmap (unique KO counts per sample–agency pair)  
**Primary inputs:** BioRemPP results table with `sample`, `referenceAG`, and `ko` columns  
**Primary outputs:** Matrix of unique KO counts (samples × regulatory agencies)

---

## Scientific Question and Rationale

**Question:** To what extent does the functional potential, measured by unique KO diversity, of different samples align with the priorities of various environmental regulatory agencies?

This use case characterizes how the functional potential encoded in each biological sample is distributed across different regulatory contexts. The heatmap visualizes the number of unique KEGG Orthology (KO) identifiers at the intersection of each sample and each reference agency. This yields a matrix of **functional relevance** that can highlight where specific samples have particularly rich functional repertoires associated with compounds monitored by specific agencies.

---

## Data and Inputs

- **Primary data source:** BioRemPP 
- **Key columns:**
  - `sample` – identifier for each biological sample
  - `referenceAG` – identifier for the regulatory or scientific agency (e.g., WFD, CONAMA, EPC)
  - `ko` – KEGG Orthology identifier associated with the annotated function
- **Accepted format:** semicolon-delimited text table (`.txt` or `.csv`)
- **Entity of interest:** unique KO identifiers counted per `(sample, referenceAG)` pair

---

## Analytical Workflow

1. **Data Loading**  
   The primary results table produced by the BioRemPP analysis is loaded into memory.

2. **Filtering**  
   The dataset is filtered to retain only complete entries that contain valid values for `sample`, `referenceAG`, and `ko`. Rows with missing or invalid entries in any of these fields are discarded.

3. **Aggregation**  
   The filtered data is grouped by each unique `(sample, referenceAG)` pair. Within each group, the number of **distinct KO identifiers** is computed. This count reflects the functional potential associated with that specific sample–agency combination.

4. **Matrix Construction**  
   The aggregated data is pivoted to construct a 2D matrix where:
   - rows represent **Reference Agencies** (`referenceAG`),
   - columns represent **Samples**, and
   - each cell value corresponds to the **unique KO count** for that sample–agency pair.

5. **Rendering**  
   The resulting matrix is rendered as an interactive heatmap, where color intensity is proportional to the KO count. A color bar indicates the quantitative scale of KO richness.

---

## How to Read the Plot

- **Y-axis (Rows)**  
  Represents the different **Reference Agencies** included in the analysis.

- **X-axis (Columns)**  
  Represents the individual **Samples**.

- **Cell Color and Optional Labels**  
  The color intensity of each cell (and, optionally, the numeric label within it) may indicate the **count of unique KOs** associated with that specific sample–agency combination. Darker or warmer colors typically correspond to higher KO counts, suggesting greater functional potential in that regulatory context.

---

## Interpretation and Key Messages

- **Functional Hotspots**  
  Brightly colored cells ("hotspots") may mark combinations where a sample's functional repertoire strongly overlaps with the compound space associated with a particular agency. These points can highlight samples that may be especially relevant for degrading compounds prioritized by that agency.

- **Agency-Level Patterns**  
  Rows with consistently high values suggest that an agency's monitored compounds are associated with widely distributed metabolic functions across many samples. This pattern can indicate broadly encoded degradation capabilities or common functional pathways.

- **Sample-Level Profiles**  
  Columns with consistently high values may correspond to functionally **"generalist"** samples, characterized by broad metabolic potential across multiple regulatory contexts. In contrast, samples with hotspots concentrated in only one or a few rows may be considered **"specialists"**, exhibiting strong functional potential for specific agencies or regulatory scopes.

---

## Reproducibility and Assumptions

- **Input Format**  
  The analysis assumes a semicolon-delimited table containing at least the columns `sample`, `referenceAG`, and `ko`.

- **Co-occurrence Definition**  
  A valid link between a sample, a reference agency, and a KO is inferred from their co-occurrence in the same row of the input table.

- **Uniqueness Handling**  
  For each `(sample, referenceAG)` pair, the final value reflects the count of **unique KO identifiers**, not the total number of occurrences. Multiple rows containing the same KO for the same sample–agency pair are collapsed into a single count.

- **Functional Interpretation**  
  KO counts are used as a proxy for functional potential. The heatmap does not distinguish between differences in expression levels, gene copy number, or kinetic efficiency, which are addressed in other parts of the analytical framework or in downstream experimental validation.
