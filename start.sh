#!/bin/bash
# ============================================================================
# BioRemPP v1.0 - Production Start Script (Non-Docker)
# ============================================================================
# Inicia a aplicação BioRemPP em produção usando Gunicorn
# Similar ao script legado mas otimizado para a nova arquitetura
#
# Usage:
#   ./start.sh              # Start in background (production)
#   ./start.sh --foreground # Start in foreground (debugging)
#   ./start.sh --dev        # Start in development mode (hot reload)
# ============================================================================

set -e

# ============================================================================
# COLORS AND FORMATTING
# ============================================================================
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# ============================================================================
# CONFIGURATION
# ============================================================================
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APP_NAME="biorempp"
VENV_DIR="$SCRIPT_DIR/.venv"
PYTHON_PATH="$VENV_DIR/bin/python"
PIP_PATH="$VENV_DIR/bin/pip"
GUNICORN_PATH="$VENV_DIR/bin/gunicorn"
PIDFILE="$SCRIPT_DIR/.biorempp.pid"
LOG_DIR="$SCRIPT_DIR/logs"
ENV_FILE="$SCRIPT_DIR/.env"

# Application files
WSGI_MODULE="wsgi:server"
GUNICORN_CONFIG="gunicorn_config.py"
MAIN_APP="biorempp_app.py"
PYPROJECT="$SCRIPT_DIR/pyproject.toml"

# Default mode
MODE="production"
FOREGROUND=false

# ============================================================================
# FUNCTIONS
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

show_banner() {
    echo ""
    echo -e "${BLUE}╔════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║${NC}           ${GREEN}BioRemPP v1.0 - Production Start${NC}                  ${BLUE}║${NC}"
    echo -e "${BLUE}╚════════════════════════════════════════════════════════════════╝${NC}"
    echo ""
}

show_usage() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --foreground, -f   Run in foreground (for debugging)"
    echo "  --dev              Run in development mode (hot reload)"
    echo "  --help, -h         Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0                 # Start in background (production)"
    echo "  $0 --foreground    # Start in foreground"
    echo "  $0 --dev           # Start in dev mode"
    echo ""
}

find_python() {
    local python_cmd=""

    # Try different Python commands in order of preference
    for cmd in python3.12 python3.11 python3.10 python3.9 python3 python; do
        if command -v "$cmd" &> /dev/null; then
            # Check if it's a real Python (not Windows Store stub)
            if "$cmd" -c "import sys; exit(0 if sys.version_info >= (3, 11) else 1)" &> /dev/null; then
                echo "$cmd"
                return 0
            fi
        fi
    done

    return 1
}

check_requirements() {
    log_step "Checking requirements..."

    # Check Python version
    if [[ ! -f "$PYTHON_PATH" ]]; then
        log_warn "Virtual environment not found at $VENV_DIR"
        return 1
    fi

    # Check if Gunicorn is installed
    if [[ ! -f "$GUNICORN_PATH" ]]; then
        log_warn "Gunicorn not installed in virtual environment"
        return 1
    fi

    # Check critical files
    if [[ ! -f "$SCRIPT_DIR/$MAIN_APP" ]]; then
        log_error "Main application file not found: $MAIN_APP"
        return 1
    fi

    if [[ ! -f "$SCRIPT_DIR/$GUNICORN_CONFIG" ]]; then
        log_error "Gunicorn config not found: $GUNICORN_CONFIG"
        return 1
    fi

    # Check if already running
    if [[ -f "$PIDFILE" ]]; then
        PID=$(cat "$PIDFILE")
        if ps -p "$PID" > /dev/null 2>&1; then
            log_error "Application already running (PID: $PID)"
            log_info "Use ./stop.sh to stop it first, or ./restart.sh to restart"
            return 1
        else
            log_warn "Stale PID file found, removing..."
            rm -f "$PIDFILE"
        fi
    fi

    log_info "All requirements satisfied"
    return 0
}

create_venv() {
    log_step "Creating virtual environment..."

    # Find suitable Python
    PYTHON_CMD=$(find_python)
    if [[ $? -ne 0 ]]; then
        log_error "No suitable Python found (Python 3.11+ required)"
        log_info "Available Python versions:"
        which python python3 python3.9 python3.10 python3.11 python3.12 2>/dev/null || echo "  None found"
        exit 1
    fi

    log_info "Using Python: $PYTHON_CMD"
    "$PYTHON_CMD" -m venv "$VENV_DIR"

    if [[ $? -ne 0 ]]; then
        log_error "Failed to create virtual environment"
        exit 1
    fi

    log_info "Virtual environment created at: $VENV_DIR"
}

install_dependencies() {
    log_step "Installing dependencies..."

    # Upgrade pip
    log_info "Upgrading pip..."
    "$PYTHON_PATH" -m pip install --upgrade pip setuptools wheel --quiet

    if [[ $? -ne 0 ]]; then
        log_error "Failed to upgrade pip"
        exit 1
    fi

    # Install package with production extras
    if [[ -f "$PYPROJECT" ]]; then
        log_info "Installing from pyproject.toml..."
        "$PIP_PATH" install -e ".[server,cache,compression]" --quiet
    else
        log_error "pyproject.toml not found"
        exit 1
    fi

    if [[ $? -ne 0 ]]; then
        log_error "Failed to install dependencies"
        exit 1
    fi

    log_info "Dependencies installed successfully"
}

prepare_environment() {
    log_step "Preparing environment..."

    # Create necessary directories
    mkdir -p "$LOG_DIR"
    mkdir -p "$SCRIPT_DIR/data"
    mkdir -p "$SCRIPT_DIR/.cache"

    # Check .env file
    if [[ ! -f "$ENV_FILE" ]]; then
        log_warn ".env file not found"
        log_info "Creating default .env for production..."

        cat > "$ENV_FILE" << 'EOF'
# BioRemPP Production Configuration
BIOREMPP_ENV=production
BIOREMPP_HOST=0.0.0.0
BIOREMPP_PORT=8080
BIOREMPP_DEBUG=False
BIOREMPP_HOT_RELOAD=False
BIOREMPP_LOG_LEVEL=WARNING
BIOREMPP_WORKERS=4
BIOREMPP_WORKER_CLASS=gevent
BIOREMPP_WORKER_CONNECTIONS=1000
BIOREMPP_TIMEOUT=300
BIOREMPP_KEEPALIVE=5
BIOREMPP_UPLOAD_MAX_SIZE_MB=100
EOF
        log_info "Created .env file - please review and adjust if needed"
    fi

    # Load environment variables
    if [[ -f "$ENV_FILE" ]]; then
        log_info "Loading environment from .env"
        set -a
        source "$ENV_FILE"
        set +a
    fi

    log_info "Environment prepared"
}

start_production() {
    log_step "Starting BioRemPP in PRODUCTION mode..."

    cd "$SCRIPT_DIR"

    if [[ "$FOREGROUND" == true ]]; then
        log_info "Starting in foreground mode (Ctrl+C to stop)..."
        log_info "Command: $GUNICORN_PATH $WSGI_MODULE -c $GUNICORN_CONFIG"
        echo ""

        # Run in foreground
        "$GUNICORN_PATH" "$WSGI_MODULE" -c "$GUNICORN_CONFIG"
    else
        log_info "Starting in background mode (daemon)..."
        log_info "Command: $GUNICORN_PATH $WSGI_MODULE -c $GUNICORN_CONFIG --daemon --pid $PIDFILE"
        echo ""

        # Run as daemon
        "$GUNICORN_PATH" "$WSGI_MODULE" \
            -c "$GUNICORN_CONFIG" \
            --daemon \
            --pid "$PIDFILE"

        # Wait a moment and check if it started
        sleep 2

        if [[ -f "$PIDFILE" ]]; then
            PID=$(cat "$PIDFILE")
            if ps -p "$PID" > /dev/null 2>&1; then
                echo ""
                log_info "${GREEN}✓${NC} Application started successfully!"
                log_info "PID: $PID"
                log_info "Mode: Production (Gunicorn)"
                log_info "Workers: ${BIOREMPP_WORKERS:-4}"
                log_info "Port: ${BIOREMPP_PORT:-8080}"
                echo ""
                log_info "Access: http://localhost:${BIOREMPP_PORT:-8080}"
                log_info "Health: http://localhost:${BIOREMPP_PORT:-8080}/health"
                echo ""
                log_info "Useful commands:"
                log_info "  View logs:    ./logs.sh"
                log_info "  Stop server:  ./stop.sh"
                log_info "  Restart:      ./restart.sh"
                log_info "  Status:       ./status.sh"
                echo ""
            else
                log_error "Failed to start application"
                log_info "Check logs: tail -50 $LOG_DIR/gunicorn_error.log"
                exit 1
            fi
        else
            log_error "PID file not created - application may have failed to start"
            log_info "Check logs: tail -50 $LOG_DIR/gunicorn_error.log"
            exit 1
        fi
    fi
}

start_development() {
    log_step "Starting BioRemPP in DEVELOPMENT mode..."

    cd "$SCRIPT_DIR"

    # Set development environment variables
    export BIOREMPP_ENV=development
    export BIOREMPP_DEBUG=True
    export BIOREMPP_HOT_RELOAD=True
    export BIOREMPP_HOST=${BIOREMPP_HOST:-127.0.0.1}
    export BIOREMPP_PORT=${BIOREMPP_PORT:-8050}

    log_info "Starting Dash development server..."
    log_info "Host: $BIOREMPP_HOST"
    log_info "Port: $BIOREMPP_PORT"
    log_info "Hot Reload: Enabled"
    echo ""
    log_warn "Press Ctrl+C to stop"
    echo ""

    # Run development server
    "$PYTHON_PATH" "$MAIN_APP"
}

# ============================================================================
# MAIN
# ============================================================================

show_banner

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --foreground|-f)
            FOREGROUND=true
            shift
            ;;
        --dev)
            MODE="development"
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

# Check if venv exists
if [[ ! -f "$PYTHON_PATH" ]]; then
    log_warn "Virtual environment not found"
    create_venv
    install_dependencies
else
    log_info "Virtual environment found at: $VENV_DIR"
fi

# Check requirements (only for production mode)
if [[ "$MODE" == "production" ]]; then
    if ! check_requirements; then
        log_error "Requirements check failed"

        # Ask user if they want to reinstall dependencies
        read -p "Do you want to reinstall dependencies? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            install_dependencies
        else
            exit 1
        fi
    fi
fi

# Prepare environment
prepare_environment

# Start application based on mode
if [[ "$MODE" == "development" ]]; then
    start_development
else
    start_production
fi

exit 0
