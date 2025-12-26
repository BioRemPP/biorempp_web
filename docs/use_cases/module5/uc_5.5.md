# UC-5.5 — Gene–Gene Interaction Network (Based on Shared Compounds) 

**Module:** 5 – Modeling Interactions of Samples, Genes, and Compounds  
**Visualization type:** Weighted gene–gene network (shared-compound edges, force-directed layout)  
**Primary inputs:** BioRemPP results table with `genesymbol` and `compoundname` columns  
**Primary outputs:** Gene–gene interaction network weighted by number of shared compounds; node-level connectivity (degree)

---

## Scientific Question and Rationale

**Question:** Which genes may exhibit potential functional relationships, as inferred from their shared interactions with the same chemical compounds, and what is the structure of these functional modules?

This use case infers **functional relationships between genes** by examining whether they interact with overlapping sets of chemical compounds across all biological samples. Genes that repeatedly co-target the same compounds could participate in related pathways, complementary steps in a degradation route, or co-regulated responses. By constructing a **gene–gene network** where edges represent shared compounds and edge weights encode the number of these shared targets, the analysis may highlight **functional modules**, highly connected **hub genes**, and potential **bridge genes** that connect distinct metabolic subsystems.

---

## Data and Inputs

- **Primary data source:** `BioRemPP_Results.xlsx or BioRemPP_Results.csv`  
- **Key columns:**
  - `genesymbol` – gene symbol or identifier
  - `compoundname` – name (or identifier) of the chemical compound associated with that gene in at least one sample
- **Accepted format:** semicolon-delimited text table (`.txt` or `.csv`)
- **Derived structures:**
  - mapping of each gene to its set of unique compounds,  
  - weighted gene–gene edge list based on the count of shared compounds.

---

## Analytical Workflow

1. **Data Loading**  
   The primary results table (`BioRemPP_Results.xlsx or BioRemPP_Results.csv`) is loaded from its semicolon-delimited format.

2. **Gene-to-Compound Mapping**  
   For each unique `genesymbol`, a **compound set** is constructed:
   - all unique `compoundname` entries associated with that gene are collected into a set,  
   - this set represents the **chemical interaction profile** of that gene.

3. **Graph Construction (Gene–Gene Network)**  
   A network graph is built where:
   - each unique **gene** is added as a **node**,  
   - all unique pairs of genes are evaluated; for each pair:
     - the intersection of their compound sets is computed,  
     - if the intersection is non-empty, an **edge** is added between the two genes,  
     - the **edge weight** is set to the number of shared unique compounds.

4. **Layout and Styling**  
   A **force-directed layout** is used to compute node positions:
   - genes with many strong connections tend to be drawn closer to one another, forming clusters,  
   - sparsely connected genes are placed closer to the periphery.  
   Node attributes are then computed:
   - **degree** (number of connected gene neighbors) is calculated for each node,  
   - this degree is mapped to node color to highlight highly connected genes.

5. **Rendering**  
   The network is rendered as an interactive plot:
   - nodes represent individual genes,  
   - edges represent gene–gene links based on shared compounds,  
   - **edge thickness** is proportional to edge weight (number of shared compounds),  
   - **node color** is proportional to degree (number of gene neighbors), with a color bar indicating the scale.

---

## How to Read the Plot

- **Nodes (Genes)**  
  Each point in the graph is a **Gene Symbol**:
  - the position is determined by the force-directed layout,  
  - the **color** of a node encodes its **degree** (how many other genes it is connected to).

- **Edges (Gene–Gene Links)**  
  Each line between two nodes represents a **functional link**:
  - two genes share at least one common compound target,  
  - the **thickness** of the edge is proportional to the **number of shared compounds** (edge weight).

- **Color Scale for Nodes**  
  A color bar indicates the range of node degrees:
  - nodes with **brighter/warmer colors** correspond to **high-degree genes** (hubs),  
  - nodes with cooler or darker colors correspond to lower-degree genes.

- **Overall Structure**  
  The spatial arrangement may reflect the **network's modular organization**:
  - dense clusters could indicate groups of genes with many shared compound partners,  
  - sparsely connected or isolated nodes might indicate more specialized or infrequent relationships.

---

## Interpretation and Key Messages

- **Functional Modules**  
  Dense clusters of interconnected nodes may represent **functional gene modules**:
  - genes in the same cluster tend to act on similar sets of compounds,  
  - they are good candidates for belonging to the same pathway, regulon, or coordinated response involved in bioremediation.

- **Hub Genes**  
  Brightly colored, centrally located nodes with many edges may be **hub genes**:
  - they interact (via shared compounds) with many other genes,  
  - they could encode enzymes with broad substrate specificity, regulatory nodes, or central metabolic components that link multiple pathways.

- **Bridge Genes**  
  Genes that connect otherwise distinct clusters may act as **bridges**:
  - they could link different metabolic routes or chemical families,  
  - their disruption or modulation might have system-level effects by altering information or flux between modules.

- **Peripheral and Specialized Genes**  
  Nodes on the network's periphery with few connections may represent **specialized genes**:
  - they could be important for rare or niche substrates,  
  - they can still be critical in targeted bioremediation scenarios even if they are not highly connected.

---

## Reproducibility and Assumptions

- **Input Format**  
  The analysis assumes a semicolon-delimited table containing at least the columns `genesymbol` and `compoundname`.

- **Functional Link Definition**  
  - A functional link between two genes is defined by the **presence of at least one shared compound** in their interaction sets.  
  - **Edge weight** is the number of shared unique compounds.  
  - **Node color** reflects **gene–gene connectivity** (degree), *not* the total number of gene–compound interactions.

- **Network Properties**  
  - The network is typically treated as **undirected and weighted**: directionality is not inferred, but the strength of association is encoded in edge weights.  
  - The layout is based on a force-directed algorithm that can be made reproducible by fixing a random seed.

- **Interpretation Scope**  
  - The network captures **association patterns** inferred from shared compound targets; it does not directly encode regulatory direction, reaction stoichiometry, or kinetic parameters.  
  - Co-connectivity should be interpreted as **hypothesis-generating evidence** for functional relationships that require additional biochemical, genomic, or regulatory validation.


 
---

## Activity diagram of the use case

*Click on the image to enlarge and explore details.*

<a class="glightbox" href="../uc_5.5.png">
  <img src="../uc_5.5.png" alt="Activity diagram of the use case">
</a>


