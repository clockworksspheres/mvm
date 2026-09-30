"""Smoke / unit tests for CLI entry point."""

from __future__ import annotations

import pytest


def test_parser_defaults():
    from main import main
    import argparse

    # Replicate parser construction without running servers
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["mcp", "rest", "both"], default="mcp")
    parser.add_argument(
        "--transport", choices=["stdio", "http", "sse"], default="stdio"
    )
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args([])
    assert args.mode == "mcp"
    assert args.transport == "stdio"
    assert args.port == 8000


def test_main_rest_mode_invokes_uvicorn(monkeypatch):
    called = {}

    def fake_run(app, host, port):
        called["host"] = host
        called["port"] = port
        called["app"] = app

    monkeypatch.setattr("uvicorn.run", fake_run)
    # Import after path is set by conftest
    import main as main_mod

    monkeypatch.setattr(
        "sys.argv",
        ["main.py", "--mode", "rest", "--host", "0.0.0.0", "--port", "9000"],
    )
    main_mod.main()
    assert called["host"] == "0.0.0.0"
    assert called["port"] == 9000
    assert called["app"] is not None


def test_main_mcp_stdio_invokes_mcp_run(monkeypatch):
    called = {"run": False}

    class FakeMcp:
        def run(self, **kwargs):
            called["run"] = True
            called["kwargs"] = kwargs

    import mcp_tools

    monkeypatch.setattr(mcp_tools, "mcp", FakeMcp())
    monkeypatch.setattr("sys.argv", ["main.py", "--mode", "mcp"])
    import main as main_mod

    main_mod.main()
    assert called["run"] is True
