# Frequently Asked Questions

Common questions about using BioRemPP for bioremediation analysis.

---

## General Questions

### What is BioRemPP?

BioRemPP (Bioremediation Potential Profile) is a web service for **functional inference** of bioremediation potential based on KEGG Orthology (KO) annotations. It integrates multiple databases (BioRemPP, KEGG, HADEG, toxCSM) to assess genetic potential for pollutant degradation.

### What is BioRemPP NOT designed for?

BioRemPP is **not**:

- A genome annotation tool (does not convert sequences to KO identifiers)
- An expression analysis platform (does not quantify gene activity)
- An experimental validation tool (does not measure degradation rates)
- A clinical or regulatory decision-support system

For details on scope and limitations, see [Limitations](../methods/limitations.md).

### Do I need to create an account?

No. BioRemPP operates with session-based storage. Data is processed in real-time and automatically deleted after 4 hours of inactivity or when the browser is closed.

---

## Input and Data Scope

### What type of data does BioRemPP accept?

**Accepted:** Plain text files (`.txt`) containing KO identifiers organized by sample.

**Not accepted:**

- Raw sequencing reads
- FASTA sequences (protein or nucleotide)
- Assembled genomes
- Gene expression matrices
- Abundance tables

### How do I obtain KO identifiers?

Use external annotation tools:

| Tool | Input | Output | URL |
|------|-------|--------|-----|
| **KAAS** | Nucleotide sequences (FASTA) | KO assignments | [https://www.genome.jp/kaas-bin/kaas_main](https://www.genome.jp/kaas-bin/kaas_main) |
| **eggNOG-mapper** | Protein/nucleotide sequences | KO + COG + GO | [http://eggnog-mapper.embl.de/](http://eggnog-mapper.embl.de/) |
| **DIAMOND** | Protein sequences + KEGG DB | BLAST-style hits → KO | [https://github.com/bbuchfink/diamond](https://github.com/bbuchfink/diamond) |
| **GhostKOALA** | Nucleotide sequences | KO assignments | [https://www.kegg.jp/ghostkoala/](https://www.kegg.jp/ghostkoala/) |

BioRemPP does not perform de novo annotation.

### Are quantitative data (e.g., gene counts, TPM) accepted?

No. BioRemPP performs **qualitative** analysis based on gene presence/absence. Quantitative data (expression levels, abundance) are not used.

### What are the input size limits?

- **Maximum samples:** 100
- **Maximum KO identifiers:** 500,000 (total across all samples)
- **Maximum file size:** 5 MB

---

## Analysis and Results

### What do BioRemPP results represent?

Results indicate **genetic potential** (presence of genes encoding bioremediation functions). They do **not** represent:

- Actual degradation activity
- Gene expression levels
- Enzyme activity or metabolic flux
- In situ bioremediation performance

For details, see [Limitations](../methods/limitations.md).

### How should results be interpreted?

Results are **computational inferences** for:

- Hypothesis generation
- Prioritization of candidates for experimental validation
- Comparative functional profiling

All predictions require wet-lab or field validation. See [Interpretation Guidelines](../user-guide/interpretation.md) for detailed guidance.

### What does "pathway completeness" mean?

Pathway completeness = (KOs present / Total KOs required) × 100%

**Important caveats:**

- Based on KEGG pathway definitions (may not reflect all biological variants)
- Binary logic (presence/absence, not expression)
- All KOs weighted equally (no distinction of critical vs. optional steps)


---

## Databases and Annotations

### Which databases are integrated?

1. **BioRemPP Database:** Curated bioremediation-specific mappings (KO → compounds, regulatory classifications)
2. **KEGG:** Metabolic pathways, reactions, enzymes
3. **HADEG:** Hydrocarbon degradation pathways
4. **toxCSM:** Machine learning-based toxicity predictions (66 endpoints)

### Are databases updated?

- **BioRemPP Database:** Versioned with the web service (deposited on Zenodo)
- **KEGG:** Updated regularly by KEGG; cite access date
- **HADEG, toxCSM:** Cite original publications

Check the "How to Cite" page for version-specific information.

### What is the coverage of the BioRemPP Database?

The database focuses on **bioremediation-relevant** compounds and enzymes. Not all KEGG pathways or compounds are included. Coverage prioritizes:

- Priority pollutants (IARC, EPA, ATSDR, WFD, PSL, EPC, CONAMA)
- Hydrocarbon degradation
- Xenobiotic metabolism

---

### What regulatory frameworks are referenced?

BioRemPP integrates seven frameworks:

- **IARC** (International Agency for Research on Cancer)
- **EPA** (U.S. Environmental Protection Agency)
- **ATSDR** (Agency for Toxic Substances and Disease Registry)
- **WFD** (Water Framework Directive, EU)
- **PSL** (Priority Substances List, Canada)
- **EPC** (Environmental Priority Chemicals)
- **CONAMA** (National Environment Council, Brazil)

These classifications are for **contextual reference**, not regulatory compliance.

---

## Technical and Performance Questions

### How long does analysis take?

**Typical processing times:**

-  10-30 seconds


Time varies with server load and dataset complexity.

### How long are results stored?

**Session timeout:** 4 hours of inactivity

After timeout or browser closure, all data is **permanently deleted**. Download results before closing the browser.

### Which browsers are supported?

**Recommended:**

- Chrome 90+ (best performance)
- Firefox 88+
- Edge 90+
- Safari 14+ (minor limitations)

**Not supported:** Internet Explorer

---

## Reproducibility and Availability

### How do I cite BioRemPP?

**Temporary citation (until DOI assignment):**

```
BioRemPP: Bioremediation Potential Profile Analysis Tool.
Version 1.0.0-beta (2025).
Available at: https://biorempp.cloud
Accessed: [DATE]
```

**In Methods sections, report:**

- BioRemPP version
- Annotation tool and version used
- Modules/use cases applied
- Analysis date
- Non-default parameters (if any)

### Is the source code available?

Yes. BioRemPP is open-source:

- **Web service code:** Apache License 2.0
- **BioRemPP Database:** Creative Commons Attribution 4.0 (CC BY 4.0)

Repository: https://github.com/BioRemPP

### Can BioRemPP be used for commercial purposes?

**Software:** Permitted under Apache 2.0

**Database:** Permitted under CC BY 4.0

**Third-party constraints:** Users must comply with KEGG licensing for commercial use. Contact KEGG directly: https://www.kegg.jp/kegg/legal.html

---

## Common Issues

### Why was my file rejected?

**Common causes:**

- Invalid KO format (must be `K#####`)
- Missing `>` prefix for sample names
- Blank lines in file
- Empty samples (sample with no KO identifiers)
- File exceeds size/sample/KO limits

See [Input Format](input-format.md) for complete validation rules. For step-by-step error resolution, consult the [Troubleshooting Guide](../user-guide/troubleshooting.md#common-processing-errors).

### Why are some database results empty?

Empty results occur when:

- No KO identifiers match the database
- Compounds from KEGG are not in toxCSM
- No bioremediation-relevant enzymes detected

This is **expected behavior** for samples without relevant annotations.

### How do I download results?

**Database downloads:**

- Navigate to database section (BioRemPP, HADEG, KEGG, ToxCSM)
- Click "Download Data" button
- Choose format: CSV, Excel, or JSON

**Plotly charts:**

- Hover over chart → toolbar appears (top-right)
- Click camera icon

For detailed export options and reproducibility requirements, see the [Downloads Guide](../user-guide/downloads.md).

---

## Related Pages

- [Quickstart](quickstart.md) — Get started with your first analysis
- [Input Format](input-format.md) — Complete format specification
- [Example Datasets](example-datasets.md) — Ready-to-use test files
- [Results Page](../user-guide/results-page.md) — Understanding the analytical interface
- [Interpretation](../user-guide/interpretation.md) — How to interpret results
- [Troubleshooting](../user-guide/troubleshooting.md) — Resolve common issues
- [Downloads](../user-guide/downloads.md) — Export and reproducibility guide
- [Contact](../about/contact.md) — Get help and support

