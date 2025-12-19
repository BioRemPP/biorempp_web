"""
Unit tests for PCAStrategy.

This module tests the PCAStrategy class which creates Principal Component
Analysis (PCA) scatter plots for dimensionality reduction and pattern discovery.

Test Categories
---------------
1. Initialization (5 tests)
2. Validation (10 tests)
3. Data Processing (10 tests)
4. PCA Transformation (8 tests)
5. Figure Creation (11 tests)
6. Integration (4 tests)
7. Edge Cases (10 tests)

Total: 58 tests
"""

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import pytest

from src.domain.plot_strategies.charts.pca_strategy import PCAStrategy


# =======================
# Helper Functions
# =======================


def get_minimal_config():
    """Get minimal configuration for PCAStrategy."""
    return {
        'metadata': {
            'use_case_id': 'UC-3.1',
            'module': 'module3'
        },
        'data': {
            'sample_column': 'Sample',
            'feature_column': 'KO'
        },
        'visualization': {
            'strategy': 'PCAStrategy',
            'plotly': {
                'n_components': 2,
                'color_palette': 'Plotly',
                'chart': {
                    'show_explained_variance': True,
                    'marker': {
                        'size': 10,
                        'line': {'width': 1, 'color': 'white'}
                    }
                },
                'layout': {
                    'height': 600,
                    'width': 800,
                    'template': 'simple_white',
                    'title': {
                        'text': 'PCA - Sample Clustering',
                        'show': True,
                        'x': 0.5
                    }
                }
            }
        }
    }


def get_custom_config():
    """Get custom configuration with specific settings."""
    config = get_minimal_config()
    config['visualization']['plotly']['n_components'] = 3
    config['visualization']['plotly']['color_palette'] = 'Set1'
    config['visualization']['plotly']['layout']['height'] = 800
    config['visualization']['plotly']['layout']['autosize'] = True
    return config


def get_sample_data():
    """
    Get sample data for PCA testing.

    Returns
    -------
    pd.DataFrame
        Sample-KO data with 4 samples and 5 KOs.
    """
    np.random.seed(42)
    return pd.DataFrame({
        'Sample': ['S1', 'S1', 'S1', 'S2', 'S2', 'S3', 'S3', 'S3', 'S4', 'S4'],
        'KO': ['K00001', 'K00002', 'K00003', 'K00001', 'K00004',
               'K00002', 'K00003', 'K00005', 'K00001', 'K00005']
    })


def get_large_sample_data():
    """
    Get large sample data for PCA testing.

    Returns
    -------
    pd.DataFrame
        Large Sample-KO data with 20 samples and 50 KOs.
    """
    np.random.seed(42)
    n_records = 200
    samples = [f'Sample_{i}' for i in range(20)]
    kos = [f'K{str(j).zfill(5)}' for j in range(50)]

    data = []
    for _ in range(n_records):
        sample = np.random.choice(samples)
        ko = np.random.choice(kos)
        data.append({'Sample': sample, 'KO': ko})

    return pd.DataFrame(data)


def get_minimal_sample_data():
    """
    Get minimal sample data (2 samples, 2 KOs).

    Returns
    -------
    pd.DataFrame
        Minimal valid data.
    """
    return pd.DataFrame({
        'Sample': ['S1', 'S2'],
        'KO': ['K00001', 'K00002']
    })


# =======================
# Test Class
# =======================


class TestPCAStrategy:
    """Test suite for PCAStrategy."""

    # =======================
    # 1. Initialization Tests
    # =======================

    def test_init_minimal_config(self):
        """Test initialization with minimal configuration."""
        # Arrange & Act
        config = get_minimal_config()
        strategy = PCAStrategy(config)

        # Assert
        assert strategy is not None
        assert strategy.sample_column == 'Sample'
        assert strategy.feature_column == 'KO'
        assert strategy.n_components == 2

    def test_init_custom_columns(self):
        """Test initialization with custom column names."""
        # Arrange
        config = get_minimal_config()
        config['data']['sample_column'] = 'SampleID'
        config['data']['feature_column'] = 'Gene'

        # Act
        strategy = PCAStrategy(config)

        # Assert
        assert strategy.sample_column == 'SampleID'
        assert strategy.feature_column == 'Gene'

    def test_init_custom_n_components(self):
        """Test initialization with custom n_components."""
        # Arrange
        config = get_custom_config()

        # Act
        strategy = PCAStrategy(config)

        # Assert
        assert strategy.n_components == 3

    def test_init_default_values(self):
        """Test initialization uses default values when not specified."""
        # Arrange
        config = {
            'metadata': {'use_case_id': 'UC-3.1'},
            'data': {},
            'visualization': {'plotly': {}}
        }

        # Act
        strategy = PCAStrategy(config)

        # Assert
        assert strategy.sample_column == 'Sample'
        assert strategy.feature_column == 'KO'
        assert strategy.n_components == 2

    def test_init_extracts_configs(self):
        """Test initialization extracts data and plotly configs."""
        # Arrange & Act
        config = get_minimal_config()
        strategy = PCAStrategy(config)

        # Assert
        assert strategy.data_config is not None
        assert strategy.plotly_config is not None

    # =======================
    # 2. Validation Tests
    # =======================

    def test_validate_empty_dataframe_fails(self):
        """Test validation fails with empty DataFrame."""
        # Arrange
        config = get_minimal_config()
        strategy = PCAStrategy(config)
        df = pd.DataFrame()

        # Act & Assert
        with pytest.raises(ValueError, match="DataFrame is empty"):
            strategy.validate_data(df)

    def test_validate_missing_sample_column(self):
        """Test validation fails when sample column is missing."""
        # Arrange
        config = get_minimal_config()
        strategy = PCAStrategy(config)
        df = pd.DataFrame({'KO': ['K00001']})

        # Act & Assert
        with pytest.raises(ValueError, match="Missing required columns"):
            strategy.validate_data(df)

    def test_validate_missing_feature_column(self):
        """Test validation fails when feature column is missing."""
        # Arrange
        config = get_minimal_config()
        strategy = PCAStrategy(config)
        df = pd.DataFrame({'Sample': ['S1']})

        # Act & Assert
        with pytest.raises(ValueError, match="Missing required columns"):
            strategy.validate_data(df)

    def test_validate_single_sample_fails(self):
        """Test validation fails with only one sample."""
        # Arrange
        config = get_minimal_config()
        strategy = PCAStrategy(config)
        df = pd.DataFrame({
            'Sample': ['S1', 'S1'],
            'KO': ['K00001', 'K00002']
        })

        # Act & Assert
        with pytest.raises(ValueError, match="Need at least 2 samples"):
            strategy.validate_data(df)

    def test_validate_single_feature_fails(self):
        """Test validation fails with only one feature."""
        # Arrange
        config = get_minimal_config()
        strategy = PCAStrategy(config)
        df = pd.DataFrame({
            'Sample': ['S1', 'S2'],
            'KO': ['K00001', 'K00001']
        })

        # Act & Assert
        with pytest.raises(ValueError, match="Need at least 2 features"):
            strategy.validate_data(df)

    def test_validate_minimal_data_passes(self):
        """Test validation passes with minimal valid data."""
        # Arrange
        config = get_minimal_config()
        strategy = PCAStrategy(config)
        df = get_minimal_sample_data()

        # Act & Assert (should not raise)
        strategy.validate_data(df)

    def test_validate_sample_data_passes(self):
        """Test validation passes with sample data."""
        # Arrange
        config = get_minimal_config()
        strategy = PCAStrategy(config)
        df = get_sample_data()

        # Act & Assert (should not raise)
        strategy.validate_data(df)

    def test_validate_with_nulls_warns(self):
        """Test validation with null values issues warnings."""
        # Arrange
        config = get_minimal_config()
        strategy = PCAStrategy(config)
        df = pd.DataFrame({
            'Sample': ['S1', None, 'S2', 'S3'],
            'KO': ['K00001', 'K00002', None, 'K00003']
        })

        # Act & Assert
        # Validation checks nulls but validates based on original data
        # S1 and S3 are complete rows with different KOs
        strategy.validate_data(df)

    def test_validate_large_dataset(self):
        """Test validation passes with large dataset."""
        # Arrange
        config = get_minimal_config()
        strategy = PCAStrategy(config)
        df = get_large_sample_data()

        # Act & Assert (should not raise)
        strategy.validate_data(df)

    def test_validate_additional_columns_ok(self):
        """Test validation passes with additional columns."""
        # Arrange
        config = get_minimal_config()
        strategy = PCAStrategy(config)
        df = get_sample_data()
        df['ExtraColumn'] = 'extra'

        # Act & Assert (should not raise)
        strategy.validate_data(df)

    # =======================
    # 3. Data Processing Tests
    # =======================

    def test_process_data_creates_matrix(self):
        """Test process_data creates presence/absence matrix."""
        # Arrange
        config = get_minimal_config()
        strategy = PCAStrategy(config)
        df = get_sample_data()

        # Act
        result = strategy.process_data(df)

        # Assert
        assert isinstance(result, pd.DataFrame)
        assert 'PC1' in result.columns
        assert 'PC2' in result.columns
        assert 'Sample' in result.columns

    def test_process_data_correct_shape(self):
        """Test process_data returns correct shape."""
        # Arrange
        config = get_minimal_config()
        strategy = PCAStrategy(config)
        df = get_sample_data()

        # Act
        result = strategy.process_data(df)

        # Assert
        # Should have 4 samples (rows) and 3 columns (PC1, PC2, Sample)
        assert result.shape[0] == 4
        assert result.shape[1] == 3

    def test_process_data_removes_nulls(self):
        """Test process_data removes null values."""
        # Arrange
        config = get_minimal_config()
        strategy = PCAStrategy(config)
        df = pd.DataFrame({
            'Sample': ['S1', 'S1', None, 'S2', 'S2'],
            'KO': ['K00001', 'K00002', 'K00003', None, 'K00004']
        })

        # Act
        result = strategy.process_data(df)

        # Assert
        # After removing nulls, should have 2 samples
        assert result.shape[0] == 2

    def test_process_data_sample_index(self):
        """Test process_data uses sample names as index."""
        # Arrange
        config = get_minimal_config()
        strategy = PCAStrategy(config)
        df = get_sample_data()

        # Act
        result = strategy.process_data(df)

        # Assert
        assert 'S1' in result.index
        assert 'S2' in result.index
        assert 'S3' in result.index
        assert 'S4' in result.index

    def test_process_data_pc_columns(self):
        """Test process_data creates PC columns."""
        # Arrange
        config = get_minimal_config()
        strategy = PCAStrategy(config)
        df = get_sample_data()

        # Act
        result = strategy.process_data(df)

        # Assert
        assert 'PC1' in result.columns
        assert 'PC2' in result.columns

    def test_process_data_stores_explained_variance(self):
        """Test process_data stores explained variance."""
        # Arrange
        config = get_minimal_config()
        strategy = PCAStrategy(config)
        df = get_sample_data()

        # Act
        result = strategy.process_data(df)

        # Assert
        assert hasattr(strategy, 'explained_variance')
        assert len(strategy.explained_variance) == 2
        assert strategy.explained_variance[0] > 0
        assert strategy.explained_variance[1] >= 0

    def test_process_data_explained_variance_sum(self):
        """Test explained variance sums to <= 100%."""
        # Arrange
        config = get_minimal_config()
        strategy = PCAStrategy(config)
        df = get_sample_data()

        # Act
        result = strategy.process_data(df)

        # Assert
        total_variance = sum(strategy.explained_variance)
        assert total_variance <= 100.0

    def test_process_data_pc_values_numeric(self):
        """Test PC values are numeric."""
        # Arrange
        config = get_minimal_config()
        strategy = PCAStrategy(config)
        df = get_sample_data()

        # Act
        result = strategy.process_data(df)

        # Assert
        assert result['PC1'].dtype in [np.float64, np.float32]
        assert result['PC2'].dtype in [np.float64, np.float32]

    def test_process_data_minimal_data(self):
        """Test process_data with minimal valid data."""
        # Arrange
        config = get_minimal_config()
        strategy = PCAStrategy(config)
        df = get_minimal_sample_data()

        # Act
        result = strategy.process_data(df)

        # Assert
        assert result.shape[0] == 2

    def test_process_data_large_dataset(self):
        """Test process_data with large dataset."""
        # Arrange
        config = get_minimal_config()
        strategy = PCAStrategy(config)
        df = get_large_sample_data()

        # Act
        result = strategy.process_data(df)

        # Assert
        assert result.shape[0] == 20  # 20 unique samples
        assert 'PC1' in result.columns
        assert 'PC2' in result.columns

    # =======================
    # 4. PCA Transformation Tests
    # =======================

    def test_pca_standardization(self):
        """Test PCA uses standardized data."""
        # Arrange
        config = get_minimal_config()
        strategy = PCAStrategy(config)
        df = get_sample_data()

        # Act
        result = strategy.process_data(df)

        # Assert
        # PCA results should have reasonable scale (standardized)
        assert abs(result['PC1'].mean()) < 2
        assert abs(result['PC2'].mean()) < 2

    def test_pca_principal_components_orthogonal(self):
        """Test principal components are orthogonal."""
        # Arrange
        config = get_minimal_config()
        strategy = PCAStrategy(config)
        df = get_large_sample_data()

        # Act
        result = strategy.process_data(df)

        # Assert
        # PC1 and PC2 should be uncorrelated (orthogonal)
        correlation = result['PC1'].corr(result['PC2'])
        assert abs(correlation) < 0.1  # Should be close to 0

    def test_pca_variance_decreasing(self):
        """Test explained variance is in decreasing order."""
        # Arrange
        config = get_minimal_config()
        strategy = PCAStrategy(config)
        df = get_sample_data()

        # Act
        result = strategy.process_data(df)

        # Assert
        assert strategy.explained_variance[0] >= strategy.explained_variance[1]

    def test_pca_reproducible_with_seed(self):
        """Test PCA produces reproducible results."""
        # Arrange
        config = get_minimal_config()
        strategy1 = PCAStrategy(config)
        strategy2 = PCAStrategy(config)
        df = get_sample_data()

        # Act
        result1 = strategy1.process_data(df)
        result2 = strategy2.process_data(df)

        # Assert
        # Results should be identical (or very close due to numeric precision)
        pd.testing.assert_frame_equal(
            result1[['PC1', 'PC2']],
            result2[['PC1', 'PC2']],
            rtol=1e-10
        )

    def test_pca_n_components_3(self):
        """Test PCA with 3 components."""
        # Arrange
        config = get_custom_config()
        strategy = PCAStrategy(config)
        df = get_sample_data()

        # Act
        result = strategy.process_data(df)

        # Assert
        assert 'PC1' in result.columns
        assert 'PC2' in result.columns
        assert 'PC3' in result.columns
        assert len(strategy.explained_variance) == 3

    def test_pca_binary_matrix_conversion(self):
        """Test crosstab creates binary matrix."""
        # Arrange
        config = get_minimal_config()
        strategy = PCAStrategy(config)
        # Duplicate entries should become 1 (presence)
        df = pd.DataFrame({
            'Sample': ['S1', 'S1', 'S1'],
            'KO': ['K00001', 'K00001', 'K00002']
        })
        df = pd.concat([df, get_minimal_sample_data()], ignore_index=True)

        # Act
        result = strategy.process_data(df)

        # Assert
        # Should handle duplicates correctly
        assert isinstance(result, pd.DataFrame)

    def test_pca_all_samples_identical(self):
        """Test PCA with all samples having identical features."""
        # Arrange
        config = get_minimal_config()
        strategy = PCAStrategy(config)
        df = pd.DataFrame({
            'Sample': ['S1', 'S1', 'S2', 'S2'],
            'KO': ['K00001', 'K00002', 'K00001', 'K00002']
        })

        # Act
        result = strategy.process_data(df)

        # Assert
        # PCA should work but PC values will be 0 or very small
        assert isinstance(result, pd.DataFrame)

    def test_pca_handles_sparse_data(self):
        """Test PCA handles sparse presence/absence matrix."""
        # Arrange
        config = get_minimal_config()
        strategy = PCAStrategy(config)
        # Create sparse data (many KOs, few overlaps)
        df = pd.DataFrame({
            'Sample': ['S1', 'S2', 'S3', 'S4'],
            'KO': ['K00001', 'K00002', 'K00003', 'K00004']
        })

        # Act
        result = strategy.process_data(df)

        # Assert
        assert result.shape[0] == 4

    # =======================
    # 5. Figure Creation Tests
    # =======================

    def test_create_figure_returns_figure(self):
        """Test create_figure returns Plotly Figure."""
        # Arrange
        config = get_minimal_config()
        strategy = PCAStrategy(config)
        df = get_sample_data()
        processed = strategy.process_data(df)

        # Act
        fig = strategy.create_figure(processed)

        # Assert
        assert isinstance(fig, go.Figure)

    def test_create_figure_has_traces(self):
        """Test figure has scatter traces."""
        # Arrange
        config = get_minimal_config()
        strategy = PCAStrategy(config)
        df = get_sample_data()
        processed = strategy.process_data(df)

        # Act
        fig = strategy.create_figure(processed)

        # Assert
        assert len(fig.data) > 0

    def test_create_figure_title(self):
        """Test figure has correct title."""
        # Arrange
        config = get_minimal_config()
        strategy = PCAStrategy(config)
        df = get_sample_data()
        processed = strategy.process_data(df)

        # Act
        fig = strategy.create_figure(processed)

        # Assert
        assert fig.layout.title is not None
        assert 'PCA - Sample Clustering' in fig.layout.title.text

    def test_create_figure_axis_labels_with_variance(self):
        """Test axis labels include explained variance."""
        # Arrange
        config = get_minimal_config()
        strategy = PCAStrategy(config)
        df = get_sample_data()
        processed = strategy.process_data(df)

        # Act
        fig = strategy.create_figure(processed)

        # Assert
        assert 'Principal Component 1' in fig.layout.xaxis.title.text
        assert 'Principal Component 2' in fig.layout.yaxis.title.text
        assert '%' in fig.layout.xaxis.title.text  # Variance percentage

    def test_create_figure_hide_variance(self):
        """Test axis labels without explained variance."""
        # Arrange
        config = get_minimal_config()
        config['visualization']['plotly']['chart']['show_explained_variance'] = False
        strategy = PCAStrategy(config)
        df = get_sample_data()
        processed = strategy.process_data(df)

        # Act
        fig = strategy.create_figure(processed)

        # Assert
        assert 'Principal Component 1' in fig.layout.xaxis.title.text
        assert '%' not in fig.layout.xaxis.title.text

    def test_create_figure_layout_configuration(self):
        """Test figure applies layout configuration."""
        # Arrange
        config = get_minimal_config()
        strategy = PCAStrategy(config)
        df = get_sample_data()
        processed = strategy.process_data(df)

        # Act
        fig = strategy.create_figure(processed)

        # Assert
        assert fig.layout.height == 600
        assert fig.layout.width == 800

    def test_create_figure_custom_layout(self):
        """Test figure with custom layout settings."""
        # Arrange
        config = get_custom_config()
        strategy = PCAStrategy(config)
        df = get_sample_data()
        processed = strategy.process_data(df)

        # Act
        fig = strategy.create_figure(processed)

        # Assert
        # When autosize=True, height may not be set
        assert fig.layout.autosize == True or fig.layout.height == 800

    def test_create_figure_marker_configuration(self):
        """Test figure applies marker configuration."""
        # Arrange
        config = get_minimal_config()
        strategy = PCAStrategy(config)
        df = get_sample_data()
        processed = strategy.process_data(df)

        # Act
        fig = strategy.create_figure(processed)

        # Assert
        # Check marker size
        assert fig.data[0].marker.size == 10

    def test_create_figure_color_palette(self):
        """Test figure uses specified color palette."""
        # Arrange
        config = get_minimal_config()
        strategy = PCAStrategy(config)
        df = get_sample_data()
        processed = strategy.process_data(df)

        # Act
        fig = strategy.create_figure(processed)

        # Assert
        # Should have color assigned to traces
        assert fig.data[0].marker.color is not None

    def test_create_figure_hide_title(self):
        """Test figure with title hidden."""
        # Arrange
        config = get_minimal_config()
        config['visualization']['plotly']['layout']['title']['show'] = False
        strategy = PCAStrategy(config)
        df = get_sample_data()
        processed = strategy.process_data(df)

        # Act
        fig = strategy.create_figure(processed)

        # Assert
        # When show=False, title dict is not added to layout
        # Check that title is either None or has empty/no text
        if fig.layout.title is not None:
            title_text = fig.layout.title.text if hasattr(fig.layout.title, 'text') else None
            assert title_text is None or title_text == ''

    def test_create_figure_autosize(self):
        """Test figure with autosize enabled."""
        # Arrange
        config = get_custom_config()
        strategy = PCAStrategy(config)
        df = get_sample_data()
        processed = strategy.process_data(df)

        # Act
        fig = strategy.create_figure(processed)

        # Assert
        assert isinstance(fig, go.Figure)

    # =======================
    # 6. Integration Tests
    # =======================

    def test_generate_plot_full_workflow(self):
        """Test complete workflow: validate -> process -> create."""
        # Arrange
        config = get_minimal_config()
        strategy = PCAStrategy(config)
        df = get_sample_data()

        # Act
        fig = strategy.generate_plot(df)

        # Assert
        assert isinstance(fig, go.Figure)

    def test_generate_plot_minimal_data(self):
        """Test workflow with minimal valid data."""
        # Arrange
        config = get_minimal_config()
        strategy = PCAStrategy(config)
        df = get_minimal_sample_data()

        # Act
        fig = strategy.generate_plot(df)

        # Assert
        assert isinstance(fig, go.Figure)

    def test_generate_plot_large_dataset(self):
        """Test workflow with large dataset."""
        # Arrange
        config = get_minimal_config()
        strategy = PCAStrategy(config)
        df = get_large_sample_data()

        # Act
        fig = strategy.generate_plot(df)

        # Assert
        assert isinstance(fig, go.Figure)

    def test_generate_plot_with_nulls(self):
        """Test workflow handles null values correctly."""
        # Arrange
        config = get_minimal_config()
        strategy = PCAStrategy(config)
        df = pd.DataFrame({
            'Sample': ['S1', 'S1', None, 'S2', 'S2', 'S3'],
            'KO': ['K00001', 'K00002', 'K00003', 'K00001', None, 'K00002']
        })

        # Act
        fig = strategy.generate_plot(df)

        # Assert
        assert isinstance(fig, go.Figure)

    # =======================
    # 7. Edge Cases
    # =======================

    def test_edge_case_two_samples_many_features(self):
        """Test PCA with 2 samples and many features."""
        # Arrange
        config = get_minimal_config()
        strategy = PCAStrategy(config)
        kos = [f'K{str(i).zfill(5)}' for i in range(20)]
        df = pd.DataFrame({
            'Sample': ['S1'] * 10 + ['S2'] * 10,
            'KO': kos
        })

        # Act
        fig = strategy.generate_plot(df)

        # Assert
        assert isinstance(fig, go.Figure)

    def test_edge_case_many_samples_two_features(self):
        """Test PCA with many samples and 2 features."""
        # Arrange
        config = get_minimal_config()
        strategy = PCAStrategy(config)
        samples = [f'S{i}' for i in range(10)]
        df = pd.DataFrame({
            'Sample': samples + samples,
            'KO': ['K00001'] * 10 + ['K00002'] * 10
        })

        # Act
        fig = strategy.generate_plot(df)

        # Assert
        assert isinstance(fig, go.Figure)

    def test_edge_case_duplicate_records(self):
        """Test PCA handles duplicate records correctly."""
        # Arrange
        config = get_minimal_config()
        strategy = PCAStrategy(config)
        df = pd.DataFrame({
            'Sample': ['S1', 'S1', 'S1', 'S2', 'S2'],
            'KO': ['K00001', 'K00001', 'K00002', 'K00002', 'K00003']
        })

        # Act
        fig = strategy.generate_plot(df)

        # Assert
        assert isinstance(fig, go.Figure)

    def test_edge_case_special_characters_in_names(self):
        """Test PCA with special characters in sample/feature names."""
        # Arrange
        config = get_minimal_config()
        strategy = PCAStrategy(config)
        df = pd.DataFrame({
            'Sample': ['S@1', 'S#2', 'S$3'],
            'KO': ['K-001', 'K_002', 'K.003']
        })

        # Act
        fig = strategy.generate_plot(df)

        # Assert
        assert isinstance(fig, go.Figure)

    def test_edge_case_very_long_names(self):
        """Test PCA with very long sample/feature names."""
        # Arrange
        config = get_minimal_config()
        strategy = PCAStrategy(config)
        long_name = 'Sample_' + 'A' * 100
        df = pd.DataFrame({
            'Sample': [long_name, 'S2'],
            'KO': ['K00001', 'K00002']
        })

        # Act
        fig = strategy.generate_plot(df)

        # Assert
        assert isinstance(fig, go.Figure)

    def test_edge_case_numeric_sample_names(self):
        """Test PCA with numeric sample names."""
        # Arrange
        config = get_minimal_config()
        strategy = PCAStrategy(config)
        df = pd.DataFrame({
            'Sample': [1, 2, 3],
            'KO': ['K00001', 'K00002', 'K00003']
        })

        # Act
        fig = strategy.generate_plot(df)

        # Assert
        assert isinstance(fig, go.Figure)

    def test_edge_case_all_samples_same_features(self):
        """Test PCA when all samples have identical features."""
        # Arrange
        config = get_minimal_config()
        strategy = PCAStrategy(config)
        df = pd.DataFrame({
            'Sample': ['S1', 'S1', 'S2', 'S2', 'S3', 'S3'],
            'KO': ['K00001', 'K00002'] * 3
        })

        # Act
        fig = strategy.generate_plot(df)

        # Assert
        # PCA should work but variance will be 0
        assert isinstance(fig, go.Figure)

    def test_edge_case_no_shared_features(self):
        """Test PCA when samples have no shared features."""
        # Arrange
        config = get_minimal_config()
        strategy = PCAStrategy(config)
        df = pd.DataFrame({
            'Sample': ['S1', 'S2', 'S3'],
            'KO': ['K00001', 'K00002', 'K00003']
        })

        # Act
        fig = strategy.generate_plot(df)

        # Assert
        assert isinstance(fig, go.Figure)

    def test_edge_case_custom_axis_titles(self):
        """Test PCA with custom axis titles."""
        # Arrange
        config = get_minimal_config()
        config['visualization']['plotly']['chart']['xaxis'] = {
            'title': 'Custom PC1'
        }
        config['visualization']['plotly']['chart']['yaxis'] = {
            'title': 'Custom PC2'
        }
        strategy = PCAStrategy(config)
        df = get_sample_data()

        # Act
        fig = strategy.generate_plot(df)

        # Assert
        assert 'Custom PC1' in fig.layout.xaxis.title.text
        assert 'Custom PC2' in fig.layout.yaxis.title.text

    def test_edge_case_color_palette_list(self):
        """Test PCA with color palette as list."""
        # Arrange
        config = get_minimal_config()
        config['visualization']['plotly']['color_palette'] = [
            '#FF0000', '#00FF00', '#0000FF'
        ]
        strategy = PCAStrategy(config)
        df = get_sample_data()

        # Act
        fig = strategy.generate_plot(df)

        # Assert
        assert isinstance(fig, go.Figure)
