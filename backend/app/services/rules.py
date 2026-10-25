"""Deterministic rule engine: one detector per message SignalCode (all but MODEL_TEXT).

Every signal carries evidence as exact character offsets into the original text,
so the UI can highlight precisely what fired. Lexicons live in lexicons/*.yaml
(English, Hinglish, Hindi, Tamil).
"""

from __future__ import annotations

import re
from collections.abc import Callable, Iterable
from dataclasses import dataclass, field
from pathlib import Path

import yaml

from backend.app.services import i18n
from backend.app.services.links import LinkResult, brand_misuse, lookalike_target, official_domain
from contracts.schemas import Evidence, Signal

LEX_DIR = Path(__file__).parent / "lexicons"

DEFAULT_WEIGHTS: dict[str, float] = {
    "URGENCY": 0.3, "ACCOUNT_THREAT": 0.5, "CREDENTIAL_REQUEST": 0.75,
    "PIN_TO_RECEIVE": 0.9, "SUSPICIOUS_LINK": 0.45, "LOOKALIKE_DOMAIN": 0.8,
    "URL_SHORTENER": 0.35, "REMOTE_ACCESS_APP": 0.8, "PRIZE_LURE": 0.45,
    "PAY_TO_EARN": 0.6, "IMPERSONATION": 0.45, "KYC_UPDATE": 0.45,
    "SENDER_MISMATCH": 0.55, "CALLBACK_NUMBER": 0.4,
}
RULE_CODES = frozenset(DEFAULT_WEIGHTS)
CRED_SHARE_WEIGHT = 0.75
CRED_ENTRY_WEIGHT = 0.6
DANGER_LINK_WEIGHT = 0.7

_SENTENCE_BREAK = re.compile(r"[!?।\n]|\.(?=\s+[A-Z])")
_PHONE = re.compile(r"(?<![\d+])(?:\+91[\s-]?|0)?[6-9]\d{4}[\s-]?\d{5}(?!\d)")
_CRED_FILLER = re.compile(
    r"^\s*(?:(?:the|your|ur|that|this|us|me|it|back|with|received|code|number|digits?|"
    r"\d-digit|of|to|our|here|now|immediately|login|bank|upi|card|atm)\s*[,:]?\s+)*$",
    re.I,
)
_CLAIM = re.compile(
    r"(?<!\w)(?:dear\s+(?:valued\s+)?(?:customer|user|student|member|account holder|sir|madam)"
    r"|valued customer|your\s+(?:\w+\s+){0,2}(?:account|a/c|card|kyc|wallet|vtop|connection|sim)"
    r"|(?:team|from)\s+(?:sbi|hdfc|icici|axis|kotak|paytm|phonepe|vit|vtop|npci|rbi|bank|amazon|flipkart|irctc)"
    r"|vtop|customer care|help\s?desk|support team)(?!\w)|बैंक|வங்கி",
    re.I,
)
FREE_MAIL = frozenset({
    "gmail.com", "googlemail.com", "yahoo.com", "yahoo.in", "outlook.com", "hotmail.com",
    "rediffmail.com", "proton.me", "protonmail.com", "aol.com", "ymail.com", "gmx.com",
    "mail.com", "icloud.com", "zoho.com",
})


@dataclass(frozen=True)
class Hit:
    start: int
    end: int
    text: str
    weight: float


@dataclass
class RuleContext:
    text: str
    channel: str = "sms"
    sender: str | None = None
    links: list[LinkResult] = field(default_factory=list)
    lang: str = "en"


Detector = Callable[[RuleContext], Signal | None]


def _dedupe(hits: Iterable[Hit]) -> list[Hit]:
    """Drop hits contained in a longer hit; keep the order of appearance."""
    ordered = sorted(hits, key=lambda h: (h.start, -(h.end - h.start)))
    kept: list[Hit] = []
    for h in ordered:
        if any(k.start <= h.start and h.end <= k.end for k in kept):
            continue
        kept.append(h)
    return kept


class Lexicon:
    """All lexicon files merged: key -> [(compiled regex, weight or None)]."""

    def __init__(self, directory: Path) -> None:
        self._patterns: dict[str, list[tuple[re.Pattern[str], float | None]]] = {}
        for path in sorted(directory.glob("*.yaml")):
            self._load_file(path)

    def _load_file(self, path: Path) -> None:
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        boundary = bool(data.get("boundary", False))
        for section in ("signals", "signals_extra"):
            for key, entries in (data.get(section) or {}).items():
                for entry in entries or []:
                    pat, weight = (entry[0], float(entry[1])) if isinstance(entry, list) else (entry, None)
                    if boundary:
                        pat = rf"(?<!\w)(?:{pat})(?!\w)"
                    self._patterns.setdefault(key, []).append((re.compile(pat, re.I), weight))

    def keys(self) -> list[str]:
        return list(self._patterns)

    def hits(self, key: str, text: str) -> list[Hit]:
        default = DEFAULT_WEIGHTS.get(key, 0.3)
        found = [
            Hit(m.start(), m.end(), m.group(0), default if w is None else w)
            for rx, w in self._patterns.get(key, [])
            for m in rx.finditer(text)
            if m.end() > m.start()
        ]
        return _dedupe(found)


LEX = Lexicon(LEX_DIR)


def _crosses_sentence(text: str, start: int, end: int) -> bool:
    return bool(_SENTENCE_BREAK.search(text, start, end))


def build_signal(code: str, weight: float, hits: Iterable[Hit], ctx: RuleContext, **params: str) -> Signal:
    evidence = [Evidence(start=h.start, end=h.end, text=h.text) for h in _dedupe(hits)]
    quoted = ", ".join(f"'{e.text.strip()}'" for e in evidence[:3])
    return Signal(
        code=code,  # type: ignore[arg-type]
        title=i18n.t(f"signal.{code}.title", ctx.lang),
        weight=round(min(0.95, max(0.0, weight)), 2),
        description=i18n.t(f"signal.{code}.description", ctx.lang, evidence=quoted, **params),
        evidence=evidence,
    )


def _combined_weight(hits: list[Hit]) -> float:
    distinct = {h.text.lower().strip() for h in hits}
    return max(h.weight for h in hits) + min(0.15, 0.05 * (len(distinct) - 1))


def _lexicon_detector(code: str) -> Detector:
    def detect(ctx: RuleContext) -> Signal | None:
        hits = LEX.hits(code, ctx.text)
        return build_signal(code, _combined_weight(hits), hits, ctx) if hits else None

    detect.__name__ = f"detect_{code.lower()}"
    return detect


detect_urgency = _lexicon_detector("URGENCY")
detect_account_threat = _lexicon_detector("ACCOUNT_THREAT")
detect_kyc_update = _lexicon_detector("KYC_UPDATE")
detect_remote_access_app = _lexicon_detector("REMOTE_ACCESS_APP")
detect_prize_lure = _lexicon_detector("PRIZE_LURE")
detect_pay_to_earn = _lexicon_detector("PAY_TO_EARN")
detect_impersonation = _lexicon_detector("IMPERSONATION")


def _pairs(a_hits: list[Hit], b_hits: list[Hit], text: str, max_len: int) -> list[tuple[int, int]]:
    spans: list[tuple[int, int]] = []
    for a in a_hits:
        for b in b_hits:
            start, end = min(a.start, b.start), max(a.end, b.end)
            if end - start <= max_len and not _crosses_sentence(text, start, end):
                spans.append((start, end))
    return spans


def detect_pin_to_receive(ctx: RuleContext) -> Signal | None:
    """'Enter PIN / scan QR to receive money': you never need a PIN to receive."""
    text = ctx.text
    negations = LEX.hits("NEGATION_TERMS", text)
    hits = []
    for start, end in _pairs(LEX.hits("PIN_TERMS", text), LEX.hits("RECEIVE_TERMS", text), text, 90):
        negated = any(start - 40 <= n.start <= end and not _crosses_sentence(text, n.start, end) for n in negations)
        if not negated:
            hits.append(Hit(start, end, text[start:end], DEFAULT_WEIGHTS["PIN_TO_RECEIVE"]))
    return build_signal("PIN_TO_RECEIVE", DEFAULT_WEIGHTS["PIN_TO_RECEIVE"], hits, ctx) if hits else None


def _cred_spans(actions: list[Hit], objects: list[Hit], text: str, weight: float) -> list[Hit]:
    out: list[Hit] = []
    for a in actions:
        for o in objects:
            if o.start >= a.end:  # "share your OTP"
                ok = bool(_CRED_FILLER.match(text[a.end:o.start]))
            elif a.start >= o.end:  # SOV order: "OTP batao", "OTP-ஐ பகிர"
                ok = a.start - o.end <= 25 and not _crosses_sentence(text, o.start, a.end)
            else:
                ok = False
            if ok:
                start, end = min(a.start, o.start), max(a.end, o.end)
                out.append(Hit(start, end, text[start:end], weight))
    return out


def detect_credential_request(ctx: RuleContext) -> Signal | None:
    """Asks you to share an OTP/PIN/password. Suppressed for genuine OTP warnings."""
    text = ctx.text
    objects = LEX.hits("CRED_OBJECT", text)
    if not objects:
        return None
    risky_link = any(link.finding.verdict != "OK" for link in ctx.links)
    if LEX.hits("OTP_WARNING", text) and not risky_link:
        return None  # "Do not share this OTP with anyone": a real bank OTP
    hits = _cred_spans(LEX.hits("CRED_ACTION", text), objects, text, CRED_SHARE_WEIGHT)
    if risky_link:
        hits += _cred_spans(LEX.hits("CRED_ENTRY", text), objects, text, CRED_ENTRY_WEIGHT)
    if not hits:
        return None
    return build_signal("CREDENTIAL_REQUEST", max(h.weight for h in hits), hits, ctx)


def detect_callback_number(ctx: RuleContext) -> Signal | None:
    """A personal mobile number to call back. Toll-free numbers never match."""
    text = ctx.text
    calls = LEX.hits("CALL_WORDS", text)
    hits = []
    for m in _PHONE.finditer(text):
        near = any(m.start() - 60 <= c.end <= m.start() + 5 or m.end() <= c.start <= m.end() + 30 for c in calls)
        if near:
            hits.append(Hit(m.start(), m.end(), m.group(0), DEFAULT_WEIGHTS["CALLBACK_NUMBER"]))
    return build_signal("CALLBACK_NUMBER", DEFAULT_WEIGHTS["CALLBACK_NUMBER"], hits, ctx) if hits else None


def sender_problem(sender: str) -> bool:
    """True if the sender cannot be an official institution sender."""
    s = sender.strip().strip("<>").lower()
    if "@" in s:
        domain = s.rsplit("@", 1)[1]
        if official_domain(domain):
            return False
        return domain in FREE_MAIL or bool(lookalike_target(domain) or brand_misuse(domain))
    digits = re.sub(r"[\s+\-()]", "", s)
    return digits.isdigit() and len(digits) >= 10


def detect_sender_mismatch(ctx: RuleContext) -> Signal | None:
    if not ctx.sender or not sender_problem(ctx.sender):
        return None
    claims = [
        Hit(m.start(), m.end(), m.group(0), DEFAULT_WEIGHTS["SENDER_MISMATCH"])
        for m in _CLAIM.finditer(ctx.text)
        if not any(lk.start <= m.start() < lk.end for lk in ctx.links)
    ]
    if not claims:
        return None
    return build_signal("SENDER_MISMATCH", DEFAULT_WEIGHTS["SENDER_MISMATCH"], claims, ctx, sender=ctx.sender.strip())


def _link_hits(links: list[LinkResult], weight: float) -> list[Hit]:
    return [Hit(lk.start, lk.end, lk.finding.raw, weight) for lk in links]


def detect_lookalike_domain(ctx: RuleContext) -> Signal | None:
    found = [lk for lk in ctx.links if "lookalike" in lk.kinds]
    weight = DEFAULT_WEIGHTS["LOOKALIKE_DOMAIN"]
    return build_signal("LOOKALIKE_DOMAIN", weight, _link_hits(found, weight), ctx) if found else None


def detect_suspicious_link(ctx: RuleContext) -> Signal | None:
    found = [lk for lk in ctx.links if lk.kinds & {"danger", "suspicious"} and "lookalike" not in lk.kinds]
    if not found:
        return None
    weight = DANGER_LINK_WEIGHT if any("danger" in lk.kinds for lk in found) else DEFAULT_WEIGHTS["SUSPICIOUS_LINK"]
    return build_signal("SUSPICIOUS_LINK", weight, _link_hits(found, weight), ctx)


def detect_url_shortener(ctx: RuleContext) -> Signal | None:
    found = [lk for lk in ctx.links if "shortener" in lk.kinds]
    weight = DEFAULT_WEIGHTS["URL_SHORTENER"]
    return build_signal("URL_SHORTENER", weight, _link_hits(found, weight), ctx) if found else None


DETECTORS: tuple[Detector, ...] = (
    detect_pin_to_receive, detect_credential_request, detect_remote_access_app,
    detect_lookalike_domain, detect_suspicious_link, detect_url_shortener,
    detect_account_threat, detect_kyc_update, detect_pay_to_earn, detect_prize_lure,
    detect_impersonation, detect_sender_mismatch, detect_callback_number, detect_urgency,
)


def run_rules(ctx: RuleContext) -> list[Signal]:
    """Run every detector; return fired signals, strongest first."""
    signals = [s for s in (d(ctx) for d in DETECTORS) if s is not None]
    return sorted(signals, key=lambda s: s.weight, reverse=True)


def rule_score(signals: Iterable[Signal]) -> float:
    """1 - prod(1 - w_i) over fired rule signals (MODEL_TEXT excluded)."""
    remaining = 1.0
    for s in signals:
        if s.code in RULE_CODES:
            remaining *= 1.0 - s.weight
    return round(1.0 - remaining, 4)


_TYPE_HINTS: tuple[tuple[str, str | None, frozenset[str]], ...] = (
    ("VIT_PHISH", r"vtop|(?<!\w)vit(?!\w)|vellore institute", frozenset()),
    ("REMOTE_ACCESS", None, frozenset({"REMOTE_ACCESS_APP"})),
    ("QR_RECEIVE", r"(?<!\w)qr(?!\w)|scan|स्कैन|ஸ்கேன்", frozenset({"PIN_TO_RECEIVE"})),
    ("COLLECT_REFUND", None, frozenset({"PIN_TO_RECEIVE"})),
    ("BILL_DISCONNECT", r"electricity|power|bijli|बिजली|மின்", frozenset()),
    ("FAKE_KYC", None, frozenset({"KYC_UPDATE"})),
    ("OTP_THEFT", None, frozenset({"CREDENTIAL_REQUEST"})),
    ("TASK_JOB", r"task|job|part[- ]time|like|naukri|नौकरी|लाइक|टास्क|வேலை|லைக்", frozenset({"PAY_TO_EARN"})),
    ("PRIZE", None, frozenset({"PRIZE_LURE", "PAY_TO_EARN"})),
    ("FAMILY_IMPERSONATION", r"new number|naya number|नया नंबर|புதிய எண்", frozenset()),
    ("FAKE_CARE", None, frozenset({"CALLBACK_NUMBER", "IMPERSONATION"})),
)


def infer_scam_type(text: str, signals: list[Signal]) -> str | None:
    """Rule fallback for scam_type when the type classifier is unavailable."""
    codes = {s.code for s in signals if s.code in RULE_CODES}
    if not codes:
        return None
    if LEX.hits("WRONG_TRANSFER", text):
        return "WRONG_TRANSFER"
    for scam_type, pattern, needs in _TYPE_HINTS:
        if pattern and not re.search(pattern, text, re.I):
            continue
        if needs and not needs & codes:
            continue
        return scam_type
    return None
