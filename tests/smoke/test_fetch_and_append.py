import os
import requests
import uuid
import pytest

pytestmark = pytest.mark.prod

BASE = os.getenv("ROAM_API_BASE")


def test_fetch_and_append():
    title = "TestPage-" + uuid.uuid4().hex[:6]

    # 1) create page
    r = requests.post(
        f"{BASE}/roam_process_batch_actions",
        json={"actions": [{"create_page": {"title": title}}]},
    )
    assert r.status_code == 200

    # 2) fetch page back
    page = requests.get(
        f"{BASE}/roam_fetch_page_by_title",
        params={"title": title},
    )
    assert page.json()["title"] == title

