"""Shared HTTP call helper for device adapters: failures become the port's *Unavailable error."""

import logging
from typing import Any

import httpx
from pydantic import BaseModel, ValidationError

from weighingms.domain.errors import DependencyUnavailable

log = logging.getLogger("weighingms.devices")


def call(
    client: httpx.Client,
    method: str,
    path: str,
    unavailable: type[DependencyUnavailable],
    message: str,
    json: Any = None,
    params: dict[str, Any] | None = None,
) -> httpx.Response:
    try:
        response = client.request(method, path, json=json, params=params)
    except httpx.HTTPError as exc:
        log.debug("%s %s failed: %s", method, path, exc.__class__.__name__)
        raise unavailable(message, {"reason": exc.__class__.__name__}) from exc
    if response.status_code >= 400:
        log.debug("%s %s -> %s", method, path, response.status_code)
        raise unavailable(message, {"status": response.status_code})
    return response


def parse[M: BaseModel](
    model: type[M], response: httpx.Response, unavailable: type[DependencyUnavailable], message: str
) -> M:
    try:
        return model.model_validate_json(response.content)
    except ValidationError as exc:
        log.warning("Unexpected device data: %s", exc.errors()[:3])
        raise unavailable(message, {"reason": "unexpected data"}) from exc
