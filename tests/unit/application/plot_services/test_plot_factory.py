"""
Unit tests for PlotFactory.

This module tests the PlotFactory class, which implements the Factory
Pattern for creating plot strategy instances.

Test Categories:
- Initialization: Test factory setup and registry
- Strategy Creation: Test strategy instantiation
- Registry Management: Test strategy registration
- Error Handling: Test validation and error cases
- All Strategies: Test all 19 registered strategies
"""

import pytest
from src.application.plot_services.plot_factory import PlotFactory
from src.domain.plot_strategies.base.base_plot_strategy import BasePlotStrategy
from src.domain.plot_strategies.charts.bar_chart_strategy import BarChartStrategy
from src.domain.plot_strategies.charts.box_scatter_strategy import (
    BoxScatterStrategy
)
from src.domain.plot_strategies.charts.heatmap_scored_strategy import (
    HeatmapScoredStrategy
)
from src.domain.plot_strategies.charts.stacked_bar_chart_strategy import (
    StackedBarChartStrategy
)
from src.domain.plot_strategies.charts.upset_strategy import UpSetStrategy


# ============================================================================
# INITIALIZATION TESTS
# ============================================================================

class TestPlotFactoryInitialization:
    """Test PlotFactory initialization and registry setup."""

    def test_initialization(self):
        """Test factory initialization creates registry."""
        factory = PlotFactory()

        assert hasattr(factory, '_strategy_registry')
        assert isinstance(factory._strategy_registry, dict)
        assert len(factory._strategy_registry) > 0

    def test_default_strategies_count(self):
        """Test that all 19 strategies are registered."""
        factory = PlotFactory()

        # PlotFactory should register exactly 19 strategies
        assert len(factory._strategy_registry) == 19

    def test_default_strategies_registered(self):
        """Test that core strategies are registered."""
        factory = PlotFactory()

        # Test presence of common strategies
        assert 'BarChartStrategy' in factory._strategy_registry
        assert 'BoxScatterStrategy' in factory._strategy_registry
        assert 'UpSetStrategy' in factory._strategy_registry
        assert 'HeatmapScoredStrategy' in factory._strategy_registry
        assert 'StackedBarChartStrategy' in factory._strategy_registry

    def test_registry_contains_only_classes(self):
        """Test that registry values are classes, not instances."""
        factory = PlotFactory()

        for strategy_class in factory._strategy_registry.values():
            assert isinstance(strategy_class, type)
            assert issubclass(strategy_class, BasePlotStrategy)


# ============================================================================
# STRATEGY CREATION TESTS
# ============================================================================

class TestStrategyCreation:
    """Test strategy instance creation."""

    def test_create_strategy_bar_chart(self):
        """Test creating BarChartStrategy from config."""
        factory = PlotFactory()

        config = {
            'metadata': {'use_case_id': 'UC-2.1', 'module': 'module2'},
            'visualization': {'strategy': 'BarChartStrategy'},
            'data': {},
            'validation': {}
        }

        strategy = factory.create_strategy(config)

        assert isinstance(strategy, BarChartStrategy)
        assert isinstance(strategy, BasePlotStrategy)

    def test_create_strategy_box_scatter(self):
        """Test creating BoxScatterStrategy from config."""
        factory = PlotFactory()

        config = {
            'metadata': {'use_case_id': 'UC-2.3'},
            'visualization': {'strategy': 'BoxScatterStrategy'},
            'data': {},
            'validation': {}
        }

        strategy = factory.create_strategy(config)

        assert isinstance(strategy, BoxScatterStrategy)

    def test_create_strategy_heatmap_scored(self):
        """Test creating HeatmapScoredStrategy from config."""
        factory = PlotFactory()

        config = {
            'metadata': {'use_case_id': 'UC-1.5'},
            'visualization': {'strategy': 'HeatmapScoredStrategy'},
            'data': {},
            'validation': {}
        }

        strategy = factory.create_strategy(config)

        assert isinstance(strategy, HeatmapScoredStrategy)

    def test_create_strategy_stacked_bar(self):
        """Test creating StackedBarChartStrategy from config."""
        factory = PlotFactory()

        config = {
            'metadata': {'use_case_id': 'UC-1.3'},
            'visualization': {'strategy': 'StackedBarChartStrategy'},
            'data': {},
            'validation': {}
        }

        strategy = factory.create_strategy(config)

        assert isinstance(strategy, StackedBarChartStrategy)

    def test_create_strategy_upset(self):
        """Test creating UpSetStrategy from config."""
        factory = PlotFactory()

        config = {
            'metadata': {'use_case_id': 'UC-1.1'},
            'visualization': {
                'strategy': 'UpSetStrategy',
                'plotly': {
                    'entity_column': 'Sample',
                    'category_column': 'Database'
                }
            },
            'data': {},
            'validation': {}
        }

        strategy = factory.create_strategy(config)

        assert isinstance(strategy, UpSetStrategy)

    def test_create_strategy_creates_new_instance(self):
        """Test that create_strategy returns new instance each time."""
        factory = PlotFactory()

        config = {
            'metadata': {'use_case_id': 'UC-2.1'},
            'visualization': {'strategy': 'BarChartStrategy'},
            'data': {},
            'validation': {}
        }

        strategy1 = factory.create_strategy(config)
        strategy2 = factory.create_strategy(config)

        assert strategy1 is not strategy2  # Different instances
        assert isinstance(strategy1, type(strategy2))  # Same class

    def test_create_strategy_with_minimal_config(self):
        """Test strategy creation with minimal config."""
        factory = PlotFactory()

        # Minimal config with just required keys
        config = {
            'visualization': {'strategy': 'BarChartStrategy'}
        }

        strategy = factory.create_strategy(config)

        assert isinstance(strategy, BarChartStrategy)

    def test_create_strategy_preserves_config(self):
        """Test that strategy receives complete config."""
        factory = PlotFactory()

        config = {
            'metadata': {'use_case_id': 'UC-2.1', 'title': 'Test'},
            'visualization': {'strategy': 'BarChartStrategy'},
            'data': {'aggregations': []},
            'validation': {'required_columns': ['Sample']}
        }

        strategy = factory.create_strategy(config)

        # Strategy should have access to config
        assert hasattr(strategy, 'config')
        assert strategy.config == config


# ============================================================================
# ERROR HANDLING TESTS
# ============================================================================

class TestErrorHandling:
    """Test error handling and validation."""

    def test_create_strategy_nonexistent(self):
        """Test error when creating non-existent strategy."""
        factory = PlotFactory()

        config = {
            'visualization': {'strategy': 'NonexistentStrategy'}
        }

        with pytest.raises(ValueError, match="Unknown strategy"):
            factory.create_strategy(config)

    def test_create_strategy_missing_strategy_key(self):
        """Test error when config missing strategy key."""
        factory = PlotFactory()

        config = {
            'metadata': {'use_case_id': 'UC-2.1'}
            # Missing visualization.strategy
        }

        with pytest.raises(
            ValueError, match="missing 'visualization.strategy'"
        ):
            factory.create_strategy(config)

    def test_create_strategy_missing_visualization_section(self):
        """Test error when config missing visualization section."""
        factory = PlotFactory()

        config = {
            'metadata': {'use_case_id': 'UC-2.1'}
            # Missing entire visualization section
        }

        with pytest.raises(ValueError):
            factory.create_strategy(config)

    def test_create_strategy_empty_strategy_name(self):
        """Test error when strategy name is empty."""
        factory = PlotFactory()

        config = {
            'visualization': {'strategy': ''}
        }

        with pytest.raises(ValueError):
            factory.create_strategy(config)

    def test_create_strategy_none_strategy_name(self):
        """Test error when strategy name is None."""
        factory = PlotFactory()

        config = {
            'visualization': {'strategy': None}
        }

        with pytest.raises(ValueError):
            factory.create_strategy(config)

    def test_error_message_includes_available_strategies(self):
        """Test error message lists available strategies."""
        factory = PlotFactory()

        config = {
            'visualization': {'strategy': 'InvalidStrategy'}
        }

        with pytest.raises(ValueError) as exc_info:
            factory.create_strategy(config)

        # Error message should include list of available strategies
        error_message = str(exc_info.value)
        assert 'Available strategies' in error_message
        assert 'BarChartStrategy' in error_message


# ============================================================================
# REGISTRY MANAGEMENT TESTS
# ============================================================================

class TestRegistryManagement:
    """Test custom strategy registration."""

    def test_register_custom_strategy(self):
        """Test registering custom strategy class."""
        # Create custom strategy class
        class CustomStrategy(BasePlotStrategy):
            def validate_data(self, df):  # noqa: ARG002
                pass

            def process_data(self, df):
                return df

            def create_figure(self, df):  # noqa: ARG002
                pass

        factory = PlotFactory()
        initial_count = len(factory._strategy_registry)

        factory.register_strategy('CustomStrategy', CustomStrategy)

        assert 'CustomStrategy' in factory._strategy_registry
        assert len(factory._strategy_registry) == initial_count + 1

    def test_register_strategy_can_be_created(self):
        """Test that registered strategy can be instantiated."""
        class CustomStrategy(BasePlotStrategy):
            def validate_data(self, df):  # noqa: ARG002
                pass

            def process_data(self, df):
                return df

            def create_figure(self, df):  # noqa: ARG002
                pass

        factory = PlotFactory()
        factory.register_strategy('CustomStrategy', CustomStrategy)

        # Test that we can create it
        config = {
            'metadata': {'use_case_id': 'UC-TEST'},
            'visualization': {'strategy': 'CustomStrategy'},
            'data': {},
            'validation': {}
        }
        strategy = factory.create_strategy(config)
        assert isinstance(strategy, CustomStrategy)

    def test_register_invalid_strategy(self):
        """Test error when registering non-BasePlotStrategy class."""
        factory = PlotFactory()

        class NotAStrategy:
            pass

        with pytest.raises(
            TypeError, match="must inherit from BasePlotStrategy"
        ):
            factory.register_strategy('InvalidStrategy', NotAStrategy)

    def test_register_strategy_overwrites_existing(self):
        """Test that registering existing name overwrites."""
        class NewBarChartStrategy(BasePlotStrategy):
            def validate_data(self, df):  # noqa: ARG002
                pass

            def process_data(self, df):
                return df

            def create_figure(self, df):  # noqa: ARG002
                pass

        factory = PlotFactory()
        original_class = factory._strategy_registry['BarChartStrategy']

        factory.register_strategy('BarChartStrategy', NewBarChartStrategy)

        assert factory._strategy_registry['BarChartStrategy'] != original_class
        assert (
            factory._strategy_registry['BarChartStrategy']
            == NewBarChartStrategy
        )

    def test_register_multiple_custom_strategies(self):
        """Test registering multiple custom strategies."""
        class CustomStrategy1(BasePlotStrategy):
            def validate_data(self, df):  # noqa: ARG002
                pass

            def process_data(self, df):
                return df

            def create_figure(self, df):  # noqa: ARG002
                pass

        class CustomStrategy2(BasePlotStrategy):
            def validate_data(self, df):  # noqa: ARG002
                pass

            def process_data(self, df):
                return df

            def create_figure(self, df):  # noqa: ARG002
                pass

        factory = PlotFactory()
        factory.register_strategy('Custom1', CustomStrategy1)
        factory.register_strategy('Custom2', CustomStrategy2)

        assert 'Custom1' in factory._strategy_registry
        assert 'Custom2' in factory._strategy_registry
        assert (
            factory._strategy_registry['Custom1'] == CustomStrategy1
        )
        assert (
            factory._strategy_registry['Custom2'] == CustomStrategy2
        )


# ============================================================================
# UTILITY METHODS TESTS
# ============================================================================

class TestUtilityMethods:
    """Test utility methods."""

    def test_get_available_strategies(self):
        """Test getting list of available strategy names."""
        factory = PlotFactory()

        strategies = factory.get_available_strategies()

        assert isinstance(strategies, list)
        assert len(strategies) == 19
        assert 'BarChartStrategy' in strategies
        assert 'UpSetStrategy' in strategies

    def test_get_available_strategies_returns_copy(self):
        """Test that get_available_strategies returns new list."""
        factory = PlotFactory()

        strategies1 = factory.get_available_strategies()
        strategies2 = factory.get_available_strategies()

        # Should be equal but not same object
        assert strategies1 == strategies2
        assert strategies1 is not strategies2

    def test_get_available_strategies_after_registration(self):
        """Test strategy list updates after registration."""
        class CustomStrategy(BasePlotStrategy):
            def validate_data(self, df):  # noqa: ARG002
                pass

            def process_data(self, df):
                return df

            def create_figure(self, df):  # noqa: ARG002
                pass

        factory = PlotFactory()
        strategies_before = factory.get_available_strategies()

        factory.register_strategy('CustomStrategy', CustomStrategy)

        strategies_after = factory.get_available_strategies()

        assert len(strategies_after) == len(strategies_before) + 1
        assert 'CustomStrategy' in strategies_after


# ============================================================================
# ALL STRATEGIES INSTANTIATION TESTS
# ============================================================================

class TestAllStrategies:
    """Test that all 19 registered strategies can be instantiated."""

    @pytest.mark.parametrize('strategy_name,extra_config', [
        ('BarChartStrategy', {}),
        ('BoxScatterStrategy', {}),
        ('ChordStrategy', {}),
        ('CorrelogramStrategy', {}),
        ('DensityPlotStrategy', {}),
        ('DotPlotStrategy', {}),
        ('FacetedHeatmapStrategy', {}),
        ('FrozensetStrategy', {}),
        ('HeatmapScoredStrategy', {}),
        ('HeatmapStrategy', {}),
        ('HierarchicalClusteringStrategy', {}),
        ('NetworkStrategy', {}),
        ('PCAStrategy', {}),
        ('RadarChartStrategy', {}),
        ('SankeyStrategy', {}),
        ('StackedBarChartStrategy', {}),
        ('SunburstStrategy', {}),
        ('TreemapStrategy', {}),
        (
            'UpSetStrategy',
            {'plotly': {'entity_column': 'Sample', 'category_column': 'DB'}}
        ),
    ])
    def test_create_all_strategies(self, strategy_name, extra_config):
        """Test that each registered strategy can be instantiated."""
        factory = PlotFactory()

        config = {
            'metadata': {'use_case_id': 'UC-TEST'},
            'visualization': {
                'strategy': strategy_name,
                **extra_config
            },
            'data': {},
            'validation': {}
        }

        strategy = factory.create_strategy(config)

        assert isinstance(strategy, BasePlotStrategy)
        assert type(strategy).__name__ == strategy_name


# ============================================================================
# EDGE CASES AND BOUNDARY CONDITIONS
# ============================================================================

class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_create_strategy_with_extra_config_keys(self):
        """Test strategy creation with unexpected config keys."""
        factory = PlotFactory()

        config = {
            'visualization': {'strategy': 'BarChartStrategy'},
            'metadata': {'use_case_id': 'UC-2.1'},
            'unexpected_key': 'unexpected_value',
            'another_key': {'nested': 'value'}
        }

        # Should not raise error
        strategy = factory.create_strategy(config)
        assert isinstance(strategy, BarChartStrategy)

    def test_factory_is_reusable(self):
        """Test that factory can create multiple strategies."""
        factory = PlotFactory()

        # Create first strategy
        config1 = {
            'visualization': {'strategy': 'BarChartStrategy'}
        }
        strategy1 = factory.create_strategy(config1)

        # Create second strategy
        config2 = {
            'visualization': {'strategy': 'BoxScatterStrategy'}
        }
        strategy2 = factory.create_strategy(config2)

        assert type(strategy1).__name__ == 'BarChartStrategy'
        assert type(strategy2).__name__ == 'BoxScatterStrategy'

    def test_strategy_name_case_sensitive(self):
        """Test that strategy names are case-sensitive."""
        factory = PlotFactory()

        config = {
            'visualization': {'strategy': 'barchartstrategy'}
        }

        # Should fail because names are case-sensitive
        with pytest.raises(ValueError):
            factory.create_strategy(config)
