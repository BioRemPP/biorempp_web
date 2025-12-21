"""
Unit tests for Graph Cache.
"""

import plotly.graph_objects as go
import pytest

from src.infrastructure.cache.graph_cache import GraphCache


class TestGraphCache:
    """Test suite for GraphCache."""

    @pytest.fixture
    def sample_figure(self):
        """Create sample Plotly figure."""
        return go.Figure(
            data=go.Bar(x=['A', 'B', 'C'], y=[1, 3, 2]),
            layout=go.Layout(title='Test Chart')
        )

    def test_initialization(self):
        """Test cache initialization."""
        cache = GraphCache(max_size=100, default_ttl=1800)
        
        assert cache.max_size == 100
        assert cache.default_ttl == 1800

    def test_cache_figure(self, sample_figure):
        """Test caching Plotly figure."""
        cache = GraphCache()
        
        cache.cache_figure('test_fig', sample_figure)
        
        assert cache.exists('test_fig') is True

    def test_get_cached_figure(self, sample_figure):
        """Test retrieving cached figure."""
        cache = GraphCache()
        
        cache.cache_figure('test_fig', sample_figure)
        retrieved = cache.get_cached_figure('test_fig')
        
        assert isinstance(retrieved, go.Figure)
        assert retrieved.layout.title.text == 'Test Chart'

    def test_get_nonexistent_figure(self):
        """Test getting non-existent figure returns None."""
        cache = GraphCache()
        
        result = cache.get_cached_figure('nonexistent')
        
        assert result is None

    def test_generate_figure_key(self):
        """Test figure key generation."""
        cache = GraphCache()
        
        key = cache.generate_figure_key(
            analysis_id='UC1_1',
            filter_values={'pathway': 'Glycolysis', 'sample': 'S1'}
        )
        
        assert isinstance(key, str)
        assert key.startswith('UC1_1_')

    def test_generate_key_consistency(self):
        """Test that same inputs generate same key."""
        cache = GraphCache()
        
        filters = {'pathway': 'Glycolysis', 'sample': 'S1'}
        
        key1 = cache.generate_figure_key('UC1_1', filters)
        key2 = cache.generate_figure_key('UC1_1', filters)
        
        assert key1 == key2

    def test_generate_key_different_filters(self):
        """Test that different filters generate different keys."""
        cache = GraphCache()
        
        key1 = cache.generate_figure_key(
            'UC1_1',
            {'pathway': 'Glycolysis'}
        )
        key2 = cache.generate_figure_key(
            'UC1_1',
            {'pathway': 'TCA Cycle'}
        )
        
        assert key1 != key2

    def test_cache_multiple_figures(self):
        """Test caching multiple figures."""
        cache = GraphCache()
        
        fig1 = go.Figure(data=go.Bar(x=[1], y=[1]))
        fig2 = go.Figure(data=go.Scatter(x=[1], y=[1]))
        
        cache.cache_figure('fig1', fig1)
        cache.cache_figure('fig2', fig2)
        
        assert cache.size() == 2

    def test_figure_data_preservation(self, sample_figure):
        """Test that figure data is preserved."""
        cache = GraphCache()
        
        cache.cache_figure('test_fig', sample_figure)
        retrieved = cache.get_cached_figure('test_fig')
        
        # Check data preservation
        original_data = sample_figure.data[0]
        retrieved_data = retrieved.data[0]
        
        assert list(retrieved_data.x) == list(original_data.x)
        assert list(retrieved_data.y) == list(original_data.y)

    def test_cache_with_config(self):
        """Test caching with additional config."""
        cache = GraphCache()
        
        key = cache.generate_figure_key(
            'UC1_1',
            {'pathway': 'Glycolysis'},
            config={'height': 600, 'template': 'simple_white'}
        )
        
        assert isinstance(key, str)
