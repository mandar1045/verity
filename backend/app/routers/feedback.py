"""POST /api/v1/feedback: 'this was wrong' labels for later retraining.

Stores only the analysis id, kind, corrected label and a redacted note.
Message text is never stored.
"""

from __future__ import annotations

import json
import re
import threading
from datetime import datetime, timezone
from pathlib import Path

from fastapi import APIRouter

from contracts.schemas import FeedbackRequest, FeedbackResponse

router = APIRouter(prefix="/api/v1", tags=["feedback"])
FEEDBACK_PATH = Path(__file__).resolve().parents[2] / "data" / "feedback.jsonl"
_LOCK = threading.Lock()
_REDACT = re.compile(r"\S+@\S+|https?://\S+|\d{4,}")


def redact(note: str | None) -> str | None:
    return _REDACT.sub("[redacted]", note)[:300] if note else None


@router.post("/feedback", response_model=FeedbackResponse)
def feedback(req: FeedbackRequest) -> FeedbackResponse:
    record = {
        "ts": datetime.now(timezone.utc).isoformat(timespec="seconds"), "analysis_id": req.analysis_id,
        "kind": req.kind, "correct_label": req.correct_label, "note": redact(req.note),
    }
    FEEDBACK_PATH.parent.mkdir(parents=True, exist_ok=True)
    with _LOCK, FEEDBACK_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")
    return FeedbackResponse(ok=True)
