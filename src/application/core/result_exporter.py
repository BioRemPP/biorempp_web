"""
Application Layer - Result Exporter.

This module provides functionality to export analysis results in multiple formats
(CSV, Excel, JSON) following Clean Architecture principles.

Classes
-------
ResultExporter
    Export processed data to various file formats with validation.

Notes
-----
- Follows Single Responsibility Principle (export only)
- Immutable operations (does not modify input data)
- Type-safe with comprehensive validation
- Supports multiple export formats
"""

import json
from dataclasses import dataclass
from enum import Enum
from io import BytesIO
from pathlib import Path
from typing import Any, Dict, Optional

import pandas as pd


class ExportFormat(Enum):
    """
    Supported export file formats.

    Attributes
    ----------
    CSV : str
        Comma-separated values format
    EXCEL : str
        Microsoft Excel format (.xlsx)
    JSON : str
        JavaScript Object Notation format
    """

    CSV = "csv"
    EXCEL = "excel"
    JSON = "json"


@dataclass(frozen=True)
class ExportResultDTO:
    """
    Data Transfer Object for export operation results.

    Attributes
    ----------
    success : bool
        Whether the export operation succeeded
    format : ExportFormat
        The format used for export
    data : Optional[bytes]
        The exported data as bytes (None if failed)
    filename : str
        The suggested filename for the export
    size_bytes : int
        Size of exported data in bytes
    message : str
        Human-readable status message
    error : Optional[str]
        Error message if export failed
    """

    success: bool
    format: ExportFormat
    data: Optional[bytes]
    filename: str
    size_bytes: int
    message: str
    error: Optional[str] = None

    def __post_init__(self) -> None:
        """Validate DTO consistency after initialization."""
        if self.success and self.data is None:
            raise ValueError("Successful export must have data")
        if not self.success and self.error is None:
            raise ValueError("Failed export must have error message")
        if self.size_bytes < 0:
            raise ValueError("Size cannot be negative")


class ResultExporter:
    """
    Export analysis results to multiple file formats.

    Handles the export of processed data (DataFrames) to various formats with
    proper validation and error handling. Follows Clean Architecture by
    operating on DTOs and not depending on infrastructure details.

    Methods
    -------
    export_to_csv(data, filename)
        Export DataFrame to CSV format
    export_to_excel(data, filename, sheet_name)
        Export DataFrame to Excel format
    export_to_json(data, filename, orient)
        Export DataFrame to JSON format
    export(data, format, filename, options)
        Generic export method with format selection

    Notes
    -----
    - All methods return ExportResultDTO
    - Input data is never modified (immutable operations)
    - Validates data before export
    - Handles encoding errors gracefully
    """

    def __init__(self) -> None:
        """
        Initialize the ResultExporter.

        No dependencies required - pure export logic.
        """
        pass

    def export_to_csv(
        self,
        data: pd.DataFrame,
        filename: str,
        index: bool = False,
        encoding: str = "utf-8",
    ) -> ExportResultDTO:
        """
        Export DataFrame to CSV format.

        Parameters
        ----------
        data : pd.DataFrame
            The data to export
        filename : str
            The suggested filename (will ensure .csv extension)
        index : bool, default=False
            Whether to include index in export
        encoding : str, default="utf-8"
            Character encoding to use

        Returns
        -------
        ExportResultDTO
            Result of the export operation including data bytes

        Raises
        ------
        ValueError
            If data is empty or invalid

        Notes
        -----
        - Ensures filename has .csv extension
        - Returns data as UTF-8 encoded bytes
        - Includes header row by default
        """
        try:
            # Validate input
            if data is None or data.empty:
                return ExportResultDTO(
                    success=False,
                    format=ExportFormat.CSV,
                    data=None,
                    filename=filename,
                    size_bytes=0,
                    message="Export failed",
                    error="Data is empty or None",
                )

            # Ensure .csv extension
            if not filename.endswith(".csv"):
                filename = f"{filename}.csv"

            # Convert to CSV
            csv_data = data.to_csv(index=index, encoding=encoding)
            data_bytes = csv_data.encode(encoding)

            return ExportResultDTO(
                success=True,
                format=ExportFormat.CSV,
                data=data_bytes,
                filename=filename,
                size_bytes=len(data_bytes),
                message=f"Exported {len(data)} rows to CSV",
            )

        except Exception as e:
            return ExportResultDTO(
                success=False,
                format=ExportFormat.CSV,
                data=None,
                filename=filename,
                size_bytes=0,
                message="Export failed",
                error=f"CSV export error: {str(e)}",
            )

    def export_to_excel(
        self,
        data: pd.DataFrame,
        filename: str,
        sheet_name: str = "Results",
        index: bool = False,
    ) -> ExportResultDTO:
        """
        Export DataFrame to Excel format.

        Parameters
        ----------
        data : pd.DataFrame
            The data to export
        filename : str
            The suggested filename (will ensure .xlsx extension)
        sheet_name : str, default="Results"
            Name of the Excel sheet
        index : bool, default=False
            Whether to include index in export

        Returns
        -------
        ExportResultDTO
            Result of the export operation including data bytes

        Notes
        -----
        - Ensures filename has .xlsx extension
        - Uses openpyxl engine for writing
        - Returns data as binary bytes
        """
        try:
            # Validate input
            if data is None or data.empty:
                return ExportResultDTO(
                    success=False,
                    format=ExportFormat.EXCEL,
                    data=None,
                    filename=filename,
                    size_bytes=0,
                    message="Export failed",
                    error="Data is empty or None",
                )

            # Ensure .xlsx extension
            if not filename.endswith(".xlsx"):
                filename = f"{filename}.xlsx"

            # Convert to Excel
            buffer = BytesIO()
            with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
                data.to_excel(writer, sheet_name=sheet_name, index=index)

            data_bytes = buffer.getvalue()

            return ExportResultDTO(
                success=True,
                format=ExportFormat.EXCEL,
                data=data_bytes,
                filename=filename,
                size_bytes=len(data_bytes),
                message=f"Exported {len(data)} rows to Excel",
            )

        except Exception as e:
            return ExportResultDTO(
                success=False,
                format=ExportFormat.EXCEL,
                data=None,
                filename=filename,
                size_bytes=0,
                message="Export failed",
                error=f"Excel export error: {str(e)}",
            )

    def export_to_json(
        self,
        data: pd.DataFrame,
        filename: str,
        orient: str = "records",
        indent: int = 2,
    ) -> ExportResultDTO:
        """
        Export DataFrame to JSON format.

        Parameters
        ----------
        data : pd.DataFrame
            The data to export
        filename : str
            The suggested filename (will ensure .json extension)
        orient : str, default="records"
            JSON orientation ('records', 'index', 'columns')
        indent : int, default=2
            JSON indentation level for readability

        Returns
        -------
        ExportResultDTO
            Result of the export operation including data bytes

        Notes
        -----
        - Ensures filename has .json extension
        - Default orient='records' creates array of objects
        - Returns data as UTF-8 encoded bytes
        """
        try:
            # Validate input
            if data is None or data.empty:
                return ExportResultDTO(
                    success=False,
                    format=ExportFormat.JSON,
                    data=None,
                    filename=filename,
                    size_bytes=0,
                    message="Export failed",
                    error="Data is empty or None",
                )

            # Ensure .json extension
            if not filename.endswith(".json"):
                filename = f"{filename}.json"

            # Convert to JSON
            json_data = data.to_json(orient=orient, indent=indent)
            data_bytes = json_data.encode("utf-8")

            return ExportResultDTO(
                success=True,
                format=ExportFormat.JSON,
                data=data_bytes,
                filename=filename,
                size_bytes=len(data_bytes),
                message=f"Exported {len(data)} rows to JSON",
            )

        except Exception as e:
            return ExportResultDTO(
                success=False,
                format=ExportFormat.JSON,
                data=None,
                filename=filename,
                size_bytes=0,
                message="Export failed",
                error=f"JSON export error: {str(e)}",
            )

    def export(
        self,
        data: pd.DataFrame,
        format: ExportFormat,
        filename: str,
        options: Optional[Dict[str, Any]] = None,
    ) -> ExportResultDTO:
        """
        Generic export method with format selection.

        Parameters
        ----------
        data : pd.DataFrame
            The data to export
        format : ExportFormat
            The desired export format
        filename : str
            The suggested filename
        options : Optional[Dict[str, Any]], default=None
            Format-specific options

        Returns
        -------
        ExportResultDTO
            Result of the export operation

        Notes
        -----
        - Routes to appropriate export method based on format
        - Passes options to specific export methods
        - Validates format before export
        """
        if options is None:
            options = {}

        if format == ExportFormat.CSV:
            return self.export_to_csv(data, filename, **options)
        elif format == ExportFormat.EXCEL:
            return self.export_to_excel(data, filename, **options)
        elif format == ExportFormat.JSON:
            return self.export_to_json(data, filename, **options)
        else:
            return ExportResultDTO(
                success=False,
                format=format,
                data=None,
                filename=filename,
                size_bytes=0,
                message="Export failed",
                error=f"Unsupported export format: {format}",
            )
