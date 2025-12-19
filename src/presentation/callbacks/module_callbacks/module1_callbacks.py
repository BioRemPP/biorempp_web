"""
Module 1 Callbacks - Database Assessment and Regulatory Analysis.

This module registers callback handlers for Module 1 functionality,
including database assessment and regulatory analysis features.

Functions
---------
register_module1_callbacks
    Register all Module 1 callbacks with Dash app.

Notes
-----
- Refer to official documentation for supported use case details
- Each use case has its own callback module with inline processing
"""

import logging

from src.presentation.callbacks.module1 import (
    register_uc_1_1_callbacks,
    register_uc_1_2_callbacks,
    register_uc_1_3_callbacks,
    register_uc_1_4_callbacks,
    register_uc_1_5_callbacks,
    register_uc_1_6_callbacks,
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)  # Ensure DEBUG level
logger.propagate = False  # Prevent duplicate logs from parent loggers
# Add handler if not present
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter("[%(levelname)s] %(name)s: %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)


def register_module1_callbacks(app, plot_service) -> None:
    """
    Register all Module 1 callbacks with Dash app.

    Parameters
    ----------
    app : Dash
        Dash application instance.
    plot_service : PlotService
        Singleton PlotService instance (shared across all callbacks).

    Notes
    -----
    - Registers callback handlers for Module 1 use cases
    - Refer to official documentation for supported use case details
    """
    logger.info("Starting Module 1 callback registration")

    try:
        # UC-1.1: Database Overlap and Unique Contributions
        logger.debug("Registering UC-1.1 callbacks...")
        register_uc_1_1_callbacks(app, plot_service)
        logger.info("[OK] UC-1.1 callbacks registered successfully")

        # UC-1.2: Regulatory Agency Compound Overlap
        logger.debug("Registering UC-1.2 callbacks...")
        register_uc_1_2_callbacks(app, plot_service)
        logger.info("[OK] UC-1.2 callbacks registered successfully")

        # UC-1.3: Proportional Contribution of Reference Agencies
        logger.debug("Registering UC-1.3 callbacks...")
        register_uc_1_3_callbacks(app, plot_service)
        logger.info("[OK] UC-1.3 callbacks registered successfully")

        # UC-1.4: Proportional Functional Diversity of Samples
        logger.debug("Registering UC-1.4 callbacks...")
        register_uc_1_4_callbacks(app, plot_service)
        logger.info("[OK] UC-1.4 callbacks registered successfully")

        # UC-1.5: Regulatory Compliance Scorecard
        logger.debug("Registering UC-1.5 callbacks...")
        register_uc_1_5_callbacks(app, plot_service)
        logger.info("[OK] UC-1.5 callbacks registered successfully")

        # UC-1.6: Sample-Agency Functional Potential Heatmap
        logger.debug("Registering UC-1.6 callbacks...")
        register_uc_1_6_callbacks(app, plot_service)
        logger.info("[OK] UC-1.6 callbacks registered successfully")

        logger.info("Module 1 callback registration complete")

    except Exception as e:
        logger.error(f"Failed to register Module 1 callbacks: {e}", exc_info=True)
        raise
