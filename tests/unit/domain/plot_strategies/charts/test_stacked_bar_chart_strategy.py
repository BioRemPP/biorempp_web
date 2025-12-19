"""
Unit tests for StackedBarChartStrategy.

This module tests the StackedBarChartStrategy class which creates 100% stacked
bar charts for proportional visualizations.

Test Categories
---------------
1. Initialization (5 tests)
2. Validation (7 tests)
3. Data Processing (15 tests)
4. Figure Creation (10 tests)
5. Integration (4 tests)
6. Edge Cases (8 tests)

Total: 49 tests
"""

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import pytest

from src.domain.plot_strategies.charts.stacked_bar_chart_strategy import (
    StackedBarChartStrategy
)


# =======================
# Helper Functions
# =======================


def get_minimal_config():
    """Get minimal configuration for StackedBarChartStrategy."""
    return {
        'metadata': {
            'use_case_id': 'UC-1.3',
            'module': 'module1'
        },
        'data': {},
        'visualization': {
            'strategy': 'StackedBarChartStrategy',
            'plotly': {
                'category_column': 'referenceAG',
                'value_column': 'ko',
                'aggregation_function': 'nunique',
                'constant_x_label': 'Total Unique KOs',
                'chart': {
                    'title': {
                        'text': 'Reference AG Proportions',
                        'x': 0.5
                    }
                },
                'layout': {
                    'height': 520,
                    'width': 380,
                    'template': 'simple_white'
                }
            }
        }
    }


def get_sample_config():
    """Get configuration for sample-based stacking (UC-1.4)."""
    config = get_minimal_config()
    config['metadata']['use_case_id'] = 'UC-1.4'
    config['visualization']['plotly']['category_column'] = 'sample'
    config['visualization']['plotly']['chart']['title']['text'] = \
        'Sample Proportions'
    return config


def get_sample_data():
    """Get sample data for stacked bar testing."""
    np.random.seed(42)
    return pd.DataFrame({
        'referenceAG': ['EPA', 'EPA', 'WHO', 'WHO', 'FDA'],
        'ko': ['K00001', 'K00002', 'K00001', 'K00003', 'K00004']
    })


def get_sample_based_data():
    """Get sample-based data for testing."""
    np.random.seed(42)
    return pd.DataFrame({
        'sample': ['S1', 'S1', 'S2', 'S2', 'S2', 'S3'],
        'ko': ['K00001', 'K00002', 'K00001', 'K00003', 'K00004', 'K00001']
    })


def get_large_sample_data():
    """Get large dataset."""
    np.random.seed(42)
    n = 100
    agencies = ['EPA', 'WHO', 'FDA', 'ATSDR', 'OSHA']
    kos = [f'K{str(i).zfill(5)}' for i in range(50)]
    return pd.DataFrame({
        'referenceAG': np.random.choice(agencies, n),
        'ko': np.random.choice(kos, n)
    })


# =======================
# Test Class
# =======================


class TestStackedBarChartStrategy:
    """Test suite for StackedBarChartStrategy."""

    # =======================
    # 1. Initialization Tests
    # =======================

    def test_init_minimal_config(self):
        """Test initialization with minimal configuration."""
        # Arrange & Act
        config = get_minimal_config()
        strategy = StackedBarChartStrategy(config)

        # Assert
        assert strategy is not None
        assert strategy.category_column == 'referenceAG'
        assert strategy.value_column == 'ko'
        assert strategy.aggregation_function == 'nunique'

    def test_init_sample_config(self):
        """Test initialization with sample-based config."""
        # Arrange & Act
        config = get_sample_config()
        strategy = StackedBarChartStrategy(config)

        # Assert
        assert strategy.category_column == 'sample'
        assert strategy.value_column == 'ko'

    def test_init_default_values(self):
        """Test initialization uses default values when not specified."""
        # Arrange
        config = {
            'metadata': {'use_case_id': 'UC-1.3'},
            'data': {},
            'visualization': {'plotly': {}}
        }

        # Act
        strategy = StackedBarChartStrategy(config)

        # Assert
        assert strategy.category_column == 'referenceAG'
        assert strategy.value_column == 'ko'
        assert strategy.aggregation_function == 'nunique'
        assert strategy.constant_x_label == 'Total'

    def test_init_extracts_configs(self):
        """Test initialization extracts data and plotly configs."""
        # Arrange & Act
        config = get_minimal_config()
        strategy = StackedBarChartStrategy(config)

        # Assert
        assert strategy.data_config is not None
        assert strategy.plotly_config is not None

    def test_init_custom_aggregation(self):
        """Test initialization with custom aggregation function."""
        # Arrange
        config = get_minimal_config()
        config['visualization']['plotly']['aggregation_function'] = 'count'

        # Act
        strategy = StackedBarChartStrategy(config)

        # Assert
        assert strategy.aggregation_function == 'count'

    # =======================
    # 2. Validation Tests
    # =======================

    def test_validate_empty_dataframe_fails(self):
        """Test validation fails with empty DataFrame."""
        # Arrange
        config = get_minimal_config()
        strategy = StackedBarChartStrategy(config)
        df = pd.DataFrame()

        # Act & Assert
        with pytest.raises(ValueError, match="Input DataFrame is empty"):
            strategy.validate_data(df)

    def test_validate_missing_category_column(self):
        """Test validation fails when category column is missing."""
        # Arrange
        config = get_minimal_config()
        strategy = StackedBarChartStrategy(config)
        df = pd.DataFrame({'ko': ['K00001']})

        # Act & Assert
        with pytest.raises(ValueError, match="Missing required columns"):
            strategy.validate_data(df)

    def test_validate_missing_value_column(self):
        """Test validation fails when value column is missing."""
        # Arrange
        config = get_minimal_config()
        strategy = StackedBarChartStrategy(config)
        df = pd.DataFrame({'referenceAG': ['EPA']})

        # Act & Assert
        with pytest.raises(ValueError, match="Missing required columns"):
            strategy.validate_data(df)

    def test_validate_all_nulls_fails(self):
        """Test validation fails when all data is null."""
        # Arrange
        config = get_minimal_config()
        strategy = StackedBarChartStrategy(config)
        df = pd.DataFrame({
            'referenceAG': [None, None],
            'ko': [None, None]
        })

        # Act & Assert
        with pytest.raises(ValueError, match="No valid data found"):
            strategy.validate_data(df)

    def test_validate_sample_data_passes(self):
        """Test validation passes with valid data."""
        # Arrange
        config = get_minimal_config()
        strategy = StackedBarChartStrategy(config)
        df = get_sample_data()

        # Act & Assert (should not raise)
        strategy.validate_data(df)

    def test_validate_with_some_nulls_passes(self):
        """Test validation passes with some nulls."""
        # Arrange
        config = get_minimal_config()
        strategy = StackedBarChartStrategy(config)
        df = pd.DataFrame({
            'referenceAG': ['EPA', None, 'WHO'],
            'ko': ['K00001', 'K00002', None]
        })

        # Act & Assert (should not raise)
        strategy.validate_data(df)

    def test_validate_large_dataset(self):
        """Test validation passes with large dataset."""
        # Arrange
        config = get_minimal_config()
        strategy = StackedBarChartStrategy(config)
        df = get_large_sample_data()

        # Act & Assert (should not raise)
        strategy.validate_data(df)

    # =======================
    # 3. Data Processing Tests
    # =======================

    def test_process_data_creates_required_columns(self):
        """Test process_data creates all required columns."""
        # Arrange
        config = get_minimal_config()
        strategy = StackedBarChartStrategy(config)
        df = get_sample_data()

        # Act
        result = strategy.process_data(df)

        # Assert
        assert 'referenceAG' in result.columns
        assert 'count' in result.columns
        assert 'percent' in result.columns
        assert 'percent_fmt' in result.columns
        assert 'x_axis' in result.columns

    def test_process_data_nunique_aggregation(self):
        """Test process_data with nunique aggregation."""
        # Arrange
        config = get_minimal_config()
        strategy = StackedBarChartStrategy(config)
        df = get_sample_data()

        # Act
        result = strategy.process_data(df)

        # Assert
        # EPA: 2 unique KOs, WHO: 2 unique KOs, FDA: 1 unique KO
        epa = result[result['referenceAG'] == 'EPA']
        assert len(epa) == 1
        assert epa['count'].values[0] == 2

    def test_process_data_count_aggregation(self):
        """Test process_data with count aggregation."""
        # Arrange
        config = get_minimal_config()
        config['visualization']['plotly']['aggregation_function'] = 'count'
        strategy = StackedBarChartStrategy(config)
        df = get_sample_data()

        # Act
        result = strategy.process_data(df)

        # Assert
        epa = result[result['referenceAG'] == 'EPA']
        assert epa['count'].values[0] == 2

    def test_process_data_sum_aggregation(self):
        """Test process_data with sum aggregation."""
        # Arrange
        config = get_minimal_config()
        config['visualization']['plotly']['aggregation_function'] = 'sum'
        config['visualization']['plotly']['value_column'] = 'value'
        strategy = StackedBarChartStrategy(config)
        df = pd.DataFrame({
            'referenceAG': ['EPA', 'EPA', 'WHO'],
            'value': [10, 20, 15]
        })

        # Act
        result = strategy.process_data(df)

        # Assert
        epa = result[result['referenceAG'] == 'EPA']
        assert epa['count'].values[0] == 30

    def test_process_data_invalid_aggregation_fails(self):
        """Test process_data fails with invalid aggregation."""
        # Arrange
        config = get_minimal_config()
        config['visualization']['plotly']['aggregation_function'] = 'invalid'
        strategy = StackedBarChartStrategy(config)
        df = get_sample_data()

        # Act & Assert
        with pytest.raises(ValueError, match="Unsupported aggregation"):
            strategy.process_data(df)

    def test_process_data_removes_nulls(self):
        """Test process_data removes null values."""
        # Arrange
        config = get_minimal_config()
        strategy = StackedBarChartStrategy(config)
        df = pd.DataFrame({
            'referenceAG': ['EPA', None, 'WHO'],
            'ko': ['K00001', 'K00002', None]
        })

        # Act
        result = strategy.process_data(df)

        # Assert
        # Only EPA should remain (1 valid row)
        assert len(result) == 1

    def test_process_data_normalizes_strings(self):
        """Test process_data normalizes strings to uppercase."""
        # Arrange
        config = get_minimal_config()
        strategy = StackedBarChartStrategy(config)
        df = pd.DataFrame({
            'referenceAG': ['epa', ' EPA ', 'who'],
            'ko': ['k00001', 'K00002', ' k00003 ']
        })

        # Act
        result = strategy.process_data(df)

        # Assert
        assert 'EPA' in result['referenceAG'].values
        assert 'WHO' in result['referenceAG'].values

    def test_process_data_drops_duplicates(self):
        """Test process_data drops duplicate rows."""
        # Arrange
        config = get_minimal_config()
        strategy = StackedBarChartStrategy(config)
        df = pd.DataFrame({
            'referenceAG': ['EPA', 'EPA', 'EPA'],
            'ko': ['K00001', 'K00001', 'K00002']
        })

        # Act
        result = strategy.process_data(df)

        # Assert
        # After dropping duplicates, EPA should have 2 unique KOs
        assert result['count'].values[0] == 2

    def test_process_data_calculates_percentages(self):
        """Test process_data calculates correct percentages."""
        # Arrange
        config = get_minimal_config()
        strategy = StackedBarChartStrategy(config)
        df = get_sample_data()

        # Act
        result = strategy.process_data(df)

        # Assert
        # Total percentages should sum to 100
        assert abs(result['percent'].sum() - 100.0) < 0.01

    def test_process_data_formats_percentages(self):
        """Test process_data formats percentage strings."""
        # Arrange
        config = get_minimal_config()
        strategy = StackedBarChartStrategy(config)
        df = get_sample_data()

        # Act
        result = strategy.process_data(df)

        # Assert
        # All percent_fmt should end with '%'
        assert all(result['percent_fmt'].str.endswith('%'))

    def test_process_data_adds_x_axis_label(self):
        """Test process_data adds constant x-axis label."""
        # Arrange
        config = get_minimal_config()
        strategy = StackedBarChartStrategy(config)
        df = get_sample_data()

        # Act
        result = strategy.process_data(df)

        # Assert
        assert all(result['x_axis'] == 'Total Unique KOs')

    def test_process_data_sample_based(self):
        """Test process_data with sample-based data."""
        # Arrange
        config = get_sample_config()
        strategy = StackedBarChartStrategy(config)
        df = get_sample_based_data()

        # Act
        result = strategy.process_data(df)

        # Assert
        # S2: 3 unique KOs
        s2 = result[result['sample'] == 'S2']
        assert s2['count'].values[0] == 3

    def test_process_data_large_dataset(self):
        """Test process_data with large dataset."""
        # Arrange
        config = get_minimal_config()
        strategy = StackedBarChartStrategy(config)
        df = get_large_sample_data()

        # Act
        result = strategy.process_data(df)

        # Assert
        assert len(result) > 0
        assert abs(result['percent'].sum() - 100.0) < 0.01

    def test_process_data_correct_shape(self):
        """Test process_data returns correct shape."""
        # Arrange
        config = get_minimal_config()
        strategy = StackedBarChartStrategy(config)
        df = get_sample_data()

        # Act
        result = strategy.process_data(df)

        # Assert
        # 3 unique agencies
        assert result.shape[0] == 3
        assert result.shape[1] == 5  # category, count, percent, percent_fmt, x_axis

    def test_process_data_percentage_range(self):
        """Test process_data percentage values are in valid range."""
        # Arrange
        config = get_minimal_config()
        strategy = StackedBarChartStrategy(config)
        df = get_sample_data()

        # Act
        result = strategy.process_data(df)

        # Assert
        assert all(result['percent'] >= 0)
        assert all(result['percent'] <= 100)

    # =======================
    # 4. Figure Creation Tests
    # =======================

    def test_create_figure_returns_figure(self):
        """Test create_figure returns Plotly Figure."""
        # Arrange
        config = get_minimal_config()
        strategy = StackedBarChartStrategy(config)
        df = get_sample_data()
        processed = strategy.process_data(df)

        # Act
        fig = strategy.create_figure(processed)

        # Assert
        assert isinstance(fig, go.Figure)

    def test_create_figure_barmode_stack(self):
        """Test figure uses barmode='stack'."""
        # Arrange
        config = get_minimal_config()
        strategy = StackedBarChartStrategy(config)
        df = get_sample_data()
        processed = strategy.process_data(df)

        # Act
        fig = strategy.create_figure(processed)

        # Assert
        assert fig.layout.barmode == 'stack'

    def test_create_figure_barnorm_percent(self):
        """Test figure uses barnorm='percent' for 100% stacking."""
        # Arrange
        config = get_minimal_config()
        strategy = StackedBarChartStrategy(config)
        df = get_sample_data()
        processed = strategy.process_data(df)

        # Act
        fig = strategy.create_figure(processed)

        # Assert
        assert fig.layout.barnorm == 'percent'

    def test_create_figure_title(self):
        """Test figure has correct title."""
        # Arrange
        config = get_minimal_config()
        strategy = StackedBarChartStrategy(config)
        df = get_sample_data()
        processed = strategy.process_data(df)

        # Act
        fig = strategy.create_figure(processed)

        # Assert
        assert 'Reference AG Proportions' in fig.layout.title.text

    def test_create_figure_layout_dimensions(self):
        """Test figure applies layout dimensions."""
        # Arrange
        config = get_minimal_config()
        strategy = StackedBarChartStrategy(config)
        df = get_sample_data()
        processed = strategy.process_data(df)

        # Act
        fig = strategy.create_figure(processed)

        # Assert
        assert fig.layout.height == 520
        assert fig.layout.width == 380

    def test_create_figure_yaxis_ticksuffix(self):
        """Test figure y-axis has percent suffix."""
        # Arrange
        config = get_minimal_config()
        strategy = StackedBarChartStrategy(config)
        df = get_sample_data()
        processed = strategy.process_data(df)

        # Act
        fig = strategy.create_figure(processed)

        # Assert
        assert fig.layout.yaxis.ticksuffix == '%'

    def test_create_figure_has_traces(self):
        """Test figure has traces for each category."""
        # Arrange
        config = get_minimal_config()
        strategy = StackedBarChartStrategy(config)
        df = get_sample_data()
        processed = strategy.process_data(df)

        # Act
        fig = strategy.create_figure(processed)

        # Assert
        # 3 categories = 3 traces
        assert len(fig.data) == 3

    def test_create_figure_text_inside(self):
        """Test figure positions text inside bars."""
        # Arrange
        config = get_minimal_config()
        strategy = StackedBarChartStrategy(config)
        df = get_sample_data()
        processed = strategy.process_data(df)

        # Act
        fig = strategy.create_figure(processed)

        # Assert
        assert fig.data[0].textposition == 'inside'

    def test_create_figure_autosize(self):
        """Test figure with autosize enabled."""
        # Arrange
        config = get_minimal_config()
        config['visualization']['plotly']['layout']['autosize'] = True
        strategy = StackedBarChartStrategy(config)
        df = get_sample_data()
        processed = strategy.process_data(df)

        # Act
        fig = strategy.create_figure(processed)

        # Assert
        assert isinstance(fig, go.Figure)

    def test_create_figure_legend_title(self):
        """Test figure has legend title."""
        # Arrange
        config = get_minimal_config()
        strategy = StackedBarChartStrategy(config)
        df = get_sample_data()
        processed = strategy.process_data(df)

        # Act
        fig = strategy.create_figure(processed)

        # Assert
        assert fig.layout.legend.title.text is not None

    # =======================
    # 5. Integration Tests
    # =======================

    def test_generate_plot_full_workflow(self):
        """Test complete workflow: validate -> process -> create."""
        # Arrange
        config = get_minimal_config()
        strategy = StackedBarChartStrategy(config)
        df = get_sample_data()

        # Act
        fig = strategy.generate_plot(df)

        # Assert
        assert isinstance(fig, go.Figure)
        assert fig.layout.barmode == 'stack'
        assert fig.layout.barnorm == 'percent'

    def test_generate_plot_sample_based(self):
        """Test workflow with sample-based data."""
        # Arrange
        config = get_sample_config()
        strategy = StackedBarChartStrategy(config)
        df = get_sample_based_data()

        # Act
        fig = strategy.generate_plot(df)

        # Assert
        assert isinstance(fig, go.Figure)

    def test_generate_plot_large_dataset(self):
        """Test workflow with large dataset."""
        # Arrange
        config = get_minimal_config()
        strategy = StackedBarChartStrategy(config)
        df = get_large_sample_data()

        # Act
        fig = strategy.generate_plot(df)

        # Assert
        assert isinstance(fig, go.Figure)

    def test_generate_plot_with_nulls(self):
        """Test workflow handles null values correctly."""
        # Arrange
        config = get_minimal_config()
        strategy = StackedBarChartStrategy(config)
        df = pd.DataFrame({
            'referenceAG': ['EPA', None, 'WHO', 'FDA'],
            'ko': ['K00001', 'K00002', None, 'K00003']
        })

        # Act
        fig = strategy.generate_plot(df)

        # Assert
        assert isinstance(fig, go.Figure)

    # =======================
    # 6. Edge Cases
    # =======================

    def test_edge_case_single_category(self):
        """Test stacked bar with single category."""
        # Arrange
        config = get_minimal_config()
        strategy = StackedBarChartStrategy(config)
        df = pd.DataFrame({
            'referenceAG': ['EPA', 'EPA'],
            'ko': ['K00001', 'K00002']
        })

        # Act
        fig = strategy.generate_plot(df)

        # Assert
        assert isinstance(fig, go.Figure)
        # Single category should have 100%
        processed = strategy.process_data(df)
        assert processed['percent'].values[0] == 100.0

    def test_edge_case_many_categories(self):
        """Test stacked bar with many categories."""
        # Arrange
        config = get_minimal_config()
        strategy = StackedBarChartStrategy(config)
        agencies = [f'AG{i}' for i in range(20)]
        df = pd.DataFrame({
            'referenceAG': agencies,
            'ko': [f'K{str(i).zfill(5)}' for i in range(20)]
        })

        # Act
        fig = strategy.generate_plot(df)

        # Assert
        assert isinstance(fig, go.Figure)

    def test_edge_case_special_characters_in_names(self):
        """Test stacked bar with special characters."""
        # Arrange
        config = get_minimal_config()
        strategy = StackedBarChartStrategy(config)
        df = pd.DataFrame({
            'referenceAG': ['AG@1', 'AG#2'],
            'ko': ['K00001', 'K00002']
        })

        # Act
        fig = strategy.generate_plot(df)

        # Assert
        assert isinstance(fig, go.Figure)

    def test_edge_case_very_long_names(self):
        """Test stacked bar with very long category names."""
        # Arrange
        config = get_minimal_config()
        strategy = StackedBarChartStrategy(config)
        long_name = 'Agency_' + 'A' * 100
        df = pd.DataFrame({
            'referenceAG': [long_name, 'WHO'],
            'ko': ['K00001', 'K00002']
        })

        # Act
        fig = strategy.generate_plot(df)

        # Assert
        assert isinstance(fig, go.Figure)

    def test_edge_case_numeric_category_names(self):
        """Test stacked bar with numeric category names."""
        # Arrange
        config = get_minimal_config()
        strategy = StackedBarChartStrategy(config)
        df = pd.DataFrame({
            'referenceAG': [1, 2, 3],
            'ko': ['K00001', 'K00002', 'K00003']
        })

        # Act
        fig = strategy.generate_plot(df)

        # Assert
        assert isinstance(fig, go.Figure)

    def test_edge_case_equal_proportions(self):
        """Test stacked bar with equal category proportions."""
        # Arrange
        config = get_minimal_config()
        strategy = StackedBarChartStrategy(config)
        df = pd.DataFrame({
            'referenceAG': ['EPA', 'WHO', 'FDA'],
            'ko': ['K00001', 'K00002', 'K00003']
        })

        # Act
        processed = strategy.process_data(df)

        # Assert
        # Each should have 33.33%
        assert all(abs(processed['percent'] - 33.333) < 0.01)

    def test_edge_case_unequal_proportions(self):
        """Test stacked bar with highly unequal proportions."""
        # Arrange
        config = get_minimal_config()
        strategy = StackedBarChartStrategy(config)
        df = pd.DataFrame({
            'referenceAG': ['EPA'] * 9 + ['WHO'],
            'ko': [f'K{str(i).zfill(5)}' for i in range(10)]
        })

        # Act
        processed = strategy.process_data(df)

        # Assert
        epa = processed[processed['referenceAG'] == 'EPA']
        who = processed[processed['referenceAG'] == 'WHO']
        assert epa['percent'].values[0] == 90.0
        assert who['percent'].values[0] == 10.0

    def test_edge_case_custom_x_label(self):
        """Test stacked bar with custom x-axis label."""
        # Arrange
        config = get_minimal_config()
        config['visualization']['plotly']['constant_x_label'] = 'Custom Label'
        strategy = StackedBarChartStrategy(config)
        df = get_sample_data()

        # Act
        processed = strategy.process_data(df)

        # Assert
        assert all(processed['x_axis'] == 'Custom Label')
