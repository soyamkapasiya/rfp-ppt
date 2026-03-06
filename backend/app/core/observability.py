from __future__ import annotations

import time
from collections import defaultdict
from typing import Callable

from fastapi import FastAPI, Request, Response

REQUEST_COUNTER: dict[str, int] = defaultdict(int)
LATENCY_ACCUM_MS: dict[str, float] = defaultdict(float)


async def metrics_middleware(request: Request, call_next: Callable) -> Response:
    route = request.url.path
    start = time.perf_counter()
    response = await call_next(request)
    elapsed_ms = (time.perf_counter() - start) * 1000
    REQUEST_COUNTER[route] += 1
    LATENCY_ACCUM_MS[route] += elapsed_ms
    response.headers["X-Trace-Id"] = request.headers.get("X-Request-ID", "trace-local")
    return response


def register_observability(app: FastAPI) -> None:
    app.middleware("http")(metrics_middleware)

    @app.get("/metrics")
    async def metrics() -> dict:
        avg_latency = {
            route: round(LATENCY_ACCUM_MS[route] / count, 2)
            for route, count in REQUEST_COUNTER.items()
            if count > 0
        }
        return {"requests": dict(REQUEST_COUNTER), "avg_latency_ms": avg_latency}
