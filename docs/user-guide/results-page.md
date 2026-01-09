# Results Page

This page documents the structure and organization of the Results Page analytical interface.

---

## Purpose of the Results Page

The Results Page is the **analytical workspace** where processed data is displayed after successful upload and validation. It provides access to integrated database results and 56 analytical use cases organized into 8 specialized modules.

The page is dynamically generated based on uploaded KO annotations and remains accessible for the duration of the session (4 hours).

---

## Global Organization of Results

### Accordion-Based Layout

Results are organized as **sequential accordion sections** that expand on user interaction:

1. **Overview Card** — Summary statistics (samples detected, total KOs, processing time)
2. **Database Integration Tables** — Merged data display (BioRemPP, KEGG, HADEG, ToxCSM)
3. **Analytical Modules** — 8 thematic sections containing 56 use cases total

### Information Flow

```
Input (KO annotations)
  ↓
Validation (format, limits, encoding)
  ↓
Database Merging (BioRemPP + KEGG + HADEG + ToxCSM)
  ↓
Results Page Display (Overview + Databases + Modules)
  ↓
On-Demand Use Case Execution
```

---

## Analytical Modules and Use Cases

The Results Page organizes analytical workflows into **8 thematic modules**:

| Module | Focus | Use Cases | Primary Output Types |
|--------|-------|-----------|---------------------|
| **Module 1** | Comparative Assessment (Databases, Samples, Regulatory) | 8 | Heatmaps, Stacked bar charts, UpSet plots |
| **Module 2** | Exploratory Analysis (Functional Potential Ranking) | 8 | Bar charts, Box-scatter plots |
| **Module 3** | System Structure (Clustering, Similarity, Co-occurrence) | 7 | Correlograms, Dendrograms, Scatter plots |
| **Module 4** | Functional and Genetic Profiling | 7 | Bar charts, Dot plots, Heatmaps, Radar charts, Sunbursts |
| **Module 5** | Modeling Interactions (Samples, Genes, Compounds) | 7 | Chord diagrams, Network graphs |
| **Module 6** | KEGG Pathway Completeness | 6 | Sankey diagrams, Treemaps |
| **Module 7** | Toxicological Risk Assessment | 7 | Box-scatter plots, Chord diagrams, Density plots, Heatmaps, Treemaps |
| **Module 8** | Assembly of Functional Consortia | 6 | Frozenset visualizations, Heatmaps, UpSet plots |

**Total:** 56 use cases across 8 modules

### Module Structure

Each module contains:

- Thematic focus addressing specific research questions
- Multiple use cases (~8 per module)
- Accordion-based layout (one use case per expandable panel)
- Independent execution (no dependencies between modules)

---

## Use Case Execution Model

### On-Demand Execution

Use cases are **not pre-computed**. Each analysis:

- Executes when user expands accordion and clicks "Run Analysis"
- Generates visualization + data table dynamically
- Returns results within the same accordion panel

### Module Independence

Modules are **conceptually independent**:

- No required execution order
- Results from one module do not affect others
- Users may analyze any subset of modules
- All modules analyze the same merged dataset

### Cross-Module Data Integrity

All modules use **identical input data**:

- Same sample count across all analyses
- Same KO coverage in all modules
- Consistent database integration results

This ensures reproducible comparisons when interpreting results across modules.

---

## Relationship Between Visualizations and Tables

### Dual Output Structure

Every use case produces two complementary outputs:

1. **Interactive Visualization** (Plotly-based)
    - Dynamic tooltips with detailed information
    - Zoom, pan, reset controls
    - Legend filtering (click to toggle series)

2. **Data Table** (AG Grid or Dash DataTable)
    - Sortable columns
    - Searchable/filterable rows
    - Paginated display

### Data Provenance and Consistency

**Critical principle:** Tables contain **exactly the data** used to generate the corresponding visualization.

- No hidden filtering post-visualization
- Sample traceability via "Sample" column
- Parameter transparency (documented in use case description)

### Display vs. Underlying Data

**Display data** (on-screen):

- May apply Top N restrictions for clarity
- Aggregated for visualization readability
- Optimized for interactive exploration

**Underlying data** (available for export):

- Complete dataset before visualization filters
- All database fields retained
- See Downloads section for export details

---

## Session-Based Nature of Results

### Data Retention Policy

Results are **session-dependent** and **not persistent**:

- **Storage mechanism:** In-memory (Redis cache)
- **Lifetime:** 4 hours of inactivity or until browser closure
- **Deletion:** Automatic and irreversible upon session termination

### User Implications

**Session management:**

- No persistent storage of results
- No retrieval from browser history
- Keep browser tab open during active analysis
- Re-upload required if session expires

### Privacy and Security

Session-based architecture ensures:

- Complete session isolation (unique session IDs)
- No permanent user data retention
- Automatic data purging after timeout
- No cross-user data access

---

## Limitations of On-Screen Results

### Display Constraints

**Visualizations:**

- Aggregation by category, pathway, or compound class
- Performance limits for very large datasets

**Tables:**

- Paginated display (default: 10-50 rows per page)
- Search/filter applied to displayed subset

### Resolution Limitations

BioRemPP provides **functional inference**, not experimental measurements:

**What results represent:**

- Genetic potential (gene presence/absence)
- Pathway completeness (based on KO assignments)
- Computational predictions (toxicity, regulatory classifications)

**What results do NOT represent:**

- Gene expression levels or transcript abundance
- Enzyme activity or metabolic flux
- Actual degradation rates or in situ performance

### Analytical Scope

Use cases are designed for **exploratory analysis**:

- Hypothesis generation
- Candidate prioritization for experimental validation
- Comparative functional profiling

**Not designed for:**

- Definitive mechanistic conclusions
- Regulatory compliance submissions
- Clinical or risk-based decision-making

All computational inferences require wet-lab or field validation.

---

## Exports in Context

Results displayed on screen can be exported for external analysis and reproducibility. Export mechanisms include:

- **Database-level exports:** Available in database section headers
- **Use-case-level exports:** Available in use case headers

For complete documentation on export formats, scopes, metadata, and reproducibility requirements, see **Downloads** section.