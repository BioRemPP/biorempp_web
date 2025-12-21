# Logging

Shared Layer - Logging Package.

Comprehensive logging infrastructure providing structured logging, performance monitoring, and error tracking across the application.

## Overview

The logging package provides:

- **Configuration management**: Centralized logging setup
- **Decorators**: Non-intrusive function logging
- **Custom formatters**: Structured log output
- **Custom handlers**: Flexible log destinations
- **Context tracking**: Request and session context

## Modules

- **[Config](logging/config.md)**: Logging configuration and setup
- **[Decorators](logging/decorators.md)**: Function logging decorators
- **[Formatters](logging/formatters.md)**: Custom log formatters
- **[Handlers](logging/handlers.md)**: Custom log handlers

## Features

### Structured Logging

All logs follow a consistent structure:

- Timestamp with timezone
- Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- Module and function name
- Message with context
- Stack trace for exceptions

### Performance Monitoring

Automatic tracking of:

- Function execution time
- Database query duration
- API call latency
- Cache hit/miss rates

### Error Tracking

Comprehensive error logging:

- Full stack traces
- Exception context
- Request/response details
- User session information

## Package Overview

::: src.shared.logging
    options:
      show_root_heading: false
      show_root_toc_entry: false
      show_source: false
      heading_level: 2
      members: false
      show_if_no_docstring: true
