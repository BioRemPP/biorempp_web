"""
Unit Tests for FacetedHeatmapStrategy.

This module tests the FacetedHeatmapStrategy class, which creates faceted
heatmap visualizations for toxicity profiles across multiple categories.

Test Categories:
- Initialization: Test strategy creation and configuration
- Data Validation: Test validate_data() method
- Data Processing: Test process_data() method
- Figure Creation: Test create_figure() method
- Integration: Test complete workflow
- Edge Cases: Test boundary conditions
"""

import pytest
import numpy as np
import pandas as pd
import plotly.graph_objects as go

from src.domain.plot_strategies.charts.faceted_heatmap_strategy import (
    FacetedHeatmapStrategy
)


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_minimal_config():
    """Get minimal configuration for faceted heatmap."""
    return {
        'metadata': {'use_case_id': 'UC-7.1'},
        'visualization': {
            'strategy': 'FacetedHeatmapStrategy',
            'plotly': {}
        }
    }


def get_full_config():
    """Get full configuration for faceted heatmap."""
    return {
        'metadata': {'use_case_id': 'UC-7.1'},
        'data': {
            'required_columns': [
                'compoundname', 'endpoint',
                'toxicity_score', 'super_category'
            ]
        },
        'visualization': {
            'strategy': 'FacetedHeatmapStrategy',
            'plotly': {
                'compound_column': 'compoundname',
                'endpoint_column': 'endpoint',
                'score_column': 'toxicity_score',
                'category_column': 'super_category',
                'category_order': [
                    'Nuclear Response',
                    'Stress Response',
                    'Genomic',
                    'Environmental',
                    'Organic'
                ],
                'chart': {
                    'title': {
                        'text': 'Faceted Heatmap of Compound Toxicity',
                        'show': True,
                        'font_size': 16
                    },
                    'colorscale': 'Reds',
                    'colorbar_title': 'Toxicity Score',
                    'yaxis_title': 'Compound',
                    'xaxis_tickangle': -45,
                    'yaxis_tickangle': 0,
                    'horizontal_spacing': 0.02
                },
                'layout': {
                    'height': 800,
                    'width': 1200,
                    'template': 'simple_white',
                    'margin': {
                        'l': 150,
                        'r': 50,
                        't': 80,
                        'b': 100
                    }
                }
            }
        }
    }


def get_sample_data():
    """Get sample toxicity data for testing."""
    np.random.seed(42)

    compounds = ['Compound_A', 'Compound_B', 'Compound_C']
    categories = ['Nuclear Response', 'Stress Response', 'Genomic']
    endpoints = {
        'Nuclear Response': ['NR_AR', 'NR_ER'],
        'Stress Response': ['SR_MMP', 'SR_ATAD5'],
        'Genomic': ['GN_P53', 'GN_BRCA1']
    }

    data = []
    for compound in compounds:
        for category in categories:
            for endpoint in endpoints[category]:
                data.append({
                    'compoundname': compound,
                    'endpoint': endpoint,
                    'toxicity_score': np.random.rand(),
                    'super_category': category
                })

    return pd.DataFrame(data)


# ============================================================================
# INITIALIZATION TESTS
# ============================================================================

class TestFacetedHeatmapStrategyInitialization:
    """Test FacetedHeatmapStrategy initialization."""

    def test_initialization_minimal_config(self):
        """Test initialization with minimal configuration."""
        config = get_minimal_config()
        strategy = FacetedHeatmapStrategy(config)

        assert strategy.compound_column == 'compoundname'
        assert strategy.endpoint_column == 'endpoint'
        assert strategy.score_column == 'toxicity_score'
        assert strategy.category_column == 'super_category'

    def test_initialization_full_config(self):
        """Test initialization with full configuration."""
        config = get_full_config()
        strategy = FacetedHeatmapStrategy(config)

        assert strategy.compound_column == 'compoundname'
        assert strategy.endpoint_column == 'endpoint'
        assert strategy.score_column == 'toxicity_score'
        assert strategy.category_column == 'super_category'
        assert len(strategy.category_order) == 5

    def test_initialization_uses_defaults(self):
        """Test that default values are used when not configured."""
        config = get_minimal_config()
        strategy = FacetedHeatmapStrategy(config)

        assert strategy.category_order == strategy.DEFAULT_CATEGORY_ORDER

    def test_initialization_custom_columns(self):
        """Test initialization with custom column names."""
        config = get_minimal_config()
        config['visualization']['plotly'] = {
            'compound_column': 'chem_name',
            'endpoint_column': 'test_type',
            'score_column': 'result',
            'category_column': 'group'
        }
        strategy = FacetedHeatmapStrategy(config)

        assert strategy.compound_column == 'chem_name'
        assert strategy.endpoint_column == 'test_type'
        assert strategy.score_column == 'result'
        assert strategy.category_column == 'group'


# ============================================================================
# DATA VALIDATION TESTS
# ============================================================================

class TestDataValidation:
    """Test validate_data() method."""

    def test_validate_empty_dataframe_fails(self):
        """Test that empty DataFrame raises ValueError."""
        config = get_minimal_config()
        strategy = FacetedHeatmapStrategy(config)
        df = pd.DataFrame()

        with pytest.raises(ValueError, match="Input DataFrame is empty"):
            strategy.validate_data(df)

    def test_validate_missing_compound_column(self):
        """Test that missing compound column raises ValueError."""
        config = get_minimal_config()
        strategy = FacetedHeatmapStrategy(config)
        df = pd.DataFrame({
            'endpoint': ['NR_AR'],
            'toxicity_score': [0.5],
            'super_category': ['Nuclear Response']
        })

        with pytest.raises(ValueError, match="Missing required columns"):
            strategy.validate_data(df)

    def test_validate_missing_endpoint_column(self):
        """Test that missing endpoint column raises ValueError."""
        config = get_minimal_config()
        strategy = FacetedHeatmapStrategy(config)
        df = pd.DataFrame({
            'compoundname': ['Compound_A'],
            'toxicity_score': [0.5],
            'super_category': ['Nuclear Response']
        })

        with pytest.raises(ValueError, match="Missing required columns"):
            strategy.validate_data(df)

    def test_validate_missing_score_column(self):
        """Test that missing score column raises ValueError."""
        config = get_minimal_config()
        strategy = FacetedHeatmapStrategy(config)
        df = pd.DataFrame({
            'compoundname': ['Compound_A'],
            'endpoint': ['NR_AR'],
            'super_category': ['Nuclear Response']
        })

        with pytest.raises(ValueError, match="Missing required columns"):
            strategy.validate_data(df)

    def test_validate_missing_category_column(self):
        """Test that missing category column raises ValueError."""
        config = get_minimal_config()
        strategy = FacetedHeatmapStrategy(config)
        df = pd.DataFrame({
            'compoundname': ['Compound_A'],
            'endpoint': ['NR_AR'],
            'toxicity_score': [0.5]
        })

        with pytest.raises(ValueError, match="Missing required columns"):
            strategy.validate_data(df)

    def test_validate_all_nulls_fails(self):
        """Test that all null values raises ValueError."""
        config = get_minimal_config()
        strategy = FacetedHeatmapStrategy(config)
        df = pd.DataFrame({
            'compoundname': [None, None],
            'endpoint': [None, None],
            'toxicity_score': [None, None],
            'super_category': [None, None]
        })

        with pytest.raises(ValueError, match="No valid data after removing nulls"):
            strategy.validate_data(df)

    def test_validate_non_numeric_scores(self):
        """Test that non-numeric scores raise ValueError."""
        config = get_minimal_config()
        strategy = FacetedHeatmapStrategy(config)
        df = pd.DataFrame({
            'compoundname': ['Compound_A'],
            'endpoint': ['NR_AR'],
            'toxicity_score': ['high'],
            'super_category': ['Nuclear Response']
        })

        with pytest.raises(ValueError, match="must be numeric"):
            strategy.validate_data(df)

    def test_validate_success(self):
        """Test successful validation."""
        config = get_minimal_config()
        strategy = FacetedHeatmapStrategy(config)
        df = get_sample_data()

        # Should not raise
        strategy.validate_data(df)


# ============================================================================
# DATA PROCESSING TESTS
# ============================================================================

class TestDataProcessing:
    """Test process_data() method."""

    def test_process_data_removes_nulls(self):
        """Test that null values are removed."""
        config = get_minimal_config()
        strategy = FacetedHeatmapStrategy(config)

        df = pd.DataFrame({
            'compoundname': ['A', 'B', None, 'D'],
            'endpoint': ['NR_AR', None, 'NR_ER', 'SR_MMP'],
            'toxicity_score': [0.5, 0.6, 0.7, None],
            'super_category': ['Nuclear Response'] * 4
        })

        result = strategy.process_data(df)

        # Only first row is fully valid
        assert len(result) == 1

    def test_process_data_converts_score_to_numeric(self):
        """Test that scores are converted to numeric."""
        config = get_minimal_config()
        strategy = FacetedHeatmapStrategy(config)

        df = pd.DataFrame({
            'compoundname': ['A', 'B'],
            'endpoint': ['NR_AR', 'NR_ER'],
            'toxicity_score': ['0.5', '0.6'],  # String values
            'super_category': ['Nuclear Response'] * 2
        })

        result = strategy.process_data(df)

        assert pd.api.types.is_numeric_dtype(result['toxicity_score'])

    def test_process_data_aggregates_duplicates(self):
        """Test that duplicate entries are aggregated."""
        config = get_minimal_config()
        strategy = FacetedHeatmapStrategy(config)

        df = pd.DataFrame({
            'compoundname': ['A', 'A', 'A'],
            'endpoint': ['NR_AR', 'NR_AR', 'NR_AR'],
            'toxicity_score': [0.3, 0.5, 0.7],
            'super_category': ['Nuclear Response'] * 3
        })

        result = strategy.process_data(df)

        # Should aggregate to single row with mean
        assert len(result) == 1
        assert abs(result['toxicity_score'].values[0] - 0.5) < 0.01

    def test_process_data_preserves_all_combinations(self):
        """Test that all compound-endpoint combinations are preserved."""
        config = get_minimal_config()
        strategy = FacetedHeatmapStrategy(config)
        df = get_sample_data()

        result = strategy.process_data(df)

        # 3 compounds × 6 endpoints (2 per category × 3 categories)
        assert len(result) == 18


# ============================================================================
# FIGURE CREATION TESTS
# ============================================================================

class TestFigureCreation:
    """Test create_figure() method."""

    def test_create_figure_returns_figure(self):
        """Test that create_figure returns a Plotly Figure."""
        config = get_full_config()
        strategy = FacetedHeatmapStrategy(config)
        df = get_sample_data()

        processed = strategy.process_data(df)
        fig = strategy.create_figure(processed)

        assert isinstance(fig, go.Figure)

    def test_create_figure_has_correct_number_of_facets(self):
        """Test that figure has correct number of subplots."""
        config = get_full_config()
        strategy = FacetedHeatmapStrategy(config)
        df = get_sample_data()

        processed = strategy.process_data(df)
        fig = strategy.create_figure(processed)

        # Should have 3 traces (one per category)
        assert len(fig.data) == 3

    def test_create_figure_applies_colorscale(self):
        """Test that colorscale is applied to heatmaps."""
        config = get_full_config()
        strategy = FacetedHeatmapStrategy(config)
        df = get_sample_data()

        processed = strategy.process_data(df)
        fig = strategy.create_figure(processed)

        # Colorscale is expanded to tuples, just check it's not None
        assert fig.data[0].colorscale is not None
        assert len(fig.data[0].colorscale) > 0

    def test_create_figure_sets_z_range(self):
        """Test that z-axis range is set to 0-1."""
        config = get_full_config()
        strategy = FacetedHeatmapStrategy(config)
        df = get_sample_data()

        processed = strategy.process_data(df)
        fig = strategy.create_figure(processed)

        for trace in fig.data:
            assert trace.zmin == 0
            assert trace.zmax == 1

    def test_create_figure_shows_colorbar_on_last_facet(self):
        """Test that colorbar only appears on last facet."""
        config = get_full_config()
        strategy = FacetedHeatmapStrategy(config)
        df = get_sample_data()

        processed = strategy.process_data(df)
        fig = strategy.create_figure(processed)

        # First facets should not show colorbar
        assert fig.data[0].showscale is False
        assert fig.data[1].showscale is False
        # Last facet should show colorbar
        assert fig.data[2].showscale is True

    def test_create_figure_applies_title(self):
        """Test that title is applied."""
        config = get_full_config()
        strategy = FacetedHeatmapStrategy(config)
        df = get_sample_data()

        processed = strategy.process_data(df)
        fig = strategy.create_figure(processed)

        assert 'Faceted Heatmap' in fig.layout.title.text

    def test_create_figure_applies_layout_config(self):
        """Test that layout configuration is applied."""
        config = get_full_config()
        strategy = FacetedHeatmapStrategy(config)
        df = get_sample_data()

        processed = strategy.process_data(df)
        fig = strategy.create_figure(processed)

        assert fig.layout.height == 800
        assert fig.layout.width == 1200

    def test_create_figure_with_minimal_config(self):
        """Test figure creation with minimal config."""
        config = get_minimal_config()
        strategy = FacetedHeatmapStrategy(config)
        df = get_sample_data()

        processed = strategy.process_data(df)
        fig = strategy.create_figure(processed)

        assert isinstance(fig, go.Figure)

    def test_create_figure_respects_category_order(self):
        """Test that facets follow specified category order."""
        config = get_full_config()
        strategy = FacetedHeatmapStrategy(config)
        df = get_sample_data()

        processed = strategy.process_data(df)
        fig = strategy.create_figure(processed)

        # Check subplot titles match category order
        # Note: subplot_titles are in annotations
        annotations = [a.text for a in fig.layout.annotations
                      if hasattr(a, 'text')]
        assert 'Nuclear Response' in annotations
        assert 'Stress Response' in annotations
        assert 'Genomic' in annotations

    def test_create_figure_no_categories_fails(self):
        """Test that no categories raises ValueError."""
        config = get_minimal_config()
        strategy = FacetedHeatmapStrategy(config)

        # Empty dataframe with correct columns
        df = pd.DataFrame({
            'compoundname': [],
            'endpoint': [],
            'toxicity_score': [],
            'super_category': []
        })

        with pytest.raises(ValueError, match="No categories found"):
            strategy.create_figure(df)

    def test_create_figure_with_autosize(self):
        """Test figure with autosize enabled."""
        config = get_full_config()
        config['visualization']['plotly']['layout']['autosize'] = True
        strategy = FacetedHeatmapStrategy(config)
        df = get_sample_data()

        processed = strategy.process_data(df)
        fig = strategy.create_figure(processed)

        assert fig.layout.autosize is True


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

class TestIntegration:
    """Test complete workflow."""

    def test_generate_plot_complete_workflow(self):
        """Test complete generate_plot workflow."""
        config = get_full_config()
        strategy = FacetedHeatmapStrategy(config)
        df = get_sample_data()

        fig = strategy.generate_plot(df)

        assert isinstance(fig, go.Figure)
        assert len(fig.data) == 3

    def test_workflow_with_validation(self):
        """Test workflow with explicit validation."""
        config = get_full_config()
        strategy = FacetedHeatmapStrategy(config)
        df = get_sample_data()

        strategy.validate_data(df)
        processed = strategy.process_data(df)
        fig = strategy.create_figure(processed)

        assert isinstance(fig, go.Figure)

    def test_workflow_minimal_config(self):
        """Test workflow with minimal configuration."""
        config = get_minimal_config()
        strategy = FacetedHeatmapStrategy(config)
        df = get_sample_data()

        fig = strategy.generate_plot(df)

        assert isinstance(fig, go.Figure)


# ============================================================================
# EDGE CASES
# ============================================================================

class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_single_compound(self):
        """Test with single compound."""
        config = get_minimal_config()
        strategy = FacetedHeatmapStrategy(config)

        df = pd.DataFrame({
            'compoundname': ['Compound_A'] * 6,
            'endpoint': ['NR_AR', 'NR_ER', 'SR_MMP', 'SR_ATAD5', 'GN_P53', 'GN_BRCA1'],
            'toxicity_score': [0.1, 0.2, 0.3, 0.4, 0.5, 0.6],
            'super_category': ['Nuclear Response'] * 2 + ['Stress Response'] * 2 + ['Genomic'] * 2
        })

        fig = strategy.generate_plot(df)

        assert isinstance(fig, go.Figure)

    def test_single_category(self):
        """Test with single category."""
        config = get_minimal_config()
        strategy = FacetedHeatmapStrategy(config)

        df = pd.DataFrame({
            'compoundname': ['A', 'B', 'C'],
            'endpoint': ['NR_AR', 'NR_ER', 'NR_AR'],
            'toxicity_score': [0.1, 0.2, 0.3],
            'super_category': ['Nuclear Response'] * 3
        })

        fig = strategy.generate_plot(df)

        assert isinstance(fig, go.Figure)
        assert len(fig.data) == 1  # Single facet

    def test_many_categories(self):
        """Test with all 5 default categories."""
        config = get_full_config()
        strategy = FacetedHeatmapStrategy(config)

        categories = [
            'Nuclear Response', 'Stress Response', 'Genomic',
            'Environmental', 'Organic'
        ]

        data = []
        for i, cat in enumerate(categories):
            data.append({
                'compoundname': 'Compound_A',
                'endpoint': f'EP_{i}',
                'toxicity_score': 0.5,
                'super_category': cat
            })

        df = pd.DataFrame(data)
        fig = strategy.generate_plot(df)

        assert isinstance(fig, go.Figure)
        assert len(fig.data) == 5  # 5 facets

    def test_extreme_score_values(self):
        """Test with extreme toxicity scores."""
        config = get_minimal_config()
        strategy = FacetedHeatmapStrategy(config)

        df = pd.DataFrame({
            'compoundname': ['A', 'B', 'C'],
            'endpoint': ['NR_AR'] * 3,
            'toxicity_score': [0.0, 1.0, 0.5],
            'super_category': ['Nuclear Response'] * 3
        })

        fig = strategy.generate_plot(df)

        assert isinstance(fig, go.Figure)

    def test_many_compounds(self):
        """Test with many compounds."""
        config = get_minimal_config()
        strategy = FacetedHeatmapStrategy(config)

        compounds = [f'Compound_{i}' for i in range(20)]
        data = []
        for compound in compounds:
            data.append({
                'compoundname': compound,
                'endpoint': 'NR_AR',
                'toxicity_score': np.random.rand(),
                'super_category': 'Nuclear Response'
            })

        df = pd.DataFrame(data)
        fig = strategy.generate_plot(df)

        assert isinstance(fig, go.Figure)

    def test_many_endpoints(self):
        """Test with many endpoints per category."""
        config = get_minimal_config()
        strategy = FacetedHeatmapStrategy(config)

        endpoints = [f'EP_{i}' for i in range(15)]
        data = []
        for endpoint in endpoints:
            data.append({
                'compoundname': 'Compound_A',
                'endpoint': endpoint,
                'toxicity_score': np.random.rand(),
                'super_category': 'Nuclear Response'
            })

        df = pd.DataFrame(data)
        fig = strategy.generate_plot(df)

        assert isinstance(fig, go.Figure)

    def test_unbalanced_categories(self):
        """Test with unbalanced data across categories."""
        config = get_minimal_config()
        strategy = FacetedHeatmapStrategy(config)

        df = pd.DataFrame({
            'compoundname': ['A', 'A', 'B', 'B', 'B', 'B'],
            'endpoint': ['NR_AR', 'NR_ER', 'SR_MMP', 'SR_ATAD5', 'GN_P53', 'GN_BRCA1'],
            'toxicity_score': [0.1, 0.2, 0.3, 0.4, 0.5, 0.6],
            'super_category': ['Nuclear Response'] * 2 + ['Stress Response'] * 2 + ['Genomic'] * 2
        })

        fig = strategy.generate_plot(df)

        assert isinstance(fig, go.Figure)

    def test_custom_category_order(self):
        """Test with custom category order."""
        config = get_minimal_config()
        config['visualization']['plotly']['category_order'] = [
            'Genomic', 'Nuclear Response', 'Stress Response'
        ]
        strategy = FacetedHeatmapStrategy(config)

        df = pd.DataFrame({
            'compoundname': ['A'] * 3,
            'endpoint': ['EP1', 'EP2', 'EP3'],
            'toxicity_score': [0.1, 0.2, 0.3],
            'super_category': ['Nuclear Response', 'Stress Response', 'Genomic']
        })

        processed = strategy.process_data(df)
        fig = strategy.create_figure(processed)

        # First annotation should be 'Genomic' (custom order)
        annotations = [a.text for a in fig.layout.annotations
                      if hasattr(a, 'text')]
        assert annotations[0] == 'Genomic'

    def test_category_not_in_default_order(self):
        """Test with category not in default order."""
        config = get_minimal_config()
        strategy = FacetedHeatmapStrategy(config)

        df = pd.DataFrame({
            'compoundname': ['A', 'B'],
            'endpoint': ['EP1', 'EP2'],
            'toxicity_score': [0.1, 0.2],
            'super_category': ['Custom Category', 'Custom Category']
        })

        fig = strategy.generate_plot(df)

        assert isinstance(fig, go.Figure)
        assert len(fig.data) == 1

    def test_mixed_score_types_coerced(self):
        """Test that mixed score types are coerced to numeric."""
        config = get_minimal_config()
        strategy = FacetedHeatmapStrategy(config)

        df = pd.DataFrame({
            'compoundname': ['A', 'B', 'C'],
            'endpoint': ['NR_AR'] * 3,
            'toxicity_score': [0.5, '0.6', 0.7],  # Mixed types
            'super_category': ['Nuclear Response'] * 3
        })

        processed = strategy.process_data(df)

        assert pd.api.types.is_numeric_dtype(processed['toxicity_score'])
        assert len(processed) == 3
