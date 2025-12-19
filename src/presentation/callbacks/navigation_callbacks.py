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
    # Callback 2: Navigate to Target Section (WITHOUT auto-close)
    # ========================================
    @app.callback(
        Output("url", "hash"),
        [
            # Database Tables
            Input("nav-biorempp", "n_clicks"),
            Input("nav-hadeg", "n_clicks"),
            Input("nav-toxcsm", "n_clicks"),
            Input("nav-kegg", "n_clicks"),
            # Module Overviews
            Input("nav-module1", "n_clicks"),
            Input("nav-module2", "n_clicks"),
            Input("nav-module3", "n_clicks"),
            Input("nav-module4", "n_clicks"),
            Input("nav-module5", "n_clicks"),
            Input("nav-module6", "n_clicks"),
            Input("nav-module7", "n_clicks"),
            Input("nav-module8", "n_clicks"),
            # Module 2 Use Cases
            Input("nav-uc-2-1", "n_clicks"),
            Input("nav-uc-2-2", "n_clicks"),
            Input("nav-uc-2-3", "n_clicks"),
            Input("nav-uc-2-4", "n_clicks"),
            Input("nav-uc-2-5", "n_clicks"),
        ],
        prevent_initial_call=True,
    )
    def navigate_to_section(*args):
        """
        Navigate to target section using URL hash.

        Parameters
        ----------
        *args : tuple
            Click counts from all navigation items

        Returns
        -------
        str
            URL hash for target section (e.g., "#module2-section")

        Notes
        -----
        - Uses ctx.triggered_id to identify clicked item
        - Maps navigation IDs to section IDs
        - Triggers browser scroll via hash change
        - Does NOT auto-close offcanvas (manual close only)
        """
        if not ctx.triggered_id:
            logger.debug("[NAVIGATION] No triggered_id, returning no_update")
            return no_update

        logger.info(f"[NAVIGATION] Navigation triggered by: {ctx.triggered_id}")

        # Navigation ID to Section ID mapping
        navigation_map = {
            # Database Tables
            "nav-biorempp": "#biorempp-section",
            "nav-hadeg": "#hadeg-section",
            "nav-toxcsm": "#toxcsm-section",
            "nav-kegg": "#kegg-section",
            # Module Overviews
            "nav-module1": "#module1-section",
            "nav-module2": "#module2-section",
            "nav-module3": "#module3-section",
            "nav-module4": "#module4-section",
            "nav-module5": "#module5-section",
            "nav-module6": "#module6-section",
            "nav-module7": "#module7-section",
            "nav-module8": "#module8-section",
            # Module 2 Use Cases
            "nav-uc-2-1": "#uc-2-1-card",
            "nav-uc-2-2": "#uc-2-2-card",
            "nav-uc-2-3": "#uc-2-3-card",
            "nav-uc-2-4": "#uc-2-4-card",
            "nav-uc-2-5": "#uc-2-5-card",
        }

        target_hash = navigation_map.get(ctx.triggered_id, "")
        if target_hash:
            logger.info(f"[NAVIGATION] Navigating to: {target_hash}")
            return target_hash
        logger.warning(f"[NAVIGATION] No mapping found for: {ctx.triggered_id}")
        return no_update

    # Mark callbacks as registered
    _navigation_callbacks_registered = True
    logger.info("[NAVIGATION] [OK] Navigation callbacks registered successfully")
    logger.info(f"[NAVIGATION] [OK] Callback IDs registered:")
    logger.info(
        f"[NAVIGATION]     - toggle_navigation: Input='nav-toggle-button', Output='navigation-offcanvas.is_open'"
    )
    logger.info(f"[NAVIGATION]     - navigate_to_section: Multiple nav-* inputs")
