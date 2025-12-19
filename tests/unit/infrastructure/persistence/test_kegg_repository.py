"""
Unit tests for KEGG Repository.
"""

import pytest
import pandas as pd
from pathlib import Path
from src.infrastructure.persistence.kegg_repository import KEGGRepository


class TestKEGGRepository:
    """Test suite for KEGGRepository."""

    def test_initialization_default_path(self):
        """Test default filepath initialization."""
        repo = KEGGRepository()
        
        assert repo.filepath == Path('data/databases/kegg_degradation_db.csv')
        assert repo.encoding == 'utf-8'
        assert repo.separator == ';'
        assert 'ko' in repo.required_columns
        assert 'pathname' in repo.required_columns  # Nome real no CSV

    def test_initialization_custom_path(self, temp_csv_file):
        """Test initialization with custom path using fixture."""
        repo = KEGGRepository(filepath=temp_csv_file)
        
        assert repo.filepath == temp_csv_file

    def test_required_columns(self):
        """Test required columns for KEGG database."""
        repo = KEGGRepository()
        
        assert 'ko' in repo.required_columns
        assert 'pathname' in repo.required_columns  # Nome real no CSV
        assert isinstance(repo.required_columns, list)
        assert len(repo.required_columns) >= 2

    @pytest.mark.skipif(
        not Path('data/databases/kegg_degradation_db.csv').exists(),
        reason="Real database file not available"
    )
    def test_load_real_database(self, analysis_data):
        """Test loading real KEGG database using analysis data."""
        repo = KEGGRepository()
        
        df = repo.load_data()
        
        assert isinstance(df, pd.DataFrame)
        assert len(df) > 0
        assert 'ko' in df.columns
        assert 'pathname' in df.columns  # Nome real da coluna
        
        # Verify against analysis data
        expected_rows = analysis_data['databases']['kegg']['shape']['rows']
        assert len(df) == expected_rows
        
        # Verify columns from analysis
        expected_cols = analysis_data['databases']['kegg']['shape']['columns']
        assert len(df.columns) == expected_cols

    @pytest.mark.skipif(
        not Path('data/databases/kegg_degradation_db.csv').exists(),
        reason="Real database file not available"
    )
    def test_load_real_database_ko_column(self, valid_ko_ids):
        """Test that loaded database may contain some expected KOs."""
        repo = KEGGRepository()
        
        df = repo.load_data()
        
        # KEGG database may have different KOs, just check structure
        assert df['ko'].dtype == 'object'
        assert len(df['ko'].unique()) > 0

    @pytest.mark.skipif(
        not Path('data/databases/kegg_degradation_db.csv').exists(),
        reason="Real database file not available"
    )
    def test_repository_caching(self):
        """Test that repository caches loaded data."""
        repo = KEGGRepository()
        
        # First load
        df1 = repo.load_data()
        
        # Second load should return cached version
        df2 = repo.load_data()
        
        # Should be the same object (cached)
        assert df1 is df2

    @pytest.mark.skipif(
        not Path('data/databases/kegg_degradation_db.csv').exists(),
        reason="Real database file not available"
    )
    def test_pathway_column_exists(self):
        """Test that pathname column exists and has data."""
        repo = KEGGRepository()
        
        df = repo.load_data()
        
        assert 'pathname' in df.columns
        assert df['pathname'].notna().sum() > 0
        
        # Verify we have unique pathways
        unique_pathways = df['pathname'].unique()
        assert len(unique_pathways) > 0

    def test_get_column_names(self):
        """Test getting column names from repository."""
        repo = KEGGRepository()
        
        # Even before loading, required_columns should be accessible
        assert 'ko' in repo.required_columns
        assert 'pathname' in repo.required_columns  # Nome real no CSV

    @pytest.mark.skipif(
        not Path('data/databases/kegg_degradation_db.csv').exists(),
        reason="Real database file not available"
    )
    def test_database_schema_validation(self, analysis_data):
        """Test that database schema matches expected structure."""
        repo = KEGGRepository()
        
        df = repo.load_data()
        
        # Check that all required columns are present
        for col in repo.required_columns:
            assert col in df.columns, f"Required column {col} missing"
        
        # Verify data types from analysis
        kegg_analysis = analysis_data['databases']['kegg']
        assert len(df) == kegg_analysis['shape']['rows']

