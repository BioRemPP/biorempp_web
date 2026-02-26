# Nginx Integration (Institutional Deployment)

BioRemPP runs behind an institutional ingress that terminates TLS.  
The in-project Nginx container is HTTP-only and proxies to Gunicorn.

## Topology

`Client -> Institutional Ingress (HTTPS/TLS) -> Nginx:80 -> BioRemPP:8080`


## Required Contract With Ingress

- `Host` is preserved for the final domain.
- `X-Forwarded-For` is forwarded with the client IP chain.
- `X-Forwarded-Proto` is forwarded as `https` at edge.
- `X-Forwarded-Host` is forwarded with public host.
- Base path routing is aligned with `BIOREMPP_URL_BASE_PATH` (`/` or `/biorempp/`).

## Proxy Trust Security

Production fail-fast is enforced in app settings:

- If `BIOREMPP_TRUST_PROXY_HEADERS=true`, then
  `BIOREMPP_TRUSTED_PROXY_CIDRS` must be explicitly set.
- Invalid CIDRs abort startup.
- Loopback-only CIDRs (`127.0.0.1/32`, `::1/128`) are rejected in this mode.

This prevents trusting spoofed forwarded headers when deployment is misconfigured.

## Upload Limit Contract

- Institutional ingress target: `100 MB` request body limit.
- Nginx internal limit can match institutional policy.
- Application parser/validation limit is controlled separately by
  `BIOREMPP_UPLOAD_MAX_SIZE_MB` (default `5 MB`).

If institutional policy requires 100 MB end-to-end processing, app limits must be
raised intentionally in configuration and capacity-tested.

## Metrics Exposure Policy

- `/metrics` must remain internal-only.
- Nginx location `/metrics` uses allowlist + `deny all`.
- External internet access to `/metrics` must stay blocked.

## Post-Deploy Validation

1. `curl -f http://<nginx-host>/health` returns `200`.
2. `curl -i http://<nginx-host>/metrics` returns `403` (or equivalent deny).
3. Internal call from app container to `/metrics` succeeds.
4. Request headers seen by app reflect trusted ingress behavior.

## See Also

- `docs/config/docker-integration.md`
- `docs/config/institutional_ingress_handoff.md`
