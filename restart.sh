#!/bin/bash
# ============================================================================
# BioRemPP v1.0 - Restart Script
# ============================================================================
# Reinicia a aplicação BioRemPP
# ============================================================================

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Functions
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

# Main
echo ""
echo -e "${BLUE}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║${NC}           ${YELLOW}BioRemPP v1.0 - Restart Server${NC}                   ${BLUE}║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""

log_step "Restarting BioRemPP application..."
echo ""

# Stop the application
log_info "Step 1/2: Stopping application..."
"$SCRIPT_DIR/stop.sh"

# Wait a moment
echo ""
log_info "Waiting 3 seconds before restart..."
sleep 3
echo ""

# Start the application
log_info "Step 2/2: Starting application..."
"$SCRIPT_DIR/start.sh" "$@"

exit 0
