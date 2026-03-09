# Input Format Specification

This document formally defines the input format accepted by the BioRemPP Web Service.

---

## Overview

BioRemPP accepts **functional annotations** as input, specifically KEGG Orthology (KO) identifiers organized by sample. The system does **not** process:

- Raw sequencing reads
- Assembled genomes or contigs  
- Protein or nucleotide sequences
- Gene expression data or abundance tables

Input must be **pre-annotated** using external tools (e.g., KAAS, eggNOG-mapper, BlastKOALA, GhostKOALA). See [FAQ](faq.md#how-do-i-obtain-ko-identifiers) for detailed annotation tool guidance.

---

## Accepted File Format

**File type:** Plain text (`.txt`)

**Character encoding:** UTF-8 (recommended) or Latin-1

**Structure:** Multi-sample format with header-delimited sections

Each file consists of:
1. One or more sample identifiers
2. Associated KO identifiers listed sequentially

---

## Sample Definition

### Sample Identifier

**Format:** `>SampleName`

**Rules:**

- Must start with the `>` character (greater-than symbol)
- Followed immediately by the sample name (no space)
- Sample names must be **non-empty**
- Whitespace within sample names is **not permitted**
- Sample names are **case-sensitive**

**Valid examples:**
```
>Soil_Sample_A
>Pseudomonas_Strain1
>MAG_bin_042
```

**Invalid examples:**
```
> Sample1        # Space after >
>Sample 1        # Space in name
>                # Empty name
Sample1          # Missing >
```

---

## KO Identifier Specification

### Format

**Required pattern:** `K` + exactly 5 digits

**Regular expression:** `^K\d{5}$`

**Examples of valid KO identifiers:**
```
K00001
K00128
K12345
K99999
```

**Examples of invalid KO identifiers:**
```
ko:K00001       # Prefix not accepted
K1              # Insufficient digits
K0001           # Insufficient digits (4 digits)
K000001         # Excessive digits (6 digits)
k00001          # Lowercase not accepted
KO00001         # 'KO' prefix not accepted
```

### Origin of KO Identifiers

KO identifiers must be obtained from external annotation tools.

**Recommended annotation tools:**

| Tool | Input | Output | URL |
|------|-------|--------|-----|
| **KAAS** | Nucleotide sequences (FASTA) | KO assignments | [https://www.genome.jp/kaas-bin/kaas_main](https://www.genome.jp/kaas-bin/kaas_main) |
| **eggNOG-mapper** | Protein/nucleotide sequences | KO + COG + GO | [http://eggnog-mapper.embl.de/](http://eggnog-mapper.embl.de/) |
| **DIAMOND** | Protein sequences + KEGG DB | BLAST-style hits → KO | [https://github.com/bbuchfink/diamond](https://github.com/bbuchfink/diamond) |
| **GhostKOALA** | Nucleotide sequences | KO assignments | [https://www.kegg.jp/ghostkoala/](https://www.kegg.jp/ghostkoala/) |



BioRemPP does **not** perform de novo KO annotation.

---

## Structural Constraints

The following limits are enforced by the validation system:

| **Constraint** | **Limit** | **Notes** |
|----------------|-----------|-----------|
| Maximum samples per file | 100 | Count of `>SampleName` headers |
| Maximum total KO identifiers | 500,000 | Sum across all samples |
| Maximum file size | 5 MB | Before upload |

**Notes:**

- Duplicate KO identifiers within a sample are **permitted** but may be deduplicated during processing
- Empty samples (sample header with no KO identifiers) are **not permitted**
- Blank lines are **not permitted** anywhere in the file

For troubleshooting validation errors, see the [Troubleshooting Guide](../user-guide/troubleshooting.md#common-processing-errors).

---

## Validation Rules

### Automatic Validation

Upon upload, the system validates:

1. **File encoding:** UTF-8 or Latin-1 (fallback)
2. **First line:** Must be a sample identifier (`>SampleName`)
3. **Line structure:** Every line must be either:
    - A sample identifier, or
    - A valid KO identifier
4. **Sample completeness:** Each sample must have at least one KO identifier
5. **KO format:** All KO identifiers must match `K#####` pattern
6. **Quantitative limits:** File size, sample count, KO count

### Error Conditions

**File rejected if:**

- Empty file or only whitespace
- First line is not a sample identifier
- Any sample has an empty name (e.g., `>` alone)
- Any KO identifier does not match `K#####` format
- Any line is neither a sample identifier nor a valid KO
- File exceeds size, sample, or KO count limits

### Warning Conditions

**Warnings issued (but file accepted) if:**
- Latin-1 encoding detected (UTF-8 recommended)

---

## Common Input Errors

### Error: Empty file or no valid content

**Cause:** File is empty, contains only whitespace, or has no valid KO identifiers

**Solution:** Ensure file contains at least one sample and one KO identifier

---

### Error: File must start with sample identifier

**Cause:** First line does not begin with `>`

**Example (incorrect):**
```
K00001
K00002
>Sample1
```

**Corrected:**
```
>Sample1
K00001
K00002
```

---

### Error: Sample name cannot be empty

**Cause:** Sample identifier has no name after `>`

**Example (incorrect):**
```
>
K00001
```

**Corrected:**
```
>Sample1
K00001
```

---

### Error: Invalid KO format

**Cause:** KO identifier does not match `K#####` pattern

**Example (incorrect):**
```
>Sample1
ko:K00001
K1
```

**Corrected:**
```
>Sample1
K00001
K00010
```

---

### Error: Invalid line format

**Cause:** Line is neither a sample identifier nor a valid KO identifier

**Common causes:**

- Blank lines
- Comments or headers (e.g., `# Sample 1`)
- Extra metadata (e.g., `K00001 | enzyme name`)

**Example (incorrect):**
```
>Sample1
K00001

K00002
```

**Corrected:**
```
>Sample1
K00001
K00002
```

---

### Error: File size exceeds maximum

**Cause:** File is larger than 5 MB

**Solution:** Split file into multiple smaller files or remove redundant entries

---

### Error: Number of samples exceeds maximum

**Cause:** File contains more than 100 sample identifiers

**Solution:** Split dataset into multiple files with ≤100 samples each

---

### Error: Number of KO entries exceeds maximum

**Cause:** Total KO identifiers across all samples exceeds 500,000

**Solution:** Reduce dataset size or split into batches

---

## Limitations

BioRemPP results indicate genetic potential for exploratory analysis, not definitive biological activity or regulatory compliance.

For complete scope and limitations, see **[Limitations and Scope Boundaries](../methods/limitations.md)**.

---

## Reproducibility Notes

To ensure reproducible results, document:

- Annotation tool and version used to generate KO identifiers
- Input file structure (number of samples, total KOs)
- File encoding (UTF-8 recommended)
- BioRemPP version used for analysis

Input files should be retained and deposited alongside results for scientific reproducibility.

---

## Related Pages

- [Quickstart](quickstart.md) — Get started with your first analysis
- [Example Datasets](example-datasets.md) — Ready-to-use test files with correct formatting
- [FAQ](faq.md) — Common questions about input requirements
- [Troubleshooting Guide](../user-guide/troubleshooting.md) — Resolve validation and parsing errors
- [Methods Overview](../methods/methods-overview.md) — Scientific methodology and data processing workflow
