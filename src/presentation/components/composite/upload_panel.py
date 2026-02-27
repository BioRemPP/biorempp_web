import dash_bootstrap_components as dbc
from dash import html

from ..base import create_button, create_upload


def create_upload_panel() -> dbc.Card:
    upload_component = create_upload(
        component_id="upload-component", max_size_mb=10, multiple=False
    )

    sample_button = create_button(
        component_id="load-example-btn",
        label="Use Example Data",
        variant="success",
        outline=True,
        icon="fas fa-database",
        size="md",
    )

    button_row = html.Div(
        [
            html.Div(
                sample_button,
                className="d-flex justify-content-center mt-3",
            ),
        ]
    )

    upload_status = html.Div(id="upload-status", className="mt-3")
    file_info = html.Div(id="file-info-display", className="mt-2")

    return dbc.Card(
        [
            dbc.CardHeader(
                [
                    html.I(className="fas fa-upload me-2"),
                    html.Span(
                        "Step 1: Upload Data",
                        className="font-weight-bold",
                    ),
                ],
                className="bg-success text-white",
            ),
            dbc.CardBody([upload_component, button_row, upload_status, file_info]),
        ],
        className="mb-3",
        id="upload-panel",
    )
