"""Typed configuration loader for internal validation."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List

import yaml

from .constants import KO_REGEX_DEFAULT


@dataclass(frozen=True)
class DatabasePathConfig:
    """Input CSV paths relative to repository root."""

    biorempp_db_path: str
    kegg_db_path: str
    hadeg_db_path: str
    toxcsm_db_path: str

    def as_dict(self) -> Dict[str, str]:
        return {
            "BioRemPP": self.biorempp_db_path,
            "KEGG": self.kegg_db_path,
            "HADEG": self.hadeg_db_path,
            "toxCSM": self.toxcsm_db_path,
        }


@dataclass(frozen=True)
class OutputDirsConfig:
    """Output directories used by the suite."""

    outputs_versioned_dir: str
    outputs_latest_dir: str


@dataclass(frozen=True)
class ValidationParametersConfig:
    """Validation thresholds and required columns."""

    top_n: int
    min_expected_rows: int
    max_null_percentage: float
    mapping_cpd_non_null_mostly: float
    allowed_reference_agencies: List[str]
    allowed_ko_regex: str
    required_columns: Dict[str, List[str]]
    expected_row_counts: Dict[str, int]


@dataclass(frozen=True)
class GXAssetConfig:
    """GX asset definition for filesystem csv files."""

    file: str
    sep: str
    required_columns_ref: str


@dataclass(frozen=True)
class GXCheckpointNames:
    """Named checkpoints used by the suite."""

    full: str
    schema: str


@dataclass(frozen=True)
class GXConfig:
    """Great Expectations runtime configuration."""

    context_root: str
    datasource_name: str
    datasource_base_directory: str
    data_docs_site_name: str
    checkpoint_names: GXCheckpointNames
    assets: Dict[str, GXAssetConfig]


@dataclass(frozen=True)
class ValidationConfig:
    """Root configuration object for the GX-first suite."""

    database_paths: DatabasePathConfig
    output_dirs: OutputDirsConfig
    example_datasets_dir: str
    validation_parameters: ValidationParametersConfig
    gx: GXConfig

    @classmethod
    def from_dict(cls, raw: Dict[str, Any]) -> "ValidationConfig":
        db = raw["database_paths"]
        out = raw["output_dirs"]
        params = raw.get("validation_parameters", {})
        gx_raw = raw["gx"]

        assets = {
            name: GXAssetConfig(
                file=cfg["file"],
                sep=cfg.get("sep", ";"),
                required_columns_ref=cfg["required_columns_ref"],
            )
            for name, cfg in gx_raw.get("assets", {}).items()
        }

        return cls(
            database_paths=DatabasePathConfig(
                biorempp_db_path=db["biorempp_db_path"],
                kegg_db_path=db["kegg_db_path"],
                hadeg_db_path=db["hadeg_db_path"],
                toxcsm_db_path=db["toxcsm_db_path"],
            ),
            output_dirs=OutputDirsConfig(
                outputs_versioned_dir=out["outputs_versioned_dir"],
                outputs_latest_dir=out["outputs_latest_dir"],
            ),
            example_datasets_dir=raw["example_datasets_dir"],
            validation_parameters=ValidationParametersConfig(
                top_n=int(params.get("top_n", 20)),
                min_expected_rows=int(params.get("min_expected_rows", 1)),
                max_null_percentage=float(params.get("max_null_percentage", 50.0)),
                mapping_cpd_non_null_mostly=float(
                    params.get("mapping_cpd_non_null_mostly", 0.95)
                ),
                allowed_reference_agencies=list(
                    params.get("allowed_reference_agencies", [])
                ),
                allowed_ko_regex=params.get("allowed_ko_regex", KO_REGEX_DEFAULT),
                required_columns=dict(params.get("required_columns", {})),
                expected_row_counts={
                    str(k): int(v)
                    for k, v in dict(params.get("expected_row_counts", {})).items()
                },
            ),
            gx=GXConfig(
                context_root=gx_raw["context_root"],
                datasource_name=gx_raw["datasource_name"],
                datasource_base_directory=gx_raw["datasource_base_directory"],
                data_docs_site_name=gx_raw.get("data_docs_site_name", "local_site"),
                checkpoint_names=GXCheckpointNames(
                    full=gx_raw["checkpoint_names"]["full"],
                    schema=gx_raw["checkpoint_names"]["schema"],
                ),
                assets=assets,
            ),
        )


def load_validation_config(config_path: Path) -> ValidationConfig:
    """Load and parse validation config from YAML."""
    with config_path.open("r", encoding="utf-8") as fh:
        raw = yaml.safe_load(fh)
    return ValidationConfig.from_dict(raw)
