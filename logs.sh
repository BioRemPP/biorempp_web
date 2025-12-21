#!/bin/bash
# ============================================================================
# BioRemPP v1.0 - Logs Viewer Script
# ============================================================================
# Visualiza logs da aplicação BioRemPP em tempo real
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

show_usage() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --error, -e       Show error log only"
    echo "  --access, -a      Show access log only"
    echo "  --all             Show both logs (default)"
    echo "  --lines, -n NUM   Number of lines to show (default: 50)"
    echo "  --follow, -f      Follow logs in real-time (default)"
    echo "  --static, -s      Show static logs (no follow)"
    echo "  --help, -h        Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0                # Follow both logs"
    echo "  $0 --error -f     # Follow error log"
    echo "  $0 --access -n 100  # Show last 100 access log lines"
    echo ""
}

# Default options
SHOW_ERROR=true
SHOW_ACCESS=true
FOLLOW=true
LINES=50

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --error|-e)
            SHOW_ERROR=true
            SHOW_ACCESS=false
            shift
            ;;
        --access|-a)
            SHOW_ACCESS=true
            SHOW_ERROR=false
            shift
            ;;
        --all)
            SHOW_ERROR=true
            SHOW_ACCESS=true
            shift
            ;;
        --lines|-n)
            LINES="$2"
            shift 2
            ;;
        --follow|-f)
            FOLLOW=true
            shift
            ;;
        --static|-s)
            FOLLOW=false
            shift
            ;;
        --help|-h)
            show_usage
            exit 0
            ;;
        *)
            log_error "Unknown option: $1"
            show_usage
            exit 1
            ;;
    esac
done

# Main
echo ""
echo -e "${BLUE}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║${NC}           ${CYAN}BioRemPP v1.0 - Logs Viewer${NC}                      ${BLUE}║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Check if log directory exists
if [[ ! -d "$LOG_DIR" ]]; then
    log_error "Log directory not found: $LOG_DIR"
    exit 1
fi

# Determine log files
ERROR_LOG="$LOG_DIR/gunicorn_error.log"
ACCESS_LOG="$LOG_DIR/gunicorn_access.log"

# Check if log files exist
if [[ "$SHOW_ERROR" == true ]] && [[ ! -f "$ERROR_LOG" ]]; then
    log_warn "Error log not found: $ERROR_LOG"
    SHOW_ERROR=false
fi

if [[ "$SHOW_ACCESS" == true ]] && [[ ! -f "$ACCESS_LOG" ]]; then
    log_warn "Access log not found: $ACCESS_LOG"
    SHOW_ACCESS=false
fi

# Exit if no logs to show
if [[ "$SHOW_ERROR" == false ]] && [[ "$SHOW_ACCESS" == false ]]; then
    log_error "No log files available"
    exit 1
fi

# Display logs
if [[ "$FOLLOW" == true ]]; then
    # Follow mode (real-time)
    if [[ "$SHOW_ERROR" == true ]] && [[ "$SHOW_ACCESS" == true ]]; then
        log_info "Following both logs (Press Ctrl+C to stop)..."
        echo ""
        tail -f -n "$LINES" "$ERROR_LOG" "$ACCESS_LOG"
    elif [[ "$SHOW_ERROR" == true ]]; then
        log_info "Following error log (Press Ctrl+C to stop)..."
        echo ""
        tail -f -n "$LINES" "$ERROR_LOG"
    else
        log_info "Following access log (Press Ctrl+C to stop)..."
        echo ""
        tail -f -n "$LINES" "$ACCESS_LOG"
    fi
else
    # Static mode (last N lines)
    if [[ "$SHOW_ERROR" == true ]]; then
        echo -e "${CYAN}Error Log (last $LINES lines):${NC}"
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        tail -n "$LINES" "$ERROR_LOG"
        echo ""
    fi

    if [[ "$SHOW_ACCESS" == true ]]; then
        echo -e "${CYAN}Access Log (last $LINES lines):${NC}"
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        tail -n "$LINES" "$ACCESS_LOG"
        echo ""
    fi
fi

exit 0
