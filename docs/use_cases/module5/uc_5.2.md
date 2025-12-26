# UC-5.2 — Sample Similarity (Based on Chemical Profiles)

**Module:** 5 – Modeling Interactions of Samples, Genes, and Compounds  
**Visualization type:** Chord diagram (sample–sample similarity based on shared compounds)  
**Primary inputs:** BioRemPP results table with `sample` and `compoundname` columns  
**Primary outputs:** Pairwise similarity matrix of samples based on shared unique compounds

---

## Scientific Question and Rationale

**Question:** How functionally similar are the samples to one another, based on the shared repertoire of chemical compounds they interact with, and what is the structure of these functional guilds?

This use case quantifies **pairwise chemical similarity** between biological samples by counting how many **unique compounds** they have in common. The similarities are then represented as a **sample–sample chord diagram**, in which chord thickness reflects the number of shared targets. This can provide an intuitive, network-like view of **functional guilds**: clusters of samples that operate on overlapping chemical spaces and may therefore share ecological niches or degradation strategies.

---

## Data and Inputs

- **Primary data source:** `BioRemPP_Results.xlsx or BioRemPP_Results.csv`  
- **Key columns:**
  - `sample` – identifier for each biological sample
  - `compoundname` – name (or identifier) of the chemical compound associated with that sample
- **Accepted format:** semicolon-delimited text table (`.txt` or `.csv`)
- **Derived structures:**
  - a mapping from each sample to its set of unique compounds  
  - a pairwise similarity table where each entry is the count of shared compounds between two samples

---

## Analytical Workflow

1. **Data Loading**  
   The primary results table (`BioRemPP_Results.xlsx or BioRemPP_Results.csv`) is loaded from its semicolon-delimited format.

2. **Feature Engineering and Mapping**  
   For each unique `sample`, a **compound set** is constructed:
   - all unique `compoundname` entries associated with that sample are collected into a set,  
   - this set represents the sample's **chemical interaction profile**.

3. **Similarity Calculation**  
   All unique pairs of samples are considered. For each pair:
   - the intersection of their compound sets is computed,  
   - the **similarity score** is defined as the **count of shared unique compound names** in this intersection.

4. **Link Construction**  
   A table of sample–sample links is built where:
   - **source** = sample A,  
   - **target** = sample B,  
   - **value** = similarity score (number of shared compounds).  
   Only pairs with a non-zero similarity may be retained for visualization to reduce clutter.

5. **Rendering**  
   The similarity data is rendered as a **chord diagram**:
   - each sample is represented as an arc on the circle,  
   - chords (ribbons) connect pairs of samples,  
   - chord thickness encodes the similarity score (shared compound count).

---

## How to Read the Plot

- **Outer Arcs (Samples)**  
  Each colored arc along the circumference corresponds to an individual **Sample**.  
  - The length of an arc is typically proportional to the sample's **total shared interactions** with all other samples (sum of similarity values).

- **Chords (Ribbons)**  
  Each ribbon connecting two arcs represents the **similarity** between that pair of samples:
  - a chord exists where the two samples share at least one compound,  
  - the placement of chords reveals patterns of connectivity within the sample set.

- **Chord Thickness**  
  The thickness of a chord is directly proportional to the **number of shared compounds** between the two samples:
  - **thicker chords** indicate high functional overlap in chemical targets,  
  - **thinner chords** indicate weaker overlap.

---

## Interpretation and Key Messages

- **Functional Guilds**  
  Groups of samples connected by **multiple thick chords** may form **functional guilds**:
  - these samples share a similar range of chemical substrates,  
  - they could occupy analogous ecological roles or employ comparable metabolic strategies to process those compounds.

- **High Similarity Pairs**  
  A single very thick chord between two samples may indicate **strong pairwise similarity**:
  - these samples have highly overlapping chemical degradation profiles,  
  - they could be functionally redundant or interchangeable for certain chemical classes.

- **Unique Chemical Profiles**  
  A sample with only **thin chords** (or few connections) to others may possess a **more unique or specialized chemical interaction profile**:
  - it could be particularly valuable for targeting niche or rare pollutants not widely addressed by the rest of the consortium.

- **Network-Level Structure**  
  The global shape of the chord diagram may reveal:
  - densely connected regions corresponding to **cores** of shared chemical capabilities,  
  - more peripheral samples that extend the consortium's chemical reach into less common substrate spaces.

---

## Reproducibility and Assumptions

- **Input Format**  
  The analysis assumes a semicolon-delimited table containing at least the columns `sample` and `compoundname`.

- **Similarity Definition**  
  The similarity metric is explicitly defined as the **count of shared unique compound names** between pairs of samples:
  - repeated occurrences of the same compound within a sample do not increase the similarity; only uniqueness matters,  
  - this provides a direct proxy for functional overlap in terms of chemical targets.

- **Scope and Limitations**  
  - The chord diagram summarizes **overlap in compound repertoires**, not kinetics, expression levels, or pathway completeness.  
  - It is best interpreted as a structural map of who shares what targets, to be complemented by more detailed mechanistic analyses in subsequent modules.


 
---

## Activity diagram of the use case

*Click on the image to enlarge and explore details.*

<a class="glightbox" href="../uc_5.2.png">
  <img src="../uc_5.2.png" alt="Activity diagram of the use case">
</a>


