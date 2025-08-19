import sys
from pathlib import Path

import requests

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src import handler


class DummyResponse:
    def __init__(self, status_code: int = 200, text: str = ""):
        self.status_code = status_code
        self.text = text


def _invoke(event, monkeypatch):
    called = {}

    def fake_request(method, url, data=None, headers=None):
        called["method"] = method
        called["url"] = url
        called["data"] = data
        called["headers"] = headers or {}
        return DummyResponse(200, '{"ok": true}')

    monkeypatch.setattr(requests, "request", fake_request)
    resp = handler.lambda_handler(event, None)
    return resp, called


def test_fetch_page_by_title(monkeypatch):
    monkeypatch.setattr(handler, "ROAM_API_BASE", "http://mcp")
    monkeypatch.setattr(handler, "ROAM_API_TOKEN", "token")
    event = {
        "rawPath": "/roam_fetch_page_by_title",
        "rawQueryString": "title=Foo",
        "requestContext": {"http": {"method": "GET"}},
        "headers": {"Content-Type": "application/json"},
    }
    resp, called = _invoke(event, monkeypatch)
    assert called["url"] == "http://mcp/roam_fetch_page_by_title?title=Foo"
    assert called["method"] == "GET"
    assert called["headers"]["Authorization"] == "Bearer token"
    assert resp["statusCode"] == 200
    assert resp["body"] == '{"ok": true}'


def test_process_batch_actions(monkeypatch):
    monkeypatch.setattr(handler, "ROAM_API_BASE", "http://mcp")
    event = {
        "rawPath": "/roam_process_batch_actions",
        "body": '{"actions": []}',
        "requestContext": {"http": {"method": "POST"}},
        "headers": {"Content-Type": "application/json"},
    }
    resp, called = _invoke(event, monkeypatch)
    assert called["url"] == "http://mcp/roam_process_batch_actions"
    assert called["method"] == "POST"
    assert called["data"] == '{"actions": []}'
    assert resp["statusCode"] == 200


def test_search_blocks(monkeypatch):
    monkeypatch.setattr(handler, "ROAM_API_BASE", "http://mcp")
    event = {
        "rawPath": "/roam_search_blocks",
        "rawQueryString": "query=test",
        "requestContext": {"http": {"method": "GET"}},
    }
    resp, called = _invoke(event, monkeypatch)
    assert called["url"] == "http://mcp/roam_search_blocks?query=test"
    assert called["method"] == "GET"
    assert resp["statusCode"] == 200
