"""Pydantic v2 models for the Verity API. Mirrors contracts/api.md and types.ts."""

from __future__ import annotations

from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

Label = Literal["SAFE", "SUSPICIOUS", "HIGH_RISK"]
Channel = Literal["sms", "whatsapp", "email"]
Lang = Literal["en", "hi", "ta"]
ExplanationSource = Literal["template", "llm"]
LinkVerdict = Literal["OK", "SUSPICIOUS", "DANGEROUS"]
TxnType = Literal["PAY", "COLLECT_REQUEST", "RECEIVE"]
TxnChannel = Literal["QR", "VPA", "PHONE"]
FeedbackKind = Literal["message", "transaction"]

SignalCode = Literal[
    "URGENCY",
    "ACCOUNT_THREAT",
    "CREDENTIAL_REQUEST",
    "PIN_TO_RECEIVE",
    "SUSPICIOUS_LINK",
    "LOOKALIKE_DOMAIN",
    "URL_SHORTENER",
    "REMOTE_ACCESS_APP",
    "PRIZE_LURE",
    "PAY_TO_EARN",
    "IMPERSONATION",
    "KYC_UPDATE",
    "SENDER_MISMATCH",
    "CALLBACK_NUMBER",
    "MODEL_TEXT",
    "NEW_PAYEE_COLLECT",
    "YOUNG_PAYEE_ACCOUNT",
    "PAYMENT_BURST",
    "NIGHT_HIGH_VALUE",
    "DEVICE_CHANGE_HIGH_VALUE",
    "REPORTED_PAYEE",
    "JUST_UNDER_LIMIT",
    "MULE_PATTERN",
    "MODEL_TXN",
]

THRESHOLD_SUSPICIOUS = 35
THRESHOLD_HIGH_RISK = 70


def label_for(score: int) -> Label:
    """Map a 0..100 risk score to its contract label."""
    if score >= THRESHOLD_HIGH_RISK:
        return "HIGH_RISK"
    if score >= THRESHOLD_SUSPICIOUS:
        return "SUSPICIOUS"
    return "SAFE"


class Health(BaseModel):
    status: Literal["ok"] = "ok"
    models_loaded: bool


class SampleMessage(BaseModel):
    id: str
    title: str
    text: str
    channel: Channel
    sender: str | None = None


class QuizItem(BaseModel):
    id: str
    text: str
    channel: Channel
    sender: str | None = None
    is_scam: bool
    scam_type: str | None = None


class Evidence(BaseModel):
    start: int = Field(ge=0)
    end: int = Field(ge=0)
    text: str


class Signal(BaseModel):
    code: SignalCode
    title: str
    weight: float = Field(ge=0.0, le=1.0)
    description: str
    evidence: list[Evidence] = Field(default_factory=list)


class LinkFinding(BaseModel):
    raw: str
    domain: str
    verdict: LinkVerdict
    reasons: list[str]
    lookalike_of: str | None = None


class AnalyzeMessageRequest(BaseModel):
    text: str = Field(min_length=1, max_length=2000)
    channel: Channel = "sms"
    sender: str | None = Field(default=None, max_length=200)
    lang_out: Lang = "en"
    polish: bool = False

    @field_validator("text")
    @classmethod
    def not_blank(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Message text is empty. Paste the message you received.")
        return v


class MessageAnalysis(BaseModel):
    id: UUID
    risk_score: int = Field(ge=0, le=100)
    label: Label
    scam_type: str | None = None
    model_prob: float = Field(ge=0.0, le=1.0)
    rule_score: float = Field(ge=0.0, le=1.0)
    signals: list[Signal]
    links: list[LinkFinding]
    explanation: str
    next_steps: list[str]
    explanation_source: ExplanationSource = "template"


class DemoUser(BaseModel):
    user_id: str
    persona: str
    home_city: str


class Transaction(BaseModel):
    model_config = ConfigDict(extra="ignore")

    txn_id: str = Field(min_length=1, max_length=64)
    user_id: str = Field(min_length=1, max_length=64)
    timestamp: datetime
    type: TxnType
    amount_inr: float = Field(gt=0, le=10_000_000)
    payee_vpa: str = Field(min_length=3, max_length=120)
    payee_name: str = Field(min_length=1, max_length=120)
    channel: TxnChannel
    payee_is_new: bool
    payee_account_age_days: int = Field(ge=0, le=36_500)
    payee_report_count: int = Field(ge=0, le=10_000)
    device_changed: bool


class FeatureContribution(BaseModel):
    feature: str
    value: str
    contribution: float


class TxnAnalysis(BaseModel):
    txn_id: str
    risk_score: int = Field(ge=0, le=100)
    label: Label
    signals: list[Signal]
    feature_contributions: list[FeatureContribution]
    explanation: str
    next_steps: list[str]
    explanation_source: ExplanationSource = "template"


class FeedItem(BaseModel):
    transaction: Transaction
    analysis: TxnAnalysis


class AnalyzeTransactionRequest(BaseModel):
    transaction: Transaction
    lang_out: Lang = "en"


class FeedbackRequest(BaseModel):
    analysis_id: str = Field(min_length=1, max_length=64)
    kind: FeedbackKind
    correct_label: Label
    note: str | None = Field(default=None, max_length=500)


class FeedbackResponse(BaseModel):
    ok: Literal[True] = True
