#!/bin/bash
# ============================================================================
# BioRemPP v1.0 - Configuração de Deploy Centralizada
# ============================================================================
# Este arquivo contém TODAS as configurações específicas do servidor.
# Para redeploy em outro servidor, edite APENAS este arquivo.
# ============================================================================

# Prevent direct execution
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    echo "ERRO: Este arquivo deve ser sourced, não executado diretamente"
    echo "Use: source deploy_config.sh"
    exit 1
fi

# ============================================================================
# SERVIDOR - Informações da Infraestrutura
# ============================================================================
export BIOREMPP_SERVER_IP="159.203.108.228"
export BIOREMPP_SERVER_DOMAIN="biorempp.cloud"
export BIOREMPP_SERVER_EMAIL="biorempp@gmail.com"

# Recursos do servidor (Digital Ocean - 2GB RAM, 1 vCPU)
export BIOREMPP_SERVER_RAM_GB=2
export BIOREMPP_SERVER_VCPUS=1

# ============================================================================
# APLICAÇÃO - Configurações do Gunicorn
# ============================================================================
# OTIMIZADO para servidor com recursos limitados (2GB RAM, 1 vCPU)
#
# IMPORTANTE: Com recursos limitados, MENOS workers = MELHOR performance!
# Múltiplos workers causam contenção de memória/CPU (thrashing)
#
# Configuração otimizada:
# - 1 worker: Evita competição por recursos
# - gevent: Permite concorrência via greenlets (leve)
# - threads=1000: Muitas conexões simultâneas por worker
export BIOREMPP_APP_WORKERS=1
export BIOREMPP_APP_WORKER_CLASS="gevent"
export BIOREMPP_APP_WORKER_CONNECTIONS=1000  # Conexões simultâneas por worker
export BIOREMPP_APP_THREADS=1000             # Threads por worker (para gevent)
export BIOREMPP_APP_PORT=8080
export BIOREMPP_APP_BIND="0.0.0.0:8080"

# Timeouts (em segundos)
# Análises podem demorar, então timeout alto
export BIOREMPP_APP_TIMEOUT=600           # 10 minutos (aumentado para análises pesadas)
export BIOREMPP_APP_GRACEFUL_TIMEOUT=30   # Shutdown gracioso
export BIOREMPP_APP_KEEPALIVE=5

# Otimizações adicionais para recursos limitados
export BIOREMPP_APP_MAX_REQUESTS=1000     # Reciclar worker após N requisições (previne memory leak)
export BIOREMPP_APP_MAX_REQUESTS_JITTER=50  # Randomização para evitar restart simultâneo
export BIOREMPP_APP_PRELOAD=true          # Pre-carregar app (economia de memória)

# ============================================================================
# NGINX - Configurações do Reverse Proxy
# ============================================================================
# Upstream (IMPORTANTE: Usar IPv4 explícito, não localhost)
export BIOREMPP_NGINX_UPSTREAM="127.0.0.1:8080"

# Limites de upload
export BIOREMPP_NGINX_UPLOAD_MAX="100M"

# Timeouts (devem ser >= APP_TIMEOUT)
# Sincronizado com BIOREMPP_APP_TIMEOUT=600
export BIOREMPP_NGINX_TIMEOUT=600

# Rate Limiting (ajustado para Dash com muitos callbacks)
export BIOREMPP_NGINX_RATE_LIMIT_API="300r/m"      # 300 req/min (5 req/s)
export BIOREMPP_NGINX_RATE_LIMIT_GENERAL="600r/m"  # 600 req/min (10 req/s)
export BIOREMPP_NGINX_BURST_API=50
export BIOREMPP_NGINX_BURST_GENERAL=100

# ============================================================================
# SSL/HTTPS - Configurações do Certbot
# ============================================================================
export BIOREMPP_SSL_ENABLED=false  # Alterar para true após configurar SSL
export BIOREMPP_SSL_DOMAINS="biorempp.cloud www.biorempp.cloud"
export BIOREMPP_SSL_EMAIL="$BIOREMPP_SERVER_EMAIL"

# ============================================================================
# DIRETÓRIOS - Estrutura do Projeto (Dinâmico)
# ============================================================================
# Detectar diretório do projeto automaticamente
BIOREMPP_SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export BIOREMPP_PROJECT_DIR="$BIOREMPP_SCRIPT_DIR"
export BIOREMPP_VENV_DIR="$BIOREMPP_PROJECT_DIR/venv"
export BIOREMPP_LOGS_DIR="$BIOREMPP_PROJECT_DIR/logs"
export BIOREMPP_BACKUP_DIR="$BIOREMPP_PROJECT_DIR/.backups"
export BIOREMPP_DEPLOY_LIB="$BIOREMPP_PROJECT_DIR/.deploy_do/lib"

# ============================================================================
# AMBIENTE - Configurações Gerais
# ============================================================================
export BIOREMPP_ENV="production"
export BIOREMPP_DEBUG=false
export BIOREMPP_LOG_LEVEL="INFO"

# ============================================================================
# MONITORAMENTO - Health Checks
# ============================================================================
export BIOREMPP_HEALTH_ENDPOINT="/health"
export BIOREMPP_HEALTH_TIMEOUT=10
export BIOREMPP_HEALTH_RETRIES=3

# ============================================================================
# BACKUP - Configurações de Backup
# ============================================================================
export BIOREMPP_BACKUP_RETENTION_DAYS=7
export BIOREMPP_BACKUP_NGINX_DIR="/etc/nginx/backup"

# ============================================================================
# VALIDAÇÃO - Verificar Valores Obrigatórios
# ============================================================================
validate_config() {
    local errors=0

    if [[ -z "$BIOREMPP_SERVER_IP" ]]; then
        echo "ERRO: BIOREMPP_SERVER_IP não configurado"
        ((errors++))
    fi

    if [[ -z "$BIOREMPP_SERVER_DOMAIN" ]]; then
        echo "ERRO: BIOREMPP_SERVER_DOMAIN não configurado"
        ((errors++))
    fi

    if [[ -z "$BIOREMPP_SERVER_EMAIL" ]]; then
        echo "ERRO: BIOREMPP_SERVER_EMAIL não configurado"
        ((errors++))
    fi

    if [[ $errors -gt 0 ]]; then
        echo "ERRO: $errors configurações obrigatórias faltando"
        return 1
    fi

    return 0
}

# Auto-validar quando sourced
if [[ "${BASH_SOURCE[0]}" != "${0}" ]]; then
    validate_config || return 1
fi
