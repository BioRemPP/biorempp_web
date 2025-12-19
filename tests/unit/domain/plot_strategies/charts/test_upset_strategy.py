"""
Unit Tests for UpSetStrategy.

This module tests the UpSetStrategy class, which creates UpSet plots for
visualizing set intersections across multiple categories (e.g., databases,
agencies).

Test Categories:
- Initialization: Test strategy creation and config validation
- Data Validation: Test _validate_data() and validate_data() methods
- Data Cleaning: Test _clean_data() method
- Set Building: Test _build_category_sets() method
- Figure Creation: Test create_figure() and helper methods
- Integration: Test complete generate_plot() workflow
- Edge Cases: Test boundary conditions and error scenarios
"""

import pytest
import pandas as pd
import plotly.graph_objects as go
from unittest.mock import Mock, patch

from src.domain.plot_strategies.charts.upset_strategy import UpSetStrategy


# ============================================================================
# HELPER FUNCTIONS - CONFIGURATION BUILDERS
# ============================================================================

def get_minimal_config():
    """Get minimal valid configuration."""
    return {
        'metadata': {'use_case_id': 'UC-1.1'},
        'visualization': {
            'strategy': 'UpSetStrategy',
            'plotly': {
                'entity_column': 'ko',
                'category_column': 'database'
            }
        }
    }


def get_full_config():
    """Get full configuration with all options."""
    return {
        'metadata': {'use_case_id': 'UC-1.1'},
        'visualization': {
            'strategy': 'UpSetStrategy',
            'plotly': {
                'entity_column': 'ko',
                'category_column': 'database',
                'sort_by': 'cardinality',
                'show_counts': True,
                'show_percentages': False,
                'min_subset_size': 1,
                'max_subset_rank': 20,
                'fig_width': 14,
                'fig_height': 8,
                'bar_color': '#0d6efd',
                'layout': {
                    'title': 'KO Distribution Across Databases',
                    'height': 600,
                    'width': 1000,
                    'margin_left': 20,
                    'margin_right': 20,
                    'margin_top': 60,
                    'margin_bottom': 80
                }
            }
        }
    }


# ============================================================================
# INITIALIZATION TESTS
# ============================================================================

class TestUpSetStrategyInitialization:
    """Test UpSetStrategy initialization."""

    def test_initialization_with_minimal_config(self):
        """Test initialization with minimal required config."""
        config = get_minimal_config()
        strategy = UpSetStrategy(config)

        assert strategy.entity_column == 'ko'
        assert strategy.category_column == 'database'
        assert strategy.sort_by == 'cardinality'  # default
        assert strategy.show_counts is True  # default

    def test_initialization_with_full_config(self):
        """Test initialization with full config."""
        config = get_full_config()
        strategy = UpSetStrategy(config)

        assert strategy.entity_column == 'ko'
        assert strategy.category_column == 'database'
        assert strategy.sort_by == 'cardinality'
        assert strategy.show_counts is True
        assert strategy.show_percentages is False
        assert strategy.min_subset_size == 1
        assert strategy.max_subset_rank == 20
        assert strategy.fig_width == 14
        assert strategy.fig_height == 8
        assert strategy.bar_color == '#0d6efd'

    def test_initialization_missing_entity_column_fails(self):
        """Test that missing entity_column raises ValueError."""
        config = get_minimal_config()
        del config['visualization']['plotly']['entity_column']

        with pytest.raises(ValueError, match="requires 'entity_column'"):
            UpSetStrategy(config)

    def test_initialization_missing_category_column_fails(self):
        """Test that missing category_column raises ValueError."""
        config = get_minimal_config()
        del config['visualization']['plotly']['category_column']

        with pytest.raises(ValueError, match="requires 'category_column'"):
            UpSetStrategy(config)

    def test_initialization_extracts_default_values(self):
        """Test that default values are set correctly."""
        config = get_minimal_config()
        strategy = UpSetStrategy(config)

        assert strategy.sort_by == 'cardinality'
        assert strategy.show_counts is True
        assert strategy.show_percentages is False
        assert strategy.min_subset_size == 0
        assert strategy.max_subset_rank is None
        assert strategy.fig_width == 14
        assert strategy.fig_height == 8
        assert strategy.bar_color == '#0d6efd'


# ============================================================================
# DATA VALIDATION TESTS
# ============================================================================

class TestDataValidation:
    """Test validate_data() and _validate_data() methods."""

    def test_validate_empty_dataframe_fails(self):
        """Test that empty DataFrame raises ValueError."""
        config = get_minimal_config()
        strategy = UpSetStrategy(config)

        df = pd.DataFrame()

        with pytest.raises(ValueError, match="DataFrame is empty"):
            strategy.validate_data(df)

    def test_validate_missing_entity_column_fails(self):
        """Test that missing entity column raises ValueError."""
        config = get_minimal_config()
        strategy = UpSetStrategy(config)

        df = pd.DataFrame({
            'database': ['BioRemPP', 'KEGG']
        })

        with pytest.raises(ValueError, match="'ko' not found"):
            strategy.validate_data(df)

    def test_validate_missing_category_column_fails(self):
        """Test that missing category column raises ValueError."""
        config = get_minimal_config()
        strategy = UpSetStrategy(config)

        df = pd.DataFrame({
            'ko': ['K00001', 'K00002']
        })

        with pytest.raises(ValueError, match="'database' not found"):
            strategy.validate_data(df)

    def test_validate_passes_with_valid_data(self):
        """Test that validation passes with valid data."""
        config = get_minimal_config()
        strategy = UpSetStrategy(config)

        df = pd.DataFrame({
            'ko': ['K00001', 'K00002'],
            'database': ['BioRemPP', 'KEGG']
        })

        # Should not raise
        strategy.validate_data(df)


# ============================================================================
# DATA CLEANING TESTS
# ============================================================================

class TestDataCleaning:
    """Test _clean_data() method."""

    def test_clean_data_removes_nulls(self):
        """Test that null values are removed."""
        config = get_minimal_config()
        strategy = UpSetStrategy(config)

        df = pd.DataFrame({
            'ko': ['K00001', None, 'K00003'],
            'database': ['BioRemPP', 'KEGG', None]
        })

        result = strategy._clean_data(df)

        # Only K00001 has both values
        assert len(result) == 1
        assert result['ko'].iloc[0] == 'K00001'

    def test_clean_data_strips_whitespace(self):
        """Test that whitespace is stripped."""
        config = get_minimal_config()
        strategy = UpSetStrategy(config)

        df = pd.DataFrame({
            'ko': ['  K00001  ', 'K00002'],
            'database': ['BioRemPP  ', '  KEGG']
        })

        result = strategy._clean_data(df)

        assert result['ko'].iloc[0] == 'K00001'
        assert result['database'].iloc[0] == 'BioRemPP'

    def test_clean_data_removes_empty_strings(self):
        """Test that empty strings are filtered out."""
        config = get_minimal_config()
        strategy = UpSetStrategy(config)

        df = pd.DataFrame({
            'ko': ['K00001', '', 'K00003'],
            'database': ['BioRemPP', 'KEGG', '']
        })

        result = strategy._clean_data(df)

        # Only K00001 has valid values
        assert len(result) == 1
        assert result['ko'].iloc[0] == 'K00001'

    def test_clean_data_removes_duplicates(self):
        """Test that duplicate entity-category pairs are removed."""
        config = get_minimal_config()
        strategy = UpSetStrategy(config)

        df = pd.DataFrame({
            'ko': ['K00001', 'K00001', 'K00002'],
            'database': ['BioRemPP', 'BioRemPP', 'KEGG'],
            'extra_col': ['A', 'B', 'C']  # Extra column
        })

        result = strategy._clean_data(df)

        # Should have 2 unique pairs
        assert len(result) == 2
        assert 'extra_col' not in result.columns  # Extra columns removed

    def test_clean_data_all_invalid_fails(self):
        """Test that all-invalid data raises ValueError."""
        config = get_minimal_config()
        strategy = UpSetStrategy(config)

        df = pd.DataFrame({
            'ko': ['', '', ''],
            'database': ['', '', '']
        })

        with pytest.raises(ValueError, match="No valid data after cleaning"):
            strategy._clean_data(df)


# ============================================================================
# SET BUILDING TESTS
# ============================================================================

class TestSetBuilding:
    """Test _build_category_sets() method."""

    def test_build_category_sets_returns_dict(self):
        """Test that category sets are returned as dict."""
        config = get_minimal_config()
        strategy = UpSetStrategy(config)

        df = pd.DataFrame({
            'ko': ['K00001', 'K00002', 'K00003'],
            'database': ['BioRemPP', 'BioRemPP', 'KEGG']
        })

        result = strategy._build_category_sets(df)

        assert isinstance(result, dict)
        assert 'BioRemPP' in result
        assert 'KEGG' in result

    def test_build_category_sets_creates_sets(self):
        """Test that values are sets of unique entities."""
        config = get_minimal_config()
        strategy = UpSetStrategy(config)

        df = pd.DataFrame({
            'ko': ['K00001', 'K00002', 'K00001', 'K00003'],
            'database': ['BioRemPP', 'BioRemPP', 'KEGG', 'KEGG']
        })

        result = strategy._build_category_sets(df)

        assert isinstance(result['BioRemPP'], set)
        assert result['BioRemPP'] == {'K00001', 'K00002'}
        assert result['KEGG'] == {'K00001', 'K00003'}

    def test_build_category_sets_handles_overlaps(self):
        """Test correct handling of overlapping entities."""
        config = get_minimal_config()
        strategy = UpSetStrategy(config)

        df = pd.DataFrame({
            'ko': ['K00001', 'K00001', 'K00002'],
            'database': ['BioRemPP', 'KEGG', 'HADEG']
        })

        result = strategy._build_category_sets(df)

        # K00001 appears in both BioRemPP and KEGG
        assert 'K00001' in result['BioRemPP']
        assert 'K00001' in result['KEGG']
        assert 'K00002' in result['HADEG']

    def test_build_category_sets_multiple_categories(self):
        """Test with multiple categories."""
        config = get_minimal_config()
        strategy = UpSetStrategy(config)

        df = pd.DataFrame({
            'ko': ['K00001', 'K00002', 'K00003', 'K00004'],
            'database': ['BioRemPP', 'KEGG', 'HADEG', 'BioRemPP']
        })

        result = strategy._build_category_sets(df)

        assert len(result) == 3
        assert len(result['BioRemPP']) == 2
        assert len(result['KEGG']) == 1
        assert len(result['HADEG']) == 1


# ============================================================================
# FIGURE CREATION TESTS
# ============================================================================

class TestFigureCreation:
    """Test create_figure() and related methods."""

    @patch('matplotlib.pyplot.close')
    @patch('matplotlib.pyplot.savefig')
    @patch('matplotlib.pyplot.figure')
    @patch('src.domain.plot_strategies.charts.upset_strategy.from_contents')
    @patch('src.domain.plot_strategies.charts.upset_strategy.UpSet')
    def test_create_figure_returns_figure(
        self, mock_upset_class, mock_from_contents,
        mock_plt_figure, mock_savefig, mock_close
    ):
        """Test that create_figure returns a Plotly Figure."""
        config = get_minimal_config()
        strategy = UpSetStrategy(config)

        # Prepare data
        df = pd.DataFrame({
            'ko': ['K00001', 'K00002'],
            'database': ['BioRemPP', 'KEGG']
        })

        # Mock category sets
        strategy._category_sets = {
            'BioRemPP': {'K00001'},
            'KEGG': {'K00002'}
        }

        # Mock upsetplot objects
        mock_upset_data = Mock()
        mock_from_contents.return_value = mock_upset_data
        mock_upset_instance = Mock()
        mock_upset_class.return_value = mock_upset_instance

        # Mock matplotlib figure
        mock_fig = Mock()
        mock_plt_figure.return_value = mock_fig
        mock_buf = Mock()
        mock_buf.read.return_value = b'fake_image_data'

        with patch('io.BytesIO', return_value=mock_buf):
            with patch('base64.b64encode', return_value=b'ZmFrZQ=='):
                fig = strategy.create_figure(df)

        assert isinstance(fig, go.Figure)

    def test_build_annotation_text_formats_correctly(self):
        """Test annotation text formatting."""
        config = get_minimal_config()
        strategy = UpSetStrategy(config)

        category_sets = {
            'BioRemPP': {'K00001', 'K00002', 'K00003'},
            'KEGG': {'K00001'},
            'HADEG': {'K00001', 'K00002'}
        }

        result = strategy._build_annotation_text(category_sets)

        assert '<b>Set Sizes:</b>' in result
        assert 'BioRemPP: 3' in result
        assert 'HADEG: 2' in result
        assert 'KEGG: 1' in result

    def test_build_annotation_text_sorted_by_size(self):
        """Test that annotation is sorted by set size."""
        config = get_minimal_config()
        strategy = UpSetStrategy(config)

        category_sets = {
            'A': {'1'},
            'B': {'1', '2', '3'},
            'C': {'1', '2'}
        }

        result = strategy._build_annotation_text(category_sets)

        # Should be ordered: B (3) > C (2) > A (1)
        b_pos = result.index('B: 3')
        c_pos = result.index('C: 2')
        a_pos = result.index('A: 1')

        assert b_pos < c_pos < a_pos


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

class TestIntegration:
    """Test complete workflow integration."""

    def test_process_data_stores_category_sets(self):
        """Test that process_data stores category sets."""
        config = get_minimal_config()
        strategy = UpSetStrategy(config)

        df = pd.DataFrame({
            'ko': ['K00001', 'K00002', 'K00001'],
            'database': ['BioRemPP', 'BioRemPP', 'KEGG']
        })

        result = strategy.process_data(df)

        # Should have stored category sets
        assert hasattr(strategy, '_category_sets')
        assert 'BioRemPP' in strategy._category_sets
        assert 'KEGG' in strategy._category_sets
        assert len(result) == 3  # Cleaned data returned

    @patch('matplotlib.pyplot.close')
    @patch('matplotlib.pyplot.savefig')
    @patch('matplotlib.pyplot.figure')
    @patch('src.domain.plot_strategies.charts.upset_strategy.from_contents')
    @patch('src.domain.plot_strategies.charts.upset_strategy.UpSet')
    def test_generate_plot_complete_workflow(
        self, mock_upset_class, mock_from_contents,
        mock_plt_figure, mock_savefig, mock_close
    ):
        """Test complete generate_plot workflow."""
        config = get_minimal_config()
        strategy = UpSetStrategy(config)

        df = pd.DataFrame({
            'ko': ['K00001', 'K00002', 'K00001', 'K00003'],
            'database': ['BioRemPP', 'BioRemPP', 'KEGG', 'HADEG']
        })

        # Mock upsetplot
        mock_upset_data = Mock()
        mock_upset_data.__len__ = Mock(return_value=5)
        mock_from_contents.return_value = mock_upset_data
        mock_upset_instance = Mock()
        mock_upset_class.return_value = mock_upset_instance

        # Mock matplotlib
        mock_fig = Mock()
        mock_plt_figure.return_value = mock_fig
        mock_buf = Mock()
        mock_buf.read.return_value = b'fake_image'

        with patch('io.BytesIO', return_value=mock_buf):
            with patch('base64.b64encode', return_value=b'ZmFrZQ=='):
                fig = strategy.generate(df)

        assert isinstance(fig, go.Figure)

    @patch('matplotlib.pyplot.close')
    @patch('matplotlib.pyplot.savefig')
    @patch('matplotlib.pyplot.figure')
    @patch('src.domain.plot_strategies.charts.upset_strategy.from_contents')
    @patch('src.domain.plot_strategies.charts.upset_strategy.UpSet')
    def test_generate_plot_via_base_class_method(
        self, mock_upset_class, mock_from_contents,
        mock_plt_figure, mock_savefig, mock_close
    ):
        """Test generate_plot via BasePlotStrategy.generate_plot()."""
        config = get_minimal_config()
        strategy = UpSetStrategy(config)

        df = pd.DataFrame({
            'ko': ['K00001', 'K00002'],
            'database': ['BioRemPP', 'KEGG']
        })

        # Mock upsetplot
        mock_upset_data = Mock()
        mock_from_contents.return_value = mock_upset_data
        mock_upset_instance = Mock()
        mock_upset_class.return_value = mock_upset_instance

        # Mock matplotlib
        mock_fig = Mock()
        mock_plt_figure.return_value = mock_fig
        mock_buf = Mock()
        mock_buf.read.return_value = b'fake'

        with patch('io.BytesIO', return_value=mock_buf):
            with patch('base64.b64encode', return_value=b'ZmFrZQ=='):
                fig = strategy.generate_plot(df)

        assert isinstance(fig, go.Figure)


# ============================================================================
# EDGE CASES
# ============================================================================

class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_single_category(self):
        """Test with single category (no intersections)."""
        config = get_minimal_config()
        strategy = UpSetStrategy(config)

        df = pd.DataFrame({
            'ko': ['K00001', 'K00002', 'K00003'],
            'database': ['BioRemPP', 'BioRemPP', 'BioRemPP']
        })

        category_sets = strategy._build_category_sets(df)

        assert len(category_sets) == 1
        assert len(category_sets['BioRemPP']) == 3

    def test_no_overlaps_between_categories(self):
        """Test categories with no overlapping entities."""
        config = get_minimal_config()
        strategy = UpSetStrategy(config)

        df = pd.DataFrame({
            'ko': ['K00001', 'K00002', 'K00003'],
            'database': ['BioRemPP', 'KEGG', 'HADEG']
        })

        category_sets = strategy._build_category_sets(df)

        # Each category has exactly one unique KO
        assert len(category_sets['BioRemPP']) == 1
        assert len(category_sets['KEGG']) == 1
        assert len(category_sets['HADEG']) == 1

        # No intersections
        assert len(category_sets['BioRemPP'] & category_sets['KEGG']) == 0

    def test_complete_overlap_all_categories(self):
        """Test when all categories share all entities."""
        config = get_minimal_config()
        strategy = UpSetStrategy(config)

        df = pd.DataFrame({
            'ko': ['K00001', 'K00001', 'K00001'],
            'database': ['BioRemPP', 'KEGG', 'HADEG']
        })

        category_sets = strategy._build_category_sets(df)

        # All categories have the same KO
        assert category_sets['BioRemPP'] == {'K00001'}
        assert category_sets['KEGG'] == {'K00001'}
        assert category_sets['HADEG'] == {'K00001'}

    def test_large_number_of_categories(self):
        """Test with many categories."""
        config = get_minimal_config()
        strategy = UpSetStrategy(config)

        # Create data with 10 categories
        df = pd.DataFrame({
            'ko': [f'K{i:05d}' for i in range(100)],
            'database': [f'DB{i % 10}' for i in range(100)]
        })

        category_sets = strategy._build_category_sets(df)

        assert len(category_sets) == 10
        for category in category_sets.values():
            assert len(category) == 10  # Each category has 10 KOs

    def test_large_number_of_entities(self):
        """Test with many entities."""
        config = get_minimal_config()
        strategy = UpSetStrategy(config)

        # Create data with 1000 unique KOs across 3 databases
        df = pd.DataFrame({
            'ko': [f'K{i:05d}' for i in range(1000)],
            'database': ['BioRemPP' if i % 3 == 0 else 'KEGG' if i % 3 == 1 else 'HADEG' for i in range(1000)]
        })

        category_sets = strategy._build_category_sets(df)

        total_entities = sum(len(s) for s in category_sets.values())
        assert total_entities == 1000

    @patch('matplotlib.pyplot.close')
    @patch('matplotlib.pyplot.savefig')
    @patch('matplotlib.pyplot.figure')
    @patch('src.domain.plot_strategies.charts.upset_strategy.from_contents')
    @patch('src.domain.plot_strategies.charts.upset_strategy.UpSet')
    def test_layout_with_autosize(
        self, mock_upset_class, mock_from_contents,
        mock_plt_figure, mock_savefig, mock_close
    ):
        """Test layout with autosize enabled."""
        config = get_full_config()
        config['visualization']['plotly']['layout']['autosize'] = True
        strategy = UpSetStrategy(config)

        df = pd.DataFrame({
            'ko': ['K00001', 'K00002'],
            'database': ['BioRemPP', 'KEGG']
        })

        # Mock upsetplot
        mock_upset_data = Mock()
        mock_from_contents.return_value = mock_upset_data
        mock_upset_instance = Mock()
        mock_upset_class.return_value = mock_upset_instance

        # Mock matplotlib
        mock_fig_obj = Mock()
        mock_plt_figure.return_value = mock_fig_obj
        mock_buf = Mock()
        mock_buf.read.return_value = b'fake'

        with patch('io.BytesIO', return_value=mock_buf):
            with patch('base64.b64encode', return_value=b'ZmFrZQ=='):
                strategy._category_sets = {
                    'BioRemPP': {'K00001'},
                    'KEGG': {'K00002'}
                }
                fig = strategy.create_figure(df)

        # Width should not be set when autosize is True
        assert isinstance(fig, go.Figure)
