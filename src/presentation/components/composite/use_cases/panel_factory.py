"""
Use Case Panel Factory - Centralized Panel Creation.

This module provides the factory function for creating use case panels
from YAML configurations using the Registry Pattern.

Design Pattern
--------------
Factory Method Pattern: Single creation point with polymorphic behavior
determined by configuration rather than code duplication.

Author: BioRemPP Development Team
Date: 2025-12-04
"""

from typing import Optional

from dash import html

from src.presentation.components.base.use_case_panel import (
    create_use_case_panel,
    load_use_case_config,
)
from src.presentation.components.composite.use_cases.panel_registry import (
    get_available_panels,
    get_panel_config_path,
)
from src.shared.logging import get_logger

logger = get_logger(__name__)


def create_panel_by_id(
    use_case_id: str, fallback_message: Optional[str] = None
) -> html.Div:
    """
    Create use case panel by ID using centralized registry.

    This factory function replaces 55 individual wrapper functions,
    providing centralized error handling, logging, and validation.

    Parameters
    ----------
    use_case_id : str
        Use case identifier (e.g., 'uc-2-1', 'uc-5-3')
    fallback_message : Optional[str], optional
        Custom error message if panel creation fails.
        If None, generic error message is used.

    Returns
    -------
    html.Div
        Informative collapsible panel component

    Raises
    ------
    KeyError
        If use_case_id is not registered
    FileNotFoundError
        If YAML configuration file is missing
    ValueError
        If YAML configuration is malformed

    Examples
    --------
    >>> # Replace old pattern:
    >>> # from src.presentation.components.composite.use_cases import (
    >>> #     create_uc_2_1_panel
    >>> # )
    >>> # panel = create_uc_2_1_panel()
    >>>
    >>> # New pattern:
    >>> from src.presentation.components.composite.use_cases import (
    ...     create_panel_by_id
    ... )
    >>> panel = create_panel_by_id('uc-2-1')

    >>> # With custom error handling:
    >>> panel = create_panel_by_id(
    ...     'uc-2-1',
    ...     fallback_message="Unable to load functional richness panel"
    ... )

    Notes
    -----
    - Logs panel creation for debugging and auditing
    - Validates use_case_id against registry before loading
    - Provides detailed error messages with available panels list
    - Maintains backward compatibility with existing panel structure

    See Also
    --------
    panel_registry.PANEL_REGISTRY : Complete list of registered panels
    presentation.components.base.use_case_panel.create_use_case_panel :
        Base factory
    """
    try:
        # Validate and get config path
        config_path = get_panel_config_path(use_case_id)

        logger.debug(
            "Creating panel",
            extra={
                "use_case_id": use_case_id,
                "config_path": str(config_path),
            },
        )

        # Load configuration
        config = load_use_case_config(str(config_path))

        # Validate required fields
        if "use_case_id" not in config:
            logger.warning(
                "Missing use_case_id in YAML config",
                extra={"config_path": str(config_path)},
            )
            config["use_case_id"] = use_case_id

        # Create panel
        panel = create_use_case_panel(**config)

        logger.info(f"Panel '{use_case_id}' created successfully")

        return panel

    except KeyError:
        # Panel not registered
        available = get_available_panels()
        error_msg = (
            f"Panel '{use_case_id}' not found. "
            f"Available: {', '.join(available[:5])}..."
            if len(available) > 5
            else f"Available: {', '.join(available)}"
        )
        logger.error(
            "Panel not found in registry",
            extra={
                "use_case_id": use_case_id,
                "available_count": len(available),
            },
            exc_info=True,
        )

        # Return error panel
        return _create_error_panel(use_case_id, fallback_message or error_msg)

    except FileNotFoundError:
        # YAML config missing
        logger.error(
            "Panel configuration file not found",
            extra={
                "use_case_id": use_case_id,
                "config_path": str(config_path),
            },
            exc_info=True,
        )

        return _create_error_panel(
            use_case_id,
            fallback_message or (f"Configuration file missing: {config_path.name}"),
        )

    except Exception as e:
        # Unexpected error
        logger.error(
            "Unexpected error creating panel",
            extra={
                "use_case_id": use_case_id,
                "error_type": type(e).__name__,
            },
            exc_info=True,
        )

        return _create_error_panel(
            use_case_id, fallback_message or f"Error loading panel: {str(e)}"
        )


def _create_error_panel(use_case_id: str, error_message: str) -> html.Div:
    """
    Create fallback error panel when main panel creation fails.

    Parameters
    ----------
    use_case_id : str
        Use case identifier for error context
    error_message : str
        Human-readable error description

    Returns
    -------
    html.Div
        Error panel with diagnostic information
    """
    import dash_bootstrap_components as dbc

    return html.Div(
        [
            dbc.Alert(
                [
                    html.H5(
                        [
                            html.I(className="fas fa-exclamation-triangle me-2"),
                            f"Panel Error: {use_case_id}",
                        ],
                        className="alert-heading",
                    ),
                    html.P(error_message, className="mb-0"),
                ],
                color="danger",
                className="mb-3",
            )
        ],
        id=f"{use_case_id}-error-panel",
    )


def create_panels_batch(use_case_ids: list[str]) -> dict[str, html.Div]:
    """
    Create multiple panels in batch for layout composition.

    Parameters
    ----------
    use_case_ids : list[str]
        List of use case identifiers

    Returns
    -------
    dict[str, html.Div]
        Mapping of use_case_id to panel component

    Examples
    --------
    >>> panels = create_panels_batch(['uc-2-1', 'uc-2-2', 'uc-2-3'])
    >>> layout = html.Div([
    ...     panels['uc-2-1'], panels['uc-2-2'], panels['uc-2-3']
    ... ])

    Notes
    -----
    Useful for creating module-level layouts with multiple panels.
    Failed panels return error components without stopping batch creation.
    """
    panels = {}

    for uc_id in use_case_ids:
        panels[uc_id] = create_panel_by_id(uc_id)

    logger.info(
        "Batch panel creation completed",
        extra={
            "total_panels": len(use_case_ids),
            "use_case_ids": use_case_ids,
        },
    )

    return panels
