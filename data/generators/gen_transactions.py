"""Generate synthetic UPI transactions (data/processed/transactions.csv) and the
hand-crafted demo feed (data/processed/demo_feed.json).

- 200 users over 60 days, 3 personas (student, young professional, first-time elderly)
- 8 fraud patterns injected at ~3% of transactions, plus legit look-alikes
  (night snacks, rent, new-but-real payees, device changes) so the task is not trivial
- chronological split: days 1-45 train, 46-60 test
Run: python -m data.generators.gen_transactions
"""

from __future__ import annotations

import csv
import json
import random
from collections import Counter
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from contracts.schemas import Transaction
from data.generators.demo_feed import build_demo_feed
from ml.transaction.features import compute_context

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "data" / "processed"
SEED = 7
N_USERS = 200
DAYS = 60
TRAIN_DAYS = 45
TARGET_FRAUD_RATE = 0.03
IST = timezone(timedelta(hours=5, minutes=30))
START = datetime(2026, 8, 1, tzinfo=IST)

PERSONAS: dict[str, dict[str, Any]] = {
    "student": {"share": 0.45, "median": (60, 220), "rate": 3.5, "hours": (8, 23), "payees": 14},
    "professional": {"share": 0.35, "median": (350, 1200), "rate": 2.2, "hours": (7, 23), "payees": 18},
    "elderly": {"share": 0.20, "median": (150, 500), "rate": 0.4, "hours": (8, 19), "payees": 5},
}
CITIES = ["Vellore", "Chennai", "Bengaluru", "Hyderabad", "Pune", "Delhi", "Kochi", "Coimbatore", "Mumbai", "Jaipur"]
FIRST = ["Aarav", "Diya", "Kabir", "Isha", "Vivaan", "Anika", "Reyansh", "Myra", "Arjun", "Sara", "Ravi", "Lata",
         "Gopal", "Meena", "Sanjay", "Kiran", "Tara", "Farhan", "Zoya", "Mohan", "Selvi", "Murugan", "Bala", "Revathi"]
LAST = ["Sharma", "Iyer", "Reddy", "Nair", "Khan", "Patel", "Das", "Rao", "Menon", "Gupta", "Kumar", "Pillai"]
SHOPS = ["Canteen", "Tea Stall", "Medical Store", "Kirana Store", "Fruit Shop", "Stationery", "Bakery", "Pharmacy",
         "Milk Booth", "Auto Stand", "Xerox Centre", "Juice Corner"]
MERCHANTS = ["Swiggy", "Zomato", "Amazon", "Flipkart", "BigBasket", "Uber", "Ola", "Airtel", "Jio", "IRCTC", "BookMyShow"]
VPA_SUFFIX = ["okaxis", "ybl", "paytm", "oksbi", "okicici", "ibl"]
FRAUD_NAMES = ["Refund Desk", "Customer Support", "KYC Update Cell", "Prize Dept", "EB Officer", "Task Payout",
               "Ramesh Kumar", "Sunil Verma", "Online Job Desk", "Loan Approval", "Courier Help", "Bank Helpdesk"]
ROUND_LIMITS = (2000, 5000, 10000, 20000, 25000, 50000)


@dataclass
class Payee:
    vpa: str
    name: str
    age_days: int
    reports: int = 0
    typical: float = 1.0
    channel: str = "VPA"


@dataclass
class User:
    user_id: str
    persona: str
    city: str
    median: float
    hours: tuple[int, int]
    payees: list[Payee] = field(default_factory=list)
    known: set[str] = field(default_factory=set)


def make_payee(rng: random.Random, persona: str) -> Payee:
    if rng.random() < 0.5:
        shop = rng.choice(SHOPS + MERCHANTS)
        handle = shop.lower().replace(" ", "")
        return Payee(f"{handle}{rng.randint(1, 99)}@{rng.choice(VPA_SUFFIX)}", shop, rng.randint(200, 3000),
                     typical=rng.uniform(0.4, 2.0), channel=rng.choice(["QR", "QR", "VPA"]))
    first, last = rng.choice(FIRST), rng.choice(LAST)
    return Payee(f"{first.lower()}.{last.lower()}{rng.randint(1, 99)}@{rng.choice(VPA_SUFFIX)}", f"{first} {last}",
                 rng.randint(150, 3500), typical=rng.uniform(0.6, 3.0), channel=rng.choice(["VPA", "PHONE"]))


def make_users(rng: random.Random) -> list[User]:
    users = []
    names = list(PERSONAS)
    weights = [PERSONAS[p]["share"] for p in names]
    for i in range(N_USERS):
        persona = rng.choices(names, weights=weights)[0]
        cfg = PERSONAS[persona]
        u = User(f"S{i:03d}", persona, rng.choice(CITIES), rng.uniform(*cfg["median"]), cfg["hours"])
        u.payees = [make_payee(rng, persona) for _ in range(cfg["payees"])]
        users.append(u)
    return users


def txn(u: User, ts: datetime, kind: str, amount: float, payee: Payee, *, new: bool, device: bool = False,
        fraud: str = "") -> dict[str, Any]:
    return {
        "txn_id": "", "user_id": u.user_id, "timestamp": ts, "type": kind, "amount_inr": round(max(1.0, amount), 2),
        "payee_vpa": payee.vpa, "payee_name": payee.name, "channel": payee.channel, "payee_is_new": new,
        "payee_account_age_days": payee.age_days, "payee_report_count": payee.reports, "device_changed": device,
        "is_fraud": int(bool(fraud)), "fraud_pattern": fraud,
    }


def _legit_amount(rng: random.Random, u: User, payee: Payee) -> float:
    return rng.lognormvariate(0, 0.55) * u.median * payee.typical


def _legit_time(rng: random.Random, u: User, day: int) -> datetime:
    hour = rng.randint(*u.hours) if rng.random() > 0.03 else rng.randint(0, 4)  # rare legit night snack
    return START + timedelta(days=day, hours=hour, minutes=rng.randint(0, 59), seconds=rng.randint(0, 59))


def legit_day(rng: random.Random, u: User, day: int, device_day: int) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    n = sum(1 for _ in range(12) if rng.random() < PERSONAS[u.persona]["rate"] / 12)
    for k in range(n):
        ts = _legit_time(rng, u, day)
        if rng.random() < 0.1:  # a genuinely new payee
            payee = make_payee(rng, u.persona)
            if rng.random() < 0.06:
                payee.age_days = rng.randint(1, 6)
            if rng.random() < 0.02:
                payee.reports = 1
            u.payees.append(payee)
        else:
            payee = rng.choice(u.payees)
        new = payee.vpa not in u.known
        u.known.add(payee.vpa)
        kind = "COLLECT_REQUEST" if rng.random() < 0.03 and not new else "PAY"
        amount = _legit_amount(rng, u, payee)
        if rng.random() < 0.015:
            amount *= rng.uniform(5, 15)  # big legit purchase
        rows.append(txn(u, ts, kind, amount, payee, new=new, device=(day == device_day and k == 0)))
    if rng.random() < 0.06:
        sender = rng.choice(u.payees)
        rows.append(txn(u, _legit_time(rng, u, day), "RECEIVE", rng.uniform(200, 6000), sender, new=False))
    if u.persona == "professional" and day % 30 == 3:
        landlord = u.payees[0]
        rows.append(txn(u, START + timedelta(days=day, hours=10), "PAY", rng.uniform(12000, 30000), landlord, new=False))
    return rows


def fraud_payee(rng: random.Random, *, age: tuple[int, int] = (1, 40), reports: int = 0) -> Payee:
    name = rng.choice(FRAUD_NAMES)
    handle = name.lower().replace(" ", ".") + str(rng.randint(10, 9999))
    return Payee(f"{handle}@{rng.choice(VPA_SUFFIX)}", name, rng.randint(*age), reports=reports,
                 channel=rng.choice(["VPA", "VPA", "PHONE", "QR"]))


def fraud_event(rng: random.Random, u: User, day: int, pattern: str) -> list[dict[str, Any]]:
    base = START + timedelta(days=day, hours=rng.randint(9, 21), minutes=rng.randint(0, 59))
    m = u.median
    if pattern == "collect_new_payee":
        p = fraud_payee(rng, age=(1, 20))
        return [txn(u, base, "COLLECT_REQUEST", rng.uniform(999, 9999), p, new=True, fraud=pattern)]
    if pattern == "young_payee_large":
        p = fraud_payee(rng, age=(0, 6))
        return [txn(u, base, "PAY", max(3000, m * rng.uniform(5, 40)), p, new=True, fraud=pattern)]
    if pattern == "burst":
        p = fraud_payee(rng, age=(1, 200))
        n = rng.randint(5, 7)
        return [txn(u, base + timedelta(seconds=i * rng.randint(40, 110)), "PAY", rng.uniform(1000, 5000), p,
                    new=(i == 0), fraud=pattern if i >= 2 else "") for i in range(n)]
    if pattern == "night_high":
        p = fraud_payee(rng, age=(1, 400)) if rng.random() < 0.8 else rng.choice(u.payees)
        ts = START + timedelta(days=day, hours=rng.randint(0, 4), minutes=rng.randint(0, 59))
        return [txn(u, ts, "PAY", m * rng.uniform(6, 15), p, new=p.vpa not in u.known, fraud=pattern)]
    if pattern == "device_change_high":
        p = fraud_payee(rng, age=(1, 300)) if rng.random() < 0.7 else rng.choice(u.payees)
        return [txn(u, base, "PAY", max(2500, m * rng.uniform(8, 30)), p, new=p.vpa not in u.known, device=True, fraud=pattern)]
    if pattern == "reported_payee":
        p = fraud_payee(rng, age=(3, 500), reports=rng.randint(1, 8))
        return [txn(u, base, "PAY", m * rng.uniform(1, 5) + 199, p, new=True, fraud=pattern)]
    if pattern == "just_under_limit":
        limit = rng.choice(ROUND_LIMITS)
        p = fraud_payee(rng, age=(2, 600))
        return [txn(u, base, "PAY", limit - rng.choice([1, 1, 2, 10, 50]), p, new=True, fraud=pattern)]
    return mule_event(rng, u, base)


def mule_event(rng: random.Random, u: User, base: datetime) -> list[dict[str, Any]]:
    rows = []
    total = 0.0
    for i in range(rng.randint(6, 14)):
        amount = rng.uniform(300, 2000)
        total += amount
        rows.append(txn(u, base + timedelta(minutes=i * rng.randint(5, 25)), "RECEIVE", amount, fraud_payee(rng), new=True))
    out = fraud_payee(rng, age=(1, 120))
    last = rows[-1]["timestamp"] + timedelta(minutes=rng.randint(5, 60))
    rows.append(txn(u, last, "PAY", total * rng.uniform(0.85, 0.99), out, new=True, fraud="mule"))
    return rows


PATTERNS = ("collect_new_payee", "young_payee_large", "burst", "night_high", "device_change_high",
            "reported_payee", "just_under_limit", "mule")
# A burst event yields 3-5 labelled frauds, the others one each; weight so patterns are balanced.
PATTERN_WEIGHTS = (1, 1, 0.27, 1, 1, 1, 1, 1)


def simulate(rng: random.Random) -> tuple[list[User], list[dict[str, Any]]]:
    users = make_users(rng)
    rows: list[dict[str, Any]] = []
    for u in users:
        device_day = rng.randint(5, DAYS - 1) if rng.random() < 0.5 else -1
        for day in range(DAYS):
            rows += legit_day(rng, u, day, device_day)
    per_user = Counter(r["user_id"] for r in rows)
    weights = [per_user[u.user_id] + 15 for u in users]
    frauds = 0
    while frauds < TARGET_FRAUD_RATE * len(rows):
        u = rng.choices(users, weights=weights)[0]
        event = fraud_event(rng, u, rng.randrange(DAYS), rng.choices(PATTERNS, weights=PATTERN_WEIGHTS)[0])
        frauds += sum(r["is_fraud"] for r in event)
        rows += event
    return users, rows


def engineer(users: list[User], rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    medians = {u.user_id: u.median for u in users}
    rows.sort(key=lambda r: (r["user_id"], r["timestamp"]))
    out: list[dict[str, Any]] = []
    window: list[dict[str, Any]] = []
    for i, r in enumerate(rows):
        if i == 0 or rows[i - 1]["user_id"] != r["user_id"]:
            window = []
        window = [h for h in window if (r["timestamp"] - h["timestamp"]).total_seconds() <= 86_400]
        ctx = compute_context(r, window, medians[r["user_id"]])
        day = (r["timestamp"] - START).days + 1
        out.append({**r, **ctx.as_dict(), "txn_id": f"T{len(out):06d}", "day": day,
                    "split": "train" if day <= TRAIN_DAYS else "test"})
        window.append(r)
    return out


def write(rows: list[dict[str, Any]], path: Path) -> None:
    cols = list(rows[0].keys())
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        for r in rows:
            w.writerow({**r, "timestamp": r["timestamp"].isoformat()})


def main() -> None:
    rng = random.Random(SEED)
    users, raw = simulate(rng)
    rows = engineer(users, raw)
    OUT.mkdir(parents=True, exist_ok=True)
    write(rows, OUT / "transactions.csv")
    write(rows[:200], OUT / "transactions_sample.csv")
    fraud_rate = sum(r["is_fraud"] for r in rows) / len(rows)
    assert 0.025 <= fraud_rate <= 0.035, f"fraud rate {fraud_rate:.3%} outside 2.5-3.5%"
    print(f"transactions.csv: {len(rows)} rows, {len(users)} users, fraud rate {fraud_rate:.2%}")
    print("  splits:", dict(Counter(r["split"] for r in rows)))
    print("  personas:", dict(Counter(u.persona for u in users)))
    print("  patterns:", dict(Counter(r["fraud_pattern"] for r in rows if r["is_fraud"])))
    feed = build_demo_feed()
    for t in feed["transactions"]:
        Transaction.model_validate(t)
    (OUT / "demo_feed.json").write_text(json.dumps(feed, indent=2, ensure_ascii=False))
    per_user = Counter(t["user_id"] for t in feed["transactions"] if t["is_fraud"])
    assert all(2 <= per_user[u["user_id"]] <= 3 for u in feed["users"]), per_user
    print(f"demo_feed.json: {len(feed['transactions'])} txns, frauds per user {dict(per_user)} (validated)")


if __name__ == "__main__":
    main()
