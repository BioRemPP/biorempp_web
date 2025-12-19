"""
BioRemPP Repository - Bioremediation Database Access.

Provides repository implementation for accessing BioRemPP database containing
bioremediation information mapped to KEGG Orthology identifiers.

Classes
-------
BioRemPPRepository
    Repository for BioRemPP bioremediation database
"""

from pathlib import Path

from .csv_database_repository import CSVDatabaseRepository


class BioRemPPRepository(CSVDatabaseRepository):
    """
    Repository for BioRemPP bioremediation database.

    Provides access to bioremediation data mapped to KEGG Orthology IDs.
    Database file: data/databases/biorempp_db.csv

    Attributes
    ----------
    filepath : Path
        Path to BioRemPP database CSV file
    encoding : str
        File encoding (default: 'utf-8')
    separator : str
        CSV separator (default: ';')
    required_columns : list[str]
        Required columns: ['ko']
    """

    def __init__(
        self,
        filepath: Path = Path("data/databases/biorempp_db.csv"),
        encoding: str = "utf-8",
        separator: str = ";",
    ):
        """
        Initialize BioRemPP repository.

        Parameters
        ----------
        filepath : Path, default=Path('data/databases/biorempp_db.csv')
            Path to BioRemPP database CSV file.
        encoding : str, default='utf-8'
            File encoding.
        separator : str, default=';'
            CSV separator.
        """
        super().__init__(
            filepath=filepath,
            encoding=encoding,
            separator=separator,
            required_columns=["ko"],  # Minimum required column
        )
