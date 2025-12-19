"""
Application Services Module.

This module contains application-level services that provide cross-cutting
concerns and coordinate complex operations across multiple domain entities.
Services handle caching, progress tracking, and analysis orchestration.

Classes
-------
CacheService
    Manages application-level caching with hash-based keys
ProgressTracker
    Tracks processing progress with weighted stages (simplified, no threading)
AnalysisOrchestrator
    Orchestrates complex multi-step analysis workflows

Notes
-----
Services in this module are stateless and use dependency injection.
Progress tracking is simplified without threading, as Dash is single-threaded.
"""

__all__ = [
    "CacheService",
    "ProgressTracker",
    "AnalysisOrchestrator",
]
