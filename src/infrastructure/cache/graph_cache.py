"""
Graph Cache - Plotly Figure Caching.

Provides specialized caching for Plotly graph objects with JSON
serialization for efficient storage.

Classes
-------
GraphCache
    Specialized cache for Plotly figures with JSON serialization
"""

import hashlib
import json
from typing import Optional

import plotly.graph_objects as go

from src.shared.logging import get_logger

from .memory_cache import MemoryCache

logger = get_logger(__name__)


class GraphCache(MemoryCache):
    """
    Specialized cache for Plotly graph objects.

    Provides JSON serialization for Plotly figures, graph-specific hash
    generation, and efficient storage of figure configurations.

    Attributes
    ----------
    max_size : int
        Maximum number of graphs to cache
    default_ttl : int
        Default TTL in seconds
    """

    def __init__(
        self,
        max_size: int = 100,
        default_ttl: int = 1800  # 30 minutes
    ):
        """
        Initialize graph cache.

        Parameters
        ----------
        max_size : int, default=100
            Maximum number of figures to cache.
        default_ttl : int, default=1800
            Default TTL in seconds (30 minutes).
        """
        super().__init__(max_size=max_size, default_ttl=default_ttl)

        logger.info(
            f"Initialized {self.__class__.__name__}",
            extra={'max_size': max_size, 'default_ttl': default_ttl}
        )

    def cache_figure(
        self,
        key: str,
        figure: go.Figure,
        ttl: Optional[int] = None
    ) -> None:
        """
        Cache a Plotly figure.

        Parameters
        ----------
        key : str
            Cache key
        figure : go.Figure
            Plotly figure to cache
        ttl : Optional[int], default=None
            TTL in seconds
        """
        # Convert figure to JSON dict
        fig_dict = figure.to_dict()

        # Store JSON-serializable dict
        self.set(key, fig_dict, ttl=ttl)

        logger.info(f"Cached figure: {key}")

    def get_cached_figure(self, key: str) -> Optional[go.Figure]:
        """
        Retrieve cached Plotly figure.

        Parameters
        ----------
        key : str
            Cache key

        Returns
        -------
        Optional[go.Figure]
            Cached figure or None if not found
        """
        fig_dict = self.get(key)

        if fig_dict is None:
            return None

        # Reconstruct figure from dict
        figure = go.Figure(fig_dict)

        logger.debug(f"Retrieved cached figure: {key}")

        return figure

    def generate_figure_key(
        self,
        analysis_id: str,
        filter_values: dict,
        config: Optional[dict] = None
    ) -> str:
        """
        Generate unique cache key for figure.

        Parameters
        ----------
        analysis_id : str
            Analysis ID (e.g., 'UC1_1')
        filter_values : dict
            Filter values used to generate figure
        config : Optional[dict], default=None
            Additional configuration parameters

        Returns
        -------
        str
            Cache key
        """
        # Create hash from analysis + filters + config
        hash_components = {
            'analysis_id': analysis_id,
            'filters': filter_values,
            'config': config or {}
        }

        hash_string = json.dumps(hash_components, sort_keys=True)
        hash_value = hashlib.md5(
            hash_string.encode()
        ).hexdigest()[:16]

        return f"{analysis_id}_{hash_value}"
