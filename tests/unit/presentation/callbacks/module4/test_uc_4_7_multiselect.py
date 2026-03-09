"""Unit tests for UC-4.7 multiselect filtering helpers."""

import pandas as pd

from src.presentation.callbacks.module4 import uc_4_7_callbacks as callbacks


def _build_df() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {"compoundname": "C1", "genesymbol": "G1"},
            {"compoundname": "C1", "genesymbol": "G2"},
            {"compoundname": "C2", "genesymbol": "G1"},
            {"compoundname": "C3", "genesymbol": "G3"},
        ]
    )


def test_normalize_selection_supports_none_string_and_list():
    assert callbacks._normalize_selection(None) == []
    assert callbacks._normalize_selection("C1") == ["C1"]
    assert callbacks._normalize_selection(["C1", " ", "C1", " C2 ", 1]) == ["C1", "C2"]


def test_apply_dual_filter_only_left_only_right_both_and_none():
    df = _build_df()

    only_compound = callbacks._apply_dual_filter(df, "compoundname", ["C1"], "genesymbol", [])
    assert len(only_compound) == 2

    only_gene = callbacks._apply_dual_filter(df, "compoundname", [], "genesymbol", ["G1"])
    assert len(only_gene) == 2

    both = callbacks._apply_dual_filter(df, "compoundname", ["C1", "C2"], "genesymbol", ["G1"])
    assert len(both) == 2
    assert set(both["compoundname"].tolist()) == {"C1", "C2"}
    assert set(both["genesymbol"].tolist()) == {"G1"}

    no_filter = callbacks._apply_dual_filter(df, "compoundname", [], "genesymbol", [])
    assert len(no_filter) == 4


def test_apply_dual_filter_with_multi_values_is_incremental():
    df = _build_df()
    filtered = callbacks._apply_dual_filter(
        df,
        "compoundname",
        ["C1", "C2"],
        "genesymbol",
        [],
    )
    assert len(filtered) == 3
    assert set(filtered["compoundname"].tolist()) == {"C1", "C2"}


def test_apply_dual_filter_invalid_selection_returns_empty_without_error():
    df = _build_df()
    filtered = callbacks._apply_dual_filter(
        df,
        "compoundname",
        ["UNKNOWN"],
        "genesymbol",
        ["G1"],
    )
    assert filtered.empty
