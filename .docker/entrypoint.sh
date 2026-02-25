#!/bin/bash
# ============================================================================
# BioRemPP v1.0 - Container Entrypoint Script
# ============================================================================
# Validates environment, applies safety checks, and starts application
# ============================================================================

set -e

# ============================================================================
# COLOR DEFINITIONS
# ============================================================================
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# ============================================================================
# LOGGING FUNCTIONS
# ============================================================================
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

# ============================================================================
# STARTUP BANNER
# ============================================================================
echo ""
echo -e "${BLUE}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║${NC}           ${GREEN}BioRemPP v1.0 - Container Startup${NC}                 ${BLUE}║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""

# ============================================================================
# ENVIRONMENT VALIDATION
# ============================================================================
log_step "Validating environment variables..."

validate_env() {
    local var_name=$1
    local var_value=${!var_name}
    local required=${2:-false}
    
    if [ "$required" = "true" ] && [ -z "$var_value" ]; then
        log_error "Required environment variable not set: ${var_name}"
        exit 1
    fi
    
    if [ -n "$var_value" ]; then
        log_info "${var_name}=${var_value}"
    fi
}

# Required variables
validate_env "BIOREMPP_ENV" true
validate_env "BIOREMPP_HOST" true
validate_env "BIOREMPP_PORT" true

# Optional with defaults
BIOREMPP_DEBUG=${BIOREMPP_DEBUG:-False}
BIOREMPP_LOG_LEVEL=${BIOREMPP_LOG_LEVEL:-WARNING}
BIOREMPP_HOT_RELOAD=${BIOREMPP_HOT_RELOAD:-False}

log_info "Environment validation passed"
echo ""

# ============================================================================
# PRODUCTION SAFETY CHECKS
# ============================================================================
if [ "$BIOREMPP_ENV" = "production" ]; then
    log_step "Production mode detected - Applying safety checks..."
    
    # Force debug off
    if [ "$BIOREMPP_DEBUG" != "False" ] && [ "$BIOREMPP_DEBUG" != "false" ]; then
        log_warn "Forcing DEBUG=False in production"
        export BIOREMPP_DEBUG=False
    fi
    
    # Force hot reload off
    if [ "$BIOREMPP_HOT_RELOAD" != "False" ] && [ "$BIOREMPP_HOT_RELOAD" != "false" ]; then
        log_warn "Forcing HOT_RELOAD=False in production"
        export BIOREMPP_HOT_RELOAD=False
    fi
    
    # Force log level to WARNING or higher
    if [ "$BIOREMPP_LOG_LEVEL" = "DEBUG" ]; then
        log_warn "Forcing LOG_LEVEL=WARNING in production"
        export BIOREMPP_LOG_LEVEL=WARNING
    fi
    
    # Check for default/insecure secret keys
    if [ -n "$SECRET_KEY" ]; then
        if [ "$SECRET_KEY" = "dev-secret-key-not-secure" ] || \
           [ "$SECRET_KEY" = "dev-secret-key-not-secure-for-development-only" ] || \
           [ "$SECRET_KEY" = "change-me-in-production-use-secrets-token-hex" ] || \
           [ "$SECRET_KEY" = "REPLACE_WITH_REAL_SECRET_FROM_DOCKER_SECRETS" ] || \
           [ "$SECRET_KEY" = "REPLACE_WITH_SECURE_KEY_MINIMUM_32_CHARS_HEX" ]; then
            log_error "Insecure SECRET_KEY detected in production!"
            log_error "Generate a secure key with: python -c \"import secrets; print(secrets.token_hex(32))\""
            log_warn "Continuing anyway for testing purposes - DO NOT USE IN REAL PRODUCTION!"
        fi
    fi
    
    log_info "Production safety checks passed"
    echo ""
fi

# ============================================================================
# DIRECTORY SETUP
# ============================================================================
log_step "Setting up application directories..."

mkdir -p /app/logs /app/data /app/cache 2>/dev/null || true

# Try to set ownership (may fail if not root, which is OK)
if [ "$(id -u)" = "0" ]; then
    chown -R ${APP_USER:-biorempp}:${APP_USER:-biorempp} /app/logs /app/data /app/cache 2>/dev/null || true
fi

# Ensure cache root is writable for runtime components (Diskcache, callbacks).
cache_root="${BIOREMPP_CACHE_DIR:-/app/cache}"
if mkdir -p "$cache_root" 2>/dev/null && touch "$cache_root/.cache_write_test" 2>/dev/null; then
    rm -f "$cache_root/.cache_write_test" 2>/dev/null || true
    log_info "Cache directory writable: ${cache_root}"
else
    fallback_cache="/tmp/biorempp-cache"
    mkdir -p "$fallback_cache"
    export BIOREMPP_CACHE_DIR="$fallback_cache"
    log_warn "Cache directory not writable (${cache_root}); fallback to ${fallback_cache}"
fi

log_info "Directories ready"
echo ""

# ============================================================================
# DATABASE MIGRATIONS (if applicable)
# ============================================================================
# Uncomment if using database migrations
# if [ "$BIOREMPP_ENV" = "production" ] && [ "$RUN_MIGRATIONS" = "true" ]; then
#     log_step "Running database migrations..."
#     python manage.py migrate --noinput
#     log_info "Migrations complete"
#     echo ""
# fi

# ============================================================================
# RESUME BACKEND HEALTH GATE (optional fail-fast for Redis)
# ============================================================================
resume_backend=$(echo "${BIOREMPP_RESUME_BACKEND:-diskcache}" | tr '[:upper:]' '[:lower:]')
resume_redis_healthcheck=$(echo "${BIOREMPP_RESUME_REDIS_HEALTHCHECK:-false}" | tr '[:upper:]' '[:lower:]')

if [ "$resume_backend" = "redis" ] && [ "$resume_redis_healthcheck" = "true" ]; then
    log_step "Checking Redis resume backend availability..."

    resume_redis_host=${BIOREMPP_RESUME_REDIS_HOST:-${REDIS_HOST:-redis}}
    resume_redis_port=${BIOREMPP_RESUME_REDIS_PORT:-${REDIS_PORT:-6379}}
    resume_redis_db=${BIOREMPP_RESUME_REDIS_DB:-${REDIS_DB:-0}}
    resume_redis_password=${BIOREMPP_RESUME_REDIS_PASSWORD:-${REDIS_PASSWORD:-}}
    resume_redis_timeout=${BIOREMPP_RESUME_REDIS_HEALTHCHECK_TIMEOUT_SECONDS:-20}

    python - "$resume_redis_host" "$resume_redis_port" "$resume_redis_db" "$resume_redis_password" "$resume_redis_timeout" <<'PY'
import sys
import time

host = sys.argv[1]
port = int(sys.argv[2])
db = int(sys.argv[3])
password = sys.argv[4] or None
timeout_seconds = float(sys.argv[5])

try:
    import redis
except Exception as exc:  # pragma: no cover
    print(f"redis dependency unavailable: {exc}", file=sys.stderr)
    sys.exit(1)

deadline = time.time() + timeout_seconds
last_error = None
while time.time() < deadline:
    try:
        client = redis.Redis(
            host=host,
            port=port,
            db=db,
            password=password,
            socket_connect_timeout=2,
            socket_timeout=2,
            decode_responses=False,
        )
        if client.ping():
            sys.exit(0)
    except Exception as exc:  # pragma: no cover
        last_error = exc
        time.sleep(1)

print(f"resume redis unavailable: {last_error}", file=sys.stderr)
sys.exit(1)
PY

    if [ $? -ne 0 ]; then
        log_error "Redis resume backend unavailable; aborting startup"
        exit 1
    fi

    log_info "Redis resume backend is available"
    echo ""
fi

# ============================================================================
# SSL CERTIFICATE CHECK (for HTTPS)
# ============================================================================
if [ "$BIOREMPP_ENV" = "production" ] && [ "$ENABLE_HTTPS" = "true" ]; then
    log_step "Checking SSL certificates..."
    
    if [ -d "/etc/letsencrypt/live/$DOMAIN" ]; then
        log_info "SSL certificates found for ${DOMAIN}"
    else
        log_warn "SSL certificates not found. HTTPS will not be available."
        log_warn "Run SSL setup: .scripts/docker/ssl-setup.sh ${DOMAIN}"
    fi
    echo ""
fi

# ============================================================================
# STARTUP SUMMARY
# ============================================================================
log_step "Starting BioRemPP Application..."
echo ""
echo -e "${GREEN}Configuration Summary:${NC}"
echo -e "  ${BLUE}Environment:${NC}    ${BIOREMPP_ENV}"
echo -e "  ${BLUE}Host:${NC}           ${BIOREMPP_HOST}:${BIOREMPP_PORT}"
echo -e "  ${BLUE}Debug Mode:${NC}     ${BIOREMPP_DEBUG}"
echo -e "  ${BLUE}Hot Reload:${NC}     ${BIOREMPP_HOT_RELOAD}"
echo -e "  ${BLUE}Log Level:${NC}      ${BIOREMPP_LOG_LEVEL}"
echo -e "  ${BLUE}Resume Backend:${NC} ${BIOREMPP_RESUME_BACKEND:-diskcache}"
if [ -n "$BIOREMPP_WORKERS" ]; then
    echo -e "  ${BLUE}Workers:${NC}        ${BIOREMPP_WORKERS}"
    echo -e "  ${BLUE}Worker Class:${NC}   ${BIOREMPP_WORKER_CLASS:-gevent}"
fi
echo ""

log_info "Application starting..."
echo ""

# ============================================================================
# START APPLICATION
# ============================================================================
# Execute CMD
exec "$@"
