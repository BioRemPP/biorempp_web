"""
Configuration Module - Application Settings Management.

Provides configuration management for the BioRemPP application including
application settings, database paths, dependency injection, and analysis
registry.

Classes
-------
Settings
    Application settings manager with singleton pattern
DatabaseConfig
    Database configuration manager for file paths and settings
AnalysisRegistry
    Registry for loading and managing analysis configurations
"""

from src.infrastructure.config.analysis_registry import AnalysisRegistry
from src.infrastructure.config.database_config import DatabaseConfig
from src.infrastructure.config.settings import Settings

__all__ = ["Settings", "DatabaseConfig", "AnalysisRegistry"]
