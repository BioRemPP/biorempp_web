"""
Unit tests for DataFrame Cache.
"""

import pytest
import pandas as pd
import hashlib
from src.infrastructure.cache.dataframe_cache import DataFrameCache


class TestDataFrameCache:
    """Test suite for DataFrameCache."""

    @pytest.fixture
    def small_dataframe(self):
        """Create small test DataFrame."""
        return pd.DataFrame({
            'A': range(10),
            'B': range(10, 20),
            'C': ['value'] * 10
        })

    @pytest.fixture
    def large_dataframe(self):
        """Create large DataFrame for compression testing."""
        return pd.DataFrame({
            'A': range(100000),
            'B': range(100000, 200000),
            'C': ['value'] * 100000
        })

    def test_initialization(self):
        """Test cache initialization."""
        cache = DataFrameCache(
            max_size=50,
            default_ttl=3600,
            compress_threshold=1024*1024
        )
        
        assert cache.max_size == 50
        assert cache.default_ttl == 3600
        assert cache.compress_threshold == 1024*1024

    def test_cache_small_dataframe(self, small_dataframe):
        """Test caching small DataFrame (no compression)."""
        cache = DataFrameCache()
        
        cache.cache_dataframe('test_df', small_dataframe)
        retrieved = cache.get_cached_dataframe('test_df')
        
        assert isinstance(retrieved, pd.DataFrame)
        assert retrieved.equals(small_dataframe)

    def test_cache_large_dataframe(self, large_dataframe):
        """Test caching large DataFrame (with compression)."""
        cache = DataFrameCache(compress_threshold=1024)  # Low threshold
        
        cache.cache_dataframe('large_df', large_dataframe)
        retrieved = cache.get_cached_dataframe('large_df')
        
        assert isinstance(retrieved, pd.DataFrame)
        assert retrieved.equals(large_dataframe)

    def test_get_nonexistent_dataframe(self):
        """Test getting non-existent DataFrame returns None."""
        cache = DataFrameCache()
        
        result = cache.get_cached_dataframe('nonexistent')
        
        assert result is None

    def test_generate_dataframe_key(self, small_dataframe):
        """Test DataFrame key generation."""
        cache = DataFrameCache()
        
        key1 = cache.generate_dataframe_key(small_dataframe, prefix='test')
        key2 = cache.generate_dataframe_key(small_dataframe, prefix='test')
        
        # Same DataFrame should generate same key
        assert key1 == key2
        assert key1.startswith('test_')

    def test_generate_key_different_dataframes(self):
        """Test that different DataFrames generate different keys."""
        cache = DataFrameCache()
        
        df1 = pd.DataFrame({'A': [1, 2, 3]})
        df2 = pd.DataFrame({'A': [4, 5, 6]})
        
        key1 = cache.generate_dataframe_key(df1)
        key2 = cache.generate_dataframe_key(df2)
        
        assert key1 != key2

    def test_cache_with_ttl(self, small_dataframe):
        """Test caching with TTL."""
        cache = DataFrameCache()
        
        cache.cache_dataframe('test_df', small_dataframe, ttl=3600)
        
        assert cache.exists('test_df') is True

    def test_cache_metadata(self, small_dataframe):
        """Test that cache stores metadata."""
        cache = DataFrameCache()
        
        cache.cache_dataframe('test_df', small_dataframe)
        
        # Get raw cache entry
        entry = cache.get('test_df')
        
        assert 'data' in entry
        assert 'is_compressed' in entry
        assert 'original_size_mb' in entry
        assert 'shape' in entry
        assert entry['shape'] == small_dataframe.shape

    def test_compression_flag(self, small_dataframe, large_dataframe):
        """Test compression flag is set correctly."""
        cache = DataFrameCache(compress_threshold=1024)
        
        # Cache small (no compression)
        cache.cache_dataframe('small', small_dataframe)
        small_entry = cache.get('small')
        
        # Cache large (with compression)
        cache.cache_dataframe('large', large_dataframe)
        large_entry = cache.get('large')
        
        assert small_entry['is_compressed'] is False
        assert large_entry['is_compressed'] is True

    def test_multiple_dataframes(self):
        """Test caching multiple DataFrames."""
        cache = DataFrameCache()
        
        df1 = pd.DataFrame({'A': [1, 2, 3]})
        df2 = pd.DataFrame({'B': [4, 5, 6]})
        df3 = pd.DataFrame({'C': [7, 8, 9]})
        
        cache.cache_dataframe('df1', df1)
        cache.cache_dataframe('df2', df2)
        cache.cache_dataframe('df3', df3)
        
        assert cache.size() == 3
        assert cache.get_cached_dataframe('df1').equals(df1)
        assert cache.get_cached_dataframe('df2').equals(df2)
        assert cache.get_cached_dataframe('df3').equals(df3)

    def test_dataframe_copy_isolation(self, small_dataframe):
        """Test that returned DataFrame is a copy."""
        cache = DataFrameCache()
        
        cache.cache_dataframe('test_df', small_dataframe)
        retrieved = cache.get_cached_dataframe('test_df')
        
        # Modify retrieved
        retrieved.loc[0, 'A'] = 999
        
        # Get again, should be unchanged
        retrieved2 = cache.get_cached_dataframe('test_df')
        
        assert retrieved2.loc[0, 'A'] != 999
