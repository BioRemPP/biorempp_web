"""
Scientific Overview Service - BioRemPP v1.0.

Service layer for loading and processing scientific methods overview data
from YAML files.

Functions
---------
load_scientific_yaml
    Load scientific foundations YAML (KO richness, compound richness, functional guilds)
load_datascience_yaml
    Load data science methods YAML (feature engineering, visualization, bioremediation DS)
load_bioremediation_yaml
    Load FAIR principles and genomics resources YAML
load_multiomics_yaml
    Load multi-omics integration YAML
get_all_overview_data
    Load all overview data from YAML files

Notes
-----
- Uses PyYAML for safe YAML loading
- Handles missing files gracefully with error messages
- Returns structured dictionaries for layout components
- Follows SOLID principles with single responsibility per function
"""

import logging
from pathlib import Path
from typing import Dict, Optional

import yaml

# Configure logging
logger = logging.getLogger(__name__)


def load_scientific_yaml(yaml_dir: Optional[Path] = None) -> Dict:
    """
    Load scientific foundations YAML file.

    Parameters
    ----------
    yaml_dir : Optional[Path], optional
        Directory containing YAML files. If None, uses default methods directory.

    Returns
    -------
    Dict
        Dictionary containing scientific terms (KO richness, compound richness,
        metabolic functional guilds) with definitions, applications, and references.

    Raises
    ------
    FileNotFoundError
        If scientific.yaml file is not found
    yaml.YAMLError
        If YAML file is malformed

    Examples
    --------
    >>> data = load_scientific_yaml()
    >>> ko_richness = data['terms']['ko_richness']
    >>> print(ko_richness['label'])
    'KO Richness'

    Notes
    -----
    Returns empty dict with error message if file cannot be loaded.
    """
    if yaml_dir is None:
        yaml_dir = Path(__file__).parent

    yaml_path = yaml_dir / "scientific.yaml"

    try:
        with open(yaml_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        logger.info(f"Successfully loaded scientific.yaml from {yaml_path}")
        return data
    except FileNotFoundError:
        logger.error(f"Scientific YAML file not found: {yaml_path}")
        return {"error": "Scientific foundations data not available"}
    except yaml.YAMLError as e:
        logger.error(f"Error parsing scientific.yaml: {e}")
        return {"error": f"Error loading scientific data: {str(e)}"}


def load_datascience_yaml(yaml_dir: Optional[Path] = None) -> Dict:
    """
    Load data science methods YAML file.

    Parameters
    ----------
    yaml_dir : Optional[Path], optional
        Directory containing YAML files. If None, uses default methods directory.

    Returns
    -------
    Dict
        Dictionary containing data science categories (feature engineering,
        visualization, bioremediation-specific data science) with methods,
        techniques, and references.

    Raises
    ------
    FileNotFoundError
        If datascience.yaml file is not found
    yaml.YAMLError
        If YAML file is malformed

    Examples
    --------
    >>> data = load_datascience_yaml()
    >>> fe_category = data['categories']['feature_engineering']
    >>> print(fe_category['title'])
    'Feature Engineering & Machine Learning'

    Notes
    -----
    Returns empty dict with error message if file cannot be loaded.
    """
    if yaml_dir is None:
        yaml_dir = Path(__file__).parent

    yaml_path = yaml_dir / "datascience.yaml"

    try:
        with open(yaml_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        logger.info(f"Successfully loaded datascience.yaml from {yaml_path}")
        return data
    except FileNotFoundError:
        logger.error(f"Data science YAML file not found: {yaml_path}")
        return {"error": "Data science methods data not available"}
    except yaml.YAMLError as e:
        logger.error(f"Error parsing datascience.yaml: {e}")
        return {"error": f"Error loading data science data: {str(e)}"}


def load_bioremediation_yaml(yaml_dir: Optional[Path] = None) -> Dict:
    """
    Load FAIR principles and bioremediation resources YAML file.

    Parameters
    ----------
    yaml_dir : Optional[Path], optional
        Directory containing YAML files. If None, uses default methods directory.

    Returns
    -------
    Dict
        Dictionary containing FAIR principles, integrated databases, and
        genomics resources for bioremediation research.

    Raises
    ------
    FileNotFoundError
        If bioremediation.yaml file is not found
    yaml.YAMLError
        If YAML file is malformed

    Examples
    --------
    >>> data = load_bioremediation_yaml()
    >>> fair = data['fair_principles']
    >>> print(fair['principles']['interoperable']['label'])
    'Interoperable'

    Notes
    -----
    Returns empty dict with error message if file cannot be loaded.
    """
    if yaml_dir is None:
        yaml_dir = Path(__file__).parent

    yaml_path = yaml_dir / "bioremediation.yaml"

    try:
        with open(yaml_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        logger.info(f"Successfully loaded bioremediation.yaml from {yaml_path}")
        return data
    except FileNotFoundError:
        logger.error(f"Bioremediation YAML file not found: {yaml_path}")
        return {"error": "Bioremediation resources data not available"}
    except yaml.YAMLError as e:
        logger.error(f"Error parsing bioremediation.yaml: {e}")
        return {"error": f"Error loading bioremediation data: {str(e)}"}


def load_multiomics_yaml(yaml_dir: Optional[Path] = None) -> Dict:
    """
    Load multi-omics integration YAML file.

    Parameters
    ----------
    yaml_dir : Optional[Path], optional
        Directory containing YAML files. If None, uses default methods directory.

    Returns
    -------
    Dict
        Dictionary containing multi-omics integration strategies, omics layers,
        case studies, and BioRemPP integration roadmap.

    Raises
    ------
    FileNotFoundError
        If multiomics.yaml file is not found
    yaml.YAMLError
        If YAML file is malformed

    Examples
    --------
    >>> data = load_multiomics_yaml()
    >>> layers = data['integration_overview']['omics_layers']
    >>> print(layers['genomics']['label'])
    'Genomics'

    Notes
    -----
    Returns empty dict with error message if file cannot be loaded.
    """
    if yaml_dir is None:
        yaml_dir = Path(__file__).parent

    yaml_path = yaml_dir / "multiomics.yaml"

    try:
        with open(yaml_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        logger.info(f"Successfully loaded multiomics.yaml from {yaml_path}")
        return data
    except FileNotFoundError:
        logger.error(f"Multi-omics YAML file not found: {yaml_path}")
        return {"error": "Multi-omics integration data not available"}
    except yaml.YAMLError as e:
        logger.error(f"Error parsing multiomics.yaml: {e}")
        return {"error": f"Error loading multi-omics data: {str(e)}"}


def get_all_overview_data(yaml_dir: Optional[Path] = None) -> Dict:
    """
    Load all scientific overview data from YAML files.

    Parameters
    ----------
    yaml_dir : Optional[Path], optional
        Directory containing YAML files. If None, uses default methods directory.

    Returns
    -------
    Dict
        Dictionary with keys: 'scientific', 'datascience', 'bioremediation', 'multiomics'
        Each containing the respective YAML data.

    Examples
    --------
    >>> all_data = get_all_overview_data()
    >>> scientific = all_data['scientific']
    >>> datascience = all_data['datascience']

    Notes
    -----
    - Loads all four YAML files in sequence
    - Each section can be accessed independently
    - Error handling is done at individual load level
    """
    return {
        "scientific": load_scientific_yaml(yaml_dir),
        "datascience": load_datascience_yaml(yaml_dir),
        "bioremediation": load_bioremediation_yaml(yaml_dir),
        "multiomics": load_multiomics_yaml(yaml_dir),
    }
