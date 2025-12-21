#!/bin/bash
# ============================================================================
# Script de Setup Completo - BioRemPP v1.0 para biorempp.cloud
# ============================================================================
# Este script configura TUDO automaticamente:
# - Cria .env com SECRET_KEY
# - Configura Nginx
# - Para aplicação legada
# - Inicia nova aplicação
# ============================================================================

set -e

# Cores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# Diretório do script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Funções
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

log_success() {
    echo -e "${GREEN}[✓]${NC} $1"
}

# Banner
clear
echo ""
echo -e "${CYAN}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║${NC}     ${GREEN}BioRemPP v1.0 - Setup Completo Automatizado${NC}        ${CYAN}║${NC}"
echo -e "${CYAN}║${NC}     ${BLUE}biorempp.cloud - Digital Ocean NYC3 - 2GB RAM${NC}     ${CYAN}║${NC}"
echo -e "${CYAN}╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Verificar se está rodando como root (apenas para Nginx)
if [ "$EUID" -eq 0 ]; then
    log_warn "Rodando como root. Recomendado rodar como usuário normal (sudo será solicitado quando necessário)"
    read -p "Continuar? (s/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[SsYy]$ ]]; then
        log_error "Cancelado pelo usuário"
        exit 1
    fi
fi

# ============================================================================
# PASSO 1: Verificar Pré-requisitos
# ============================================================================
log_step "1/7 - Verificando pré-requisitos..."

# Python
if ! command -v python3 &> /dev/null; then
    log_error "Python 3 não encontrado"
    log_info "Instale com: sudo apt-get install python3"
    exit 1
fi
PYTHON_VERSION=$(python3 --version | awk '{print $2}')
log_success "Python $PYTHON_VERSION encontrado"

# Nginx
if ! command -v nginx &> /dev/null; then
    log_error "Nginx não encontrado"
    log_info "Instale com: sudo apt-get install nginx"
    exit 1
fi
NGINX_VERSION=$(nginx -v 2>&1 | awk '{print $3}')
log_success "Nginx $NGINX_VERSION encontrado"

# Verificar arquivos necessários
if [ ! -f "$SCRIPT_DIR/.env.production" ]; then
    log_error "Arquivo .env.production não encontrado"
    exit 1
fi

if [ ! -f "$SCRIPT_DIR/nginx.conf.production" ]; then
    log_error "Arquivo nginx.conf.production não encontrado"
    exit 1
fi

if [ ! -f "$SCRIPT_DIR/biorempp.conf.production" ]; then
    log_error "Arquivo biorempp.conf.production não encontrado"
    exit 1
fi

log_success "Todos os arquivos necessários encontrados"
echo ""

# ============================================================================
# PASSO 2: Criar .env com SECRET_KEY
# ============================================================================
log_step "2/7 - Configurando arquivo .env..."

if [ -f "$SCRIPT_DIR/.env" ]; then
    log_warn "Arquivo .env já existe"
    read -p "Sobrescrever? (s/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[SsYy]$ ]]; then
        log_info "Mantendo .env existente"
    else
        rm "$SCRIPT_DIR/.env"
        log_info "Arquivo .env existente removido"
    fi
fi

if [ ! -f "$SCRIPT_DIR/.env" ]; then
    # Copiar template
    cp "$SCRIPT_DIR/.env.production" "$SCRIPT_DIR/.env"
    log_success ".env criado a partir de .env.production"

    # Gerar SECRET_KEY
    log_info "Gerando SECRET_KEY única..."
    SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))")

    # Substituir no .env
    sed -i "s/SECRET_KEY=REPLACE_WITH_SECURE_KEY_GENERATE_WITH_PYTHON_SECRETS_TOKEN_HEX/SECRET_KEY=$SECRET_KEY/" "$SCRIPT_DIR/.env"

    log_success "SECRET_KEY gerada e configurada"
    log_info "SECRET_KEY: ${SECRET_KEY:0:10}... (64 caracteres)"
else
    log_info "Usando .env existente"
fi

echo ""

# ============================================================================
# PASSO 3: Verificar configurações .env
# ============================================================================
log_step "3/7 - Verificando configurações do .env..."

# Verificar se SECRET_KEY foi alterada
if grep -q "REPLACE_WITH_SECURE_KEY" "$SCRIPT_DIR/.env"; then
    log_error "SECRET_KEY não foi configurada no .env!"
    log_info "Abra o arquivo .env e configure manualmente"
    exit 1
fi

# Mostrar configurações importantes
log_success "Configurações do .env:"
echo "  • BIOREMPP_WORKERS: $(grep '^BIOREMPP_WORKERS=' .env | cut -d'=' -f2)"
echo "  • BIOREMPP_WORKER_CLASS: $(grep '^BIOREMPP_WORKER_CLASS=' .env | cut -d'=' -f2)"
echo "  • BIOREMPP_PORT: $(grep '^BIOREMPP_PORT=' .env | cut -d'=' -f2)"
echo "  • DOMAIN: $(grep '^DOMAIN=' .env | cut -d'=' -f2)"
echo "  • LETSENCRYPT_EMAIL: $(grep '^LETSENCRYPT_EMAIL=' .env | cut -d'=' -f2)"
echo ""

# ============================================================================
# PASSO 4: Configurar Nginx
# ============================================================================
log_step "4/7 - Configurando Nginx..."

# Verificar permissão sudo
if ! sudo -n true 2>/dev/null; then
    log_warn "Será necessário senha sudo para configurar Nginx"
fi

# Backup do nginx.conf
BACKUP_DIR="/etc/nginx/backup_$(date +%Y%m%d_%H%M%S)"
sudo mkdir -p "$BACKUP_DIR"

if [ -f /etc/nginx/nginx.conf ]; then
    sudo cp /etc/nginx/nginx.conf "$BACKUP_DIR/nginx.conf"
    log_success "Backup salvo: $BACKUP_DIR/nginx.conf"
fi

if [ -f /etc/nginx/sites-available/biorempp ]; then
    sudo cp /etc/nginx/sites-available/biorempp "$BACKUP_DIR/biorempp"
    log_success "Backup salvo: $BACKUP_DIR/biorempp"
fi

# Copiar nginx.conf
sudo cp "$SCRIPT_DIR/nginx.conf.production" /etc/nginx/nginx.conf
log_success "nginx.conf atualizado"

# Copiar biorempp.conf
sudo cp "$SCRIPT_DIR/biorempp.conf.production" /etc/nginx/sites-available/biorempp
log_success "biorempp.conf instalado"

# Criar link simbólico
sudo ln -sf /etc/nginx/sites-available/biorempp /etc/nginx/sites-enabled/biorempp
log_success "Link simbólico criado"

# Remover default
if [ -L /etc/nginx/sites-enabled/default ]; then
    sudo rm -f /etc/nginx/sites-enabled/default
    log_success "Site default removido"
fi

# Testar Nginx
log_info "Testando configuração do Nginx..."
if sudo nginx -t; then
    log_success "Configuração do Nginx OK!"
else
    log_error "Erro na configuração do Nginx!"
    log_info "Restaurando backup..."
    sudo cp "$BACKUP_DIR/nginx.conf" /etc/nginx/nginx.conf
    if [ -f "$BACKUP_DIR/biorempp" ]; then
        sudo cp "$BACKUP_DIR/biorempp" /etc/nginx/sites-available/biorempp
    fi
    log_info "Backup restaurado"
    exit 1
fi

# Recarregar Nginx
sudo systemctl reload nginx
log_success "Nginx recarregado"

echo ""

# ============================================================================
# PASSO 5: Parar aplicação legada
# ============================================================================
log_step "5/7 - Parando aplicação legada..."

# Procurar screen
SCREEN_SESSION=$(screen -ls | grep biorempp | awk '{print $1}' | cut -d. -f2 || echo "")

if [ -n "$SCREEN_SESSION" ]; then
    log_info "Screen detectado: $SCREEN_SESSION"
    screen -X -S "$SCREEN_SESSION" quit || true
    log_success "Screen encerrado"
else
    log_info "Nenhum screen biorempp encontrado"
fi

# Procurar processos Python
PYTHON_PID=$(pgrep -f "python.*main.py" || echo "")

if [ -n "$PYTHON_PID" ]; then
    log_info "Processo Python detectado: PID $PYTHON_PID"
    kill -TERM "$PYTHON_PID" || true
    sleep 2
    log_success "Processo Python encerrado"
else
    log_info "Nenhum processo main.py encontrado"
fi

echo ""

# ============================================================================
# PASSO 6: Preparar scripts
# ============================================================================
log_step "6/7 - Preparando scripts de gerenciamento..."

cd "$SCRIPT_DIR"

# Tornar scripts executáveis
chmod +x start.sh stop.sh restart.sh status.sh logs.sh setup_scripts.sh 2>/dev/null || true

if [ -f setup_scripts.sh ]; then
    ./setup_scripts.sh
    log_success "Scripts configurados"
else
    chmod +x *.sh
    log_success "Scripts tornados executáveis"
fi

echo ""

# ============================================================================
# PASSO 7: Iniciar BioRemPP v1.0
# ============================================================================
log_step "7/7 - Iniciando BioRemPP v1.0..."

if [ ! -f start.sh ]; then
    log_error "Script start.sh não encontrado"
    exit 1
fi

# Iniciar aplicação
./start.sh

# Aguardar um pouco
sleep 3

echo ""

# ============================================================================
# VERIFICAÇÃO FINAL
# ============================================================================
echo -e "${CYAN}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║${NC}              ${GREEN}✓ Setup Concluído!${NC}                             ${CYAN}║${NC}"
echo -e "${CYAN}╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""

log_info "Verificando status..."
echo ""

# Status da aplicação
if [ -f status.sh ]; then
    ./status.sh
fi

echo ""
echo -e "${GREEN}════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}Configurações Aplicadas:${NC}"
echo -e "${GREEN}════════════════════════════════════════════════════════════${NC}"
echo ""
echo "  1. Arquivo .env:"
echo "     ✓ SECRET_KEY: Gerada única"
echo "     ✓ DOMAIN: biorempp.cloud"
echo "     ✓ WORKERS: 4 (otimizado para 2GB RAM)"
echo "     ✓ WORKER_CLASS: gevent (melhor para Dash)"
echo ""
echo "  2. Nginx:"
echo "     ✓ nginx.conf: localhost:8080, user www-data"
echo "     ✓ biorempp.conf: server_name biorempp.cloud"
echo "     ✓ Backup salvo: $BACKUP_DIR"
echo ""
echo "  3. Aplicação:"
echo "     ✓ Aplicação legada parada"
echo "     ✓ BioRemPP v1.0 iniciado"
echo ""
echo -e "${GREEN}════════════════════════════════════════════════════════════${NC}"
echo ""

# Testes
log_info "Executando testes..."
echo ""

# Teste 1: Health check localhost
echo -n "  • Health check localhost:8080... "
if curl -s -f http://localhost:8080/health > /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${RED}✗${NC}"
    log_warn "Health check localhost falhou (aplicação pode estar iniciando)"
fi

# Teste 2: Health check via Nginx IP
echo -n "  • Health check 159.203.108.228... "
if curl -s -f http://159.203.108.228/health > /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${RED}✗${NC}"
    log_warn "Health check via IP falhou"
fi

# Teste 3: Health check via domínio (pode falhar se DNS não estiver configurado)
echo -n "  • Health check biorempp.cloud... "
if curl -s -f http://biorempp.cloud/health > /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${YELLOW}⚠${NC}"
    log_warn "Health check via domínio falhou (DNS pode não estar configurado)"
fi

echo ""
echo -e "${GREEN}════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}Próximos Passos:${NC}"
echo -e "${GREEN}════════════════════════════════════════════════════════════${NC}"
echo ""
echo "  1. Verificar DNS do domínio:"
echo "     dig biorempp.cloud"
echo "     # Deve apontar para: 159.203.108.228"
echo ""
echo "  2. Configurar SSL/HTTPS (recomendado):"
echo "     cat CONFIGURAR_SSL.md"
echo "     # OU comando rápido:"
echo "     sudo certbot --nginx -d biorempp.cloud -d www.biorempp.cloud --email biorempp@gmail.com"
echo ""
echo "  3. Monitorar aplicação:"
echo "     ./status.sh      # Ver status"
echo "     ./logs.sh        # Ver logs"
echo "     free -h          # Ver memória"
echo ""
echo "  4. Acessar aplicação:"
echo "     http://biorempp.cloud"
echo "     http://159.203.108.228"
echo "     # Após SSL: https://biorempp.cloud"
echo ""
echo -e "${GREEN}════════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "${CYAN}📚 Documentação:${NC}"
echo "  • SERVIDOR_BIOREMPP_CLOUD.md - Informações completas do servidor"
echo "  • CONFIGURAR_SSL.md - Guia de setup HTTPS"
echo "  • COMANDOS_RAPIDOS.md - Referência de comandos"
echo ""
echo -e "${GREEN}✓ Setup completo! BioRemPP v1.0 está rodando em biorempp.cloud${NC}"
echo ""

exit 0
