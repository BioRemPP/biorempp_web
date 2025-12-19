"""
Unit tests for FrozensetStrategy.

Tests cover:
- Initialization and configuration
- Data validation
- Data processing (compound profile grouping, set cover minimization)
- Figure creation with subplots
- KO count calculation
- Filter application
- Helper methods
- Integration workflows
- Edge cases

Author: BioRemPP Test Suite
Date: 2025-12-08
"""

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import pytest
from unittest.mock import Mock, patch

from src.domain.plot_strategies.charts.frozenset_strategy import (
    FrozensetStrategy,
    DEFAULT_COLOR_SCALE,
    DEFAULT_MARKER_SIZE,
    DEFAULT_CHART_HEIGHT,
    DEFAULT_CHART_WIDTH,
    DEFAULT_TEMPLATE
)


# ============================================================================
# HELPER FUNCTIONS - Configuration and Sample Data
# ============================================================================

def get_minimal_config():
    """Get minimal configuration for FrozensetStrategy."""
    return {
        'metadata': {
            'use_case_id': 'UC-8.1',
            'module': 'module8'
        },
        'visualization': {
            'strategy': 'FrozensetStrategy',
            'plotly': {
                'sample_column': 'sample',
                'compound_column': 'compoundname',
                'compoundclass_column': 'compoundclass',
                'ko_column': 'ko'
            }
        }
    }


def get_full_config():
    """Get full configuration with all options."""
    return {
        'metadata': {
            'use_case_id': 'UC-8.1',
            'module': 'module8'
        },
        'data': {
            'required_columns': ['sample', 'compoundname', 'compoundclass', 'ko']
        },
        'visualization': {
            'strategy': 'FrozensetStrategy',
            'plotly': {
                'sample_column': 'sample',
                'compound_column': 'compoundname',
                'compoundclass_column': 'compoundclass',
                'ko_column': 'ko',
                'color_scale': 'Blues',
                'marker_size': 12,
                'chart': {
                    'title': {
                        'show': True,
                        'text': 'Test Frozenset Visualization',
                        'font_size': 18
                    },
                    'horizontal_spacing': 0.05,
                    'colorbar_title': 'KO<br>Count',
                    'xaxis_tickangle': -45,
                    'yaxis_tickangle': 0,
                    'xaxis_title': 'Sample',
                    'yaxis_title': 'Compound'
                },
                'layout': {
                    'height': 700,
                    'width': 1000,
                    'template': 'plotly_white',
                    'autosize': False,
                    'margin': {
                        'l': 200,
                        'r': 100,
                        't': 100,
                        'b': 100
                    }
                }
            }
        }
    }


def get_sample_data():
    """
    Get sample data for testing frozenset strategy.

    Creates data with:
    - 3 compound classes
    - 2 samples per class
    - Different compound profiles per sample
    """
    np.random.seed(42)

    data = []

    # Class 1: Hydrocarbons (2 samples, different compound profiles)
    # Sample S1: compounds A, B
    data.extend([
        {'sample': 'S1', 'compoundname': 'Benzene', 'compoundclass': 'Hydrocarbon', 'ko': 'K00001'},
        {'sample': 'S1', 'compoundname': 'Benzene', 'compoundclass': 'Hydrocarbon', 'ko': 'K00002'},
        {'sample': 'S1', 'compoundname': 'Toluene', 'compoundclass': 'Hydrocarbon', 'ko': 'K00003'},
    ])

    # Sample S2: compounds A, C
    data.extend([
        {'sample': 'S2', 'compoundname': 'Benzene', 'compoundclass': 'Hydrocarbon', 'ko': 'K00001'},
        {'sample': 'S2', 'compoundname': 'Xylene', 'compoundclass': 'Hydrocarbon', 'ko': 'K00004'},
        {'sample': 'S2', 'compoundname': 'Xylene', 'compoundclass': 'Hydrocarbon', 'ko': 'K00005'},
    ])

    # Class 2: Pesticides (2 samples, identical profiles)
    # Sample S3 and S4: both have compounds D, E
    data.extend([
        {'sample': 'S3', 'compoundname': 'Atrazine', 'compoundclass': 'Pesticide', 'ko': 'K00010'},
        {'sample': 'S3', 'compoundname': 'Glyphosate', 'compoundclass': 'Pesticide', 'ko': 'K00011'},
        {'sample': 'S4', 'compoundname': 'Atrazine', 'compoundclass': 'Pesticide', 'ko': 'K00010'},
        {'sample': 'S4', 'compoundname': 'Glyphosate', 'compoundclass': 'Pesticide', 'ko': 'K00012'},
    ])

    # Class 3: Heavy Metals (1 sample)
    data.extend([
        {'sample': 'S5', 'compoundname': 'Cadmium', 'compoundclass': 'Heavy Metal', 'ko': 'K00020'},
        {'sample': 'S5', 'compoundname': 'Lead', 'compoundclass': 'Heavy Metal', 'ko': 'K00021'},
    ])

    return pd.DataFrame(data)


def get_complex_data():
    """Get complex data with multiple groups requiring set cover."""
    data = []

    # Sample 1: compounds A, B, C
    for compound in ['Comp_A', 'Comp_B', 'Comp_C']:
        data.append({
            'sample': 'Sample_1',
            'compoundname': compound,
            'compoundclass': 'ClassX',
            'ko': f'K0000{hash(compound) % 10}'
        })

    # Sample 2: compounds A, B (subset of Sample 1)
    for compound in ['Comp_A', 'Comp_B']:
        data.append({
            'sample': 'Sample_2',
            'compoundname': compound,
            'compoundclass': 'ClassX',
            'ko': f'K0000{hash(compound) % 10}'
        })

    # Sample 3: compounds C, D (overlaps with Sample 1)
    for compound in ['Comp_C', 'Comp_D']:
        data.append({
            'sample': 'Sample_3',
            'compoundname': compound,
            'compoundclass': 'ClassX',
            'ko': f'K0000{hash(compound) % 10}'
        })

    # Sample 4: compound D only
    data.append({
        'sample': 'Sample_4',
        'compoundname': 'Comp_D',
        'compoundclass': 'ClassX',
        'ko': 'K00004'
    })

    return pd.DataFrame(data)


# ============================================================================
# TEST CLASS: Initialization
# ============================================================================

class TestFrozensetStrategyInitialization:
    """Test FrozensetStrategy initialization."""

    def test_initialization_minimal_config(self):
        """Test initialization with minimal configuration."""
        config = get_minimal_config()
        strategy = FrozensetStrategy(config)

        assert strategy is not None
        assert strategy.sample_column == 'sample'
        assert strategy.compound_column == 'compoundname'
        assert strategy.compoundclass_column == 'compoundclass'
        assert strategy.ko_column == 'ko'

    def test_initialization_full_config(self):
        """Test initialization with full configuration."""
        config = get_full_config()
        strategy = FrozensetStrategy(config)

        assert strategy.color_scale == 'Blues'
        assert strategy.marker_size == 12
        assert strategy.metadata.get('use_case_id') == 'UC-8.1'

    def test_initialization_uses_defaults(self):
        """Test that defaults are applied when not specified."""
        config = get_minimal_config()
        strategy = FrozensetStrategy(config)

        assert strategy.color_scale == DEFAULT_COLOR_SCALE
        assert strategy.marker_size == DEFAULT_MARKER_SIZE

    def test_initialization_custom_columns(self):
        """Test initialization with custom column names."""
        config = get_minimal_config()
        config['visualization']['plotly'].update({
            'sample_column': 'sample_id',
            'compound_column': 'chemical',
            'compoundclass_column': 'chemical_class',
            'ko_column': 'kegg_id'
        })

        strategy = FrozensetStrategy(config)

        assert strategy.sample_column == 'sample_id'
        assert strategy.compound_column == 'chemical'
        assert strategy.compoundclass_column == 'chemical_class'
        assert strategy.ko_column == 'kegg_id'

    def test_initialization_internal_state(self):
        """Test that internal state is properly initialized."""
        config = get_minimal_config()
        strategy = FrozensetStrategy(config)

        assert strategy._selected_compoundclass is None
        assert strategy._grouped_df is None
        assert strategy._minimized_groups == []
        assert strategy._ko_counts is None


# ============================================================================
# TEST CLASS: Data Validation
# ============================================================================

class TestDataValidation:
    """Test validate_data() method."""

    def test_validate_empty_dataframe_fails(self):
        """Test that empty DataFrame raises error."""
        config = get_minimal_config()
        strategy = FrozensetStrategy(config)

        df = pd.DataFrame()

        with pytest.raises(ValueError, match="Input DataFrame is empty"):
            strategy.validate_data(df)

    def test_validate_missing_sample_column(self):
        """Test that missing sample column raises error."""
        config = get_minimal_config()
        strategy = FrozensetStrategy(config)

        df = pd.DataFrame({
            'compoundname': ['Benzene'],
            'compoundclass': ['Hydrocarbon']
        })

        with pytest.raises(ValueError, match="Missing required columns"):
            strategy.validate_data(df)

    def test_validate_missing_compound_column(self):
        """Test that missing compound column raises error."""
        config = get_minimal_config()
        strategy = FrozensetStrategy(config)

        df = pd.DataFrame({
            'sample': ['S1'],
            'compoundclass': ['Hydrocarbon']
        })

        with pytest.raises(ValueError, match="Missing required columns"):
            strategy.validate_data(df)

    def test_validate_missing_compoundclass_column(self):
        """Test that missing compound class column raises error."""
        config = get_minimal_config()
        strategy = FrozensetStrategy(config)

        df = pd.DataFrame({
            'sample': ['S1'],
            'compoundname': ['Benzene']
        })

        with pytest.raises(ValueError, match="Missing required columns"):
            strategy.validate_data(df)

    def test_validate_missing_ko_column_logs_warning(self, caplog):
        """Test that missing KO column logs warning (not required)."""
        config = get_minimal_config()
        strategy = FrozensetStrategy(config)

        df = pd.DataFrame({
            'sample': ['S1'],
            'compoundname': ['Benzene'],
            'compoundclass': ['Hydrocarbon']
        })

        # Should not raise, just log warning
        strategy.validate_data(df)

        assert "KO column" in caplog.text
        assert "not found" in caplog.text

    def test_validate_success(self):
        """Test successful validation."""
        config = get_minimal_config()
        strategy = FrozensetStrategy(config)

        df = get_sample_data()

        # Should not raise
        strategy.validate_data(df)


# ============================================================================
# TEST CLASS: Data Processing
# ============================================================================

class TestDataProcessing:
    """Test process_data() method."""

    def test_process_data_removes_nulls(self):
        """Test that null values are removed."""
        config = get_minimal_config()
        strategy = FrozensetStrategy(config)

        df = pd.DataFrame({
            'sample': ['S1', 'S2', None, 'S4'],
            'compoundname': ['Benzene', None, 'Toluene', 'Xylene'],
            'compoundclass': ['Hydrocarbon', 'Hydrocarbon', 'Hydrocarbon', None],
            'ko': ['K00001', 'K00002', 'K00003', 'K00004']
        })

        result = strategy.process_data(df)

        # Only S1 has all required columns
        assert len(result) >= 1
        assert not result['sample'].isna().any()
        assert not result['compoundname'].isna().any()
        assert not result['compoundclass'].isna().any()

    def test_process_data_selects_first_class_if_none_selected(self):
        """Test that first compound class is selected if none provided."""
        config = get_minimal_config()
        strategy = FrozensetStrategy(config)

        df = get_sample_data()

        # No class selected initially
        assert strategy._selected_compoundclass is None

        result = strategy.process_data(df)

        # Should auto-select first class
        assert strategy._selected_compoundclass is not None
        assert strategy._selected_compoundclass in df['compoundclass'].unique()

    def test_process_data_filters_by_selected_class(self):
        """Test that data is filtered to selected compound class."""
        config = get_minimal_config()
        strategy = FrozensetStrategy(config)

        df = get_sample_data()

        # Pre-select class
        strategy._selected_compoundclass = 'Pesticide'

        result = strategy.process_data(df)

        # All results should be Pesticide class
        assert (result['compoundclass'] == 'Pesticide').all()

    def test_process_data_groups_by_compound_profile(self):
        """Test that samples are grouped by compound profile."""
        config = get_minimal_config()
        strategy = FrozensetStrategy(config)

        df = get_sample_data()
        strategy._selected_compoundclass = 'Pesticide'

        result = strategy.process_data(df)

        # Should have _group column
        assert '_group' in result.columns
        assert result['_group'].notna().all()

    def test_process_data_calculates_ko_counts(self):
        """Test that unique KO counts are calculated."""
        config = get_minimal_config()
        strategy = FrozensetStrategy(config)

        df = get_sample_data()

        result = strategy.process_data(df)

        # Should have _unique_ko_count column
        assert '_unique_ko_count' in result.columns
        assert result['_unique_ko_count'].notna().all()
        assert (result['_unique_ko_count'] >= 0).all()

    def test_process_data_empty_after_filtering_fails(self):
        """Test that empty data after filtering raises error."""
        config = get_minimal_config()
        strategy = FrozensetStrategy(config)

        df = get_sample_data()

        # Select non-existent class
        strategy._selected_compoundclass = 'NonExistentClass'

        with pytest.raises(ValueError, match="No data for compound class"):
            strategy.process_data(df)

    def test_process_data_minimizes_groups(self):
        """Test that groups are minimized using set cover."""
        config = get_minimal_config()
        strategy = FrozensetStrategy(config)

        df = get_complex_data()

        result = strategy.process_data(df)

        # Should have minimized groups
        assert len(strategy._minimized_groups) > 0
        assert len(strategy._minimized_groups) <= result['_group'].nunique()


# ============================================================================
# TEST CLASS: Compound Profile Grouping
# ============================================================================

class TestCompoundProfileGrouping:
    """Test _group_by_compound_profile() method."""

    def test_group_by_compound_profile_creates_groups(self):
        """Test that groups are created based on compound profiles."""
        config = get_minimal_config()
        strategy = FrozensetStrategy(config)

        df = pd.DataFrame({
            'sample': ['S1', 'S1', 'S2', 'S2', 'S3'],
            'compoundname': ['A', 'B', 'A', 'B', 'C'],
            'compoundclass': ['X', 'X', 'X', 'X', 'X']
        })

        result = strategy._group_by_compound_profile(df)

        # S1 and S2 have same profile (A, B), S3 has different (C)
        assert '_group' in result.columns
        assert result['_group'].nunique() == 2

    def test_group_by_compound_profile_identical_profiles_same_group(self):
        """Test that samples with identical profiles get same group."""
        config = get_minimal_config()
        strategy = FrozensetStrategy(config)

        df = pd.DataFrame({
            'sample': ['S1', 'S1', 'S2', 'S2'],
            'compoundname': ['A', 'B', 'A', 'B'],
            'compoundclass': ['X', 'X', 'X', 'X']
        })

        result = strategy._group_by_compound_profile(df)

        # Both samples should be in same group
        groups = result.groupby('sample')['_group'].first()
        assert groups['S1'] == groups['S2']

    def test_group_by_compound_profile_different_profiles_different_groups(self):
        """Test that samples with different profiles get different groups."""
        config = get_minimal_config()
        strategy = FrozensetStrategy(config)

        df = pd.DataFrame({
            'sample': ['S1', 'S2'],
            'compoundname': ['A', 'B'],
            'compoundclass': ['X', 'X']
        })

        result = strategy._group_by_compound_profile(df)

        # Different profiles should be in different groups
        groups = result.groupby('sample')['_group'].first()
        assert groups['S1'] != groups['S2']

    def test_group_by_compound_profile_empty_dataframe(self):
        """Test grouping with empty DataFrame."""
        config = get_minimal_config()
        strategy = FrozensetStrategy(config)

        df = pd.DataFrame({
            'sample': [],
            'compoundname': [],
            'compoundclass': []
        })

        result = strategy._group_by_compound_profile(df)

        assert len(result) == 0


# ============================================================================
# TEST CLASS: Set Cover Minimization
# ============================================================================

class TestSetCoverMinimization:
    """Test _minimize_groups() method."""

    def test_minimize_groups_selects_minimal_set(self):
        """Test that minimal set of groups is selected."""
        config = get_minimal_config()
        strategy = FrozensetStrategy(config)

        # Create groups where one group covers all compounds
        df = pd.DataFrame({
            '_group': ['Group 1', 'Group 1', 'Group 1', 'Group 2', 'Group 2'],
            'compoundname': ['A', 'B', 'C', 'A', 'B']
        })

        result = strategy._minimize_groups(df)

        # Should select only Group 1 (covers all compounds)
        assert len(result) == 1
        assert 'Group 1' in result

    def test_minimize_groups_multiple_groups_needed(self):
        """Test when multiple groups are needed to cover all compounds."""
        config = get_minimal_config()
        strategy = FrozensetStrategy(config)

        df = pd.DataFrame({
            '_group': ['Group 1', 'Group 1', 'Group 2', 'Group 2'],
            'compoundname': ['A', 'B', 'C', 'D']
        })

        result = strategy._minimize_groups(df)

        # Need both groups to cover all compounds
        assert len(result) == 2

    def test_minimize_groups_empty_dataframe(self):
        """Test minimization with empty DataFrame."""
        config = get_minimal_config()
        strategy = FrozensetStrategy(config)

        df = pd.DataFrame({
            '_group': [],
            'compoundname': []
        })

        result = strategy._minimize_groups(df)

        assert len(result) == 0

    def test_minimize_groups_greedy_selection(self):
        """Test that greedy algorithm selects largest coverage first."""
        config = get_minimal_config()
        strategy = FrozensetStrategy(config)

        # Group 1 covers 3 compounds, Group 2 covers 2, Group 3 covers 1
        df = pd.DataFrame({
            '_group': ['G1', 'G1', 'G1', 'G2', 'G2', 'G3'],
            'compoundname': ['A', 'B', 'C', 'C', 'D', 'E']
        })

        result = strategy._minimize_groups(df)

        # G1 should be selected first (largest coverage)
        assert 'G1' in result


# ============================================================================
# TEST CLASS: KO Count Calculation
# ============================================================================

class TestKOCountCalculation:
    """Test _calculate_ko_counts() method."""

    def test_calculate_ko_counts_returns_series(self):
        """Test that KO counts returns a Series."""
        config = get_minimal_config()
        strategy = FrozensetStrategy(config)

        df_full = get_sample_data()
        df_filtered = df_full[df_full['compoundclass'] == 'Hydrocarbon']

        result = strategy._calculate_ko_counts(df_full, df_filtered)

        assert result is not None
        assert isinstance(result, pd.Series)
        assert result.name == '_unique_ko_count'

    def test_calculate_ko_counts_correct_values(self):
        """Test that KO counts are correctly calculated."""
        config = get_minimal_config()
        strategy = FrozensetStrategy(config)

        df = pd.DataFrame({
            'compoundname': ['Benzene', 'Benzene', 'Toluene', 'Toluene', 'Toluene'],
            'compoundclass': ['Hydrocarbon'] * 5,
            'ko': ['K00001', 'K00002', 'K00003', 'K00003', 'K00004']
        })

        result = strategy._calculate_ko_counts(df, df)

        # Benzene: 2 unique KOs, Toluene: 2 unique KOs
        assert result['Benzene'] == 2
        assert result['Toluene'] == 2

    def test_calculate_ko_counts_missing_ko_column(self):
        """Test KO counts when KO column is missing."""
        config = get_minimal_config()
        strategy = FrozensetStrategy(config)

        df = pd.DataFrame({
            'compoundname': ['Benzene'],
            'compoundclass': ['Hydrocarbon']
        })

        result = strategy._calculate_ko_counts(df, df)

        assert result is None

    def test_calculate_ko_counts_with_nulls(self):
        """Test KO counts with null KO values."""
        config = get_minimal_config()
        strategy = FrozensetStrategy(config)

        df = pd.DataFrame({
            'compoundname': ['Benzene', 'Benzene', 'Toluene'],
            'compoundclass': ['Hydrocarbon'] * 3,
            'ko': ['K00001', None, 'K00002']
        })

        result = strategy._calculate_ko_counts(df, df)

        # Should only count non-null KOs
        assert result['Benzene'] == 1
        assert result['Toluene'] == 1


# ============================================================================
# TEST CLASS: Figure Creation
# ============================================================================

class TestFigureCreation:
    """Test create_figure() method."""

    def test_create_figure_returns_figure(self):
        """Test that create_figure returns a Plotly Figure."""
        config = get_minimal_config()
        strategy = FrozensetStrategy(config)

        df = get_sample_data()
        processed = strategy.process_data(df)

        fig = strategy.create_figure(processed)

        assert isinstance(fig, go.Figure)

    def test_create_figure_creates_subplots(self):
        """Test that subplots are created for each group."""
        config = get_minimal_config()
        strategy = FrozensetStrategy(config)

        df = get_sample_data()
        processed = strategy.process_data(df)

        fig = strategy.create_figure(processed)

        # Should have traces for minimized groups
        n_groups = len(strategy._minimized_groups)
        assert len(fig.data) == n_groups

    def test_create_figure_applies_color_scale(self):
        """Test that color scale is applied to markers."""
        config = get_full_config()
        strategy = FrozensetStrategy(config)

        df = get_sample_data()
        processed = strategy.process_data(df)

        fig = strategy.create_figure(processed)

        # Colorscale is expanded to RGB tuples, just check it exists
        assert fig.data[0].marker.colorscale is not None
        assert len(fig.data[0].marker.colorscale) > 0

    def test_create_figure_sets_marker_size(self):
        """Test that marker size is applied."""
        config = get_full_config()
        strategy = FrozensetStrategy(config)

        df = get_sample_data()
        processed = strategy.process_data(df)

        fig = strategy.create_figure(processed)

        assert fig.data[0].marker.size == 12

    def test_create_figure_shows_colorbar_on_first_only(self):
        """Test that colorbar is shown only on first subplot."""
        config = get_minimal_config()
        strategy = FrozensetStrategy(config)

        df = get_complex_data()
        processed = strategy.process_data(df)

        fig = strategy.create_figure(processed)

        if len(fig.data) > 1:
            # First trace should have colorbar
            assert fig.data[0].marker.showscale is True
            # Others should not
            for trace in fig.data[1:]:
                assert trace.marker.showscale is False

    def test_create_figure_applies_title(self):
        """Test that title is applied to figure."""
        config = get_full_config()
        strategy = FrozensetStrategy(config)

        df = get_sample_data()
        processed = strategy.process_data(df)

        fig = strategy.create_figure(processed)

        assert fig.layout.title.text == 'Test Frozenset Visualization'

    def test_create_figure_title_hidden(self):
        """Test that title can be hidden."""
        config = get_full_config()
        config['visualization']['plotly']['chart']['title']['show'] = False
        strategy = FrozensetStrategy(config)

        df = get_sample_data()
        processed = strategy.process_data(df)

        fig = strategy.create_figure(processed)

        assert fig.layout.title.text == '' or fig.layout.title.text is None

    def test_create_figure_applies_layout_config(self):
        """Test that layout configuration is applied."""
        config = get_full_config()
        strategy = FrozensetStrategy(config)

        df = get_sample_data()
        processed = strategy.process_data(df)

        fig = strategy.create_figure(processed)

        assert fig.layout.height == 700
        assert fig.layout.width == 1000

    def test_create_figure_with_autosize(self):
        """Test figure with autosize enabled."""
        config = get_full_config()
        config['visualization']['plotly']['layout']['autosize'] = True
        strategy = FrozensetStrategy(config)

        df = get_sample_data()
        processed = strategy.process_data(df)

        fig = strategy.create_figure(processed)

        assert fig.layout.autosize is True

    def test_create_figure_empty_groups_fails(self):
        """Test that empty groups raises error."""
        config = get_minimal_config()
        strategy = FrozensetStrategy(config)

        # Create processed df with no groups
        df = pd.DataFrame({
            'sample': [],
            'compoundname': [],
            '_group': [],
            '_unique_ko_count': []
        })

        with pytest.raises(ValueError, match="No groups to visualize"):
            strategy.create_figure(df)

    def test_create_figure_colorbar_range(self):
        """Test that colorbar range is set correctly."""
        config = get_minimal_config()
        strategy = FrozensetStrategy(config)

        df = get_sample_data()
        processed = strategy.process_data(df)

        fig = strategy.create_figure(processed)

        # Check color range
        cmin = fig.data[0].marker.cmin
        cmax = fig.data[0].marker.cmax

        assert cmin is not None
        assert cmax is not None
        assert cmax >= cmin


# ============================================================================
# TEST CLASS: Filter Application
# ============================================================================

class TestFilterApplication:
    """Test apply_filters() method."""

    def test_apply_filters_sets_compound_class(self):
        """Test that filters set the compound class."""
        config = get_minimal_config()
        strategy = FrozensetStrategy(config)

        df = get_sample_data()

        filters = {'compoundclass': 'Pesticide'}
        strategy.apply_filters(df, filters)

        assert strategy._selected_compoundclass == 'Pesticide'

    def test_apply_filters_no_filters(self):
        """Test apply_filters with no filters provided."""
        config = get_minimal_config()
        strategy = FrozensetStrategy(config)

        df = get_sample_data()

        result = strategy.apply_filters(df, None)

        # Should return same data
        assert len(result) == len(df)

    def test_apply_filters_other_filters_ignored(self):
        """Test that other filters are passed to parent."""
        config = get_minimal_config()
        strategy = FrozensetStrategy(config)

        df = get_sample_data()

        filters = {'compoundclass': 'Pesticide', 'other_filter': 'value'}
        result = strategy.apply_filters(df, filters)

        # Should set compound class
        assert strategy._selected_compoundclass == 'Pesticide'


# ============================================================================
# TEST CLASS: Helper Methods
# ============================================================================

class TestHelperMethods:
    """Test helper methods."""

    def test_get_available_compound_classes(self):
        """Test getting available compound classes."""
        config = get_minimal_config()
        strategy = FrozensetStrategy(config)

        df = get_sample_data()

        classes = strategy.get_available_compound_classes(df)

        assert isinstance(classes, list)
        assert 'Hydrocarbon' in classes
        assert 'Pesticide' in classes
        assert 'Heavy Metal' in classes
        assert len(classes) == 3

    def test_get_available_compound_classes_sorted(self):
        """Test that compound classes are sorted."""
        config = get_minimal_config()
        strategy = FrozensetStrategy(config)

        df = get_sample_data()

        classes = strategy.get_available_compound_classes(df)

        assert classes == sorted(classes)

    def test_get_available_compound_classes_missing_column(self):
        """Test getting classes when column is missing."""
        config = get_minimal_config()
        strategy = FrozensetStrategy(config)

        df = pd.DataFrame({
            'sample': ['S1'],
            'compoundname': ['Benzene']
        })

        classes = strategy.get_available_compound_classes(df)

        assert classes == []

    def test_get_group_statistics(self):
        """Test getting group statistics."""
        config = get_minimal_config()
        strategy = FrozensetStrategy(config)

        df = get_sample_data()
        processed = strategy.process_data(df)

        stats = strategy.get_group_statistics(processed)

        assert 'compound_class' in stats
        assert 'total_groups' in stats
        assert 'groups' in stats
        assert 'total_samples' in stats
        assert 'total_compounds' in stats
        assert 'ko_range' in stats

    def test_get_group_statistics_ko_range(self):
        """Test that KO range is calculated correctly."""
        config = get_minimal_config()
        strategy = FrozensetStrategy(config)

        df = get_sample_data()
        processed = strategy.process_data(df)

        stats = strategy.get_group_statistics(processed)

        assert 'min' in stats['ko_range']
        assert 'max' in stats['ko_range']
        assert stats['ko_range']['min'] <= stats['ko_range']['max']


# ============================================================================
# TEST CLASS: Integration
# ============================================================================

class TestIntegration:
    """Test complete workflow integration."""

    def test_generate_plot_complete_workflow(self):
        """Test complete workflow from data to figure."""
        config = get_minimal_config()
        strategy = FrozensetStrategy(config)

        df = get_sample_data()

        # Set compound class
        filters = {'compoundclass': 'Hydrocarbon'}
        strategy.apply_filters(df, filters)

        # Generate plot
        fig = strategy.generate_plot(df)

        assert isinstance(fig, go.Figure)
        assert len(fig.data) > 0

    def test_workflow_with_validation(self):
        """Test that validation is called in workflow."""
        config = get_minimal_config()
        strategy = FrozensetStrategy(config)

        df = pd.DataFrame()

        with pytest.raises(ValueError, match="Input DataFrame is empty"):
            strategy.generate_plot(df)

    def test_workflow_minimal_config(self):
        """Test workflow with minimal configuration."""
        config = get_minimal_config()
        strategy = FrozensetStrategy(config)

        df = get_sample_data()

        # Should work with defaults
        fig = strategy.generate_plot(df)

        assert isinstance(fig, go.Figure)


# ============================================================================
# TEST CLASS: Edge Cases
# ============================================================================

class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_single_sample(self):
        """Test with single sample."""
        config = get_minimal_config()
        strategy = FrozensetStrategy(config)

        df = pd.DataFrame({
            'sample': ['S1', 'S1'],
            'compoundname': ['Benzene', 'Toluene'],
            'compoundclass': ['Hydrocarbon', 'Hydrocarbon'],
            'ko': ['K00001', 'K00002']
        })

        fig = strategy.generate_plot(df)

        assert isinstance(fig, go.Figure)
        assert len(fig.data) == 1

    def test_single_compound(self):
        """Test with single compound."""
        config = get_minimal_config()
        strategy = FrozensetStrategy(config)

        df = pd.DataFrame({
            'sample': ['S1', 'S2'],
            'compoundname': ['Benzene', 'Benzene'],
            'compoundclass': ['Hydrocarbon', 'Hydrocarbon'],
            'ko': ['K00001', 'K00001']
        })

        fig = strategy.generate_plot(df)

        assert isinstance(fig, go.Figure)

    def test_many_groups(self):
        """Test with many groups."""
        config = get_minimal_config()
        strategy = FrozensetStrategy(config)

        # Create data with 10 samples, each with unique compound profile
        data = []
        for i in range(10):
            data.append({
                'sample': f'S{i}',
                'compoundname': f'Compound_{i}',
                'compoundclass': 'ClassX',
                'ko': f'K0000{i}'
            })

        df = pd.DataFrame(data)

        fig = strategy.generate_plot(df)

        assert isinstance(fig, go.Figure)
        assert len(fig.data) > 0

    def test_many_compounds_per_sample(self):
        """Test with many compounds per sample."""
        config = get_minimal_config()
        strategy = FrozensetStrategy(config)

        data = []
        for i in range(20):
            data.append({
                'sample': 'S1',
                'compoundname': f'Compound_{i}',
                'compoundclass': 'ClassX',
                'ko': f'K{str(i).zfill(5)}'
            })

        df = pd.DataFrame(data)

        fig = strategy.generate_plot(df)

        assert isinstance(fig, go.Figure)

    def test_no_ko_data(self):
        """Test when KO column has all nulls."""
        config = get_minimal_config()
        strategy = FrozensetStrategy(config)

        df = pd.DataFrame({
            'sample': ['S1', 'S2'],
            'compoundname': ['Benzene', 'Toluene'],
            'compoundclass': ['Hydrocarbon', 'Hydrocarbon'],
            'ko': [None, None]
        })

        # Should still work with default KO counts
        fig = strategy.generate_plot(df)

        assert isinstance(fig, go.Figure)

    def test_duplicate_compound_sample_pairs(self):
        """Test with duplicate compound-sample pairs."""
        config = get_minimal_config()
        strategy = FrozensetStrategy(config)

        df = pd.DataFrame({
            'sample': ['S1', 'S1', 'S1'],
            'compoundname': ['Benzene', 'Benzene', 'Toluene'],
            'compoundclass': ['Hydrocarbon'] * 3,
            'ko': ['K00001', 'K00002', 'K00003']
        })

        # Should handle duplicates in grouping
        fig = strategy.generate_plot(df)

        assert isinstance(fig, go.Figure)

    def test_all_samples_identical_profiles(self):
        """Test when all samples have identical compound profiles."""
        config = get_minimal_config()
        strategy = FrozensetStrategy(config)

        df = pd.DataFrame({
            'sample': ['S1', 'S1', 'S2', 'S2', 'S3', 'S3'],
            'compoundname': ['A', 'B', 'A', 'B', 'A', 'B'],
            'compoundclass': ['X'] * 6,
            'ko': ['K00001', 'K00002'] * 3
        })

        result = strategy.process_data(df)

        # Should create single group
        assert result['_group'].nunique() == 1

    def test_special_characters_in_names(self):
        """Test with special characters in compound/sample names."""
        config = get_minimal_config()
        strategy = FrozensetStrategy(config)

        df = pd.DataFrame({
            'sample': ['Sample-1', 'Sample_2', 'Sample#3'],
            'compoundname': ['Comp (A)', 'Comp [B]', 'Comp {C}'],
            'compoundclass': ['Class-X'] * 3,
            'ko': ['K00001', 'K00002', 'K00003']
        })

        # Should handle special characters
        fig = strategy.generate_plot(df)

        assert isinstance(fig, go.Figure)

    def test_very_long_names(self):
        """Test with very long compound/sample names."""
        config = get_minimal_config()
        strategy = FrozensetStrategy(config)

        long_name = 'A' * 100

        df = pd.DataFrame({
            'sample': [long_name],
            'compoundname': [long_name],
            'compoundclass': ['ClassX'],
            'ko': ['K00001']
        })

        fig = strategy.generate_plot(df)

        assert isinstance(fig, go.Figure)

    def test_zero_ko_counts(self):
        """Test when all compounds have zero KO counts."""
        config = get_minimal_config()
        strategy = FrozensetStrategy(config)

        df = pd.DataFrame({
            'sample': ['S1', 'S2'],
            'compoundname': ['Benzene', 'Toluene'],
            'compoundclass': ['Hydrocarbon', 'Hydrocarbon']
        })

        # Missing KO column, should default to 0 or 1
        processed = strategy.process_data(df)

        # Should handle zero/default KO counts
        assert '_unique_ko_count' in processed.columns
