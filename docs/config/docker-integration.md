# Docker Integration (Prod + Institutional Ingress)

This project uses Docker Compose profiles for development and production.

## Profiles

- `dev`: local development app (`biorempp-dev`)
- `prod`: production app (`biorempp` + `biorempp-nginx`)
- `cache`: Redis (`biorempp-redis`)
- `observability`: Prometheus + Grafana

## Environment Files

Use only the official tracked templates:

- `.env/env.example` for onboarding and defaults
- `.env/env.production` for production configuration

## Production Runtime Model

- App container (`biorempp`) is internal-only (`expose: 8080`).
- Nginx is the external HTTP entrypoint in compose.
- TLS is terminated outside this stack (institutional ingress).

## Baseline and Optional Stack

### Baseline (institutional validation)

```bash
docker compose --env-file .env/env.production --profile prod up -d --build
docker compose --env-file .env/env.production --profile prod ps
```

### Add cache (Redis)

```bash
docker compose --env-file .env/env.production --profile prod --profile cache up -d --build
docker compose --env-file .env/env.production --profile prod --profile cache ps
```

### Add observability

```bash
docker compose --env-file .env/env.production --profile prod --profile cache --profile observability up -d --build
docker compose --env-file .env/env.production --profile prod --profile cache --profile observability ps
```

## Security-Critical Environment Variables

- `SECRET_KEY` (required, secure)
- `REDIS_PASSWORD` / `BIOREMPP_RESUME_REDIS_PASSWORD` (required when Redis is used)
- `BIOREMPP_TRUST_PROXY_HEADERS`
- `BIOREMPP_TRUSTED_PROXY_CIDRS`
- `BIOREMPP_URL_BASE_PATH`

## Production Fail-Fast Rules

Startup aborts when:

- required secrets are empty/insecure placeholders;
- `BIOREMPP_TRUST_PROXY_HEADERS=true` and trusted CIDRs are missing/invalid/loopback-only;
- Redis-backed resume/rate-limit is enabled without secure Redis credentials.

This behavior is implemented in `config/settings.py` and `.docker/entrypoint.sh`.

## Operational Validation Commands

```bash
curl -f http://localhost/health
curl -i http://localhost/metrics
docker exec biorempp curl -fsS http://127.0.0.1:8080/metrics
```

Expected:

- all active services healthy;
- `/health` returns 200;
- external `/metrics` blocked;
- internal `/metrics` available when observability is enabled.

## HTTP Error Troubleshooting (400/500)

Use the following sequence to investigate browser/API errors with correlation IDs:

```bash
docker compose --env-file .env/env.production --profile prod --profile cache --profile observability logs -f biorempp
```

Trigger test requests:

```bash
curl -i -H "Accept: text/html" http://localhost/error/400
curl -i -H "Accept: application/json" http://localhost/error/500
```

Validate in logs:

- structured fields: `status_code`, `path`, `method`, `request_id`, `trace_id`;
- correlate repeated failures by `request_id`/`trace_id` instead of payload/IP data.

Useful PromQL queries:

```promql
status_class:biorempp_http_errors:rate5m
status_code:biorempp_http_errors:rate5m
topk(10, endpoint:biorempp_http_error_ratio:rate5m)
job:biorempp_http_5xx_ratio:rate5m
job:biorempp_http_4xx_ratio:rate5m
```

## Notes

- No Certbot/Let's Encrypt automation exists in this repository by design.
- Final certificate lifecycle is managed by institutional infrastructure.

## See Also

- [Environment Variables](environment-variables.md) - Complete variable reference
- [YAML Configuration](yaml-configuration.md) - Declarative use case configuration
- [Gunicorn Configuration](gunicorn.md) - Production server settings
- [Logging Configuration](logging.md) - Container logging configuration
- [Health Endpoints](health-endpoints.md) - Health check configuration
- [Nginx Integration](nginx-integration.md) - Reverse proxy for container deployment
- [Institutional Ingress Handoff](institutional_ingress_handoff.md) - TI handoff checklist
