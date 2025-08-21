from __future__ import annotations

import json
import logging
import os
import uuid
from datetime import datetime, timezone
from typing import Any, Dict

import requests

from . import token_loader
from .logger import log_event

ROAM_API_BASE = os.environ.get("ROAM_API_BASE", "http://0.0.0.0:8088")
ROAM_API_TOKEN = os.environ.get("ROAM_API_TOKEN")
_SECRET_NAME = os.environ.get("ROAM_API_SECRET_NAME")


logger = logging.getLogger(__name__)


class RequestIdFilter(logging.Filter):
    """Attach a request identifier to all log records."""

    def __init__(self) -> None:
        super().__init__()
        self.request_id = "-"

    def set(self, request_id: str) -> None:
        self.request_id = request_id

    def filter(self, record: logging.LogRecord) -> bool:  # pragma: no cover - trivial
        record.request_id = self.request_id
        return True


_request_id_filter = RequestIdFilter()
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(levelname)s %(name)s [%(request_id)s] %(message)s",
)
logging.getLogger().addFilter(_request_id_filter)

# Fetch the token from Secrets Manager if a secret name is provided and no token
# was supplied directly via the ``ROAM_API_TOKEN`` environment variable.
if _SECRET_NAME and not ROAM_API_TOKEN:
    try:
        secret_payload = token_loader.load(_SECRET_NAME)
        ROAM_API_TOKEN = secret_payload.get("token")
    except token_loader.TokenLoaderError:
        ROAM_API_TOKEN = None


def _problem_response(
    status: int,
    title: str,
    detail: str,
    type_: str = "about:blank",
    instance: str | None = None,
) -> Dict[str, Any]:
    body = {
        "type": type_,
        "title": title,
        "status": status,
        "detail": detail,
    }
    if instance:
        body["instance"] = instance
    return {
        "statusCode": status,
        "headers": {"Content-Type": "application/problem+json"},
        "body": json.dumps(body),
    }


def _proxy_to_roam(event: Dict[str, Any], path: str, method: str) -> Dict[str, Any]:
    url = f"{ROAM_API_BASE}{path}"
    qs = event.get("rawQueryString") or ""
    if not qs and event.get("queryStringParameters"):
        from urllib.parse import urlencode

        qs = urlencode(event.get("queryStringParameters", {}))
    if qs:
        url = f"{url}?{qs}"
    headers = {}
    if ROAM_API_TOKEN:
        headers["Authorization"] = f"Bearer {ROAM_API_TOKEN}"
    req_headers = event.get("headers") or {}
    if "Content-Type" in req_headers:
        headers["Content-Type"] = req_headers["Content-Type"]
    elif event.get("body"):
        headers["Content-Type"] = "application/json"
    body = event.get("body")
    response = requests.request(method, url, data=body, headers=headers)
    if response.status_code >= 400:
        logger.error("ROAM API error %s %s -> %s", method, url, response.status_code)
    return {"statusCode": response.status_code, "body": response.text}


def _get_request_id(event: Dict[str, Any], context: Any) -> str:
    headers = {k.lower(): v for k, v in (event.get("headers") or {}).items()}
    return headers.get("x-request-id") or getattr(
        context, "aws_request_id", str(uuid.uuid4())
    )


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Basic router for Lambda events."""
    request_id = _get_request_id(event, context)
    _request_id_filter.set(request_id)
    try:
        path = event.get("rawPath") or event.get("path")
        method = event.get("requestContext", {}).get("http", {}).get(
            "method"
        ) or event.get("httpMethod")
        logger.info("Handling %s %s", method, path)

        if path and path.startswith("/roam_"):
            return _proxy_to_roam(event, path, method)

        if method == "POST" and path == "/analytics/log":
            body = event.get("body")
            try:
                payload = json.loads(body or "{}")
            except json.JSONDecodeError:
                return _problem_response(
                    400,
                    "Bad Request",
                    "Invalid JSON",
                    instance=f"urn:uuid:{request_id}",
                )

            user_id = (
                event.get("requestContext", {})
                .get("authorizer", {})
                .get("claims", {})
                .get("sub")
            )

            data = {
                "user_id": user_id,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "payload": payload,
            }
            log_event(data)
            return {
                "statusCode": 200,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"status": "ok"}),
            }

        return _problem_response(
            404, "Not Found", "Not found", instance=f"urn:uuid:{request_id}"
        )
    except Exception:  # pragma: no cover - safety net
        logger.exception("Unhandled error")
        return _problem_response(
            500,
            "Internal Server Error",
            "Internal server error",
            instance=f"urn:uuid:{request_id}",
        )
