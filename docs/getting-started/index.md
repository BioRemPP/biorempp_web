# Getting Started with BioRemPP

Welcome to BioRemPP! This section will help you get started with your first bioremediation analysis in under 5 minutes.

---

## Quick Navigation

| Page | Purpose | Time Required |
|------|---------|---------------|
| **[Quickstart](quickstart.md)** | Your first analysis walkthrough | 3–5 minutes |
| **[Input Format](input-format.md)** | Complete format specification | Reference |
| **[Example Datasets](example-datasets.md)** | Ready-to-use demonstration data | Reference |
| **[FAQ](faq.md)** | Frequently asked questions | Reference |

---

## New to BioRemPP? Start Here

### 1️⃣ **Run Your First Analysis**

Follow the **[Quickstart Guide](quickstart.md)** for a 5-minute walkthrough:

- ✅ No account required
- ✅ No installation needed  
- ✅ Use pre-loaded example data or your own KO annotations

**What you'll learn:** Upload → Validate → Analyze → Export

---

### 2️⃣ **Understand Input Requirements**

BioRemPP accepts **KEGG Orthology (KO) identifiers** in plain text format.

**[Input Format Specification](input-format.md)** — Complete validation rules and format examples

**Key Requirements:**

- Plain text files (`.txt`) with UTF-8 encoding
- Sample headers start with `>`
- KO identifiers in format `K#####` (K + 5 digits)
- Max: 100 samples, 500,000 KOs, 5 MB file size

**Don't have KO identifiers?** See [FAQ: How do I obtain KO identifiers?](faq.md#how-do-i-obtain-ko-identifiers)

---

### 3️⃣ **Try Example Datasets**

Test BioRemPP with scientifically relevant demonstration data:

**[Example Datasets](example-datasets.md)** — Ready-to-use files and organism profiles

**Available examples:**

- **Minimal demo** (2 samples, 10 KOs) — Quick format validation
- **Published dataset** (9 organisms: bacteria, fungi, microalgae) — Multi-kingdom comparison

**Load directly:** Click "Use Example Data" in the upload panel (no download needed)

---

### 4️⃣ **Get Answers to Common Questions**

**[Frequently Asked Questions](faq.md)** — Common questions about inputs, analysis, and results

**Popular topics:**

- What do BioRemPP results represent?
- How do I obtain KO identifiers?
- What are the input size limits?
- How long are results stored?
- How do I cite BioRemPP?

---

## What BioRemPP Does (and Doesn't Do)

### ✅ BioRemPP Analyzes:

- **Genetic potential** for bioremediation based on KO annotations
- **Functional profiles** across 4 integrated databases (BioRemPP, KEGG, HADEG, ToxCSM)
- **Comparative assessments** across samples and databases
- **Toxicological predictions** for associated compounds

### ❌ BioRemPP Does NOT:

- Annotate sequences (use KAAS, eggNOG-mapper, or similar tools first)
- Measure gene expression or enzymatic activity
- Provide regulatory compliance determinations
- Replace experimental validation

⚠️ **All results require wet-lab or field validation.** See [Limitations](../methods/limitations.md)

---

## Ready to Analyze Your Data?

**Recommended workflow:**

1. **Annotate genomes** → Use KAAS, eggNOG-mapper, or DIAMOND to generate KO identifiers
2. **Format input** → Follow [Input Format](input-format.md) specification
3. **Upload to BioRemPP** → Visit [https://biorempp.cloud](https://biorempp.cloud)
4. **Explore results** → 8 modules, 56 use cases for comprehensive analysis
5. **Export data** → Download results for external analysis

**[Start with Quickstart Guide →](quickstart.md)**

---

## Need Help?

- **File format errors?** → [Troubleshooting Guide](../user-guide/troubleshooting.md)
- **Result interpretation?** → [Interpretation Guidelines](../user-guide/interpretation.md)
- **Technical support?** → [Contact](../about/contact.md)

---

## Related Sections

- **[User Guide](../user-guide/index.md)** — Results interpretation and data export
- **[Use Cases](../use_cases/index.md)** — All 56 analytical workflows
- **[Methods](../methods/methods-overview.md)** — Scientific methodology and data sources
- **[How to Cite](../about/how-to-cite.md)** — Citation requirements
