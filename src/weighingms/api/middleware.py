"""Request ID + request logging. High-frequency polling endpoints log at DEBUG only."""

import logging
import time
import uuid
from collections.abc import Awaitable, Callable

from fastapi import FastAPI, Request, Response

from weighingms.logging_setup import request_id

log = logging.getLogger("weighingms.http")

_POLLING_SUFFIXES = ("/live", "/devices/status", "/scanner/scans")


def install_request_logging(app: FastAPI) -> None:
    @app.middleware("http")
    async def _log_requests(
        request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        rid = uuid.uuid4().hex[:8]
        token = request_id.set(rid)
        started = time.perf_counter()
        try:
            response = await call_next(request)
        finally:
            request_id.reset(token)
        elapsed_ms = (time.perf_counter() - started) * 1000
        level = logging.DEBUG if request.url.path.endswith(_POLLING_SUFFIXES) else logging.INFO
        log.log(
            level,
            "%s %s -> %s (%.0f ms) [%s]",
            request.method,
            request.url.path,
            response.status_code,
            elapsed_ms,
            rid,
        )
        response.headers["X-Request-ID"] = rid
        return response
