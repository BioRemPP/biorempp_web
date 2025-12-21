"""
Cache Module - Memory Caching Implementations.

Provides caching mechanisms for general data, pandas DataFrames, and Plotly
figures with LRU eviction, TTL support, and compression.

Classes
-------
MemoryCache
    In-memory LRU cache with TTL support
DataFrameCache
    Specialized cache for pandas DataFrames with compression
GraphCache
    Specialized cache for Plotly figures
GraphCacheManager
    Manager interface for graph caching operations
"""

from .dataframe_cache import DataFrameCache
from .graph_cache import GraphCache
from .graph_cache_manager import GraphCacheManager
from .memory_cache import MemoryCache

__all__ = [
    'MemoryCache',
    'DataFrameCache',
    'GraphCache',
    'GraphCacheManager'
]
