#!/usr/bin/env python3
"""
FastMCP + FastAPI server for clockworksspheres/mvm
==================================================

Exposes local VM management (VMware, VirtualBox, UTM, Hyper-V) as:

  1. MCP tools  – for LLMs (Claude Desktop, Cursor, Qwen Code, etc.)
  2. REST API   – classic FastAPI/OpenAPI endpoints (Pydantic-validated)

Requires the mvm package on PYTHONPATH (clone + install from
https://github.com/clockworksspheres/mvm).

Usage
-----
    # MCP stdio (default – for Claude Desktop / Cursor / Qwen Code)
    python main.py

    # MCP over HTTP
    python main.py --mode mcp --transport http --port 8000

    # Pure FastAPI REST API (OpenAPI docs at /docs)
    python main.py --mode rest --port 8000
"""

from __future__ import annotations

import argparse


def main() -> None:
    parser = argparse.ArgumentParser(description="mvm FastMCP + FastAPI server")
    parser.add_argument(
        "--mode",
        choices=["mcp", "rest", "both"],
        default="mcp",
        help=(
            "mcp  = FastMCP only (stdio or HTTP)  |  "
            "rest = pure FastAPI REST API  |  "
            "both = REST on this port (run MCP separately if needed)"
        ),
    )
    parser.add_argument(
        "--transport",
        choices=["stdio", "http", "sse"],
        default="stdio",
        help="MCP transport when --mode mcp (default: stdio)",
    )
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()

    if args.mode == "mcp":
        from mcp_tools import mcp

        if args.transport == "stdio":
            mcp.run()
        else:
            mcp.run(transport=args.transport, host=args.host, port=args.port)

    elif args.mode == "rest":
        import uvicorn
        from rest_api import app

        uvicorn.run(app, host=args.host, port=args.port)

    else:  # both
        import uvicorn
        from rest_api import app

        print(
            f"Serving FastAPI REST on http://{args.host}:{args.port}  "
            f"(OpenAPI docs → /docs)\n"
            "For MCP, start a second process with --mode mcp --transport http"
        )
        uvicorn.run(app, host=args.host, port=args.port)


if __name__ == "__main__":
    main()
