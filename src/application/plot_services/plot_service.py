"""
Plot Service: Orchestration and Caching.

Main service coordinating plot generation with multi-layer caching.

Classes
-------
PlotService
    Orchestrates plot generation pipeline with caching.

Notes
-----
Implements Facade Pattern, providing simple interface while managing:
- Configuration loading
- Strategy creation
- Multi-layer caching
- Error handling
"""

import hashlib
import json
import logging
import time
from typing import Any, Dict, Optional, Tuple

import pandas as pd
import plotly.graph_objects as go

from src.application.plot_services.plot_config_loader import PlotConfigLoader
from src.application.plot_services.plot_factory import PlotFactory
from src.infrastructure.cache import GraphCacheManager

logger = logging.getLogger(__name__)


class PlotService:
    """
    Central service for plot generation with caching.

    This service implements the Facade pattern, providing a simple
    interface for plot generation while managing complex operations
    behind the scenes:
    - Load YAML configuration
    - Create strategy via factory
    - Check multi-layer cache
    - Generate plot
    - Cache results

    Attributes
    ----------
    config_loader : PlotConfigLoader
        Configuration loader instance.
    factory : PlotFactory
        Plot factory instance.
    cache_manager : GraphCacheManager
        Cache manager instance.

    Examples
    --------
    >>> service = PlotService()
    >>> fig = service.generate_plot(
    ...     "UC-2.1",
    ...     df,
    ...     filters={"uc-2-1-range-slider": [10, 50]}
    ... )
    """

    def __init__(self):
        """Initialize plot service with dependencies."""
        self.config_loader = PlotConfigLoader()
        self.factory = PlotFactory()
        self.cache_manager = GraphCacheManager()
        logger.info("PlotService initialized")

    def generate_plot(
        self,
        use_case_id: str,
        data: pd.DataFrame,
        filters: Optional[Dict[str, Any]] = None,
        customizations: Optional[Any] = None,
        force_refresh: bool = False,
    ) -> go.Figure:
        """
        Generate plot for given use case with caching.

        Pipeline:
        1. Load configuration from YAML
        2. Generate cache keys
        3. Check graph cache
        4. If miss: Create strategy and generate plot
        5. Cache result
        6. Return figure

        Parameters
        ----------
        use_case_id : str
            Use case identifier (e.g., "UC-2.1").
        data : pd.DataFrame
            Input data.
        filters : Optional[Dict[str, Any]], default=None
            Filters to apply (e.g., {"uc-2-1-range-slider": [10, 50]}).
        customizations : Optional[Any], default=None
            Additional customizations (future feature).
        force_refresh : bool, default=False
            Force cache refresh.

        Returns
        -------
        go.Figure
            Generated Plotly figure.

        Raises
        ------
        ValueError
            If data validation fails.
        FileNotFoundError
            If configuration file not found.

        Examples
        --------
        >>> service = PlotService()
        >>> fig = service.generate_plot("UC-2.1", df)
        >>> fig.layout.height
        500
        """
        start_time = time.time()
        logger.info(f"Generating plot for {use_case_id}")

        # 1. Load configuration (force reload if force_refresh is True)
        config = self.config_loader.load_config(use_case_id, force_reload=force_refresh)
        perf_config = config.get("performance", {})
        cache_config = perf_config.get("cache", {})

        # 2. Generate cache keys
        data_hash = self._generate_data_hash(data)
        filters_hash = self._generate_filters_hash(filters) if filters else "no_filters"

        # Generate cache key (needed for both checking and storing)
        graph_cache_key = self._get_cache_key(config, "graph", data_hash, filters_hash)

        # 3. Check if caching is enabled
        if cache_config.get("enabled", True) and not force_refresh:
            # Check graph cache (fastest)
            cached_figure = self.cache_manager.get_cached_graph(graph_cache_key)
            if cached_figure:
                cache_time = time.time() - start_time
                logger.info(
                    f"Cache HIT (graph) for {use_case_id}: " f"{cache_time:.3f}s"
                )
                return cached_figure

            logger.debug(f"Cache MISS (graph) for {use_case_id}")

        # 4. Create strategy via factory
        strategy = self.factory.create_strategy(config)

        # 5. Generate plot (includes validation, processing, filtering)
        try:
            figure = strategy.generate_plot(
                data, filters=filters, customizations=customizations
            )

            # 6. Cache the figure
            if cache_config.get("enabled", True):
                ttl = self._get_cache_ttl(cache_config, "graph")
                # Note: ttl is not used by current GraphCacheManager
                # (it uses global TTL), but we pass metadata
                metadata = {"use_case_id": use_case_id, "filters": filters, "ttl": ttl}
                self.cache_manager.cache_graph(
                    graph_cache_key, figure, metadata=metadata
                )
                logger.debug(f"Cached graph for {use_case_id} (TTL: {ttl}s)")

            total_time = time.time() - start_time
            logger.info(f"Plot generated for {use_case_id}: {total_time:.3f}s")

            return figure

        except Exception as e:
            logger.error(f"Error generating plot for {use_case_id}: {e}", exc_info=True)
            raise

    def _generate_data_hash(self, df: pd.DataFrame) -> str:
        """
        Generate hash from DataFrame content.

        Parameters
        ----------
        df : pd.DataFrame
            Input DataFrame.

        Returns
        -------
        str
            MD5 hash (16 characters).
        """
        hash_df = df
        # UpSet-like datasets are often built from Python sets; sort rows to
        # stabilize hash generation across callback executions.
        if {"category", "identifier"}.issubset(df.columns):
            try:
                hash_df = (
                    df.sort_values(
                        by=["category", "identifier"],
                        kind="mergesort",
                        na_position="last",
                    )
                    .reset_index(drop=True)
                )
            except Exception:
                hash_df = df

        # Create hash from shape + columns + sample of data
        hash_components = [
            str(hash_df.shape),
            str(sorted(hash_df.columns.tolist())),
            str(hash_df.head(5).values.tobytes()) if len(hash_df) > 0 else "",
            str(hash_df.tail(5).values.tobytes()) if len(hash_df) > 5 else "",
        ]

        hash_string = "|".join(hash_components)
        return hashlib.md5(hash_string.encode()).hexdigest()[:16]

    def _generate_filters_hash(self, filters: Dict[str, Any]) -> str:
        """
        Generate hash from filters.

        Parameters
        ----------
        filters : Dict[str, Any]
            Filter values.

        Returns
        -------
        str
            MD5 hash (16 characters).
        """
        # Sort keys for consistency
        filter_string = json.dumps(filters, sort_keys=True)
        return hashlib.md5(filter_string.encode()).hexdigest()[:16]

    def generate_token_hash(self, value: Any) -> str:
        """
        Generate deterministic hash for arbitrary cache token values.

        Parameters
        ----------
        value : Any
            Value to hash.

        Returns
        -------
        str
            MD5 hash (16 characters).
        """
        try:
            token_string = json.dumps(value, sort_keys=True, default=str)
        except Exception:
            token_string = str(value)
        return hashlib.md5(token_string.encode()).hexdigest()[:16]

    def _get_cache_key(
        self,
        config: Dict[str, Any],
        layer: str,
        data_hash: str,
        filters_hash: str,
        extra_tokens: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Generate cache key from template.

        Parameters
        ----------
        config : Dict[str, Any]
            Configuration dictionary.
        layer : str
            Cache layer ('dataframe' or 'graph').
        data_hash : str
            Data content hash.
        filters_hash : str
            Filters hash.
        extra_tokens : Optional[Dict[str, Any]], default=None
            Additional placeholders for key template substitution.

        Returns
        -------
        str
            Cache key.
        """
        cache_config = config.get("performance", {}).get("cache", {})
        layers = cache_config.get("layers", [])

        logger.debug(
            f"Generating cache key for layer '{layer}'",
            extra={
                "data_hash": data_hash[:16] if data_hash else None,
                "filters_hash": filters_hash[:16] if filters_hash else None,
                "available_layers": [layer_def.get("layer") for layer_def in layers],
            },
        )

        # Find layer configuration
        layer_config = next(
            (layer_def for layer_def in layers if layer_def.get("layer") == layer), None
        )

        if not layer_config:
            # Fallback to default key
            fallback_key = f"{layer}_{data_hash}_{filters_hash}"
            logger.debug(
                f"Layer '{layer}' not found in config, using fallback key",
                extra={"fallback_key": fallback_key[:50]},
            )
            return fallback_key

        # Get template and substitute values
        template = layer_config.get("key_template", "")

        logger.debug(
            f"Using template for layer '{layer}': {template}",
            extra={
                "template": template,
                "available_placeholders": (
                    ["data_hash", "filters_hash"]
                    + sorted((extra_tokens or {}).keys())
                ),
            },
        )

        try:
            template_values: Dict[str, Any] = {
                "data_hash": data_hash,
                "filters_hash": filters_hash,
            }
            if extra_tokens:
                template_values.update(extra_tokens)

            key = template.format(**template_values)
            logger.debug(
                "Cache key generated successfully",
                extra={"key": key[:50], "full_length": len(key)},
            )
        except KeyError as e:
            logger.error(
                f"Cache key template error: missing placeholder '{e}'",
                extra={
                    "template": template,
                    "available": (
                        ["data_hash", "filters_hash"]
                        + sorted((extra_tokens or {}).keys())
                    ),
                    "error": str(e),
                },
            )
            raise

        return key

    def resolve_graph_cache(
        self,
        use_case_id: str,
        data: pd.DataFrame,
        filters: Optional[Dict[str, Any]] = None,
        *,
        config: Optional[Dict[str, Any]] = None,
        force_refresh: bool = False,
        extra_cache_tokens: Optional[Dict[str, Any]] = None,
    ) -> Tuple[Optional[go.Figure], Optional[Dict[str, Any]]]:
        """
        Resolve graph cache hit and return reusable cache context.

        This method is intended for callbacks that build figures manually but
        still need to use the YAML-driven graph cache contract.

        Parameters
        ----------
        use_case_id : str
            Use case identifier.
        data : pd.DataFrame
            Data used to derive cache key.
        filters : Optional[Dict[str, Any]], default=None
            Filter state used to derive cache key.
        config : Optional[Dict[str, Any]], default=None
            Preloaded use case configuration.
        force_refresh : bool, default=False
            Skip cache read if True.
        extra_cache_tokens : Optional[Dict[str, Any]], default=None
            Extra placeholders expected by key template.

        Returns
        -------
        Tuple[Optional[go.Figure], Optional[Dict[str, Any]]]
            Cached figure (if hit) and cache context for later storage.
        """
        use_case_config = config or self.config_loader.load_config(use_case_id)
        cache_config = use_case_config.get("performance", {}).get("cache", {})
        if not cache_config.get("enabled", True):
            return None, None

        data_hash = self._generate_data_hash(data)
        filters_hash = self._generate_filters_hash(filters) if filters else "no_filters"
        graph_cache_key = self._get_cache_key(
            use_case_config,
            "graph",
            data_hash,
            filters_hash,
            extra_tokens=extra_cache_tokens,
        )
        ttl = self._get_cache_ttl(cache_config, "graph")
        cache_context: Dict[str, Any] = {
            "use_case_id": use_case_id,
            "key": graph_cache_key,
            "ttl": ttl,
            "filters": filters,
        }

        if force_refresh:
            return None, cache_context

        cached_figure = self.cache_manager.get_cached_graph(graph_cache_key)
        if cached_figure is not None:
            logger.info(f"Cache HIT (graph) for {use_case_id}")
        else:
            logger.debug(f"Cache MISS (graph) for {use_case_id}")
        return cached_figure, cache_context

    def store_graph_cache(
        self,
        cache_context: Optional[Dict[str, Any]],
        figure: go.Figure,
        *,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Store figure in graph cache using context from resolve_graph_cache.

        Parameters
        ----------
        cache_context : Optional[Dict[str, Any]]
            Context returned by resolve_graph_cache.
        figure : go.Figure
            Figure to cache.
        metadata : Optional[Dict[str, Any]], default=None
            Additional cache metadata.
        """
        if not cache_context:
            return

        base_metadata: Dict[str, Any] = {
            "use_case_id": cache_context.get("use_case_id"),
            "filters": cache_context.get("filters"),
            "ttl": cache_context.get("ttl"),
        }
        if metadata:
            base_metadata.update(metadata)

        self.cache_manager.cache_graph(
            cache_context["key"],
            figure,
            metadata=base_metadata,
            ttl=cache_context.get("ttl"),
        )

    def _get_cache_ttl(self, cache_config: Dict[str, Any], layer: str) -> int:
        """
        Get TTL for cache layer.

        Parameters
        ----------
        cache_config : Dict[str, Any]
            Cache configuration.
        layer : str
            Cache layer.

        Returns
        -------
        int
            TTL in seconds.
        """
        layers = cache_config.get("layers", [])
        layer_config = next(
            (layer_def for layer_def in layers if layer_def.get("layer") == layer), None
        )

        if not layer_config:
            return 3600  # Default 1 hour

        return layer_config.get("ttl", 3600)

    def clear_cache(self, use_case_id: Optional[str] = None) -> None:
        """
        Clear cache for specific use case or all.

        Parameters
        ----------
        use_case_id : Optional[str], default=None
            Use case ID to clear. If None, clears all.
        """
        if use_case_id:
            # Clear specific use case (would need pattern matching)
            logger.info(f"Clearing cache for {use_case_id}")
        else:
            self.cache_manager.clear()
            logger.info("Cleared all plot caches")
