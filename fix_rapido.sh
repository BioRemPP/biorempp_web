#!/bin/bash
# ============================================================================
# Fix Rápido - BioRemPP v1.0
# ============================================================================
# Script para corrigir erros comuns de setup automaticamente
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
echo -e "${BLUE}║${NC}     ${GREEN}Fix Rápido - BioRemPP v1.0${NC}                            ${BLUE}║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""

log_warn "Este script irá:"
echo "  1. Parar processos em conflito"
echo "  2. Recriar virtual environment"
echo "  3. Configurar .env corretamente"
echo "  4. Reinstalar dependências"
echo "  5. Corrigir Nginx se necessário"
echo "  6. Iniciar aplicação"
echo ""
read -p "Continuar? (s/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[SsYy]$ ]]; then
    log_error "Cancelado pelo usuário"
    exit 1
fi

# ============================================================================
# PASSO 1: Parar tudo
# ============================================================================
log_step "1/6 - Parando processos..."

# Parar aplicação se estiver rodando
if [ -f "stop.sh" ]; then
    ./stop.sh 2>/dev/null || true
    log_info "Script stop.sh executado"
fi

# Matar processos Python na porta 8080
if sudo lsof -i :8080 >/dev/null 2>&1; then
    log_warn "Porta 8080 em uso, matando processos..."
    sudo lsof -t -i :8080 | xargs -r sudo kill -9 2>/dev/null || true
    sleep 2
fi

# Matar screens
if screen -ls | grep -q biorempp; then
    log_warn "Screen biorempp encontrado, encerrando..."
    screen -X -S biorempp quit 2>/dev/null || true
fi

# Matar processos gunicorn órfãos
pkill -9 -f "gunicorn.*biorempp" 2>/dev/null || true

log_info "Processos parados"
echo ""

# ============================================================================
# PASSO 2: Recriar virtual environment
# ============================================================================
log_step "2/6 - Recriando virtual environment..."

# Remover venv antigo
if [ -d "venv" ]; then
    log_info "Removendo venv antigo..."
    rm -rf venv
fi

# Criar novo
log_info "Criando novo venv..."
python3 -m venv venv

# Ativar
source venv/bin/activate

# Atualizar pip
log_info "Atualizando pip..."
pip install --upgrade pip setuptools wheel -q

log_info "Virtual environment criado"
echo ""

# ============================================================================
# PASSO 3: Instalar dependências críticas primeiro
# ============================================================================
log_step "3/6 - Instalando dependências..."

# Instalar build tools se necessário
log_info "Verificando build tools..."
if ! gcc --version >/dev/null 2>&1; then
    log_warn "GCC não encontrado, instalando..."
    sudo apt-get update -qq
    sudo apt-get install -y gcc python3-dev -qq
fi

# Instalar gevent separadamente (pode dar erro de compilação)
log_info "Instalando gevent..."
pip install gevent greenlet -q || {
    log_warn "Erro ao instalar gevent, tentando com build deps..."
    sudo apt-get install -y python3-dev gcc -qq
    pip install gevent greenlet
}

# Instalar todas as dependências
log_info "Instalando todas as dependências..."
pip install -r requirements.txt -q

log_info "Dependências instaladas"
echo ""

# ============================================================================
# PASSO 4: Configurar .env
# ============================================================================
log_step "4/6 - Configurando .env..."

# Backup se existir
if [ -f ".env" ]; then
    cp .env .env.backup_$(date +%Y%m%d_%H%M%S)
    log_info "Backup do .env criado"
fi

# Copiar template
cp .env.production .env
log_info ".env criado a partir de .env.production"

# Gerar SECRET_KEY
log_info "Gerando SECRET_KEY..."
SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))")

# Substituir no .env
sed -i "s/SECRET_KEY=.*/SECRET_KEY=$SECRET_KEY/" .env

log_info "SECRET_KEY configurada: ${SECRET_KEY:0:16}..."

# Verificar configurações importantes
log_info "Configurações aplicadas:"
grep -E "^(BIOREMPP_WORKERS|BIOREMPP_WORKER_CLASS|BIOREMPP_PORT|DOMAIN)=" .env

echo ""

# ============================================================================
# PASSO 5: Verificar/Corrigir Nginx
# ============================================================================
log_step "5/6 - Verificando Nginx..."

# Verificar se Nginx está instalado
if ! command -v nginx >/dev/null 2>&1; then
    log_error "Nginx não está instalado!"
    log_info "Instale com: sudo apt-get install nginx"
    exit 1
fi

# Testar configuração
log_info "Testando configuração Nginx..."
if sudo nginx -t >/dev/null 2>&1; then
    log_info "Configuração Nginx OK"
else
    log_error "Erro na configuração Nginx"
    sudo nginx -t
    echo ""
    read -p "Tentar corrigir Nginx automaticamente? (s/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[SsYy]$ ]]; then
        log_info "Aplicando correções Nginx..."

        # Backup
        sudo cp /etc/nginx/nginx.conf /etc/nginx/nginx.conf.backup_$(date +%Y%m%d_%H%M%S)

        # Aplicar configs
        sudo cp nginx.conf.production /etc/nginx/nginx.conf
        sudo cp biorempp.conf.production /etc/nginx/sites-available/biorempp
        sudo ln -sf /etc/nginx/sites-available/biorempp /etc/nginx/sites-enabled/biorempp
        sudo rm -f /etc/nginx/sites-enabled/default

        # Testar novamente
        if sudo nginx -t; then
            log_info "Nginx corrigido!"
        else
            log_error "Ainda há erros no Nginx. Verifique manualmente."
            exit 1
        fi
    fi
fi

# Garantir que Nginx está rodando
if ! sudo systemctl is-active nginx >/dev/null 2>&1; then
    log_warn "Nginx não está rodando, iniciando..."
    sudo systemctl start nginx || {
        log_error "Falha ao iniciar Nginx"
        log_info "Tente manualmente: sudo systemctl start nginx"
        log_info "Ver logs: sudo journalctl -xeu nginx"
    }
fi

echo ""

# ============================================================================
# PASSO 6: Iniciar aplicação
# ============================================================================
log_step "6/6 - Iniciando aplicação..."

# Garantir que scripts são executáveis
chmod +x *.sh 2>/dev/null || true

# Testar se aplicação inicia manualmente primeiro
log_info "Testando inicialização..."

# Criar diretório de logs se não existir
mkdir -p logs

# Tentar iniciar em background por 5 segundos para ver se há erros
timeout 5 python3 biorempp_app.py > /tmp/biorempp_test.log 2>&1 &
TEST_PID=$!

sleep 3

# Verificar se ainda está rodando
if kill -0 $TEST_PID 2>/dev/null; then
    log_info "Aplicação inicia sem erros!"
    kill $TEST_PID 2>/dev/null || true
else
    log_error "Aplicação falhou ao iniciar"
    log_info "Últimas linhas do log:"
    cat /tmp/biorempp_test.log | tail -20
    echo ""
    log_error "Corrija os erros acima e tente novamente"
    exit 1
fi

# Iniciar com script
log_info "Iniciando com start.sh..."
./start.sh

sleep 3

echo ""

# ============================================================================
# VERIFICAÇÃO FINAL
# ============================================================================
echo -e "${BLUE}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║${NC}              ${GREEN}Verificação Final${NC}                              ${BLUE}║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Testar aplicação
echo -n "• Aplicação rodando: "
if pgrep -f "gunicorn.*biorempp" >/dev/null 2>&1; then
    echo -e "${GREEN}SIM${NC}"
else
    echo -e "${RED}NÃO${NC}"
fi

echo -n "• Health check localhost:8080: "
if curl -s -f http://localhost:8080/health >/dev/null 2>&1; then
    echo -e "${GREEN}OK${NC}"
else
    echo -e "${RED}FALHOU${NC}"
fi

echo -n "• Health check via IP: "
if curl -s -f http://159.203.108.228/health >/dev/null 2>&1; then
    echo -e "${GREEN}OK${NC}"
else
    echo -e "${RED}FALHOU${NC}"
fi

echo -n "• Health check via domínio: "
if curl -s -f http://biorempp.cloud/health >/dev/null 2>&1; then
    echo -e "${GREEN}OK${NC}"
else
    echo -e "${YELLOW}FALHOU (DNS?)${NC}"
fi

echo -n "• Nginx rodando: "
if sudo systemctl is-active nginx >/dev/null 2>&1; then
    echo -e "${GREEN}SIM${NC}"
else
    echo -e "${RED}NÃO${NC}"
fi

echo ""

# Status
if [ -f "status.sh" ]; then
    ./status.sh
fi

echo ""
echo -e "${GREEN}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║${NC}                    ${GREEN}Fix Concluído!${NC}                             ${GREEN}║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""

log_info "Próximos passos:"
echo "  1. Verificar logs: ./logs.sh"
echo "  2. Ver status: ./status.sh"
echo "  3. Acessar: http://biorempp.cloud"
echo "  4. Configurar SSL: migration/03_CONFIGURAR_SSL.md"
echo ""

deactivate 2>/dev/null || true
exit 0
