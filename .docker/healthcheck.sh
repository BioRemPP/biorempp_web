#!/bin/bash
# ============================================================================
# BioRemPP v1.0 - Health Check Script
# ============================================================================
# Container health monitoring for Docker HEALTHCHECK
# ============================================================================

set -e

# Health check endpoint (default for Dash apps)
HEALTH_URL="http://${BIOREMPP_HOST:-0.0.0.0}:${BIOREMPP_PORT:-8080}/_dash-update-component"

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
