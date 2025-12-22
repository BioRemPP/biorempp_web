#!/bin/bash
# ============================================================================
# Diagnóstico Rápido - BioRemPP v1.0
# ============================================================================
# Execute este script para diagnosticar erros de setup
# ============================================================================

# Cores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║${NC}     ${GREEN}Diagnóstico Rápido - BioRemPP v1.0${NC}                    ${BLUE}║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""

# ============================================================================
# 1. VERIFICAR PORTAS
# ============================================================================
echo -e "${BLUE}[1/8]${NC} Verificando portas..."

echo -n "  • Porta 8080 (aplicação): "
if sudo lsof -i :8080 >/dev/null 2>&1; then
    echo -e "${YELLOW}EM USO${NC}"
    sudo lsof -i :8080 | grep LISTEN
else
    echo -e "${GREEN}LIVRE${NC}"
fi

echo -n "  • Porta 80 (nginx): "
if sudo lsof -i :80 >/dev/null 2>&1; then
    echo -e "${GREEN}EM USO (esperado)${NC}"
else
    echo -e "${YELLOW}LIVRE (nginx não está rodando?)${NC}"
fi

echo ""

# ============================================================================
# 2. VERIFICAR NGINX
# ============================================================================
echo -e "${BLUE}[2/8]${NC} Verificando Nginx..."

echo -n "  • Nginx instalado: "
if command -v nginx >/dev/null 2>&1; then
    echo -e "${GREEN}$(nginx -v 2>&1)${NC}"
else
    echo -e "${RED}NÃO INSTALADO${NC}"
fi

echo -n "  • Nginx rodando: "
if sudo systemctl is-active nginx >/dev/null 2>&1; then
    echo -e "${GREEN}SIM${NC}"
else
    echo -e "${RED}NÃO${NC}"
fi

echo -n "  • Configuração válida: "
if sudo nginx -t >/dev/null 2>&1; then
    echo -e "${GREEN}OK${NC}"
else
    echo -e "${RED}ERRO${NC}"
    sudo nginx -t
fi

echo ""

# ============================================================================
# 3. VERIFICAR PYTHON
# ============================================================================
echo -e "${BLUE}[3/8]${NC} Verificando Python..."

echo -n "  • Python instalado: "
if command -v python3 >/dev/null 2>&1; then
    echo -e "${GREEN}$(python3 --version)${NC}"
else
    echo -e "${RED}NÃO INSTALADO${NC}"
fi

echo -n "  • Virtual env: "
if [ -d "venv" ]; then
    echo -e "${GREEN}EXISTE${NC}"
else
    echo -e "${RED}NÃO EXISTE${NC}"
fi

if [ -d "venv" ]; then
    source venv/bin/activate
    echo -n "  • Gunicorn: "
    if pip show gunicorn >/dev/null 2>&1; then
        echo -e "${GREEN}$(pip show gunicorn | grep Version)${NC}"
    else
        echo -e "${RED}NÃO INSTALADO${NC}"
    fi

    echo -n "  • Gevent: "
    if pip show gevent >/dev/null 2>&1; then
        echo -e "${GREEN}$(pip show gevent | grep Version)${NC}"
    else
        echo -e "${RED}NÃO INSTALADO${NC}"
    fi
    deactivate
fi

echo ""

# ============================================================================
# 4. VERIFICAR .ENV
# ============================================================================
echo -e "${BLUE}[4/8]${NC} Verificando .env..."

echo -n "  • Arquivo .env: "
if [ -f ".env" ]; then
    echo -e "${GREEN}EXISTE${NC}"
else
    echo -e "${RED}NÃO EXISTE${NC}"
fi

if [ -f ".env" ]; then
    echo -n "  • SECRET_KEY configurada: "
    SECRET_KEY=$(grep "^SECRET_KEY=" .env | cut -d'=' -f2)
    if [[ "$SECRET_KEY" == *"REPLACE"* ]] || [ -z "$SECRET_KEY" ]; then
        echo -e "${RED}NÃO (precisa gerar)${NC}"
    else
        echo -e "${GREEN}SIM (${SECRET_KEY:0:10}...)${NC}"
    fi

    echo "  • Configurações:"
    grep -E "^(BIOREMPP_WORKERS|BIOREMPP_WORKER_CLASS|BIOREMPP_PORT|DOMAIN)=" .env | while read line; do
        echo "    $line"
    done
fi

echo ""

# ============================================================================
# 5. VERIFICAR PROCESSOS
# ============================================================================
echo -e "${BLUE}[5/8]${NC} Verificando processos..."

echo -n "  • Gunicorn rodando: "
if pgrep -f "gunicorn.*biorempp" >/dev/null 2>&1; then
    echo -e "${GREEN}SIM${NC}"
    pgrep -af "gunicorn.*biorempp" | head -5
else
    echo -e "${YELLOW}NÃO${NC}"
fi

echo -n "  • Screen biorempp: "
if screen -ls | grep -q biorempp; then
    echo -e "${YELLOW}SIM (legado ainda rodando?)${NC}"
    screen -ls | grep biorempp
else
    echo -e "${GREEN}NÃO (correto)${NC}"
fi

echo ""

# ============================================================================
# 6. TESTAR CONECTIVIDADE
# ============================================================================
echo -e "${BLUE}[6/8]${NC} Testando conectividade..."

echo -n "  • localhost:8080 responde: "
if curl -s -f http://localhost:8080/health >/dev/null 2>&1; then
    echo -e "${GREEN}SIM${NC}"
else
    echo -e "${RED}NÃO${NC}"
fi

echo -n "  • 159.203.108.228:80 responde: "
if curl -s -f http://159.203.108.228/health >/dev/null 2>&1; then
    echo -e "${GREEN}SIM${NC}"
else
    echo -e "${RED}NÃO${NC}"
fi

echo -n "  • biorempp.cloud responde: "
if curl -s -f http://biorempp.cloud/health >/dev/null 2>&1; then
    echo -e "${GREEN}SIM${NC}"
else
    echo -e "${YELLOW}NÃO (DNS pode não estar configurado)${NC}"
fi

echo ""

# ============================================================================
# 7. VERIFICAR LOGS
# ============================================================================
echo -e "${BLUE}[7/8]${NC} Últimos erros (se houver)..."

if [ -f "logs/biorempp.log" ]; then
    echo "  • Logs da aplicação (últimas 10 linhas de erro):"
    grep -i error logs/biorempp.log | tail -10 || echo "    Nenhum erro encontrado"
else
    echo -e "  ${YELLOW}Arquivo de log não encontrado${NC}"
fi

if [ -f "/var/log/nginx/error.log" ]; then
    echo "  • Logs do Nginx (últimas 5 linhas):"
    sudo tail -5 /var/log/nginx/error.log || echo "    Nenhum erro recente"
fi

echo ""

# ============================================================================
# 8. MEMÓRIA
# ============================================================================
echo -e "${BLUE}[8/8]${NC} Verificando memória..."

free -h | grep -E "Mem:|Swap:"

echo ""

# ============================================================================
# RESUMO
# ============================================================================
echo -e "${BLUE}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║${NC}                    ${GREEN}RESUMO DO DIAGNÓSTICO${NC}                      ${BLUE}║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Determinar problemas
PROBLEMS=0

if ! command -v nginx >/dev/null 2>&1; then
    echo -e "${RED}✗${NC} Nginx não instalado"
    PROBLEMS=$((PROBLEMS + 1))
fi

if ! sudo systemctl is-active nginx >/dev/null 2>&1; then
    echo -e "${RED}✗${NC} Nginx não está rodando"
    PROBLEMS=$((PROBLEMS + 1))
fi

if [ ! -d "venv" ]; then
    echo -e "${RED}✗${NC} Virtual environment não existe"
    PROBLEMS=$((PROBLEMS + 1))
fi

if [ ! -f ".env" ]; then
    echo -e "${RED}✗${NC} Arquivo .env não existe"
    PROBLEMS=$((PROBLEMS + 1))
elif [[ $(grep "^SECRET_KEY=" .env | cut -d'=' -f2) == *"REPLACE"* ]]; then
    echo -e "${RED}✗${NC} SECRET_KEY não configurada"
    PROBLEMS=$((PROBLEMS + 1))
fi

if ! pgrep -f "gunicorn.*biorempp" >/dev/null 2>&1; then
    echo -e "${RED}✗${NC} Aplicação não está rodando"
    PROBLEMS=$((PROBLEMS + 1))
fi

if [ $PROBLEMS -eq 0 ]; then
    echo -e "${GREEN}✓ Nenhum problema crítico detectado!${NC}"
    echo ""
    echo "Se ainda tiver erros, execute:"
    echo "  ./logs.sh --error --lines 50"
else
    echo ""
    echo -e "${YELLOW}Foram encontrados $PROBLEMS problema(s).${NC}"
    echo ""
    echo "Soluções rápidas:"
    echo ""

    if [ ! -d "venv" ] || [ ! -f ".env" ]; then
        echo "1. Recriar ambiente:"
        echo "   rm -rf venv .env"
        echo "   cp .env.production .env"
        echo "   python3 -m venv venv"
        echo "   source venv/bin/activate"
        echo "   pip install -r requirements.txt"
        echo "   # Editar .env e gerar SECRET_KEY"
        echo ""
    fi

    if ! sudo systemctl is-active nginx >/dev/null 2>&1; then
        echo "2. Iniciar Nginx:"
        echo "   sudo systemctl start nginx"
        echo ""
    fi

    if ! pgrep -f "gunicorn.*biorempp" >/dev/null 2>&1; then
        echo "3. Iniciar aplicação:"
        echo "   ./start.sh"
        echo ""
    fi

    echo "Ver guia completo: migration/05_ERROS_COMUNS_SETUP.md"
fi

echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo ""
