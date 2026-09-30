"""FastAPI REST application – OpenAPI endpoints."""

from __future__ import annotations

from fastapi import FastAPI, HTTPException, Query

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
from models import (
    ActionResult,
    ErrorDetail,
    Hypervisor,
    IpResult,
    ListResult,
    ResetVmRequest,
    StartVmRequest,
    StatusResult,
    VmIdentifier,
)

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
    except Exception as exc:  # noqa: BLE001
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
