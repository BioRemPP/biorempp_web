"""
Gunicorn Configuration for BioRemPP v1.0

This module configures Gunicorn WSGI server for production deployment.

Features:
- Multi-worker process model
- Async workers with gevent (optional)
- Automatic worker restart to prevent memory leaks
- Structured logging
- Health monitoring

Usage:
    gunicorn wsgi:server -c gunicorn_config.py
"""

# Ensure project root is importable when Gunicorn loads this config file.
import os
import shutil
import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Load settings
from config.settings import get_settings


def _prepare_prometheus_multiproc_dir() -> None:
    """
    Ensure PROMETHEUS_MULTIPROC_DIR exists and is writable before metric import.

    This prevents startup failures when container volumes mount read-only or
    root-owned cache paths.
    """
    raw_dir = os.getenv("PROMETHEUS_MULTIPROC_DIR", "").strip()
    if not raw_dir:
        return

    target_dir = Path(raw_dir)
    try:
        target_dir.mkdir(parents=True, exist_ok=True)
        probe_path = target_dir / ".prom_write_probe"
        probe_path.write_text("ok", encoding="utf-8")
        probe_path.unlink(missing_ok=True)
    except Exception:
        fallback_dir = Path("/tmp/biorempp-cache/prometheus_multiproc")
        fallback_dir.mkdir(parents=True, exist_ok=True)
        os.environ["PROMETHEUS_MULTIPROC_DIR"] = str(fallback_dir)


_prepare_prometheus_multiproc_dir()

from src.shared.metrics import WORKERS_ACTIVE, WORKER_REQUESTS_TOTAL, WORKER_RESTARTS_TOTAL

try:
    from prometheus_client import multiprocess as prom_multiprocess
except Exception:  # pragma: no cover - defensive fallback
    prom_multiprocess = None

settings = get_settings()

# ============================================================================
# SERVER SOCKET
# ============================================================================
bind = f"{settings.HOST}:{settings.PORT}"
backlog = 2048  # Number of pending connections

# ============================================================================
# WORKER PROCESSES
# ============================================================================
workers = settings.WORKERS
worker_class = settings.WORKER_CLASS
worker_connections = settings.WORKER_CONNECTIONS
timeout = settings.TIMEOUT
keepalive = settings.KEEPALIVE

# Restart workers periodically (prevents memory leaks)
max_requests = 1000
max_requests_jitter = 50  # Randomize restart to avoid all workers restarting at once

# ============================================================================
# LOGGING
# ============================================================================
# Ensure log directory exists
log_dir = settings.LOG_DIR
log_dir.mkdir(exist_ok=True)

# Access log (HTTP requests)
accesslog = str(log_dir / 'gunicorn_access.log') if settings.is_production else '-'
# Error log (application errors)
errorlog = str(log_dir / 'gunicorn_error.log') if settings.is_production else '-'
# Log level
loglevel = settings.LOG_LEVEL.lower()

# Access log format
access_log_format = (
    '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s '
    '"%(f)s" "%(a)s" %(D)s'
)
# Format explanation:
# %(h)s - Remote address
# %(l)s - '-' (not used)
# %(u)s - User name
# %(t)s - Date/time of request
# %(r)s - Request line (method, path, protocol)
# %(s)s - Status code
# %(b)s - Response length
# %(f)s - Referer
# %(a)s - User agent
# %(D)s - Request time in microseconds

# ============================================================================
# PROCESS NAMING
# ============================================================================
proc_name = 'biorempp'

# ============================================================================
# SERVER MECHANICS
# ============================================================================
daemon = False  # Don't daemonize (Docker/systemd handles this)
pidfile = None  # No PID file needed
umask = 0
user = None  # Run as current user
group = None  # Run as current group
tmp_upload_dir = None

# ============================================================================
# SSL (if needed)
# ============================================================================
# Uncomment and configure if running Gunicorn with SSL directly
# (Usually SSL is handled by Nginx reverse proxy)
# keyfile = '/path/to/key.pem'
# certfile = '/path/to/cert.pem'

# ============================================================================
# SERVER HOOKS
# ============================================================================


def _resolve_multiproc_dir() -> Path | None:
    """Return configured Prometheus multiprocess directory."""
    raw = os.getenv("PROMETHEUS_MULTIPROC_DIR", "").strip()
    if not raw:
        return None
    return Path(raw)


def _cleanup_multiproc_dir(multiproc_dir: Path) -> int:
    """Remove stale Prometheus multiprocess files before startup."""
    if not multiproc_dir.exists():
        multiproc_dir.mkdir(parents=True, exist_ok=True)
        return 0

    removed_entries = 0
    for child in multiproc_dir.iterdir():
        if child.is_dir():
            shutil.rmtree(child, ignore_errors=True)
            removed_entries += 1
        else:
            child.unlink(missing_ok=True)
            removed_entries += 1
    return removed_entries


def on_starting(server):
    """
    Called just before the master process is initialized.

    Server initialization hook.
    """
    print("=" * 80)
    print("Gunicorn server starting...")
    print(f"Environment: {settings.ENV}")
    print(f"Bind: {bind}")
    print(f"Workers: {workers} ({worker_class})")
    print(f"Timeout: {timeout}s")
    print(f"Keepalive: {keepalive}s")
    print(f"Max Requests: {max_requests} +/- {max_requests_jitter}")
    print(
        "Security Limits: "
        f"line={limit_request_line}, "
        f"header_fields={limit_request_fields}, "
        f"header_field_size={limit_request_field_size}, "
        f"max_body={max_request_body_bytes}"
    )

    multiproc_dir = _resolve_multiproc_dir()
    if multiproc_dir is not None:
        try:
            removed_entries = _cleanup_multiproc_dir(multiproc_dir)
            print(
                "Prometheus multiprocess dir prepared: "
                f"{multiproc_dir} (removed {removed_entries} stale entries)"
            )
        except Exception as exc:  # pragma: no cover - startup diagnostics
            print(
                "WARNING: failed to prepare PROMETHEUS_MULTIPROC_DIR "
                f"({multiproc_dir}): {exc}"
            )

    print("=" * 80)


def when_ready(server):
    """
    Called just after the server is started.

    Server ready hook.
    """
    print("=" * 80)
    print(f"[OK] Gunicorn server ready on {bind}")
    print(f"[OK] Process name: {proc_name}")
    print(f"[OK] Logging to: {log_dir}")
    print("=" * 80)


def on_exit(server):
    """
    Called just before exiting Gunicorn.

    Server exit hook.
    """
    print("=" * 80)
    print("Gunicorn server shutting down...")
    print("=" * 80)


def worker_int(worker):
    """
    Called when a worker receives the INT or QUIT signal.

    Worker interrupt hook.
    """
    print(f"Worker {worker.pid} interrupted")


def pre_fork(server, worker):
    """
    Called just before a worker is forked.

    Pre-fork hook.
    """
    pass


def post_fork(server, worker):
    """
    Called just after a worker has been forked.

    Post-fork hook.
    """
    WORKERS_ACTIVE.set(1)
    print(f"Worker spawned (pid: {worker.pid})")


def pre_exec(server):
    """
    Called just before a new master process is forked.

    Pre-exec hook.
    """
    print("Forking new master process")


def pre_request(worker, req):
    """
    Called just before a worker processes the request.

    Pre-request hook.
    """
    # Log request start time for performance monitoring
    worker.log.debug(f"{req.method} {req.path}")
    WORKER_REQUESTS_TOTAL.labels(worker_pid=str(worker.pid)).inc()
    try:
        content_length_raw = req.headers.get("Content-Length", "0")
        content_length = int(content_length_raw)
    except Exception:
        content_length = 0
    if content_length > max_request_body_bytes:
        worker.log.warning(
            "request_body_limit_exceeded "
            f"path={req.path} method={req.method} "
            f"content_length={content_length} limit={max_request_body_bytes}"
        )


def post_request(worker, req, environ, resp):
    """
    Called after a worker processes the request.

    Post-request hook.
    """
    pass


def child_exit(server, worker):
    """
    Called just after a worker has been exited.

    Child exit hook.
    """
    WORKER_RESTARTS_TOTAL.labels(reason="child_exit").inc()
    multiproc_dir = _resolve_multiproc_dir()
    if prom_multiprocess is not None and multiproc_dir is not None:
        try:
            prom_multiprocess.mark_process_dead(worker.pid)
        except Exception as exc:  # pragma: no cover - lifecycle fallback
            print(
                "WARNING: failed to mark worker as dead for prometheus "
                f"(pid={worker.pid}): {exc}"
            )
    print(f"Worker exited (pid: {worker.pid})")


def worker_abort(worker):
    """
    Called when a worker received the SIGABRT signal.

    Worker abort hook.
    """
    WORKER_RESTARTS_TOTAL.labels(reason="worker_abort").inc()
    print(f"Worker aborted (pid: {worker.pid})")


def nworkers_changed(server, new_value, old_value):
    """
    Called when the number of workers changes.

    Workers changed hook.
    """
    WORKER_RESTARTS_TOTAL.labels(reason="scale_change").inc()
    print(f"Workers changed: {old_value} -> {new_value}")


# ============================================================================
# SECURITY
# ============================================================================
# Request body limit (enforced at app level; logged here for observability)
max_request_body_bytes = settings.GUNICORN_MAX_REQUEST_BODY_BYTES
# Limit request line size
limit_request_line = settings.GUNICORN_LIMIT_REQUEST_LINE
# Limit request header field size
limit_request_field_size = settings.GUNICORN_LIMIT_REQUEST_FIELD_SIZE
# Limit number of request header fields
limit_request_fields = settings.GUNICORN_LIMIT_REQUEST_FIELDS

# ============================================================================
# PERFORMANCE TUNING
# ============================================================================
# Enable sendfile for static file serving (if serving static files)
sendfile = False  # Dash handles static files

# Disable error capture for better performance
capture_output = False

# Preload application code before worker processes are forked
# CRITICAL: Set to True to prevent duplicate callback registration
# With preload_app=True, the app is initialized once in the master process,
# then forked to workers, ensuring callbacks are registered only once
preload_app = True

# Reuse port (SO_REUSEPORT) - Linux 3.9+
reuse_port = False
