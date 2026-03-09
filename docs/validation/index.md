# Validation & Quality Assurance

BioRemPP employs a **three-pillar validation framework** to ensure data integrity, computational transparency, and functional correctness. This section documents the internal validation strategies used to establish reproducibility, consistency, and reliability of the web service.

---

## Quick Navigation

| Validation Pillar | Focus | Documentation |
|------------------|-------|---------------|
| **Internal Validation Suite** | Data integration coherence and analytical reproducibility | [Validation Suite](validation-suite.md), [Internal Validation](internal-validation.md) |
| **Computational Profiling** | Performance characterization and computational transparency | [Computational Profiling](profiling-biorempp.md) |
| **Unit Test Suite** | Functional correctness and regression detection | [Unit Test Suite](test-suite.md) |

---

## Overview: Three-Pillar Validation Framework

Each pillar provides distinct but complementary evidence of platform reliability:

| Aspect | Internal Validation | Profiling | Unit Tests |
|--------|-------------------|-----------|------------|
| **Purpose** | Scientific coherence | Computational transparency | Functional correctness |
| **Validates** | Cross-database consistency, mapping logic | Resource consumption, execution stability | Component behavior, business rules |
| **Evidence** | Structural plausibility, reproducible outputs | Baseline metrics, deterministic performance | Regression-free code, invariant preservation |
| **Scope** | Data integration layer | Runtime behavior | Software components |

---

## Pillar 1: Internal Validation Suite

**[Full Documentation ->](validation-suite.md) | [Detailed Analysis ->](internal-validation.md)**

### Purpose

The Internal Validation Suite ensures that integrated data behave coherently, analytical outputs are structurally plausible, and results are reproducible under identical input conditions.

### Structure: 7 Validation Components

| Component | Domain | Evidence Provided |
|-----------|--------|-------------------|
| **Provenance Snapshot** | Data stability | Database checksums (SHA-256), version fingerprints |
| **Schema Integrity** | Data integrity | Required-field presence, structural consistency |
| **Cross-Database Overlap** | Integration coherence | Expected concordance/complementarity across KO universes |
| **Mapping Consistency** | Mapping coherence | KO->compound and compound->toxicity linkage patterns |
| **Example Roundtrip Regression** | Reproducibility | Stable outputs for standardized example inputs |
| **Use Case Invariants** | Output correctness | Logical constraints preserved in representative outputs |
| **Controlled Vocabulary Audit** | Semantic stability | Drift monitoring for controlled terms |

### Key Features

- **Cross-Resource Coherence**: Validates expected overlap and divergence patterns across BioRemPP, KEGG, HADEG, and toxCSM databases.
- **Deterministic Mapping**: Exact identifier matching (no probabilistic inference or fuzzy matching).
- **GX Declarative Layer**: Great Expectations suites/checkpoints encode schema, mapping, invariants, and vocabulary constraints.
- **Hybrid Analytical Tasks**: Provenance, overlap, and roundtrip regression are executed as deterministic Python tasks integrated into the same run summary.
- **Versioned Resources**: All databases are checksummed with SHA-256 for integrity verification.
- **Declarative Configuration**: YAML-driven analyses ensure auditability and parameter transparency.

### What It Does NOT Validate

- Experimental degradation outcomes (requires wet-lab validation)
- Predictive accuracy (no field-wide gold-standard dataset exists)
- Regulatory compliance or approval
- Superiority over alternative tools (no comparable platforms exist)

---

## Pillar 2: Computational Profiling

**[Full Documentation ->](profiling-biorempp.md)**

**Profiling Suite Version:** v1.0  
**Last Run:** 2026-01-17

### Purpose

Computational profiling characterizes the runtime behavior of the BioRemPP web service, documenting resource consumption, execution stability, and computational transparency as part of the internal validation and reproducibility framework.

### Profiling Methodology

**Target-Based Strategy**: 5 profiling targets representing functional pipeline components

| Target | Pipeline Stage | Characterizes |
|--------|---------------|---------------|
| `database_load` | Initialization | Loading 12,961 records from 4 CSV databases |
| `biorempp_operations` | Core Processing | In-memory DataFrame operations (filter, transform, melt) |
| `io_operations` | Output Generation | Serialization to Excel and JSON formats |
| `batch_export` | Batch Processing | Multi-format export (CSV, XLSX, JSON) |
| `data_transforms` | Advanced Processing | Normalization and aggregation with scikit-learn/scipy |

**Instrumentation Stack:**

- **cProfile**: CPU profiling with cumulative time sorting
- **tracemalloc**: Memory allocation tracking
- **psutil**: Process-level memory monitoring

### Summary Results

| Target | Time (s) | Memory Delta (MB) | Peak (MB) | Function Calls | Status |
|--------|----------|-------------------|-----------|----------------|--------|
| database_load | 2.884 | 84.8 | 38.4 | 443,164 | PASS |
| biorempp_operations | 0.270 | -1.2 | 6.3 | 17,622 | PASS |
| io_operations | 2.313 | 9.0 | 8.1 | 669,364 | PASS |
| batch_export | 2.664 | 3.7 | 3.3 | 697,125 | PASS |
| data_transforms | 4.367 | 71.0 | 36.7 | 727,729 | PASS |

**Total Execution Time:** 12.50 seconds  
**Total Memory Allocated:** 167.3 MB  
**Success Rate:** 100% (5/5 targets)

### Key Features

- **Baseline Characterization**: Establishes expected resource consumption patterns
- **Reproducible Execution**: Deterministic targets produce identical outputs
- **Structured Reporting**: JSON summaries enable programmatic comparison across runs
- **Audit Trail Support**: Timestamped reports linked to versioned databases

### What It Does NOT Validate

- Biological accuracy of predictions
- Production-scale concurrency behavior
- Comparative performance against other tools
- Experimental validation of results

---

## Pillar 3: Unit Test Suite

**[Full Documentation ->](test-suite.md)**

**Test Framework:** pytest  
**Total Test Modules:** 53

### Purpose

The Unit Test Suite provides automated verification of component behavior, enabling regression detection, maintaining functional correctness, and ensuring that identical inputs produce identical outputs across software versions.

### Test Organization by Architectural Layer

```text
tests/unit/
|-- application/     # 25+ modules: services, DTOs, mappers, plot services
|-- domain/          # 20+ modules: entities, value objects, strategies
`-- infrastructure/  # 8+ modules: cache, config, repositories
```

| Layer | Responsibility | Test Focus |
|-------|----------------|------------|
| **Domain** | Business rules and entities | Validation, invariants, behavior |
| **Application** | Use cases and orchestration | Coordination, data flow, transformations |
| **Infrastructure** | Technical concerns | Persistence, caching, configuration |

### Test Coverage Highlights

**Visualization Strategies (19 tests)**

- Statistical: Correlogram, PCA, Hierarchical Clustering
- Distribution: Box-Scatter, Density, Stacked Bar
- Relationship: Network, Chord, Sankey
- Hierarchical: Treemap, Sunburst

**Repository Tests**

- BioRemPPRepository, KEGGRepository, HADEGRepository, ToxCSMRepository
- CSV-based data sources with type optimization and error handling

**Cache Components**

- MemoryCache (TTL, LRU eviction, size limits)
- DataFrameCache (pandas serialization)
- GraphCache (network graph caching)

### Test Design Principles

- **Determinism**: Consistent results across executions
- **Isolation**: Independent tests without shared state
- **Dependency Substitution**: Mocks and stubs for fast execution
- **Clarity**: Descriptive names and docstrings as documentation

### What It Does NOT Cover

- Biological validation (experimental accuracy)
- External benchmarking (comparative tool evaluation)
- UI testing (Dash component rendering)
- Performance benchmarking (execution time targets)

---

## Validation Scope Summary

### What BioRemPP Validation Establishes

- **Data Integration Coherence**: Cross-database consistency and expected overlap patterns
- **Structural Plausibility**: Mapping cardinality, identifier integrity, controlled vocabularies
- **Computational Reproducibility**: Deterministic outputs, versioned databases, parameter transparency
- **Functional Correctness**: Component behavior matches specifications, regressions detected
- **Performance Transparency**: Baseline resource consumption documented

### What BioRemPP Validation Does NOT Claim

- **Experimental Validation**: Wet-lab confirmation of degradation predictions
- **Predictive Accuracy**: Sensitivity/specificity against gold-standard datasets (none exist)
- **Regulatory Compliance**: Certification or approval for environmental decision-making
- **Comparative Superiority**: Benchmarking against alternative tools (no comparable platforms)
- **Real-World Performance**: Gene expression, enzymatic activity, or in situ degradation

---

## Reproducibility Requirements

All validation evidence is linked to specific versions and conditions:

| Resource | Version | Checksum (SHA-256) |
|----------|---------|-------------------|
| BioRemPP Database | v1.0.0 | `216cf113...` |
| KEGG Degradation | Release 116.0+/12-19 | `f3df93d3...` |
| HADEG | Commit 8f1ff8f | `d546c01b...` |
| ToxCSM | v1.0 | `0d461693...` |

**To reproduce validation results:**

1. Use identical database versions (checksummed)
2. Run the official suite command: `python internal_validation/scripts/run_all_gx.py --checkpoint biorempp_full_validation`
3. Document execution environment (Python 3.11+)
4. Link results to `internal_validation/outputs_latest/index.json` and run timestamp

---

## Related Documentation

- **[Methods Overview](../methods/methods-overview.md)** - Scientific methodology and analytical framework
- **[Data Sources](../methods/data-sources.md)** - Database provenance and scope
- **[Mapping Strategy](../methods/mapping-strategy.md)** - Integration logic and join mechanisms
- **[Limitations](../methods/limitations.md)** - Comprehensive scope boundaries
- **[Interpretation Guidelines](../user-guide/interpretation.md)** - Responsible result interpretation

---

## Questions?

For technical details on validation implementation, see the individual documentation pages linked above. For questions about validation scope or methodology, refer to the [Limitations](../methods/limitations.md) page.
