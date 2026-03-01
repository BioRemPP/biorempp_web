"""Centralized URL path helpers for presentation-layer routing."""

from __future__ import annotations

from config.settings import get_settings


def get_url_base_path() -> str:
    """Return normalized URL base path configured for the app."""
    return get_settings().URL_BASE_PATH


def app_path(path: str = "/") -> str:
    """Build an application-internal URL respecting URL_BASE_PATH."""
    return get_settings().build_app_path(path)


def strip_base_path(pathname: str | None) -> str:
    """Remove URL_BASE_PATH prefix for internal route matching."""
    return get_settings().strip_base_path(pathname)

