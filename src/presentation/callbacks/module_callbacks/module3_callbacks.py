"""
Module 3 Callbacks - Functional Similarity Analysis.

This module registers callback handlers for Module 3 functionality,
including PCA analysis and sample similarity visualizations.

Functions
---------
register_module3_callbacks
    Register all Module 3 callbacks with Dash app.

Notes
-----
- Refer to official documentation for supported use case details
- Uses PCAStrategy and CorrelogramStrategy for visualizations
"""

import logging

from src.presentation.callbacks.module3 import (
    register_uc_3_1_callbacks,
    register_uc_3_2_callbacks,
    register_uc_3_3_callbacks,
    register_uc_3_4_callbacks,
    register_uc_3_5_callbacks,
    register_uc_3_6_callbacks,
    register_uc_3_7_callbacks,
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.propagate = False
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter("[%(levelname)s] %(name)s: %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)


def register_module3_callbacks(app, plot_service) -> None:
    """
    Register all Module 3 callbacks with Dash app.

    Parameters
    ----------
    app : Dash
        Dash application instance.
    plot_service : PlotService
        Singleton PlotService instance (shared across all callbacks).

    Notes
    -----
    - Registers callback handlers for Module 3 use cases
    - Refer to official documentation for supported use case details
    """
    logger.info("=" * 60)
    logger.info("REGISTERING MODULE 3 CALLBACKS...")
    logger.info("=" * 60)

    # Register UC-3.1: PCA - Sample Relationships by KO Profile
    logger.info("→ Registering UC-3.1...")
    register_uc_3_1_callbacks(app, plot_service)
    logger.info("[OK] UC-3.1 callbacks registered (PCA - KO profile)")

    # Register UC-3.2: PCA - Sample Relationships by Chemical Profile
    logger.info("→ Registering UC-3.2...")
    register_uc_3_2_callbacks(app, plot_service)
    logger.info("[OK] UC-3.2 callbacks registered (PCA - Compound profile)")

    # Register UC-3.3: Interactive Hierarchical Clustering of Samples
    logger.info("→ Registering UC-3.3...")
    register_uc_3_3_callbacks(app, plot_service)
    logger.info("[OK] UC-3.3 callbacks registered (Hierarchical clustering)")

    # Register UC-3.4: Sample Similarity Based on KO Profiles
    logger.info("→ Registering UC-3.4...")
    register_uc_3_4_callbacks(app, plot_service)
    logger.info("[OK] UC-3.4 callbacks registered (Sample similarity - KO)")

    # Register UC-3.5: Sample Similarity Based on Compound Profiles
    logger.info("→ Registering UC-3.5...")
    register_uc_3_5_callbacks(app, plot_service)
    logger.info("[OK] UC-3.5 callbacks registered (Sample similarity - Compound)")

    # Register UC-3.6: Gene Co-occurrence Patterns Across Samples
    logger.info("→ Registering UC-3.6...")
    register_uc_3_6_callbacks(app, plot_service)
    logger.info("[OK] UC-3.6 callbacks registered (Gene symbol co-occurrence)")

    # Register UC-3.7: Compound Co-occurrence Patterns Across Samples
    logger.info("→ Registering UC-3.7...")
    register_uc_3_7_callbacks(app, plot_service)
    logger.info("[OK] UC-3.7 callbacks registered (Compound co-occurrence)")

    logger.info("=" * 60)
    logger.info("[OK] ALL MODULE 3 CALLBACKS REGISTERED SUCCESSFULLY")
    logger.info("=" * 60)
