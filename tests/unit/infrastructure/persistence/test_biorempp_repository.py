"""
Unit tests for BioRemPP Repository.
"""

import pytest
import pandas as pd
from pathlib import Path
from src.infrastructure.persistence.biorempp_repository import (
    BioRemPPRepository
)


class TestBioRemPPRepository:
    """Test suite for BioRemPPRepository."""

    def test_initialization_default_path(self):
        """Test default filepath initialization."""
        repo = BioRemPPRepository()
        
        assert repo.filepath == Path('data/databases/biorempp_db.csv')
        assert repo.encoding == 'utf-8'
        assert repo.separator == ';'
        assert 'ko' in repo.required_columns

    def test_initialization_custom_path(self, temp_csv_file):
        """Test initialization with custom path using fixture."""
        repo = BioRemPPRepository(filepath=temp_csv_file)
        
        assert repo.filepath == temp_csv_file

    def test_required_columns(self):
        """Test that 'ko' is required column."""
        repo = BioRemPPRepository()
        
        assert 'ko' in repo.required_columns
        assert isinstance(repo.required_columns, list)

    @pytest.mark.skipif(
        not Path('data/databases/biorempp_db.csv').exists(),
        reason="Real database file not available"
    )
    def test_load_real_database(self, analysis_data):
        """Test loading real BioRemPP database using analysis data."""
        repo = BioRemPPRepository()
        
        df = repo.load_data()
        
        assert isinstance(df, pd.DataFrame)
        assert len(df) > 0
        assert 'ko' in df.columns
        
        # Verify against analysis data
        expected_rows = analysis_data['databases']['biorempp']['shape']['rows']
        assert len(df) == expected_rows
        
        # Verify columns from analysis
        expected_cols = analysis_data['databases']['biorempp']['shape']['columns']
        assert len(df.columns) == expected_cols

    @pytest.mark.skipif(
        not Path('data/databases/biorempp_db.csv').exists(),
        reason="Real database file not available"
    )
    def test_load_real_database_ko_column(self, valid_ko_ids):
        """Test that loaded database contains expected KOs."""
        repo = BioRemPPRepository()
        
        df = repo.load_data()
        
        # Check if some of our real KOs are in the database
        for ko_id in valid_ko_ids[:3]:
            msg = f"KO {ko_id} should be in database"
            assert ko_id in df['ko'].values, msg

    @pytest.mark.skipif(
        not Path('data/databases/biorempp_db.csv').exists(),
        reason="Real database file not available"
    )
    def test_repository_caching(self):
        """Test that repository caches loaded data."""
        repo = BioRemPPRepository()
        
        # First load
        df1 = repo.load_data()
        
        # Second load should return cached version
        df2 = repo.load_data()
        
        # Should be the same object (cached)
        assert df1 is df2

    def test_get_column_names(self):
        """Test getting column names from repository."""
        repo = BioRemPPRepository()
        
        # Even before loading, required_columns should be accessible
        assert 'ko' in repo.required_columns

