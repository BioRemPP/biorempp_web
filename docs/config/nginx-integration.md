# Nginx Integration

<<<<<<< HEAD
BioRemPP Web Service is designed to run behind **Nginx as a reverse proxy**. This page describes how environment variables and configuration files integrate with Nginx—it is not a complete Nginx deployment guide.
=======
BioRemPP is designed for institutional deployment with TLS termination at the edge.
The in-project Nginx container is HTTP-only and proxies to Gunicorn.
>>>>>>> 852602f (docs: update and align technical documentation with runtime behavior for v1.0.6-beta)

---

## Scope

<<<<<<< HEAD
**This page covers:**

- How configuration variables map to Nginx
- Development vs. production Nginx setup
- Minimal required environment variables
- Integration points between BioRemPP and Nginx

---
=======
## Required Ingress Contract

Ingress must preserve/forward:

- `Host` (final public host)
- `X-Forwarded-For` (client IP chain)
- `X-Forwarded-Proto` (`https` at edge)
- `X-Forwarded-Host` (public host)

Base path must match app configuration in `.env/env.production`:

- root deployment: `BIOREMPP_URL_BASE_PATH=/`
- subpath deployment: `BIOREMPP_URL_BASE_PATH=/biorempp/` or `/app/biorempp/`
>>>>>>> 852602f (docs: update and align technical documentation with runtime behavior for v1.0.6-beta)

## Architecture

<<<<<<< HEAD
```
[ Client ] → [ Nginx :80/:443 ] → [ Gunicorn :8080 ] → [ BioRemPP App ]
```

| Component | Responsibility |
|-----------|----------------|
| **Nginx** | TLS termination, static file serving, request buffering, load balancing (if multi-instance) |
| **Gunicorn** | WSGI application server |
| **BioRemPP** | Application logic |

---

## Configuration Files

Nginx configuration is environment-specific:

| Environment | Config File | Purpose |
|-------------|-------------|---------|
| Development | `.docker/nginx/nginx.dev.conf` | HTTP-only reverse proxy |
| Production | `.docker/nginx/nginx.prod.conf` | HTTPS with Let's Encrypt SSL |
=======
Production fail-fast rules:

- if `BIOREMPP_TRUST_PROXY_HEADERS=true`, `BIOREMPP_TRUSTED_PROXY_CIDRS` is mandatory;
- invalid CIDRs abort startup;
- loopback-only CIDRs are rejected in trusted mode.

## Upload Contract

- Current Nginx proxy body limit in runtime: `32 MB` (`client_max_body_size 32M`).
- Application parser limit is independent (`BIOREMPP_UPLOAD_MAX_SIZE_MB`, default `5 MB`).
- Effective user upload limit remains `5 MB` unless app parser limit is intentionally raised.

If institutional operation needs >5 MB processing, increase app limits intentionally and run capacity tests.
>>>>>>> 852602f (docs: update and align technical documentation with runtime behavior for v1.0.6-beta)

---

<<<<<<< HEAD
## Environment Variables Used by Nginx
=======
- `/metrics` must remain internal-only.
- Nginx `/metrics` location must use allowlist + `deny all`.
- External internet access to `/metrics` must be blocked.
>>>>>>> 852602f (docs: update and align technical documentation with runtime behavior for v1.0.6-beta)

### Required Variables

<<<<<<< HEAD
| Variable | Purpose | Typical Values |
|----------|---------|----------------|
| `DOMAIN` | Server name for SSL certificates | `biorempp.example.com` |
| `BIOREMPP_PORT` | Upstream application port | `8050` (dev), `8080` (prod) |

### Optional Variables

| Variable | Purpose | Default |
|----------|---------|---------|
| `HTTP_PORT` | Nginx HTTP listen port | `80` |
| `HTTPS_PORT` | Nginx HTTPS listen port | `443` |

---

## Development Configuration

**File:** `.docker/nginx/nginx.dev.conf`

### Characteristics

- **No SSL:** HTTP-only on port 80
- **Upstream:** `biorempp:8050`
- **Static files:** Served with `expires -1` (no cache)
- **WebSocket support:** Enabled for Dash hot reload
- **Timeouts:** 60 seconds
- **Logging:** Debug level

### Key Directives

```nginx
upstream biorempp_app {
    server biorempp:8050 fail_timeout=10s max_fails=3;
}

server {
    listen 80;
    server_name localhost;

    client_max_body_size 100M;

    # WebSocket for Dash hot reload
    location /_dash-update-component {
        proxy_pass http://biorempp_app;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }

    location / {
        proxy_pass http://biorempp_app;
        proxy_buffering off;  # Immediate feedback in dev
    }
}
```

---

## Production Configuration

**File:** `.docker/nginx/nginx.prod.conf`

### Characteristics

- **HTTPS only:** TLS 1.2/1.3 with Let's Encrypt certificates
- **HTTP → HTTPS redirect:** Port 80 redirects to 443
- **Upstream:** `biorempp:8080`
- **Static files:** Cached for 30 days
- **WebSocket support:** Enabled for Dash
- **Timeouts:** 300 seconds
- **Logging:** Warn level
- **Security headers:** HSTS, CSP, X-Frame-Options
- **Gzip compression:** Enabled

### Key Directives

```nginx
# HTTP → HTTPS redirect
server {
    listen 80;
    server_name ${DOMAIN};

    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }

    location / {
        return 301 https://$server_name$request_uri;
    }
}

# HTTPS server
server {
    listen 443 ssl http2;
    server_name ${DOMAIN};

    ssl_certificate /etc/letsencrypt/live/${DOMAIN}/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/${DOMAIN}/privkey.pem;

    # Security headers
    add_header Strict-Transport-Security "max-age=63072000" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;

    # Gzip compression
    gzip on;
    gzip_types text/css application/javascript application/json;

    location / {
        proxy_pass http://biorempp_app;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

---

## Minimal Environment Variables for Nginx

### Development

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

- [Gunicorn Configuration](gunicorn.md) — Upstream application server
- [Environment Variables](environment-variables.md) — Configuration reference
- [Logging Configuration](logging.md) — Nginx and application logging
- [Health Endpoints](health-endpoints.md) — Health check endpoints for load balancing
- [Docker Integration](docker-integration.md) — Container deployment with Nginx
