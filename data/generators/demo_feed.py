"""Hand-crafted demo accounts. Each user's last ~20 transactions tell one story
with exactly 2-3 frauds. All names, VPAs and amounts are synthetic.

U001 student      : late-night 'game top-up', a task-scam fee to a reported payee,
                    then his account is used as a money mule.
U002 professional : fake electricity officer (just under 10k), fake Amazon care,
                    and a 48k transfer right after a SIM/device swap.
U003 elderly      : a fake 'Aadhaar KYC' payment, then the demo moment: a
                    collect request from a 3-day-old 'SBI Refund Desk'.
"""

from __future__ import annotations

from typing import Any

USERS = [
    {"user_id": "U001", "persona": "Student", "home_city": "Vellore", "median_amount": 120},
    {"user_id": "U002", "persona": "Young professional", "home_city": "Bengaluru", "median_amount": 650},
    {"user_id": "U003", "persona": "First-time elderly user", "home_city": "Chennai", "median_amount": 300},
]

# (timestamp IST, type, amount, payee_vpa, payee_name, channel, new, age_days, reports, device, fraud_pattern)
Row = tuple[str, str, float, str, str, str, bool, int, int, bool, str]

U001: list[Row] = [
    ("2026-10-22T08:42", "PAY", 45, "vitcanteen@okaxis", "VIT Canteen", "QR", False, 1400, 0, False, ""),
    ("2026-10-22T13:05", "PAY", 80, "foodcourt.vit@ybl", "VIT Food Court", "QR", False, 1100, 0, False, ""),
    ("2026-10-22T19:30", "PAY", 240, "rohan.iyer21@oksbi", "Rohan Iyer", "VPA", False, 900, 0, False, ""),
    ("2026-10-23T09:10", "RECEIVE", 3000, "gopal.sharma@okicici", "Gopal Sharma (Dad)", "VPA", False, 2400, 0, False, ""),
    ("2026-10-23T12:55", "PAY", 120, "xeroxcentre7@paytm", "Xerox Centre", "QR", False, 700, 0, False, ""),
    ("2026-10-23T18:20", "PAY", 349, "swiggy@ybl", "Swiggy", "VPA", False, 3000, 0, False, ""),
    ("2026-10-24T02:10", "PAY", 1150, "quickgame.topup@ybl", "QuickGame Topup", "VPA", True, 45, 0, False, "night_high"),
    ("2026-10-24T11:30", "PAY", 499, "task.payout77@ybl", "WorkFromHome Tasks", "VPA", True, 12, 6, False, "reported_payee"),
    ("2026-10-24T14:02", "RECEIVE", 1000, "neha.k1990@ybl", "Neha K", "VPA", True, 60, 0, False, ""),
    ("2026-10-24T14:31", "RECEIVE", 750, "amit.v.88@okaxis", "Amit V", "VPA", True, 33, 0, False, ""),
    ("2026-10-24T15:05", "RECEIVE", 1200, "pooja.r.12@paytm", "Pooja R", "VPA", True, 21, 0, False, ""),
    ("2026-10-24T15:40", "RECEIVE", 900, "sanju.pay@ibl", "Sanjay", "VPA", True, 14, 0, False, ""),
    ("2026-10-24T16:12", "RECEIVE", 1100, "kiran.m.4@ybl", "Kiran M", "VPA", True, 40, 0, False, ""),
    ("2026-10-24T16:45", "RECEIVE", 800, "meena.s.77@oksbi", "Meena S", "VPA", True, 9, 0, False, ""),
    ("2026-10-24T17:10", "RECEIVE", 1250, "farhan.k@okicici", "Farhan K", "VPA", True, 27, 0, False, ""),
    ("2026-10-24T17:30", "RECEIVE", 1200, "tara.d.21@ybl", "Tara D", "VPA", True, 18, 0, False, ""),
    ("2026-10-24T17:52", "PAY", 7850, "cryptodesk.in@ybl", "Crypto Desk", "VPA", True, 9, 0, False, "mule"),
    ("2026-10-25T08:40", "PAY", 45, "vitcanteen@okaxis", "VIT Canteen", "QR", False, 1400, 0, False, ""),
    ("2026-10-25T13:05", "PAY", 80, "foodcourt.vit@ybl", "VIT Food Court", "QR", False, 1100, 0, False, ""),
    ("2026-10-25T13:40", "PAY", 60, "juicecorner3@paytm", "Juice Corner", "QR", False, 650, 0, False, ""),
]

U002: list[Row] = [
    ("2026-10-21T08:30", "PAY", 40, "chaipoint12@ybl", "Chai Point", "QR", False, 1500, 0, False, ""),
    ("2026-10-21T10:00", "PAY", 18000, "prakash.rao@oksbi", "Prakash Rao (Landlord)", "VPA", False, 3100, 0, False, ""),
    ("2026-10-21T13:15", "PAY", 420, "zomato@hdfcbank", "Zomato", "VPA", False, 3200, 0, False, ""),
    ("2026-10-21T20:05", "PAY", 1280, "amazon@apl", "Amazon", "VPA", False, 3500, 0, False, ""),
    ("2026-10-22T09:00", "PAY", 2140, "bescom.bill@okaxis", "BESCOM", "VPA", False, 2900, 0, False, ""),
    ("2026-10-22T13:00", "PAY", 220, "meghana.foods@ybl", "Meghana Foods", "QR", False, 1300, 0, False, ""),
    ("2026-10-22T19:45", "PAY", 380, "uber.india@ybl", "Uber", "VPA", False, 3300, 0, False, ""),
    ("2026-10-23T08:30", "COLLECT_REQUEST", 1265, "irctc@ybl", "IRCTC", "VPA", False, 3600, 0, False, ""),
    ("2026-10-23T12:20", "PAY", 650, "cultfit@icici", "Cult Fit", "VPA", False, 1800, 0, False, ""),
    ("2026-10-23T18:00", "PAY", 1500, "kabir.menon@okaxis", "Kabir Menon", "VPA", False, 1600, 0, False, ""),
    ("2026-10-23T21:10", "PAY", 540, "swiggy@ybl", "Swiggy", "VPA", False, 3000, 0, False, ""),
    ("2026-10-24T08:15", "PAY", 120, "9876501234@ybl", "Auto (Manjunath)", "PHONE", False, 800, 0, False, ""),
    ("2026-10-24T10:05", "PAY", 9999, "eb.officer.ramesh@ybl", "EB Officer Ramesh", "PHONE", True, 5, 0, False, "just_under_limit"),
    ("2026-10-24T10:30", "PAY", 299, "jio@sbi", "Jio Recharge", "VPA", False, 3400, 0, False, ""),
    ("2026-10-24T15:00", "PAY", 4500, "amazon.refund.care@ybl", "Amazon Refund Care", "VPA", True, 30, 3, False, "reported_payee"),
    ("2026-10-24T19:40", "PAY", 710, "bigbasket@ybl", "BigBasket", "VPA", False, 2800, 0, False, ""),
    ("2026-10-24T22:10", "PAY", 260, "blinkit@ybl", "Blinkit", "VPA", False, 1200, 0, False, ""),
    ("2026-10-25T09:12", "PAY", 48000, "sunil.verma.77@okaxis", "Sunil Verma", "VPA", True, 18, 0, True, "device_change_high"),
    ("2026-10-25T09:40", "PAY", 180, "chaipoint12@ybl", "Chai Point", "QR", False, 1500, 0, False, ""),
    ("2026-10-25T12:30", "PAY", 350, "zomato@hdfcbank", "Zomato", "VPA", False, 3200, 0, False, ""),
]

U003: list[Row] = [
    ("2026-10-06T10:15", "PAY", 340, "apollopharmacy@okaxis", "Apollo Pharmacy", "QR", False, 2600, 0, False, ""),
    ("2026-10-07T07:30", "PAY", 60, "aavin.milk22@paytm", "Aavin Milk Booth", "QR", False, 1900, 0, False, ""),
    ("2026-10-08T11:00", "PAY", 520, "murugan.stores@ybl", "Murugan Stores", "QR", False, 2200, 0, False, ""),
    ("2026-10-09T07:30", "PAY", 60, "aavin.milk22@paytm", "Aavin Milk Booth", "QR", False, 1900, 0, False, ""),
    ("2026-10-10T18:00", "RECEIVE", 5000, "ravi.iyer@okicici", "Ravi Iyer (Son)", "VPA", False, 2700, 0, False, ""),
    ("2026-10-11T10:40", "PAY", 1120, "tangedco.bill@okaxis", "TANGEDCO", "VPA", False, 3000, 0, False, ""),
    ("2026-10-12T07:35", "PAY", 60, "aavin.milk22@paytm", "Aavin Milk Booth", "QR", False, 1900, 0, False, ""),
    ("2026-10-13T11:30", "PAY", 280, "apollopharmacy@okaxis", "Apollo Pharmacy", "QR", False, 2600, 0, False, ""),
    ("2026-10-14T16:00", "PAY", 450, "saravana.veg@ybl", "Saravana Vegetables", "QR", False, 1400, 0, False, ""),
    ("2026-10-15T07:30", "PAY", 60, "aavin.milk22@paytm", "Aavin Milk Booth", "QR", False, 1900, 0, False, ""),
    ("2026-10-16T12:10", "PAY", 200, "temple.trust@sbi", "Kapaleeshwarar Temple", "QR", False, 3400, 0, False, ""),
    ("2026-10-17T10:05", "PAY", 12000, "aadhaar.kyc.seva@ybl", "Aadhaar KYC Seva", "PHONE", True, 2, 0, False, "young_payee_large"),
    ("2026-10-18T07:30", "PAY", 60, "aavin.milk22@paytm", "Aavin Milk Booth", "QR", False, 1900, 0, False, ""),
    ("2026-10-19T11:15", "PAY", 610, "murugan.stores@ybl", "Murugan Stores", "QR", False, 2200, 0, False, ""),
    ("2026-10-20T10:20", "PAY", 390, "apollopharmacy@okaxis", "Apollo Pharmacy", "QR", False, 2600, 0, False, ""),
    ("2026-10-21T07:30", "PAY", 60, "aavin.milk22@paytm", "Aavin Milk Booth", "QR", False, 1900, 0, False, ""),
    ("2026-10-22T17:45", "PAY", 1500, "ravi.iyer@okicici", "Ravi Iyer (Son)", "VPA", False, 2700, 0, False, ""),
    ("2026-10-23T11:00", "PAY", 300, "saravana.veg@ybl", "Saravana Vegetables", "QR", False, 1400, 0, False, ""),
    ("2026-10-24T07:30", "PAY", 60, "aavin.milk22@paytm", "Aavin Milk Booth", "QR", False, 1900, 0, False, ""),
    ("2026-10-25T10:32", "COLLECT_REQUEST", 2499, "sbi.refund.desk@ybl", "SBI Refund Desk", "VPA", True, 3, 0, False, "collect_new_payee"),
]


def _expand(user_id: str, rows: list[Row]) -> list[dict[str, Any]]:
    out = []
    for i, (ts, kind, amount, vpa, name, channel, new, age, reports, device, fraud) in enumerate(rows):
        out.append({
            "txn_id": f"{user_id}-{i + 1:03d}", "user_id": user_id, "timestamp": f"{ts}:00+05:30",
            "type": kind, "amount_inr": float(amount), "payee_vpa": vpa, "payee_name": name, "channel": channel,
            "payee_is_new": new, "payee_account_age_days": age, "payee_report_count": reports,
            "device_changed": device, "is_fraud": int(bool(fraud)), "fraud_pattern": fraud,
        })
    return out


def build_demo_feed() -> dict[str, Any]:
    txns = _expand("U001", U001) + _expand("U002", U002) + _expand("U003", U003)
    return {"users": USERS, "transactions": txns}
