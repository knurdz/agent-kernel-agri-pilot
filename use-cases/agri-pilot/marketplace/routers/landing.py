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
        "telegram-chat.jpg",
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


def _render_list_items(items: list[str]) -> str:
    return "".join(f"<li>{html.escape(item)}</li>" for item in items)


def _build_landing_html() -> str:
    channels = public_channel_config()
    wa_me = html.escape(channels.get("whatsapp_wa_me") or "https://wa.me/94771234567")
    telegram_base = html.escape(channels.get("telegram_deep_link_base") or "https://t.me/agripilot_bot")
    wa_display = html.escape(channels.get("whatsapp_display_number") or "+94 77 123 4567")
    telegram_label = html.escape(channels.get("telegram_bot_username") or "agripilot_bot")
    contact_email = "support@knurdz.org"
    contact_phone = "+94 77 123 4567"
    contact_phone_raw = "+94771234567"
    repo_url = "https://github.com/knurdz/agent-kernel-agri-pilot"
    framework_url = "https://github.com/yaalalabs/agent-kernel"
    download_url = "/download"

    # AI Advisor Feature items
    advisor_diagnosis_items = [
        "Photo-based disease detection using HuggingFace Vision Transformer (ViT)",
        "Image quality validator checking blur, lighting, and foliage presence",
        "Top-3 diagnosis predictions with calibrated confidence scores",
        "Safety backstops preventing handoff loops and unverified chemicals",
    ]
    advisor_treatment_items = [
        "Agricultural RAG over ChromaDB domain knowledge docs",
        "Safety validation gate for chemical treatments and dosage rates",
        "Open-Meteo forecasts for rainfall, temperature, and spray timing",
        "Persistent session memory with follow-up resolution (e.g. 'it is getting worse')",
    ]
    advisor_channels_items = [
        "JWT-authenticated mobile chat threads with image attachment upload",
        "Fast-ack WhatsApp webhook support for instant field access",
        "Telegram Bot integration with phone-number verification gate",
        "Thread history restoration across mobile app and chat channels",
    ]

    # Supply Chain Role items
    farmer_marketplace_items = [
        "Create listings with crop type, quantity, price/kg, category, and harvest date",
        "Upload high-resolution crop photos to showcase harvest quality",
        "Listing analytics dashboard: view counts, connection requests, and estimated revenue",
        "Import tracked plant health directly into sell listings for full buyer transparency",
        "Manage incoming order requests, confirm available quantities, and mark orders ready",
        "Link WhatsApp or Telegram to chat with the AI agronomy advisor anywhere",
    ]
    farmer_plants_items = [
        "Track individual crops with observation photos and growth timeline",
        "Quick crop scan: instant ViT disease diagnosis without creating a plant entry",
        "Derived health series, disease trends, and estimated days to harvest",
        "Automated case history logging: crop, disease, severity, and advice summary",
    ]

    buyer_discovery_items = [
        "Browse and filter listings by crop, district, category, quantity, and price",
        "Intelligent ranked match algorithm finding produce matching exact requirements",
        "Inspect verified crop-health observation history and diagnosis timeline",
        "Express interest via connections; phone numbers revealed upon acceptance",
        "Direct checkout with self-pickup or rider doorstep delivery option",
        "Real-time order tracking with interactive OpenStreetMap, rider GPS, and live ETA",
    ]

    rider_logistics_items = [
        "Quick rider self-registration with vehicle confirmation (bike, three-wheeler, truck)",
        "One-tap online/offline toggle to receive nearby delivery jobs",
        "View job requests with pickup and delivery district, cargo weight, and route distance",
        "Live GPS location publishing with turn-by-turn road routing via OSRM",
        "Interactive delivery map with next-stop indicator and ETA countdown",
        "Secure 4-6 digit buyer PIN handoff confirmation on the Deliveries tab",
    ]

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>AgriPilot: No Middlemen. Farmers Earn More. Fresh Food for Less.</title>
  <meta name="description" content="Cut out middlemen: farmers earn more, consumers get fresh food at lower cost, and citizens deliver to earn, all powered by multi-agent AI on Android, WhatsApp, and Telegram." />
  <link rel="icon" href="/favicon.ico" type="image/png" />
  <style>
    :root {{
      --cream: #F8F6F0;
      --cream-card: #FFFFFF;
      --cream-accent: #EFECE3;
      --green-50: #ECFDF5;
      --green-100: #D1FAE5;
      --green-200: #A7F3D0;
      --green-500: #10B981;
      --green-600: #059669;
      --green-700: #047857;
      --green-800: #065F46;
      --green-900: #064E3B;
      --dark: #111827;
      --dark-muted: #4B5563;
      --dark-light: #6B7280;
      --border: rgba(0, 0, 0, 0.08);
      --border-green: rgba(5, 150, 105, 0.2);
      --shadow-sm: 0 2px 8px rgba(0, 0, 0, 0.04);
      --shadow-md: 0 8px 24px rgba(6, 78, 59, 0.07);
      --shadow-lg: 0 16px 40px rgba(6, 78, 59, 0.1);
      --radius-sm: 10px;
      --radius-md: 18px;
      --radius-lg: 26px;
      --radius-pill: 9999px;
      --max-width: 1200px;
    }}
    *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
    html {{
      scroll-behavior: smooth;
      font-size: 16px;
      overflow-x: hidden;
    }}
    body {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
      background-color: var(--cream);
      color: var(--dark);
      line-height: 1.6;
      overflow-x: hidden;
      -webkit-font-smoothing: antialiased;
    }}
    a {{ color: inherit; text-decoration: none; transition: color 0.15s ease; }}
    img {{ max-width: 100%; height: auto; display: block; }}
    .container {{ width: min(var(--max-width), 100% - 2.5rem); margin-inline: auto; }}

    /* Top Utility Bar */
    .top-bar {{
      background: var(--green-900);
      color: #E6F4EA;
      font-size: 0.8rem;
      padding: 0.5rem 0;
      border-bottom: 1px solid rgba(255,255,255,0.1);
    }}
    .top-bar-inner {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      flex-wrap: wrap;
      gap: 0.5rem;
    }}
    .top-contacts {{
      display: flex;
      align-items: center;
      gap: 1.25rem;
      flex-wrap: wrap;
    }}
    .top-contact-link {{
      color: #D1FAE5;
      display: inline-flex;
      align-items: center;
      gap: 0.35rem;
      font-weight: 500;
    }}
    .top-contact-link:hover {{ color: #ffffff; text-decoration: underline; }}
    .top-badge {{
      background: rgba(255, 255, 255, 0.15);
      padding: 0.15rem 0.55rem;
      border-radius: var(--radius-pill);
      font-size: 0.72rem;
      font-weight: 600;
      letter-spacing: 0.04em;
    }}

    /* Main Navigation Header */
    .header {{
      position: sticky;
      top: 0;
      z-index: 100;
      background: rgba(248, 246, 240, 0.94);
      backdrop-filter: blur(16px);
      border-bottom: 1px solid var(--border);
    }}
    .nav {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 0.9rem 0;
      gap: 1rem;
    }}
    .brand {{
      display: flex;
      align-items: center;
      gap: 0.65rem;
      font-weight: 800;
      font-size: 1.25rem;
      color: var(--green-900);
      letter-spacing: -0.01em;
    }}
    .brand-logo {{
      width: 38px;
      height: 38px;
      border-radius: 10px;
      box-shadow: 0 2px 6px rgba(6, 78, 59, 0.15);
    }}
    .brand-tagline {{
      font-size: 0.7rem;
      font-weight: 600;
      color: var(--green-600);
      text-transform: uppercase;
      letter-spacing: 0.08em;
      display: block;
      margin-top: -3px;
    }}
    .nav-menu {{
      display: flex;
      align-items: center;
      gap: 1.4rem;
      list-style: none;
    }}
    .nav-link {{
      font-size: 0.85rem;
      font-weight: 600;
      color: var(--dark-muted);
      letter-spacing: 0.02em;
    }}
    .nav-link:hover {{ color: var(--green-700); }}
    .nav-actions {{
      display: flex;
      align-items: center;
      gap: 0.75rem;
    }}

    /* Button Styles */
    .btn {{
      display: inline-flex;
      align-items: center;
      justify-content: center;
      gap: 0.45rem;
      font-weight: 600;
      font-size: 0.9rem;
      padding: 0.75rem 1.4rem;
      border-radius: var(--radius-pill);
      border: 1px solid transparent;
      cursor: pointer;
      transition: all 0.18s cubic-bezier(0.16, 1, 0.3, 1);
      white-space: nowrap;
    }}
    .btn:hover {{ transform: translateY(-1px); }}
    .btn-primary {{
      background: linear-gradient(135deg, var(--green-600), var(--green-800));
      color: #ffffff;
      box-shadow: 0 4px 14px rgba(5, 150, 105, 0.35);
    }}
    .btn-primary:hover {{
      background: linear-gradient(135deg, var(--green-700), var(--green-900));
      box-shadow: 0 6px 18px rgba(5, 150, 105, 0.45);
    }}
    .btn-secondary {{
      background: var(--cream-card);
      color: var(--green-800);
      border-color: var(--border-green);
      box-shadow: var(--shadow-sm);
    }}
    .btn-secondary:hover {{
      background: var(--green-50);
      border-color: var(--green-600);
      color: var(--green-900);
    }}
    .btn-ghost {{
      background: transparent;
      color: var(--dark);
      border-color: var(--border);
    }}
    .btn-ghost:hover {{
      background: var(--cream-accent);
      color: var(--green-900);
    }}
    .btn-sm {{
      padding: 0.5rem 1rem;
      font-size: 0.8rem;
    }}
    .badge-pill {{
      font-size: 0.68rem;
      font-weight: 700;
      letter-spacing: 0.05em;
      text-transform: uppercase;
      padding: 0.2rem 0.6rem;
      border-radius: var(--radius-pill);
      background: var(--green-100);
      color: var(--green-800);
    }}

    /* Hero Section */
    .hero {{
      padding: 3.5rem 0 2.5rem;
      text-align: center;
    }}
    .hero-tag-wrap {{
      margin-bottom: 1.25rem;
    }}
    .hero-tag {{
      display: inline-flex;
      align-items: center;
      gap: 0.4rem;
      background: #E6F4EA;
      color: var(--green-800);
      font-size: 0.78rem;
      font-weight: 700;
      letter-spacing: 0.06em;
      text-transform: uppercase;
      padding: 0.35rem 0.9rem;
      border-radius: var(--radius-pill);
      border: 1px solid rgba(5, 150, 105, 0.2);
    }}
    .hero-title {{
      font-size: clamp(2.2rem, 5vw, 3.8rem);
      font-weight: 800;
      line-height: 1.12;
      color: var(--dark);
      letter-spacing: -0.03em;
      max-width: 820px;
      margin: 0 auto 1.25rem;
    }}
    .hero-title span.accent {{
      color: var(--green-700);
    }}
    .hero-subtitle {{
      font-size: clamp(1.05rem, 2vw, 1.2rem);
      color: var(--dark-muted);
      max-width: 680px;
      margin: 0 auto 2rem;
      line-height: 1.65;
    }}
    .hero-cta-group {{
      display: flex;
      justify-content: center;
      align-items: center;
      flex-wrap: wrap;
      gap: 0.9rem;
      margin-bottom: 2.5rem;
    }}

    /* Hero value proposition (top highlight) */
    .hero-agent-badge {{
      display: inline-flex;
      align-items: center;
      gap: 0.45rem;
      font-size: 0.78rem;
      font-weight: 700;
      color: var(--green-800);
      background: linear-gradient(135deg, var(--green-50), #E8F5E9);
      border: 1px solid rgba(22, 101, 52, 0.15);
      padding: 0.4rem 0.9rem;
      border-radius: var(--radius-pill);
      margin-bottom: 1.25rem;
      letter-spacing: 0.02em;
      text-transform: uppercase;
    }}
    .hero-value-strip {{
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 1rem;
      max-width: 960px;
      margin: 0 auto 2.25rem;
    }}
    .value-pillar {{
      background: var(--cream-card);
      border: 1px solid var(--border);
      border-radius: var(--radius-md);
      padding: 1.35rem 1.15rem;
      box-shadow: var(--shadow-sm);
      text-align: center;
      position: relative;
      overflow: hidden;
      transition: transform 0.2s ease, box-shadow 0.2s ease;
    }}
    .value-pillar:hover {{
      transform: translateY(-3px);
      box-shadow: var(--shadow-md);
    }}
    .value-pillar::before {{
      content: "";
      position: absolute;
      top: 0;
      left: 0;
      right: 0;
      height: 3px;
      background: var(--green-600);
    }}
    .value-pillar-icon {{
      font-size: 1.75rem;
      margin-bottom: 0.5rem;
      line-height: 1;
    }}
    .value-pillar-title {{
      font-size: 1rem;
      font-weight: 800;
      color: var(--dark);
      margin-bottom: 0.35rem;
      letter-spacing: -0.01em;
    }}
    .value-pillar-desc {{
      font-size: 0.82rem;
      color: var(--dark-muted);
      line-height: 1.45;
    }}
    @media (max-width: 768px) {{
      .hero-value-strip {{
        grid-template-columns: 1fr;
        gap: 0.85rem;
      }}
    }}

    /* Trust Highlights Ticker */
    .highlights-bar {{
      background: var(--cream-card);
      border: 1px solid var(--border);
      border-radius: var(--radius-md);
      padding: 1rem 1.5rem;
      box-shadow: var(--shadow-sm);
      max-width: 980px;
      margin: 0 auto 3rem;
    }}
    .highlights-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
      gap: 1rem;
      text-align: left;
    }}
    .highlight-item {{
      display: flex;
      align-items: center;
      gap: 0.65rem;
    }}
    .highlight-icon {{
      width: 32px;
      height: 32px;
      border-radius: 50%;
      background: var(--green-50);
      color: var(--green-700);
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 1rem;
      flex-shrink: 0;
    }}
    .highlight-text {{
      font-size: 0.85rem;
      font-weight: 600;
      color: var(--dark);
    }}
    .highlight-sub {{
      font-size: 0.72rem;
      color: var(--dark-light);
      display: block;
    }}

    /* Hero Phone Mockup */
    .hero-preview-wrap {{
      display: flex;
      justify-content: center;
      align-items: center;
      gap: 1.5rem;
      margin-top: 1rem;
      perspective: 1000px;
    }}
    .phone-mockup {{
      width: min(290px, 80vw);
      background: #FFFFFF;
      border-radius: 38px;
      padding: 10px;
      box-shadow: var(--shadow-lg), 0 0 0 1px rgba(0, 0, 0, 0.08);
      border: 4px solid #1F2937;
    }}
    .phone-mockup img {{
      border-radius: 28px;
      width: 100%;
      height: auto;
    }}
    .phone-mockup.secondary {{
      display: none;
    }}
    @media (min-width: 768px) {{
      .phone-mockup.secondary {{
        display: block;
        width: 250px;
        opacity: 0.95;
        transform: translateY(20px);
      }}
    }}

    /* Common Section Styles */
    .section {{
      padding: 5rem 0;
    }}
    .section-alt {{
      background: #FFFFFF;
      border-top: 1px solid var(--border);
      border-bottom: 1px solid var(--border);
    }}
    .section-header {{
      text-align: center;
      max-width: 680px;
      margin: 0 auto 3rem;
    }}
    .section-badge {{
      display: inline-block;
      font-size: 0.75rem;
      font-weight: 700;
      letter-spacing: 0.1em;
      text-transform: uppercase;
      color: var(--green-600);
      margin-bottom: 0.6rem;
    }}
    .section-title {{
      font-size: clamp(1.8rem, 3.5vw, 2.5rem);
      font-weight: 800;
      line-height: 1.18;
      letter-spacing: -0.02em;
      color: var(--dark);
      margin-bottom: 0.85rem;
    }}
    .section-desc {{
      font-size: 1rem;
      color: var(--dark-muted);
      line-height: 1.6;
    }}

    /* 3-Column Feature Cards (Hope Rise Style) */
    .cards-grid-3 {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
      gap: 1.5rem;
    }}
    .card-feature {{
      background: var(--cream-card);
      border: 1px solid var(--border);
      border-radius: var(--radius-lg);
      padding: 2.2rem 1.85rem;
      box-shadow: var(--shadow-sm);
      display: flex;
      flex-direction: column;
      transition: transform 0.2s ease, box-shadow 0.2s ease, border-color 0.2s ease;
    }}
    .card-feature:hover {{
      transform: translateY(-3px);
      box-shadow: var(--shadow-md);
      border-color: var(--border-green);
    }}
    .card-icon-pill {{
      display: inline-flex;
      align-items: center;
      justify-content: center;
      width: 46px;
      height: 46px;
      border-radius: var(--radius-md);
      background: var(--green-50);
      color: var(--green-700);
      font-size: 1.4rem;
      margin-bottom: 1.25rem;
    }}
    .card-feature-title {{
      font-size: 1.25rem;
      font-weight: 700;
      color: var(--dark);
      margin-bottom: 0.6rem;
      letter-spacing: -0.01em;
    }}
    .card-feature-desc {{
      font-size: 0.92rem;
      color: var(--dark-muted);
      margin-bottom: 1.25rem;
      line-height: 1.55;
    }}
    .card-feature-list {{
      list-style: none;
      margin-bottom: 1.5rem;
      flex-grow: 1;
    }}
    .card-feature-list li {{
      position: relative;
      padding-left: 1.3rem;
      margin-bottom: 0.65rem;
      font-size: 0.88rem;
      color: var(--dark-muted);
      line-height: 1.45;
    }}
    .card-feature-list li::before {{
      content: "";
      position: absolute;
      left: 0;
      top: 0.45rem;
      width: 6px;
      height: 6px;
      border-radius: 50%;
      background: var(--green-500);
    }}
    .card-footer-action {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding-top: 1rem;
      border-top: 1px solid rgba(0, 0, 0, 0.05);
      font-size: 0.82rem;
      font-weight: 700;
      color: var(--green-700);
    }}
    .circle-arrow {{
      width: 36px;
      height: 36px;
      border-radius: 50%;
      background: var(--green-50);
      color: var(--green-700);
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 1rem;
      transition: background 0.15s, color 0.15s;
    }}
    .card-feature:hover .circle-arrow {{
      background: var(--green-600);
      color: #FFFFFF;
    }}

    /* App Screens Gallery Grid */
    .screens-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
      gap: 1.25rem;
      align-items: stretch;
    }}
    @media (min-width: 1024px) {{
      .screens-grid {{
        grid-template-columns: repeat(5, 1fr);
      }}
    }}
    .screen-card {{
      background: var(--cream-card);
      border: 1px solid var(--border);
      border-radius: var(--radius-md);
      padding: 1rem;
      box-shadow: var(--shadow-sm);
      text-align: center;
      display: flex;
      flex-direction: column;
      transition: transform 0.2s ease, box-shadow 0.2s ease;
    }}
    .screen-card:hover {{
      transform: translateY(-4px);
      box-shadow: var(--shadow-md);
    }}
    .screen-img-box {{
      border-radius: 14px;
      overflow: hidden;
      margin-bottom: 0.9rem;
      border: 1px solid rgba(0, 0, 0, 0.06);
      background: #FAFAFA;
      box-shadow: 0 4px 12px rgba(0,0,0,0.04);
    }}
    .screen-img-box img {{
      width: 100%;
      height: auto;
      object-fit: cover;
    }}
    .screen-tag-pill {{
      display: inline-block;
      font-size: 0.68rem;
      font-weight: 700;
      color: var(--green-700);
      background: var(--green-50);
      padding: 0.15rem 0.5rem;
      border-radius: var(--radius-pill);
      margin-bottom: 0.35rem;
      text-transform: uppercase;
    }}
    .screen-title {{
      font-size: 0.95rem;
      font-weight: 700;
      color: var(--dark);
      margin-bottom: 0.3rem;
    }}
    .screen-desc {{
      font-size: 0.8rem;
      color: var(--dark-muted);
      line-height: 1.4;
      flex-grow: 1;
    }}

    /* Supply Chain Roles (Farmer, Buyer, Rider) */
    .roles-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
      gap: 1.5rem;
    }}
    .role-card {{
      background: var(--cream-card);
      border: 1px solid var(--border);
      border-radius: var(--radius-lg);
      padding: 2.2rem 1.85rem;
      box-shadow: var(--shadow-sm);
      position: relative;
      overflow: hidden;
    }}
    .role-card::before {{
      content: "";
      position: absolute;
      top: 0;
      left: 0;
      right: 0;
      height: 4px;
      background: var(--green-600);
    }}
    .role-header {{
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      margin-bottom: 1rem;
    }}
    .role-name {{
      font-size: 1.45rem;
      font-weight: 800;
      color: var(--dark);
      letter-spacing: -0.01em;
    }}
    .role-summary {{
      font-size: 0.94rem;
      color: var(--dark-muted);
      margin-bottom: 1.5rem;
      line-height: 1.5;
    }}
    .role-feature-list {{
      list-style: none;
    }}
    .role-feature-list li {{
      padding: 0.75rem 0;
      border-bottom: 1px solid rgba(0, 0, 0, 0.05);
      font-size: 0.88rem;
      color: var(--dark-muted);
      display: flex;
      align-items: flex-start;
      gap: 0.5rem;
    }}
    .role-feature-list li:last-child {{
      border-bottom: none;
      padding-bottom: 0;
    }}
    .role-check {{
      color: var(--green-600);
      font-weight: 700;
      line-height: 1;
      margin-top: 0.15rem;
    }}

    /* Channels & Architecture Section */
    .channels-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
      gap: 1.25rem;
      margin-top: 2rem;
    }}
    .channel-box {{
      background: var(--cream-card);
      border: 1px solid var(--border);
      border-radius: var(--radius-md);
      padding: 1.5rem;
      box-shadow: var(--shadow-sm);
      text-align: left;
    }}
    .channel-title {{
      font-size: 1.05rem;
      font-weight: 700;
      color: var(--dark);
      margin-bottom: 0.35rem;
      display: flex;
      align-items: center;
      gap: 0.5rem;
    }}
    .channel-desc {{
      font-size: 0.85rem;
      color: var(--dark-muted);
      margin-bottom: 0.9rem;
      line-height: 1.45;
    }}
    .channel-link {{
      font-size: 0.82rem;
      font-weight: 700;
      color: var(--green-700);
      display: inline-flex;
      align-items: center;
      gap: 0.25rem;
    }}
    .integration-proof {{
      margin-top: 2.5rem;
      display: grid;
      grid-template-columns: minmax(220px, 280px) 1fr;
      gap: 2rem;
      align-items: center;
      background: var(--cream-card);
      border: 1px solid var(--border);
      border-radius: var(--radius-lg);
      padding: 1.75rem;
      box-shadow: var(--shadow-sm);
    }}
    .integration-proof-img {{
      border-radius: 16px;
      overflow: hidden;
      border: 1px solid rgba(0, 0, 0, 0.06);
      box-shadow: 0 8px 24px rgba(0, 0, 0, 0.08);
      background: #FAFAFA;
      max-width: 280px;
      margin: 0 auto;
    }}
    .integration-proof-img img {{
      width: 100%;
      height: auto;
      display: block;
    }}
    .integration-proof-badge {{
      display: inline-block;
      font-size: 0.7rem;
      font-weight: 700;
      color: var(--green-700);
      background: var(--green-50);
      padding: 0.2rem 0.6rem;
      border-radius: var(--radius-pill);
      margin-bottom: 0.6rem;
      text-transform: uppercase;
      letter-spacing: 0.03em;
    }}
    .integration-proof-title {{
      font-size: 1.35rem;
      font-weight: 800;
      color: var(--dark);
      margin-bottom: 0.6rem;
      letter-spacing: -0.01em;
    }}
    .integration-proof-desc {{
      font-size: 0.92rem;
      color: var(--dark-muted);
      line-height: 1.55;
      margin-bottom: 1rem;
    }}
    .integration-proof-list {{
      list-style: none;
      margin-bottom: 1.25rem;
    }}
    .integration-proof-list li {{
      font-size: 0.88rem;
      color: var(--dark-muted);
      padding: 0.35rem 0;
      display: flex;
      align-items: flex-start;
      gap: 0.5rem;
    }}
    .integration-proof-list li::before {{
      content: "✓";
      color: var(--green-600);
      font-weight: 700;
      flex-shrink: 0;
    }}
    @media (max-width: 768px) {{
      .integration-proof {{
        grid-template-columns: 1fr;
        text-align: center;
        padding: 1.25rem;
      }}
      .integration-proof-list li {{
        justify-content: center;
      }}
    }}
    .channel-link:hover {{ text-decoration: underline; }}

    /* Download / Install Panel */
    .download-panel {{
      background: linear-gradient(145deg, var(--green-900), #063C2E);
      color: #FFFFFF;
      border-radius: var(--radius-lg);
      padding: 3.5rem 2rem;
      text-align: center;
      box-shadow: var(--shadow-lg);
      max-width: 820px;
      margin: 0 auto;
      position: relative;
      overflow: hidden;
    }}
    .download-panel h2 {{
      font-size: clamp(1.8rem, 3.5vw, 2.4rem);
      font-weight: 800;
      margin-bottom: 0.85rem;
    }}
    .download-panel p.lead {{
      font-size: 1.05rem;
      color: #D1FAE5;
      max-width: 580px;
      margin: 0 auto 2rem;
    }}
    .steps-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
      gap: 1.25rem;
      text-align: left;
      margin-bottom: 2.5rem;
    }}
    .step-box {{
      background: rgba(255, 255, 255, 0.08);
      border: 1px solid rgba(255, 255, 255, 0.12);
      border-radius: var(--radius-md);
      padding: 1.25rem;
    }}
    .step-num {{
      display: inline-flex;
      align-items: center;
      justify-content: center;
      width: 28px;
      height: 28px;
      border-radius: 50%;
      background: var(--green-500);
      color: #FFFFFF;
      font-weight: 800;
      font-size: 0.85rem;
      margin-bottom: 0.6rem;
    }}
    .step-title {{
      font-size: 0.95rem;
      font-weight: 700;
      color: #FFFFFF;
      margin-bottom: 0.25rem;
    }}
    .step-desc {{
      font-size: 0.82rem;
      color: #A7F3D0;
      line-height: 1.4;
    }}

    /* Contact Section */
    .contact-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
      gap: 1.25rem;
    }}
    .contact-card {{
      background: var(--cream-card);
      border: 1px solid var(--border);
      border-radius: var(--radius-md);
      padding: 1.75rem 1.5rem;
      box-shadow: var(--shadow-sm);
      text-align: center;
      transition: border-color 0.15s ease;
    }}
    .contact-card:hover {{
      border-color: var(--green-500);
    }}
    .contact-icon {{
      width: 48px;
      height: 48px;
      border-radius: 50%;
      background: var(--green-50);
      color: var(--green-700);
      display: inline-flex;
      align-items: center;
      justify-content: center;
      font-size: 1.35rem;
      margin-bottom: 1rem;
    }}
    .contact-card-title {{
      font-size: 1rem;
      font-weight: 700;
      color: var(--dark);
      margin-bottom: 0.35rem;
    }}
    .contact-card-val {{
      font-size: 0.95rem;
      font-weight: 600;
      color: var(--green-700);
      margin-bottom: 0.35rem;
      display: block;
    }}
    .contact-card-desc {{
      font-size: 0.78rem;
      color: var(--dark-light);
    }}

    /* Footer - Full Width Clean Horizontal Layout */
    .footer {{
      background: var(--dark);
      color: #E5E7EB;
      padding: 4.5rem 0 2rem;
      font-size: 0.9rem;
    }}
    .footer-top {{
      display: grid;
      grid-template-columns: 2fr 1fr 1fr 1.2fr;
      gap: 3.5rem;
      padding-bottom: 3rem;
      border-bottom: 1px solid rgba(255, 255, 255, 0.1);
    }}
    .footer-brand h4 {{
      font-size: 1.35rem;
      font-weight: 800;
      color: #FFFFFF;
      margin-bottom: 0.75rem;
      display: flex;
      align-items: center;
      gap: 0.55rem;
    }}
    .footer-brand p {{
      color: #9CA3AF;
      font-size: 0.88rem;
      max-width: 360px;
      line-height: 1.6;
      margin-bottom: 1.25rem;
    }}
    .footer-brand-meta {{
      display: flex;
      flex-direction: column;
      gap: 0.35rem;
      font-size: 0.85rem;
      color: #9CA3AF;
    }}
    .footer-brand-meta a {{
      color: #34D399;
    }}
    .footer-brand-meta a:hover {{
      text-decoration: underline;
    }}
    .footer-col h5 {{
      font-size: 0.82rem;
      font-weight: 700;
      letter-spacing: 0.08em;
      text-transform: uppercase;
      color: #FFFFFF;
      margin-bottom: 1.25rem;
    }}
    .footer-links {{
      list-style: none;
      display: flex;
      flex-direction: column;
      gap: 0.65rem;
    }}
    .footer-links a {{
      color: #9CA3AF;
      font-size: 0.88rem;
      transition: color 0.15s ease;
    }}
    .footer-links a:hover {{
      color: #34D399;
    }}
    .footer-bottom {{
      padding-top: 2rem;
      display: flex;
      justify-content: space-between;
      align-items: center;
      flex-wrap: wrap;
      gap: 1rem;
      color: #9CA3AF;
      font-size: 0.82rem;
    }}
    .footer-bottom a {{
      color: #34D399;
    }}
    .footer-bottom a:hover {{
      text-decoration: underline;
    }}

    /* Fully Responsive Breakpoints */
    @media (max-width: 1024px) {{
      .footer-top {{
        grid-template-columns: 1.5fr 1fr 1fr 1fr;
        gap: 2rem;
      }}
    }}
    @media (max-width: 860px) {{
      .nav-menu {{ display: none; }}
      .footer-top {{
        grid-template-columns: 1fr 1fr;
        gap: 2.5rem;
      }}
    }}
    @media (max-width: 600px) {{
      .top-bar-inner {{ justify-content: center; text-align: center; }}
      .top-contacts {{ justify-content: center; }}
      .hero-cta-group {{ flex-direction: column; width: 100%; }}
      .hero-cta-group .btn {{ width: 100%; }}
      .footer-top {{
        grid-template-columns: 1fr;
        gap: 2rem;
      }}
      .footer-bottom {{
        flex-direction: column;
        text-align: center;
        gap: 0.75rem;
      }}
    }}
  </style>
</head>
<body>

  <!-- Top Utility Bar with Contact Details -->
  <div class="top-bar">
    <div class="container top-bar-inner">
      <div class="top-contacts">
        <a class="top-contact-link" href="mailto:{contact_email}">
          <span>&#9993;</span> {contact_email}
        </a>
        <a class="top-contact-link" href="tel:{contact_phone_raw}">
          <span>&#9742;</span> {contact_phone}
        </a>
        <span class="top-contact-link">
          <span>&#128205;</span> University of Moratuwa
        </span>
        <a class="top-contact-link" href="{repo_url}" target="_blank" rel="noopener">
          <span>&#9733;</span> GitHub Repo
        </a>
      </div>
      <div>
        <span class="top-badge">Android &middot; WhatsApp &middot; Telegram</span>
      </div>
    </div>
  </div>

  <!-- Main Navigation Header -->
  <header class="header">
    <div class="container nav">
      <a class="brand" href="/">
        <img class="brand-logo" src="/static/agripilot-icon.png" alt="AgriPilot Logo" width="38" height="38" />
        <div>
          <span>AgriPilot</span>
          <span class="brand-tagline">AI Agriculture</span>
        </div>
      </a>
      <ul class="nav-menu">
        <li><a class="nav-link" href="#features">Features</a></li>
        <li><a class="nav-link" href="#advisor">AI Advisor</a></li>
        <li><a class="nav-link" href="#roles">Supply Chain</a></li>
        <li><a class="nav-link" href="#app-screens">Screens</a></li>
        <li><a class="nav-link" href="/architecture">Architecture</a></li>
        <li><a class="nav-link" href="/docs">API Docs</a></li>
        <li><a class="nav-link" href="{repo_url}" target="_blank" rel="noopener">GitHub</a></li>
        <li><a class="nav-link" href="#contact">Contact</a></li>
      </ul>
      <div class="nav-actions">
        <a class="btn btn-ghost btn-sm" href="{repo_url}" target="_blank" rel="noopener" style="padding: 0.5rem 0.85rem;">
          <span>&#128187;</span> GitHub
        </a>
        <a class="btn btn-primary btn-sm" href="{download_url}">
          <span>&#8595;</span> Download APK
        </a>
      </div>
    </div>
  </header>

  <main>
    <!-- Hero Section -->
    <section class="hero" id="hero">
      <div class="container">
        <div class="hero-tag-wrap" style="margin-bottom: 0.75rem;">
          <span class="hero-agent-badge">&#129302; Powered by Multi-Agent AI</span>
        </div>
        <div class="hero-tag-wrap">
          <span class="hero-tag">&#127807; No Middlemen &middot; Direct Farm-to-Table</span>
        </div>
        <h1 class="hero-title">
          Farmers Earn More. <span class="accent">Fresh Food</span> at Lower Cost. Citizens Deliver &amp; Earn.
        </h1>
        <p class="hero-subtitle">
          AgriPilot removes middlemen from the supply chain, so growers keep their margin, families get farm-fresh produce at fair prices, and local riders earn on every delivery. Multi-agent AI coordinates diagnosis, marketplace matching, and live GPS tracking on Android, WhatsApp, and Telegram.
        </p>

        <div class="hero-value-strip">
          <article class="value-pillar">
            <div class="value-pillar-icon">&#127806;</div>
            <h2 class="value-pillar-title">Farmers Earn More</h2>
            <p class="value-pillar-desc">Sell harvests direct to buyers: no middlemen, no commission cuts. Keep more of what you grow.</p>
          </article>
          <article class="value-pillar">
            <div class="value-pillar-icon">&#129382;</div>
            <h2 class="value-pillar-title">Fresh Food, Lower Cost</h2>
            <p class="value-pillar-desc">Consumers buy straight from the farm: fresher produce at fair prices without trader markups.</p>
          </article>
          <article class="value-pillar">
            <div class="value-pillar-icon">&#128757;</div>
            <h2 class="value-pillar-title">Citizens Deliver &amp; Earn</h2>
            <p class="value-pillar-desc">Anyone can sign up as a rider, fulfill local farm-to-doorstep deliveries, and earn flexible income.</p>
          </article>
        </div>
        <div class="hero-cta-group">
          <a class="btn btn-primary" href="{download_url}">
            <span>&#128242;</span> Download Android App <span class="badge-pill" style="background: rgba(255,255,255,0.25); color: #fff;">APK</span>
          </a>
          <a class="btn btn-secondary" href="{wa_me}" target="_blank" rel="noopener">
            <span>&#128172;</span> WhatsApp Advisor ({wa_display})
          </a>
          <a class="btn btn-ghost" href="{telegram_base}" target="_blank" rel="noopener">
            <span>&#9992;</span> Telegram Bot (@{telegram_label})
          </a>
          <a class="btn btn-ghost" href="{repo_url}" target="_blank" rel="noopener">
            <span>&#128187;</span> GitHub Repo
          </a>
        </div>

        <!-- Trust Highlights Ticker -->
        <div class="highlights-bar">
          <div class="highlights-grid">
            <div class="highlight-item">
              <div class="highlight-icon">&#127806;</div>
              <div>
                <span class="highlight-text">No Middlemen</span>
                <span class="highlight-sub">Farmers sell direct, keep full margin</span>
              </div>
            </div>
            <div class="highlight-item">
              <div class="highlight-icon">&#129382;</div>
              <div>
                <span class="highlight-text">Lower Prices</span>
                <span class="highlight-sub">Fresh farm produce without trader markup</span>
              </div>
            </div>
            <div class="highlight-item">
              <div class="highlight-icon">&#128757;</div>
              <div>
                <span class="highlight-text">Earn as a Rider</span>
                <span class="highlight-sub">Citizens deliver locally &amp; get paid</span>
              </div>
            </div>
            <div class="highlight-item">
              <div class="highlight-icon">&#129302;</div>
              <div>
                <span class="highlight-text">Agent-Powered</span>
                <span class="highlight-sub">AI diagnosis, matching &amp; logistics</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Hero Phone Preview -->
        <div class="hero-preview-wrap">
          <div class="phone-mockup">
            <img src="/static/screenshots/home.png" alt="AgriPilot Farmer Home Screen" width="290" height="580" />
          </div>
          <div class="phone-mockup secondary">
            <img src="/static/screenshots/plant-detail.png" alt="AgriPilot Plant Health Detail Screen" width="250" height="500" />
          </div>
        </div>
      </div>
    </section>

    <!-- Core Capabilities (Hope Rise 3-Card Layout) -->
    <section class="section section-alt" id="features">
      <div class="container">
        <div class="section-header">
          <span class="section-badge">Core Capabilities</span>
          <h2 class="section-title">Intelligent Solutions for the Agriculture Ecosystem</h2>
          <p class="section-desc">
            Combining LangGraph multi-agent orchestration, PostgreSQL marketplace transactions, and real-time logistics.
          </p>
        </div>

        <div class="cards-grid-3">
          <!-- Card 1: AI Agronomy -->
          <article class="card-feature">
            <div class="card-icon-pill">&#127807;</div>
            <h3 class="card-feature-title">AI Agronomy &amp; Diagnosis</h3>
            <p class="card-feature-desc">
              Instant crop disease identification from leaf photos with lab-grade safety validation backstops.
            </p>
            <ul class="card-feature-list">
              {_render_list_items(advisor_diagnosis_items)}
            </ul>
            <div class="card-footer-action">
              <span>EXPLORE ADVISOR</span>
              <span class="circle-arrow">&#8594;</span>
            </div>
          </article>

          <!-- Card 2: Treatment & Weather -->
          <article class="card-feature">
            <div class="card-icon-pill">&#9925;</div>
            <h3 class="card-feature-title">Treatment RAG &amp; Weather</h3>
            <p class="card-feature-desc">
              Domain-verified chemical guidelines, weather forecasts, and irrigation advice tailored to your coordinates.
            </p>
            <ul class="card-feature-list">
              {_render_list_items(advisor_treatment_items)}
            </ul>
            <div class="card-footer-action">
              <span>EXPLORE WEATHER</span>
              <span class="circle-arrow">&#8594;</span>
            </div>
          </article>

          <!-- Card 3: Multi-Channel -->
          <article class="card-feature">
            <div class="card-icon-pill">&#128172;</div>
            <h3 class="card-feature-title">Multi-Channel Access</h3>
            <p class="card-feature-desc">
              Interact seamlessly through the native Android Flutter app or your preferred messaging platforms.
            </p>
            <ul class="card-feature-list">
              {_render_list_items(advisor_channels_items)}
            </ul>
            <div class="card-footer-action">
              <span>EXPLORE CHANNELS</span>
              <span class="circle-arrow">&#8594;</span>
            </div>
          </article>
        </div>
      </div>
    </section>

    <!-- Mobile App Screenshots Showcase -->
    <section class="section" id="app-screens">
      <div class="container">
        <div class="section-header">
          <span class="section-badge">Mobile Experience</span>
          <h2 class="section-title">Designed for the Field &amp; the Market</h2>
          <p class="section-desc">
            Clean, accessible Flutter interface with offline resilience, low-bandwidth optimization, and Sinhala/Tamil/English readiness.
          </p>
        </div>

        <div class="screens-grid">
          <!-- Screen 1 -->
          <article class="screen-card">
            <div class="screen-img-box">
              <img src="/static/screenshots/home.png" alt="Farmer Home Screen" loading="lazy" />
            </div>
            <span class="screen-tag-pill">Dashboard</span>
            <h3 class="screen-title">Farmer Home</h3>
            <p class="screen-desc">Track active crops, check sell listings, and launch instant AI diagnosis.</p>
          </article>

          <!-- Screen 2 -->
          <article class="screen-card">
            <div class="screen-img-box">
              <img src="/static/screenshots/advisor.png" alt="AI Advisor Chat Screen" loading="lazy" />
            </div>
            <span class="screen-tag-pill">Diagnosis</span>
            <h3 class="screen-title">AI Advisor</h3>
            <p class="screen-desc">Step-by-step disease identification and safety-validated treatments.</p>
          </article>

          <!-- Screen 3 -->
          <article class="screen-card">
            <div class="screen-img-box">
              <img src="/static/screenshots/plant-detail.png" alt="Plant Health Detail Screen" loading="lazy" />
            </div>
            <span class="screen-tag-pill">Tracking</span>
            <h3 class="screen-title">Plant Health</h3>
            <p class="screen-desc">Photo timeline, growth milestones, and historical diagnosis logs.</p>
          </article>

          <!-- Screen 4 -->
          <article class="screen-card">
            <div class="screen-img-box">
              <img src="/static/screenshots/orders.png" alt="Orders Screen" loading="lazy" />
            </div>
            <span class="screen-tag-pill">Orders</span>
            <h3 class="screen-title">Fulfillment</h3>
            <p class="screen-desc">Confirm bulk quantities, set pickup coordinates, and trigger rider dispatch.</p>
          </article>

          <!-- Screen 5 -->
          <article class="screen-card">
            <div class="screen-img-box">
              <img src="/static/screenshots/delivery-tracking.jpg" alt="Live Map Delivery Tracking" loading="lazy" />
            </div>
            <span class="screen-tag-pill">Logistics</span>
            <h3 class="screen-title">Live Tracking</h3>
            <p class="screen-desc">Realtime OpenStreetMap rider route, ETA countdown, and PIN verification.</p>
          </article>
        </div>
      </div>
    </section>

    <!-- Supply Chain Roles Section -->
    <section class="section section-alt" id="roles">
      <div class="container">
        <div class="section-header">
          <span class="section-badge">Built for Everyone</span>
          <h2 class="section-title">Complete Support for Farmers, Buyers &amp; Riders</h2>
          <p class="section-desc">
            Connecting agricultural producers with consumers and transparent logistics partners without middlemen commissions.
          </p>
        </div>

        <div class="roles-grid">
          <!-- Role 1: Farmers -->
          <article class="role-card">
            <div class="role-header">
              <div>
                <span class="badge-pill">PRODUCERS</span>
                <h3 class="role-name" style="margin-top: 0.35rem;">Farmers</h3>
              </div>
              <div class="card-icon-pill" style="margin-bottom:0;">&#129382;</div>
            </div>
            <p class="role-summary">
              Sell harvests directly at fair prices, monitor crop health, and get immediate agronomy advice anytime.
            </p>
            <ul class="role-feature-list">
              {_render_list_items(farmer_marketplace_items)}
              {_render_list_items(farmer_plants_items)}
            </ul>
          </article>

          <!-- Role 2: Buyers -->
          <article class="role-card">
            <div class="role-header">
              <div>
                <span class="badge-pill">BUYERS &amp; BUSINESSES</span>
                <h3 class="role-name" style="margin-top: 0.35rem;">Buyers</h3>
              </div>
              <div class="card-icon-pill" style="margin-bottom:0;">&#128722;</div>
            </div>
            <p class="role-summary">
              Source verified fresh produce directly from local farms with full crop-health traceability and live delivery.
            </p>
            <ul class="role-feature-list">
              {_render_list_items(buyer_discovery_items)}
            </ul>
          </article>

          <!-- Role 3: Riders -->
          <article class="role-card">
            <div class="role-header">
              <div>
                <span class="badge-pill">LOGISTICS PARTNERS</span>
                <h3 class="role-name" style="margin-top: 0.35rem;">Delivery Riders</h3>
              </div>
              <div class="card-icon-pill" style="margin-bottom:0;">&#128757;</div>
            </div>
            <p class="role-summary">
              Earn flexible income fulfilling nearby farm-to-doorstep deliveries with turn-by-turn navigation.
            </p>
            <ul class="role-feature-list">
              {_render_list_items(rider_logistics_items)}
            </ul>
          </article>
        </div>
      </div>
    </section>

    <!-- Architecture & Integration Channels -->
    <section class="section" id="advisor">
      <div class="container">
        <div class="section-header">
          <span class="section-badge">Architecture &amp; Integration</span>
          <h2 class="section-title">Open, Modular &amp; Multi-Agent Infrastructure</h2>
          <p class="section-desc">
            Built on Agent Kernel and LangGraph supervisor routing, PostgreSQL marketplace schemas, and Redis-backed session memory.
          </p>
        </div>

        <div class="channels-grid">
          <div class="channel-box">
            <h3 class="channel-title">&#128242; Android Client</h3>
            <p class="channel-desc">Flutter mobile client with JWT token auth, multipart photo uploads, and OSM map integration.</p>
            <a class="channel-link" href="{download_url}">Download APK &rarr;</a>
          </div>

          <div class="channel-box">
            <h3 class="channel-title">&#128172; WhatsApp Cloud API</h3>
            <p class="channel-desc">Fast-ack webhook adapter providing verified farmers with instant diagnostic replies in the field.</p>
            <a class="channel-link" href="{wa_me}" target="_blank" rel="noopener">Open WhatsApp &rarr;</a>
          </div>

          <div class="channel-box">
            <h3 class="channel-title">&#9992; Telegram Bot API</h3>
            <p class="channel-desc">Gated Telegram handler with contact-sharing verification linking farmers to persistent profiles.</p>
            <a class="channel-link" href="{telegram_base}" target="_blank" rel="noopener">Open Telegram &rarr;</a>
          </div>

          <div class="channel-box">
            <h3 class="channel-title">&#9881; REST &amp; MCP API</h3>
            <p class="channel-desc">Comprehensive OpenAPI documented endpoints for marketplace listings, orders, and dispatch.</p>
            <a class="channel-link" href="/docs">Interactive Docs &rarr;</a>
          </div>
        </div>

        <div class="integration-proof" id="telegram-proof">
          <div class="integration-proof-img">
            <img src="/static/screenshots/telegram-chat.jpg" alt="AgriPilot Telegram bot: linked farmer account asking about crop listings" loading="lazy" width="280" height="622" />
          </div>
          <div>
            <span class="integration-proof-badge">Live Integration Proof</span>
            <h3 class="integration-proof-title">Telegram Bot in Production</h3>
            <p class="integration-proof-desc">
              Farmers link their AgriPilot account via contact sharing, then chat with the same AI advisor and marketplace tools used in the Android app; no separate login required.
            </p>
            <ul class="integration-proof-list">
              <li>Phone-number contact share links Telegram chat to farmer profile</li>
              <li>Persistent session memory across mobile app and Telegram</li>
              <li>Marketplace queries: crop listings, sold history, and inventory counts</li>
              <li>Farmer-only gate blocks unlinked or inactive accounts before any LLM call</li>
            </ul>
            <a class="btn btn-secondary" href="{telegram_base}" target="_blank" rel="noopener">
              <span>&#9992;</span> Try @{telegram_label} on Telegram
            </a>
          </div>
        </div>

        <div style="text-align: center; margin-top: 2.5rem;">
          <a class="btn btn-secondary" href="/architecture">
            <span>&#128202;</span> View runtime architecture &rarr;
          </a>
        </div>
      </div>
    </section>

    <!-- Download & Install Section -->
    <section class="section section-alt" id="download">
      <div class="container">
        <div class="download-panel">
          <span class="badge-pill" style="background: rgba(255,255,255,0.2); color: #fff; margin-bottom: 1rem;">GET STARTED</span>
          <h2>Install AgriPilot on Your Android Device</h2>
          <p class="lead">
            Download the official release APK to start diagnosing crops, selling harvests, and tracking deliveries today.
          </p>

          <div class="steps-grid">
            <div class="step-box">
              <span class="step-num">1</span>
              <h3 class="step-title">Download APK</h3>
              <p class="step-desc">Tap the button below to download the latest <code>agripilot-*.apk</code> package.</p>
            </div>
            <div class="step-box">
              <span class="step-num">2</span>
              <h3 class="step-title">Allow Install</h3>
              <p class="step-desc">Enable "Install Unknown Apps" in your Android settings or browser if prompted.</p>
            </div>
            <div class="step-box">
              <span class="step-num">3</span>
              <h3 class="step-title">Sign Up &amp; Start</h3>
              <p class="step-desc">Choose your role as Farmer, Buyer, or Rider and get started immediately.</p>
            </div>
          </div>

          <div style="display: flex; justify-content: center; gap: 1rem; flex-wrap: wrap;">
            <a class="btn btn-primary" href="{download_url}" style="background: #FFFFFF; color: var(--green-900); font-weight: 700;">
              <span>&#128242;</span> Download Android App (APK)
            </a>
            <a class="btn btn-ghost" href="{repo_url}" target="_blank" rel="noopener" style="color: #FFFFFF; border-color: rgba(255,255,255,0.3);">
              <span>&#128187;</span> GitHub Repository &rarr;
            </a>
          </div>
        </div>
      </div>
    </section>

    <!-- Contact Details Section -->
    <section class="section" id="contact">
      <div class="container">
        <div class="section-header">
          <span class="section-badge">Get in Touch</span>
          <h2 class="section-title">Support &amp; Inquiries</h2>
          <p class="section-desc">
            Need help with your account, marketplace listings, or technical integration? Reach out to our team.
          </p>
        </div>

        <div class="contact-grid">
          <div class="contact-card">
            <div class="contact-icon">&#9993;</div>
            <h3 class="contact-card-title">Email Support</h3>
            <a class="contact-card-val" href="mailto:{contact_email}">{contact_email}</a>
            <span class="contact-card-desc">General inquiries &amp; technical help</span>
          </div>

          <div class="contact-card">
            <div class="contact-icon">&#9742;</div>
            <h3 class="contact-card-title">Phone &amp; Hotline</h3>
            <a class="contact-card-val" href="tel:{contact_phone_raw}">{contact_phone}</a>
            <span class="contact-card-desc">Direct line (Sri Lanka)</span>
          </div>

          <div class="contact-card">
            <div class="contact-icon">&#128172;</div>
            <h3 class="contact-card-title">WhatsApp Advisor</h3>
            <a class="contact-card-val" href="{wa_me}" target="_blank" rel="noopener">{wa_display}</a>
            <span class="contact-card-desc">AI Agronomy &amp; diagnostics chat</span>
          </div>

          <div class="contact-card">
            <div class="contact-icon">&#128205;</div>
            <h3 class="contact-card-title">Location</h3>
            <span class="contact-card-val">University of Moratuwa</span>
            <span class="contact-card-desc">Moratuwa, Sri Lanka</span>
          </div>
        </div>
      </div>
    </section>
  </main>

  <!-- Footer - Desktop Horizontal Grid Layout -->
  <footer class="footer">
    <div class="container">
      <div class="footer-top">
        <div class="footer-brand">
          <h4>
            <img src="/static/agripilot-icon.png" alt="AgriPilot" width="28" height="28" style="border-radius: 6px;" />
            AgriPilot
          </h4>
          <p>
            An agentic agricultural intelligence, marketplace, and delivery platform empowering local farmers and buyers through multi-agent AI.
          </p>
          <div class="footer-brand-meta">
            <span>Email: <a href="mailto:{contact_email}">{contact_email}</a></span>
            <span>Hotline: <a href="tel:{contact_phone_raw}">{contact_phone}</a></span>
            <span>Location: University of Moratuwa</span>
          </div>
        </div>

        <div class="footer-col">
          <h5>Platform</h5>
          <ul class="footer-links">
            <li><a href="#features">Core Features</a></li>
            <li><a href="#advisor">AI Advisor</a></li>
            <li><a href="#roles">Supply Chain Roles</a></li>
            <li><a href="#app-screens">App Screenshots</a></li>
            <li><a href="{download_url}">Download Android APK</a></li>
          </ul>
        </div>

        <div class="footer-col">
          <h5>Developers</h5>
          <ul class="footer-links">
            <li><a href="/docs">REST API Documentation</a></li>
            <li><a href="/architecture">Architecture Diagram</a></li>
            <li><a href="{repo_url}" target="_blank" rel="noopener">AgriPilot GitHub Repo</a></li>
            <li><a href="{framework_url}" target="_blank" rel="noopener">Agent Kernel Framework</a></li>
            <li><a href="https://kernel.yaala.ai/docs" target="_blank" rel="noopener">Framework Docs</a></li>
          </ul>
        </div>

        <div class="footer-col">
          <h5>Channels &amp; Contact</h5>
          <ul class="footer-links">
            <li><a href="{wa_me}" target="_blank" rel="noopener">WhatsApp ({wa_display})</a></li>
            <li><a href="{telegram_base}" target="_blank" rel="noopener">Telegram (@{telegram_label})</a></li>
            <li><a href="mailto:{contact_email}">{contact_email}</a></li>
            <li><a href="tel:{contact_phone_raw}">{contact_phone}</a></li>
          </ul>
        </div>
      </div>

      <div class="footer-bottom">
        <div>
          &copy; 2026 AgriPilot &middot; <a href="{repo_url}" target="_blank" rel="noopener">GitHub Repository</a> &middot; Built with <a href="{framework_url}" target="_blank" rel="noopener">Agent Kernel</a> &middot; <a href="https://knurdz.org" target="_blank" rel="noopener">knurdz.org</a>
        </div>
        <div>
          <a href="#hero">Back to top &uarr;</a>
        </div>
      </div>
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
