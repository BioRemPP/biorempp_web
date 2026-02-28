# Nginx Integration (Institutional Deployment)

BioRemPP is designed for institutional deployment with TLS termination at the edge.
The in-project Nginx container is HTTP-only and proxies to Gunicorn.

## Topology

`Client -> Institutional Ingress (HTTPS/TLS) -> Nginx:80 -> BioRemPP:8080`

## Required Ingress Contract

Ingress must preserve/forward:

- `Host` (final public host)
- `X-Forwarded-For` (client IP chain)
- `X-Forwarded-Proto` (`https` at edge)
- `X-Forwarded-Host` (public host)

Base path must match app configuration in `.env/env.production`:

- root deployment: `BIOREMPP_URL_BASE_PATH=/`
- subpath deployment: `BIOREMPP_URL_BASE_PATH=/biorempp/` or `/app/biorempp/`

## Proxy Trust Security

Production fail-fast rules:

- if `BIOREMPP_TRUST_PROXY_HEADERS=true`, `BIOREMPP_TRUSTED_PROXY_CIDRS` is mandatory;
- invalid CIDRs abort startup;
- loopback-only CIDRs are rejected in trusted mode.

## Upload Contract

- Current Nginx proxy body limit in runtime: `32 MB` (`client_max_body_size 32M`).
- Application parser limit is independent (`BIOREMPP_UPLOAD_MAX_SIZE_MB`, default `5 MB`).
- Effective user upload limit remains `5 MB` unless app parser limit is intentionally raised.

If institutional operation needs >5 MB processing, increase app limits intentionally and run capacity tests.

## Metrics Exposure Policy

- `/metrics` must remain internal-only.
- Nginx `/metrics` location must use allowlist + `deny all`.
- External internet access to `/metrics` must be blocked.

## Post-Deploy Validation

```bash
curl -f http://<nginx-host>/health
curl -i http://<nginx-host>/metrics
docker exec biorempp curl -fsS http://127.0.0.1:8080/metrics
```

Expected:

- `/health` returns `200`.
- external `/metrics` is denied (`403` or equivalent).
- internal metrics call succeeds.

## See Also

- [Docker Integration](docker-integration.md)
- [Institutional Ingress Handoff](institutional_ingress_handoff.md)
- [Environment Variables](environment-variables.md)
