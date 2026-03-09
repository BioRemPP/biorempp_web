# BioRemPP Internal Validation (GX-First)

This directory contains the official internal validation suite for BioRemPP using
Great Expectations (`>=1.12,<2.0`) with hybrid analytical tasks for provenance,
cross-database overlap, and roundtrip determinism.

## Main Commands

```bash
python internal_validation/scripts/run_all_gx.py --checkpoint biorempp_full_validation
python internal_validation/scripts/run_all_gx.py --schema-only
python internal_validation/scripts/run_all_gx.py --ci
```

## Directory Layout

```text
internal_validation/
|-- config/
|   `-- validation_config.yaml
|-- data/
|   `-- example_datasets/
|-- docs/
|   `-- migration/
|-- gx_context/
|   `-- gx.yaml
|-- outputs/
|-- outputs_latest/
|-- plugins/
|-- scripts/
|   |-- run_all_gx.py
|   |-- ci_validation.py
|   |-- init_gx_context.py
|   |-- configure_data_sources.py
|   `-- tasks/
`-- suites/
    |-- schema/
    |-- mapping/
    |-- invariants/
    `-- vocabulary/
```

## Notes

- Outputs are written to:
  - `internal_validation/outputs/YYYY-MM-DD/`
  - `internal_validation/outputs_latest/`
- Data Docs are generated at:
  - `internal_validation/gx_context/uncommitted/data_docs/local_site/`

