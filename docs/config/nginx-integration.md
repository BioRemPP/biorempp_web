# Nginx Integration

BioRemPP Web Service is designed to run behind **Nginx as a reverse proxy**. This page describes how environment variables and configuration files integrate with Nginx—it is not a complete Nginx deployment guide.

---

## Scope

**This page covers:**

- How configuration variables map to Nginx
- Development vs. production Nginx setup
- Minimal required environment variables
- Integration points between BioRemPP and Nginx

---

## Architecture

```
[ Client ] → [ Institutional TLS/Ingress ] → [ Nginx :80 ] → [ Gunicorn :8080 ] → [ BioRemPP App ]
```

| Component | Responsibility |
|-----------|----------------|
| **Nginx** | Internal HTTP reverse proxy, static file serving, request buffering |
| **Gunicorn** | WSGI application server |
| **BioRemPP** | Application logic |

---

## Configuration Files

Nginx configuration is environment-specific:

| Environment | Config File | Purpose |
|-------------|-------------|---------|
| Development | `.docker/nginx/nginx.dev.conf` | HTTP-only reverse proxy |
| Production | `.docker/nginx/nginx.prod.conf` | HTTP reverse proxy (TLS terminated upstream) |

---

## Environment Variables Used by Nginx

### Required Variables

| Variable | Purpose | Typical Values |
|----------|---------|----------------|
| `DOMAIN` | Server name for virtual host matching | `biorempp.example.com` |
| `BIOREMPP_PORT` | Upstream application port | `8050` (dev), `8080` (prod) |

### Optional Variables

| Variable | Purpose | Default |
|----------|---------|---------|
| `HTTP_PORT` | Nginx HTTP listen port | `80` |

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

- **HTTP reverse proxy:** TLS is handled by institutional ingress
- **Upstream:** `biorempp:8080`
- **Static files:** Cached for 30 days
- **WebSocket support:** Enabled for Dash
- **Timeouts:** 300 seconds
- **Logging:** Warn level
- **Security headers:** CSP, X-Frame-Options
- **Gzip compression:** Enabled

### Key Directives

```nginx
server {
    listen 80;
    server_name ${DOMAIN};

    # Security headers
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
# .env (development)
BIOREMPP_HOST=0.0.0.0
BIOREMPP_PORT=8050
DOMAIN=localhost
```

### Production

```bash
# .env (production)
BIOREMPP_HOST=0.0.0.0
BIOREMPP_PORT=8080
DOMAIN=biorempp.example.com
```

---

## Common Pitfalls

1. **Mismatched ports:** Nginx upstream port must match `BIOREMPP_PORT`; mismatch causes 502 Bad Gateway

2. **Missing WebSocket headers:** Without `Upgrade` and `Connection` headers, Dash live updates fail

3. **Timeout too short:** If `proxy_read_timeout` < `BIOREMPP_TIMEOUT`, Nginx terminates requests prematurely

4. **Template variable not set:** `${DOMAIN}` must be provided for Nginx config generation

5. **Upload size mismatch:** If `client_max_body_size` < actual upload, Nginx returns 413 Request Entity Too Large before BioRemPP sees the request

---

## See Also

- [Gunicorn Configuration](gunicorn.md) — Upstream application server
- [Environment Variables](environment-variables.md) — Configuration reference
- [Logging Configuration](logging.md) — Nginx and application logging
- [Health Endpoints](health-endpoints.md) — Health check endpoints for load balancing
- [Docker Integration](docker-integration.md) — Container deployment with Nginx
