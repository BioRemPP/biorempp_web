"""
Plot Configuration Loader.

Loads YAML configuration files for plot use cases.

Classes
-------
PlotConfigLoader
    Loads and caches YAML configurations.

Notes
-----
Configurations are loaded from:
src/infrastructure/plot_configs/module{N}/uc_{X}_{Y}_config.yaml
"""

import logging
from pathlib import Path
from typing import Any, Dict

import yaml

logger = logging.getLogger(__name__)


class PlotConfigLoader:
    """
    Configuration loader for plot use cases.

    Loads YAML configuration files and caches them in memory for performance.

    Attributes
    ----------
    config_dir : Path
        Base directory for configurations
    _cache : Dict[str, Dict[str, Any]]
        Configuration cache
    """

    def __init__(self, config_dir: str = "src/infrastructure/plot_configs"):
        """
        Initialize configuration loader.

        Parameters
        ----------
        config_dir : str, default="src/infrastructure/plot_configs"
            Base directory for plot configurations.
        """
        self.config_dir = Path(config_dir)
        self._cache: Dict[str, Dict[str, Any]] = {}
        logger.info(f"PlotConfigLoader initialized: {self.config_dir}")

    def load_config(
        self, use_case_id: str, force_reload: bool = False
    ) -> Dict[str, Any]:
        """
        Load configuration for given use case.

        Configuration file naming convention:
        - UC-2.1 -> module2/uc_2_1_config.yaml
        - UC-3.4 -> module3/uc_3_4_config.yaml

        Parameters
        ----------
        use_case_id : str
            Use case identifier (e.g., "UC-2.1")
        force_reload : bool, default=False
            Force reload from file (bypass cache)

        Returns
        -------
        Dict[str, Any]
            Configuration dictionary

        Raises
        ------
        FileNotFoundError
            If configuration file not found
        ValueError
            If YAML is invalid
        """
        # Check cache
        if use_case_id in self._cache and not force_reload:
            logger.debug(f"Cache HIT for config: {use_case_id}")
            return self._cache[use_case_id]

        logger.debug(f"Cache MISS for config: {use_case_id}")

        # Parse use case ID to get module and file name
        # UC-2.1 -> module2, uc_2_1_config.yaml
        # UC-3.2 -> module3, uc_3_2_config.yaml

        # Remove 'UC-' prefix and split by '.'
        if not use_case_id.startswith("UC-"):
            raise ValueError(
                f"Invalid use case ID format: {use_case_id}. "
                f"Expected format: UC-X.Y"
            )

        # Extract module and subcase numbers
        # "UC-2.1" -> "2.1" -> ["2", "1"]
        id_part = use_case_id.replace("UC-", "")
        parts = id_part.split(".")

        if len(parts) != 2:
            raise ValueError(
                f"Invalid use case ID format: {use_case_id}. "
                f"Expected format: UC-X.Y"
            )

        module_num = parts[0]  # "2"
        sub_case = parts[1]  # "1"

        # Build file path
        # module2/uc_2_1_config.yaml
        module_dir = f"module{module_num}"
        filename = f"uc_{module_num}_{sub_case}_config.yaml"
        config_path = self.config_dir / module_dir / filename

        logger.debug(f"Looking for config: {use_case_id} -> {config_path}")

        # Load YAML
        if not config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")

        try:
            with open(config_path, "r", encoding="utf-8") as f:
                config = yaml.safe_load(f)

            # Cache and return
            self._cache[use_case_id] = config
            logger.info(f"Loaded configuration for {use_case_id}")

            return config

        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML in {config_path}: {e}")

    def clear_cache(self) -> None:
        """Clear configuration cache."""
        self._cache.clear()
        logger.info("Configuration cache cleared")

    def get_cached_keys(self) -> list:
        """
        Get list of cached use case IDs.

        Returns
        -------
        list
            List of cached use case IDs.
        """
        return list(self._cache.keys())
