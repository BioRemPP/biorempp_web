"""
Module 6 Callbacks - Hierarchical and Flow-based Functional Analysis.

This module registers callback handlers for Module 6 functionality,
including Sankey flow diagrams and treemap hierarchical visualizations.

Functions
---------
register_module6_callbacks
    Register all Module 6 callbacks with Dash app.

Notes
-----
- Refer to official documentation for supported use case details
- Uses SankeyStrategy for flow visualizations
- Uses TreemapStrategy for hierarchical visualizations
"""

import logging

from src.presentation.callbacks.module6 import (
    register_uc_6_1_callbacks,
    register_uc_6_2_callbacks,
    register_uc_6_3_callbacks,
    register_uc_6_4_callbacks,
    register_uc_6_5_callbacks,
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.propagate = False
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter("[%(levelname)s] %(name)s: %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)


def register_module6_callbacks(app, plot_service) -> None:
    """
    Register all Module 6 callbacks with Dash app.

    Parameters
    ----------
    app : Dash
        Dash application instance.
    plot_service : PlotService
        Singleton PlotService instance (shared across all callbacks).

    Notes
    -----
    - Registers callback handlers for Module 6 use cases
    - Refer to official documentation for supported use case details
    """
    logger.info("=" * 60)
    logger.info("REGISTERING MODULE 6 CALLBACKS...")
    logger.info("=" * 60)

    # Register UC-6.1: Regulatory to Molecular Interaction Flow
    logger.info("→ Registering UC-6.1...")
    register_uc_6_1_callbacks(app, plot_service)
    logger.info("[OK] UC-6.1 callbacks registered (Regulatory-Molecular Sankey)")

    # Register UC-6.2: Biological Interaction Flow
    logger.info("→ Registering UC-6.2...")
    register_uc_6_2_callbacks(app, plot_service)
    logger.info("[OK] UC-6.2 callbacks registered (Biological Interaction Sankey)")

    # Register UC-6.3: Chemical Hierarchy of Bioremediation
    logger.info("→ Registering UC-6.3...")
    register_uc_6_3_callbacks(app, plot_service)
    logger.info("[OK] UC-6.3 callbacks registered (Chemical Hierarchy Treemap)")

    # Register UC-6.4: Overview of Enzymatic Activity and Substrate Scope
    logger.info("→ Registering UC-6.4...")
    register_uc_6_4_callbacks(app, plot_service)
    logger.info("[OK] UC-6.4 callbacks registered (Enzymatic Activity Treemap)")

    # Register UC-6.5: Chemical-Enzymatic Landscape by Substrate Scope
    logger.info("→ Registering UC-6.5...")
    register_uc_6_5_callbacks(app, plot_service)
    logger.info("[OK] UC-6.5 callbacks registered (Chemo-Enzymatic Landscape)")

    logger.info("=" * 60)
    logger.info("[OK] ALL MODULE 6 CALLBACKS REGISTERED SUCCESSFULLY")
    logger.info("=" * 60)
