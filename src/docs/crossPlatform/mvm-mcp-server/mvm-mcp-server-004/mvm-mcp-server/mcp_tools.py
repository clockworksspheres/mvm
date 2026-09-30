"""FastMCP tools – LLM-facing interface."""

from __future__ import annotations

from typing import Annotated

from fastmcp import FastMCP

from core import (
    do_get_ip,
    do_get_status,
    do_list_vms,
    do_pause_vm,
    do_reset_vm,
    do_start_vm,
    do_stop_vm,
    do_unpause_vm,
)
from models import Hypervisor, ResetVmRequest, StartVmRequest, VmIdentifier

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
