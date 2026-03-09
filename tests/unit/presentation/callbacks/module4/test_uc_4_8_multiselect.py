"""Unit tests for UC-4.8 multiselect filtering helpers."""

import pandas as pd

from src.presentation.callbacks.module4 import uc_4_8_callbacks as callbacks


def _build_df() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {"sample": "S1", "genesymbol": "G1"},
            {"sample": "S1", "genesymbol": "G2"},
            {"sample": "S2", "genesymbol": "G1"},
            {"sample": "S3", "genesymbol": "G3"},
        ]
    )


def test_normalize_selection_supports_none_string_and_list():
    assert callbacks._normalize_selection(None) == []
    assert callbacks._normalize_selection("S1") == ["S1"]
    assert callbacks._normalize_selection(["S1", "", " S2 ", "S1", 5]) == ["S1", "S2"]


def test_apply_dual_filter_only_left_only_right_both_and_none():
    df = _build_df()

    only_sample = callbacks._apply_dual_filter(df, "sample", ["S1"], "genesymbol", [])
    assert len(only_sample) == 2

    only_gene = callbacks._apply_dual_filter(df, "sample", [], "genesymbol", ["G1"])
    assert len(only_gene) == 2

    both = callbacks._apply_dual_filter(df, "sample", ["S1", "S2"], "genesymbol", ["G1"])
    assert len(both) == 2
    assert set(both["sample"].tolist()) == {"S1", "S2"}
    assert set(both["genesymbol"].tolist()) == {"G1"}

    no_filter = callbacks._apply_dual_filter(df, "sample", [], "genesymbol", [])
    assert len(no_filter) == 4


def test_apply_dual_filter_with_multi_values_is_incremental():
    df = _build_df()
    filtered = callbacks._apply_dual_filter(
        df,
        "sample",
        ["S1", "S2"],
        "genesymbol",
        [],
    )
    assert len(filtered) == 3
    assert set(filtered["sample"].tolist()) == {"S1", "S2"}


def test_apply_dual_filter_invalid_selection_returns_empty_without_error():
    df = _build_df()
    filtered = callbacks._apply_dual_filter(
        df,
        "sample",
        ["UNKNOWN"],
        "genesymbol",
        ["G1"],
    )
    assert filtered.empty
