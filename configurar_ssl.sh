#!/bin/bash
# ============================================================================
# Configurar SSL/HTTPS - biorempp.cloud
# ============================================================================
# Script automatizado para obter certificado SSL e configurar HTTPS
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

log_warn() {
    echo -e "${YELLOW}[AVISO]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERRO]${NC} $1"
}

log_step() {
    echo -e "${BLUE}[PASSO]${NC} $1"
}

echo ""
echo -e "${BLUE}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║${NC}     ${GREEN}Configurar SSL/HTTPS - biorempp.cloud${NC}                 ${BLUE}║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""

# ============================================================================
# PASSO 1: Verificar Pré-requisitos
# ============================================================================
log_step "1/5 - Verificando pré-requisitos..."

# Verificar se é root ou tem sudo
if [ "$EUID" -ne 0 ]; then
    if ! sudo -n true 2>/dev/null; then
        log_error "Este script precisa de permissões sudo"
        log_info "Execute: sudo ./configurar_ssl.sh"
        exit 1
    fi
fi

# Verificar DNS
log_info "Verificando DNS..."
if dig +short biorempp.cloud | grep -q "159.203.108.228"; then
    log_info "✓ DNS configurado corretamente"
else
    log_warn "DNS pode não estar configurado ou propagado"
    log_info "biorempp.cloud deve apontar para 159.203.108.228"
    echo ""
    read -p "Continuar mesmo assim? (s/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[SsYy]$ ]]; then
        log_error "Cancelado. Configure o DNS primeiro."
        exit 1
    fi
fi

# Verificar se aplicação está rodando
log_info "Verificando aplicação..."
if curl -s -f http://localhost:8080/health >/dev/null 2>&1; then
    log_info "✓ Aplicação está rodando"
else
    log_error "Aplicação não está rodando em localhost:8080"
    log_info "Execute: ./start.sh"
    exit 1
fi

# Verificar se Nginx está rodando
log_info "Verificando Nginx..."
if sudo systemctl is-active nginx >/dev/null 2>&1; then
    log_info "✓ Nginx está rodando"
else
    log_error "Nginx não está rodando"
    log_info "Execute: sudo systemctl start nginx"
    exit 1
fi

# Verificar HTTP funciona
log_info "Verificando HTTP..."
if curl -s -f http://biorempp.cloud/health >/dev/null 2>&1; then
    log_info "✓ HTTP funciona (biorempp.cloud)"
else
    log_warn "HTTP não responde via domínio"
    log_info "Certbot pode falhar. Recomendo verificar primeiro."
fi

echo ""

# ============================================================================
# PASSO 2: Instalar Certbot
# ============================================================================
log_step "2/5 - Instalando Certbot..."

if command -v certbot >/dev/null 2>&1; then
    log_info "Certbot já instalado: $(certbot --version 2>&1 | head -1)"
else
    log_info "Instalando Certbot..."
    sudo apt-get update -qq
    sudo apt-get install -y certbot python3-certbot-nginx
    log_info "✓ Certbot instalado"
fi

echo ""

# ============================================================================
# PASSO 3: Backup
# ============================================================================
log_step "3/5 - Fazendo backup do Nginx..."

BACKUP_DIR="/etc/nginx/backup_ssl_$(date +%Y%m%d_%H%M%S)"
sudo mkdir -p "$BACKUP_DIR"
sudo cp /etc/nginx/sites-available/biorempp "$BACKUP_DIR/biorempp"
log_info "Backup salvo: $BACKUP_DIR"

echo ""

# ============================================================================
# PASSO 4: Obter Certificado SSL
# ============================================================================
log_step "4/5 - Obtendo certificado SSL..."

log_info "Executando Certbot..."
log_warn "Isso pode levar alguns minutos..."
echo ""

# Executar Certbot
if sudo certbot --nginx \
    -d biorempp.cloud \
    -d www.biorempp.cloud \
    --email biorempp@gmail.com \
    --agree-tos \
    --redirect \
    --non-interactive; then

    echo ""
    log_info "✓ Certificado SSL obtido com sucesso!"
else
    log_error "Falha ao obter certificado SSL"
    echo ""
    log_info "Possíveis causas:"
    echo "  1. DNS não está configurado ou não propagou"
    echo "  2. Firewall bloqueando porta 80/443"
    echo "  3. Limite de tentativas do Let's Encrypt (5 falhas/hora)"
    echo ""
    log_info "Verificar logs:"
    echo "  sudo tail -50 /var/log/letsencrypt/letsencrypt.log"
    echo ""
    log_info "Testar sem realmente obter certificado:"
    echo "  sudo certbot --nginx --dry-run -d biorempp.cloud -d www.biorempp.cloud"
    exit 1
fi

echo ""

# ============================================================================
# PASSO 5: Verificar
# ============================================================================
log_step "5/5 - Verificando instalação..."

# Verificar HTTPS
log_info "Testando HTTPS..."
sleep 3

if curl -s -f https://biorempp.cloud/health >/dev/null 2>&1; then
    log_info "✓ HTTPS funciona!"
else
    log_warn "HTTPS ainda não responde (aguarde propagação)"
fi

# Verificar redirect HTTP → HTTPS
log_info "Testando redirect HTTP → HTTPS..."
REDIRECT=$(curl -s -o /dev/null -w "%{http_code}" http://biorempp.cloud 2>/dev/null)
if [ "$REDIRECT" = "301" ] || [ "$REDIRECT" = "302" ]; then
    log_info "✓ Redirect HTTP → HTTPS configurado"
else
    log_warn "Redirect pode não estar funcionando (código: $REDIRECT)"
fi

# Verificar certificados
log_info "Certificados instalados:"
sudo certbot certificates | grep -E "(Certificate Name|Domains|Expiry Date)" || true

echo ""

# ============================================================================
# RESUMO
# ============================================================================
echo -e "${GREEN}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║${NC}                    ${GREEN}SSL Configurado!${NC}                           ${GREEN}║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""

log_info "Configurações aplicadas:"
echo "  • Certificado SSL obtido do Let's Encrypt"
echo "  • HTTPS habilitado em biorempp.cloud"
echo "  • Redirect HTTP → HTTPS ativado"
echo "  • Renovação automática configurada"
echo ""

log_info "Acessar aplicação:"
echo "  https://biorempp.cloud"
echo "  https://www.biorempp.cloud"
echo ""

log_info "Verificar certificado:"
echo "  sudo certbot certificates"
echo ""

log_info "Testar renovação:"
echo "  sudo certbot renew --dry-run"
echo ""

log_info "Renovação automática:"
echo "  sudo systemctl status certbot.timer"
echo ""

echo -e "${GREEN}🔒 Seu site agora está seguro com HTTPS!${NC}"
echo ""

exit 0
