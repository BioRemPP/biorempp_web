# Quickstart

Execute your first bioremediation analysis in BioRemPP in under 5 minutes.

---

## What You Need Before Starting

BioRemPP analyzes functional profiles based on KEGG Orthology (KO) identifiers. You will need:

- **KO annotations** for your samples (obtained from tools like KAAS, eggNOG-mapper, or BlastKOALA)
- **Plain text file** formatted as shown below

No account creation required. No installation needed.

---

## Minimal Input Example

Create a text file with this structure:

```
>Sample1
K00001
K00002
K00128
```

**Format rules:**
- Sample names start with `>`
- KO identifiers follow (one per line, format: `K#####`)
- No blank lines between samples

For complete format specification, see [Input Format](input-format.md). If you encounter validation errors, consult the [Troubleshooting Guide](../user-guide/troubleshooting.md).

---

## Step-by-Step: From Upload to Results

### 1. Open BioRemPP

Navigate to: **https://biorempp.cloud**

### 2. Upload Your File

- Drag and drop your `.txt` file, **or**
- Click "Select a file" to browse
- Alternatively, click "Use Example Data" to test with pre-loaded data

### 3. Wait for Validation

System automatically validates format and displays summary (samples detected, KO count, file size).

### 4. Navigate to Results

After processing, scroll to **Module 1** section. Learn more about the [Results Page structure](../user-guide/results-page.md).

### 5. Run Your First Analysis

- Expand **Use Case 1.1** (Intersections across BioRemPP, HADEG, and KEGG)
- Click **"View Results"**
- Wait for UpSet plot to appear (< 1 second)

### 6. Export Results

Download options available:

- **Database tables:** Click "Download Data" (CSV, Excel, or JSON)
- **Plots:** Hover over chart → camera icon (PNG, SVG)

**Session timeout:** 4 hours. Download results before closing browser. See [Downloads Guide](../user-guide/downloads.md) for export details and reproducibility requirements.

---

## What Happens Next?

**To understand your results:**

- [Results Page Overview](../user-guide/results-page.md) — Structure and organization of analytical interface
- [Interpretation Guidelines](../user-guide/interpretation.md) — How to interpret functional potential results
- [Use Cases Index](../use_cases/index.md) — All 56 analytical workflows
- [Downloads Guide](../user-guide/downloads.md) — Export results for external analysis

**To use your own data:**

- [Input Format](input-format.md) — Complete format specification and validation rules
- [Example Datasets](example-datasets.md) — Scientific datasets for testing

**Need help?**

- [FAQ](faq.md) — Common questions and solutions
- [Troubleshooting](../user-guide/troubleshooting.md) — Technical issues and error resolution
- [Contact](../about/contact.md) — Support and collaboration

---

## Scope Reminder

BioRemPP provides **computational inference** of bioremediation potential based on genomic annotations. Results indicate:

✓ Genetic capacity (gene presence)  
✗ NOT actual degradation activity  
✗ NOT gene expression levels  
✗ NOT enzyme activity

**All predictions require experimental validation.** This tool supports exploratory analysis and hypothesis generation for research purposes only. See [Interpretation Guidelines](../user-guide/interpretation.md) for detailed guidance on result interpretation.

**Limits:** 100 samples, 500,000 KOs, 5 MB file size.

---

## Related Pages

- [Home](../index.md) — BioRemPP overview and scope
- [Input Format](input-format.md) — Detailed format specification
- [Example Datasets](example-datasets.md) — Ready-to-use test datasets
- [FAQ](faq.md) — Frequently asked questions
- [Methods Overview](../methods/methods-overview.md) — Scientific methodology
- - [Use Cases Index](../use_cases/index.md) — All 56 analytical workflows for dataset analysis
- [Contact](../about/contact.md) — Support and collaboration

