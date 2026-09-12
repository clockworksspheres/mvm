#!/usr/bin/env python3
"""
FastMCP + FastAPI server for clockworksspheres/mvm
==================================================

Exposes local VM management (VMware, VirtualBox, UTM, Hyper-V) as:

  1. MCP tools  – for LLMs (Claude Desktop, Cursor, etc.)
  2. REST API   – classic FastAPI/OpenAPI endpoints (Pydantic-validated)

Requires the mvm package on PYTHONPATH (clone + install from
https://github.com/clockworksspheres/mvm).

Usage
-----
    # MCP stdio (default – for Claude Desktop / Cursor)
    python mvm_mcp_server.py

    # MCP over HTTP
    python mvm_mcp_server.py --transport http --port 8000

    # Pure FastAPI REST API (OpenAPI docs at /docs)
    python mvm_mcp_server.py --mode rest --port 8000

    # Both MCP HTTP + REST on the same port (mounted)
    python mvm_mcp_server.py --mode both --port 8000
"""

from __future__ import annotations

import sys
from enum import Enum
from pathlib import Path
from typing import Annotated, Optional

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field
from fastmcp import FastMCP

# ---------------------------------------------------------------------------
# Make the mvm package importable.
# Prefer an installed package; fall back to a sibling / parent clone.
# ---------------------------------------------------------------------------
def _ensure_mvm_on_path() -> None:
    candidates = [
        Path(__file__).resolve().parent / "mvm" / "src",
        Path(__file__).resolve().parent.parent / "mvm" / "src",
        Path.home() / "src" / "mvm" / "src",
        Path("/opt/mvm/src"),
    ]
    for p in candidates:
        if (p / "mvm").is_dir() or (p / "ManageVirtualMachines.py").exists():
            sys.path.insert(0, str(p))
            return


_ensure_mvm_on_path()

try:
    from ManageVirtualMachines import ManageVirtualMachines
    from mvm.lib.libHelperExceptions import (
        HypervisorNotApplicable,
        HypervisorNotAvailableError,
    )
except ImportError:
    ManageVirtualMachines = None  # type: ignore
    HypervisorNotApplicable = Exception  # type: ignore
    HypervisorNotAvailableError = Exception  # type: ignore


# ---------------------------------------------------------------------------
# Pydantic models
# ---------------------------------------------------------------------------

class Hypervisor(str, Enum):
    """Supported hypervisors (same set as upstream mvm)."""

    vmware = "vmware"
    virtualbox = "virtualbox"
    utm = "utm"
    hyperv = "hyperv"


class VmIdentifier(BaseModel):
    """Common payload: which hypervisor + which VM."""

    hypervisor: Hypervisor = Field(
        ..., description="vmware | virtualbox | utm | hyperv"
    )
    vm: str = Field(
        ...,
        min_length=1,
        description="VM name or full path to .vmx / .vbox / UTM package",
    )


class StartVmRequest(VmIdentifier):
    headless: bool = Field(
        False,
        description="Start without a GUI window (where supported)",
    )


class ResetVmRequest(VmIdentifier):
    hard: bool = Field(
        False,
        description="Force a hard reset (like pressing the power button)",
    )


class ActionResult(BaseModel):
    """Standard response for mutating operations."""

    ok: bool = True
    message: str
    hypervisor: Hypervisor
    vm: Optional[str] = None


class StatusResult(BaseModel):
    hypervisor: Hypervisor
    vm: str
    status: str = Field(
        ...,
        description="Typically: running | suspended | off | error text",
    )


class IpResult(BaseModel):
    hypervisor: Hypervisor
    vm: str
    ip: Optional[str] = Field(
        None,
        description="Guest IP if available (requires guest tools)",
    )


class ListResult(BaseModel):
    hypervisor: Hypervisor
    table: str = Field(
        ...,
        description="Human-readable table of VMs, state and IP",
    )


class ErrorDetail(BaseModel):
    detail: str


# ---------------------------------------------------------------------------
# Shared business logic
# ---------------------------------------------------------------------------

def _get_manager(hypervisor: Hypervisor | str):
    """Instantiate the concrete ManageVirtualMachines factory."""
    if ManageVirtualMachines is None:
        raise RuntimeError(
            "mvm package not found. Clone https://github.com/clockworksspheres/mvm "
            "and put its src/ directory on PYTHONPATH, or install it editable."
        )
    name = hypervisor.value if isinstance(hypervisor, Hypervisor) else hypervisor
    try:
        return ManageVirtualMachines(name)
    except HypervisorNotApplicable as exc:
        raise RuntimeError(
            f"Hypervisor '{name}' is not applicable on this OS / host "
            f"configuration: {exc}"
        ) from exc


def do_list_vms(hypervisor: Hypervisor) -> ListResult:
    mvm = _get_manager(hypervisor)
    result = mvm.list_vms()
    return ListResult(
        hypervisor=hypervisor,
        table=result if isinstance(result, str) else str(result),
    )


def do_start_vm(req: StartVmRequest) -> ActionResult:
    mvm = _get_manager(req.hypervisor)
    mvm.start_vm(req.vm, headless=req.headless)
    mode = "headless" if req.headless else "GUI"
    return ActionResult(
        message=f"Started {req.hypervisor.value} → {req.vm} ({mode})",
        hypervisor=req.hypervisor,
        vm=req.vm,
    )


def do_stop_vm(req: VmIdentifier) -> ActionResult:
    mvm = _get_manager(req.hypervisor)
    mvm.stop_vm(req.vm)
    return ActionResult(
        message=f"Stopped {req.hypervisor.value} → {req.vm}",
        hypervisor=req.hypervisor,
        vm=req.vm,
    )


def do_pause_vm(req: VmIdentifier) -> ActionResult:
    mvm = _get_manager(req.hypervisor)
    mvm.pause_vm(req.vm)
    return ActionResult(
        message=f"Paused (suspended) {req.hypervisor.value} → {req.vm}",
        hypervisor=req.hypervisor,
        vm=req.vm,
    )


def do_unpause_vm(req: VmIdentifier) -> ActionResult:
    mvm = _get_manager(req.hypervisor)
    mvm.unpause_vm(req.vm)
    return ActionResult(
        message=f"Resumed {req.hypervisor.value} → {req.vm}",
        hypervisor=req.hypervisor,
        vm=req.vm,
    )


def do_reset_vm(req: ResetVmRequest) -> ActionResult:
    mvm = _get_manager(req.hypervisor)
    mvm.reset_vm(req.vm, hard=req.hard)
    kind = "hard" if req.hard else "soft"
    return ActionResult(
        message=f"Reset ({kind}) {req.hypervisor.value} → {req.vm}",
        hypervisor=req.hypervisor,
        vm=req.vm,
    )


def do_get_status(hypervisor: Hypervisor, vm: str) -> StatusResult:
    mvm = _get_manager(hypervisor)
    status = mvm.get_vm_status(vm)
    return StatusResult(hypervisor=hypervisor, vm=vm, status=str(status))


def do_get_ip(hypervisor: Hypervisor, vm: str) -> IpResult:
    mvm = _get_manager(hypervisor)
    ip = mvm.get_ip(vm)
    return IpResult(
        hypervisor=hypervisor,
        vm=vm,
        ip=str(ip) if ip else None,
    )


# ---------------------------------------------------------------------------
# FastMCP server (LLM tools)
# ---------------------------------------------------------------------------

mcp = FastMCP(
    name="mvm",
    instructions=(
        "Local virtual-machine manager (clockworksspheres/mvm). "
        "Supports VMware Fusion/Workstation, VirtualBox, UTM (macOS) and "
        "Hyper-V (Windows). Use list_vms first, then start/stop/pause/etc. "
        "The chosen hypervisor process must already be running on the host."
    ),
)


@mcp.tool
def list_vms(
    hypervisor: Annotated[Hypervisor, "Which hypervisor to query"],
) -> str:
    """List virtual machines known to the given hypervisor together with their current state (and IP when available)."""
    return do_list_vms(hypervisor).table


@mcp.tool
def start_vm(
    hypervisor: Annotated[Hypervisor, "Hypervisor that owns the VM"],
    vm: Annotated[str, "VM name or full path to .vmx / .vbox / UTM package"],
    headless: Annotated[bool, "Start without a GUI window"] = False,
) -> str:
    """Start (power-on) a virtual machine."""
    return do_start_vm(
        StartVmRequest(hypervisor=hypervisor, vm=vm, headless=headless)
    ).message


@mcp.tool
def stop_vm(
    hypervisor: Annotated[Hypervisor, "Hypervisor that owns the VM"],
    vm: Annotated[str, "VM name or path"],
) -> str:
    """Gracefully shut down (or power-off) a virtual machine."""
    return do_stop_vm(VmIdentifier(hypervisor=hypervisor, vm=vm)).message


@mcp.tool
def pause_vm(
    hypervisor: Annotated[Hypervisor, "Hypervisor that owns the VM"],
    vm: Annotated[str, "VM name or path"],
) -> str:
    """Suspend / save the state of a running virtual machine."""
    return do_pause_vm(VmIdentifier(hypervisor=hypervisor, vm=vm)).message


@mcp.tool
def unpause_vm(
    hypervisor: Annotated[Hypervisor, "Hypervisor that owns the VM"],
    vm: Annotated[str, "VM name or path"],
) -> str:
    """Resume a previously suspended virtual machine."""
    return do_unpause_vm(VmIdentifier(hypervisor=hypervisor, vm=vm)).message


@mcp.tool
def reset_vm(
    hypervisor: Annotated[Hypervisor, "Hypervisor that owns the VM"],
    vm: Annotated[str, "VM name or path"],
    hard: Annotated[bool, "Force a hard reset"] = False,
) -> str:
    """Reset / reboot a virtual machine."""
    return do_reset_vm(
        ResetVmRequest(hypervisor=hypervisor, vm=vm, hard=hard)
    ).message


@mcp.tool
def get_vm_status(
    hypervisor: Annotated[Hypervisor, "Hypervisor that owns the VM"],
    vm: Annotated[str, "VM name or path"],
) -> str:
    """Return the current power state of a VM (running / suspended / off)."""
    return do_get_status(hypervisor, vm).status


@mcp.tool
def get_vm_ip(
    hypervisor: Annotated[Hypervisor, "Hypervisor that owns the VM"],
    vm: Annotated[str, "VM name or path"],
) -> str:
    """Attempt to retrieve the guest IP address (requires guest tools)."""
    result = do_get_ip(hypervisor, vm)
    return result.ip or "IP not available (guest tools missing or VM not running)"


# ---------------------------------------------------------------------------
# FastAPI REST application
# ---------------------------------------------------------------------------

app = FastAPI(
    title="mvm REST API",
    description=(
        "REST interface for clockworksspheres/mvm – local management of "
        "VMware, VirtualBox, UTM and Hyper-V virtual machines."
    ),
    version="1.0.0",
    responses={500: {"model": ErrorDetail}},
)


def _http_wrap(fn, *args, **kwargs):
    try:
        return fn(*args, **kwargs)
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    except Exception as exc:  # noqa: BLE001 – surface upstream errors cleanly
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get(
    "/vms",
    response_model=ListResult,
    summary="List VMs",
)
def api_list_vms(
    hypervisor: Hypervisor = Query(..., description="Target hypervisor"),
) -> ListResult:
    return _http_wrap(do_list_vms, hypervisor)


@app.post(
    "/vms/start",
    response_model=ActionResult,
    summary="Start a VM",
)
def api_start_vm(body: StartVmRequest) -> ActionResult:
    return _http_wrap(do_start_vm, body)


@app.post(
    "/vms/stop",
    response_model=ActionResult,
    summary="Stop a VM",
)
def api_stop_vm(body: VmIdentifier) -> ActionResult:
    return _http_wrap(do_stop_vm, body)


@app.post(
    "/vms/pause",
    response_model=ActionResult,
    summary="Pause / suspend a VM",
)
def api_pause_vm(body: VmIdentifier) -> ActionResult:
    return _http_wrap(do_pause_vm, body)


@app.post(
    "/vms/unpause",
    response_model=ActionResult,
    summary="Resume a suspended VM",
)
def api_unpause_vm(body: VmIdentifier) -> ActionResult:
    return _http_wrap(do_unpause_vm, body)


@app.post(
    "/vms/reset",
    response_model=ActionResult,
    summary="Reset a VM",
)
def api_reset_vm(body: ResetVmRequest) -> ActionResult:
    return _http_wrap(do_reset_vm, body)


@app.get(
    "/vms/status",
    response_model=StatusResult,
    summary="Get VM power state",
)
def api_get_status(
    hypervisor: Hypervisor = Query(...),
    vm: str = Query(..., min_length=1),
) -> StatusResult:
    return _http_wrap(do_get_status, hypervisor, vm)


@app.get(
    "/vms/ip",
    response_model=IpResult,
    summary="Get guest IP",
)
def api_get_ip(
    hypervisor: Hypervisor = Query(...),
    vm: str = Query(..., min_length=1),
) -> IpResult:
    return _http_wrap(do_get_ip, hypervisor, vm)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import argparse

    import uvicorn

    parser = argparse.ArgumentParser(description="mvm FastMCP + FastAPI server")
    parser.add_argument(
        "--mode",
        choices=["mcp", "rest", "both"],
        default="mcp",
        help=(
            "mcp  = FastMCP only (stdio or HTTP)  |  "
            "rest = pure FastAPI REST API  |  "
            "both = mount MCP + REST on one HTTP server"
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
        if args.transport == "stdio":
            mcp.run()
        else:
            mcp.run(transport=args.transport, host=args.host, port=args.port)

    elif args.mode == "rest":
        uvicorn.run(app, host=args.host, port=args.port)

    else:  # both – serve FastAPI and expose MCP over the same process
        # FastMCP HTTP transport can be mounted; simplest reliable path is
        # to run the REST app and let users point MCP clients at a second
        # process, or use the streamable-http mount when available.
        # For now we run pure REST under "both" and document the dual-process
        # approach; advanced users can compose the two ASGI apps themselves.
        print(
            f"Serving FastAPI REST on http://{args.host}:{args.port}  "
            f"(OpenAPI docs → /docs)\n"
            "For MCP, start a second process with --mode mcp --transport http"
        )
        uvicorn.run(app, host=args.host, port=args.port)
