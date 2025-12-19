"""
Callbacks Package - BioRemPP v1.0.

Dash callbacks for UI interactivity and backend integration.
"""

import logging

from .info_modal_callbacks import register_info_modal_callbacks
from .module_callbacks import (
    register_module1_callbacks,
    register_module2_callbacks,
    register_module3_callbacks,
    register_module4_callbacks,
    register_module5_callbacks,
    register_module6_callbacks,
    register_module7_callbacks,
    register_module8_callbacks,
)
from .processing_callbacks import register_processing_callbacks
from .real_processing_callbacks import register_real_processing_callbacks
from .real_upload_callbacks import register_real_upload_callbacks
from .results_callbacks import register_results_callbacks
from .upload_callbacks import register_upload_callbacks

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.propagate = False  # Prevent duplicate logs from parent loggers
# Only add handler if not already present (prevents duplicates on reimport)
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter("[%(levelname)s] %(name)s: %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)

__all__ = [
    "register_upload_callbacks",
    "register_processing_callbacks",
    "register_real_upload_callbacks",
    "register_real_processing_callbacks",
    "register_results_callbacks",
    "register_module1_callbacks",
    "register_module2_callbacks",
    "register_module3_callbacks",
    "register_module4_callbacks",
    "register_module5_callbacks",
    "register_module6_callbacks",
    "register_module7_callbacks",
    "register_module8_callbacks",
    "register_info_modal_callbacks",
    "register_all_callbacks",
]


def register_all_callbacks(
    app,
    plot_service=None,
    upload_handler=None,
    data_processor=None,
    progress_tracker=None,
):
    """
    Register all application callbacks.

    Parameters
    ----------
    app : Dash
        Dash application instance
    plot_service : Optional[PlotService]
        Singleton PlotService instance (CRITICAL: shared across all callbacks)
    upload_handler : Optional[UploadHandler]
        UploadHandler from Application Layer
    data_processor : Optional[DataProcessor]
        DataProcessor from Application Layer
    progress_tracker : Optional[ProgressTracker]
        ProgressTracker from Application Layer

    Notes
    -----
    - Registers upload callbacks (file upload, validation)
    - Registers processing callbacks (data processing, progress)
    - Services can be injected or auto-initialized
    - Falls back to real callbacks if Application Layer not available
    - PlotService is passed to all module callbacks (Singleton pattern)

    Examples
    --------
    >>> from dash import Dash
    >>> from application.plot_services.singleton import get_plot_service
    >>> app = Dash(__name__)
    >>> plot_service = get_plot_service()
    >>> register_all_callbacks(app, plot_service=plot_service)
    """
    logger.info("\n" + "=" * 80)
    logger.info("REGISTERING ALL CALLBACKS")
    logger.info("=" * 80)

    # Always register real callbacks (they work standalone)
    logger.info("\n[1/10] Registering REAL UPLOAD callbacks...")
    register_real_upload_callbacks(app)

    logger.info("\n[2/10] Registering REAL PROCESSING callbacks...")
    register_real_processing_callbacks(app)

    logger.info("\n[3/10] Registering RESULTS callbacks...")
    register_results_callbacks(app)

    logger.info("\n[4/10] Registering MODULE 1 callbacks...")
    register_module1_callbacks(app, plot_service)

    logger.info("\n[5/10] Registering MODULE 2 callbacks...")
    register_module2_callbacks(app, plot_service)

    logger.info("\n[6/10] Registering MODULE 3 callbacks...")
    register_module3_callbacks(app, plot_service)

    logger.info("\n[7/11] Registering MODULE 4 callbacks...")
    register_module4_callbacks(app, plot_service)

    logger.info("\n[8/11] Registering MODULE 5 callbacks...")
    register_module5_callbacks(app, plot_service)

    logger.info("\n[9/11] Registering MODULE 6 callbacks...")
    register_module6_callbacks(app, plot_service)

    logger.info("\n[10/11] Registering MODULE 7 callbacks...")
    register_module7_callbacks(app, plot_service)

    logger.info("\n[11/11] Registering MODULE 8 callbacks...")
    register_module8_callbacks(app, plot_service)

    logger.info("\n[12/12] Registering INFO MODAL callbacks...")
    register_info_modal_callbacks(app)

    logger.info("\n" + "=" * 80)
    logger.info("[OK] ALL CALLBACKS REGISTERED SUCCESSFULLY")
    logger.info("=" * 80 + "\n")

    # Application Layer callbacks are optional and not used in Phase 5
    # They can be enabled in future phases if needed
