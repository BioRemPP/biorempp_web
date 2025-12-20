# Application Services

Application Layer - Services Package.

This package contains application services that provide high-level business operations
and coordinate between different layers of the application.

## Modules

- **[Cache Service](services/cache_service.md)**: Manages caching operations for improved performance
- **[Analysis Orchestrator](services/analysis_orchestrator.md)**: Orchestrates complex analysis workflows
- **[Progress Tracker](services/progress_tracker.md)**: Tracks and reports processing progress

## Package Overview

::: src.application.services
    options:
      show_root_heading: false
      show_root_toc_entry: false
      show_source: false
      heading_level: 2
      members: false
      show_if_no_docstring: true

---
## AnalysisOrchestrator

::: src.application.services.analysis_orchestrator.AnalysisOrchestrator
    options:
      show_source: true
      heading_level: 3

### AnalysisSessionDTO

::: src.application.services.analysis_orchestrator.AnalysisSessionDTO
    options:
      show_source: false
      heading_level: 4

---
## CacheService

::: src.application.services.cache_service.CacheService
    options:
      show_source: true
      heading_level: 3

---
## ProgressTracker

::: src.application.services.progress_tracker.ProgressTracker
    options:
      show_source: true
      heading_level: 3

---

