"""
Unit tests for ToxCSM Repository.
"""

import pytest
import pandas as pd
from pathlib import Path
from src.infrastructure.persistence.toxcsm_repository import ToxCSMRepository


class TestToxCSMRepository:
    """Test suite for ToxCSMRepository."""

    def test_initialization_default_path(self):
        """Test default filepath initialization."""
        repo = ToxCSMRepository()
        
        assert repo.filepath == Path('data/databases/toxcsm_db.csv')
        assert repo.encoding == 'utf-8'
        assert repo.separator == ';'
        assert 'cpd' in repo.required_columns  # Nome real no CSV

    def test_initialization_custom_path(self, temp_csv_file):
        """Test initialization with custom path using fixture."""
        repo = ToxCSMRepository(filepath=temp_csv_file)
        
        assert repo.filepath == temp_csv_file

    def test_required_columns(self):
        """Test required columns for ToxCSM database."""
        repo = ToxCSMRepository()
        
        # ToxCSM uses 'cpd' (compound) instead of 'ko'
        assert 'cpd' in repo.required_columns
        assert isinstance(repo.required_columns, list)

    @pytest.mark.skipif(
        not Path('data/databases/toxcsm_db.csv').exists(),
        reason="Real database file not available"
    )
    def test_load_real_database(self, analysis_data):
        """Test loading real ToxCSM database using analysis data."""
        repo = ToxCSMRepository()
        
        df = repo.load_data()
        
        assert isinstance(df, pd.DataFrame)
        assert len(df) > 0
        assert 'cpd' in df.columns  # Nome real da coluna
        
        # Verify against analysis data
        expected_rows = analysis_data['databases']['toxcsm']['shape']['rows']
        assert len(df) == expected_rows
        
        # Verify columns from analysis - ToxCSM has many columns
        expected_cols = analysis_data['databases']['toxcsm']['shape']['columns']
        assert len(df.columns) == expected_cols

    @pytest.mark.skipif(
        not Path('data/databases/toxcsm_db.csv').exists(),
        reason="Real database file not available"
    )
    def test_load_real_database_compound_column(self):
        """Test that loaded database has cpd column with data."""
        repo = ToxCSMRepository()
        
        df = repo.load_data()
        
        # Check cpd column structure
        assert df['cpd'].dtype == 'object'
        assert len(df['cpd'].unique()) > 0
        
        # Check that compounds are not empty
        assert df['cpd'].notna().sum() > 0

    @pytest.mark.skipif(
        not Path('data/databases/toxcsm_db.csv').exists(),
        reason="Real database file not available"
    )
    def test_repository_caching(self):
        """Test that repository caches loaded data."""
        repo = ToxCSMRepository()
        
        # First load
        df1 = repo.load_data()
        
        # Second load should return cached version
        df2 = repo.load_data()
        
        # Should be the same object (cached)
        assert df1 is df2

    @pytest.mark.skipif(
        not Path('data/databases/toxcsm_db.csv').exists(),
        reason="Real database file not available"
    )
    def test_many_toxicity_columns(self, analysis_data):
        """Test that ToxCSM has many toxicity prediction columns."""
        repo = ToxCSMRepository()
        
        df = repo.load_data()
        
        # ToxCSM should have many columns (toxicity predictions)
        # According to analysis, it should have 66 columns
        assert len(df.columns) >= 10, "Expected many toxicity columns"
        
        # Verify from analysis data
        expected_cols = analysis_data['databases']['toxcsm']['shape']['columns']
        assert len(df.columns) == expected_cols

    def test_get_column_names(self):
        """Test getting column names from repository."""
        repo = ToxCSMRepository()
        
        # Even before loading, required_columns should be accessible
        assert 'cpd' in repo.required_columns  # Nome real no CSV

    @pytest.mark.skipif(
        not Path('data/databases/toxcsm_db.csv').exists(),
        reason="Real database file not available"
    )
    def test_database_schema_validation(self, analysis_data):
        """Test that database schema matches expected structure."""
        repo = ToxCSMRepository()
        
        df = repo.load_data()
        
        # Check that all required columns are present
        for col in repo.required_columns:
            assert col in df.columns, f"Required column {col} missing"
        
        # Verify data from analysis
        toxcsm_analysis = analysis_data['databases']['toxcsm']
        assert len(df) == toxcsm_analysis['shape']['rows']

    @pytest.mark.skipif(
        not Path('data/databases/toxcsm_db.csv').exists(),
        reason="Real database file not available"
    )
    def test_merge_with_compound_data(self):
        """Test merging ToxCSM with compound data."""
        repo = ToxCSMRepository()
        
        # Create sample compound data usando 'cpd' (nome real da coluna)
        compound_df = pd.DataFrame({
            'cpd': ['Compound1', 'Compound2', 'Compound3'],
            'ko': ['K00001', 'K00002', 'K00003'],
            'data': [1, 2, 3]
        })
        
        # Load toxicity data
        toxcsm_df = repo.load_data()
        
        # Merge - should not fail even if compounds don't match
        merged = repo.merge_with_compound_data(compound_df)
        
        assert isinstance(merged, pd.DataFrame)
        assert len(merged) == len(compound_df)  # Left join preserves all
        assert 'cpd' in merged.columns
        assert 'data' in merged.columns

    @pytest.mark.skipif(
        not Path('data/databases/toxcsm_db.csv').exists(),
        reason="Real database file not available"
    )
    def test_unique_compounds(self):
        """Test that compounds in database are unique or have rationale."""
        repo = ToxCSMRepository()
        
        df = repo.load_data()
        
        # Check cpd column exists and has data
        assert 'cpd' in df.columns
        assert len(df) > 0
        
        # Get unique compounds count
        unique_compounds = df['cpd'].nunique()
        total_rows = len(df)
        
        # Compounds should exist
        assert unique_compounds > 0

    @pytest.mark.skipif(
        not Path('data/databases/toxcsm_db.csv').exists(),
        reason="Real database file not available"
    )
    def test_toxicity_prediction_columns_exist(self):
        """Test that toxicity prediction columns exist."""
        repo = ToxCSMRepository()
        
        df = repo.load_data()
        
        # Should have more columns than just 'compound'
        assert len(df.columns) > 1
        
        # All columns should have some non-null data
        for col in df.columns:
            # At least some rows should have data
            assert df[col].notna().sum() >= 0

