"""
Module 7 Callbacks - Toxicological Risk Assessment.

This module registers callback handlers for Module 7 functionality,
including toxicity profiling and risk assessment visualizations.

Functions
---------
register_module7_callbacks
    Register all Module 7 callbacks with Dash app.

Notes
-----
- Refer to official documentation for supported use case details
- Each use case has its own callback module with inline processing
"""

import logging

from src.presentation.callbacks.module7 import (
    register_uc_7_1_callbacks,
    register_uc_7_2_callbacks,
    register_uc_7_3_callbacks,
    register_uc_7_4_callbacks,
    register_uc_7_5_callbacks,
    register_uc_7_6_callbacks,
    register_uc_7_7_callbacks,
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.propagate = False
if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("[%(levelname)s] %(name)s: %(message)s"))
    logger.addHandler(handler)


def register_module7_callbacks(app, plot_service) -> None:
    """
    Register all Module 7 callbacks with Dash app.

    Parameters
    ----------
    app : Dash
        Dash application instance.
    plot_service : PlotService
        Singleton PlotService instance (shared across all callbacks).

    Notes
    -----
    - Registers callback handlers for Module 7 use cases
    - Refer to official documentation for supported use case details
    """
    logger.info("=" * 60)
    logger.info("REGISTERING MODULE 7 CALLBACKS...")
    logger.info("=" * 60)

    # Register UC-7.1: Faceted Heatmap of Predicted Compound Toxicity Profiles
    logger.info("→ Registering UC-7.1...")
    register_uc_7_1_callbacks(app, plot_service)
    logger.info("[OK] UC-7.1 callbacks registered (Toxicity fingerprints)")

    # Register UC-7.2: Concordance Between Predicted Risk and Regulatory Focus
    logger.info("→ Registering UC-7.2...")
    register_uc_7_2_callbacks(app, plot_service)
    logger.info("[OK] UC-7.2 callbacks registered (Risk-Regulatory Concordance)")

    # Register UC-7.3: Elite Specialist Identification
    logger.info("→ Registering UC-7.3...")
    register_uc_7_3_callbacks(app, plot_service)
    logger.info("[OK] UC-7.3 callbacks registered (Genetic Response Mapping)")

    # Register UC-7.4: Toxicity Score Distribution
    logger.info("→ Registering UC-7.4...")
    register_uc_7_4_callbacks(app, plot_service)
    logger.info("[OK] UC-7.4 callbacks registered (Toxicity endpoint distribution)")

    # Register UC-7.5: Interactive Distribution of Toxicity Scores by Endpoint Category
    logger.info("→ Registering UC-7.5...")
    register_uc_7_5_callbacks(app, plot_service)
    logger.info("[OK] UC-7.5 callbacks registered (Density plot toxicity distribution)")

    # Register UC-7.6: Sample Risk Mitigation Breadth by Compound Variety
    logger.info("→ Registering UC-7.6...")
    register_uc_7_6_callbacks(app, plot_service)
    logger.info("[OK] UC-7.6 callbacks registered (Risk Mitigation Breadth)")

    # Register UC-7.7: Sample Risk Mitigation Depth Profile by Genetic Investment
    logger.info("→ Registering UC-7.7...")
    register_uc_7_7_callbacks(app, plot_service)
    logger.info("[OK] UC-7.7 callbacks registered (Risk Mitigation Depth)")

    logger.info("=" * 60)
    logger.info("[OK] ALL MODULE 7 CALLBACKS REGISTERED SUCCESSFULLY")
    logger.info("=" * 60)
