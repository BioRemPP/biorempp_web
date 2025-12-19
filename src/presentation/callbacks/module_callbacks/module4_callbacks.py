"""
Module 4 Callbacks - Functional and Genetic Profiling.

This module registers callback handlers for Module 4 functionality,
including metabolic pathway profiling and genetic architecture analysis.

Functions
---------
register_module4_callbacks
    Register all Module 4 callbacks with Dash app.

Notes
-----
- Refer to official documentation for supported use case details
- Each use case has its own callback module with inline processing

Version: 1.0.0
"""

import logging

from src.presentation.callbacks.module4 import (
    register_uc_4_1_callbacks,
    register_uc_4_2_callbacks,
    register_uc_4_3_callbacks,
    register_uc_4_4_callbacks,
    register_uc_4_5_callbacks,
    register_uc_4_6_callbacks,
    register_uc_4_7_callbacks,
    register_uc_4_8_callbacks,
    register_uc_4_9_callbacks,
    register_uc_4_10_callbacks,
    register_uc_4_11_callbacks,
    register_uc_4_12_callbacks,
    register_uc_4_13_callbacks,
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)  # Ensure DEBUG level
logger.propagate = False  # Prevent duplicate logs from parent loggers
# Add handler if not present
if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("[%(levelname)s] %(name)s: %(message)s"))
    logger.addHandler(handler)


def register_module4_callbacks(app, plot_service) -> None:
    """
    Register all Module 4 callbacks with Dash app.

    Parameters
    ----------
    app : Dash
        Dash application instance.
    plot_service : PlotService
        Singleton PlotService instance (shared across all callbacks).

    Notes
    -----
    - Registers callback handlers for Module 4 use cases
    - Refer to official documentation for supported use case details
    """
    logger.info("=" * 60)
    logger.info("REGISTERING MODULE 4 CALLBACKS...")
    logger.info("=" * 60)

    # Register UC-4.1: Interactive Functional Profiling by Pathway
    logger.info("→ Registering UC-4.1...")
    register_uc_4_1_callbacks(app, plot_service)
    logger.info("[OK] UC-4.1 callbacks registered (Pathway functional profiling)")

    # Register UC-4.2: Interactive Sample Ranking by Pathway
    logger.info("→ Registering UC-4.2...")
    register_uc_4_2_callbacks(app, plot_service)
    logger.info("[OK] UC-4.2 callbacks registered (Sample ranking by pathway richness)")

    # Register UC-4.3: Interactive Sample Comparison by Pathway (Radar)
    logger.info("→ Registering UC-4.3...")
    register_uc_4_3_callbacks(app, plot_service)
    logger.info(
        "[OK] UC-4.3 callbacks registered (Sample comparison by pathway - Radar)"
    )

    # Register UC-4.4: Interactive Functional Fingerprint by Sample (Radar)
    logger.info("→ Registering UC-4.4...")
    register_uc_4_4_callbacks(app, plot_service)
    logger.info(
        "[OK] UC-4.4 callbacks registered (Functional fingerprint by sample - Radar)"
    )

    # Register UC-4.5: Interactive Gene Presence Map by Pathway
    logger.info("→ Registering UC-4.5...")
    register_uc_4_5_callbacks(app, plot_service)
    logger.info("[OK] UC-4.5 callbacks registered (Gene presence map by pathway)")

    # Register UC-4.6: Interactive Functional Potential by Compound
    logger.info("→ Registering UC-4.6...")
    register_uc_4_6_callbacks(app, plot_service)
    logger.info(
        "[OK] UC-4.6 callbacks registered " "(Functional potential by compound)"
    )

    # Register UC-4.9: Interactive Enzymatic Activity Profiling
    logger.info("→ Registering UC-4.9...")
    register_uc_4_9_callbacks(app, plot_service)
    logger.info("[OK] UC-4.9 callbacks registered " "(Enzymatic activity profiling)")

    # Register UC-4.7: Interactive Gene-Compound Association Explorer
    logger.info("→ Registering UC-4.7...")
    register_uc_4_7_callbacks(app, plot_service)
    logger.info(
        "[OK] UC-4.7 callbacks registered " "(Gene-compound association explorer)"
    )

    # Register UC-4.8: Interactive Gene Inventory Explorer
    logger.info("→ Registering UC-4.8...")
    register_uc_4_8_callbacks(app, plot_service)
    logger.info(
        "[OK] UC-4.8 callbacks registered " "(Gene inventory explorer by sample)"
    )

    # Register UC-4.10: Genetic Diversity of Enzymatic Activities
    logger.info("→ Registering UC-4.10...")
    register_uc_4_10_callbacks(app, plot_service)
    logger.info(
        "[OK] UC-4.10 callbacks registered " "(Genetic diversity by enzyme activity)"
    )

    # Register UC-4.11: Global Hierarchical View of Genetic Diversity (HADEG)
    logger.info("→ Registering UC-4.11...")
    register_uc_4_11_callbacks(app, plot_service)
    logger.info(
        "[OK] UC-4.11 callbacks registered "
        "(Global genetic diversity hierarchy - HADEG Sunburst)"
    )

    # Register UC-4.12: Interactive Pathway Relationships by Sample (HADEG)
    logger.info("→ Registering UC-4.12...")
    register_uc_4_12_callbacks(app, plot_service)
    logger.info(
        "[OK] UC-4.12 callbacks registered " "(Pathway relationships by sample - HADEG)"
    )

    # Register UC-4.13: Interactive Genetic Profile by Compound Pathway (HADEG)
    logger.info("→ Registering UC-4.13...")
    register_uc_4_13_callbacks(app, plot_service)
    logger.info(
        "[OK] UC-4.13 callbacks registered "
        "(Genetic profile by compound pathway - HADEG)"
    )

    logger.info("=" * 60)
    logger.info("[OK] ALL MODULE 4 CALLBACKS REGISTERED SUCCESSFULLY")
    logger.info("=" * 60)
