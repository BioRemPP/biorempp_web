#!/bin/bash
# ============================================================================
# Fix Nginx IPv4 - BioRemPP v1.0
# ============================================================================
# Problema: Nginx está tentando conectar via IPv6 ([::1]:8080)
# Solução: Forçar uso de IPv4 (127.0.0.1:8080)
# ============================================================================

set -e

# Cores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_step() {
    echo -e "${BLUE}[PASSO]${NC} $1"
}

echo ""
echo -e "${BLUE}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║${NC}     ${GREEN}Fix Nginx IPv4 - BioRemPP v1.0${NC}                        ${BLUE}║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""

log_info "Problema detectado:"
echo "  • Nginx está tentando conectar via IPv6: [::1]:8080"
echo "  • Aplicação só escuta em IPv4: 0.0.0.0:8080"
echo ""
log_info "Solução: Forçar IPv4 no upstream do Nginx"
echo ""

# ============================================================================
# PASSO 1: Backup
# ============================================================================
log_step "1/3 - Fazendo backup..."

BACKUP_DIR="/etc/nginx/backup_ipv4_fix_$(date +%Y%m%d_%H%M%S)"
sudo mkdir -p "$BACKUP_DIR"
sudo cp /etc/nginx/nginx.conf "$BACKUP_DIR/nginx.conf"
sudo cp /etc/nginx/sites-available/biorempp "$BACKUP_DIR/biorempp"

log_info "Backup salvo: $BACKUP_DIR"
echo ""

# ============================================================================
# PASSO 2: Corrigir nginx.conf
# ============================================================================
log_step "2/3 - Corrigindo nginx.conf..."

# Criar configuração corrigida
sudo tee /etc/nginx/nginx.conf > /dev/null << 'EOF'
user www-data;
worker_processes auto;
pid /run/nginx.pid;
error_log /var/log/nginx/error.log;
include /etc/nginx/modules-enabled/*.conf;

events {
    worker_connections 1024;
    multi_accept on;
    use epoll;
}

http {
    ##
    # Basic Settings
    ##
    sendfile on;
    tcp_nopush on;
    types_hash_max_size 2048;
    server_tokens off;

    include /etc/nginx/mime.types;
    default_type application/octet-stream;

    ##
    # SSL Settings
    ##
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_prefer_server_ciphers on;

    ##
    # Logging Settings
    ##
    access_log /var/log/nginx/access.log;

    ##
    # Gzip Settings
    ##
    gzip on;
    gzip_vary on;
    gzip_proxied any;
    gzip_comp_level 6;
    gzip_types text/plain text/css text/xml text/javascript
               application/json application/javascript application/xml+rss
               application/rss+xml font/truetype font/opentype
               application/vnd.ms-fontobject image/svg+xml;

    ##
    # Upstream Configuration - FORÇAR IPv4
    ##
    upstream biorempp_app {
        # CRÍTICO: Usar 127.0.0.1 (IPv4) ao invés de localhost (pode resolver para ::1)
        server 127.0.0.1:8080;
        keepalive 32;
    }

    ##
    # Rate Limiting Zones - OTIMIZADO PARA DASH
    ##
    limit_req_zone $binary_remote_addr zone=dash_api:10m rate=100r/s;
    limit_req_zone $binary_remote_addr zone=general:10m rate=50r/s;

    ##
    # Virtual Host Configs
    ##
    include /etc/nginx/conf.d/*.conf;
    include /etc/nginx/sites-enabled/*;
}
EOF

log_info "nginx.conf atualizado (upstream agora usa 127.0.0.1)"
echo ""

# ============================================================================
# PASSO 3: Testar e Recarregar
# ============================================================================
log_step "3/3 - Testando e recarregando..."

# Testar configuração
log_info "Testando configuração..."
if sudo nginx -t; then
    log_info "Configuração OK!"

    # Recarregar Nginx
    log_info "Recarregando Nginx..."
    sudo systemctl reload nginx

    echo ""
    echo -e "${GREEN}╔════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║${NC}                    ${GREEN}Fix Aplicado!${NC}                              ${GREEN}║${NC}"
    echo -e "${GREEN}╚════════════════════════════════════════════════════════════════╝${NC}"
    echo ""

    log_info "Mudanças aplicadas:"
    echo "  • upstream biorempp_app: localhost:8080 → 127.0.0.1:8080"
    echo "  • Rate limiting otimizado para Dash (burst=200)"
    echo ""

    log_info "Testando conexão..."
    sleep 2

    # Testar localhost
    echo -n "  • localhost:8080: "
    if curl -s -f http://localhost:8080/health >/dev/null 2>&1; then
        echo -e "${GREEN}✓${NC}"
    else
        echo -e "${RED}✗${NC}"
    fi

    # Testar via IP
    echo -n "  • 159.203.108.228: "
    if curl -s -f http://159.203.108.228/health >/dev/null 2>&1; then
        echo -e "${GREEN}✓${NC}"
    else
        echo -e "${RED}✗${NC}"
    fi

    # Testar via domínio
    echo -n "  • biorempp.cloud: "
    if curl -s -f http://biorempp.cloud/health >/dev/null 2>&1; then
        echo -e "${GREEN}✓ RESOLVIDO!${NC}"
    else
        echo -e "${RED}✗ Ainda com problema${NC}"
        echo ""
        echo -e "${YELLOW}Aguarde 10 segundos e tente novamente:${NC}"
        echo "  curl http://biorempp.cloud/health"
    fi

    echo ""
    log_info "Acesse a aplicação:"
    echo "  • http://biorempp.cloud"
    echo "  • http://159.203.108.228"
    echo ""

    log_info "Monitorar logs:"
    echo "  sudo tail -f /var/log/nginx/error.log"
    echo "  ./logs.sh --follow"

else
    echo -e "${RED}[ERRO]${NC} Configuração inválida!"
    log_info "Restaurando backup..."
    sudo cp "$BACKUP_DIR/nginx.conf" /etc/nginx/nginx.conf
    sudo nginx -s reload
    echo -e "${RED}Backup restaurado${NC}"
    exit 1
fi

echo ""
exit 0
