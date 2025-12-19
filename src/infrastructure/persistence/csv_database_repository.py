"""
CSV Database Repository - Base Implementation.

Provides base class for CSV-based database repositories with lazy loading,
caching, schema validation, and merge operations.

Classes
-------
CSVDatabaseRepository
    Base class for CSV database operations with caching and validation
"""

from pathlib import Path
from typing import Optional

import pandas as pd

from src.shared.logging import get_logger

logger = get_logger(__name__)


class CSVDatabaseRepository:
    """
    Base implementation for CSV-based database repositories.

    Provides common functionality for loading, caching, validating, and merging
    CSV databases. Specific database repositories inherit from this class.

    Attributes
    ----------
    filepath : Path
        Path to CSV database file
    encoding : str
        File encoding (default: 'utf-8')
    separator : str
        CSV separator (default: ';')
    required_columns : list[str]
        List of required column names for validation
    _data : Optional[pd.DataFrame]
        Cached database data (lazy loaded)

    Methods
    -------
    load_data()
        Load CSV database with caching
    reload_data()
        Force reload database from file
    merge_with_dataset(dataset_df, on, how)
        Merge dataset with database
    get_column_names()
        Get column names from database
    validate_schema(df)
        Validate database schema
    get_stats()
        Get database statistics

    Notes
    -----
    - Implements lazy loading with caching for performance
    - Optimizes dtypes to reduce memory usage
    """

    def __init__(
        self,
        filepath: Path,
        encoding: str = "utf-8",
        separator: str = ";",
        required_columns: Optional[list[str]] = None,
    ):
        """
        Initialize CSV database repository.

        Parameters
        ----------
        filepath : Path
            Path to CSV file.
        encoding : str, default='utf-8'
            File encoding.
        separator : str, default=';'
            CSV separator.
        required_columns : Optional[list[str]], default=None
            List of required column names for validation.
        """
        self.filepath = filepath
        self.encoding = encoding
        self.separator = separator
        self.required_columns = required_columns or []
        self._data: Optional[pd.DataFrame] = None

        logger.info(
            f"Initialized {self.__class__.__name__}",
            extra={
                "filepath": str(filepath),
                "encoding": encoding,
                "separator": separator,
                "required_columns": self.required_columns,
            },
        )

    def load_data(self) -> pd.DataFrame:
        """
        Load CSV database into DataFrame with caching.

        Returns
        -------
        pd.DataFrame
            Database data with optimized dtypes

        Raises
        ------
        FileNotFoundError
            If CSV file doesn't exist
        ValueError
            If CSV format is invalid or required columns missing
        """
        if self._data is not None:
            logger.debug(
                f"Using cached data for {self.filepath.name}",
                extra={"rows": len(self._data)},
            )
            return self._data

        logger.info(f"Loading database from {self.filepath}")

        if not self.filepath.exists():
            error_msg = f"Database file not found: {self.filepath}"
            logger.error(error_msg)
            raise FileNotFoundError(error_msg)

        try:
            # Load CSV
            df = pd.read_csv(self.filepath, encoding=self.encoding, sep=self.separator)

            # Validate schema
            if not self.validate_schema(df):
                raise ValueError(
                    f"Invalid database schema. "
                    f"Required columns: {self.required_columns}"
                )

            # Optimize dtypes
            df = self._optimize_dtypes(df)

            # Cache
            self._data = df

            logger.info(
                f"Successfully loaded database: {self.filepath.name}",
                extra={
                    "rows": len(df),
                    "columns": len(df.columns),
                    "memory_mb": round(df.memory_usage(deep=True).sum() / 1024**2, 2),
                },
            )

            return df

        except Exception as e:
            logger.error(f"Failed to load database: {e}")
            raise

    def reload_data(self) -> pd.DataFrame:
        """
        Force reload database from file.

        Clears cache and reloads data from CSV file.

        Returns
        -------
        pd.DataFrame
            Freshly loaded database data
        """
        logger.info(f"Forcing reload of {self.filepath.name}")
        self._data = None
        return self.load_data()

    def merge_with_dataset(
        self, dataset_df: pd.DataFrame, on: str = "ko", how: str = "inner"
    ) -> pd.DataFrame:
        """
        Merge dataset with database.

        Parameters
        ----------
        dataset_df : pd.DataFrame
            Input dataset (must have join column)
        on : str, default='ko'
            Column name to join on
        how : str, default='inner'
            Join type ('inner', 'left', 'right', 'outer')

        Returns
        -------
        pd.DataFrame
            Merged DataFrame

        Raises
        ------
        ValueError
            If join column missing in either DataFrame
        """
        logger.info(
            f"Merging dataset with {self.__class__.__name__}",
            extra={"on": on, "how": how, "input_rows": len(dataset_df)},
        )

        # Load database if not already loaded
        db_df = self.load_data()

        # Validate join column exists
        if on not in dataset_df.columns:
            error_msg = f"Column '{on}' not found in dataset"
            logger.error(error_msg)
            raise ValueError(error_msg)

        if on not in db_df.columns:
            error_msg = f"Column '{on}' not found in database"
            logger.error(error_msg)
            raise ValueError(error_msg)

        # Perform merge
        merged = pd.merge(dataset_df, db_df, on=on, how=how)

        # Calculate match rate
        match_rate = len(merged) / len(dataset_df) * 100 if len(dataset_df) > 0 else 0

        logger.info(
            f"Merge completed",
            extra={
                "input_rows": len(dataset_df),
                "database_rows": len(db_df),
                "output_rows": len(merged),
                "match_rate_percent": round(match_rate, 2),
            },
        )

        return merged

    def get_column_names(self) -> list[str]:
        """
        Get column names from database.

        Returns
        -------
        list[str]
            List of column names
        """
        df = self.load_data()
        return df.columns.tolist()

    def validate_schema(self, df: Optional[pd.DataFrame] = None) -> bool:
        """
        Validate database schema.

        Checks if all required columns are present in DataFrame.

        Parameters
        ----------
        df : Optional[pd.DataFrame], default=None
            DataFrame to validate (if None, loads from file)

        Returns
        -------
        bool
            True if all required columns present, False otherwise
        """
        if df is None:
            df = self.load_data()

        if not self.required_columns:
            # No required columns specified, always valid
            return True

        missing = set(self.required_columns) - set(df.columns)

        if missing:
            logger.warning(
                f"Missing required columns in {self.filepath.name}",
                extra={
                    "missing_columns": list(missing),
                    "required": self.required_columns,
                    "found": df.columns.tolist(),
                },
            )
            return False

        return True

    def _optimize_dtypes(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Optimize DataFrame dtypes to reduce memory usage.

        Converts low-cardinality object columns to category and downcasts
        numeric columns to smallest possible dtype.

        Parameters
        ----------
        df : pd.DataFrame
            DataFrame to optimize

        Returns
        -------
        pd.DataFrame
            Optimized DataFrame with reduced memory footprint
        """
        original_memory = df.memory_usage(deep=True).sum()

        # Convert low-cardinality strings to category
        for col in df.select_dtypes(include="object").columns:
            num_unique = df[col].nunique()
            num_total = len(df[col])

            # If less than 50% unique values, convert to category
            if num_unique / num_total < 0.5:
                df[col] = df[col].astype("category")

        # Downcast numeric columns
        for col in df.select_dtypes(include=["int", "float"]).columns:
            df[col] = pd.to_numeric(df[col], downcast="integer")

        optimized_memory = df.memory_usage(deep=True).sum()
        reduction = (1 - optimized_memory / original_memory) * 100

        logger.debug(
            f"Optimized dtypes for {self.filepath.name}",
            extra={
                "original_mb": round(original_memory / 1024**2, 2),
                "optimized_mb": round(optimized_memory / 1024**2, 2),
                "reduction_percent": round(reduction, 2),
            },
        )

        return df

    def get_stats(self) -> dict:
        """
        Get database statistics.

        Returns
        -------
        dict
            Dictionary containing:
            - 'rows': Number of rows
            - 'columns': Number of columns
            - 'memory_mb': Memory usage in MB
            - 'column_names': List of column names
            - 'dtypes': Dictionary of column datatypes
        """
        df = self.load_data()

        return {
            "rows": len(df),
            "columns": len(df.columns),
            "memory_mb": round(df.memory_usage(deep=True).sum() / 1024**2, 2),
            "column_names": df.columns.tolist(),
            "dtypes": df.dtypes.astype(str).to_dict(),
        }
