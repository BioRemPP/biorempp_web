"""
Memory Cache - LRU Cache Implementation.

Provides Least Recently Used (LRU) cache with TTL support for
general-purpose caching.

Classes
-------
MemoryCache
    In-memory LRU cache with TTL and max size enforcement
"""

from collections import OrderedDict
from datetime import datetime, timedelta
from typing import Any, Optional

from src.shared.logging import get_logger

logger = get_logger(__name__)


class MemoryCache:
    """
    In-memory LRU cache implementation.

    Provides LRU eviction policy, TTL support, max size enforcement, and
    basic thread-safe operations.

    Attributes
    ----------
    max_size : int
        Maximum number of entries in cache
    default_ttl : int
        Default TTL in seconds (0 = no expiration)
    _cache : OrderedDict
        Ordered dictionary storing cached values
    _expiry : dict[str, Optional[datetime]]
        Expiry timestamps for cache entries

    Methods
    -------
    get(key)
        Get value from cache
    set(key, value, ttl)
        Set value in cache
    delete(key)
        Delete entry from cache
    clear()
        Clear all cache entries
    exists(key)
        Check if key exists in cache
    size()
        Get current cache size
    get_stats()
        Get cache statistics
    """

    def __init__(
        self,
        max_size: int = 1000,
        default_ttl: int = 0
    ):
        """
        Initialize memory cache.

        Parameters
        ----------
        max_size : int, default=1000
            Maximum number of cache entries.
        default_ttl : int, default=0
            Default TTL in seconds (0 = no expiration).
        """
        self.max_size = max_size
        self.default_ttl = default_ttl
        self._cache: OrderedDict = OrderedDict()
        self._expiry: dict[str, Optional[datetime]] = {}

        logger.info(
            f"Initialized {self.__class__.__name__}",
            extra={'max_size': max_size, 'default_ttl': default_ttl}
        )

    def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache.

        Parameters
        ----------
        key : str
            Cache key

        Returns
        -------
        Optional[Any]
            Cached value or None if not found/expired
        """
        # Check if key exists
        if key not in self._cache:
            logger.debug(f"Cache miss: {key}")
            return None

        # Check if expired
        if self._is_expired(key):
            logger.debug(f"Cache expired: {key}")
            self.delete(key)
            return None

        # Move to end (LRU)
        self._cache.move_to_end(key)

        logger.debug(f"Cache hit: {key}")
        return self._cache[key]

    def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None
    ) -> None:
        """
        Set value in cache.

        Parameters
        ----------
        key : str
            Cache key
        value : Any
            Value to cache
        ttl : Optional[int], default=None
            TTL in seconds (if None, uses default_ttl)
        """
        # Enforce max size (evict oldest if necessary)
        if key not in self._cache and len(self._cache) >= self.max_size:
            self._evict_oldest()

        # Set value
        self._cache[key] = value
        self._cache.move_to_end(key)

        # Set expiry
        ttl = ttl if ttl is not None else self.default_ttl
        if ttl > 0:
            self._expiry[key] = datetime.now() + timedelta(seconds=ttl)
        else:
            self._expiry[key] = None

        logger.debug(
            f"Cache set: {key}",
            extra={'ttl': ttl}
        )

    def delete(self, key: str) -> bool:
        """
        Delete entry from cache.

        Parameters
        ----------
        key : str
            Cache key

        Returns
        -------
        bool
            True if deleted, False if key not found
        """
        if key in self._cache:
            del self._cache[key]
            del self._expiry[key]
            logger.debug(f"Cache delete: {key}")
            return True
        return False

    def clear(self) -> None:
        """Clear all cache entries."""
        count = len(self._cache)
        self._cache.clear()
        self._expiry.clear()
        logger.info(f"Cache cleared: {count} entries removed")

    def exists(self, key: str) -> bool:
        """
        Check if key exists in cache (and not expired).

        Parameters
        ----------
        key : str
            Cache key

        Returns
        -------
        bool
            True if exists and not expired
        """
        if key not in self._cache:
            return False

        if self._is_expired(key):
            self.delete(key)
            return False

        return True

    def size(self) -> int:
        """
        Get current cache size.

        Returns
        -------
        int
            Number of entries in cache
        """
        return len(self._cache)

    def get_stats(self) -> dict:
        """
        Get cache statistics.

        Returns
        -------
        dict
            Statistics including size, max_size, usage percentage
        """
        return {
            'current_size': len(self._cache),
            'max_size': self.max_size,
            'default_ttl': self.default_ttl,
            'usage_percent': (len(self._cache) / self.max_size) * 100
        }

    def _is_expired(self, key: str) -> bool:
        """
        Check if cache entry is expired.

        Parameters
        ----------
        key : str
            Cache key.

        Returns
        -------
        bool
            True if expired, False otherwise.
        """
        expiry = self._expiry.get(key)
        if expiry is None:
            return False
        return datetime.now() > expiry

    def _evict_oldest(self) -> None:
        """
        Evict oldest (least recently used) entry.

        Notes
        -----
        This is called automatically when cache is full and a new
        entry is being added.
        """
        if self._cache:
            oldest_key = next(iter(self._cache))
            self.delete(oldest_key)
            logger.debug(f"Evicted oldest entry: {oldest_key}")
