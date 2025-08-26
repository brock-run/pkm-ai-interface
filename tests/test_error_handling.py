import json
import logging

from src import handler


def test_invalid_json_returns_rfc7807():
    event = {
        "rawPath": "/analytics/log",
        "body": "{invalid",
        "requestContext": {"http": {"method": "POST"}},
    }
    resp = handler.lambda_handler(event, None)
    assert resp["statusCode"] == 400
    assert resp["headers"]["Content-Type"] == "application/problem+json"
    body = json.loads(resp["body"])
    assert body["title"] == "Bad Request"
    assert body["status"] == 400
    assert body["instance"]


def test_not_found_returns_rfc7807():
    event = {"rawPath": "/missing", "requestContext": {"http": {"method": "GET"}}}
    resp = handler.lambda_handler(event, None)
    assert resp["statusCode"] == 404
    body = json.loads(resp["body"])
    assert body["title"] == "Not Found"
    assert body["status"] == 404
    assert body["instance"]


def test_exception_handling_logs_and_returns_problem(monkeypatch, caplog):
    def boom(*_args, **_kwargs):
        raise RuntimeError("boom")

    monkeypatch.setattr(handler, "_proxy_to_roam", boom)
    event = {"rawPath": "/roam_boom", "requestContext": {"http": {"method": "GET"}}}
    caplog.set_level(logging.ERROR)
    resp = handler.lambda_handler(event, None)
    assert resp["statusCode"] == 500
    body = json.loads(resp["body"])
    assert body["title"] == "Internal Server Error"
    assert "Unhandled error" in caplog.text
    assert body["instance"]


def test_request_id_header_propagated():
    event = {
        "rawPath": "/missing",
        "requestContext": {"http": {"method": "GET"}},
        "headers": {"X-Request-Id": "abc-123"},
    }
    resp = handler.lambda_handler(event, None)
    body = json.loads(resp["body"])
    assert body["instance"].endswith("abc-123")
