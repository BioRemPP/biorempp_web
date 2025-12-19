"""
Unit tests for PlotService Singleton.

Tests thread safety, instance uniqueness, and reset functionality.
"""

import threading
import pytest
from src.application.plot_services.singleton import (
    PlotServiceSingleton,
    get_plot_service
)
from src.application.plot_services.plot_service import PlotService


class TestPlotServiceSingleton:
    """Test suite for PlotServiceSingleton class."""

    def setup_method(self):
        """Reset singleton before each test to ensure isolation."""
        PlotServiceSingleton.reset()

    def teardown_method(self):
        """Reset singleton after each test to ensure isolation."""
        PlotServiceSingleton.reset()

    def test_singleton_returns_same_instance(self):
        """Test that get_instance() always returns the same instance."""
        # Act
        instance1 = PlotServiceSingleton.get_instance()
        instance2 = PlotServiceSingleton.get_instance()
        instance3 = PlotServiceSingleton.get_instance()

        # Assert
        assert instance1 is instance2, "Should return same instance"
        assert instance2 is instance3, "Should return same instance"
        assert isinstance(instance1, PlotService), "Should be PlotService"

    def test_get_plot_service_returns_same_instance(self):
        """Test that module function returns same instance as class method."""
        # Act
        service1 = get_plot_service()
        service2 = get_plot_service()
        class_service = PlotServiceSingleton.get_instance()

        # Assert
        assert service1 is service2, "Module function should return same instance"
        assert service1 is class_service, "Should match class method instance"

    def test_singleton_cannot_be_instantiated_directly(self):
        """Test that direct instantiation raises RuntimeError."""
        # Act & Assert
        with pytest.raises(RuntimeError) as exc_info:
            PlotServiceSingleton()

        assert "cannot be instantiated directly" in str(exc_info.value)
        assert "get_plot_service()" in str(exc_info.value)

    def test_singleton_reset(self):
        """Test that reset() allows new instance creation."""
        # Arrange
        instance1 = PlotServiceSingleton.get_instance()

        # Act
        PlotServiceSingleton.reset()
        instance2 = PlotServiceSingleton.get_instance()

        # Assert
        assert instance1 is not instance2, "Reset should create new instance"
        assert isinstance(instance2, PlotService), "New instance should be PlotService"

    def test_singleton_thread_safety_concurrent_creation(self):
        """
        Test that concurrent calls to get_instance() from multiple threads
        still create only ONE instance (thread safety test).
        """
        # Arrange
        instances = []
        num_threads = 10
        barrier = threading.Barrier(num_threads)  # Synchronize thread starts

        def create_instance():
            """Thread worker: wait at barrier, then get instance."""
            barrier.wait()  # All threads start simultaneously
            instance = PlotServiceSingleton.get_instance()
            instances.append(instance)

        # Act: Create multiple threads that simultaneously request instance
        threads = [
            threading.Thread(target=create_instance)
            for _ in range(num_threads)
        ]

        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()

        # Assert: All threads should have received the SAME instance
        assert len(instances) == num_threads, "All threads should get instance"
        unique_instances = set(id(inst) for inst in instances)
        assert len(unique_instances) == 1, (
            f"Only ONE unique instance should exist, found {len(unique_instances)}"
        )

        # Verify all are the same object
        first_instance = instances[0]
        for instance in instances:
            assert instance is first_instance, "All instances must be identical"

    def test_singleton_thread_safety_with_reset(self):
        """
        Test thread safety when one thread resets while others are getting
        the instance.
        """
        # Arrange
        instances_before_reset = []
        instances_after_reset = []
        barrier1 = threading.Barrier(5)  # First wave
        barrier2 = threading.Barrier(5)  # Second wave

        def get_instance_wave1():
            barrier1.wait()
            instance = PlotServiceSingleton.get_instance()
            instances_before_reset.append(instance)

        def get_instance_wave2():
            barrier2.wait()
            instance = PlotServiceSingleton.get_instance()
            instances_after_reset.append(instance)

        # Act: First wave creates instance
        threads_wave1 = [
            threading.Thread(target=get_instance_wave1)
            for _ in range(5)
        ]
        for t in threads_wave1:
            t.start()
        for t in threads_wave1:
            t.join()

        # Reset
        PlotServiceSingleton.reset()

        # Second wave creates new instance
        threads_wave2 = [
            threading.Thread(target=get_instance_wave2)
            for _ in range(5)
        ]
        for t in threads_wave2:
            t.start()
        for t in threads_wave2:
            t.join()

        # Assert
        # All instances in wave1 should be identical
        assert len(set(id(i) for i in instances_before_reset)) == 1

        # All instances in wave2 should be identical
        assert len(set(id(i) for i in instances_after_reset)) == 1

        # Wave1 and Wave2 should be DIFFERENT instances
        assert instances_before_reset[0] is not instances_after_reset[0]

    def test_singleton_instance_is_valid_plot_service(self):
        """Test that singleton returns a functional PlotService instance."""
        # Act
        service = get_plot_service()

        # Assert: Check that PlotService components exist
        assert hasattr(service, 'config_loader'), "Should have config_loader"
        assert hasattr(service, 'factory'), "Should have factory"
        assert hasattr(service, 'cache_manager'), "Should have cache_manager"
        assert hasattr(service, 'generate_plot'), "Should have generate_plot method"

    def test_multiple_resets_work_correctly(self):
        """Test that multiple consecutive resets work as expected."""
        # Act & Assert
        instance1 = get_plot_service()

        PlotServiceSingleton.reset()
        instance2 = get_plot_service()
        assert instance1 is not instance2

        PlotServiceSingleton.reset()
        instance3 = get_plot_service()
        assert instance2 is not instance3
        assert instance1 is not instance3

        PlotServiceSingleton.reset()
        PlotServiceSingleton.reset()  # Double reset
        instance4 = get_plot_service()
        assert instance3 is not instance4

    def test_reset_when_no_instance_exists(self):
        """Test that reset() is safe to call when no instance exists."""
        # Arrange: Ensure no instance exists
        PlotServiceSingleton.reset()

        # Act: Reset again (should not raise error)
        PlotServiceSingleton.reset()

        # Assert: Can still create instance normally
        instance = get_plot_service()
        assert isinstance(instance, PlotService)


class TestSingletonIntegration:
    """Integration tests for Singleton usage patterns."""

    def setup_method(self):
        """Reset singleton before each test."""
        PlotServiceSingleton.reset()

    def teardown_method(self):
        """Reset singleton after each test."""
        PlotServiceSingleton.reset()

    def test_multiple_callbacks_share_same_instance(self):
        """
        Simulate multiple callbacks obtaining PlotService - should all
        share the same instance.
        """
        # Arrange: Simulate 51 callbacks (like UC-1.1, UC-1.2, etc.)
        callback_services = []

        # Act: Each "callback" gets PlotService via get_plot_service()
        for i in range(51):
            service = get_plot_service()
            callback_services.append(service)

        # Assert: All 51 callbacks should have the SAME instance
        unique_instances = set(id(service) for service in callback_services)
        assert len(unique_instances) == 1, (
            "All 51 callbacks should share single instance"
        )

        # Verify cache manager is also shared
        cache_managers = [s.cache_manager for s in callback_services]
        unique_cache_managers = set(id(cm) for cm in cache_managers)
        assert len(unique_cache_managers) == 1, (
            "All callbacks should share same cache manager"
        )

    def test_singleton_pattern_memory_benefit(self):
        """
        Demonstrate memory benefit: creating 37 separate instances vs
        1 singleton instance.
        """
        import sys

        # Scenario 1: OLD pattern (create 37 instances)
        PlotServiceSingleton.reset()
        old_pattern_instances = [PlotService() for _ in range(37)]
        old_pattern_size = sum(
            sys.getsizeof(inst) for inst in old_pattern_instances
        )

        # Scenario 2: NEW pattern (1 singleton instance accessed 37 times)
        PlotServiceSingleton.reset()
        new_pattern_instances = [get_plot_service() for _ in range(37)]
        # All references point to same object
        assert len(set(id(i) for i in new_pattern_instances)) == 1

        new_pattern_size = sys.getsizeof(new_pattern_instances[0])

        # Assert: New pattern uses significantly less memory
        # (37 instances vs 1 instance)
        assert new_pattern_size < old_pattern_size, (
            f"Singleton should use less memory: "
            f"{new_pattern_size} bytes (1 instance) vs "
            f"{old_pattern_size} bytes (37 instances)"
        )

        # Calculate memory reduction
        reduction_ratio = (old_pattern_size - new_pattern_size) / old_pattern_size * 100
        print(f"\n✓ Memory reduction: {reduction_ratio:.1f}%")


# Pytest fixtures for easy singleton reset in other tests
@pytest.fixture
def reset_singleton():
    """
    Fixture to automatically reset singleton before and after tests.

    Usage in test files:
    >>> def test_something(reset_singleton):
    >>>     service = get_plot_service()
    >>>     # Test with fresh singleton instance
    """
    PlotServiceSingleton.reset()
    yield
    PlotServiceSingleton.reset()


@pytest.fixture
def plot_service_singleton():
    """
    Fixture that provides a fresh PlotService singleton instance.

    Usage in test files:
    >>> def test_something(plot_service_singleton):
    >>>     fig = plot_service_singleton.generate_plot(...)
    >>>     # Test with singleton instance
    """
    PlotServiceSingleton.reset()
    service = get_plot_service()
    yield service
    PlotServiceSingleton.reset()
