#!/bin/bash
# ============================================================================
# BioRemPP v1.0 - Health Check Script
# ============================================================================
# Container health monitoring for Docker HEALTHCHECK
# ============================================================================

set -e

# Health check endpoint
HEALTH_HOST=${BIOREMPP_HEALTH_HOST:-127.0.0.1}
HEALTH_PORT=${BIOREMPP_PORT:-8080}
HEALTH_URL="http://${HEALTH_HOST}:${HEALTH_PORT}/health"

# Alternative: check if main app route is accessible
# HEALTH_URL="http://${BIOREMPP_HOST:-0.0.0.0}:${BIOREMPP_PORT:-8080}/"

# Timeout for health check (seconds)
TIMEOUT=${HEALTHCHECK_TIMEOUT:-5}

# Perform health check using curl
if curl --fail --silent --max-time "$TIMEOUT" "$HEALTH_URL" > /dev/null 2>&1; then
    echo "[HEALTH] OK - Application responding at ${HEALTH_URL}"
    exit 0
else
    echo "[HEALTH] FAIL - Application not responding at ${HEALTH_URL}"
    exit 1
fi
