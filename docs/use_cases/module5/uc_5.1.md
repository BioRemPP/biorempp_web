# UC-5.1 — Sample-Compound Class Interaction

**Module:** 5 – Modeling Interactions of Samples, Genes, and Compounds  
**Visualization type:** Chord diagram (bipartite sample–compound-class interaction network)  
**Primary inputs:** BioRemPP results table with `sample` and `compoundclass` columns  
**Primary outputs:** Interaction matrix of samples × compound classes (co-occurrence counts)

---

## Scientific Question and Rationale

**Question:** Which samples are most strongly associated with which chemical classes, and what might this reveal about their metabolic specializations?

This use case maps the **interaction strength** between each biological sample and the different **classes of chemical compounds**. By summarizing how often each sample is associated with each compound class, and visualizing these relationships as a **chord diagram**, the analysis can provide an intuitive, systems-level overview of the interaction landscape. It may highlight both broad generalists that span many classes and specialists with strong preferences for specific chemical domains.

---

## Data and Inputs

- **Primary data source:** `BioRemPP_Results.xlsx or BioRemPP_Results.csv`  
- **Key columns:**
  - `sample` – identifier for each biological sample
  - `compoundclass` – categorical label for the chemical class of each compound
- **Accepted format:** semicolon-delimited text table (`.txt` or `.csv`)
- **Derived structure:** interaction matrix with:
  - rows = samples  
  - columns = compound classes  
  - cell = interaction count for each sample–class pair

---

## Analytical Workflow

1. **Data Loading**  
   The primary results table (`BioRemPP_Results.xlsx or BioRemPP_Results.csv`) is loaded from its semicolon-delimited format.

2. **Filtering**  
   The dataset is filtered to retain only complete entries containing both a valid `sample` and a `compoundclass`. Rows with missing values in either field are removed.

3. **Aggregation (Interaction Strength)**  
   The filtered data is grouped by each unique `(sample, compoundclass)` pair.  
   - For each pair, the total number of **co-occurrences** (rows) is counted.  
   - This count serves as the **interaction strength** between that sample and that compound class.

4. **Chord Matrix Construction**  
   The aggregated counts are arranged into a matrix or edge list suitable for chord diagram rendering, where:
   - each **sample** is treated as a source node,  
   - each **compound class** is treated as a target node, and  
   - the edge weight is the interaction count.

5. **Rendering**  
   A **chord diagram** is generated:
   - arcs on the circumference represent samples and compound classes,  
   - ribbons (chords) connect each sample to the classes with which it interacts,  
   - chord thickness encodes interaction strength.

---

## How to Read the Plot

- **Outer Arcs (Nodes)**  
  Each colored arc along the circle represents either:
  - a **Sample**, or  
  - a **Compound Class**.  
  The length of an arc is proportional to the **total number of interactions** (sum of counts) associated with that entity.

- **Chords (Ribbons)**  
  The ribbons spanning between arcs represent individual **Sample–Compound Class** interactions:
  - one end of the ribbon is anchored at a sample arc,  
  - the other end at a compound class arc.

- **Chord Thickness**  
  The thickness of a chord at its connection points is proportional to the **interaction count** for that sample–class pair:
  - **thicker chords** indicate stronger associations (more co-occurrences),  
  - **thinner chords** indicate weaker or less frequent associations.

---

## Interpretation and Key Messages

- **Strong Associations and Specialization**  
  A thick chord between a specific sample and a given compound class may indicate a **strong association**:
  - the sample interacts frequently with compounds from that class,  
  - which may suggest potential **metabolic specialization** or preferential adaptation to that chemical domain.

- **Generalists vs. Specialists**  
  - A sample with **multiple substantial chords** connecting to several compound classes may behave as a **generalist**, displaying broad degradative capabilities across diverse chemical spaces.  
  - A sample whose representation is dominated by one or a few **very thick chords** could be a **specialist**, particularly well-adapted to a narrower set of chemical classes.

- **Dominant Chemical Classes**  
  Compound classes that receive **many thick chords from multiple samples** may emerge as:
  - **major targets** of metabolic activity within the system, and  
  - potential focal points for bioremediation efforts, as they are widely addressed by the available biological repertoire.

- **Interaction Landscape Overview**  
  The overall pattern of chords can provide a **global view** of how functional potential is distributed:
  - identifying central samples and classes that structure the network,  
  - potentially revealing imbalances, redundancies, or gaps in coverage.

---

## Reproducibility and Assumptions

- **Input Format**  
  The analysis assumes a semicolon-delimited table containing at least the columns `sample` and `compoundclass`.

- **Interaction Definition**  
  Interaction strength is defined as the **total number of co-occurrence records** for each `(sample, compoundclass)` pair in the raw table:
  - multiple entries for the same pair (e.g., different compounds within the same class, or multiple genes linked to that class) increase the aggregate count,  
  - the chord diagram thus reflects overall interaction intensity rather than unique compound counts.

- **Scope of Interpretation**  
  The chord diagram summarizes **association frequency**, not mechanistic detail:
  - it does not directly encode pathway completeness, kinetic efficiency, or regulatory control,  
  - but it can provide a high-level map that may guide more detailed, pathway-focused or gene-level analyses in subsequent use cases.
