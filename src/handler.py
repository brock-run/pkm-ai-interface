from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from typing import Any, Dict

import requests

from .logger import log_event

ROAM_API_BASE = os.environ.get("ROAM_API_BASE", "http://0.0.0.0:8088")
ROAM_API_TOKEN = os.environ.get("ROAM_API_TOKEN")


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
    return {"statusCode": response.status_code, "body": response.text}


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Basic router for Lambda events."""
    path = event.get("rawPath") or event.get("path")
    method = event.get("requestContext", {}).get("http", {}).get("method") or event.get(
        "httpMethod"
    )

    if path and path.startswith("/roam_"):
        return _proxy_to_roam(event, path, method)

    if method == "POST" and path == "/analytics/log":
        body = event.get("body")
        try:
            payload = json.loads(body or "{}")
        except json.JSONDecodeError:
            return {
                "statusCode": 400,
                "body": json.dumps({"detail": "Invalid JSON"}),
            }

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
            "body": json.dumps({"status": "ok"}),
        }

    return {
        "statusCode": 404,
        "body": json.dumps({"detail": "Not found"}),
    }
