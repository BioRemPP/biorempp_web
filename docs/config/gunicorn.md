# Gunicorn Configuration

Gunicorn is the recommended production WSGI server for BioRemPP Web Service. It provides a multi-worker process model with support for async I/O through optional worker classes.

---

## Scope

**This page covers:**

- Gunicorn configuration file structure
- Worker settings and selection guidance
- Environment variable mapping
- Recommended values for production

---

## Configuration File

Gunicorn reads configuration from `gunicorn_config.py` located at the project root. The server is invoked as:

```bash
gunicorn wsgi:server -c gunicorn_config.py
```

### Entry Point

The WSGI entry point is defined in `wsgi.py`, which:

- Loads application settings
- Configures logging
- Creates the Dash application instance
- Exposes the Flask `server` object for Gunicorn

---

## Key Settings

### Workers

| Variable | Purpose | Typical Values | Default |
|----------|---------|----------------|---------|
| `BIOREMPP_WORKERS` | Number of worker processes | `2–8` | `4` |
| `BIOREMPP_WORKER_CLASS` | Worker type | `sync`, `gevent` | `sync` |
| `BIOREMPP_WORKER_CONNECTIONS` | Max connections per worker (gevent/eventlet only) | `500–2000` | `1000` |

**Worker count guidance:**
- Formula: `(2 × CPU cores) + 1`
- 2 CPU cores → 5 workers
- 4 CPU cores → 9 workers (cap at 4–8 for most deployments)

**Worker class selection:**

| Class | Use When | Characteristics |
|-------|----------|-----------------|
| `sync` | CPU-bound tasks, simple workloads | Blocking I/O, lower memory |
| `gevent` | I/O-bound tasks, many concurrent requests | Async I/O, higher concurrency |
| `eventlet` | Similar to gevent | Alternative async I/O library |

For BioRemPP, `sync` workers are typically sufficient unless serving many simultaneous long-running requests.

### Timeouts

| Variable | Purpose | Typical Values | Default |
|----------|---------|----------------|---------|
| `BIOREMPP_TIMEOUT` | Max request duration (seconds) | `60–300` | `60` |
| `BIOREMPP_KEEPALIVE` | Keepalive timeout (seconds) | `2–10` | `5` |

Set `TIMEOUT` higher for processing-heavy workflows (e.g., large dataset uploads).

### Worker Lifecycle

| Setting | Value | Purpose |
|---------|-------|---------|
| `max_requests` | `1000` | Restart worker after N requests |
| `max_requests_jitter` | `50` | Randomize restart to avoid synchronized restarts |

Periodic worker restarts mitigate memory leaks from long-running processes.

### Logging

Gunicorn logs are written to:

- **Access log:** `logs/gunicorn_access.log` (production) or stdout (development)
- **Error log:** `logs/gunicorn_error.log` (production) or stderr (development)

Log level is controlled by `BIOREMPP_LOG_LEVEL`.

---

## Configuration Example

### Minimal Production Configuration

```bash
# .env (production)
BIOREMPP_ENV=production
BIOREMPP_WORKERS=4
BIOREMPP_WORKER_CLASS=sync
BIOREMPP_TIMEOUT=300
BIOREMPP_KEEPALIVE=5
```

### Gevent Workers (High Concurrency)

```bash
# .env (high-concurrency production)
BIOREMPP_ENV=production
BIOREMPP_WORKERS=4
BIOREMPP_WORKER_CLASS=gevent
BIOREMPP_WORKER_CONNECTIONS=1000
BIOREMPP_TIMEOUT=300
```

---

## Running Gunicorn

### Direct Invocation

```bash
gunicorn wsgi:server -c gunicorn_config.py
```

### With Environment Variables

```bash
BIOREMPP_ENV=production \
BIOREMPP_WORKERS=4 \
BIOREMPP_TIMEOUT=300 \
gunicorn wsgi:server -c gunicorn_config.py
```

### Inside Docker

The provided entrypoint script (`entrypoint.sh`) handles environment validation before starting Gunicorn:

```bash
docker run -p 8080:8080 \
  -e BIOREMPP_ENV=production \
  -e BIOREMPP_WORKERS=4 \
  biorempp:latest
```

---

## Server Hooks

The configuration file defines lifecycle hooks for monitoring and debugging:

| Hook | When Called | Purpose |
|------|-------------|---------|
| `on_starting` | Before master process initializes | Log startup configuration |
| `when_ready` | After server starts | Confirm readiness |
| `post_fork` | After worker is forked | Log worker PID |
| `worker_abort` | Worker receives SIGABRT | Log abnormal termination |
| `on_exit` | Before shutdown | Log graceful exit |

---

## Common Pitfalls

1. **Too many workers for available CPU:** Over-provisioning workers degrades performance due to context switching

2. **Timeout too short:** Processing large datasets requires `TIMEOUT=300` or higher; default `60s` may cause premature worker termination

3. **Using gevent without gevent library:** Setting `WORKER_CLASS=gevent` requires `gevent` to be installed

4. **Not setting `preload_app=True`:** Without preload, each worker re-initializes the application, potentially causing duplicate callback registration in Dash apps

5. **Forgetting to expose port in containers:** Ensure `BIOREMPP_HOST=0.0.0.0` when running in Docker

---

## See Also

- [Environment Variables](environment-variables.md) — Full variable reference
- [YAML Configuration](yaml-configuration.md) — Declarative use case configuration
- [Logging Configuration](logging.md) — Log profiles and verbosity
- [Health Endpoints](health-endpoints.md) — Health check endpoints for monitoring
- [Nginx Integration](nginx-integration.md) — Reverse proxy configuration
- [Docker Integration](docker-integration.md) — Container deployment
