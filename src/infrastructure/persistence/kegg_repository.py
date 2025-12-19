"""
KEGG Repository - Pathway Database Access.

Provides repository implementation for accessing KEGG degradation pathways
database containing pathway information for degradation processes.

Classes
-------
KEGGRepository
    Repository for KEGG degradation pathways database
"""

from pathlib import Path

from .csv_database_repository import CSVDatabaseRepository


class KEGGRepository(CSVDatabaseRepository):
    """
    Repository for KEGG degradation pathways database.

    Provides access to KEGG pathway data for degradation processes.
    Database file: data/databases/kegg_degradation_db.csv

    Attributes
    ----------
    filepath : Path
        Path to KEGG database CSV file
    encoding : str
        File encoding (default: 'utf-8')
    separator : str
        CSV separator (default: ';')
    required_columns : list[str]
        Required columns: ['ko', 'pathname']
    """

    def __init__(
        self,
        filepath: Path = Path("data/databases/kegg_degradation_db.csv"),
        encoding: str = "utf-8",
        separator: str = ";",
    ):
        """
        Initialize KEGG repository.

        Parameters
        ----------
        filepath : Path, default=Path('data/databases/kegg_degradation_db.csv')
            Path to KEGG database CSV file.
        encoding : str, default='utf-8'
            File encoding.
        separator : str, default=';'
            CSV separator.
        """
        super().__init__(
            filepath=filepath,
            encoding=encoding,
            separator=separator,
            required_columns=["ko", "pathname"],  # Nome real da coluna no CSV
        )
