"""Optional LLM polish of the template explanation.

Only runs when ANTHROPIC_API_KEY is set AND the request asks for polish=true.
Guardrails (responsible-AI rule: the LLM may re-phrase, never decide):
- the LLM sees only the template explanation and signal titles, never the raw message
- 3-second timeout, no retries
- output is rejected if it adds any number, URL or phone number not in the input,
  or exceeds 90 words
- on any failure the template text is returned with explanation_source="template"
"""

from __future__ import annotations

import logging
import os
import re

log = logging.getLogger(__name__)

MODEL = "claude-opus-5-5"
TIMEOUT_S = 3.0
MAX_WORDS = 90
LANG_NAMES = {"en": "English", "hi": "Hindi (Devanagari script)", "ta": "Tamil"}
_NUMBER = re.compile(r"\d[\d,.:]*")
_URLISH = re.compile(r"(?:https?://|www\.)\S+|\b[\w-]+\.(?:com|in|org|net|xyz|top|ly|gov)\b", re.I)

SYSTEM = (
    "You rewrite short fraud-safety warnings for first-time UPI users so they read warmly and "
    "clearly at a Class 8 reading level. Keep every fact. Do not add facts, numbers, links, phone "
    "numbers or advice that are not in the input. Do not change how risky the message is said to be. "
    "Reply with the rewritten warning only, in at most 80 words."
)


def enabled() -> bool:
    return bool(os.environ.get("ANTHROPIC_API_KEY"))


def _tokens(pattern: re.Pattern[str], text: str) -> set[str]:
    return {m.group(0).strip(".,").lower() for m in pattern.finditer(text)}


def acceptable(original: str, candidate: str, titles: list[str]) -> bool:
    """Reject output that invents numbers/links or runs long."""
    if not candidate or len(candidate.split()) > MAX_WORDS:
        return False
    source = " ".join([original, *titles])
    if not _tokens(_NUMBER, candidate) <= _tokens(_NUMBER, source):
        return False
    return _tokens(_URLISH, candidate) <= _tokens(_URLISH, source)


def _call_llm(explanation: str, titles: list[str], lang: str) -> str | None:
    import anthropic

    client = anthropic.Anthropic(timeout=TIMEOUT_S, max_retries=0)
    prompt = (
        f"Target language: {LANG_NAMES.get(lang, 'English')}\n"
        f"Warning signs found: {'; '.join(titles) or 'none'}\n\n"
        f"Warning to rewrite:\n{explanation}"
    )
    response = client.beta.messages.create(
        model=MODEL,
        max_tokens=2000,
        system=SYSTEM,
        output_config={"effort": "low"},
        betas=["server-side-fallback-2026-07-01"],
        fallbacks="default",
        messages=[{"role": "user", "content": prompt}],
    )
    if response.stop_reason != "end_turn":
        return None
    text = "".join(b.text for b in response.content if b.type == "text").strip()
    return text or None


def polish(explanation: str, titles: list[str], lang: str) -> tuple[str, str]:
    """Return (text, source). Never raises; falls back to the template."""
    if not enabled():
        return explanation, "template"
    try:
        candidate = _call_llm(explanation, titles, lang)
    except Exception as exc:  # noqa: BLE001 - timeouts, auth, network: all fall back
        log.warning("LLM polish skipped: %s", type(exc).__name__)
        return explanation, "template"
    if candidate and acceptable(explanation, candidate, titles):
        return candidate, "llm"
    return explanation, "template"
