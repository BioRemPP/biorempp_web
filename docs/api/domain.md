
# Domain Layer

The Domain Layer contains the core business logic of BioRemPP, implementing Domain-Driven Design (DDD) principles for bioremediation potential analysis.

## Overview

The domain layer is the heart of the application, containing:

- **Pure business logic** - No framework dependencies
- **Domain models** - Entities and value objects representing biological concepts
- **Domain services** - Business operations that don't belong to entities
- **Plot strategies** - Visualization algorithms following the Strategy Pattern
- **Repository interfaces** - Contracts for data access

## Architecture

### Domain-Driven Design Principles

The domain layer follows DDD tactical patterns:

- **Entities**: Objects with identity (Sample, Dataset, Analysis, MergedData)
- **Value Objects**: Immutable objects defined by attributes (SampleId, Compound, KEGGOrthology, Pathway)
- **Domain Services**: Stateless services for complex operations (Validation, Sanitization, Merge)
- **Repositories**: Interfaces for persistence abstraction
- **Strategies**: Pluggable algorithms for plot generation

### Clean Architecture

The domain layer is:

- **Independent**: No dependencies on external frameworks or infrastructure
- **Testable**: All business logic can be unit tested in isolation
- **Focused**: Contains only business rules and domain concepts
- **Stable**: Changes rarely, driven only by business requirements

## Package Structure

### [Entities](domain/entities.md)

Business objects with unique identity and lifecycle:

- **Sample**: Represents a biological sample with genomic data
- **Dataset**: Collection of samples with metadata
- **Analysis**: Results of bioremediation potential analysis
- **MergedData**: Combined data from multiple databases (KEGG, UniProt, etc.)

### [Value Objects](domain/value_objects.md)

Immutable objects representing descriptive aspects:

- **SampleId**: Unique identifier for samples
- **Compound**: Chemical compound information
- **KEGGOrthology**: KO numbers and functional annotations
- **Pathway**: Metabolic pathway data

### [Services](domain/services.md)

Stateless services implementing domain logic:

- **ValidationService**: Validates domain rules and invariants
- **SanitizationService**: Sanitizes and normalizes data
- **MergeService**: Merges data from multiple sources

### [Repositories](domain/repositories.md)

Interfaces defining data access contracts:

- Abstract interfaces for persistence operations
- Implementation provided by Infrastructure Layer
- Enables dependency inversion and testability

### [Plot Strategies](domain/plot_strategies.md)

Visualization algorithms following Strategy Pattern:

- **Base Strategy**: Abstract base class defining the template method
- **Chart Strategies**: 19 concrete implementations for different plot types
- Encapsulates plotting logic separate from UI concerns

## Design Patterns

### Strategy Pattern

Used for plot generation to enable:

- Runtime selection of visualization algorithms
- Easy addition of new plot types
- Separation of plotting logic from application layer

### Repository Pattern

Used for data access to provide:

- Abstraction over persistence mechanisms
- Testability through interface contracts
- Independence from infrastructure details

### Template Method Pattern

Used in base plot strategy to:

- Define the skeleton of plot creation
- Allow subclasses to customize specific steps
- Ensure consistent execution flow

## Type Safety

All domain code uses:

- **Type hints**: Full type annotations for all functions and methods
- **NumPy docstrings**: Comprehensive documentation with parameter types
- **Validation**: Runtime validation of business rules

## Testing

The domain layer emphasizes:

- **Unit tests**: All business logic is unit testable
- **No mocks needed**: Pure functions and minimal dependencies
- **Fast execution**: Tests run quickly without external dependencies

## Navigation

Explore the domain layer components:

- **[Entities](domain/entities.md)**: Business objects with identity
- **[Value Objects](domain/value_objects.md)**: Immutable descriptive objects  
- **[Services](domain/services.md)**: Domain business logic
- **[Repositories](domain/repositories.md)**: Data access interfaces
- **[Plot Strategies](domain/plot_strategies.md)**: Visualization algorithms
