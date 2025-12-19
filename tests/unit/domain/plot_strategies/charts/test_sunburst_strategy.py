"""
Unit tests for SunburstStrategy.

This module tests the SunburstStrategy class for hierarchical radial
visualizations with proportional sizing based on quantitative values.

Test Coverage:
- Initialization and configuration parsing
- Data validation (empty data, missing columns, numeric values)
- Data processing (null removal, type coercion, sorting)
- Figure creation (continuous/discrete color, layout, branchvalues)
- Integration tests (full workflow)
- Edge cases (single level, many levels, special characters, etc.)

Author: BioRemPP Development Team
Date: 2025-12-08
"""

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import pytest

from src.domain.plot_strategies.charts.sunburst_strategy import (
    SunburstStrategy
)


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_minimal_config():
    """Get minimal configuration for SunburstStrategy."""
    return {
        'metadata': {'use_case_id': 'UC-4.11', 'module': 'module4'},
        'data': {},
        'validation': {
            'rules': [
                {'type': 'min_rows', 'value': 1}
            ]
        },
        'visualization': {
            'strategy': 'SunburstStrategy',
            'plotly': {
                'path_columns': ['root', 'compound_pathway', 'Pathway'],
                'values_column': 'unique_gene_count',
                'color_column': 'unique_gene_count',
                'color_mode': 'continuous',
                'color_continuous_scale': [
                    '#e9f7f1', 'mediumseagreen', '#0b3d2e'
                ],
                'chart': {
                    'title': {'text': 'Genetic Diversity'},
                    'branchvalues': 'total'
                },
                'layout': {
                    'height': 600,
                    'width': 600,
                    'template': 'simple_white',
                    'margin': {'t': 40, 'l': 20, 'r': 20, 'b': 20}
                }
            }
        }
    }


def get_discrete_color_config():
    """Get configuration with discrete color mode."""
    return {
        'metadata': {'use_case_id': 'UC-4.11', 'module': 'module4'},
        'data': {},
        'validation': {
            'rules': [{'type': 'min_rows', 'value': 1}]
        },
        'visualization': {
            'strategy': 'SunburstStrategy',
            'plotly': {
                'path_columns': ['root', 'level1'],
                'values_column': 'count',
                'color_column': 'level1',
                'color_mode': 'discrete',
                'color_discrete_sequence': ['#1f77b4', '#ff7f0e'],
                'chart': {'title': {'text': 'Discrete Sunburst'}},
                'layout': {'height': 600, 'template': 'simple_white'}
            }
        }
    }


def get_sample_data():
    """Get sample hierarchical data."""
    np.random.seed(42)
    return pd.DataFrame({
        'root': ['All Pathways'] * 6,
        'compound_pathway': ['Alkanes', 'Alkanes', 'Alkenes',
                             'Alkenes', 'Aromatics', 'Aromatics'],
        'Pathway': ['P450-A', 'P450-B', 'Cyto-A',
                    'Cyto-B', 'Ring-A', 'Ring-B'],
        'unique_gene_count': [5, 10, 8, 12, 7, 15]
    })


def get_large_sample_data():
    """Get large hierarchical dataset."""
    np.random.seed(42)
    n_pathways = 100
    compounds = ['Alkanes', 'Alkenes', 'Aromatics', 'Cyclic']
    pathways = [f'Pathway-{i}' for i in range(20)]

    return pd.DataFrame({
        'root': ['All Pathways'] * n_pathways,
        'compound_pathway': np.random.choice(compounds, n_pathways),
        'Pathway': np.random.choice(pathways, n_pathways),
        'unique_gene_count': np.random.randint(1, 50, n_pathways)
    })


# ============================================================================
# TEST CLASS
# ============================================================================

class TestSunburstStrategy:
    """Test suite for SunburstStrategy."""

    # ========================================================================
    # INITIALIZATION TESTS
    # ========================================================================

    def test_init_minimal_config(self):
        """Test initialization with minimal configuration."""
        # Arrange
        config = get_minimal_config()

        # Act
        strategy = SunburstStrategy(config)

        # Assert
        assert strategy is not None
        assert hasattr(strategy, 'data_config')
        assert hasattr(strategy, 'plotly_config')

    def test_init_discrete_color_config(self):
        """Test initialization with discrete color mode."""
        # Arrange
        config = get_discrete_color_config()

        # Act
        strategy = SunburstStrategy(config)

        # Assert
        assert strategy is not None
        assert strategy.plotly_config['color_mode'] == 'discrete'

    def test_init_extracts_configs(self):
        """Test initialization extracts data and plotly configs."""
        # Arrange
        config = get_minimal_config()

        # Act
        strategy = SunburstStrategy(config)

        # Assert
        assert isinstance(strategy.data_config, dict)
        assert isinstance(strategy.plotly_config, dict)
        assert 'path_columns' in strategy.plotly_config
        assert 'values_column' in strategy.plotly_config

    def test_init_logs_use_case(self):
        """Test initialization logs use case ID."""
        # Arrange
        config = get_minimal_config()

        # Act
        strategy = SunburstStrategy(config)

        # Assert
        assert strategy.metadata['use_case_id'] == 'UC-4.11'

    # ========================================================================
    # VALIDATION TESTS
    # ========================================================================

    def test_validate_empty_dataframe_fails(self):
        """Test validation fails with empty DataFrame."""
        # Arrange
        config = get_minimal_config()
        strategy = SunburstStrategy(config)
        df = pd.DataFrame()

        # Act & Assert
        with pytest.raises(ValueError, match="cannot be empty"):
            strategy.validate_data(df)

    def test_validate_no_path_columns_fails(self):
        """Test validation fails when no path_columns configured."""
        # Arrange
        config = get_minimal_config()
        config['visualization']['plotly']['path_columns'] = []
        strategy = SunburstStrategy(config)
        df = get_sample_data()

        # Act & Assert
        with pytest.raises(ValueError, match="path_columns"):
            strategy.validate_data(df)

    def test_validate_no_values_column_fails(self):
        """Test validation fails when no values_column configured."""
        # Arrange
        config = get_minimal_config()
        del config['visualization']['plotly']['values_column']
        strategy = SunburstStrategy(config)
        df = get_sample_data()

        # Act & Assert
        with pytest.raises(ValueError, match="values_column"):
            strategy.validate_data(df)

    def test_validate_missing_path_column(self):
        """Test validation fails when path column is missing."""
        # Arrange
        config = get_minimal_config()
        strategy = SunburstStrategy(config)
        df = pd.DataFrame({
            'root': ['All'],
            'compound_pathway': ['Alkanes'],
            # Missing 'Pathway'
            'unique_gene_count': [5]
        })

        # Act & Assert
        with pytest.raises(ValueError, match="not found"):
            strategy.validate_data(df)

    def test_validate_missing_values_column(self):
        """Test validation fails when values column is missing."""
        # Arrange
        config = get_minimal_config()
        strategy = SunburstStrategy(config)
        df = pd.DataFrame({
            'root': ['All'],
            'compound_pathway': ['Alkanes'],
            'Pathway': ['P450']
            # Missing 'unique_gene_count'
        })

        # Act & Assert
        with pytest.raises(ValueError, match="not found"):
            strategy.validate_data(df)

    def test_validate_non_numeric_values_fails(self):
        """Test validation fails when values column is not numeric."""
        # Arrange
        config = get_minimal_config()
        strategy = SunburstStrategy(config)
        df = pd.DataFrame({
            'root': ['All'],
            'compound_pathway': ['Alkanes'],
            'Pathway': ['P450'],
            'unique_gene_count': ['not_a_number']
        })

        # Act & Assert
        with pytest.raises(ValueError, match="must be numeric"):
            strategy.validate_data(df)

    def test_validate_sample_data_passes(self):
        """Test validation passes with valid sample data."""
        # Arrange
        config = get_minimal_config()
        strategy = SunburstStrategy(config)
        df = get_sample_data()

        # Act & Assert (should not raise)
        strategy.validate_data(df)

    def test_validate_with_nulls_warns(self):
        """Test validation warns about null values."""
        # Arrange
        config = get_minimal_config()
        strategy = SunburstStrategy(config)
        df = pd.DataFrame({
            'root': ['All', None, 'All'],
            'compound_pathway': ['Alkanes', 'Alkenes', 'Aromatics'],
            'Pathway': ['P450', 'Cyto', None],
            'unique_gene_count': [5, 10, 8]
        })

        # Act & Assert
        # Validation should pass but warn (at least 1 complete row)
        strategy.validate_data(df)

    def test_validate_min_rows_constraint(self):
        """Test validation respects min_rows constraint."""
        # Arrange
        config = get_minimal_config()
        # Sunburst reads from validation_rules not validation['rules']
        strategy = SunburstStrategy(config)
        strategy.validation_rules = {'min_rows': 10}
        df = get_sample_data()  # Only 6 rows

        # Act & Assert
        with pytest.raises(ValueError, match="at least 10 rows"):
            strategy.validate_data(df)

    def test_validate_large_dataset(self):
        """Test validation passes with large dataset."""
        # Arrange
        config = get_minimal_config()
        strategy = SunburstStrategy(config)
        df = get_large_sample_data()

        # Act & Assert (should not raise)
        strategy.validate_data(df)

    # ========================================================================
    # DATA PROCESSING TESTS
    # ========================================================================

    def test_process_data_removes_nulls(self):
        """Test process_data removes rows with nulls."""
        # Arrange
        config = get_minimal_config()
        strategy = SunburstStrategy(config)
        df = pd.DataFrame({
            'root': ['All', None, 'All', 'All'],
            'compound_pathway': ['Alkanes', 'Alkenes', 'Aromatics', 'Cyclic'],
            'Pathway': ['P450', 'Cyto', None, 'Ring'],
            'unique_gene_count': [5, 10, 8, 12]
        })

        # Act
        result = strategy.process_data(df)

        # Assert
        # Only 2 complete rows: row 0 and row 3
        assert len(result) == 2

    def test_process_data_coerces_numeric(self):
        """Test process_data coerces values to numeric."""
        # Arrange
        config = get_minimal_config()
        strategy = SunburstStrategy(config)
        df = pd.DataFrame({
            'root': ['All', 'All'],
            'compound_pathway': ['Alkanes', 'Alkenes'],
            'Pathway': ['P450', 'Cyto'],
            'unique_gene_count': ['5', '10']  # String numbers
        })

        # Act
        result = strategy.process_data(df)

        # Assert
        assert pd.api.types.is_numeric_dtype(result['unique_gene_count'])
        assert result['unique_gene_count'].values[0] == 5

    def test_process_data_removes_invalid_numeric(self):
        """Test process_data removes rows with invalid numeric values."""
        # Arrange
        config = get_minimal_config()
        strategy = SunburstStrategy(config)
        df = pd.DataFrame({
            'root': ['All', 'All', 'All'],
            'compound_pathway': ['Alkanes', 'Alkenes', 'Aromatics'],
            'Pathway': ['P450', 'Cyto', 'Ring'],
            'unique_gene_count': [5, 'invalid', 10]
        })

        # Act
        result = strategy.process_data(df)

        # Assert
        # Only 2 rows with valid numeric values
        assert len(result) == 2

    def test_process_data_sorts_by_hierarchy(self):
        """Test process_data sorts by hierarchical columns."""
        # Arrange
        config = get_minimal_config()
        strategy = SunburstStrategy(config)
        df = pd.DataFrame({
            'root': ['All', 'All', 'All'],
            'compound_pathway': ['Cyclic', 'Alkanes', 'Alkenes'],
            'Pathway': ['Ring', 'P450', 'Cyto'],
            'unique_gene_count': [10, 5, 8]
        })

        # Act
        result = strategy.process_data(df)

        # Assert
        # Should be sorted: Alkanes, Alkenes, Cyclic
        assert result['compound_pathway'].values[0] == 'Alkanes'
        assert result['compound_pathway'].values[1] == 'Alkenes'
        assert result['compound_pathway'].values[2] == 'Cyclic'

    def test_process_data_sample_data(self):
        """Test process_data with sample data."""
        # Arrange
        config = get_minimal_config()
        strategy = SunburstStrategy(config)
        df = get_sample_data()

        # Act
        result = strategy.process_data(df)

        # Assert
        assert len(result) == 6  # All rows valid
        assert 'unique_gene_count' in result.columns

    def test_process_data_large_dataset(self):
        """Test process_data handles large datasets."""
        # Arrange
        config = get_minimal_config()
        strategy = SunburstStrategy(config)
        df = get_large_sample_data()

        # Act
        result = strategy.process_data(df)

        # Assert
        assert len(result) == 100  # All rows valid
        assert result['unique_gene_count'].sum() > 0

    def test_process_data_empty_after_cleaning_fails(self):
        """Test process_data fails when no data remains after cleaning."""
        # Arrange
        config = get_minimal_config()
        strategy = SunburstStrategy(config)
        df = pd.DataFrame({
            'root': [None, None],
            'compound_pathway': [None, None],
            'Pathway': [None, None],
            'unique_gene_count': [None, None]
        })

        # Act & Assert
        with pytest.raises(
            ValueError,
            match="All data removed during processing"
        ):
            strategy.process_data(df)

    def test_process_data_preserves_columns(self):
        """Test process_data preserves all original columns."""
        # Arrange
        config = get_minimal_config()
        strategy = SunburstStrategy(config)
        df = get_sample_data()

        # Act
        result = strategy.process_data(df)

        # Assert
        assert set(df.columns) == set(result.columns)

    # ========================================================================
    # FIGURE CREATION TESTS
    # ========================================================================

    def test_create_figure_returns_figure(self):
        """Test create_figure returns a Plotly Figure."""
        # Arrange
        config = get_minimal_config()
        strategy = SunburstStrategy(config)
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
        strategy = SunburstStrategy(config)
        df = get_sample_data()
        processed = strategy.process_data(df)

        # Act
        fig = strategy.create_figure(processed)

        # Assert
        assert len(fig.data) > 0
        assert fig.data[0].type == 'sunburst'

    def test_create_figure_discrete_color_mode(self):
        """Test figure uses discrete color sequence."""
        # Arrange
        config = get_discrete_color_config()
        strategy = SunburstStrategy(config)
        df = pd.DataFrame({
            'root': ['All', 'All'],
            'level1': ['A', 'B'],
            'count': [10, 20]
        })
        processed = strategy.process_data(df)

        # Act
        fig = strategy.create_figure(processed)

        # Assert
        assert len(fig.data) > 0
        assert fig.data[0].type == 'sunburst'

    def test_create_figure_title(self):
        """Test figure applies title configuration."""
        # Arrange
        config = get_minimal_config()
        strategy = SunburstStrategy(config)
        df = get_sample_data()
        processed = strategy.process_data(df)

        # Act
        fig = strategy.create_figure(processed)

        # Assert
        assert fig.layout.title is not None
        assert 'Genetic Diversity' in fig.layout.title.text

    def test_create_figure_layout_dimensions(self):
        """Test figure applies layout dimensions."""
        # Arrange
        config = get_minimal_config()
        strategy = SunburstStrategy(config)
        df = get_sample_data()
        processed = strategy.process_data(df)

        # Act
        fig = strategy.create_figure(processed)

        # Assert
        assert fig.layout.height == 600
        assert fig.layout.width == 600

    def test_create_figure_autosize(self):
        """Test figure with autosize enabled."""
        # Arrange
        config = get_minimal_config()
        config['visualization']['plotly']['layout']['autosize'] = True
        del config['visualization']['plotly']['layout']['width']
        strategy = SunburstStrategy(config)
        df = get_sample_data()
        processed = strategy.process_data(df)

        # Act
        fig = strategy.create_figure(processed)

        # Assert
        assert fig.layout.autosize is True

    def test_create_figure_template(self):
        """Test figure applies template."""
        # Arrange
        config = get_minimal_config()
        strategy = SunburstStrategy(config)
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
        strategy = SunburstStrategy(config)
        df = get_sample_data()
        processed = strategy.process_data(df)

        # Act
        fig = strategy.create_figure(processed)

        # Assert
        assert fig.layout.margin.t == 40
        assert fig.layout.margin.l == 20
        assert fig.layout.margin.r == 20
        assert fig.layout.margin.b == 20

    def test_create_figure_branchvalues_total(self):
        """Test figure uses branchvalues='total'."""
        # Arrange
        config = get_minimal_config()
        strategy = SunburstStrategy(config)
        df = get_sample_data()
        processed = strategy.process_data(df)

        # Act
        fig = strategy.create_figure(processed)

        # Assert
        assert fig.data[0].branchvalues == 'total'

    def test_create_figure_branchvalues_remainder(self):
        """Test figure uses branchvalues='remainder'."""
        # Arrange
        config = get_minimal_config()
        config['visualization']['plotly']['chart']['branchvalues'] = (
            'remainder'
        )
        strategy = SunburstStrategy(config)
        df = get_sample_data()
        processed = strategy.process_data(df)

        # Act
        fig = strategy.create_figure(processed)

        # Assert
        assert fig.data[0].branchvalues == 'remainder'

    def test_create_figure_text_font_size(self):
        """Test figure applies text font size."""
        # Arrange
        config = get_minimal_config()
        config['visualization']['plotly']['chart']['text_font_size'] = 16
        strategy = SunburstStrategy(config)
        df = get_sample_data()
        processed = strategy.process_data(df)

        # Act
        fig = strategy.create_figure(processed)

        # Assert
        assert fig.data[0].textfont.size == 16

    def test_create_figure_colorbar_continuous(self):
        """Test figure adds colorbar for continuous mode."""
        # Arrange
        config = get_minimal_config()
        config['visualization']['plotly']['chart']['colorbar'] = {
            'title': 'Gene Count'
        }
        strategy = SunburstStrategy(config)
        df = get_sample_data()
        processed = strategy.process_data(df)

        # Act
        fig = strategy.create_figure(processed)

        # Assert
        # Sunburst uses coloraxis.colorbar not coloraxis_colorbar
        assert hasattr(fig.layout, 'coloraxis')
        if hasattr(fig.layout, 'coloraxis'):
            assert fig.layout.coloraxis.colorbar.title.text == 'Gene Count'

    def test_create_figure_hide_title(self):
        """Test figure with title hidden."""
        # Arrange
        config = get_minimal_config()
        config['visualization']['plotly']['chart']['title'] = {
            'show': False
        }
        strategy = SunburstStrategy(config)
        df = get_sample_data()
        processed = strategy.process_data(df)

        # Act
        fig = strategy.create_figure(processed)

        # Assert
        # When show=False, title should be empty or None
        if fig.layout.title is not None:
            title_text = (
                fig.layout.title.text
                if hasattr(fig.layout.title, 'text')
                else None
            )
            assert title_text is None or title_text == ''

    def test_create_figure_default_color_scale(self):
        """Test figure uses default color scale when not specified."""
        # Arrange
        config = get_minimal_config()
        del config['visualization']['plotly']['color_continuous_scale']
        strategy = SunburstStrategy(config)
        df = get_sample_data()
        processed = strategy.process_data(df)

        # Act
        fig = strategy.create_figure(processed)

        # Assert
        assert isinstance(fig, go.Figure)

    # ========================================================================
    # INTEGRATION TESTS
    # ========================================================================

    def test_generate_plot_full_workflow(self):
        """Test complete workflow from raw data to figure."""
        # Arrange
        config = get_minimal_config()
        strategy = SunburstStrategy(config)
        df = get_sample_data()

        # Act
        fig = strategy.generate_plot(df)

        # Assert
        assert isinstance(fig, go.Figure)
        assert fig.data[0].type == 'sunburst'
        assert fig.layout.height == 600

    def test_generate_plot_discrete_mode(self):
        """Test complete workflow with discrete color mode."""
        # Arrange
        config = get_discrete_color_config()
        strategy = SunburstStrategy(config)
        df = pd.DataFrame({
            'root': ['All', 'All'],
            'level1': ['A', 'B'],
            'count': [10, 20]
        })

        # Act
        fig = strategy.generate_plot(df)

        # Assert
        assert isinstance(fig, go.Figure)
        assert fig.data[0].type == 'sunburst'

    def test_generate_plot_large_dataset(self):
        """Test complete workflow with large dataset."""
        # Arrange
        config = get_minimal_config()
        strategy = SunburstStrategy(config)
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
        strategy = SunburstStrategy(config)
        df = pd.DataFrame({
            'root': ['All', None, 'All', 'All'],
            'compound_pathway': ['Alkanes', 'Alkenes', None, 'Cyclic'],
            'Pathway': ['P450', 'Cyto', 'Ring', 'Ring'],
            'unique_gene_count': [5, 10, 8, 12]
        })

        # Act
        fig = strategy.generate_plot(df)

        # Assert
        assert isinstance(fig, go.Figure)
        # Should only have 2 valid combinations after cleaning

    # ========================================================================
    # EDGE CASES
    # ========================================================================

    def test_edge_case_single_row(self):
        """Test sunburst with single row."""
        # Arrange
        config = get_minimal_config()
        strategy = SunburstStrategy(config)
        df = pd.DataFrame({
            'root': ['All'],
            'compound_pathway': ['Alkanes'],
            'Pathway': ['P450'],
            'unique_gene_count': [5]
        })

        # Act
        fig = strategy.generate_plot(df)

        # Assert
        assert isinstance(fig, go.Figure)

    def test_edge_case_two_level_hierarchy(self):
        """Test sunburst with only two-level hierarchy."""
        # Arrange
        config = get_minimal_config()
        config['visualization']['plotly']['path_columns'] = ['root', 'level1']
        strategy = SunburstStrategy(config)
        df = pd.DataFrame({
            'root': ['All', 'All'],
            'level1': ['A', 'B'],
            'unique_gene_count': [10, 20]
        })

        # Act
        fig = strategy.generate_plot(df)

        # Assert
        assert isinstance(fig, go.Figure)

    def test_edge_case_four_level_hierarchy(self):
        """Test sunburst with four-level hierarchy."""
        # Arrange
        config = get_minimal_config()
        config['visualization']['plotly']['path_columns'] = [
            'root', 'level1', 'level2', 'level3'
        ]
        strategy = SunburstStrategy(config)
        df = pd.DataFrame({
            'root': ['All', 'All'],
            'level1': ['A', 'A'],
            'level2': ['A1', 'A1'],
            'level3': ['A1a', 'A1b'],
            'unique_gene_count': [10, 20]
        })

        # Act
        fig = strategy.generate_plot(df)

        # Assert
        assert isinstance(fig, go.Figure)

    def test_edge_case_special_characters_in_names(self):
        """Test sunburst handles special characters in names."""
        # Arrange
        config = get_minimal_config()
        strategy = SunburstStrategy(config)
        df = pd.DataFrame({
            'root': ['All (Total)'],
            'compound_pathway': ['Alkanes & Alkenes'],
            'Pathway': ['P450/Cyto'],
            'unique_gene_count': [5]
        })

        # Act
        fig = strategy.generate_plot(df)

        # Assert
        assert isinstance(fig, go.Figure)

    def test_edge_case_unicode_characters(self):
        """Test sunburst handles Unicode characters."""
        # Arrange
        config = get_minimal_config()
        strategy = SunburstStrategy(config)
        df = pd.DataFrame({
            'root': ['Todos'],
            'compound_pathway': ['Alcanos'],
            'Pathway': ['P450-α'],
            'unique_gene_count': [5]
        })

        # Act
        fig = strategy.generate_plot(df)

        # Assert
        assert isinstance(fig, go.Figure)

    def test_edge_case_very_long_names(self):
        """Test sunburst handles very long names."""
        # Arrange
        config = get_minimal_config()
        strategy = SunburstStrategy(config)
        long_name = 'A' * 200
        df = pd.DataFrame({
            'root': ['All'],
            'compound_pathway': [long_name],
            'Pathway': ['P450'],
            'unique_gene_count': [5]
        })

        # Act
        fig = strategy.generate_plot(df)

        # Assert
        assert isinstance(fig, go.Figure)

    def test_edge_case_zero_values(self):
        """Test sunburst handles all zero values (sum to zero)."""
        # Arrange
        config = get_minimal_config()
        strategy = SunburstStrategy(config)
        df = pd.DataFrame({
            'root': ['All', 'All'],
            'compound_pathway': ['Alkanes', 'Alkenes'],
            'Pathway': ['P450', 'Cyto'],
            'unique_gene_count': [0, 0]  # All zeros - sum to zero
        })

        # Act & Assert
        # Plotly sunburst cannot handle when all values sum to zero
        # This is expected behavior
        with pytest.raises(ValueError, match="Failed to create sunburst"):
            strategy.generate_plot(df)

    def test_edge_case_large_values(self):
        """Test sunburst handles very large values."""
        # Arrange
        config = get_minimal_config()
        strategy = SunburstStrategy(config)
        df = pd.DataFrame({
            'root': ['All', 'All'],
            'compound_pathway': ['Alkanes', 'Alkenes'],
            'Pathway': ['P450', 'Cyto'],
            'unique_gene_count': [1000000, 2000000]
        })

        # Act
        fig = strategy.generate_plot(df)

        # Assert
        assert isinstance(fig, go.Figure)

    def test_edge_case_float_values(self):
        """Test sunburst handles float values."""
        # Arrange
        config = get_minimal_config()
        strategy = SunburstStrategy(config)
        df = pd.DataFrame({
            'root': ['All', 'All'],
            'compound_pathway': ['Alkanes', 'Alkenes'],
            'Pathway': ['P450', 'Cyto'],
            'unique_gene_count': [5.5, 10.8]
        })

        # Act
        fig = strategy.generate_plot(df)

        # Assert
        assert isinstance(fig, go.Figure)

    def test_edge_case_string_title_backward_compatibility(self):
        """Test sunburst handles string title (backward compatibility)."""
        # Arrange
        config = get_minimal_config()
        config['visualization']['plotly']['chart']['title'] = 'Simple Title'
        strategy = SunburstStrategy(config)
        df = get_sample_data()
        processed = strategy.process_data(df)

        # Act
        fig = strategy.create_figure(processed)

        # Assert
        assert fig.layout.title is not None
        assert 'Simple Title' in fig.layout.title.text
