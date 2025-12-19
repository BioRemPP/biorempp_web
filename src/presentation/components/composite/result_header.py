"""
Result Header Component - Results Page Summary Header.

Displays processing metadata and match statistics.

Functions
---------
create_result_header
    Create result header with metadata and statistics

Notes
-----
- Shows file info, processing time, match stats
- Displays database merge summary
- Visual badges for statistics
"""

from typing import Any, Dict, Optional

import dash_bootstrap_components as dbc
from dash import html


def create_result_header(result_data: Optional[Dict[str, Any]] = None) -> dbc.Card:
    """
    Create result header component.

    Parameters
    ----------
    result_data : Optional[Dict[str, Any]], optional
        Result metadata from MergedDataDTO or processing summary
        Expected keys: filename, sample_count, ko_count,
        processing_time, matched_kos, total_kos, databases

    Returns
    -------
    dbc.Card
        Header card with metadata and statistics

    Examples
    --------
    >>> # Default (no data)
    >>> header = create_result_header()
    >>>
    >>> # With result data
    >>> data = {
    ...     "filename": "samples.txt",
    ...     "sample_count": 5,
    ...     "ko_count": 150,
    ...     "processing_time": 23.5,
    ...     "matched_kos": 145,
    ...     "total_kos": 150,
    ...     "databases": ["BioRemPP", "HADEG", "ToxCSM", "KEGG"]
    ... }
    >>> header = create_result_header(data)

    Notes
    -----
    - Green header with icon
    - Metadata badges (file, samples, KOs, time)
    - Match statistics with percentage
    - Database merge summary
    """
    if result_data is None:
        result_data = {
            "filename": "No file",
            "sample_count": 0,
            "ko_count": 0,
            "processing_time": 0,
            "matched_kos": 0,
            "total_kos": 0,
            "databases": [],
        }

    filename = result_data.get("filename", "Unknown")
    sample_count = result_data.get("sample_count", 0)
    ko_count = result_data.get("ko_count", 0)
    processing_time = result_data.get("processing_time", 0)
    matched_kos = result_data.get("matched_kos", 0)
    total_kos = result_data.get("total_kos", 0)
    databases = result_data.get("databases", [])

    # Calculate match percentage
    match_pct = (matched_kos / total_kos * 100) if total_kos > 0 else 0

    # Metadata badges
    metadata = html.Div(
        [
            dbc.Badge(
                [html.I(className="fas fa-file me-1"), f"File: {filename}"],
                color="light",
                text_color="dark",
                className="me-2",
            ),
            dbc.Badge(
                [html.I(className="fas fa-flask me-1"), f"Samples: {sample_count}"],
                color="light",
                text_color="dark",
                className="me-2",
            ),
            dbc.Badge(
                [html.I(className="fas fa-dna me-1"), f"KOs: {ko_count}"],
                color="light",
                text_color="dark",
                className="me-2",
            ),
            dbc.Badge(
                [
                    html.I(className="fas fa-clock me-1"),
                    f"Time: {processing_time:.1f}s",
                ],
                color="light",
                text_color="dark",
            ),
        ],
        className="mb-3",
    )

    # Match statistics
    match_stats = html.Div(
        [
            html.Div(
                [
                    html.I(className="fas fa-check-circle text-success me-2"),
                    html.Span(
                        f"Matched {matched_kos}/{total_kos} KOs ({match_pct:.1f}%)",
                        className="text-success font-weight-bold",
                    ),
                ],
                className="mb-2",
            ),
            html.Div(
                [
                    html.I(className="fas fa-database text-success me-2"),
                    html.Span(
                        f"{len(databases)} databases merged: "
                        f"{', '.join(databases)}",
                        className="text-success",
                    ),
                ]
            ),
        ]
    )

    return dbc.Card(
        [
            dbc.CardHeader(
                [
                    html.I(className="fas fa-chart-bar me-2"),
                    html.Span(
                        "BioRemPP Analysis Results", className="font-weight-bold"
                    ),
                ],
                className="bg-success text-white",
            ),
            dbc.CardBody([metadata, html.Hr(), match_stats]),
        ],
        className="mb-4",
    )
