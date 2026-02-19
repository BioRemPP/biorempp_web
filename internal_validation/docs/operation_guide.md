# Operation Guide (GX-First)

## Setup

```bash
python internal_validation/scripts/init_gx_context.py
python internal_validation/scripts/configure_data_sources.py
python internal_validation/scripts/create_validation_definitions.py
python internal_validation/scripts/create_checkpoints.py
python internal_validation/scripts/create_baseline_snapshot.py
```

## Daily Runs

```bash
python internal_validation/scripts/run_all_gx.py --checkpoint biorempp_full_validation
python internal_validation/scripts/run_all_gx.py --schema-only
python internal_validation/scripts/run_all_gx.py --ci
```

## Output Contracts

- Versioned outputs: `internal_validation/outputs/YYYY-MM-DD/`
- Latest outputs: `internal_validation/outputs_latest/`
- Data Docs: `internal_validation/gx_context/uncommitted/data_docs/local_site/`

## Exit Semantics

- `run_all_gx.py`: returns `0` on full success, `1` on validation failures
- `ci_validation.py`:
  - `0`: all checks passed
  - `1`: one or more checks failed
  - `2`: execution error

## Cutover Rule

Only mark cutover complete when:

1. Baseline parity has no critical failures.
2. CI pipeline passes on `main`.
3. Team confirms this directory as canonical (`internal_validation/`).

