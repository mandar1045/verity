"""Tiny i18n layer over app/services/i18n/{en,hi,ta}.yaml with English fallback."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

I18N_DIR = Path(__file__).parent / "i18n"
LANGS = ("en", "hi", "ta")


class _SafeDict(dict[str, Any]):
    def __missing__(self, key: str) -> str:
        return ""


@lru_cache(maxsize=None)
def _load(lang: str) -> dict[str, Any]:
    path = I18N_DIR / f"{lang}.yaml"
    if not path.exists():
        return {}
    with path.open(encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def _lookup(tree: dict[str, Any], key: str) -> str | None:
    node: Any = tree
    for part in key.split("."):
        if not isinstance(node, dict) or part not in node:
            return None
        node = node[part]
    return node if isinstance(node, str) else None


def t(key: str, lang: str = "en", **params: Any) -> str:
    """Translate a dotted key. Falls back to English, then to the key itself."""
    text = _lookup(_load(lang), key) if lang in LANGS else None
    if text is None:
        text = _lookup(_load("en"), key)
    if text is None:
        return key
    return text.format_map(_SafeDict(params)) if params else text


def has(key: str, lang: str = "en") -> bool:
    return _lookup(_load(lang), key) is not None
