"""Verity API. Run: uvicorn backend.app.main:app --port 8000"""

from __future__ import annotations

import asyncio
import logging
import os
from collections.abc import AsyncIterator, Awaitable, Callable
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse, Response
from fastapi.staticfiles import StaticFiles

from backend.app.routers import feedback, messages, meta, transactions
from backend.app.services.registry import load_registry
from backend.app.services.txn_analyzer import DemoFeed

log = logging.getLogger("verity")
REQUEST_TIMEOUT_S = float(os.environ.get("VERITY_REQUEST_TIMEOUT", "15"))
DEFAULT_ORIGINS = "http://localhost:5173,http://127.0.0.1:5173,http://localhost:4173,http://127.0.0.1:4173,http://localhost:8080"


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    app.state.registry = load_registry()
    app.state.feed = DemoFeed()
    log.info("models_loaded=%s", app.state.registry.models_loaded)
    yield


app = FastAPI(title="Verity API", version="1.0.0", lifespan=lifespan,
              description="Scam-message and UPI-transaction risk explainer. Synthetic data only.")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in os.environ.get("VERITY_CORS_ORIGINS", DEFAULT_ORIGINS).split(",") if o.strip()],
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)


@app.middleware("http")
async def timeout_middleware(request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
    try:
        return await asyncio.wait_for(call_next(request), timeout=REQUEST_TIMEOUT_S)
    except TimeoutError:
        return JSONResponse(status_code=504, content={"detail": "The request took too long. Please try again."})


@app.exception_handler(RequestValidationError)
async def validation_handler(_: Request, exc: RequestValidationError) -> JSONResponse:
    errors = [{"field": ".".join(str(p) for p in e["loc"][1:]) or "body", "message": e["msg"]} for e in exc.errors()]
    readable = "; ".join(f"{e['field']}: {e['message']}" for e in errors)
    return JSONResponse(status_code=422, content={"detail": readable, "errors": errors})


@app.exception_handler(Exception)
async def unhandled_handler(_: Request, exc: Exception) -> JSONResponse:
    log.exception("unhandled error: %s", exc)
    return JSONResponse(status_code=500, content={"detail": "Something went wrong on our side. Please try again."})


for r in (meta.router, messages.router, transactions.router, feedback.router):
    app.include_router(r)


# Serve the built frontend (frontend/dist) from the same origin when it exists,
# so `make demo-offline` and a single-service deploy need only this process.
DIST = Path(os.environ.get("VERITY_FRONTEND_DIST", Path(__file__).resolve().parents[2] / "frontend" / "dist"))
if (DIST / "index.html").exists():
    app.mount("/assets", StaticFiles(directory=DIST / "assets"), name="assets")

    @app.get("/{path:path}", include_in_schema=False)
    async def spa(path: str) -> FileResponse:
        if path.startswith("api/"):
            raise HTTPException(status_code=404, detail="Not found")
        candidate = (DIST / path).resolve()
        if path and candidate.is_file() and candidate.is_relative_to(DIST.resolve()):
            return FileResponse(candidate)
        return FileResponse(DIST / "index.html")
