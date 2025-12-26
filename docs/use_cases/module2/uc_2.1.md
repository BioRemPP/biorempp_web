
# UC-2.1 — Ranking of Sample Functional Richness Across Databases

**Module:** 2 – Exploratory Analysis: Ranking the Functional Potential of Samples and Compounds  
**Visualization type:** Interactive vertical bar chart (ranked unique KO counts per sample)  
**Primary inputs:** BioRemPP, HADEG, and KEGG results tables with sample-level KO annotations  
**Primary outputs:** Ranked list of samples by functional richness (unique KO count) for each database

---

## Scientific Question and Rationale

**Question:** How does the ranking of functional richness for each sample change when viewed through the lens of different annotation databases (BioRemPP, HADEG, KEGG)?

This use case enables a direct comparison of the **functional richness** of each biological sample across multiple annotation sources. By allowing the user to switch between BioRemPP, HADEG, and KEGG, the horizontal bar chart reveals how many unique KEGG Orthology (KO) identifiers are associated with each sample in each database. This comparative view can help assess the extent to which perceived functional potential depends on the chosen reference source and may help distinguish robust "generalist" samples from database-dependent "specialists."

---

## Data and Inputs

- **Primary data sources:**
  - BioRemPP results table
  - HADEG results table
  - KEGG results table
- **Key columns (per selected database):**
  - `sample` – identifier for each biological sample
  - `ko` or `Gene` – KEGG Orthology identifier (or equivalent column used to store KO IDs)
- **Accepted format:** semicolon-delimited text tables (`.txt` or `.csv`)
- **Entity of interest:** unique KO identifiers counted per sample for the selected database

---

## Analytical Workflow

1. **Database Selection**  
   The user selects one of the available data sources (e.g., "BioRemPP", "HADEG", or "KEGG") via an interactive dropdown menu.

2. **Dynamic Data Loading**  
   Based on the selected database, the corresponding raw results table is loaded and parsed from its semicolon-delimited format.

3. **Data Processing and Aggregation**  
   The loaded data is filtered to remove invalid or incomplete entries (e.g., missing `sample` or KO identifier). For the selected database, the script:
   - identifies the appropriate KO column (`ko` or `Gene`), and  
   - calculates the number of **distinct KO identifiers** associated with each unique `sample`.

4. **Rendering and Sorting**  
   The aggregated counts are visualized as a vertical bar chart:
   - each bar represents a **Sample**,  
   - bar length shows the **unique KO count**, and  
   - bars are automatically sorted (typically ascending or descending) to create an intuitive ranking from lower to higher functional richness.

---

## How to Read the Plot

- **Dropdown Menu**  
  Use the dropdown control to switch between the **BioRemPP**, **HADEG**, and **KEGG** datasets. The chart updates dynamically based on the selected source.

- **X-axis (Horizontal Axis)**  
  Represents individual **Samples** (one bar per sample).


- **Y-axis (Vertical Axis)**  
   Represents the **count of unique KOs** associated with each sample in the selected database.



- **Bar Length and Labels**  
  The length of each bar reflects the total number of unique KOs for that sample. Optional numeric labels at the end of the bars explicitly state the KO count, supporting precise comparisons.

---

## Interpretation and Key Messages

- **Comparative Ranking Across Databases**  
  By switching between databases, users can observe how each sample's ranking changes. For instance, a sample that ranks highly in HADEG but lower in KEGG may have strong specialization in functions related to hydrocarbon degradation, potentially reflecting HADEG's focused scope.

- **Identifying Generalists vs. Specialists**  
  Samples that consistently rank near the top across **all three** databases may be regarded as robust functional **"generalists"**, likely encoding broad, multi-context functional potential. In contrast, samples whose rank fluctuates markedly between databases may act as **"specialists"**, excelling in functional domains best captured by specific annotation sources.

- **Assessing Database Scope and Bias**  
  Differences in rankings across BioRemPP, HADEG, and KEGG can suggest the inherent scope, curation strategy, and thematic focus of each database. This may help users understand which resource is more appropriate for identifying particular types of functional potential (e.g., broad metabolic coverage vs. targeted bioremediation pathways).

---

## Reproducibility and Assumptions

- **Input Format**  
  The analysis assumes semicolon-delimited tables for each database, each containing at least `sample` and either `ko` or `Gene` columns.

- **KO Column Handling**  
  The script dynamically detects whether KO identifiers are stored in a `ko` or `Gene` column and treats both as equivalent sources of KO IDs.

- **Uniqueness Definition**  
  Functional richness per sample is defined as the **count of unique KO identifiers**. Multiple occurrences of the same KO in the same sample (e.g., linked to several genes or compounds) are counted only once.

- **Comparability Across Databases**  
  Rankings are based on direct comparisons of unique KO counts within each database. Cross-database differences in curation depth, pathway coverage, and update cycles can influence KO diversity and should be considered when interpreting shifts in rank.


 
---

## Activity diagram of the use case

*Click on the image to enlarge and explore details.*

<a class="glightbox" href="../uc_2.1.png">
  <img src="../uc_2.1.png" alt="Activity diagram of the use case">
</a>


