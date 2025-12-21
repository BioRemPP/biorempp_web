# API Reference

> **Comprehensive technical documentation for the BioRemPP platform**

---

## Overview

The BioRemPP API is organized following **Clean Architecture** principles with four distinct layers. Each layer has specific responsibilities and maintains clear separation of concerns.

---

## Architecture Layers

### Domain Layer

**Core business logic and domain models**

The Domain Layer contains the essential business rules, entities, and value objects that define the bioremediation analysis domain.

**Components:**

- [**Overview**](domain.md) - Domain layer architecture and principles
- [**Entities**](domain/entities.md) - Core domain entities (Sample, Dataset, Analysis)
- [**Value Objects**](domain/value_objects.md) - Immutable domain values (SampleID, Compound, KEGG Orthology)
- [**Services**](domain/services.md) - Domain services (Validation, Sanitization, Merge)
- [**Repositories**](domain/repositories.md) - Repository interfaces
- [**Plot Strategies**](domain/plot_strategies.md) - Visualization strategy patterns (19 chart types)

[:octicons-arrow-right-24: Explore Domain Layer](domain.md)

---

### Application Layer

**Use case orchestration and application services**

The Application Layer coordinates domain objects to fulfill specific use cases and manages data flow between layers.

**Components:**

- [**Overview**](application.md) - Application layer architecture
- [**Core Handlers**](application/core.md) - Upload, data processing, parsing, export
- [**Services**](application/services.md) - Cache, analysis orchestration, progress tracking
- [**DTOs**](application/dtos.md) - Data Transfer Objects for layer communication
- [**Mappers**](application/mappers.md) - Entity ↔ DTO transformations
- [**Plot Services**](application/plot_services.md) - Plot generation and configuration

[:octicons-arrow-right-24: Explore Application Layer](application.md)

---

### Infrastructure Layer

**External integrations and technical implementations**

The Infrastructure Layer handles external concerns such as data persistence, caching, and configuration management.

**Components:**

- [**Overview**](infrastructure.md) - Infrastructure layer architecture
- [**Cache**](infrastructure/cache.md) - DataFrame, Graph, and Memory caching mechanisms
- [**Configuration**](infrastructure/config.md) - Settings, database config, dependency injection
- [**Persistence**](infrastructure/persistence.md) - Data repositories (BioRemPP, HADEG, KEGG, ToxCSM)

[:octicons-arrow-right-24: Explore Infrastructure Layer](infrastructure.md)

---

### Presentation Layer

**User interface and interaction handling**

The Presentation Layer manages the web interface, user interactions, and data visualization using Dash framework.

**Components:**

- [**Callbacks**](presentation/callbacks.md) - Event handlers for all 8 modules and core functionality
- [**Data Tables**](presentation/data_tables.md) - Interactive AG Grid tables for database results

[:octicons-arrow-right-24: Explore Presentation Layer](presentation/callbacks.md)

---

## Key Design Patterns

### Strategy Pattern
Used extensively for plot generation, allowing dynamic selection of visualization strategies based on use case requirements.

### Factory Pattern
Implements dynamic panel and component creation based on configuration files.

### Repository Pattern
Abstracts data access logic for different databases (BioRemPP, HADEG, KEGG, ToxCSM).

### DTO Pattern
Ensures clean data transfer between architectural layers without exposing internal domain models.

---

## Technology Stack

**Backend:**

- Python 3.11+
- NumPy, Pandas (data processing)
- Scikit-learn (statistical analysis)

**Frontend:**

- Dash 3.3.0+ (web framework)
- Plotly (interactive visualizations)
- Dash Bootstrap Components (UI components)
- AG Grid (data tables)

**Architecture:**

- Clean Architecture
- Domain-Driven Design (DDD)
- SOLID Principles
- NumPy-style Docstrings

---

## Documentation Standards

All code follows strict documentation standards:

- **Docstring Style**: NumPy format
- **Type Hints**: Full type annotations
- **Code Coverage**: 83% overall (1,581 tests)
- **Linting**: Black, isort, mypy

---

## Quick Navigation

<div class="grid cards" markdown>

-   :material-cube:{ .lg .middle } **Domain Layer**

    ---

    Business logic, entities, and domain services

    [:octicons-arrow-right-24: View Domain](domain.md)

-   :material-application:{ .lg .middle } **Application Layer**

    ---

    Use cases, orchestration, and DTOs

    [:octicons-arrow-right-24: View Application](application.md)

-   :material-server:{ .lg .middle } **Infrastructure Layer**

    ---

    Persistence, caching, and configuration

    [:octicons-arrow-right-24: View Infrastructure](infrastructure.md)

-   :material-monitor-dashboard:{ .lg .middle } **Presentation Layer**

    ---

    UI components, callbacks, and data tables

    [:octicons-arrow-right-24: View Presentation](presentation/callbacks.md)

</div>

---

## See Also

- [User Guide](../user-guide/overview.md) - Learn how to use the platform
- [Tests Documentation](../tests.md) - Test suite and coverage information
- [Scientific Methods](../scientific/methods_overview.md) - Methodological foundation
