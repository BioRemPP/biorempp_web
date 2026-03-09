# UC-7.6 — Sample Risk Mitigation Breadth

**Module:** 7 – Toxicological Risk Assessment and Profiling  
**Visualization type:** Interactive treemap (hierarchical breadth of high-risk compound coverage per sample)  
**Primary inputs:** `BioRemPP_Results.xlsx or BioRemPP_Results.csv` (sample–compound interactions) and `ToxCSM.xlsx or ToxCSM.csv` (predicted toxicity and categories)  
**Primary outputs:** Per-sample "Risk Mitigation Breadth Profile" across toxicological categories

---

## Scientific Question and Rationale

**Question:** Which samples have the broadest compound co-annotation coverage, as measured by the variety of distinct high-risk compounds they are co-annotated with within each toxicological category?

This use case characterizes the **annotation-level breadth** of sample–compound co-annotations for predicted high-risk compounds. The treemap quantifies, for each sample and toxicological category, the **number of distinct high-risk compounds** that the sample is co-annotated with. The resulting "Compound Co-annotation Breadth Profile" may highlight samples co-annotated with many different hazardous compounds, as well as samples with broad coverage within a particular toxicological domain (e.g., Genomic, Environmental, Organic). Experimental validation is required to confirm any mitigation capacity.

---

## Data and Inputs

- **Primary data sources:**
  - `BioRemPP_Results.xlsx or BioRemPP_Results.csv` – KO annotation data linking samples and compounds
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
  The **area** of each rectangle is proportional to the **count of unique high-risk compounds** co-annotated with a given `(sample, category)` combination. Larger areas indicate broader compound co-annotation coverage.

- **Color Encoding**  
  Color is typically used to distinguish **Toxicity Categories** at the second level, helping users quickly see which risk domains dominate within each sample.

- **Interactivity (Zoom and Tooltips)**  
  Interactive behavior typically includes:
  - clicking on a rectangle to **zoom in** on a particular sample or category, and  
  - tooltips showing precise values (sample name, category, and unique high-risk compound count).

---

## Representative Output

The image below illustrates a representative output generated by this use case using the example dataset.

*Click on the image to enlarge and explore details.*

<a class="glightbox" href="../uc_7.6_result.png">
    <img src="../uc_7.6_result.png" alt="Representative output for UC-7.6">
</a>

---

## Interpretation and Key Messages

- **Samples with Broad Co-annotation Coverage**
  Samples whose **top-level rectangles** dominate the treemap area are co-annotated with many distinct high-risk compounds across multiple categories. These samples may be candidates for prioritized experimental investigation, though confirmed mitigation capacity requires experimental validation.

- **Category-Specific Annotation Breadth**
  Within a sample, a particularly large rectangle for a single **Toxicity Category** (e.g., Environmental) may indicate high co-annotation breadth within that domain. Such samples could be relevant candidates for targeted investigation in that specific risk category.

- **Annotation-based Complementarity for Hypothesis Generation**
  The treemap can be useful for identifying **complementary annotation profiles** across samples. For example:
  - a sample with broad Genomic annotation coverage can be compared with one that has broad Organic or Environmental coverage,
  - together, they may represent candidates for hypothetical complementary roles (experimental validation required).

- **Breadth vs. Depth**
  This use case emphasizes **breadth of co-annotation coverage**—the variety of high-risk compounds co-annotated—rather than **depth** (e.g., number of KO annotations per compound). It is therefore complementary to analyses that focus on annotation counts and annotation diversity.

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
  The notion of "risk" is derived from ToxCSM's predictive outputs. The treemap does not directly reflect exposure levels, environmental concentrations, or experimental toxicology; it should be interpreted as a model-informed **relative breadth** of compound co-annotation coverage.


 
---

## Activity diagram of the use case

*Click on the image to enlarge and explore details.*

<a class="glightbox" href="../uc_7.6.png">
  <img src="../uc_7.6.png" alt="Activity diagram of the use case">
</a>


