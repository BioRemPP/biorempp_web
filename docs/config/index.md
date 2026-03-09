# Configuration Guide

BioRemPP uses a layered configuration model covering runtime, deployment, and observability.

---

## Configuration Layers

| Layer | Purpose | Main Artifacts |
|---|---|---|
| Deployment | Container topology and proxy integration | `docker-compose.yml`, `.docker/nginx/*` |
| Runtime | Server behavior, security, resume, limits | `config/settings.py`, `.env/env.production` |
| Observability | Metrics, alerts, dashboards | `src/shared/metrics/*`, `observability/*` |

---

## Official Environment Files

Use only tracked templates as source of truth:

- `.env/env.example` (starting template)
- `.env/env.production` (production baseline)

---

## Quick Reference

| Topic | Page |
|---|---|
| Environment variables | [Environment Variables](environment-variables.md) |
| Gunicorn runtime | [Gunicorn](gunicorn.md) |
| Health probes | [Health Endpoints](health-endpoints.md) |
| Logging | [Logging](logging.md) |
| Docker profiles | [Docker Integration](docker-integration.md) |
| Institutional ingress contract | [Institutional Ingress Handoff](institutional_ingress_handoff.md) |
| Nginx reverse proxy | [Nginx Integration](nginx-integration.md) |

---

## Runtime Profiles

### Development

```bash
BIOREMPP_ENV=development
```

### Production

```bash
BIOREMPP_ENV=production
BIOREMPP_DEBUG=False
BIOREMPP_HOT_RELOAD=False
```

---

## Compose Execution Model

### Baseline (app + nginx)

```bash
docker compose --env-file .env/env.production --profile prod up -d --build
```

### Add Redis cache/resume backend

```bash
docker compose --env-file .env/env.production --profile prod --profile cache up -d --build
```

### Add observability stack

```bash
docker compose --env-file .env/env.production --profile prod --profile cache --profile observability up -d --build
```

---

## Project Configuration Structure

```text
biorempp_web/
|-- docker-compose.yml
|-- gunicorn_config.py
|-- config/
|   |-- settings.py
|   |-- logging_dev.yaml
|   `-- logging_prod.yaml
|-- .env/
|   |-- env.example
|   `-- env.production
|-- .docker/
|   |-- Dockerfile
|   |-- entrypoint.sh
|   |-- healthcheck.sh
|   `-- nginx/
|       |-- nginx.prod.conf
|       `-- nginx.prod.tls-mock.conf
`-- observability/
    |-- prometheus/
    `-- grafana/
```

---

## Validation Checklist

1. Render effective compose config:

```bash
docker compose --env-file .env/env.production --profile prod config
```

2. Validate app and proxy health:

```bash
curl -f http://localhost/health
curl -i http://localhost/metrics
```

3. Validate internal metrics path:

```bash
docker exec biorempp curl -fsS http://127.0.0.1:8080/metrics
```

---

## Common Issues

| Issue | Likely Cause | Action |
|---|---|---|
| 404 on root route | `BIOREMPP_URL_BASE_PATH` mismatch with ingress rewrite | Align base path in env + ingress |
| App startup fail-fast | insecure/missing required secrets | set secure values in `.env/env.production` |
| Wrong client IP in logs/rate-limit | trusted proxy CIDRs missing/incorrect | fix `BIOREMPP_TRUSTED_PROXY_CIDRS` |
| `/metrics` exposed publicly | proxy restrictions not applied | enforce allowlist + `deny all` in Nginx |

---

## See Also

- [Quickstart](../getting-started/quickstart.md)
- [Methods Overview](../methods/methods-overview.md)
- [Validation](../validation/index.md)
