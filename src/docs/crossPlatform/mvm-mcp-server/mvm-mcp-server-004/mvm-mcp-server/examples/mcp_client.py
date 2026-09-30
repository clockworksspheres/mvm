#!/usr/bin/env python3
"""
Example MCP client for the mvm FastMCP server
==============================================

Connects over stdio (spawns the server) or HTTP and demonstrates:

  * listing tools
  * calling list_vms / get_vm_status / start_vm (optional)

Usage
-----
    # Stdio – client starts the server as a subprocess
    python examples/mcp_client.py

    # Point at an already-running HTTP MCP server
    python examples/mcp_client.py --http http://127.0.0.1:8000/mcp

    # List tools only (no VM calls)
    python examples/mcp_client.py --list-only

    # Call list_vms for a specific hypervisor
    python examples/mcp_client.py --hypervisor virtualbox

    # Full demo: list → status → (optional start)
    python examples/mcp_client.py --hypervisor virtualbox --vm DevBox --start

Prerequisites
-------------
    pip install -r requirements.txt
    # For real VM control, mvm on PYTHONPATH and hypervisor running
"""

from __future__ import annotations

import argparse
import asyncio
import os
import sys
from pathlib import Path

# Project root on path when run as scripts/examples/mcp_client.py
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def _text_from_result(result) -> str:
    """Normalize FastMCP / MCP tool result to a plain string."""
    if result is None:
        return ""
    if isinstance(result, str):
        return result
    # CallToolResult-like: .data or .content
    data = getattr(result, "data", None)
    if data is not None:
        return str(data)
    content = getattr(result, "content", None)
    if content:
        parts = []
        for block in content:
            text = getattr(block, "text", None)
            if text is not None:
                parts.append(text)
            else:
                parts.append(str(block))
        return "\n".join(parts)
    return str(result)


async def run_session(client, args: argparse.Namespace) -> None:
    async with client:
        # --- discover ---
        tools = await client.list_tools()
        print("Available tools:")
        for t in tools:
            desc = (t.description or "").strip().split("\n")[0]
            print(f"  • {t.name}: {desc}")
        print()

        if args.list_only:
            return

        hypervisor = args.hypervisor

        # --- list_vms ---
        print(f"→ list_vms(hypervisor={hypervisor!r})")
        try:
            listed = await client.call_tool(
                "list_vms", {"hypervisor": hypervisor}
            )
            print(_text_from_result(listed))
        except Exception as exc:  # noqa: BLE001
            print(f"  (list_vms failed: {exc})")
            print("  Tip: ensure mvm is on PYTHONPATH and the hypervisor is running.")
            return
        print()

        if not args.vm:
            return

        # --- status ---
        print(f"→ get_vm_status(hypervisor={hypervisor!r}, vm={args.vm!r})")
        status = await client.call_tool(
            "get_vm_status",
            {"hypervisor": hypervisor, "vm": args.vm},
        )
        print(_text_from_result(status))
        print()

        # --- optional start ---
        if args.start:
            print(
                f"→ start_vm(hypervisor={hypervisor!r}, vm={args.vm!r}, "
                f"headless={args.headless})"
            )
            started = await client.call_tool(
                "start_vm",
                {
                    "hypervisor": hypervisor,
                    "vm": args.vm,
                    "headless": args.headless,
                },
            )
            print(_text_from_result(started))
            print()

            status2 = await client.call_tool(
                "get_vm_status",
                {"hypervisor": hypervisor, "vm": args.vm},
            )
            print("status after start:", _text_from_result(status2))

        # --- optional IP ---
        if args.ip:
            print(f"→ get_vm_ip(hypervisor={hypervisor!r}, vm={args.vm!r})")
            ip = await client.call_tool(
                "get_vm_ip",
                {"hypervisor": hypervisor, "vm": args.vm},
            )
            print(_text_from_result(ip))


def build_client(args: argparse.Namespace):
    """Build a FastMCP Client for stdio or HTTP."""
    from fastmcp import Client

    if args.http:
        print(f"Connecting via HTTP → {args.http}")
        return Client(args.http)

    # Stdio: spawn main.py in MCP mode
    main_py = ROOT / "main.py"
    if not main_py.is_file():
        raise SystemExit(f"Server entry not found: {main_py}")

    env = os.environ.copy()
    # Keep project root importable for the child process
    py_path = env.get("PYTHONPATH", "")
    parts = [str(ROOT)] + ([py_path] if py_path else [])
    env["PYTHONPATH"] = os.pathsep.join(parts)

    print(f"Spawning stdio server: python {main_py}")
    return Client(
        main_py,
        env=env,
    )


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Example MCP client for the mvm server",
    )
    p.add_argument(
        "--http",
        metavar="URL",
        default=None,
        help="Connect to an HTTP MCP endpoint (e.g. http://127.0.0.1:8000/mcp)",
    )
    p.add_argument(
        "--list-only",
        action="store_true",
        help="Only list tools; do not call VM tools",
    )
    p.add_argument(
        "--hypervisor",
        default="virtualbox",
        choices=["vmware", "virtualbox", "utm", "hyperv"],
        help="Hypervisor for tool calls (default: virtualbox)",
    )
    p.add_argument(
        "--vm",
        default=None,
        help="VM name/path for status / start / ip",
    )
    p.add_argument(
        "--start",
        action="store_true",
        help="Also call start_vm (requires --vm)",
    )
    p.add_argument(
        "--headless",
        action="store_true",
        help="Pass headless=True to start_vm",
    )
    p.add_argument(
        "--ip",
        action="store_true",
        help="Also call get_vm_ip (requires --vm)",
    )
    return p.parse_args()


def main() -> None:
    args = parse_args()
    if args.start and not args.vm:
        raise SystemExit("--start requires --vm")
    if args.ip and not args.vm:
        raise SystemExit("--ip requires --vm")

    client = build_client(args)
    asyncio.run(run_session(client, args))


if __name__ == "__main__":
    main()
