"""
Unit Tests for Application Services.

This module tests the application services including CacheService
and ProgressTracker.
"""

import time
from unittest.mock import patch

import pytest

from src.application.services.cache_service import CacheService
from src.application.services.progress_tracker import ProgressTracker


class TestCacheService:
    """Test CacheService functionality."""

    def test_set_and_get(self):
        """Test basic set and get operations."""
        cache = CacheService()
        cache.set("key1", "value1")

        result = cache.get("key1")

        assert result == "value1"

    def test_get_nonexistent_returns_none(self):
        """Test getting nonexistent key returns None."""
        cache = CacheService()

        result = cache.get("nonexistent")

        assert result is None

    def test_delete(self):
        """Test deleting cache entry."""
        cache = CacheService()
        cache.set("key1", "value1")

        deleted = cache.delete("key1")
        result = cache.get("key1")

        assert deleted is True
        assert result is None

    def test_clear(self):
        """Test clearing entire cache."""
        cache = CacheService()
        cache.set("key1", "value1")
        cache.set("key2", "value2")

        cache.clear()

        assert cache.size() == 0

    def test_has(self):
        """Test checking if key exists."""
        cache = CacheService()
        cache.set("key1", "value1")

        assert cache.has("key1") is True
        assert cache.has("nonexistent") is False

    def test_size(self):
        """Test getting cache size."""
        cache = CacheService()
        cache.set("key1", "value1")
        cache.set("key2", "value2")

        assert cache.size() == 2

    def test_generate_hash_key(self):
        """Test hash key generation."""
        cache = CacheService()
        key1 = cache.generate_hash_key("content1")
        key2 = cache.generate_hash_key("content1")
        key3 = cache.generate_hash_key("content2")

        # Same content = same key
        assert key1 == key2
        # Different content = different key
        assert key1 != key3
        # Hash is 64 chars (SHA256)
        assert len(key1) == 64

    def test_eviction_when_full(self):
        """Test that oldest entry is evicted when cache is full."""
        cache = CacheService(max_size=2)
        cache.set("key1", "value1")
        time.sleep(0.01)
        cache.set("key2", "value2")
        cache.set("key3", "value3")  # Should evict key1

        assert cache.has("key1") is False
        assert cache.has("key2") is True
        assert cache.has("key3") is True

    def test_ttl_expiration(self):
        """Test that entries expire after TTL."""
        cache = CacheService(default_ttl_seconds=1)
        cache.set("key1", "value1", ttl_seconds=1)

        # Should exist immediately
        assert cache.get("key1") == "value1"

        # Wait for expiration
        time.sleep(1.1)

        # Should be expired
        assert cache.get("key1") is None


class TestProgressTracker:
    """Test ProgressTracker functionality."""

    def test_initial_state(self):
        """Tracker should start in not-started state."""
        tracker = ProgressTracker("session-1")

        progress = tracker.get_progress()

        assert progress.current_stage == "Not Started"
        assert progress.stage_number == 1
        assert progress.progress_percentage == 0.0
        assert progress.error is None

    def test_start_stage_and_update_progress(self):
        """Progress should reflect weighted stage completion."""
        tracker = ProgressTracker("session-2")
        tracker.start_stage(3, "BioRemPP Database Merge", "Starting merge")
        tracker.update_progress(50.0, "Halfway")

        progress = tracker.get_progress()

        assert progress.current_stage == "BioRemPP Database Merge"
        assert progress.message == "Halfway"
        # Stage1+2 complete = 15%, plus 50% of stage3 (30%) = 15%
        assert progress.progress_percentage == pytest.approx(30.0)

    def test_start_stage_invalid_number_raises(self):
        """Invalid stage numbers should raise ValueError."""
        tracker = ProgressTracker("session-3")

        with pytest.raises(ValueError, match="Invalid stage number"):
            tracker.start_stage(9, "Invalid Stage")

    def test_complete_sets_final_state(self):
        """complete() should move tracker to 100% finalization."""
        tracker = ProgressTracker("session-4")
        tracker.complete()

        progress = tracker.get_progress()

        assert progress.current_stage == "Finalization"
        assert progress.stage_number == 8
        assert progress.progress_percentage == 100.0
        assert progress.message == "Processing complete"

    def test_set_error_records_error_state(self):
        """set_error should store error and expose it in DTO."""
        tracker = ProgressTracker("session-5")
        tracker.set_error("database unavailable")

        progress = tracker.get_progress()

        assert progress.error == "database unavailable"
        assert progress.message == "Error: database unavailable"

    def test_estimated_time_is_computed_after_enough_elapsed_time(self):
        """Estimated time should be available when elapsed >= 1s and progress > 0."""
        tracker = ProgressTracker("session-6")
        tracker.start_stage(4, "KEGG Database Merge")
        tracker.update_progress(50.0)
        tracker._start_time = 0.0

        with patch("src.application.services.progress_tracker.time.time", return_value=10.0):
            progress = tracker.get_progress()

        assert progress.estimated_time_remaining is not None
        assert progress.estimated_time_remaining > 0
