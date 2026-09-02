"""AgriPilot bot slash commands for Telegram (menu) and WhatsApp (keywords).

Telegram: register via ``setMyCommands`` so typing ``/`` shows the menu.
WhatsApp: no native command menu — same keywords are intercepted as plain text.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any, Optional

if TYPE_CHECKING:
    from marketplace.models import User

_log = logging.getLogger("agripilot.bot_commands")

BOT_COMMANDS: list[dict[str, str]] = [
    {"command": "start", "description": "Link account / get started"},
    {"command": "help", "description": "What AgriPilot can do"},
    {"command": "status", "description": "Show account link status"},
    {"command": "new", "description": "Start a fresh chat session"},
]

KNOWN_COMMANDS = frozenset(f"/{c['command']}" for c in BOT_COMMANDS)
KNOWN_KEYWORDS = frozenset(c["command"] for c in BOT_COMMANDS)


def normalize_command(text: str | None) -> Optional[str]:
    """Return ``/help``-style command if the first token is a known command/keyword.

    Accepts ``/help``, ``/help@BotName``, and bare ``help`` (WhatsApp-friendly).
    Returns None for unknown text or multi-arg ``/start <token>`` (deep link).
    """
    if not text or not str(text).strip():
        return None
    first = str(text).strip().split(maxsplit=1)[0]
    # Deep-link /start <token> is not a bare command — leave to token handler.
    rest = str(text).strip().split(maxsplit=1)
    if len(rest) > 1 and rest[0].split("@", 1)[0].lower() in ("/start", "start"):
        return None

    token = first.split("@", 1)[0].lower()
    if token.startswith("/"):
        return token if token in KNOWN_COMMANDS else None
    if token in KNOWN_KEYWORDS:
        return f"/{token}"
    return None


def help_text(*, channel: str = "telegram") -> str:
    """Plain-text help for messaging channels."""
    if channel == "whatsapp":
        how = "Send a crop photo or ask a question about disease, weather, or irrigation."
        cmds = (
            "Shortcuts:\n"
            "help — this message\n"
            "start — welcome / account tips\n"
            "status — account status\n"
            "new — start a fresh chat"
        )
    else:
        how = "Send a crop photo or ask about disease, weather, irrigation, or your farm."
        cmds = (
            "Commands:\n"
            "/start — link account / get started\n"
            "/help — this message\n"
            "/status — account link status\n"
            "/new — start a fresh chat"
        )
    return (
        "AgriPilot helps active farmers with crop disease checks, agronomic advice, "
        f"and farm marketplace tips.\n\n{how}\n\n{cmds}"
    )


def start_text(user: Optional[User] = None, *, eligible: bool = False) -> str:
    if user is not None and eligible:
        name = getattr(user, "name", None) or "farmer"
        return (
            f"Welcome back, {name}! You're connected to AgriPilot. "
            "Send a crop photo or ask a question anytime. Tap /help for commands."
        )
    if user is not None:
        return (
            "Your Telegram is linked, but AgriPilot chat needs an active farmer account. "
            "Check your subscription in the app."
        )
    return (
        "Welcome to AgriPilot! Link your active farmer account to get crop advice, "
        "photo diagnosis, and more. Tap the button below to share your phone number, "
        "or open Link Telegram from the mobile app."
    )


def status_text(user: Optional[User] = None, *, channel: str = "telegram") -> str:
    link_label = "Telegram" if channel == "telegram" else "WhatsApp"
    if user is None:
        return (
            f"{link_label} is not linked to an AgriPilot account.\n"
            "Use /start (or share your phone number) to link an active farmer account."
            if channel == "telegram"
            else f"{link_label} is not linked to an active farmer AgriPilot account.\n"
            "Sign up or activate your farmer subscription in the app."
        )
    name = getattr(user, "name", None) or "(no name)"
    role = getattr(user, "role", None) or "?"
    sub = getattr(user, "subscription_status", None) or "?"
    return (
        f"Linked: yes ({link_label})\n"
        f"Name: {name}\n"
        f"Role: {role}\n"
        f"Subscription: {sub}"
    )


def new_chat_text() -> str:
    return "Fresh chat started. Previous conversation context was cleared. How can I help?"


def gated_command_note(*, channel: str = "whatsapp") -> str:
    """Short note when a gated user asks for help/status without agent access."""
    return (
        "AgriPilot messaging is for active farmer accounts. "
        "Sign up or activate your subscription in the app, then message again."
    )


async def clear_channel_session(session_id: str, user: Optional[User] = None) -> bool:
    """Clear agent session data for this channel thread. Returns True on success."""
    try:
        from agentkernel.core.runtime import Runtime

        from marketplace.session_identity import seed_marketplace_session

        runtime = Runtime.current()
        store = runtime.sessions()
        session = store.load(session_id)
        if session is None:
            return False
        session.clear()
        if user is not None:
            seed_marketplace_session(session, user)
        result = store.store(session)
        if hasattr(result, "__await__"):
            await result  # type: ignore[misc]
        return True
    except Exception as exc:  # noqa: BLE001
        _log.warning("clear_channel_session failed sid=%s: %s", session_id, exc)
        return False


async def register_telegram_commands(bot_token: str | None) -> bool:
    """POST setMyCommands so Telegram shows the `/` menu. Never raises."""
    token = (bot_token or "").strip()
    if not token or token.lower() in {"dummy", "changeme", "none"}:
        _log.info("Skipping setMyCommands: no Telegram bot token configured")
        return False
    url = f"https://api.telegram.org/bot{token}/setMyCommands"
    payload: dict[str, Any] = {"commands": BOT_COMMANDS}
    try:
        import httpx

        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.post(url, json=payload)
            data = resp.json() if resp.content else {}
            ok = bool(data.get("ok")) if isinstance(data, dict) else resp.is_success
            if ok:
                _log.info("Telegram setMyCommands registered %d commands", len(BOT_COMMANDS))
                return True
            _log.warning("Telegram setMyCommands failed status=%s body=%s", resp.status_code, data)
            return False
    except Exception as exc:  # noqa: BLE001
        _log.warning("Telegram setMyCommands error: %s", exc)
        return False
