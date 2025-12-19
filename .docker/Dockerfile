# ============================================================================
# BioRemPP v1.0 - Unified Multi-Stage Dockerfile
# ============================================================================
# Supports: Development | Production | Testing
# Usage:
#   Development:  docker build --target development -t biorempp:dev .
#   Production:   docker build --target production -t biorempp:prod .
#   Custom:       docker build --build-arg PYTHON_VERSION=3.12 -t biorempp:latest .
# ============================================================================

# ============================================================================
# BUILD ARGUMENTS
# ============================================================================
ARG PYTHON_VERSION=3.11
ARG DEBIAN_VERSION=slim-bookworm
ARG APP_USER=biorempp
ARG APP_UID=1000
ARG APP_GID=1000

# ============================================================================
# STAGE: base
# Base image with system dependencies and non-root user
# ============================================================================
FROM python:${PYTHON_VERSION}-${DEBIAN_VERSION} AS base

# Build arguments
ARG APP_USER
ARG APP_UID
ARG APP_GID

# Environment variables for Python
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    DEBIAN_FRONTEND=noninteractive

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    # Build essentials
    gcc \
    g++ \
    make \
    # Git for pip installs from git repos
    git \
    # curl for health checks
    curl \
    # ca-certificates for HTTPS
    ca-certificates \
    # Clean up
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Create non-root user and group
RUN groupadd -g ${APP_GID} ${APP_USER} && \
    useradd -m -u ${APP_UID} -g ${APP_GID} -s /bin/bash ${APP_USER}

# Create application directories
RUN mkdir -p /app /app/logs /app/data && \
    chown -R ${APP_USER}:${APP_USER} /app

WORKDIR /app

# ============================================================================
# STAGE: builder
# Build dependencies and compile wheels
# ============================================================================
FROM base AS builder

ARG APP_USER

# Upgrade pip, setuptools, wheel
RUN pip install --upgrade pip setuptools wheel

# Copy dependency files and package directories (for setuptools)
COPY --chown=${APP_USER}:${APP_USER} pyproject.toml README.md ./
COPY --chown=${APP_USER}:${APP_USER} src ./src
COPY --chown=${APP_USER}:${APP_USER} config ./config

# Install build dependencies
RUN pip install build

# Pre-download all dependencies as wheels (core + production extras)
RUN pip wheel --no-cache-dir --wheel-dir=/wheels \
    ".[server,cache,compression]"

# ============================================================================
# STAGE: development
# Development environment with hot-reload and dev tools
# ============================================================================
FROM base AS development

ARG APP_USER

# Development environment variables
ENV BIOREMPP_ENV=development \
    BIOREMPP_DEBUG=True \
    BIOREMPP_HOT_RELOAD=True \
    BIOREMPP_HOST=0.0.0.0 \
    BIOREMPP_PORT=8050 \
    PYTHONPATH=/app

# Install development tools
RUN pip install --upgrade pip setuptools wheel

# Copy pyproject.toml and ALL package directories (needed for setuptools)
COPY --chown=${APP_USER}:${APP_USER} pyproject.toml README.md ./
COPY --chown=${APP_USER}:${APP_USER} src ./src
COPY --chown=${APP_USER}:${APP_USER} config ./config

# Install ALL dependencies from pyproject.toml including optional extras
RUN pip install --no-cache-dir ".[dev,docs,profiling,server,cache,compression]"

# Copy remaining application files
COPY --chown=${APP_USER}:${APP_USER} . .

# Switch to non-root user
USER ${APP_USER}

# Expose development port
EXPOSE 8050

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:8050/_health || exit 1

# Development command (hot-reload enabled)
CMD ["python", "biorempp_app.py"]

# ============================================================================
# STAGE: production
# Production-ready image with minimal size and security hardening
# ============================================================================
FROM base AS production

ARG APP_USER

# Production environment variables
ENV BIOREMPP_ENV=production \
    BIOREMPP_DEBUG=False \
    BIOREMPP_HOT_RELOAD=False \
    BIOREMPP_HOST=0.0.0.0 \
    BIOREMPP_PORT=8080 \
    PYTHONPATH=/app

# Copy pre-built wheels from builder
COPY --from=builder /wheels /wheels

# Upgrade pip and install wheels
RUN pip install --upgrade pip setuptools wheel && \
    pip install --no-cache-dir --no-index --find-links=/wheels \
    /wheels/*.whl && \
    rm -rf /wheels

# Copy application source code
COPY --chown=${APP_USER}:${APP_USER} . .

# Copy entrypoint and health check scripts
COPY --chown=${APP_USER}:${APP_USER} .docker/entrypoint.sh /usr/local/bin/entrypoint.sh
COPY --chown=${APP_USER}:${APP_USER} .docker/healthcheck.sh /usr/local/bin/healthcheck.sh

# Make scripts executable
RUN chmod +x /usr/local/bin/entrypoint.sh /usr/local/bin/healthcheck.sh

# Switch to non-root user
USER ${APP_USER}

# Expose production port
EXPOSE 8080

# Health check with custom script
HEALTHCHECK --interval=60s --timeout=30s --start-period=60s --retries=3 \
    CMD /usr/local/bin/healthcheck.sh

# Set entrypoint
ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]

# Default command (can be overridden)
CMD ["gunicorn", "wsgi:server", "-c", "gunicorn_config.py"]

# ============================================================================
# METADATA
# ============================================================================
LABEL maintainer="BioRemPP Development Team" \
    version="1.0.0" \
    description="BioRemPP Web Service - Unified Docker Image" \
    org.opencontainers.image.source="https://github.com/BioRemPP" \
    org.opencontainers.image.licenses="MIT"
