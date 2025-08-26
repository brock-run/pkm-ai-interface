import os
import uuid

import pytest
import requests

pytestmark = pytest.mark.prod

BASE = os.getenv("ROAM_API_BASE")


@pytest.mark.skipif(BASE is None, reason="ROAM_API_BASE not set")
def test_fetch_and_append() -> None:
    title = "TestPage-" + uuid.uuid4().hex[:6]

    # 1) create page
    r = requests.post(
        f"{BASE}/roam_process_batch_actions",
        json={"actions": [{"create_page": {"title": title}}]},
    )
    assert r.status_code == 200

    # 2) append a block
    r = requests.post(
        f"{BASE}/roam_process_batch_actions",
        json={
            "actions": [
                {
                    "append_block": {
                        "location": {"page": {"title": title}},
                        "string": "hello world",
                    }
                }
            ]
        },
    )
    assert r.status_code == 200

    # 3) fetch page back and verify
    page = requests.get(
        f"{BASE}/roam_fetch_page_by_title",
        params={"title": title},
    )
    data = page.json()
    assert data["title"] == title
    assert any(child["string"] == "hello world" for child in data.get("children", []))
