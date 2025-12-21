"""
Unit tests for Memory Cache.
"""

import pytest
from datetime import datetime, timedelta
from src.infrastructure.cache.memory_cache import MemoryCache


class TestMemoryCache:
    """Test suite for MemoryCache."""

    def test_initialization(self):
        """Test cache initialization."""
        cache = MemoryCache(max_size=100, default_ttl=3600)
        
        assert cache.max_size == 100
        assert cache.default_ttl == 3600
        assert cache.size() == 0

    def test_set_and_get(self):
        """Test basic set and get operations."""
        cache = MemoryCache()
        
        cache.set('key1', 'value1')
        value = cache.get('key1')
        
        assert value == 'value1'

    def test_get_nonexistent_key(self):
        """Test getting non-existent key returns None."""
        cache = MemoryCache()
        
        value = cache.get('nonexistent')
        
        assert value is None

    def test_set_with_ttl(self):
        """Test TTL expiration."""
        cache = MemoryCache(default_ttl=0)
        
        # Set with 1 second TTL
        cache.set('key1', 'value1', ttl=1)
        
        # Should exist immediately
        assert cache.exists('key1') is True
        
        # Manually set expiry to past (simulate expiration)
        cache._expiry['key1'] = datetime.now() - timedelta(seconds=10)
        
        # Should be expired
        assert cache.exists('key1') is False
        assert cache.get('key1') is None

    def test_delete(self):
        """Test deleting cache entry."""
        cache = MemoryCache()
        
        cache.set('key1', 'value1')
        assert cache.exists('key1') is True
        
        result = cache.delete('key1')
        
        assert result is True
        assert cache.exists('key1') is False

    def test_delete_nonexistent(self):
        """Test deleting non-existent key."""
        cache = MemoryCache()
        
        result = cache.delete('nonexistent')
        
        assert result is False

    def test_clear(self):
        """Test clearing all cache entries."""
        cache = MemoryCache()
        
        cache.set('key1', 'value1')
        cache.set('key2', 'value2')
        cache.set('key3', 'value3')
        
        assert cache.size() == 3
        
        cache.clear()
        
        assert cache.size() == 0

    def test_lru_eviction(self):
        """Test LRU eviction when max_size reached."""
        cache = MemoryCache(max_size=3)
        
        cache.set('key1', 'value1')
        cache.set('key2', 'value2')
        cache.set('key3', 'value3')
        
        # Add 4th item, should evict key1 (oldest)
        cache.set('key4', 'value4')
        
        assert cache.size() == 3
        assert cache.get('key1') is None
        assert cache.get('key4') == 'value4'

    def test_lru_ordering(self):
        """Test that access updates LRU order."""
        cache = MemoryCache(max_size=3)
        
        cache.set('key1', 'value1')
        cache.set('key2', 'value2')
        cache.set('key3', 'value3')
        
        # Access key1 (moves to end)
        cache.get('key1')
        
        # Add key4, should evict key2 (now oldest)
        cache.set('key4', 'value4')
        
        assert cache.get('key1') == 'value1'  # Still exists
        assert cache.get('key2') is None  # Evicted
        assert cache.get('key4') == 'value4'

    def test_size(self):
        """Test size tracking."""
        cache = MemoryCache()
        
        assert cache.size() == 0
        
        cache.set('key1', 'value1')
        assert cache.size() == 1
        
        cache.set('key2', 'value2')
        assert cache.size() == 2
        
        cache.delete('key1')
        assert cache.size() == 1

    def test_exists(self):
        """Test exists check."""
        cache = MemoryCache()
        
        assert cache.exists('key1') is False
        
        cache.set('key1', 'value1')
        assert cache.exists('key1') is True

    def test_get_stats(self):
        """Test cache statistics."""
        cache = MemoryCache(max_size=100, default_ttl=3600)
        
        cache.set('key1', 'value1')
        cache.set('key2', 'value2')
        
        stats = cache.get_stats()
        
        assert stats['current_size'] == 2
        assert stats['max_size'] == 100
        assert stats['default_ttl'] == 3600
        assert stats['usage_percent'] == 2.0

    def test_store_different_types(self):
        """Test storing different data types."""
        cache = MemoryCache()
        
        cache.set('string', 'value')
        cache.set('int', 42)
        cache.set('float', 3.14)
        cache.set('list', [1, 2, 3])
        cache.set('dict', {'key': 'value'})
        
        assert cache.get('string') == 'value'
        assert cache.get('int') == 42
        assert cache.get('float') == 3.14
        assert cache.get('list') == [1, 2, 3]
        assert cache.get('dict') == {'key': 'value'}

    def test_override_existing_key(self):
        """Test overriding existing key."""
        cache = MemoryCache()
        
        cache.set('key1', 'value1')
        assert cache.get('key1') == 'value1'
        
        cache.set('key1', 'value2')
        assert cache.get('key1') == 'value2'
        assert cache.size() == 1  # Size shouldn't increase

    def test_default_ttl_zero_means_no_expiration(self):
        """Test that TTL=0 means no expiration."""
        cache = MemoryCache(default_ttl=0)
        
        cache.set('key1', 'value1')
        
        # Check internal expiry is None
        assert cache._expiry['key1'] is None
        
        # Should never expire
        assert cache.exists('key1') is True
