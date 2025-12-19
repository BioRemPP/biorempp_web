"""
Module 5 Callbacks - Interaction Networks and Similarity Analysis.

This module registers callback handlers for Module 5 functionality,
including chord diagrams and network visualizations.

Functions
---------
register_module5_callbacks
    Register all Module 5 callbacks with Dash app.

Notes
-----
- Refer to official documentation for supported use case details
- Uses ChordStrategy for network visualizations
"""

import logging

from src.presentation.callbacks.module5 import (
    register_uc_5_1_callbacks,
    register_uc_5_2_callbacks,
    register_uc_5_3_callbacks,
    register_uc_5_4_callbacks,
    register_uc_5_5_callbacks,
    register_uc_5_6_callbacks,
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.propagate = False
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter("[%(levelname)s] %(name)s: %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)


def register_module5_callbacks(app, plot_service) -> None:
    """
    Register all Module 5 callbacks with Dash app.

    Parameters
    ----------
    app : Dash
        Dash application instance.
    plot_service : PlotService
        Singleton PlotService instance (shared across all callbacks).

    Notes
    -----
    - Registers callback handlers for Module 5 use cases
    - Refer to official documentation for supported use case details
    """
    logger.info("=" * 60)
    logger.info("REGISTERING MODULE 5 CALLBACKS...")
    logger.info("=" * 60)

    # Register UC-5.1: Sample - Compound Class Interaction Strength
    logger.info("-> Registering UC-5.1...")
    register_uc_5_1_callbacks(app, plot_service)
    logger.info("UC-5.1 callbacks registered (Chord Diagram)")

    # Register UC-5.2: Sample Similarity Based on Shared Chemical Profiles
    logger.info("-> Registering UC-5.2...")
    register_uc_5_2_callbacks(app, plot_service)
    logger.info("UC-5.2 callbacks registered (Chord Diagram - Pairwise Mode)")

    # Register UC-5.3: Regulatory Relevance of Samples
    logger.info("-> Registering UC-5.3...")
    register_uc_5_3_callbacks(app, plot_service)
    logger.info("UC-5.3 callbacks registered (Chord Diagram - Dropdown Trigger)")

    # Register UC-5.4: Gene-Compound Interaction Network
    logger.info("-> Registering UC-5.4...")
    register_uc_5_4_callbacks(app, plot_service)
    logger.info("UC-5.4 callbacks registered (Network Diagram - Accordion Trigger)")

    # Register UC-5.5: Gene-Gene Functional Interaction Network
    logger.info("-> Registering UC-5.5...")
    register_uc_5_5_callbacks(app, plot_service)
    logger.info("UC-5.5 callbacks registered (Similarity Network - Accordion Trigger)")

    # Register UC-5.6: Compound-Compound Functional Similarity Network
    logger.info("-> Registering UC-5.6...")
    register_uc_5_6_callbacks(app, plot_service)
    logger.info("UC-5.6 callbacks registered (Similarity Network - Accordion Trigger)")

    logger.info("=" * 60)
    logger.info("ALL MODULE 5 CALLBACKS REGISTERED SUCCESSFULLY")
    logger.info("=" * 60)
