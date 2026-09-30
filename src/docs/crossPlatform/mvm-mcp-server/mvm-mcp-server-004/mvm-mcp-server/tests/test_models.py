"""Unit tests for Pydantic models."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

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


class TestHypervisor:
    def test_values(self):
        assert set(Hypervisor) == {
            Hypervisor.vmware,
            Hypervisor.virtualbox,
            Hypervisor.utm,
            Hypervisor.hyperv,
        }

    def test_string_coercion(self):
        assert Hypervisor("virtualbox") is Hypervisor.virtualbox

    def test_invalid_raises(self):
        with pytest.raises(ValueError):
            Hypervisor("parallels")


class TestVmIdentifier:
    def test_valid(self):
        m = VmIdentifier(hypervisor="virtualbox", vm="DevBox")
        assert m.hypervisor is Hypervisor.virtualbox
        assert m.vm == "DevBox"

    def test_empty_vm_rejected(self):
        with pytest.raises(ValidationError):
            VmIdentifier(hypervisor="utm", vm="")

    def test_missing_fields(self):
        with pytest.raises(ValidationError):
            VmIdentifier(hypervisor="utm")  # type: ignore[call-arg]


class TestStartVmRequest:
    def test_defaults(self):
        m = StartVmRequest(hypervisor="vmware", vm="/path/to/x.vmx")
        assert m.headless is False

    def test_headless_true(self):
        m = StartVmRequest(hypervisor="vmware", vm="X", headless=True)
        assert m.headless is True


class TestResetVmRequest:
    def test_defaults(self):
        m = ResetVmRequest(hypervisor="hyperv", vm="srv")
        assert m.hard is False

    def test_hard_true(self):
        m = ResetVmRequest(hypervisor="hyperv", vm="srv", hard=True)
        assert m.hard is True


class TestResponseModels:
    def test_action_result(self):
        r = ActionResult(
            message="ok",
            hypervisor=Hypervisor.virtualbox,
            vm="DevBox",
        )
        assert r.ok is True
        assert r.message == "ok"

    def test_status_result(self):
        r = StatusResult(
            hypervisor=Hypervisor.utm,
            vm="Linux",
            status="running",
        )
        assert r.status == "running"

    def test_ip_result_none(self):
        r = IpResult(hypervisor=Hypervisor.virtualbox, vm="X", ip=None)
        assert r.ip is None

    def test_list_result(self):
        r = ListResult(hypervisor=Hypervisor.vmware, table="header\nrow")
        assert "row" in r.table

    def test_json_roundtrip(self):
        m = StartVmRequest(hypervisor="virtualbox", vm="A", headless=True)
        data = m.model_dump()
        assert data == {
            "hypervisor": Hypervisor.virtualbox,
            "vm": "A",
            "headless": True,
        }
        again = StartVmRequest.model_validate(data)
        assert again == m
