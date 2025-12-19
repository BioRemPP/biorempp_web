"""
Unit Tests for Application Services.

This module tests the application services including CacheService
and ProgressTracker.
"""

import time

import pytest

from biorempp_web.src.application.services.cache_service import CacheService
from biorempp_web.src.application.services.progress_tracker import ProgressTracker


class TestCacheService:
    """Test CacheService functionality."""

    def test_set_and_get(self):
        """Test basic set and get operations."""
        cache = CacheService()
        cache.set("key1", "value1")

        result = cache.get("key1")

        assert result == "value1"

    def test_get_nonexistent_returns_none(self):
        """Test getting nonexistent key returns None."""
        cache = CacheService()

        result = cache.get("nonexistent")

        assert result is None

    def test_delete(self):
        """Test deleting cache entry."""
        cache = CacheService()
        cache.set("key1", "value1")

        deleted = cache.delete("key1")
        result = cache.get("key1")

        assert deleted is True
        assert result is None

    def test_clear(self):
        """Test clearing entire cache."""
        cache = CacheService()
        cache.set("key1", "value1")
        cache.set("key2", "value2")

        cache.clear()

        assert cache.size() == 0

    def test_has(self):
        """Test checking if key exists."""
        cache = CacheService()
        cache.set("key1", "value1")

        assert cache.has("key1") is True
        assert cache.has("nonexistent") is False

    def test_size(self):
        """Test getting cache size."""
        cache = CacheService()
        cache.set("key1", "value1")
        cache.set("key2", "value2")

        assert cache.size() == 2

    def test_generate_hash_key(self):
        """Test hash key generation."""
        cache = CacheService()
        key1 = cache.generate_hash_key("content1")
        key2 = cache.generate_hash_key("content1")
        key3 = cache.generate_hash_key("content2")

        # Same content = same key
        assert key1 == key2
        # Different content = different key
        assert key1 != key3
        # Hash is 64 chars (SHA256)
        assert len(key1) == 64

    def test_eviction_when_full(self):
        """Test that oldest entry is evicted when cache is full."""
        cache = CacheService(max_size=2)
        cache.set("key1", "value1")
        time.sleep(0.01)
        cache.set("key2", "value2")
        cache.set("key3", "value3")  # Should evict key1

        assert cache.has("key1") is False
        assert cache.has("key2") is True
        assert cache.has("key3") is True

    def test_ttl_expiration(self):
        """Test that entries expire after TTL."""
        cache = CacheService(default_ttl_seconds=1)
        cache.set("key1", "value1", ttl_seconds=1)

        # Should exist immediately
        assert cache.get("key1") == "value1"

        # Wait for expiration
        time.sleep(1.1)

        # Should be expired
        assert cache.get("key1") is None