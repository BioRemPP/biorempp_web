"""
Upload Component - Atomic UI Component.

Creates drag-and-drop upload interface for dataset files.

Functions
---------
create_upload
        Create upload component with drag-drop styling

Notes
-----
- Atomic UI component (presentation only).
- Accepts any file in the browser; server-side validation enforces
    required format and size limits.
- Max size (server-side): 10 MB by default (configured centrally).
- Styled with dashed border for drag-and-drop affordance.
"""

from dash import dcc, html


def create_upload(
    component_id: str = "upload-data", max_size_mb: int = 10, multiple: bool = False
) -> html.Div:
    """
    Create file upload component.

    Parameters
    ----------
    component_id : str, optional
        ID for the upload component, by default "upload-data"
    max_size_mb : int, optional
        Maximum file size in MB, by default 10
    multiple : bool, optional
        Allow multiple file upload, by default False

    Returns
    -------
    html.Div
        Upload component with drag-drop interface

    Examples
    --------
    >>> upload = create_upload()
    >>> upload = create_upload("my-upload", max_size_mb=20, multiple=True)

        Notes
        -----
        - UI component only: server-side performs all validations
            (size, encoding, structure, sample/KO limits).
        - Drag and drop or click to browse
        - Visual feedback on hover
        - Parameter ``max_size_mb`` is retained for documentation
            and display purposes; the limit is enforced by the server.
    """
    # client-side size enforcement removed; server-side validates instead

    upload_style = {
        "width": "100%",
        "height": "120px",
        "lineHeight": "120px",
        "borderWidth": "2px",
        "borderStyle": "dashed",
        "borderColor": "#28a745",
        "borderRadius": "8px",
        "textAlign": "center",
        "backgroundColor": "#f8f9fa",
        "cursor": "pointer",
        "transition": "all 0.3s ease",
    }

    upload_component = dcc.Upload(
        id=component_id,
        children=html.Div(
            [
                html.I(className="fas fa-cloud-upload-alt fa-2x text-success mb-2"),
                html.Div(
                    [
                        "Drag and Drop or ",
                        html.A(
                            "Select Files", className="text-success font-weight-bold"
                        ),
                    ]
                ),
                html.Div(
                    [
                        "Required format: plain text ",
                        html.Span(
                            "Samples must start with '>' and KO IDs on next lines.",
                            className="d-block",
                        ),
                    ],
                    className="text-muted",
                    style={"fontSize": "0.85rem", "lineHeight": "1.2"},
                ),
                html.Div(
                    [
                        "Maximum limits: 100 samples or 500,000 KO numbers",
                        #                   html.Span("500,000 KO numbers", className="d-block")
                    ],
                    className="text-muted",
                    style={"fontSize": "0.85rem", "lineHeight": "1.2"},
                ),
            ],
            style={"lineHeight": "1.5"},
        ),
        style=upload_style,
        multiple=multiple,
    )

    return html.Div(
        [
            upload_component,
            html.Div(
                id=f"{component_id}-filename",
                className="mt-2 text-center text-muted",
                style={"fontSize": "0.9rem"},
            ),
        ]
    )
