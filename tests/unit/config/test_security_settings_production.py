"""Security-focused tests for production settings validation."""

from __future__ import annotations

import pytest

from config.settings import Settings


def _set_base_env(monkeypatch, tmp_path, env: str) -> None:
    """Configure minimum env context to instantiate Settings deterministically."""
    monkeypatch.setenv("BIOREMPP_ENV", env)
    monkeypatch.setenv("BIOREMPP_CACHE_DIR", str(tmp_path / "cache"))
    monkeypatch.setenv("BIOREMPP_HOST", "127.0.0.1")
    monkeypatch.setenv("BIOREMPP_PORT", "8050")


def test_production_rejects_empty_secret_key(monkeypatch, tmp_path):
    """Production mode should fail-fast when SECRET_KEY is empty."""
    _set_base_env(monkeypatch, tmp_path, env="production")
    monkeypatch.setenv("SECRET_KEY", "")
    monkeypatch.setenv("BIOREMPP_RESUME_BACKEND", "diskcache")

    with pytest.raises(ValueError, match="SECRET_KEY"):
        Settings()


def test_production_rejects_placeholder_secret_key(monkeypatch, tmp_path):
    """Production mode should reject placeholder secret values."""
    _set_base_env(monkeypatch, tmp_path, env="production")
    monkeypatch.setenv("SECRET_KEY", "REPLACE_WITH_REAL_SECRET_FROM_DOCKER_SECRETS")
    monkeypatch.setenv("BIOREMPP_RESUME_BACKEND", "diskcache")

    with pytest.raises(ValueError, match="SECRET_KEY"):
        Settings()


def test_production_rejects_redis_resume_without_password(monkeypatch, tmp_path):
    """Redis resume backend must have secure password in production."""
    _set_base_env(monkeypatch, tmp_path, env="production")
    monkeypatch.setenv("SECRET_KEY", "a" * 64)
    monkeypatch.setenv("BIOREMPP_RESUME_BACKEND", "redis")
    monkeypatch.setenv("BIOREMPP_RESUME_REDIS_PASSWORD", "")
    monkeypatch.setenv("REDIS_PASSWORD", "")

    with pytest.raises(ValueError, match="Redis password"):
        Settings()


def test_development_allows_placeholder_values(monkeypatch, tmp_path):
    """Development mode should remain permissive for local workflows."""
    _set_base_env(monkeypatch, tmp_path, env="development")
    monkeypatch.setenv("SECRET_KEY", "__SET_IN_PROD__")
    monkeypatch.setenv("BIOREMPP_RESUME_BACKEND", "redis")
    monkeypatch.setenv("BIOREMPP_RESUME_REDIS_PASSWORD", "")
    monkeypatch.setenv("REDIS_PASSWORD", "")

    settings = Settings()
    assert settings.is_development is True


def test_production_rejects_proxy_trust_without_explicit_cidrs(monkeypatch, tmp_path):
    """Production must fail when trusting proxy headers without explicit CIDRs."""
    _set_base_env(monkeypatch, tmp_path, env="production")
    monkeypatch.setenv("SECRET_KEY", "a" * 64)
    monkeypatch.setenv("BIOREMPP_RESUME_BACKEND", "diskcache")
    monkeypatch.setenv("BIOREMPP_TRUST_PROXY_HEADERS", "true")
    monkeypatch.delenv("BIOREMPP_TRUSTED_PROXY_CIDRS", raising=False)

    with pytest.raises(ValueError, match="BIOREMPP_TRUSTED_PROXY_CIDRS"):
        Settings()


def test_production_rejects_proxy_trust_with_invalid_cidr(monkeypatch, tmp_path):
    """Invalid trusted CIDR entries must abort production startup."""
    _set_base_env(monkeypatch, tmp_path, env="production")
    monkeypatch.setenv("SECRET_KEY", "a" * 64)
    monkeypatch.setenv("BIOREMPP_RESUME_BACKEND", "diskcache")
    monkeypatch.setenv("BIOREMPP_TRUST_PROXY_HEADERS", "true")
    monkeypatch.setenv("BIOREMPP_TRUSTED_PROXY_CIDRS", "10.20.0.0/16,not-a-cidr")

    with pytest.raises(ValueError, match="invalid CIDR entries"):
        Settings()


def test_production_rejects_loopback_only_proxy_cidrs(monkeypatch, tmp_path):
    """Loopback-only trusted proxies are not allowed in production trust mode."""
    _set_base_env(monkeypatch, tmp_path, env="production")
    monkeypatch.setenv("SECRET_KEY", "a" * 64)
    monkeypatch.setenv("BIOREMPP_RESUME_BACKEND", "diskcache")
    monkeypatch.setenv("BIOREMPP_TRUST_PROXY_HEADERS", "true")
    monkeypatch.setenv("BIOREMPP_TRUSTED_PROXY_CIDRS", "127.0.0.1/32,::1/128")

    with pytest.raises(ValueError, match="loopback-only trusted CIDRs"):
        Settings()


def test_production_allows_proxy_trust_with_valid_cidrs(monkeypatch, tmp_path):
    """Valid institutional CIDRs should pass production proxy trust checks."""
    _set_base_env(monkeypatch, tmp_path, env="production")
    monkeypatch.setenv("SECRET_KEY", "a" * 64)
    monkeypatch.setenv("BIOREMPP_RESUME_BACKEND", "diskcache")
    monkeypatch.setenv("BIOREMPP_TRUST_PROXY_HEADERS", "true")
    monkeypatch.setenv("BIOREMPP_TRUSTED_PROXY_CIDRS", "10.20.0.0/16,10.21.0.0/16")

    settings = Settings()
    assert settings.TRUST_PROXY_HEADERS is True
    assert settings.TRUSTED_PROXY_CIDRS == ("10.20.0.0/16", "10.21.0.0/16")
