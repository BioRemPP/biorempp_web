"""Unified GX-first runner for BioRemPP internal validation."""

from __future__ import annotations

import argparse
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

import pandas as pd


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from internal_validation.scripts.common import (
    RunSummary,
    checkpoint_result_to_dict,
    configure_data_source_from_config,
    ensure_gx_context,
    get_repo_root,
    load_csv,
    load_validation_config,
    write_json,
)
from internal_validation.scripts.create_checkpoints import create_checkpoints
from internal_validation.scripts.create_validation_definitions import (
    create_all_validation_definitions,
)
from internal_validation.scripts.tasks.overlap import run_cross_database_overlap
from internal_validation.scripts.tasks.parity import compare_run_with_baseline
from internal_validation.scripts.tasks.provenance import run_provenance_snapshot
from internal_validation.scripts.tasks.roundtrip import (
    run_roundtrip_invariants,
    run_roundtrip_regression,
)


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _date_dir() -> str:
    return _utc_now().strftime("%Y-%m-%d")


def _run_id() -> str:
    return _utc_now().strftime("%Y%m%dT%H%M%SZ")


def _output_roots(repo_root: Path, config) -> List[Path]:
    versioned = repo_root / config.output_dirs.outputs_versioned_dir / _date_dir()
    latest = repo_root / config.output_dirs.outputs_latest_dir
    versioned.mkdir(parents=True, exist_ok=True)
    latest.mkdir(parents=True, exist_ok=True)
    return [versioned, latest]


def _write_payload_to_roots(roots: List[Path], task_name: str, payload: Dict[str, Any]) -> None:
    for root in roots:
        write_json(root / task_name / "summary.json", payload)


def _write_index_markdown(root: Path, summary: RunSummary) -> None:
    lines = [
        "# Internal Validation GX Run",
        "",
        f"- Run ID: `{summary.run_id}`",
        f"- Checkpoint: `{summary.checkpoint_name}`",
        f"- Overall Success: `{summary.overall_success}`",
        f"- Checkpoint Success: `{summary.checkpoint_success}`",
        f"- Timestamp UTC: `{summary.timestamp_utc}`",
        "",
        "## Validation Definitions",
        "",
        "| Validation Definition | Success | Evaluated | Failed |",
        "|---|---|---:|---:|",
    ]
    for row in summary.checkpoint_results:
        stats = row.get("statistics", {})
        lines.append(
            f"| {row.get('validation_definition_name')} | {row.get('success')} | "
            f"{stats.get('evaluated_expectations', 0)} | "
            f"{stats.get('unsuccessful_expectations', 0)} |"
        )
    lines.extend(["", "## Hybrid Tasks", "", "```json", str(summary.hybrid_tasks), "```", ""])
    path = root / "index.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def _export_vocabulary_csvs(repo_root: Path, roots: List[Path], config) -> Dict[str, Any]:
    biorempp_df = load_csv(repo_root / config.database_paths.biorempp_db_path)
    columns = ["compoundclass", "referenceAG", "enzyme_activity"]
    summary: Dict[str, Any] = {}
    for col in columns:
        if col not in biorempp_df.columns:
            summary[col] = {"error": "column_not_found"}
            continue
        value_counts = biorempp_df[col].value_counts(dropna=False)
        rows = []
        for value, count in value_counts.items():
            value_str = "[NULL]" if pd.isna(value) else str(value)
            rows.append(
                {
                    "value": value_str,
                    "count": int(count),
                    "percentage": round((count / len(biorempp_df)) * 100, 2),
                }
            )
        summary[col] = {"unique_values": int(biorempp_df[col].nunique(dropna=True)), "rows": rows}

        for root in roots:
            out = root / "07_controlled_vocabulary_audit" / "artifacts" / f"vocab_{col}.csv"
            out.parent.mkdir(parents=True, exist_ok=True)
            pd.DataFrame(rows).to_csv(out, sep=";", index=False, encoding="utf-8")
    return summary


def run_pipeline(
    checkpoint_name: str | None = None,
    schema_only: bool = False,
    ci_mode: bool = False,
    open_docs: bool = False,
) -> int:
    repo_root = get_repo_root()
    config = load_validation_config(
        repo_root / "internal_validation" / "config" / "validation_config.yaml"
    )
    roots = _output_roots(repo_root, config)

    context = ensure_gx_context(config)
    configure_data_source_from_config(context, config)
    create_all_validation_definitions(context, config)
    create_checkpoints(context, config)

    if schema_only:
        selected_checkpoint = config.gx.checkpoint_names.schema
    else:
        selected_checkpoint = checkpoint_name or config.gx.checkpoint_names.full

    hybrid: Dict[str, Any] = {}

    provenance = run_provenance_snapshot(repo_root, config)
    overlap = run_cross_database_overlap(repo_root, config)
    _write_payload_to_roots(roots, "01_provenance_snapshot", provenance)
    _write_payload_to_roots(roots, "03_cross_database_overlap", overlap)
    hybrid["provenance"] = {"success": True, "rows": len(provenance.get("databases", {}))}
    hybrid["overlap"] = {"success": True, "pairs": len(overlap.get("pairwise", {}))}

    checkpoint = context.checkpoints.get(selected_checkpoint)
    checkpoint_result = checkpoint.run()

    if not schema_only:
        roundtrip_versioned = run_roundtrip_regression(
            repo_root, config, roots[0] / "05_example_roundtrip_regression"
        )
        roundtrip_latest = run_roundtrip_regression(
            repo_root, config, roots[1] / "05_example_roundtrip_regression"
        )
        invariants = run_roundtrip_invariants(roundtrip_versioned, config)
        _write_payload_to_roots(roots, "05_example_roundtrip_regression", roundtrip_versioned)
        _write_payload_to_roots(roots, "06_uc_invariants", invariants)
        vocab_summary = _export_vocabulary_csvs(repo_root, roots, config)
        _write_payload_to_roots(roots, "07_controlled_vocabulary_audit", vocab_summary)

        hybrid["roundtrip"] = {
            "success": True,
            "datasets_processed": roundtrip_versioned.get("datasets_processed", 0),
        }
        hybrid["invariants"] = {
            "success": bool(invariants.get("overall_pass", False)),
            "checks": len(invariants.get("checks", [])),
        }
        hybrid["vocabulary_export"] = {"success": True, "columns": list(vocab_summary.keys())}
        hybrid["_latest_roundtrip_datasets"] = roundtrip_latest.get("datasets_processed", 0)

    checkpoint_rows = checkpoint_result_to_dict(checkpoint_result)
    checkpoint_success = bool(checkpoint_result.success)
    overall_success = checkpoint_success and all(
        v.get("success", True)
        for k, v in hybrid.items()
        if isinstance(v, dict) and not k.startswith("_")
    )

    summary = RunSummary(
        run_id=_run_id(),
        checkpoint_name=selected_checkpoint,
        overall_success=overall_success,
        checkpoint_success=checkpoint_success,
        checkpoint_results=checkpoint_rows,
        hybrid_tasks=hybrid,
    )

    baseline_path = repo_root / "internal_validation" / "docs" / "migration" / "baseline_snapshot.json"
    if baseline_path.exists() and not schema_only:
        from internal_validation.scripts.common import read_json

        baseline = read_json(baseline_path)
        parity = compare_run_with_baseline(baseline, summary.to_dict())
        summary.hybrid_tasks["parity_comparison"] = parity.to_dict()
        if not parity.passed:
            summary.overall_success = False
            overall_success = False

    for root in roots:
        write_json(root / "index.json", summary.to_dict())
        _write_index_markdown(root, summary)

    if open_docs:
        context.build_data_docs()
        context.open_data_docs()

    print("=" * 80)
    print(f"Checkpoint: {selected_checkpoint}")
    print(f"Checkpoint success: {checkpoint_success}")
    print(f"Overall success: {overall_success}")
    print(f"Versioned output: {roots[0]}")
    print(f"Latest output: {roots[1]}")
    print("=" * 80)

    if ci_mode:
        return 0 if overall_success else 1
    return 0 if overall_success else 1


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run BioRemPP internal validation using GX-first pipeline."
    )
    parser.add_argument(
        "--checkpoint",
        default=None,
        help="Checkpoint to run (default: biorempp_full_validation)",
    )
    parser.add_argument("--schema-only", action="store_true", help="Run schema checkpoint only")
    parser.add_argument("--ci", action="store_true", help="CI mode exit semantics")
    parser.add_argument("--open-docs", action="store_true", help="Open Data Docs after run")
    args = parser.parse_args()
    return run_pipeline(
        checkpoint_name=args.checkpoint,
        schema_only=args.schema_only,
        ci_mode=args.ci,
        open_docs=args.open_docs,
    )


if __name__ == "__main__":
    raise SystemExit(main())

