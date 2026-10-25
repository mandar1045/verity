from __future__ import annotations

import pytest

from backend.app.services import i18n
from backend.app.services.explain import MAX_WORDS, explain_message, explain_transaction
from backend.app.services.polish import acceptable, polish
from backend.app.services.scoring import FusionConfig, calibrate, score_message
from backend.tests.conftest import signals_for
from contracts.schemas import LinkFinding, label_for


def test_calibration_maps_threshold_to_35() -> None:
    assert calibrate(0.6, 0.6) == 35
    assert calibrate(0.0, 0.6) == 0
    assert calibrate(1.0, 0.6) == 100


@pytest.mark.parametrize(("score", "label"), [(0, "SAFE"), (34, "SAFE"), (35, "SUSPICIOUS"), (69, "SUSPICIOUS"), (70, "HIGH_RISK"), (100, "HIGH_RISK")])
def test_contract_thresholds(score: int, label: str) -> None:
    assert label_for(score) == label


def test_dangerous_link_forces_floor() -> None:
    link = LinkFinding(raw="sbi-kyc.xyz", domain="sbi-kyc.xyz", verdict="DANGEROUS", reasons=["x"])
    assert score_message(0.0, 0.0, [], [link], FusionConfig()) >= 75


def test_pin_to_receive_forces_floor() -> None:
    sig = signals_for("Enter UPI PIN to receive Rs 5,000")
    assert score_message(0.0, 0.0, sig, [], FusionConfig()) >= 75


def test_strong_rules_floor() -> None:
    cfg = FusionConfig(weight=0.9, threshold=0.6, rule_floor_min=0.75)
    assert score_message(0.1, 0.8, [], [], cfg) == 80
    assert score_message(0.1, 0.5, [], [], cfg) < 35


def test_model_alone_cannot_reach_high_risk() -> None:
    cfg = FusionConfig(weight=0.9, threshold=0.6)
    assert score_message(0.99, 0.0, [], [], cfg) == 69
    assert score_message(0.99, 0.3, [], [], cfg) >= 70


def test_rules_only_when_model_missing() -> None:
    cfg = FusionConfig(rules_threshold=0.35)
    assert score_message(None, 0.35, [], [], cfg) == 35


def test_explanation_under_70_words_and_has_headline() -> None:
    sig = signals_for("Dear Customer, your account will be blocked today. Update KYC immediately at sbi-kyc-verify.xyz. Call 98765 43210")
    text, steps = explain_message("HIGH_RISK", sig, "FAKE_KYC", "en")
    assert text.startswith(i18n.t("headline.HIGH_RISK", "en"))
    assert len(text.split()) <= MAX_WORDS
    assert any("1930" in s for s in steps)
    assert len(steps) <= 5


def test_vit_phish_steps_include_helpdesk() -> None:
    _, steps = explain_message("HIGH_RISK", [], "VIT_PHISH", "en")
    assert any("VIT IT helpdesk" in s for s in steps)


def test_safe_explanation_is_headline_only() -> None:
    text, steps = explain_message("SAFE", [], None, "en")
    assert text == i18n.t("headline.SAFE", "en")
    assert steps


@pytest.mark.parametrize("lang", ["hi", "ta"])
def test_translations_exist_for_every_english_key(lang: str) -> None:
    en = i18n._load("en")
    for section in ("headline", "txn_headline", "step", "scam_type", "txnfeat", "label"):
        for key in en[section]:
            assert i18n.has(f"{section}.{key}", lang), f"{lang} missing {section}.{key}"
    for code in en["signal"]:
        assert i18n.has(f"signal.{code}.title", lang) and i18n.has(f"signal.{code}.sentence", lang)


def test_missing_key_falls_back_to_english() -> None:
    assert i18n.t("signal.NEW_PAYEE_COLLECT.description", "hi", evidence="x") == "x"
    assert i18n.t("no.such.key", "ta") == "no.such.key"


def test_hindi_explanation_is_hindi() -> None:
    text, _ = explain_message("HIGH_RISK", signals_for("Enter UPI PIN to receive Rs 5,000"), "QR_RECEIVE", "hi")
    assert any("ऀ" <= ch <= "ॿ" for ch in text)


def test_txn_steps_drop_collect_advice_for_pay() -> None:
    _, steps = explain_transaction("HIGH_RISK", [], "PAY", "en")
    assert i18n.t("step.decline_collect", "en") not in steps


def test_polish_without_key_returns_template(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    assert polish("Template text.", [], "en") == ("Template text.", "template")


def test_polish_guardrails() -> None:
    original = "It asks for your OTP. Call 1930 if you lost money."
    assert acceptable(original, "Please never share your OTP. Call 1930 if money was lost.", [])
    assert not acceptable(original, "Call 9876543210 now.", [])
    assert not acceptable(original, "Visit sbi-help.xyz for help.", [])
    assert not acceptable(original, "word " * 95, [])
