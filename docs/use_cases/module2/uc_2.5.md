# UC-2.5 — Descriptive Statistics of Samples Across Databases

**Module:** 2 – Exploratory Analysis: Ranking the Functional Potential of Samples and Compounds  
**Visualization type:** Interactive box-and-scatter (jitter) plot of unique KO counts  
**Primary inputs:** BioRemPP, HADEG, and KEGG results tables with sample-level KO annotations  
**Primary outputs:** Distribution of unique KO counts per sample for each database

---

## Scientific Question and Rationale

**Question:** How does the statistical distribution of functional richness (unique KO counts) compare across different samples and annotation databases, and what might this reveal about their scope and focus?

This use case provides a comparative **statistical summary** of unique KEGG Orthology (KO) counts across all analyzed biological samples under different annotation sources. By switching between BioRemPP, HADEG, and KEGG, the visualization shows how functional richness is distributed for each database. A combined box plot and jittered scatter plot allows users to see both the **overall distribution** (median, quartiles, spread) and the **position of individual samples**, which may offer insight into database-specific coverage, variability, and potential outliers.

---

## Data and Inputs

- **Primary data sources:**
  - BioRemPP results table
  - HADEG results table
  - KEGG results table
- **Key columns (per selected database):**
  - `sample` – identifier for each biological sample
  - `ko` or `Gene` – KEGG Orthology identifier (or equivalent KO column)
- **Accepted format:** semicolon-delimited text tables (`.txt` or `.csv`)
- **Entity of interest:** unique KO counts per sample for the selected database

---

## Analytical Workflow

1. **Database Selection**  
   The user selects a data source (e.g., "BioRemPP") from an interactive dropdown menu.

2. **Dynamic Data Loading**  
   The corresponding raw results table for the selected database is loaded and parsed from its semicolon-delimited format.

3. **Column Resolution**  
   The script automatically identifies the correct columns for `sample` and the KO identifier, treating both `ko` and `Gene` as valid KO columns.

4. **Data Processing and Aggregation**  
   The data is filtered to remove invalid entries (e.g., missing `sample` or KO identifier). For the selected database, the script computes, for each unique `sample`, the number of **distinct KO identifiers**, yielding a per-sample `unique_ko_count`.

5. **Rendering**  
   The visualization is constructed using the per-sample `unique_ko_count` values:
   - A **box plot** is rendered to summarize the distribution (median and quartiles, with potential whiskers and outliers).  
   - A **jittered scatter plot** is overlaid, where each point represents one sample; the vertical position encodes its `unique_ko_count`, and the horizontal position is slightly jittered to reduce overlap and improve readability.

---

## How to Read the Plot

- **Dropdown Menu**  
  Use the dropdown to switch between the **BioRemPP**, **HADEG**, and **KEGG** datasets. The distribution updates dynamically for the selected source.

- **Box (Central Distribution)**  
  The box represents the **interquartile range (IQR)**—the central 50% of the `unique_ko_count` values for the selected database.  
  - The horizontal line inside the box marks the **median**.  
  - Whiskers and optional points outside the whiskers indicate the spread and possible outliers.

- **Jittered Points (Individual Samples)**  
  Each dot corresponds to a single **Sample**.  
  - Its vertical position encodes the `unique_ko_count` for that sample.  
  - Its horizontal position is slightly randomized (jittered) to prevent overlap between samples with similar counts.

- **Hover Information**  
  Hovering over a point reveals detailed information, such as:
  - sample name,  
  - exact unique KO count, and  
  - rank of that sample within the selected database.

---

## Interpretation and Key Messages

- **Comparing Distributions Across Databases**  
  By toggling between BioRemPP, HADEG, and KEGG, users can compare how functional richness is distributed:
  - A higher **median** in one database may suggest broader average functional coverage per sample.  
  - A wider **IQR** or longer whiskers could indicate more variability in functional richness among samples in that database.

- **Identifying Database-Specific Outliers**  
  Samples that appear as outliers (points far above or below the box) in one database but not in others may reflect:
  - specialized strengths captured by that annotation source (e.g., HADEG capturing high KO counts for hydrocarbon degraders), or  
  - differences in curation, annotation depth, or database scope.

- **Assessing Annotation Scope and Focus**  
  Databases with narrow, tightly clustered distributions (short boxes and whiskers) may have more uniform annotation depth or a focused scope (e.g., specialized domain such as hydrocarbon degradation), while broader distributions may correspond to more generalist, heterogeneous coverage (e.g., KEGG).

---

## Reproducibility and Assumptions

- **Input Format**  
  The analysis assumes semicolon-delimited tables for each database, each containing at least `sample` and a KO identifier column (`ko` or `Gene`).

- **KO Column Handling**  
  The code dynamically resolves whether the KO identifiers are stored under `ko` or `Gene` and treats both as equivalent sources of KO IDs.

- **Uniqueness Definition**  
  Functional richness is defined as the **count of unique KO identifiers per sample**. Multiple occurrences of the same KO within a sample (e.g., via multiple genes or compounds) are counted only once.

- **Jitter and Determinism**  
  The horizontal jitter applied to sample points is seeded to produce a **stable layout** for a given dataset, so the same input data yields identical visual arrangements across runs. The box plot itself is a deterministic statistical summary of the `unique_ko_count` distribution.
