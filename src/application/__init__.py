"""
Application Layer for BioRemPP Web.

This package contains the application layer components that orchestrate
business logic, coordinate domain entities, and manage application-specific
workflows. The application layer acts as a bridge between the presentation
layer (Dash frontend) and the domain layer (core business logic).

Package Structure
-----------------
application/
    core/           Core operations and handlers
    services/       Application services
    dto/            Data Transfer Objects
    mappers/        Entity-DTO mappers

Notes
-----
This layer implements the Clean Architecture application layer pattern,
ensuring separation of concerns and dependency inversion principles.
All components follow SOLID principles and use dependency injection.

Version
-------
2.0.0
"""

__version__ = "2.0.0"
__all__ = ["core", "services", "dto", "mappers"]
