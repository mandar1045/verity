"""Transaction analysis: context -> rules + GBM (SHAP) -> risk -> explanation.

risk = max(calibrated model probability, rule floor). Without a model the
rules alone decide and their contributions are shown instead of SHAP.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from backend.app.services import i18n
from backend.app.services.explain import explain_transaction
from backend.app.services.registry import DEMO_FEED, Registry
from backend.app.services.scoring import calibrate
from backend.app.services.txn_rules import describe_feature, run_txn_rules, txn_rule_score
from contracts.schemas import DemoUser, FeatureContribution, FeedItem, Signal, Transaction, TxnAnalysis, label_for
from ml.transaction.features import TxnContext, compute_context

DEFAULT_MEDIAN = 500.0


def _model_signal(prob: float, lang: str) -> Signal:
    return Signal(
        code="MODEL_TXN", title=i18n.t("signal.MODEL_TXN.title", lang), weight=round(min(prob, 0.95), 2),
        description=i18n.t("signal.MODEL_TXN.sentence", lang), evidence=[],
    )


def _model_part(t: Transaction, ctx: TxnContext, reg: Registry, lang: str) -> tuple[int, list[FeatureContribution], Signal | None]:
    assert reg.txn_model is not None
    prob, contribs = reg.txn_model.predict(t.model_dump(), ctx)
    score = calibrate(prob, reg.txn_model.threshold)
    features = []
    for name, value in contribs:
        sentence, shown = describe_feature(name, t, ctx, lang)
        features.append(FeatureContribution(feature=sentence, value=shown, contribution=value))
    signal = _model_signal(prob, lang) if prob >= reg.txn_model.threshold else None
    return score, features, signal


def analyze_transaction(
    t: Transaction, history: list[dict[str, Any]], user_median: float, lang: str, reg: Registry
) -> TxnAnalysis:
    ctx = compute_context(t.model_dump(), history, user_median)
    hits = run_txn_rules(t, ctx, lang)
    signals = [h.signal for h in hits]
    rules = txn_rule_score(hits)
    if reg.txn_model is not None:
        model_score, contributions, model_signal = _model_part(t, ctx, reg, lang)
        if model_signal:
            signals.append(model_signal)
        floor = int(round(100 * rules)) if rules >= reg.txn_model.floor_min else 0
        risk = max(model_score, floor)
    else:
        risk, contributions = int(round(100 * rules)), [h.contribution for h in hits]
    label = label_for(risk)
    explanation, steps = explain_transaction(label, signals, t.type, lang)
    return TxnAnalysis(
        txn_id=t.txn_id, risk_score=risk, label=label, signals=signals,
        feature_contributions=contributions, explanation=explanation, next_steps=steps,
        explanation_source="template",
    )


class DemoFeed:
    """The hand-crafted demo accounts from data/processed/demo_feed.json."""

    def __init__(self, path: Path = DEMO_FEED) -> None:
        data = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {"users": [], "transactions": []}
        self._users = {u["user_id"]: u for u in data["users"]}
        self._txns: dict[str, list[Transaction]] = {}
        for raw in data["transactions"]:
            self._txns.setdefault(raw["user_id"], []).append(Transaction.model_validate(raw))
        for rows in self._txns.values():
            rows.sort(key=lambda x: x.timestamp)
        self._cache: dict[tuple[str, str], list[FeedItem]] = {}

    def users(self) -> list[DemoUser]:
        return [DemoUser(user_id=u["user_id"], persona=u["persona"], home_city=u["home_city"]) for u in self._users.values()]

    def has_user(self, user_id: str) -> bool:
        return user_id in self._users

    def median(self, user_id: str) -> float:
        return float(self._users.get(user_id, {}).get("median_amount", DEFAULT_MEDIAN))

    def history(self, user_id: str, before: datetime, exclude: str | None = None) -> list[dict[str, Any]]:
        return [x.model_dump() for x in self._txns.get(user_id, []) if x.timestamp < before and x.txn_id != exclude]

    def transactions(self, user_id: str) -> list[Transaction]:
        return list(self._txns.get(user_id, []))

    def feed(self, user_id: str, lang: str, reg: Registry, limit: int) -> list[FeedItem]:
        """Newest first. Cached per (user, language) because the demo feed is static."""
        key = (user_id, lang)
        if key not in self._cache:
            items = []
            for t in self.transactions(user_id):
                history = self.history(user_id, t.timestamp, t.txn_id)
                items.append(FeedItem(transaction=t, analysis=analyze_transaction(t, history, self.median(user_id), lang, reg)))
            self._cache[key] = list(reversed(items))
        return self._cache[key][:limit]
