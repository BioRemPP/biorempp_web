"""
Database Configuration - Path Management.

Provides configuration management for database file paths and connection
settings for all four databases.

Classes
-------
DatabaseConfig
    Database configuration manager for file paths and settings
"""

from pathlib import Path
from typing import Dict, Optional

import yaml

from src.shared.logging import get_logger

logger = get_logger(__name__)


class DatabaseConfig:
    """
    Database configuration manager.

    Manages paths and settings for all four databases: BioRemPP, KEGG,
    HADEG, and ToxCSM.

    Attributes
    ----------
    config_file : Path
        Path to database config YAML file
    _config : Dict[str, Dict[str, str]]
        Loaded database configurations

    Methods
    -------
    get_database_path(database_name)
        Get database file path
    get_database_encoding(database_name, default)
        Get database file encoding
    get_database_separator(database_name, default)
        Get database CSV separator
    get_all_database_paths()
        Get all database paths
    validate_paths()
        Validate that all database files exist
    get_database_info(database_name)
        Get complete database configuration
    get_available_databases()
        Get list of available database names
    """

    def __init__(self, config_file: Optional[Path] = None):
        """
        Initialize database configuration.

        Parameters
        ----------
        config_file : Optional[Path], default=None
            Path to database config YAML file.
            Defaults to 'config/databases.yaml'.
        """
        if config_file is None:
            config_file = Path("config/databases.yaml")

        self.config_file = config_file
        self._config: Dict[str, Dict[str, str]] = {}
        self._load_config()

    def _load_config(self) -> None:
        """Load database configuration from YAML file."""
        if not self.config_file.exists():
            logger.warning(
                f"Database config not found: {self.config_file}. "
                "Using default paths."
            )
            self._config = self._get_default_config()
            return

        try:
            with open(self.config_file, "r", encoding="utf-8") as f:
                self._config = yaml.safe_load(f) or {}

            logger.info(
                f"Loaded database config from {self.config_file}",
                extra={"databases": list(self._config.keys())},
            )

        except Exception as e:
            logger.error(f"Failed to load database config: {e}")
            self._config = self._get_default_config()

    def _get_default_config(self) -> Dict[str, Dict[str, str]]:
        """
        Get default database configuration.

        Returns
        -------
        Dict[str, Dict[str, str]]
            Default database paths and settings.
        """
        return {
            "biorempp": {
                "filepath": "data/databases/biorempp_db.csv",
                "encoding": "utf-8",
                "separator": ";",
                "description": "BioRemPP main database",
            },
            "kegg": {
                "filepath": "data/databases/kegg_degradation_db.csv",
                "encoding": "utf-8",
                "separator": ";",
                "description": "KEGG degradation pathways",
            },
            "hadeg": {
                "filepath": "data/databases/hadeg_db.csv",
                "encoding": "utf-8",
                "separator": ";",
                "description": "HADEG enzyme database",
            },
            "toxcsm": {
                "filepath": "data/databases/toxcsm_db.csv",
                "encoding": "utf-8",
                "separator": ";",
                "description": "ToxCSM toxicity predictions",
            },
        }

    def get_database_path(self, database_name: str) -> Path:
        """
        Get database file path.

        Parameters
        ----------
        database_name : str
            Database name ('biorempp', 'kegg', 'hadeg', 'toxcsm')

        Returns
        -------
        Path
            Path to database file

        Raises
        ------
        ValueError
            If database name is unknown
        """
        if database_name not in self._config:
            available = list(self._config.keys())
            raise ValueError(
                f"Unknown database: '{database_name}'. " f"Available: {available}"
            )

        filepath = self._config[database_name]["filepath"]
        return Path(filepath)

    def get_database_encoding(self, database_name: str, default: str = "utf-8") -> str:
        """
        Get database file encoding.

        Parameters
        ----------
        database_name : str
            Database name.
        default : str, default='utf-8'
            Default encoding if not specified.

        Returns
        -------
        str
            File encoding.
        """
        if database_name not in self._config:
            return default

        return self._config[database_name].get("encoding", default)

    def get_database_separator(self, database_name: str, default: str = ";") -> str:
        """
        Get database CSV separator.

        Parameters
        ----------
        database_name : str
            Database name.
        default : str, default=';'
            Default separator if not specified.

        Returns
        -------
        str
            CSV separator.
        """
        if database_name not in self._config:
            return default

        return self._config[database_name].get("separator", default)

    def get_all_database_paths(self) -> Dict[str, Path]:
        """
        Get all database paths.

        Returns
        -------
        Dict[str, Path]
            Dictionary mapping database names to paths
        """
        return {name: Path(cfg["filepath"]) for name, cfg in self._config.items()}

    def validate_paths(self) -> Dict[str, bool]:
        """
        Validate that all database files exist.

        Returns
        -------
        Dict[str, bool]
            Dictionary mapping database names to existence status
        """
        status = {}

        for name, path in self.get_all_database_paths().items():
            exists = path.exists()
            status[name] = exists

            if not exists:
                logger.warning(f"Database file not found: {name} ({path})")

        return status

    def get_database_info(self, database_name: str) -> Dict[str, str]:
        """
        Get complete database configuration.

        Parameters
        ----------
        database_name : str
            Database name.

        Returns
        -------
        Dict[str, str]
            Database configuration dictionary.

        Raises
        ------
        ValueError
            If database name is unknown.
        """
        if database_name not in self._config:
            available = list(self._config.keys())
            raise ValueError(
                f"Unknown database: '{database_name}'. " f"Available: {available}"
            )

        return self._config[database_name].copy()

    def get_available_databases(self) -> list[str]:
        """
        Get list of available database names.

        Returns
        -------
        list[str]
            List of database names.
        """
        return list(self._config.keys())
