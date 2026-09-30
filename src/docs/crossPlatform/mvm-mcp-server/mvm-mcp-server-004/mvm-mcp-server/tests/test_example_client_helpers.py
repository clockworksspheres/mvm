"""Smoke tests for example client helpers (no live server required)."""

from __future__ import annotations

import importlib.util
from pathlib import Path
from types import SimpleNamespace

import pytest

ROOT = Path(__file__).resolve().parent.parent
CLIENT_PATH = ROOT / "examples" / "mcp_client.py"


def _load_client_module():
    spec = importlib.util.spec_from_file_location("mcp_client_example", CLIENT_PATH)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_client_script_exists():
    assert CLIENT_PATH.is_file()


def test_text_from_result_string():
    mod = _load_client_module()
    assert mod._text_from_result("hello") == "hello"
    assert mod._text_from_result(None) == ""


def test_text_from_result_content_blocks():
    mod = _load_client_module()
    block = SimpleNamespace(text="line1")
    result = SimpleNamespace(content=[block], data=None)
    assert mod._text_from_result(result) == "line1"


def test_text_from_result_data_attr():
    mod = _load_client_module()
    result = SimpleNamespace(data={"ok": True}, content=None)
    assert "ok" in mod._text_from_result(result)
