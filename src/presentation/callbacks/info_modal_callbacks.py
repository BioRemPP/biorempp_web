"""
Info Modal Callbacks - BioRemPP v1.0
====================================

Callbacks for modal interactions (More Info, Sample Data, and Publications).

Functions
---------
register_info_modal_callbacks
    Register all modal-related callbacks with the Dash app

Notes
-----
- Toggle modal visibility via button/card click
- Modals can be closed via X button or clicking outside (backdrop)
- Handles Info Modal, Sample Data Modal, and Publications Modal
- Follows the same pattern as navigation_callbacks.py
"""

import logging
import uuid

from dash import Input, Output, State, ctx, no_update

logger = logging.getLogger(__name__)
logger.propagate = False  # Prevent duplicate logs from parent loggers

# Global flag to prevent duplicate callback registration
_info_modal_callbacks_registered = False
_callback_instance_id = str(uuid.uuid4())[:8]


def register_info_modal_callbacks(app):
    """
    Register info modal callbacks with Dash app.

    Parameters
    ----------
    app : Dash
        Dash application instance

    Notes
    -----
    Registered Callbacks:
    1. Toggle modal (open button, close button, backdrop click)

    Behavior:
    - Modal opens when "More Info" button is clicked
    - Modal closes when X button is clicked or when clicking outside
    - Modal is extra-large and vertically centered

    See Also
    --------
    create_info_modal : Modal component
    create_intro_card : Intro card with More Info button
    """
    global _info_modal_callbacks_registered

    # Prevent duplicate registration
    if _info_modal_callbacks_registered:
        logger.warning(
            "[INFO_MODAL] Callbacks already registered, skipping duplicate registration"
        )
        return

    logger.info("[INFO_MODAL] Registering info modal callbacks...")

    # ========================================
    # Callback: Toggle Modal Open/Close
    # ========================================
    @app.callback(
        Output("info-modal", "is_open"),
        [
            Input("info-modal-open-button", "n_clicks"),
            Input("info-modal-close-button", "n_clicks"),
        ],
        State("info-modal", "is_open"),
        prevent_initial_call=True,
    )
    def toggle_info_modal(open_clicks, close_clicks, is_open):
        """
        Toggle info modal open/close state.

        Parameters
        ----------
        open_clicks : int
            Number of open button clicks
        close_clicks : int
            Number of close button clicks
        is_open : bool
            Current modal state

        Returns
        -------
        bool
            New modal state (toggled based on which button was clicked)

        Notes
        -----
        - Uses ctx.triggered_id to determine which button was clicked
        - Open button opens the modal
        - Close button closes the modal
        - Backdrop click automatically closes (handled by dbc.Modal backdrop=True)
        """
        logger.info("=" * 80)
        logger.info(f"[INFO_MODAL-{_callback_instance_id}] TOGGLE_INFO_MODAL CALLED")
        logger.info(
            f"[INFO_MODAL-{_callback_instance_id}]   Input open_clicks: {open_clicks}"
        )
        logger.info(
            f"[INFO_MODAL-{_callback_instance_id}]   Input close_clicks: {close_clicks}"
        )
        logger.info(f"[INFO_MODAL-{_callback_instance_id}]   State is_open: {is_open}")
        logger.info(
            f"[INFO_MODAL-{_callback_instance_id}]   ctx.triggered: {ctx.triggered}"
        )
        logger.info(
            f"[INFO_MODAL-{_callback_instance_id}]   ctx.triggered_id: {ctx.triggered_id}"
        )

        if not ctx.triggered_id:
            logger.warning(
                f"[INFO_MODAL-{_callback_instance_id}] No triggered_id, returning no_update"
            )
            logger.info("=" * 80)
            return no_update

        # Determine action based on which button was clicked
        if ctx.triggered_id == "info-modal-open-button":
            new_state = True
            logger.info(
                f"[INFO_MODAL-{_callback_instance_id}] OPEN BUTTON CLICKED: "
                f"Setting modal to OPEN (clicks={open_clicks})"
            )
        elif ctx.triggered_id == "info-modal-close-button":
            new_state = False
            logger.info(
                f"[INFO_MODAL-{_callback_instance_id}] CLOSE BUTTON CLICKED: "
                f"Setting modal to CLOSED (clicks={close_clicks})"
            )
        else:
            logger.warning(
                f"[INFO_MODAL-{_callback_instance_id}] Unknown trigger: {ctx.triggered_id}, "
                f"returning current state"
            )
            new_state = is_open

        logger.info(f"[INFO_MODAL-{_callback_instance_id}] RETURNING: {new_state}")
        logger.info("=" * 80)
        return new_state

    # ========================================
    # Callback: Toggle Sample Data Modal Open/Close
    # ========================================
    @app.callback(
        Output("sample-data-modal", "is_open"),
        [
            Input("sample-data-card", "n_clicks"),
            Input("sample-data-modal-close-button", "n_clicks"),
        ],
        State("sample-data-modal", "is_open"),
        prevent_initial_call=True,
    )
    def toggle_sample_data_modal(card_clicks, close_clicks, is_open):
        """
        Toggle sample data modal open/close state.

        Parameters
        ----------
        card_clicks : int
            Number of card clicks
        close_clicks : int
            Number of close button clicks
        is_open : bool
            Current modal state

        Returns
        -------
        bool
            New modal state (toggled based on which element was clicked)

        Notes
        -----
        - Uses ctx.triggered_id to determine which element was clicked
        - Card click opens the modal
        - Close button closes the modal
        - Backdrop click automatically closes (handled by dbc.Modal backdrop=True)
        """
        logger.info("=" * 80)
        logger.info(
            f"[SAMPLE_DATA_MODAL-{_callback_instance_id}] TOGGLE_SAMPLE_DATA_MODAL CALLED"
        )
        logger.info(
            f"[SAMPLE_DATA_MODAL-{_callback_instance_id}]   Input card_clicks: {card_clicks}"
        )
        logger.info(
            f"[SAMPLE_DATA_MODAL-{_callback_instance_id}]   Input close_clicks: {close_clicks}"
        )
        logger.info(
            f"[SAMPLE_DATA_MODAL-{_callback_instance_id}]   State is_open: {is_open}"
        )
        logger.info(
            f"[SAMPLE_DATA_MODAL-{_callback_instance_id}]   ctx.triggered: {ctx.triggered}"
        )
        logger.info(
            f"[SAMPLE_DATA_MODAL-{_callback_instance_id}]   ctx.triggered_id: {ctx.triggered_id}"
        )

        if not ctx.triggered_id:
            logger.warning(
                f"[SAMPLE_DATA_MODAL-{_callback_instance_id}] No triggered_id, returning no_update"
            )
            logger.info("=" * 80)
            return no_update

        # Determine action based on which element was clicked
        if ctx.triggered_id == "sample-data-card":
            new_state = True
            logger.info(
                f"[SAMPLE_DATA_MODAL-{_callback_instance_id}] CARD CLICKED: "
                f"Setting modal to OPEN (clicks={card_clicks})"
            )
        elif ctx.triggered_id == "sample-data-modal-close-button":
            new_state = False
            logger.info(
                f"[SAMPLE_DATA_MODAL-{_callback_instance_id}] CLOSE BUTTON CLICKED: "
                f"Setting modal to CLOSED (clicks={close_clicks})"
            )
        else:
            logger.warning(
                f"[SAMPLE_DATA_MODAL-{_callback_instance_id}] Unknown trigger: {ctx.triggered_id}, "
                f"returning current state"
            )
            new_state = is_open

        logger.info(
            f"[SAMPLE_DATA_MODAL-{_callback_instance_id}] RETURNING: {new_state}"
        )
        logger.info("=" * 80)
        return new_state

    # ========================================
    # Callback: Toggle Publications Modal Open/Close
    # ========================================
    @app.callback(
        Output("publications-modal", "is_open"),
        [
            Input("publications-card", "n_clicks"),
            Input("publications-modal-close-button", "n_clicks"),
        ],
        State("publications-modal", "is_open"),
        prevent_initial_call=True,
    )
    def toggle_publications_modal(card_clicks, close_clicks, is_open):
        """
        Toggle publications modal open/close state.

        Parameters
        ----------
        card_clicks : int
            Number of card clicks
        close_clicks : int
            Number of close button clicks
        is_open : bool
            Current modal state

        Returns
        -------
        bool
            New modal state (toggled based on which element was clicked)

        Notes
        -----
        - Uses ctx.triggered_id to determine which element was clicked
        - Card click opens the modal
        - Close button closes the modal
        - Backdrop click automatically closes (handled by dbc.Modal backdrop=True)
        """
        logger.info("=" * 80)
        logger.info(
            f"[PUBLICATIONS_MODAL-{_callback_instance_id}] TOGGLE_PUBLICATIONS_MODAL CALLED"
        )
        logger.info(
            f"[PUBLICATIONS_MODAL-{_callback_instance_id}]   Input card_clicks: {card_clicks}"
        )
        logger.info(
            f"[PUBLICATIONS_MODAL-{_callback_instance_id}]   Input close_clicks: {close_clicks}"
        )
        logger.info(
            f"[PUBLICATIONS_MODAL-{_callback_instance_id}]   State is_open: {is_open}"
        )
        logger.info(
            f"[PUBLICATIONS_MODAL-{_callback_instance_id}]   ctx.triggered: {ctx.triggered}"
        )
        logger.info(
            f"[PUBLICATIONS_MODAL-{_callback_instance_id}]   ctx.triggered_id: {ctx.triggered_id}"
        )

        if not ctx.triggered_id:
            logger.warning(
                f"[PUBLICATIONS_MODAL-{_callback_instance_id}] No triggered_id, returning no_update"
            )
            logger.info("=" * 80)
            return no_update

        # Determine action based on which element was clicked
        if ctx.triggered_id == "publications-card":
            new_state = True
            logger.info(
                f"[PUBLICATIONS_MODAL-{_callback_instance_id}] CARD CLICKED: "
                f"Setting modal to OPEN (clicks={card_clicks})"
            )
        elif ctx.triggered_id == "publications-modal-close-button":
            new_state = False
            logger.info(
                f"[PUBLICATIONS_MODAL-{_callback_instance_id}] CLOSE BUTTON CLICKED: "
                f"Setting modal to CLOSED (clicks={close_clicks})"
            )
        else:
            logger.warning(
                f"[PUBLICATIONS_MODAL-{_callback_instance_id}] Unknown trigger: {ctx.triggered_id}, "
                f"returning current state"
            )
            new_state = is_open

        logger.info(
            f"[PUBLICATIONS_MODAL-{_callback_instance_id}] RETURNING: {new_state}"
        )
        logger.info("=" * 80)
        return new_state

    # Mark callbacks as registered
    _info_modal_callbacks_registered = True
    logger.info("[INFO_MODAL] [OK] Info modal callbacks registered successfully")
    logger.info(f"[INFO_MODAL] [OK] Callback IDs registered:")
    logger.info(
        f"[INFO_MODAL]     - toggle_info_modal: Inputs=['info-modal-open-button', 'info-modal-close-button'], Output='info-modal.is_open'"
    )
    logger.info(
        f"[INFO_MODAL]     - toggle_sample_data_modal: Inputs=['sample-data-card', 'sample-data-modal-close-button'], Output='sample-data-modal.is_open'"
    )
    logger.info(
        f"[INFO_MODAL]     - toggle_publications_modal: Inputs=['publications-card', 'publications-modal-close-button'], Output='publications-modal.is_open'"
    )
