# UC-7.7 — Sample Risk Mitigation Depth

**Module:** 7 – Toxicological Risk Assessment and Profiling  
**Visualization type:** Interactive treemap (hierarchical depth of gene–compound interactions per sample)  
**Primary inputs:** `BioRemPP_Results.xlsx or BioRemPP_Results.csv` (sample–compound–gene interactions) and `ToxCSM.xlsx or ToxCSM.csv` (predicted toxicity and categories)  
**Primary outputs:** Per-sample "Risk Mitigation Depth Profile" across toxicological categories and compounds

---

## Scientific Question and Rationale

**Question:** Which samples invest the most significant genetic resources (i.e., the highest number of interactions) in mitigating different categories of toxicological risk?

This use case focuses on the **depth** or **intensity** of the functional response rather than the variety of compounds. The treemap builds a **Risk Mitigation Depth Profile** by quantifying, for each sample and toxicological category, how many **gene–compound interactions** are deployed against predicted high-risk compounds. Larger areas correspond to more interactions, which may highlight where each sample concentrates its genetic machinery and which compounds might demand particularly complex or multi-faceted responses.

---

## Data and Inputs

- **Primary data sources:**
  - `BioRemPP_Results.xlsx or BioRemPP_Results.csv` – functional interaction data linking samples, compounds, and genes
  - `ToxCSM.xlsx or ToxCSM.csv` – predicted toxicity scores and qualitative labels for compounds
- **Key columns:**
  - From `BioRemPP_Results.xlsx or BioRemPP_Results.csv`:
    - `sample` – identifier for each biological sample
    - `compoundname` – name of the chemical compound
    - `genesymbol` – gene symbol or identifier associated with the interaction
  - From `ToxCSM.xlsx or ToxCSM.csv`:
    - `compoundname` – chemical compound name (to be matched with BioRemPP)
    - `endpoint` / `label_*` – endpoint-specific toxicity labels (e.g., "High Toxicity", "High Safety")
    - `supercategory` (derived) – mapped toxicological super-category (e.g., Genomic, Environmental, Organic)
- **Hierarchy represented in the treemap:**
  - Level 1: **Sample**  
  - Level 2: **Toxicity Category** (super-category)  
  - Level 3: **Compound Name**  

The quantitative value is the **total count of gene–compound interactions** for each `(sample, category, compound)` path.

---

## Analytical Workflow

1. **Data Loading and Integration**  
   The primary results tables `BioRemPP_Results.xlsx or BioRemPP_Results.csv` and `ToxCSM.xlsx or ToxCSM.csv` are loaded from their semicolon-delimited formats.

2. **Risk Filtering in ToxCSM**  
   The `ToxCSM` dataset is reshaped into a **long format** (one row per compound–endpoint pair) and filtered to retain only entries corresponding to compounds with a **non-trivial predicted risk**, i.e., compounds that are not labeled as "High Safety". The remaining set defines risk-relevant compounds.

3. **Endpoint-to-Category Mapping**  
   Individual toxicological endpoints are mapped to broader **Toxicity Categories** (e.g., Genomic, Environmental, Organic) using a predefined lookup table. This mapping assigns each endpoint to its parent super-category.

4. **Data Merging**  
   The risk-filtered ToxCSM data is merged with `BioRemPP_Results.xlsx or BioRemPP_Results.csv` on `compoundname`, connecting:
   - samples,  
   - compounds,  
   - genes, and  
   - their associated toxicological categories.

5. **Aggregation for Depth**  
   The merged dataset is grouped along the full hierarchy:  
   `sample` → `Toxicity Category` → `compoundname`.  
   For each unique path, the **total number of gene–compound interactions** is computed (e.g., using `.size()` on the rows belonging to that path). This count is used as a proxy for **genetic investment** or **response depth**.

6. **Rendering as Treemap**  
   The aggregated data is rendered as an **interactive treemap**:
   - top-level rectangles represent **Samples**,  
   - nested rectangles at the second level represent **Toxicity Categories**,  
   - third-level rectangles represent individual **Compounds**,  
   - the **area** of each rectangle is proportional to the total interaction count for that path.

---

## How to Read the Plot

- **Nested Rectangles (Hierarchy)**  
  The treemap uses nested rectangles to encode the hierarchical structure:
  - the largest, outer rectangles correspond to **Samples**,  
  - within each sample, rectangles represent **Toxicity Categories**,  
  - within each category, smaller rectangles represent individual **Compounds**.

- **Area (Values)**  
  The **area** of each rectangle is proportional to the **total number of gene–compound interactions** associated with that `(sample, category, compound)` path. Larger areas indicate greater depth of genetic investment.

- **Color Encoding**  
  Color is typically used to distinguish **Toxicity Categories** at the second level. This makes it easy to visually group compounds and see which categories dominate a sample's depth profile.

- **Interactivity (Zoom and Tooltips)**  
  The treemap is interactive:
  - clicking on a rectangle allows the user to **zoom in** on a specific sample or category,  
  - tooltips reveal details such as sample name, toxicity category, compound name, and total interaction count.

---

## Interpretation and Key Messages

- **High Genetic Investment**  
  Large rectangles (especially at the compound level) may indicate **high genetic investment** by a sample towards mitigating risk associated with a particular compound or category. This could correspond to multi-gene or multi-pathway responses.

- **Sample Specialization in Depth**  
  Examining the second level (Toxicity Category) within a sample may reveal **depth specialization**:
  - a sample with a particularly large Genomic rectangle could be a specialist in deploying a deep, complex genetic response against **genotoxic** compounds,  
  - similarly, dominance of Environmental or Organic categories may signal focused investment in those risk domains.

- **Complex Targets**  
  Compounds that appear as **large rectangles at the third level** may be inferred as **complex targets**, potentially requiring substantial and multifaceted genetic responses. These compounds could:
  - be structurally or chemically challenging, or  
  - participate in multi-step degradation pathways involving many distinct genes.

- **Complementarity with Breadth (UC-7.6)**  
  This visualization complements the **breadth-oriented** perspective in UC-7.6:
  - UC-7.6 emphasizes *how many different high-risk compounds* a sample can address,  
  - UC-7.7 emphasizes *how intensively* a sample responds to those compounds in terms of genetic interactions.  
  Together, they may support a balanced design of consortia combining broad coverage with deep, robust responses to critical targets.

---

## Reproducibility and Assumptions

- **Input Format**  
  The analysis requires:
  - `BioRemPP_Results.xlsx or BioRemPP_Results.csv` – semicolon-delimited, containing at least `sample`, `compoundname`, and `genesymbol`, and  
  - `ToxCSM.xlsx or ToxCSM.csv` – semicolon-delimited, containing `compoundname`, toxicity scores, labels, and endpoint metadata.

- **Definition of Risk-Relevant Compounds**  
  Compounds are retained if they are **not labeled as "High Safety"** in at least one endpoint. This can be tightened (e.g., only "High Toxicity") or relaxed depending on the desired risk threshold.

- **Depth Metric**  
  The value driving the visualization is the **total count of interactions (rows)** in the merged dataset per `(sample, category, compound)`:
  - repeated gene–compound associations increase this count,  
  - the metric prioritizes **depth of functional response** rather than the number of unique entities.

- **Name Consistency and Mapping**  
  Reliable merging requires consistent `compoundname` usage between `BioRemPP_Results.xlsx or BioRemPP_Results.csv` and `ToxCSM.xlsx or ToxCSM.csv`. Synonyms and naming variants should be harmonized upstream.

- **Model and Annotation Context**  
  As with other UC-7 analyses, the concept of risk is based on **ToxCSM predictions**, and interaction depth is based on the coverage and granularity of **BioRemPP annotations**. The treemap should be interpreted as a model- and annotation-informed view of genetic investment, rather than a direct measurement of in situ metabolic flux or expression levels.
