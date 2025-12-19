"""
Analysis Registry - Configuration Management.

Provides registry for loading and managing analysis configurations.
Each analysis (Use Case) has a JSON configuration defining its parameters,
filters, and visualization settings.

Classes
-------
AnalysisRegistry
    Registry for analysis configurations with JSON support
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from src.shared.logging import get_logger

logger = get_logger(__name__)


class AnalysisRegistry:
    """
    Registry for analysis configurations.

    Loads analysis definitions from JSON files and provides access to
    analysis metadata, parameters, and settings.

    Attributes
    ----------
    analyses_dir : Path
        Directory containing analysis JSON files
    _analyses : Dict[str, Dict[str, Any]]
        Loaded analysis configurations

    Methods
    -------
    get_analysis(analysis_id)
        Get analysis configuration by ID
    get_all_analyses()
        Get all registered analyses
    get_analyses_by_use_case(use_case)
        Get all analyses for a specific Use Case
    get_analysis_ids()
        Get list of all analysis IDs
    get_use_cases()
        Get list of unique Use Cases
    analysis_exists(analysis_id)
        Check if analysis exists
    get_analysis_plot_type(analysis_id)
        Get plot type for analysis
    reload()
        Reload all analysis configurations
    get_stats()
        Get registry statistics
    """

    def __init__(self, analyses_dir: Optional[Path] = None):
        """
        Initialize analysis registry.

        Parameters
        ----------
        analyses_dir : Optional[Path], default=None
            Directory containing analysis JSON files.
            Defaults to 'config/analyses/'.
        """
        if analyses_dir is None:
            analyses_dir = Path("config/analyses")

        self.analyses_dir = analyses_dir
        self._analyses: Dict[str, Dict[str, Any]] = {}
        self._load_analyses()

    def _load_analyses(self) -> None:
        """Load all analysis configurations from JSON files."""
        if not self.analyses_dir.exists():
            logger.warning(
                f"Analyses directory not found: {self.analyses_dir}. "
                "No analyses loaded."
            )
            return

        # Find all JSON files
        json_files = list(self.analyses_dir.glob("*.json"))

        if not json_files:
            logger.warning(f"No JSON files found in {self.analyses_dir}")
            return

        # Load each JSON file
        for json_file in json_files:
            try:
                with open(json_file, "r", encoding="utf-8") as f:
                    data = json.load(f)

                # Expect format: {"analyses": [...]}
                if "analyses" in data:
                    analyses = data["analyses"]

                    for analysis in analyses:
                        analysis_id = analysis.get("id")
                        if analysis_id:
                            self._analyses[analysis_id] = analysis
                        else:
                            logger.warning(f"Analysis without ID in {json_file}")

                logger.info(
                    f"Loaded analyses from {json_file.name}",
                    extra={"count": len(data.get("analyses", []))},
                )

            except Exception as e:
                logger.error(f"Failed to load {json_file}: {e}", exc_info=True)

        logger.info(
            "Analysis registry initialized",
            extra={"total_analyses": len(self._analyses)},
        )

    def get_analysis(self, analysis_id: str) -> Optional[Dict[str, Any]]:
        """
        Get analysis configuration by ID.

        Parameters
        ----------
        analysis_id : str
            Analysis identifier (e.g., 'UC1_1')

        Returns
        -------
        Optional[Dict[str, Any]]
            Analysis configuration or None if not found
        """
        analysis = self._analyses.get(analysis_id)

        if analysis is None:
            logger.warning(f"Analysis not found: {analysis_id}")

        return analysis

    def get_all_analyses(self) -> Dict[str, Dict[str, Any]]:
        """
        Get all registered analyses.

        Returns
        -------
        Dict[str, Dict[str, Any]]
            Dictionary mapping analysis IDs to configurations.
        """
        return self._analyses.copy()

    def get_analyses_by_use_case(self, use_case: str) -> List[Dict[str, Any]]:
        """
        Get all analyses for a specific Use Case.

        Parameters
        ----------
        use_case : str
            Use Case identifier (e.g., 'UC1')

        Returns
        -------
        List[Dict[str, Any]]
            List of analysis configurations
        """
        return [
            analysis
            for analysis_id, analysis in self._analyses.items()
            if analysis_id.startswith(use_case)
        ]

    def get_analysis_ids(self) -> List[str]:
        """
        Get list of all analysis IDs.

        Returns
        -------
        List[str]
            List of analysis identifiers.
        """
        return list(self._analyses.keys())

    def get_use_cases(self) -> List[str]:
        """
        Get list of unique Use Cases.

        Returns
        -------
        List[str]
            List of Use Case identifiers
        """
        use_cases = set()

        for analysis_id in self._analyses.keys():
            # Extract UC prefix (e.g., 'UC1' from 'UC1_1')
            if "_" in analysis_id:
                uc = analysis_id.split("_")[0]
                use_cases.add(uc)

        return sorted(list(use_cases))

    def analysis_exists(self, analysis_id: str) -> bool:
        """
        Check if analysis exists.

        Parameters
        ----------
        analysis_id : str
            Analysis identifier.

        Returns
        -------
        bool
            True if analysis is registered.
        """
        return analysis_id in self._analyses

    def get_analysis_plot_type(self, analysis_id: str) -> Optional[str]:
        """
        Get plot type for analysis.

        Parameters
        ----------
        analysis_id : str
            Analysis identifier

        Returns
        -------
        Optional[str]
            Plot type (e.g., 'heatmap', 'bar_chart') or None
        """
        analysis = self.get_analysis(analysis_id)

        if analysis is None:
            return None

        return analysis.get("plot_type")

    def reload(self) -> None:
        """Reload all analysis configurations from files."""
        logger.info("Reloading analysis configurations")
        self._analyses.clear()
        self._load_analyses()

    def get_stats(self) -> Dict[str, Any]:
        """
        Get registry statistics.

        Returns
        -------
        Dict[str, Any]
            Statistics including total analyses, use cases, etc.
        """
        use_cases = self.get_use_cases()
        use_case_counts = {
            uc: len(self.get_analyses_by_use_case(uc)) for uc in use_cases
        }

        return {
            "total_analyses": len(self._analyses),
            "total_use_cases": len(use_cases),
            "use_cases": use_cases,
            "analyses_per_use_case": use_case_counts,
        }
