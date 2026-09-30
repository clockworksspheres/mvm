"""Shared business logic – mvm path setup, factory, and do_* helpers."""

from __future__ import annotations

import sys
from pathlib import Path

from models import (
    ActionResult,
    Hypervisor,
    IpResult,
    ListResult,
    ResetVmRequest,
    StartVmRequest,
    StatusResult,
    VmIdentifier,
)

# ---------------------------------------------------------------------------
# Make the mvm package importable.
# Prefer an installed package; fall back to a sibling / parent clone.
# ---------------------------------------------------------------------------


def ensure_mvm_on_path() -> None:
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


ensure_mvm_on_path()

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


def get_manager(hypervisor: Hypervisor | str):
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


# ---------------------------------------------------------------------------
# Operations
# ---------------------------------------------------------------------------


def do_list_vms(hypervisor: Hypervisor) -> ListResult:
    mvm = get_manager(hypervisor)
    result = mvm.list_vms()
    return ListResult(
        hypervisor=hypervisor,
        table=result if isinstance(result, str) else str(result),
    )


def do_start_vm(req: StartVmRequest) -> ActionResult:
    mvm = get_manager(req.hypervisor)
    mvm.start_vm(req.vm, headless=req.headless)
    mode = "headless" if req.headless else "GUI"
    return ActionResult(
        message=f"Started {req.hypervisor.value} → {req.vm} ({mode})",
        hypervisor=req.hypervisor,
        vm=req.vm,
    )


def do_stop_vm(req: VmIdentifier) -> ActionResult:
    mvm = get_manager(req.hypervisor)
    mvm.stop_vm(req.vm)
    return ActionResult(
        message=f"Stopped {req.hypervisor.value} → {req.vm}",
        hypervisor=req.hypervisor,
        vm=req.vm,
    )


def do_pause_vm(req: VmIdentifier) -> ActionResult:
    mvm = get_manager(req.hypervisor)
    mvm.pause_vm(req.vm)
    return ActionResult(
        message=f"Paused (suspended) {req.hypervisor.value} → {req.vm}",
        hypervisor=req.hypervisor,
        vm=req.vm,
    )


def do_unpause_vm(req: VmIdentifier) -> ActionResult:
    mvm = get_manager(req.hypervisor)
    mvm.unpause_vm(req.vm)
    return ActionResult(
        message=f"Resumed {req.hypervisor.value} → {req.vm}",
        hypervisor=req.hypervisor,
        vm=req.vm,
    )


def do_reset_vm(req: ResetVmRequest) -> ActionResult:
    mvm = get_manager(req.hypervisor)
    mvm.reset_vm(req.vm, hard=req.hard)
    kind = "hard" if req.hard else "soft"
    return ActionResult(
        message=f"Reset ({kind}) {req.hypervisor.value} → {req.vm}",
        hypervisor=req.hypervisor,
        vm=req.vm,
    )


def do_get_status(hypervisor: Hypervisor, vm: str) -> StatusResult:
    mvm = get_manager(hypervisor)
    status = mvm.get_vm_status(vm)
    return StatusResult(hypervisor=hypervisor, vm=vm, status=str(status))


def do_get_ip(hypervisor: Hypervisor, vm: str) -> IpResult:
    mvm = get_manager(hypervisor)
    ip = mvm.get_ip(vm)
    return IpResult(
        hypervisor=hypervisor,
        vm=vm,
        ip=str(ip) if ip else None,
    )
