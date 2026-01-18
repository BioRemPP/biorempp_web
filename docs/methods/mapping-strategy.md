# Mapping Strategy

This page describes the technical strategy used to map KEGG Orthology (KO) identifiers to enzymatic functions, chemical compounds, metabolic pathways, toxicological endpoints, and regulatory classifications within the BioRemPP integration pipeline.

---

## 1. Scope and Input Contract (Mapping Layer)

### Input Abstraction

BioRemPP operates exclusively on **KEGG Orthology (KO) identifiers**. KO identifiers are treated as immutable functional units representing orthologous gene groups with conserved biochemical roles.

**Input contract:**

- **Accepted:** KO identifiers in format `K#####` (K + 5 digits)
- **Not accepted:**
  - Nucleotide or protein sequences
  - Genome assemblies
  - Gene expression matrices
  - Taxonomic identifiers

**Rationale for KO-level abstraction:**

The use of KO identifiers as the exclusive input format reflects a deliberate design choice prioritizing functional comparability and reproducibility over sequence-level resolution.

**Trade-offs:**

| Gain | Loss |
|------|------|
| Cross-organism functional comparability | Strain-specific isoform variation |
| Deterministic mapping to reference databases | Substrate specificity differences within ortholog groups |
| Platform-independent annotation compatibility | Allelic polymorphisms affecting catalytic efficiency |
| Reproducible integration across studies | Context-dependent regulatory variation |

**Implication:**

Results indicate **functional potential** (presence of gene encoding a conserved biochemical role) but do not resolve finer enzymatic distinctions that may be biologically relevant under specific environmental conditions.

---

## 2. Validation and Preprocessing

### 2.1 Identifier Validation

**Format enforcement:**

All KO identifiers must conform to the pattern `K\d{5}`:

**Validation layers:**

1. **String pattern validation** (format check)
2. **Value object instantiation** (immutable KO type creation)
3. **Entity-level validation** (sample integrity)
4. **Domain-level validation** (dataset consistency)

**Error handling policy:**

- **Structural violations:** Exceeding sample count, input format, KO count, or file size limits triggers immediate rejection. No partial processing.

---

### 2.2 Duplicate Handling

**Sample-level deduplication:**

Within a single sample, duplicate KO identifiers are automatically deduplicated during entity construction. The first occurrence is retained; subsequent duplicates are silently discarded.


**Post-merge duplicate preservation:**

After database integration, **one-to-many relationships are preserved**. A single input KO may produce multiple output rows if it maps to multiple compounds, enzymes, or pathways in the integrated databases.

**Example:**

```
Input:
>Sample1
K00001

BioRemPP Database matches:
K00001 → Compound A (regulatory agency: EPA)
K00001 → Compound A (regulatory agency: ATSDR)
K00001 → Compound B (regulatory agency: EPA)

Output (3 rows):
Sample1, K00001, Compound A, EPA
Sample1, K00001, Compound A, ATSDR
Sample1, K00001, Compound B, EPA
```

**No aggregation:** BioRemPP does not collapse, summarize, or aggregate multiple associations. All mappings are preserved in output tables.

---

### 2.3 Structural Constraints

**Limits enforced during validation:**

| Constraint | Default Value | Configuration Variable |
|------------|---------------|------------------------|
| Maximum samples per upload | 100 | `BIOREMPP_UPLOAD_SAMPLE_LIMIT` |
| Maximum total KO identifiers | 500,000 | `BIOREMPP_UPLOAD_KO_LIMIT` |
| Maximum KOs per sample | 10,000 | `BIOREMPP_PARSING_MAX_KOS_PER_SAMPLE` |
| Maximum file size | 5 MB | `BIOREMPP_UPLOAD_MAX_SIZE_MB` |

**Constraints on sample names:**

- Pattern: `[a-zA-Z0-9_\-\.]+` (alphanumeric, underscores, hyphens, periods)
- No whitespace permitted
- Case-sensitive
- Non-empty required

**Blank lines:**

Not permitted. Any line that is neither a sample header (`>...`) nor a valid KO identifier triggers format validation error.

**Configurability:**

All numeric limits are configurable via **config\settings.py**. Values listed above reflect deployment defaults and may differ across installations.

---

## 3. Integration Keys and Join Logic

### Global Integration Rules

**Matching strategy:**

All database integrations use **exact string matching** on identifier columns.

- **Case-sensitive:** `K00001` ≠ `k00001`
- **No normalization:** Whitespace, special characters, or formatting differences cause match failures
- **No fuzzy matching:** Typographical errors or approximate matches are not resolved
- **No synonym resolution:** Alternative identifiers (e.g., EC numbers, gene names) are not used for matching

**Join type:**

All integrations use **inner joins** (SQL `INNER JOIN` equivalent).

**Consequence:** KO identifiers without matches in a given database are excluded from that database's result table. Different databases may return different subsets of the input KO set.

**Determinism:**

Join operations are deterministic. Given identical input KO sets and unchanged databases, output is reproducible.

**No probabilistic inference:**

BioRemPP does not:

- Infer missing mappings based on sequence similarity
- Use machine learning to predict associations
- Assign confidence scores to mappings
- Fill missing values with defaults

**Cardinality preservation:**

One-to-many (1:N) and many-to-many (N:M) relationships are fully preserved. No automatic aggregation, grouping, or summarization occurs during integration.

---

## 4. Cascading Mapping Stages

BioRemPP integration proceeds through four sequential database merge stages, executed in the order listed below.

---

### Stage A — KO → BioRemPP Database

**Join key:** `ko` (KO identifier)

**Join type:** Inner join

**Entities added:**

- Compound ID (`cpd`)
- Compound name (`compoundname`)
- Compound class (`compoundclass`)
- Gene symbol (`genesymbol`)
- Gene name (`genename`)
- Enzyme activity (`enzyme_activity`)
- Regulatory agency (`referenceAG`)

**Cardinality:** 1:N (one KO may map to multiple compounds, enzymes, or regulatory classifications)

**Database schema:**

```
ko;cpd;referenceAG;compoundclass;compoundname;genesymbol;genename;enzyme_activity
```

**Example mapping:**

```
Input: K00001

BioRemPP Database records:
K00001;C00038;EPA;Metal;Zinc cation;E1.1.1.1;alcohol dehydrogenase;dehydrogenase
K00001;C00038;ATSDR;Metal;Zinc cation;E1.1.1.1;alcohol dehydrogenase;dehydrogenase
K00001;C00123;EPA;Organic;Ethanol;E1.1.1.1;alcohol dehydrogenase;dehydrogenase

Output: 3 rows (1 KO → 2 compounds × 2 agencies for first compound + 1 compound × 1 agency)
```

**Critical field: `cpd` (Compound ID)**

This field is used as the join key for **Stage D (toxCSM)**, creating the following mapping: KO → BioRemPP → Compound → Toxicity.

---

### Stage B — KO → KEGG Database

**Join key:** `ko` (KO identifier)

**Join type:** Inner join

**Entities added:**

- Pathway name (`pathname`)
- Gene symbol (`genesymbol`)

**Cardinality:** 1:N (one KO may participate in multiple metabolic pathways)

**Database schema:**

```
ko;pathname;genesymbol
```

**Example mapping:**

```
Input: K00002

KEGG Database records:
K00002;Glycolysis / Gluconeogenesis;adhE
K00002;Pyruvate metabolism;adhE

Output: 2 rows (1 KO → 2 pathways)
```

**Independence:**

KEGG integration is independent of BioRemPP integration. KOs absent from BioRemPP may still match KEGG, and vice versa. Result tables reflect database-specific coverage.

---

### Stage C — KO → HADEG Database

**Join key:** `ko` (KO identifier)

**Join type:** Inner join

**Entities added:**

- Gene identifier (`Gene`)
- Degradation pathway (`Pathway`)
- Compound pathway (`compound_pathway`)

**Cardinality:** 1:N (one KO may be associated with multiple hydrocarbon degradation pathways)

**Database schema:**

```
Gene;ko;Pathway;compound_pathway
```

**Example mapping:**

```
Input: K00003

HADEG Database records:
K00003;alkB;Alkane degradation (terminal oxidation);Alkanes (C5-C16)

Output: 1 row
```

**Independence:**

HADEG integration is independent of BioRemPP and KEGG. Results reflect HADEG-specific curation scope.

---

### Stage D — Compound → toxCSM Database

**Join key:** `cpd` (Compound identifier from BioRemPP)

**Join type:** Inner join

**Two-stage mapping:**

Unlike other stages, toxicity mapping is **indirect**:

1. **Stage A** provides `cpd` field (compound IDs)
2. **Stage D** joins compound IDs to toxCSM database

**Critical dependency:** ToxCSM integration requires successful BioRemPP integration. If BioRemPP returns no matches, toxCSM cannot proceed.

**Entities added:**

- SMILES notation (`SMILES`)
- ChEBI identifier (`ChEBI`)
- 31 toxicity value fields (`value_*`)
- 31 toxicity label fields (`label_*`)

**Toxicity categories:**

- **NR_** (Nuclear Response): AR, AhR, ER, PPAR_gamma, GR, TR, Aromatase
- **SR_** (Stress Response): ARE, ATAD5, HSE, MMP, p53
- **Gen_** (Genomic): AMES_Mutagenesis, Carcinogenesis, Micronucleus
- **Env_** (Environmental): Fathead_Minnow, T_Pyriformis, Honey_Bee, Biodegradation, Crustacean, Avian
- **Org_** (Organismal): Skin_Sensitisation, hERG_I_Inhibitor, hERG_II_Inhibitor, Liver_Injury, Eye_Irritation, Eye_Corrosion, Respiratory_Disease

**Data transformation:**

ToxCSM data is provided in **two formats**:

1. **Wide format** (66 columns): Sample + cpd + SMILES + ChEBI + compoundname + 31 value columns + 31 label columns
2. **Long format** (5 columns): compoundname, endpoint, toxicity_score, super_category, prefix

**Cardinality:** 1:N (one compound may have multiple toxicity endpoints)

---

### Regulatory Classification Integration

**Embedded in BioRemPP Database:**

Regulatory classifications are not a separate integration stage. The `referenceAG` field in the BioRemPP database contains regulatory agency codes.

**Multi-reference associations:**

A single compound may be classified by multiple regulatory references. This is represented by multiple rows in the BioRemPP database with different `referenceAG` values but identical `cpd` and `compoundname` values.

**N:M cardinality:**

One KO may map to multiple compounds, each classified by multiple agencies. All associations are preserved.

---

## 5. Missing Data and Ambiguity Semantics

### 5.1 Inner Join Behavior

**Definition:** Inner joins retain only rows with matches in both the left (input KO set) and right (database) tables.

**Consequence:** KO identifiers without matches in a given database are **silently excluded** from that database's result table.

**Example:**

```
Input KOs: K00001, K00002, K99999

BioRemPP Database matches:
  K00001 → Match (included)
  K00002 → Match (included)
  K99999 → No match (excluded)

BioRemPP Result: 2 KOs (K00001, K00002)

KEGG Database matches:
  K00001 → Match (included)
  K00003 → No match (excluded)

KEGG Result: 1 KO (K00001)
```

**Interpretation:** Different databases may return different KO counts. This is expected behavior, not an error. Empty result tables indicate absence of matches, not system failure.

---

### 5.2 Null Value Semantics

**Null ≠ Zero:**

Null values (`NaN` in pandas, `NULL` in SQL) represent **absence of data**, not a measurement of zero.


**User responsibility:**

Interpretation of null values is the user's responsibility. Null may indicate:
- Data not available in source database
- Field not applicable to this entity
- Curation gap

BioRemPP does not infer meaning from null values.

---

### 5.3 One-to-Many Relationship Preservation

**Cartesian product:**

When a KO matches multiple database records, all matches are preserved as separate rows in the output.

**Example:**

```
Input:
>Sample1
K00001

BioRemPP Database:
K00001 → Compound A (Agency: EPA)
K00001 → Compound A (Agency: ATSDR)
K00001 → Compound B (Agency: EPA)

Output:
Sample1, K00001, Compound A, EPA
Sample1, K00001, Compound A, ATSDR
Sample1, K00001, Compound B, EPA
```

**Result:** 1 input KO → 3 output rows.

**Rationale:** Preservation of all associations maximizes information content and allows users to apply domain-specific filtering or prioritization logic during downstream analysis.

---

### 5.4 Ambiguity Non-Resolution

**No automated disambiguation:**

BioRemPP does not resolve:

- Multiple compounds for a single KO
- Multiple pathways for a single KO
- Multiple enzymes with identical KO assignments
- Conflicting regulatory classifications

**User-facing consequence:**

Users encounter all possible associations and must interpret biological relevance based on research context, sample origin, or experimental validation.

**Design principle:**

Ambiguity preservation is intentional. Automated disambiguation would require assumptions about biological context (e.g., "which compound is more likely in soil vs. marine environments?") that cannot be generalized across BioRemPP's diverse use cases.

---

## 6. Determinism and Reproducibility

### 6.1 Exact Matching

**String comparison:**

All join operations use exact string matching via pandas `merge()` function with default equality semantics.

- **Case-sensitive:** `K00001` ≠ `k00001`
- **Whitespace-sensitive:** Leading/trailing spaces cause match failures
- **No type coercion:** String `"K00001"` ≠ Integer `00001`

**No fuzzy matching:**

BioRemPP does not apply:

- Levenshtein distance
- Phonetic matching
- Regular expression patterns
- Probabilistic matching

**Consequence:**

Typographical errors in input KO identifiers result in match failures. Validation layer rejects malformed KO identifiers before matching.

---

### 6.2 Absence of Randomization

**Deterministic pipeline:**

No stage of the integration pipeline introduces:

- Random sampling
- Probabilistic selection
- Stochastic processes
- Non-deterministic ordering (with one exception: see below)

**Exception: DataFrame row order**

Pandas merge operations do not guarantee row order stability across Python versions or pandas versions. However, **content** (which rows are present and their values) is deterministic.

**Implication:**

- Same input + same databases → same output rows with same values
- Row order may vary between executions (but see cache normalization below)

---

### 6.3 Cache Determinism

**Cache key generation:**

Before caching, input datasets are normalized:

1. **Samples sorted** by sample ID (lexicographic)
2. **KOs within each sample sorted** alphabetically
3. **Normalized content serialized** as string
4. **SHA256 hash computed** from normalized string

**Determinism guarantee:**

Same dataset uploaded in different order → same cache key → same cached result.

**Cache properties:**

- **TTL (Time-to-Live):** 3600 seconds (1 hour)
- **Max entries:** 100 (FIFO eviction)
- **Storage:** In-memory or Redis

**Cache hit behavior:**

If cache key matches an unexpired entry, entire integration pipeline is skipped. Cached result is returned immediately.

**Reproducibility implication:**

First upload executes full pipeline. Subsequent uploads within 1 hour retrieve cached result. Both return identical data, but processing is bypassed on cache hit.

---

### 6.4 Reproducibility Guarantees and Limitations

| Aspect | Guaranteed | Not Guaranteed |
|--------|-----------|----------------|
| **Same input → same output** | ✅ Yes (if databases unchanged) | ❌ No (if databases updated) |
| **Order independence** | ✅ Yes (after cache normalization) | ❌ Row order may vary |
| **Platform independence** | ✅ Yes (deterministic merges) | ❌ Pandas version differences may affect edge cases |
| **Null handling** | ✅ Consistent (preserved, except toxCSM) | — |
| **Timestamps** | ❌ No (`created_at` fields use system time) | — |
| **Database versioning** | ❌ No (databases are file-based, no embedded version) | — |

**Critical limitation: Database versioning**

BioRemPP databases are loaded from CSV files without embedded version identifiers or checksums. Updates to database files will change integration results for identical input KO sets.

**User responsibility for reproducibility:**

To ensure reproducibility, users must:

1. **Document BioRemPP version** (service version, e.g., v1.0.0)
2. **Record analysis date** (database snapshot date)
3. **Preserve input file** (original KO annotations)
4. **Archive result downloads** (database exports)
5. **Compute database checksums** (optional: SHA256 of CSV files)

**Reproducibility checklist:**

- [ ] BioRemPP service version
- [ ] Analysis execution date
- [ ] Input file (KO annotations)
- [ ] Annotation tool and version (e.g., eggNOG-mapper v2.1.12)
- [ ] Database access date
- [ ] Database file checksums (if available)
- [ ] Use case IDs analyzed
- [ ] Non-default parameters (if any)

---

## 7. Scope and Limitations

BioRemPP provides **exploratory functional inference** of bioremediation potential based on genetic annotations. Results represent **genetic capacity**, not confirmed biological activity, gene expression, or degradation rates.

**Critical boundaries:**

- Genetic potential ≠ biological activity
- No kinetic modeling or expression weighting
- Computational predictions require experimental validation
- Not suitable for regulatory compliance or clinical decisions

For complete documentation of scope boundaries, methodological constraints, interpretation guidelines, and usage restrictions, see **[Limitations and Scope Boundaries](limitations.md)**.

---

## 8. Implementation Traceability

BioRemPP mapping layer is implemented in the following codebase components:

| Component | File Path | Responsibility |
|-----------|-----------|----------------|
| **KO Value Object** | `src/domain/value_objects/kegg_orthology.py` | KO format validation, immutable KO type |
| **Sample Entity** | `src/domain/entities/sample.py` | Sample-level deduplication, KO list management |
| **Dataset Entity** | `src/domain/entities/dataset.py` | Dataset validation, consistency checks |
| **Sample Parser** | `src/application/core/sample_parser.py` | FASTA-like format parsing, entity construction |
| **Upload Handler** | `src/application/core/upload_handler.py` | File upload processing, base64 decoding |
| **Validation Service** | `src/domain/services/validation_service.py` | Multi-layer validation (format, entity, domain) |
| **Data Processor** | `src/application/core/data_processor.py` | Pipeline orchestration, retry logic, circuit breakers |
| **Data Processing Service** | `src/presentation/services/data_processing_service.py` | Database merge implementations (BioRemPP, KEGG, HADEG, toxCSM) |
| **BioRemPP Repository** | `src/infrastructure/persistence/biorempp_repository.py` | BioRemPP database loading, schema validation |
| **KEGG Repository** | `src/infrastructure/persistence/kegg_repository.py` | KEGG database loading, schema validation |
| **HADEG Repository** | `src/infrastructure/persistence/hadeg_repository.py` | HADEG database loading, schema validation |
| **ToxCSM Repository** | `src/infrastructure/persistence/toxcsm_repository.py` | ToxCSM database loading, compound-based joins |
| **CSV Base Repository** | `src/infrastructure/persistence/csv_database_repository.py` | Generic CSV loading, caching, dtype optimization |
| **Cache Service** | `src/application/services/cache_service.py` | Cache key generation (SHA256), TTL management |
| **Database Config** | `src/infrastructure/config/database_config.py` | Database paths, encoding, separator configuration |
| **Application Settings** | `config/settings.py` | Validation patterns, limits, timeout configuration |

**Configuration files:**

- `config/settings.py`: Default limits and patterns
- `config/databases.yaml`: Optional database path overrides (if present)

**Environment variables:**

All structural constraints and validation patterns are configurable via environment variables prefixed with `BIOREMPP_`.

---

## Related Pages

- [Methods Overview](methods-overview.md) — High-level scientific methodology
- [Data Sources](data-sources.md) — Detailed database descriptions
- [Database Schemas](../database_schemas/biorempp-schema.md) — Formal schema specifications for all databases
- [Regulatory Frameworks](regulatory-frameworks.md) — Integration of regulatory classifications
- [Input Format](../getting-started/input-format.md) — User-facing input specification
- [Interpretation Guidelines](../user-guide/interpretation.md) — How to interpret mapping results
- [Downloads Guide](../user-guide/downloads.md) — Reproducibility requirements for exported data
