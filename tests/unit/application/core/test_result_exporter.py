"""
Unit tests for ResultExporter.

Tests cover:
- CSV export (happy path and edge cases)
- Excel export (happy path and edge cases)
- JSON export (happy path and edge cases)
- Generic export method
- Error handling
- Validation
"""

import pytest
import pandas as pd
from biorempp_web.src.application.core.result_exporter import (
    ResultExporter,
    ExportFormat,
    ExportResultDTO
)


class TestExportResultDTO:
    """Test ExportResultDTO validation."""
    
    def test_successful_export_dto_valid(self):
        """Test successful export DTO creation."""
        dto = ExportResultDTO(
            success=True,
            format=ExportFormat.CSV,
            data=b"test data",
            filename="test.csv",
            size_bytes=9,
            message="Success"
        )
        assert dto.success
        assert dto.data == b"test data"
        assert dto.error is None
    
    def test_failed_export_dto_valid(self):
        """Test failed export DTO creation."""
        dto = ExportResultDTO(
            success=False,
            format=ExportFormat.CSV,
            data=None,
            filename="test.csv",
            size_bytes=0,
            message="Failed",
            error="Error occurred"
        )
        assert not dto.success
        assert dto.error == "Error occurred"
    
    def test_successful_export_without_data_raises_error(self):
        """Test that successful export must have data."""
        with pytest.raises(ValueError, match="must have data"):
            ExportResultDTO(
                success=True,
                format=ExportFormat.CSV,
                data=None,
                filename="test.csv",
                size_bytes=0,
                message="Success"
            )
    
    def test_failed_export_without_error_raises_error(self):
        """Test that failed export must have error message."""
        with pytest.raises(ValueError, match="must have error"):
            ExportResultDTO(
                success=False,
                format=ExportFormat.CSV,
                data=None,
                filename="test.csv",
                size_bytes=0,
                message="Failed"
            )
    
    def test_negative_size_raises_error(self):
        """Test that size cannot be negative."""
        with pytest.raises(ValueError, match="cannot be negative"):
            ExportResultDTO(
                success=False,
                format=ExportFormat.CSV,
                data=None,
                filename="test.csv",
                size_bytes=-1,
                message="Failed",
                error="Error"
            )


class TestResultExporterCSV:
    """Test CSV export functionality."""
    
    @pytest.fixture
    def exporter(self):
        """Create ResultExporter instance."""
        return ResultExporter()
    
    @pytest.fixture
    def sample_df(self):
        """Create sample DataFrame for testing."""
        return pd.DataFrame({
            "Sample": ["S1", "S2", "S3"],
            "KO": ["K00001", "K00002", "K00003"],
            "Value": [10, 20, 30]
        })
    
    def test_export_csv_success(self, exporter, sample_df):
        """Test successful CSV export."""
        result = exporter.export_to_csv(sample_df, "test.csv")
        
        assert result.success
        assert result.format == ExportFormat.CSV
        assert result.data is not None
        assert result.filename == "test.csv"
        assert result.size_bytes > 0
        assert result.error is None
        assert "3 rows" in result.message
    
    def test_export_csv_adds_extension(self, exporter, sample_df):
        """Test that .csv extension is added if missing."""
        result = exporter.export_to_csv(sample_df, "test")
        
        assert result.filename == "test.csv"
    
    def test_export_csv_with_index(self, exporter, sample_df):
        """Test CSV export with index included."""
        result = exporter.export_to_csv(sample_df, "test.csv", index=True)
        
        assert result.success
        # Check that index column is in the data
        csv_content = result.data.decode('utf-8')
        assert csv_content.startswith(',')  # First column is index
    
    def test_export_csv_empty_dataframe(self, exporter):
        """Test CSV export with empty DataFrame."""
        empty_df = pd.DataFrame()
        result = exporter.export_to_csv(empty_df, "test.csv")
        
        assert not result.success
        assert result.data is None
        assert "empty" in result.error.lower()
    
    def test_export_csv_none_dataframe(self, exporter):
        """Test CSV export with None DataFrame."""
        result = exporter.export_to_csv(None, "test.csv")
        
        assert not result.success
        assert result.data is None
        assert "empty or None" in result.error


class TestResultExporterExcel:
    """Test Excel export functionality."""
    
    @pytest.fixture
    def exporter(self):
        """Create ResultExporter instance."""
        return ResultExporter()
    
    @pytest.fixture
    def sample_df(self):
        """Create sample DataFrame for testing."""
        return pd.DataFrame({
            "Sample": ["S1", "S2"],
            "KO": ["K00001", "K00002"]
        })
    
    def test_export_excel_success(self, exporter, sample_df):
        """Test successful Excel export."""
        result = exporter.export_to_excel(sample_df, "test.xlsx")
        
        assert result.success
        assert result.format == ExportFormat.EXCEL
        assert result.data is not None
        assert result.filename == "test.xlsx"
        assert result.size_bytes > 0
        assert result.error is None
    
    def test_export_excel_adds_extension(self, exporter, sample_df):
        """Test that .xlsx extension is added if missing."""
        result = exporter.export_to_excel(sample_df, "test")
        
        assert result.filename == "test.xlsx"
    
    def test_export_excel_custom_sheet_name(self, exporter, sample_df):
        """Test Excel export with custom sheet name."""
        result = exporter.export_to_excel(
            sample_df, 
            "test.xlsx", 
            sheet_name="CustomSheet"
        )
        
        assert result.success
        # Note: We can't easily verify sheet name without reading back
        # but at least we test it doesn't crash
    
    def test_export_excel_empty_dataframe(self, exporter):
        """Test Excel export with empty DataFrame."""
        empty_df = pd.DataFrame()
        result = exporter.export_to_excel(empty_df, "test.xlsx")
        
        assert not result.success
        assert result.data is None
        assert "empty" in result.error.lower()
    
    def test_export_excel_none_dataframe(self, exporter):
        """Test Excel export with None DataFrame."""
        result = exporter.export_to_excel(None, "test.xlsx")
        
        assert not result.success
        assert result.error == "Data is empty or None"


class TestResultExporterJSON:
    """Test JSON export functionality."""
    
    @pytest.fixture
    def exporter(self):
        """Create ResultExporter instance."""
        return ResultExporter()
    
    @pytest.fixture
    def sample_df(self):
        """Create sample DataFrame for testing."""
        return pd.DataFrame({
            "Sample": ["S1", "S2"],
            "Value": [100, 200]
        })
    
    def test_export_json_success(self, exporter, sample_df):
        """Test successful JSON export."""
        result = exporter.export_to_json(sample_df, "test.json")
        
        assert result.success
        assert result.format == ExportFormat.JSON
        assert result.data is not None
        assert result.filename == "test.json"
        assert result.size_bytes > 0
        assert result.error is None
    
    def test_export_json_adds_extension(self, exporter, sample_df):
        """Test that .json extension is added if missing."""
        result = exporter.export_to_json(sample_df, "test")
        
        assert result.filename == "test.json"
    
    def test_export_json_records_orient(self, exporter, sample_df):
        """Test JSON export with records orientation."""
        result = exporter.export_to_json(sample_df, "test.json", orient="records")
        
        assert result.success
        json_str = result.data.decode('utf-8')
        assert json_str.startswith('[')  # Records orient creates array
    
    def test_export_json_empty_dataframe(self, exporter):
        """Test JSON export with empty DataFrame."""
        empty_df = pd.DataFrame()
        result = exporter.export_to_json(empty_df, "test.json")
        
        assert not result.success
        assert result.data is None
    
    def test_export_json_none_dataframe(self, exporter):
        """Test JSON export with None DataFrame."""
        result = exporter.export_to_json(None, "test.json")
        
        assert not result.success
        assert "empty or None" in result.error


class TestResultExporterGeneric:
    """Test generic export method."""
    
    @pytest.fixture
    def exporter(self):
        """Create ResultExporter instance."""
        return ResultExporter()
    
    @pytest.fixture
    def sample_df(self):
        """Create sample DataFrame for testing."""
        return pd.DataFrame({"A": [1, 2, 3]})
    
    def test_export_csv_via_generic(self, exporter, sample_df):
        """Test CSV export via generic method."""
        result = exporter.export(sample_df, ExportFormat.CSV, "test.csv")
        
        assert result.success
        assert result.format == ExportFormat.CSV
    
    def test_export_excel_via_generic(self, exporter, sample_df):
        """Test Excel export via generic method."""
        result = exporter.export(sample_df, ExportFormat.EXCEL, "test.xlsx")
        
        assert result.success
        assert result.format == ExportFormat.EXCEL
    
    def test_export_json_via_generic(self, exporter, sample_df):
        """Test JSON export via generic method."""
        result = exporter.export(sample_df, ExportFormat.JSON, "test.json")
        
        assert result.success
        assert result.format == ExportFormat.JSON
    
    def test_export_with_options(self, exporter, sample_df):
        """Test export with format-specific options."""
        options = {"index": True}
        result = exporter.export(
            sample_df, 
            ExportFormat.CSV, 
            "test.csv", 
            options=options
        )
        
        assert result.success
        csv_content = result.data.decode('utf-8')
        assert csv_content.startswith(',')  # Index included
