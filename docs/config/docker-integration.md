# Docker Integration

BioRemPP Web Service provides containerized deployment via Docker with profile-based orchestration. This page describes how configuration integrates with Docker—it is not a complete Docker deployment guide.

---

## Scope

**This page covers:**

- How environment variables map to Docker services
- Profile-based deployment (dev vs. prod)
- Multi-stage builds and targets
- Volume and network configuration

---

## Architecture

BioRemPP uses **Docker Compose profiles** to manage multiple deployment scenarios from a single configuration file.

| Profile | Services | Use Case |
|---------|----------|----------|
| `dev` | biorempp-dev | Local development with hot reload |
| `prod` | biorempp | Production application server |
| `nginx` | nginx | HTTP reverse proxy (TLS terminated upstream) |
| `cache` | redis | Caching layer |

---

## Multi-Stage Dockerfile

**File:** `.docker/Dockerfile`

The Dockerfile defines multiple build targets:

| Target | Base | Purpose | Exposed Port |
|--------|------|---------|--------------|
| `base` | python:3.11-slim | Common system dependencies | — |
| `builder` | base | Compile Python wheels | — |
| `development` | base | Dev environment with all extras | 8050 |
| `production` | base | Minimal production image | 8080 |

### Build Arguments

| Argument | Default | Purpose |
|----------|---------|---------|
| `PYTHON_VERSION` | `3.11` | Python runtime version |
| `APP_USER` | `biorempp` | Non-root container user |
| `UID` | `1000` | User ID |
| `GID` | `1000` | Group ID |

### Build Commands

```bash
# Development
docker build --target development -t biorempp:dev .

# Production
docker build --target production -t biorempp:prod .

# Custom Python version
docker build --target production --build-arg PYTHON_VERSION=3.12 -t biorempp:prod .
```

---

## Docker Compose Services

### Development Service (`biorempp-dev`)

**Profile:** `dev`

**Key features:**

- Hot reload enabled via volume mounts
- Source code mounted read-write
- Debug mode enabled
- Port 8050 exposed

**Environment variables:**
```yaml
BIOREMPP_ENV: development
BIOREMPP_HOST: 0.0.0.0
BIOREMPP_PORT: 8050
BIOREMPP_DEBUG: True
BIOREMPP_HOT_RELOAD: False  # Disabled in container for stability
BIOREMPP_LOG_LEVEL: INFO
```

**Volumes:**

- `./src:/app/src:rw` — Source code mount
- `./config:/app/config:rw` — Configuration mount
- `biorempp-dev-logs:/app/logs` — Persistent logs

**Start command:**
```bash
docker compose --profile dev up
```

---

### Production Service (`biorempp`)

**Profile:** `prod`

**Key features:**

- Multi-worker Gunicorn server
- No source code mounts (immutable)
- Resource limits enforced
- Internal service port `8080` (ingress via nginx)

**Environment variables:**
```yaml
BIOREMPP_ENV: production
BIOREMPP_HOST: 0.0.0.0
BIOREMPP_PORT: 8080
BIOREMPP_DEBUG: False
BIOREMPP_HOT_RELOAD: False
BIOREMPP_LOG_LEVEL: WARNING

# Gunicorn
BIOREMPP_WORKERS: 4
BIOREMPP_WORKER_CLASS: gevent
BIOREMPP_TIMEOUT: 300
```

**Resource limits:**
```yaml
deploy:
  resources:
    limits:
      cpus: '4.0'
      memory: 8G
    reservations:
      cpus: '2.0'
      memory: 4G
```

**Start command:**
```bash
docker compose --profile prod up -d
```

---

### Nginx Reverse Proxy

**Profile:** `nginx`

**Key features:**

- HTTP reverse proxy (TLS terminated by external institutional ingress)
- Static file serving
- WebSocket support for Dash
- Health check proxying

**Environment variables:**
```yaml
DOMAIN: biorempp.example.com
HTTP_PORT: 80
NGINX_CONFIG: nginx.prod.conf
```

**Volumes:**

- `.docker/nginx/${NGINX_CONFIG}:/etc/nginx/conf.d/default.conf:ro` — Configuration
- `./src/assets:/app/src/assets:ro` — Static files

**Start command:**
```bash
docker compose --profile prod --profile nginx up -d
```

---

### Redis Cache 

**Profile:** `cache`

**Key features:**
- LRU eviction policy
- 512MB memory limit
- Persistent storage

**Environment variables:**
```yaml
REDIS_HOST: redis
REDIS_PORT: 6379
REDIS_DB: 0
ENABLE_CACHE: True
```

**Start command:**
```bash
docker compose --profile prod --profile cache up -d
```

---

## Environment Variable Mapping

### Application to Container

| Application Variable | Docker Compose Variable | Default (Dev) | Default (Prod) |
|---------------------|------------------------|---------------|----------------|
| `BIOREMPP_ENV` | Hardcoded in service | `development` | `production` |
| `BIOREMPP_HOST` | `${BIOREMPP_HOST}` | `0.0.0.0` | `0.0.0.0` |
| `BIOREMPP_PORT` | `${BIOREMPP_PORT}` | `8050` | `8080` |
| `BIOREMPP_DEBUG` | Hardcoded in prod | `True` | `False` |
| `BIOREMPP_WORKERS` | `${BIOREMPP_WORKERS}` | — | `4` |
| `SECRET_KEY` | `${SECRET_KEY}` | — | Required |

### External Port Mapping

| Service | Internal Port | External Port (Variable) |
|---------|---------------|--------------------------|
| biorempp-dev | 8050 | `${DEV_PORT:-8050}` |
| biorempp | 8080 | Internal-only (`expose`) |
| nginx | 80 | `${HTTP_PORT:-80}` |
| redis | 6379 | `${REDIS_PORT:-6379}` |

---

## Entrypoint and Health Checks

### Entrypoint Script

**File:** `.docker/entrypoint.sh`

**Purpose:** Environment validation and safety checks before starting the application.

**Checks performed:**

- Required environment variables present
- Production safety (DEBUG=False, HOT_RELOAD=False)
- Insecure `SECRET_KEY` detection
- Directory setup (`logs/`, `data/`, `cache/`)

### Health Check Script

**File:** `.docker/healthcheck.sh`

**Purpose:** Container liveness probe.

**Checked endpoint:**
```bash
http://${BIOREMPP_HOST}:${BIOREMPP_PORT}/health
```

**Health check configuration:**
```yaml
healthcheck:
  interval: 30s
  timeout: 10s
  retries: 3
  start_period: 40s
```

---

## Volume Persistence

### Development Volumes

| Volume | Purpose | Persistence |
|--------|---------|-------------|
| `biorempp-dev-logs` | Application logs | Named volume |
| `biorempp-dev-cache` | Diskcache storage | Named volume |

### Production Volumes

| Volume | Purpose | Persistence |
|--------|---------|-------------|
| `biorempp-logs` | Application logs | Named volume |
| `biorempp-data` | User uploads, outputs | Named volume |
| `biorempp-cache` | Diskcache storage | Named volume |
| `nginx-logs` | Nginx logs | Named volume |
| `redis-data` | Redis persistence | Named volume |

---

## Configuration Files

Environment-specific configuration is provided via `.env` files:

```bash
# Development
docker compose --env-file .env/env.development --profile dev up

# Production
docker compose --env-file .env/env.production --profile prod --profile nginx up -d
```

**Required files:**

- `.env/env.development` — Development profile
- `.env/env.production` — Production profile
- `.env/env.local` — Local overrides (gitignored)

---

## Common Pitfalls

1. **Missing `.env` file:** Docker Compose uses `.env` by default; specify `--env-file` for custom locations

2. **Profile not activated:** Without `--profile`, services won't start; use `--profile dev` or `--profile prod`

3. **Port conflicts:** Ensure `DEV_PORT` and `PROD_PORT` don't conflict with host services

4. **Volume mount permissions:** Non-root container user requires proper file ownership; use `chown` if needed

5. **Hardcoded environment in compose:** `biorempp-dev` and `biorempp` have hardcoded `BIOREMPP_ENV`; changing it in `.env` has no effect

---

## See Also

- [Environment Variables](environment-variables.md) — Complete variable reference
- [YAML Configuration](yaml-configuration.md) — Declarative use case configuration
- [Gunicorn Configuration](gunicorn.md) — Production server settings
- [Logging Configuration](logging.md) — Container logging configuration
- [Health Endpoints](health-endpoints.md) — Health check configuration
- [Nginx Integration](nginx-integration.md) — Reverse proxy for container deployment
