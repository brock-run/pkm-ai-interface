from __future__ import annotations

import importlib
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src import token_loader


def test_import_fetches_token_from_secret(monkeypatch):
    monkeypatch.delenv("ROAM_API_TOKEN", raising=False)
    monkeypatch.setenv("ROAM_API_SECRET_NAME", "my/secret")

    called = {}

    def fake_load(name):
        called["name"] = name
        return {"token": "abc123"}

    monkeypatch.setattr(token_loader, "load", fake_load)
    import src.handler as handler

    importlib.reload(handler)

    assert handler.ROAM_API_TOKEN == "abc123"
    assert called["name"] == "my/secret"

    monkeypatch.delenv("ROAM_API_SECRET_NAME", raising=False)
    importlib.reload(handler)


def test_import_handles_missing_secret(monkeypatch):
    monkeypatch.delenv("ROAM_API_TOKEN", raising=False)
    monkeypatch.setenv("ROAM_API_SECRET_NAME", "missing")

    def fake_load(name):
        raise token_loader.TokenLoaderError("not found")

    monkeypatch.setattr(token_loader, "load", fake_load)
    import src.handler as handler

    importlib.reload(handler)

    assert handler.ROAM_API_TOKEN is None

    monkeypatch.delenv("ROAM_API_SECRET_NAME", raising=False)
    importlib.reload(handler)
