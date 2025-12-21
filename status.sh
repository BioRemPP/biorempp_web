#!/bin/bash
# ============================================================================
# BioRemPP v1.0 - Status Script
# ============================================================================
# Verifica o status da aplicação BioRemPP
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
ENV_FILE="$SCRIPT_DIR/.env"
LOG_DIR="$SCRIPT_DIR/logs"

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

# Main
echo ""
echo -e "${BLUE}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║${NC}           ${CYAN}BioRemPP v1.0 - Server Status${NC}                    ${BLUE}║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Check PID file
if [[ ! -f "$PIDFILE" ]]; then
    echo -e "${RED}✗${NC} Application: ${RED}NOT RUNNING${NC} (no PID file)"
    echo ""

    # Check for orphaned processes
    PIDS=$(pgrep -f "gunicorn.*biorempp" || true)
    if [[ -n "$PIDS" ]]; then
        log_warn "Found orphaned processes:"
        ps -f -p $PIDS
        echo ""
        log_info "Run ./stop.sh to clean up, then ./start.sh to restart"
    else
        log_info "Run ./start.sh to start the application"
    fi

    exit 1
fi

# Read PID
PID=$(cat "$PIDFILE")

# Check if process is running
if ! ps -p "$PID" > /dev/null 2>&1; then
    echo -e "${RED}✗${NC} Application: ${RED}NOT RUNNING${NC} (stale PID file)"
    echo -e "  PID file exists but process $PID is not running"
    echo ""
    log_info "Run ./start.sh to restart the application"
    exit 1
fi

# Application is running
echo -e "${GREEN}✓${NC} Application: ${GREEN}RUNNING${NC}"
echo ""

# Show process information
echo -e "${CYAN}Process Information:${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Master process
echo -e "${BLUE}Master Process:${NC}"
ps -f -p "$PID" | tail -n +2
echo ""

# Worker processes
WORKERS=$(pgrep -P "$PID" || true)
if [[ -n "$WORKERS" ]]; then
    WORKER_COUNT=$(echo "$WORKERS" | wc -l)
    echo -e "${BLUE}Worker Processes:${NC} ($WORKER_COUNT workers)"
    ps -f -p $(echo $WORKERS | tr ' ' ',') | tail -n +2
else
    echo -e "${YELLOW}No worker processes found${NC}"
fi

echo ""

# Load environment configuration
if [[ -f "$ENV_FILE" ]]; then
    echo -e "${CYAN}Configuration:${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

    source "$ENV_FILE"

    echo "  Environment:      ${BIOREMPP_ENV:-production}"
    echo "  Host:             ${BIOREMPP_HOST:-0.0.0.0}"
    echo "  Port:             ${BIOREMPP_PORT:-8080}"
    echo "  Workers:          ${BIOREMPP_WORKERS:-4}"
    echo "  Worker Class:     ${BIOREMPP_WORKER_CLASS:-gevent}"
    echo "  Timeout:          ${BIOREMPP_TIMEOUT:-300}s"
    echo "  Log Level:        ${BIOREMPP_LOG_LEVEL:-WARNING}"
    echo ""
fi

# Resource usage
echo -e "${CYAN}Resource Usage:${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Get all processes (master + workers)
ALL_PIDS="$PID"
if [[ -n "$WORKERS" ]]; then
    ALL_PIDS="$PID $(echo $WORKERS | tr '\n' ' ')"
fi

# Calculate total CPU and memory
TOTAL_CPU=0
TOTAL_MEM=0
TOTAL_RSS=0

for P in $ALL_PIDS; do
    if ps -p "$P" > /dev/null 2>&1; then
        # Get CPU and memory for this process
        PROC_INFO=$(ps -p "$P" -o %cpu,rss | tail -n 1)
        PROC_CPU=$(echo "$PROC_INFO" | awk '{print $1}')
        PROC_RSS=$(echo "$PROC_INFO" | awk '{print $2}')

        # Add to totals (using bc for float arithmetic)
        TOTAL_CPU=$(echo "$TOTAL_CPU + $PROC_CPU" | bc)
        TOTAL_RSS=$((TOTAL_RSS + PROC_RSS))
    fi
done

# Convert RSS to MB
TOTAL_MEM=$(echo "scale=2; $TOTAL_RSS / 1024" | bc)

echo "  Total CPU:        ${TOTAL_CPU}%"
echo "  Total Memory:     ${TOTAL_MEM} MB"
echo ""

# Check health endpoint
echo -e "${CYAN}Health Check:${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

PORT="${BIOREMPP_PORT:-8080}"
HEALTH_URL="http://localhost:$PORT/health"

if command -v curl &> /dev/null; then
    HEALTH_RESPONSE=$(curl -s -w "\n%{http_code}" "$HEALTH_URL" 2>/dev/null || echo "failed")
    HTTP_CODE=$(echo "$HEALTH_RESPONSE" | tail -n 1)
    BODY=$(echo "$HEALTH_RESPONSE" | head -n -1)

    if [[ "$HTTP_CODE" == "200" ]]; then
        echo -e "  Status: ${GREEN}✓ HEALTHY${NC}"
        echo "  URL:    $HEALTH_URL"
        if [[ -n "$BODY" ]]; then
            echo "  Response: $BODY"
        fi
    else
        echo -e "  Status: ${RED}✗ UNHEALTHY${NC} (HTTP $HTTP_CODE)"
        echo "  URL:    $HEALTH_URL"
    fi
else
    echo -e "  ${YELLOW}curl not available - skipping health check${NC}"
    echo "  URL:    $HEALTH_URL"
fi

echo ""

# Log files
echo -e "${CYAN}Recent Logs:${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [[ -d "$LOG_DIR" ]]; then
    # Find latest log files
    ACCESS_LOG="$LOG_DIR/gunicorn_access.log"
    ERROR_LOG="$LOG_DIR/gunicorn_error.log"

    if [[ -f "$ERROR_LOG" ]]; then
        ERROR_COUNT=$(wc -l < "$ERROR_LOG" 2>/dev/null || echo "0")
        ERROR_SIZE=$(du -h "$ERROR_LOG" 2>/dev/null | cut -f1 || echo "0")
        echo "  Error Log:   $ERROR_LOG ($ERROR_COUNT lines, $ERROR_SIZE)"

        # Show last error (if any)
        if [[ -s "$ERROR_LOG" ]]; then
            LAST_ERROR=$(tail -n 1 "$ERROR_LOG")
            echo "  Last Entry:  $LAST_ERROR"
        fi
    fi

    echo ""

    if [[ -f "$ACCESS_LOG" ]]; then
        ACCESS_COUNT=$(wc -l < "$ACCESS_LOG" 2>/dev/null || echo "0")
        ACCESS_SIZE=$(du -h "$ACCESS_LOG" 2>/dev/null | cut -f1 || echo "0")
        echo "  Access Log:  $ACCESS_LOG ($ACCESS_COUNT requests, $ACCESS_SIZE)"

        # Show last access (if any)
        if [[ -s "$ACCESS_LOG" ]]; then
            LAST_ACCESS=$(tail -n 1 "$ACCESS_LOG")
            echo "  Last Entry:  $LAST_ACCESS"
        fi
    fi
else
    echo "  ${YELLOW}Log directory not found${NC}"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Useful commands
echo -e "${CYAN}Useful Commands:${NC}"
echo "  View logs:    ./logs.sh"
echo "  Stop server:  ./stop.sh"
echo "  Restart:      ./restart.sh"
echo ""

exit 0
