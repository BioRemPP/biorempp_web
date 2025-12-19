"""
Unit tests for PlotConfigLoader.

This module tests the PlotConfigLoader class, which loads and caches
YAML configuration files for plot use cases.

Test Categories:
- Initialization: Test loader setup
- Config Loading: Test YAML file loading
- Caching: Test cache hit/miss scenarios
- ID Parsing: Test use case ID validation
- Error Handling: Test file and YAML errors
- Cache Management: Test cache operations
"""

import pytest
import yaml
from pathlib import Path

from src.application.plot_services.plot_config_loader import PlotConfigLoader


# ============================================================================
# INITIALIZATION TESTS
# ============================================================================

class TestPlotConfigLoaderInitialization:
    """Test PlotConfigLoader initialization."""

    def test_initialization_default_path(self):
        """Test initialization with default config directory."""
        loader = PlotConfigLoader()

        assert loader.config_dir == Path("src/infrastructure/plot_configs")
        assert isinstance(loader._cache, dict)
        assert len(loader._cache) == 0

    def test_initialization_custom_path(self, temp_dir):
        """Test initialization with custom config directory."""
        custom_path = str(temp_dir / "custom_configs")
        loader = PlotConfigLoader(config_dir=custom_path)

        assert loader.config_dir == Path(custom_path)
        assert isinstance(loader._cache, dict)

    def test_initialization_creates_path_object(self):
        """Test that config_dir is a Path object."""
        loader = PlotConfigLoader()

        assert isinstance(loader.config_dir, Path)


# ============================================================================
# CONFIG LOADING TESTS
# ============================================================================

class TestConfigLoading:
    """Test configuration file loading."""

    def test_load_config_success(self, temp_plot_config_dir):
        """Test successful config loading."""
        loader = PlotConfigLoader(config_dir=str(temp_plot_config_dir))

        config = loader.load_config("UC-2.1")

        assert config is not None
        assert isinstance(config, dict)
        assert 'metadata' in config
        assert config['metadata']['use_case_id'] == 'UC-2.1'

    def test_load_config_caches_result(self, temp_plot_config_dir):
        """Test that loaded config is cached."""
        loader = PlotConfigLoader(config_dir=str(temp_plot_config_dir))

        # First load
        config1 = loader.load_config("UC-2.1")
        # Second load (should be from cache)
        config2 = loader.load_config("UC-2.1")

        # Should return same object from cache
        assert config1 is config2
        assert "UC-2.1" in loader._cache

    def test_load_config_with_force_reload(self, temp_plot_config_dir):
        """Test force reload bypasses cache."""
        loader = PlotConfigLoader(config_dir=str(temp_plot_config_dir))

        # Load and cache
        config1 = loader.load_config("UC-2.1")

        # Modify cache to verify reload
        loader._cache["UC-2.1"]["modified"] = True

        # Force reload
        config2 = loader.load_config("UC-2.1", force_reload=True)

        # Should be new object without modification
        assert "modified" not in config2

    def test_load_config_builds_correct_path(self, temp_dir):
        """Test that correct file path is constructed."""
        # Create config structure
        config_dir = temp_dir / "plot_configs"
        module_dir = config_dir / "module3"
        module_dir.mkdir(parents=True)

        config_file = module_dir / "uc_3_4_config.yaml"
        config_data = {
            'metadata': {'use_case_id': 'UC-3.4'},
            'visualization': {'strategy': 'TestStrategy'}
        }
        with open(config_file, 'w', encoding='utf-8') as f:
            yaml.dump(config_data, f)

        loader = PlotConfigLoader(config_dir=str(config_dir))
        config = loader.load_config("UC-3.4")

        assert config['metadata']['use_case_id'] == 'UC-3.4'


# ============================================================================
# USE CASE ID PARSING TESTS
# ============================================================================

class TestUseCaseIDParsing:
    """Test use case ID validation and parsing."""

    def test_valid_use_case_id_format(self, temp_plot_config_dir):
        """Test that valid UC-X.Y format is accepted."""
        loader = PlotConfigLoader(config_dir=str(temp_plot_config_dir))

        # Should not raise error
        config = loader.load_config("UC-2.1")
        assert config is not None

    def test_invalid_use_case_id_no_prefix(self):
        """Test error when use case ID missing UC- prefix."""
        loader = PlotConfigLoader()

        with pytest.raises(ValueError, match="Invalid use case ID format"):
            loader.load_config("2.1")

    def test_invalid_use_case_id_wrong_prefix(self):
        """Test error when use case ID has wrong prefix."""
        loader = PlotConfigLoader()

        with pytest.raises(ValueError, match="Invalid use case ID format"):
            loader.load_config("TC-2.1")

    def test_invalid_use_case_id_missing_dot(self):
        """Test error when use case ID missing dot separator."""
        loader = PlotConfigLoader()

        with pytest.raises(ValueError, match="Invalid use case ID format"):
            loader.load_config("UC-21")

    def test_invalid_use_case_id_too_many_parts(self):
        """Test error when use case ID has too many parts."""
        loader = PlotConfigLoader()

        with pytest.raises(ValueError, match="Invalid use case ID format"):
            loader.load_config("UC-2.1.3")

    def test_invalid_use_case_id_empty_string(self):
        """Test error with empty string."""
        loader = PlotConfigLoader()

        with pytest.raises(ValueError):
            loader.load_config("")

    def test_use_case_id_case_sensitive(self, temp_plot_config_dir):
        """Test that use case ID is case-sensitive for prefix."""
        loader = PlotConfigLoader(config_dir=str(temp_plot_config_dir))

        with pytest.raises(ValueError, match="Invalid use case ID format"):
            loader.load_config("uc-2.1")


# ============================================================================
# ERROR HANDLING TESTS
# ============================================================================

class TestErrorHandling:
    """Test error handling scenarios."""

    def test_file_not_found_error(self):
        """Test FileNotFoundError when config file doesn't exist."""
        loader = PlotConfigLoader()

        with pytest.raises(
            FileNotFoundError,
            match="Configuration file not found"
        ):
            loader.load_config("UC-99.99")

    def test_invalid_yaml_error(self, temp_dir):
        """Test ValueError when YAML is invalid."""
        config_dir = temp_dir / "plot_configs"
        module_dir = config_dir / "module2"
        module_dir.mkdir(parents=True)

        # Create invalid YAML file
        config_file = module_dir / "uc_2_1_config.yaml"
        with open(config_file, 'w', encoding='utf-8') as f:
            f.write("invalid: yaml: content: [unclosed")

        loader = PlotConfigLoader(config_dir=str(config_dir))

        with pytest.raises(ValueError, match="Invalid YAML"):
            loader.load_config("UC-2.1")

    def test_nonexistent_directory(self, temp_dir):
        """Test error when config directory doesn't exist."""
        nonexistent = temp_dir / "does_not_exist"
        loader = PlotConfigLoader(config_dir=str(nonexistent))

        with pytest.raises(FileNotFoundError):
            loader.load_config("UC-2.1")


# ============================================================================
# CACHING BEHAVIOR TESTS
# ============================================================================

class TestCachingBehavior:
    """Test cache hit/miss scenarios."""

    def test_cache_hit_on_second_load(self, temp_plot_config_dir):
        """Test cache hit on subsequent loads."""
        loader = PlotConfigLoader(config_dir=str(temp_plot_config_dir))

        # First load - cache miss
        config1 = loader.load_config("UC-2.1")

        # Verify it's cached
        assert "UC-2.1" in loader._cache

        # Second load - cache hit
        config2 = loader.load_config("UC-2.1")

        # Should be same object
        assert config1 is config2

    def test_cache_miss_on_first_load(self, temp_plot_config_dir):
        """Test cache miss on initial load."""
        loader = PlotConfigLoader(config_dir=str(temp_plot_config_dir))

        # Cache should be empty initially
        assert "UC-2.1" not in loader._cache

        # Load config
        config = loader.load_config("UC-2.1")

        # Now should be in cache
        assert "UC-2.1" in loader._cache
        assert loader._cache["UC-2.1"] == config

    def test_multiple_configs_cached_independently(
        self, temp_plot_config_dir
    ):
        """Test that multiple configs are cached independently."""
        # Create second config
        module_dir = temp_plot_config_dir / "module2"
        config_file = module_dir / "uc_2_2_config.yaml"
        config_data = {
            'metadata': {'use_case_id': 'UC-2.2'},
            'visualization': {'strategy': 'TestStrategy'}
        }
        with open(config_file, 'w', encoding='utf-8') as f:
            yaml.dump(config_data, f)

        loader = PlotConfigLoader(config_dir=str(temp_plot_config_dir))

        # Load both configs
        config1 = loader.load_config("UC-2.1")
        config2 = loader.load_config("UC-2.2")

        # Both should be in cache
        assert "UC-2.1" in loader._cache
        assert "UC-2.2" in loader._cache

        # Should be different objects
        assert config1 is not config2

    def test_force_reload_updates_cache(self, temp_plot_config_dir):
        """Test that force reload updates cached config."""
        loader = PlotConfigLoader(config_dir=str(temp_plot_config_dir))

        # Initial load
        config1 = loader.load_config("UC-2.1")

        # Manually modify cache
        loader._cache["UC-2.1"]["test_key"] = "test_value"

        # Force reload
        config2 = loader.load_config("UC-2.1", force_reload=True)

        # Cache should be updated (no test_key)
        assert "test_key" not in config2
        assert "test_key" not in loader._cache["UC-2.1"]


# ============================================================================
# CACHE MANAGEMENT TESTS
# ============================================================================

class TestCacheManagement:
    """Test cache management operations."""

    def test_clear_cache(self, temp_plot_config_dir):
        """Test clearing the cache."""
        loader = PlotConfigLoader(config_dir=str(temp_plot_config_dir))

        # Load and cache config
        loader.load_config("UC-2.1")
        assert len(loader._cache) == 1

        # Clear cache
        loader.clear_cache()

        assert len(loader._cache) == 0
        assert "UC-2.1" not in loader._cache

    def test_get_cached_keys_empty(self):
        """Test get_cached_keys with empty cache."""
        loader = PlotConfigLoader()

        keys = loader.get_cached_keys()

        assert keys == []
        assert isinstance(keys, list)

    def test_get_cached_keys_with_entries(self, temp_plot_config_dir):
        """Test get_cached_keys with cached entries."""
        loader = PlotConfigLoader(config_dir=str(temp_plot_config_dir))

        # Load config
        loader.load_config("UC-2.1")

        keys = loader.get_cached_keys()

        assert "UC-2.1" in keys
        assert len(keys) == 1

    def test_get_cached_keys_returns_copy(self, temp_plot_config_dir):
        """Test that get_cached_keys returns a new list."""
        loader = PlotConfigLoader(config_dir=str(temp_plot_config_dir))
        loader.load_config("UC-2.1")

        keys1 = loader.get_cached_keys()
        keys2 = loader.get_cached_keys()

        # Should be equal but not same object
        assert keys1 == keys2
        assert keys1 is not keys2


# ============================================================================
# PATH CONSTRUCTION TESTS
# ============================================================================

class TestPathConstruction:
    """Test file path construction logic."""

    def test_path_construction_single_digit_module(self, temp_dir):
        """Test path for single-digit module (UC-2.1)."""
        config_dir = temp_dir / "plot_configs"
        module_dir = config_dir / "module2"
        module_dir.mkdir(parents=True)

        config_file = module_dir / "uc_2_1_config.yaml"
        with open(config_file, 'w', encoding='utf-8') as f:
            yaml.dump({'metadata': {'use_case_id': 'UC-2.1'}}, f)

        loader = PlotConfigLoader(config_dir=str(config_dir))
        config = loader.load_config("UC-2.1")

        assert config is not None

    def test_path_construction_double_digit_subcase(self, temp_dir):
        """Test path for double-digit subcase (UC-1.15)."""
        config_dir = temp_dir / "plot_configs"
        module_dir = config_dir / "module1"
        module_dir.mkdir(parents=True)

        config_file = module_dir / "uc_1_15_config.yaml"
        with open(config_file, 'w', encoding='utf-8') as f:
            yaml.dump({'metadata': {'use_case_id': 'UC-1.15'}}, f)

        loader = PlotConfigLoader(config_dir=str(config_dir))
        config = loader.load_config("UC-1.15")

        assert config is not None


# ============================================================================
# EDGE CASES AND BOUNDARY CONDITIONS
# ============================================================================

class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_load_empty_yaml_file(self, temp_dir):
        """Test loading empty YAML file."""
        config_dir = temp_dir / "plot_configs"
        module_dir = config_dir / "module2"
        module_dir.mkdir(parents=True)

        config_file = module_dir / "uc_2_1_config.yaml"
        config_file.touch()  # Create empty file

        loader = PlotConfigLoader(config_dir=str(config_dir))
        config = loader.load_config("UC-2.1")

        # Empty YAML returns None
        assert config is None

    def test_load_yaml_with_null_values(self, temp_dir):
        """Test loading YAML with null values."""
        config_dir = temp_dir / "plot_configs"
        module_dir = config_dir / "module2"
        module_dir.mkdir(parents=True)

        config_file = module_dir / "uc_2_1_config.yaml"
        with open(config_file, 'w', encoding='utf-8') as f:
            yaml.dump({'metadata': None, 'data': {'value': None}}, f)

        loader = PlotConfigLoader(config_dir=str(config_dir))
        config = loader.load_config("UC-2.1")

        assert config['metadata'] is None
        assert config['data']['value'] is None

    def test_load_yaml_with_special_characters(self, temp_dir):
        """Test loading YAML with special characters."""
        config_dir = temp_dir / "plot_configs"
        module_dir = config_dir / "module2"
        module_dir.mkdir(parents=True)

        config_file = module_dir / "uc_2_1_config.yaml"
        config_data = {
            'metadata': {
                'title': 'Test with "quotes" and \'apostrophes\'',
                'description': 'Unicode: café, 日本語'
            }
        }
        with open(config_file, 'w', encoding='utf-8') as f:
            yaml.dump(config_data, f, allow_unicode=True)

        loader = PlotConfigLoader(config_dir=str(config_dir))
        config = loader.load_config("UC-2.1")

        assert 'café' in config['metadata']['description']
        assert '日本語' in config['metadata']['description']

    def test_config_with_nested_structures(self, temp_dir):
        """Test loading config with deeply nested structures."""
        config_dir = temp_dir / "plot_configs"
        module_dir = config_dir / "module2"
        module_dir.mkdir(parents=True)

        config_file = module_dir / "uc_2_1_config.yaml"
        config_data = {
            'level1': {
                'level2': {
                    'level3': {
                        'level4': {
                            'value': 'deeply_nested'
                        }
                    }
                }
            }
        }
        with open(config_file, 'w', encoding='utf-8') as f:
            yaml.dump(config_data, f)

        loader = PlotConfigLoader(config_dir=str(config_dir))
        config = loader.load_config("UC-2.1")

        assert config['level1']['level2']['level3']['level4']['value'] == 'deeply_nested'

    def test_loader_reusability(self, temp_plot_config_dir):
        """Test that loader can load multiple configs sequentially."""
        # Create additional config
        module_dir = temp_plot_config_dir / "module1"
        module_dir.mkdir(parents=True)

        config_file = module_dir / "uc_1_1_config.yaml"
        with open(config_file, 'w', encoding='utf-8') as f:
            yaml.dump({'metadata': {'use_case_id': 'UC-1.1'}}, f)

        loader = PlotConfigLoader(config_dir=str(temp_plot_config_dir))

        # Load multiple configs
        config1 = loader.load_config("UC-2.1")
        config2 = loader.load_config("UC-1.1")
        config3 = loader.load_config("UC-2.1")  # Cached

        assert config1['metadata']['use_case_id'] == 'UC-2.1'
        assert config2['metadata']['use_case_id'] == 'UC-1.1'
        assert config1 is config3  # From cache
