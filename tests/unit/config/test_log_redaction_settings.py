"""Tests for log-reference redaction settings behavior."""

from __future__ import annotations

from config.settings import Settings


def _set_base_env(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("BIOREMPP_ENV", "development")
    monkeypatch.setenv("BIOREMPP_CACHE_DIR", str(tmp_path / "cache"))
    monkeypatch.setenv("BIOREMPP_HOST", "127.0.0.1")
    monkeypatch.setenv("BIOREMPP_PORT", "8050")
    monkeypatch.setenv("BIOREMPP_RESUME_BACKEND", "diskcache")


def test_log_ref_salt_falls_back_to_secret_key(monkeypatch, tmp_path):
    """When dedicated salt is missing, SECRET_KEY should be reused if secure."""
    _set_base_env(monkeypatch, tmp_path)
    monkeypatch.setenv("SECRET_KEY", "a" * 64)
    monkeypatch.delenv("BIOREMPP_LOG_REF_SALT", raising=False)

    settings = Settings()

    assert settings.LOG_REF_SALT == "a" * 64
    assert settings._log_ref_salt_source == "secret_key"


def test_log_ref_salt_is_ephemeral_in_dev_when_no_secure_secret(monkeypatch, tmp_path):
    """Development mode should generate ephemeral salt if no secure source exists."""
    _set_base_env(monkeypatch, tmp_path)
    monkeypatch.setenv("SECRET_KEY", "__SET_IN_PROD__")
    monkeypatch.delenv("BIOREMPP_LOG_REF_SALT", raising=False)

    settings = Settings()

    assert settings.LOG_REF_SALT
    assert settings._log_ref_salt_source == "ephemeral_dev"


def test_log_ref_length_is_clamped(monkeypatch, tmp_path):
    """LOG_REF_LENGTH must stay inside the hard bounds [8, 24]."""
    _set_base_env(monkeypatch, tmp_path)
    monkeypatch.setenv("SECRET_KEY", "b" * 64)
    monkeypatch.setenv("BIOREMPP_LOG_REF_LENGTH", "999")

    high_settings = Settings()
    assert high_settings.LOG_REF_LENGTH == 24

    monkeypatch.setenv("BIOREMPP_LOG_REF_LENGTH", "1")
    low_settings = Settings()
    assert low_settings.LOG_REF_LENGTH == 8

