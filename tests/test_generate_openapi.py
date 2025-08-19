import http.server
import json
import os
import socketserver
import subprocess
import threading
from pathlib import Path


def run_server(tmpdir):
    class Handler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=str(tmpdir), **kwargs)

    server = socketserver.TCPServer(("localhost", 0), Handler)
    thread = threading.Thread(target=server.serve_forever)
    thread.daemon = True
    thread.start()
    return server, thread


def test_generate_openapi(tmp_path):
    data_dir = Path(__file__).parent / "data"
    # copy openapi.json to tmp path
    src = data_dir / "openapi.json"
    dest = tmp_path / "openapi.json"
    dest.write_bytes(src.read_bytes())

    server, thread = run_server(tmp_path)
    try:
        docs_dir = tmp_path / "docs"
        docs_dir.mkdir()
        env = {
            **os.environ,
            "MCP_URL": f"http://localhost:{server.server_address[1]}/openapi.json",
            "DOCS_DIR": str(docs_dir),
        }
        subprocess.run(
            [
                "bash",
                str(Path(__file__).parents[1] / "scripts" / "generate_openapi.sh"),
            ],
            check=True,
            env=env,
        )
        trimmed = json.loads((docs_dir / "openapi_trim.json").read_text())
    finally:
        server.shutdown()
        thread.join()

    assert set(trimmed["paths"].keys()) == {
        "/roam_process_batch_actions",
        "/roam_fetch_page_by_title",
        "/roam_search_blocks",
        "/analytics/log",
    }
