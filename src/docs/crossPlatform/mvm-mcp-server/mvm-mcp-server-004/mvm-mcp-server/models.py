"""Pydantic models for request/response validation."""

from __future__ import annotations

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


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
