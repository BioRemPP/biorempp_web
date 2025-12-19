"""
Pytest configuration and shared fixtures for BioRemPP test suite.

This conftest.py provides comprehensive fixtures for all test modules,
using realistic data patterns extracted from actual databases.

Fixtures are organized by:
- Domain entities (Sample, Dataset, KO, etc.)
- Infrastructure components (Databases, Cache, Config)
- Test data (CSV files, DataFrames, etc.)
"""

import sys
from pathlib import Path

# Add parent directory to path to allow imports from biorempp_web
sys.path.insert(0, str(Path(__file__).parent.parent))

import json
import pytest
import pandas as pd
import tempfile
import shutil
from datetime import datetime
from typing import List, Dict, Any

# Domain imports
from src.domain.entities.sample import Sample
from src.domain.entities.dataset import Dataset
from src.domain.value_objects.kegg_orthology import KO
from src.domain.value_objects.sample_id import SampleId

# Infrastructure imports
from src.infrastructure.cache.memory_cache import MemoryCache
from src.infrastructure.cache.dataframe_cache import DataFrameCache
from src.infrastructure.cache.graph_cache import GraphCache
from src.infrastructure.config.dependency_injection import DIContainer


# ============================================================================
# DATA LOADING - Load extracted analysis data
# ============================================================================

@pytest.fixture(scope="session")
def analysis_data():
    """
    Load database analysis data.
    
    Returns
    -------
    dict
        Complete analysis from explore_databases.py
    """
    analysis_file = Path(__file__).parent / "analysis" / "database_analysis.json"
    
    if not analysis_file.exists():
        pytest.skip("Database analysis not available. Run: python -m tests.analysis.explore_databases")
    
    with open(analysis_file, 'r', encoding='utf-8') as f:
        return json.load(f)


@pytest.fixture(scope="session")
def representative_data():
    """
    Load representative data samples.
    
    Returns
    -------
    dict
        Representative data from extract_representative_data.py
    """
    rep_file = Path(__file__).parent / "analysis" / "representative_data.json"
    
    if not rep_file.exists():
        pytest.skip("Representative data not available. Run: python -m tests.analysis.extract_representative_data")
    
    with open(rep_file, 'r', encoding='utf-8') as f:
        return json.load(f)


# ============================================================================
# DOMAIN FIXTURES - Value Objects and Entities
# ============================================================================

@pytest.fixture
def valid_ko_ids(representative_data):
    """
    Valid KO IDs from real data.
    
    Returns
    -------
    list
        List of valid KO strings
    """
    biorempp_data = representative_data["representative_data"]["biorempp"]
    sample_kos = biorempp_data["column_representatives"]["ko"]["examples"]["typical_values"]
    
    # Return real KOs from database
    return sample_kos[:10]


@pytest.fixture
def invalid_ko_ids():
    """
    Invalid KO IDs for testing validation.
    
    Returns
    -------
    list
        List of invalid KO strings
    """
    return [
        "",           # Empty
        "K0001",      # Too short
        "K000001",    # Too long
        "00001",      # Missing K prefix
        "KXXXXX",     # Non-numeric
        "k00001",     # Lowercase
        None,         # Null
        "  ",         # Whitespace
    ]


@pytest.fixture
def sample_ko(valid_ko_ids):
    """
    Single valid KO instance.
    
    Returns
    -------
    KO
        KO value object
    """
    return KO(valid_ko_ids[0])


@pytest.fixture
def sample_ko_list(valid_ko_ids):
    """
    List of KO instances.
    
    Returns
    -------
    list[KO]
        List of KO value objects
    """
    return [KO(ko_id) for ko_id in valid_ko_ids[:5]]


@pytest.fixture
def valid_sample_id():
    """
    Valid Sample ID string.
    
    Returns
    -------
    str
        Sample ID string
    """
    return "TestSample1"


@pytest.fixture
def sample_id_instance(valid_sample_id):
    """
    Sample ID value object instance.
    
    Returns
    -------
    SampleId
        Sample ID value object
    """
    return SampleId(valid_sample_id)


@pytest.fixture
def edge_case_sample_ids():
    """
    Edge case sample IDs for testing.
    
    Returns
    -------
    list
        List of edge case sample ID strings
    """
    return [
        "Sample_with_underscore",
        "Sample-with-dash",
        "Sample.with.dots",
        "Sample#1",
        "Sample 123",
        "A",  # Single character
        "Very_Long_Sample_Name_With_Many_Characters_123456789",
    ]


@pytest.fixture
def sample_with_kos(valid_sample_id, sample_ko_list):
    """
    Sample entity with KOs.
    
    Returns
    -------
    Sample
        Sample with multiple KOs
    """
    sample = Sample(id=SampleId(valid_sample_id))
    for ko in sample_ko_list:
        sample.add_ko(ko)
    return sample


@pytest.fixture
def empty_sample(valid_sample_id):
    """
    Empty sample (no KOs).
    
    Returns
    -------
    Sample
        Sample without KOs
    """
    return Sample(id=SampleId(valid_sample_id))


@pytest.fixture
def sample_with_single_ko(valid_sample_id, sample_ko):
    """
    Sample with only one KO.
    
    Returns
    -------
    Sample
        Sample with single KO
    """
    sample = Sample(id=SampleId(valid_sample_id))
    sample.add_ko(sample_ko)
    return sample


@pytest.fixture
def sample_with_many_kos(representative_data):
    """
    Sample with many KOs (realistic count from analysis).
    
    Returns
    -------
    Sample
        Sample with typical number of KOs
    """
    sample_data = representative_data["representative_data"]["sample_data"]
    median_ko_count = int(sample_data["representative_samples"][1]["ko_count"])
    
    # Use real KO IDs from common KOs
    common_kos = [item["ko"] for item in sample_data["common_kos"]]
    
    sample = Sample(id=SampleId("LargeSample"))
    
    # Add KOs up to median count
    for ko_id in common_kos[:min(median_ko_count, len(common_kos))]:
        try:
            sample.add_ko(KO(ko_id))
        except ValueError:
            # Skip invalid KOs
            continue
    
    return sample


@pytest.fixture
def empty_dataset():
    """
    Empty dataset.
    
    Returns
    -------
    Dataset
        Dataset with no samples
    """
    return Dataset()


@pytest.fixture
def dataset_with_samples(sample_with_kos):
    """
    Dataset with multiple samples.
    
    Returns
    -------
    Dataset
        Dataset containing samples
    """
    dataset = Dataset()
    
    # Add 5 samples with different IDs
    for i in range(5):
        sample = Sample(id=SampleId(f"Sample{i+1}"))
        # Add 3 KOs to each
        for j in range(3):
            ko_num = str(i * 3 + j + 1).zfill(5)
            sample.add_ko(KO(f"K{ko_num}"))
        dataset.add_sample(sample)
    
    return dataset


# ============================================================================
# INFRASTRUCTURE FIXTURES - Temporary Files and Directories
# ============================================================================

@pytest.fixture
def temp_dir():
    """
    Temporary directory for test files.
    
    Yields
    ------
    Path
        Temporary directory path (auto-cleaned)
    """
    temp_path = Path(tempfile.mkdtemp())
    yield temp_path
    shutil.rmtree(temp_path, ignore_errors=True)


@pytest.fixture
def temp_csv_file(temp_dir, representative_data):
    """
    Temporary CSV file with realistic data.
    
    Parameters
    ----------
    temp_dir : Path
        Temporary directory
    representative_data : dict
        Representative data samples
    
    Yields
    ------
    Path
        Path to temporary CSV file
    """
    csv_path = temp_dir / "test_database.csv"
    
    # Get sample data from biorempp
    biorempp_samples = representative_data["representative_data"]["biorempp"]["complete_row_samples"]
    
    # Create DataFrame from samples
    rows = [sample["data"] for sample in biorempp_samples[:5]]
    df = pd.DataFrame(rows)
    
    # Save to CSV
    df.to_csv(csv_path, sep=';', index=False, encoding='utf-8')
    
    yield csv_path


@pytest.fixture
def minimal_csv_file(temp_dir):
    """
    Minimal CSV for testing basic functionality.
    
    Parameters
    ----------
    temp_dir : Path
        Temporary directory
    
    Yields
    ------
    Path
        Path to minimal CSV file
    """
    csv_path = temp_dir / "minimal.csv"
    
    data = pd.DataFrame({
        'ko': ['K00001', 'K00002', 'K00003'],
        'gene': ['geneA', 'geneB', 'geneC'],
        'pathway': ['path1', 'path1', 'path2']
    })
    
    data.to_csv(csv_path, sep=';', index=False, encoding='utf-8')
    
    yield csv_path


@pytest.fixture
def csv_with_nulls(temp_dir):
    """
    CSV file with NULL values for testing.
    
    Parameters
    ----------
    temp_dir : Path
        Temporary directory
    
    Yields
    ------
    Path
        Path to CSV with NULLs
    """
    csv_path = temp_dir / "with_nulls.csv"
    
    data = pd.DataFrame({
        'ko': ['K00001', 'K00002', None, 'K00004'],
        'gene': ['geneA', None, 'geneC', 'geneD'],
        'description': [None, 'desc2', 'desc3', None]
    })
    
    data.to_csv(csv_path, sep=';', index=False, encoding='utf-8')
    
    yield csv_path


@pytest.fixture
def large_csv_file(temp_dir):
    """
    Large CSV file for performance testing.
    
    Parameters
    ----------
    temp_dir : Path
        Temporary directory
    
    Yields
    ------
    Path
        Path to large CSV file
    """
    csv_path = temp_dir / "large_database.csv"
    
    # Create 1000 rows
    n_rows = 1000
    data = pd.DataFrame({
        'ko': [f'K{str(i).zfill(5)}' for i in range(n_rows)],
        'gene': [f'gene{i}' for i in range(n_rows)],
        'pathway': [f'pathway{i % 10}' for i in range(n_rows)],
        'count': range(n_rows)
    })
    
    data.to_csv(csv_path, sep=';', index=False, encoding='utf-8')
    
    yield csv_path


# ============================================================================
# DATAFRAME FIXTURES
# ============================================================================

@pytest.fixture
def small_dataframe():
    """
    Small DataFrame (10 rows).
    
    Returns
    -------
    pd.DataFrame
        Small test DataFrame
    """
    return pd.DataFrame({
        'A': range(10),
        'B': range(10, 20),
        'C': [f'value{i}' for i in range(10)]
    })


@pytest.fixture
def medium_dataframe():
    """
    Medium DataFrame (100 rows).
    
    Returns
    -------
    pd.DataFrame
        Medium test DataFrame
    """
    return pd.DataFrame({
        'A': range(100),
        'B': range(100, 200),
        'C': [f'value{i}' for i in range(100)]
    })


@pytest.fixture
def large_dataframe():
    """
    Large DataFrame (10,000 rows) for compression testing.
    
    Returns
    -------
    pd.DataFrame
        Large test DataFrame
    """
    return pd.DataFrame({
        'A': range(10000),
        'B': range(10000, 20000),
        'C': [f'value{i % 100}' for i in range(10000)]
    })


@pytest.fixture
def dataframe_with_nulls():
    """
    DataFrame with NULL values.
    
    Returns
    -------
    pd.DataFrame
        DataFrame containing NULLs
    """
    df = pd.DataFrame({
        'A': [1, 2, None, 4, 5],
        'B': [10, None, 30, None, 50],
        'C': ['a', 'b', None, 'd', 'e']
    })
    return df


@pytest.fixture
def realistic_biorempp_dataframe(representative_data):
    """
    Realistic BioRemPP DataFrame from actual data.
    
    Returns
    -------
    pd.DataFrame
        DataFrame with real BioRemPP structure
    """
    biorempp_samples = representative_data["representative_data"]["biorempp"]["complete_row_samples"]
    rows = [sample["data"] for sample in biorempp_samples]
    return pd.DataFrame(rows)


# ============================================================================
# CACHE FIXTURES
# ============================================================================

@pytest.fixture
def memory_cache():
    """
    Fresh MemoryCache instance.
    
    Returns
    -------
    MemoryCache
        Clean cache instance
    """
    return MemoryCache(max_size=100, default_ttl=3600)


@pytest.fixture
def dataframe_cache():
    """
    Fresh DataFrameCache instance.
    
    Returns
    -------
    DataFrameCache
        Clean DataFrame cache
    """
    return DataFrameCache(
        max_size=50,
        default_ttl=3600,
        compress_threshold=1024*1024  # 1MB
    )


@pytest.fixture
def graph_cache():
    """
    Fresh GraphCache instance.
    
    Returns
    -------
    GraphCache
        Clean graph cache
    """
    return GraphCache(max_size=50, default_ttl=3600)


# ============================================================================
# PLOTLY FIXTURES
# ============================================================================

@pytest.fixture
def sample_figure():
    """
    Sample Plotly figure for testing.
    
    Returns
    -------
    go.Figure
        Plotly figure object
    """
    import plotly.graph_objects as go
    
    fig = go.Figure(
        data=[go.Bar(x=['A', 'B', 'C'], y=[10, 20, 15])],
        layout=go.Layout(title='Test Chart')
    )
    return fig


@pytest.fixture
def sample_plot_data():
    """
    Sample data for plotting.
    
    Returns
    -------
    pd.DataFrame
        Data for plot testing
    """
    return pd.DataFrame({
        'category': ['A', 'B', 'C', 'D'],
        'value': [10, 25, 15, 30],
        'group': ['G1', 'G1', 'G2', 'G2']
    })


# ============================================================================
# CONFIGURATION FIXTURES
# ============================================================================

@pytest.fixture
def temp_yaml_config(temp_dir):
    """
    Temporary YAML configuration file.
    
    Parameters
    ----------
    temp_dir : Path
        Temporary directory
    
    Yields
    ------
    Path
        Path to YAML config file
    """
    import yaml
    
    config_path = temp_dir / "test_config.yaml"
    
    config = {
        'cache': {
            'memory': {
                'max_size': 100,
                'default_ttl': 1800
            }
        },
        'plotting': {
            'default_height': 600,
            'default_width': 800
        },
        'database': {
            'encoding': 'utf-8',
            'separator': ';'
        }
    }
    
    with open(config_path, 'w', encoding='utf-8') as f:
        yaml.dump(config, f)
    
    yield config_path


@pytest.fixture
def di_container():
    """
    Fresh DIContainer instance.
    
    Returns
    -------
    DIContainer
        Clean dependency injection container
    """
    return DIContainer()


# ============================================================================
# SAMPLE DATA FIXTURES (from sample_data.txt)
# ============================================================================

@pytest.fixture
def sample_data_species(representative_data):
    """
    Real species names from sample_data.txt.
    
    Returns
    -------
    list
        List of species names
    """
    samples = representative_data["representative_data"]["sample_data"]["representative_samples"]
    return [s["species"] for s in samples]


@pytest.fixture
def sample_data_codes(representative_data):
    """
    Real organism codes from sample_data.txt.
    
    Returns
    -------
    list
        List of organism codes
    """
    samples = representative_data["representative_data"]["sample_data"]["representative_samples"]
    return [s["code"] for s in samples]


@pytest.fixture
def common_kos(representative_data):
    """
    Most common KOs across all samples.
    
    Returns
    -------
    list
        List of common KO IDs
    """
    common = representative_data["representative_data"]["sample_data"]["common_kos"]
    return [item["ko"] for item in common]


# ============================================================================
# CROSS-DATABASE FIXTURES
# ============================================================================

@pytest.fixture
def linked_ko_data(representative_data):
    """
    KO data linked across multiple databases.
    
    Returns
    -------
    dict
        Linked data examples
    """
    return representative_data["cross_database_samples"]["linked_data_examples"][0]


@pytest.fixture
def common_kos_all_databases(representative_data):
    """
    KOs present in all three databases.
    
    Returns
    -------
    list
        KO IDs common to all databases
    """
    return representative_data["cross_database_samples"]["common_kos"]["all_three_databases"]


# ============================================================================
# EDGE CASE FIXTURES
# ============================================================================

@pytest.fixture
def edge_case_empty_string_ko():
    """
    Edge case: Empty string KO.
    
    Returns
    -------
    str
        Empty string
    """
    return ""


@pytest.fixture
def edge_case_empty_string():
    """
    Edge case: Generic empty string.
    
    Returns
    -------
    str
        Empty string
    """
    return ""


@pytest.fixture
def edge_case_whitespace_string():
    """
    Edge case: Whitespace-only string.
    
    Returns
    -------
    str
        Whitespace string
    """
    return "   "


@pytest.fixture
def edge_case_whitespace_sample_id():
    """
    Edge case: Whitespace-only sample ID.
    
    Returns
    -------
    str
        Whitespace string
    """
    return "   "


@pytest.fixture
def edge_case_duplicate_samples():
    """
    Edge case: Dataset with duplicate sample IDs.
    
    Returns
    -------
    list[Sample]
        Samples with duplicate IDs
    """
    sample_id = SampleId("DuplicateID")
    
    sample1 = Sample(id=sample_id)
    sample1.add_ko(KO("K00001"))
    
    sample2 = Sample(id=sample_id)
    sample2.add_ko(KO("K00002"))
    
    return [sample1, sample2]


# ============================================================================
# APPLICATION FIXTURES - Plot Services
# ============================================================================

@pytest.fixture
def plot_config_loader():
    """
    Fresh PlotConfigLoader instance.

    Returns
    -------
    PlotConfigLoader
        Clean config loader instance
    """
    from src.application.plot_services.plot_config_loader import PlotConfigLoader
    return PlotConfigLoader()


@pytest.fixture
def plot_factory():
    """
    Fresh PlotFactory instance.

    Returns
    -------
    PlotFactory
        Clean plot factory instance
    """
    from src.application.plot_services.plot_factory import PlotFactory
    return PlotFactory()


@pytest.fixture
def graph_cache_manager():
    """
    Fresh GraphCacheManager instance.

    Returns
    -------
    GraphCacheManager
        Clean cache manager instance
    """
    from src.infrastructure.cache import GraphCacheManager
    return GraphCacheManager()


@pytest.fixture
def plot_service():
    """
    Fresh PlotService instance.

    Returns
    -------
    PlotService
        Clean plot service instance
    """
    from src.application.plot_services.plot_service import PlotService
    return PlotService()


@pytest.fixture
def sample_plot_config():
    """
    Sample plot configuration dictionary.

    Returns
    -------
    dict
        Valid plot configuration
    """
    return {
        'metadata': {
            'use_case_id': 'UC-2.1',
            'module': 'module2',
            'title': 'Test Plot',
            'description': 'Test plot description'
        },
        'visualization': {
            'strategy': 'BarChartStrategy'
        },
        'data': {
            'required_columns': ['Sample', 'KO']
        },
        'validation': {},
        'performance': {
            'cache': {
                'enabled': True,
                'layers': [
                    {
                        'layer': 'graph',
                        'key_template': 'graph_{data_hash}_{filters_hash}',
                        'ttl': 3600
                    },
                    {
                        'layer': 'dataframe',
                        'key_template': 'df_{data_hash}_{filters_hash}',
                        'ttl': 7200
                    }
                ]
            }
        }
    }


@pytest.fixture
def sample_plot_dataframe():
    """
    Sample DataFrame for plot generation.

    Returns
    -------
    pd.DataFrame
        DataFrame suitable for plotting
    """
    return pd.DataFrame({
        'Sample': ['S1', 'S1', 'S2', 'S2', 'S3', 'S3'],
        'KO': ['K00001', 'K00002', 'K00001', 'K00003', 'K00002', 'K00004'],
        'Gene': ['geneA', 'geneB', 'geneA', 'geneC', 'geneB', 'geneD']
    })


@pytest.fixture
def temp_plot_config_dir(temp_dir):
    """
    Temporary plot config directory with sample configs.

    Parameters
    ----------
    temp_dir : Path
        Temporary directory

    Yields
    ------
    Path
        Path to plot configs directory
    """
    import yaml

    config_dir = temp_dir / "plot_configs"
    module_dir = config_dir / "module2"
    module_dir.mkdir(parents=True)

    # Create UC-2.1 config
    config_path = module_dir / "uc_2_1_config.yaml"
    config = {
        'metadata': {
            'use_case_id': 'UC-2.1',
            'module': 'module2',
            'title': 'Test Plot'
        },
        'visualization': {
            'strategy': 'BarChartStrategy'
        },
        'data': {
            'required_columns': ['Sample', 'KO']
        },
        'validation': {},
        'performance': {
            'cache': {
                'enabled': True,
                'layers': [
                    {
                        'layer': 'graph',
                        'key_template': 'graph_{data_hash}_{filters_hash}',
                        'ttl': 3600
                    }
                ]
            }
        }
    }

    with open(config_path, 'w', encoding='utf-8') as f:
        yaml.dump(config, f)

    yield config_dir


# ============================================================================
# HELPER FIXTURES
# ============================================================================

@pytest.fixture
def project_root():
    """
    Project root directory.

    Returns
    -------
    Path
        Path to biorempp_web directory
    """
    return Path(__file__).parent.parent


@pytest.fixture
def data_directory(project_root):
    """
    Data directory path.
    
    Returns
    -------
    Path
        Path to data directory
    """
    return project_root / "data"


@pytest.fixture
def databases_directory(data_directory):
    """
    Databases directory path.
    
    Returns
    -------
    Path
        Path to databases directory
    """
    return data_directory / "databases"


# ============================================================================
# PYTEST CONFIGURATION
# ============================================================================

def pytest_configure(config):
    """
    Pytest configuration hook.
    
    Registers custom markers.
    """
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "unit: marks tests as unit tests"
    )
    config.addinivalue_line(
        "markers", "requires_database: marks tests that require real database files"
    )


def pytest_collection_modifyitems(config, items):
    """
    Modify test items during collection.
    
    Adds markers automatically based on test location.
    """
    for item in items:
        # Add unit marker to tests in unit/ directory
        if "unit" in str(item.fspath):
            item.add_marker(pytest.mark.unit)
        
        # Add integration marker to tests in integration/ directory
        if "integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)
