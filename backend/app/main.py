"""
RFP AI Platform – FastAPI entrypoint.

Production-ready hardening:
- CORS origin whitelist via settings (not wildcard with credentials)
- Global validation error handler returning consistent JSON
- 404 / 500 handlers
- Security headers middleware
- Lifespan context for startup/shutdown logging
"""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.logging import configure_logging
from app.core.observability import register_observability

configure_logging()
logger = logging.getLogger(__name__)


# ── Lifespan ──────────────────────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("RFP AI Platform starting", extra={"env": settings.app_env, "port": settings.api_port})
    yield
    logger.info("RFP AI Platform shutting down")


# ── App factory ───────────────────────────────────────────────────────────────
app = FastAPI(
    title="RFP AI Platform",
    description="AI-assisted RFP proposal and PowerPoint generation platform.",
    version="0.2.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    lifespan=lifespan,
)


# ── CORS ─────────────────────────────────────────────────────────────────────
# In development we allow the Vite dev server (localhost:5173).
# In production, set CORS_ORIGINS in your environment to the real domain.
_cors_origins: list[str] = [o.strip() for o in settings.cors_origins.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "X-API-Key", "X-Request-ID", "Authorization"],
    expose_headers=["X-Trace-Id", "Content-Disposition"],
)


# ── Security headers middleware ────────────────────────────────────────────────
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    return response


# ── Exception handlers ────────────────────────────────────────────────────────
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """Return 422 with a clean, structured error list."""
    errors: list[dict[str, Any]] = []
    for err in exc.errors():
        errors.append(
            {
                "field": " → ".join(str(loc) for loc in err["loc"] if loc != "body"),
                "msg": err["msg"],
                "type": err["type"],
            }
        )
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": errors, "error": "Validation failed"},
    )


@app.exception_handler(404)
async def not_found_handler(request: Request, exc) -> JSONResponse:
    return JSONResponse(
        status_code=404,
        content={"detail": "Resource not found", "path": str(request.url.path)},
    )


@app.exception_handler(500)
async def internal_error_handler(request: Request, exc) -> JSONResponse:
    logger.exception("Unhandled internal error", exc_info=exc)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error – please try again or contact support."},
    )


# ── WebSockets & Observability ───────────────────────────────────────────────
@app.websocket("/ws/jobs/{job_id}/progress")
async def job_progress_ws(websocket: WebSocket, job_id: str):
    await progress_service.connect(job_id, websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        progress_service.disconnect(job_id, websocket)


register_observability(app)
app.include_router(api_router)


# ── Health ────────────────────────────────────────────────────────────────────
@app.get("/health", tags=["ops"], summary="Health check")
async def health() -> dict[str, str]:
    return {"status": "ok", "version": "0.2.0", "env": settings.app_env}
