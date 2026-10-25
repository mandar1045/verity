"""Deterministic explanation engine.

The explanation is a headline chosen by label plus one plain sentence for each
of the top three signals, capped at 70 words. Next steps come from
next_steps.yaml by scam_type and label. An LLM may later re-phrase this text
(see polish.py) but never changes the label, score or steps.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

from backend.app.services import i18n
from contracts.schemas import Signal

STEPS_PATH = Path(__file__).parent / "next_steps.yaml"
MAX_WORDS = 70
MAX_STEPS = 5
COLLECT_ONLY_STEPS = frozenset({"decline_collect"})


@lru_cache(maxsize=1)
def _steps_config() -> dict[str, Any]:
    return yaml.safe_load(STEPS_PATH.read_text(encoding="utf-8")) or {}


def _word_count(text: str) -> int:
    return len(text.split())


def _compose(headline: str, sentences: list[str]) -> str:
    parts = [headline]
    for s in sentences:
        if _word_count(" ".join([*parts, s])) > MAX_WORDS:
            break
        parts.append(s)
    return " ".join(parts)


def _top_sentences(signals: list[Signal], lang: str, limit: int = 3) -> list[str]:
    ranked = sorted(signals, key=lambda s: (s.code in ("MODEL_TEXT", "MODEL_TXN"), -s.weight))
    seen: set[str] = set()
    out: list[str] = []
    for s in ranked:
        if s.code in seen:
            continue
        seen.add(s.code)
        out.append(i18n.t(f"signal.{s.code}.sentence", lang))
        if len(out) == limit:
            break
    return out


def _dedupe(keys: list[str]) -> list[str]:
    return list(dict.fromkeys(keys))


def explain_message(label: str, signals: list[Signal], scam_type: str | None, lang: str) -> tuple[str, list[str]]:
    headline = i18n.t(f"headline.{label}", lang)
    explanation = headline if label == "SAFE" else _compose(headline, _top_sentences(signals, lang))
    cfg = _steps_config()
    if label == "SAFE":
        keys = list(cfg["label"]["SAFE"])
    else:
        keys = list(cfg["scam_type"].get(scam_type or "", cfg["label"][label]))
        for s in signals:
            keys += cfg["signals"].get(s.code, [])
        if label == "HIGH_RISK":
            keys.append("call_1930")
    steps = [i18n.t(f"step.{k}", lang) for k in _dedupe(keys)[:MAX_STEPS]]
    return explanation, steps


def explain_transaction(label: str, signals: list[Signal], txn_type: str, lang: str) -> tuple[str, list[str]]:
    headline = i18n.t(f"txn_headline.{label}", lang)
    explanation = headline if label == "SAFE" else _compose(headline, _top_sentences(signals, lang))
    cfg = _steps_config()
    keys = list(cfg["txn_label"][label])
    if label != "SAFE":
        for s in signals:
            keys += cfg["txn_signals"].get(s.code, [])
    if txn_type != "COLLECT_REQUEST":
        keys = [k for k in keys if k not in COLLECT_ONLY_STEPS and k != "pin_only_sends"]
    steps = [i18n.t(f"step.{k}", lang) for k in _dedupe(keys)[:MAX_STEPS]]
    return explanation, steps
