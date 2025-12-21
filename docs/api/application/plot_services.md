# Plot Services

Application Layer - Plot Services Package.

This package provides services for managing plot generation, configuration loading,
and factory pattern implementation for chart creation across all use cases.

## Modules

- **[Plot Service](plot_services/plot_service.md)**: Main service orchestrating plot generation
- **[Plot Factory](plot_services/plot_factory.md)**: Factory for creating plot strategies
- **[Plot Config Loader](plot_services/plot_config_loader.md)**: Loads plot configurations from YAML
- **[Singleton](plot_services/singleton.md)**: Singleton pattern implementation for plot service

## Architecture

The plot services follow the Strategy Pattern and Factory Pattern to provide flexible
and extensible chart generation capabilities.

## Package Overview

::: src.application.plot_services
    options:
      show_root_heading: false
      show_root_toc_entry: false
      show_source: false
      heading_level: 2
      members: false
      show_if_no_docstring: true

---
## PlotService

::: src.application.plot_services.plot_service.PlotService
    options:
      show_source: true
      heading_level: 3

---
## PlotFactory

::: src.application.plot_services.plot_factory.PlotFactory
    options:
      show_source: true
      heading_level: 3

---
## PlotConfigLoader

::: src.application.plot_services.plot_config_loader.PlotConfigLoader
    options:
      show_source: true
      heading_level: 3

---

