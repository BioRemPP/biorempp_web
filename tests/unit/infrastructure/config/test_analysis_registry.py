"""
Unit tests for Analysis Registry module.
"""

import pytest
from pathlib import Path
from src.infrastructure.config.analysis_registry import AnalysisRegistry


class TestAnalysisRegistry:
    """Test suite for AnalysisRegistry."""

    def test_initialization(self):
        """Test registry initialization."""
        registry = AnalysisRegistry()
        
        assert isinstance(registry._analyses, dict)

    def test_get_analysis_ids(self):
        """Test getting all analysis IDs."""
        registry = AnalysisRegistry()
        
        ids = registry.get_analysis_ids()
        
        assert isinstance(ids, list)

    def test_get_all_analyses(self):
        """Test getting all analyses."""
        registry = AnalysisRegistry()
        
        analyses = registry.get_all_analyses()
        
        assert isinstance(analyses, dict)

    def test_get_use_cases(self):
        """Test getting unique use cases."""
        registry = AnalysisRegistry()
        
        use_cases = registry.get_use_cases()
        
        assert isinstance(use_cases, list)

    def test_analysis_exists(self):
        """Test checking if analysis exists."""
        registry = AnalysisRegistry()
        
        # Check with non-existent ID
        exists = registry.analysis_exists('NONEXISTENT')
        
        assert exists is False

    def test_get_stats(self):
        """Test getting registry statistics."""
        registry = AnalysisRegistry()
        
        stats = registry.get_stats()
        
        assert isinstance(stats, dict)
        assert 'total_analyses' in stats
        assert 'total_use_cases' in stats
        assert 'use_cases' in stats
        assert 'analyses_per_use_case' in stats

    def test_get_analysis_nonexistent(self):
        """Test getting non-existent analysis returns None."""
        registry = AnalysisRegistry()
        
        analysis = registry.get_analysis('NONEXISTENT_ID')
        
        assert analysis is None

    def test_get_analyses_by_use_case(self):
        """Test getting analyses by use case."""
        registry = AnalysisRegistry()
        
        # Get UC1 analyses (even if empty)
        uc1_analyses = registry.get_analyses_by_use_case('UC1')
        
        assert isinstance(uc1_analyses, list)

    def test_get_analysis_plot_type(self):
        """Test getting plot type for analysis."""
        registry = AnalysisRegistry()
        
        # Non-existent analysis should return None
        plot_type = registry.get_analysis_plot_type('NONEXISTENT')
        
        assert plot_type is None
