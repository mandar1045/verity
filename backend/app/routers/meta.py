"""Health, samples and metrics."""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml
from fastapi import APIRouter, HTTPException, Request

from backend.app.services.registry import REPORTS
from contracts.schemas import Health, QuizItem, SampleMessage

router = APIRouter(prefix="/api/v1", tags=["meta"])
SAMPLES = Path(__file__).resolve().parents[1] / "fixtures" / "samples.yaml"


@lru_cache(maxsize=1)
def _samples() -> dict[str, Any]:
    return yaml.safe_load(SAMPLES.read_text(encoding="utf-8"))


@router.get("/health", response_model=Health)
def health(request: Request) -> Health:
    return Health(status="ok", models_loaded=request.app.state.registry.models_loaded)


@router.get("/samples/messages", response_model=list[SampleMessage])
def sample_messages() -> list[SampleMessage]:
    return [SampleMessage(**m) for m in _samples()["messages"]]


@router.get("/samples/quiz", response_model=list[QuizItem])
def quiz_items() -> list[QuizItem]:
    return [QuizItem(**q) for q in _samples()["quiz"]]


@router.get("/metrics")
def metrics() -> dict[str, Any]:
    path = REPORTS / "metrics.json"
    if not path.exists():
        raise HTTPException(status_code=404, detail="metrics.json not found. Run `make eval`.")
    return json.loads(path.read_text(encoding="utf-8"))
