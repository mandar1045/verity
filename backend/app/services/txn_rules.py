"""Transaction rules: one detector per injected fraud pattern.

Each detector returns a Signal plus a FeatureContribution so the UI can show
reasons even when the ML model is unavailable.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from backend.app.services import i18n
from contracts.schemas import FeatureContribution, Signal, Transaction
from ml.transaction.features import OUTGOING, TxnContext

ROUND_LIMITS = (2000, 5000, 10000, 20000, 25000, 50000, 100000)
YOUNG_DAYS = 7
BURST_MIN = 4
MULE_MIN_INBOUND = 5


@dataclass(frozen=True)
class TxnHit:
    signal: Signal
    contribution: FeatureContribution


def inr(amount: float) -> str:
    """Indian digit grouping: 1234567 -> 12,34,567."""
    whole = str(int(round(amount)))
    if len(whole) <= 3:
        return whole
    head, tail = whole[:-3], whole[-3:]
    groups = []
    while len(head) > 2:
        groups.insert(0, head[-2:])
        head = head[:-2]
    return ",".join([head, *groups, tail]) if head else ",".join([*groups, tail])


def _hit(code: str, weight: float, evidence: str, feature: str, value: str, lang: str) -> TxnHit:
    signal = Signal(
        code=code,  # type: ignore[arg-type]
        title=i18n.t(f"signal.{code}.title", lang),
        weight=round(min(0.95, weight), 2),
        description=i18n.t(f"signal.{code}.description", lang, evidence=evidence),
        evidence=[],
    )
    return TxnHit(signal, FeatureContribution(feature=feature, value=value, contribution=round(weight, 3)))


Rule = Callable[[Transaction, TxnContext, str], TxnHit | None]


def detect_new_payee_collect(t: Transaction, ctx: TxnContext, lang: str) -> TxnHit | None:
    if t.type != "COLLECT_REQUEST" or not t.payee_is_new:
        return None
    weight = 0.55 + (0.1 if t.payee_account_age_days < 30 else 0.0)
    text = f"{i18n.t('txnfeat.payee_new_yes', lang)} · {i18n.t('txnfeat.type_COLLECT_REQUEST', lang)}"
    return _hit("NEW_PAYEE_COLLECT", weight, text, i18n.t("txnfeat.type_COLLECT_REQUEST", lang), "COLLECT_REQUEST", lang)


def detect_young_payee_account(t: Transaction, ctx: TxnContext, lang: str) -> TxnHit | None:
    if t.type not in OUTGOING or t.payee_account_age_days >= YOUNG_DAYS:
        return None
    weight = 0.65 if t.amount_inr >= 2000 else 0.3
    text = i18n.t("txnfeat.payee_age_young", lang, n=t.payee_account_age_days)
    return _hit("YOUNG_PAYEE_ACCOUNT", weight, text, text, str(t.payee_account_age_days), lang)


def detect_payment_burst(t: Transaction, ctx: TxnContext, lang: str) -> TxnHit | None:
    if t.type not in OUTGOING or ctx.txns_last_10m < BURST_MIN:
        return None
    weight = min(0.75, 0.55 + 0.05 * (ctx.txns_last_10m - BURST_MIN))
    text = i18n.t("txnfeat.burst", lang, n=ctx.txns_last_10m)
    return _hit("PAYMENT_BURST", weight, text, text, str(ctx.txns_last_10m), lang)


def detect_night_high_value(t: Transaction, ctx: TxnContext, lang: str) -> TxnHit | None:
    if t.type not in OUTGOING or not ctx.is_night or ctx.amount_vs_median < 5:
        return None
    hhmm = t.timestamp.strftime("%H:%M")
    ratio = i18n.t("txnfeat.amount_vs_median", lang, x=f"{ctx.amount_vs_median:.1f}")
    text = f"{i18n.t('txnfeat.hour', lang, hhmm=hhmm)} · {ratio}"
    return _hit("NIGHT_HIGH_VALUE", 0.6, text, i18n.t("txnfeat.is_night_yes", lang), hhmm, lang)


def detect_device_change_high_value(t: Transaction, ctx: TxnContext, lang: str) -> TxnHit | None:
    if t.type not in OUTGOING or not t.device_changed or ctx.amount_vs_median < 3:
        return None
    ratio = i18n.t("txnfeat.amount_vs_median", lang, x=f"{ctx.amount_vs_median:.1f}")
    text = f"{i18n.t('txnfeat.device_yes', lang)} · {ratio}"
    return _hit("DEVICE_CHANGE_HIGH_VALUE", 0.6, text, i18n.t("txnfeat.device_yes", lang), "true", lang)


def detect_reported_payee(t: Transaction, ctx: TxnContext, lang: str) -> TxnHit | None:
    if t.type not in OUTGOING or t.payee_report_count <= 0:
        return None
    weight = min(0.8, 0.45 + 0.1 * (t.payee_report_count - 1))
    text = i18n.t("txnfeat.reports_yes", lang, n=t.payee_report_count)
    return _hit("REPORTED_PAYEE", weight, text, text, str(t.payee_report_count), lang)


def detect_just_under_limit(t: Transaction, ctx: TxnContext, lang: str) -> TxnHit | None:
    if t.type not in OUTGOING or not t.payee_is_new:
        return None
    limit = next((lim for lim in ROUND_LIMITS if lim * 0.98 <= t.amount_inr < lim), None)
    if limit is None:
        return None
    text = f"₹{inr(t.amount_inr)} < ₹{inr(limit)} · {i18n.t('txnfeat.payee_new_yes', lang)}"
    return _hit("JUST_UNDER_LIMIT", 0.4, text, i18n.t("txnfeat.amount_inr", lang, amount=inr(t.amount_inr)), str(limit), lang)


def detect_mule_pattern(t: Transaction, ctx: TxnContext, lang: str) -> TxnHit | None:
    if t.type not in OUTGOING or ctx.inbound_count_24h < MULE_MIN_INBOUND or ctx.received_then_sent_ratio_24h < 0.7:
        return None
    pct = round(min(ctx.received_then_sent_ratio_24h, 1.0) * 100)
    text = f"{i18n.t('txnfeat.inbound', lang, n=ctx.inbound_count_24h)} · {i18n.t('txnfeat.ratio', lang, pct=pct)}"
    return _hit("MULE_PATTERN", 0.7, text, i18n.t("txnfeat.ratio", lang, pct=pct), f"{ctx.received_then_sent_ratio_24h:.2f}", lang)


RULES: tuple[Rule, ...] = (
    detect_new_payee_collect, detect_young_payee_account, detect_payment_burst, detect_night_high_value,
    detect_device_change_high_value, detect_reported_payee, detect_just_under_limit, detect_mule_pattern,
)


def run_txn_rules(t: Transaction, ctx: TxnContext, lang: str = "en") -> list[TxnHit]:
    hits = [h for h in (rule(t, ctx, lang) for rule in RULES) if h is not None]
    return sorted(hits, key=lambda h: h.signal.weight, reverse=True)


def txn_rule_score(hits: list[TxnHit]) -> float:
    remaining = 1.0
    for h in hits:
        remaining *= 1.0 - h.signal.weight
    return round(1.0 - remaining, 4)


def describe_feature(name: str, t: Transaction, ctx: TxnContext, lang: str) -> tuple[str, str]:
    """Plain-language sentence and display value for a model feature."""
    if name == "amount_log":
        return i18n.t("txnfeat.amount_inr", lang, amount=inr(t.amount_inr)), f"₹{inr(t.amount_inr)}"
    if name == "amount_vs_median":
        x = f"{ctx.amount_vs_median:.1f}"
        return i18n.t("txnfeat.amount_vs_median", lang, x=x), f"{x}×"
    if name == "hour":
        hhmm = t.timestamp.strftime("%H:%M")
        return i18n.t("txnfeat.hour", lang, hhmm=hhmm), hhmm
    if name == "is_night":
        return i18n.t(f"txnfeat.is_night_{'yes' if ctx.is_night else 'no'}", lang), str(ctx.is_night).lower()
    if name == "type":
        return i18n.t(f"txnfeat.type_{t.type}", lang), t.type
    if name == "channel":
        return i18n.t(f"txnfeat.channel_{t.channel}", lang), t.channel
    if name == "payee_is_new":
        return i18n.t(f"txnfeat.payee_new_{'yes' if t.payee_is_new else 'no'}", lang), str(t.payee_is_new).lower()
    if name == "payee_account_age_days":
        key = "payee_age_young" if t.payee_account_age_days < 30 else "payee_age_old"
        return i18n.t(f"txnfeat.{key}", lang, n=t.payee_account_age_days), f"{t.payee_account_age_days}d"
    if name == "payee_report_count":
        key = "reports_yes" if t.payee_report_count else "reports_no"
        return i18n.t(f"txnfeat.{key}", lang, n=t.payee_report_count), str(t.payee_report_count)
    if name == "device_changed":
        return i18n.t(f"txnfeat.device_{'yes' if t.device_changed else 'no'}", lang), str(t.device_changed).lower()
    if name == "txns_last_10m":
        return i18n.t("txnfeat.burst", lang, n=ctx.txns_last_10m), str(ctx.txns_last_10m)
    if name == "inbound_count_24h":
        return i18n.t("txnfeat.inbound", lang, n=ctx.inbound_count_24h), str(ctx.inbound_count_24h)
    pct = round(min(ctx.received_then_sent_ratio_24h, 5.0) * 100)
    return i18n.t("txnfeat.ratio", lang, pct=pct), f"{pct}%"
