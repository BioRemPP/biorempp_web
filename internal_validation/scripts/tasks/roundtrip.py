"""Hybrid roundtrip regression and merged invariants checks."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Dict, List, Tuple

import pandas as pd

from internal_validation.scripts.common import (
    compute_dataframe_hash,
    compute_file_sha256,
    load_csv,
)
from internal_validation.scripts.common.config import ValidationConfig


def _load_example_dataset(path: Path) -> pd.DataFrame:
    samples: List[str] = []
    kos: List[str] = []
    current_sample = None

    with path.open("r", encoding="utf-8") as fh:
        for raw in fh:
            line = raw.strip()
            if not line:
                continue
            if line.startswith(">"):
                current_sample = line[1:]
                continue
            if current_sample is None:
                raise ValueError(f"Invalid dataset format (missing sample): {path}")
            samples.append(current_sample)
            kos.append(line)
    return pd.DataFrame({"Sample": samples, "ko": kos})


def _load_databases(repo_root: Path, config: ValidationConfig) -> Dict[str, pd.DataFrame]:
    mapping = config.database_paths.as_dict()
    return {name: load_csv(repo_root / rel) for name, rel in mapping.items()}


def _merge_all(example_df: pd.DataFrame, dbs: Dict[str, pd.DataFrame]) -> Dict[str, pd.DataFrame]:
    biorempp = example_df.merge(dbs["BioRemPP"], on="ko", how="left")
    kegg = example_df.merge(dbs["KEGG"], on="ko", how="left")
    hadeg = example_df.merge(dbs["HADEG"], on="ko", how="left")
    toxcsm = biorempp.merge(dbs["toxCSM"], on="cpd", how="left", suffixes=("", "_toxcsm"))
    return {"biorempp": biorempp, "kegg": kegg, "hadeg": hadeg, "toxcsm": toxcsm}


def _save_merged_outputs(base_dir: Path, merged: Dict[str, pd.DataFrame]) -> Dict[str, str]:
    files: Dict[str, str] = {}
    for key, df in merged.items():
        out = base_dir / f"merged_{key}.csv"
        out.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(out, sep=";", index=False, encoding="utf-8")
        files[key] = str(out)
    return files


def run_roundtrip_regression(
    repo_root: Path, config: ValidationConfig, output_dir: Path
) -> Dict[str, object]:
    """Run deterministic roundtrip merges and hash outputs."""
    example_dir = repo_root / config.example_datasets_dir
    if not example_dir.exists():
        return {"datasets_processed": 0, "datasets": [], "note": "No example dataset directory."}

    dbs = _load_databases(repo_root, config)
    datasets = sorted(example_dir.glob("*.txt"))
    results = []

    for dataset in datasets:
        dataset_name = dataset.stem
        dataset_base = output_dir / "artifacts" / dataset_name
        example_df = _load_example_dataset(dataset)
        merged = _merge_all(example_df, dbs)
        output_files = _save_merged_outputs(dataset_base, merged)
        output_checksums = {k: compute_file_sha256(Path(v)) for k, v in output_files.items()}
        content_hashes = {
            f"{k}_content": compute_dataframe_hash(v) for k, v in merged.items()
        }

        stats = {
            "input_rows": int(len(example_df)),
            "unique_kos": int(example_df["ko"].nunique()),
            "biorempp_matches": int(merged["biorempp"]["cpd"].notna().sum())
            if "cpd" in merged["biorempp"]
            else 0,
            "kegg_matches": int(merged["kegg"]["pathname"].notna().sum())
            if "pathname" in merged["kegg"]
            else 0,
            "hadeg_matches": int(merged["hadeg"]["Gene"].notna().sum())
            if "Gene" in merged["hadeg"]
            else 0,
            "toxcsm_matches": int(merged["toxcsm"]["SMILES"].notna().sum())
            if "SMILES" in merged["toxcsm"]
            else 0,
        }

        results.append(
            {
                "dataset_name": dataset_name,
                "dataset_path": str(dataset),
                "input_sha256": compute_file_sha256(dataset),
                "statistics": stats,
                "output_checksums": output_checksums,
                "content_hashes": content_hashes,
                "output_files": output_files,
            }
        )

    return {"datasets_processed": len(results), "datasets": results}


def _check_example_invariants(
    df: pd.DataFrame, allowed_ko_regex: str, allowed_agencies: List[str]
) -> Tuple[bool, Dict[str, object]]:
    ko_re = re.compile(allowed_ko_regex)
    fail_reasons: List[str] = []

    if "ko" in df.columns:
        invalid_kos = df["ko"].dropna().astype(str).loc[~df["ko"].dropna().astype(str).str.match(ko_re)]
        if len(invalid_kos) > 0:
            fail_reasons.append(f"invalid_ko_count={len(invalid_kos)}")

    if "Sample" in df.columns:
        empty_samples = int(df["Sample"].isna().sum() + (df["Sample"].astype(str).str.strip() == "").sum())
        if empty_samples > 0:
            fail_reasons.append(f"empty_samples={empty_samples}")

    if "referenceAG" in df.columns:
        invalid = set(df["referenceAG"].dropna().astype(str).unique()) - set(allowed_agencies)
        if invalid:
            fail_reasons.append(f"invalid_agencies={sorted(invalid)}")

    value_cols = [c for c in df.columns if c.startswith("value_")]
    for col in value_cols:
        numeric = pd.to_numeric(df[col], errors="coerce")
        negatives = int((numeric < 0).sum())
        gt_one = int((numeric > 1).sum())
        if negatives > 0 or gt_one > 0:
            fail_reasons.append(f"{col}:neg={negatives},gt1={gt_one}")

    return (len(fail_reasons) == 0, {"fail_reasons": fail_reasons})


def run_roundtrip_invariants(
    roundtrip_result: Dict[str, object], config: ValidationConfig
) -> Dict[str, object]:
    """Run invariant checks directly on merged roundtrip outputs."""
    checks = []
    all_passed = True
    datasets = roundtrip_result.get("datasets", [])
    for item in datasets:
        dataset_name = item["dataset_name"]
        for merged_name, path in item["output_files"].items():
            if merged_name not in {"biorempp", "toxcsm"}:
                continue
            df = load_csv(Path(path))
            passed, details = _check_example_invariants(
                df,
                config.validation_parameters.allowed_ko_regex,
                config.validation_parameters.allowed_reference_agencies,
            )
            checks.append(
                {
                    "dataset": dataset_name,
                    "merged": merged_name,
                    "passed": passed,
                    **details,
                }
            )
            if not passed:
                all_passed = False

    return {"overall_pass": all_passed, "checks": checks}

