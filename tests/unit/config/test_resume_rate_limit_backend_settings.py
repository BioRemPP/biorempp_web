"""Tests for resume rate-limit backend settings and production guards."""

from __future__ import annotations

import pytest

from config.settings import Settings


def _set_base_env(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("BIOREMPP_ENV", "development")
    monkeypatch.setenv("BIOREMPP_CACHE_DIR", str(tmp_path / "cache"))
    monkeypatch.setenv("BIOREMPP_HOST", "127.0.0.1")
    monkeypatch.setenv("BIOREMPP_PORT", "8050")
    monkeypatch.setenv("BIOREMPP_RESUME_BACKEND", "diskcache")


def test_resume_rate_limit_backend_defaults_to_auto(monkeypatch, tmp_path):
    """Rate-limit backend should default to AUTO with safe key prefix."""
    _set_base_env(monkeypatch, tmp_path)
    monkeypatch.delenv("BIOREMPP_RESUME_RATE_LIMIT_BACKEND", raising=False)
    monkeypatch.delenv("BIOREMPP_RESUME_RATE_LIMIT_REDIS_KEY_PREFIX", raising=False)

    settings = Settings()

    assert settings.RESUME_RATE_LIMIT_BACKEND == "auto"
    assert settings.RESUME_RATE_LIMIT_REDIS_KEY_PREFIX == "biorempp:resume:ratelimit:"


def test_invalid_resume_rate_limit_backend_falls_back_to_auto(monkeypatch, tmp_path):
    """Invalid rate-limit backend values should normalize to AUTO."""
    _set_base_env(monkeypatch, tmp_path)
    monkeypatch.setenv("BIOREMPP_RESUME_RATE_LIMIT_BACKEND", "invalid-backend")

    settings = Settings()

    assert settings.RESUME_RATE_LIMIT_BACKEND == "auto"


def test_production_rate_limit_redis_requires_secure_password(monkeypatch, tmp_path):
    """Production must fail fast when Redis rate-limit backend lacks secure password."""
    monkeypatch.setenv("BIOREMPP_ENV", "production")
    monkeypatch.setenv("SECRET_KEY", "a" * 64)
    monkeypatch.setenv("BIOREMPP_CACHE_DIR", str(tmp_path / "cache"))
    monkeypatch.setenv("BIOREMPP_HOST", "0.0.0.0")
    monkeypatch.setenv("BIOREMPP_PORT", "8080")
    monkeypatch.setenv("BIOREMPP_RESUME_BACKEND", "diskcache")
    monkeypatch.setenv("BIOREMPP_RESUME_RATE_LIMIT_BACKEND", "redis")
    monkeypatch.setenv("BIOREMPP_RESUME_REDIS_PASSWORD", "")
    monkeypatch.setenv("BIOREMPP_TRUST_PROXY_HEADERS", "false")

    with pytest.raises(ValueError, match="resume rate-limit backend"):
        Settings()

