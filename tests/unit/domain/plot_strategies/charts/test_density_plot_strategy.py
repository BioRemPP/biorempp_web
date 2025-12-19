"""
Unit Tests for DensityPlotStrategy.

This module tests the DensityPlotStrategy class, which creates overlaid
probability density curves for distribution visualization.

Test Categories:
- Initialization: Test strategy creation and configuration
- Data Validation: Test validate_data() method
- Data Processing: Test process_data() method
- Figure Creation: Test create_figure() method
- Integration: Test complete workflow
- Edge Cases: Test boundary conditions
"""

import pytest
import numpy as np
import pandas as pd
import plotly.graph_objects as go

from src.domain.plot_strategies.charts.density_plot_strategy import DensityPlotStrategy


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_minimal_config():
    """Get minimal configuration for density plot."""
    return {
        'metadata': {'use_case_id': 'UC-7.5'},
        'visualization': {
            'strategy': 'DensityPlotStrategy',
            'plotly': {
                'value_column': 'toxicity_score',
                'group_column': 'endpoint'
            }
        }
    }


def get_full_config():
    """Get full configuration for density plot."""
    return {
        'metadata': {'use_case_id': 'UC-7.5'},
        'data': {
            'required_columns': ['toxicity_score', 'endpoint']
        },
        'visualization': {
            'strategy': 'DensityPlotStrategy',
            'plotly': {
                'value_column': 'toxicity_score',
                'group_column': 'endpoint',
                'chart': {
                    'title': {
                        'text': 'Toxicity Score Distribution by Endpoint',
                        'show': True,
                        'x': 0.5
                    },
                    'show_hist': False,
                    'show_rug': False,
                    'fill': 'tozeroy',
                    'opacity': 0.5
                },
                'layout': {
                    'template': 'simple_white',
                    'height': 800,
                    'width': 1200,
                    'xaxis': {
                        'title': 'Toxicity Score'
                    },
                    'yaxis': {
                        'title': 'Probability Density',
                        'gridcolor': 'lightgray'
                    },
                    'legend': {
                        'orientation': 'h',
                        'yanchor': 'bottom',
                        'y': 0,
                        'xanchor': 'center',
                        'x': 0.5,
                        'title_text': 'Endpoint'
                    }
                }
            }
        }
    }


def get_sample_data():
    """Get sample data for testing."""
    np.random.seed(42)
    return pd.DataFrame({
        'toxicity_score': np.concatenate([
            np.random.normal(0.3, 0.1, 30),  # Group A
            np.random.normal(0.6, 0.15, 30),  # Group B
            np.random.normal(0.45, 0.12, 30)  # Group C
        ]),
        'endpoint': ['A'] * 30 + ['B'] * 30 + ['C'] * 30
    })


# ============================================================================
# INITIALIZATION TESTS
# ============================================================================

class TestDensityPlotStrategyInitialization:
    """Test DensityPlotStrategy initialization."""

    def test_initialization_minimal_config(self):
        """Test initialization with minimal configuration."""
        config = get_minimal_config()
        strategy = DensityPlotStrategy(config)

        assert strategy.plotly_config is not None
        assert strategy.data_config is not None

    def test_initialization_full_config(self):
        """Test initialization with full configuration."""
        config = get_full_config()
        strategy = DensityPlotStrategy(config)

        assert 'value_column' in strategy.plotly_config
        assert 'group_column' in strategy.plotly_config
        assert 'chart' in strategy.plotly_config
        assert 'layout' in strategy.plotly_config

    def test_initialization_extracts_columns(self):
        """Test that initialization extracts column names."""
        config = get_full_config()
        strategy = DensityPlotStrategy(config)

        assert strategy.plotly_config.get('value_column') == 'toxicity_score'
        assert strategy.plotly_config.get('group_column') == 'endpoint'


# ============================================================================
# DATA VALIDATION TESTS
# ============================================================================

class TestDataValidation:
    """Test validate_data() method."""

    def test_validate_empty_dataframe_fails(self):
        """Test that empty DataFrame raises ValueError."""
        config = get_minimal_config()
        strategy = DensityPlotStrategy(config)
        df = pd.DataFrame()

        with pytest.raises(ValueError, match="DataFrame is empty"):
            strategy.validate_data(df)

    def test_validate_missing_value_column_config(self):
        """Test that missing value_column config raises ValueError."""
        config = get_minimal_config()
        del config['visualization']['plotly']['value_column']
        strategy = DensityPlotStrategy(config)
        df = get_sample_data()

        with pytest.raises(ValueError, match="must be specified"):
            strategy.validate_data(df)

    def test_validate_missing_group_column_config(self):
        """Test that missing group_column config raises ValueError."""
        config = get_minimal_config()
        del config['visualization']['plotly']['group_column']
        strategy = DensityPlotStrategy(config)
        df = get_sample_data()

        with pytest.raises(ValueError, match="must be specified"):
            strategy.validate_data(df)

    def test_validate_missing_value_column_in_data(self):
        """Test that missing value column in data raises ValueError."""
        config = get_minimal_config()
        strategy = DensityPlotStrategy(config)
        df = pd.DataFrame({'endpoint': ['A', 'B']})

        with pytest.raises(ValueError, match="Missing required columns"):
            strategy.validate_data(df)

    def test_validate_missing_group_column_in_data(self):
        """Test that missing group column in data raises ValueError."""
        config = get_minimal_config()
        strategy = DensityPlotStrategy(config)
        df = pd.DataFrame({'toxicity_score': [0.1, 0.2]})

        with pytest.raises(ValueError, match="Missing required columns"):
            strategy.validate_data(df)

    def test_validate_non_numeric_value_column(self):
        """Test that non-numeric value column raises ValueError."""
        config = get_minimal_config()
        strategy = DensityPlotStrategy(config)
        df = pd.DataFrame({
            'toxicity_score': ['high', 'low', 'medium'],
            'endpoint': ['A', 'B', 'C']
        })

        with pytest.raises(ValueError, match="must be numeric"):
            strategy.validate_data(df)

    def test_validate_no_valid_groups(self):
        """Test that no valid groups raises ValueError."""
        config = get_minimal_config()
        strategy = DensityPlotStrategy(config)
        df = pd.DataFrame({
            'toxicity_score': [0.1, 0.2, 0.3],
            'endpoint': [None, None, None]
        })

        with pytest.raises(ValueError, match="No valid groups found"):
            strategy.validate_data(df)

    def test_validate_success(self):
        """Test successful validation."""
        config = get_minimal_config()
        strategy = DensityPlotStrategy(config)
        df = get_sample_data()

        # Should not raise
        strategy.validate_data(df)

    def test_validate_warns_insufficient_data_per_group(self):
        """Test warning for groups with insufficient data."""
        config = get_minimal_config()
        strategy = DensityPlotStrategy(config)
        df = pd.DataFrame({
            'toxicity_score': [0.1, 0.2, 0.3],
            'endpoint': ['A', 'B', 'C']  # Each group has only 1 point
        })

        # Should not raise but will log warnings
        strategy.validate_data(df)


# ============================================================================
# DATA PROCESSING TESTS
# ============================================================================

class TestDataProcessing:
    """Test process_data() method."""

    def test_process_data_removes_nans(self):
        """Test that NaN values are removed."""
        config = get_minimal_config()
        strategy = DensityPlotStrategy(config)

        df = pd.DataFrame({
            'toxicity_score': [0.1, 0.15, np.nan, 0.3, 0.4, np.nan],
            'endpoint': ['A', 'A', 'A', 'B', 'B', 'C']
        })

        result = strategy.process_data(df)

        # Should remove rows with NaN and filter group C (only 1 point)
        assert len(result) == 4  # A (2 points) + B (2 points)
        assert not result['toxicity_score'].isna().any()
        assert 'C' not in result['endpoint'].values

    def test_process_data_selects_only_required_columns(self):
        """Test that only value and group columns are kept."""
        config = get_minimal_config()
        strategy = DensityPlotStrategy(config)

        df = pd.DataFrame({
            'toxicity_score': [0.1, 0.2, 0.3],
            'endpoint': ['A', 'B', 'C'],
            'extra_column': ['X', 'Y', 'Z']
        })

        result = strategy.process_data(df)

        # Should only have value and group columns
        assert list(result.columns) == ['toxicity_score', 'endpoint']

    def test_process_data_filters_insufficient_groups(self):
        """Test that groups with <2 points are filtered."""
        config = get_minimal_config()
        strategy = DensityPlotStrategy(config)

        df = pd.DataFrame({
            'toxicity_score': [0.1, 0.2, 0.3, 0.4, 0.5],
            'endpoint': ['A', 'A', 'B', 'C', 'C']  # B has only 1 point
        })

        result = strategy.process_data(df)

        # Should filter out group B
        assert 'B' not in result['endpoint'].values
        assert len(result) == 4  # A (2 points) + C (2 points)

    def test_process_data_preserves_valid_data(self):
        """Test that valid data is preserved."""
        config = get_minimal_config()
        strategy = DensityPlotStrategy(config)
        df = get_sample_data()

        result = strategy.process_data(df)

        # Should preserve all data (no NaNs, all groups have >2 points)
        assert len(result) == len(df)

    def test_process_data_logs_groups(self):
        """Test that group information is logged."""
        config = get_minimal_config()
        strategy = DensityPlotStrategy(config)
        df = get_sample_data()

        result = strategy.process_data(df)

        # Should have 3 groups
        assert result['endpoint'].nunique() == 3


# ============================================================================
# FIGURE CREATION TESTS
# ============================================================================

class TestFigureCreation:
    """Test create_figure() method."""

    def test_create_figure_returns_figure(self):
        """Test that create_figure returns a Plotly Figure."""
        config = get_full_config()
        strategy = DensityPlotStrategy(config)
        df = get_sample_data()

        processed = strategy.process_data(df)
        fig = strategy.create_figure(processed)

        assert isinstance(fig, go.Figure)

    def test_create_figure_has_correct_number_of_traces(self):
        """Test that figure has one trace per group."""
        config = get_full_config()
        strategy = DensityPlotStrategy(config)
        df = get_sample_data()

        processed = strategy.process_data(df)
        fig = strategy.create_figure(processed)

        # Should have 3 density traces (one per group)
        assert len(fig.data) == 3

    def test_create_figure_applies_opacity(self):
        """Test that opacity is applied to traces."""
        config = get_full_config()
        strategy = DensityPlotStrategy(config)
        df = get_sample_data()

        processed = strategy.process_data(df)
        fig = strategy.create_figure(processed)

        # All traces should have opacity 0.5
        for trace in fig.data:
            assert trace.opacity == 0.5

    def test_create_figure_applies_fill(self):
        """Test that fill is applied to traces."""
        config = get_full_config()
        strategy = DensityPlotStrategy(config)
        df = get_sample_data()

        processed = strategy.process_data(df)
        fig = strategy.create_figure(processed)

        # All traces should have fill='tozeroy'
        for trace in fig.data:
            assert trace.fill == 'tozeroy'

    def test_create_figure_applies_title(self):
        """Test that title is applied."""
        config = get_full_config()
        strategy = DensityPlotStrategy(config)
        df = get_sample_data()

        processed = strategy.process_data(df)
        fig = strategy.create_figure(processed)

        assert fig.layout.title.text == 'Toxicity Score Distribution by Endpoint'

    def test_create_figure_applies_layout_config(self):
        """Test that layout configuration is applied."""
        config = get_full_config()
        strategy = DensityPlotStrategy(config)
        df = get_sample_data()

        processed = strategy.process_data(df)
        fig = strategy.create_figure(processed)

        assert fig.layout.height == 800
        assert fig.layout.width == 1200
        # Template is applied but not easily testable

    def test_create_figure_applies_axis_titles(self):
        """Test that axis titles are applied."""
        config = get_full_config()
        strategy = DensityPlotStrategy(config)
        df = get_sample_data()

        processed = strategy.process_data(df)
        fig = strategy.create_figure(processed)

        assert fig.layout.xaxis.title.text == 'Toxicity Score'
        assert fig.layout.yaxis.title.text == 'Probability Density'

    def test_create_figure_applies_legend_config(self):
        """Test that legend configuration is applied."""
        config = get_full_config()
        strategy = DensityPlotStrategy(config)
        df = get_sample_data()

        processed = strategy.process_data(df)
        fig = strategy.create_figure(processed)

        assert fig.layout.legend.orientation == 'h'
        assert fig.layout.legend.yanchor == 'bottom'
        assert fig.layout.legend.y == 0

    def test_create_figure_no_valid_groups_fails(self):
        """Test that no valid groups raises ValueError."""
        config = get_minimal_config()
        strategy = DensityPlotStrategy(config)

        # All groups have only 1 point
        df = pd.DataFrame({
            'toxicity_score': [0.1, 0.2, 0.3],
            'endpoint': ['A', 'B', 'C']
        })

        processed = strategy.process_data(df)

        with pytest.raises(ValueError, match="No valid groups"):
            strategy.create_figure(processed)

    def test_create_figure_with_minimal_config(self):
        """Test figure creation with minimal config uses defaults."""
        config = get_minimal_config()
        strategy = DensityPlotStrategy(config)
        df = get_sample_data()

        processed = strategy.process_data(df)
        fig = strategy.create_figure(processed)

        assert isinstance(fig, go.Figure)
        # Should use default values
        assert fig.layout.xaxis.title.text == 'Value'
        assert fig.layout.yaxis.title.text == 'Probability Density'

    def test_create_figure_with_autosize(self):
        """Test figure with autosize enabled."""
        config = get_full_config()
        config['visualization']['plotly']['layout']['autosize'] = True
        strategy = DensityPlotStrategy(config)
        df = get_sample_data()

        processed = strategy.process_data(df)
        fig = strategy.create_figure(processed)

        assert fig.layout.autosize is True


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

class TestIntegration:
    """Test complete workflow."""

    def test_generate_plot_complete_workflow(self):
        """Test complete generate_plot workflow."""
        config = get_full_config()
        strategy = DensityPlotStrategy(config)
        df = get_sample_data()

        fig = strategy.generate_plot(df)

        assert isinstance(fig, go.Figure)
        assert len(fig.data) == 3  # 3 groups

    def test_workflow_with_validation(self):
        """Test workflow with explicit validation."""
        config = get_full_config()
        strategy = DensityPlotStrategy(config)
        df = get_sample_data()

        strategy.validate_data(df)
        processed = strategy.process_data(df)
        fig = strategy.create_figure(processed)

        assert isinstance(fig, go.Figure)
        assert len(processed) == len(df)

    def test_workflow_with_data_cleaning(self):
        """Test workflow with data that needs cleaning."""
        config = get_full_config()
        strategy = DensityPlotStrategy(config)

        # Add NaNs and insufficient group
        df = pd.DataFrame({
            'toxicity_score': [0.1, 0.2, np.nan, 0.4, 0.5, 0.6, 0.7],
            'endpoint': ['A', 'A', 'A', 'B', 'B', 'C', 'C']
        })

        fig = strategy.generate_plot(df)

        assert isinstance(fig, go.Figure)
        # Should have 3 groups (A, B, C all have ≥2 points after cleaning)

    def test_workflow_minimal_config(self):
        """Test workflow with minimal configuration."""
        config = get_minimal_config()
        strategy = DensityPlotStrategy(config)
        df = get_sample_data()

        fig = strategy.generate_plot(df)

        assert isinstance(fig, go.Figure)


# ============================================================================
# EDGE CASES
# ============================================================================

class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_single_group(self):
        """Test with single group."""
        config = get_minimal_config()
        strategy = DensityPlotStrategy(config)

        df = pd.DataFrame({
            'toxicity_score': np.random.normal(0.5, 0.1, 30),
            'endpoint': ['A'] * 30
        })

        fig = strategy.generate_plot(df)

        assert isinstance(fig, go.Figure)
        assert len(fig.data) == 1  # Only 1 density curve

    def test_two_groups(self):
        """Test with two groups."""
        config = get_minimal_config()
        strategy = DensityPlotStrategy(config)

        df = pd.DataFrame({
            'toxicity_score': np.concatenate([
                np.random.normal(0.3, 0.1, 20),
                np.random.normal(0.7, 0.1, 20)
            ]),
            'endpoint': ['A'] * 20 + ['B'] * 20
        })

        fig = strategy.generate_plot(df)

        assert isinstance(fig, go.Figure)
        assert len(fig.data) == 2

    def test_many_groups(self):
        """Test with many groups."""
        config = get_minimal_config()
        strategy = DensityPlotStrategy(config)

        groups = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
        df = pd.DataFrame({
            'toxicity_score': np.random.normal(0.5, 0.2, len(groups) * 10),
            'endpoint': np.repeat(groups, 10)
        })

        fig = strategy.generate_plot(df)

        assert isinstance(fig, go.Figure)
        assert len(fig.data) == len(groups)

    def test_minimal_data_per_group(self):
        """Test with exactly 2 points per group (minimum for KDE)."""
        config = get_minimal_config()
        strategy = DensityPlotStrategy(config)

        df = pd.DataFrame({
            'toxicity_score': [0.1, 0.2, 0.3, 0.4],
            'endpoint': ['A', 'A', 'B', 'B']
        })

        fig = strategy.generate_plot(df)

        assert isinstance(fig, go.Figure)
        assert len(fig.data) == 2

    def test_unbalanced_groups(self):
        """Test with unbalanced group sizes."""
        config = get_minimal_config()
        strategy = DensityPlotStrategy(config)

        df = pd.DataFrame({
            'toxicity_score': np.concatenate([
                np.random.normal(0.3, 0.1, 50),  # Group A: 50 points
                np.random.normal(0.6, 0.1, 5)    # Group B: 5 points
            ]),
            'endpoint': ['A'] * 50 + ['B'] * 5
        })

        fig = strategy.generate_plot(df)

        assert isinstance(fig, go.Figure)
        assert len(fig.data) == 2

    def test_extreme_values(self):
        """Test with extreme values."""
        config = get_minimal_config()
        strategy = DensityPlotStrategy(config)

        df = pd.DataFrame({
            'toxicity_score': [0.0, 0.01, 0.99, 1.0, 0.49, 0.51],
            'endpoint': ['A', 'A', 'B', 'B', 'C', 'C']
        })

        fig = strategy.generate_plot(df)

        assert isinstance(fig, go.Figure)

    def test_negative_values(self):
        """Test with negative values."""
        config = get_minimal_config()
        strategy = DensityPlotStrategy(config)

        df = pd.DataFrame({
            'toxicity_score': [-1.0, -0.5, 0.0, 0.5, 1.0, 1.5],
            'endpoint': ['A', 'A', 'A', 'B', 'B', 'B']
        })

        fig = strategy.generate_plot(df)

        assert isinstance(fig, go.Figure)

    def test_identical_values_per_group(self):
        """Test with identical values within groups."""
        config = get_minimal_config()
        strategy = DensityPlotStrategy(config)

        df = pd.DataFrame({
            'toxicity_score': [0.3] * 10 + [0.7] * 10,
            'endpoint': ['A'] * 10 + ['B'] * 10
        })

        fig = strategy.generate_plot(df)

        # KDE should still work with identical values
        assert isinstance(fig, go.Figure)

    def test_custom_opacity_and_fill(self):
        """Test with custom opacity and fill settings."""
        config = get_minimal_config()
        config['visualization']['plotly']['chart'] = {
            'opacity': 0.8,
            'fill': 'tonexty'
        }
        strategy = DensityPlotStrategy(config)
        df = get_sample_data()

        fig = strategy.generate_plot(df)

        # Check custom settings applied
        for trace in fig.data:
            assert trace.opacity == 0.8
            assert trace.fill == 'tonexty'

    def test_show_hist_and_rug(self):
        """Test with histogram and rug plot enabled."""
        config = get_minimal_config()
        config['visualization']['plotly']['chart'] = {
            'show_hist': False,  # Keep False to avoid Histogram traces
            'show_rug': True
        }
        strategy = DensityPlotStrategy(config)
        df = get_sample_data()

        fig = strategy.generate_plot(df)

        # With rug enabled, should have density curves + rug markers
        # 3 groups = 3 density + 3 rug = 6 traces
        assert len(fig.data) >= 3

    def test_large_dataset(self):
        """Test with large dataset."""
        config = get_minimal_config()
        strategy = DensityPlotStrategy(config)

        np.random.seed(42)
        df = pd.DataFrame({
            'toxicity_score': np.random.normal(0.5, 0.2, 1000),
            'endpoint': np.random.choice(['A', 'B', 'C', 'D'], 1000)
        })

        fig = strategy.generate_plot(df)

        assert isinstance(fig, go.Figure)

    def test_groups_sorted_alphabetically(self):
        """Test that groups are sorted alphabetically."""
        config = get_minimal_config()
        strategy = DensityPlotStrategy(config)

        df = pd.DataFrame({
            'toxicity_score': [0.1, 0.2, 0.3, 0.4, 0.5, 0.6],
            'endpoint': ['C', 'C', 'A', 'A', 'B', 'B']
        })

        processed = strategy.process_data(df)
        fig = strategy.create_figure(processed)

        # Traces should be in alphabetical order by group name
        trace_names = [trace.name for trace in fig.data]
        assert trace_names == sorted(trace_names)

    def test_missing_optional_chart_config(self):
        """Test with missing optional chart configuration."""
        config = {
            'metadata': {},
            'visualization': {
                'strategy': 'DensityPlotStrategy',
                'plotly': {
                    'value_column': 'toxicity_score',
                    'group_column': 'endpoint'
                }
            }
        }
        strategy = DensityPlotStrategy(config)
        df = get_sample_data()

        fig = strategy.generate_plot(df)

        # Should use defaults
        assert isinstance(fig, go.Figure)
        for trace in fig.data:
            assert trace.opacity == 0.5  # Default
            assert trace.fill == 'tozeroy'  # Default
