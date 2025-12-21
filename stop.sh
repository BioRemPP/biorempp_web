#!/bin/bash
# ============================================================================
# BioRemPP v1.0 - Stop Script
# ============================================================================
# Para a aplicação BioRemPP de forma graceful
# ============================================================================

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PIDFILE="$SCRIPT_DIR/.biorempp.pid"
APP_NAME="biorempp"

# Functions
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

# Main
echo ""
echo -e "${BLUE}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║${NC}           ${RED}BioRemPP v1.0 - Stop Server${NC}                      ${BLUE}║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""

log_step "Stopping BioRemPP application..."

# Check if PID file exists
if [[ ! -f "$PIDFILE" ]]; then
    log_warn "PID file not found at $PIDFILE"

    # Try to find running processes anyway
    log_info "Searching for running Gunicorn processes..."
    PIDS=$(pgrep -f "gunicorn.*$APP_NAME" || true)

    if [[ -z "$PIDS" ]]; then
        log_info "No running processes found"
        exit 0
    else
        log_warn "Found running processes without PID file:"
        ps -f -p $PIDS

        read -p "Kill these processes? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            for PID in $PIDS; do
                log_info "Killing process $PID..."
                kill -TERM $PID
            done
            sleep 2
            log_info "Processes terminated"
        fi
        exit 0
    fi
fi

# Read PID
PID=$(cat "$PIDFILE")
log_info "Found PID: $PID"

# Check if process is running
if ! ps -p "$PID" > /dev/null 2>&1; then
    log_warn "Process $PID is not running (stale PID file)"
    rm -f "$PIDFILE"
    log_info "Removed stale PID file"
    exit 0
fi

# Try graceful shutdown first (SIGTERM)
log_info "Sending SIGTERM to process $PID (graceful shutdown)..."
kill -TERM "$PID"

# Wait for process to stop (max 30 seconds)
TIMEOUT=30
ELAPSED=0

while ps -p "$PID" > /dev/null 2>&1; do
    if [[ $ELAPSED -ge $TIMEOUT ]]; then
        log_warn "Graceful shutdown timeout (${TIMEOUT}s)"
        log_info "Sending SIGKILL to force stop..."
        kill -KILL "$PID"
        sleep 1
        break
    fi

    echo -n "."
    sleep 1
    ELAPSED=$((ELAPSED + 1))
done

echo ""

# Verify process stopped
if ps -p "$PID" > /dev/null 2>&1; then
    log_error "Failed to stop process $PID"
    exit 1
else
    log_info "${GREEN}✓${NC} Process stopped successfully"
    rm -f "$PIDFILE"
    log_info "Removed PID file"
fi

# Also check for any orphaned worker processes
log_info "Checking for orphaned worker processes..."
WORKERS=$(pgrep -f "gunicorn.*worker" || true)

if [[ -n "$WORKERS" ]]; then
    log_warn "Found orphaned worker processes:"
    ps -f -p $WORKERS

    log_info "Cleaning up workers..."
    for WPID in $WORKERS; do
        kill -TERM $WPID 2>/dev/null || true
    done
    sleep 1
    log_info "Workers cleaned up"
fi

echo ""
log_info "${GREEN}✓${NC} BioRemPP stopped successfully"
echo ""

exit 0
