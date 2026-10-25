"""Generate the synthetic message dataset (data/processed/messages.csv).

- 12 scam types + 8 legit classes, 4 languages (60% en, 25% Hinglish, 10% hi, 5% ta)
- every value is synthetic: fake VPAs, phone numbers, look-alike links
- noise: random caps, typos, emoji, extra spaces
- split by template family (stratified per class+language) so test phrasings
  are never seen in training; asserted below
- also converts the UCI SMS Spam Collection into uci_external.csv

Run: python -m data.generators.gen_messages
"""

from __future__ import annotations

import csv
import hashlib
import random
import re
import string
import sys
from collections import Counter
from pathlib import Path
from typing import Callable

from data.generators.templates import (
    CLOSERS, LEGIT_CLASSES, OPENERS, SALUTATION_PREFIXES, SCAM_CLASSES, TEMPLATES,
)

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "data" / "processed"
UCI_PATH = ROOT / "data" / "seeds" / "uci" / "SMSSpamCollection"
SEED = 42
TARGET_ROWS = 6600
SCAM_SHARE = 0.43
LANG_MIX = {"en": 0.60, "hinglish": 0.25, "hi": 0.10, "ta": 0.05}
COLUMNS = ["id", "text", "channel", "sender", "label", "scam_type", "legit_class", "language", "template_id", "template_group", "split"]

BANKS = [("State Bank of India", "SBI"), ("HDFC Bank", "HDFC"), ("ICICI Bank", "ICICI"), ("Axis Bank", "AXIS"),
         ("Kotak Bank", "KOTAK"), ("Punjab National Bank", "PNB"), ("Canara Bank", "CANARA")]
BRANDS = [("Amazon", "amazon.in"), ("Flipkart", "flipkart.com"), ("Paytm", "paytm.com"), ("PhonePe", "phonepe.com"),
          ("Myntra", "myntra.com"), ("Swiggy", "swiggy.com"), ("Zomato", "zomato.com"), ("Meesho", "meesho.com")]
MERCHANTS = [("Swiggy", "swiggy.com"), ("Zomato", "zomato.com"), ("BigBasket", "bigbasket.com"), ("D-Mart", "dmart.in"),
             ("Reliance Digital", "reliancedigital.in"), ("Croma", "croma.com"), ("Domino's", "dominos.co.in")]
NAMES = ["Rahul", "Priya", "Arjun", "Sneha", "Karthik", "Ananya", "Vikram", "Divya", "Rohan", "Meera", "Aditya",
         "Lakshmi", "Suresh", "Pooja", "Harish", "Kavya", "Nikhil", "Fatima", "Imran", "Deepa", "Manoj", "Asha"]
LOOKALIKE_WORDS = ["kyc", "update", "verify", "secure", "login", "reward", "refund", "help", "support", "alert", "care"]
RISKY_TLDS = ["xyz", "top", "click", "icu", "buzz", "online", "link", "live", "site", "in", "com", "info"]
SPELLED = ["vit-ac.in", "hdfcbnk.com", "icic1bank.com", "sbi-co.in", "onlinesbi-sbi.com", "paytrn.com", "phonepe-help.com",
           "axisbamk.com", "amaz0n-offers.in", "flipkart-sale.top"]
VIT_BAD = ["vtop-vit-ac.in", "vit-ac.in", "vtop.vit-ac.co", "vitvtop-login.xyz", "vtop.vit.ac.in.verify-login.top",
           "vit-placements.online", "vtopvit.in", "vtop-login.vit-edu.in", "vit-scholarship.site", "vtop-helpdesk.click"]
SHORTENERS = ["bit.ly", "tinyurl.com", "cutt.ly", "rb.gy", "is.gd", "shorturl.at", "tiny.cc"]
UPI_APPS = ["GPay", "PhonePe", "Paytm", "BHIM", "your UPI app"]
VPA_SUFFIX = ["okaxis", "ybl", "paytm", "oksbi", "okicici", "ibl", "axl"]
EB = ["BESCOM", "TNEB", "TANGEDCO", "MSEDCL", "Electricity Board"]
ITEMS = ["sofa", "cycle", "laptop", "phone", "study table", "guitar", "fridge", "bike helmet", "textbooks"]
APPS = ["AnyDesk", "TeamViewer QuickSupport", "RustDesk", "AirDroid"]
COURIERS = ["BlueDart", "Delhivery", "Ekart", "India Post", "DTDC"]
CITIES = ["Vellore", "Chennai", "Bengaluru", "Hyderabad", "Pune", "Delhi", "Kochi", "Coimbatore"]
MOBILE_OPS = ["Airtel", "Jio", "Vi", "BSNL"]
SUBS = ["Netflix", "Spotify", "Amazon Prime", "JioCinema", "Hotstar", "YouTube Premium"]
FUNDS = ["Axis Bluechip Fund", "SBI Small Cap Fund", "HDFC Index Fund", "Parag Parikh Flexi Cap"]
RESTAURANTS = ["Hotel Saravana Bhavan", "Meghana Foods", "Paradise Biryani", "A2B", "Behrouz Biryani"]
EMOJI = ["🙏", "😊", "⚠️", "✅", "🎉", "💰", "🔴", "👍", "📢", "❗"]


def money(rng: random.Random, lo: int, hi: int) -> str:
    n = rng.randint(lo, hi)
    if rng.random() < 0.4:
        n = round(n, -2) - 1 if n > 1000 else n
    num = f"{n:,}" if rng.random() < 0.6 else str(n)
    style = rng.choice(["Rs {}", "Rs.{}", "₹{}", "INR {}", "Rs {}/-", "₹ {}"])
    return style.format(num)


def phone(rng: random.Random) -> str:
    digits = str(rng.choice([6, 7, 8, 9])) + "".join(rng.choice(string.digits) for _ in range(9))
    style = rng.random()
    if style < 0.35:
        return digits
    if style < 0.7:
        return f"+91 {digits[:5]} {digits[5:]}"
    return f"{digits[:5]}-{digits[5:]}"


def vpa(rng: random.Random, name: str | None = None) -> str:
    base = (name or rng.choice(NAMES)).lower()
    tail = rng.choice(["", str(rng.randint(1, 999)), ".refund", ".help", "pay", f".{rng.randint(10, 99)}"])
    return f"{base}{tail}@{rng.choice(VPA_SUFFIX)}"


def with_scheme(rng: random.Random, host: str, paths: list[str]) -> str:
    scheme = rng.choices(["", "http://", "https://", "hxxp://", "www."], weights=[3, 3, 3, 1, 1])[0]
    if rng.random() < 0.06 and "." in host:
        host = host.replace(".", "[.]", 1)
    return f"{scheme}{host}{rng.choice(paths)}"


class Slots(dict[str, str]):
    """Lazily generates a synthetic value the first time a slot is requested."""

    def __init__(self, rng: random.Random) -> None:
        super().__init__()
        self.rng = rng

    def __missing__(self, key: str) -> str:
        gen = SLOT_GENERATORS.get(key)
        if gen is None:
            raise KeyError(key)
        value = gen(self)
        self[key] = value
        return value

    def _pair(self, options: list[tuple[str, str]], first: str, second: str) -> tuple[str, str]:
        a, b = self.rng.choice(options)
        self[first], self[second] = a, b
        return a, b


def _bad_link(s: Slots) -> str:
    rng = s.rng
    if rng.random() < 0.25:
        host = rng.choice(SPELLED)
    else:
        brand = (dict.get(s, "bank_short") or dict.get(s, "brand") or rng.choice(["sbi", "hdfc", "upi", "paytm", "kyc"])).lower()
        words = rng.sample(LOOKALIKE_WORDS, k=rng.choice([1, 2]))
        host = f"{brand.split()[0]}-{'-'.join(words)}.{rng.choice(RISKY_TLDS)}"
    if rng.random() < 0.15:
        return f"{rng.choice(SHORTENERS)}/{''.join(rng.choices(string.ascii_letters + string.digits, k=6))}"
    return with_scheme(rng, host, ["", "", "/login", "/kyc", f"/verify?id={rng.randint(1000, 9999)}", "/update"])


SLOT_GENERATORS: dict[str, Callable[[Slots], str]] = {
    "amt": lambda s: money(s.rng, 499, 9999),
    "amt_small": lambda s: money(s.rng, 99, 1999),
    "amt_big": lambda s: money(s.rng, 25000, 2500000),
    "amt_day": lambda s: money(s.rng, 1500, 8000),
    "amt_n": lambda s: f"{s.rng.randint(20, 9999):,}.{s.rng.choice(['00', '50', '00'])}",
    "amt_small_n": lambda s: str(s.rng.choice([25, 50, 75, 100, 150])),
    "amt_big_n": lambda s: f"{s.rng.randint(15000, 120000):,}.00",
    "bal": lambda s: f"{s.rng.randint(500, 250000):,}.{s.rng.randint(10, 99)}",
    "bank": lambda s: s._pair(BANKS, "bank", "bank_short")[0],
    "bank_short": lambda s: s._pair(BANKS, "bank", "bank_short")[1],
    "brand": lambda s: s._pair(BRANDS, "brand", "brand_domain")[0],
    "brand_domain": lambda s: s._pair(BRANDS, "brand", "brand_domain")[1],
    "merchant": lambda s: s._pair(MERCHANTS, "merchant", "merchant_domain")[0],
    "merchant_domain": lambda s: s._pair(MERCHANTS, "merchant", "merchant_domain")[1],
    "bad_link": _bad_link,
    "bad_apk": lambda s: with_scheme(s.rng, f"{s.rng.choice(['refund', 'support', 'kyc', 'eb'])}-{s.rng.choice(LOOKALIKE_WORDS)}.{s.rng.choice(RISKY_TLDS)}", ["/app.apk", "/install.apk"]),
    "vit_bad": lambda s: with_scheme(s.rng, s.rng.choice(VIT_BAD), ["", "/login", "/verify", "/student/auth"]),
    "short": lambda s: f"{s.rng.choice(['', 'https://'])}{s.rng.choice(SHORTENERS)}/{''.join(s.rng.choices(string.ascii_letters + string.digits, k=s.rng.randint(5, 8)))}",
    "phone": lambda s: phone(s.rng),
    "tollfree": lambda s: s.rng.choice(["1800 1234", "1800-425-3800", "1800 266 0050", "1860 500 1111", "1800 103 4455"]),
    "vpa": lambda s: vpa(s.rng),
    "vpa_m": lambda s: f"{s.rng.choice(['canteen', 'swiggy', 'zomato', 'bigbasket', 'irctc', 'jio'])}@{s.rng.choice(VPA_SUFFIX)}",
    "name": lambda s: s.rng.choice(NAMES),
    "otp": lambda s: "".join(s.rng.choices(string.digits, k=s.rng.choice([4, 6, 6]))),
    "acct": lambda s: f"XX{s.rng.randint(1000, 9999)}",
    "card4": lambda s: str(s.rng.randint(1000, 9999)),
    "ref": lambda s: str(s.rng.randint(10**11, 10**12 - 1)),
    "order": lambda s: f"{s.rng.randint(100, 999)}-{s.rng.randint(1000000, 9999999)}",
    "awb": lambda s: f"{s.rng.choice(['BD', 'DL', 'EK'])}{s.rng.randint(10**8, 10**9 - 1)}",
    "pnr": lambda s: str(s.rng.randint(10**9, 10**10 - 1)),
    "date": lambda s: s.rng.choice([f"{s.rng.randint(1, 28)}-{s.rng.choice(['Oct', 'Nov', 'Dec'])}", f"{s.rng.randint(1, 28):02d}/{s.rng.randint(10, 12)}/2026"]),
    "time": lambda s: f"{s.rng.randint(1, 11)}:{s.rng.choice(['00', '15', '30', '45'])} {s.rng.choice(['AM', 'PM'])}",
    "hours": lambda s: str(s.rng.choice([2, 6, 12, 24, 48])),
    "item": lambda s: s.rng.choice(ITEMS),
    "app": lambda s: s.rng.choice(APPS),
    "course": lambda s: f"{s.rng.choice(['CSE', 'MAT', 'PHY', 'ECE', 'HUM'])}{s.rng.randint(1001, 4099)}",
    "room": lambda s: str(s.rng.randint(101, 820)),
    "block": lambda s: s.rng.choice(["A", "B", "C", "D", "J", "K", "Q"]),
    "courier": lambda s: s.rng.choice(COURIERS),
    "city": lambda s: s.rng.choice(CITIES),
    "eb": lambda s: s.rng.choice(EB),
    "upi_app": lambda s: s.rng.choice(UPI_APPS),
    "mobile_op": lambda s: s.rng.choice(MOBILE_OPS),
    "subscription": lambda s: s.rng.choice(SUBS),
    "fund": lambda s: s.rng.choice(FUNDS),
    "restaurant": lambda s: s.rng.choice(RESTAURANTS),
}


SMS_SPEAK = {"you": "u", "your": "ur", "please": "pls", "tomorrow": "tmrw", "okay": "ok", "are": "r",
             "message": "msg", "before": "b4", "today": "2day", "thanks": "thx", "what": "wat"}


def sms_speak(text: str) -> str:
    """Texting shorthand, applied equally to scam and legit messages."""
    return re.sub(r"\b(" + "|".join(SMS_SPEAK) + r")\b", lambda m: SMS_SPEAK[m.group(1).lower()] if m.group(1).islower() else m.group(1), text)


def add_noise(rng: random.Random, text: str, lang: str) -> str:
    latin = lang in ("en", "hinglish")
    if latin and rng.random() < 0.15:
        text = sms_speak(text)
    if latin and rng.random() < 0.07:
        text = text.upper()
    elif latin and rng.random() < 0.1:
        words = text.split(" ")
        i = rng.randrange(len(words))
        words[i] = words[i].upper()
        text = " ".join(words)
    if latin and rng.random() < 0.1:
        words = text.split(" ")
        i = rng.randrange(len(words))
        w = words[i]
        if len(w) > 3 and w.isalpha():
            j = rng.randrange(len(w) - 1)
            words[i] = w[:j] + w[j + 1] + w[j] + w[j + 2:]
        text = " ".join(words)
    if rng.random() < 0.15:
        e = rng.choice(EMOJI)
        text = f"{e} {text}" if rng.random() < 0.4 else f"{text} {e}"
    if rng.random() < 0.08:
        text = text.replace(" ", "  ", rng.randint(1, 3))
    return text


SCAM_CHANNELS = {"VIT_PHISH": ([0.2, 0.1, 0.7]), "FAMILY_IMPERSONATION": [0.25, 0.75, 0], "TASK_JOB": [0.3, 0.7, 0],
                 "QR_RECEIVE": [0.3, 0.7, 0], "WRONG_TRANSFER": [0.4, 0.6, 0], "REMOTE_ACCESS": [0.5, 0.5, 0],
                 "FAKE_CARE": [0.6, 0.4, 0], "PERSONAL_CHAT": [0.2, 0.8, 0], "CASUAL_CHAT": [0.3, 0.7, 0], "COLLEGE_NOTICE": [0.4, 0, 0.6]}


def pick_channel(rng: random.Random, cls: str) -> str:
    weights = SCAM_CHANNELS.get(cls, [0.8, 0.1, 0.1])
    return rng.choices(["sms", "whatsapp", "email"], weights=weights)[0]


def pick_sender(rng: random.Random, cls: str, channel: str, is_scam: bool) -> str:
    if channel == "whatsapp":
        return f"+91 {phone(rng)[-10:]}"
    if channel == "email":
        if cls == "COLLEGE_NOTICE":
            return rng.choice(["noreply@vit.ac.in", "exam.cell@vit.ac.in", "hostel.office@vit.ac.in", "library@vit.ac.in"])
        if cls == "VIT_PHISH":
            return rng.choice(["vtop.helpdesk.vit@gmail.com", "it-support@vit-ac.in", "admin@vtop-login.xyz", "vit.examcell2026@outlook.com"])
        if is_scam:
            return rng.choice(["support.kyc.desk@gmail.com", "noreply@sbi-alerts.top", "care@refund-help.online", "rewards.team@yahoo.com"])
        return rng.choice(["alerts@hdfcbank.com", "noreply@amazon.in", "orders@flipkart.com", "alerts@icicibank.com"])
    if is_scam and rng.random() < 0.55:
        return f"+91 {phone(rng)[-10:]}"
    prefix = rng.choice(["VM", "AX", "JD", "BZ", "AD", "VK", "TX"])
    code = rng.choice(["SBIINB", "HDFCBK", "ICICIT", "AXISBK", "KOTAKB", "VITUNI", "AMAZON", "SWIGGY", "PAYTMB"])
    if is_scam:
        code = rng.choice(["KYCUPD", "SBIUPD", "ALERTS", "REFUND", "BNKUPD", "EBBILL", "PRIZES"])
    return f"{prefix}-{code}"


def assign_splits(rng: random.Random) -> dict[str, str]:
    """Stratified group split: within each class+language, whole template families go to one split."""
    split_of: dict[str, str] = {}
    for cls, by_lang in TEMPLATES.items():
        for lang, bodies in by_lang.items():
            groups = [f"{cls}-{lang}-{i:02d}" for i in range(len(bodies))]
            rng.shuffle(groups)
            n = len(groups)
            n_test = max(1, round(0.15 * n))
            n_val = max(1, round(0.15 * n)) if n >= 4 else 0
            for i, g in enumerate(groups):
                split_of[g] = "test" if i < n_test else "val" if i < n_test + n_val else "train"
    return split_of


def render(rng: random.Random, cls: str, lang: str) -> tuple[str, str, str]:
    bodies = TEMPLATES[cls][lang]
    b = rng.randrange(len(bodies))
    body = bodies[b]
    openers = OPENERS[lang]
    if body.lower().startswith(SALUTATION_PREFIXES) or body.startswith(("{", "प्रिय", "அன்புள்ள")):
        openers = [""]
    o, c = rng.randrange(len(openers)), rng.randrange(len(CLOSERS[lang]))
    text = openers[o] + body.format_map(Slots(rng)) + CLOSERS[lang][c]
    group = f"{cls}-{lang}-{b:02d}"
    return add_noise(rng, text, lang), f"{group}-o{o}c{c}", group


def generate(rng: random.Random) -> list[dict[str, str]]:
    split_of = assign_splits(rng)
    rows: list[dict[str, str]] = []
    seen: set[str] = set()
    langs, weights = list(LANG_MIX), list(LANG_MIX.values())
    attempts = 0
    while len(rows) < TARGET_ROWS and attempts < TARGET_ROWS * 5:
        attempts += 1
        lang = rng.choices(langs, weights=weights)[0]
        is_scam = rng.random() < SCAM_SHARE
        cls = rng.choice(SCAM_CLASSES if is_scam else LEGIT_CLASSES)
        text, template_id, group = render(rng, cls, lang)
        if text in seen:
            continue
        seen.add(text)
        channel = pick_channel(rng, cls)
        rows.append({
            "id": f"m{len(rows):05d}", "text": text, "channel": channel,
            "sender": pick_sender(rng, cls, channel, is_scam), "label": str(int(is_scam)),
            "scam_type": cls if is_scam else "", "legit_class": "" if is_scam else cls,
            "language": lang, "template_id": template_id, "template_group": group, "split": split_of[group],
        })
    return rows


def convert_uci() -> list[dict[str, str]]:
    if not UCI_PATH.exists():
        print("UCI file missing; skipping external set", file=sys.stderr)
        return []
    rows = []
    for i, line in enumerate(UCI_PATH.read_text(encoding="utf-8", errors="replace").splitlines()):
        tag, _, text = line.partition("\t")
        if not text.strip():
            continue
        spam = tag.strip() == "spam"
        rows.append({
            "id": f"u{i:05d}", "text": text.strip()[:2000], "channel": "sms", "sender": "", "label": str(int(spam)),
            "scam_type": "GENERIC_SPAM" if spam else "", "legit_class": "" if spam else "UCI_HAM", "language": "en",
            "template_id": "uci", "template_group": "uci", "split": "external",
        })
    return rows


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=COLUMNS)
        w.writeheader()
        w.writerows(rows)


def check(rows: list[dict[str, str]]) -> None:
    groups_by_split: dict[str, set[str]] = {}
    for r in rows:
        groups_by_split.setdefault(r["split"], set()).add(r["template_group"])
    splits = list(groups_by_split)
    for i, a in enumerate(splits):
        for b in splits[i + 1:]:
            overlap = groups_by_split[a] & groups_by_split[b]
            assert not overlap, f"template families leak between {a} and {b}: {sorted(overlap)[:5]}"
    ids_by_split = {s: {r["template_id"] for r in rows if r["split"] == s} for s in splits}
    for i, a in enumerate(splits):
        for b in splits[i + 1:]:
            assert not ids_by_split[a] & ids_by_split[b], "template_id appears in two splits"


def summarise(rows: list[dict[str, str]], uci: list[dict[str, str]]) -> None:
    scam = sum(r["label"] == "1" for r in rows)
    print(f"messages.csv: {len(rows)} rows, scam share {scam / len(rows):.1%}")
    print("  splits:", dict(Counter(r["split"] for r in rows)))
    print("  languages:", dict(Counter(r["language"] for r in rows)))
    templates = Counter(r["scam_type"] or r["legit_class"] for r in {r["template_id"]: r for r in rows}.values())
    print(f"  classes: {len(templates)}; min distinct templates per class: {min(templates.values())}")
    print(f"uci_external.csv: {len(uci)} rows, spam share {sum(r['label'] == '1' for r in uci) / max(1, len(uci)):.1%}")


def data_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()[:12]


def main() -> None:
    rng = random.Random(SEED)
    rows = generate(rng)
    check(rows)
    write_csv(OUT / "messages.csv", rows)
    write_csv(OUT / "messages_sample.csv", rows[:200])
    uci = convert_uci()
    write_csv(OUT / "uci_external.csv", uci)
    summarise(rows, uci)
    print(f"  data hash {data_hash(OUT / 'messages.csv')}")


if __name__ == "__main__":
    main()
