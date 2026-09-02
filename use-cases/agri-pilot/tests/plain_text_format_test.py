"""Tests for Markdown → Unicode emphasis conversion for plain chat channels."""

from channel_handlers.plain_text_format import to_unicode_emphasis


def _bold(s: str) -> str:
    """Expected Mathematical Bold for ASCII letters/digits (mirrors implementation)."""
    out = []
    for ch in s:
        if "A" <= ch <= "Z":
            out.append(chr(0x1D400 + (ord(ch) - ord("A"))))
        elif "a" <= ch <= "z":
            out.append(chr(0x1D41A + (ord(ch) - ord("a"))))
        elif "0" <= ch <= "9":
            out.append(chr(0x1D7CE + (ord(ch) - ord("0"))))
        else:
            out.append(ch)
    return "".join(out)


def _italic(s: str) -> str:
    out = []
    for ch in s:
        if "A" <= ch <= "Z":
            out.append(chr(0x1D434 + (ord(ch) - ord("A"))))
        elif ch == "h":
            out.append("\u210e")
        elif "a" <= ch <= "z":
            out.append(chr(0x1D44E + (ord(ch) - ord("a"))))
        else:
            out.append(ch)
    return "".join(out)


def _bold_italic(s: str) -> str:
    out = []
    for ch in s:
        if "A" <= ch <= "Z":
            out.append(chr(0x1D468 + (ord(ch) - ord("A"))))
        elif "a" <= ch <= "z":
            out.append(chr(0x1D482 + (ord(ch) - ord("a"))))
        else:
            out.append(ch)
    return "".join(out)


def test_bold_double_asterisk():
    result = to_unicode_emphasis("The issue is **Early Blight** on tomatoes.")
    assert "**" not in result
    assert _bold("Early Blight") in result
    assert result.startswith("The issue is ")


def test_bold_double_underscore():
    result = to_unicode_emphasis("Use __Fungicide__ carefully.")
    assert "__" not in result
    assert _bold("Fungicide") in result


def test_italic_single_asterisk():
    result = to_unicode_emphasis("Keep foliage *dry*.")
    assert result == f"Keep foliage {_italic('dry')}."


def test_italic_single_underscore():
    result = to_unicode_emphasis("Keep foliage _dry_.")
    assert result == f"Keep foliage {_italic('dry')}."


def test_italic_special_h():
    result = to_unicode_emphasis("*the*")
    assert result == _italic("the")
    assert "\u210e" in result  # Planck h for mathematical italic h


def test_bold_italic_triple():
    result = to_unicode_emphasis("***Urgent*** action needed.")
    assert "***" not in result
    assert _bold_italic("Urgent") in result


def test_order_triple_before_double_before_single():
    text = "See ***both***, then **bold**, then *italic*."
    result = to_unicode_emphasis(text)
    assert "***" not in result and "**" not in result
    assert _bold_italic("both") in result
    assert _bold("bold") in result
    assert _italic("italic") in result


def test_screenshot_style_numbered_steps():
    text = (
        "The issue with your tomato plants is **Early Blight**, a fungal disease.\n\n"
        "1. **Remove infected leaves:** Pick off and destroy affected leaves.\n"
        "2. **Water at the base:** Avoid wetting the foliage.\n"
        "3. **Improve airflow:** Space plants and prune lower leaves.\n"
        "4. **Fungicide:** Use a copper-based fungicide, but "
        "**always follow the label instructions** for safety and dosage."
    )
    result = to_unicode_emphasis(text)
    assert "**" not in result
    assert _bold("Early Blight") in result
    assert _bold("Remove infected leaves") in result
    assert _bold("always follow the label instructions") in result
    assert "1. " in result and "4. " in result


def test_noop_plain_text():
    plain = "Sorry, there was an error processing your request."
    assert to_unicode_emphasis(plain) == plain


def test_noop_empty():
    assert to_unicode_emphasis("") == ""


def test_url_underscores_preserved():
    url = "https://example.com/path_with_underscores?a=1"
    text = f"Read more: {url} and **act** now."
    result = to_unicode_emphasis(text)
    assert url in result
    assert _bold("act") in result
    assert "**" not in result


def test_inline_code_backticks_stripped():
    result = to_unicode_emphasis("Run `npm install` then **restart**.")
    assert "`" not in result
    assert "npm install" in result
    assert _bold("restart") in result


def test_non_ascii_passes_through():
    text = "රෝගය **Early Blight** වේ"
    result = to_unicode_emphasis(text)
    assert "රෝගය" in result
    assert _bold("Early Blight") in result
