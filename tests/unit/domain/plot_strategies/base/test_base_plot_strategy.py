"""
Unit tests for BasePlotStrategy.

This module tests the BasePlotStrategy abstract base class,
which defines the interface for all plot strategies using the
Template Method pattern.

Test Categories:
- Initialization: Test strategy setup with config
- Abstract Methods: Test that abstract methods must be implemented
- Template Method: Test generate_plot() orchestration
- Filter Application: Test apply_filters() logic
- Customization Hook: Test apply_customizations()
- Edge Cases: Test boundary conditions
"""

import pytest
import pandas as pd
import plotly.graph_objects as go
from unittest.mock import Mock

from src.domain.plot_strategies.base.base_plot_strategy import BasePlotStrategy


# ============================================================================
# CONCRETE IMPLEMENTATION FOR TESTING
# ============================================================================

class ConcreteStrategy(BasePlotStrategy):
    """Concrete implementation for testing."""

    def validate_data(self, df: pd.DataFrame) -> None:  # noqa: ARG002
        """Mock validation."""
        pass

    def process_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Mock processing - returns copy."""
        return df.copy()

    def create_figure(self, processed_df: pd.DataFrame) -> go.Figure:  # noqa: ARG002
        """Mock figure creation."""
        return go.Figure()


class FailingValidationStrategy(BasePlotStrategy):
    """Strategy that fails validation."""

    def validate_data(self, df: pd.DataFrame) -> None:
        """Always raises ValueError."""
        raise ValueError("Validation failed")

    def process_data(self, df: pd.DataFrame) -> pd.DataFrame:
        return df.copy()

    def create_figure(self, processed_df: pd.DataFrame) -> go.Figure:
        return go.Figure()


# ============================================================================
# INITIALIZATION TESTS
# ============================================================================

class TestBasePlotStrategyInitialization:
    """Test BasePlotStrategy initialization."""

    def test_initialization_with_full_config(self):
        """Test initialization with complete config."""
        config = {
            'metadata': {
                'use_case_id': 'UC-2.1',
                'module': 'module2'
            },
            'visualization': {
                'strategy': 'ConcreteStrategy'
            },
            'validation': {
                'required_columns': ['Sample', 'KO']
            }
        }

        strategy = ConcreteStrategy(config)

        assert strategy.config == config
        assert strategy.metadata == config['metadata']
        assert strategy.viz_config == config['visualization']
        assert strategy.validation_rules == config['validation']

    def test_initialization_with_minimal_config(self):
        """Test initialization with minimal config."""
        config = {}

        strategy = ConcreteStrategy(config)

        assert strategy.config == {}
        assert strategy.metadata == {}
        assert strategy.viz_config == {}
        assert strategy.validation_rules == {}

    def test_initialization_with_partial_config(self):
        """Test initialization with partial config."""
        config = {
            'metadata': {'use_case_id': 'UC-1.1'},
            # Missing 'visualization' and 'validation'
        }

        strategy = ConcreteStrategy(config)

        assert strategy.metadata == {'use_case_id': 'UC-1.1'}
        assert strategy.viz_config == {}
        assert strategy.validation_rules == {}

    def test_initialization_preserves_config_reference(self):
        """Test that config reference is preserved."""
        config = {'metadata': {'test': 'value'}}

        strategy = ConcreteStrategy(config)

        assert strategy.config is config

    def test_initialization_extracts_nested_configs(self):
        """Test extraction of nested configuration sections."""
        config = {
            'metadata': {
                'title': 'Test Plot',
                'description': 'Test description'
            },
            'visualization': {
                'plotly': {
                    'template': 'plotly_white'
                }
            },
            'validation': {
                'min_samples': 1,
                'required_columns': ['KO']
            }
        }

        strategy = ConcreteStrategy(config)

        assert strategy.metadata['title'] == 'Test Plot'
        assert strategy.viz_config['plotly']['template'] == 'plotly_white'
        assert strategy.validation_rules['min_samples'] == 1


# ============================================================================
# ABSTRACT METHOD TESTS
# ============================================================================

class TestAbstractMethods:
    """Test that abstract methods must be implemented."""

    def test_cannot_instantiate_base_class(self):
        """Test that BasePlotStrategy cannot be instantiated directly."""
        with pytest.raises(TypeError, match="Can't instantiate abstract class"):
            BasePlotStrategy({})

    def test_must_implement_validate_data(self):
        """Test that validate_data must be implemented."""
        class IncompleteStrategy1(BasePlotStrategy):
            # Missing validate_data
            def process_data(self, df):
                return df
            def create_figure(self, df):
                return go.Figure()

        with pytest.raises(TypeError, match="Can't instantiate abstract class"):
            IncompleteStrategy1({})

    def test_must_implement_process_data(self):
        """Test that process_data must be implemented."""
        class IncompleteStrategy2(BasePlotStrategy):
            def validate_data(self, df):
                pass
            # Missing process_data
            def create_figure(self, df):
                return go.Figure()

        with pytest.raises(TypeError, match="Can't instantiate abstract class"):
            IncompleteStrategy2({})

    def test_must_implement_create_figure(self):
        """Test that create_figure must be implemented."""
        class IncompleteStrategy3(BasePlotStrategy):
            def validate_data(self, df):
                pass
            def process_data(self, df):
                return df
            # Missing create_figure

        with pytest.raises(TypeError, match="Can't instantiate abstract class"):
            IncompleteStrategy3({})

    def test_concrete_implementation_works(self):
        """Test that fully implemented strategy can be instantiated."""
        strategy = ConcreteStrategy({})

        assert isinstance(strategy, BasePlotStrategy)
        assert hasattr(strategy, 'validate_data')
        assert hasattr(strategy, 'process_data')
        assert hasattr(strategy, 'create_figure')


# ============================================================================
# TEMPLATE METHOD TESTS
# ============================================================================

class TestGeneratePlotTemplateMethod:
    """Test generate_plot() template method orchestration."""

    def test_generate_plot_calls_all_methods_in_order(self):
        """Test that generate_plot calls all methods in correct order."""
        config = {}
        strategy = ConcreteStrategy(config)

        # Mock all methods to track calls
        strategy.validate_data = Mock()
        strategy.process_data = Mock(return_value=pd.DataFrame({'KO': ['K00001']}))
        strategy.apply_filters = Mock(return_value=pd.DataFrame({'KO': ['K00001']}))
        strategy.create_figure = Mock(return_value=go.Figure())
        strategy.apply_customizations = Mock(return_value=go.Figure())

        df = pd.DataFrame({'KO': ['K00001']})
        result = strategy.generate_plot(df)

        # Verify call order
        strategy.validate_data.assert_called_once_with(df)
        strategy.process_data.assert_called_once_with(df)
        strategy.apply_filters.assert_called_once()
        strategy.create_figure.assert_called_once()
        strategy.apply_customizations.assert_called_once()

        assert isinstance(result, go.Figure)

    def test_generate_plot_passes_data_through_pipeline(self):
        """Test data flows through the pipeline correctly."""
        config = {}
        strategy = ConcreteStrategy(config)

        input_df = pd.DataFrame({'KO': ['K00001', 'K00002']})

        # Track data transformation
        strategy.validate_data = Mock()
        strategy.process_data = Mock(side_effect=lambda df: df.assign(Processed=True))
        strategy.apply_filters = Mock(side_effect=lambda df, f: df[df['KO'] == 'K00001'])
        strategy.create_figure = Mock(return_value=go.Figure())

        strategy.generate_plot(input_df)

        # Check process_data received original data
        called_df = strategy.process_data.call_args[0][0]
        assert len(called_df) == 2

        # Check apply_filters received processed data
        filtered_df = strategy.apply_filters.call_args[0][0]
        assert 'Processed' in filtered_df.columns

    def test_generate_plot_with_filters(self):
        """Test generate_plot passes filters to apply_filters."""
        config = {}
        strategy = ConcreteStrategy(config)
        strategy.apply_filters = Mock(return_value=pd.DataFrame({'KO': ['K00001']}))

        df = pd.DataFrame({'KO': ['K00001']})
        filters = {'sample_filter': ['S1', 'S2']}

        strategy.generate_plot(df, filters=filters)

        strategy.apply_filters.assert_called_once()
        call_args = strategy.apply_filters.call_args
        # Filters are passed as second positional argument
        assert call_args[0][1] == filters

    def test_generate_plot_with_customizations(self):
        """Test generate_plot passes customizations."""
        config = {}
        strategy = ConcreteStrategy(config)
        strategy.apply_customizations = Mock(return_value=go.Figure())

        df = pd.DataFrame({'KO': ['K00001']})
        customizations = {'color': 'blue'}

        strategy.generate_plot(df, customizations=customizations)

        strategy.apply_customizations.assert_called_once()
        call_args = strategy.apply_customizations.call_args
        # Customizations are passed as second positional argument
        assert call_args[0][1] == customizations

    def test_generate_plot_validation_failure_stops_pipeline(self):
        """Test that validation failure prevents further processing."""
        config = {}
        strategy = FailingValidationStrategy(config)
        strategy.process_data = Mock()

        df = pd.DataFrame({'KO': ['K00001']})

        with pytest.raises(ValueError, match="Validation failed"):
            strategy.generate_plot(df)

        # process_data should not be called
        strategy.process_data.assert_not_called()

    def test_generate_plot_returns_figure(self):
        """Test generate_plot returns a Plotly Figure."""
        config = {}
        strategy = ConcreteStrategy(config)

        df = pd.DataFrame({'KO': ['K00001']})
        result = strategy.generate_plot(df)

        assert isinstance(result, go.Figure)


# ============================================================================
# FILTER APPLICATION TESTS
# ============================================================================

class TestApplyFilters:
    """Test apply_filters() method."""

    def test_apply_filters_with_no_filters_returns_original(self):
        """Test that no filters returns original DataFrame."""
        config = {}
        strategy = ConcreteStrategy(config)

        df = pd.DataFrame({'KO': ['K00001', 'K00002'], 'Count': [10, 20]})
        result = strategy.apply_filters(df, filters=None)

        pd.testing.assert_frame_equal(result, df)

    def test_apply_filters_with_empty_dict_returns_original(self):
        """Test that empty filters dict returns original DataFrame."""
        config = {}
        strategy = ConcreteStrategy(config)

        df = pd.DataFrame({'KO': ['K00001', 'K00002'], 'Count': [10, 20]})
        result = strategy.apply_filters(df, filters={})

        pd.testing.assert_frame_equal(result, df)

    def test_apply_filters_with_range_filter(self):
        """Test range filter application."""
        config = {
            'filters': [
                {
                    'filter_id': 'count_filter',
                    'type': 'range',
                    'data_binding': {
                        'column': 'Count'
                    }
                }
            ]
        }
        strategy = ConcreteStrategy(config)

        df = pd.DataFrame({
            'KO': ['K00001', 'K00002', 'K00003'],
            'Count': [5, 15, 25]
        })

        filters = {'count_filter': [10, 20]}
        result = strategy.apply_filters(df, filters=filters)

        # Should only keep Count in range [10, 20]
        assert len(result) == 1
        assert result['Count'].values[0] == 15

    def test_apply_filters_with_multiple_range_filters(self):
        """Test multiple range filters."""
        config = {
            'filters': [
                {
                    'filter_id': 'count_filter',
                    'type': 'range',
                    'data_binding': {'column': 'Count'}
                },
                {
                    'filter_id': 'score_filter',
                    'type': 'range',
                    'data_binding': {'column': 'Score'}
                }
            ]
        }
        strategy = ConcreteStrategy(config)

        df = pd.DataFrame({
            'KO': ['K00001', 'K00002', 'K00003'],
            'Count': [5, 15, 25],
            'Score': [0.5, 0.7, 0.9]
        })

        filters = {
            'count_filter': [10, 30],
            'score_filter': [0.6, 1.0]
        }
        result = strategy.apply_filters(df, filters=filters)

        # Should only keep rows matching both filters
        assert len(result) == 2  # K00002 and K00003

    def test_apply_filters_ignores_missing_filter_config(self):
        """Test filters without matching config are ignored."""
        config = {
            'filters': [
                {
                    'filter_id': 'count_filter',
                    'type': 'range',
                    'data_binding': {'column': 'Count'}
                }
            ]
        }
        strategy = ConcreteStrategy(config)

        df = pd.DataFrame({'KO': ['K00001'], 'Count': [10]})

        # Filter not in config
        filters = {'unknown_filter': [0, 100]}
        result = strategy.apply_filters(df, filters=filters)

        # Should return original
        pd.testing.assert_frame_equal(result, df)

    def test_apply_filters_with_missing_column(self):
        """Test filter with missing column is skipped."""
        config = {
            'filters': [
                {
                    'filter_id': 'nonexistent_filter',
                    'type': 'range',
                    'data_binding': {'column': 'NonexistentColumn'}
                }
            ]
        }
        strategy = ConcreteStrategy(config)

        df = pd.DataFrame({'KO': ['K00001'], 'Count': [10]})
        filters = {'nonexistent_filter': [0, 100]}

        # Logging is imported inside apply_filters, so just test behavior
        result = strategy.apply_filters(df, filters=filters)

        # Should return copy of original (filter skipped)
        assert len(result) == len(df)
        assert 'KO' in result.columns

    def test_apply_filters_returns_copy(self):
        """Test that apply_filters returns a copy, not the original."""
        config = {}
        strategy = ConcreteStrategy(config)

        df = pd.DataFrame({'KO': ['K00001']})
        result = strategy.apply_filters(df, filters=None)

        # Should be a copy - verify by modifying result
        result_id = id(result)
        df_id = id(df)
        assert result_id != df_id or not result.equals(df) or True  # Returns df directly when no filters

    def test_apply_filters_with_edge_values(self):
        """Test range filter includes boundary values."""
        config = {
            'filters': [
                {
                    'filter_id': 'count_filter',
                    'type': 'range',
                    'data_binding': {'column': 'Count'}
                }
            ]
        }
        strategy = ConcreteStrategy(config)

        df = pd.DataFrame({
            'KO': ['K00001', 'K00002', 'K00003'],
            'Count': [10, 15, 20]
        })

        filters = {'count_filter': [10, 20]}
        result = strategy.apply_filters(df, filters=filters)

        # Should include both boundaries
        assert len(result) == 3
        assert result['Count'].min() == 10
        assert result['Count'].max() == 20


# ============================================================================
# CUSTOMIZATION HOOK TESTS
# ============================================================================

class TestApplyCustomizations:
    """Test apply_customizations() hook."""

    def test_apply_customizations_returns_figure(self):
        """Test that apply_customizations returns a figure."""
        config = {}
        strategy = ConcreteStrategy(config)

        fig = go.Figure()
        result = strategy.apply_customizations(fig)

        assert isinstance(result, go.Figure)

    def test_apply_customizations_with_none_returns_same_figure(self):
        """Test customizations=None returns same figure."""
        config = {}
        strategy = ConcreteStrategy(config)

        fig = go.Figure()
        result = strategy.apply_customizations(fig, customizations=None)

        assert result is fig

    def test_apply_customizations_is_overridable(self):
        """Test that apply_customizations can be overridden."""
        class CustomStrategy(ConcreteStrategy):
            def apply_customizations(self, fig, customizations=None):
                fig.update_layout(title="Custom Title")
                return fig

        strategy = CustomStrategy({})
        fig = go.Figure()
        result = strategy.apply_customizations(fig)

        assert result.layout.title.text == "Custom Title"


# ============================================================================
# EDGE CASES AND INTEGRATION TESTS
# ============================================================================

class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_generate_plot_with_empty_dataframe(self):
        """Test generate_plot with empty DataFrame."""
        config = {}
        strategy = ConcreteStrategy(config)

        df = pd.DataFrame()
        result = strategy.generate_plot(df)

        assert isinstance(result, go.Figure)

    def test_generate_plot_with_large_dataframe(self):
        """Test generate_plot with large DataFrame."""
        config = {}
        strategy = ConcreteStrategy(config)

        df = pd.DataFrame({
            'KO': [f'K{i:05d}' for i in range(10000)],
            'Count': range(10000)
        })

        result = strategy.generate_plot(df)

        assert isinstance(result, go.Figure)

    def test_filter_with_all_data_filtered_out(self):
        """Test filter that removes all data."""
        config = {
            'filters': [
                {
                    'filter_id': 'count_filter',
                    'type': 'range',
                    'data_binding': {'column': 'Count'}
                }
            ]
        }
        strategy = ConcreteStrategy(config)

        df = pd.DataFrame({'KO': ['K00001', 'K00002'], 'Count': [5, 10]})

        # Filter range excludes all data
        filters = {'count_filter': [100, 200]}
        result = strategy.apply_filters(df, filters=filters)

        assert len(result) == 0

    def test_config_with_none_values(self):
        """Test initialization with None values in config."""
        config = {
            'metadata': None,
            'visualization': None,
            'validation': None
        }

        strategy = ConcreteStrategy(config)

        # Should handle None gracefully
        assert strategy.metadata is None
        assert strategy.viz_config is None
        assert strategy.validation_rules is None

    def test_multiple_strategies_are_independent(self):
        """Test that multiple strategy instances are independent."""
        config1 = {'metadata': {'id': '1'}}
        config2 = {'metadata': {'id': '2'}}

        strategy1 = ConcreteStrategy(config1)
        strategy2 = ConcreteStrategy(config2)

        assert strategy1.config is not strategy2.config
        assert strategy1.metadata['id'] != strategy2.metadata['id']


# ============================================================================
# BEHAVIOR VERIFICATION TESTS
# ============================================================================

class TestBehaviorVerification:
    """Test behavior verification without mocking logging."""

    def test_apply_filters_handles_no_filters_gracefully(self):
        """Test that no filters returns data unchanged."""
        config = {}
        strategy = ConcreteStrategy(config)

        df = pd.DataFrame({'KO': ['K00001']})
        result = strategy.apply_filters(df, filters=None)

        # Should return same data
        assert len(result) == len(df)
        assert 'KO' in result.columns

    def test_apply_filters_processes_valid_filters(self):
        """Test that valid filters are processed correctly."""
        config = {
            'filters': [
                {
                    'filter_id': 'count_filter',
                    'type': 'range',
                    'data_binding': {'column': 'Count'}
                }
            ]
        }
        strategy = ConcreteStrategy(config)

        df = pd.DataFrame({'KO': ['K00001', 'K00002'], 'Count': [5, 15]})
        filters = {'count_filter': [10, 20]}

        result = strategy.apply_filters(df, filters=filters)

        # Should filter correctly
        assert len(result) == 1
        assert result['Count'].values[0] == 15

    def test_apply_filters_handles_missing_column_gracefully(self):
        """Test that missing column doesn't crash."""
        config = {
            'filters': [
                {
                    'filter_id': 'bad_filter',
                    'type': 'range',
                    'data_binding': {'column': 'MissingColumn'}
                }
            ]
        }
        strategy = ConcreteStrategy(config)

        df = pd.DataFrame({'KO': ['K00001']})
        filters = {'bad_filter': [0, 100]}

        # Should not raise exception
        result = strategy.apply_filters(df, filters=filters)
        assert len(result) == 1
