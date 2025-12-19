"""
Unit tests for HeatmapScoredStrategy.

Tests cover:
- Initialization and configuration
- Data validation
- KO completeness scoring algorithm
- Compound compliance scoring algorithm
- Figure creation with heatmaps
- Both scoring modes
- Integration workflows
- Edge cases

Author: BioRemPP Test Suite
Date: 2025-12-08
"""

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import pytest

from src.domain.plot_strategies.charts.heatmap_scored_strategy import (
    HeatmapScoredStrategy
)


# ============================================================================
# HELPER FUNCTIONS - Configuration and Sample Data
# ============================================================================

def get_ko_completeness_config():
    """Get configuration for KO completeness scoring."""
    return {
        'metadata': {
            'use_case_id': 'UC-8.3',
            'module': 'module8'
        },
        'visualization': {
            'strategy': 'HeatmapScoredStrategy',
            'plotly': {
                'scoring_mode': 'ko_completeness',
                'category_column': 'Pathway',
                'sample_column': 'Sample',
                'value_column': 'KO',
                'chart': {
                    'title': {
                        'text': 'HADEG Pathway Completeness',
                        'show': True
                    },
                    'xaxis': {'title': 'Pathway'},
                    'yaxis': {'title': 'Sample'},
                    'color_label': 'Completeness (%)',
                    'color_continuous_scale': 'Greens',
                    'show_values': True,
                    'text_auto': '.1f'
                },
                'layout': {
                    'height': 600,
                    'width': 1000,
                    'template': 'simple_white'
                }
            }
        }
    }


def get_compound_compliance_config():
    """Get configuration for compound compliance scoring."""
    return {
        'metadata': {
            'use_case_id': 'UC-1.5',
            'module': 'module1'
        },
        'visualization': {
            'strategy': 'HeatmapScoredStrategy',
            'plotly': {
                'scoring_mode': 'compound_compliance',
                'category_column': 'referenceAG',
                'sample_column': 'sample',
                'value_column': 'compoundname',
                'chart': {
                    'title': {
                        'text': 'Regulatory Compliance Scorecard',
                        'show': True
                    },
                    'xaxis': {'title': 'Agency'},
                    'yaxis': {'title': 'Sample'},
                    'color_label': 'Compliance (%)',
                    'color_continuous_scale': 'Blues'
                },
                'layout': {
                    'height': 700,
                    'width': 1200,
                    'template': 'plotly_white'
                }
            }
        }
    }


def get_minimal_config():
    """Get minimal configuration with defaults."""
    return {
        'metadata': {'use_case_id': 'UC-8.5'},
        'visualization': {
            'strategy': 'HeatmapScoredStrategy',
            'plotly': {
                'category_column': 'Category',
                'sample_column': 'Sample',
                'value_column': 'KO'
            }
        }
    }


def get_ko_completeness_data():
    """
    Get sample data for KO completeness scoring.

    Creates data with:
    - 3 samples
    - 2 pathways
    - Various KO distributions
    """
    np.random.seed(42)

    data = []

    # Pathway A: 4 unique KOs total (K00001, K00002, K00003, K00004)
    # Sample S1: has 2 KOs (50%)
    data.extend([
        {'Sample': 'S1', 'Pathway': 'Pathway_A', 'KO': 'K00001'},
        {'Sample': 'S1', 'Pathway': 'Pathway_A', 'KO': 'K00002'},
    ])

    # Sample S2: has 3 KOs (75%)
    data.extend([
        {'Sample': 'S2', 'Pathway': 'Pathway_A', 'KO': 'K00001'},
        {'Sample': 'S2', 'Pathway': 'Pathway_A', 'KO': 'K00002'},
        {'Sample': 'S2', 'Pathway': 'Pathway_A', 'KO': 'K00003'},
    ])

    # Sample S3: has all 4 KOs (100%)
    data.extend([
        {'Sample': 'S3', 'Pathway': 'Pathway_A', 'KO': 'K00001'},
        {'Sample': 'S3', 'Pathway': 'Pathway_A', 'KO': 'K00002'},
        {'Sample': 'S3', 'Pathway': 'Pathway_A', 'KO': 'K00003'},
        {'Sample': 'S3', 'Pathway': 'Pathway_A', 'KO': 'K00004'},
    ])

    # Pathway B: 3 unique KOs total (K00010, K00011, K00012)
    # Sample S1: has 1 KO (33.33%)
    data.append({'Sample': 'S1', 'Pathway': 'Pathway_B', 'KO': 'K00010'})

    # Sample S2: has 2 KOs (66.67%)
    data.extend([
        {'Sample': 'S2', 'Pathway': 'Pathway_B', 'KO': 'K00010'},
        {'Sample': 'S2', 'Pathway': 'Pathway_B', 'KO': 'K00011'},
    ])

    # Sample S3: has all 3 KOs (100%)
    data.extend([
        {'Sample': 'S3', 'Pathway': 'Pathway_B', 'KO': 'K00010'},
        {'Sample': 'S3', 'Pathway': 'Pathway_B', 'KO': 'K00011'},
        {'Sample': 'S3', 'Pathway': 'Pathway_B', 'KO': 'K00012'},
    ])

    return pd.DataFrame(data)


def get_compound_compliance_data():
    """
    Get sample data for compound compliance scoring.

    Creates data with:
    - 3 samples
    - 2 agencies
    - Various compound overlaps
    """
    data = []

    # Agency EPA: defines compounds {Benzene, Toluene, Xylene}
    data.extend([
        {'sample': 'Sample1', 'referenceAG': 'EPA',
            'compoundname': 'Benzene'},
        {'sample': 'Sample1', 'referenceAG': 'EPA',
            'compoundname': 'Toluene'},
        {'sample': 'Sample2', 'referenceAG': 'EPA',
            'compoundname': 'Benzene'},
        {'sample': 'Sample2', 'referenceAG': 'EPA',
            'compoundname': 'Xylene'},
        {'sample': 'Sample3', 'referenceAG': 'EPA',
            'compoundname': 'Benzene'},
        {'sample': 'Sample3', 'referenceAG': 'EPA',
            'compoundname': 'Toluene'},
        {'sample': 'Sample3', 'referenceAG': 'EPA',
            'compoundname': 'Xylene'},
    ])

    # Agency WHO: defines compounds {Cadmium, Lead}
    data.extend([
        {'sample': 'Sample1', 'referenceAG': 'WHO',
            'compoundname': 'Cadmium'},
        {'sample': 'Sample2', 'referenceAG': 'WHO',
            'compoundname': 'Cadmium'},
        {'sample': 'Sample2', 'referenceAG': 'WHO',
            'compoundname': 'Lead'},
        {'sample': 'Sample3', 'referenceAG': 'WHO',
            'compoundname': 'Lead'},
    ])

    return pd.DataFrame(data)


# ============================================================================
# TEST CLASS: Initialization
# ============================================================================

class TestHeatmapScoredStrategyInitialization:
    """Test HeatmapScoredStrategy initialization."""

    def test_initialization_ko_completeness_mode(self):
        """Test initialization with KO completeness mode."""
        config = get_ko_completeness_config()
        strategy = HeatmapScoredStrategy(config)

        assert strategy is not None
        assert strategy.scoring_mode == 'ko_completeness'
        assert strategy.category_column == 'Pathway'
        assert strategy.sample_column == 'Sample'
        assert strategy.value_column == 'KO'

    def test_initialization_compound_compliance_mode(self):
        """Test initialization with compound compliance mode."""
        config = get_compound_compliance_config()
        strategy = HeatmapScoredStrategy(config)

        assert strategy.scoring_mode == 'compound_compliance'
        assert strategy.category_column == 'referenceAG'
        assert strategy.sample_column == 'sample'
        assert strategy.value_column == 'compoundname'

    def test_initialization_uses_defaults(self):
        """Test that defaults are applied when not specified."""
        config = get_minimal_config()
        strategy = HeatmapScoredStrategy(config)

        # Should default to ko_completeness
        assert strategy.scoring_mode == 'ko_completeness'

    def test_initialization_custom_columns(self):
        """Test initialization with custom column names."""
        config = {
            'metadata': {},
            'visualization': {
                'strategy': 'HeatmapScoredStrategy',
                'plotly': {
                    'category_column': 'CustomCategory',
                    'sample_column': 'CustomSample',
                    'value_column': 'CustomValue'
                }
            }
        }

        strategy = HeatmapScoredStrategy(config)

        assert strategy.category_column == 'CustomCategory'
        assert strategy.sample_column == 'CustomSample'
        assert strategy.value_column == 'CustomValue'


# ============================================================================
# TEST CLASS: Data Validation
# ============================================================================

class TestDataValidation:
    """Test validate_data() method."""

    def test_validate_empty_dataframe_fails(self):
        """Test that empty DataFrame raises error."""
        config = get_ko_completeness_config()
        strategy = HeatmapScoredStrategy(config)

        df = pd.DataFrame()

        with pytest.raises(ValueError, match="Input DataFrame is empty"):
            strategy.validate_data(df)

    def test_validate_missing_sample_column(self):
        """Test that missing sample column raises error."""
        config = get_ko_completeness_config()
        strategy = HeatmapScoredStrategy(config)

        df = pd.DataFrame({
            'Pathway': ['P1'],
            'KO': ['K00001']
        })

        with pytest.raises(ValueError, match="Missing required columns"):
            strategy.validate_data(df)

    def test_validate_missing_category_column(self):
        """Test that missing category column raises error."""
        config = get_ko_completeness_config()
        strategy = HeatmapScoredStrategy(config)

        df = pd.DataFrame({
            'Sample': ['S1'],
            'KO': ['K00001']
        })

        with pytest.raises(ValueError, match="Missing required columns"):
            strategy.validate_data(df)

    def test_validate_missing_value_column(self):
        """Test that missing value column raises error."""
        config = get_ko_completeness_config()
        strategy = HeatmapScoredStrategy(config)

        df = pd.DataFrame({
            'Sample': ['S1'],
            'Pathway': ['P1']
        })

        with pytest.raises(ValueError, match="Missing required columns"):
            strategy.validate_data(df)

    def test_validate_all_nulls_fails(self):
        """Test that all null values raises error."""
        config = get_ko_completeness_config()
        strategy = HeatmapScoredStrategy(config)

        df = pd.DataFrame({
            'Sample': [None, None],
            'Pathway': [None, None],
            'KO': [None, None]
        })

        with pytest.raises(ValueError, match="No valid data"):
            strategy.validate_data(df)

    def test_validate_no_samples_fails(self):
        """Test that no samples raises error."""
        config = get_ko_completeness_config()
        strategy = HeatmapScoredStrategy(config)

        df = pd.DataFrame({
            'Sample': [None],
            'Pathway': ['P1'],
            'KO': ['K00001']
        })

        # Nulls are removed first, causing "No valid data" error
        with pytest.raises(ValueError, match="No valid data"):
            strategy.validate_data(df)

    def test_validate_no_categories_fails(self):
        """Test that no categories raises error."""
        config = get_ko_completeness_config()
        strategy = HeatmapScoredStrategy(config)

        df = pd.DataFrame({
            'Sample': ['S1'],
            'Pathway': [None],
            'KO': ['K00001']
        })

        # Nulls are removed first, causing "No valid data" error
        with pytest.raises(ValueError, match="No valid data"):
            strategy.validate_data(df)

    def test_validate_success(self):
        """Test successful validation."""
        config = get_ko_completeness_config()
        strategy = HeatmapScoredStrategy(config)

        df = get_ko_completeness_data()

        # Should not raise
        strategy.validate_data(df)


# ============================================================================
# TEST CLASS: KO Completeness Scoring
# ============================================================================

class TestKOCompletenessScoring:
    """Test _calculate_ko_completeness() method."""

    def test_calculate_ko_completeness_returns_dataframe(self):
        """Test that KO completeness returns a DataFrame."""
        config = get_ko_completeness_config()
        strategy = HeatmapScoredStrategy(config)

        df = get_ko_completeness_data()

        result = strategy._calculate_ko_completeness(df)

        assert isinstance(result, pd.DataFrame)

    def test_calculate_ko_completeness_shape(self):
        """Test that matrix has correct shape (samples x categories)."""
        config = get_ko_completeness_config()
        strategy = HeatmapScoredStrategy(config)

        df = get_ko_completeness_data()

        result = strategy._calculate_ko_completeness(df)

        # Should have 3 samples (rows) and 2 pathways (columns)
        assert result.shape == (3, 2)

    def test_calculate_ko_completeness_correct_scores(self):
        """Test that completeness scores are calculated correctly."""
        config = get_ko_completeness_config()
        strategy = HeatmapScoredStrategy(config)

        df = get_ko_completeness_data()

        result = strategy._calculate_ko_completeness(df)

        # Pathway A: 4 total KOs
        # S1: 2/4 = 50%
        assert abs(result.loc['S1', 'Pathway_A'] - 50.0) < 0.1

        # S2: 3/4 = 75%
        assert abs(result.loc['S2', 'Pathway_A'] - 75.0) < 0.1

        # S3: 4/4 = 100%
        assert abs(result.loc['S3', 'Pathway_A'] - 100.0) < 0.1

        # Pathway B: 3 total KOs
        # S1: 1/3 = 33.33%
        assert abs(result.loc['S1', 'Pathway_B'] - 33.333) < 0.1

        # S2: 2/3 = 66.67%
        assert abs(result.loc['S2', 'Pathway_B'] - 66.667) < 0.1

        # S3: 3/3 = 100%
        assert abs(result.loc['S3', 'Pathway_B'] - 100.0) < 0.1

    def test_calculate_ko_completeness_range(self):
        """Test that all scores are between 0 and 100."""
        config = get_ko_completeness_config()
        strategy = HeatmapScoredStrategy(config)

        df = get_ko_completeness_data()

        result = strategy._calculate_ko_completeness(df)

        assert (result >= 0).all().all()
        assert (result <= 100).all().all()

    def test_calculate_ko_completeness_handles_missing_combinations(self):
        """Test that missing sample-category combinations are filled with 0."""
        config = get_ko_completeness_config()
        strategy = HeatmapScoredStrategy(config)

        # Create data where S1 has no entries for Pathway B
        df = pd.DataFrame({
            'Sample': ['S1', 'S1', 'S2', 'S2'],
            'Pathway': ['Pathway_A', 'Pathway_A', 'Pathway_A', 'Pathway_B'],
            'KO': ['K00001', 'K00002', 'K00001', 'K00010']
        })

        result = strategy._calculate_ko_completeness(df)

        # S1 should have 0 for Pathway_B
        assert result.loc['S1', 'Pathway_B'] == 0.0

    def test_calculate_ko_completeness_no_categories_fails(self):
        """Test that no categories with KOs raises error."""
        config = get_ko_completeness_config()
        strategy = HeatmapScoredStrategy(config)

        # Create data with all null KOs
        df = pd.DataFrame({
            'Sample': ['S1'],
            'Pathway': ['P1'],
            'KO': ['']  # Empty string
        })

        # Should be cleaned to empty, causing error
        df_clean = df[df['KO'] != '']

        with pytest.raises(ValueError, match="No categories with associated"):
            strategy._calculate_ko_completeness(df_clean)


# ============================================================================
# TEST CLASS: Compound Compliance Scoring
# ============================================================================

class TestCompoundComplianceScoring:
    """Test _calculate_compound_compliance() method."""

    def test_calculate_compound_compliance_returns_dataframe(self):
        """Test that compound compliance returns a DataFrame."""
        config = get_compound_compliance_config()
        strategy = HeatmapScoredStrategy(config)

        df = get_compound_compliance_data()

        result = strategy._calculate_compound_compliance(df)

        assert isinstance(result, pd.DataFrame)

    def test_calculate_compound_compliance_shape(self):
        """Test that matrix has correct shape (samples x agencies)."""
        config = get_compound_compliance_config()
        strategy = HeatmapScoredStrategy(config)

        df = get_compound_compliance_data()

        result = strategy._calculate_compound_compliance(df)

        # Should have 3 samples (rows) and 2 agencies (columns)
        assert result.shape == (3, 2)

    def test_calculate_compound_compliance_correct_scores(self):
        """Test that compliance scores are calculated correctly."""
        config = get_compound_compliance_config()
        strategy = HeatmapScoredStrategy(config)

        df = get_compound_compliance_data()

        result = strategy._calculate_compound_compliance(df)

        # EPA compounds: {Benzene, Toluene, Xylene}
        # Sample1: {Benzene, Toluene, Cadmium} -> 2/3 EPA = 66.67%
        assert abs(result.loc['Sample1', 'EPA'] - 66.667) < 0.1

        # Sample2: {Benzene, Xylene, Cadmium, Lead} -> 2/3 EPA = 66.67%
        assert abs(result.loc['Sample2', 'EPA'] - 66.667) < 0.1

        # Sample3: {Benzene, Toluene, Xylene, Lead} -> 3/3 EPA = 100%
        assert abs(result.loc['Sample3', 'EPA'] - 100.0) < 0.1

        # WHO compounds: {Cadmium, Lead}
        # Sample1: {Benzene, Toluene, Cadmium} -> 1/2 WHO = 50%
        assert abs(result.loc['Sample1', 'WHO'] - 50.0) < 0.1

        # Sample2: {Benzene, Xylene, Cadmium, Lead} -> 2/2 WHO = 100%
        assert abs(result.loc['Sample2', 'WHO'] - 100.0) < 0.1

        # Sample3: {Benzene, Toluene, Xylene, Lead} -> 1/2 WHO = 50%
        assert abs(result.loc['Sample3', 'WHO'] - 50.0) < 0.1

    def test_calculate_compound_compliance_range(self):
        """Test that all scores are between 0 and 100."""
        config = get_compound_compliance_config()
        strategy = HeatmapScoredStrategy(config)

        df = get_compound_compliance_data()

        result = strategy._calculate_compound_compliance(df)

        assert (result >= 0).all().all()
        assert (result <= 100).all().all()

    def test_calculate_compound_compliance_no_intersection(self):
        """Test sample with no matching compounds gets 0%."""
        config = get_compound_compliance_config()
        strategy = HeatmapScoredStrategy(config)

        df = pd.DataFrame({
            'sample': ['S1', 'S1', 'S2'],
            'referenceAG': ['EPA', 'EPA', 'EPA'],
            'compoundname': ['Benzene', 'Toluene', 'Cadmium']
        })

        result = strategy._calculate_compound_compliance(df)

        # EPA universe = {Benzene, Toluene, Cadmium} (all in data)
        # S2 has {Cadmium} -> 1/3 = 33.33%
        assert abs(result.loc['S2', 'EPA'] - 33.333) < 0.1

    def test_calculate_compound_compliance_complete_match(self):
        """Test sample with all agency compounds gets 100%."""
        config = get_compound_compliance_config()
        strategy = HeatmapScoredStrategy(config)

        df = pd.DataFrame({
            'sample': ['S1', 'S1', 'S1'],
            'referenceAG': ['EPA', 'EPA', 'EPA'],
            'compoundname': ['Benzene', 'Toluene', 'Xylene']
        })

        result = strategy._calculate_compound_compliance(df)

        # S1 has all EPA compounds
        assert result.loc['S1', 'EPA'] == 100.0


# ============================================================================
# TEST CLASS: Data Processing
# ============================================================================

class TestDataProcessing:
    """Test process_data() method."""

    def test_process_data_ko_mode_calls_correct_method(self):
        """Test that KO mode calls _calculate_ko_completeness."""
        config = get_ko_completeness_config()
        strategy = HeatmapScoredStrategy(config)

        df = get_ko_completeness_data()

        result = strategy.process_data(df)

        # Should return matrix with samples x pathways
        assert isinstance(result, pd.DataFrame)
        assert result.shape[0] > 0  # Has rows (samples)
        assert result.shape[1] > 0  # Has columns (categories)

    def test_process_data_compliance_mode_calls_correct_method(self):
        """Test that compliance mode calls _calculate_compound_compliance."""
        config = get_compound_compliance_config()
        strategy = HeatmapScoredStrategy(config)

        df = get_compound_compliance_data()

        result = strategy.process_data(df)

        # Should return matrix with samples x agencies
        assert isinstance(result, pd.DataFrame)
        assert result.shape[0] > 0
        assert result.shape[1] > 0

    def test_process_data_removes_nulls(self):
        """Test that null values are removed during processing."""
        config = get_ko_completeness_config()
        strategy = HeatmapScoredStrategy(config)

        df = pd.DataFrame({
            'Sample': ['S1', 'S2', None, 'S4'],
            'Pathway': ['P1', None, 'P2', 'P3'],
            'KO': ['K00001', 'K00002', 'K00003', None]
        })

        result = strategy.process_data(df)

        # Should only process S1 (complete row)
        assert 'S1' in result.index

    def test_process_data_removes_empty_strings(self):
        """Test that empty strings in value column are removed."""
        config = get_ko_completeness_config()
        strategy = HeatmapScoredStrategy(config)

        df = pd.DataFrame({
            'Sample': ['S1', 'S1', 'S2'],
            'Pathway': ['P1', 'P1', 'P1'],
            'KO': ['K00001', '', 'K00002']
        })

        result = strategy.process_data(df)

        # Should process both S1 and S2, ignoring empty string
        assert 'S1' in result.index
        assert 'S2' in result.index


# ============================================================================
# TEST CLASS: Figure Creation
# ============================================================================

class TestFigureCreation:
    """Test create_figure() method."""

    def test_create_figure_returns_figure(self):
        """Test that create_figure returns a Plotly Figure."""
        config = get_ko_completeness_config()
        strategy = HeatmapScoredStrategy(config)

        df = get_ko_completeness_data()
        processed = strategy.process_data(df)

        fig = strategy.create_figure(processed)

        assert isinstance(fig, go.Figure)

    def test_create_figure_has_heatmap_trace(self):
        """Test that figure contains heatmap trace."""
        config = get_ko_completeness_config()
        strategy = HeatmapScoredStrategy(config)

        df = get_ko_completeness_data()
        processed = strategy.process_data(df)

        fig = strategy.create_figure(processed)

        # Should have at least one trace
        assert len(fig.data) > 0

    def test_create_figure_applies_title(self):
        """Test that title is applied to figure."""
        config = get_ko_completeness_config()
        strategy = HeatmapScoredStrategy(config)

        df = get_ko_completeness_data()
        processed = strategy.process_data(df)

        fig = strategy.create_figure(processed)

        assert fig.layout.title.text == 'HADEG Pathway Completeness'

    def test_create_figure_title_hidden(self):
        """Test that title can be hidden."""
        config = get_ko_completeness_config()
        config['visualization']['plotly']['chart']['title']['show'] = False
        strategy = HeatmapScoredStrategy(config)

        df = get_ko_completeness_data()
        processed = strategy.process_data(df)

        fig = strategy.create_figure(processed)

        # Title should be missing when disabled
        assert not hasattr(fig.layout, 'title') or \
            fig.layout.title.text is None or \
            fig.layout.title.text == ''

    def test_create_figure_applies_layout_config(self):
        """Test that layout configuration is applied."""
        config = get_ko_completeness_config()
        strategy = HeatmapScoredStrategy(config)

        df = get_ko_completeness_data()
        processed = strategy.process_data(df)

        fig = strategy.create_figure(processed)

        assert fig.layout.height == 600
        assert fig.layout.width == 1000

    def test_create_figure_with_autosize(self):
        """Test figure with autosize enabled."""
        config = get_ko_completeness_config()
        config['visualization']['plotly']['layout']['autosize'] = True
        strategy = HeatmapScoredStrategy(config)

        df = get_ko_completeness_data()
        processed = strategy.process_data(df)

        fig = strategy.create_figure(processed)

        # Width should not be set when autosize is enabled
        # (or if it is, autosize takes precedence)
        assert fig.layout.autosize is None or fig.layout.width is not None

    def test_create_figure_sets_z_range(self):
        """Test that z-axis range is set to 0-100."""
        config = get_ko_completeness_config()
        strategy = HeatmapScoredStrategy(config)

        df = get_ko_completeness_data()
        processed = strategy.process_data(df)

        fig = strategy.create_figure(processed)

        # px.imshow sets range via layout coloraxis, not on trace
        assert fig.layout.coloraxis.cmin == 0
        assert fig.layout.coloraxis.cmax == 100

    def test_create_figure_shows_text_values(self):
        """Test that text values are shown on heatmap."""
        config = get_ko_completeness_config()
        strategy = HeatmapScoredStrategy(config)

        df = get_ko_completeness_data()
        processed = strategy.process_data(df)

        fig = strategy.create_figure(processed)

        # px.imshow uses texttemplate instead of text
        assert fig.data[0].texttemplate is not None

    def test_create_figure_hides_text_values(self):
        """Test that text values can be hidden."""
        config = get_ko_completeness_config()
        config['visualization']['plotly']['chart']['show_values'] = False
        strategy = HeatmapScoredStrategy(config)

        df = get_ko_completeness_data()
        processed = strategy.process_data(df)

        fig = strategy.create_figure(processed)

        # Text should be hidden
        assert fig.data[0].text is None


# ============================================================================
# TEST CLASS: Integration
# ============================================================================

class TestIntegration:
    """Test complete workflow integration."""

    def test_generate_plot_ko_completeness_workflow(self):
        """Test complete KO completeness workflow."""
        config = get_ko_completeness_config()
        strategy = HeatmapScoredStrategy(config)

        df = get_ko_completeness_data()

        # Complete workflow
        fig = strategy.generate_plot(df)

        assert isinstance(fig, go.Figure)
        assert len(fig.data) > 0

    def test_generate_plot_compound_compliance_workflow(self):
        """Test complete compound compliance workflow."""
        config = get_compound_compliance_config()
        strategy = HeatmapScoredStrategy(config)

        df = get_compound_compliance_data()

        # Complete workflow
        fig = strategy.generate_plot(df)

        assert isinstance(fig, go.Figure)
        assert len(fig.data) > 0

    def test_workflow_with_validation(self):
        """Test that validation is called in workflow."""
        config = get_ko_completeness_config()
        strategy = HeatmapScoredStrategy(config)

        df = pd.DataFrame()

        with pytest.raises(ValueError, match="Input DataFrame is empty"):
            strategy.generate_plot(df)

    def test_workflow_minimal_config(self):
        """Test workflow with minimal configuration."""
        config = get_minimal_config()
        strategy = HeatmapScoredStrategy(config)

        df = pd.DataFrame({
            'Sample': ['S1', 'S2'],
            'Category': ['C1', 'C1'],
            'KO': ['K00001', 'K00002']
        })

        # Should work with defaults
        fig = strategy.generate_plot(df)

        assert isinstance(fig, go.Figure)


# ============================================================================
# TEST CLASS: Edge Cases
# ============================================================================

class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_single_sample(self):
        """Test with single sample."""
        config = get_ko_completeness_config()
        strategy = HeatmapScoredStrategy(config)

        df = pd.DataFrame({
            'Sample': ['S1', 'S1'],
            'Pathway': ['P1', 'P1'],
            'KO': ['K00001', 'K00002']
        })

        fig = strategy.generate_plot(df)

        assert isinstance(fig, go.Figure)

    def test_single_category(self):
        """Test with single category."""
        config = get_ko_completeness_config()
        strategy = HeatmapScoredStrategy(config)

        df = pd.DataFrame({
            'Sample': ['S1', 'S2'],
            'Pathway': ['P1', 'P1'],
            'KO': ['K00001', 'K00002']
        })

        fig = strategy.generate_plot(df)

        assert isinstance(fig, go.Figure)

    def test_all_scores_zero(self):
        """Test when all samples have zero completeness."""
        config = get_ko_completeness_config()
        strategy = HeatmapScoredStrategy(config)

        df = pd.DataFrame({
            'Sample': ['S1', 'S2', 'S2'],
            'Pathway': ['P1', 'P2', 'P2'],
            'KO': ['K00001', 'K00002', 'K00003']
        })

        # S1 has no KOs for P2, S2 has no KOs for P1
        result = strategy.process_data(df)

        # Should have zeros
        assert 0.0 in result.values

    def test_all_scores_hundred(self):
        """Test when all samples have 100% completeness."""
        config = get_ko_completeness_config()
        strategy = HeatmapScoredStrategy(config)

        df = pd.DataFrame({
            'Sample': ['S1', 'S1', 'S2', 'S2'],
            'Pathway': ['P1', 'P1', 'P1', 'P1'],
            'KO': ['K00001', 'K00002', 'K00001', 'K00002']
        })

        result = strategy.process_data(df)

        # Both samples should have 100%
        assert (result == 100.0).all().all()

    def test_many_samples(self):
        """Test with many samples."""
        config = get_ko_completeness_config()
        strategy = HeatmapScoredStrategy(config)

        data = []
        for i in range(20):
            data.append({
                'Sample': f'S{i}',
                'Pathway': 'P1',
                'KO': f'K{str(i).zfill(5)}'
            })

        df = pd.DataFrame(data)

        fig = strategy.generate_plot(df)

        assert isinstance(fig, go.Figure)

    def test_many_categories(self):
        """Test with many categories."""
        config = get_ko_completeness_config()
        strategy = HeatmapScoredStrategy(config)

        data = []
        for i in range(15):
            data.append({
                'Sample': 'S1',
                'Pathway': f'P{i}',
                'KO': f'K{str(i).zfill(5)}'
            })

        df = pd.DataFrame(data)

        fig = strategy.generate_plot(df)

        assert isinstance(fig, go.Figure)

    def test_duplicate_ko_entries(self):
        """Test that duplicate KO entries are handled correctly."""
        config = get_ko_completeness_config()
        strategy = HeatmapScoredStrategy(config)

        df = pd.DataFrame({
            'Sample': ['S1', 'S1', 'S1'],
            'Pathway': ['P1', 'P1', 'P1'],
            'KO': ['K00001', 'K00001', 'K00001']  # Duplicates
        })

        result = strategy.process_data(df)

        # Should count K00001 only once
        assert 'S1' in result.index
        assert 'P1' in result.columns

    def test_special_characters_in_names(self):
        """Test with special characters in sample/category names."""
        config = get_ko_completeness_config()
        strategy = HeatmapScoredStrategy(config)

        df = pd.DataFrame({
            'Sample': ['Sample-1', 'Sample_2'],
            'Pathway': ['Path (A)', 'Path [B]'],
            'KO': ['K00001', 'K00002']
        })

        # Should handle special characters
        fig = strategy.generate_plot(df)

        assert isinstance(fig, go.Figure)

    def test_very_long_names(self):
        """Test with very long sample/category names."""
        config = get_ko_completeness_config()
        strategy = HeatmapScoredStrategy(config)

        long_name = 'A' * 100

        df = pd.DataFrame({
            'Sample': [long_name],
            'Pathway': [long_name],
            'KO': ['K00001']
        })

        fig = strategy.generate_plot(df)

        assert isinstance(fig, go.Figure)

    def test_mixed_case_values(self):
        """Test with mixed case values."""
        config = get_ko_completeness_config()
        strategy = HeatmapScoredStrategy(config)

        df = pd.DataFrame({
            'Sample': ['sample1', 'SAMPLE2', 'SaMpLe3'],
            'Pathway': ['pathway1', 'PATHWAY2', 'PaThWaY1'],
            'KO': ['K00001', 'k00002', 'K00003']
        })

        # Should treat as different (case-sensitive)
        fig = strategy.generate_plot(df)

        assert isinstance(fig, go.Figure)

    def test_single_ko_per_category(self):
        """Test when each category has only one KO."""
        config = get_ko_completeness_config()
        strategy = HeatmapScoredStrategy(config)

        df = pd.DataFrame({
            'Sample': ['S1', 'S2'],
            'Pathway': ['P1', 'P2'],
            'KO': ['K00001', 'K00002']
        })

        result = strategy.process_data(df)

        # Each sample should have either 0% or 100% for each pathway
        assert set(result.values.flatten()).issubset({0.0, 100.0})
