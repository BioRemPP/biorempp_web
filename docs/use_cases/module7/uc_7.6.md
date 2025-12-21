# UC-7.6 — Sample Risk Mitigation Breadth

**Module:** 7 – Toxicological Risk Assessment and Profiling  
**Visualization type:** Interactive treemap (hierarchical breadth of high-risk compound coverage per sample)  
**Primary inputs:** `BioRemPP_Results.xlsx or BioRemPP_Results.csv` (sample–compound interactions) and `ToxCSM.xlsx or ToxCSM.csv` (predicted toxicity and categories)  
**Primary outputs:** Per-sample "Risk Mitigation Breadth Profile" across toxicological categories

---

## Scientific Question and Rationale

**Question:** Which samples possess the broadest capability to mitigate risk, as measured by the variety of distinct high-risk compounds they can target within each toxicological category?

This use case characterizes the **breadth** of risk mitigation. The treemap quantifies, for each sample and toxicological category, the **number of distinct high-risk compounds** that the sample can interact with. The resulting "Risk Mitigation Breadth Profile" may highlight generalist samples that cover many different hazardous compounds, as well as category-specific specialists that provide broad coverage within a particular toxicological domain (e.g., Genomic, Environmental, Organic).

---

## Data and Inputs

- **Primary data sources:**
  - `BioRemPP_Results.xlsx or BioRemPP_Results.csv` – functional interaction data linking samples and compounds
  - `ToxCSM.xlsx or ToxCSM.csv` – predicted toxicity scores and qualitative labels for compounds
- **Key columns:**
  - From `ToxCSM.xlsx or ToxCSM.csv`:
    - `compoundname` – chemical compound name
    - `endpoint` / `label_*` – endpoint-specific toxicity labels (e.g., "High Toxicity", "High Safety")
    - `supercategory` (derived) – mapped toxicological category (e.g., Genomic, Environmental, Organic)
  - From `BioRemPP_Results.xlsx or BioRemPP_Results.csv`:
    - `sample` – identifier for each biological sample
    - `compoundname` – compound associated with the sample
- **Hierarchy represented in the treemap:**
  - Level 1: **Sample**  
  - Level 2: **Toxicity Category** (toxicological super-category)  

The quantitative value displayed is the **count of distinct high-risk compounds** per `(sample, category)` pair.

---

## Analytical Workflow

1. **Data Loading and Integration**  
   Both `BioRemPP_Results.xlsx or BioRemPP_Results.csv` and `ToxCSM.xlsx or ToxCSM.csv` are loaded from their semicolon-delimited formats.

2. **Risk Filtering in ToxCSM**  
   The `ToxCSM` data is reshaped into a **long format** (one row per compound–endpoint pair) and filtered to keep only interactions where the predicted risk is **high**. The remaining set defines compounds with **relevant predicted toxicity**.

3. **Endpoint-to-Category Mapping**  
   Individual toxicological endpoints are mapped to broader **Toxicity Categories** (e.g., Genomic, Environmental, Organic) using a predefined lookup, assigning each endpoint to its parent super-category.

4. **Data Merging**  
   The risk-filtered and categorized ToxCSM data is merged with `BioRemPP_Results.xlsx or BioRemPP_Results.csv` on `compoundname` to connect:
   - high-risk compounds,  
   - their toxicological categories, and  
   - the samples known to interact with them.

5. **Aggregation for Breadth**  
   The merged dataset is grouped by `sample` and `Toxicity Category`. For each `(sample, category)` combination, the number of **distinct compound names** is computed (e.g., via `nunique()` on `compoundname`). This count is the **breadth metric** used in the visualization.

6. **Rendering as Treemap**  
   The aggregated data is rendered as an **interactive treemap**:
   - each **Sample** is represented as a top-level rectangle,  
   - within each sample, second-level rectangles represent **Toxicity Categories**,  
   - the **area** of each category rectangle is proportional to the number of unique high-risk compounds covered by that sample in that category.

---

## How to Read the Plot

- **Nested Rectangles (Hierarchy)**  
  The treemap uses nested rectangles to encode the hierarchy:
  - the largest rectangles correspond to **Samples**,  
  - rectangles nested within each sample correspond to **Toxicity Categories**.

- **Area (Values)**  
  The **area** of each rectangle is proportional to the **count of unique high-risk compounds** targeted by a given `(sample, category)` combination. Larger areas indicate broader mitigation breadth.

- **Color Encoding**  
  Color is typically used to distinguish **Toxicity Categories** at the second level, helping users quickly see which risk domains dominate within each sample.

- **Interactivity (Zoom and Tooltips)**  
  Interactive behavior typically includes:
  - clicking on a rectangle to **zoom in** on a particular sample or category, and  
  - tooltips showing precise values (sample name, category, and unique high-risk compound count).

---

## Interpretation and Key Messages

- **Versatile Generalists**  
  Samples whose **top-level rectangles** dominate the treemap area may be **broad generalists**. They can interact with a wide variety of high-risk compounds across multiple categories, potentially making them strong candidates for inclusion in broadly protective consortia.

- **Category Specialists**  
  Within a sample, a particularly large rectangle for a single **Toxicity Category** (e.g., Environmental) may indicate that the sample is a **category specialist**, covering many different high-risk compounds in that domain. Such samples could be valuable for targeted risk mitigation strategies focusing on specific threat types.

- **Complementary Consortium Design**  
  The treemap can be especially useful for designing **complementary consortia**. For example:
  - a sample with broad Genomic coverage can be paired with another that excels in Organic or Environmental categories,  
  - together, they may maximize the overall **chemical coverage** across diverse high-risk profiles.

- **Breadth vs. Depth**  
  This use case emphasizes **breadth of coverage**—the variety of high-risk compounds addressed—rather than **depth** (e.g., number of genes per compound). It is therefore complementary to analyses that focus on genetic investment and mechanistic complexity.

---

## Reproducibility and Assumptions

- **Input Format**  
  The analysis requires:
  - `BioRemPP_Results.xlsx or BioRemPP_Results.csv` – semicolon-delimited, containing at least `sample` and `compoundname`, and  
  - `ToxCSM.xlsx or ToxCSM.csv` – semicolon-delimited, containing `compoundname`, toxicity scores, labels, and endpoint metadata.

- **Definition of "High-Risk" or "Non-Safe"**  
  Compounds are included in the breadth calculation if they are **not** labeled as "High Safety" in at least one endpoint. Depending on the project's risk tolerance, this filter can be **tightened** (e.g., only "High Toxicity") or **relaxed**.

- **Breadth Metric**  
  The visualization uses the **count of unique high-risk compound names per (sample, category)** as its driving value. Multiple occurrences of the same compound for a given sample–category combination are counted only once.

- **Name Consistency and Mapping**  
  Accurate integration relies on consistent `compoundname` fields between `BioRemPP_Results.xlsx or BioRemPP_Results.csv` and `ToxCSM.xlsx or ToxCSM.csv`. Synonyms, salts, or different naming conventions should be harmonized upstream to avoid underestimating breadth.

- **Model Dependency**  
  The notion of "risk" is derived from ToxCSM's predictive outputs. The treemap does not directly reflect exposure levels, environmental concentrations, or experimental toxicology; it should be interpreted as a model-informed **relative breadth** of potential mitigation.
