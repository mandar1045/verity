"""Smoke test: start the API if needed, hit every endpoint, validate every
response against contracts/schemas.py, and fetch the frontend index.
Run: python scripts/smoke.py [--base http://localhost:8000] [--frontend URL]
"""

from __future__ import annotations

import argparse
import subprocess
import sys
import time
from collections.abc import Callable
from typing import Any

import httpx
from pydantic import TypeAdapter

from contracts.schemas import DemoUser, FeedbackResponse, FeedItem, Health, MessageAnalysis, QuizItem, SampleMessage, TxnAnalysis

TXN = {"txn_id": "SMOKE-1", "user_id": "U003", "timestamp": "2026-10-25T10:40:00+05:30", "type": "COLLECT_REQUEST",
       "amount_inr": 2499, "payee_vpa": "sbi.refund.desk@ybl", "payee_name": "SBI Refund Desk", "channel": "VPA",
       "payee_is_new": True, "payee_account_age_days": 3, "payee_report_count": 0, "device_changed": False}


def wait_for(base: str, seconds: float = 40) -> bool:
    deadline = time.time() + seconds
    while time.time() < deadline:
        try:
            if httpx.get(f"{base}/api/v1/health", timeout=2).status_code == 200:
                return True
        except httpx.HTTPError:
            time.sleep(0.5)
    return False


def checks(c: httpx.Client) -> list[tuple[str, Callable[[], Any]]]:
    msg = {"text": "Enter your UPI PIN to receive Rs 2,499 refund now", "channel": "sms", "sender": None, "lang_out": "hi"}
    fb = {"analysis_id": "smoke", "kind": "message", "correct_label": "SAFE", "note": None}
    return [
        ("GET  /health", lambda: Health.model_validate(c.get("/api/v1/health").raise_for_status().json())),
        ("GET  /samples/messages", lambda: TypeAdapter(list[SampleMessage]).validate_python(c.get("/api/v1/samples/messages").raise_for_status().json())),
        ("GET  /samples/quiz", lambda: TypeAdapter(list[QuizItem]).validate_python(c.get("/api/v1/samples/quiz").raise_for_status().json())),
        ("POST /analyze/message", lambda: MessageAnalysis.model_validate(c.post("/api/v1/analyze/message", json=msg).raise_for_status().json())),
        ("GET  /transactions/demo-users", lambda: TypeAdapter(list[DemoUser]).validate_python(c.get("/api/v1/transactions/demo-users").raise_for_status().json())),
        ("GET  /transactions/feed", lambda: TypeAdapter(list[FeedItem]).validate_python(c.get("/api/v1/transactions/feed?user_id=U001").raise_for_status().json())),
        ("POST /analyze/transaction", lambda: TxnAnalysis.model_validate(c.post("/api/v1/analyze/transaction", json={"transaction": TXN, "lang_out": "en"}).raise_for_status().json())),
        ("POST /feedback", lambda: FeedbackResponse.model_validate(c.post("/api/v1/feedback", json=fb).raise_for_status().json())),
        ("GET  /metrics", lambda: c.get("/api/v1/metrics").raise_for_status().json()["message"]["models"]),
    ]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default="http://localhost:8000")
    ap.add_argument("--frontend", default=None, help="frontend URL (default: the API origin, which serves frontend/dist)")
    args = ap.parse_args()
    proc = None
    if not wait_for(args.base, 1):
        print("starting API on :8000 ...")
        proc = subprocess.Popen([sys.executable, "-m", "uvicorn", "backend.app.main:app", "--port", "8000"],
                                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if not wait_for(args.base):
            print("FAIL: API did not start")
            return 1
    failed = 0
    with httpx.Client(base_url=args.base, timeout=15) as c:
        for name, check in checks(c):
            try:
                check()
                print(f"  PASS {name}")
            except Exception as exc:  # noqa: BLE001 - report every failure, keep going
                failed += 1
                print(f"  FAIL {name}: {exc}")
    front = args.frontend or args.base
    try:
        html = httpx.get(front, timeout=5).text
        ok = "<div id=\"root\">" in html
        print(f"  {'PASS' if ok else 'FAIL'} frontend index at {front}")
        failed += 0 if ok else 1
    except httpx.HTTPError as exc:
        failed += 1
        print(f"  FAIL frontend index at {front}: {exc} (build it with `make build`)")
    if proc:
        proc.terminate()
    print("smoke: OK" if not failed else f"smoke: {failed} failure(s)")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
