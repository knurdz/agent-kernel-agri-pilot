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
    assert 'href="/architecture"' in body
    assert 'href="/docs"' in body
    assert "Farmers Earn More" in body
    assert "Fresh Food" in body and "Lower Cost" in body
    assert "Citizens Deliver" in body
    assert "Multi-Agent AI" in body
    assert "Plant Health" in body or "Plant tracking" in body
    assert "Live Tracking" in body or "Live delivery" in body
    assert "Farmers" in body
    assert "Buyers" in body
    assert "Delivery Riders" in body
    assert "support@knurdz.org" in body
    assert "+1 (555) 678-0512" in body
    assert "https://github.com/knurdz/agent-kernel-agri-pilot" in body
    assert "telegram-chat.jpg" in body
    assert "Telegram Bot in Production" in body


def test_architecture_page_returns_html():
    html_path = Path(__file__).resolve().parents[1] / "docs" / "architecture" / "agripilot.architecture.html"
    if not html_path.is_file():
        pytest.skip("architecture HTML not present")
    client = _client()
    r = client.get("/architecture")
    assert r.status_code == 200
    assert "text/html" in r.headers.get("content-type", "")
    assert "AgriPilot Runtime" in r.text


def test_landing_page_links_architecture():
    html_path = Path(__file__).resolve().parents[1] / "docs" / "architecture" / "agripilot.architecture.html"
    if not html_path.is_file():
        pytest.skip("architecture HTML not present")
    client = _client()
    r = client.get("/")
    assert r.status_code == 200
    assert 'href="/architecture"' in r.text
    assert "View runtime architecture" in r.text


def test_screenshot_assets():
    client = _client()
    screenshots_dir = Path(__file__).resolve().parents[1] / "docs" / "screenshots"
    for name in ("home.png", "advisor.png", "plant-detail.png", "orders.png", "delivery-tracking.jpg", "telegram-chat.jpg"):
        if not (screenshots_dir / name).is_file():
            pytest.skip(f"screenshot {name} not present")
        r = client.get(f"/static/screenshots/{name}")
        assert r.status_code == 200
        assert len(r.content) > 0


def test_unknown_screenshot_404():
    client = _client()
    assert client.get("/static/screenshots/not-real.png").status_code == 404


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
