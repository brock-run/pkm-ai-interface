"""Integration tests for the handler proxy behaviour."""

import json
import os
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

from src import handler


class _RoamHandler(BaseHTTPRequestHandler):
    def do_GET(self):  # noqa: N802  (method name from BaseHTTPRequestHandler)
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'{"status": "ok"}')

    def log_message(self, format, *args):  # noqa: D401,N803
        """Silence default logging."""
        return


def test_proxy_to_roam_integration():
    """Proxy request should reach the external service and return its response."""
    server = HTTPServer(("127.0.0.1", 0), _RoamHandler)
    thread = threading.Thread(target=server.serve_forever)
    thread.daemon = True
    thread.start()

    port = server.server_port
    old_base = handler.ROAM_API_BASE
    handler.ROAM_API_BASE = f"http://127.0.0.1:{port}"
    try:
        event = {
            "rawPath": "/roam_test",
            "requestContext": {"http": {"method": "GET"}},
            "rawQueryString": "",
            "headers": {},
        }
        result = handler.lambda_handler(event, None)
    finally:
        server.shutdown()
        handler.ROAM_API_BASE = old_base

    assert result["statusCode"] == 200
    assert json.loads(result["body"]) == {"status": "ok"}
