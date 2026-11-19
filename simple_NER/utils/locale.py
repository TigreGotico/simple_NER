"""Locale-based pattern loader for simple_NER annotators.

Supports two file types under ``simple_NER/locale/<lang>/``:

* ``<name>.rx``     — one raw regex per non-blank, non-comment line.
* ``<name>.intent`` — natural language templates with ``{variable}``
  placeholders that are compiled to named-capture-group regexes.

Both file types fall back to ``en`` when a language-specific file
does not exist.  Language tags are normalised to their primary subtag:
``"de-DE"`` and ``"de-de"`` both resolve to the ``de/`` directory.

Usage::

    from simple_NER.utils.locale import load_rx, load_intents, intent_to_regex

    patterns = load_rx("phone", "de-DE")   # list[re.Pattern]  → locale/de/phone.rx
    captures = load_intents("currency", "fr-FR")  # list[re.Pattern]  → locale/fr/currency.intent
"""
from __future__ import annotations

import re
from pathlib import Path

_LOCALE_DIR = Path(__file__).parent.parent / "locale"


def _locale_path(name: str, ext: str, lang: str) -> Path | None:
    """Return the best matching locale file path or None.

    Normalises *lang* to its primary subtag (``"de-DE"`` → ``"de"``) and
    tries ``<lang>/<name>.<ext>`` then ``en/<name>.<ext>``.
    """
    lang = lang.lower().split("-")[0]
    for candidate in (lang, "en"):
        path = _LOCALE_DIR / candidate / f"{name}.{ext}"
        if path.exists():
            return path
    return None


def _read_lines(path: Path) -> list[str]:
    """Read non-blank, non-comment lines from *path*."""
    lines = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if line and not line.startswith("#"):
            lines.append(line)
    return lines


def intent_to_regex(template: str, flags: re.RegexFlag = re.IGNORECASE) -> re.Pattern[str]:
    r"""Compile an ``.intent`` template to a named-capture-group regex.

    ``{variable}`` placeholders become ``(?P<variable>.+?)`` groups.
    All literal text between placeholders is ``re.escape``\d.

    Args:
        template: Template string, e.g. ``"the price is {amount} {currency}"``.
        flags: Regex flags to apply (default: ``re.IGNORECASE``).

    Returns:
        Compiled regex pattern.

    Example::

        p = intent_to_regex("send {amount} to {recipient}")
        m = p.search("send 50 dollars to Alice")
        m.group("amount")    # "50 dollars"
        m.group("recipient") # "Alice"
    """
    parts = re.split(r"\{(\w+)\}", template)
    buf: list[str] = []
    for i, part in enumerate(parts):
        if i % 2 == 0:
            buf.append(re.escape(part))
        else:
            buf.append(f"(?P<{part}>.+?)")
    return re.compile("".join(buf), flags)


def load_rx(
    name: str,
    lang: str = "en-us",
    flags: re.RegexFlag = re.IGNORECASE,
) -> list[re.Pattern[str]]:
    """Load and compile regex patterns from ``locale/<lang>/<name>.rx``.

    Args:
        name: File stem (e.g. ``"phone"``).
        lang: BCP-47 language tag.
        flags: Regex flags applied to every pattern.

    Returns:
        List of compiled patterns; empty list if no file found or all lines fail.
    """
    path = _locale_path(name, "rx", lang)
    if path is None:
        return []
    compiled = []
    for line in _read_lines(path):
        try:
            compiled.append(re.compile(line, flags))
        except re.error:
            pass  # malformed line — skip silently
    return compiled


def load_wordlist(
    name: str,
    lang: str = "en-us",
) -> list[str]:
    """Load a plain wordlist from ``locale/<lang>/<name>.txt``.

    Args:
        name: File stem (e.g. ``"date_months"``).
        lang: BCP-47 language tag.

    Returns:
        List of non-blank, non-comment lines; empty list if no file found.
    """
    path = _locale_path(name, "txt", lang)
    if path is None:
        return []
    return _read_lines(path)


def load_intents(
    name: str,
    lang: str = "en-us",
    flags: re.RegexFlag = re.IGNORECASE,
) -> list[re.Pattern[str]]:
    """Load and compile ``.intent`` templates from ``locale/<lang>/<name>.intent``.

    Args:
        name: File stem (e.g. ``"currency"``).
        lang: BCP-47 language tag.
        flags: Regex flags applied to every compiled pattern.

    Returns:
        List of compiled patterns with named capture groups.
    """
    path = _locale_path(name, "intent", lang)
    if path is None:
        return []
    compiled = []
    for line in _read_lines(path):
        try:
            compiled.append(intent_to_regex(line, flags))
        except re.error:
            pass
    return compiled
