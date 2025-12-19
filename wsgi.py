"""
WSGI Entry Point for Production (Gunicorn)

This module provides the WSGI application entry point for running
BioRemPP v1.0 with Gunicorn in production environments.

Usage:
    gunicorn wsgi:server -c gunicorn_config.py

Notes:
    - This file must be in the same directory as biorempp_app.py
    - Gunicorn will use the 'server' variable to access the Flask server
    - All application initialization happens in biorempp_app
"""

import logging
import sys
from pathlib import Path

# Add current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from config.settings import get_settings
from src.shared.logging.config import LogConfig

# Load settings
settings = get_settings()

# Configure logging for production
log_config = LogConfig(environment=settings.ENV)
log_config.setup()

logger = logging.getLogger(__name__)
logger.info("=" * 80)
logger.info(f"BioRemPP v1.0 - WSGI Entry Point ({settings.ENV} mode)")
logger.info("=" * 80)

# Import factory and create full app instance for WSGI servers
# Import the factory and request a forced full initialization. Some WSGI
# servers import this module at startup; force initialization bypasses the
# development reloader parent guard so the returned app has callbacks/layout
# registered.
from biorempp_app import create_app

# Create the full application instance here so that WSGI servers
# (Gunicorn, Waitress) get a properly initialized Dash app.
app = create_app(force_initialize=True)

# Expose Flask server for WSGI
server = app.server

logger.info("[OK] WSGI server instance created")
logger.info(f"  Environment: {settings.ENV}")
logger.info(f"  Workers: {settings.WORKERS}")
logger.info(f"  Worker Class: {settings.WORKER_CLASS}")
logger.info("=" * 80)

if __name__ == "__main__":
    # This should not be called directly in production
    logger.warning("=" * 80)
    logger.warning("WARNING: Do not run wsgi.py directly!")
    logger.warning("Use Gunicorn to run this application:")
    logger.warning("  gunicorn wsgi:server -c gunicorn_config.py")
    logger.warning("=" * 80)
