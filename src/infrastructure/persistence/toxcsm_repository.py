"""
ToxCSM Repository - Toxicity Prediction Database Access.

Provides repository implementation for accessing ToxCSM (Toxicity Prediction)
database containing toxicity predictions for environmental compounds.

Classes
-------
ToxCSMRepository
    Repository for ToxCSM toxicity prediction database
"""

from pathlib import Path

import pandas as pd

from src.shared.logging import get_logger

from .csv_database_repository import CSVDatabaseRepository

logger = get_logger(__name__)


class ToxCSMRepository(CSVDatabaseRepository):
    """
    Repository for ToxCSM toxicity prediction database.

    Provides access to compound-level toxicity predictions.
    Database file: data/databases/toxcsm_db.csv

    Attributes
    ----------
    filepath : Path
        Path to ToxCSM database CSV file
    encoding : str
        File encoding (default: 'utf-8')
    separator : str
        CSV separator (default: ';')
    required_columns : list[str]
        Required columns: ['cpd']

    Methods
    -------
    merge_with_compound_data(compound_df, on, how)
        Merge compound data with toxicity predictions

    Notes
    -----
    - Merges on 'cpd' column instead of 'ko' (compound-level data)
    """

    def __init__(
        self,
        filepath: Path = Path("data/databases/toxcsm_db.csv"),
        encoding: str = "utf-8",
        separator: str = ";",
    ):
        """
        Initialize ToxCSM repository.

        Parameters
        ----------
        filepath : Path, default=Path('data/databases/toxcsm_db.csv')
            Path to ToxCSM database CSV file.
        encoding : str, default='utf-8'
            File encoding.
        separator : str, default=';'
            CSV separator.
        """
        super().__init__(
            filepath=filepath,
            encoding=encoding,
            separator=separator,
            required_columns=["cpd"],  # Nome real da coluna no CSV
        )

    def merge_with_compound_data(
        self,
        compound_df: pd.DataFrame,
        on: str = "cpd",  # Atualizar nome da coluna padrão
        how: str = "left",
    ) -> pd.DataFrame:
        """
        Merge compound data with toxicity predictions.

        Parameters
        ----------
        compound_df : pd.DataFrame
            DataFrame containing compound information (must have join column)
        on : str, default='cpd'
            Column to join on
        how : str, default='left'
            Join type (default 'left' keeps all compounds)

        Returns
        -------
        pd.DataFrame
            Merged DataFrame with toxicity predictions
        """
        logger.info(
            "Merging compound data with ToxCSM predictions",
            extra={"input_rows": len(compound_df)},
        )

        return self.merge_with_dataset(dataset_df=compound_df, on=on, how=how)
