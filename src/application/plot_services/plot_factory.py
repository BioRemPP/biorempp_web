"""
Plot Factory - Strategy Creation.

Creates plot strategy instances based on configuration.

Classes
-------
PlotFactory
    Factory for creating plot strategies.

Notes
-----
Implements Factory Pattern for strategy instantiation.
"""

import logging
from typing import Any, Dict

from src.domain.plot_strategies import (
    BarChartStrategy,
    BasePlotStrategy,
    BoxScatterStrategy,
    ChordStrategy,
    CorrelogramStrategy,
    DensityPlotStrategy,
    DotPlotStrategy,
    FacetedHeatmapStrategy,
    FrozensetStrategy,
    HeatmapScoredStrategy,
    HeatmapStrategy,
    HierarchicalClusteringStrategy,
    NetworkStrategy,
    PCAStrategy,
    RadarChartStrategy,
    SankeyStrategy,
    StackedBarChartStrategy,
    SunburstStrategy,
    TreemapStrategy,
    UpSetStrategy,
)

logger = logging.getLogger(__name__)


class PlotFactory:
    """
    Factory for creating plot strategies.

    Maps strategy names (from YAML config) to concrete strategy classes.

    Attributes
    ----------
    _strategy_registry : Dict[str, type]
        Registry mapping strategy names to classes
    """

    def __init__(self):
        """Initialize plot factory with strategy registry."""
        self._strategy_registry: Dict[str, type] = {
            "BarChartStrategy": BarChartStrategy,
            "BoxScatterStrategy": BoxScatterStrategy,
            "ChordStrategy": ChordStrategy,
            "CorrelogramStrategy": CorrelogramStrategy,
            "DensityPlotStrategy": DensityPlotStrategy,
            "DotPlotStrategy": DotPlotStrategy,
            "FacetedHeatmapStrategy": FacetedHeatmapStrategy,
            "FrozensetStrategy": FrozensetStrategy,
            "HeatmapScoredStrategy": HeatmapScoredStrategy,
            "HeatmapStrategy": HeatmapStrategy,
            "HierarchicalClusteringStrategy": HierarchicalClusteringStrategy,
            "NetworkStrategy": NetworkStrategy,
            "PCAStrategy": PCAStrategy,
            "RadarChartStrategy": RadarChartStrategy,
            "SankeyStrategy": SankeyStrategy,
            "StackedBarChartStrategy": StackedBarChartStrategy,
            "SunburstStrategy": SunburstStrategy,
            "TreemapStrategy": TreemapStrategy,
            "UpSetStrategy": UpSetStrategy,
        }
        logger.info(
            f"PlotFactory initialized with "
            f"{len(self._strategy_registry)} strategies"
        )

    def create_strategy(self, config: Dict[str, Any]) -> BasePlotStrategy:
        """
        Create strategy instance from configuration.

        Parameters
        ----------
        config : Dict[str, Any]
            Complete configuration dictionary (must contain
            visualization.strategy: str)

        Returns
        -------
        BasePlotStrategy
            Instantiated strategy

        Raises
        ------
        ValueError
            If strategy name not found in registry
        KeyError
            If configuration missing required keys
        """
        # Get strategy name from config
        viz_config = config.get("visualization", {})
        strategy_name = viz_config.get("strategy")

        if not strategy_name:
            raise ValueError("Configuration missing 'visualization.strategy' key")

        # Lookup strategy class
        strategy_class = self._strategy_registry.get(strategy_name)

        if not strategy_class:
            available = list(self._strategy_registry.keys())
            raise ValueError(
                f"Unknown strategy: '{strategy_name}'. "
                f"Available strategies: {available}"
            )

        # Instantiate and return
        strategy = strategy_class(config)

        use_case_id = config.get("metadata", {}).get("use_case_id", "unknown")
        logger.info(f"Created {strategy_name} for {use_case_id}")

        return strategy

    def register_strategy(self, name: str, strategy_class: type) -> None:
        """
        Register new strategy class.

        Allows dynamic registration of strategies at runtime.

        Parameters
        ----------
        name : str
            Strategy name (used in YAML config)
        strategy_class : type
            Strategy class (must inherit from BasePlotStrategy)
        """
        if not issubclass(strategy_class, BasePlotStrategy):
            raise TypeError(f"{strategy_class} must inherit from BasePlotStrategy")

        self._strategy_registry[name] = strategy_class
        logger.info(f"Registered strategy: {name}")

    def get_available_strategies(self) -> list:
        """
        Get list of available strategy names.

        Returns
        -------
        list
            List of registered strategy names.
        """
        return list(self._strategy_registry.keys())
