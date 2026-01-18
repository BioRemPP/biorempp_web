# Environment Variables Reference

BioRemPP Web Service uses environment variables prefixed with `BIOREMPP_` to configure runtime behavior. Variables can be set via a `.env` file at the project root or passed directly to the process environment.

This page lists **stable, supported variables** organized by functional category.

---

## Scope

**This page covers:**

- Documented environment variables used by the web service
- Default behavior when variables are unset
- Recommended values for development and production profiles

---

## Key Settings

### Runtime Environment

| Variable | Purpose | Typical Values | Default |
|----------|---------|----------------|---------|
| `BIOREMPP_ENV` | Environment profile | `development`, `production` | `development` |
| `BIOREMPP_DEBUG` | Enable debug mode (detailed errors) | `True`, `False` | `True` in dev, forced `False` in prod |
| `BIOREMPP_HOT_RELOAD` | Enable hot reload (development only) | `True`, `False` | `True` in dev, forced `False` in prod |

> **Note:** When `BIOREMPP_ENV=production`, `DEBUG` and `HOT_RELOAD` are forced to `False` regardless of their configured values.

---

### Server Configuration

| Variable | Purpose | Typical Values | Default |
|----------|---------|----------------|---------|
| `BIOREMPP_HOST` | Server bind address | `127.0.0.1`, `0.0.0.0` | `127.0.0.1` (changed to `0.0.0.0` in production) |
| `BIOREMPP_PORT` | Server port | `8050`, `8080` | `8050` |
| `BIOREMPP_TIMEOUT` | Request timeout (seconds) | `60`, `300` | `60` |

---

### Gunicorn (Production WSGI)

These variables are relevant when running with Gunicorn in production mode.

| Variable | Purpose | Typical Values | Default |
|----------|---------|----------------|---------|
| `BIOREMPP_WORKERS` | Number of worker processes | `2–8` (formula: `2×CPU + 1`) | `4` |
| `BIOREMPP_WORKER_CLASS` | Worker type | `sync`, `gevent` | `sync` |
| `BIOREMPP_WORKER_CONNECTIONS` | Max connections per worker (gevent only) | `500–2000` | `1000` |
| `BIOREMPP_KEEPALIVE` | Keepalive timeout (seconds) | `2–10` | `5` |

For detailed Gunicorn configuration, see [Gunicorn Configuration](gunicorn.md).

---

### Logging

| Variable | Purpose | Typical Values | Default |
|----------|---------|----------------|---------|
| `BIOREMPP_LOG_LEVEL` | Logging verbosity | `DEBUG`, `INFO`, `WARNING`, `ERROR` | `DEBUG` in dev, `WARNING` in prod |
| `BIOREMPP_LOG_FILE` | Optional log file path | `/var/log/biorempp/app.log` | None (console only) |

For detailed logging configuration, see [Logging Configuration](logging.md).

---

### Upload Limits

| Variable | Purpose | Typical Values | Default |
|----------|---------|----------------|---------|
| `BIOREMPP_UPLOAD_MAX_SIZE_MB` | Maximum file size (MB) | `1–10` | `5` |
| `BIOREMPP_UPLOAD_SAMPLE_LIMIT` | Maximum samples per file | `50–200` | `100` |
| `BIOREMPP_UPLOAD_KO_LIMIT` | Maximum total KO entries | `100000–500000` | `500000` |
| `BIOREMPP_UPLOAD_ENCODING` | Expected file encoding | `utf-8` | `utf-8` |

---

### Parsing Limits

| Variable | Purpose | Typical Values | Default |
|----------|---------|----------------|---------|
| `BIOREMPP_PARSING_MAX_SAMPLES` | Maximum samples to process | `500–2000` | `1000` |
| `BIOREMPP_PARSING_MAX_KOS_PER_SAMPLE` | Maximum KOs per sample | `5000–20000` | `10000` |
| `BIOREMPP_PARSING_MAX_TOTAL_KOS` | Maximum total KOs to process | `50000–200000` | `100000` |

---

### Validation Patterns

| Variable | Purpose | Default Pattern |
|----------|---------|-----------------|
| `BIOREMPP_KO_PATTERN` | Regex for KO identifier validation | `^K\d{5}$` |
| `BIOREMPP_SAMPLE_NAME_PATTERN` | Regex for sample name validation | `^[a-zA-Z0-9_\-\.]+$` |

---

## Examples

### Minimal Development `.env`

```bash
# .env (development)
BIOREMPP_ENV=development
BIOREMPP_DEBUG=True
BIOREMPP_LOG_LEVEL=DEBUG
```

### Minimal Production `.env`

```bash
# .env (production)
BIOREMPP_ENV=production
BIOREMPP_PORT=8080
BIOREMPP_WORKERS=4
BIOREMPP_WORKER_CLASS=gevent
BIOREMPP_LOG_LEVEL=WARNING
BIOREMPP_TIMEOUT=300
```

---

## Common Pitfalls

1. **Forgetting `BIOREMPP_ENV=production`:** Without this, production overrides (disabling debug, changing host) are not applied.

2. **Using `127.0.0.1` in containers:** When running inside Docker, set `BIOREMPP_HOST=0.0.0.0` or rely on the automatic production override.

3. **Setting `DEBUG=True` in production:** This is overridden to `False` automatically, but explicit configuration avoids confusion.

4. **Timeout too short for large datasets:** For processing-heavy workflows, consider `BIOREMPP_TIMEOUT=300` or higher.

5. **Mismatched upload vs parsing limits:** If `UPLOAD_MAX_SIZE_MB` allows large files but `PARSING_MAX_TOTAL_KOS` is low, processing may fail silently on valid uploads.

---

## See Also

- [Logging Configuration](logging.md) — Logging profiles and verbosity
- [Gunicorn Configuration](gunicorn.md) — Production WSGI server settings
- [YAML Configuration](yaml-configuration.md) — Declarative use case configuration
- [Docker Integration](docker-integration.md) — Container-specific configuration
- [Nginx Integration](nginx-integration.md) — Reverse proxy configuration
- [Health Endpoints](health-endpoints.md) — Health check endpoints for monitoring
