"""
Graph Cache Manager - Graph Caching Interface.

Provides manager interface compatible with PlotService for graph caching
operations.

Classes
-------
GraphCacheManager
    Manager wrapper for GraphCache with metadata support
"""

from typing import Any, Optional

import plotly.graph_objects as go

from src.infrastructure.cache.graph_cache import GraphCache
from src.shared.logging import get_logger

logger = get_logger(__name__)


class GraphCacheManager:
    """
    Manager for graph caching operations.

    Wraps GraphCache with additional management capabilities and metadata
    support.

    Attributes
    ----------
    cache : GraphCache
        Underlying cache instance

    Methods
    -------
    cache_graph(key, figure, metadata, ttl)
        Cache a Plotly figure
    get_cached_graph(key)
        Retrieve cached Plotly figure
    clear()
        Clear all cached graphs
    get_stats()
        Get cache statistics
    """

    def __init__(
        self,
        max_size: int = 100,
        default_ttl: int = 3600
    ):
        """
        Initialize graph cache manager.

        Parameters
        ----------
        max_size : int, default=100
            Maximum number of graphs to cache.
        default_ttl : int, default=3600
            Default TTL in seconds (1 hour).
        """
        self.cache = GraphCache(
            max_size=max_size,
            default_ttl=default_ttl
        )
        logger.info("GraphCacheManager initialized")

    def cache_graph(
        self,
        key: str,
        figure: go.Figure,
        metadata: Optional[dict] = None,
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
        metadata : Optional[dict], default=None
            Optional metadata (for logging/tracking)
        ttl : Optional[int], default=None
            TTL in seconds (if None, uses default)
        """
        self.cache.cache_figure(key, figure, ttl=ttl)

        if metadata:
            logger.debug(f"Cached graph with metadata: {metadata}")

    def get_cached_graph(self, key: str) -> Optional[go.Figure]:
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
        return self.cache.get_cached_figure(key)

    def clear(self) -> None:
        """Clear all cached graphs."""
        self.cache.clear()
        logger.info("All cached graphs cleared")

    def get_stats(self) -> dict:
        """
        Get cache statistics.

        Returns
        -------
        dict
            Statistics including size, max_size, etc.
        """
        return self.cache.get_stats()
