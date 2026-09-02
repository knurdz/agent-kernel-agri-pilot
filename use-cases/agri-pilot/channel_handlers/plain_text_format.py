"""Convert Markdown emphasis to Unicode mathematical styled characters.

Telegram and WhatsApp send agent replies as plain text (no parse_mode).
LLM replies often contain CommonMark ``**bold**`` / ``*italic*``, which
appear as literal asterisks. This module rewrites those markers to Unicode
Mathematical Bold / Italic so the text still looks emphasized without
Markdown rendering.

Mobile in-app chat already renders Markdown and must keep the raw markers;
call this only on Telegram / WhatsApp outbound agent replies.
"""

from __future__ import annotations

import re

# Mathematical Bold: A-Z, a-z, 0-9
_BOLD_UPPER = {chr(ord("A") + i): chr(0x1D400 + i) for i in range(26)}
_BOLD_LOWER = {chr(ord("a") + i): chr(0x1D41A + i) for i in range(26)}
_BOLD_DIGIT = {chr(ord("0") + i): chr(0x1D7CE + i) for i in range(10)}
_BOLD_MAP = {**_BOLD_UPPER, **_BOLD_LOWER, **_BOLD_DIGIT}

# Mathematical Italic: A-Z, a-z (digits have no italic math forms)
# Special case: Mathematical Italic Small H is U+210E (Planck constant), not in the block.
_ITALIC_UPPER = {chr(ord("A") + i): chr(0x1D434 + i) for i in range(26)}
_ITALIC_LOWER = {chr(ord("a") + i): chr(0x1D44E + i) for i in range(26)}
_ITALIC_LOWER["h"] = "\u210e"
_ITALIC_MAP = {**_ITALIC_UPPER, **_ITALIC_LOWER}

# Mathematical Bold Italic: A-Z, a-z
_BOLD_ITALIC_UPPER = {chr(ord("A") + i): chr(0x1D468 + i) for i in range(26)}
_BOLD_ITALIC_LOWER = {chr(ord("a") + i): chr(0x1D482 + i) for i in range(26)}
_BOLD_ITALIC_MAP = {**_BOLD_ITALIC_UPPER, **_BOLD_ITALIC_LOWER}

# Protect URLs and fenced/inline code so underscores in links aren't italicized.
_URL_RE = re.compile(r"https?://[^\s<>\]]+", re.IGNORECASE)
_FENCED_CODE_RE = re.compile(r"```[\s\S]*?```")
_INLINE_CODE_RE = re.compile(r"`[^`\n]+`")

# Emphasis patterns — longest first so *** wins over ** over *
_BOLD_ITALIC_RE = re.compile(r"(?<!\*)\*\*\*(?!\*)(.+?)(?<!\*)\*\*\*(?!\*)|(?<!_)___(?!_)(.+?)(?<!_)___(?!_)")
_BOLD_RE = re.compile(r"(?<!\*)\*\*(?!\*)(.+?)(?<!\*)\*\*(?!\*)|(?<!_)__(?!_)(.+?)(?<!_)__(?!_)")
# Single * / _ — avoid matching ** leftovers; require non-empty, non-whitespace-only span
_ITALIC_RE = re.compile(
    r"(?<!\*)\*(?!\*)([^*\n]+?)(?<!\*)\*(?!\*)|(?<!_)_(?!_)([^_\n]+?)(?<!_)_(?!_)"
)


def _style_chars(text: str, mapping: dict[str, str]) -> str:
    return "".join(mapping.get(ch, ch) for ch in text)


def _protect(text: str) -> tuple[str, list[str]]:
    """Replace URLs and code spans with placeholders; return (masked, stash)."""
    stash: list[str] = []

    def _stash(match: re.Match[str]) -> str:
        stash.append(match.group(0))
        return f"\x00P{len(stash) - 1}\x00"

    out = _FENCED_CODE_RE.sub(_stash, text)
    out = _INLINE_CODE_RE.sub(_stash, out)
    out = _URL_RE.sub(_stash, out)
    return out, stash


def _restore(text: str, stash: list[str]) -> str:
    for i, original in enumerate(stash):
        text = text.replace(f"\x00P{i}\x00", original)
    return text


def _strip_inline_code_backticks(text: str) -> str:
    """Remove single backticks around inline code (content already protected or plain)."""

    def _repl(match: re.Match[str]) -> str:
        return match.group(0)[1:-1]

    return _INLINE_CODE_RE.sub(_repl, text)


def _apply_emphasis(text: str) -> str:
    def bold_italic(m: re.Match[str]) -> str:
        inner = m.group(1) if m.group(1) is not None else m.group(2)
        return _style_chars(inner, _BOLD_ITALIC_MAP)

    def bold(m: re.Match[str]) -> str:
        inner = m.group(1) if m.group(1) is not None else m.group(2)
        return _style_chars(inner, _BOLD_MAP)

    def italic(m: re.Match[str]) -> str:
        inner = m.group(1) if m.group(1) is not None else m.group(2)
        return _style_chars(inner, _ITALIC_MAP)

    text = _BOLD_ITALIC_RE.sub(bold_italic, text)
    text = _BOLD_RE.sub(bold, text)
    text = _ITALIC_RE.sub(italic, text)
    return text


def to_unicode_emphasis(text: str) -> str:
    """Rewrite Markdown emphasis markers into Unicode styled characters.

    Non-ASCII letters (e.g. Sinhala) pass through unchanged. URLs and code
    fences are left alone so underscores in links are not treated as italic.
    Inline ``code`` backticks are stripped after protection restore so plain
    messaging clients do not show stray backticks.
    """
    if not text or ("*" not in text and "_" not in text and "`" not in text):
        return text

    masked, stash = _protect(text)
    converted = _apply_emphasis(masked)
    restored = _restore(converted, stash)
    # Strip backticks from inline code segments that were protected (still have `...`)
    restored = _strip_inline_code_backticks(restored)
    return restored
