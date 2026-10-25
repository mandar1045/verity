"""Transaction context + feature vector. Shared by the data generator, training
and the backend, so train-time and serve-time features are computed the same way.
"""

from __future__ import annotations

import math
from collections.abc import Iterable, Mapping
from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Any

OUTGOING = ("PAY", "COLLECT_REQUEST")
NIGHT_HOURS = range(0, 5)

FEATURES: tuple[str, ...] = (
    "amount_log", "amount_vs_median", "hour", "is_night",
    "type_PAY", "type_COLLECT_REQUEST", "type_RECEIVE",
    "channel_QR", "channel_VPA", "channel_PHONE",
    "payee_is_new", "payee_account_age_days", "payee_report_count", "device_changed",
    "txns_last_10m", "inbound_count_24h", "received_then_sent_ratio_24h",
)


@dataclass(frozen=True)
class TxnContext:
    amount_vs_median: float
    txns_last_10m: int
    hour: int
    is_night: bool
    inbound_count_24h: int
    received_then_sent_ratio_24h: float

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


def _ts(value: Any) -> datetime:
    return value if isinstance(value, datetime) else datetime.fromisoformat(str(value))


def compute_context(txn: Mapping[str, Any], history: Iterable[Mapping[str, Any]], user_median: float) -> TxnContext:
    """Context from the user's earlier transactions (any order; only the past 24 h matters)."""
    ts = _ts(txn["timestamp"])
    outgoing = txn["type"] in OUTGOING
    out_10m, in_count, in_sum = 0, 0, 0.0
    for h in history:
        age = (ts - _ts(h["timestamp"])).total_seconds()
        if age < 0 or age > 86_400:
            continue
        if h["type"] == "RECEIVE":
            in_count += 1
            in_sum += float(h["amount_inr"])
        elif age <= 600:
            out_10m += 1
    amount = float(txn["amount_inr"])
    ratio = min(5.0, amount / in_sum) if outgoing and in_sum > 0 else 0.0
    return TxnContext(
        amount_vs_median=round(amount / max(user_median, 1.0), 3),
        txns_last_10m=out_10m + (1 if outgoing else 0),
        hour=ts.hour,
        is_night=ts.hour in NIGHT_HOURS,
        inbound_count_24h=in_count,
        received_then_sent_ratio_24h=round(ratio, 3),
    )


def feature_vector(txn: Mapping[str, Any], ctx: TxnContext) -> list[float]:
    t, ch = txn["type"], txn["channel"]
    return [
        math.log1p(float(txn["amount_inr"])),
        ctx.amount_vs_median,
        float(ctx.hour),
        float(ctx.is_night),
        float(t == "PAY"), float(t == "COLLECT_REQUEST"), float(t == "RECEIVE"),
        float(ch == "QR"), float(ch == "VPA"), float(ch == "PHONE"),
        float(bool(txn["payee_is_new"])),
        float(txn["payee_account_age_days"]),
        float(txn["payee_report_count"]),
        float(bool(txn["device_changed"])),
        float(ctx.txns_last_10m),
        float(ctx.inbound_count_24h),
        ctx.received_then_sent_ratio_24h,
    ]
