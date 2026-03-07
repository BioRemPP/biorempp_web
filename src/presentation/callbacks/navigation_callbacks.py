"""
Navigation Callbacks - BioRemPP v1.0
====================================

Callbacks for navigation system interaction and scroll behavior.

Functions
---------
register_navigation_callbacks
    Register all navigation-related callbacks with the Dash app

Notes
-----
- Toggle offcanvas visibility
- Navigate to target sections via URL hash
- Offcanvas stays open until manually closed
- Button visibility controlled via CSS
- Smooth scroll behavior via CSS
"""

import logging
import uuid

from dash import Input, Output, State, callback, ctx, no_update
from src.presentation.services.results_navigation import (
    normalize_target_hash,
    resolve_target_module,
)

logger = logging.getLogger(__name__)
logger.propagate = False  # Prevent duplicate logs from parent loggers

# Global flag to prevent duplicate callback registration
_navigation_callbacks_registered = False
_callback_instance_id = str(uuid.uuid4())[:8]


def register_navigation_callbacks(app):
    """
    Register navigation callbacks with Dash app.

    Parameters
    ----------
    app : Dash
        Dash application instance

    Notes
    -----
    Registered Callbacks:
    1. Toggle offcanvas (button click)
    2. Navigate to section (list item clicks)

    Navigation Map:
    - Database sections: biorempp, hadeg, toxcsm, kegg
    - Module sections: module1-8
    - Use cases: uc-2-1 through uc-2-5

    Behavior:
    - Offcanvas backdrop='static' prevents auto-close
    - User must click X or press ESC to close
    - Button hidden via CSS when offcanvas is open

    See Also
    --------
    create_navigation_button : Button component
    create_navigation_offcanvas : Offcanvas component
    """
    global _navigation_callbacks_registered

    # Prevent duplicate registration
    if _navigation_callbacks_registered:
        logger.warning(
            "[NAVIGATION] Callbacks already registered, skipping duplicate registration"
        )
        return

    logger.info("[NAVIGATION] Registering navigation callbacks...")

    # ========================================
    # Callback 1: Toggle Offcanvas and Control Button Visibility
    # ========================================
    @app.callback(
        [
            Output("navigation-offcanvas", "is_open"),
            Output("navigation-button-container", "style"),
        ],
        [
            Input("nav-toggle-button", "n_clicks"),
            Input("suggestions-offcanvas", "is_open"),
            Input(
                "navigation-offcanvas", "is_open"
            ),  # Listen to offcanvas state changes
        ],
        prevent_initial_call=True,
    )
    def toggle_navigation_and_control_visibility(
        nav_clicks, suggestions_is_open, nav_is_open
    ):
        """
        Toggle navigation offcanvas and control button visibility.

        Button is hidden when:
        - Navigation offcanvas is open, OR
        - Suggestions offcanvas is open

        Parameters
        ----------
        nav_clicks : int
            Number of navigate button clicks
        suggestions_is_open : bool
            Whether suggestions offcanvas is open
        nav_is_open : bool
            Current navigation offcanvas state

        Returns
        -------
        tuple
            (new_nav_is_open, button_style)
        """
        from dash import ctx, no_update

        logger.info("=" * 80)
        logger.info("[NAV-VISIBILITY] Callback triggered")
        logger.info(f"[NAV-VISIBILITY] triggered_id: {ctx.triggered_id}")
        logger.info(f"[NAV-VISIBILITY] nav_clicks: {nav_clicks}")
        logger.info(f"[NAV-VISIBILITY] suggestions_is_open: {suggestions_is_open}")
        logger.info(f"[NAV-VISIBILITY] nav_is_open: {nav_is_open}")

        # Default button style (visible)
        button_visible = {
            "position": "fixed",
            "bottom": "80px",
            "right": "20px",
            "zIndex": "999",
            "display": "block",
        }

        button_hidden = {
            "position": "fixed",
            "bottom": "80px",
            "right": "20px",
            "zIndex": "999",
            "display": "none",
        }

        # Check which input triggered the callback
        if ctx.triggered_id == "nav-toggle-button":
            # Navigate button was clicked - toggle offcanvas
            new_nav_is_open = not nav_is_open
            logger.info(
                f"[NAV-VISIBILITY] Navigate button clicked, toggling: {nav_is_open} -> {new_nav_is_open}"
            )

            # Hide button if either offcanvas is open
            if new_nav_is_open or suggestions_is_open:
                logger.info(
                    f"[NAV-VISIBILITY] Hiding button (nav_open={new_nav_is_open}, sug_open={suggestions_is_open})"
                )
                logger.info("=" * 80)
                return new_nav_is_open, button_hidden
            else:
                logger.info(f"[NAV-VISIBILITY] Showing button (both closed)")
                logger.info("=" * 80)
                return new_nav_is_open, button_visible

        elif ctx.triggered_id == "navigation-offcanvas":
            # Navigation offcanvas state changed (e.g., closed via X button)
            logger.info(
                f"[NAV-VISIBILITY] Navigation offcanvas changed to: {nav_is_open}"
            )
            # Don't change nav offcanvas state (no_update), just update button visibility
            if nav_is_open or suggestions_is_open:
                logger.info(
                    f"[NAV-VISIBILITY] Hiding button (nav_open={nav_is_open}, sug_open={suggestions_is_open})"
                )
                logger.info("=" * 80)
                return no_update, button_hidden
            else:
                logger.info(f"[NAV-VISIBILITY] Showing button (both closed)")
                logger.info("=" * 80)
                return no_update, button_visible

        elif ctx.triggered_id == "suggestions-offcanvas":
            # Suggestions offcanvas state changed
            logger.info(
                f"[NAV-VISIBILITY] Suggestions offcanvas changed to: {suggestions_is_open}"
            )
            # Don't change nav offcanvas state (no_update), just update button visibility
            if nav_is_open or suggestions_is_open:
                logger.info(
                    f"[NAV-VISIBILITY] Hiding button (nav_open={nav_is_open}, sug_open={suggestions_is_open})"
                )
                logger.info("=" * 80)
                return no_update, button_hidden
            else:
                logger.info(f"[NAV-VISIBILITY] Showing button (both closed)")
                logger.info("=" * 80)
                return no_update, button_visible

        # Default: both closed, button visible
        logger.info("[NAV-VISIBILITY] Default case - showing button")
        logger.info("=" * 80)
        return False, button_visible

    # ========================================
    # Callback 2: Sync hash target with lazy module selector
    # ========================================
    @app.callback(
        [
            Output("results-module-selector", "value"),
            Output("navigation-offcanvas", "is_open", allow_duplicate=True),
            Output("suggestions-offcanvas", "is_open", allow_duplicate=True),
        ],
        Input("url", "hash"),
        State("results-module-selector", "value"),
        prevent_initial_call=True,
    )
    def sync_navigation_target(url_hash, current_module):
        """
        Sync URL hash target with lazy module selector and panel visibility.

        Parameters
        ----------
        url_hash : str
            Current URL hash target.
        current_module : int | None
            Current selector value for active results module.

        Returns
        -------
        tuple
            (
                results_module_selector_value_or_no_update,
                navigation_offcanvas_is_open,
                suggestions_offcanvas_is_open,
            )

        Notes
        -----
        - Supports canonical and legacy UC hashes:
          #uc-x-y-card and #uc-x-y-info-panel
        - Closes both offcanvas panels after a valid navigation target
        - Only updates selector when target resolves to module 1..8
        """
        normalized_hash = normalize_target_hash(url_hash)
        if not normalized_hash:
            return no_update, no_update, no_update

        target_module = resolve_target_module(normalized_hash)
        if target_module is None:
            return no_update, False, False

        try:
            current_module_int = int(current_module) if current_module is not None else None
        except (TypeError, ValueError):
            current_module_int = None

        if current_module_int == target_module:
            return no_update, False, False

        return str(target_module), False, False

    # Mark callbacks as registered
    _navigation_callbacks_registered = True
    logger.info("[NAVIGATION] [OK] Navigation callbacks registered successfully")
    logger.info(f"[NAVIGATION] [OK] Callback IDs registered:")
    logger.info(
        f"[NAVIGATION]     - toggle_navigation: Input='nav-toggle-button', Output='navigation-offcanvas.is_open'"
    )
    logger.info(
        "[NAVIGATION]     - sync_navigation_target: Input='url.hash', Output='results-module-selector.value'"
    )
