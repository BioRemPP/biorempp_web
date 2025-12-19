"""
Unit tests for HeatmapStrategy.

Tests cover:
- Initialization and configuration
- Data validation
- Data processing with aggregations (nunique, count, sum)
- Matrix creation and pivoting
- Sorting by totals
- Figure creation with heatmaps
- Text display logic
- Integration workflows
- Edge cases

Author: BioRemPP Test Suite
Date: 2025-12-08
"""

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import pytest

from src.domain.plot_strategies.charts.heatmap_strategy import (
    HeatmapStrategy
)


# ============================================================================
# HELPER FUNCTIONS - Configuration and Sample Data
# ============================================================================

def get_nunique_config():
    """Get configuration for nunique aggregation (default)."""
    return {
        'metadata': {
            'use_case_id': 'UC-1.6',
            'module': 'module1'
        },
        'visualization': {
            'strategy': 'HeatmapStrategy',
            'plotly': {
                'row_column': 'referenceAG',
                'col_column': 'sample',
                'value_column': 'ko',
                'aggregation': 'nunique',
                'chart': {
                    'title': {
                        'text': 'Sample-Agency Functional Potential',
                        'show': True
                    },
                    'xaxis': {'title': 'Sample'},
                    'yaxis': {'title': 'Reference Agency'},
                    'color_label': 'Unique KO Count',
                    'color_continuous_scale': 'Greens',
                    'text_auto': True
                },
                'layout': {
                    'height': 600,
                    'width': 1000,
                    'template': 'simple_white'
                }
            }
        }
    }


def get_count_config():
    """Get configuration for count aggregation."""
    return {
        'metadata': {'use_case_id': 'UC-TEST'},
        'visualization': {
            'strategy': 'HeatmapStrategy',
            'plotly': {
                'row_column': 'category',
                'col_column': 'item',
                'value_column': 'value',
                'aggregation': 'count'
            }
        }
    }


def get_sum_config():
    """Get configuration for sum aggregation."""
    return {
        'metadata': {'use_case_id': 'UC-TEST'},
        'visualization': {
            'strategy': 'HeatmapStrategy',
            'plotly': {
                'row_column': 'category',
                'col_column': 'item',
                'value_column': 'amount',
                'aggregation': 'sum'
            }
        }
    }


def get_minimal_config():
    """Get minimal configuration with defaults."""
    return {
        'metadata': {'use_case_id': 'UC-TEST'},
        'visualization': {
            'strategy': 'HeatmapStrategy',
            'plotly': {}
        }
    }


def get_sample_data():
    """
    Get sample data for heatmap strategy.

    Creates data with:
    - 3 reference agencies
    - 3 samples
    - Various KO distributions
    """
    np.random.seed(42)

    data = []

    # EPA: 5 unique KOs across samples
    data.extend([
        {'referenceAG': 'EPA', 'sample': 'Sample1', 'ko': 'K00001'},
        {'referenceAG': 'EPA', 'sample': 'Sample1', 'ko': 'K00002'},
        {'referenceAG': 'EPA', 'sample': 'Sample2', 'ko': 'K00001'},
        {'referenceAG': 'EPA', 'sample': 'Sample2', 'ko': 'K00003'},
        {'referenceAG': 'EPA', 'sample': 'Sample3', 'ko': 'K00001'},
        {'referenceAG': 'EPA', 'sample': 'Sample3', 'ko': 'K00004'},
        {'referenceAG': 'EPA', 'sample': 'Sample3', 'ko': 'K00005'},
    ])

    # WHO: 4 unique KOs across samples
    data.extend([
        {'referenceAG': 'WHO', 'sample': 'Sample1', 'ko': 'K00010'},
        {'referenceAG': 'WHO', 'sample': 'Sample2', 'ko': 'K00010'},
        {'referenceAG': 'WHO', 'sample': 'Sample2', 'ko': 'K00011'},
        {'referenceAG': 'WHO', 'sample': 'Sample3', 'ko': 'K00012'},
        {'referenceAG': 'WHO', 'sample': 'Sample3', 'ko': 'K00013'},
    ])

    # ATSDR: 2 unique KOs across samples
    data.extend([
        {'referenceAG': 'ATSDR', 'sample': 'Sample1', 'ko': 'K00020'},
        {'referenceAG': 'ATSDR', 'sample': 'Sample3', 'ko': 'K00021'},
    ])

    return pd.DataFrame(data)


def get_numeric_data():
    """Get sample data with numeric values for sum aggregation."""
    return pd.DataFrame({
        'category': ['A', 'A', 'B', 'B', 'C', 'C'],
        'item': ['X', 'Y', 'X', 'Y', 'X', 'Y'],
        'amount': [10, 20, 30, 40, 50, 60]
    })


# ============================================================================
# TEST CLASS: Initialization
# ============================================================================

class TestHeatmapStrategyInitialization:
    """Test HeatmapStrategy initialization."""

    def test_initialization_nunique_mode(self):
        """Test initialization with nunique aggregation."""
        config = get_nunique_config()
        strategy = HeatmapStrategy(config)

        assert strategy is not None
        assert strategy.aggregation == 'nunique'
        assert strategy.row_column == 'referenceAG'
        assert strategy.col_column == 'sample'
        assert strategy.value_column == 'ko'

    def test_initialization_count_mode(self):
        """Test initialization with count aggregation."""
        config = get_count_config()
        strategy = HeatmapStrategy(config)

        assert strategy.aggregation == 'count'
        assert strategy.row_column == 'category'
        assert strategy.col_column == 'item'
        assert strategy.value_column == 'value'

    def test_initialization_sum_mode(self):
        """Test initialization with sum aggregation."""
        config = get_sum_config()
        strategy = HeatmapStrategy(config)

        assert strategy.aggregation == 'sum'
        assert strategy.value_column == 'amount'

    def test_initialization_uses_defaults(self):
        """Test that defaults are applied when not specified."""
        config = get_minimal_config()
        strategy = HeatmapStrategy(config)

        # Should default to nunique
        assert strategy.aggregation == 'nunique'
        assert strategy.row_column == 'referenceAG'
        assert strategy.col_column == 'sample'
        assert strategy.value_column == 'ko'

    def test_initialization_custom_columns(self):
        """Test initialization with custom column names."""
        config = {
            'metadata': {},
            'visualization': {
                'strategy': 'HeatmapStrategy',
                'plotly': {
                    'row_column': 'CustomRow',
                    'col_column': 'CustomCol',
                    'value_column': 'CustomValue'
                }
            }
        }

        strategy = HeatmapStrategy(config)

        assert strategy.row_column == 'CustomRow'
        assert strategy.col_column == 'CustomCol'
        assert strategy.value_column == 'CustomValue'


# ============================================================================
# TEST CLASS: Data Validation
# ============================================================================

class TestDataValidation:
    """Test validate_data() method."""

    def test_validate_empty_dataframe_fails(self):
        """Test that empty DataFrame raises error."""
        config = get_nunique_config()
        strategy = HeatmapStrategy(config)

        df = pd.DataFrame()

        with pytest.raises(ValueError, match="Input DataFrame is empty"):
            strategy.validate_data(df)

    def test_validate_missing_row_column(self):
        """Test that missing row column raises error."""
        config = get_nunique_config()
        strategy = HeatmapStrategy(config)

        df = pd.DataFrame({
            'sample': ['S1'],
            'ko': ['K00001']
        })

        with pytest.raises(ValueError, match="Missing required columns"):
            strategy.validate_data(df)

    def test_validate_missing_col_column(self):
        """Test that missing column column raises error."""
        config = get_nunique_config()
        strategy = HeatmapStrategy(config)

        df = pd.DataFrame({
            'referenceAG': ['EPA'],
            'ko': ['K00001']
        })

        with pytest.raises(ValueError, match="Missing required columns"):
            strategy.validate_data(df)

    def test_validate_missing_value_column(self):
        """Test that missing value column raises error."""
        config = get_nunique_config()
        strategy = HeatmapStrategy(config)

        df = pd.DataFrame({
            'referenceAG': ['EPA'],
            'sample': ['S1']
        })

        with pytest.raises(ValueError, match="Missing required columns"):
            strategy.validate_data(df)

    def test_validate_all_nulls_fails(self):
        """Test that all null values raises error."""
        config = get_nunique_config()
        strategy = HeatmapStrategy(config)

        df = pd.DataFrame({
            'referenceAG': [None, None],
            'sample': [None, None],
            'ko': [None, None]
        })

        with pytest.raises(ValueError, match="No valid data"):
            strategy.validate_data(df)

    def test_validate_no_row_categories_fails(self):
        """Test that no row categories raises error."""
        config = get_nunique_config()
        strategy = HeatmapStrategy(config)

        df = pd.DataFrame({
            'referenceAG': [None],
            'sample': ['S1'],
            'ko': ['K00001']
        })

        # Nulls removed first
        with pytest.raises(ValueError, match="No valid data"):
            strategy.validate_data(df)

    def test_validate_no_col_categories_fails(self):
        """Test that no column categories raises error."""
        config = get_nunique_config()
        strategy = HeatmapStrategy(config)

        df = pd.DataFrame({
            'referenceAG': ['EPA'],
            'sample': [None],
            'ko': ['K00001']
        })

        # Nulls removed first
        with pytest.raises(ValueError, match="No valid data"):
            strategy.validate_data(df)

    def test_validate_success(self):
        """Test successful validation."""
        config = get_nunique_config()
        strategy = HeatmapStrategy(config)

        df = get_sample_data()

        # Should not raise
        strategy.validate_data(df)


# ============================================================================
# TEST CLASS: Data Processing - nunique
# ============================================================================

class TestDataProcessingNunique:
    """Test process_data() with nunique aggregation."""

    def test_process_data_returns_dataframe(self):
        """Test that process_data returns a DataFrame."""
        config = get_nunique_config()
        strategy = HeatmapStrategy(config)

        df = get_sample_data()

        result = strategy.process_data(df)

        assert isinstance(result, pd.DataFrame)

    def test_process_data_shape(self):
        """Test that matrix has correct shape (rows x columns)."""
        config = get_nunique_config()
        strategy = HeatmapStrategy(config)

        df = get_sample_data()

        result = strategy.process_data(df)

        # Should have 3 agencies (rows) and 3 samples (columns)
        assert result.shape == (3, 3)

    def test_process_data_correct_counts(self):
        """Test that nunique counts are calculated correctly."""
        config = get_nunique_config()
        strategy = HeatmapStrategy(config)

        df = get_sample_data()

        result = strategy.process_data(df)

        # EPA - Sample1: 2 unique KOs
        assert result.loc['EPA', 'Sample1'] == 2

        # EPA - Sample2: 2 unique KOs
        assert result.loc['EPA', 'Sample2'] == 2

        # EPA - Sample3: 3 unique KOs
        assert result.loc['EPA', 'Sample3'] == 3

        # WHO - Sample1: 1 unique KO
        assert result.loc['WHO', 'Sample1'] == 1

        # ATSDR - Sample1: 1 unique KO
        assert result.loc['ATSDR', 'Sample1'] == 1

    def test_process_data_fills_missing_with_zero(self):
        """Test that missing combinations are filled with 0."""
        config = get_nunique_config()
        strategy = HeatmapStrategy(config)

        df = get_sample_data()

        result = strategy.process_data(df)

        # ATSDR - Sample2: no entries -> 0
        assert result.loc['ATSDR', 'Sample2'] == 0

    def test_process_data_removes_nulls(self):
        """Test that null values are removed."""
        config = get_nunique_config()
        strategy = HeatmapStrategy(config)

        df = pd.DataFrame({
            'referenceAG': ['EPA', 'WHO', None, 'ATSDR'],
            'sample': ['S1', None, 'S2', 'S3'],
            'ko': ['K00001', 'K00002', 'K00003', None]
        })

        result = strategy.process_data(df)

        # Only EPA-S1 is complete
        assert 'EPA' in result.index
        assert 'S1' in result.columns

    def test_process_data_normalizes_strings(self):
        """Test that string columns are normalized."""
        config = get_nunique_config()
        strategy = HeatmapStrategy(config)

        df = pd.DataFrame({
            'referenceAG': ['  epa  ', 'who', 'atsdr'],
            'sample': ['Sample1', 'Sample2', 'Sample3'],
            'ko': ['  k00001  ', 'k00002', 'k00003']
        })

        result = strategy.process_data(df)

        # Should be uppercased and stripped
        assert 'EPA' in result.index
        assert 'WHO' in result.index


# ============================================================================
# TEST CLASS: Data Processing - count
# ============================================================================

class TestDataProcessingCount:
    """Test process_data() with count aggregation."""

    def test_process_data_count_mode(self):
        """Test count aggregation."""
        config = get_count_config()
        strategy = HeatmapStrategy(config)

        df = pd.DataFrame({
            'category': ['A', 'A', 'A', 'B', 'B'],
            'item': ['X', 'X', 'Y', 'X', 'Y'],
            'value': ['v1', 'v2', 'v3', 'v4', 'v5']
        })

        result = strategy.process_data(df)

        # A-X: 2 occurrences
        assert result.loc['A', 'X'] == 2

        # A-Y: 1 occurrence
        assert result.loc['A', 'Y'] == 1

        # B-X: 1 occurrence
        assert result.loc['B', 'X'] == 1

    def test_process_data_count_duplicates(self):
        """Test that count includes duplicate values."""
        config = get_count_config()
        strategy = HeatmapStrategy(config)

        df = pd.DataFrame({
            'category': ['A', 'A', 'A'],
            'item': ['X', 'X', 'X'],
            'value': ['same', 'same', 'same']  # All identical
        })

        result = strategy.process_data(df)

        # Should count all 3 occurrences
        assert result.loc['A', 'X'] == 3


# ============================================================================
# TEST CLASS: Data Processing - sum
# ============================================================================

class TestDataProcessingSum:
    """Test process_data() with sum aggregation."""

    def test_process_data_sum_mode(self):
        """Test sum aggregation."""
        config = get_sum_config()
        strategy = HeatmapStrategy(config)

        df = get_numeric_data()

        result = strategy.process_data(df)

        # A-X: 10
        assert result.loc['A', 'X'] == 10

        # B-Y: 40
        assert result.loc['B', 'Y'] == 40

        # C-X: 50
        assert result.loc['C', 'X'] == 50

    def test_process_data_sum_multiple_values(self):
        """Test sum aggregation with multiple values."""
        config = get_sum_config()
        strategy = HeatmapStrategy(config)

        df = pd.DataFrame({
            'category': ['A', 'A', 'A'],
            'item': ['X', 'X', 'X'],
            'amount': [10, 20, 30]
        })

        result = strategy.process_data(df)

        # Should sum: 10 + 20 + 30 = 60
        assert result.loc['A', 'X'] == 60


# ============================================================================
# TEST CLASS: Sorting and Conversion
# ============================================================================

class TestSortingAndConversion:
    """Test sorting and data type conversion."""

    def test_process_data_sorts_by_totals(self):
        """Test that rows and columns are sorted by total counts."""
        config = get_nunique_config()
        strategy = HeatmapStrategy(config)

        df = get_sample_data()

        result = strategy.process_data(df)

        # Calculate row totals
        row_totals = result.sum(axis=1)

        # Check rows are sorted descending by total
        assert list(row_totals.index) == list(
            row_totals.sort_values(ascending=False).index
        )

        # Calculate column totals
        col_totals = result.sum(axis=0)

        # Check columns are sorted descending by total
        assert list(col_totals.index) == list(
            col_totals.sort_values(ascending=False).index
        )

    def test_process_data_converts_to_int(self):
        """Test that whole numbers are converted to int."""
        config = get_nunique_config()
        strategy = HeatmapStrategy(config)

        df = get_sample_data()

        result = strategy.process_data(df)

        # Should be integers for count data
        assert result.dtypes.iloc[0] == int


# ============================================================================
# TEST CLASS: Invalid Aggregation
# ============================================================================

class TestInvalidAggregation:
    """Test invalid aggregation method."""

    def test_process_data_invalid_aggregation_fails(self):
        """Test that invalid aggregation raises error."""
        config = {
            'metadata': {},
            'visualization': {
                'strategy': 'HeatmapStrategy',
                'plotly': {
                    'row_column': 'category',
                    'col_column': 'item',
                    'value_column': 'value',
                    'aggregation': 'invalid_method'
                }
            }
        }

        strategy = HeatmapStrategy(config)

        df = pd.DataFrame({
            'category': ['A'],
            'item': ['X'],
            'value': ['v1']
        })

        with pytest.raises(ValueError, match="Unknown aggregation method"):
            strategy.process_data(df)


# ============================================================================
# TEST CLASS: Figure Creation
# ============================================================================

class TestFigureCreation:
    """Test create_figure() method."""

    def test_create_figure_returns_figure(self):
        """Test that create_figure returns a Plotly Figure."""
        config = get_nunique_config()
        strategy = HeatmapStrategy(config)

        df = get_sample_data()
        processed = strategy.process_data(df)

        fig = strategy.create_figure(processed)

        assert isinstance(fig, go.Figure)

    def test_create_figure_has_heatmap_trace(self):
        """Test that figure contains heatmap trace."""
        config = get_nunique_config()
        strategy = HeatmapStrategy(config)

        df = get_sample_data()
        processed = strategy.process_data(df)

        fig = strategy.create_figure(processed)

        # Should have at least one trace
        assert len(fig.data) > 0

    def test_create_figure_applies_title(self):
        """Test that title is applied to figure."""
        config = get_nunique_config()
        strategy = HeatmapStrategy(config)

        df = get_sample_data()
        processed = strategy.process_data(df)

        fig = strategy.create_figure(processed)

        assert fig.layout.title.text == 'Sample-Agency Functional Potential'

    def test_create_figure_title_hidden(self):
        """Test that title can be hidden."""
        config = get_nunique_config()
        config['visualization']['plotly']['chart']['title']['show'] = False
        strategy = HeatmapStrategy(config)

        df = get_sample_data()
        processed = strategy.process_data(df)

        fig = strategy.create_figure(processed)

        # Title should be empty when disabled
        assert not hasattr(fig.layout, 'title') or \
            fig.layout.title.text is None or \
            fig.layout.title.text == ''

    def test_create_figure_applies_layout_config(self):
        """Test that layout configuration is applied."""
        config = get_nunique_config()
        strategy = HeatmapStrategy(config)

        df = get_sample_data()
        processed = strategy.process_data(df)

        fig = strategy.create_figure(processed)

        assert fig.layout.height == 600
        assert fig.layout.width == 1000

    def test_create_figure_with_autosize(self):
        """Test figure with autosize enabled."""
        config = get_nunique_config()
        config['visualization']['plotly']['layout']['autosize'] = True
        strategy = HeatmapStrategy(config)

        df = get_sample_data()
        processed = strategy.process_data(df)

        fig = strategy.create_figure(processed)

        # When autosize is True, width may or may not be set
        # Just check that figure is created
        assert isinstance(fig, go.Figure)

    def test_create_figure_dynamic_height(self):
        """Test that height adjusts to number of rows."""
        config = get_minimal_config()
        strategy = HeatmapStrategy(config)

        # Create data with many rows
        df = pd.DataFrame({
            'referenceAG': [f'Agency{i}' for i in range(20)],
            'sample': ['S1'] * 20,
            'ko': [f'K{str(i).zfill(5)}' for i in range(20)]
        })

        processed = strategy.process_data(df)
        fig = strategy.create_figure(processed)

        # Height should be dynamically calculated
        assert fig.layout.height > 500

    def test_create_figure_text_auto_small_matrix(self):
        """Test that text is shown for small matrices."""
        config = get_nunique_config()
        config['visualization']['plotly']['chart']['text_auto'] = True
        strategy = HeatmapStrategy(config)

        df = get_sample_data()
        processed = strategy.process_data(df)

        fig = strategy.create_figure(processed)

        # Small matrix should have text
        assert fig.data[0].texttemplate is not None

    def test_create_figure_no_grid_lines(self):
        """Test that grid lines are removed."""
        config = get_nunique_config()
        strategy = HeatmapStrategy(config)

        df = get_sample_data()
        processed = strategy.process_data(df)

        fig = strategy.create_figure(processed)

        # Grid lines should be disabled
        assert fig.layout.xaxis.showgrid is False
        assert fig.layout.yaxis.showgrid is False


# ============================================================================
# TEST CLASS: Integration
# ============================================================================

class TestIntegration:
    """Test complete workflow integration."""

    def test_generate_plot_nunique_workflow(self):
        """Test complete nunique workflow."""
        config = get_nunique_config()
        strategy = HeatmapStrategy(config)

        df = get_sample_data()

        # Complete workflow
        fig = strategy.generate_plot(df)

        assert isinstance(fig, go.Figure)
        assert len(fig.data) > 0

    def test_generate_plot_count_workflow(self):
        """Test complete count workflow."""
        config = get_count_config()
        strategy = HeatmapStrategy(config)

        df = pd.DataFrame({
            'category': ['A', 'A', 'B'],
            'item': ['X', 'Y', 'X'],
            'value': ['v1', 'v2', 'v3']
        })

        # Complete workflow
        fig = strategy.generate_plot(df)

        assert isinstance(fig, go.Figure)
        assert len(fig.data) > 0

    def test_generate_plot_sum_workflow(self):
        """Test complete sum workflow."""
        config = get_sum_config()
        strategy = HeatmapStrategy(config)

        df = get_numeric_data()

        # Complete workflow
        fig = strategy.generate_plot(df)

        assert isinstance(fig, go.Figure)
        assert len(fig.data) > 0

    def test_workflow_with_validation(self):
        """Test that validation is called in workflow."""
        config = get_nunique_config()
        strategy = HeatmapStrategy(config)

        df = pd.DataFrame()

        with pytest.raises(ValueError, match="Input DataFrame is empty"):
            strategy.generate_plot(df)

    def test_workflow_minimal_config(self):
        """Test workflow with minimal configuration."""
        config = get_minimal_config()
        strategy = HeatmapStrategy(config)

        df = pd.DataFrame({
            'referenceAG': ['EPA', 'WHO'],
            'sample': ['S1', 'S1'],
            'ko': ['K00001', 'K00002']
        })

        # Should work with defaults
        fig = strategy.generate_plot(df)

        assert isinstance(fig, go.Figure)


# ============================================================================
# TEST CLASS: Edge Cases
# ============================================================================

class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_single_row_category(self):
        """Test with single row category."""
        config = get_nunique_config()
        strategy = HeatmapStrategy(config)

        df = pd.DataFrame({
            'referenceAG': ['EPA', 'EPA'],
            'sample': ['S1', 'S2'],
            'ko': ['K00001', 'K00002']
        })

        fig = strategy.generate_plot(df)

        assert isinstance(fig, go.Figure)

    def test_single_col_category(self):
        """Test with single column category."""
        config = get_nunique_config()
        strategy = HeatmapStrategy(config)

        df = pd.DataFrame({
            'referenceAG': ['EPA', 'WHO'],
            'sample': ['S1', 'S1'],
            'ko': ['K00001', 'K00002']
        })

        fig = strategy.generate_plot(df)

        assert isinstance(fig, go.Figure)

    def test_all_counts_zero(self):
        """Test when combinations result in zero counts."""
        config = get_nunique_config()
        strategy = HeatmapStrategy(config)

        df = pd.DataFrame({
            'referenceAG': ['EPA', 'WHO'],
            'sample': ['S1', 'S2'],
            'ko': ['K00001', 'K00002']
        })

        result = strategy.process_data(df)

        # Should have zeros for missing combinations
        assert 0 in result.values

    def test_many_rows(self):
        """Test with many row categories."""
        config = get_nunique_config()
        strategy = HeatmapStrategy(config)

        data = []
        for i in range(20):
            data.append({
                'referenceAG': f'Agency{i}',
                'sample': 'S1',
                'ko': f'K{str(i).zfill(5)}'
            })

        df = pd.DataFrame(data)

        fig = strategy.generate_plot(df)

        assert isinstance(fig, go.Figure)

    def test_many_columns(self):
        """Test with many column categories."""
        config = get_nunique_config()
        strategy = HeatmapStrategy(config)

        data = []
        for i in range(15):
            data.append({
                'referenceAG': 'EPA',
                'sample': f'Sample{i}',
                'ko': f'K{str(i).zfill(5)}'
            })

        df = pd.DataFrame(data)

        fig = strategy.generate_plot(df)

        assert isinstance(fig, go.Figure)

    def test_duplicate_entries(self):
        """Test that duplicate entries are handled correctly."""
        config = get_nunique_config()
        strategy = HeatmapStrategy(config)

        df = pd.DataFrame({
            'referenceAG': ['EPA', 'EPA', 'EPA'],
            'sample': ['S1', 'S1', 'S1'],
            'ko': ['K00001', 'K00001', 'K00001']  # Duplicates
        })

        result = strategy.process_data(df)

        # Should count K00001 only once (nunique)
        assert result.loc['EPA', 'S1'] == 1

    def test_special_characters_in_names(self):
        """Test with special characters in category names."""
        config = get_nunique_config()
        strategy = HeatmapStrategy(config)

        df = pd.DataFrame({
            'referenceAG': ['EPA-USA', 'WHO/Europe'],
            'sample': ['Sample (1)', 'Sample [2]'],
            'ko': ['K00001', 'K00002']
        })

        # Should handle special characters
        fig = strategy.generate_plot(df)

        assert isinstance(fig, go.Figure)

    def test_very_long_names(self):
        """Test with very long category names."""
        config = get_nunique_config()
        strategy = HeatmapStrategy(config)

        long_name = 'A' * 100

        df = pd.DataFrame({
            'referenceAG': [long_name],
            'sample': [long_name],
            'ko': ['K00001']
        })

        fig = strategy.generate_plot(df)

        assert isinstance(fig, go.Figure)

    def test_mixed_case_values(self):
        """Test with mixed case values."""
        config = get_nunique_config()
        strategy = HeatmapStrategy(config)

        df = pd.DataFrame({
            'referenceAG': ['epa', 'EPA', 'Epa'],
            'sample': ['Sample1', 'Sample2', 'Sample3'],
            'ko': ['k00001', 'K00002', 'K00003']
        })

        result = strategy.process_data(df)

        # All should be normalized to uppercase EPA
        assert 'EPA' in result.index
        # Original case variations should be merged
        assert result.shape[0] == 1  # Single row after normalization

    def test_single_value_per_combination(self):
        """Test when each combination has only one value."""
        config = get_nunique_config()
        strategy = HeatmapStrategy(config)

        df = pd.DataFrame({
            'referenceAG': ['EPA', 'WHO'],
            'sample': ['S1', 'S2'],
            'ko': ['K00001', 'K00002']
        })

        result = strategy.process_data(df)

        # Each cell should have count 1 or 0
        assert set(result.values.flatten()).issubset({0, 1})

    def test_negative_values_sum(self):
        """Test sum aggregation with negative values."""
        config = get_sum_config()
        strategy = HeatmapStrategy(config)

        df = pd.DataFrame({
            'category': ['A', 'A'],
            'item': ['X', 'X'],
            'amount': [10, -5]
        })

        result = strategy.process_data(df)

        # Should sum: 10 + (-5) = 5
        assert result.loc['A', 'X'] == 5
