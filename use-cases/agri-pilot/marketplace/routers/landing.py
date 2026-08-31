"""Public landing page and Android app download routes."""

from __future__ import annotations

import html
import os
from pathlib import Path

from fastapi import APIRouter
from fastapi.responses import FileResponse, HTMLResponse, RedirectResponse

from marketplace.channels import public_channel_config

router = APIRouter(tags=["landing"])

_DEFAULT_DOWNLOAD_URL = "https://github.com/yaalalabs/agent-kernel/releases?q=agripilot-mobile"
_BRANDING_DIR = Path(__file__).resolve().parents[2] / "docs" / "branding"
_ICON_PATH = _BRANDING_DIR / "agripilot-icon.png"


def resolve_app_download_url() -> str:
    """Resolve APK download URL from env, config.yaml, or default GitHub Releases."""
    env = os.environ.get("AGRIPILOT_APP_DOWNLOAD_URL", "").strip()
    if env:
        return env
    try:
        import yaml

        with open("config.yaml", "r", encoding="utf-8") as fh:
            data = yaml.safe_load(fh) or {}
        cfg = str((data.get("app") or {}).get("download_url") or "").strip()
        if cfg:
            return cfg
    except Exception:
        pass
    return _DEFAULT_DOWNLOAD_URL


def resolve_apk_path() -> Path | None:
    """Return local APK path when configured and the file exists."""
    env = os.environ.get("AGRIPILOT_APK_PATH", "").strip()
    if not env:
        try:
            import yaml

            with open("config.yaml", "r", encoding="utf-8") as fh:
                data = yaml.safe_load(fh) or {}
            env = str((data.get("app") or {}).get("apk_path") or "").strip()
        except Exception:
            env = ""
    if not env:
        return None
    path = Path(env)
    return path if path.is_file() else None


def _icon_response() -> FileResponse:
    if not _ICON_PATH.is_file():
        raise FileNotFoundError(str(_ICON_PATH))
    return FileResponse(_ICON_PATH, media_type="image/png")


def _build_landing_html() -> str:
    channels = public_channel_config()
    wa_me = channels.get("whatsapp_wa_me") or "#"
    telegram_base = channels.get("telegram_deep_link_base") or "#"
    download_url = "/download"

    wa_display = html.escape(channels.get("whatsapp_display_number") or "WhatsApp")
    telegram_label = html.escape(channels.get("telegram_bot_username") or "Telegram")

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>AgriPilot — AI Agricultural Intelligence</title>
  <meta name="description" content="Crop diagnostics, marketplace, and delivery for farmers, buyers, and riders." />
  <link rel="icon" href="/favicon.ico" type="image/png" />
  <style>
    :root {{
      --emerald-50: #ecfdf5;
      --emerald-100: #d1fae5;
      --emerald-200: #a7f3d0;
      --emerald-500: #10b981;
      --emerald-600: #059669;
      --emerald-700: #047857;
      --emerald-900: #064e3b;
      --slate-50: #f8fafc;
      --slate-100: #f1f5f9;
      --slate-600: #475569;
      --slate-700: #334155;
      --slate-900: #0f172a;
      --glass: rgba(255, 255, 255, 0.72);
      --shadow: 0 4px 24px rgba(6, 78, 59, 0.08);
      --radius: 16px;
    }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      font-family: system-ui, -apple-system, "Segoe UI", Roboto, sans-serif;
      color: var(--slate-900);
      background: linear-gradient(165deg, var(--emerald-50) 0%, var(--slate-50) 45%, #fff 100%);
      line-height: 1.6;
      min-height: 100vh;
    }}
    a {{ color: var(--emerald-700); text-decoration: none; }}
    a:hover {{ text-decoration: underline; }}
    .wrap {{ max-width: 1080px; margin: 0 auto; padding: 0 1.25rem; }}
    header {{
      position: sticky; top: 0; z-index: 10;
      background: var(--glass);
      backdrop-filter: blur(12px);
      border-bottom: 1px solid var(--emerald-100);
    }}
    .nav {{
      display: flex; align-items: center; justify-content: space-between;
      padding: 0.85rem 0; gap: 1rem; flex-wrap: wrap;
    }}
    .brand {{ display: flex; align-items: center; gap: 0.65rem; font-weight: 700; font-size: 1.2rem; color: var(--emerald-900); }}
    .brand img {{ width: 40px; height: 40px; border-radius: 10px; }}
    .nav-links {{ display: flex; gap: 1.25rem; flex-wrap: wrap; font-size: 0.95rem; }}
    .nav-links a {{ color: var(--slate-700); font-weight: 500; }}
    .hero {{ padding: 3.5rem 0 2.5rem; text-align: center; }}
    .hero h1 {{
      font-size: clamp(1.85rem, 4vw, 2.75rem);
      line-height: 1.15; color: var(--emerald-900);
      margin-bottom: 1rem; max-width: 720px; margin-left: auto; margin-right: auto;
    }}
    .hero p {{
      font-size: 1.1rem; color: var(--slate-600);
      max-width: 560px; margin: 0 auto 1.75rem;
    }}
    .cta-row {{
      display: flex; flex-wrap: wrap; gap: 0.75rem; justify-content: center; margin-bottom: 2rem;
    }}
    .btn {{
      display: inline-flex; align-items: center; gap: 0.5rem;
      padding: 0.85rem 1.35rem; border-radius: 999px;
      font-weight: 600; font-size: 1rem; border: none; cursor: pointer;
      text-decoration: none; transition: transform 0.15s, box-shadow 0.15s;
    }}
    .btn:hover {{ transform: translateY(-1px); text-decoration: none; }}
    .btn-primary {{
      background: linear-gradient(135deg, var(--emerald-500), var(--emerald-700));
      color: #fff; box-shadow: 0 8px 24px rgba(5, 150, 105, 0.35);
    }}
    .btn-primary:hover {{ box-shadow: 0 10px 28px rgba(5, 150, 105, 0.45); }}
    .btn-secondary {{
      background: #fff; color: var(--emerald-800, var(--emerald-700));
      border: 1px solid var(--emerald-200);
    }}
    .badge {{
      font-size: 0.7rem; font-weight: 700; letter-spacing: 0.04em;
      background: rgba(255,255,255,0.25); padding: 0.15rem 0.45rem; border-radius: 6px;
    }}
    section {{ padding: 2.5rem 0; }}
    section h2 {{
      text-align: center; font-size: 1.65rem; color: var(--emerald-900);
      margin-bottom: 1.5rem;
    }}
    .grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
      gap: 1.25rem;
    }}
    .card {{
      background: var(--glass);
      backdrop-filter: blur(8px);
      border: 1px solid var(--emerald-100);
      border-radius: var(--radius);
      padding: 1.35rem;
      box-shadow: var(--shadow);
    }}
    .card h3 {{ font-size: 1.05rem; color: var(--emerald-800, var(--emerald-700)); margin-bottom: 0.5rem; }}
    .card p {{ font-size: 0.95rem; color: var(--slate-600); }}
    .card .icon {{ font-size: 1.75rem; margin-bottom: 0.5rem; }}
    .roles .card {{ border-left: 4px solid var(--emerald-500); }}
    .steps {{
      counter-reset: step; list-style: none; max-width: 520px; margin: 0 auto;
    }}
    .steps li {{
      counter-increment: step;
      position: relative; padding-left: 2.75rem; margin-bottom: 1rem;
      color: var(--slate-700);
    }}
    .steps li::before {{
      content: counter(step);
      position: absolute; left: 0; top: 0;
      width: 2rem; height: 2rem; line-height: 2rem; text-align: center;
      background: var(--emerald-500); color: #fff; font-weight: 700;
      border-radius: 50%; font-size: 0.9rem;
    }}
    footer {{
      text-align: center; padding: 2rem 0 2.5rem;
      color: var(--slate-600); font-size: 0.9rem;
      border-top: 1px solid var(--emerald-100); margin-top: 1rem;
    }}
    @media (max-width: 600px) {{
      .nav-links {{ width: 100%; justify-content: center; }}
      .hero {{ padding-top: 2rem; }}
    }}
  </style>
</head>
<body>
  <header>
    <div class="wrap nav">
      <div class="brand">
        <img src="/static/agripilot-icon.png" alt="AgriPilot" width="40" height="40" />
        AgriPilot
      </div>
      <nav class="nav-links">
        <a href="#features">Features</a>
        <a href="#roles">Roles</a>
        <a href="/docs">API Docs</a>
        <a href="{download_url}">Download</a>
      </nav>
    </div>
  </header>

  <main>
    <section class="hero">
      <div class="wrap">
        <h1>AI Agricultural Intelligence, Marketplace &amp; Delivery</h1>
        <p>Diagnose crop problems, track plant health, sell produce, connect with buyers, and coordinate rider delivery — on Android, WhatsApp, and Telegram.</p>
        <div class="cta-row">
          <a class="btn btn-primary" href="{download_url}">
            Download Android App <span class="badge">APK</span>
          </a>
          <a class="btn btn-secondary" href="/docs">API Docs</a>
          <a class="btn btn-secondary" href="{html.escape(wa_me)}">WhatsApp Advisor</a>
          <a class="btn btn-secondary" href="{html.escape(telegram_base)}">Telegram Bot</a>
        </div>
      </div>
    </section>

    <section id="features">
      <div class="wrap">
        <h2>Features</h2>
        <div class="grid">
          <article class="card">
            <div class="icon" aria-hidden="true">&#127807;</div>
            <h3>AI Crop Diagnostics</h3>
            <p>Photo-based leaf disease identification with safety-validated treatment advice.</p>
          </article>
          <article class="card">
            <div class="icon" aria-hidden="true">&#128200;</div>
            <h3>Plant Health Tracking</h3>
            <p>Observation timeline, growth monitoring, and crop health insight history.</p>
          </article>
          <article class="card">
            <div class="icon" aria-hidden="true">&#128722;</div>
            <h3>Farmer-to-Buyer Marketplace</h3>
            <p>Direct farm listings, buyer matching, and connection requests without middlemen.</p>
          </article>
          <article class="card">
            <div class="icon" aria-hidden="true">&#128757;</div>
            <h3>Rider Delivery Network</h3>
            <p>Live dispatch, OpenStreetMap GPS tracking, and secure PIN delivery verification.</p>
          </article>
          <article class="card">
            <div class="icon" aria-hidden="true">&#128172;</div>
            <h3>Multi-Channel AI Access</h3>
            <p>Use the mobile app or chat with the AI advisor via WhatsApp ({wa_display}) and Telegram ({telegram_label}).</p>
          </article>
        </div>
      </div>
    </section>

    <section id="roles" class="roles">
      <div class="wrap">
        <h2>Built for Everyone in the Supply Chain</h2>
        <div class="grid">
          <article class="card">
            <h3>Farmers</h3>
            <p>Sell listings, track plants, scan crops, manage orders, and link WhatsApp or Telegram for advisor chat.</p>
          </article>
          <article class="card">
            <h3>Buyers</h3>
            <p>Browse and match listings, view crop-health insights, connect with farmers, and track deliveries live.</p>
          </article>
          <article class="card">
            <h3>Riders</h3>
            <p>Go online, accept nearby jobs, share GPS, and complete handoffs with buyer PIN verification.</p>
          </article>
        </div>
      </div>
    </section>

    <section id="install">
      <div class="wrap">
        <h2>Install the Android App</h2>
        <ol class="steps">
          <li>Tap <strong>Download Android App</strong> above to get the latest APK.</li>
          <li>On your phone, allow installation from your browser or files app when prompted.</li>
          <li>Open AgriPilot and sign up as a farmer, buyer, or rider.</li>
        </ol>
        <div class="cta-row" style="margin-top: 1.5rem;">
          <a class="btn btn-primary" href="{download_url}">Download Android App</a>
        </div>
      </div>
    </section>
  </main>

  <footer>
    <div class="wrap">
      <p>AgriPilot &mdash; built with <a href="https://github.com/yaalalabs/agent-kernel">Agent Kernel</a></p>
    </div>
  </footer>
</body>
</html>"""


@router.get("/", response_class=HTMLResponse, include_in_schema=False)
def landing_page():
    return HTMLResponse(content=_build_landing_html())


@router.get("/download", include_in_schema=False)
def download_app():
    return RedirectResponse(url=resolve_app_download_url(), status_code=307)


@router.get("/download/apk", include_in_schema=False)
def download_apk_file():
    local = resolve_apk_path()
    if local is not None:
        return FileResponse(local, media_type="application/vnd.android.package-archive", filename=local.name)
    return RedirectResponse(url="/download", status_code=307)


@router.get("/static/agripilot-icon.png", include_in_schema=False)
def serve_icon():
    return _icon_response()


@router.get("/favicon.ico", include_in_schema=False)
def serve_favicon():
    return _icon_response()
