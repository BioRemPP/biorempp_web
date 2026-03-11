# Environment Variables Reference

BioRemPP uses environment variables to configure runtime behavior, security, resume flow, and observability.

Use the tracked files below as reference:

- `.env/env.example` (template)
- `.env/env.production` (production baseline)
- `.env/env.production.biome` (institutional production baseline)

---

## Runtime Core

| Variable | Purpose | Default |
|---|---|---|
| `BIOREMPP_ENV` | Environment profile (`development` or `production`) | `development` |
| `BIOREMPP_DEBUG` | Dash/Flask debug mode | `True` in dev, forced `False` in prod |
| `BIOREMPP_HOT_RELOAD` | Dash hot reload | `True` in dev, forced `False` in prod |
| `BIOREMPP_HOST` | Bind host | `127.0.0.1` (forced `0.0.0.0` in prod) |
| `BIOREMPP_PORT` | Bind port | `8050` |
| `BIOREMPP_URL_BASE_PATH` | Base path prefix (`/`, `/biorempp/`, `/app/biorempp/`) | `/` |

---

## Gunicorn

| Variable | Purpose | Default |
|---|---|---|
| `BIOREMPP_WORKERS` | Worker count | `4` |
| `BIOREMPP_WORKER_CLASS` | Worker class (`sync`, `gevent`, `eventlet`) | `sync` |
| `BIOREMPP_WORKER_CONNECTIONS` | Connections per worker (async classes) | `1000` |
| `BIOREMPP_TIMEOUT` | Request timeout (seconds) | `60` |
| `BIOREMPP_KEEPALIVE` | Keepalive timeout (seconds) | `5` |
| `BIOREMPP_MAX_REQUESTS` | Worker recycle threshold | `1000` |
| `BIOREMPP_MAX_REQUESTS_JITTER` | Worker recycle jitter | `100` |

---

## Upload and Parsing Limits

| Variable | Purpose | Default |
|---|---|---|
| `BIOREMPP_UPLOAD_MAX_SIZE_MB` | Max upload size (MB) | `5` |
| `BIOREMPP_UPLOAD_SAMPLE_LIMIT` | Max samples in uploaded file | `100` |
| `BIOREMPP_UPLOAD_KO_LIMIT` | Max KO identifiers in uploaded file | `500000` |
| `BIOREMPP_UPLOAD_ENCODING` | Expected file encoding | `utf-8` |
| `BIOREMPP_PARSING_MAX_SAMPLES` | Max samples during parsing | `1000` |
| `BIOREMPP_PARSING_MAX_KOS_PER_SAMPLE` | Max KOs per sample | `10000` |
| `BIOREMPP_PARSING_MAX_TOTAL_KOS` | Max KOs during parsing | `100000` |

---

## Resume by Job ID

| Variable | Purpose | Default |
|---|---|---|
| `BIOREMPP_RESUME_BACKEND` | Resume storage backend (`diskcache`, `redis`) | `diskcache` |
| `BIOREMPP_RESUME_SECURITY_MODE` | Error exposure mode (`normal`, `strict`) | `normal` |
| `BIOREMPP_RESUME_TTL_SECONDS` | Resume TTL in seconds | `14400` (4h) |
| `BIOREMPP_RESUME_CACHE_SIZE_MB` | Resume cache max size | `512` |
| `BIOREMPP_RESUME_MAX_PAYLOAD_MB` | Max payload size per job | `64` |
| `BIOREMPP_RESUME_REDIS_HOST` | Resume Redis host | `redis` |
| `BIOREMPP_RESUME_REDIS_PORT` | Resume Redis port | `6379` |
| `BIOREMPP_RESUME_REDIS_DB` | Resume Redis DB index | `0` |
| `BIOREMPP_RESUME_REDIS_PASSWORD` | Resume Redis password | inherits `REDIS_PASSWORD` if unset |
| `BIOREMPP_RESUME_REDIS_KEY_PREFIX` | Resume key prefix in Redis | `biorempp:resume:` |
| `BIOREMPP_RESUME_REDIS_COMPRESSION_LEVEL` | Redis payload compression level (1..9) | `6` |
| `BIOREMPP_RESUME_REDIS_SOCKET_TIMEOUT_SECONDS` | Redis socket timeout | `3` |
| `BIOREMPP_RESUME_REDIS_HEALTHCHECK` | Startup Redis health gate for resume | `false` |
| `BIOREMPP_RESUME_SAVE_TIMEOUT_SECONDS` | Max wait (seconds) for non-blocking resume save confirmation | `5.0` |

---

## Results Payload Transport

| Variable | Purpose | Default |
|---|---|---|
| `BIOREMPP_RESULTS_PAYLOAD_MODE` | Transport mode for `merged-result-store` (`client`, `server`) | `server` |
| `BIOREMPP_RESULTS_HYDRATION_CACHE_SIZE` | In-memory entries for hydrated payload cache | `64` |
| `BIOREMPP_RESULTS_HYDRATION_CACHE_TTL_SECONDS` | TTL (seconds) for hydrated payload cache entries | `900` |
| `BIOREMPP_RESULTS_HYDRATION_RETRY_ATTEMPTS` | Retry attempts when hydration returns `not_found` | `8` |
| `BIOREMPP_RESULTS_HYDRATION_RETRY_DELAY_MS` | Delay in milliseconds between hydration retries | `250` |

---

## Resume Rate-Limit

| Variable | Purpose | Default |
|---|---|---|
| `BIOREMPP_RESUME_RATE_LIMIT_ATTEMPTS` | Attempts per window | `10` |
| `BIOREMPP_RESUME_RATE_LIMIT_WINDOW_SECONDS` | Rate-limit window | `60` |
| `BIOREMPP_RESUME_RATE_LIMIT_BACKOFF_BASE_SECONDS` | Base backoff | `5` |
| `BIOREMPP_RESUME_RATE_LIMIT_BACKOFF_MAX_SECONDS` | Max backoff | `300` |
| `BIOREMPP_RESUME_RATE_LIMIT_CACHE_SIZE_MB` | Local limiter cache size | `64` |
| `BIOREMPP_RESUME_RATE_LIMIT_BACKEND` | Backend (`auto`, `diskcache`, `redis`) | `auto` |
| `BIOREMPP_RESUME_RATE_LIMIT_REDIS_KEY_PREFIX` | Redis limiter key prefix | `biorempp:resume:ratelimit:` |

---

## Resume Alert Thresholds

| Variable | Purpose | Default |
|---|---|---|
| `BIOREMPP_RESUME_ALERT_WINDOW_SECONDS` | Alert window | `300` |
| `BIOREMPP_RESUME_ALERT_NOT_FOUND_THRESHOLD` | Not-found threshold | `30` |
| `BIOREMPP_RESUME_ALERT_TOKEN_MISMATCH_THRESHOLD` | Token mismatch threshold | `10` |
| `BIOREMPP_RESUME_ALERT_SAVE_FAILED_THRESHOLD` | Save failed threshold | `5` |

---

## Security and Proxy Trust

| Variable | Purpose | Default |
|---|---|---|
| `SECRET_KEY` | Required secret in production | empty (must be set securely in prod) |
| `BIOREMPP_TRUST_PROXY_HEADERS` | Trust `X-Forwarded-*` headers | `false` |
| `BIOREMPP_TRUSTED_PROXY_CIDRS` | Trusted ingress/proxy CIDRs | `127.0.0.1/32,::1/128` |
| `BIOREMPP_PUBLIC_DATA_ALLOWED_FILES` | Allowlist for `/data/<filename>` | `exemple_dataset.txt` |
| `BIOREMPP_LOG_REF_SALT` | Salt for HMAC log references | falls back to `SECRET_KEY` |
| `BIOREMPP_LOG_REF_LENGTH` | Redacted reference length | `12` (clamped 8..24) |

### Production fail-fast notes

Startup aborts in production when:

- `SECRET_KEY` is missing, placeholder, or weak;
- Redis backend is selected without secure Redis password;
- `BIOREMPP_TRUST_PROXY_HEADERS=true` with invalid/missing trusted CIDRs.

---

## Observability

| Variable | Purpose | Default |
|---|---|---|
| `BIOREMPP_OBSERVABILITY_ENABLED` | Enable app metrics instrumentation | `false` |
| `BIOREMPP_OBSERVABILITY_METRICS_PATH` | Metrics endpoint path | `/metrics` |
| `BIOREMPP_OBSERVABILITY_FAIL_FAST` | Fail startup when observability prerequisites fail | `false` |
| `PROMETHEUS_MULTIPROC_DIR` | Prometheus multiprocess directory | `/tmp/prometheus_multiproc` |
| `BIOREMPP_OBSERVABILITY_MULTIPROC_TMPFS_SIZE_BYTES` | tmpfs size for multiprocess files | `67108864` |

---

## Redis Cache (Optional)

| Variable | Purpose | Default |
|---|---|---|
| `ENABLE_CACHE` | Enable application Redis cache usage | `False` |
| `REDIS_HOST` | Redis host | `redis` |
| `REDIS_PORT` | Redis port | `6379` |
| `REDIS_DB` | Redis DB index | `0` |
| `REDIS_PASSWORD` | Redis password | empty (must be secure in prod use) |
| `CACHE_DEFAULT_TIMEOUT` | Cache TTL (seconds) | `300` |
| `CACHE_THRESHOLD` | Cache entry threshold | `1000` |

---

## Minimal Production Example

```bash
# .env/env.production
BIOREMPP_ENV=production
BIOREMPP_URL_BASE_PATH=/
SECRET_KEY=<secure-secret>
BIOREMPP_TRUST_PROXY_HEADERS=true
BIOREMPP_TRUSTED_PROXY_CIDRS=<institution-cidrs>
BIOREMPP_RESUME_BACKEND=diskcache
BIOREMPP_OBSERVABILITY_ENABLED=false
```

To enable Redis-backed resume and full observability, adjust values in `.env/env.production` and activate `cache`/`observability` profiles in Docker Compose.

---

## See Also

- [Docker Integration](docker-integration.md)
- [Nginx Integration](nginx-integration.md)
- [Institutional Ingress Handoff](institutional_ingress_handoff.md)
- [Gunicorn Configuration](gunicorn.md)
- [Health Endpoints](health-endpoints.md)
