from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from backend.app.services.txn_rules import inr, run_txn_rules, txn_rule_score
from contracts.schemas import Transaction
from ml.transaction.features import compute_context

IST = timezone(timedelta(hours=5, minutes=30))
BASE = datetime(2026, 10, 25, 14, 0, tzinfo=IST)


def txn(**kw: object) -> Transaction:
    data: dict[str, object] = {
        "txn_id": "T1", "user_id": "U9", "timestamp": BASE, "type": "PAY", "amount_inr": 100.0,
        "payee_vpa": "shop@ybl", "payee_name": "Shop", "channel": "QR", "payee_is_new": False,
        "payee_account_age_days": 900, "payee_report_count": 0, "device_changed": False,
    }
    data.update(kw)
    return Transaction.model_validate(data)


def codes(t: Transaction, history: list[dict[str, object]] | None = None, median: float = 200) -> set[str]:
    ctx = compute_context(t.model_dump(), history or [], median)
    return {h.signal.code for h in run_txn_rules(t, ctx)}


def test_normal_payment_is_clean() -> None:
    assert codes(txn()) == set()


def test_new_payee_collect() -> None:
    assert "NEW_PAYEE_COLLECT" in codes(txn(type="COLLECT_REQUEST", payee_is_new=True, payee_account_age_days=3))


def test_young_payee_account() -> None:
    assert "YOUNG_PAYEE_ACCOUNT" in codes(txn(amount_inr=5000, payee_is_new=True, payee_account_age_days=2))


def test_payment_burst() -> None:
    history = [txn(txn_id=f"b{i}", timestamp=BASE - timedelta(minutes=i + 1)).model_dump() for i in range(4)]
    assert "PAYMENT_BURST" in codes(txn(), history)


def test_night_high_value() -> None:
    assert "NIGHT_HIGH_VALUE" in codes(txn(timestamp=BASE.replace(hour=2, minute=10), amount_inr=1800))


def test_device_change_high_value() -> None:
    assert "DEVICE_CHANGE_HIGH_VALUE" in codes(txn(device_changed=True, amount_inr=4000))


def test_reported_payee() -> None:
    assert "REPORTED_PAYEE" in codes(txn(payee_report_count=3))


def test_just_under_limit() -> None:
    assert "JUST_UNDER_LIMIT" in codes(txn(amount_inr=9999, payee_is_new=True))
    assert "JUST_UNDER_LIMIT" not in codes(txn(amount_inr=9999, payee_is_new=False))


def test_mule_pattern() -> None:
    inbound = [txn(txn_id=f"r{i}", type="RECEIVE", amount_inr=1000, timestamp=BASE - timedelta(minutes=20 * (i + 1))).model_dump() for i in range(8)]
    assert "MULE_PATTERN" in codes(txn(amount_inr=7800, payee_is_new=True), inbound)


def test_receive_never_flags() -> None:
    assert codes(txn(type="RECEIVE", amount_inr=90000, payee_report_count=5, device_changed=True)) == set()


def test_rule_score_bounds() -> None:
    t = txn(type="COLLECT_REQUEST", payee_is_new=True, payee_account_age_days=3, amount_inr=2499)
    hits = run_txn_rules(t, compute_context(t.model_dump(), [], 300))
    assert 0.7 < txn_rule_score(hits) < 1


@pytest.mark.parametrize(("n", "s"), [(80, "80"), (2499, "2,499"), (48000, "48,000"), (1250000, "12,50,000")])
def test_indian_number_format(n: float, s: str) -> None:
    assert inr(n) == s
