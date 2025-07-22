from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any, Dict

from .logger import log_event


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Basic router for Lambda events."""
    path = event.get("rawPath") or event.get("path")
    method = event.get("requestContext", {}).get("http", {}).get("method") or event.get(
        "httpMethod"
    )

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
