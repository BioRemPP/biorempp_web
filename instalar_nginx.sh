#!/bin/bash
# ============================================================================
# Script de Instalação - Configuração Nginx para BioRemPP v1.0
# ============================================================================
# Este script configura automaticamente o Nginx para produção sem Docker
# ============================================================================

set -e

# Cores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
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

# Banner
echo ""
echo -e "${BLUE}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║${NC}     ${GREEN}BioRemPP v1.0 - Instalação Nginx (Sem Docker)${NC}         ${BLUE}║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Verificar se está rodando como root
if [ "$EUID" -ne 0 ]; then
    log_error "Este script precisa ser executado com sudo"
    echo "Execute: sudo ./instalar_nginx.sh"
    exit 1
fi

# Verificar se Nginx está instalado
if ! command -v nginx &> /dev/null; then
    log_error "Nginx não está instalado"
    log_info "Instale com: sudo apt-get update && sudo apt-get install nginx"
    exit 1
fi

log_info "Nginx encontrado: $(nginx -v 2>&1)"
echo ""

# ============================================================================
# PASSO 1: Backup da configuração atual
# ============================================================================
log_step "1/5 - Fazendo backup da configuração atual..."

BACKUP_DIR="/etc/nginx/backup_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"

if [ -f /etc/nginx/nginx.conf ]; then
    cp /etc/nginx/nginx.conf "$BACKUP_DIR/nginx.conf"
    log_info "Backup salvo: $BACKUP_DIR/nginx.conf"
fi

if [ -f /etc/nginx/sites-available/biorempp ]; then
    cp /etc/nginx/sites-available/biorempp "$BACKUP_DIR/biorempp"
    log_info "Backup salvo: $BACKUP_DIR/biorempp"
fi

echo ""

# ============================================================================
# PASSO 2: Atualizar nginx.conf
# ============================================================================
log_step "2/5 - Atualizando /etc/nginx/nginx.conf..."

if [ -f "$SCRIPT_DIR/nginx.conf.production" ]; then
    cp "$SCRIPT_DIR/nginx.conf.production" /etc/nginx/nginx.conf
    log_info "nginx.conf atualizado com sucesso"
    log_info "Mudanças aplicadas:"
    log_info "  ✓ user www-data (era nginx)"
    log_info "  ✓ upstream localhost:8080 (era biorempp-app:8050)"
    log_info "  ✓ include sites-enabled/* (adicionado)"
else
    log_error "Arquivo nginx.conf.production não encontrado"
    log_info "Aplicando correções manualmente..."

    # Corrigir user
    sed -i 's/^user nginx;/user www-data;/' /etc/nginx/nginx.conf

    # Corrigir upstream
    sed -i 's/server biorempp-app:8050;/server localhost:8080;/' /etc/nginx/nginx.conf

    # Adicionar sites-enabled (se não existir)
    if ! grep -q "sites-enabled" /etc/nginx/nginx.conf; then
        sed -i '/include \/etc\/nginx\/conf.d\/\*.conf;/a\    include /etc/nginx/sites-enabled/*;' /etc/nginx/nginx.conf
    fi

    log_info "Correções aplicadas manualmente"
fi

echo ""

# ============================================================================
# PASSO 3: Instalar biorempp.conf
# ============================================================================
log_step "3/5 - Instalando configuração do site BioRemPP..."

if [ -f "$SCRIPT_DIR/biorempp.conf.production" ]; then
    cp "$SCRIPT_DIR/biorempp.conf.production" /etc/nginx/sites-available/biorempp
    log_info "biorempp.conf instalado em /etc/nginx/sites-available/"
elif [ -f "$SCRIPT_DIR/nginx/biorempp.conf" ]; then
    # Usar arquivo do diretório nginx do projeto
    log_warn "Usando biorempp.conf do diretório nginx/"
    log_warn "ATENÇÃO: Este arquivo pode estar configurado para Docker"

    read -p "Deseja continuar? (s/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[SsYy]$ ]]; then
        log_error "Instalação cancelada"
        exit 1
    fi

    cp "$SCRIPT_DIR/nginx/biorempp.conf" /etc/nginx/sites-available/biorempp
else
    log_error "Nenhum arquivo biorempp.conf encontrado"
    log_info "Procurado em:"
    log_info "  - $SCRIPT_DIR/biorempp.conf.production"
    log_info "  - $SCRIPT_DIR/nginx/biorempp.conf"
    exit 1
fi

# Criar link simbólico
ln -sf /etc/nginx/sites-available/biorempp /etc/nginx/sites-enabled/biorempp
log_info "Link simbólico criado em /etc/nginx/sites-enabled/"

# Remover site default (opcional)
if [ -L /etc/nginx/sites-enabled/default ]; then
    rm -f /etc/nginx/sites-enabled/default
    log_info "Site default removido (opcional)"
fi

echo ""

# ============================================================================
# PASSO 4: Testar configuração
# ============================================================================
log_step "4/5 - Testando configuração do Nginx..."

if nginx -t; then
    echo ""
    log_info "${GREEN}✓ Configuração do Nginx está OK!${NC}"
else
    echo ""
    log_error "Erro na configuração do Nginx!"
    log_info "Restaurando backup..."

    if [ -f "$BACKUP_DIR/nginx.conf" ]; then
        cp "$BACKUP_DIR/nginx.conf" /etc/nginx/nginx.conf
    fi
    if [ -f "$BACKUP_DIR/biorempp" ]; then
        cp "$BACKUP_DIR/biorempp" /etc/nginx/sites-available/biorempp
    fi

    log_info "Backup restaurado. Configuração anterior mantida."
    exit 1
fi

echo ""

# ============================================================================
# PASSO 5: Recarregar Nginx
# ============================================================================
log_step "5/5 - Recarregando Nginx..."

if systemctl reload nginx; then
    log_info "${GREEN}✓ Nginx recarregado com sucesso!${NC}"
else
    log_error "Erro ao recarregar Nginx"
    log_info "Tente manualmente: sudo systemctl reload nginx"
    exit 1
fi

echo ""

# ============================================================================
# RESUMO
# ============================================================================
echo -e "${GREEN}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║${NC}              ${GREEN}✓ Instalação Concluída!${NC}                        ${GREEN}║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""
log_info "Configurações aplicadas:"
echo ""
echo "  1. nginx.conf:"
echo "     • user: www-data (Ubuntu)"
echo "     • upstream: localhost:8080"
echo "     • include: sites-enabled/*"
echo ""
echo "  2. biorempp.conf:"
echo "     • Instalado em: /etc/nginx/sites-available/biorempp"
echo "     • Link criado em: /etc/nginx/sites-enabled/biorempp"
echo ""
log_info "Backup salvo em: $BACKUP_DIR"
echo ""
log_info "Próximos passos:"
echo ""
echo "  1. Configurar arquivo .env da aplicação"
echo "     cd ~/BioPotExA"
echo "     cp .env.production .env"
echo "     nano .env  # Configurar SECRET_KEY (gerar com: python3 -c \"import secrets; print(secrets.token_hex(32))\")"
echo ""
echo "  2. Iniciar aplicação BioRemPP"
echo "     ./start.sh"
echo ""
echo "  3. Verificar funcionamento"
echo "     ./status.sh"
echo "     curl http://localhost:8080/health"
echo "     curl http://localhost/health"
echo ""

# Verificar se aplicação está rodando
if lsof -i :8080 &> /dev/null; then
    log_info "${GREEN}✓ Aplicação detectada na porta 8080${NC}"
    echo ""
    log_info "Testando health check..."
    if curl -s http://localhost/health | grep -q "healthy"; then
        echo ""
        log_info "${GREEN}✓✓✓ TUDO FUNCIONANDO! ✓✓✓${NC}"
        echo ""
    else
        log_warn "Aplicação respondendo mas health check falhou"
        log_info "Verifique os logs: ./logs.sh"
    fi
else
    log_warn "Aplicação ainda não está rodando na porta 8080"
    log_info "Inicie com: cd ~/BioPotExA && ./start.sh"
fi

echo ""
log_info "Para ver logs do Nginx:"
echo "  sudo tail -f /var/log/nginx/error.log"
echo ""

exit 0
