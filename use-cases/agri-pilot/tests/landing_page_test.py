"""Landing page and Android app download routes."""

from __future__ import annotations

import os
from pathlib import Path

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from marketplace.routers.landing import (
    _DEFAULT_DOWNLOAD_URL,
    resolve_app_download_url,
    router as landing_router,
)


def _client():
    app = FastAPI()
    app.include_router(landing_router)
    return TestClient(app)


def test_landing_page_returns_html():
    client = _client()
    r = client.get("/")
    assert r.status_code == 200
    assert "text/html" in r.headers.get("content-type", "")
    body = r.text
    assert "AgriPilot" in body
    assert "Download Android App" in body
    assert 'href="/download"' in body
    assert 'href="/docs"' in body
    assert "AI Agricultural Intelligence" in body
    assert "Features" in body
    assert "Farmers" in body


def test_download_redirects_to_default_github_releases(monkeypatch):
    monkeypatch.delenv("AGRIPILOT_APP_DOWNLOAD_URL", raising=False)
    client = _client()
    r = client.get("/download", follow_redirects=False)
    assert r.status_code == 307
    assert r.headers["location"] == _DEFAULT_DOWNLOAD_URL


def test_download_respects_env_override(monkeypatch):
    custom = "https://example.com/agripilot.apk"
    monkeypatch.setenv("AGRIPILOT_APP_DOWNLOAD_URL", custom)
    assert resolve_app_download_url() == custom
    client = _client()
    r = client.get("/download", follow_redirects=False)
    assert r.status_code == 307
    assert r.headers["location"] == custom


def test_download_apk_redirects_when_no_local_file(monkeypatch):
    monkeypatch.delenv("AGRIPILOT_APK_PATH", raising=False)
    client = _client()
    r = client.get("/download/apk", follow_redirects=False)
    assert r.status_code == 307
    assert r.headers["location"] == "/download"


def test_download_apk_serves_local_file(tmp_path, monkeypatch):
    apk = tmp_path / "agripilot-test.apk"
    apk.write_bytes(b"PK fake apk")
    monkeypatch.setenv("AGRIPILOT_APK_PATH", str(apk))
    client = _client()
    r = client.get("/download/apk")
    assert r.status_code == 200
    assert r.content == b"PK fake apk"
    assert "application/vnd.android.package-archive" in r.headers.get("content-type", "")


def test_static_icon_and_favicon():
    client = _client()
    icon_path = Path(__file__).resolve().parents[1] / "docs" / "branding" / "agripilot-icon.png"
    if not icon_path.is_file():
        pytest.skip("branding icon not present")
    for path in ("/static/agripilot-icon.png", "/favicon.ico"):
        r = client.get(path)
        assert r.status_code == 200
        assert "image/png" in r.headers.get("content-type", "")
        assert len(r.content) > 0
