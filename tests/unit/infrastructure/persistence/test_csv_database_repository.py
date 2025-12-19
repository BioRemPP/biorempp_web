"""
Unit tests for CSV Database Repository.

Tests the base repository implementation including loading,
merging, validation, and optimization features.
"""

import pytest
import pandas as pd
from pathlib import Path
import tempfile
import shutil
from src.infrastructure.persistence.csv_database_repository import (
    CSVDatabaseRepository
)


class TestCSVDatabaseRepository:
    """Test suite for CSVDatabaseRepository."""

    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for test files."""
        temp_path = Path(tempfile.mkdtemp())
        yield temp_path
        shutil.rmtree(temp_path)

    @pytest.fixture
    def sample_csv(self, temp_dir):
        """Create sample CSV file for testing."""
        csv_path = temp_dir / "test_database.csv"
        
        # Create sample data
        data = pd.DataFrame({
            'ko': ['K00001', 'K00002', 'K00003', 'K00004', 'K00005'],
            'gene': ['geneA', 'geneB', 'geneC', 'geneD', 'geneE'],
            'pathway': ['path1', 'path1', 'path2', 'path2', 'path3'],
            'count': [10, 20, 15, 25, 30]
        })
        
        # Save to CSV
        data.to_csv(csv_path, sep=';', index=False, encoding='utf-8')
        
        return csv_path

    def test_initialization(self, sample_csv):
        """Test repository initialization."""
        repo = CSVDatabaseRepository(
            filepath=sample_csv,
            encoding='utf-8',
            separator=';',
            required_columns=['ko', 'gene']
        )
        
        assert repo.filepath == sample_csv
        assert repo.encoding == 'utf-8'
        assert repo.separator == ';'
        assert repo.required_columns == ['ko', 'gene']
        assert repo._data is None  # Not loaded yet

    def test_load_data(self, sample_csv):
        """Test loading data from CSV."""
        repo = CSVDatabaseRepository(
            filepath=sample_csv,
            required_columns=['ko']
        )
        
        df = repo.load_data()
        
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 5
        assert 'ko' in df.columns
        assert 'gene' in df.columns
        assert df.iloc[0]['ko'] == 'K00001'

    def test_load_data_caching(self, sample_csv):
        """Test that data is cached after first load."""
        repo = CSVDatabaseRepository(filepath=sample_csv)
        
        # First load
        df1 = repo.load_data()
        
        # Second load should return cached data
        df2 = repo.load_data()
        
        assert df1 is df2  # Same object reference

    def test_reload_data(self, sample_csv):
        """Test force reload of data."""
        repo = CSVDatabaseRepository(filepath=sample_csv)
        
        # Initial load
        df1 = repo.load_data()
        
        # Reload
        df2 = repo.reload_data()
        
        assert df1 is not df2  # Different objects
        assert df1.equals(df2)  # Same data

    def test_file_not_found(self, temp_dir):
        """Test error handling when file doesn't exist."""
        repo = CSVDatabaseRepository(
            filepath=temp_dir / "nonexistent.csv"
        )
        
        with pytest.raises(FileNotFoundError):
            repo.load_data()

    def test_validate_schema_success(self, sample_csv):
        """Test schema validation with valid columns."""
        repo = CSVDatabaseRepository(
            filepath=sample_csv,
            required_columns=['ko', 'gene']
        )
        
        df = repo.load_data()
        assert repo.validate_schema(df) is True

    def test_validate_schema_failure(self, sample_csv):
        """Test schema validation with missing columns."""
        repo = CSVDatabaseRepository(
            filepath=sample_csv,
            required_columns=['ko', 'missing_column']
        )
        
        with pytest.raises(ValueError, match="Invalid database schema"):
            repo.load_data()

    def test_merge_with_dataset(self, sample_csv):
        """Test merging dataset with database."""
        repo = CSVDatabaseRepository(filepath=sample_csv)
        
        # Create input dataset
        input_df = pd.DataFrame({
            'ko': ['K00001', 'K00003', 'K00999'],  # K00999 doesn't exist
            'sample': ['S1', 'S2', 'S3']
        })
        
        # Merge (inner join)
        merged = repo.merge_with_dataset(input_df, on='ko', how='inner')
        
        assert len(merged) == 2  # Only K00001 and K00003 match
        assert 'sample' in merged.columns
        assert 'gene' in merged.columns

    def test_merge_with_dataset_left_join(self, sample_csv):
        """Test merging with left join."""
        repo = CSVDatabaseRepository(filepath=sample_csv)
        
        input_df = pd.DataFrame({
            'ko': ['K00001', 'K00999'],
            'sample': ['S1', 'S2']
        })
        
        merged = repo.merge_with_dataset(input_df, on='ko', how='left')
        
        assert len(merged) == 2  # All input rows preserved
        assert pd.isna(merged.iloc[1]['gene'])  # K00999 has no match

    def test_merge_missing_column(self, sample_csv):
        """Test error when merge column is missing."""
        repo = CSVDatabaseRepository(filepath=sample_csv)
        
        input_df = pd.DataFrame({
            'wrong_column': ['A', 'B']
        })
        
        with pytest.raises(ValueError, match="Column 'ko' not found"):
            repo.merge_with_dataset(input_df, on='ko')

    def test_get_column_names(self, sample_csv):
        """Test retrieving column names."""
        repo = CSVDatabaseRepository(filepath=sample_csv)
        
        columns = repo.get_column_names()
        
        assert isinstance(columns, list)
        assert 'ko' in columns
        assert 'gene' in columns
        assert 'pathway' in columns

    def test_get_stats(self, sample_csv):
        """Test getting database statistics."""
        repo = CSVDatabaseRepository(filepath=sample_csv)
        
        stats = repo.get_stats()
        
        assert stats['rows'] == 5
        assert stats['columns'] == 4
        assert 'memory_mb' in stats
        assert 'column_names' in stats
        assert 'dtypes' in stats

    def test_optimize_dtypes(self, temp_dir):
        """Test dtype optimization."""
        # Create CSV with repeating values (good for categorical)
        csv_path = temp_dir / "optimize_test.csv"
        data = pd.DataFrame({
            'ko': ['K00001'] * 100,  # Low cardinality
            'value': range(100)
        })
        data.to_csv(csv_path, sep=';', index=False)
        
        repo = CSVDatabaseRepository(filepath=csv_path)
        df = repo.load_data()
        
        # 'ko' should be converted to category (low cardinality)
        assert df['ko'].dtype.name == 'category'

    def test_different_separator(self, temp_dir):
        """Test loading CSV with different separator."""
        csv_path = temp_dir / "comma_separated.csv"
        
        data = pd.DataFrame({
            'ko': ['K00001', 'K00002'],
            'value': [10, 20]
        })
        data.to_csv(csv_path, sep=',', index=False)
        
        repo = CSVDatabaseRepository(
            filepath=csv_path,
            separator=','
        )
        
        df = repo.load_data()
        assert len(df) == 2

    def test_different_encoding(self, temp_dir):
        """Test loading CSV with different encoding."""
        csv_path = temp_dir / "utf16_file.csv"
        
        data = pd.DataFrame({
            'ko': ['K00001'],
            'text': ['São Paulo']  # UTF-16 compatible
        })
        data.to_csv(csv_path, sep=';', index=False, encoding='utf-16')
        
        repo = CSVDatabaseRepository(
            filepath=csv_path,
            encoding='utf-16'
        )
        
        df = repo.load_data()
        assert df.iloc[0]['text'] == 'São Paulo'
