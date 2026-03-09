"""
Use Case Panel Component - Informative Description Panel.

Creates atomic informative panels for use cases with scientific context,
interpretation guidelines, and visual element descriptions.

Functions
---------
create_use_case_panel
    Create informative collapsible panel for a specific use case
load_use_case_config
    Load use case configuration from YAML file

Notes
-----
- Uses Dash Bootstrap Components for consistent styling
- Fully atomic and reusable component
- Configuration loaded from YAML files
- Collapsible panel for better UX and space management

Individual Use Case Panels
--------------------------
Individual panel creation functions have been moved to:
presentation/components/composite/use_cases/

Import pattern:
>>> from src.presentation.components.composite.use_cases import create_uc_2_1_panel

Author: BioRemPP Development Team
Date: 2025-11-17
"""

from pathlib import Path
import json
import os
from copy import deepcopy
from dataclasses import dataclass
from threading import RLock
from typing import Any, Dict, List, Optional

import dash_bootstrap_components as dbc
import yaml
from dash import html

from src.shared.logging import get_logger
from src.shared.metrics import (
    CACHE_ENTRY_SIZE_BYTES,
    CACHE_HIT_RATIO,
    CACHE_OPERATIONS_TOTAL,
    CACHE_SIZE_ITEMS,
)


logger = get_logger(__name__)

_UC_PANEL_CACHE_TYPE = "uc_panel_yaml"
_UC_PANEL_CACHE_ENABLED_ENV = "BIOREMPP_UC_PANEL_CACHE_ENABLED"
_UC_PANEL_CACHE_VALIDATE_MTIME_ENV = "BIOREMPP_UC_PANEL_CACHE_VALIDATE_MTIME"


@dataclass(frozen=True)
class _UseCaseCacheEntry:
    """In-process cache entry for one use case YAML config."""

    mtime_ns: int
    config: Dict[str, Any]


_USE_CASE_CONFIG_CACHE: Dict[str, _UseCaseCacheEntry] = {}
_USE_CASE_CONFIG_CACHE_LOCK = RLock()
_USE_CASE_CONFIG_CACHE_HITS = 0
_USE_CASE_CONFIG_CACHE_MISSES = 0


def _get_bool_env(name: str, default: bool) -> bool:
    """Parse boolean environment variable using common truthy values."""
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _is_uc_panel_cache_enabled() -> bool:
    """Return whether UC panel YAML cache is enabled for this process."""
    return _get_bool_env(_UC_PANEL_CACHE_ENABLED_ENV, True)


def _should_validate_cache_mtime() -> bool:
    """Return whether cached entry should validate file mtime before hit."""
    return _get_bool_env(_UC_PANEL_CACHE_VALIDATE_MTIME_ENV, True)


def _observe_cache_operation(operation: str, outcome: str) -> None:
    """Emit cache operation metric without raising on observability failures."""
    try:
        CACHE_OPERATIONS_TOTAL.labels(
            cache_type=_UC_PANEL_CACHE_TYPE,
            operation=operation,
            outcome=outcome,
        ).inc()
    except Exception:
        return


def _estimate_cache_entry_size_bytes(config: Dict[str, Any]) -> float:
    """Estimate serialized cache entry size in bytes."""
    try:
        serialized = json.dumps(config, ensure_ascii=False, sort_keys=True)
        return float(len(serialized.encode("utf-8")))
    except Exception:
        return 0.0


def _update_cache_snapshot_metrics(config: Optional[Dict[str, Any]] = None) -> None:
    """Update cache gauges/hit ratio and optional entry-size histogram."""
    try:
        CACHE_SIZE_ITEMS.labels(cache_type=_UC_PANEL_CACHE_TYPE).set(
            float(len(_USE_CASE_CONFIG_CACHE))
        )
        total = _USE_CASE_CONFIG_CACHE_HITS + _USE_CASE_CONFIG_CACHE_MISSES
        ratio = (
            float(_USE_CASE_CONFIG_CACHE_HITS) / float(total)
            if total > 0
            else 0.0
        )
        CACHE_HIT_RATIO.labels(cache_type=_UC_PANEL_CACHE_TYPE).set(ratio)
        if config is not None:
            CACHE_ENTRY_SIZE_BYTES.labels(cache_type=_UC_PANEL_CACHE_TYPE).observe(
                _estimate_cache_entry_size_bytes(config)
            )
    except Exception:
        return


def clear_use_case_config_cache() -> None:
    """Clear in-memory cache used by UC panel YAML loader."""
    global _USE_CASE_CONFIG_CACHE_HITS, _USE_CASE_CONFIG_CACHE_MISSES
    with _USE_CASE_CONFIG_CACHE_LOCK:
        _USE_CASE_CONFIG_CACHE.clear()
        _USE_CASE_CONFIG_CACHE_HITS = 0
        _USE_CASE_CONFIG_CACHE_MISSES = 0
    _observe_cache_operation("clear", "ok")
    _update_cache_snapshot_metrics()


def get_use_case_config_cache_stats() -> Dict[str, Any]:
    """Return lightweight cache stats for diagnostics/tests."""
    with _USE_CASE_CONFIG_CACHE_LOCK:
        entries = len(_USE_CASE_CONFIG_CACHE)
        hits = _USE_CASE_CONFIG_CACHE_HITS
        misses = _USE_CASE_CONFIG_CACHE_MISSES
    total = hits + misses
    hit_ratio = float(hits) / float(total) if total > 0 else 0.0
    return {
        "enabled": _is_uc_panel_cache_enabled(),
        "entries": entries,
        "hits": hits,
        "misses": misses,
        "hit_ratio": hit_ratio,
    }


def load_use_case_config(config_path: str) -> Dict[str, Any]:
    """
    Load use case configuration from YAML file.

    Parameters
    ----------
    config_path : str
        Path to YAML configuration file

    Returns
    -------
    Dict[str, Any]
        Use case configuration dictionary

    Examples
    --------
    >>> config = load_use_case_config('configs/uc_2_1.yaml')
    >>> panel = create_use_case_panel(**config)
    """
    global _USE_CASE_CONFIG_CACHE_HITS, _USE_CASE_CONFIG_CACHE_MISSES
    config_file = Path(config_path).expanduser().resolve()
    if not config_file.exists():
        _observe_cache_operation("get", "error")
        raise FileNotFoundError(f"Config file not found: {config_path}")

    cache_enabled = _is_uc_panel_cache_enabled()
    validate_mtime = _should_validate_cache_mtime()
    cache_key = str(config_file)

    # Resolve file mtime once for this read attempt and compare with cached entry.
    mtime_ns = config_file.stat().st_mtime_ns

    if cache_enabled:
        with _USE_CASE_CONFIG_CACHE_LOCK:
            cached = _USE_CASE_CONFIG_CACHE.get(cache_key)
            if cached is not None:
                is_valid = (not validate_mtime) or (cached.mtime_ns == mtime_ns)
                if is_valid:
                    _USE_CASE_CONFIG_CACHE_HITS += 1
                    _observe_cache_operation("get", "hit")
                    _update_cache_snapshot_metrics()
                    logger.debug(
                        "UC panel YAML cache hit",
                        extra={
                            "cache_key": cache_key,
                            "cache_entries": len(_USE_CASE_CONFIG_CACHE),
                        },
                    )
                    return deepcopy(cached.config)

    try:
        with open(config_file, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
    except yaml.YAMLError as exc:
        _observe_cache_operation("get", "error")
        raise ValueError(f"Invalid YAML config file: {config_path}") from exc

    if not isinstance(config, dict):
        _observe_cache_operation("get", "error")
        raise ValueError(f"Invalid YAML content (expected mapping): {config_path}")

    if not cache_enabled:
        _observe_cache_operation("get", "disabled")
        return deepcopy(config)

    with _USE_CASE_CONFIG_CACHE_LOCK:
        _USE_CASE_CONFIG_CACHE[cache_key] = _UseCaseCacheEntry(
            mtime_ns=mtime_ns,
            config=deepcopy(config),
        )
        _USE_CASE_CONFIG_CACHE_MISSES += 1
        _observe_cache_operation("get", "miss")
        _update_cache_snapshot_metrics(config=config)
        logger.debug(
            "UC panel YAML cache miss",
            extra={
                "cache_key": cache_key,
                "cache_entries": len(_USE_CASE_CONFIG_CACHE),
                "validate_mtime": validate_mtime,
            },
        )

    return deepcopy(config)


def create_use_case_panel(
    use_case_id: str,
    scientific_question: str,
    description: str,
    visual_elements: Optional[List[Dict[str, str]]] = None,
    interpretation_guidelines: Optional[List[str]] = None,
    color_scheme: str = "info",
) -> html.Div:
    """
    Create collapsible informative panel for use case description.

    Parameters
    ----------
    use_case_id : str
        Unique identifier for the use case (e.g., 'uc-2-1')
    scientific_question : str
        The main scientific question being addressed
    description : str
        Detailed description (plain text, supports line breaks)
    visual_elements : Optional[List[Dict[str, str]]], optional
        List of visual element descriptions
        Example: [{'label': 'Y-axis', 'description': 'Samples'}]
    interpretation_guidelines : Optional[List[str]], optional
        List of interpretation guidelines (plain text)
    color_scheme : str, optional
        Bootstrap color (info, primary, success, warning),
        by default "info"

    Returns
    -------
    html.Div
        Collapsible informative panel with button

    Examples
    --------
    >>> panel = create_use_case_panel(
    ...     use_case_id='uc-2-1',
    ...     scientific_question='How does ranking change?',
    ...     description='Compare functional richness.',
    ...     visual_elements=[
    ...         {'label': 'Y-axis', 'description': 'Samples'},
    ...         {'label': 'X-axis', 'description': 'KO counts'}
    ...     ],
    ...     interpretation_guidelines=[
    ...         'Ranking: Observe changes',
    ...         'Generalists: High ranks'
    ...     ]
    ... )

    Notes
    -----
    - Collapsible with button for better UX
    - Plain text rendering (no markdown processing)
    - Color-coded borders for visual hierarchy
    - Can be configured via YAML using load_use_case_config()
    """
    # Visual elements section
    visual_elements_content = []
    if visual_elements:
        visual_items = [
            html.Li([html.Strong(f"{elem['label']}: "), elem["description"]])
            for elem in visual_elements
        ]
        visual_elements_content = [
            html.H6(
                [html.I(className="fas fa-eye me-2"), "Visual Elements"],
                className="mt-3 mb-2 text-primary",
            ),
            html.Ul(visual_items, className="mb-0"),
        ]

    # Interpretation guidelines section
    interpretation_content = []
    if interpretation_guidelines:
        interpretation_items = [
            html.Li(guideline) for guideline in interpretation_guidelines
        ]
        interpretation_content = [
            html.H6(
                [html.I(className="fas fa-lightbulb me-2"), "Interpretation"],
                className="mt-3 mb-2 text-warning fw-bold",
            ),
            html.Ul(interpretation_items, className="mb-0"),
        ]

    # Main panel with collapse button
    collapse_id = f"{use_case_id}-collapse"
    button_id = f"{use_case_id}-collapse-button"

    panel = html.Div(
        [
            # Collapse Button
            dbc.Button(
                [
                    html.I(className="fas fa-info-circle me-2"),
                    "View Use Case Description",
                ],
                id=button_id,
                color=color_scheme,
                outline=True,
                className="mb-3 w-100",
                n_clicks=0,
            ),
            # Collapsible Content
            dbc.Collapse(
                dbc.Card(
                    [
                        dbc.CardBody(
                            [
                                # Scientific Question Header
                                html.Div(
                                    [
                                        html.H6(
                                            [
                                                html.I(
                                                    className="fas fa-question-circle me-2"
                                                ),
                                                "Scientific Question",
                                            ],
                                            className="mb-2 text-success fw-bold",
                                        ),
                                        html.Blockquote(
                                            scientific_question,
                                            className=(
                                                "border-start border-4 border-success "
                                                "ps-3 mb-3 fst-italic"
                                            ),
                                        ),
                                    ]
                                ),
                                # Description
                                html.Div(
                                    [
                                        html.H6(
                                            [
                                                html.I(
                                                    className="fas fa-info-circle me-2"
                                                ),
                                                "Description",
                                            ],
                                            className="mb-2 text-info fw-bold",
                                        ),
                                        html.P(
                                            description,
                                            className="text-muted mb-3",
                                            style={"whiteSpace": "pre-line"},
                                        ),
                                    ]
                                ),
                                # Visual Elements
                                (
                                    html.Div(visual_elements_content)
                                    if visual_elements
                                    else html.Div()
                                ),
                                # Interpretation Guidelines
                                (
                                    html.Div(interpretation_content)
                                    if interpretation_guidelines
                                    else html.Div()
                                ),
                            ],
                            className="p-4",
                        )
                    ],
                    className=f"border-{color_scheme} shadow-sm",
                ),
                id=collapse_id,
                is_open=False,
            ),
        ],
        id=f"{use_case_id}-info-panel",
    )

    return panel
