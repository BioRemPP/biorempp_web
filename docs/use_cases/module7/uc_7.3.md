# UC-7.3 — Mapping of Genetic Response to High-Priority Threats

**Module:** 7 – Toxicological Risk Assessment and Profiling  
**Visualization type:** Interactive heatmap (unique gene count per sample–compound pair for high-risk threats)  
**Primary inputs:** `BioRemPP_Results.xlsx or BioRemPP_Results.csv` (sample–compound–gene associations) and `ToxCSM.xlsx or ToxCSM.csv` (predicted toxicity per compound and endpoint)  
**Primary outputs:** Matrix of unique gene counts for high-risk compounds across samples, stratified by toxicological super-category

---

## Scientific Question and Rationale

**Question:** For a given high-level toxicological category (e.g., Genomic Toxicity), which samples possess the most diverse genetic toolkit to degrade the associated high-priority compounds?

This use case acts as a tool for designing **risk-oriented consortia**. By focusing on compounds predicted as **"High Toxicity"** within a selected toxicological super-category, the heatmap quantifies the **genetic response** that each sample can deploy against these priority threats. The color intensity in each cell reflects the number of unique genes associated with a specific sample–compound pair, which can provide a direct proxy for the **depth and complexity** of the underlying degradation machinery.

---

## Data and Inputs

- **Primary data sources:**
  - `BioRemPP_Results.xlsx or BioRemPP_Results.csv` – functional and genetic annotations linking samples, compounds, and genes
  - `ToxCSM.xlsx or ToxCSM.csv` – predicted toxicity scores and labels for compounds across multiple endpoints
- **Key columns:**
  - From `ToxCSM.xlsx or ToxCSM.csv`:
    - `compoundname` – name of the chemical compound
    - `endpoint` / `label_*` – toxicity endpoints and their qualitative labels (e.g., "High Toxicity")
    - `supercategory` (derived) – toxicological super-category (e.g., Genomic, Environmental, Organic)
  - From `BioRemPP_Results.xlsx or BioRemPP_Results.csv`:
    - `sample` – identifier for each biological sample
    - `compoundname` – compound associated with the interaction
    - `genesymbol` – gene symbol or identifier
- **Entities of interest:**
  - **High-Risk Compounds** within a chosen toxicological super-category
  - **Samples** and their associated **gene repertoires** targeting these compounds

---

## Analytical Workflow

1. **User Selection**  
   The user selects a **toxicological super-category** (e.g., "Genomic", "Environmental", "Organic") from an interactive dropdown menu.

2. **Threat Scenario Definition (High-Risk Compound Set)**  
   The `ToxCSM` dataset is filtered to identify all `compoundname` entries that:
   - belong to the selected super-category, and  
   - are labeled **"High Toxicity"** in at least one endpoint within that category.  
   The result is a list of **high-priority compounds** for the chosen threat scenario.

3. **Genetic Response Assessment**  
   The `BioRemPP_Results.xlsx or BioRemPP_Results.csv` table is filtered to include only rows in which:
   - `compoundname` is in the high-priority list obtained in Step 2.  
   This subset captures all known sample–gene associations relevant to the chosen threat class.

4. **Aggregation and Matrix Construction**  
   The filtered data is aggregated to construct a 2D matrix where:
   - rows represent **high-risk compounds** (`compoundname`),  
   - columns represent **Samples** (`sample`), and  
   - each cell value is the **count of distinct `genesymbol`** associated with that sample–compound pair.  
   This count is used as a proxy for the **genetic investment** made by each sample towards each high-risk compound.

5. **Rendering**  
   The sample–compound matrix is rendered as an interactive heatmap:
   - axis labels denote compounds (rows) and samples (columns),  
   - color intensity encodes the unique gene count per cell,  
   - optional hover tooltips expose detailed information (compound, sample, gene count).

---

## How to Read the Plot

- **Dropdown Menu**  
   Use the dropdown to select the **Toxicological Super-Category** of interest (e.g., Genomic, Environmental, Organic). The heatmap updates to reflect high-risk compounds and responses specific to that category.

- **Y-axis (Rows)**  
  Represents individual **High-Risk Compounds** that are predicted as "High Toxicity" within the selected super-category.

- **X-axis (Columns)**  
  Represents individual **Samples**, each potentially encoding a genetic toolkit against one or more of the high-risk compounds.

- **Cell Color**  
  The color intensity of each cell indicates the **count of unique genes** (`genesymbol`) that a sample possesses and associates with a specific high-risk compound:
  - more intense (warmer, darker) colors correspond to higher gene counts,  
  - lighter colors correspond to fewer genes or no detected association.

---

## Interpretation and Key Messages

- **Identifying Elite Specialists**  
  Brightly colored cells ("hotspots") may highlight **strong sample–compound pairings**, where a sample deploys a particularly diverse genetic toolkit against a specific high-risk compound.  
  - A **column with many bright cells** may indicate a **"specialist sample"** that is especially well-equipped to mitigate threats in the selected toxicological category.

- **Key Genetic Responses to Priority Compounds**  
  A **row with many bright cells** may signify a high-risk compound that elicits a strong and diverse genetic response from multiple samples. Such compounds could be:
  - central targets for remediation efforts, or  
  - key drivers of selective pressure in contaminated environments.

- **Targeted Consortium Design**  
  By examining both rows and columns, users can assemble a **consortium** tailored to a specific toxicological domain. For example:
  - when "Genomic" is selected, samples with the brightest columns can be chosen to build a consortium optimized for mitigating genotoxic threats (e.g., carcinogens, DNA-damaging agents).

- **Complementarity vs. Redundancy**  
  Overlapping bright cells across multiple samples for the same compound may indicate **redundant capacity** (robustness), while complementary patterns (different samples covering different compounds) could support **division of labor** in consortium design.

---

## Reproducibility and Assumptions

- **Input Format**  
  The analysis requires two semicolon-delimited tables:
  - `ToxCSM.xlsx or ToxCSM.csv` – containing compound-level toxicity predictions and labels,  
  - `BioRemPP_Results.xlsx or BioRemPP_Results.csv` – containing sample–compound–gene associations.

- **Definition of "High Toxicity"**  
  A compound is considered **high-risk** within a super-category if it is labeled "High Toxicity" for at least one endpoint mapped to that category.

- **Genetic Response Metric**  
  The "genetic response" is quantified as the **count of unique gene symbols** per sample–compound pair. This is treated as a proxy for:
  - the genetic investment, and  
  - the potential mechanistic complexity of the degradation or mitigation strategy.


- **Model and Annotation Limitations**  
  The analysis reflects:
  - the predictive scope and calibration of ToxCSM, and  
  - the coverage and curation of BioRemPP annotations.  
  It does not directly incorporate expression levels, kinetic parameters, or environmental exposure, which may require additional data and analyses.


 
---

## Activity diagram of the use case

![Activity diagram of the use case](uc_7.3.png)


