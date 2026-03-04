"""
BioRemPP v1.0 - Main Application Entry Point.

Dash application with Phase 4 Presentation Layer.

Usage
-----
python biorempp_app.py

Notes
-----
- Clean Architecture with separated layers
- Homepage with upload workflow
- Backend integration via callbacks
- State management with dcc.Stores
"""

import logging
import os
from pathlib import Path

import dash
import dash_bootstrap_components as dbc
import diskcache
from dash import DiskcacheManager, Input, Output, State, callback, dcc, html

# Silence watchdog debug logs (used by Dash hot-reload)
logging.getLogger("watchdog").setLevel(logging.WARNING)
logging.getLogger("watchdog.observers").setLevel(logging.WARNING)
logging.getLogger("watchdog.observers.inotify_buffer").setLevel(logging.WARNING)

# Import unified configuration system
from config.settings import APP_NAME, APP_VERSION, get_settings

# Import Singleton PlotService
from src.application.plot_services.singleton import get_plot_service
from src.presentation.callbacks import register_all_callbacks
from src.presentation.callbacks.database_download_callbacks import (
    register_database_download_callbacks,
)
from src.presentation.callbacks.download_callbacks import register_download_callbacks
from src.presentation.callbacks.navigation_callbacks import (
    register_navigation_callbacks,
)
from src.presentation.errors import (
    FILE_NOT_FOUND_PAYLOAD,
    register_http_error_handlers,
)
from src.presentation.routing import app_path, strip_base_path
from src.presentation.components.composite.analysis_suggestions import (
    register_suggestions_callbacks,
)

# Presentation Layer
from src.presentation.pages import (
    create_contact_page,
    create_documentation_page,
    create_error_400_page,
    create_error_500_page,
    create_faq_page,
    create_how_to_cite_page,
    create_methods_page,
    create_regulatory_page,
    create_scientific_methods_page,
    create_user_guide_page,
    get_home_layout,
    get_results_layout,
)
from src.presentation.pages.database_schemas import (
    create_schemas_index_page,
    create_biorempp_schema_page,
    create_hadeg_schema_page,
    create_kegg_schema_page,
    create_toxcsm_schema_page,
)
from src.presentation.pages.methods.callbacks import (
    register_callbacks as register_methods_callbacks,
)
from src.presentation.pages.new_user import register_new_user_guide_callbacks
from src.presentation.pages.uc_user_guide import register_demo_callbacks

# Initialize application settings and logging
settings = get_settings()
settings.configure_logging()  # Setup logging based on environment

# Get logger for this module
logger = logging.getLogger(__name__)

# Application Layer (optional - not used in Phase 5)

# Phase 5 uses real callbacks directly with DataProcessingService
APPLICATION_LAYER_AVAILABLE = False


# ============================================================================
# CRITICAL: Prevent duplicate app initialization from Werkzeug reloader
# ============================================================================


def is_reloader_process():
    """Check if this is the Werkzeug reloader parent process."""
    # If hot reload is disabled, we're never in a reloader process
    if not settings.HOT_RELOAD:
        return False
    return os.environ.get('WERKZEUG_RUN_MAIN') != 'true'


def create_app(force_initialize: bool = False) -> dash.Dash:
    """
    Create and configure Dash application.
    
    Returns
    -------
    dash.Dash
        Configured Dash application
    
    Notes
    -----
    - Uses DashBootstrap BOOTSTRAP theme
    - Registers all callbacks
    - Sets up routing for / and /results
    """
    # CRITICAL: Skip full initialization in parent reloader process unless
    # `force_initialize` is True (used by WSGI entrypoints to ensure a fully
    # initialized application when imported by servers such as Gunicorn/Waitress).
    if is_reloader_process() and not force_initialize:
        logger.warning("=" * 80)
        logger.warning("PARENT PROCESS DETECTED - SKIPPING INITIALIZATION")
        logger.warning("Only child worker will register callbacks")
        logger.warning("=" * 80)
        # Return minimal dummy app for parent process
        dummy = dash.Dash(__name__)
        return dummy
    
    logger.info("=" * 80)
    logger.info("CHILD WORKER PROCESS - CREATING FULL APP INSTANCE")
    logger.info("=" * 80)

    long_callback_manager = None
    if settings.BACKGROUND_CALLBACKS_ENABLED:
        # Configure long callback cache manager for progress tracking.
        # Cache root is standardized via BIOREMPP_CACHE_DIR
        # (default: /app/cache in Docker).
        cache_dir = settings.CACHE_DIR / "long_callbacks"
        cache_dir.mkdir(parents=True, exist_ok=True)
        cache = diskcache.Cache(str(cache_dir))
        long_callback_manager = DiskcacheManager(cache)
        logger.info(f"[OK] Long callback cache configured at: {cache_dir}")
    else:
        logger.warning(
            "Background callbacks disabled; processing will run in request worker"
        )

    # Initialize Dash app with Font Awesome
    font_awesome = "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css"

    dash_kwargs = dict(
        external_stylesheets=[
            dbc.themes.MINTY,
            font_awesome
        ],
        suppress_callback_exceptions=True,
        title=f"{APP_NAME} v{APP_VERSION}",
        assets_folder='src/assets',
        url_base_pathname=settings.URL_BASE_PATH,
    )
    if long_callback_manager is not None:
        dash_kwargs["background_callback_manager"] = long_callback_manager

    app = dash.Dash(__name__, **dash_kwargs)
    app.server.config["BIOREMPP_BACKGROUND_CALLBACKS_ENABLED"] = (
        settings.BACKGROUND_CALLBACKS_ENABLED
    )
    favicon_href = f"{app.get_asset_url('favicon.ico')}?v={APP_VERSION}"
    app.index_string = app.index_string.replace(
        "{%favicon%}",
        f'<link rel="icon" type="image/x-icon" href="{favicon_href}">'
    )
    logger.info("[OK] Dash app created")
    logger.info("  - Theme: Bootstrap MINTY")
    logger.info("  - Callback exceptions: Suppressed")
    logger.info(
        f"  - Long callbacks: {'Enabled with diskcache' if long_callback_manager else 'Disabled'}"
    )
    
    # Set app layout with routing
    app.layout = html.Div([
        dcc.Location(id='url', refresh=False),
        
        # Global data stores (memory to avoid quota errors with large datasets)
        dcc.Store(id='upload-data-store', storage_type='memory'),
        dcc.Store(id='example-data-store', storage_type='memory'),
        dcc.Store(id='merged-result-store', storage_type='memory'),
        
        html.Div(id='page-content')
    ])
    logger.info("[OK] App layout configured")
    logger.info("  - Stores: upload-data, example-data, merged-result")
    logger.info("  - Routing: url, page-content")
    
    # Routing callback
    @app.callback(
        Output('page-content', 'children'),
        Input('url', 'pathname'),
        State('merged-result-store', 'data')
    )
    def display_page(pathname, merged_data):
        """
        Route page display based on URL pathname.

        Parameters
        ----------
        pathname : str
            URL pathname
        merged_data : dict
            Merged result data from processing

        Returns
        -------
        Component
            Page layout component
        """
        normalized_pathname = strip_base_path(pathname)

        if normalized_pathname == '/faq':
            # FAQ page
            return create_faq_page()
        elif normalized_pathname == '/regulatory':
            # Regulatory reference page
            return create_regulatory_page()
        elif normalized_pathname == '/help/contact' or normalized_pathname == '/contact':
            # Contact/Help page
            return create_contact_page()
        elif normalized_pathname == '/help/user-guide' or normalized_pathname == '/user-guide':
            # User Guide page
            return create_user_guide_page()
        elif normalized_pathname == '/methods/overview':
            # Scientific Methods Overview page
            return create_scientific_methods_page()
        elif normalized_pathname == '/methods':
            # Methods page
            return create_methods_page()
        elif normalized_pathname == '/documentation':
            # Documentation page
            return create_documentation_page()
        elif normalized_pathname == '/how-to-cite':
            # How to Cite page
            return create_how_to_cite_page()
        elif normalized_pathname == '/schemas':
            # Database Schemas index page
            return create_schemas_index_page()
        elif normalized_pathname == '/schemas/biorempp':
            # BioRemPP schema page
            return create_biorempp_schema_page()
        elif normalized_pathname == '/schemas/hadeg':
            # HADEG schema page
            return create_hadeg_schema_page()
        elif normalized_pathname == '/schemas/kegg':
            # KEGG schema page
            return create_kegg_schema_page()
        elif normalized_pathname == '/schemas/toxcsm':
            # ToxCSM schema page
            return create_toxcsm_schema_page()
        elif normalized_pathname == '/error/400':
            # Custom bad request page
            return create_error_400_page()
        elif normalized_pathname == '/error/500':
            # Custom internal server error page
            return create_error_500_page()
        elif normalized_pathname == '/results':
            if merged_data is None:
                # No data available - show alert
                return dbc.Container([
                    dbc.Alert(
                        [
                            html.I(className="fas fa-info-circle me-2"),
                            html.Div([
                                html.H5(
                                    "No Results Available",
                                    className="alert-heading"
                                ),
                                html.P(
                                    "Please upload data and process it first "
                                    "before viewing results."
                                ),
                                html.Hr(),
                                dbc.Button(
                                    [
                                        html.I(className="fas fa-home me-2"),
                                        "Go to Homepage"
                                    ],
                                    href=app_path("/"),
                                    color="primary"
                                )
                            ])
                        ],
                        color="info",
                        className="mt-5"
                    )
                ], className="mt-5")

            return get_results_layout(merged_data=merged_data)
        else:
            # Default to homepage
            return get_home_layout()
    
    # ========================================================================
    # Initialize Singleton PlotService (CRITICAL: Single instance per worker)
    # ========================================================================
    logger.info("\n" + "=" * 80)
    logger.info("INITIALIZING SINGLETON PLOTSERVICE")
    logger.info("=" * 80)
    plot_service = get_plot_service()
    logger.info("[OK] Singleton PlotService instance created and ready")
    logger.info("  - This single instance will be shared across all 51 callbacks")
    logger.info("  - Memory optimization: 37 instances → 1 instance (97% reduction)")
    logger.info("=" * 80 + "\n")

    # Register callbacks (Phase 5: Real callbacks only)
    logger.info("Registering callbacks with shared PlotService instance...")
    register_all_callbacks(app, plot_service=plot_service)

    # Register navigation callbacks
    logger.info("Registering navigation callbacks...")
    register_navigation_callbacks(app)

    # Register download callbacks (Phase 6: Download Feature)
    logger.info("Registering download callbacks for all use cases...")
    register_download_callbacks(app)
    register_database_download_callbacks(app)  # Database table downloads

    # Register user guide demo callbacks
    logger.info("Registering user guide interactive demo callbacks...")
    register_demo_callbacks(app)

    # Register analytical suggestions callbacks
    logger.info("Registering analytical suggestions callbacks...")
    register_suggestions_callbacks(app)

    # Register Methods page callbacks
    logger.info("Registering Methods page callbacks...")
    register_methods_callbacks(app)
    
    # Register New User Guide callbacks
    logger.info("Registering New User Guide callbacks...")
    register_new_user_guide_callbacks(app)

    # Add health check endpoints
    @app.server.route('/health')
    def health_check():
        """
        Health check endpoint for load balancers and monitoring.

        Returns:
            200: Service is healthy
        """
        return {
            "status": "healthy",
            "service": APP_NAME,
            "version": APP_VERSION,
            "environment": settings.ENV
        }, 200

    @app.server.route('/ready')
    def readiness_check():
        """
        Readiness check - verifies all dependencies are loaded.

        Returns:
            200: Service is ready to handle requests
            503: Service not ready (dependencies not loaded)
        """
        try:
            # Check if critical components are available
            checks = {
                "app": "ok",
                "settings": "ok",
                "logging": "ok"
            }

            # Optional: Add more checks if needed
            # - Database connection
            # - Cache availability
            # - Required files exist

            return {
                "status": "ready",
                "checks": checks
            }, 200
        except Exception as e:
            logger.error(f"Readiness check failed: {e}")
            return {
                "status": "not ready",
                "error": str(e)
            }, 503

    register_http_error_handlers(app)

    logger.info("[OK] Health/error endpoints registered (/health, /ready, 400, 500)")

    if settings.OBSERVABILITY_ENABLED:
        from src.shared.metrics import setup_observability

        setup_observability(
            app,
            metrics_path=settings.OBSERVABILITY_METRICS_PATH,
        )
        logger.info(
            "[OK] Observability enabled "
            f"({settings.OBSERVABILITY_METRICS_PATH})"
        )
    else:
        @app.server.route(settings.OBSERVABILITY_METRICS_PATH)
        def metrics_disabled():
            return {
                "status": "disabled",
                "message": "Observability is disabled",
            }, 404

        logger.info("[OK] Observability disabled")

    # Add static file route for example dataset download
    def serve_data_files(filename):
        """
        Serve static data files (e.g., example datasets) for download.

        Parameters
        ----------
        filename : str
            Name of the file to serve

        Returns
        -------
        Response
            File download response or 404 if not found
        """
        from flask import send_from_directory
        data_dir = Path(__file__).parent / "data"
        if not settings.is_public_data_file_allowed(filename):
            logger.warning("Blocked non-allowlisted public data file request")
            return FILE_NOT_FOUND_PAYLOAD, 404
        try:
            return send_from_directory(data_dir, filename, as_attachment=True)
        except FileNotFoundError:
            logger.warning("Allowlisted public data file not found on disk")
            return FILE_NOT_FOUND_PAYLOAD, 404

    root_data_route = "/data/<filename>"
    app.server.add_url_rule(
        root_data_route,
        endpoint="serve_public_data_root",
        view_func=serve_data_files,
    )

    prefixed_data_route = app_path("/data/<filename>")
    if prefixed_data_route != root_data_route:
        app.server.add_url_rule(
            prefixed_data_route,
            endpoint="serve_public_data_prefixed",
            view_func=serve_data_files,
        )
        logger.info(
            "[OK] Static data file routes registered "
            f"({root_data_route}, {prefixed_data_route})"
        )
    else:
        logger.info(f"[OK] Static data file route registered ({root_data_route})")

    logger.info("\n" + "=" * 80)
    logger.info("[OK] APPLICATION INITIALIZED SUCCESSFULLY")
    logger.info("=" * 80 + "\n")

    return app


if __name__ == "__main__":
    # Log which process this is
    if is_reloader_process():
        logger.info("=" * 80)
        logger.info("WERKZEUG RELOADER: Parent process starting")
        logger.info("This process will spawn a child worker process")
        logger.info("=" * 80)
    else:
        logger.info("=" * 80)
        logger.info("WERKZEUG RELOADER: Child worker process starting")
        logger.info("This is the actual application process")
        logger.info("=" * 80)
    
    app = create_app()
    
    # Always start server - the reloader will manage processes
    logger.info("\n" + "=" * 80)
    logger.info("STARTING DASH SERVER")
    logger.info(f"Environment: {settings.ENV}")
    logger.info(f"Debug Mode: {settings.DEBUG}")
    logger.info(f"Host: {settings.HOST}")
    logger.info(f"Port: {settings.PORT}")
    logger.info("=" * 80)
    app.run(
        debug=settings.DEBUG,
        host=settings.HOST,
        port=settings.PORT,
        dev_tools_hot_reload=settings.HOT_RELOAD,
        use_reloader=settings.HOT_RELOAD
    )

# NOTE: Export app for compatibility with Dash development server reloader ONLY.
# WSGI servers (Gunicorn/Waitress) should ALWAYS use wsgi.py which calls
# create_app(force_initialize=True) - this prevents duplicate callback registration.
#
# CRITICAL: When running under WSGI servers, do NOT initialize the app here.
# Each worker will import this module, and we must prevent duplicate initialization.
# The app instance should ONLY be created by wsgi.py for production deployments.
if __name__ != "__main__" and "gunicorn" not in os.environ.get("SERVER_SOFTWARE", "").lower():
    # Development mode with reloader - create app instance only for child worker
    if not is_reloader_process():
        app = create_app()
    else:
        app = None
else:
    # Production mode (Gunicorn) or direct execution - don't create module-level instance
    # wsgi.py will create the app instance explicitly
    app = None

