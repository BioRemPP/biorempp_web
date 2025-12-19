"""
Module 2 Callbacks - Rankings and Compound Analysis.

This module registers callback handlers for Module 2 functionality,
including sample rankings and compound analysis features.

Functions
---------
register_module2_callbacks
    Register all Module 2 callbacks with Dash app.

Notes
-----
- Refer to official documentation for supported use case details
- Each use case has its own callback module with inline processing
"""

import logging

from src.presentation.callbacks.module2 import (
    register_uc_2_1_callbacks,
    register_uc_2_2_callbacks,
    register_uc_2_3_callbacks,
    register_uc_2_4_callbacks,
    register_uc_2_5_callbacks,
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)  # Ensure DEBUG level
logger.propagate = False  # Prevent duplicate logs from parent loggers
# Add handler if not present
if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("[%(levelname)s] %(name)s: %(message)s"))
    logger.addHandler(handler)


def register_module2_callbacks(app, plot_service) -> None:
    """
    Register all Module 2 callbacks with Dash app.

    Parameters
    ----------
    app : Dash
        Dash application instance.
    plot_service : PlotService
        Singleton PlotService instance (shared across all callbacks).

    Notes
    -----
    - Registers callback handlers for Module 2 use cases
    - Refer to official documentation for supported use case details
    """
    logger.info("=" * 60)
    logger.info("REGISTERING MODULE 2 CALLBACKS...")
    logger.info("=" * 60)

    # Register UC-2.1: Ranking of Samples by KO Richness
    logger.info("→ Registering UC-2.1...")
    register_uc_2_1_callbacks(app, plot_service)
    logger.info("[OK] UC-2.1 callbacks registered (KO richness analysis)")

    # Register UC-2.2: Ranking of Samples by Compound Richness
    logger.info("→ Registering UC-2.2...")
    register_uc_2_2_callbacks(app, plot_service)
    logger.info("[OK] UC-2.2 callbacks registered (Compound richness analysis)")

    # Register UC-2.3: Ranking of Compounds by Sample Diversity per Class
    logger.info("→ Registering UC-2.3...")
    register_uc_2_3_callbacks(app, plot_service)
    logger.info("[OK] UC-2.3 callbacks registered (Compound-sample diversity)")

    # Register UC-2.4: Ranking of Compounds by Genetic Interaction per Class
    logger.info("→ Registering UC-2.4...")
    register_uc_2_4_callbacks(app, plot_service)
    logger.info("[OK] UC-2.4 callbacks registered (Compound-gene diversity)")

    # Register UC-2.5: Distribution of KO Across Samples
    logger.info("→ Registering UC-2.5...")
    register_uc_2_5_callbacks(app, plot_service)
    logger.info("[OK] UC-2.5 callbacks registered (KO distribution)")

    logger.info("=" * 60)
    logger.info("[OK] ALL MODULE 2 CALLBACKS REGISTERED SUCCESSFULLY")
    logger.info("=" * 60)
