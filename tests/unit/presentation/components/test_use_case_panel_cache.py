"""Unit tests for UC panel YAML cache behavior (Phase 1.2)."""

import os
from pathlib import Path

import pytest
import yaml

from src.presentation.components.base.use_case_panel import (
    clear_use_case_config_cache,
    get_use_case_config_cache_stats,
    load_use_case_config,
)


@pytest.fixture(autouse=True)
def _reset_uc_panel_cache():
    """Ensure cache does not leak state across tests."""
    clear_use_case_config_cache()
    yield
    clear_use_case_config_cache()


def _write_uc_yaml(path: Path, description: str) -> None:
    """Write minimal valid UC YAML configuration file."""
    payload = {
        "use_case_id": "uc-test-1",
        "scientific_question": "Test question?",
        "description": description,
    }
    path.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")


def test_load_use_case_config_uses_cache_hit_when_enabled(monkeypatch, tmp_path):
    """Second read should be cache hit and return isolated copy."""
    monkeypatch.setenv("BIOREMPP_UC_PANEL_CACHE_ENABLED", "true")
    monkeypatch.setenv("BIOREMPP_UC_PANEL_CACHE_VALIDATE_MTIME", "true")

    config_path = tmp_path / "uc_cache_hit.yaml"
    _write_uc_yaml(config_path, description="v1")

    first = load_use_case_config(str(config_path))
    # Mutate caller copy to ensure cache stays immutable for subsequent reads.
    first["description"] = "mutated-by-caller"
    second = load_use_case_config(str(config_path))
    stats = get_use_case_config_cache_stats()

    assert second["description"] == "v1"
    assert stats["entries"] == 1
    assert stats["hits"] == 1
    assert stats["misses"] == 1


def test_load_use_case_config_invalidates_cache_on_file_change(monkeypatch, tmp_path):
    """Changed mtime/content should force miss and refresh cached config."""
    monkeypatch.setenv("BIOREMPP_UC_PANEL_CACHE_ENABLED", "true")
    monkeypatch.setenv("BIOREMPP_UC_PANEL_CACHE_VALIDATE_MTIME", "true")

    config_path = tmp_path / "uc_cache_invalidate.yaml"
    _write_uc_yaml(config_path, description="before")
    first = load_use_case_config(str(config_path))
    assert first["description"] == "before"

    _write_uc_yaml(config_path, description="after")
    current_stat = config_path.stat()
    # Guarantee mtime delta even on coarse timestamp filesystems.
    os.utime(
        config_path,
        ns=(current_stat.st_atime_ns + 1_000_000, current_stat.st_mtime_ns + 1_000_000),
    )
    second = load_use_case_config(str(config_path))
    stats = get_use_case_config_cache_stats()

    assert second["description"] == "after"
    assert stats["entries"] == 1
    assert stats["hits"] == 0
    assert stats["misses"] == 2


def test_load_use_case_config_bypasses_cache_when_disabled(monkeypatch, tmp_path):
    """Disabled cache should not keep entries in memory."""
    monkeypatch.setenv("BIOREMPP_UC_PANEL_CACHE_ENABLED", "false")
    monkeypatch.setenv("BIOREMPP_UC_PANEL_CACHE_VALIDATE_MTIME", "true")

    config_path = tmp_path / "uc_cache_disabled.yaml"
    _write_uc_yaml(config_path, description="first")
    first = load_use_case_config(str(config_path))
    assert first["description"] == "first"

    _write_uc_yaml(config_path, description="second")
    second = load_use_case_config(str(config_path))
    stats = get_use_case_config_cache_stats()

    assert second["description"] == "second"
    assert stats["enabled"] is False
    assert stats["entries"] == 0
    assert stats["hits"] == 0
    assert stats["misses"] == 0


def test_load_use_case_config_raises_value_error_for_non_mapping_yaml(
    monkeypatch, tmp_path
):
    """Invalid YAML root type should raise explicit ValueError."""
    monkeypatch.setenv("BIOREMPP_UC_PANEL_CACHE_ENABLED", "true")
    config_path = tmp_path / "uc_invalid.yaml"
    config_path.write_text("- invalid\n- yaml\n", encoding="utf-8")

    with pytest.raises(ValueError, match="expected mapping"):
        load_use_case_config(str(config_path))
