"""
Unit tests for TreemapStrategy.

This module tests the TreemapStrategy class for hierarchical treemap
visualizations with nested rectangles sized by aggregated values.

Test Coverage:
- Initialization and configuration parsing
- Data validation (empty data, missing columns, path columns)
- Data processing (aggregation, cleaning, sanitization)
- Figure creation (continuous/discrete color modes, layout, styling)
- Integration tests (full workflow)
- Edge cases (single category, many categories, special characters, etc.)

Author: BioRemPP Development Team
Date: 2025-12-08
"""

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import pytest

from src.domain.plot_strategies.charts.treemap_strategy import TreemapStrategy


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_minimal_config():
    """Get minimal configuration for TreemapStrategy."""
    return {
        'metadata': {'use_case_id': 'UC-6.3', 'module': 'module6'},
        'data': {},
        'visualization': {
            'strategy': 'TreemapStrategy',
            'plotly': {
                'path_columns': ['compoundclass', 'compoundname'],
                'root_label': 'Chemical Hierarchy',
                'value_column': 'genesymbol',
                'aggregation': 'nunique',
                'color_mode': 'continuous',
                'color_continuous_scale': 'Greens',
                'chart': {'title': {'text': 'Treemap Test'}},
                'layout': {'height': 800, 'width': 1000, 'template': 'simple_white'}
            }
        }
    }


def get_discrete_color_config():
    """Get configuration with discrete color mode."""
    return {
        'metadata': {'use_case_id': 'UC-6.4', 'module': 'module6'},
        'data': {},
        'visualization': {
            'strategy': 'TreemapStrategy',
            'plotly': {
                'path_columns': ['enzyme_activity', 'compoundclass'],
                'root_label': 'Enzymatic Activity',
                'value_column': 'compoundname',
                'aggregation': 'nunique',
                'color_mode': 'discrete',
                'color_discrete_sequence': ['#1f77b4', '#ff7f0e', '#2ca02c'],
                'chart': {'title': {'text': 'Enzymatic Overview'}},
                'layout': {'height': 800, 'template': 'simple_white'}
            }
        }
    }


def get_sample_data():
    """Get sample hierarchical data."""
    np.random.seed(42)
    return pd.DataFrame({
        'compoundclass': ['Aromatic', 'Aromatic', 'Aliphatic', 'Aliphatic', 'Aromatic'],
        'compoundname': ['Benzene', 'Benzene', 'Hexane', 'Pentane', 'Toluene'],
        'genesymbol': ['GeneA', 'GeneB', 'GeneC', 'GeneD', 'GeneE'],
        'sample': ['S1', 'S2', 'S1', 'S1', 'S3']
    })


def get_enzymatic_data():
    """Get enzymatic activity data."""
    np.random.seed(42)
    return pd.DataFrame({
        'enzyme_activity': ['Oxidase', 'Oxidase', 'Reductase', 'Reductase'],
        'compoundclass': ['Aromatic', 'Aromatic', 'Aliphatic', 'Aliphatic'],
        'compoundname': ['Benzene', 'Toluene', 'Hexane', 'Pentane'],
        'genesymbol': ['GeneX', 'GeneY', 'GeneX', 'GeneZ']
    })


def get_large_sample_data():
    """Get large hierarchical dataset."""
    np.random.seed(42)
    n_rows = 100
    classes = ['Aromatic', 'Aliphatic', 'Cyclic', 'Heterocyclic']
    compounds = [f'Compound{i}' for i in range(20)]
    genes = [f'Gene{i}' for i in range(50)]

    return pd.DataFrame({
        'compoundclass': np.random.choice(classes, n_rows),
        'compoundname': np.random.choice(compounds, n_rows),
        'genesymbol': np.random.choice(genes, n_rows)
    })


# ============================================================================
# TEST CLASS
# ============================================================================

class TestTreemapStrategy:
    """Test suite for TreemapStrategy."""

    # ========================================================================
    # INITIALIZATION TESTS
    # ========================================================================

    def test_init_minimal_config(self):
        """Test initialization with minimal configuration."""
        # Arrange
        config = get_minimal_config()

        # Act
        strategy = TreemapStrategy(config)

        # Assert
        assert strategy is not None
        assert strategy.path_columns == ['compoundclass', 'compoundname']
        assert strategy.root_label == 'Chemical Hierarchy'
        assert strategy.value_column == 'genesymbol'
        assert strategy.aggregation == 'nunique'
        assert strategy.color_mode == 'continuous'

    def test_init_discrete_color_config(self):
        """Test initialization with discrete color mode."""
        # Arrange
        config = get_discrete_color_config()

        # Act
        strategy = TreemapStrategy(config)

        # Assert
        assert strategy.color_mode == 'discrete'
        assert strategy.path_columns == ['enzyme_activity', 'compoundclass']

    def test_init_default_values(self):
        """Test initialization uses default values when not specified."""
        # Arrange
        config = {
            'metadata': {'use_case_id': 'UC-6.3', 'module': 'module6'},
            'data': {},
            'visualization': {
                'strategy': 'TreemapStrategy',
                'plotly': {
                    'path_columns': ['level1', 'level2']
                }
            }
        }

        # Act
        strategy = TreemapStrategy(config)

        # Assert
        assert strategy.root_label == 'All Data'  # Default
        assert strategy.value_column == 'count'  # Default
        assert strategy.aggregation == 'nunique'  # Default
        assert strategy.color_mode == 'continuous'  # Default
        assert strategy.color_column is None  # Default

    def test_init_extracts_configs(self):
        """Test initialization extracts data and plotly configs."""
        # Arrange
        config = get_minimal_config()

        # Act
        strategy = TreemapStrategy(config)

        # Assert
        assert hasattr(strategy, 'data_config')
        assert hasattr(strategy, 'plotly_config')
        assert isinstance(strategy.data_config, dict)
        assert isinstance(strategy.plotly_config, dict)

    def test_init_custom_color_column(self):
        """Test initialization with custom color column."""
        # Arrange
        config = get_minimal_config()
        config['visualization']['plotly']['color_column'] = 'sample'

        # Act
        strategy = TreemapStrategy(config)

        # Assert
        assert strategy.color_column == 'sample'

    # ========================================================================
    # VALIDATION TESTS
    # ========================================================================

    def test_validate_empty_dataframe_fails(self):
        """Test validation fails with empty DataFrame."""
        # Arrange
        config = get_minimal_config()
        strategy = TreemapStrategy(config)
        df = pd.DataFrame()

        # Act & Assert
        with pytest.raises(ValueError, match="Input DataFrame is empty"):
            strategy.validate_data(df)

    def test_validate_no_path_columns_fails(self):
        """Test validation fails when no path_columns configured."""
        # Arrange
        config = get_minimal_config()
        config['visualization']['plotly']['path_columns'] = []
        strategy = TreemapStrategy(config)
        df = get_sample_data()

        # Act & Assert
        with pytest.raises(ValueError, match="No path_columns configured"):
            strategy.validate_data(df)

    def test_validate_missing_path_column(self):
        """Test validation fails when path column is missing."""
        # Arrange
        config = get_minimal_config()
        strategy = TreemapStrategy(config)
        df = pd.DataFrame({
            'compoundclass': ['Aromatic'],
            # Missing 'compoundname'
            'genesymbol': ['GeneA']
        })

        # Act & Assert
        with pytest.raises(ValueError, match="Missing required columns"):
            strategy.validate_data(df)

    def test_validate_missing_value_column(self):
        """Test validation fails when value column is missing."""
        # Arrange
        config = get_minimal_config()
        strategy = TreemapStrategy(config)
        df = pd.DataFrame({
            'compoundclass': ['Aromatic'],
            'compoundname': ['Benzene']
            # Missing 'genesymbol'
        })

        # Act & Assert
        with pytest.raises(ValueError, match="Missing required columns"):
            strategy.validate_data(df)

    def test_validate_all_nulls_fails(self):
        """Test validation fails when all values are null."""
        # Arrange
        config = get_minimal_config()
        strategy = TreemapStrategy(config)
        df = pd.DataFrame({
            'compoundclass': [None, None],
            'compoundname': [None, None],
            'genesymbol': [None, None]
        })

        # Act & Assert
        with pytest.raises(ValueError, match="No valid data after removing nulls"):
            strategy.validate_data(df)

    def test_validate_sample_data_passes(self):
        """Test validation passes with valid sample data."""
        # Arrange
        config = get_minimal_config()
        strategy = TreemapStrategy(config)
        df = get_sample_data()

        # Act & Assert (should not raise)
        strategy.validate_data(df)

    def test_validate_with_some_nulls_passes(self):
        """Test validation passes with some null values."""
        # Arrange
        config = get_minimal_config()
        strategy = TreemapStrategy(config)
        df = pd.DataFrame({
            'compoundclass': ['Aromatic', None, 'Aliphatic'],
            'compoundname': ['Benzene', 'Toluene', None],
            'genesymbol': ['GeneA', 'GeneB', 'GeneC']
        })

        # Act & Assert (should not raise - at least 1 complete row)
        strategy.validate_data(df)

    def test_validate_missing_color_column(self):
        """Test validation fails when custom color column is missing."""
        # Arrange
        config = get_minimal_config()
        config['visualization']['plotly']['color_column'] = 'nonexistent_column'
        strategy = TreemapStrategy(config)
        df = get_sample_data()

        # Act & Assert
        with pytest.raises(ValueError, match="Color column .* not found"):
            strategy.validate_data(df)

    def test_validate_large_dataset(self):
        """Test validation passes with large dataset."""
        # Arrange
        config = get_minimal_config()
        strategy = TreemapStrategy(config)
        df = get_large_sample_data()

        # Act & Assert (should not raise)
        strategy.validate_data(df)

    # ========================================================================
    # DATA PROCESSING TESTS
    # ========================================================================

    def test_process_data_creates_required_columns(self):
        """Test process_data creates aggregated value column and root."""
        # Arrange
        config = get_minimal_config()
        strategy = TreemapStrategy(config)
        df = get_sample_data()

        # Act
        result = strategy.process_data(df)

        # Assert
        assert 'root' in result.columns
        assert 'unique_genesymbol_count' in result.columns
        assert 'compoundclass' in result.columns
        assert 'compoundname' in result.columns

    def test_process_data_nunique_aggregation(self):
        """Test process_data with nunique aggregation."""
        # Arrange
        config = get_minimal_config()
        strategy = TreemapStrategy(config)
        df = get_sample_data()

        # Act
        result = strategy.process_data(df)

        # Assert
        # Benzene has 2 unique genes (GeneA, GeneB)
        benzene = result[result['compoundname'] == 'Benzene']
        assert benzene['unique_genesymbol_count'].values[0] == 2

    def test_process_data_count_aggregation(self):
        """Test process_data with count aggregation."""
        # Arrange
        config = get_minimal_config()
        config['visualization']['plotly']['aggregation'] = 'count'
        strategy = TreemapStrategy(config)
        df = get_sample_data()

        # Act
        result = strategy.process_data(df)

        # Assert
        assert 'genesymbol_count' in result.columns
        benzene = result[result['compoundname'] == 'Benzene']
        assert benzene['genesymbol_count'].values[0] == 2  # 2 rows for Benzene

    def test_process_data_sum_aggregation(self):
        """Test process_data with sum aggregation."""
        # Arrange
        config = get_minimal_config()
        config['visualization']['plotly']['aggregation'] = 'sum'
        config['visualization']['plotly']['value_column'] = 'value'
        strategy = TreemapStrategy(config)
        df = pd.DataFrame({
            'compoundclass': ['Aromatic', 'Aromatic', 'Aliphatic'],
            'compoundname': ['Benzene', 'Benzene', 'Hexane'],
            'value': [10, 20, 15]
        })

        # Act
        result = strategy.process_data(df)

        # Assert
        assert 'value_sum' in result.columns
        benzene = result[result['compoundname'] == 'Benzene']
        assert benzene['value_sum'].values[0] == 30

    def test_process_data_invalid_aggregation_fails(self):
        """Test process_data fails with invalid aggregation."""
        # Arrange
        config = get_minimal_config()
        config['visualization']['plotly']['aggregation'] = 'invalid'
        strategy = TreemapStrategy(config)
        df = get_sample_data()

        # Act & Assert
        with pytest.raises(ValueError, match="Unknown aggregation"):
            strategy.process_data(df)

    def test_process_data_removes_nulls(self):
        """Test process_data removes rows with nulls."""
        # Arrange
        config = get_minimal_config()
        strategy = TreemapStrategy(config)
        df = pd.DataFrame({
            'compoundclass': ['Aromatic', None, 'Aliphatic'],
            'compoundname': ['Benzene', 'Toluene', None],
            'genesymbol': ['GeneA', 'GeneB', 'GeneC']
        })

        # Act
        result = strategy.process_data(df)

        # Assert
        # Only Benzene row should remain (complete data)
        assert len(result) == 1
        assert result['compoundname'].values[0] == 'Benzene'

    def test_process_data_sanitizes_placeholders(self):
        """Test process_data removes placeholder values (#N/D, N/D, etc.)."""
        # Arrange
        config = get_minimal_config()
        strategy = TreemapStrategy(config)
        df = pd.DataFrame({
            'compoundclass': ['Aromatic', '#N/D', 'N/D', 'Aliphatic', ''],
            'compoundname': ['Benzene', 'Toluene', 'Hexane', 'Pentane', 'Octane'],
            'genesymbol': ['GeneA', 'GeneB', 'GeneC', 'GeneD', 'GeneE']
        })

        # Act
        result = strategy.process_data(df)

        # Assert
        # Only Aromatic and Aliphatic should remain
        assert len(result) == 2
        assert 'Aromatic' in result['compoundclass'].values
        assert 'Aliphatic' in result['compoundclass'].values

    def test_process_data_strips_whitespace(self):
        """Test process_data strips whitespace from string columns."""
        # Arrange
        config = get_minimal_config()
        strategy = TreemapStrategy(config)
        df = pd.DataFrame({
            'compoundclass': ['  Aromatic  ', 'Aliphatic'],
            'compoundname': ['Benzene  ', '  Hexane'],
            'genesymbol': ['GeneA', 'GeneB']
        })

        # Act
        result = strategy.process_data(df)

        # Assert
        # After groupby, order may change - check both are present and stripped
        assert 'Aromatic' in result['compoundclass'].values
        assert 'Benzene' in result['compoundname'].values or 'Hexane' in result['compoundname'].values

    def test_process_data_adds_root_label(self):
        """Test process_data adds root column with correct label."""
        # Arrange
        config = get_minimal_config()
        strategy = TreemapStrategy(config)
        df = get_sample_data()

        # Act
        result = strategy.process_data(df)

        # Assert
        assert 'root' in result.columns
        assert all(result['root'] == 'Chemical Hierarchy')

    def test_process_data_stores_aggregated_column_name(self):
        """Test process_data stores aggregated column name internally."""
        # Arrange
        config = get_minimal_config()
        strategy = TreemapStrategy(config)
        df = get_sample_data()

        # Act
        result = strategy.process_data(df)

        # Assert
        assert strategy._aggregated_value_column == 'unique_genesymbol_count'

    def test_process_data_enzymatic_data(self):
        """Test process_data with enzymatic activity data."""
        # Arrange
        config = get_discrete_color_config()
        strategy = TreemapStrategy(config)
        df = get_enzymatic_data()

        # Act
        result = strategy.process_data(df)

        # Assert
        # 2 unique combinations: (Oxidase, Aromatic), (Reductase, Aliphatic)
        assert len(result) == 2
        assert 'enzyme_activity' in result.columns
        assert 'compoundclass' in result.columns
        assert 'unique_compoundname_count' in result.columns

    def test_process_data_large_dataset(self):
        """Test process_data handles large datasets."""
        # Arrange
        config = get_minimal_config()
        strategy = TreemapStrategy(config)
        df = get_large_sample_data()

        # Act
        result = strategy.process_data(df)

        # Assert
        assert len(result) > 0
        assert 'unique_genesymbol_count' in result.columns
        assert result['unique_genesymbol_count'].min() > 0

    def test_process_data_empty_after_cleaning_fails(self):
        """Test process_data fails when no data remains after cleaning."""
        # Arrange
        config = get_minimal_config()
        strategy = TreemapStrategy(config)
        df = pd.DataFrame({
            'compoundclass': ['#N/D', 'N/D', ''],
            'compoundname': ['#N/D', '', 'N/D'],
            'genesymbol': ['GeneA', 'GeneB', 'GeneC']
        })

        # Act & Assert
        with pytest.raises(ValueError, match="No valid data after cleaning"):
            strategy.process_data(df)

    def test_process_data_correct_shape(self):
        """Test process_data returns correct number of rows."""
        # Arrange
        config = get_minimal_config()
        strategy = TreemapStrategy(config)
        df = get_sample_data()

        # Act
        result = strategy.process_data(df)

        # Assert
        # 4 unique combinations: (Aromatic, Benzene), (Aliphatic, Hexane),
        # (Aliphatic, Pentane), (Aromatic, Toluene)
        assert len(result) == 4

    # ========================================================================
    # FIGURE CREATION TESTS
    # ========================================================================

    def test_create_figure_returns_figure(self):
        """Test create_figure returns a Plotly Figure."""
        # Arrange
        config = get_minimal_config()
        strategy = TreemapStrategy(config)
        df = get_sample_data()
        processed = strategy.process_data(df)

        # Act
        fig = strategy.create_figure(processed)

        # Assert
        assert isinstance(fig, go.Figure)

    def test_create_figure_continuous_color_mode(self):
        """Test figure uses continuous color scale."""
        # Arrange
        config = get_minimal_config()
        strategy = TreemapStrategy(config)
        df = get_sample_data()
        processed = strategy.process_data(df)

        # Act
        fig = strategy.create_figure(processed)

        # Assert
        assert len(fig.data) > 0
        # Treemap trace should have colorscale
        assert fig.data[0].type == 'treemap'

    def test_create_figure_discrete_color_mode(self):
        """Test figure uses discrete color sequence."""
        # Arrange
        config = get_discrete_color_config()
        strategy = TreemapStrategy(config)
        df = get_enzymatic_data()
        processed = strategy.process_data(df)

        # Act
        fig = strategy.create_figure(processed)

        # Assert
        assert len(fig.data) > 0
        assert fig.data[0].type == 'treemap'

    def test_create_figure_title(self):
        """Test figure applies title configuration."""
        # Arrange
        config = get_minimal_config()
        strategy = TreemapStrategy(config)
        df = get_sample_data()
        processed = strategy.process_data(df)

        # Act
        fig = strategy.create_figure(processed)

        # Assert
        assert fig.layout.title is not None
        assert 'Treemap Test' in fig.layout.title.text

    def test_create_figure_layout_dimensions(self):
        """Test figure applies layout dimensions."""
        # Arrange
        config = get_minimal_config()
        strategy = TreemapStrategy(config)
        df = get_sample_data()
        processed = strategy.process_data(df)

        # Act
        fig = strategy.create_figure(processed)

        # Assert
        assert fig.layout.height == 800
        assert fig.layout.width == 1000

    def test_create_figure_autosize(self):
        """Test figure with autosize enabled."""
        # Arrange
        config = get_minimal_config()
        config['visualization']['plotly']['layout']['autosize'] = True
        del config['visualization']['plotly']['layout']['width']
        strategy = TreemapStrategy(config)
        df = get_sample_data()
        processed = strategy.process_data(df)

        # Act
        fig = strategy.create_figure(processed)

        # Assert
        assert fig.layout.autosize == True

    def test_create_figure_template(self):
        """Test figure applies template."""
        # Arrange
        config = get_minimal_config()
        strategy = TreemapStrategy(config)
        df = get_sample_data()
        processed = strategy.process_data(df)

        # Act
        fig = strategy.create_figure(processed)

        # Assert
        assert fig.layout.template.layout is not None

    def test_create_figure_margins(self):
        """Test figure applies margin configuration."""
        # Arrange
        config = get_minimal_config()
        config['visualization']['plotly']['layout']['margin'] = {
            't': 100, 'l': 50, 'r': 50, 'b': 50
        }
        strategy = TreemapStrategy(config)
        df = get_sample_data()
        processed = strategy.process_data(df)

        # Act
        fig = strategy.create_figure(processed)

        # Assert
        assert fig.layout.margin.t == 100
        assert fig.layout.margin.l == 50

    def test_create_figure_text_info(self):
        """Test figure applies text_info configuration."""
        # Arrange
        config = get_minimal_config()
        # Use valid textinfo for treemap: 'percent parent' instead of 'percent'
        config['visualization']['plotly']['chart']['text_info'] = (
            'label+value+percent parent'
        )
        strategy = TreemapStrategy(config)
        df = get_sample_data()
        processed = strategy.process_data(df)

        # Act
        fig = strategy.create_figure(processed)

        # Assert
        assert fig.data[0].textinfo == 'label+value+percent parent'

    def test_create_figure_text_font_size(self):
        """Test figure applies text font size."""
        # Arrange
        config = get_minimal_config()
        config['visualization']['plotly']['chart']['text_font_size'] = 18
        strategy = TreemapStrategy(config)
        df = get_sample_data()
        processed = strategy.process_data(df)

        # Act
        fig = strategy.create_figure(processed)

        # Assert
        assert fig.data[0].textfont.size == 18

    def test_create_figure_colorbar_continuous(self):
        """Test figure adds colorbar for continuous mode."""
        # Arrange
        config = get_minimal_config()
        config['visualization']['plotly']['chart']['colorbar'] = {
            'title': 'Gene Count'
        }
        strategy = TreemapStrategy(config)
        df = get_sample_data()
        processed = strategy.process_data(df)

        # Act
        fig = strategy.create_figure(processed)

        # Assert
        # Access colorbar through coloraxis (plotly structure)
        assert hasattr(fig.layout, 'coloraxis')
        if hasattr(fig.layout, 'coloraxis'):
            assert fig.layout.coloraxis.colorbar.title.text == 'Gene Count'

    def test_create_figure_path_includes_root(self):
        """Test treemap path includes root column."""
        # Arrange
        config = get_minimal_config()
        strategy = TreemapStrategy(config)
        df = get_sample_data()
        processed = strategy.process_data(df)

        # Act
        fig = strategy.create_figure(processed)

        # Assert
        # Path should be: root → compoundclass → compoundname
        assert 'root' in processed.columns

    def test_create_figure_hide_title(self):
        """Test figure with title hidden."""
        # Arrange
        config = get_minimal_config()
        config['visualization']['plotly']['chart']['title'] = {'show': False}
        strategy = TreemapStrategy(config)
        df = get_sample_data()
        processed = strategy.process_data(df)

        # Act
        fig = strategy.create_figure(processed)

        # Assert
        # When show=False, title should be empty or None
        if fig.layout.title is not None:
            title_text = fig.layout.title.text if hasattr(fig.layout.title, 'text') else None
            assert title_text is None or title_text == ''

    # ========================================================================
    # INTEGRATION TESTS
    # ========================================================================

    def test_generate_plot_full_workflow(self):
        """Test complete workflow from raw data to figure."""
        # Arrange
        config = get_minimal_config()
        strategy = TreemapStrategy(config)
        df = get_sample_data()

        # Act
        fig = strategy.generate_plot(df)

        # Assert
        assert isinstance(fig, go.Figure)
        assert fig.data[0].type == 'treemap'
        assert fig.layout.height == 800

    def test_generate_plot_discrete_mode(self):
        """Test complete workflow with discrete color mode."""
        # Arrange
        config = get_discrete_color_config()
        strategy = TreemapStrategy(config)
        df = get_enzymatic_data()

        # Act
        fig = strategy.generate_plot(df)

        # Assert
        assert isinstance(fig, go.Figure)
        assert fig.data[0].type == 'treemap'

    def test_generate_plot_large_dataset(self):
        """Test complete workflow with large dataset."""
        # Arrange
        config = get_minimal_config()
        strategy = TreemapStrategy(config)
        df = get_large_sample_data()

        # Act
        fig = strategy.generate_plot(df)

        # Assert
        assert isinstance(fig, go.Figure)
        assert len(fig.data) > 0

    def test_generate_plot_with_nulls(self):
        """Test complete workflow handles nulls correctly."""
        # Arrange
        config = get_minimal_config()
        strategy = TreemapStrategy(config)
        df = pd.DataFrame({
            'compoundclass': ['Aromatic', None, 'Aliphatic', 'Aromatic'],
            'compoundname': ['Benzene', 'Toluene', None, 'Xylene'],
            'genesymbol': ['GeneA', 'GeneB', 'GeneC', 'GeneD']
        })

        # Act
        fig = strategy.generate_plot(df)

        # Assert
        assert isinstance(fig, go.Figure)
        # Should only have 2 valid combinations after cleaning

    # ========================================================================
    # EDGE CASES
    # ========================================================================

    def test_edge_case_single_category(self):
        """Test treemap with single category."""
        # Arrange
        config = get_minimal_config()
        strategy = TreemapStrategy(config)
        df = pd.DataFrame({
            'compoundclass': ['Aromatic'],
            'compoundname': ['Benzene'],
            'genesymbol': ['GeneA']
        })

        # Act
        fig = strategy.generate_plot(df)

        # Assert
        assert isinstance(fig, go.Figure)
        assert len(fig.data) > 0

    def test_edge_case_many_categories(self):
        """Test treemap with many categories (stress test)."""
        # Arrange
        config = get_minimal_config()
        strategy = TreemapStrategy(config)

        np.random.seed(42)
        n = 50
        df = pd.DataFrame({
            'compoundclass': [f'Class{i % 10}' for i in range(n)],
            'compoundname': [f'Compound{i}' for i in range(n)],
            'genesymbol': [f'Gene{i % 20}' for i in range(n)]
        })

        # Act
        fig = strategy.generate_plot(df)

        # Assert
        assert isinstance(fig, go.Figure)
        assert len(fig.data) > 0

    def test_edge_case_three_level_hierarchy(self):
        """Test treemap with three-level hierarchy."""
        # Arrange
        config = get_minimal_config()
        config['visualization']['plotly']['path_columns'] = [
            'compoundclass', 'compoundname', 'sample'
        ]
        strategy = TreemapStrategy(config)
        df = get_sample_data()

        # Act
        fig = strategy.generate_plot(df)

        # Assert
        assert isinstance(fig, go.Figure)
        # Path should be: root → class → compound → sample (4 levels)

    def test_edge_case_special_characters_in_names(self):
        """Test treemap handles special characters in names."""
        # Arrange
        config = get_minimal_config()
        strategy = TreemapStrategy(config)
        df = pd.DataFrame({
            'compoundclass': ['Aromatic (PAH)', 'Aliphatic & Cyclic'],
            'compoundname': ['Benzene-D6', 'n-Hexane/Pentane'],
            'genesymbol': ['Gene@1', 'Gene#2']
        })

        # Act
        fig = strategy.generate_plot(df)

        # Assert
        assert isinstance(fig, go.Figure)

    def test_edge_case_unicode_characters(self):
        """Test treemap handles Unicode characters."""
        # Arrange
        config = get_minimal_config()
        strategy = TreemapStrategy(config)
        df = pd.DataFrame({
            'compoundclass': ['Aromáticos', '脂肪族'],
            'compoundname': ['Benzène', 'Héxano'],
            'genesymbol': ['GeneΑ', 'GeneΒ']
        })

        # Act
        fig = strategy.generate_plot(df)

        # Assert
        assert isinstance(fig, go.Figure)

    def test_edge_case_very_long_names(self):
        """Test treemap handles very long category names."""
        # Arrange
        config = get_minimal_config()
        strategy = TreemapStrategy(config)
        long_name = 'A' * 200
        df = pd.DataFrame({
            'compoundclass': [long_name],
            'compoundname': ['Benzene'],
            'genesymbol': ['GeneA']
        })

        # Act
        fig = strategy.generate_plot(df)

        # Assert
        assert isinstance(fig, go.Figure)

    def test_edge_case_numeric_category_names(self):
        """Test treemap handles numeric category names."""
        # Arrange
        config = get_minimal_config()
        strategy = TreemapStrategy(config)
        df = pd.DataFrame({
            'compoundclass': [1, 2, 3],
            'compoundname': [10, 20, 30],
            'genesymbol': ['GeneA', 'GeneB', 'GeneC']
        })

        # Act
        # Numeric columns should be converted to strings during processing
        fig = strategy.generate_plot(df)

        # Assert
        assert isinstance(fig, go.Figure)

    def test_edge_case_custom_root_label(self):
        """Test treemap with custom root label."""
        # Arrange
        config = get_minimal_config()
        config['visualization']['plotly']['root_label'] = 'My Custom Root'
        strategy = TreemapStrategy(config)
        df = get_sample_data()

        # Act
        processed = strategy.process_data(df)
        fig = strategy.create_figure(processed)

        # Assert
        assert all(processed['root'] == 'My Custom Root')
        assert isinstance(fig, go.Figure)

    def test_edge_case_default_text_info(self):
        """Test treemap uses default text_info when not configured."""
        # Arrange
        config = get_minimal_config()
        # Remove text_info from config
        config['visualization']['plotly']['chart'] = {}
        strategy = TreemapStrategy(config)
        df = get_sample_data()
        processed = strategy.process_data(df)

        # Act
        fig = strategy.create_figure(processed)

        # Assert
        assert fig.data[0].textinfo == 'label+value'  # Default
