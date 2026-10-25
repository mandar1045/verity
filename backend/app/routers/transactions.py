"""Demo users, the simulated feed, and single-transaction analysis."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, HTTPException, Query, Request
from starlette.concurrency import run_in_threadpool

from backend.app.services.txn_analyzer import DEFAULT_MEDIAN, analyze_transaction
from contracts.schemas import AnalyzeTransactionRequest, DemoUser, FeedItem, Lang, TxnAnalysis

router = APIRouter(prefix="/api/v1", tags=["transactions"])
IST = timezone(timedelta(hours=5, minutes=30))
FUTURE_TOLERANCE = timedelta(days=1)


@router.get("/transactions/demo-users", response_model=list[DemoUser])
def demo_users(request: Request) -> list[DemoUser]:
    return request.app.state.feed.users()


@router.get("/transactions/feed", response_model=list[FeedItem])
async def feed(
    request: Request,
    user_id: str = Query("U001", min_length=1, max_length=16),
    limit: int = Query(50, ge=1, le=200),
    lang_out: Lang = Query("en"),
) -> list[FeedItem]:
    demo = request.app.state.feed
    if not demo.has_user(user_id):
        raise HTTPException(status_code=404, detail=f"Unknown demo user '{user_id}'.")
    return await run_in_threadpool(demo.feed, user_id, lang_out, request.app.state.registry, limit)


@router.post("/analyze/transaction", response_model=TxnAnalysis)
async def analyze(req: AnalyzeTransactionRequest, request: Request) -> TxnAnalysis:
    t = req.transaction
    ts = t.timestamp if t.timestamp.tzinfo else t.timestamp.replace(tzinfo=IST)
    if ts > datetime.now(timezone.utc) + FUTURE_TOLERANCE:
        raise HTTPException(status_code=422, detail="Transaction timestamp is in the future.")
    t = t.model_copy(update={"timestamp": ts})
    demo = request.app.state.feed
    history = demo.history(t.user_id, ts, t.txn_id) if demo.has_user(t.user_id) else []
    median = demo.median(t.user_id) if demo.has_user(t.user_id) else DEFAULT_MEDIAN
    return await run_in_threadpool(analyze_transaction, t, history, median, req.lang_out, request.app.state.registry)
