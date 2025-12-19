"""
Cache Service - Application-Level Caching with Hash-Based Keys.

Provides caching functionality for expensive operations like database merges.
Uses hash-based keys for cache invalidation and supports multiple data types
(DataFrame, Dataset, MergedDataDTO).

Classes
-------
CacheService
    Manages application-level caching with TTL and size limits
"""

import hashlib
import time
from typing import Any, Dict, Optional


class CacheService:
    """
    Manage application-level caching with hash-based keys.

    Provides caching for expensive operations with automatic expiration, size
    limits, and hash-based key generation.

    Parameters
    ----------
    max_size : int, default=100
        Maximum number of cached items
    default_ttl_seconds : int, default=3600
        Default time-to-live in seconds (1 hour)

    Attributes
    ----------
    _cache : Dict[str, Dict[str, Any]]
        Internal cache storage
    _max_size : int
        Maximum cache size
    _default_ttl : int
        Default TTL

    Methods
    -------
    set(key, value, ttl_seconds)
        Store value in cache
    get(key)
        Retrieve value from cache
    delete(key)
        Remove value from cache
    clear()
        Clear entire cache
    generate_hash_key(content)
        Generate hash-based cache key
    has(key)
        Check if key exists and is valid
    size()
        Get current cache size

    Notes
    -----
    Cache entries structure:
    {
        'key': {
            'value': cached_value,
            'timestamp': creation_time,
            'ttl': time_to_live_seconds
        }
    }

    Uses SHA256 for hash key generation.
    """

    def __init__(self, max_size: int = 100, default_ttl_seconds: int = 3600) -> None:
        """
        Initialize cache service.

        Parameters
        ----------
        max_size : int, default=100
            Maximum cached items
        default_ttl_seconds : int, default=3600
            Default TTL (1 hour)
        """
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._max_size = max_size
        self._default_ttl = default_ttl_seconds

    def set(self, key: str, value: Any, ttl_seconds: Optional[int] = None) -> None:
        """
        Store value in cache.

        Parameters
        ----------
        key : str
            Cache key
        value : Any
            Value to cache
        ttl_seconds : Optional[int]
            Time-to-live (uses default if None)

        Notes
        -----
        If cache is full, removes oldest entry (FIFO eviction).
        """
        # Check size limit and evict if needed
        if len(self._cache) >= self._max_size:
            self._evict_oldest()

        ttl = ttl_seconds if ttl_seconds is not None else self._default_ttl

        self._cache[key] = {
            "value": value,
            "timestamp": time.time(),
            "ttl": ttl,
        }

    def get(self, key: str) -> Optional[Any]:
        """
        Retrieve value from cache.

        Parameters
        ----------
        key : str
            Cache key

        Returns
        -------
        Optional[Any]
            Cached value or None if not found/expired

        Notes
        -----
        Automatically removes expired entries.
        """
        if key not in self._cache:
            return None

        entry = self._cache[key]

        # Check expiration
        if self._is_expired(entry):
            del self._cache[key]
            return None

        return entry["value"]

    def delete(self, key: str) -> bool:
        """
        Remove value from cache.

        Parameters
        ----------
        key : str
            Cache key

        Returns
        -------
        bool
            True if key was deleted, False if not found
        """
        if key in self._cache:
            del self._cache[key]
            return True
        return False

    def clear(self) -> None:
        """Clear entire cache."""
        self._cache.clear()

    def generate_hash_key(self, content: str) -> str:
        """
        Generate SHA256 hash-based cache key.

        Parameters
        ----------
        content : str
            Content to hash (e.g., upload content or dataset identifier)

        Returns
        -------
        str
            SHA256 hash hexadecimal string

        Notes
        -----
        - Same content always generates same key (deterministic)
        - Compatible with legacy cache key generation
        """
        return hashlib.sha256(content.encode("utf-8")).hexdigest()

    def has(self, key: str) -> bool:
        """
        Check if key exists and is valid (not expired).

        Parameters
        ----------
        key : str
            Cache key

        Returns
        -------
        bool
            True if key exists and not expired
        """
        if key not in self._cache:
            return False

        entry = self._cache[key]
        if self._is_expired(entry):
            del self._cache[key]
            return False

        return True

    def size(self) -> int:
        """
        Get current cache size (number of entries).

        Returns
        -------
        int
            Number of cached entries
        """
        # Clean expired entries first
        self._clean_expired()
        return len(self._cache)

    def _is_expired(self, entry: Dict[str, Any]) -> bool:
        """
        Check if cache entry is expired.

        Parameters
        ----------
        entry : Dict[str, Any]
            Cache entry

        Returns
        -------
        bool
            True if expired
        """
        elapsed = time.time() - entry["timestamp"]
        return elapsed > entry["ttl"]

    def _evict_oldest(self) -> None:
        """
        Evict oldest cache entry (FIFO eviction policy).

        Notes
        -----
        Called automatically when cache reaches max_size.
        """
        if not self._cache:
            return

        # Find oldest entry
        oldest_key = min(self._cache.keys(), key=lambda k: self._cache[k]["timestamp"])
        del self._cache[oldest_key]

    def _clean_expired(self) -> None:
        """
        Remove all expired entries.

        Notes
        -----
        Called by size() to ensure accurate count.
        """
        expired_keys = [
            key for key, entry in self._cache.items() if self._is_expired(entry)
        ]
        for key in expired_keys:
            del self._cache[key]
