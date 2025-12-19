"""
HADEG Repository - Enzyme Database Access.

Provides repository implementation for accessing HADEG (Hydrocarbon Aerobic
Degrading Enzymes) database containing enzyme information for hydrocarbon
degradation.

Classes
-------
HADEGRepository
    Repository for HADEG enzyme database
"""

from pathlib import Path

from .csv_database_repository import CSVDatabaseRepository


class HADEGRepository(CSVDatabaseRepository):
    """
    Repository for HADEG enzyme database.

    Provides access to enzyme data for hydrocarbon degradation pathways.
    Database file: data/databases/hadeg_db.csv

    Attributes
    ----------
    filepath : Path
        Path to HADEG database CSV file
    encoding : str
        File encoding (default: 'utf-8')
    separator : str
        CSV separator (default: ';')
    required_columns : list[str]
        Required columns: ['ko', 'Gene', 'Pathway']
    """

    def __init__(
        self,
        filepath: Path = Path("data/databases/hadeg_db.csv"),
        encoding: str = "utf-8",
        separator: str = ";",
    ):
        """
        Initialize HADEG repository.

        Parameters
        ----------
        filepath : Path, default=Path('data/databases/hadeg_db.csv')
            Path to HADEG database CSV file.
        encoding : str, default='utf-8'
            File encoding.
        separator : str, default=';'
            CSV separator.
        """
        super().__init__(
            filepath=filepath,
            encoding=encoding,
            separator=separator,
            required_columns=[
                "ko",
                "Gene",
                "Pathway",
            ],  # Nome real: Pathway com maiúscula
        )
