"""Console logging with a request ID on each line (coding standards: Logging)."""

import contextvars
import logging

request_id: contextvars.ContextVar[str] = contextvars.ContextVar("request_id", default="-")

_FORMAT = "%(asctime)s %(levelname)-7s [%(request_id)s] %(name)s: %(message)s"


class _RequestIdFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = request_id.get()
        return True


def configure_logging(level: int = logging.INFO) -> None:
    logger = logging.getLogger("weighingms")
    if any(isinstance(f, _RequestIdFilter) for h in logger.handlers for f in h.filters):
        return
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter(_FORMAT))
    handler.addFilter(_RequestIdFilter())
    logger.addHandler(handler)
    logger.setLevel(level)
    logger.propagate = False
