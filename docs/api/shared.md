# Shared Layer

The Shared Layer provides cross-cutting concerns and utilities used across all application layers, including logging, exceptions, and common utilities.

## Overview

The shared layer contains:

- **Exception handling**: Custom exception classes for domain-specific errors
- **Logging utilities**: Centralized logging configuration and utilities
- **Common utilities**: Shared helper functions and utilities
- **Cross-cutting concerns**: Functionality used across multiple layers

## Architecture Principles

### Cross-Cutting Concerns

The shared layer implements cross-cutting concerns that don't belong to any specific layer:

- Available to all layers (Domain, Application, Infrastructure, Presentation)
- No dependencies on other application layers
- Focuses on technical utilities, not business logic

### Dependency Direction

The shared layer:

- Has no dependencies on other application layers
- Can be used by any layer
- Contains only technical utilities, not domain knowledge

## Package Structure

### Exception Handling

Custom exception classes for specific error scenarios:

- **[Exceptions](shared/exceptions.md)**: Domain-specific exception classes

### Logging

Comprehensive logging infrastructure:

- **[Logger Utils](shared/logger_utils.md)**: Logging utility functions
- **[Logging Config](shared/logging/config.md)**: Logging configuration
- **[Logging Decorators](shared/logging/decorators.md)**: Function logging decorators
- **[Logging Formatters](shared/logging/formatters.md)**: Custom log formatters
- **[Logging Handlers](shared/logging/handlers.md)**: Custom log handlers

## Design Patterns

### Decorator Pattern

Logging decorators provide non-intrusive logging:

- Function entry/exit logging
- Exception logging
- Performance monitoring
- Automatic context capture

### Strategy Pattern

Custom formatters and handlers allow flexible logging configuration:

- Different formats for different environments
- Multiple output destinations
- Configurable log levels

## Logging Features

The logging infrastructure provides:

- **Structured logging**: Consistent log format across application
- **Context tracking**: Request/session context in logs
- **Performance monitoring**: Execution time tracking
- **Error tracking**: Exception capture and formatting
- **Multi-destination**: Console, file, and external service outputs

## Exception Handling

Custom exceptions provide:

- **Domain-specific errors**: Clear error semantics
- **Error context**: Additional information for debugging
- **Type safety**: Specific exception types for different scenarios
- **Clean propagation**: Proper error handling across layers

## Navigation

Explore shared layer components:

- **[Exceptions](shared/exceptions.md)**: Exception classes
- **[Logger Utils](shared/logger_utils.md)**: Logging utilities
- **[Logging](shared/logging.md)**: Logging infrastructure
