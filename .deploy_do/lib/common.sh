#!/bin/bash
# ============================================================================
# BioRemPP v1.0 - Biblioteca Compartilhada de Funções
# ============================================================================
# Funções comuns para todos os scripts de deploy/produção
# Prefixo: biorempp_ (evitar conflitos)
# ============================================================================

# Prevent direct execution
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    echo "ERRO: Esta biblioteca deve ser sourced, não executada diretamente"
    echo "Use: source .deploy_do/lib/common.sh"
    exit 1
fi

# ============================================================================
# Carregar Configurações
# ============================================================================
BIOREMPP_LIB_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
source "$BIOREMPP_LIB_DIR/deploy_config.sh" || {
    echo "ERRO: Não foi possível carregar deploy_config.sh"
    return 1
}

# ============================================================================
# CORES - Terminal
# ============================================================================
export BIOREMPP_COLOR_RED='\033[0;31m'
export BIOREMPP_COLOR_GREEN='\033[0;32m'
export BIOREMPP_COLOR_YELLOW='\033[1;33m'
export BIOREMPP_COLOR_BLUE='\033[0;34m'
export BIOREMPP_COLOR_CYAN='\033[0;36m'
export BIOREMPP_COLOR_NC='\033[0m'  # No Color

# ============================================================================
# FUNÇÕES DE LOG
# ============================================================================

biorempp_log_info() {
    echo -e "${BIOREMPP_COLOR_GREEN}[INFO]${BIOREMPP_COLOR_NC} $1"
}

biorempp_log_warn() {
    echo -e "${BIOREMPP_COLOR_YELLOW}[AVISO]${BIOREMPP_COLOR_NC} $1"
}

biorempp_log_error() {
    echo -e "${BIOREMPP_COLOR_RED}[ERRO]${BIOREMPP_COLOR_NC} $1"
}

biorempp_log_step() {
    echo -e "${BIOREMPP_COLOR_BLUE}[PASSO]${BIOREMPP_COLOR_NC} $1"
}

biorempp_log_success() {
    echo -e "${BIOREMPP_COLOR_GREEN}[SUCESSO]${BIOREMPP_COLOR_NC} $1"
}

biorempp_log_debug() {
    if [[ "$BIOREMPP_DEBUG" == "true" ]]; then
        echo -e "${BIOREMPP_COLOR_CYAN}[DEBUG]${BIOREMPP_COLOR_NC} $1"
    fi
}

# ============================================================================
# BANNER
# ============================================================================

biorempp_banner() {
    local title="$1"
    echo ""
    echo -e "${BIOREMPP_COLOR_BLUE}╔════════════════════════════════════════════════════════════════╗${BIOREMPP_COLOR_NC}"
    echo -e "${BIOREMPP_COLOR_BLUE}║${BIOREMPP_COLOR_NC}     ${BIOREMPP_COLOR_GREEN}${title}${BIOREMPP_COLOR_NC}"
    echo -e "${BIOREMPP_COLOR_BLUE}╚════════════════════════════════════════════════════════════════╝${BIOREMPP_COLOR_NC}"
    echo ""
}

# ============================================================================
# FUNÇÕES DE PERGUNTA INTERATIVA
# ============================================================================

biorempp_ask_yes_no() {
    local question="$1"
    local default="${2:-N}"  # Default N

    while true; do
        if [[ "$default" == "Y" ]]; then
            read -p "$question (S/n): " -n 1 -r
        else
            read -p "$question (s/N): " -n 1 -r
        fi
        echo

        if [[ -z "$REPLY" ]]; then
            REPLY="$default"
        fi

        case "$REPLY" in
            [SsYy]) return 0 ;;
            [Nn]) return 1 ;;
            *) echo "Por favor responda s (sim) ou n (não)." ;;
        esac
    done
}

# ============================================================================
# VERIFICAÇÕES DE SISTEMA
# ============================================================================

biorempp_check_root() {
    if [[ "$EUID" -eq 0 ]]; then
        return 0
    fi
    return 1
}

biorempp_check_sudo() {
    if biorempp_check_root; then
        return 0
    fi

    if sudo -n true 2>/dev/null; then
        return 0
    fi

    biorempp_log_error "Este script precisa de permissões sudo"
    biorempp_log_info "Execute: sudo $0 ou configure sudoers"
    return 1
}

biorempp_check_command() {
    local cmd="$1"
    if command -v "$cmd" &>/dev/null; then
        return 0
    fi
    return 1
}

biorempp_check_python() {
    if ! biorempp_check_command python3; then
        biorempp_log_error "Python 3 não encontrado"
        biorempp_log_info "Execute: sudo apt-get install python3 python3-pip python3-venv"
        return 1
    fi

    local version=$(python3 --version 2>&1 | awk '{print $2}')
    biorempp_log_debug "Python versão: $version"
    return 0
}

biorempp_check_nginx() {
    if ! biorempp_check_command nginx; then
        biorempp_log_error "Nginx não encontrado"
        biorempp_log_info "Execute: sudo apt-get install nginx"
        return 1
    fi

    local version=$(nginx -v 2>&1 | awk -F'/' '{print $2}')
    biorempp_log_debug "Nginx versão: $version"
    return 0
}

# ============================================================================
# VERIFICAÇÕES DE PORTA
# ============================================================================

biorempp_check_port_listening() {
    local port="$1"

    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        return 0  # Porta em uso
    fi
    return 1  # Porta livre
}

biorempp_get_port_pid() {
    local port="$1"
    lsof -Pi :$port -sTCP:LISTEN -t 2>/dev/null || echo ""
}

biorempp_get_port_process() {
    local port="$1"
    local pid=$(biorempp_get_port_pid $port)

    if [[ -n "$pid" ]]; then
        ps -p $pid -o comm= 2>/dev/null || echo "desconhecido"
    else
        echo ""
    fi
}

biorempp_kill_port() {
    local port="$1"
    local force="${2:-false}"

    if ! biorempp_check_port_listening $port; then
        biorempp_log_success "Porta $port já está livre"
        return 0
    fi

    local pid=$(biorempp_get_port_pid $port)
    local process=$(biorempp_get_port_process $port)

    biorempp_log_warn "Porta $port está em uso"
    biorempp_log_info "Processo: $process (PID: $pid)"

    if [[ "$force" != "true" ]]; then
        if ! biorempp_ask_yes_no "Matar processo e liberar porta?"; then
            biorempp_log_error "Cancelado. Porta continua ocupada."
            return 1
        fi
    fi

    kill $pid 2>/dev/null
    sleep 2

    # Verificar se liberou
    if biorempp_check_port_listening $port; then
        biorempp_log_warn "Processo resiliente. Tentando kill -9..."
        kill -9 $pid 2>/dev/null
        sleep 1

        if biorempp_check_port_listening $port; then
            biorempp_log_error "Falha ao liberar porta"
            biorempp_log_info "Execute manualmente: sudo kill -9 $pid"
            return 1
        fi
    fi

    biorempp_log_success "Porta $port liberada"
    return 0
}

# ============================================================================
# VERIFICAÇÕES DE PROCESSO
# ============================================================================

biorempp_check_process_running() {
    local pid="$1"

    if ps -p $pid >/dev/null 2>&1; then
        return 0
    fi
    return 1
}

biorempp_check_app_running() {
    local pidfile="$BIOREMPP_PROJECT_DIR/gunicorn.pid"

    if [[ ! -f "$pidfile" ]]; then
        return 1  # PID file não existe
    fi

    local pid=$(cat "$pidfile" 2>/dev/null)
    if [[ -z "$pid" ]]; then
        return 1  # PID vazio
    fi

    if ! biorempp_check_process_running $pid; then
        return 1  # Processo não está rodando
    fi

    return 0  # App rodando
}

# ============================================================================
# HEALTH CHECK
# ============================================================================

biorempp_check_app_health() {
    local url="http://$BIOREMPP_NGINX_UPSTREAM$BIOREMPP_HEALTH_ENDPOINT"
    local retries="${1:-$BIOREMPP_HEALTH_RETRIES}"

    for i in $(seq 1 $retries); do
        if curl -sf --max-time $BIOREMPP_HEALTH_TIMEOUT "$url" >/dev/null 2>&1; then
            return 0
        fi
        if [[ $i -lt $retries ]]; then
            sleep 2
        fi
    done

    return 1
}

biorempp_wait_for_app_start() {
    local max_retries=30  # 30 segundos
    local retry=0

    biorempp_log_info "Aguardando aplicação iniciar..."

    while [[ $retry -lt $max_retries ]]; do
        if biorempp_check_app_health 1; then
            echo ""
            biorempp_log_success "Aplicação respondendo!"
            return 0
        fi

        echo -n "."
        sleep 1
        ((retry++))
    done

    echo ""
    biorempp_log_error "Timeout: Aplicação não respondeu após ${max_retries}s"
    return 1
}

# ============================================================================
# BACKUP E RESTORE
# ============================================================================

biorempp_backup() {
    local file="$1"
    local backup_name="${2:-$(basename "$file")}"

    if [[ ! -f "$file" ]]; then
        biorempp_log_warn "Arquivo não existe, pulando backup: $file"
        return 1
    fi

    mkdir -p "$BIOREMPP_BACKUP_DIR"
    local timestamp=$(date +%Y%m%d_%H%M%S)
    local backup_file="$BIOREMPP_BACKUP_DIR/${backup_name}.${timestamp}.bak"

    cp "$file" "$backup_file"
    biorempp_log_debug "Backup criado: $backup_file"

    echo "$backup_file"
}

biorempp_restore() {
    local backup_file="$1"
    local target_file="$2"

    if [[ ! -f "$backup_file" ]]; then
        biorempp_log_error "Backup não encontrado: $backup_file"
        return 1
    fi

    cp "$backup_file" "$target_file"
    biorempp_log_info "Restaurado de backup: $backup_file → $target_file"
    return 0
}

biorempp_cleanup_old_backups() {
    local days="${1:-$BIOREMPP_BACKUP_RETENTION_DAYS}"

    if [[ ! -d "$BIOREMPP_BACKUP_DIR" ]]; then
        return 0
    fi

    biorempp_log_info "Limpando backups com mais de $days dias..."
    find "$BIOREMPP_BACKUP_DIR" -type f -name "*.bak" -mtime +$days -delete
}

# ============================================================================
# NGINX HELPERS
# ============================================================================

biorempp_nginx_test() {
    if sudo nginx -t 2>&1 | grep -q "syntax is ok"; then
        return 0
    fi
    return 1
}

biorempp_nginx_reload() {
    if ! biorempp_nginx_test; then
        biorempp_log_error "Configuração do Nginx inválida. Não recarregando."
        return 1
    fi

    if sudo systemctl is-active nginx >/dev/null 2>&1; then
        biorempp_log_info "Recarregando Nginx..."
        sudo systemctl reload nginx
    else
        biorempp_log_info "Nginx não está rodando. Iniciando..."
        sudo systemctl start nginx
    fi
}

biorempp_nginx_status() {
    sudo systemctl status nginx --no-pager -l
}

# ============================================================================
# VENV HELPERS
# ============================================================================

biorempp_create_venv() {
    if [[ -d "$BIOREMPP_VENV_DIR" ]]; then
        biorempp_log_info "Virtual environment já existe"
        return 0
    fi

    biorempp_log_info "Criando virtual environment..."
    python3 -m venv "$BIOREMPP_VENV_DIR"

    if [[ ! -d "$BIOREMPP_VENV_DIR" ]]; then
        biorempp_log_error "Falha ao criar virtual environment"
        return 1
    fi

    biorempp_log_success "Virtual environment criado"
    return 0
}

biorempp_activate_venv() {
    if [[ ! -d "$BIOREMPP_VENV_DIR" ]]; then
        biorempp_log_error "Virtual environment não existe"
        return 1
    fi

    source "$BIOREMPP_VENV_DIR/bin/activate"
}

biorempp_install_deps() {
    biorempp_log_info "Instalando dependências..."

    biorempp_activate_venv || return 1

    pip install --upgrade pip setuptools wheel -q
    pip install -r "$BIOREMPP_PROJECT_DIR/requirements.txt" -q

    deactivate
    biorempp_log_success "Dependências instaladas"
}

# ============================================================================
# DNS HELPERS
# ============================================================================

biorempp_check_dns() {
    if ! biorempp_check_command dig; then
        biorempp_log_warn "dig não instalado. Pulando verificação DNS."
        return 0
    fi

    biorempp_log_info "Verificando DNS para $BIOREMPP_SERVER_DOMAIN..."

    local resolved_ip=$(dig +short $BIOREMPP_SERVER_DOMAIN 2>/dev/null | head -1)

    if [[ "$resolved_ip" == "$BIOREMPP_SERVER_IP" ]]; then
        biorempp_log_success "DNS configurado corretamente"
        return 0
    else
        biorempp_log_warn "DNS não resolve ou não propagou:"
        echo "  Esperado: $BIOREMPP_SERVER_IP"
        echo "  Resolvido: ${resolved_ip:-nada}"
        echo "  Aguardar propagação DNS (até 48h)"
        return 1
    fi
}

# ============================================================================
# VALIDAÇÃO DE CONFIGURAÇÕES
# ============================================================================

biorempp_validate_config_sync() {
    biorempp_log_info "Validando sincronização de configurações..."

    local errors=0

    # Carregar .env se existir
    if [[ -f "$BIOREMPP_PROJECT_DIR/.env" ]]; then
        set -a
        source "$BIOREMPP_PROJECT_DIR/.env"
        set +a
    fi

    # Validar TIMEOUT
    local env_timeout=${BIOREMPP_TIMEOUT:-300}
    local config_timeout=${BIOREMPP_NGINX_TIMEOUT:-300}

    if [[ "$env_timeout" -gt "$config_timeout" ]]; then
        biorempp_log_error "Timeout desincronizado:"
        echo "  .env BIOREMPP_TIMEOUT: ${env_timeout}s"
        echo "  nginx timeout: ${config_timeout}s"
        echo "  FIX: Aumentar BIOREMPP_NGINX_TIMEOUT em deploy_config.sh"
        ((errors++))
    fi

    # Validar UPLOAD SIZE
    local env_upload=${BIOREMPP_UPLOAD_MAX_SIZE_MB:-100}
    local nginx_upload=${BIOREMPP_NGINX_UPLOAD_MAX:-"100M"}
    local nginx_upload_num=${nginx_upload%M}

    if [[ "$env_upload" -gt "$nginx_upload_num" ]]; then
        biorempp_log_error "Upload size desincronizado:"
        echo "  .env BIOREMPP_UPLOAD_MAX_SIZE_MB: ${env_upload}MB"
        echo "  nginx client_max_body_size: ${nginx_upload}"
        echo "  FIX: Aumentar BIOREMPP_NGINX_UPLOAD_MAX em deploy_config.sh"
        ((errors++))
    fi

    if [[ $errors -eq 0 ]]; then
        biorempp_log_success "Configurações sincronizadas"
        return 0
    else
        biorempp_log_error "$errors problema(s) de configuração"
        return 1
    fi
}

# ============================================================================
# INICIALIZAÇÃO
# ============================================================================

# Criar diretórios necessários
mkdir -p "$BIOREMPP_LOGS_DIR" "$BIOREMPP_BACKUP_DIR"

biorempp_log_debug "Biblioteca common.sh carregada com sucesso"
