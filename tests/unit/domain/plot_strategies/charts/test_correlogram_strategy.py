"""
Unit tests for CorrelogramStrategy.

This module tests the CorrelogramStrategy concrete implementation,
which generates correlogram (correlation heatmap) visualizations
for sample similarity or feature co-occurrence analysis.

Test Categories:
- Initialization: Test strategy setup with different modes
- Data Validation: Test validate_data() with various scenarios
- Data Processing: Test correlation matrix computation
- Figure Creation: Test correlogram heatmap generation
- Mode Switching: Test sample vs feature correlation modes
- Integration: Test complete workflow
- Edge Cases: Test boundary conditions
"""

import pytest
import pandas as pd
import numpy as np
import plotly.graph_objects as go

from src.domain.plot_strategies.charts.correlogram_strategy import CorrelogramStrategy


# ============================================================================
# TEST CONFIGURATIONS
# ============================================================================

def get_sample_mode_config():
    """Get configuration for sample-sample correlation."""
    return {
        'metadata': {
            'use_case_id': 'UC-3.4',
            'module': 'module3'
        },
        'visualization': {
            'strategy': 'CorrelogramStrategy',
            'plotly': {
                'correlation_mode': 'sample',
                'row_column': 'Sample',
                'col_column': 'KO',
                'correlation_method': 'pearson',
                'chart': {
                    'title': {
                        'text': 'Sample Similarity Correlogram',
                        'show': True
                    },
                    'color_continuous_scale': 'RdBu_r',
                    'color_label': 'Pearson r',
                    'xaxis_tickangle': -45
                },
                'layout': {
                    'height': 600,
                    'width': 600,
                    'template': 'simple_white'
                }
            }
        },
        'data': {},
        'validation': {}
    }


def get_feature_mode_config():
    """Get configuration for feature-feature correlation."""
    return {
        'metadata': {
            'use_case_id': 'UC-3.6',
            'module': 'module3'
        },
        'visualization': {
            'strategy': 'CorrelogramStrategy',
            'plotly': {
                'correlation_mode': 'feature',
                'row_column': 'Sample',
                'col_column': 'Gene_Symbol',
                'correlation_method': 'spearman',
                'chart': {
                    'title': {
                        'text': 'Gene Symbol Co-occurrence',
                        'show': True
                    },
                    'color_continuous_scale': 'Viridis'
                },
                'layout': {
                    'height': 500,
                    'autosize': True
                }
            }
        },
        'data': {},
        'validation': {}
    }


# ============================================================================
# INITIALIZATION TESTS
# ============================================================================

class TestCorrelogramStrategyInitialization:
    """Test CorrelogramStrategy initialization."""

    def test_initialization_sample_mode(self):
        """Test initialization in sample-sample correlation mode."""
        config = get_sample_mode_config()
        strategy = CorrelogramStrategy(config)

        assert strategy.correlation_mode == 'sample'
        assert strategy.row_column == 'Sample'
        assert strategy.col_column == 'KO'
        assert strategy.correlation_method == 'pearson'

    def test_initialization_feature_mode(self):
        """Test initialization in feature-feature correlation mode."""
        config = get_feature_mode_config()
        strategy = CorrelogramStrategy(config)

        assert strategy.correlation_mode == 'feature'
        assert strategy.row_column == 'Sample'
        assert strategy.col_column == 'Gene_Symbol'
        assert strategy.correlation_method == 'spearman'

    def test_initialization_default_values(self):
        """Test initialization with default values."""
        config = {
            'metadata': {},
            'visualization': {'plotly': {}},
            'data': {},
            'validation': {}
        }
        strategy = CorrelogramStrategy(config)

        # Defaults
        assert strategy.correlation_mode == 'sample'
        assert strategy.row_column == 'Sample'
        assert strategy.col_column == 'KO'
        assert strategy.correlation_method == 'pearson'

    def test_initialization_extracts_plotly_config(self):
        """Test that plotly configuration is extracted."""
        config = get_sample_mode_config()
        strategy = CorrelogramStrategy(config)

        assert 'chart' in strategy.plotly_config
        assert 'layout' in strategy.plotly_config


# ============================================================================
# DATA VALIDATION TESTS
# ============================================================================

class TestDataValidation:
    """Test validate_data() method."""

    def test_validate_empty_dataframe_fails(self):
        """Test validation fails with empty DataFrame."""
        config = get_sample_mode_config()
        strategy = CorrelogramStrategy(config)

        df = pd.DataFrame()

        with pytest.raises(ValueError, match="Input DataFrame is empty"):
            strategy.validate_data(df)

    def test_validate_missing_row_column_fails(self):
        """Test validation fails when row column is missing."""
        config = get_sample_mode_config()
        strategy = CorrelogramStrategy(config)

        df = pd.DataFrame({'KO': ['K00001', 'K00002']})  # Missing 'Sample'

        with pytest.raises(ValueError, match="Missing required columns"):
            strategy.validate_data(df)

    def test_validate_missing_col_column_fails(self):
        """Test validation fails when col column is missing."""
        config = get_sample_mode_config()
        strategy = CorrelogramStrategy(config)

        df = pd.DataFrame({'Sample': ['S1', 'S2']})  # Missing 'KO'

        with pytest.raises(ValueError, match="Missing required columns"):
            strategy.validate_data(df)

    def test_validate_all_nulls_fails(self):
        """Test validation fails when all values are null."""
        config = get_sample_mode_config()
        strategy = CorrelogramStrategy(config)

        df = pd.DataFrame({
            'Sample': [None, None],
            'KO': [None, None]
        })

        with pytest.raises(ValueError, match="No valid data after removing nulls"):
            strategy.validate_data(df)

    def test_validate_sample_mode_needs_min_2_samples(self):
        """Test sample mode needs at least 2 unique samples."""
        config = get_sample_mode_config()
        strategy = CorrelogramStrategy(config)

        df = pd.DataFrame({
            'Sample': ['S1', 'S1'],  # Only 1 unique sample
            'KO': ['K00001', 'K00002']
        })

        with pytest.raises(ValueError, match="Need at least 2 unique Sample values"):
            strategy.validate_data(df)

    def test_validate_feature_mode_needs_min_2_features(self):
        """Test feature mode needs at least 2 unique features."""
        config = get_feature_mode_config()
        strategy = CorrelogramStrategy(config)

        df = pd.DataFrame({
            'Sample': ['S1', 'S2'],
            'Gene_Symbol': ['geneA', 'geneA']  # Only 1 unique gene
        })

        with pytest.raises(ValueError, match="Need at least 2 unique Gene_Symbol values"):
            strategy.validate_data(df)

    def test_validate_passes_with_valid_data(self):
        """Test validation passes with valid data."""
        config = get_sample_mode_config()
        strategy = CorrelogramStrategy(config)

        df = pd.DataFrame({
            'Sample': ['S1', 'S1', 'S2', 'S2'],
            'KO': ['K00001', 'K00002', 'K00001', 'K00003']
        })

        strategy.validate_data(df)  # Should not raise


# ============================================================================
# DATA PROCESSING TESTS - SAMPLE MODE
# ============================================================================

class TestDataProcessingSampleMode:
    """Test process_data() in sample-sample correlation mode."""

    def test_process_data_sample_mode_returns_correlation_matrix(self):
        """Test processing returns correlation matrix."""
        config = get_sample_mode_config()
        strategy = CorrelogramStrategy(config)

        df = pd.DataFrame({
            'Sample': ['S1', 'S1', 'S2', 'S2'],
            'KO': ['K00001', 'K00002', 'K00001', 'K00003']
        })

        result = strategy.process_data(df)

        assert isinstance(result, pd.DataFrame)
        assert result.shape[0] == result.shape[1]  # Square matrix
        assert result.shape[0] == 2  # 2 samples

    def test_process_data_sample_mode_correlation_values(self):
        """Test correlation values are in valid range."""
        config = get_sample_mode_config()
        strategy = CorrelogramStrategy(config)

        df = pd.DataFrame({
            'Sample': ['S1', 'S1', 'S2', 'S2'],
            'KO': ['K00001', 'K00002', 'K00001', 'K00003']
        })

        result = strategy.process_data(df)

        # Correlation values should be between -1 and 1
        assert (result >= -1.0).all().all()
        assert (result <= 1.0).all().all()

    def test_process_data_sample_mode_diagonal_is_one(self):
        """Test diagonal values are 1 (self-correlation)."""
        config = get_sample_mode_config()
        strategy = CorrelogramStrategy(config)

        df = pd.DataFrame({
            'Sample': ['S1', 'S1', 'S2', 'S2'],
            'KO': ['K00001', 'K00002', 'K00001', 'K00003']
        })

        result = strategy.process_data(df)

        # Diagonal should be 1 (perfect correlation with self)
        for i in range(len(result)):
            assert abs(result.iloc[i, i] - 1.0) < 0.001

    def test_process_data_sample_mode_symmetric(self):
        """Test correlation matrix is symmetric."""
        config = get_sample_mode_config()
        strategy = CorrelogramStrategy(config)

        df = pd.DataFrame({
            'Sample': ['S1', 'S1', 'S2', 'S2', 'S3', 'S3'],
            'KO': ['K00001', 'K00002', 'K00001', 'K00003', 'K00002', 'K00003']
        })

        result = strategy.process_data(df)

        # Matrix should be symmetric
        assert np.allclose(result.values, result.values.T, atol=1e-10)


# ============================================================================
# DATA PROCESSING TESTS - FEATURE MODE
# ============================================================================

class TestDataProcessingFeatureMode:
    """Test process_data() in feature-feature correlation mode."""

    def test_process_data_feature_mode_returns_correlation_matrix(self):
        """Test processing returns correlation matrix for features."""
        config = get_feature_mode_config()
        strategy = CorrelogramStrategy(config)

        df = pd.DataFrame({
            'Sample': ['S1', 'S1', 'S2', 'S2', 'S3', 'S3'],
            'Gene_Symbol': ['geneA', 'geneB', 'geneB', 'geneC', 'geneA', 'geneC']
        })

        result = strategy.process_data(df)

        assert isinstance(result, pd.DataFrame)
        assert result.shape[0] == result.shape[1]  # Square matrix
        assert result.shape[0] == 3  # 3 genes

    def test_process_data_feature_mode_index_and_columns_match(self):
        """Test that index and columns are identical."""
        config = get_feature_mode_config()
        strategy = CorrelogramStrategy(config)

        df = pd.DataFrame({
            'Sample': ['S1', 'S1', 'S2', 'S2', 'S3', 'S3'],
            'Gene_Symbol': ['geneA', 'geneB', 'geneB', 'geneC', 'geneA', 'geneC']
        })

        result = strategy.process_data(df)

        assert result.index.tolist() == result.columns.tolist()

    def test_process_data_cleans_whitespace(self):
        """Test that whitespace is stripped from data."""
        config = get_sample_mode_config()
        strategy = CorrelogramStrategy(config)

        df = pd.DataFrame({
            'Sample': [' S1 ', 'S1', ' S2', 'S2 '],
            'KO': ['K00001 ', ' K00002', 'K00001', 'K00003']
        })

        result = strategy.process_data(df)

        # Should have 2 samples (S1 and S2 after cleaning)
        assert result.shape[0] == 2

    def test_process_data_removes_empty_strings(self):
        """Test that empty strings are removed."""
        config = get_sample_mode_config()
        strategy = CorrelogramStrategy(config)

        df = pd.DataFrame({
            'Sample': ['S1', '', 'S2', 'S3'],
            'KO': ['K00001', 'K00002', '', 'K00003']
        })

        result = strategy.process_data(df)

        # Should process only valid data
        assert result.shape[0] > 0


# ============================================================================
# FIGURE CREATION TESTS
# ============================================================================

class TestFigureCreation:
    """Test create_figure() method."""

    def test_create_figure_returns_figure(self):
        """Test that create_figure returns a Plotly Figure."""
        config = get_sample_mode_config()
        strategy = CorrelogramStrategy(config)

        # Create simple correlation matrix
        corr_matrix = pd.DataFrame(
            [[1.0, 0.5], [0.5, 1.0]],
            index=['S1', 'S2'],
            columns=['S1', 'S2']
        )

        fig = strategy.create_figure(corr_matrix)

        assert isinstance(fig, go.Figure)

    def test_create_figure_has_heatmap_trace(self):
        """Test figure contains heatmap trace."""
        config = get_sample_mode_config()
        strategy = CorrelogramStrategy(config)

        corr_matrix = pd.DataFrame(
            [[1.0, 0.5], [0.5, 1.0]],
            index=['S1', 'S2'],
            columns=['S1', 'S2']
        )

        fig = strategy.create_figure(corr_matrix)

        assert len(fig.data) > 0
        assert fig.data[0].type == 'heatmap'

    def test_create_figure_applies_title(self):
        """Test that title is applied."""
        config = get_sample_mode_config()
        strategy = CorrelogramStrategy(config)

        corr_matrix = pd.DataFrame(
            [[1.0, 0.5], [0.5, 1.0]],
            index=['S1', 'S2'],
            columns=['S1', 'S2']
        )

        fig = strategy.create_figure(corr_matrix)

        assert fig.layout.title.text == 'Sample Similarity Correlogram'

    def test_create_figure_without_title(self):
        """Test figure without title (show=False)."""
        config = {
            **get_sample_mode_config(),
            'visualization': {
                **get_sample_mode_config()['visualization'],
                'plotly': {
                    **get_sample_mode_config()['visualization']['plotly'],
                    'chart': {
                        'title': {
                            'show': False,
                            'text': 'Should not appear'
                        }
                    }
                }
            }
        }
        strategy = CorrelogramStrategy(config)

        corr_matrix = pd.DataFrame(
            [[1.0, 0.5], [0.5, 1.0]],
            index=['S1', 'S2'],
            columns=['S1', 'S2']
        )

        fig = strategy.create_figure(corr_matrix)

        assert fig.layout.title.text == ''

    def test_create_figure_applies_layout(self):
        """Test that layout configuration is applied."""
        config = get_sample_mode_config()
        strategy = CorrelogramStrategy(config)

        corr_matrix = pd.DataFrame(
            [[1.0]], index=['S1'], columns=['S1']
        )

        fig = strategy.create_figure(corr_matrix)

        assert fig.layout.height == 600
        assert fig.layout.width == 600

    def test_create_figure_with_autosize(self):
        """Test figure with autosize enabled."""
        config = get_feature_mode_config()
        strategy = CorrelogramStrategy(config)

        corr_matrix = pd.DataFrame(
            [[1.0]], index=['geneA'], columns=['geneA']
        )

        fig = strategy.create_figure(corr_matrix)

        assert fig.layout.autosize is True


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

class TestIntegration:
    """Test complete generate_plot() workflow."""

    def test_generate_plot_sample_mode_complete_workflow(self):
        """Test full pipeline for sample-sample correlation."""
        config = get_sample_mode_config()
        strategy = CorrelogramStrategy(config)

        df = pd.DataFrame({
            'Sample': ['S1', 'S1', 'S2', 'S2', 'S3', 'S3'],
            'KO': ['K00001', 'K00002', 'K00001', 'K00003', 'K00002', 'K00003']
        })

        fig = strategy.generate_plot(df)

        assert isinstance(fig, go.Figure)
        assert len(fig.data) > 0

    def test_generate_plot_feature_mode_complete_workflow(self):
        """Test full pipeline for feature-feature correlation."""
        config = get_feature_mode_config()
        strategy = CorrelogramStrategy(config)

        df = pd.DataFrame({
            'Sample': ['S1', 'S1', 'S2', 'S2', 'S3', 'S3'],
            'Gene_Symbol': ['geneA', 'geneB', 'geneA', 'geneC', 'geneB', 'geneC']
        })

        fig = strategy.generate_plot(df)

        assert isinstance(fig, go.Figure)
        assert len(fig.data) > 0

    def test_generate_plot_with_filters(self):
        """Test generate_plot with base class filters."""
        config = get_sample_mode_config()
        strategy = CorrelogramStrategy(config)

        df = pd.DataFrame({
            'Sample': ['S1', 'S1', 'S2', 'S2'],
            'KO': ['K00001', 'K00002', 'K00001', 'K00003']
        })

        # Base class filter application
        fig = strategy.generate_plot(df, filters={})

        assert isinstance(fig, go.Figure)


# ============================================================================
# EDGE CASES
# ============================================================================

class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_process_data_with_single_ko_per_sample(self):
        """Test processing when each sample has only 1 KO."""
        config = get_sample_mode_config()
        strategy = CorrelogramStrategy(config)

        df = pd.DataFrame({
            'Sample': ['S1', 'S2', 'S3'],
            'KO': ['K00001', 'K00002', 'K00003']
        })

        result = strategy.process_data(df)

        assert result.shape[0] == 3

    def test_process_data_with_perfect_correlation(self):
        """Test processing with highly correlated samples."""
        config = get_sample_mode_config()
        strategy = CorrelogramStrategy(config)

        # S1 and S2 have very similar KO profiles
        # Add S3 with different profile to provide variance for correlation calculation
        df = pd.DataFrame({
            'Sample': ['S1', 'S1', 'S1', 'S2', 'S2', 'S2', 'S3', 'S3'],
            'KO': ['K00001', 'K00002', 'K00003', 'K00001', 'K00002', 'K00003', 'K00004', 'K00005']
        })

        result = strategy.process_data(df)

        # S1 and S2 should have correlation = 1 (identical profiles)
        # S1 and S3 should be uncorrelated (different profiles)
        assert abs(result.loc['S1', 'S2'] - 1.0) < 0.001
        assert result.loc['S1', 'S3'] < 0.5  # Lower correlation with different sample

    def test_process_data_with_no_correlation(self):
        """Test processing with no overlapping features."""
        config = get_sample_mode_config()
        strategy = CorrelogramStrategy(config)

        # S1 and S2 have completely different KOs (non-overlapping)
        df = pd.DataFrame({
            'Sample': ['S1', 'S1', 'S2', 'S2'],
            'KO': ['K00001', 'K00002', 'K00003', 'K00004']
        })

        result = strategy.process_data(df)

        # S1 and S2 should have correlation = -1 (perfectly anti-correlated in binary matrix)
        # When one has 1, the other has 0, and vice versa
        assert abs(result.loc['S1', 'S2'] + 1.0) < 0.001

    def test_create_figure_with_large_matrix(self):
        """Test creating figure from large correlation matrix."""
        config = get_sample_mode_config()
        strategy = CorrelogramStrategy(config)

        # Create 50x50 correlation matrix
        n = 50
        corr_matrix = pd.DataFrame(
            np.random.rand(n, n),
            index=[f'S{i}' for i in range(n)],
            columns=[f'S{i}' for i in range(n)]
        )

        fig = strategy.create_figure(corr_matrix)

        assert isinstance(fig, go.Figure)

    def test_different_correlation_methods(self):
        """Test different correlation methods (pearson, spearman, kendall)."""
        df = pd.DataFrame({
            'Sample': ['S1', 'S1', 'S2', 'S2', 'S3', 'S3'],
            'KO': ['K00001', 'K00002', 'K00001', 'K00003', 'K00002', 'K00003']
        })

        for method in ['pearson', 'spearman', 'kendall']:
            config = {
                **get_sample_mode_config(),
                'visualization': {
                    **get_sample_mode_config()['visualization'],
                    'plotly': {
                        **get_sample_mode_config()['visualization']['plotly'],
                        'correlation_method': method
                    }
                }
            }
            strategy = CorrelogramStrategy(config)
            result = strategy.process_data(df)

            assert isinstance(result, pd.DataFrame)
            assert result.shape[0] == 3


# ============================================================================
# MODE COMPARISON TESTS
# ============================================================================

class TestModeComparison:
    """Test differences between sample and feature modes."""

    def test_sample_vs_feature_mode_different_output_size(self):
        """Test that sample and feature modes produce different matrix sizes."""
        df = pd.DataFrame({
            'Sample': ['S1', 'S1', 'S2', 'S2'],
            'KO': ['K00001', 'K00002', 'K00003', 'K00004']
        })

        # Sample mode: 2x2 (2 samples)
        config_sample = get_sample_mode_config()
        strategy_sample = CorrelogramStrategy(config_sample)
        result_sample = strategy_sample.process_data(df)

        # Feature mode: 4x4 (4 KOs)
        config_feature = get_feature_mode_config()
        config_feature['visualization']['plotly']['col_column'] = 'KO'
        strategy_feature = CorrelogramStrategy(config_feature)
        result_feature = strategy_feature.process_data(df)

        assert result_sample.shape[0] == 2
        assert result_feature.shape[0] == 4
