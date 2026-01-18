# Logging Configuration

BioRemPP Web Service uses structured logging with profile-based configuration to support debugging in development and operational monitoring in production.

---

## Scope

**This page covers:**

- Logging profiles (development vs. production)
- Log levels and handlers
- Log file rotation and retention
- How to change log verbosity

---

## Configuration Profiles

Logging behavior is controlled by YAML configuration files that change based on the environment.

| Environment | Config File | Primary Formatter | Console Level | File Level |
|-------------|-------------|-------------------|---------------|------------|
| Development | `config/logging_dev.yaml` | Colored (human-readable) | `DEBUG` | `DEBUG` |
| Production | `config/logging_prod.yaml` | JSON (structured) | `INFO` | `INFO` |

The active profile is selected automatically based on `BIOREMPP_ENV`.

---

## Development Profile

**File:** `config/logging_dev.yaml`

**Purpose:** Maximize visibility for debugging and development.

### Characteristics

- **Console output:** Colored, human-readable format
- **Verbosity:** `DEBUG` level for most loggers
- **File output:** Detailed formatter with full context
- **Log rotation:** 5 backups, 10MB per file
- **Special loggers:**
  - `presentation.callbacks`: Debug callback execution
  - `watchdog`: Suppressed (file watcher noise)

### Handlers

| Handler | Level | Output | Format |
|---------|-------|--------|--------|
| `console` | `DEBUG` | stdout | Colored |
| `file` | `DEBUG` | `logs/app.log` | Detailed |
| `error_file` | `ERROR` | `logs/error.log` | Detailed |
| `security_file` | `WARNING` | `logs/security.log` | Detailed |
| `performance_file` | `WARNING` | `logs/performance.log` | Detailed |

### Example Output

```
2026-01-16 21:15:30 - biorempp_web - INFO - Application starting...
2026-01-16 21:15:31 - application.plot_services.singleton - DEBUG - PlotService instance created
```

---

## Production Profile

**File:** `config/logging_prod.yaml`

**Purpose:** Reduce noise and enable log aggregation.

### Characteristics

- **Console output:** Standard format, structured for parsing
- **Verbosity:** `INFO` level for application, `WARNING` for infrastructure
- **File output:** JSON format for machine parsing
- **Log rotation:** 10 backups, 50MB per file
- **Special loggers:**
  - `biorempp_web.security`: Separate file for audit
  - `wsgi`: WSGI server logs

### Handlers

| Handler | Level | Output | Format |
|---------|-------|--------|--------|
| `console` | `INFO` | stdout | Standard |
| `file` | `INFO` | `logs/app.log` | JSON |
| `error_file` | `ERROR` | `logs/error.log` | JSON |
| `security_file` | `INFO` | `logs/security.log` | JSON |
| `performance_file` | `WARNING` | `logs/performance.log` | JSON |

---

## Log Files

All log files are written to the `logs/` directory with automatic rotation.

| File | Purpose | When Written |
|------|---------|--------------|
| `app.log` | General application logs | All INFO+ events |
| `error.log` | Errors and exceptions | All ERROR+ events |
| `security.log` | Security-relevant events | Authentication, validation failures |
| `performance.log` | Performance metrics | Slow operations, cache stats |
| `gunicorn_access.log` | HTTP request logs | All requests (production only) |
| `gunicorn_error.log` | WSGI server errors | Gunicorn-level errors (production only) |

### Rotation Policy

| Profile | Max Size | Backup Count | Total Retention |
|---------|----------|--------------|-----------------|
| Development | 10 MB | 5 | 50 MB per file |
| Production | 50 MB | 10 | 500 MB per file |

Oldest files are deleted automatically when the limit is reached.

---

## Changing Log Level

### Via Environment Variable

Override the default log level:

```bash
export BIOREMPP_LOG_LEVEL=DEBUG
```

This affects the **root logger** level but does not change formatter or handler configuration.

### Via Configuration File

Edit the appropriate YAML file and modify logger levels:

```yaml
# config/logging_prod.yaml
loggers:
  biorempp_web:
    level: DEBUG  # Change from INFO to DEBUG
```

Then restart the application.

---

## Logger Hierarchy

BioRemPP uses hierarchical logger names for granular control:

```
root (INFO)
├── biorempp_web (INFO in prod, DEBUG in dev)
│   ├── domain (INFO)
│   │   ├── entities (INFO)
│   │   └── services (INFO)
│   ├── application (INFO)
│   ├── infrastructure (WARNING in prod, DEBUG in dev)
│   ├── security (INFO) → security.log
│   └── performance (WARNING) → performance.log
├── presentation.callbacks (INFO in prod, DEBUG in dev)
└── watchdog (WARNING, suppressed)
```

---

## Common Pitfalls

1. **DEBUG in production:** Excessive logging degrades performance and fills disk space; use `INFO` or `WARNING`

2. **Not rotating logs:** Without rotation, log files grow unbounded and fill disk

3. **Logging sensitive data:** Never log passwords, API keys, or user PII; use structured logging to redact

4. **Ignoring log levels:** Setting everything to `DEBUG` defeats the purpose of log levels; be selective

5. **Missing log directory:** Ensure `logs/` directory exists and has write permissions; the application creates it automatically if possible

---

## See Also

- [Environment Variables](environment-variables.md) — Runtime configuration including `BIOREMPP_LOG_LEVEL`
- [Gunicorn Configuration](gunicorn.md) — WSGI server logging
- [YAML Configuration](yaml-configuration.md) — Declarative use case configuration
- [Health Endpoints](health-endpoints.md) — Health check endpoints for monitoring
- [Docker Integration](docker-integration.md) — Container logging configuration
