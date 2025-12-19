"""
Unit tests for PlotService.

This module tests the PlotService class, which orchestrates plot generation
with multi-layer caching.

Test Categories:
- Initialization: Test service initialization
- Plot Generation: Test complete plot generation pipeline
- Caching: Test cache hit/miss scenarios
- Data Hashing: Test data and filter hash generation
- Cache Key Generation: Test cache key templates
- TTL Configuration: Test TTL retrieval from config
- Error Handling: Test error scenarios
- Cache Clearing: Test cache invalidation
"""

import pytest
import pandas as pd
import plotly.graph_objects as go
from unittest.mock import Mock

from src.application.plot_services.plot_service import PlotService
from src.application.plot_services.plot_config_loader import PlotConfigLoader
from src.application.plot_services.plot_factory import PlotFactory
from src.infrastructure.cache import GraphCacheManager


# ============================================================================
# INITIALIZATION TESTS
# ============================================================================

class TestPlotServiceInitialization:
    """Test PlotService initialization."""

    def test_initialization_creates_dependencies(self):
        """Test that initialization creates all dependencies."""
        service = PlotService()

        assert hasattr(service, 'config_loader')
        assert hasattr(service, 'factory')
        assert hasattr(service, 'cache_manager')
        assert isinstance(
            service.config_loader, PlotConfigLoader
        )
        assert isinstance(service.factory, PlotFactory)
        assert isinstance(
            service.cache_manager, GraphCacheManager
        )

    def test_initialization_components_are_instances(self, plot_service):
        """Test that all components are properly instantiated."""
        assert plot_service.config_loader is not None
        assert plot_service.factory is not None
        assert plot_service.cache_manager is not None


# ============================================================================
# DATA HASHING TESTS
# ============================================================================

class TestDataHashing:
    """Test data hash generation."""

    def test_generate_data_hash_consistency(
        self, plot_service, sample_plot_dataframe
    ):
        """Test that same DataFrame generates same hash."""
        hash1 = plot_service._generate_data_hash(
            sample_plot_dataframe
        )
        hash2 = plot_service._generate_data_hash(
            sample_plot_dataframe
        )

        assert hash1 == hash2
        assert isinstance(hash1, str)
        assert len(hash1) == 16  # MD5 truncated to 16 chars

    def test_generate_data_hash_different_data(self, plot_service):
        """Test that different DataFrames generate different hashes."""
        df1 = pd.DataFrame({'A': [1, 2, 3], 'B': [4, 5, 6]})
        df2 = pd.DataFrame({'A': [7, 8, 9], 'B': [10, 11, 12]})

        hash1 = plot_service._generate_data_hash(df1)
        hash2 = plot_service._generate_data_hash(df2)

        assert hash1 != hash2

    def test_generate_data_hash_empty_dataframe(self, plot_service):
        """Test hash generation with empty DataFrame."""
        df = pd.DataFrame()

        hash_value = plot_service._generate_data_hash(df)

        assert isinstance(hash_value, str)
        assert len(hash_value) == 16

    def test_generate_data_hash_different_columns(self, plot_service):
        """Test that DataFrames with different columns generate different hashes."""
        df1 = pd.DataFrame({'A': [1, 2, 3]})
        df2 = pd.DataFrame({'B': [1, 2, 3]})

        hash1 = plot_service._generate_data_hash(df1)
        hash2 = plot_service._generate_data_hash(df2)

        assert hash1 != hash2

    def test_generate_data_hash_different_shapes(self, plot_service):
        """Test that DataFrames with different shapes generate different hashes."""
        df1 = pd.DataFrame({'A': [1, 2, 3]})
        df2 = pd.DataFrame({'A': [1, 2]})

        hash1 = plot_service._generate_data_hash(df1)
        hash2 = plot_service._generate_data_hash(df2)

        assert hash1 != hash2

    def test_generate_data_hash_column_order_matters(
        self, plot_service
    ):
        """Test that column order is considered in hashing."""
        # Column names sorted, so order should NOT matter
        df1 = pd.DataFrame({'A': [1], 'B': [2]})
        df2 = pd.DataFrame({'B': [2], 'A': [1]})

        hash1 = plot_service._generate_data_hash(df1)
        hash2 = plot_service._generate_data_hash(df2)

        # Hashes are DIFFERENT because data.values.tobytes()
        # is sensitive to column order
        assert hash1 != hash2


# ============================================================================
# FILTER HASHING TESTS
# ============================================================================

class TestFilterHashing:
    """Test filter hash generation."""

    def test_generate_filters_hash_consistency(self, plot_service):
        """Test that same filters generate same hash."""
        filters = {'uc-2-1-range-slider': [10, 50], 'sample': 'S1'}

        hash1 = plot_service._generate_filters_hash(filters)
        hash2 = plot_service._generate_filters_hash(filters)

        assert hash1 == hash2
        assert isinstance(hash1, str)
        assert len(hash1) == 16

    def test_generate_filters_hash_different_filters(self, plot_service):
        """Test that different filters generate different hashes."""
        filters1 = {'uc-2-1-range-slider': [10, 50]}
        filters2 = {'uc-2-1-range-slider': [20, 60]}

        hash1 = plot_service._generate_filters_hash(filters1)
        hash2 = plot_service._generate_filters_hash(filters2)

        assert hash1 != hash2

    def test_generate_filters_hash_empty_filters(self, plot_service):
        """Test hash generation with empty filters."""
        filters = {}

        hash_value = plot_service._generate_filters_hash(filters)

        assert isinstance(hash_value, str)
        assert len(hash_value) == 16

    def test_generate_filters_hash_key_order_independence(
        self, plot_service
    ):
        """Test that filter key order doesn't affect hash."""
        filters1 = {'a': 1, 'b': 2, 'c': 3}
        filters2 = {'c': 3, 'a': 1, 'b': 2}

        hash1 = plot_service._generate_filters_hash(filters1)
        hash2 = plot_service._generate_filters_hash(filters2)

        # JSON dumps with sort_keys=True ensures consistency
        assert hash1 == hash2

    def test_generate_filters_hash_nested_structures(self, plot_service):
        """Test hash generation with nested filter structures."""
        filters = {
            'range': [10, 50],
            'categories': ['A', 'B', 'C'],
            'settings': {'enabled': True, 'value': 42}
        }

        hash_value = plot_service._generate_filters_hash(filters)

        assert isinstance(hash_value, str)
        assert len(hash_value) == 16


# ============================================================================
# CACHE KEY GENERATION TESTS
# ============================================================================

class TestCacheKeyGeneration:
    """Test cache key generation from templates."""

    def test_get_cache_key_with_template(self, plot_service, sample_plot_config):
        """Test cache key generation using template."""
        data_hash = "abc123def456"
        filters_hash = "xyz789uvw012"

        key = plot_service._get_cache_key(
            sample_plot_config,
            'graph',
            data_hash,
            filters_hash
        )

        assert 'graph' in key
        assert data_hash in key
        assert filters_hash in key
        assert key == f"graph_{data_hash}_{filters_hash}"

    def test_get_cache_key_fallback_when_layer_not_found(
        self, plot_service, sample_plot_config
    ):
        """Test fallback cache key when layer not in config."""
        data_hash = "abc123"
        filters_hash = "xyz789"

        # Request non-existent layer
        key = plot_service._get_cache_key(
            sample_plot_config,
            'nonexistent_layer',
            data_hash,
            filters_hash
        )

        # Should return fallback format
        expected = f"nonexistent_layer_{data_hash}_{filters_hash}"
        assert key == expected

    def test_get_cache_key_with_no_cache_config(self, plot_service):
        """Test cache key generation when config has no cache section."""
        config = {
            'metadata': {'use_case_id': 'UC-TEST'},
            'visualization': {'strategy': 'BarChartStrategy'}
        }

        data_hash = "abc123"
        filters_hash = "xyz789"

        key = plot_service._get_cache_key(
            config,
            'graph',
            data_hash,
            filters_hash
        )

        # Should use fallback
        assert key == f"graph_{data_hash}_{filters_hash}"

    def test_get_cache_key_multiple_layers(
        self, plot_service, sample_plot_config
    ):
        """Test cache key generation for different layers."""
        data_hash = "abc123"
        filters_hash = "xyz789"

        graph_key = plot_service._get_cache_key(
            sample_plot_config, 'graph', data_hash, filters_hash
        )
        df_key = plot_service._get_cache_key(
            sample_plot_config, 'dataframe', data_hash, filters_hash
        )

        # Keys should be different for different layers
        assert graph_key != df_key
        assert 'graph' in graph_key
        assert 'df' in df_key


# ============================================================================
# TTL CONFIGURATION TESTS
# ============================================================================

class TestCacheTTL:
    """Test TTL retrieval from configuration."""

    def test_get_cache_ttl_from_config(
        self, plot_service, sample_plot_config
    ):
        """Test TTL retrieval from cache config."""
        cache_config = sample_plot_config['performance']['cache']

        ttl = plot_service._get_cache_ttl(cache_config, 'graph')

        assert ttl == 3600

    def test_get_cache_ttl_different_layers(
        self, plot_service, sample_plot_config
    ):
        """Test TTL for different cache layers."""
        cache_config = sample_plot_config['performance']['cache']

        graph_ttl = plot_service._get_cache_ttl(
            cache_config, 'graph'
        )
        df_ttl = plot_service._get_cache_ttl(
            cache_config, 'dataframe'
        )

        assert graph_ttl == 3600
        assert df_ttl == 7200

    def test_get_cache_ttl_default_when_not_found(self, plot_service):
        """Test default TTL when layer not found."""
        cache_config = {
            'enabled': True,
            'layers': [
                {'layer': 'graph', 'ttl': 3600}
            ]
        }

        ttl = plot_service._get_cache_ttl(cache_config, 'nonexistent')

        assert ttl == 3600  # Default

    def test_get_cache_ttl_default_when_ttl_missing(self, plot_service):
        """Test default TTL when layer exists but has no TTL."""
        cache_config = {
            'enabled': True,
            'layers': [
                {'layer': 'graph', 'key_template': 'graph_{data_hash}'}
                # No ttl specified
            ]
        }

        ttl = plot_service._get_cache_ttl(cache_config, 'graph')

        assert ttl == 3600  # Default


# ============================================================================
# PLOT GENERATION TESTS WITH MOCKING
# ============================================================================

class TestPlotGeneration:
    """Test complete plot generation pipeline."""

    def test_generate_plot_calls_dependencies(
        self, plot_service, sample_plot_dataframe
    ):
        """Test that generate_plot calls all required dependencies."""
        # Mock dependencies
        plot_service.config_loader = Mock()
        plot_service.factory = Mock()
        plot_service.cache_manager = Mock()

        # Setup mock returns
        mock_config = {
            'metadata': {'use_case_id': 'UC-2.1'},
            'visualization': {'strategy': 'BarChartStrategy'},
            'performance': {
                'cache': {
                    'enabled': False  # Disable caching to test generation path
                }
            }
        }
        plot_service.config_loader.load_config.return_value = mock_config

        # Mock strategy
        mock_strategy = Mock()
        mock_figure = go.Figure()
        mock_strategy.generate_plot.return_value = mock_figure
        plot_service.factory.create_strategy.return_value = mock_strategy

        # Execute
        result = plot_service.generate_plot(
            'UC-2.1', sample_plot_dataframe
        )

        # Assertions
        plot_service.config_loader.load_config.assert_called_once_with(
            'UC-2.1', force_reload=False
        )
        call_config = mock_config
        plot_service.factory.create_strategy.assert_called_once_with(
            call_config
        )
        mock_strategy.generate_plot.assert_called_once()
        assert result == mock_figure

    def test_generate_plot_with_filters(
        self, plot_service, sample_plot_dataframe
    ):
        """Test plot generation with filters."""
        # Mock dependencies
        plot_service.config_loader = Mock()
        plot_service.factory = Mock()
        plot_service.cache_manager = Mock()

        mock_config = {
            'metadata': {'use_case_id': 'UC-2.1'},
            'visualization': {'strategy': 'BarChartStrategy'},
            'performance': {'cache': {'enabled': False}}
        }
        plot_service.config_loader.load_config.return_value = mock_config

        mock_strategy = Mock()
        mock_figure = go.Figure()
        mock_strategy.generate_plot.return_value = mock_figure
        plot_service.factory.create_strategy.return_value = mock_strategy

        filters = {'uc-2-1-range-slider': [10, 50]}

        # Execute
        plot_service.generate_plot(
            'UC-2.1',
            sample_plot_dataframe,
            filters=filters
        )

        # Verify filters passed to strategy
        call_kwargs = mock_strategy.generate_plot.call_args[1]
        assert call_kwargs['filters'] == filters

    def test_generate_plot_with_force_refresh(
        self, plot_service, sample_plot_dataframe
    ):
        """Test plot generation with force_refresh flag."""
        plot_service.config_loader = Mock()
        plot_service.factory = Mock()
        plot_service.cache_manager = Mock()

        mock_config = {
            'metadata': {'use_case_id': 'UC-2.1'},
            'visualization': {'strategy': 'BarChartStrategy'},
            'performance': {'cache': {'enabled': False}}
        }
        plot_service.config_loader.load_config.return_value = mock_config

        mock_strategy = Mock()
        mock_figure = go.Figure()
        mock_strategy.generate_plot.return_value = mock_figure
        plot_service.factory.create_strategy.return_value = mock_strategy

        # Execute with force_refresh
        plot_service.generate_plot(
            'UC-2.1',
            sample_plot_dataframe,
            force_refresh=True
        )

        # Verify force_reload passed to config loader
        plot_service.config_loader.load_config.assert_called_once_with(
            'UC-2.1', force_reload=True
        )


# ============================================================================
# CACHING BEHAVIOR TESTS
# ============================================================================

class TestCachingBehavior:
    """Test caching scenarios."""

    def test_cache_hit_returns_cached_figure(
        self, plot_service, sample_plot_dataframe
    ):
        """Test that cache hit returns cached figure without regeneration."""
        # Mock dependencies
        plot_service.config_loader = Mock()
        plot_service.factory = Mock()
        plot_service.cache_manager = Mock()

        mock_config = {
            'metadata': {'use_case_id': 'UC-2.1'},
            'visualization': {'strategy': 'BarChartStrategy'},
            'performance': {
                'cache': {
                    'enabled': True,
                    'layers': [
                        {
                            'layer': 'graph',
                            'key_template': 'graph_{data_hash}_{filters_hash}',
                            'ttl': 3600
                        }
                    ]
                }
            }
        }
        plot_service.config_loader.load_config.return_value = mock_config

        # Mock cache hit
        cached_figure = go.Figure()
        plot_service.cache_manager.get_cached_graph.return_value = cached_figure

        # Execute
        result = plot_service.generate_plot('UC-2.1', sample_plot_dataframe)

        # Assertions
        assert result == cached_figure
        # Factory should NOT be called on cache hit
        plot_service.factory.create_strategy.assert_not_called()

    def test_cache_miss_generates_and_caches(
        self, plot_service, sample_plot_dataframe
    ):
        """Test that cache miss generates plot and caches it."""
        # Mock dependencies
        plot_service.config_loader = Mock()
        plot_service.factory = Mock()
        plot_service.cache_manager = Mock()

        mock_config = {
            'metadata': {'use_case_id': 'UC-2.1'},
            'visualization': {'strategy': 'BarChartStrategy'},
            'performance': {
                'cache': {
                    'enabled': True,
                    'layers': [
                        {
                            'layer': 'graph',
                            'key_template': 'graph_{data_hash}_{filters_hash}',
                            'ttl': 3600
                        }
                    ]
                }
            }
        }
        plot_service.config_loader.load_config.return_value = mock_config

        # Mock cache miss
        plot_service.cache_manager.get_cached_graph.return_value = None

        # Mock strategy
        mock_strategy = Mock()
        mock_figure = go.Figure()
        mock_strategy.generate_plot.return_value = mock_figure
        plot_service.factory.create_strategy.return_value = mock_strategy

        # Execute
        result = plot_service.generate_plot('UC-2.1', sample_plot_dataframe)

        # Assertions
        plot_service.factory.create_strategy.assert_called_once()
        mock_strategy.generate_plot.assert_called_once()
        plot_service.cache_manager.cache_graph.assert_called_once()
        assert result == mock_figure

    def test_cache_disabled_skips_cache_check(
        self, plot_service, sample_plot_dataframe
    ):
        """Test that disabled cache skips cache operations."""
        # Mock dependencies
        plot_service.config_loader = Mock()
        plot_service.factory = Mock()
        plot_service.cache_manager = Mock()

        mock_config = {
            'metadata': {'use_case_id': 'UC-2.1'},
            'visualization': {'strategy': 'BarChartStrategy'},
            'performance': {
                'cache': {
                    'enabled': False
                }
            }
        }
        plot_service.config_loader.load_config.return_value = mock_config

        mock_strategy = Mock()
        mock_figure = go.Figure()
        mock_strategy.generate_plot.return_value = mock_figure
        plot_service.factory.create_strategy.return_value = mock_strategy

        # Execute
        result = plot_service.generate_plot('UC-2.1', sample_plot_dataframe)

        # Cache should NOT be checked or written
        plot_service.cache_manager.get_cached_graph.assert_not_called()
        plot_service.cache_manager.cache_graph.assert_not_called()

    def test_force_refresh_bypasses_cache(
        self, plot_service, sample_plot_dataframe
    ):
        """Test that force_refresh bypasses cache check."""
        # Mock dependencies
        plot_service.config_loader = Mock()
        plot_service.factory = Mock()
        plot_service.cache_manager = Mock()

        mock_config = {
            'metadata': {'use_case_id': 'UC-2.1'},
            'visualization': {'strategy': 'BarChartStrategy'},
            'performance': {
                'cache': {
                    'enabled': True,
                    'layers': [
                        {
                            'layer': 'graph',
                            'key_template': 'graph_{data_hash}_{filters_hash}',
                            'ttl': 3600
                        }
                    ]
                }
            }
        }
        plot_service.config_loader.load_config.return_value = mock_config

        mock_strategy = Mock()
        mock_figure = go.Figure()
        mock_strategy.generate_plot.return_value = mock_figure
        plot_service.factory.create_strategy.return_value = mock_strategy

        # Execute with force_refresh
        plot_service.generate_plot(
            'UC-2.1',
            sample_plot_dataframe,
            force_refresh=True
        )

        # Cache check should be skipped
        cache_mgr = plot_service.cache_manager
        cache_mgr.get_cached_graph.assert_not_called()
        # But result should still be cached
        cache_mgr.cache_graph.assert_called_once()


# ============================================================================
# ERROR HANDLING TESTS
# ============================================================================

class TestErrorHandling:
    """Test error handling scenarios."""

    def test_generate_plot_propagates_config_errors(
        self, plot_service, sample_plot_dataframe
    ):
        """Test that configuration errors are propagated."""
        plot_service.config_loader = Mock()
        plot_service.config_loader.load_config.side_effect = FileNotFoundError(
            "Config not found"
        )

        with pytest.raises(FileNotFoundError, match="Config not found"):
            plot_service.generate_plot('UC-999.999', sample_plot_dataframe)

    def test_generate_plot_propagates_strategy_errors(
        self, plot_service, sample_plot_dataframe
    ):
        """Test that strategy creation errors are propagated."""
        plot_service.config_loader = Mock()
        plot_service.factory = Mock()

        mock_config = {
            'metadata': {'use_case_id': 'UC-2.1'},
            'visualization': {'strategy': 'InvalidStrategy'},
            'performance': {'cache': {'enabled': False}}
        }
        plot_service.config_loader.load_config.return_value = mock_config
        plot_service.factory.create_strategy.side_effect = ValueError(
            "Unknown strategy"
        )

        with pytest.raises(ValueError, match="Unknown strategy"):
            plot_service.generate_plot('UC-2.1', sample_plot_dataframe)

    def test_generate_plot_propagates_validation_errors(
        self, plot_service, sample_plot_dataframe
    ):
        """Test that data validation errors are propagated."""
        plot_service.config_loader = Mock()
        plot_service.factory = Mock()
        plot_service.cache_manager = Mock()

        mock_config = {
            'metadata': {'use_case_id': 'UC-2.1'},
            'visualization': {'strategy': 'BarChartStrategy'},
            'performance': {'cache': {'enabled': False}}
        }
        plot_service.config_loader.load_config.return_value = mock_config

        # Mock strategy that raises validation error
        mock_strategy = Mock()
        mock_strategy.generate_plot.side_effect = ValueError(
            "Invalid data: missing required column"
        )
        plot_service.factory.create_strategy.return_value = mock_strategy

        with pytest.raises(ValueError, match="Invalid data"):
            plot_service.generate_plot('UC-2.1', sample_plot_dataframe)


# ============================================================================
# CACHE CLEARING TESTS
# ============================================================================

class TestCacheClearing:
    """Test cache invalidation."""

    def test_clear_cache_all(self, plot_service):
        """Test clearing all cache."""
        plot_service.cache_manager = Mock()

        plot_service.clear_cache()

        plot_service.cache_manager.clear.assert_called_once()

    def test_clear_cache_specific_use_case(self, plot_service):
        """Test clearing cache for specific use case."""
        plot_service.cache_manager = Mock()

        # Current implementation logs but doesn't clear specific patterns
        # This test documents current behavior
        plot_service.clear_cache(use_case_id='UC-2.1')

        # clear() should not be called for specific use case
        plot_service.cache_manager.clear.assert_not_called()


# ============================================================================
# INTEGRATION-LIKE TESTS (with real components, mocked I/O)
# ============================================================================

class TestPlotServiceIntegration:
    """Integration-like tests with real components but mocked I/O."""

    def test_end_to_end_with_mocked_strategy(
        self, sample_plot_dataframe
    ):
        """Test end-to-end with mocked strategy generation."""
        # This test validates the orchestration logic
        # without testing actual plot rendering
        service = PlotService()

        # Mock dependencies
        service.config_loader = Mock()
        service.factory = Mock()

        mock_config = {
            'metadata': {'use_case_id': 'UC-2.1'},
            'visualization': {'strategy': 'BarChartStrategy'},
            'performance': {'cache': {'enabled': False}}
        }
        service.config_loader.load_config.return_value = mock_config

        # Mock strategy with figure
        mock_strategy = Mock()
        test_figure = go.Figure()
        test_figure.update_layout(title='Test Plot')
        mock_strategy.generate_plot.return_value = test_figure
        service.factory.create_strategy.return_value = mock_strategy

        # Execute
        result = service.generate_plot('UC-2.1', sample_plot_dataframe)

        # Verify orchestration
        assert isinstance(result, go.Figure)
        assert result.layout.title.text == 'Test Plot'
        mock_strategy.generate_plot.assert_called_once()

    def test_hash_consistency_across_calls(self, plot_service):
        """Test that hashing is deterministic across multiple calls."""
        df = pd.DataFrame({
            'A': [1, 2, 3],
            'B': ['x', 'y', 'z']
        })
        filters = {'range': [10, 50], 'category': 'test'}

        # Generate hashes multiple times
        data_hashes = [plot_service._generate_data_hash(df) for _ in range(5)]
        filter_hashes = [
            plot_service._generate_filters_hash(filters) for _ in range(5)
        ]

        # All hashes should be identical
        assert len(set(data_hashes)) == 1
        assert len(set(filter_hashes)) == 1


# ============================================================================
# EDGE CASES AND BOUNDARY CONDITIONS
# ============================================================================

class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_generate_plot_with_none_filters(
        self, plot_service, sample_plot_dataframe
    ):
        """Test plot generation with None filters."""
        plot_service.config_loader = Mock()
        plot_service.factory = Mock()
        plot_service.cache_manager = Mock()

        mock_config = {
            'metadata': {'use_case_id': 'UC-2.1'},
            'visualization': {'strategy': 'BarChartStrategy'},
            'performance': {'cache': {'enabled': False}}
        }
        plot_service.config_loader.load_config.return_value = mock_config

        mock_strategy = Mock()
        mock_figure = go.Figure()
        mock_strategy.generate_plot.return_value = mock_figure
        plot_service.factory.create_strategy.return_value = mock_strategy

        # Execute with None filters
        result = plot_service.generate_plot(
            'UC-2.1',
            sample_plot_dataframe,
            filters=None
        )

        # Should complete without error
        assert result == mock_figure

    def test_generate_plot_with_empty_filters(
        self, plot_service, sample_plot_dataframe
    ):
        """Test plot generation with empty filters dict."""
        plot_service.config_loader = Mock()
        plot_service.factory = Mock()
        plot_service.cache_manager = Mock()

        mock_config = {
            'metadata': {'use_case_id': 'UC-2.1'},
            'visualization': {'strategy': 'BarChartStrategy'},
            'performance': {'cache': {'enabled': False}}
        }
        plot_service.config_loader.load_config.return_value = mock_config

        mock_strategy = Mock()
        mock_figure = go.Figure()
        mock_strategy.generate_plot.return_value = mock_figure
        plot_service.factory.create_strategy.return_value = mock_strategy

        # Execute with empty filters
        result = plot_service.generate_plot(
            'UC-2.1',
            sample_plot_dataframe,
            filters={}
        )

        # Should complete without error
        assert result == mock_figure

    def test_data_hash_with_large_dataframe(self, plot_service):
        """Test data hashing with large DataFrame."""
        # Create large DataFrame
        large_df = pd.DataFrame({
            'A': range(10000),
            'B': range(10000, 20000),
            'C': [f'value{i}' for i in range(10000)]
        })

        # Should complete without error
        hash_value = plot_service._generate_data_hash(large_df)

        assert isinstance(hash_value, str)
        assert len(hash_value) == 16

    def test_data_hash_with_special_characters(self, plot_service):
        """Test data hashing with special characters in data."""
        df = pd.DataFrame({
            'col': ['test@#$%', 'unicode_\u00e9\u00e7\u00e0', '日本語']
        })

        hash_value = plot_service._generate_data_hash(df)

        assert isinstance(hash_value, str)
        assert len(hash_value) == 16

    def test_filters_hash_with_special_values(self, plot_service):
        """Test filter hashing with special values."""
        filters = {
            'unicode': 'café_\u00e9',
            'special': '@#$%^&*()',
            'null': None,
            'bool': True,
            'number': 42.5
        }

        hash_value = plot_service._generate_filters_hash(filters)

        assert isinstance(hash_value, str)
        assert len(hash_value) == 16
