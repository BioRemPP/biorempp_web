# Regulatory Frameworks

This page describes how regulatory classifications are integrated into BioRemPP to contextualize bioremediation relevance and prioritize pollutant assessment.

---

## Rationale for Regulatory Contextualization

BioRemPP integrates priority pollutant classifications from seven environmental regulatory references to provide scientific context for the assessment of bioremediation potential. This integration serves multiple purposes:

### Why Regulatory References Matter

**Prioritization of Research Efforts**

Regulatory classifications identify compounds that have been systematically evaluated for environmental and human health risks by authoritative agencies. By mapping functional annotations to these priority pollutants, BioRemPP enables researchers to:

- Focus bioremediation research on compounds of established environmental significance
- Identify genetic capacity for degradation of high-priority contaminants
- Align experimental validation efforts with substances of regulatory concern

**Contextualizing Environmental Significance**

Regulatory frameworks provide external validation of a compound's environmental relevance beyond its chemical properties. Inclusion in priority lists reflects:

- **Persistence:** Resistance to environmental degradation
- **Toxicity:** Demonstrated or suspected harm to ecosystems or human health
- **Bioaccumulation potential:** Tendency to concentrate in organisms and food chains
- **Widespread occurrence:** Detection frequency in environmental monitoring programs

**Facilitating Comparative Assessment**

Multiple regulatory jurisdictions may classify the same compound differently based on regional priorities, exposure scenarios, or available evidence. BioRemPP's multi-framework integration allows users to:

- Compare regulatory classifications across agencies
- Identify compounds prioritized by multiple jurisdictions (consensus pollutants)
- Understand jurisdiction-specific regulatory landscapes

**Supporting Hypothesis Generation**

Regulatory context informs the scientific interpretation of functional potential results by:

- Identifying which detected genetic capacities correspond to high-priority environmental threats
- Guiding selection of model compounds for experimental validation
- Contextualizing bioremediation capacity within broader environmental management objectives

---

## Overview of Integrated Frameworks

### IARC (International Agency for Research on Cancer)

**Scope:** International (World Health Organization)

**Classification System:**

IARC classifies compounds based on the strength of evidence for their carcinogenic potential:

- **Group 1:** Carcinogenic to humans (sufficient evidence)
- **Group 2A:** Probably carcinogenic to humans (limited evidence in humans, sufficient in animals)
- **Group 2B:** Possibly carcinogenic to humans (limited evidence in humans, less than sufficient in animals)

**Role in BioRemPP:**

IARC classifications contextualize compounds by their carcinogenic risk. Genetic capacity to degrade Group 1 or 2A compounds is of particular relevance for bioremediation applications targeting cancer-associated environmental pollutants.

**Reference:** [IARC Monographs - List of Classifications](https://monographs.iarc.who.int/list-of-classifications/)

---

### US EPA (Environmental Protection Agency)

**Scope:** United States

**Classification System:**

The EPA maintains multiple priority pollutant programs:

- **National Priorities List (NPL):** Sites prioritized for cleanup under CERCLA (Superfund)
- **Priority Pollutants List:** 126 compounds regulated under the Clean Water Act
- **Toxic Release Inventory (TRI):** Substances subject to reporting requirements

**Role in BioRemPP:**

EPA classifications identify compounds prevalent at contaminated sites requiring remediation. Functional annotations matching EPA-listed pollutants indicate potential applicability for site-specific bioremediation strategies.

**Reference:** [US EPA - Superfund National Priorities List](https://www.epa.gov/superfund/superfund-national-priorities-list-npl)

---

### ATSDR (Agency for Toxic Substances and Disease Registry)

**Scope:** United States (Public Health Service)

**Classification System:**

ATSDR maintains a **Substance Priority List (SPL)** ranking hazardous substances based on:

- Frequency of occurrence at National Priorities List (NPL) sites
- Toxicity to humans
- Potential for human exposure

**Role in BioRemPP:**

ATSDR prioritization reflects both prevalence and health risk. Compounds ranked highly on the SPL represent critical targets for bioremediation research due to their combined toxicity and environmental abundance.

**Reference:** [ATSDR - Substance Priority List](https://www.atsdr.cdc.gov/programs/substance-priority-list.html)

---

### WFD (Water Framework Directive)

**Scope:** European Union

**Classification System:**

The WFD (Directive 2000/60/EC) establishes:

- **Priority Substances:** Pollutants posing significant risk to aquatic environments
- **Priority Hazardous Substances:** Subset requiring elimination or progressive reduction

**Objectives:**

- Prevent deterioration of aquatic ecosystems
- Promote sustainable water use
- Achieve good chemical and ecological status of water bodies

**Role in BioRemPP:**

WFD classifications contextualize compounds by their impact on aquatic ecosystems. Genetic capacity to degrade priority hazardous substances is particularly relevant for water-focused bioremediation applications.

**Reference:** [EU Water Framework Directive (2000/60/EC)](https://eur-lex.europa.eu/eli/dir/2000/60/oj)

---

### PSL (Priority Substances List, Canada - CEPA)

**Scope:** Canada

**Classification System:**

Under the Canadian Environmental Protection Act (CEPA), compounds are categorized as:

- **PSL1 (Priority Substances List 1):** Initial assessment of 44 substances
- **PSL2 (Priority Substances List 2):** Extended assessment of 25 additional substances

Substances are evaluated for:

- Toxicity to humans or the environment
- Persistence in the environment
- Bioaccumulation potential

**Role in BioRemPP:**

PSL classifications reflect Canadian environmental priorities. Compounds on PSL1 or PSL2 represent targets for bioremediation relevant to Canadian regulatory contexts and Arctic/boreal ecosystems.

**Reference:** [CEPA - Priority Substances Lists](https://www.canada.ca/en/environment-climate-change/services/canadian-environmental-protection-act-registry/substances-list)

---

### EPC (European Parliament Commission - Priority Chemicals)

**Scope:** European Union

**Classification System:**

The European Parliament regulates chemicals through frameworks including:

- **REACH (Registration, Evaluation, Authorisation, and Restriction of Chemicals):** Comprehensive chemical safety assessment
- **Priority substance lists** under various environmental directives

**Role in BioRemPP:**

EPC-derived classifications provide EU-specific regulatory context. Overlap with WFD classifications is common, reflecting coordinated EU environmental policy.

**Reference:** [EU REACH Regulation](https://eur-lex.europa.eu/)

---

### CONAMA (National Environmental Council, Brazil)

**Scope:** Brazil

**Classification System:**

CONAMA resolution (430/2011) establishes guidelines for:

- Water quality standards (freshwater, brackish, and marine)    
- Soil contamination thresholds
- Air quality standards
- Hazardous waste classification

**Role in BioRemPP:**

CONAMA classifications reflect Brazilian environmental priorities, including pollutants relevant to tropical ecosystems, agricultural contexts, and industrial pollution patterns specific to South America.

**Reference:** [CONAMA - Brazilian Environmental Regulations](https://conama.mma.gov.br/)

---

## Regulatory Data Representation

### Storage and Display

**Database Field: `referenceAG`**

In the BioRemPP Database, regulatory classifications are stored in the `referenceAG` column, which contains the acronym of the agency that classified the compound as a priority pollutant.

**Possible values:**

- `IARC`, `IARC2A`, `IARC2B` (IARC classifications by group)
- `EPA`
- `ATSDR`
- `WFD`
- `PSL` (Canada)
- `EPC` (European Parliament Commission)
- `CONAMA`

**Multiple Classifications:**

A single compound may appear in multiple regulatory frameworks. BioRemPP represents this through:

- Multiple database rows (one per agency classification)
- Aggregated views in analytical use cases (e.g., Module 1 - UC 1.2: Regulatory Relevance Landscape)

**Example:**

Benzene may have the following entries:

| Compound | referenceAG |
|----------|-------------|
| Benzene  | IARC        |
| Benzene  | EPA         |
| Benzene  | ATSDR       |
| Benzene  | WFD         |

This allows comparative analysis of regulatory consensus and jurisdiction-specific priorities.

---

### Non-Hierarchical Nature

**Important:** BioRemPP does not impose a hierarchical ranking among regulatory frameworks.

- No agency is treated as more authoritative than another
- Classifications are presented as parallel, complementary information sources
- Users interpret relative importance based on their research context and jurisdiction

**Rationale:**

Regulatory frameworks serve different purposes (carcinogenicity assessment, site contamination prioritization, water quality standards) and apply to different geographic or legal contexts. Hierarchical ranking would misrepresent their complementary roles.

---

## Scope and Limitations

BioRemPP provides **exploratory functional inference** of bioremediation potential based on genetic annotations. Results represent **genetic capacity**, not confirmed biological activity, gene expression, or degradation rates.

**Critical boundaries:**

- Genetic potential ≠ biological activity
- No kinetic modeling or expression weighting
- Computational predictions require experimental validation
- Not suitable for regulatory compliance or clinical decisions

For complete documentation of scope boundaries, methodological constraints, interpretation guidelines, and usage restrictions, see **[Limitations and Scope Boundaries](limitations.md)**.

---

## Related Pages

- [Data Sources](data-sources.md) — Overview of integrated databases
- [Interpretation Guidelines](../user-guide/interpretation.md) — How to interpret regulatory context in results
- [Use Cases Index](../use_cases/index.md) — Analytical workflows incorporating regulatory classifications
- [About - Terms of Use](../about/terms-of-use.md) — Legal disclaimers and usage limitations
- [FAQ](../getting-started/faq.md#what-regulatory-frameworks-are-referenced) — Common questions about regulatory integration
