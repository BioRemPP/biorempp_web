# Docker Integration (Prod + Institutional Ingress)

This project uses Docker Compose profiles for development and production.

## Profiles

- `dev`: local development app (`biorempp-dev`)
- `prod`: production app (`biorempp`)
- `nginx`: internal reverse proxy (`biorempp-nginx`)
- `cache`: Redis (`biorempp-redis`)
- `observability`: Prometheus + Grafana

## Production Runtime Model

- App container (`biorempp`) is internal-only (`expose: 8080`).
- Nginx is the external HTTP entrypoint in compose.
- TLS is terminated outside this stack (institutional ingress).

## Security-Critical Environment Variables

- `SECRET_KEY` (required, secure)
- `REDIS_PASSWORD` / `BIOREMPP_RESUME_REDIS_PASSWORD` (required when Redis is used)
- `BIOREMPP_TRUST_PROXY_HEADERS`
- `BIOREMPP_TRUSTED_PROXY_CIDRS`
- `BIOREMPP_URL_BASE_PATH`

## Production Fail-Fast Rules

Startup aborts when:

- required secrets are empty/insecure placeholders;
- `BIOREMPP_TRUST_PROXY_HEADERS=true` and trusted CIDRs are missing/invalid/loopback-only.

This behavior is implemented in `config/settings.py`.



## Operational Validation Commands

```bash
docker compose --env-file .env/env.production.local --profile prod --profile cache --profile observability --profile nginx up -d
docker compose --env-file .env/env.production.local ps
curl -f http://localhost/health
curl -i http://localhost/metrics
docker exec biorempp curl -fsS http://127.0.0.1:8080/metrics
```

Expected:

- all services healthy;
- `/health` returns 200;
- external `/metrics` blocked;
- internal `/metrics` available.

## Notes

- No Certbot/Let's Encrypt automation exists in this repository by design.
- Final certificate lifecycle is managed by institutional infrastructure.

## See Also

- [Environment Variables](environment-variables.md) — Complete variable reference
- [YAML Configuration](yaml-configuration.md) — Declarative use case configuration
- [Gunicorn Configuration](gunicorn.md) — Production server settings
- [Logging Configuration](logging.md) — Container logging configuration
- [Health Endpoints](health-endpoints.md) — Health check configuration
- [Nginx Integration](nginx-integration.md) — Reverse proxy for container deployment
