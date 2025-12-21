# UC-5.6 — Compound–Compound Interaction Network (Based on Shared Genes)

**Module:** 5 – Modeling Interactions of Samples, Genes, and Compounds  
**Visualization type:** Weighted compound–compound network (shared-gene edges, force-directed layout)  
**Primary inputs:** BioRemPP results table with `compoundname` and `genesymbol` columns  
**Primary outputs:** Compound–compound interaction network weighted by number of shared genes; node-level connectivity (degree)

---

## Scientific Question and Rationale

**Question:** Which chemical compounds may be processed by similar enzymatic machinery, as inferred from their shared interactions with the same genes, and what is the structure of these chemically related groups?

This use case infers **functional similarity between compounds** by examining whether they are targeted by overlapping sets of genes across all biological samples. Compounds that repeatedly share the same enzymatic toolkit could be **structurally related**, **pathway-connected intermediates**, or typical **co-contaminants** that are addressed by similar metabolic solutions. By constructing a **compound–compound network** where edges represent shared genes and edge weights encode the number of these shared genes, the analysis may reveal **chemical clusters**, highly connected **hub compounds**, and **bridge compounds** that link distinct chemical groups.

---

## Data and Inputs

- **Primary data source:** `BioRemPP_Results.xlsx or BioRemPP_Results.csv`  
- **Key columns:**
  - `compoundname` – name (or identifier) of the chemical compound
  - `genesymbol` – gene symbol or identifier associated with that compound in at least one sample
- **Accepted format:** semicolon-delimited text table (`.txt` or `.csv`)
- **Derived structures:**
  - mapping of each compound to its set of unique genes,  
  - weighted compound–compound edge list based on the count of shared genes.

---

## Analytical Workflow

1. **Data Loading**  
   The primary results table (`BioRemPP_Results.xlsx or BioRemPP_Results.csv`) is loaded from its semicolon-delimited format.

2. **Compound-to-Gene Mapping**  
   For each unique `compoundname`, a **gene set** is constructed:
   - all unique `genesymbol` entries associated with that compound are collected into a set,  
   - this set represents the **enzymatic interaction profile** of that compound.

3. **Graph Construction (Compound–Compound Network)**  
   A network graph is built where:
   - each unique **compound** is added as a **node**,  
   - all unique pairs of compounds are evaluated; for each pair:
     - the intersection of their gene sets is computed,  
     - if the intersection is non-empty, an **edge** is added between the two compounds,  
     - the **edge weight** is set to the number of shared unique genes.

4. **Layout and Styling**  
   A **force-directed layout** is used to compute node positions:
   - compounds with many strong connections tend to cluster toward the center,  
   - sparsely connected compounds are positioned closer to the periphery.  
   Node attributes are then computed:
   - **degree** (number of connected compound neighbors) is calculated for each node,  
   - this degree is mapped to node color to highlight highly connected compounds.

5. **Rendering**  
   The network is rendered as an interactive plot:
   - nodes represent individual compounds,  
   - edges represent compound–compound links based on shared genes,  
   - **edge thickness** is proportional to edge weight (number of shared genes),  
   - **node color** is proportional to degree (number of compound neighbors), with a color bar indicating the scale.

---

## How to Read the Plot

- **Nodes (Compounds)**  
  Each point in the graph is a **Compound Name**:
  - its position is determined by the force-directed layout,  
  - its **color** encodes its **degree** (how many other compounds it is connected to).

- **Edges (Compound–Compound Links)**  
  Each line between two nodes represents a **functional link**:
  - the two compounds are targeted by at least one common gene,  
  - the **thickness** of the edge is proportional to the **number of shared genes** (edge weight).

- **Node Color Scale**  
  A color bar indicates the range of node degrees:
  - **brighter/warmer colors** correspond to **high-degree compounds** (hubs),  
  - cooler or darker colors correspond to compounds with fewer connections.

- **Overall Structure**  
  The spatial arrangement may reflect the **organization of chemically related groups**:
  - dense regions could correspond to clusters of compounds sharing many genes,  
  - more isolated nodes might suggest compounds with relatively unique enzymatic profiles.

---

## Interpretation and Key Messages

- **Chemical Clusters**  
  Dense clusters of interconnected nodes may represent **groups of functionally related compounds**:
  - they could be structurally similar molecules,  
  - intermediates in the same degradation pathway, or  
  - co-contaminants processed by a shared enzymatic toolkit.

- **Hub Compounds**  
  Brightly colored, highly connected nodes may be **hub compounds**:
  - they share genes with many other compounds,  
  - they could represent central intermediates or widely distributed pollutants that intersect with multiple degradation pathways.

- **Bridge Compounds**  
  Compounds that connect distinct clusters may act as **functional bridges**:
  - they could link two different chemical classes through shared enzymes,  
  - they may indicate metabolic cross-talk or convergence between distinct pathways.

- **Specialized Compounds**  
  Nodes on the periphery with few connections may represent **specialized targets**:
  - compounds that require a distinct or limited set of genes,  
  - possibly relevant for niche contamination scenarios or specific environmental contexts.

---

## Reproducibility and Assumptions

- **Input Format**  
  The analysis assumes a semicolon-delimited table containing at least the columns `compoundname` and `genesymbol`.

- **Functional Link Definition**  
  - A functional link between two compounds is defined by the **presence of at least one shared gene** in their interaction sets.  
  - **Edge weight** is the number of shared unique genes.  
  - **Node color** reflects **connectivity to other compounds** (degree), *not* the total number of unique genes that target each compound.

- **Network Properties**  
  - The network is typically treated as **undirected and weighted**: edges encode symmetric relationships based on shared genes and carry a weight proportional to that overlap.  
  - The force-directed layout can be made reproducible by fixing a random seed.

- **Interpretation Scope**  
  - The network captures **association patterns** inferred from shared enzymatic machinery; it does not directly encode chemical structure, thermodynamics, or kinetic parameters.  
  - Co-connectivity should be seen as **hypothesis-generating evidence** for chemical relatedness or pathway co-membership, requiring further structural, biochemical, or environmental validation.
