"""
Base Plot Strategy - Abstract Base Class.

This module defines the interface for all plot strategies following
the Strategy Pattern.

Classes
-------
BasePlotStrategy
    Abstract base class for plot strategies.

Notes
-----
All concrete strategies must implement:
- validate_data()
- process_data()
- create_figure()
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

import pandas as pd
import plotly.graph_objects as go


class BasePlotStrategy(ABC):
    """
    Abstract base class for plot generation strategies.

    This class defines the common interface that all plot strategies
    must implement. It follows the Template Method pattern, where
    `generate_plot()` orchestrates the overall process while leaving
    specific steps to be implemented by subclasses.

    Attributes
    ----------
    config : Dict[str, Any]
        Complete configuration from YAML file
    metadata : Dict[str, Any]
        Metadata section from config
    viz_config : Dict[str, Any]
        Visualization section from config
    validation_rules : Dict[str, Any]
        Validation rules from config

    Notes
    -----
    Subclasses must implement three abstract methods:
    - `validate_data()` - Validate input data
    - `process_data()` - Process and transform data
    - `create_figure()` - Create Plotly figure
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize base strategy with configuration.

        Parameters
        ----------
        config : Dict[str, Any]
            Complete configuration dictionary from YAML.
        """
        self.config = config
        self.metadata = config.get("metadata", {})
        self.viz_config = config.get("visualization", {})
        self.validation_rules = config.get("validation", {})

    @abstractmethod
    def validate_data(self, df: pd.DataFrame) -> None:
        """
        Validate input data.

        Parameters
        ----------
        df : pd.DataFrame
            Input data to validate.

        Raises
        ------
        ValueError
            If validation fails.
        """
        pass

    @abstractmethod
    def process_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Process and transform data for visualization.

        Parameters
        ----------
        df : pd.DataFrame
            Input data.

        Returns
        -------
        pd.DataFrame
            Processed data ready for visualization.
        """
        pass

    @abstractmethod
    def create_figure(self, processed_df: pd.DataFrame) -> go.Figure:
        """
        Create Plotly figure from processed data.

        Parameters
        ----------
        processed_df : pd.DataFrame
            Processed data.

        Returns
        -------
        go.Figure
            Configured Plotly figure.
        """
        pass

    def apply_filters(
        self, df: pd.DataFrame, filters: Optional[Dict[str, Any]] = None
    ) -> pd.DataFrame:
        """
        Apply filters to data.

        This is a common implementation that can be overridden
        by subclasses if needed.

        Parameters
        ----------
        df : pd.DataFrame
            Data to filter.
        filters : Optional[Dict[str, Any]], default=None
            Filter specifications.

        Returns
        -------
        pd.DataFrame
            Filtered data.
        """
        import logging

        logger = logging.getLogger(__name__)

        if not filters:
            logger.debug("No filters provided, returning original data")
            return df

        logger.info(
            f"Applying filters - Input shape: {df.shape}, "
            f"Columns: {df.columns.tolist()}"
        )
        logger.info(f"Filters to apply: {filters}")

        filtered_df = df.copy()

        # Get filter configurations
        filter_configs = self.config.get("filters", [])

        for filter_config in filter_configs:
            filter_id = filter_config.get("filter_id")
            filter_type = filter_config.get("type")

            if filter_id not in filters:
                continue

            filter_value = filters[filter_id]
            data_binding = filter_config.get("data_binding", {})
            column = data_binding.get("column")

            if not column or column not in filtered_df.columns:
                logger.warning(
                    f"Filter '{filter_id}': Column '{column}' not found. "
                    f"Available: {filtered_df.columns.tolist()}"
                )
                continue

            # Apply range filter
            if filter_type == "range" and isinstance(filter_value, list):
                min_val, max_val = filter_value
                logger.info(
                    f"Applying range filter on '{column}': " f"[{min_val}, {max_val}]"
                )
                filtered_df = filtered_df[
                    (filtered_df[column] >= min_val) & (filtered_df[column] <= max_val)
                ]
                logger.info(f"After filter: {len(filtered_df)} rows remaining")

        logger.info(f"Final filtered shape: {filtered_df.shape}")
        return filtered_df

    def apply_customizations(
        self, fig: go.Figure, customizations: Optional[Any] = None
    ) -> go.Figure:
        """
        Apply custom styling to figure.

        This is a hook for future customization features
        (FLEXIVEL and FLEXIVEL2).

        Parameters
        ----------
        fig : go.Figure
            Base figure.
        customizations : Optional[Any], default=None
            Customization specifications.

        Returns
        -------
        go.Figure
            Customized figure.
        """
        # Hook for future implementation
        return fig

    def generate_plot(
        self,
        data: pd.DataFrame,
        filters: Optional[Dict[str, Any]] = None,
        customizations: Optional[Any] = None,
    ) -> go.Figure:
        """
        Generate complete plot (Template Method).

        This method orchestrates the entire plot generation process:
        1. Validate input data
        2. Process data
        3. Apply filters
        4. Create figure
        5. Apply customizations

        Parameters
        ----------
        data : pd.DataFrame
            Input data.
        filters : Optional[Dict[str, Any]], default=None
            Filters to apply.
        customizations : Optional[Any], default=None
            Customizations to apply.

        Returns
        -------
        go.Figure
            Complete Plotly figure.

        Raises
        ------
        ValueError
            If validation fails.
        """
        # 1. Validate
        self.validate_data(data)

        # 2. Process
        processed_df = self.process_data(data)

        # 3. Filter
        filtered_df = self.apply_filters(processed_df, filters)

        # 4. Create figure
        figure = self.create_figure(filtered_df)

        # 5. Apply customizations (hook for future)
        figure = self.apply_customizations(figure, customizations)

        return figure
