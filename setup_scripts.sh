#!/bin/bash
# ============================================================================
# BioRemPP v1.0 - Setup Scripts
# ============================================================================
# Torna todos os scripts executáveis e configura permissões
# Execute este script uma vez após transferir os arquivos para o servidor
# ============================================================================

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo ""
echo -e "${BLUE}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║${NC}           ${GREEN}BioRemPP v1.0 - Setup Scripts${NC}                    ${BLUE}║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""

echo -e "${GREEN}[INFO]${NC} Making scripts executable..."

# List of scripts to make executable
SCRIPTS=(
    "start.sh"
    "stop.sh"
    "restart.sh"
    "status.sh"
    "logs.sh"
)

for script in "${SCRIPTS[@]}"; do
    if [[ -f "$SCRIPT_DIR/$script" ]]; then
        chmod +x "$SCRIPT_DIR/$script"
        echo -e "${GREEN}✓${NC} $script"
    else
        echo -e "${YELLOW}⚠${NC} $script not found"
    fi
done

echo ""
echo -e "${GREEN}[INFO]${NC} Creating .env file (if not exists)..."

if [[ ! -f "$SCRIPT_DIR/.env" ]]; then
    cat > "$SCRIPT_DIR/.env" << 'EOF'
# BioRemPP Production Configuration
# ============================================================================
# Copie este arquivo e ajuste conforme necessário
# ============================================================================

# Environment
BIOREMPP_ENV=production

# Server
BIOREMPP_HOST=0.0.0.0
BIOREMPP_PORT=8080
BIOREMPP_DEBUG=False
BIOREMPP_HOT_RELOAD=False

# Logging
BIOREMPP_LOG_LEVEL=WARNING

# Gunicorn
BIOREMPP_WORKERS=4
BIOREMPP_WORKER_CLASS=gevent
BIOREMPP_WORKER_CONNECTIONS=1000
BIOREMPP_TIMEOUT=300
BIOREMPP_KEEPALIVE=5

# Upload Limits
BIOREMPP_UPLOAD_MAX_SIZE_MB=100
BIOREMPP_UPLOAD_SAMPLE_LIMIT=1000
BIOREMPP_UPLOAD_KO_LIMIT=500000

# Processing
BIOREMPP_PROCESSING_TIMEOUT=300
EOF
    echo -e "${GREEN}✓${NC} .env file created"
    echo -e "${BLUE}[IMPORTANT]${NC} Please review and adjust .env file before starting"
else
    echo -e "${GREEN}✓${NC} .env file already exists"
fi

echo ""
echo -e "${GREEN}[INFO]${NC} Creating necessary directories..."

mkdir -p "$SCRIPT_DIR/logs"
mkdir -p "$SCRIPT_DIR/data"
mkdir -p "$SCRIPT_DIR/.cache"
mkdir -p "$SCRIPT_DIR/.archive"

echo -e "${GREEN}✓${NC} logs/"
echo -e "${GREEN}✓${NC} data/"
echo -e "${GREEN}✓${NC} .cache/"
echo -e "${GREEN}✓${NC} .archive/"

echo ""
echo -e "${GREEN}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║${NC}                  ${GREEN}Setup Complete!${NC}                             ${GREEN}║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo "Next steps:"
echo ""
echo "  1. Review .env configuration:"
echo "     nano .env"
echo ""
echo "  2. Install dependencies:"
echo "     ./start.sh"
echo "     (Will create venv and install automatically)"
echo ""
echo "  3. Check status:"
echo "     ./status.sh"
echo ""
echo "Useful commands:"
echo "  ./start.sh        - Start application"
echo "  ./stop.sh         - Stop application"
echo "  ./restart.sh      - Restart application"
echo "  ./status.sh       - Check status"
echo "  ./logs.sh         - View logs"
echo ""

exit 0
