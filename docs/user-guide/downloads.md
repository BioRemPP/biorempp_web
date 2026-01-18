# Downloads and Data Export

This page documents export mechanisms, supported formats, and reproducibility requirements for BioRemPP results.

---

## Purpose of the Downloads Page

After analysis, users can export results for:
- External statistical analysis
- Scientific publication
- Reproducible research
- Long-term archival (beyond 4-hour session timeout)

This page defines export scopes, formats, metadata structure, and reproducibility requirements.

---

## Exportable Artifact Types

BioRemPP generates two categories of exportable artifacts:

### 1. Integrated Database Tables

Complete merged datasets combining user-uploaded KO annotations with database integration results.

**Sources:**

- **BioRemPP Database:** Curated bioremediation-specific mappings
- **KEGG:** Metabolic pathways, reactions, compounds
- **HADEG:** Hydrocarbon degradation pathways
- **ToxCSM:** Machine learning-based toxicity predictions (66 endpoints)

**Content:**

- All matched records for user samples
- Complete database fields (e.g., 67 columns for ToxCSM)
- Sample column for traceability
- Only data matching uploaded KO identifiers

### 2. Use Case–Specific Analysis Outputs

Results from individual analytical use cases (visualizations + tables).

**Content:**

- Exact data used to generate visualization
- Subset of columns relevant to specific analysis

---

## Export Scopes

### Dataset-Level Exports

**Location:** Database section headers ("Download Data" button)

**Scope:** Complete merged dataset for entire database

**When to use:**

- Comprehensive external analysis
- Building custom visualizations
- Integration with other tools (R, Python, Excel)
- Maximum flexibility for post-processing

**Example:** Download all ToxCSM predictions for all matched compounds across all samples

---

### Use-Case-Level Exports

**Location:** Use case header within each use case panel 

**Scope:** Data specific to that visualization

**When to use:**

- Reproducing exact chart from BioRemPP
- Focused analysis on specific question
- Minimal dataset for targeted interpretation
- Quick export for presentation

**Example:** Download Top 20 samples from UC-2.1 table

---

## Supported Formats and Use Cases

### Tabular Data Formats

| Format | Extension | Best For | Notes |
|--------|-----------|----------|-------|
| **CSV** | `.csv` | Universal compatibility | Opens in Excel, R, Python; UTF-8 encoding |
| **Excel** | `.xlsx` | Spreadsheet analysis | Native Excel format; preserves formatting |
| **JSON** | `.json` | Programmatic access | Structured format for Python, R, JavaScript |

### Visualization Formats

| Format | Extension | Best For | Notes |
|--------|-----------|----------|-------|
| **PNG** | `.png` | Presentations, quick sharing | Raster format; 1200 DPI default |
| **SVG** | `.svg` | Publications, editing | Vector format; scalable, editable in Illustrator/Inkscape |
| **JPEG** | `.jpg` | Web use, file size constraints | Lossy compression; smaller files |

### Format Selection Guidelines

**For publications:**

- Tables: CSV or Excel (for supplementary files)
- Figures: SVG (vector graphics, editable)

**For presentations:**

- PNG (high resolution raster)

**For programmatic analysis:**

- JSON (structured, preserves data types)
- CSV (universal, simple parsing)

**For archival:**

- Excel (self-contained, human-readable)
- JSON (machine-readable, version-controlled)

---

## Metadata and Versioning

### Exported File Metadata

While BioRemPP does not automatically embed metadata in exported files, users should document:

**Required for reproducibility:**

- **BioRemPP version:** Displayed in page footer (e.g., v1.0.0)
- **Analysis date:** Timestamp of export in file name (automatically generated)
- **Module and Use Case ID:** e.g., Module 2, UC-2.1 (automatically generated)
- **Parameters:** Top N values, thresholds, filters applied

**Database versions:**

- **BioRemPP Database:** Versioned with web service
- **KEGG:** Cite access date (updated regularly)
- **HADEG:** Cite original publication
- **ToxCSM:** Cite original publication

### File Naming Conventions

BioRemPP generates filenames using two distinct patterns:

#### Database-Level Downloads

Fixed naming pattern for complete merged databases:

```
{DatabaseName}_Results.{ext}
```

**Actual examples:**
- `BioRemPP_Results.csv`
- `HADEG_Results.xlsx`
- `KEGG_Results.json`
- `toxCSM.csv` (legacy format, no "_Results" suffix)

**Notes:**

- Database names are capitalized as shown
- No timestamp included (session-based, not chronological)
- Extension matches selected format

---

#### Use Case-Level Downloads

Dynamic naming pattern with timestamp:

```
UC-{Module}-{UseCase}_{descriptor}_{timestamp}.{ext}
```

**Pattern components:**

- `UC-X-Y`: Use case identifier (e.g., `UC-2-1`, dots replaced with hyphens)
- `descriptor`: Database or analysis type (e.g., `biorempp_df`, `kegg_df`)
- `timestamp`: Format `YYYYMMDD_HHMMSS` (e.g., `20250108_143022`)
- `ext`: File extension (`csv`, `xlsx`, json`)

**Actual examples:**

- `UC-2-1_biorempp_df_20250108_143022.csv`
- `UC-7-3_toxcsm_df_20250108_144201.xlsx`

**Timestamp purpose:**

- Automatically generated at export time
- Ensures uniqueness for multiple exports
- Provides chronological sorting
- Aids in archival organization

---

### Column Naming: Raw vs. Processed

BioRemPP maintains **two versions** of database tables:

#### Raw Database Tables (for Reproducibility)

**Downloaded from:** Database section headers ("Download Data" button)

**Column names:** Original database field names

**Purpose:** Scientific reproducibility and citation

**Examples:**

- **BioRemPP:** `Sample`, `ko`, `genesymbol`, `genename`, `cpd`, `compoundclass`, `referenceAG`, `compoundname`, `enzyme_activity`
- **HADEG:** `Sample`, `ko`, `Gene`, `Pathway`, `compound_pathway`
- **KEGG:** `Sample`, `ko`, `pathname`, `genesymbol`
- **ToxCSM:** `Sample`, `Compound`, `SMILES`, `LD50_mg_kg`, `AMES_Toxicity`, ... (66 columns total)

**Why use raw names:**

- Match published database schemas
- Ensure compatibility with database citations
- Enable validation against source databases

---

#### Processed Data Tables (for Backend Analysis)

**Downloaded from:** Use case headers ("Download Data" in use case accordion)

**Column names:** May be sanitized or aggregated

**Purpose:** Internal processing and visualization

**Differences:**

- Column names may differ from raw databases
- May include computed/aggregated fields not in original databases
- Optimized for specific use case calculations

**Example transformation:**

- Raw: `referenceAG` → Processed: `Agency`
- Raw: `compoundname` → Processed: `Compound_Name`
- Raw: `ko` → Processed: `KO`

Users citing database content should reference **raw database downloads** to ensure field name consistency with original sources.

---

## Reproducibility Checklist

To ensure scientific reproducibility, document and retain:

### Minimal Requirements

- [ ] **Input file:** Original `.txt` file with KO annotations
- [ ] **BioRemPP version:** From page footer
- [ ] **Analysis date:** Date of export
- [ ] **Module/Use Case IDs:** e.g., Module 7, UC-7.3
- [ ] **Non-default parameters:** Top N, thresholds, filters (if modified)

### Recommended Additional Information

- [ ] **Annotation tool and version:** How KO identifiers were generated (e.g., eggNOG-mapper v2.1.12)
- [ ] **Genome/MAG completeness:** If applicable (CheckM, BUSCO scores)
- [ ] **Sample metadata:** Biological context, experimental conditions
- [ ] **Database access dates:** Especially for KEGG

### Archival Best Practices

1. **Create analysis directory** with structured subdirectories:
   ```
   analysis_YYYYMMDD/
   ├── input/
   │   └── ko_annotations.txt
   ├── database_exports/
   │   ├── biorempp_data.csv
   │   ├── kegg_data.csv
   │   └── toxcsm_data.xlsx
   ├── use_case_outputs/
   │   ├── uc_2_1_table.csv
   │   └── uc_2_1_plot.svg
   └── metadata.txt
   ```

2. **Document parameters** in `metadata.txt`:
   ```
   BioRemPP version: 1.0.0-beta
   Analysis date: 2025-01-08
   Input samples: 12
   Input KOs: 4532
   Annotation tool: eggNOG-mapper v2.1.12
   Modules analyzed: 1, 2, 7
   ```

3. **Deposit with publications:**
   - Zenodo, Figshare, or institutional repository
   - Include DOI in Methods section

---

## Limitations

BioRemPP results indicate genetic potential for exploratory analysis, not definitive biological activity or regulatory compliance.

For complete scope and limitations, see **[Limitations and Scope Boundaries](../methods/limitations.md)**.

---

## Export Workflow Example

### Complete Export Workflow

1. **Run analysis** (e.g., Module 2, UC-2.1)
2. **Download dataset-level databases:**
    - BioRemPP database (CSV)
    - KEGG database (CSV)
    - ToxCSM database (Excel)

3. **Download use-case outputs:**
    - UC-2.1 table (CSV)
    - UC-2.1 heatmap (SVG)

4. **Document metadata:**
    - Record BioRemPP version, date, parameters
    - Note annotation tool used

5. **Organize files:**
    - Create directory structure
    - Add metadata.txt

6. **Archive:**
    - Commit to version control or repository
    - Include in supplementary materials

---

## Related Pages

- [Results Page](results-page.md) — Understanding export locations and data scopes
- [Interpretation Guidelines](interpretation.md) — How to interpret exported results
- [About - How to Cite](../about/how-to-cite.md) — Citation requirements for publications
- [Troubleshooting](troubleshooting.md#download-related-issues) — Resolve export errors
- [FAQ](../getting-started/faq.md#how-do-i-download-results) — Common download questions
- [Methods Overview](../methods/methods-overview.md) — Scientific methodology for reproducibility
