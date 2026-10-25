from __future__ import annotations

import time

import pytest
from fastapi.testclient import TestClient

from contracts.schemas import DemoUser, FeedItem, Health, MessageAnalysis, QuizItem, SampleMessage, TxnAnalysis

FAKE_KYC = "Dear Customer, your SBI account will be blocked today. Update your KYC immediately at http://sbi-kyc-verify.xyz/update"
BANK_OTP = "482910 is your OTP for txn of Rs 1,250.00 at AMAZON. Do not share this OTP with anyone. SBI never asks for OTP. -SBI"


def post_message(client: TestClient, text: str, **kw: object) -> dict[str, object]:
    body = {"text": text, "channel": "sms", "sender": None, "lang_out": "en"} | kw
    r = client.post("/api/v1/analyze/message", json=body)
    assert r.status_code == 200, r.text
    return MessageAnalysis.model_validate(r.json()).model_dump(mode="json")


def test_health(client: TestClient) -> None:
    assert Health.model_validate(client.get("/api/v1/health").json()).status == "ok"


def test_samples(client: TestClient) -> None:
    items = [SampleMessage.model_validate(x) for x in client.get("/api/v1/samples/messages").json()]
    assert len(items) >= 6


def test_quiz(client: TestClient) -> None:
    items = [QuizItem.model_validate(x) for x in client.get("/api/v1/samples/quiz").json()]
    assert len(items) == 5 and any(i.is_scam for i in items) and any(not i.is_scam for i in items)


def test_fake_kyc_is_high_risk_with_offsets(client: TestClient) -> None:
    d = post_message(client, FAKE_KYC, sender="AX-SBIUPD")
    assert d["label"] == "HIGH_RISK"
    for s in d["signals"]:
        for e in s["evidence"]:
            assert FAKE_KYC[e["start"]:e["end"]] == e["text"]
    assert any(lk["verdict"] == "DANGEROUS" for lk in d["links"])


def test_genuine_otp_is_safe(client: TestClient) -> None:
    assert post_message(client, BANK_OTP, sender="VM-SBIOTP")["label"] == "SAFE"


def test_hindi_output(client: TestClient) -> None:
    d = post_message(client, "Enter UPI PIN to receive Rs 5,000 refund", lang_out="hi")
    assert any("ऀ" <= ch <= "ॿ" for ch in str(d["explanation"]))


@pytest.mark.parametrize("text", ["", " ", "x" * 2001])
def test_invalid_message_is_422(client: TestClient, text: str) -> None:
    r = client.post("/api/v1/analyze/message", json={"text": text, "channel": "sms", "lang_out": "en"})
    assert r.status_code == 422 and isinstance(r.json()["detail"], str)


@pytest.mark.parametrize(
    "text",
    ["😂🔥🙏", "https://sbi-kyc.xyz", "தமிழ் English हिन्दी mixed 9876543210", "<b>hi</b> <i>there</i>",
     "a" * 500, "<script>alert('x')</script>", "Rs.500 a/c no. 12 e.g."],
)
def test_odd_inputs_never_500(client: TestClient, text: str) -> None:
    d = post_message(client, text)
    assert 0 <= int(d["risk_score"]) <= 100


def test_demo_users_and_feed(client: TestClient) -> None:
    users = [DemoUser.model_validate(u) for u in client.get("/api/v1/transactions/demo-users").json()]
    assert {u.user_id for u in users} == {"U001", "U002", "U003"}
    feed = [FeedItem.model_validate(x) for x in client.get("/api/v1/transactions/feed?user_id=U003&limit=50").json()]
    newest = feed[0]
    assert newest.transaction.type == "COLLECT_REQUEST" and newest.analysis.label == "HIGH_RISK"
    assert newest.analysis.feature_contributions


def test_feed_unknown_user_404(client: TestClient) -> None:
    assert client.get("/api/v1/transactions/feed?user_id=NOPE").status_code == 404


def test_analyze_transaction(client: TestClient) -> None:
    txn = {"txn_id": "X1", "user_id": "U001", "timestamp": "2026-10-24T13:05:00+05:30", "type": "PAY",
           "amount_inr": 80, "payee_vpa": "foodcourt.vit@ybl", "payee_name": "VIT Food Court", "channel": "QR",
           "payee_is_new": False, "payee_account_age_days": 1100, "payee_report_count": 0, "device_changed": False}
    r = client.post("/api/v1/analyze/transaction", json={"transaction": txn, "lang_out": "en"})
    assert r.status_code == 200
    assert TxnAnalysis.model_validate(r.json()).label == "SAFE"


@pytest.mark.parametrize(
    "patch",
    [{"amount_inr": -5}, {"timestamp": "2099-01-01T00:00:00+05:30"}, {"type": "STEAL"}, {"payee_vpa": None}],
)
def test_malformed_transaction_is_422(client: TestClient, patch: dict[str, object]) -> None:
    txn = {"txn_id": "X2", "user_id": "U001", "timestamp": "2026-10-24T13:05:00+05:30", "type": "PAY",
           "amount_inr": 80, "payee_vpa": "a@ybl", "payee_name": "A", "channel": "QR", "payee_is_new": False,
           "payee_account_age_days": 10, "payee_report_count": 0, "device_changed": False} | patch
    r = client.post("/api/v1/analyze/transaction", json={"transaction": txn, "lang_out": "en"})
    assert r.status_code == 422


def test_feedback(client: TestClient) -> None:
    r = client.post("/api/v1/feedback", json={"analysis_id": "abc", "kind": "message", "correct_label": "SAFE", "note": "call 9876543210"})
    assert r.json() == {"ok": True}


def test_metrics(client: TestClient) -> None:
    r = client.get("/api/v1/metrics")
    assert r.status_code == 200 and "message" in r.json()


def test_p95_latency_under_300ms(client: TestClient) -> None:
    times = []
    for _ in range(50):
        t = time.perf_counter()
        post_message(client, FAKE_KYC)
        times.append((time.perf_counter() - t) * 1000)
    p95 = sorted(times)[int(0.95 * len(times)) - 1]
    print(f"p95 /analyze/message latency: {p95:.1f} ms")
    assert p95 < 300
