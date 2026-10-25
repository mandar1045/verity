"""Record real backend responses into frontend/src/api/fixtures/fixtures.json
so the UI can run with VITE_USE_MOCKS=true (offline demo, no backend).
Run: python scripts/export_fixtures.py
"""

from __future__ import annotations

import json
from pathlib import Path

from fastapi.testclient import TestClient

from backend.app.main import app

OUT = Path(__file__).resolve().parents[1] / "frontend" / "src" / "api" / "fixtures" / "fixtures.json"
LANGS = ("en", "hi", "ta")


def main() -> None:
    with TestClient(app) as c:
        samples = c.get("/api/v1/samples/messages").json()
        quiz = c.get("/api/v1/samples/quiz").json()
        users = c.get("/api/v1/transactions/demo-users").json()
        analyses: dict[str, dict[str, object]] = {}
        for item in samples + quiz:
            analyses[item["text"].strip()] = {
                lang: c.post("/api/v1/analyze/message", json={"text": item["text"], "channel": item["channel"],
                                                              "sender": item["sender"], "lang_out": lang}).json()
                for lang in LANGS
            }
        feeds = {u["user_id"]: {lang: c.get(f"/api/v1/transactions/feed?user_id={u['user_id']}&limit=200&lang_out={lang}").json()
                                for lang in LANGS} for u in users}
        metrics = c.get("/api/v1/metrics").json()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps({"samples": samples, "quiz": quiz, "users": users, "analyses": analyses,
                               "feeds": feeds, "metrics": metrics}, ensure_ascii=False))
    print(f"wrote {OUT.relative_to(Path.cwd()) if OUT.is_relative_to(Path.cwd()) else OUT} ({OUT.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
