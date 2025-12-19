import dash_bootstrap_components as dbc
from dash import html

from ..base import create_button, create_upload


def create_upload_panel() -> dbc.Card:
    example_download_href = "/data/example_dataset.txt"

    instructions = html.Div(
        [
            # Main instruction with clean formatting
            html.P(
                [
                    "Select a file or drag and drop your dataset in the ",
                    html.Span(
                        "required format",
                        id="short-example-popover-target",
                        className="text-primary fw-semibold",
                        style={
                            "cursor": "help",
                            "borderBottom": "2px dotted #0d6efd",
                            "paddingBottom": "2px",
                        },
                    ),
                    ". You can also load the example dataset using the button below or ",
                    html.A(
                        "download it here",
                        href=example_download_href,
                        download="example_dataset.txt",
                        className="text-success fw-semibold",
                        style={
                            "textDecoration": "none",
                            "borderBottom": "2px solid #198754",
                        },
                    ),
                    ".",
                ],
                className="mb-3 text-center text-muted",
                style={
                    "lineHeight": "1.6",
                    "fontSize": "0.95rem",
                    "maxWidth": "700px",
                    "margin": "0 auto",
                },
            ),
            # Popover (hover) for format details
            dbc.Popover(
                [
                    dbc.PopoverHeader(
                        "Input data format",
                        className="text-dark fw-semibold",
                        style={
                            "backgroundColor": "#ffffff",
                            "borderBottom": "1px solid #e9ecef",
                            "textAlign": "center",
                        },
                    ),
                    dbc.PopoverBody(
                        [
                            html.P(
                                "Input file rules:",
                                className="mb-2 text-dark",
                                style={"fontWeight": "600"},
                            ),
                            html.Ul(
                                [
                                    html.Li(
                                        [
                                            "Plain text file (.txt); ",
                                            html.Span("UTF-8 or Latin-1 encoding."),
                                        ]
                                    ),
                                    html.Li(
                                        [
                                            "Each sample starts with '>' ",
                                            html.Span("followed by the sample name, without spaces."),
                                        ]
                                    ),
                                    html.Li(
                                        [
                                            "Following lines: KO IDs in the ",
                                            html.Span("format K00001 (K + 5 digits)."),
                                        ]
                                    ),
                                    html.Li(
                                        [
                                            "Do not leave blank lines ",
                                            html.Span("between samples."),
                                        ]
                                    ),
                                    html.Li(
                                        [
                                            "Limits: up to 100 samples; ",
                                            html.Span("500,000 KOs total."),
                                        ]
                                    ),
                                ],
                                className="mb-2 text-dark",
                                style={
                                    "fontSize": "0.9rem",
                                    "lineHeight": "1.25rem",
                                },
                            ),
                            html.Hr(),
                            html.P(
                                "Example:",
                                className="mb-2 text-dark",
                                style={"fontWeight": "600"},
                            ),
                            html.Pre(
                                """>Sample1
K00031
K00032
K00090
K00042
K00052
>Sample2
K00031
K00032
K00090
K00042
K00052
>Sample3
K00031
K00032
K00090
K00042
K00052""",
                                className="mb-0 text-dark",
                                style={
                                    "fontSize": "0.85rem",
                                    "whiteSpace": "pre-wrap",
                                    "lineHeight": "1.25rem",
                                    "backgroundColor": "#f8f9fa",
                                    "padding": "0.75rem",
                                    "border": "1px solid #e9ecef",
                                    "borderRadius": "0.5rem",
                                },
                            ),
                        ],
                        style={"backgroundColor": "#ffffff"},
                    ),
                ],
                target="short-example-popover-target",
                trigger="hover",
                placement="right",
                body=True,
                style={
                    "maxWidth": "460px",
                    "boxShadow": "0 6px 18px rgba(0,0,0,0.15)",
                    "border": "1px solid #e9ecef",
                    "borderRadius": "0.75rem",
                },
            ),
        ],
        className="px-3 pt-2",
    )

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
            html.P(
                "Don't have data? Click above to load an example dataset.",
                className="text-center text-muted mt-2",
                style={"fontSize": "0.85rem"},
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
            dbc.CardBody(
                [instructions, upload_component, button_row, upload_status, file_info]
            ),
        ],
        className="mb-3",
        id="upload-panel",
    )
