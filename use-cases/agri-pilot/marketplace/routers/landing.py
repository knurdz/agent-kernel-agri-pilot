"""Public landing page and Android app download routes."""

from __future__ import annotations

import html
import mimetypes
import os
from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse, HTMLResponse, RedirectResponse

from marketplace.channels import public_channel_config

router = APIRouter(tags=["landing"])

_DEFAULT_DOWNLOAD_URL = "https://github.com/yaalalabs/agent-kernel/releases?q=agripilot-mobile"
_DOCS_DIR = Path(__file__).resolve().parents[2] / "docs"
_BRANDING_DIR = _DOCS_DIR / "branding"
_SCREENSHOTS_DIR = _DOCS_DIR / "screenshots"
_ARCHITECTURE_DIR = _DOCS_DIR / "architecture"
_ICON_PATH = _BRANDING_DIR / "agripilot-icon.png"
_ARCHITECTURE_HTML = _ARCHITECTURE_DIR / "agripilot.architecture.html"
_ALLOWED_SCREENSHOTS = frozenset(
    {
        "home.png",
        "advisor.png",
        "plant-detail.png",
        "orders.png",
        "delivery-tracking.jpg",
    }
)


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


def _screenshot_response(filename: str) -> FileResponse:
    if filename not in _ALLOWED_SCREENSHOTS:
        raise HTTPException(status_code=404, detail="Not found")
    path = _SCREENSHOTS_DIR / filename
    if not path.is_file():
        raise HTTPException(status_code=404, detail="Not found")
    media_type = mimetypes.guess_type(filename)[0] or "application/octet-stream"
    return FileResponse(path, media_type=media_type)


def _architecture_response() -> FileResponse:
    if not _ARCHITECTURE_HTML.is_file():
        raise HTTPException(status_code=404, detail="Not found")
    return FileResponse(_ARCHITECTURE_HTML, media_type="text/html")


def _feature_item(text: str) -> str:
    return f"<li>{html.escape(text)}</li>"


def _build_landing_html() -> str:
    channels = public_channel_config()
    wa_me = html.escape(channels.get("whatsapp_wa_me") or "#")
    telegram_base = html.escape(channels.get("telegram_deep_link_base") or "#")
    wa_display = html.escape(channels.get("whatsapp_display_number") or "")
    telegram_label = html.escape(channels.get("telegram_bot_username") or "")
    download_url = "/download"

    ai_advisor = [
        "Photo-based crop diagnosis (HuggingFace ViT) with quality checks and confidence threshold",
        "Treatment advice via ChromaDB RAG with chemical and dosage safety validation",
        "Weather and irrigation forecasts from Open-Meteo — no API key required",
        "Redis-backed conversation memory, case history, and follow-up resolution",
        "Mobile chat thread history via Agent Kernel thread routes",
        "Supervisor handoff-loop guard and knowledge-agent treatment validation",
    ]
    farmer = [
        "Sell listings with crop, quantity, price, category, harvest date, and product photo",
        "Listing analytics: views, connections, and estimated revenue",
        "Plant tracking with photo timeline and derived insights",
        "Quick crop scan — one-time ViT analysis without creating a plant",
        "Import tracked plant health into a sell listing for buyers",
        "Confirm orders, mark ready, and follow live tracking maps",
        "Link WhatsApp or Telegram for advisor chat outside the app",
    ]
    buyer = [
        "Browse and match listings by crop, district, category, quantity, and price",
        "Crop-health insights on listings linked to tracked plants",
        "Express interest via connections; phone numbers revealed after acceptance",
        "Checkout with pickup or rider delivery",
        "Live order tracking with map, ETA, and rider GPS",
    ]
    rider = [
        "Self-register with vehicle confirmation",
        "Go online and share GPS to see nearby delivery jobs by weight and distance",
        "Accept jobs in the app — one active delivery at a time",
        "Post GPS every few seconds with OpenStreetMap tiles (no Google Maps API key)",
        "PIN handoff — enter buyer PIN on the Deliveries tab at drop-off",
    ]

    ai_list = "".join(_feature_item(x) for x in ai_advisor)
    farmer_list = "".join(_feature_item(x) for x in farmer)
    buyer_list = "".join(_feature_item(x) for x in buyer)
    rider_list = "".join(_feature_item(x) for x in rider)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>AgriPilot — From crop diagnosis to doorstep delivery</title>
  <meta name="description" content="AI advisory, farmer marketplace, and live order tracking for farmers, buyers, and riders on Android, WhatsApp, and Telegram." />
  <link rel="icon" href="/favicon.ico" type="image/png" />
  <style>
    :root {{
      --cream: #f4f1ea;
      --cream-dark: #ebe6dc;
      --white: #ffffff;
      --green-50: #ecfdf5;
      --green-100: #d1fae5;
      --green-500: #2d6a4f;
      --green-600: #1b4332;
      --green-700: #14532d;
      --text: #1a1a1a;
      --text-muted: #5c5c5c;
      --text-light: #8a8a8a;
      --radius-sm: 12px;
      --radius-md: 20px;
      --radius-lg: 28px;
      --radius-pill: 999px;
      --shadow-soft: 0 8px 32px rgba(27, 67, 50, 0.08);
      --shadow-card: 0 4px 20px rgba(0, 0, 0, 0.06);
      --max: 1180px;
    }}
    *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
    html {{ scroll-behavior: smooth; }}
    body {{
      font-family: "Segoe UI", system-ui, -apple-system, Roboto, sans-serif;
      background: var(--cream);
      color: var(--text);
      line-height: 1.55;
      -webkit-font-smoothing: antialiased;
    }}
    a {{ color: inherit; text-decoration: none; }}
    img {{ max-width: 100%; display: block; }}
    .wrap {{ width: min(var(--max), 100% - 2.5rem); margin-inline: auto; }}

    /* ---- Nav ---- */
    .site-header {{
      position: sticky; top: 0; z-index: 50;
      background: rgba(244, 241, 234, 0.92);
      backdrop-filter: blur(14px);
      border-bottom: 1px solid rgba(0,0,0,0.05);
    }}
    .nav-bar {{
      display: grid;
      grid-template-columns: 1fr auto 1fr;
      align-items: center;
      gap: 1rem;
      padding: 1.1rem 0;
    }}
    .brand {{
      display: flex; align-items: center; gap: 0.6rem;
      font-weight: 800; font-size: 1rem; letter-spacing: 0.06em;
      text-transform: uppercase; color: var(--green-600);
    }}
    .brand img {{ width: 36px; height: 36px; border-radius: 10px; }}
    .nav-links {{
      display: flex; flex-wrap: wrap; justify-content: center; gap: 1.5rem;
      font-size: 0.72rem; font-weight: 600; letter-spacing: 0.08em;
      text-transform: uppercase; color: var(--text-muted);
    }}
    .nav-links a:hover {{ color: var(--green-600); }}
    .nav-cta {{ display: flex; justify-content: flex-end; }}
    .btn {{
      display: inline-flex; align-items: center; justify-content: center; gap: 0.45rem;
      padding: 0.85rem 1.6rem; border-radius: var(--radius-pill);
      font-weight: 700; font-size: 0.78rem; letter-spacing: 0.06em;
      text-transform: uppercase; border: none; cursor: pointer;
      transition: transform 0.15s ease, box-shadow 0.15s ease, background 0.15s ease;
    }}
    .btn:hover {{ transform: translateY(-1px); }}
    .btn-primary {{
      background: var(--green-500); color: var(--white);
      box-shadow: 0 6px 20px rgba(45, 106, 79, 0.35);
    }}
    .btn-primary:hover {{ background: var(--green-600); box-shadow: 0 8px 24px rgba(45, 106, 79, 0.4); }}
    .btn-ghost {{
      background: transparent; color: var(--text);
      border: 1.5px solid rgba(0,0,0,0.12);
    }}
    .btn-ghost:hover {{ border-color: var(--green-500); color: var(--green-600); }}
    .btn-sm {{ padding: 0.65rem 1.2rem; font-size: 0.72rem; }}

    /* ---- Hero ---- */
    .hero {{ padding: 3rem 0 2rem; text-align: center; }}
    .hero-headline {{
      display: flex; flex-wrap: wrap; align-items: center; justify-content: center;
      gap: 0.35rem 0.75rem;
      font-size: clamp(2.4rem, 6vw, 4.5rem);
      font-weight: 800; line-height: 1.05; letter-spacing: -0.02em;
      color: var(--text); margin-bottom: 1.75rem;
    }}
    .hero-headline .pill-img {{
      display: inline-block; width: clamp(4.5rem, 14vw, 7.5rem);
      height: clamp(2.8rem, 8vw, 4.5rem); border-radius: var(--radius-pill);
      overflow: hidden; vertical-align: middle; box-shadow: var(--shadow-soft);
    }}
    .hero-headline .pill-img img {{ width: 100%; height: 100%; object-fit: cover; object-position: top; }}
    .hero-sub {{
      max-width: 34rem; margin: 0 auto 2rem;
      font-size: 1.05rem; color: var(--text-muted);
    }}
    .hero-actions {{
      display: flex; flex-wrap: wrap; gap: 0.85rem; justify-content: center;
      margin-bottom: 2.5rem;
    }}
    .hero-phone {{
      display: flex; justify-content: center; margin-top: 1rem;
    }}
    .phone-frame {{
      width: min(280px, 72vw);
      background: var(--white);
      border-radius: 36px;
      padding: 10px;
      box-shadow: var(--shadow-soft), 0 0 0 1px rgba(0,0,0,0.06);
    }}
    .phone-frame img {{
      border-radius: 28px;
      width: 100%;
      height: auto;
    }}

    /* ---- Trust bar ---- */
    .trust-bar {{
      background: var(--white);
      border-block: 1px solid rgba(0,0,0,0.06);
      padding: 1.25rem 0;
    }}
    .trust-inner {{
      display: flex; flex-wrap: wrap; align-items: center;
      justify-content: space-between; gap: 1rem;
    }}
    .trust-channels {{
      display: flex; flex-wrap: wrap; gap: 1.5rem 2.5rem;
      font-size: 0.85rem; font-weight: 600; color: var(--text-muted);
    }}
    .trust-channels span {{ color: var(--green-600); }}
    .scroll-hint {{
      font-size: 0.7rem; font-weight: 700; letter-spacing: 0.12em;
      text-transform: uppercase; color: var(--text-light);
    }}

    /* ---- Section common ---- */
    .section {{ padding: 4.5rem 0; }}
    .section-tag {{
      display: block; text-align: center;
      font-size: 0.72rem; font-weight: 700; letter-spacing: 0.14em;
      text-transform: uppercase; color: var(--green-500); margin-bottom: 0.75rem;
    }}
    .section-title {{
      text-align: center; font-size: clamp(1.75rem, 3.5vw, 2.5rem);
      font-weight: 800; line-height: 1.15; letter-spacing: -0.02em;
      max-width: 28ch; margin: 0 auto 1rem;
    }}
    .section-lead {{
      text-align: center; max-width: 42rem; margin: 0 auto 2.5rem;
      color: var(--text-muted); font-size: 1rem;
    }}
    .section-link {{
      display: inline-flex; align-items: center; gap: 0.35rem;
      margin: 0 auto 2rem; font-size: 0.78rem; font-weight: 700;
      letter-spacing: 0.08em; text-transform: uppercase; color: var(--green-600);
    }}
    .section-link-wrap {{ text-align: center; }}

    /* ---- App showcase ---- */
    .showcase-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
      gap: 1.25rem;
      align-items: end;
    }}
    .showcase-item {{
      background: var(--white);
      border-radius: var(--radius-md);
      padding: 1rem;
      box-shadow: var(--shadow-card);
      text-align: center;
    }}
    .showcase-item.featured {{
      grid-column: span 1;
      padding: 1.25rem;
    }}
    @media (min-width: 900px) {{
      .showcase-grid {{
        grid-template-columns: 1fr 1.15fr 1fr 1fr 1fr;
        gap: 1rem;
      }}
      .showcase-item:nth-child(3) {{ transform: translateY(-12px); }}
    }}
    .showcase-phone {{
      border-radius: 22px;
      overflow: hidden;
      margin-bottom: 0.85rem;
      box-shadow: 0 4px 16px rgba(0,0,0,0.08);
    }}
    .showcase-phone img {{ width: 100%; height: auto; }}
    .showcase-item h3 {{
      font-size: 0.9rem; font-weight: 700; margin-bottom: 0.25rem;
    }}
    .showcase-item p {{
      font-size: 0.8rem; color: var(--text-muted); line-height: 1.4;
    }}

    /* ---- Feature cards (Hope Rise style) ---- */
    .cards-3 {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
      gap: 1.25rem;
    }}
    .feature-card {{
      background: var(--white);
      border-radius: var(--radius-md);
      padding: 2rem 1.75rem;
      box-shadow: var(--shadow-card);
      display: flex; flex-direction: column;
      min-height: 100%;
    }}
    .feature-card h3 {{
      font-size: 1.15rem; font-weight: 800; margin-bottom: 0.75rem;
      letter-spacing: -0.01em;
    }}
    .feature-card p {{
      color: var(--text-muted); font-size: 0.92rem; margin-bottom: 1.25rem;
      flex: 1;
    }}
    .feature-card ul {{
      list-style: none; margin-bottom: 1.5rem;
    }}
    .feature-card li {{
      position: relative; padding-left: 1.1rem; margin-bottom: 0.55rem;
      font-size: 0.88rem; color: var(--text-muted); line-height: 1.45;
    }}
    .feature-card li::before {{
      content: "";
      position: absolute; left: 0; top: 0.55em;
      width: 5px; height: 5px; border-radius: 50%;
      background: var(--green-500);
    }}
    .card-arrow {{
      align-self: flex-start;
      width: 44px; height: 44px; border-radius: 50%;
      border: 1.5px solid rgba(0,0,0,0.1);
      display: flex; align-items: center; justify-content: center;
      font-size: 1.1rem; color: var(--green-600);
      transition: background 0.15s, border-color 0.15s;
    }}
    .feature-card:hover .card-arrow {{
      background: var(--green-50); border-color: var(--green-500);
    }}

    /* ---- Role blocks ---- */
    .role-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
      gap: 1.5rem;
    }}
    .role-block {{
      background: var(--white);
      border-radius: var(--radius-lg);
      padding: 2rem;
      box-shadow: var(--shadow-card);
    }}
    .role-block h3 {{
      font-size: 1.35rem; font-weight: 800; margin-bottom: 0.35rem;
      color: var(--green-600);
    }}
    .role-block .role-tag {{
      font-size: 0.72rem; font-weight: 700; letter-spacing: 0.1em;
      text-transform: uppercase; color: var(--text-light); margin-bottom: 1rem;
    }}
    .role-block ul {{ list-style: none; }}
    .role-block li {{
      padding: 0.65rem 0;
      border-bottom: 1px solid rgba(0,0,0,0.06);
      font-size: 0.9rem; color: var(--text-muted);
    }}
    .role-block li:last-child {{ border-bottom: none; }}

    /* ---- Install ---- */
    .install-panel {{
      background: var(--white);
      border-radius: var(--radius-lg);
      padding: 3rem 2rem;
      text-align: center;
      box-shadow: var(--shadow-soft);
      max-width: 640px;
      margin: 0 auto;
    }}
    .install-steps {{
      list-style: none; text-align: left;
      max-width: 420px; margin: 1.5rem auto 2rem;
    }}
    .install-steps li {{
      counter-increment: install;
      position: relative; padding-left: 2.5rem; margin-bottom: 1rem;
      font-size: 0.95rem; color: var(--text-muted);
    }}
    .install-steps {{ counter-reset: install; }}
    .install-steps li::before {{
      content: counter(install);
      position: absolute; left: 0; top: 0;
      width: 1.75rem; height: 1.75rem; line-height: 1.75rem;
      text-align: center; border-radius: 50%;
      background: var(--green-500); color: var(--white);
      font-size: 0.8rem; font-weight: 700;
    }}
    .note-bar {{
      margin-top: 2rem; padding: 1rem 1.25rem;
      background: var(--green-50); border-radius: var(--radius-sm);
      font-size: 0.85rem; color: var(--text-muted); text-align: center;
    }}

    /* ---- Footer ---- */
    footer {{
      padding: 2.5rem 0 3rem;
      text-align: center; font-size: 0.85rem; color: var(--text-light);
      border-top: 1px solid rgba(0,0,0,0.06);
    }}
    footer a {{ color: var(--green-600); font-weight: 600; }}

    /* ---- Mobile nav ---- */
    @media (max-width: 860px) {{
      .nav-bar {{ grid-template-columns: 1fr auto; }}
      .nav-links {{ display: none; }}
      .nav-cta {{ grid-column: 2; }}
    }}
    @media (max-width: 520px) {{
      .hero-headline {{ font-size: 2rem; }}
      .hero-actions {{ flex-direction: column; align-items: stretch; }}
      .hero-actions .btn {{ width: 100%; }}
    }}
  </style>
</head>
<body>
  <header class="site-header">
    <div class="wrap nav-bar">
      <a class="brand" href="/">
        <img src="/static/agripilot-icon.png" alt="" width="36" height="36" />
        AgriPilot
      </a>
      <nav class="nav-links" aria-label="Primary">
        <a href="#app">App</a>
        <a href="#advisor">Advisor</a>
        <a href="#farmer">Farmer</a>
        <a href="#buyer">Buyer</a>
        <a href="#rider">Rider</a>
        <a href="/architecture">Architecture</a>
        <a href="/docs">API</a>
      </nav>
      <div class="nav-cta">
        <a class="btn btn-primary btn-sm" href="{download_url}">Download</a>
      </div>
    </div>
  </header>

  <main>
    <section class="hero">
      <div class="wrap">
        <h1 class="hero-headline">
          <span>Agri</span>
          <span class="pill-img"><img src="/static/screenshots/home.png" alt="AgriPilot home screen" /></span>
          <span>Pilot</span>
          <span>is</span>
          <span>Support</span>
        </h1>
        <p class="hero-sub">
          From crop diagnosis to doorstep delivery — an agentic platform for farmers, buyers, and riders with AI advisory on Android, WhatsApp, and Telegram.
        </p>
        <div class="hero-actions">
          <a class="btn btn-primary" href="{download_url}">Download Android App</a>
          <a class="btn btn-ghost" href="#advisor">Explore features &#8594;</a>
        </div>
        <div class="hero-phone">
          <div class="phone-frame">
            <img src="/static/screenshots/home.png" alt="AgriPilot farmer home — plants, listings, and Ask AgriPilot" width="260" height="520" />
          </div>
        </div>
      </div>
    </section>

    <div class="trust-bar">
      <div class="wrap trust-inner">
        <div class="trust-channels">
          <div><span>Android</span> mobile app</div>
          <div><span>WhatsApp</span>{f" · {wa_display}" if wa_display else ""} advisor</div>
          <div><span>Telegram</span>{f" · @{telegram_label}" if telegram_label else ""} bot</div>
        </div>
        <div class="scroll-hint">Scroll down</div>
      </div>
    </div>

    <section id="app" class="section">
      <div class="wrap">
        <span class="section-tag">Mobile app</span>
        <h2 class="section-title">One platform from field to doorstep</h2>
        <p class="section-lead">
          Diagnose crops, track plant health, manage sell listings, coordinate orders, and follow live delivery — payment is cash/off-platform; maps use OpenStreetMap with optional OSRM routing on the server.
        </p>
        <div class="showcase-grid">
          <article class="showcase-item">
            <div class="showcase-phone">
              <img src="/static/screenshots/home.png" alt="Farmer home with plants and listings" loading="lazy" />
            </div>
            <h3>Farmer home</h3>
            <p>Plants, listings, and one-tap access to the AI advisor.</p>
          </article>
          <article class="showcase-item">
            <div class="showcase-phone">
              <img src="/static/screenshots/advisor.png" alt="AI advisor chat with crop diagnosis advice" loading="lazy" />
            </div>
            <h3>AI advisor</h3>
            <p>Photo diagnosis and validated treatment advice in chat.</p>
          </article>
          <article class="showcase-item featured">
            <div class="showcase-phone">
              <img src="/static/screenshots/plant-detail.png" alt="Plant tracking with photo timeline" loading="lazy" />
            </div>
            <h3>Plant tracking</h3>
            <p>Photo timeline, growth stage, and diagnosis history per crop.</p>
          </article>
          <article class="showcase-item">
            <div class="showcase-phone">
              <img src="/static/screenshots/orders.png" alt="Farmer order management and dispatch" loading="lazy" />
            </div>
            <h3>Orders</h3>
            <p>Confirm quantity, dispatch riders, and track fulfillment.</p>
          </article>
          <article class="showcase-item">
            <div class="showcase-phone">
              <img src="/static/screenshots/delivery-tracking.jpg" alt="Live rider delivery tracking on map" loading="lazy" />
            </div>
            <h3>Live delivery</h3>
            <p>OSM map, route ETA, progress steps, and PIN handoff.</p>
          </article>
        </div>
      </div>
    </section>

    <section id="advisor" class="section" style="background: var(--white);">
      <div class="wrap">
        <span class="section-tag">AI advisor</span>
        <h2 class="section-title">Intelligent crop support for every role</h2>
        <p class="section-lead">
          LangGraph multi-agent routing with vision, knowledge, and resource specialists. The agent explains marketplace and delivery status but never creates orders or mutates order state — those actions are REST-only in the mobile app.
        </p>
        <div class="cards-3">
          <article class="feature-card">
            <h3>Diagnose &amp; treat</h3>
            <p>Photo-based disease detection and safety-validated treatment recommendations.</p>
            <ul>{ai_list[:2]}</ul>
            <span class="card-arrow" aria-hidden="true">&#8594;</span>
          </article>
          <article class="feature-card">
            <h3>Weather &amp; memory</h3>
            <p>Forecasts and irrigation guidance with durable session context across channels.</p>
            <ul>{ai_list[2:4]}</ul>
            <span class="card-arrow" aria-hidden="true">&#8594;</span>
          </article>
          <article class="feature-card">
            <h3>Safety &amp; threads</h3>
            <p>Guardrails, handoff-loop detection, and mobile chat thread history.</p>
            <ul>{ai_list[4:]}</ul>
            <span class="card-arrow" aria-hidden="true">&#8594;</span>
          </article>
        </div>
        <div class="section-link-wrap" style="margin-top: 2rem;">
          <a class="section-link" href="/architecture">View runtime architecture</a>
          &nbsp;&nbsp;
          <a class="section-link" href="{wa_me}">WhatsApp advisor</a>
          &nbsp;&nbsp;
          <a class="section-link" href="{telegram_base}">Telegram bot</a>
        </div>
      </div>
    </section>

    <section id="farmer" class="section">
      <div class="wrap">
        <span class="section-tag">Farmer</span>
        <h2 class="section-title">Sell, track, and fulfill from your farm</h2>
        <div class="role-grid">
          <article class="role-block">
            <div class="role-tag">Marketplace &amp; plants</div>
            <h3>Listings &amp; tracking</h3>
            <ul>{farmer_list[:5]}</ul>
          </article>
          <article class="role-block">
            <div class="role-tag">Orders &amp; channels</div>
            <h3>Fulfillment &amp; chat</h3>
            <ul>{farmer_list[5:]}</ul>
          </article>
        </div>
      </div>
    </section>

    <section id="buyer" class="section" style="background: var(--white);">
      <div class="wrap">
        <span class="section-tag">Buyer</span>
        <h2 class="section-title">Discover produce and track delivery</h2>
        <div class="role-grid">
          <article class="role-block">
            <div class="role-tag">Discovery</div>
            <h3>Browse &amp; connect</h3>
            <ul>{buyer_list[:3]}</ul>
          </article>
          <article class="role-block">
            <div class="role-tag">Checkout</div>
            <h3>Pickup or delivery</h3>
            <ul>{buyer_list[3:]}</ul>
          </article>
        </div>
      </div>
    </section>

    <section id="rider" class="section">
      <div class="wrap">
        <span class="section-tag">Rider</span>
        <h2 class="section-title">Dispatch, navigate, and hand off</h2>
        <div class="role-block" style="max-width: 640px; margin: 0 auto;">
          <div class="role-tag">Delivery network</div>
          <h3>On the road</h3>
          <ul>{rider_list}</ul>
        </div>
      </div>
    </section>

    <section id="install" class="section" style="background: var(--white);">
      <div class="wrap">
        <div class="install-panel">
          <span class="section-tag">Get started</span>
          <h2 class="section-title" style="font-size: 1.75rem;">Install the Android app</h2>
          <ol class="install-steps">
            <li>Download the latest <strong>agripilot-*.apk</strong> from GitHub Releases.</li>
            <li>On your phone, allow installation from your browser or files app.</li>
            <li>Open AgriPilot and sign up as a farmer, buyer, or rider.</li>
          </ol>
          <a class="btn btn-primary" href="{download_url}">Download Android App</a>
          <p class="note-bar">
            Production builds use HTTPS via Caddy. Release APKs are published by the AgriPilot Mobile Release workflow with the API URL baked in at build time.
          </p>
        </div>
      </div>
    </section>
  </main>

  <footer>
    <div class="wrap">
      <p>AgriPilot &mdash; built with <a href="https://github.com/yaalalabs/agent-kernel">Agent Kernel</a> &middot; <a href="/docs">API docs</a></p>
    </div>
  </footer>
</body>
</html>"""


@router.get("/", response_class=HTMLResponse, include_in_schema=False)
def landing_page():
    return HTMLResponse(content=_build_landing_html())


@router.get("/architecture", include_in_schema=False)
def architecture_page():
    return _architecture_response()


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


@router.get("/static/screenshots/{filename}", include_in_schema=False)
def serve_screenshot(filename: str):
    return _screenshot_response(filename)


@router.get("/favicon.ico", include_in_schema=False)
def serve_favicon():
    return _icon_response()
