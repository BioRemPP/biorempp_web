"""
Unit tests for HADEG Repository.
"""

import pytest
import pandas as pd
from pathlib import Path
from src.infrastructure.persistence.hadeg_repository import HADEGRepository


class TestHADEGRepository:
    """Test suite for HADEGRepository."""

    def test_initialization_default_path(self):
        """Test default filepath initialization."""
        repo = HADEGRepository()
        
        assert repo.filepath == Path('data/databases/hadeg_db.csv')
        assert repo.encoding == 'utf-8'
        assert repo.separator == ';'
        assert 'ko' in repo.required_columns
        assert 'Gene' in repo.required_columns
        assert 'Pathway' in repo.required_columns  # Maiúscula no CSV

    def test_initialization_custom_path(self, temp_csv_file):
        """Test initialization with custom path using fixture."""
        repo = HADEGRepository(filepath=temp_csv_file)
        
        assert repo.filepath == temp_csv_file

    def test_required_columns(self):
        """Test required columns for HADEG database."""
        repo = HADEGRepository()
        
        assert 'ko' in repo.required_columns
        assert 'Gene' in repo.required_columns
        assert 'Pathway' in repo.required_columns  # Maiúscula no CSV
        assert isinstance(repo.required_columns, list)
        assert len(repo.required_columns) >= 3

    @pytest.mark.skipif(
        not Path('data/databases/hadeg_db.csv').exists(),
        reason="Real database file not available"
    )
    def test_load_real_database(self, analysis_data):
        """Test loading real HADEG database using analysis data."""
        repo = HADEGRepository()
        
        df = repo.load_data()
        
        assert isinstance(df, pd.DataFrame)
        assert len(df) > 0
        assert 'ko' in df.columns
        assert 'Gene' in df.columns
        assert 'Pathway' in df.columns  # Nome real da coluna (maiúscula)
        
        # Verify against analysis data
        expected_rows = analysis_data['databases']['hadeg']['shape']['rows']
        assert len(df) == expected_rows
        
        # Verify columns from analysis
        expected_cols = analysis_data['databases']['hadeg']['shape']['columns']
        assert len(df.columns) == expected_cols

    @pytest.mark.skipif(
        not Path('data/databases/hadeg_db.csv').exists(),
        reason="Real database file not available"
    )
    def test_load_real_database_ko_column(self):
        """Test that loaded database has KO column with data."""
        repo = HADEGRepository()
        
        df = repo.load_data()
        
        # Check KO column structure (pode ser object ou category após otimização)
        assert df['ko'].dtype in ['object', 'category'] or str(df['ko'].dtype).startswith('CategoricalDtype')
        assert len(df['ko'].unique()) > 0
        
        # Check that KOs are not empty
        assert df['ko'].notna().sum() > 0

    @pytest.mark.skipif(
        not Path('data/databases/hadeg_db.csv').exists(),
        reason="Real database file not available"
    )
    def test_repository_caching(self):
        """Test that repository caches loaded data."""
        repo = HADEGRepository()
        
        # First load
        df1 = repo.load_data()
        
        # Second load should return cached version
        df2 = repo.load_data()
        
        # Should be the same object (cached)
        assert df1 is df2

    @pytest.mark.skipif(
        not Path('data/databases/hadeg_db.csv').exists(),
        reason="Real database file not available"
    )
    def test_gene_column_exists(self):
        """Test that Gene column exists and has data."""
        repo = HADEGRepository()
        
        df = repo.load_data()
        
        assert 'Gene' in df.columns
        assert df['Gene'].notna().sum() > 0
        
        # Verify we have unique genes
        unique_genes = df['Gene'].unique()
        assert len(unique_genes) > 0

    @pytest.mark.skipif(
        not Path('data/databases/hadeg_db.csv').exists(),
        reason="Real database file not available"
    )
    def test_pathway_column_exists(self):
        """Test that Pathway column exists (maiúscula)."""
        repo = HADEGRepository()
        
        df = repo.load_data()
        
        assert 'Pathway' in df.columns
        assert df['Pathway'].notna().sum() > 0

    def test_get_column_names(self):
        """Test getting column names from repository."""
        repo = HADEGRepository()
        
        # Even before loading, required_columns should be accessible
        assert 'ko' in repo.required_columns
        assert 'Gene' in repo.required_columns
        assert 'Pathway' in repo.required_columns  # Maiúscula como no CSV

    @pytest.mark.skipif(
        not Path('data/databases/hadeg_db.csv').exists(),
        reason="Real database file not available"
    )
    def test_database_schema_validation(self, analysis_data):
        """Test that database schema matches expected structure."""
        repo = HADEGRepository()
        
        df = repo.load_data()
        
        # Check that all required columns are present
        for col in repo.required_columns:
            assert col in df.columns, f"Required column {col} missing"
        
        # Verify data from analysis
        hadeg_analysis = analysis_data['databases']['hadeg']
        assert len(df) == hadeg_analysis['shape']['rows']

    @pytest.mark.skipif(
        not Path('data/databases/hadeg_db.csv').exists(),
        reason="Real database file not available"
    )
    def test_ko_gene_relationship(self):
        """Test relationship between KO and Gene columns."""
        repo = HADEGRepository()
        
        df = repo.load_data()
        
        # Each KO should have at least one gene
        ko_groups = df.groupby('ko')['Gene'].count()
        assert (ko_groups > 0).all()

