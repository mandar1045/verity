from __future__ import annotations

import pytest

from backend.app.services.rules import infer_scam_type, rule_score
from backend.tests.conftest import codes_for, signals_for


@pytest.mark.parametrize(
    ("text", "code"),
    [
        ("Update your details immediately or lose access", "URGENCY"),
        ("Your account will be blocked today", "ACCOUNT_THREAT"),
        ("Share the OTP sent to your number to confirm cashback", "CREDENTIAL_REQUEST"),
        ("Enter your UPI PIN to receive Rs 2,499 refund", "PIN_TO_RECEIVE"),
        ("Pay the bill at http://192.168.4.20/pay", "SUSPICIOUS_LINK"),
        ("Login at https://hdfcbnk.com/secure", "LOOKALIKE_DOMAIN"),
        ("Track your parcel at bit.ly/3xYz9Q", "URL_SHORTENER"),
        ("Install AnyDesk so our executive can fix your refund", "REMOTE_ACCESS_APP"),
        ("Congratulations! You have won a lucky draw prize", "PRIZE_LURE"),
        ("Pay Rs 499 registration fee to start earning", "PAY_TO_EARN"),
        ("Hi Mom, this is my new number, phone fell in water", "IMPERSONATION"),
        ("Complete your KYC to continue using UPI", "KYC_UPDATE"),
        ("Call customer care at 98765 43210 for a refund", "CALLBACK_NUMBER"),
    ],
)
def test_each_signal_fires(text: str, code: str) -> None:
    assert code in codes_for(text)


def test_sender_mismatch_for_gmail_claiming_vit() -> None:
    text = "Dear Student, your VTOP account is suspended. Verify now."
    assert "SENDER_MISMATCH" in codes_for(text, "email", "vtop.helpdesk@gmail.com")
    assert "SENDER_MISMATCH" not in codes_for(text, "email", "exam.cell@vit.ac.in")


def test_sender_mismatch_for_phone_number_claiming_bank() -> None:
    assert "SENDER_MISMATCH" in codes_for("Dear customer, your SBI account is blocked", "sms", "+91 98765 43210")
    assert "SENDER_MISMATCH" not in codes_for("Dear customer, your SBI account is blocked", "sms", "VM-SBIINB")


def test_genuine_otp_is_suppressed() -> None:
    text = "482910 is your OTP for txn of Rs 1,250.00. Do not share this OTP with anyone. -SBI"
    assert "CREDENTIAL_REQUEST" not in codes_for(text)
    assert rule_score(signals_for(text)) == 0


def test_otp_warning_does_not_hide_phishing_link() -> None:
    text = "Verify your password at https://vtop-vit-ac.in/login. Do not share your password with anyone."
    assert "CREDENTIAL_REQUEST" in codes_for(text)


def test_legit_otp_send_phrasing_not_flagged() -> None:
    assert "CREDENTIAL_REQUEST" not in codes_for("We will send you an OTP to verify your Swiggy login.")


def test_pin_awareness_message_is_negated() -> None:
    assert "PIN_TO_RECEIVE" not in codes_for("Your bank never asks for your PIN to receive money. Stay safe!")


def test_pin_to_receive_weight_is_strongest() -> None:
    sig = {s.code: s for s in signals_for("Scan this QR to receive payment for your OLX sofa")}
    assert sig["PIN_TO_RECEIVE"].weight == 0.9


def test_hinglish_collect_refund() -> None:
    codes = codes_for("Aapka refund Rs 2499 approve ho gaya hai. Collect request accept karke PIN daalo, paise turant milenge.")
    assert {"PIN_TO_RECEIVE", "URGENCY"} <= codes


def test_hindi_task_job() -> None:
    assert "PAY_TO_EARN" in codes_for("घर बैठे रोज़ ₹3000 कमाएं, बस वीडियो लाइक करें। पहले ₹500 रजिस्ट्रेशन फीस भेजें।")


def test_tamil_bill_disconnect() -> None:
    text = "உங்கள் மின் இணைப்பு இன்றிரவு 9:30க்கு துண்டிக்கப்படும். உடனே மின் வாரிய அதிகாரியை 9876543210 அழைக்கவும்."
    assert {"URGENCY", "CALLBACK_NUMBER", "ACCOUNT_THREAT"} <= codes_for(text)


def test_tamil_after_is_not_a_pin() -> None:
    assert "PIN_TO_RECEIVE" not in codes_for("பின்னர் பணம் பெற வங்கிக்கு செல்லவும்.")


def test_evidence_offsets_are_exact() -> None:
    text = "🔴 Dear Customer, your account will be blocked today. Update KYC immediately at sbi-kyc-verify.xyz"
    for s in signals_for(text):
        for e in s.evidence:
            assert text[e.start:e.end] == e.text


def test_devanagari_offsets_are_exact() -> None:
    text = "प्रिय ग्राहक, आपका खाता आज बंद हो जाएगा। तुरंत केवाईसी अपडेट करें"
    sig = signals_for(text)
    assert sig
    for s in sig:
        for e in s.evidence:
            assert text[e.start:e.end] == e.text


def test_toll_free_number_is_not_a_callback() -> None:
    assert "CALLBACK_NUMBER" not in codes_for("Not you? Call 1800 1234 -SBI")


def test_rule_score_combines_weights() -> None:
    sig = signals_for("Your account will be blocked today. Update KYC immediately")
    expected = 1.0
    for s in sig:
        expected *= 1 - s.weight
    assert rule_score(sig) == pytest.approx(1 - expected, abs=1e-4)


def test_infer_scam_type_fallback() -> None:
    text = "Install AnyDesk so our executive can fix your refund"
    assert infer_scam_type(text, signals_for(text)) == "REMOTE_ACCESS"
    assert infer_scam_type("See you at lunch", []) is None
