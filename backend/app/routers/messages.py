"""POST /api/v1/analyze/message."""

from __future__ import annotations

from fastapi import APIRouter, Request
from starlette.concurrency import run_in_threadpool

from backend.app.services.analyzer import analyze_message
from contracts.schemas import AnalyzeMessageRequest, MessageAnalysis

router = APIRouter(prefix="/api/v1", tags=["messages"])


@router.post("/analyze/message", response_model=MessageAnalysis)
async def analyze(req: AnalyzeMessageRequest, request: Request) -> MessageAnalysis:
    return await run_in_threadpool(analyze_message, req, request.app.state.registry)
