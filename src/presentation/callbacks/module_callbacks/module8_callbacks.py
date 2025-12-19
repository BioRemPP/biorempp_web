"""
Module 8 Callbacks - Assembly of Functional Consortia.

This module registers callback handlers for Module 8 functionality,
including consortium assembly and completeness analysis.

Functions
---------
register_module8_callbacks
    Register all Module 8 callbacks with Dash app.

Notes
-----
- Refer to official documentation for supported use case details
- Each use case has its own callback module with inline processing
"""

import logging

from src.presentation.callbacks.module8 import (
    register_uc_8_1_callbacks,
    register_uc_8_2_callbacks,
    register_uc_8_3_callbacks,
    register_uc_8_4_callbacks,
    register_uc_8_5_callbacks,
    register_uc_8_6_callbacks,
    register_uc_8_7_callbacks,
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


def register_module8_callbacks(app, plot_service) -> None:
    """
    Register all Module 8 callbacks with Dash app.

    Parameters
    ----------
    app : dash.Dash
        Dash application instance.
    plot_service : PlotService
        Singleton PlotService instance (shared across all callbacks).

    Notes
    -----
    - Registers callback handlers for Module 8 use cases
    - Refer to official documentation for supported use case details
    """
    logger.info("=" * 60)
    logger.info("REGISTERING MODULE 8 CALLBACKS")
    logger.info("=" * 60)

    # UC-8.1: Minimal Sample Grouping for Complete Compound Coverage
    logger.info("[Module 8] Registering UC-8.1 callbacks...")
    register_uc_8_1_callbacks(app, plot_service)
    logger.info("[Module 8] [OK] UC-8.1 callbacks registered successfully")

    # UC-8.2: Chemical Class Completeness Scorecard
    logger.info("[Module 8] Registering UC-8.2 callbacks...")
    register_uc_8_2_callbacks(app, plot_service)
    logger.info("[Module 8] [OK] UC-8.2 callbacks registered successfully")

    # UC-8.3: Compound-Specific KO Completeness Scorecard
    logger.info("[Module 8] Registering UC-8.3 callbacks...")
    register_uc_8_3_callbacks(app, plot_service)
    logger.info("[Module 8] [OK] UC-8.3 callbacks registered successfully")

    # UC-8.4: Pathway Completeness Scorecard for HADEG Pathways
    logger.info("[Module 8] Registering UC-8.4 callbacks...")
    register_uc_8_4_callbacks(app, plot_service)
    logger.info("[Module 8] \u2713 UC-8.4 callbacks registered successfully")

    # UC-8.5: KEGG Pathway Completeness Scorecard
    logger.info("[Module 8] Registering UC-8.5 callbacks...")
    register_uc_8_5_callbacks(app, plot_service)
    logger.info("[Module 8] \u2713 UC-8.5 callbacks registered successfully")

    # UC-8.6: Pathway-Centric Consortium Design by KO Coverage
    logger.info("[Module 8] Registering UC-8.6 callbacks...")
    register_uc_8_6_callbacks(app, plot_service)
    logger.info("[Module 8] [OK] UC-8.6 callbacks registered successfully")

    # UC-8.7: Intersection of Genes Across Samples
    logger.info("[Module 8] Registering UC-8.7 callbacks...")
    register_uc_8_7_callbacks(app, plot_service)
    logger.info("[Module 8] [OK] UC-8.7 callbacks registered successfully")

    logger.info("=" * 60)
    logger.info("MODULE 8 CALLBACKS REGISTRATION COMPLETE")
    logger.info("=" * 60)
