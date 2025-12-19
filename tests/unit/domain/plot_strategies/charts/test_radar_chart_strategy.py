"""
Unit tests for RadarChartStrategy.

This module tests the RadarChartStrategy class which creates radar/polar
charts for multi-dimensional comparative visualization.

Test Categories
---------------
1. Initialization (5 tests)
2. Validation (8 tests)
3. Data Processing (12 tests)
4. Figure Creation (13 tests)
5. Integration (4 tests)
6. Edge Cases (10 tests)

Total: 52 tests
"""

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import pytest

from src.domain.plot_strategies.charts.radar_chart_strategy import (
    RadarChartStrategy
)


# =======================
# Helper Functions
# =======================


def get_minimal_config():
    """Get minimal configuration for RadarChartStrategy."""
    return {
        'metadata': {
            'use_case_id': 'UC-4.3',
            'module': 'module4'
        },
        'data': {},
        'visualization': {
            'strategy': 'RadarChartStrategy',
            'plotly': {
                'theta_column': 'sample',
                'r_column': 'ko',
                'aggregation': 'nunique',
                'chart': {
                    'title': {
                        'text': 'Sample Comparison',
                        'show': True
                    },
                    'fill': 'toself',
                    'marker_color': 'mediumseagreen'
                },
                'layout': {
                    'height': 600,
                    'width': 800,
                    'template': 'plotly_white',
                    'showlegend': False
                }
            }
        }
    }


def get_pathway_comparison_config():
    """Get configuration for pathway comparison (UC-4.4)."""
    return {
        'metadata': {
            'use_case_id': 'UC-4.4',
            'module': 'module4'
        },
        'data': {},
        'visualization': {
            'strategy': 'RadarChartStrategy',
            'plotly': {
                'theta_column': 'pathname',
                'r_column': 'ko',
                'group_column': 'sample',
                'aggregation': 'nunique',
                'chart': {
                    'title': {
                        'text': 'Pathway Comparison',
                        'show': True
                    }
                },
                'layout': {
                    'height': 600,
                    'template': 'simple_white'
                }
            }
        }
    }


def get_sample_data():
    """
    Get sample data for radar chart testing.

    Returns
    -------
    pd.DataFrame
        Sample-KO data for 3 samples.
    """
    np.random.seed(42)
    return pd.DataFrame({
        'sample': ['A', 'A', 'B', 'B', 'B', 'C', 'C'],
        'ko': ['K00001', 'K00002', 'K00001', 'K00003', 'K00004',
               'K00001', 'K00002']
    })


def get_pathway_data():
    """
    Get pathway data for radar chart testing.

    Returns
    -------
    pd.DataFrame
        Pathway-KO data for 4 pathways.
    """
    np.random.seed(42)
    return pd.DataFrame({
        'pathname': ['Path1', 'Path1', 'Path2', 'Path2', 'Path3',
                     'Path3', 'Path3', 'Path4'],
        'ko': ['K00001', 'K00002', 'K00001', 'K00003', 'K00004',
               'K00005', 'K00006', 'K00001']
    })


def get_large_sample_data():
    """
    Get large sample data.

    Returns
    -------
    pd.DataFrame
        Large dataset with 10 samples and 50 KOs.
    """
    np.random.seed(42)
    n_records = 100
    samples = [f'Sample_{i}' for i in range(10)]
    kos = [f'K{str(j).zfill(5)}' for j in range(50)]

    data = []
    for _ in range(n_records):
        sample = np.random.choice(samples)
        ko = np.random.choice(kos)
        data.append({'sample': sample, 'ko': ko})

    return pd.DataFrame(data)


# =======================
# Test Class
# =======================


class TestRadarChartStrategy:
    """Test suite for RadarChartStrategy."""

    # =======================
    # 1. Initialization Tests
    # =======================

    def test_init_minimal_config(self):
        """Test initialization with minimal configuration."""
        # Arrange & Act
        config = get_minimal_config()
        strategy = RadarChartStrategy(config)

        # Assert
        assert strategy is not None
        assert strategy.data_config is not None
        assert strategy.plotly_config is not None

    def test_init_extracts_data_config(self):
        """Test initialization extracts data config."""
        # Arrange
        config = get_minimal_config()
        config['data'] = {'some_key': 'some_value'}

        # Act
        strategy = RadarChartStrategy(config)

        # Assert
        assert strategy.data_config == {'some_key': 'some_value'}

    def test_init_extracts_plotly_config(self):
        """Test initialization extracts plotly config."""
        # Arrange & Act
        config = get_minimal_config()
        strategy = RadarChartStrategy(config)

        # Assert
        assert 'theta_column' in strategy.plotly_config
        assert 'r_column' in strategy.plotly_config

    def test_init_sample_comparison_config(self):
        """Test initialization with sample comparison config."""
        # Arrange & Act
        config = get_minimal_config()
        strategy = RadarChartStrategy(config)

        # Assert
        assert strategy.plotly_config['theta_column'] == 'sample'
        assert strategy.plotly_config['r_column'] == 'ko'

    def test_init_pathway_comparison_config(self):
        """Test initialization with pathway comparison config."""
        # Arrange & Act
        config = get_pathway_comparison_config()
        strategy = RadarChartStrategy(config)

        # Assert
        assert strategy.plotly_config['theta_column'] == 'pathname'
        assert strategy.plotly_config['r_column'] == 'ko'

    # =======================
    # 2. Validation Tests
    # =======================

    def test_validate_empty_dataframe_fails(self):
        """Test validation fails with empty DataFrame."""
        # Arrange
        config = get_minimal_config()
        strategy = RadarChartStrategy(config)
        df = pd.DataFrame()

        # Act & Assert
        with pytest.raises(ValueError, match="DataFrame is empty"):
            strategy.validate_data(df)

    def test_validate_missing_theta_column(self):
        """Test validation fails when theta column is missing."""
        # Arrange
        config = get_minimal_config()
        strategy = RadarChartStrategy(config)
        df = pd.DataFrame({'ko': ['K00001']})

        # Act & Assert
        with pytest.raises(ValueError, match="Missing required columns"):
            strategy.validate_data(df)

    def test_validate_missing_r_column(self):
        """Test validation fails when r column is missing."""
        # Arrange
        config = get_minimal_config()
        strategy = RadarChartStrategy(config)
        df = pd.DataFrame({'sample': ['A']})

        # Act & Assert
        with pytest.raises(ValueError, match="Missing required columns"):
            strategy.validate_data(df)

    def test_validate_no_theta_config(self):
        """Test validation fails when theta_column not in config."""
        # Arrange
        config = get_minimal_config()
        del config['visualization']['plotly']['theta_column']
        strategy = RadarChartStrategy(config)
        df = get_sample_data()

        # Act & Assert
        with pytest.raises(ValueError, match="must be specified"):
            strategy.validate_data(df)

    def test_validate_no_r_config(self):
        """Test validation fails when r_column not in config."""
        # Arrange
        config = get_minimal_config()
        del config['visualization']['plotly']['r_column']
        strategy = RadarChartStrategy(config)
        df = get_sample_data()

        # Act & Assert
        with pytest.raises(ValueError, match="must be specified"):
            strategy.validate_data(df)

    def test_validate_sample_data_passes(self):
        """Test validation passes with valid sample data."""
        # Arrange
        config = get_minimal_config()
        strategy = RadarChartStrategy(config)
        df = get_sample_data()

        # Act & Assert (should not raise)
        strategy.validate_data(df)

    def test_validate_pathway_data_passes(self):
        """Test validation passes with valid pathway data."""
        # Arrange
        config = get_pathway_comparison_config()
        strategy = RadarChartStrategy(config)
        df = get_pathway_data()

        # Act & Assert (should not raise)
        strategy.validate_data(df)

    def test_validate_large_dataset(self):
        """Test validation passes with large dataset."""
        # Arrange
        config = get_minimal_config()
        strategy = RadarChartStrategy(config)
        df = get_large_sample_data()

        # Act & Assert (should not raise)
        strategy.validate_data(df)

    # =======================
    # 3. Data Processing Tests
    # =======================

    def test_process_data_creates_theta_r_columns(self):
        """Test process_data creates theta and r columns."""
        # Arrange
        config = get_minimal_config()
        strategy = RadarChartStrategy(config)
        df = get_sample_data()

        # Act
        result = strategy.process_data(df)

        # Assert
        assert 'theta' in result.columns
        assert 'r' in result.columns

    def test_process_data_nunique_aggregation(self):
        """Test process_data with nunique aggregation."""
        # Arrange
        config = get_minimal_config()
        strategy = RadarChartStrategy(config)
        df = get_sample_data()

        # Act
        result = strategy.process_data(df)

        # Assert
        # Sample A: 2 unique KOs, B: 3 unique KOs, C: 2 unique KOs
        assert result[result['theta'] == 'A']['r'].values[0] == 2
        assert result[result['theta'] == 'B']['r'].values[0] == 3
        assert result[result['theta'] == 'C']['r'].values[0] == 2

    def test_process_data_count_aggregation(self):
        """Test process_data with count aggregation."""
        # Arrange
        config = get_minimal_config()
        config['visualization']['plotly']['aggregation'] = 'count'
        strategy = RadarChartStrategy(config)
        df = get_sample_data()

        # Act
        result = strategy.process_data(df)

        # Assert
        # Sample A: 2 records, B: 3 records, C: 2 records
        assert result[result['theta'] == 'A']['r'].values[0] == 2
        assert result[result['theta'] == 'B']['r'].values[0] == 3
        assert result[result['theta'] == 'C']['r'].values[0] == 2

    def test_process_data_sum_aggregation(self):
        """Test process_data with sum aggregation."""
        # Arrange
        config = get_minimal_config()
        config['visualization']['plotly']['aggregation'] = 'sum'
        strategy = RadarChartStrategy(config)
        df = pd.DataFrame({
            'sample': ['A', 'A', 'B', 'B'],
            'value': [10, 20, 15, 25]
        })
        config['visualization']['plotly']['r_column'] = 'value'

        # Act
        result = strategy.process_data(df)

        # Assert
        assert result[result['theta'] == 'A']['r'].values[0] == 30
        assert result[result['theta'] == 'B']['r'].values[0] == 40

    def test_process_data_mean_aggregation(self):
        """Test process_data with mean aggregation."""
        # Arrange
        config = get_minimal_config()
        config['visualization']['plotly']['aggregation'] = 'mean'
        strategy = RadarChartStrategy(config)
        df = pd.DataFrame({
            'sample': ['A', 'A', 'B', 'B'],
            'value': [10, 20, 15, 25]
        })
        config['visualization']['plotly']['r_column'] = 'value'

        # Act
        result = strategy.process_data(df)

        # Assert
        assert result[result['theta'] == 'A']['r'].values[0] == 15.0
        assert result[result['theta'] == 'B']['r'].values[0] == 20.0

    def test_process_data_unknown_aggregation_defaults_nunique(self):
        """Test process_data defaults to nunique for unknown aggregation."""
        # Arrange
        config = get_minimal_config()
        config['visualization']['plotly']['aggregation'] = 'invalid'
        strategy = RadarChartStrategy(config)
        df = get_sample_data()

        # Act
        result = strategy.process_data(df)

        # Assert
        # Should default to nunique
        assert result[result['theta'] == 'A']['r'].values[0] == 2

    def test_process_data_pathway_comparison(self):
        """Test process_data with pathway data."""
        # Arrange
        config = get_pathway_comparison_config()
        strategy = RadarChartStrategy(config)
        df = get_pathway_data()

        # Act
        result = strategy.process_data(df)

        # Assert
        # Path1: 2 unique KOs, Path2: 2, Path3: 3, Path4: 1
        assert len(result) == 4
        assert result[result['theta'] == 'Path1']['r'].values[0] == 2
        assert result[result['theta'] == 'Path3']['r'].values[0] == 3

    def test_process_data_correct_shape(self):
        """Test process_data returns correct shape."""
        # Arrange
        config = get_minimal_config()
        strategy = RadarChartStrategy(config)
        df = get_sample_data()

        # Act
        result = strategy.process_data(df)

        # Assert
        # 3 unique samples
        assert result.shape[0] == 3
        assert result.shape[1] == 2  # theta, r

    def test_process_data_preserves_all_categories(self):
        """Test process_data includes all categories."""
        # Arrange
        config = get_minimal_config()
        strategy = RadarChartStrategy(config)
        df = get_sample_data()

        # Act
        result = strategy.process_data(df)

        # Assert
        assert 'A' in result['theta'].values
        assert 'B' in result['theta'].values
        assert 'C' in result['theta'].values

    def test_process_data_r_values_numeric(self):
        """Test process_data r values are numeric."""
        # Arrange
        config = get_minimal_config()
        strategy = RadarChartStrategy(config)
        df = get_sample_data()

        # Act
        result = strategy.process_data(df)

        # Assert
        assert pd.api.types.is_numeric_dtype(result['r'])

    def test_process_data_large_dataset(self):
        """Test process_data with large dataset."""
        # Arrange
        config = get_minimal_config()
        strategy = RadarChartStrategy(config)
        df = get_large_sample_data()

        # Act
        result = strategy.process_data(df)

        # Assert
        # 10 unique samples
        assert result.shape[0] == 10
        assert 'theta' in result.columns
        assert 'r' in result.columns

    def test_process_data_default_aggregation(self):
        """Test process_data uses nunique as default aggregation."""
        # Arrange
        config = get_minimal_config()
        del config['visualization']['plotly']['aggregation']
        strategy = RadarChartStrategy(config)
        df = get_sample_data()

        # Act
        result = strategy.process_data(df)

        # Assert
        # Should use nunique by default
        assert result[result['theta'] == 'A']['r'].values[0] == 2

    # =======================
    # 4. Figure Creation Tests
    # =======================

    def test_create_figure_returns_figure(self):
        """Test create_figure returns Plotly Figure."""
        # Arrange
        config = get_minimal_config()
        strategy = RadarChartStrategy(config)
        df = get_sample_data()
        processed = strategy.process_data(df)

        # Act
        fig = strategy.create_figure(processed)

        # Assert
        assert isinstance(fig, go.Figure)

    def test_create_figure_has_scatterpolar_trace(self):
        """Test figure has Scatterpolar trace."""
        # Arrange
        config = get_minimal_config()
        strategy = RadarChartStrategy(config)
        df = get_sample_data()
        processed = strategy.process_data(df)

        # Act
        fig = strategy.create_figure(processed)

        # Assert
        assert len(fig.data) > 0
        assert isinstance(fig.data[0], go.Scatterpolar)

    def test_create_figure_title(self):
        """Test figure has correct title."""
        # Arrange
        config = get_minimal_config()
        strategy = RadarChartStrategy(config)
        df = get_sample_data()
        processed = strategy.process_data(df)

        # Act
        fig = strategy.create_figure(processed)

        # Assert
        assert fig.layout.title is not None
        assert 'Sample Comparison' in fig.layout.title.text

    def test_create_figure_radial_axis_auto_range(self):
        """Test radial axis has auto-calculated range."""
        # Arrange
        config = get_minimal_config()
        strategy = RadarChartStrategy(config)
        df = get_sample_data()
        processed = strategy.process_data(df)

        # Act
        fig = strategy.create_figure(processed)

        # Assert
        # Max value is 3, range should be [0, 3.3] (10% padding)
        assert fig.layout.polar.radialaxis.range[0] == 0
        assert fig.layout.polar.radialaxis.range[1] >= 3
        assert fig.layout.polar.radialaxis.range[1] <= 3.5

    def test_create_figure_fill_toself(self):
        """Test figure uses fill='toself'."""
        # Arrange
        config = get_minimal_config()
        strategy = RadarChartStrategy(config)
        df = get_sample_data()
        processed = strategy.process_data(df)

        # Act
        fig = strategy.create_figure(processed)

        # Assert
        assert fig.data[0].fill == 'toself'

    def test_create_figure_custom_colors(self):
        """Test figure uses custom colors."""
        # Arrange
        config = get_minimal_config()
        config['visualization']['plotly']['chart']['marker_color'] = 'red'
        config['visualization']['plotly']['chart']['line_color'] = 'blue'
        strategy = RadarChartStrategy(config)
        df = get_sample_data()
        processed = strategy.process_data(df)

        # Act
        fig = strategy.create_figure(processed)

        # Assert
        # Scatterpolar uses marker.color instead of marker_color
        assert fig.data[0].marker.color == 'red'
        assert fig.data[0].line.color == 'blue'

    def test_create_figure_layout_height_width(self):
        """Test figure applies layout height and width."""
        # Arrange
        config = get_minimal_config()
        strategy = RadarChartStrategy(config)
        df = get_sample_data()
        processed = strategy.process_data(df)

        # Act
        fig = strategy.create_figure(processed)

        # Assert
        assert fig.layout.height == 600
        assert fig.layout.width == 800

    def test_create_figure_template(self):
        """Test figure applies template."""
        # Arrange
        config = get_minimal_config()
        strategy = RadarChartStrategy(config)
        df = get_sample_data()
        processed = strategy.process_data(df)

        # Act
        fig = strategy.create_figure(processed)

        # Assert
        assert fig.layout.template.layout is not None

    def test_create_figure_showlegend(self):
        """Test figure respects showlegend setting."""
        # Arrange
        config = get_minimal_config()
        strategy = RadarChartStrategy(config)
        df = get_sample_data()
        processed = strategy.process_data(df)

        # Act
        fig = strategy.create_figure(processed)

        # Assert
        assert fig.layout.showlegend == False

    def test_create_figure_title_hide(self):
        """Test figure with title hidden."""
        # Arrange
        config = get_minimal_config()
        config['visualization']['plotly']['chart']['title']['show'] = False
        strategy = RadarChartStrategy(config)
        df = get_sample_data()
        processed = strategy.process_data(df)

        # Act
        fig = strategy.create_figure(processed)

        # Assert
        # When show=False, title should be empty or not set
        if hasattr(fig.layout, 'title'):
            assert fig.layout.title.text == '' or fig.layout.title.text is None

    def test_create_figure_autosize(self):
        """Test figure with autosize enabled."""
        # Arrange
        config = get_minimal_config()
        config['visualization']['plotly']['layout']['autosize'] = True
        strategy = RadarChartStrategy(config)
        df = get_sample_data()
        processed = strategy.process_data(df)

        # Act
        fig = strategy.create_figure(processed)

        # Assert
        assert fig.layout.autosize == True

    def test_create_figure_custom_fillcolor(self):
        """Test figure with custom fillcolor."""
        # Arrange
        config = get_minimal_config()
        config['visualization']['plotly']['chart']['fillcolor'] = \
            'rgba(255,0,0,0.5)'
        strategy = RadarChartStrategy(config)
        df = get_sample_data()
        processed = strategy.process_data(df)

        # Act
        fig = strategy.create_figure(processed)

        # Assert
        assert fig.data[0].fillcolor == 'rgba(255,0,0,0.5)'

    def test_create_figure_trace_name(self):
        """Test figure trace has custom name."""
        # Arrange
        config = get_minimal_config()
        config['visualization']['plotly']['chart']['name'] = 'Custom Name'
        strategy = RadarChartStrategy(config)
        df = get_sample_data()
        processed = strategy.process_data(df)

        # Act
        fig = strategy.create_figure(processed)

        # Assert
        assert fig.data[0].name == 'Custom Name'

    # =======================
    # 5. Integration Tests
    # =======================

    def test_generate_plot_full_workflow(self):
        """Test complete workflow: validate -> process -> create."""
        # Arrange
        config = get_minimal_config()
        strategy = RadarChartStrategy(config)
        df = get_sample_data()

        # Act
        fig = strategy.generate_plot(df)

        # Assert
        assert isinstance(fig, go.Figure)

    def test_generate_plot_pathway_comparison(self):
        """Test workflow with pathway comparison data."""
        # Arrange
        config = get_pathway_comparison_config()
        strategy = RadarChartStrategy(config)
        df = get_pathway_data()

        # Act
        fig = strategy.generate_plot(df)

        # Assert
        assert isinstance(fig, go.Figure)

    def test_generate_plot_large_dataset(self):
        """Test workflow with large dataset."""
        # Arrange
        config = get_minimal_config()
        strategy = RadarChartStrategy(config)
        df = get_large_sample_data()

        # Act
        fig = strategy.generate_plot(df)

        # Assert
        assert isinstance(fig, go.Figure)

    def test_generate_plot_with_nulls(self):
        """Test workflow handles null values correctly."""
        # Arrange
        config = get_minimal_config()
        strategy = RadarChartStrategy(config)
        df = pd.DataFrame({
            'sample': ['A', 'A', None, 'B', 'B'],
            'ko': ['K00001', None, 'K00002', 'K00003', 'K00004']
        })

        # Act
        # Nulls will be handled by groupby (excluded)
        fig = strategy.generate_plot(df)

        # Assert
        assert isinstance(fig, go.Figure)

    # =======================
    # 6. Edge Cases
    # =======================

    def test_edge_case_single_category(self):
        """Test radar chart with single category."""
        # Arrange
        config = get_minimal_config()
        strategy = RadarChartStrategy(config)
        df = pd.DataFrame({
            'sample': ['A', 'A', 'A'],
            'ko': ['K00001', 'K00002', 'K00003']
        })

        # Act
        fig = strategy.generate_plot(df)

        # Assert
        assert isinstance(fig, go.Figure)

    def test_edge_case_many_categories(self):
        """Test radar chart with many categories."""
        # Arrange
        config = get_minimal_config()
        strategy = RadarChartStrategy(config)
        samples = [f'S{i}' for i in range(20)]
        df = pd.DataFrame({
            'sample': samples,
            'ko': [f'K{str(i).zfill(5)}' for i in range(20)]
        })

        # Act
        fig = strategy.generate_plot(df)

        # Assert
        assert isinstance(fig, go.Figure)

    def test_edge_case_zero_values(self):
        """Test radar chart with zero aggregated values."""
        # Arrange
        config = get_minimal_config()
        config['visualization']['plotly']['aggregation'] = 'sum'
        strategy = RadarChartStrategy(config)
        df = pd.DataFrame({
            'sample': ['A', 'B', 'C'],
            'value': [0, 0, 0]
        })
        config['visualization']['plotly']['r_column'] = 'value'

        # Act
        fig = strategy.generate_plot(df)

        # Assert
        # Radial range should still be valid
        assert fig.layout.polar.radialaxis.range[0] == 0
        assert fig.layout.polar.radialaxis.range[1] >= 1

    def test_edge_case_large_values(self):
        """Test radar chart with large aggregated values."""
        # Arrange
        config = get_minimal_config()
        config['visualization']['plotly']['aggregation'] = 'sum'
        strategy = RadarChartStrategy(config)
        df = pd.DataFrame({
            'sample': ['A', 'B', 'C'],
            'value': [1000, 2000, 3000]
        })
        config['visualization']['plotly']['r_column'] = 'value'

        # Act
        fig = strategy.generate_plot(df)

        # Assert
        # Range should accommodate large values
        assert fig.layout.polar.radialaxis.range[1] > 3000

    def test_edge_case_special_characters_in_names(self):
        """Test radar chart with special characters in category names."""
        # Arrange
        config = get_minimal_config()
        strategy = RadarChartStrategy(config)
        df = pd.DataFrame({
            'sample': ['S@1', 'S#2', 'S$3'],
            'ko': ['K00001', 'K00002', 'K00003']
        })

        # Act
        fig = strategy.generate_plot(df)

        # Assert
        assert isinstance(fig, go.Figure)

    def test_edge_case_very_long_names(self):
        """Test radar chart with very long category names."""
        # Arrange
        config = get_minimal_config()
        strategy = RadarChartStrategy(config)
        long_name = 'Sample_' + 'A' * 100
        df = pd.DataFrame({
            'sample': [long_name, 'B', 'C'],
            'ko': ['K00001', 'K00002', 'K00003']
        })

        # Act
        fig = strategy.generate_plot(df)

        # Assert
        assert isinstance(fig, go.Figure)

    def test_edge_case_numeric_category_names(self):
        """Test radar chart with numeric category names."""
        # Arrange
        config = get_minimal_config()
        strategy = RadarChartStrategy(config)
        df = pd.DataFrame({
            'sample': [1, 2, 3],
            'ko': ['K00001', 'K00002', 'K00003']
        })

        # Act
        fig = strategy.generate_plot(df)

        # Assert
        assert isinstance(fig, go.Figure)

    def test_edge_case_string_title_backward_compatibility(self):
        """Test radar chart with string title (backward compatibility)."""
        # Arrange
        config = get_minimal_config()
        config['visualization']['plotly']['chart']['title'] = 'Simple Title'
        strategy = RadarChartStrategy(config)
        df = get_sample_data()

        # Act
        fig = strategy.generate_plot(df)

        # Assert
        assert 'Simple Title' in fig.layout.title.text

    def test_edge_case_custom_radial_range(self):
        """Test radar chart with custom radial range."""
        # Arrange
        config = get_minimal_config()
        config['visualization']['plotly']['layout']['polar'] = {
            'radialaxis': {'range': [0, 10]}
        }
        strategy = RadarChartStrategy(config)
        df = get_sample_data()

        # Act
        fig = strategy.generate_plot(df)

        # Assert
        # Plotly returns tuple instead of list
        assert fig.layout.polar.radialaxis.range[0] == 0
        assert fig.layout.polar.radialaxis.range[1] == 10

    def test_edge_case_fill_none(self):
        """Test radar chart with no fill."""
        # Arrange
        config = get_minimal_config()
        config['visualization']['plotly']['chart']['fill'] = 'none'
        strategy = RadarChartStrategy(config)
        df = get_sample_data()

        # Act
        fig = strategy.generate_plot(df)

        # Assert
        assert fig.data[0].fill == 'none'
