#!/bin/bash
# ============================================================================
# BioRemPP v1.0 - Setup Completo (Multi-mode)
# ============================================================================
# Script consolidado para setup, troubleshooting e manutenção
#
# MODOS:
#   (nenhum)       Setup completo inicial
#   --diagnose     Executar diagnóstico completo
#   --fix          Corrigir problemas automaticamente
#   --fix-nginx    Corrigir problema IPv6 do Nginx
#   --ssl          Configurar SSL/HTTPS
#   --help         Mostrar esta ajuda
# ============================================================================

set -e

# ============================================================================
# Carregar biblioteca comum
# ============================================================================
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Verificar se biblioteca existe
if [[ ! -f "$SCRIPT_DIR/.deploy_do/lib/common.sh" ]]; then
    echo "ERRO: Biblioteca não encontrada: .deploy_do/lib/common.sh"
    echo "Execute primeiro: mkdir -p .deploy_do/lib"
    exit 1
fi

source "$SCRIPT_DIR/.deploy_do/lib/common.sh"

# ============================================================================
# Variáveis Globais
# ============================================================================
MODE="install"  # Padrão: instalação normal

# ============================================================================
# Função: Mostrar Ajuda
# ============================================================================
show_help() {
    cat << EOF

BioRemPP v1.0 - Setup Completo

Uso: ./setup_completo.sh [OPÇÃO]

OPÇÕES:
  (nenhuma)      Setup completo inicial
                 - Configura .env
                 - Configura Nginx
                 - Inicia aplicação

  --diagnose     Executar diagnóstico completo
                 - Verifica portas
                 - Verifica processos
                 - Verifica configurações
                 - Mostra problemas encontrados

  --fix          Corrigir problemas automaticamente
                 - Para processos conflitantes
                 - Recria virtual environment
                 - Reinstala dependências
                 - Corrige configurações

  --fix-nginx    Corrigir problema IPv6 do Nginx
                 - Força uso de IPv4 (127.0.0.1)
                 - Aplica correções de rate limiting

  --ssl          Configurar SSL/HTTPS
                 - Instala Certbot
                 - Obtém certificado Let's Encrypt
                 - Configura redirect HTTP→HTTPS

  --help, -h     Mostrar esta ajuda

EXEMPLOS:
  # Setup inicial
  ./setup_completo.sh

  # Diagnosticar problemas
  ./setup_completo.sh --diagnose

  # Corrigir problemas
  ./setup_completo.sh --fix

  # Configurar SSL depois
  ./setup_completo.sh --ssl

DOCS:
  migration/README.md - Guia completo de migração
  migration/05_ERROS_COMUNS_SETUP.md - Troubleshooting

EOF
}

# ============================================================================
# Parse argumentos
# ============================================================================
while [[ $# -gt 0 ]]; do
    case $1 in
        --diagnose|--diagnostic)
            MODE="diagnose"
            shift
            ;;
        --fix)
            MODE="fix"
            shift
            ;;
        --fix-nginx)
            MODE="fix-nginx"
            shift
            ;;
        --ssl)
            MODE="ssl"
            shift
            ;;
        --help|-h)
            show_help
            exit 0
            ;;
        *)
            biorempp_log_error "Opção desconhecida: $1"
            show_help
            exit 1
            ;;
    esac
done

# ============================================================================
# MODO: Instalação Normal
# ============================================================================
run_installation() {
    biorempp_banner "BioRemPP v1.0 - Setup Completo Automatizado"
    echo -e "     ${BIOREMPP_COLOR_BLUE}biorempp.cloud - Digital Ocean NYC3 - 2GB RAM${BIOREMPP_COLOR_NC}"
    echo ""

    # Verificar se está rodando como root
    if biorempp_check_root; then
        biorempp_log_warn "Rodando como root. Recomendado rodar como usuário normal"
        if ! biorempp_ask_yes_no "Continuar mesmo assim?" N; then
            biorempp_log_error "Cancelado pelo usuário"
            exit 1
        fi
    fi

    # PASSO 1: Verificar pré-requisitos
    biorempp_log_step "1/8 - Verificando pré-requisitos..."

    biorempp_check_python || exit 1
    biorempp_check_nginx || exit 1

    # Verificar arquivos necessários
    local required_files=(".env.production" "nginx.conf.production" "biorempp.conf.production")
    for file in "${required_files[@]}"; do
        if [[ ! -f "$BIOREMPP_PROJECT_DIR/$file" ]]; then
            biorempp_log_error "Arquivo não encontrado: $file"
            exit 1
        fi
    done

    biorempp_log_success "Todos os pré-requisitos OK"
    echo ""

    # PASSO 2: Criar .env com SECRET_KEY
    biorempp_log_step "2/8 - Configurando arquivo .env..."

    if [[ -f "$BIOREMPP_PROJECT_DIR/.env" ]]; then
        biorempp_log_warn "Arquivo .env já existe"
        if ! biorempp_ask_yes_no "Sobrescrever?" N; then
            biorempp_log_info "Mantendo .env existente"
        else
            rm "$BIOREMPP_PROJECT_DIR/.env"
            biorempp_log_info "Arquivo .env existente removido"
        fi
    fi

    if [[ ! -f "$BIOREMPP_PROJECT_DIR/.env" ]]; then
        cp "$BIOREMPP_PROJECT_DIR/.env.production" "$BIOREMPP_PROJECT_DIR/.env"
        biorempp_log_success ".env criado a partir de .env.production"

        # Gerar SECRET_KEY
        biorempp_log_info "Gerando SECRET_KEY única..."
        local secret_key=$(python3 -c "import secrets; print(secrets.token_hex(32))")

        sed -i "s/SECRET_KEY=REPLACE_WITH_SECURE_KEY_GENERATE_WITH_PYTHON_SECRETS_TOKEN_HEX/SECRET_KEY=$secret_key/" "$BIOREMPP_PROJECT_DIR/.env"

        biorempp_log_success "SECRET_KEY gerada e configurada"
        biorempp_log_info "SECRET_KEY: ${secret_key:0:10}... (64 caracteres)"
    else
        biorempp_log_info "Usando .env existente"
    fi

    echo ""

    # PASSO 3: Verificar configurações .env
    biorempp_log_step "3/8 - Verificando configurações do .env..."

    if grep -q "REPLACE_WITH_SECURE_KEY" "$BIOREMPP_PROJECT_DIR/.env"; then
        biorempp_log_error "SECRET_KEY não foi configurada no .env!"
        exit 1
    fi

    biorempp_log_success "Configurações do .env:"
    echo "  • BIOREMPP_WORKERS: $(grep '^BIOREMPP_WORKERS=' .env | cut -d'=' -f2)"
    echo "  • BIOREMPP_WORKER_CLASS: $(grep '^BIOREMPP_WORKER_CLASS=' .env | cut -d'=' -f2)"
    echo "  • BIOREMPP_PORT: $(grep '^BIOREMPP_PORT=' .env | cut -d'=' -f2)"
    echo "  • DOMAIN: $(grep '^DOMAIN=' .env | cut -d'=' -f2)"
    echo ""

    # PASSO 4: Validar sincronização de configs
    biorempp_log_step "4/8 - Validando sincronização de configurações..."
    biorempp_validate_config_sync || biorempp_log_warn "Algumas configurações podem estar desincronizadas"
    echo ""

    # PASSO 5: Configurar Nginx
    biorempp_log_step "5/8 - Configurando Nginx..."

    setup_nginx_production || exit 1

    echo ""

    # PASSO 6: Parar aplicação legada
    biorempp_log_step "6/8 - Parando aplicação legada..."

    stop_legacy_app

    echo ""

    # PASSO 7: Preparar scripts
    biorempp_log_step "7/8 - Preparando scripts de gerenciamento..."

    chmod +x "$BIOREMPP_PROJECT_DIR"/*.sh 2>/dev/null || true
    biorempp_log_success "Scripts configurados"

    echo ""

    # PASSO 8: Iniciar BioRemPP v1.0
    biorempp_log_step "8/8 - Iniciando BioRemPP v1.0..."

    if [[ ! -f "$BIOREMPP_PROJECT_DIR/start.sh" ]]; then
        biorempp_log_error "Script start.sh não encontrado"
        exit 1
    fi

    "$BIOREMPP_PROJECT_DIR/start.sh"

    echo ""

    # Verificação final
    show_installation_summary
}

# ============================================================================
# MODO: Diagnóstico
# ============================================================================
run_diagnostic() {
    biorempp_banner "Diagnóstico Completo do Sistema"

    local issues=0

    # 1. Verificar portas
    biorempp_log_step "1/8 - Verificando portas..."
    if biorempp_check_port_listening 8080; then
        local pid=$(biorempp_get_port_pid 8080)
        local process=$(biorempp_get_port_process 8080)
        biorempp_log_info "Porta 8080: EM USO ($process, PID: $pid)"
    else
        biorempp_log_warn "Porta 8080: LIVRE (aplicação não está rodando)"
        ((issues++))
    fi

    if biorempp_check_port_listening 80; then
        biorempp_log_info "Porta 80: EM USO (Nginx)"
    else
        biorempp_log_warn "Porta 80: LIVRE (Nginx não está rodando)"
        ((issues++))
    fi
    echo ""

    # 2. Verificar Nginx
    biorempp_log_step "2/8 - Verificando Nginx..."
    if sudo systemctl is-active nginx >/dev/null 2>&1; then
        biorempp_log_success "Nginx: RODANDO"

        if biorempp_nginx_test; then
            biorempp_log_success "Nginx config: VÁLIDA"
        else
            biorempp_log_error "Nginx config: INVÁLIDA"
            ((issues++))
        fi
    else
        biorempp_log_error "Nginx: PARADO"
        ((issues++))
    fi
    echo ""

    # 3. Verificar aplicação Python
    biorempp_log_step "3/8 - Verificando aplicação Python..."
    if biorempp_check_app_running; then
        biorempp_log_success "Aplicação: RODANDO"

        if biorempp_check_app_health 3; then
            biorempp_log_success "Health check: OK"
        else
            biorempp_log_error "Health check: FALHOU"
            ((issues++))
        fi
    else
        biorempp_log_error "Aplicação: PARADA"
        ((issues++))
    fi
    echo ""

    # 4. Verificar .env
    biorempp_log_step "4/8 - Verificando arquivo .env..."
    if [[ -f "$BIOREMPP_PROJECT_DIR/.env" ]]; then
        biorempp_log_success ".env: EXISTE"

        if grep -q "REPLACE_WITH_SECURE_KEY" "$BIOREMPP_PROJECT_DIR/.env"; then
            biorempp_log_error ".env: SECRET_KEY não configurada"
            ((issues++))
        else
            biorempp_log_success ".env: SECRET_KEY configurada"
        fi
    else
        biorempp_log_error ".env: NÃO EXISTE"
        ((issues++))
    fi
    echo ""

    # 5. Verificar virtual environment
    biorempp_log_step "5/8 - Verificando virtual environment..."
    if [[ -d "$BIOREMPP_VENV_DIR" ]]; then
        biorempp_log_success "Virtual environment: EXISTE"

        if source "$BIOREMPP_VENV_DIR/bin/activate" 2>/dev/null; then
            if python -c "import dash" 2>/dev/null; then
                biorempp_log_success "Dependências: INSTALADAS"
            else
                biorempp_log_error "Dependências: FALTANDO"
                ((issues++))
            fi
            deactivate
        fi
    else
        biorempp_log_error "Virtual environment: NÃO EXISTE"
        ((issues++))
    fi
    echo ""

    # 6. Verificar conectividade
    biorempp_log_step "6/8 - Verificando conectividade..."

    echo -n "  • localhost:8080/health... "
    if curl -sf --max-time 5 "http://localhost:8080/health" >/dev/null 2>&1; then
        echo -e "${BIOREMPP_COLOR_GREEN}✓${BIOREMPP_COLOR_NC}"
    else
        echo -e "${BIOREMPP_COLOR_RED}✗${BIOREMPP_COLOR_NC}"
        ((issues++))
    fi

    echo -n "  • $BIOREMPP_SERVER_IP/health... "
    if curl -sf --max-time 5 "http://$BIOREMPP_SERVER_IP/health" >/dev/null 2>&1; then
        echo -e "${BIOREMPP_COLOR_GREEN}✓${BIOREMPP_COLOR_NC}"
    else
        echo -e "${BIOREMPP_COLOR_RED}✗${BIOREMPP_COLOR_NC}"
        ((issues++))
    fi

    echo -n "  • $BIOREMPP_SERVER_DOMAIN/health... "
    if curl -sf --max-time 5 "http://$BIOREMPP_SERVER_DOMAIN/health" >/dev/null 2>&1; then
        echo -e "${BIOREMPP_COLOR_GREEN}✓${BIOREMPP_COLOR_NC}"
    else
        echo -e "${BIOREMPP_COLOR_YELLOW}⚠${BIOREMPP_COLOR_NC} (DNS pode não estar configurado)"
    fi
    echo ""

    # 7. Verificar DNS
    biorempp_log_step "7/8 - Verificando DNS..."
    biorempp_check_dns || biorempp_log_warn "DNS não está configurado ou não propagou"
    echo ""

    # 8. Verificar memória
    biorempp_log_step "8/8 - Verificando uso de memória..."
    free -h | head -2
    echo ""

    # Resumo
    echo ""
    echo -e "${BIOREMPP_COLOR_BLUE}════════════════════════════════════════════════════════${BIOREMPP_COLOR_NC}"
    if [[ $issues -eq 0 ]]; then
        biorempp_log_success "Nenhum problema encontrado!"
    else
        biorempp_log_warn "$issues problema(s) encontrado(s)"
        echo ""
        biorempp_log_info "Para corrigir automaticamente:"
        echo "  ./setup_completo.sh --fix"
    fi
    echo -e "${BIOREMPP_COLOR_BLUE}════════════════════════════════════════════════════════${BIOREMPP_COLOR_NC}"
    echo ""
}

# ============================================================================
# MODO: Fix Automático
# ============================================================================
run_fix() {
    biorempp_banner "Fix Automático de Problemas"

    if ! biorempp_ask_yes_no "Executar fix completo? Isso irá parar processos e recriar ambiente" N; then
        biorempp_log_error "Cancelado pelo usuário"
        exit 0
    fi

    # 1. Parar processos
    biorempp_log_step "1/6 - Parando todos os processos..."

    if [[ -f "$BIOREMPP_PROJECT_DIR/stop.sh" ]]; then
        "$BIOREMPP_PROJECT_DIR/stop.sh" || true
    fi

    biorempp_kill_port 8080 true || true
    stop_legacy_app

    biorempp_log_success "Processos parados"
    echo ""

    # 2. Limpar PID obsoleto
    biorempp_log_step "2/6 - Limpando arquivos temporários..."
    rm -f "$BIOREMPP_PROJECT_DIR/gunicorn.pid" 2>/dev/null || true
    biorempp_log_success "Arquivos temporários limpos"
    echo ""

    # 3. Recriar virtual environment
    biorempp_log_step "3/6 - Recriando virtual environment..."

    if [[ -d "$BIOREMPP_VENV_DIR" ]]; then
        biorempp_log_info "Removendo venv antigo..."
        rm -rf "$BIOREMPP_VENV_DIR"
    fi

    biorempp_create_venv || exit 1
    echo ""

    # 4. Reinstalar dependências
    biorempp_log_step "4/6 - Reinstalando dependências..."
    biorempp_install_deps || exit 1
    echo ""

    # 5. Corrigir Nginx se necessário
    biorempp_log_step "5/6 - Verificando configuração do Nginx..."

    if grep -q "server localhost:$BIOREMPP_APP_PORT" /etc/nginx/nginx.conf 2>/dev/null; then
        biorempp_log_warn "Detectado 'localhost' - corrigindo para IPv4..."
        fix_nginx_ipv6
    else
        biorempp_log_success "Nginx já está com IPv4 explícito"
    fi
    echo ""

    # 6. Reiniciar aplicação
    biorempp_log_step "6/6 - Iniciando aplicação..."

    if [[ -f "$BIOREMPP_PROJECT_DIR/start.sh" ]]; then
        "$BIOREMPP_PROJECT_DIR/start.sh" || {
            biorempp_log_error "Falha ao iniciar aplicação"
            biorempp_log_info "Execute diagnóstico: ./setup_completo.sh --diagnose"
            exit 1
        }
    fi
    echo ""

    biorempp_log_success "Fix concluído!"
    echo ""
    biorempp_log_info "Verificar status: ./status.sh"
}

# ============================================================================
# MODO: Fix Nginx IPv6
# ============================================================================
run_fix_nginx() {
    biorempp_banner "Fix Nginx - IPv6 → IPv4"

    fix_nginx_ipv6
}

# ============================================================================
# MODO: Configurar SSL
# ============================================================================
run_ssl_setup() {
    biorempp_banner "Configurar SSL/HTTPS - $BIOREMPP_SERVER_DOMAIN"

    # 1. Verificar pré-requisitos
    biorempp_log_step "1/5 - Verificando pré-requisitos..."

    if ! biorempp_check_sudo; then
        exit 1
    fi

    # Verificar DNS
    biorempp_check_dns || biorempp_log_warn "DNS pode não estar configurado"

    # Verificar aplicação rodando
    biorempp_log_info "Verificando aplicação..."
    if ! biorempp_check_app_health 3; then
        biorempp_log_error "Aplicação não está rodando"
        biorempp_log_info "Execute: ./start.sh"
        exit 1
    fi
    biorempp_log_success "Aplicação está rodando"

    # Verificar Nginx
    if ! sudo systemctl is-active nginx >/dev/null 2>&1; then
        biorempp_log_error "Nginx não está rodando"
        biorempp_log_info "Execute: sudo systemctl start nginx"
        exit 1
    fi
    biorempp_log_success "Nginx está rodando"

    # Verificar HTTP funciona
    biorempp_log_info "Verificando HTTP..."
    if curl -sf "http://$BIOREMPP_SERVER_DOMAIN/health" >/dev/null 2>&1; then
        biorempp_log_success "HTTP funciona via domínio"
    else
        biorempp_log_warn "HTTP não responde via domínio"
        biorempp_log_warn "Certbot pode falhar"

        if ! biorempp_ask_yes_no "Continuar mesmo assim?" N; then
            exit 1
        fi
    fi

    echo ""

    # 2. Instalar Certbot
    biorempp_log_step "2/5 - Instalando Certbot..."

    if biorempp_check_command certbot; then
        biorempp_log_info "Certbot já instalado: $(certbot --version 2>&1 | head -1)"
    else
        biorempp_log_info "Instalando Certbot..."
        sudo apt-get update -qq
        sudo apt-get install -y certbot python3-certbot-nginx
        biorempp_log_success "Certbot instalado"
    fi

    echo ""

    # 3. Backup
    biorempp_log_step "3/5 - Fazendo backup do Nginx..."

    local backup_dir="/etc/nginx/backup_ssl_$(date +%Y%m%d_%H%M%S)"
    sudo mkdir -p "$backup_dir"
    sudo cp /etc/nginx/sites-available/biorempp "$backup_dir/biorempp" 2>/dev/null || true
    biorempp_log_info "Backup salvo: $backup_dir"

    echo ""

    # 4. Obter certificado SSL
    biorempp_log_step "4/5 - Obtendo certificado SSL..."

    biorempp_log_info "Executando Certbot..."
    biorempp_log_warn "Isso pode levar alguns minutos..."
    echo ""

    if sudo certbot --nginx \
        -d ${BIOREMPP_SSL_DOMAINS// / -d } \
        --email $BIOREMPP_SSL_EMAIL \
        --agree-tos \
        --redirect \
        --non-interactive; then

        echo ""
        biorempp_log_success "Certificado SSL obtido com sucesso!"
    else
        biorempp_log_error "Falha ao obter certificado SSL"
        echo ""
        biorempp_log_info "Possíveis causas:"
        echo "  1. DNS não está configurado ou não propagou"
        echo "  2. Firewall bloqueando porta 80/443"
        echo "  3. Limite de tentativas do Let's Encrypt (5 falhas/hora)"
        echo ""
        biorempp_log_info "Verificar logs:"
        echo "  sudo tail -50 /var/log/letsencrypt/letsencrypt.log"
        exit 1
    fi

    echo ""

    # 5. Verificar
    biorempp_log_step "5/5 - Verificando instalação..."

    sleep 3

    biorempp_log_info "Testando HTTPS..."
    if curl -sf "https://$BIOREMPP_SERVER_DOMAIN/health" >/dev/null 2>&1; then
        biorempp_log_success "HTTPS funciona!"
    else
        biorempp_log_warn "HTTPS ainda não responde (aguarde propagação)"
    fi

    biorempp_log_info "Testando redirect HTTP → HTTPS..."
    local redirect=$(curl -s -o /dev/null -w "%{http_code}" "http://$BIOREMPP_SERVER_DOMAIN" 2>/dev/null)
    if [[ "$redirect" == "301" ]] || [[ "$redirect" == "302" ]]; then
        biorempp_log_success "Redirect HTTP → HTTPS configurado"
    else
        biorempp_log_warn "Redirect pode não estar funcionando (código: $redirect)"
    fi

    echo ""

    # Resumo
    echo -e "${BIOREMPP_COLOR_GREEN}════════════════════════════════════════════════════════${BIOREMPP_COLOR_NC}"
    echo -e "${BIOREMPP_COLOR_GREEN}SSL Configurado!${BIOREMPP_COLOR_NC}"
    echo -e "${BIOREMPP_COLOR_GREEN}════════════════════════════════════════════════════════${BIOREMPP_COLOR_NC}"
    echo ""
    biorempp_log_info "Configurações aplicadas:"
    echo "  • Certificado SSL obtido do Let's Encrypt"
    echo "  • HTTPS habilitado em $BIOREMPP_SERVER_DOMAIN"
    echo "  • Redirect HTTP → HTTPS ativado"
    echo "  • Renovação automática configurada"
    echo ""
    biorempp_log_info "Acessar aplicação:"
    echo "  https://$BIOREMPP_SERVER_DOMAIN"
    echo ""
    biorempp_log_info "Verificar certificado:"
    echo "  sudo certbot certificates"
    echo ""
    biorempp_log_success "Seu site agora está seguro com HTTPS!"
    echo ""
}

# ============================================================================
# FUNÇÕES AUXILIARES
# ============================================================================

setup_nginx_production() {
    biorempp_check_sudo || return 1

    # Backup
    local backup_dir="$BIOREMPP_BACKUP_NGINX_DIR/backup_$(date +%Y%m%d_%H%M%S)"
    sudo mkdir -p "$backup_dir"

    if [[ -f /etc/nginx/nginx.conf ]]; then
        sudo cp /etc/nginx/nginx.conf "$backup_dir/"
        biorempp_log_success "Backup nginx.conf: $backup_dir"
    fi

    if [[ -f /etc/nginx/sites-available/biorempp ]]; then
        sudo cp /etc/nginx/sites-available/biorempp "$backup_dir/"
        biorempp_log_success "Backup biorempp.conf: $backup_dir"
    fi

    # Detectar e corrigir IPv6 automaticamente
    biorempp_log_info "Verificando configuração IPv6..."

    local temp_nginx="/tmp/nginx.conf.$$"
    cp "$BIOREMPP_PROJECT_DIR/nginx.conf.production" "$temp_nginx"

    if grep -q "server localhost:$BIOREMPP_APP_PORT" "$temp_nginx"; then
        biorempp_log_warn "Detectado 'localhost' - corrigindo para IPv4 explícito"
        sed -i "s/server localhost:$BIOREMPP_APP_PORT;/server $BIOREMPP_NGINX_UPSTREAM;/" "$temp_nginx"
    fi

    sudo cp "$temp_nginx" /etc/nginx/nginx.conf
    rm "$temp_nginx"

    sudo cp "$BIOREMPP_PROJECT_DIR/biorempp.conf.production" /etc/nginx/sites-available/biorempp
    biorempp_log_success "Configurações copiadas"

    # Criar link simbólico
    if [[ ! -L "/etc/nginx/sites-enabled/biorempp" ]]; then
        sudo ln -sf /etc/nginx/sites-available/biorempp /etc/nginx/sites-enabled/biorempp
        biorempp_log_success "Link simbólico criado"
    fi

    # Remover default
    if [[ -L /etc/nginx/sites-enabled/default ]]; then
        sudo rm -f /etc/nginx/sites-enabled/default
        biorempp_log_success "Site default removido"
    fi

    # Testar configuração
    biorempp_log_info "Testando configuração do Nginx..."
    if ! biorempp_nginx_test; then
        biorempp_log_error "Configuração inválida!"
        biorempp_log_warn "Restaurando backup..."
        sudo cp "$backup_dir/nginx.conf" /etc/nginx/nginx.conf 2>/dev/null || true
        return 1
    fi
    biorempp_log_success "Configuração válida"

    # Reload ou start
    biorempp_nginx_reload
    biorempp_log_success "Nginx configurado e rodando"

    return 0
}

stop_legacy_app() {
    # Procurar screen
    local screen_session=$(screen -ls 2>/dev/null | grep biorempp | awk '{print $1}' | cut -d. -f2 || echo "")

    if [[ -n "$screen_session" ]]; then
        biorempp_log_info "Screen detectado: $screen_session"
        screen -X -S "$screen_session" quit 2>/dev/null || true
        biorempp_log_success "Screen encerrado"
    else
        biorempp_log_info "Nenhum screen biorempp encontrado"
    fi

    # Procurar processos Python legados
    local python_pid=$(pgrep -f "python.*main.py" 2>/dev/null || echo "")

    if [[ -n "$python_pid" ]]; then
        biorempp_log_info "Processo Python detectado: PID $python_pid"
        kill -TERM "$python_pid" 2>/dev/null || true
        sleep 2
        biorempp_log_success "Processo Python encerrado"
    else
        biorempp_log_info "Nenhum processo main.py encontrado"
    fi
}

fix_nginx_ipv6() {
    biorempp_log_info "Detectando problema IPv6..."

    if grep -q "server localhost:$BIOREMPP_APP_PORT" /etc/nginx/nginx.conf 2>/dev/null; then
        biorempp_log_warn "Detectado 'localhost' (pode resolver IPv6)"

        local backup=$(biorempp_backup /etc/nginx/nginx.conf "nginx.conf")

        sudo sed -i "s/server localhost:$BIOREMPP_APP_PORT;/server $BIOREMPP_NGINX_UPSTREAM;/" /etc/nginx/nginx.conf

        if biorempp_nginx_test; then
            biorempp_nginx_reload
            biorempp_log_success "Nginx corrigido para IPv4!"
        else
            biorempp_restore "$backup" /etc/nginx/nginx.conf
            biorempp_log_error "Falha. Backup restaurado."
            return 1
        fi
    else
        biorempp_log_success "Nginx já está correto ($BIOREMPP_NGINX_UPSTREAM)"
    fi

    return 0
}

show_installation_summary() {
    echo -e "${BIOREMPP_COLOR_GREEN}════════════════════════════════════════════════════════${BIOREMPP_COLOR_NC}"
    echo -e "${BIOREMPP_COLOR_GREEN}Setup Concluído!${BIOREMPP_COLOR_NC}"
    echo -e "${BIOREMPP_COLOR_GREEN}════════════════════════════════════════════════════════${BIOREMPP_COLOR_NC}"
    echo ""

    biorempp_log_info "Verificando status..."
    echo ""

    if [[ -f "$BIOREMPP_PROJECT_DIR/status.sh" ]]; then
        "$BIOREMPP_PROJECT_DIR/status.sh"
    fi

    echo ""
    biorempp_log_info "Executando testes..."
    echo ""

    echo -n "  • Health check localhost:8080... "
    if curl -sf "http://localhost:8080/health" >/dev/null 2>&1; then
        echo -e "${BIOREMPP_COLOR_GREEN}✓${BIOREMPP_COLOR_NC}"
    else
        echo -e "${BIOREMPP_COLOR_RED}✗${BIOREMPP_COLOR_NC}"
    fi

    echo -n "  • Health check $BIOREMPP_SERVER_IP... "
    if curl -sf "http://$BIOREMPP_SERVER_IP/health" >/dev/null 2>&1; then
        echo -e "${BIOREMPP_COLOR_GREEN}✓${BIOREMPP_COLOR_NC}"
    else
        echo -e "${BIOREMPP_COLOR_RED}✗${BIOREMPP_COLOR_NC}"
    fi

    echo -n "  • Health check $BIOREMPP_SERVER_DOMAIN... "
    if curl -sf "http://$BIOREMPP_SERVER_DOMAIN/health" >/dev/null 2>&1; then
        echo -e "${BIOREMPP_COLOR_GREEN}✓${BIOREMPP_COLOR_NC}"
    else
        echo -e "${BIOREMPP_COLOR_YELLOW}⚠${BIOREMPP_COLOR_NC} (DNS pode não estar configurado)"
    fi

    echo ""
    echo -e "${BIOREMPP_COLOR_GREEN}════════════════════════════════════════════════════════${BIOREMPP_COLOR_NC}"
    echo -e "${BIOREMPP_COLOR_GREEN}Próximos Passos:${BIOREMPP_COLOR_NC}"
    echo -e "${BIOREMPP_COLOR_GREEN}════════════════════════════════════════════════════════${BIOREMPP_COLOR_NC}"
    echo ""
    echo "  1. Configurar SSL/HTTPS (recomendado):"
    echo "     ./setup_completo.sh --ssl"
    echo ""
    echo "  2. Monitorar aplicação:"
    echo "     ./status.sh      # Ver status"
    echo "     ./logs.sh        # Ver logs"
    echo ""
    echo "  3. Troubleshooting se necessário:"
    echo "     ./setup_completo.sh --diagnose   # Diagnosticar problemas"
    echo "     ./setup_completo.sh --fix        # Corrigir automaticamente"
    echo ""
    echo "  4. Acessar aplicação:"
    echo "     http://$BIOREMPP_SERVER_DOMAIN"
    echo "     http://$BIOREMPP_SERVER_IP"
    echo ""
    echo -e "${BIOREMPP_COLOR_GREEN}✓ Setup completo! BioRemPP v1.0 rodando${BIOREMPP_COLOR_NC}"
    echo ""
}

# ============================================================================
# Main - Dispatcher de Modos
# ============================================================================

case $MODE in
    install)
        run_installation
        ;;
    diagnose)
        run_diagnostic
        ;;
    fix)
        run_fix
        ;;
    fix-nginx)
        run_fix_nginx
        ;;
    ssl)
        run_ssl_setup
        ;;
esac

exit 0
