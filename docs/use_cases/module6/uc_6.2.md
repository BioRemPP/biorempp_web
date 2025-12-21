# UC-6.2 — Biological Interaction Flow

**Module:** 6 – Hierarchical and Flow-based Functional Analysis  
**Visualization type:** Three-stage alluvial / Sankey diagram  
**Primary inputs:** BioRemPP results table with `sample`, `compoundclass`, and `enzyme_activity`  
**Primary outputs:** Multi-stage flow network from samples → compound classes → enzyme activities

---

## Scientific Question and Rationale

**Question:** How is the functional potential of each sample distributed across different chemical classes, and which enzymatic activities are predominantly employed for each?

This use case characterizes the **metabolic strategies** of the biological samples by tracing how their functional potential is deployed across **chemical classes** and **enzyme activities**. By organizing the information into a **three-stage alluvial diagram**, the analysis can reveal which compound classes are most heavily targeted by each sample and which enzymatic functions are preferentially used to process them. The thickness of each flow encodes how frequently a given combination occurs, which can provide a quantitative, pathway-like view of **specialization vs. generalism** and **enzyme versatility** within the system.

---

## Data and Inputs

- **Primary data source:** `BioRemPP_Results.xlsx or BioRemPP_Results.csv`  
- **Key columns:**
  - `sample` – identifier for each biological sample
  - `compoundclass` – chemical class/category of the compound
  - `enzyme_activity` – functional label for the enzymatic activity (e.g., monooxygenase, dehydrogenase)
- **Accepted format:** semicolon-delimited text table (`.txt` or `.csv`)

- **Conceptual flow (stages):**  
  1. **Sample** (`sample`)  
  2. **Compound Class** (`compoundclass`)  
  3. **Enzyme Activity** (`enzyme_activity`)

---

## Analytical Workflow

1. **Data Loading**  
   The primary results table (`BioRemPP_Results.xlsx or BioRemPP_Results.csv`) is loaded from its semicolon-delimited format.

2. **Path Definition**  
   A three-stage path is defined for each row using:
   - `sample` → `compoundclass` → `enzyme_activity`.  
   Each complete combination represents a **biological interaction flow** from a given sample, through a chemical class, to a specific enzymatic function.

3. **Aggregation of Flows**  
   The data is grouped by each unique three-step path:
   - for every unique `(sample, compoundclass, enzyme_activity)` combination,  
   - the number of occurrences is counted.  
   This **count** becomes the **flow value** that determines ribbon thickness.

4. **Link Construction for Sankey / Alluvial Diagram**  
   The aggregated paths are transformed into a set of linked pairs suitable for a Sankey diagram:
   - **Stage 1 → Stage 2:** `sample` → `compoundclass`  
   - **Stage 2 → Stage 3:** `compoundclass` → `enzyme_activity`  
   Node indices and link values are encoded in the input format required by the plotting library.

5. **Rendering**  
   The data is rendered as an **interactive alluvial (Sankey) diagram**:
   - three vertical columns represent the stages,  
   - nodes within each column represent unique entities (samples, compound classes, enzyme activities),  
   - ribbons connecting them represent flows weighted by their aggregated counts.

---

## How to Read the Plot

- **Vertical Columns (Stages)**  
  From left to right, the columns represent:
  1. **Sample**  
  2. **Compound Class**  
  3. **Enzyme Activity**

- **Nodes within Columns**  
  Each node is a unique entity at that stage:
  - a specific sample, a specific compound class, or a specific enzyme activity.  
  Node size (height) is proportional to the **total flow** entering or leaving that node.

- **Flows (Ribbons)**  
  The ribbons connecting nodes represent **interaction flows**:
  - a ribbon from a sample to a compound class shows how strongly that sample is associated with that class,  
  - a ribbon from a compound class to an enzyme activity shows how strongly that class is linked to that enzymatic function.

- **Flow Thickness**  
  The **thickness** of each ribbon is proportional to the **number of co-occurrences** of that specific path in the data:
  - thicker ribbons may indicate **more dominant or frequently observed** metabolic strategies.

- **Interactivity**  
  In the interactive version:
  - hovering over nodes or flows reveals labels and numeric values (counts),  
  - nodes can be dragged vertically to reduce overlap and improve readability.

---

## Interpretation and Key Messages

- **Dominant Metabolic Strategies per Sample**  
  The thickest flows emerging from a given sample may highlight its **primary metabolic strategies**:
  - for example, a strong flow from a sample to an **aromatic** compound class and then to a **monooxygenase** activity may suggest that aromatic transformation via monooxygenation is a central pathway for that sample.

- **Sample Specialization vs. Generalism**  
  - A sample dominated by a **few very thick flows** (one or two classes and enzyme activities) may be indicative of a **specialist**, optimized for a narrower set of substrates or pathways.  
  - A sample whose flows **branch out across many compound classes and enzyme activities** could behave as a **functional generalist**, contributing to broad chemical coverage.

- **Enzyme Versatility and Key Functions**  
  - **Enzyme activity nodes** that receive flows from many different compound classes, or from many samples via multiple classes, may indicate **versatile functions**—enzymes that can act on diverse chemical backgrounds.  
  - These versatile activities could be prime targets for deeper mechanistic study or for engineering efforts.

- **Chemical Class Profiles**  
  The intermediate column for **compound classes** may reveal:
  - which classes are focal points of metabolic investment,  
  - and which enzymatic activities are preferentially associated with each class, potentially providing insight into likely pathway architectures.

---

## Reproducibility and Assumptions

- **Input Format**  
  The analysis assumes a semicolon-delimited table containing at least the columns:
  - `sample`, `compoundclass`, and `enzyme_activity`.

- **Flow Definition**  
  - Each unique `(sample, compoundclass, enzyme_activity)` combination contributes a unit count to the corresponding path.  
  - The **strength of a flow** is defined as the **total count of co-occurrences** for that path in the raw data.

- **Scope and Limitations**  
  - The alluvial diagram encodes **frequency of observed associations**, not reaction rates, kinetic efficiencies, or thermodynamic feasibility.  
  - It should be interpreted as a **structural and comparative overview** of which metabolic routes are most frequently represented, and not as a direct measure of in situ activity or performance.
