# UC-5.3 — Regulatory Relevance of Samples 

**Module:** 5 – Modeling Interactions of Samples, Genes, and Compounds  
**Visualization type:** Chord diagram (bipartite sample–agency interaction network)  
**Primary inputs:** BioRemPP results table with `sample` and `referenceAG` columns  
**Primary outputs:** Interaction matrix of samples × regulatory agencies (co-occurrence counts)

---

## Scientific Question and Rationale

**Question:** Which samples are most functionally relevant to the compounds monitored by different environmental regulatory agencies?

This use case quantifies how strongly each biological sample is functionally connected to the **regulatory context** represented in the dataset. By summarizing interactions between samples and **environmental or regulatory agencies** (`referenceAG`), the analysis can reveal which samples are most frequently associated with compounds under formal monitoring. A **chord diagram** is used to provide an integrated, system-level view of regulatory relevance, which may highlight both broadly compliant "generalists" and highly focused "specialists".

---

## Data and Inputs

- **Primary data source:** `BioRemPP_Results.xlsx or BioRemPP_Results.csv`  
- **Key columns:**
  - `sample` – identifier for each biological sample
  - `referenceAG` – regulatory or scientific agency label (e.g., WFD, CONAMA, EPC)
- **Accepted format:** semicolon-delimited text table (`.txt` or `.csv`)
- **Derived structure:** interaction matrix with:
  - rows = samples  
  - columns = regulatory agencies  
  - cell = interaction count for each sample–agency pair

---

## Analytical Workflow

1. **Data Loading**  
   The primary results table (`BioRemPP_Results.xlsx or BioRemPP_Results.csv`) is loaded from its semicolon-delimited format.

2. **Filtering**  
   The dataset is filtered to retain only rows containing valid entries for both `sample` and `referenceAG`. Incomplete records are discarded.

3. **Aggregation (Interaction Strength)**  
   The filtered data is grouped by unique `(sample, referenceAG)` pairs:
   - for each pair, the total number of **co-occurrence records** (rows) is counted,  
   - this count provides a measure of **interaction strength** between the sample and the agency's monitored chemical space.

4. **Chord Matrix / Edge List Construction**  
   The aggregated counts are arranged into a matrix or edge list suitable for chord diagram rendering, where:
   - each **sample** is treated as one set of nodes,  
   - each **regulatory agency (`referenceAG`)** is treated as the other set,  
   - the edge weight between them is the interaction count.

5. **Rendering**  
   A **chord diagram** is generated:
   - arcs on the circumference represent both samples and regulatory agencies,  
   - ribbons (chords) connect each sample to the agencies with which it is associated,  
   - chord thickness encodes interaction strength.

---

## How to Read the Plot

- **Outer Arcs (Nodes)**  
  Each colored arc along the circle represents either:
  - a **Sample**, or  
  - a **Regulatory Agency** (`referenceAG`).  
  The length of an arc is proportional to the **total number of interactions** (sum of counts) associated with that entity.

- **Chords (Ribbons)**  
  The ribbons spanning between arcs represent **Sample–Agency** relationships:
  - one end of the ribbon is anchored at a sample arc,  
  - the other at an agency arc.

- **Chord Thickness**  
  The thickness of a chord where it connects to an arc is proportional to the **interaction strength**:
  - **thicker chords** may denote stronger associations (more co-occurrences),  
  - **thinner chords** reflect weaker or less frequent associations.

---

## Interpretation and Key Messages

- **High Regulatory Relevance**  
  A thick chord between a given sample and a specific agency may indicate a **strong functional relevance** of that sample to the agency's monitored chemical space:
  - the sample has many functions associated with compounds under that agency's purview,  
  - suggesting it could be a strong candidate for remediation strategies aligned with that regulatory framework.

- **Identifying Key Samples**  
  - Samples connected by **multiple thick chords** to several agencies may be **regulatory generalists**, relevant across diverse policy or monitoring regimes.  
  - Samples characterized by one **dominant thick chord** could be **specialists**, particularly suited to the pollutant profile emphasized by a specific agency.

- **Agency-Level Impact**  
  Agencies that receive **many substantial chords** from different samples may have a **broad footprint** in the dataset:
  - their monitored compound lists intersect with widely distributed functional capabilities,  
  - suggesting that the system may be well equipped to address their priority pollutants.

- **Strategic Insight for Design and Policy Alignment**  
  The chord diagram can help align **consortium design** with **regulatory priorities**:
  - samples can be selected or combined based on how well they collectively cover the regulatory agencies of interest,  
  - potentially facilitating the design of bioremediation solutions that are both biologically effective and policy-aware.

---

## Reproducibility and Assumptions

- **Input Format**  
  The analysis assumes a semicolon-delimited table containing at least the columns `sample` and `referenceAG`.

- **Interaction Definition**  
  Interaction strength is defined as the **total number of co-occurrence records** for each `(sample, referenceAG)` pair in the raw data:
  - multiple rows linking the same sample and agency (e.g., via different compounds or genes) increase the aggregate count,  
  - the chord diagram therefore reflects overall **intensity of association**, not unique compound or KO counts.

- **Scope and Limitations**  
  - The visualization summarizes **frequency of functional linkage** to regulatory contexts, not compliance status, toxicity levels, or pathway completeness.  
  - It should be interpreted as a high-level map to prioritize detailed downstream analyses, rather than a standalone compliance assessment.
