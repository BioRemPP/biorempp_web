"""
Global workflow modal callbacks for /results page.
"""

import logging
from typing import Any

import dash_bootstrap_components as dbc
from dash import ALL, Input, Output, State, ctx, html, no_update
from dash.exceptions import PreventUpdate

from src.presentation.pages.methods.methods_service import get_methods_service
from src.presentation.pages.methods.workflow_modal import (
    _build_workflow_body_children,
    _build_workflow_title_children,
)
from src.presentation.routing import strip_base_path


logger = logging.getLogger(__name__)


def _is_results_path(pathname: str | None) -> bool:
    """Return True when pathname resolves to /results route."""
    return strip_base_path(pathname or "") == "/results"


def resolve_results_workflow_modal_update(
    trigger: Any,
    trigger_value: int | None,
    close_n_clicks: int | None,
    pathname: str | None,
):
    """Resolve workflow modal state update from current trigger context."""
    if not trigger:
        raise PreventUpdate

    if trigger == "results-workflow-modal-close":
        if not close_n_clicks:
            raise PreventUpdate
        return False, no_update, no_update

    if not isinstance(trigger, dict):
        raise PreventUpdate

    if trigger.get("type") != "results-methods-link":
        raise PreventUpdate

    # Ignore callback executions caused by component mount/hydration where n_clicks is
    # still 0/None (prevents modal auto-open on first /results render).
    if not trigger_value:
        raise PreventUpdate

    if not _is_results_path(pathname):
        raise PreventUpdate

    uc_id = str(trigger.get("index", "")).strip()
    if not uc_id:
        raise PreventUpdate

    service = get_methods_service()
    workflow = service.get_workflow(uc_id)

    if not isinstance(workflow, dict):
        logger.warning("Workflow not found for UC", extra={"uc_id": uc_id})
        return (
            True,
            html.Div(
                [
                    html.Strong(f"{uc_id}: ", className="text-primary"),
                    html.Span("Workflow unavailable"),
                ]
            ),
            dbc.Alert(
                "Methods workflow is not available for this use case yet.",
                color="warning",
                className="mb-0",
            ),
        )

    return (
        True,
        _build_workflow_title_children(workflow),
        _build_workflow_body_children(workflow),
    )


def register_results_workflow_modal_callbacks(app) -> None:
    """Register global workflow modal callback used by all UC Methods buttons."""

    @app.callback(
        [
            Output("results-workflow-modal", "is_open"),
            Output("results-workflow-modal-title", "children"),
            Output("results-workflow-modal-body", "children"),
        ],
        [
            Input({"type": "results-methods-link", "index": ALL}, "n_clicks"),
            Input("results-workflow-modal-close", "n_clicks"),
        ],
        State("url", "pathname"),
        prevent_initial_call=True,
    )
    def open_results_workflow_modal(_, close_n_clicks, pathname):
        """
        Open/close global workflow modal for UC Methods actions on /results.

        Parameters
        ----------
        _ : list[int | None]
            Click counts from all UC Methods buttons in /results layouts.
        close_n_clicks : int | None
            Close button clicks from global modal footer.
        pathname : str | None
            Current URL pathname.
        """
        return resolve_results_workflow_modal_update(
            trigger=ctx.triggered_id,
            trigger_value=(ctx.triggered[0]["value"] if ctx.triggered else None),
            close_n_clicks=close_n_clicks,
            pathname=pathname,
        )
