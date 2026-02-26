"""Tests for proxy trust and public data allowlist settings."""

from __future__ import annotations

from config.settings import Settings


def _set_base_env(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("BIOREMPP_ENV", "development")
    monkeypatch.setenv("BIOREMPP_CACHE_DIR", str(tmp_path / "cache"))
    monkeypatch.setenv("BIOREMPP_HOST", "127.0.0.1")
    monkeypatch.setenv("BIOREMPP_PORT", "8050")
    monkeypatch.setenv("BIOREMPP_RESUME_BACKEND", "diskcache")


def test_trusted_proxy_cidrs_are_normalized(monkeypatch, tmp_path):
    """Valid proxy CIDRs should be normalized and kept."""
    _set_base_env(monkeypatch, tmp_path)
    monkeypatch.setenv(
        "BIOREMPP_TRUSTED_PROXY_CIDRS",
        "127.0.0.1/32, 10.0.0.0/8 ,::1/128",
    )

    settings = Settings()

    assert settings.TRUSTED_PROXY_CIDRS == (
        "127.0.0.1/32",
        "10.0.0.0/8",
        "::1/128",
    )


def test_invalid_proxy_cidrs_fall_back_to_safe_defaults(monkeypatch, tmp_path):
    """Invalid proxy CIDRs should not break config and must fallback safely."""
    _set_base_env(monkeypatch, tmp_path)
    monkeypatch.setenv("BIOREMPP_TRUSTED_PROXY_CIDRS", "invalid-cidr,another-invalid")

    settings = Settings()

    assert settings.TRUSTED_PROXY_CIDRS == ("127.0.0.1/32", "::1/128")


def test_public_data_allowlist_sanitizes_unsafe_entries(monkeypatch, tmp_path):
    """Unsafe path-like entries should be dropped from public allowlist."""
    _set_base_env(monkeypatch, tmp_path)
    monkeypatch.setenv(
        "BIOREMPP_PUBLIC_DATA_ALLOWED_FILES",
        "exemple_dataset.txt, ../secret.txt, data/file.csv,custom.csv,sub\\file.tsv",
    )

    settings = Settings()

    assert settings.PUBLIC_DATA_ALLOWED_FILES == ("exemple_dataset.txt", "custom.csv")


def test_is_trusted_proxy_ip_checks_cidr_membership(monkeypatch, tmp_path):
    """Trusted proxy helper should match only configured networks."""
    _set_base_env(monkeypatch, tmp_path)
    monkeypatch.setenv("BIOREMPP_TRUSTED_PROXY_CIDRS", "172.16.0.0/12")

    settings = Settings()

    assert settings.is_trusted_proxy_ip("172.16.10.2") is True
    assert settings.is_trusted_proxy_ip("203.0.113.10") is False
    assert settings.is_trusted_proxy_ip("not-an-ip") is False


def test_is_public_data_file_allowed_enforces_basename(monkeypatch, tmp_path):
    """Public filename helper should reject traversal and unknown files."""
    _set_base_env(monkeypatch, tmp_path)
    monkeypatch.setenv("BIOREMPP_PUBLIC_DATA_ALLOWED_FILES", "exemple_dataset.txt")

    settings = Settings()

    assert settings.is_public_data_file_allowed("exemple_dataset.txt") is True
    assert settings.is_public_data_file_allowed("../exemple_dataset.txt") is False
    assert settings.is_public_data_file_allowed("data/exemple_dataset.txt") is False
    assert settings.is_public_data_file_allowed("hadeg_db.csv") is False
