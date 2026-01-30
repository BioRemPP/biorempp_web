# syntax=docker/dockerfile:1.4
# ============================================================================
# BioRemPP v1.0.3 - Optimized Multi-Stage Dockerfile with Cache
# ============================================================================
# Supports: Development | Production
#
# Usage:
#   Development:  docker build -f .docker/Dockerfile --target development -t biorempp:dev .
#   Production:   docker build -f .docker/Dockerfile --target production -t biorempp:prod .
#
# Cache Optimizations:
#   - BuildKit cache mounts for pip downloads
#   - Optimized COPY order (deps before code)
#   - Rebuild on code change: ~15s (vs ~2min without cache)
#
# IMPORTANT: Development tools (pytest, black, mypy, mkdocs) are NOT included.
#            Install them locally: pip install -e ".[dev,docs,profiling]"
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
# STAGE: base-build
# Base image WITH build tools (gcc, g++, make) for compiling dependencies
# Used by: builder, development
# ============================================================================
FROM python:${PYTHON_VERSION}-${DEBIAN_VERSION} AS base-build

ARG APP_USER
ARG APP_UID
ARG APP_GID

# OPTIMIZED: Removed PIP_NO_CACHE_DIR to allow caching
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    DEBIAN_FRONTEND=noninteractive

# Install build tools and system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    make \
    git \
    curl \
    ca-certificates \
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
# Compiles wheels for production (transient stage, not in final image)
# ============================================================================
FROM base-build AS builder

ARG APP_USER

# OPTIMIZED: Copy ONLY dependency files first (change rarely)
COPY --chown=${APP_USER}:${APP_USER} pyproject.toml README.md ./

# Create full package structure for setuptools
# Must match packages defined in pyproject.toml
RUN mkdir -p src/domain src/application src/presentation src/infrastructure \
             src/shared src/data_tables src/assets config && \
    touch src/__init__.py src/domain/__init__.py src/application/__init__.py \
          src/presentation/__init__.py src/infrastructure/__init__.py \
          src/shared/__init__.py src/data_tables/__init__.py src/assets/__init__.py \
          config/__init__.py

# OPTIMIZED: Build wheels with BuildKit cache mount
# Cache persists between builds, avoiding re-downloads
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --upgrade pip setuptools wheel build && \
    pip wheel --wheel-dir=/wheels ".[runtime-full]"

# ============================================================================
# STAGE: runtime
# Slim base image WITHOUT build tools (for production)
# Smaller footprint, better security
# ============================================================================
FROM python:${PYTHON_VERSION}-${DEBIAN_VERSION} AS runtime

ARG APP_USER
ARG APP_UID
ARG APP_GID

# OPTIMIZED: Removed PIP_NO_CACHE_DIR
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    DEBIAN_FRONTEND=noninteractive

# Install ONLY runtime dependencies (NO gcc, g++, make)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
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
# STAGE: development
# Development container with hot-reload support
# Includes build tools (for installing new packages during development)
# ============================================================================
FROM base-build AS development

ARG APP_USER

# Development environment variables
ENV BIOREMPP_ENV=development \
    BIOREMPP_DEBUG=True \
    BIOREMPP_HOT_RELOAD=True \
    BIOREMPP_HOST=0.0.0.0 \
    BIOREMPP_PORT=8050 \
    PYTHONPATH=/app

# ==========================================================================
# OPTIMIZED COPY ORDER: Dependencies BEFORE source code
# This ensures pip install layer is cached when only code changes
# ==========================================================================

# Step 1: Copy ONLY dependency definition file (changes rarely)
COPY --chown=${APP_USER}:${APP_USER} pyproject.toml README.md ./

# Step 2: Create full package structure for setuptools
# Must match packages defined in pyproject.toml
RUN mkdir -p src/domain src/application src/presentation src/infrastructure \
             src/shared src/data_tables src/assets config && \
    touch src/__init__.py src/domain/__init__.py src/application/__init__.py \
          src/presentation/__init__.py src/infrastructure/__init__.py \
          src/shared/__init__.py src/data_tables/__init__.py src/assets/__init__.py \
          config/__init__.py

# Step 3: Install dependencies with BuildKit cache mount
# THIS LAYER IS CACHED if pyproject.toml hasn't changed
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --upgrade pip setuptools wheel && \
    pip install ".[runtime]"

# Step 4: NOW copy source code (doesn't invalidate pip cache)
COPY --chown=${APP_USER}:${APP_USER} src ./src
COPY --chown=${APP_USER}:${APP_USER} config ./config

# Step 5: Copy remaining application files
COPY --chown=${APP_USER}:${APP_USER} . .

# Switch to non-root user
USER ${APP_USER}

# Expose development port
EXPOSE 8050

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:8050/_health || exit 1

# Image labels and metadata
LABEL org.opencontainers.image.title="BioRemPP Web Application (Development)" \
      org.opencontainers.image.description="Bioremediation Potential Profile - Optimized dev image with cache. Install dev tools locally: pip install -e '.[dev,docs,profiling]'" \
      org.opencontainers.image.authors="biorempp@gmail.com" \
      org.opencontainers.image.url="https://biorempp.github.io" \
      org.opencontainers.image.documentation="https://biormepp-web.readthedocs.io/en/latest/" \
      org.opencontainers.image.source="https://github.com/biorempp/biorempp_web" \
      org.opencontainers.image.version="1.0.3-beta" \
      org.opencontainers.image.licenses="Apache-2.0" \
      org.opencontainers.image.vendor="BioRemPP Development Team" \
      maintainer="biorempp@gmail.com"

# Development command (hot-reload enabled via volume mount)
CMD ["python", "biorempp_app.py"]

# ============================================================================
# STAGE: production
# Production-ready image optimized for size and security
# NO build tools (gcc, g++, make) - uses pre-compiled wheels
# ============================================================================
FROM runtime AS production

ARG APP_USER

# Production environment variables
ENV BIOREMPP_ENV=production \
    BIOREMPP_DEBUG=False \
    BIOREMPP_HOT_RELOAD=False \
    BIOREMPP_HOST=0.0.0.0 \
    BIOREMPP_PORT=8080 \
    PYTHONPATH=/app

# Install wheels with BuildKit cache mount
COPY --from=builder /wheels /tmp/wheels
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --upgrade pip setuptools wheel && \
    pip install --no-index --find-links=/tmp/wheels /tmp/wheels/*.whl && \
    rm -rf /tmp/wheels

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

# Image labels and metadata
LABEL org.opencontainers.image.title="BioRemPP Web Application (Production)" \
      org.opencontainers.image.description="Bioremediation Potential Profile - Optimized production image without build tools" \
      org.opencontainers.image.authors="biorempp@gmail.com" \
      org.opencontainers.image.url="https://biorempp.github.io" \
      org.opencontainers.image.documentation="https://biormepp-web.readthedocs.io/en/latest/" \
      org.opencontainers.image.source="https://github.com/biorempp/biorempp_web" \
      org.opencontainers.image.version="1.0.3-beta" \
      org.opencontainers.image.licenses="Apache-2.0" \
      org.opencontainers.image.vendor="BioRemPP Development Team" \
      maintainer="biorempp@gmail.com"

# Default command (can be overridden)
CMD ["gunicorn", "wsgi:server", "-c", "gunicorn_config.py"]
