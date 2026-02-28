# Example Datasets

BioRemPP provides ready-to-use example datasets to help you get started quickly. These datasets demonstrate proper input formatting and represent biologically relevant organisms used in bioremediation research.

---

## Quick Access

**Download example dataset:**

- **From homepage:** use **Need a KO Input Example? -> Download Example**
- **Load directly:** click **Use Example Data** in the upload panel (no download required)

---

## Example Dataset: Minimal Demo

### Overview

- **Samples:** 2
- **KO identifiers:** 10 total (5 per sample)
- **Purpose:** Demonstrate proper input format and quick testing

### Dataset Content

```
>Sample1
K00031
K00032
K00090
K00042
K00052
>Sample2
K00031
K00032
K00090
K00042
K00052
```

### What This Demonstrates

- **Proper sample headers:** Each sample starts with `>` followed by name
- **Valid KO format:** All identifiers are `K` + 5 digits
- **No blank lines:** Samples immediately follow KO lists
- **Shared KOs:** Both samples have identical KO profiles (useful for testing comparative analyses)

For complete format specification, see [Input Format](input-format.md).



## Published Demonstration Dataset: Nine Representative Organisms

### Overview

BioRemPP's published demonstration uses **nine representative organisms** spanning three principal groups in bioremediation:

- **Total samples:** 9 (3 bacteria, 3 fungi, 3 microalgae/cyanobacteria)
- **Purpose:** Demonstrate multi-kingdom comparative analysis
- **Based on:** Organisms relevant to hydrocarbon bioremediation studies

### Organisms Included

#### Bacteria

| Organism | KEGG Code | Notes |
|----------|-----------|-------|
| *Acinetobacter baumannii* | `acb` | Gram-negative, opportunistic pathogen with xenobiotic degradation capacity |
| *Enterobacter asburiae* | `eau` | Emerging bioremediation agent, aromatic compound degradation |
| *Pseudomonas aeruginosa* | `pae` | Model organism for biodegradation, versatile metabolic capacity |

#### Fungi

| Organism | KEGG Code | Notes |
|----------|-----------|-------|
| *Aspergillus nidulans* | `ani` | Filamentous fungus, lignocellulose degradation |
| *Fusarium graminearum* | `fgr` | Plant pathogen, aromatic compound transformation |
| *Cryptococcus gattii* | `cgi` | Yeast, environmental stress tolerance |

#### Microalgae / Cyanobacteria

| Organism | KEGG Code | Notes |
|----------|-----------|-------|
| *Chlorella variabilis* | `cvr` | Green microalga, heavy metal biosorption |
| *Nannochloropsis gaditana* | `ngd` | Marine microalga, lipid accumulation |
| *Synechocystis* sp. | `syn` | Model cyanobacterium, photosynthetic bioremediation |

### Scientific Reference

These organisms were selected based on their relevance in hydrocarbon bioremediation studies:

**Publication:**  
*Bacteria, Fungi and Microalgae for the Bioremediation of Marine Sediments Contaminated by Petroleum Hydrocarbons in the Omics Era*  
Microorganisms 2021, 9, 1695.  
DOI: [10.3390/microorganisms9081695](https://doi.org/10.3390/microorganisms9081695)

### How to Use This Dataset

**If you have genome annotations for these organisms:**

1. Annotate genomes using KAAS, eggNOG-mapper, or similar tools
2. Extract KO identifiers for each organism
3. Format as described in [Input Format](input-format.md)
4. Compare with BioRemPP Database to assess bioremediation potential

**Typical analyses:**

- **Cross-kingdom comparison:** Compare bacterial vs. fungal vs. microalgal bioremediation potential
- **Consortium optimization:** Identify complementary gene profiles for mixed-culture applications
- **Regulatory compliance:** Verify presence of genes for priority pollutant degradation

See [Use Cases Index](../use_cases/index.md) for all 56 analytical workflows available for these types of comparisons.

---

## Creating Your Own Dataset

### Step 1: Choose Your Samples

**Sample selection criteria:**

- **Biological relevance:** Organisms or communities with suspected bioremediation capacity
- **Genome availability:** Complete or draft genomes annotated with KO identifiers
- **Comparative context:** Include replicates or related samples for comparative analysis


---

### Step 2: Annotate Genomes with KO Identifiers

| Tool | Input | Output | URL |
|------|-------|--------|-----|
| **KAAS** | Nucleotide sequences (FASTA) | KO assignments | [https://www.genome.jp/kaas-bin/kaas_main](https://www.genome.jp/kaas-bin/kaas_main) |
| **eggNOG-mapper** | Protein/nucleotide sequences | KO + COG + GO | [http://eggnog-mapper.embl.de/](http://eggnog-mapper.embl.de/) |
| **DIAMOND** | Protein sequences + KEGG DB | BLAST-style hits → KO | [https://github.com/bbuchfink/diamond](https://github.com/bbuchfink/diamond) |
| **GhostKOALA** | Nucleotide sequences | KO assignments | [https://www.kegg.jp/ghostkoala/](https://www.kegg.jp/ghostkoala/) |

---

### Step 3: Format for BioRemPP

**Format KO assignments as:**

```
>YourSampleName
K00001
K00002
K00003
...
>YourSampleName2
K00010
K00020
K00030
...
```

**Important formatting rules:**

- **Sample names:** No spaces (use underscores or hyphens)
- **KO format:** Exactly `K` + 5 digits (remove `ko:` prefix if present)
- **No duplicates:** Each KO should appear once per sample
- **No blank lines:** Samples follow immediately after KO lists

---

### Step 4: Validate Format

**Before uploading:**

- Check for blank lines (remove all)
- Verify sample headers start with `>`
- Confirm all KOs match `K#####` format
- Ensure file is UTF-8 encoded

**Quick validation:**

```bash
# Count samples (should match expected)
grep -c "^>" your_dataset.txt

# Count total KOs
grep -c "^K" your_dataset.txt

# Check for invalid lines (should return nothing)
grep -v "^>" your_dataset.txt | grep -v "^K"
```

---

## Dataset Quality Checklist

**Before uploading, verify:**

- [ ] All sample headers start with `>`
- [ ] All sample names contain no spaces
- [ ] All KO identifiers are exactly `K#####` format
- [ ] No blank lines between samples
- [ ] File is UTF-8 encoded (not UTF-16 or Latin-1)
- [ ] File size <5 MB
- [ ] Total samples ≤100
- [ ] Total KO identifiers ≤500,000

---

## Troubleshooting Example Datasets

### "Example data doesn't load"

**Possible causes:**

- Browser cache issue
- Server connectivity problem

**Solutions:**

1. Refresh browser (Ctrl+F5 or Cmd+Shift+R)
2. Clear browser cache
3. Try different browser (Chrome, Firefox, Safari)
4. Download example file manually and upload

---

## Related Pages

- [Quickstart](quickstart.md) — Get started with your first analysis
- [Input Format](input-format.md) — Complete format specification and validation rules
- [FAQ](faq.md#how-do-i-obtain-ko-identifiers) — How to obtain KO identifiers
- [Troubleshooting Guide](../user-guide/troubleshooting.md) — Resolve file upload and validation errors
- [Use Cases Index](../use_cases/index.md) — All 56 analytical workflows for dataset analysis
- [Contact](../about/contact.md) — Support and collaboration
