# Configuration Guide

BioRemPP Web Service uses a layered configuration approach that separates runtime settings, analytical behavior, and deployment infrastructure. This guide provides an overview of configuration options and directs you to detailed documentation for each area.

---

## Configuration Architecture

BioRemPP configuration is organized into three layers:

```
┌─────────────────────────────────────────────────────────────┐
│                    Deployment Layer                         │
│         Docker, Nginx, Container Orchestration              │
├─────────────────────────────────────────────────────────────┤
│                    Runtime Layer                            │
│      Environment Variables, Gunicorn, Logging               │
├─────────────────────────────────────────────────────────────┤
│                   Application Layer                         │
│           YAML Use Cases, Plot Configs, Panels              │
└─────────────────────────────────────────────────────────────┘
```

| Layer | Purpose | Configuration Method |
|-------|---------|---------------------|
| **Deployment** | Infrastructure and container setup | Docker Compose, Nginx configs |
| **Runtime** | Server behavior and operational settings | Environment variables, `.env` files |
| **Application** | Analytical use cases and visualization | YAML configuration files |

---

## Quick Reference

### Runtime Configuration

| Page | Purpose | Key Settings |
|------|---------|--------------|
| [Environment Variables](environment-variables.md) | Runtime behavior control | `BIOREMPP_ENV`, `BIOREMPP_PORT`, `BIOREMPP_DEBUG` |
| [Gunicorn](gunicorn.md) | Production WSGI server | Workers, timeouts, worker class |
| [Logging](logging.md) | Log profiles and verbosity | Log levels, file rotation, handlers |
| [Health Endpoints](health-endpoints.md) | Monitoring and health checks | `/health`, `/ready` endpoints |

### Application Configuration

| Page | Purpose | Key Settings |
|------|---------|--------------|
| [YAML Configuration](yaml-configuration.md) | Declarative use case definition | Data sources, processing steps, visualization |

### Deployment Configuration

| Page | Purpose | Key Settings |
|------|---------|--------------|
| [Docker Integration](docker-integration.md) | Container deployment | Profiles, volumes, environment mapping |
| [Nginx Integration](nginx-integration.md) | Reverse proxy setup | SSL, upstream, WebSocket support |

---

## Configuration Precedence

When the same setting can be configured in multiple places, BioRemPP follows this precedence order (highest to lowest):

1. **Command-line arguments** (if applicable)
2. **Environment variables** (`BIOREMPP_*`)
3. **`.env` file** in project root
4. **Configuration files** (`config/*.yaml`)
5. **Default values** in code

Example: If `BIOREMPP_LOG_LEVEL=DEBUG` is set as an environment variable, it overrides the default `INFO` level defined in the logging configuration file.

---

## Environment Profiles

BioRemPP supports two primary profiles that affect multiple configuration defaults:

### Development Profile

```bash
BIOREMPP_ENV=development
```

| Setting | Default Value |
|---------|---------------|
| Debug mode | `True` |
| Hot reload | `True` |
| Log level | `DEBUG` |
| Host | `127.0.0.1` |
| Port | `8050` |

### Production Profile

```bash
BIOREMPP_ENV=production
```

| Setting | Default Value |
|---------|---------------|
| Debug mode | `False` (forced) |
| Hot reload | `False` (forced) |
| Log level | `WARNING` |
| Host | `0.0.0.0` |
| Port | `8080` |

---

## Common Configuration Tasks

### Starting Development Server

```bash
# Minimal development setup
export BIOREMPP_ENV=development
python -m src.biorempp_app
```

### Starting Production Server

```bash
# Minimal production setup
export BIOREMPP_ENV=production
export BIOREMPP_WORKERS=4
gunicorn wsgi:server -c gunicorn_config.py
```

### Running with Docker

```bash
# Development
docker compose --profile dev up

# Production with Nginx
docker compose --profile prod --profile nginx up -d
```

---

## Configuration Files Overview

### Project Structure

```
biorempp_web/
├── .env                          # Environment variables (gitignored)
├── .env.example                  # Template for .env
├── gunicorn_config.py            # Gunicorn WSGI configuration
├── config/
│   ├── logging_dev.yaml          # Development logging profile
│   └── logging_prod.yaml         # Production logging profile
├── src/infrastructure/plot_configs/
│   └── moduleX/
│       ├── uc_X_Y_config.yaml    # Use case plot configuration
│       └── uc_X_Y_panel.yaml     # Use case panel configuration
└── .docker/
    ├── Dockerfile                # Multi-stage build
    ├── docker-compose.yml        # Service orchestration
    ├── entrypoint.sh             # Container entry point
    ├── healthcheck.sh            # Health check script
    └── nginx/
        ├── nginx.dev.conf        # Development Nginx config
        └── nginx.prod.conf       # Production Nginx config
```

---

## Validation and Troubleshooting

### Validating Configuration

1. **Check environment variables:**
   ```bash
   env | grep BIOREMPP
   ```

2. **Verify logging configuration:**
   ```bash
   python -c "from src.infrastructure.config import get_settings; print(get_settings())"
   ```

3. **Test health endpoints:**
   ```bash
   curl http://localhost:8080/health
   curl http://localhost:8080/ready
   ```

### Common Issues

| Issue | Likely Cause | Solution |
|-------|--------------|----------|
| 502 Bad Gateway | Port mismatch between Nginx and Gunicorn | Verify `BIOREMPP_PORT` matches Nginx upstream |
| Slow startup | Too many workers for available CPU | Reduce `BIOREMPP_WORKERS` |
| Missing logs | Log directory doesn't exist | Create `logs/` directory with write permissions |
| Debug info in production | `BIOREMPP_ENV` not set to `production` | Set `BIOREMPP_ENV=production` |

---

## See Also

- [Quickstart Guide](../getting-started/quickstart.md) — Getting started with BioRemPP
- [Use Case YAML Methodology](../methods/use-case-yaml.md) — Complete YAML schema reference
- [Internal Validation](../validation/internal-validation.md) — Validation and quality control