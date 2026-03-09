"""Unit tests for /results hash navigation helpers."""

from src.presentation.services.results_navigation import (
    normalize_target_hash,
    resolve_fallback_hash,
    resolve_target_module,
)


def test_normalize_target_hash_accepts_legacy_info_panel() -> None:
    assert normalize_target_hash("#uc-4-7-info-panel") == "#uc-4-7-card"


def test_normalize_target_hash_keeps_card_and_module_hashes() -> None:
    assert normalize_target_hash("#uc-2-1-card") == "#uc-2-1-card"
    assert normalize_target_hash("#module8-section") == "#module8-section"
    assert normalize_target_hash("#biorempp-section") == "#biorempp-section"


def test_resolve_target_module_for_uc_and_module_hashes() -> None:
    assert resolve_target_module("#uc-2-1-card") == 2
    assert resolve_target_module("#module8-section") == 8
    assert resolve_target_module("#kegg-section") is None


def test_resolve_fallback_hash_prefers_module_section() -> None:
    assert resolve_fallback_hash("#uc-7-4-card", 7) == "#module7-section"
    assert resolve_fallback_hash("#kegg-section", None) == "#kegg-section"
    assert resolve_fallback_hash("#unknown", None) == "#module1-section"

