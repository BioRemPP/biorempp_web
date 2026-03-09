"""Tests for URL base-path normalization and path helpers."""

from __future__ import annotations

from config.settings import Settings


def _set_base_env(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("BIOREMPP_ENV", "development")
    monkeypatch.setenv("BIOREMPP_CACHE_DIR", str(tmp_path / "cache"))
    monkeypatch.setenv("BIOREMPP_HOST", "127.0.0.1")
    monkeypatch.setenv("BIOREMPP_PORT", "8050")
    monkeypatch.setenv("BIOREMPP_RESUME_BACKEND", "diskcache")


def test_url_base_path_defaults_to_root(monkeypatch, tmp_path):
    """When not configured, URL base path should stay at root."""
    _set_base_env(monkeypatch, tmp_path)
    monkeypatch.delenv("BIOREMPP_URL_BASE_PATH", raising=False)

    settings = Settings()

    assert settings.URL_BASE_PATH == "/"
    assert settings.build_app_path("/results") == "/results"
    assert settings.strip_base_path("/results") == "/results"


def test_url_base_path_normalizes_prefix(monkeypatch, tmp_path):
    """Prefix variants should normalize to '/prefix/' format."""
    _set_base_env(monkeypatch, tmp_path)
    monkeypatch.setenv("BIOREMPP_URL_BASE_PATH", "biorempp")

    settings = Settings()

    assert settings.URL_BASE_PATH == "/biorempp/"


def test_build_app_path_respects_base_and_avoids_double_prefix(monkeypatch, tmp_path):
    """Path builder should prepend base once and keep prefixed paths stable."""
    _set_base_env(monkeypatch, tmp_path)
    monkeypatch.setenv("BIOREMPP_URL_BASE_PATH", "/biorempp/")

    settings = Settings()

    assert settings.build_app_path("/") == "/biorempp/"
    assert settings.build_app_path("/results") == "/biorempp/results"
    assert settings.build_app_path("/biorempp/results") == "/biorempp/results"
    assert settings.build_app_path("results") == "/biorempp/results"


def test_strip_base_path_supports_prefixed_and_unprefixed_paths(monkeypatch, tmp_path):
    """Route matching helper should work with and without prefix."""
    _set_base_env(monkeypatch, tmp_path)
    monkeypatch.setenv("BIOREMPP_URL_BASE_PATH", "/biorempp/")

    settings = Settings()

    assert settings.strip_base_path("/biorempp/") == "/"
    assert settings.strip_base_path("/biorempp/results") == "/results"
    assert settings.strip_base_path("/results") == "/results"


def test_build_app_path_keeps_external_links(monkeypatch, tmp_path):
    """External links and anchors should not be rewritten."""
    _set_base_env(monkeypatch, tmp_path)
    monkeypatch.setenv("BIOREMPP_URL_BASE_PATH", "/biorempp/")

    settings = Settings()

    assert settings.build_app_path("https://example.org/doc") == "https://example.org/doc"
    assert settings.build_app_path("mailto:test@example.org") == "mailto:test@example.org"
    assert settings.build_app_path("#section") == "#section"
