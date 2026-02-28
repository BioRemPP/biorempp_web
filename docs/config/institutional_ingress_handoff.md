# Institutional Ingress Handoff Checklist

This checklist is for the institutional IT team during production onboarding.

## 1) Parameters TI Must Provide

- Final public domain (example: `biorempp.institution.tld`)
- Trusted ingress/proxy CIDRs (source IPs seen by app/Nginx)
- Final base path (`/`, `/biorempp/`, or `/app/biorempp/`)
- Header behavior at ingress:
  - `X-Forwarded-For`
  - `X-Forwarded-Proto`
  - `X-Forwarded-Host`
- Upload policy aligned with runtime (`32 MB` at proxy, `5 MB` at app parser)
- Metrics exposure policy (`/metrics` internal-only)

## 2) Values That Must Be Updated Before Go-Live

Use `.env/env.production` (seeded from `.env/env.example`) or an external secret manager:

- `DOMAIN`
- `BIOREMPP_TRUST_PROXY_HEADERS=true`
- `BIOREMPP_TRUSTED_PROXY_CIDRS=<institution CIDRs>`
- `BIOREMPP_URL_BASE_PATH=<final base path>`
- `SECRET_KEY=<secure value>`
- `REDIS_PASSWORD=<secure value>`
- `BIOREMPP_RESUME_REDIS_PASSWORD=<secure value>`
- `GRAFANA_ADMIN_PASSWORD=<secure value>`

## 3) Header Contract (Mandatory)

Ingress/proxy must forward:

- `X-Forwarded-For`: client chain
- `X-Forwarded-Proto`: `https` at edge
- `X-Forwarded-Host`: public host

Application trust is conditional:

- trust only enabled when `BIOREMPP_TRUST_PROXY_HEADERS=true`;
- startup aborts in production if trusted CIDRs are missing/invalid/loopback-only.

## 4) Post-Deployment Validation Commands

### Baseline

```bash
docker compose --env-file .env/env.production --profile prod up -d --build
docker compose --env-file .env/env.production --profile prod ps
curl -f http://localhost/health
curl -i http://localhost/metrics
```

### With cache + observability

```bash
docker compose --env-file .env/env.production --profile prod --profile cache --profile observability up -d --build
docker compose --env-file .env/env.production --profile prod --profile cache --profile observability ps
docker exec biorempp curl -fsS http://127.0.0.1:8080/metrics
curl -s http://127.0.0.1:9090/api/v1/targets
curl -s http://127.0.0.1:3300/api/health
```

## 5) Ready-for-Go-Live Criteria

- All containers healthy, no restart loop.
- `/health` available through ingress/Nginx path.
- `/metrics` blocked externally and reachable internally.
- `biorempp-app` target is `UP` in Prometheus when observability profile is active.
- Proxy trust fail-fast passes with institutional CIDRs.
- Navigation and callbacks work with final `BIOREMPP_URL_BASE_PATH`.

## 6) Out of Scope in This Repository

- Certificate issuance/renewal automation (Certbot/Let's Encrypt).
- Institutional WAF/firewall policy definition.
- External DNS lifecycle.
