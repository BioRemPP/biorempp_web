"""
Application Settings - Configuration Management.

Provides centralized configuration management using singleton pattern to
ensure consistent settings across the application.

Classes
-------
Settings
    Application settings manager with YAML configuration support
"""

from pathlib import Path
from typing import Any, Dict, Optional

import yaml

from src.shared.logging import get_logger

logger = get_logger(__name__)


class Settings:
    """
    Application settings manager with singleton pattern.

    Loads configuration from YAML file and provides access to settings
    throughout the application. Only one instance exists per application.

    Attributes
    ----------
    config_file : Path
        Path to configuration YAML file
    _settings : Dict[str, Any]
        Loaded settings dictionary

    Methods
    -------
    get(key, default)
        Get setting value by dot-notation key
    set(key, value)
        Set setting value by dot-notation key
    get_section(section)
        Get entire settings section
    reload()
        Reload settings from file
    save(output_file)
        Save current settings to YAML file
    get_all()
        Get all settings
    """

    _instance: Optional["Settings"] = None

    def __new__(cls, config_file: Optional[Path] = None):
        """
        Singleton implementation.

        Parameters
        ----------
        config_file : Optional[Path], default=None
            Path to config file. Only used on first instantiation.
        """
        if cls._instance is None:
            cls._instance = super(Settings, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, config_file: Optional[Path] = None):
        """
        Initialize settings.

        Parameters
        ----------
        config_file : Optional[Path], default=None
            Path to YAML configuration file.
            Defaults to 'config/settings.yaml'.
        """
        if self._initialized:
            return

        if config_file is None:
            config_file = Path("config/settings.yaml")

        self.config_file = config_file
        self._settings: Dict[str, Any] = {}
        self._load_settings()
        self._initialized = True

    def _load_settings(self) -> None:
        """
        Load settings from YAML file.

        Creates default settings if file doesn't exist.
        """
        if not self.config_file.exists():
            logger.warning(
                f"Config file not found: {self.config_file}. " "Using default settings."
            )
            self._settings = self._get_default_settings()
            return

        try:
            with open(self.config_file, "r", encoding="utf-8") as f:
                self._settings = yaml.safe_load(f) or {}

            logger.info(
                f"Loaded settings from {self.config_file}",
                extra={"settings_count": len(self._settings)},
            )

        except Exception as e:
            logger.error(f"Failed to load settings: {e}")
            self._settings = self._get_default_settings()

    def _get_default_settings(self) -> Dict[str, Any]:
        """
        Get default settings.

        Returns
        -------
        Dict[str, Any]
            Default configuration dictionary.
        """
        return {
            "cache": {
                "memory": {"max_size": 1000, "default_ttl": 0},
                "dataframe": {
                    "max_size": 50,
                    "default_ttl": 3600,
                    "compress_threshold": 1048576,
                    "compression_level": 6,
                },
                "graph": {"max_size": 100, "default_ttl": 1800},
            },
            "plotting": {
                "default_template": "simple_white",
                "default_height": 600,
                "default_width": None,
                "show_values": False,
            },
            "performance": {
                "enable_caching": True,
                "lazy_loading": True,
                "optimize_dtypes": True,
            },
        }

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get setting value by dot-notation key.

        Parameters
        ----------
        key : str
            Setting key in dot notation (e.g., 'cache.max_size')
        default : Any, default=None
            Default value if key not found

        Returns
        -------
        Any
            Setting value or default
        """
        keys = key.split(".")
        value = self._settings

        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default

        return value

    def set(self, key: str, value: Any) -> None:
        """
        Set setting value by dot-notation key.

        Parameters
        ----------
        key : str
            Setting key in dot notation
        value : Any
            Value to set
        """
        keys = key.split(".")
        settings = self._settings

        # Navigate to nested dict
        for k in keys[:-1]:
            if k not in settings:
                settings[k] = {}
            settings = settings[k]

        # Set value
        settings[keys[-1]] = value

        logger.debug(f"Setting updated: {key} = {value}")

    def get_section(self, section: str) -> Dict[str, Any]:
        """
        Get entire settings section.

        Parameters
        ----------
        section : str
            Section name (e.g., 'cache')

        Returns
        -------
        Dict[str, Any]
            Section dictionary or empty dict if not found
        """
        return self._settings.get(section, {})

    def reload(self) -> None:
        """Reload settings from file."""
        logger.info("Reloading settings")
        self._load_settings()

    def save(self, output_file: Optional[Path] = None) -> None:
        """
        Save current settings to YAML file.

        Parameters
        ----------
        output_file : Optional[Path], default=None
            Output file path. If None, uses original config_file.
        """
        output_file = output_file or self.config_file

        try:
            output_file.parent.mkdir(parents=True, exist_ok=True)

            with open(output_file, "w", encoding="utf-8") as f:
                yaml.dump(
                    self._settings, f, default_flow_style=False, allow_unicode=True
                )

            logger.info(f"Settings saved to {output_file}")

        except Exception as e:
            logger.error(f"Failed to save settings: {e}")
            raise

    def get_all(self) -> Dict[str, Any]:
        """
        Get all settings.

        Returns
        -------
        Dict[str, Any]
            Complete settings dictionary.
        """
        return self._settings.copy()
