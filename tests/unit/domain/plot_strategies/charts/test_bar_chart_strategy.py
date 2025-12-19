"""
Unit tests for BarChartStrategy.

This module tests the BarChartStrategy concrete implementation,
which generates bar chart visualizations with flexible configuration.

Test Categories:
- Initialization: Test strategy setup with config
- Data Validation: Test validate_data() with various validation rules
- Data Processing: Test process_data() pipeline (filter, group, count, sort)
- Figure Creation: Test create_figure() with Plotly
- Integration: Test complete generate_plot() workflow
- Edge Cases: Test boundary conditions
"""

import pytest
import pandas as pd
import plotly.graph_objects as go
from unittest.mock import Mock, patch

from src.domain.plot_strategies.charts.bar_chart_strategy import BarChartStrategy


# ============================================================================
# TEST CONFIGURATIONS
# ============================================================================

def get_minimal_config():
    """Get minimal valid configuration."""
    return {
        'metadata': {
            'use_case_id': 'UC-2.1',
            'module': 'module2'
        },
        'visualization': {
            'strategy': 'BarChartStrategy',
            'plotly': {
                'x': 'sample',
                'y': 'ko_count',
                'orientation': 'v'
            }
        },
        'data': {
            'processing': {
                'steps': []
            }
        },
        'validation': {
            'rules': []
        }
    }


def get_full_config():
    """Get complete configuration with all features."""
    return {
        'metadata': {
            'use_case_id': 'UC-2.1',
            'module': 'module2',
            'title': 'KO Count by Sample'
        },
        'visualization': {
            'strategy': 'BarChartStrategy',
            'plotly': {
                'x': 'sample',
                'y': 'ko_count',
                'orientation': 'v',
                'labels': {
                    'sample': 'Sample ID',
                    'ko_count': 'Number of KOs'
                },
                'color_discrete_sequence': ['#4682B4'],
                'title': {
                    'text': 'KO Count by Sample',
                    'x': 0.5,
                    'xanchor': 'center',
                    'font': {'size': 16}
                },
                'layout': {
                    'height': 500,
                    'width': 800,
                    'template': 'simple_white',
                    'xaxis': {'title': 'Sample'},
                    'yaxis': {'title': 'KO Count'},
                    'hovermode': 'closest',
                    'margin': {'l': 50, 'r': 50, 't': 80, 'b': 50}
                }
            }
        },
        'data': {
            'processing': {
                'steps': [
                    {
                        'name': 'group_and_count',
                        'enabled': True,
                        'params': {
                            'group_by': 'sample',
                            'agg_column': 'KO',
                            'agg_function': 'nunique',
                            'result_column': 'ko_count'
                        }
                    },
                    {
                        'name': 'sort',
                        'enabled': True,
                        'params': {
                            'by': 'ko_count',
                            'ascending': False
                        }
                    }
                ]
            }
        },
        'validation': {
            'rules': [
                {
                    'rule': 'not_empty',
                    'message': 'DataFrame cannot be empty'
                },
                {
                    'rule': 'required_columns',
                    'columns': ['sample', 'KO'],
                    'message': 'Missing required columns'
                }
            ]
        }
    }


# ============================================================================
# INITIALIZATION TESTS
# ============================================================================

class TestBarChartStrategyInitialization:
    """Test BarChartStrategy initialization."""

    def test_initialization_with_minimal_config(self):
        """Test initialization with minimal config."""
        config = get_minimal_config()
        strategy = BarChartStrategy(config)

        assert strategy.config == config
        assert strategy.metadata == config['metadata']
        assert strategy.viz_config == config['visualization']
        assert strategy.data_config == config['data']
        assert strategy.validation_rules == config['validation']
        assert strategy.plotly_config == config['visualization']['plotly']

    def test_initialization_with_full_config(self):
        """Test initialization with complete config."""
        config = get_full_config()
        strategy = BarChartStrategy(config)

        assert strategy.metadata['use_case_id'] == 'UC-2.1'
        assert strategy.plotly_config['x'] == 'sample'
        assert strategy.plotly_config['y'] == 'ko_count'
        assert len(strategy.data_config['processing']['steps']) == 2

    def test_initialization_extracts_plotly_config(self):
        """Test that plotly config is extracted correctly."""
        config = get_full_config()
        strategy = BarChartStrategy(config)

        assert strategy.plotly_config['orientation'] == 'v'
        assert 'labels' in strategy.plotly_config
        assert 'title' in strategy.plotly_config

    def test_initialization_with_empty_data_config(self):
        """Test initialization when data config is empty."""
        config = {
            'metadata': {},
            'visualization': {'plotly': {}},
            'data': {},
            'validation': {}
        }
        strategy = BarChartStrategy(config)

        assert strategy.data_config == {}
        assert strategy.plotly_config == {}


# ============================================================================
# DATA VALIDATION TESTS
# ============================================================================

class TestDataValidation:
    """Test validate_data() method."""

    def test_validate_empty_rules_passes(self):
        """Test validation passes with no rules."""
        config = get_minimal_config()
        strategy = BarChartStrategy(config)

        df = pd.DataFrame({'sample': ['S1'], 'KO': ['K00001']})
        strategy.validate_data(df)  # Should not raise

    def test_validate_not_empty_rule_with_data(self):
        """Test not_empty rule passes with data."""
        config = {
            **get_minimal_config(),
            'validation': {
                'rules': [
                    {'rule': 'not_empty', 'message': 'Empty DataFrame'}
                ]
            }
        }
        strategy = BarChartStrategy(config)

        df = pd.DataFrame({'sample': ['S1'], 'KO': ['K00001']})
        strategy.validate_data(df)  # Should not raise

    def test_validate_not_empty_rule_fails_with_empty_df(self):
        """Test not_empty rule fails with empty DataFrame."""
        config = {
            **get_minimal_config(),
            'validation': {
                'rules': [
                    {'rule': 'not_empty', 'message': 'Empty DataFrame'}
                ]
            }
        }
        strategy = BarChartStrategy(config)

        df = pd.DataFrame()

        with pytest.raises(ValueError, match="Empty DataFrame"):
            strategy.validate_data(df)

    def test_validate_required_columns_passes(self):
        """Test required_columns rule passes when columns exist."""
        config = {
            **get_minimal_config(),
            'validation': {
                'rules': [
                    {
                        'rule': 'required_columns',
                        'columns': ['sample', 'KO'],
                        'message': 'Missing columns'
                    }
                ]
            }
        }
        strategy = BarChartStrategy(config)

        df = pd.DataFrame({'sample': ['S1'], 'KO': ['K00001']})
        strategy.validate_data(df)  # Should not raise

    def test_validate_required_columns_fails_when_missing(self):
        """Test required_columns rule fails when columns missing."""
        config = {
            **get_minimal_config(),
            'validation': {
                'rules': [
                    {
                        'rule': 'required_columns',
                        'columns': ['sample', 'KO'],
                        'message': 'Missing columns'
                    }
                ]
            }
        }
        strategy = BarChartStrategy(config)

        df = pd.DataFrame({'sample': ['S1']})  # Missing 'KO'

        with pytest.raises(ValueError, match="Missing columns"):
            strategy.validate_data(df)

    def test_validate_no_nulls_passes(self):
        """Test no_nulls rule passes when no null values."""
        config = {
            **get_minimal_config(),
            'validation': {
                'rules': [
                    {
                        'rule': 'no_nulls',
                        'columns': ['sample', 'KO'],
                        'message': 'Null values found'
                    }
                ]
            }
        }
        strategy = BarChartStrategy(config)

        df = pd.DataFrame({
            'sample': ['S1', 'S2'],
            'KO': ['K00001', 'K00002']
        })
        strategy.validate_data(df)  # Should not raise

    def test_validate_no_nulls_fails_with_nulls(self):
        """Test no_nulls rule fails when null values present."""
        config = {
            **get_minimal_config(),
            'validation': {
                'rules': [
                    {
                        'rule': 'no_nulls',
                        'columns': ['sample', 'KO'],
                        'message': 'Null values found'
                    }
                ]
            }
        }
        strategy = BarChartStrategy(config)

        df = pd.DataFrame({
            'sample': ['S1', None],
            'KO': ['K00001', 'K00002']
        })

        with pytest.raises(ValueError, match="Null values found"):
            strategy.validate_data(df)

    def test_validate_minimum_samples_passes(self):
        """Test minimum_samples rule passes when enough samples."""
        config = {
            **get_minimal_config(),
            'validation': {
                'rules': [
                    {
                        'rule': 'minimum_samples',
                        'min_count': 2,
                        'message': 'Insufficient samples'
                    }
                ]
            }
        }
        strategy = BarChartStrategy(config)

        df = pd.DataFrame({
            'sample': ['S1', 'S2'],
            'KO': ['K00001', 'K00002']
        })
        strategy.validate_data(df)  # Should not raise

    def test_validate_minimum_samples_fails(self):
        """Test minimum_samples rule fails when insufficient samples."""
        config = {
            **get_minimal_config(),
            'validation': {
                'rules': [
                    {
                        'rule': 'minimum_samples',
                        'min_count': 5,
                        'message': 'Insufficient samples'
                    }
                ]
            }
        }
        strategy = BarChartStrategy(config)

        df = pd.DataFrame({'sample': ['S1'], 'KO': ['K00001']})

        with pytest.raises(ValueError, match="Insufficient samples"):
            strategy.validate_data(df)

    def test_validate_multiple_rules(self):
        """Test validation with multiple rules."""
        config = get_full_config()
        strategy = BarChartStrategy(config)

        df = pd.DataFrame({
            'sample': ['S1', 'S2'],
            'KO': ['K00001', 'K00002']
        })
        strategy.validate_data(df)  # Should pass all rules


# ============================================================================
# DATA PROCESSING TESTS
# ============================================================================

class TestDataProcessing:
    """Test process_data() method."""

    def test_process_data_with_no_steps(self):
        """Test processing with no steps returns copy."""
        config = get_minimal_config()
        strategy = BarChartStrategy(config)

        df = pd.DataFrame({'sample': ['S1', 'S2'], 'KO': ['K00001', 'K00002']})
        result = strategy.process_data(df)

        assert len(result) == 2
        assert result is not df  # Should be a copy

    def test_process_data_group_and_count(self):
        """Test group_and_count step."""
        config = {
            **get_minimal_config(),
            'data': {
                'processing': {
                    'steps': [
                        {
                            'name': 'group_and_count',
                            'enabled': True,
                            'params': {
                                'group_by': 'sample',
                                'agg_column': 'KO',
                                'agg_function': 'nunique',
                                'result_column': 'ko_count'
                            }
                        }
                    ]
                }
            }
        }
        strategy = BarChartStrategy(config)

        df = pd.DataFrame({
            'sample': ['S1', 'S1', 'S2', 'S2'],
            'KO': ['K00001', 'K00002', 'K00001', 'K00003']
        })

        result = strategy.process_data(df)

        assert len(result) == 2  # 2 unique samples
        assert 'ko_count' in result.columns
        assert result[result['sample'] == 'S1']['ko_count'].values[0] == 2
        assert result[result['sample'] == 'S2']['ko_count'].values[0] == 2

    def test_process_data_sort_descending(self):
        """Test sort step in descending order."""
        config = {
            **get_minimal_config(),
            'data': {
                'processing': {
                    'steps': [
                        {
                            'name': 'group_and_count',
                            'enabled': True,
                            'params': {
                                'group_by': 'sample',
                                'agg_column': 'KO',
                                'agg_function': 'nunique',
                                'result_column': 'ko_count'
                            }
                        },
                        {
                            'name': 'sort',
                            'enabled': True,
                            'params': {
                                'by': 'ko_count',
                                'ascending': False
                            }
                        }
                    ]
                }
            }
        }
        strategy = BarChartStrategy(config)

        df = pd.DataFrame({
            'sample': ['S1', 'S1', 'S2', 'S2', 'S2'],
            'KO': ['K00001', 'K00002', 'K00001', 'K00002', 'K00003']
        })

        result = strategy.process_data(df)

        # S2 should be first (3 KOs), S1 second (2 KOs)
        assert result.iloc[0]['sample'] == 'S2'
        assert result.iloc[1]['sample'] == 'S1'

    def test_process_data_filter_not_equal(self):
        """Test filter step with != operator."""
        config = {
            **get_minimal_config(),
            'data': {
                'processing': {
                    'steps': [
                        {
                            'name': 'filter',
                            'enabled': True,
                            'params': {
                                'column': 'sample',
                                'operator': '!=',
                                'value': 'S1'
                            }
                        }
                    ]
                }
            }
        }
        strategy = BarChartStrategy(config)

        df = pd.DataFrame({
            'sample': ['S1', 'S2', 'S3'],
            'KO': ['K00001', 'K00002', 'K00003']
        })

        result = strategy.process_data(df)

        assert len(result) == 2  # S1 filtered out
        assert 'S1' not in result['sample'].values

    def test_process_data_filter_equal(self):
        """Test filter step with == operator."""
        config = {
            **get_minimal_config(),
            'data': {
                'processing': {
                    'steps': [
                        {
                            'name': 'filter',
                            'enabled': True,
                            'params': {
                                'column': 'sample',
                                'operator': '==',
                                'value': 'S1'
                            }
                        }
                    ]
                }
            }
        }
        strategy = BarChartStrategy(config)

        df = pd.DataFrame({
            'sample': ['S1', 'S2', 'S3'],
            'KO': ['K00001', 'K00002', 'K00003']
        })

        result = strategy.process_data(df)

        assert len(result) == 1
        assert result['sample'].values[0] == 'S1'

    def test_process_data_filter_in_operator(self):
        """Test filter step with 'in' operator."""
        config = {
            **get_minimal_config(),
            'data': {
                'processing': {
                    'steps': [
                        {
                            'name': 'filter',
                            'enabled': True,
                            'params': {
                                'column': 'sample',
                                'operator': 'in',
                                'value': ['S1', 'S3']
                            }
                        }
                    ]
                }
            }
        }
        strategy = BarChartStrategy(config)

        df = pd.DataFrame({
            'sample': ['S1', 'S2', 'S3'],
            'KO': ['K00001', 'K00002', 'K00003']
        })

        result = strategy.process_data(df)

        assert len(result) == 2
        assert 'S2' not in result['sample'].values

    def test_process_data_disabled_step_skipped(self):
        """Test that disabled steps are skipped."""
        config = {
            **get_minimal_config(),
            'data': {
                'processing': {
                    'steps': [
                        {
                            'name': 'filter',
                            'enabled': False,  # Disabled
                            'params': {
                                'column': 'sample',
                                'operator': '==',
                                'value': 'S1'
                            }
                        }
                    ]
                }
            }
        }
        strategy = BarChartStrategy(config)

        df = pd.DataFrame({
            'sample': ['S1', 'S2'],
            'KO': ['K00001', 'K00002']
        })

        result = strategy.process_data(df)

        # Filter was disabled, so both rows should remain
        assert len(result) == 2


# ============================================================================
# FIGURE CREATION TESTS
# ============================================================================

class TestFigureCreation:
    """Test create_figure() method."""

    def test_create_figure_returns_figure(self):
        """Test that create_figure returns a Plotly Figure."""
        config = get_full_config()
        strategy = BarChartStrategy(config)

        df = pd.DataFrame({
            'sample': ['S1', 'S2'],
            'ko_count': [10, 20]
        })

        fig = strategy.create_figure(df)

        assert isinstance(fig, go.Figure)

    def test_create_figure_vertical_orientation(self):
        """Test creating vertical bar chart."""
        config = {
            **get_minimal_config(),
            'visualization': {
                'plotly': {
                    'x': 'sample',
                    'y': 'ko_count',
                    'orientation': 'v',
                    'labels': {}
                }
            }
        }
        strategy = BarChartStrategy(config)

        df = pd.DataFrame({
            'sample': ['S1', 'S2'],
            'ko_count': [10, 20]
        })

        fig = strategy.create_figure(df)

        assert fig.data[0].type == 'bar'
        assert fig.data[0].orientation == 'v'

    def test_create_figure_horizontal_orientation(self):
        """Test creating horizontal bar chart."""
        config = {
            **get_minimal_config(),
            'visualization': {
                'plotly': {
                    'x': 'ko_count',
                    'y': 'sample',
                    'orientation': 'h',
                    'labels': {}
                }
            }
        }
        strategy = BarChartStrategy(config)

        df = pd.DataFrame({
            'sample': ['S1', 'S2'],
            'ko_count': [10, 20]
        })

        fig = strategy.create_figure(df)

        assert fig.data[0].orientation == 'h'

    def test_create_figure_applies_layout(self):
        """Test that layout configuration is applied."""
        config = get_full_config()
        strategy = BarChartStrategy(config)

        df = pd.DataFrame({
            'sample': ['S1'],
            'ko_count': [10]
        })

        fig = strategy.create_figure(df)

        assert fig.layout.height == 500
        assert fig.layout.width == 800
        assert fig.layout.template.layout.plot_bgcolor is not None

    def test_create_figure_with_title(self):
        """Test figure with title."""
        config = get_full_config()
        strategy = BarChartStrategy(config)

        df = pd.DataFrame({
            'sample': ['S1'],
            'ko_count': [10]
        })

        fig = strategy.create_figure(df)

        assert fig.layout.title.text == 'KO Count by Sample'

    def test_create_figure_without_title(self):
        """Test figure without title (show=False)."""
        config = {
            **get_full_config(),
            'visualization': {
                **get_full_config()['visualization'],
                'plotly': {
                    **get_full_config()['visualization']['plotly'],
                    'title': {
                        'show': False,
                        'text': 'Should not appear'
                    }
                }
            }
        }
        strategy = BarChartStrategy(config)

        df = pd.DataFrame({
            'sample': ['S1'],
            'ko_count': [10]
        })

        fig = strategy.create_figure(df)

        # Title should not be set
        assert fig.layout.title.text is None or fig.layout.title.text == ''


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

class TestIntegration:
    """Test complete generate_plot() workflow."""

    def test_generate_plot_complete_workflow(self):
        """Test full pipeline from input to figure."""
        config = get_full_config()
        strategy = BarChartStrategy(config)

        df = pd.DataFrame({
            'sample': ['S1', 'S1', 'S2', 'S2', 'S2'],
            'KO': ['K00001', 'K00002', 'K00001', 'K00002', 'K00003']
        })

        fig = strategy.generate_plot(df)

        assert isinstance(fig, go.Figure)
        # Should have processed and created figure
        assert len(fig.data) > 0

    def test_generate_plot_with_filters(self):
        """Test generate_plot with filters."""
        config = get_full_config()
        strategy = BarChartStrategy(config)

        df = pd.DataFrame({
            'sample': ['S1', 'S1', 'S2', 'S2'],
            'KO': ['K00001', 'K00002', 'K00001', 'K00003']
        })

        # This tests that base class filter application works
        fig = strategy.generate_plot(df, filters={})

        assert isinstance(fig, go.Figure)


# ============================================================================
# EDGE CASES
# ============================================================================

class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_process_data_with_single_row(self):
        """Test processing with single row."""
        config = get_full_config()
        strategy = BarChartStrategy(config)

        df = pd.DataFrame({
            'sample': ['S1'],
            'KO': ['K00001']
        })

        result = strategy.process_data(df)

        assert len(result) == 1

    def test_create_figure_with_empty_processed_df(self):
        """Test creating figure from empty DataFrame."""
        config = get_minimal_config()
        strategy = BarChartStrategy(config)

        df = pd.DataFrame(columns=['sample', 'ko_count'])

        # Should handle empty DataFrame gracefully
        fig = strategy.create_figure(df)
        assert isinstance(fig, go.Figure)

    def test_process_data_with_large_dataset(self):
        """Test processing with large dataset."""
        config = get_full_config()
        strategy = BarChartStrategy(config)

        # Create large dataset
        df = pd.DataFrame({
            'sample': [f'S{i//10}' for i in range(1000)],
            'KO': [f'K{i:05d}' for i in range(1000)]
        })

        result = strategy.process_data(df)

        assert len(result) > 0
        assert 'ko_count' in result.columns
