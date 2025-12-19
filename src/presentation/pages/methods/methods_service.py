"""
Methods Service - YAML Workflow Data Loader and Query Interface

This service provides methods to load and query analytical workflow data
from the workflow_methods.yaml configuration file.
"""

from functools import lru_cache
from pathlib import Path
from typing import Dict, List, Optional

import yaml


class MethodsService:
    """Service for loading and querying workflow methods from YAML configuration."""

    def __init__(self, yaml_path: Optional[Path] = None):
        """
        Initialize the MethodsService.

        Args:
            yaml_path: Path to workflow_methods.yaml. If None, uses default location.
        """
        if yaml_path is None:
            # Default to workflow_methods.yaml in the same directory
            yaml_path = Path(__file__).parent / "workflow_methods.yaml"

        self.yaml_path = yaml_path
        self._workflows: Optional[Dict] = None

    @lru_cache(maxsize=1)
    def load_workflows(self) -> Dict:
        """
        Load all workflows from YAML file.

        Returns:
            Dictionary containing all workflow data.

        Raises:
            FileNotFoundError: If YAML file doesn't exist.
            yaml.YAMLError: If YAML parsing fails.
        """
        if not self.yaml_path.exists():
            raise FileNotFoundError(f"Workflow YAML not found: {self.yaml_path}")

        try:
            with open(self.yaml_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)

            self._workflows = data.get("workflows", {})
            return self._workflows

        except yaml.YAMLError as e:
            raise yaml.YAMLError(f"Error parsing workflow YAML: {e}")

    def get_workflow(self, use_case_id: str) -> Optional[Dict]:
        """
        Get workflow data for a specific use case.

        Args:
            use_case_id: Use case ID (e.g., "UC-1.1" or "uc-1-1")

        Returns:
            Workflow dictionary or None if not found.
        """
        workflows = self.load_workflows()

        # Normalize UC ID to lowercase with hyphens
        uc_key = use_case_id.lower().replace(".", "-")

        return workflows.get(uc_key)

    def get_workflows_by_module(self, module: int) -> List[Dict]:
        """
        Get all workflows for a specific module.

        Args:
            module: Module number (1-8)

        Returns:
            List of workflow dictionaries for the module, sorted by UC ID.
        """
        workflows = self.load_workflows()

        module_workflows = [
            wf for wf in workflows.values() if wf.get("module") == module
        ]

        # Sort by use_case_id
        module_workflows.sort(key=lambda x: x.get("use_case_id", ""))

        return module_workflows

    def get_all_modules(self) -> List[int]:
        """
        Get list of all available module numbers.

        Returns:
            Sorted list of module numbers.
        """
        workflows = self.load_workflows()

        modules = set(wf.get("module") for wf in workflows.values())
        return sorted(modules)

    def get_module_info(self, module: int) -> Dict:
        """
        Get summary information for a module.

        Args:
            module: Module number (1-8)

        Returns:
            Dictionary with module statistics:
            - module: Module number
            - use_case_count: Number of use cases
            - use_case_ids: List of UC IDs
        """
        workflows = self.get_workflows_by_module(module)

        return {
            "module": module,
            "use_case_count": len(workflows),
            "use_case_ids": [wf.get("use_case_id") for wf in workflows],
        }

    def get_total_use_cases(self) -> int:
        """
        Get total number of use cases across all modules.

        Returns:
            Total count of use cases.
        """
        workflows = self.load_workflows()
        return len(workflows)

    def search_workflows(self, query: str) -> List[Dict]:
        """
        Search workflows by title or description content.

        Args:
            query: Search query string

        Returns:
            List of matching workflows.
        """
        workflows = self.load_workflows()
        query_lower = query.lower()

        matches = []
        for wf in workflows.values():
            # Search in title
            if query_lower in wf.get("title", "").lower():
                matches.append(wf)
                continue

            # Search in step descriptions
            for step in wf.get("steps", []):
                if query_lower in step.get("description", "").lower():
                    matches.append(wf)
                    break

        return matches


# Singleton instance for application-wide use
_methods_service_instance = None


def get_methods_service() -> MethodsService:
    """
    Get singleton instance of MethodsService.

    Returns:
        MethodsService instance.
    """
    global _methods_service_instance

    if _methods_service_instance is None:
        _methods_service_instance = MethodsService()

    return _methods_service_instance
