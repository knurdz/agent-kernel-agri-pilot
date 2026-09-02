"""Tests for AgriPilot bot slash commands (Telegram menu + WhatsApp keywords)."""

from __future__ import annotations

import asyncio
import logging
import os
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

for _var in ("AK_TELEGRAM__BOT_TOKEN", "AK_WHATSAPP__ACCESS_TOKEN", "AK_WHATSAPP__PHONE_NUMBER_ID"):
    os.environ.setdefault(_var, "dummy")

import marketplace.database as database_module
import marketplace.models  # noqa: F401
from channel_handlers.bot_commands import (
    BOT_COMMANDS,
    help_text,
    normalize_command,
    register_telegram_commands,
    status_text,
)
from marketplace.database import Base
from marketplace.models import User
from marketplace.session_identity import canonical_session_id
from telegram_handler import GatedTelegramHandler
from whatsapp_handler import FastAckWhatsAppHandler

FARMER_PHONE = "+94770000401"
CHAT_ID = 555200


@pytest.fixture
def db_factory(monkeypatch):
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    factory = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    monkeypatch.setattr(database_module, "SessionLocal", factory)
    yield factory
    engine.dispose()


def _make_user(db, phone=FARMER_PHONE, **overrides) -> User:
    fields = dict(role="farmer", password_hash="hash", name="Amal", subscription_status="active")
    fields.update(overrides)
    user = User(phone_number=phone, **fields)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def tg_handler():
    logging.getLogger("agripilot.telegram").setLevel(logging.ERROR)
    h = GatedTelegramHandler()
    sent: list = []
    delegated: list = []

    async def fake_send(chat_id, text, parse_mode=None, reply_markup=None):
        await asyncio.sleep(0)
        sent.append((chat_id, text, reply_markup))

    async def fake_delegate(body: dict):
        await asyncio.sleep(0)
        delegated.append(body["update_id"])

    h._send_message = fake_send  # type: ignore[method-assign]
    h._delegate = fake_delegate  # type: ignore[method-assign]
    h.sent = sent  # type: ignore[attr-defined]
    h.delegated = delegated  # type: ignore[attr-defined]
    return h


def _text_update(update_id: int, text: str, chat_id: int = CHAT_ID) -> dict:
    return {
        "update_id": update_id,
        "message": {
            "message_id": update_id,
            "date": 0,
            "chat": {"id": chat_id, "type": "private"},
            "from": {"id": chat_id, "is_bot": False},
            "text": text,
        },
    }


# ------------------------------------------------------------------ normalize


def test_normalize_command_slash_and_bot_suffix():
    assert normalize_command("/help") == "/help"
    assert normalize_command("/help@MyBot") == "/help"
    assert normalize_command("  /STATUS  ") == "/status"
    assert normalize_command("help") == "/help"
    assert normalize_command("HELP") == "/help"
    assert normalize_command("/new") == "/new"
    assert normalize_command("/start") == "/start"


def test_normalize_command_ignores_start_token_and_unknown():
    assert normalize_command("/start abc123token") is None
    assert normalize_command("start abc123token") is None
    assert normalize_command("/foo") is None
    assert normalize_command("my tomato leaves") is None
    assert normalize_command("") is None
    assert normalize_command(None) is None


# ----------------------------------------------------------- setMyCommands


@pytest.mark.asyncio
async def test_register_telegram_commands_posts_catalog():
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.is_success = True
    mock_resp.content = b'{"ok":true}'
    mock_resp.json.return_value = {"ok": True}

    with patch("httpx.AsyncClient") as client_cls:
        client = AsyncMock()
        client.__aenter__.return_value = client
        client.__aexit__.return_value = None
        client.post = AsyncMock(return_value=mock_resp)
        client_cls.return_value = client

        ok = await register_telegram_commands("123456:ABC-REALTOKEN")
        assert ok is True
        client.post.assert_awaited_once()
        args, kwargs = client.post.await_args
        assert args[0].endswith("/setMyCommands")
        assert kwargs["json"]["commands"] == BOT_COMMANDS


@pytest.mark.asyncio
async def test_register_telegram_commands_skips_dummy_token():
    assert await register_telegram_commands("dummy") is False
    assert await register_telegram_commands("") is False
    assert await register_telegram_commands(None) is False


# -------------------------------------------------------------- Telegram


def test_unlinked_help_returns_help_not_only_keyboard(tg_handler, db_factory):
    asyncio.run(tg_handler._process_webhook_body(_text_update(1, "/help")))
    assert tg_handler.delegated == []
    assert len(tg_handler.sent) == 1
    _, text, markup = tg_handler.sent[0]
    assert "AgriPilot" in text
    assert "/status" in text
    assert markup is None


def test_unlinked_start_still_gets_link_prompt(tg_handler, db_factory):
    asyncio.run(tg_handler._process_webhook_body(_text_update(2, "/start")))
    assert tg_handler.delegated == []
    assert tg_handler.sent and tg_handler.sent[0][2]["keyboard"][0][0]["request_contact"] is True


def test_linked_status_mentions_farmer(tg_handler, db_factory):
    with db_factory() as db:
        _make_user(db, telegram_chat_id=CHAT_ID, name="Sadeepa")

    asyncio.run(tg_handler._process_webhook_body(_text_update(3, "/status")))
    assert tg_handler.delegated == []
    body = tg_handler.sent[0][1]
    assert "Sadeepa" in body
    assert "farmer" in body.lower()
    assert "active" in body.lower()


def test_new_clears_session(tg_handler, db_factory):
    with db_factory() as db:
        user = _make_user(db, telegram_chat_id=CHAT_ID)

    session = MagicMock()
    store = MagicMock()
    store.load.return_value = session
    store.store.return_value = None
    runtime = MagicMock()
    runtime.sessions.return_value = store

    with patch("agentkernel.core.runtime.Runtime.current", return_value=runtime):
        asyncio.run(tg_handler._process_webhook_body(_text_update(4, "/new")))

    store.load.assert_called_with(canonical_session_id(user.id))
    session.clear.assert_called_once()
    store.store.assert_called_once_with(session)
    assert "Fresh chat" in tg_handler.sent[0][1]


def test_help_text_lists_commands():
    tg = help_text(channel="telegram")
    assert "/help" in tg and "/new" in tg
    wa = help_text(channel="whatsapp")
    assert "help" in wa and "new" in wa


def test_status_text_unlinked():
    assert "not linked" in status_text(None, channel="telegram").lower()


# -------------------------------------------------------------- WhatsApp


def test_whatsapp_help_does_not_call_agent(db_factory):
    logging.getLogger("agripilot.whatsapp").setLevel(logging.ERROR)
    handler = FastAckWhatsAppHandler()
    handler._skip_marketplace_gate = True  # type: ignore[attr-defined]
    sent: list = []
    executed: list = []

    async def fake_send(to, text, reply_to=None):
        await asyncio.sleep(0)
        sent.append((to, text))

    class _Chat:
        async def execute(self, *args, **kwargs):
            executed.append(1)
            return "agent-should-not-run", None

    handler._send_message = fake_send  # type: ignore[method-assign]
    handler._chat_service = _Chat()  # type: ignore[attr-defined]
    handler._whatsapp_agent_acknowledgement = None

    message = {"id": "wamid.help1", "from": "15556780512", "type": "text", "text": {"body": "/help"}}
    value = {"messaging_product": "whatsapp", "contacts": [{"wa_id": "15556780512"}]}
    asyncio.run(handler._handle_message(message, value))

    assert executed == []
    assert sent and "AgriPilot" in sent[0][1]
    assert "help" in sent[0][1].lower()
