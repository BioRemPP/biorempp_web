"""
PlotService Singleton - Thread-Safe Singleton Pattern.

Provides a single, shared instance of PlotService across the entire
application to prevent redundant instantiations and reduce memory overhead.

Classes
-------
PlotServiceSingleton
    Thread-safe Singleton implementation for PlotService

Functions
---------
get_plot_service()
    Public interface to obtain the singleton PlotService instance

Notes
-----
Implements the Singleton pattern with double-checked locking to ensure
thread safety in multi-worker environments (Gunicorn).

Benefits:
- Reduces memory usage from 37+ instances to 1 per worker
- Centralizes cache (GraphCacheManager shared across all callbacks)
- Improves startup performance (single initialization)

Thread Safety:
Uses threading.Lock with double-checked locking pattern to prevent race
conditions during instance creation.
"""

import logging
import threading
from typing import Optional

from src.application.plot_services.plot_service import PlotService

logger = logging.getLogger(__name__)


class PlotServiceSingleton:
    """
    Thread-safe Singleton for PlotService.

    Implements the Singleton pattern with double-checked locking to ensure
    only one instance of PlotService exists per application process.

    Attributes
    ----------
    _instance : Optional[PlotService]
        The singleton instance (class-level attribute)
    _lock : threading.Lock
        Thread lock for synchronized instance creation

    Methods
    -------
    get_instance()
        Returns the singleton instance, creating it if necessary
    reset()
        Resets the singleton instance (for testing purposes only)

    Notes
    -----
    This class should NOT be instantiated directly. Use the module-level
    `get_plot_service()` function instead.

    Thread Safety:
    Uses double-checked locking pattern:
    1. Check if instance exists (fast path, no lock)
    2. Acquire lock if instance doesn't exist
    3. Check again inside lock (prevents race condition)
    4. Create instance if still None
    """

    _instance: Optional[PlotService] = None
    _lock: threading.Lock = threading.Lock()

    def __init__(self):
        """
        Private constructor.

        Raises
        ------
        RuntimeError
            Always raises to prevent direct instantiation.

        Notes
        -----
        Use `get_plot_service()` or `PlotServiceSingleton.get_instance()`
        instead of creating instances directly.
        """
        raise RuntimeError(
            "PlotServiceSingleton cannot be instantiated directly. "
            "Use get_plot_service() function instead."
        )

    @classmethod
    def get_instance(cls) -> PlotService:
        """
        Get the singleton PlotService instance.

        Creates the instance on first call (lazy initialization) and returns
        the same instance on subsequent calls. Thread-safe via double-checked
        locking.

        Returns
        -------
        PlotService
            The singleton PlotService instance

        Notes
        -----
        Thread Safety:
        - First check (outside lock): Fast path for already-created instance
        - Lock acquisition: Synchronizes competing threads
        - Second check (inside lock): Prevents race condition
        - Instance creation: Only one thread creates the instance
        """
        # Fast path: instance already exists (no lock needed)
        if cls._instance is not None:
            return cls._instance

        # Slow path: need to create instance (acquire lock)
        with cls._lock:
            # Double-check: another thread might have created instance
            # while we were waiting for the lock
            if cls._instance is None:
                logger.info(
                    "Creating singleton PlotService instance " "(first initialization)"
                )
                cls._instance = PlotService()
                logger.info("Singleton PlotService instance created successfully")
            else:
                logger.debug("Singleton instance already created by another thread")

        return cls._instance

    @classmethod
    def reset(cls) -> None:
        """
        Reset the singleton instance.

        Destroys the current singleton instance, allowing a new one to be
        created on next `get_instance()` call.

        Warnings
        --------
        This method is ONLY for testing purposes. Do NOT use in production
        code as it breaks the Singleton contract and can cause unpredictable
        behavior.

        Notes
        -----
        Use this in pytest fixtures to ensure test isolation.

        Thread Safety:
        Acquires lock to ensure no other thread is creating an instance
        during reset.
        """
        with cls._lock:
            if cls._instance is not None:
                logger.warning(
                    "Resetting singleton PlotService instance "
                    "(TEST MODE ONLY - do not use in production)"
                )
                cls._instance = None
                logger.info("Singleton instance reset complete")
            else:
                logger.debug("Singleton reset called but no instance existed")


def get_plot_service() -> PlotService:
    """
    Get the singleton PlotService instance.

    Public interface for obtaining the application-wide PlotService instance.
    This is the recommended way to access PlotService throughout the codebase.

    Returns
    -------
    PlotService
        The singleton PlotService instance, shared across all callbacks

    Notes
    -----
    **Benefits**:
    - Memory reduction: 37 instances → 1 instance (97% reduction)
    - Shared cache: All callbacks use same GraphCacheManager
    - Faster startup: Single initialization overhead

    **Thread Safety**:
    Safe to call from multiple threads/workers simultaneously. Double-checked
    locking ensures only one instance is created even under concurrent access.
    """
    return PlotServiceSingleton.get_instance()
