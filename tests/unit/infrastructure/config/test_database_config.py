"""
Unit tests for Database Config module.
"""

import pytest
from pathlib import Path
from src.infrastructure.config.database_config import DatabaseConfig


class TestDatabaseConfig:
    """Test suite for DatabaseConfig."""

    def test_initialization(self):
        """Test database config initialization."""
        config = DatabaseConfig()
        
        assert config._config is not None
        assert isinstance(config._config, dict)

    def test_get_available_databases(self, analysis_data):
        """Test getting available databases using real data."""
        config = DatabaseConfig()
        
        databases = config.get_available_databases()
        
        assert isinstance(databases, list)
        # Verify databases that exist in analysis_data
        expected_dbs = ['biorempp', 'kegg', 'hadeg', 'toxcsm']
        for db in expected_dbs:
            assert db in databases
        
        # Verify all databases in analysis_data are in config
        for db_name in analysis_data['databases'].keys():
            db_key = db_name.lower().replace('_', '')
            # Some databases have different naming conventions
            assert any(db_key in db.lower() for db in databases)

    def test_get_database_path(self):
        """Test getting database path."""
        config = DatabaseConfig()
        
        path = config.get_database_path('biorempp')
        
        assert isinstance(path, Path)
        # Use Path comparison to handle Windows/Unix separators
        assert path == Path('data/databases/biorempp_db.csv')

    def test_get_database_path_invalid(self):
        """Test error when getting invalid database."""
        config = DatabaseConfig()
        
        with pytest.raises(ValueError, match="Unknown database"):
            config.get_database_path('invalid_db')

    def test_get_database_encoding(self):
        """Test getting database encoding."""
        config = DatabaseConfig()
        
        encoding = config.get_database_encoding('biorempp')
        
        assert encoding == 'utf-8'

    def test_get_database_encoding_default(self):
        """Test default encoding for unknown database."""
        config = DatabaseConfig()
        
        encoding = config.get_database_encoding(
            'unknown',
            default='latin-1'
        )
        
        assert encoding == 'latin-1'

    def test_get_database_separator(self):
        """Test getting database separator."""
        config = DatabaseConfig()
        
        separator = config.get_database_separator('kegg')
        
        assert separator == ';'

    def test_get_all_database_paths(self):
        """Test getting all database paths."""
        config = DatabaseConfig()
        
        paths = config.get_all_database_paths()
        
        assert isinstance(paths, dict)
        assert len(paths) == 4
        assert 'biorempp' in paths
        assert isinstance(paths['biorempp'], Path)

    def test_validate_paths(self):
        """Test path validation."""
        config = DatabaseConfig()
        
        status = config.validate_paths()
        
        assert isinstance(status, dict)
        assert len(status) == 4
        assert 'biorempp' in status
        assert isinstance(status['biorempp'], bool)

    def test_get_database_info(self):
        """Test getting complete database info."""
        config = DatabaseConfig()
        
        info = config.get_database_info('hadeg')
        
        assert isinstance(info, dict)
        assert 'filepath' in info
        assert 'encoding' in info
        assert 'separator' in info
        assert 'description' in info

    def test_get_database_info_invalid(self):
        """Test error when getting info for invalid database."""
        config = DatabaseConfig()
        
        with pytest.raises(ValueError, match="Unknown database"):
            config.get_database_info('invalid')

