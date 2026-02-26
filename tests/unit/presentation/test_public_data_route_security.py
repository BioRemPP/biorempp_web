"""Security tests for public data download route."""

from __future__ import annotations

import biorempp_app


def _build_test_client(monkeypatch, allowed_files: tuple[str, ...]):
    """Create test client with controlled public-file allowlist."""
    monkeypatch.setattr(
        biorempp_app.settings,
        "PUBLIC_DATA_ALLOWED_FILES",
        allowed_files,
    )
    app = biorempp_app.create_app(force_initialize=True)
    app.server.config["TESTING"] = True
    return app.server.test_client()


def test_public_data_route_serves_allowlisted_file(monkeypatch):
    """Allowlisted file should be downloadable from /data endpoint."""
    client = _build_test_client(monkeypatch, ("exemple_dataset.txt",))

    response = client.get("/data/exemple_dataset.txt")

    assert response.status_code == 200
    assert "attachment" in response.headers.get("Content-Disposition", "").lower()


def test_public_data_route_blocks_non_allowlisted_file(monkeypatch):
    """Non-allowlisted file should return generic 404."""
    client = _build_test_client(monkeypatch, ("exemple_dataset.txt",))

    response = client.get("/data/hadeg_db.csv")

    assert response.status_code == 404
    assert response.get_json() == {"error": "File not found"}


def test_public_data_route_blocks_suspicious_filename(monkeypatch):
    """Suspicious filename patterns should be blocked by allowlist validator."""
    client = _build_test_client(monkeypatch, ("exemple_dataset.txt",))

    response = client.get("/data/..")

    assert response.status_code == 404
    assert response.get_json() == {"error": "File not found"}


def test_public_data_route_supports_prefixed_base_path(monkeypatch):
    """Prefixed base path should expose the same allowlisted download route."""
    monkeypatch.setattr(biorempp_app.settings, "URL_BASE_PATH", "/biorempp/")
    client = _build_test_client(monkeypatch, ("exemple_dataset.txt",))

    response = client.get("/biorempp/data/exemple_dataset.txt")

    assert response.status_code == 200
    assert "attachment" in response.headers.get("Content-Disposition", "").lower()
