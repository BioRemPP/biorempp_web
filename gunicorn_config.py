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

import multiprocessing
import os
from pathlib import Path

# Load settings
from config.settings import get_settings

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
    print(f"Max Requests: {max_requests} ± {max_requests_jitter}")
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
    print(f"Worker exited (pid: {worker.pid})")


def worker_abort(worker):
    """
    Called when a worker received the SIGABRT signal.

    Worker abort hook.
    """
    print(f"Worker aborted (pid: {worker.pid})")


def nworkers_changed(server, new_value, old_value):
    """
    Called when the number of workers changes.

    Workers changed hook.
    """
    print(f"Workers changed: {old_value} → {new_value}")


# ============================================================================
# SECURITY
# ============================================================================
# Limit request line size
limit_request_line = 4096  # 4KB
# Limit request header field size
limit_request_field_size = 8190  # 8KB
# Limit number of request header fields
limit_request_fields = 100

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
