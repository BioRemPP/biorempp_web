"""
Unit tests for Settings module.
"""

import pytest
from pathlib import Path
from src.infrastructure.config.settings import Settings


class TestSettings:
    """Test suite for Settings."""

    def test_singleton_pattern(self):
        """Test that Settings uses singleton pattern."""
        settings1 = Settings()
        settings2 = Settings()
        
        assert settings1 is settings2

    def test_default_settings(self):
        """Test default settings when no file exists."""
        # Force new instance
        Settings._instance = None
        
        settings = Settings(config_file=Path('nonexistent.yaml'))
        
        # Should have default cache settings
        assert settings.get('cache.memory.max_size') is not None

    def test_load_from_file(self, temp_yaml_config):
        """Test loading settings from file using global fixture."""
        # Force new instance
        Settings._instance = None
        
        settings = Settings(config_file=temp_yaml_config)
        
        # temp_yaml_config has max_size: 100 (from conftest)
        assert settings.get('cache.memory.max_size') == 100
        assert settings.get('plotting.default_height') == 600

    def test_get_with_dot_notation(self):
        """Test getting values with dot notation."""
        Settings._instance = None
        settings = Settings()
        
        value = settings.get('cache.memory.max_size')
        
        assert value is not None

    def test_get_with_default(self):
        """Test getting value with default."""
        Settings._instance = None
        settings = Settings()
        
        value = settings.get('nonexistent.key', default=999)
        
        assert value == 999

    def test_set_value(self):
        """Test setting a value."""
        Settings._instance = None
        settings = Settings()
        
        settings.set('custom.key', 'custom_value')
        
        assert settings.get('custom.key') == 'custom_value'

    def test_set_nested_value(self):
        """Test setting nested value."""
        Settings._instance = None
        settings = Settings()
        
        settings.set('level1.level2.level3', 'deep_value')
        
        assert settings.get('level1.level2.level3') == 'deep_value'

    def test_get_section(self):
        """Test getting entire section."""
        Settings._instance = None
        settings = Settings()
        
        cache_section = settings.get_section('cache')
        
        assert isinstance(cache_section, dict)
        assert 'memory' in cache_section

    def test_get_all(self):
        """Test getting all settings."""
        Settings._instance = None
        settings = Settings()
        
        all_settings = settings.get_all()
        
        assert isinstance(all_settings, dict)
        assert 'cache' in all_settings

