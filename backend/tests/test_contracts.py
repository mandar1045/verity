"""One valid example of every contract model."""

from __future__ import annotations

import uuid

from contracts.schemas import (
    AnalyzeMessageRequest, AnalyzeTransactionRequest, DemoUser, Evidence, FeatureContribution, FeedbackRequest,
    FeedbackResponse, FeedItem, Health, LinkFinding, MessageAnalysis, QuizItem, SampleMessage, Signal, Transaction,
    TxnAnalysis,
)

TXN = Transaction(
    txn_id="T1", user_id="U001", timestamp="2026-10-25T10:32:00+05:30", type="COLLECT_REQUEST", amount_inr=2499,
    payee_vpa="sbi.refund.desk@ybl", payee_name="SBI Refund Desk", channel="VPA", payee_is_new=True,
    payee_account_age_days=3, payee_report_count=0, device_changed=False,
)
SIGNAL = Signal(code="PIN_TO_RECEIVE", title="PIN asked", weight=0.9, description="d",
                evidence=[Evidence(start=0, end=5, text="Enter")])


def test_every_model_builds() -> None:
    analysis = TxnAnalysis(txn_id="T1", risk_score=90, label="HIGH_RISK", signals=[SIGNAL],
                           feature_contributions=[FeatureContribution(feature="f", value="v", contribution=1.2)],
                           explanation="e", next_steps=["s"])
    examples = [
        Health(models_loaded=True),
        SampleMessage(id="s", title="t", text="x", channel="sms"),
        QuizItem(id="q", text="x", channel="sms", is_scam=True, scam_type="PRIZE"),
        AnalyzeMessageRequest(text="hello", channel="sms", lang_out="ta"),
        MessageAnalysis(id=uuid.uuid4(), risk_score=10, label="SAFE", model_prob=0.1, rule_score=0.0, signals=[SIGNAL],
                        links=[LinkFinding(raw="a.com", domain="a.com", verdict="OK", reasons=["r"])],
                        explanation="e", next_steps=["s"]),
        DemoUser(user_id="U001", persona="Student", home_city="Vellore"),
        TXN, analysis, FeedItem(transaction=TXN, analysis=analysis),
        AnalyzeTransactionRequest(transaction=TXN, lang_out="hi"),
        FeedbackRequest(analysis_id="a", kind="message", correct_label="SAFE"),
        FeedbackResponse(),
    ]
    for ex in examples:
        assert type(ex).model_validate(ex.model_dump(mode="json")) == ex
