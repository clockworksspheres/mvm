"""Unit tests for core business logic (mocked mvm backend)."""

from __future__ import annotations

import pytest

from core import (
    do_get_ip,
    do_get_status,
    do_list_vms,
    do_pause_vm,
    do_reset_vm,
    do_start_vm,
    do_stop_vm,
    do_unpause_vm,
    get_manager,
)
from models import Hypervisor, ResetVmRequest, StartVmRequest, VmIdentifier


class TestGetManager:
    def test_raises_when_mvm_missing(self, monkeypatch):
        monkeypatch.setattr("core.ManageVirtualMachines", None)
        with pytest.raises(RuntimeError, match="mvm package not found"):
            get_manager(Hypervisor.virtualbox)

    def test_wraps_hypervisor_not_applicable(self, monkeypatch):
        class Boom(Exception):
            pass

        def raise_na(name):
            raise Boom("not applicable")

        # Simulate HypervisorNotApplicable being Boom
        monkeypatch.setattr("core.ManageVirtualMachines", raise_na)
        monkeypatch.setattr("core.HypervisorNotApplicable", Boom)
        with pytest.raises(RuntimeError, match="not applicable"):
            get_manager("virtualbox")


class TestDoOperations:
    def test_list_vms(self, mock_get_manager):
        result = do_list_vms(Hypervisor.virtualbox)
        assert result.hypervisor is Hypervisor.virtualbox
        assert "DevBox" in result.table
        assert "Win11-Test" in result.table
        assert mock_get_manager.calls[-1][0] == "list_vms"

    def test_start_vm_gui(self, mock_get_manager):
        req = StartVmRequest(hypervisor=Hypervisor.virtualbox, vm="DevBox")
        result = do_start_vm(req)
        assert result.ok is True
        assert "Started" in result.message
        assert "GUI" in result.message
        assert mock_get_manager.vms["DevBox"]["state"] == "running"

    def test_start_vm_headless(self, mock_get_manager):
        req = StartVmRequest(
            hypervisor=Hypervisor.virtualbox, vm="DevBox", headless=True
        )
        result = do_start_vm(req)
        assert "headless" in result.message
        assert ("start_vm", ("DevBox",), {"headless": True}) in [
            (n, a, k) for n, a, k in mock_get_manager.calls if n == "start_vm"
        ] or any(
            c[0] == "start_vm" and c[2].get("headless") is True
            for c in mock_get_manager.calls
        )

    def test_stop_vm(self, mock_get_manager):
        req = VmIdentifier(hypervisor=Hypervisor.virtualbox, vm="Win11-Test")
        result = do_stop_vm(req)
        assert "Stopped" in result.message
        assert mock_get_manager.vms["Win11-Test"]["state"] == "off"

    def test_pause_unpause(self, mock_get_manager):
        req = VmIdentifier(hypervisor=Hypervisor.virtualbox, vm="Win11-Test")
        do_pause_vm(req)
        assert mock_get_manager.vms["Win11-Test"]["state"] == "suspended"
        do_unpause_vm(req)
        assert mock_get_manager.vms["Win11-Test"]["state"] == "running"

    def test_reset_soft_and_hard(self, mock_get_manager):
        soft = ResetVmRequest(
            hypervisor=Hypervisor.virtualbox, vm="Win11-Test", hard=False
        )
        r1 = do_reset_vm(soft)
        assert "soft" in r1.message
        hard = ResetVmRequest(
            hypervisor=Hypervisor.virtualbox, vm="Win11-Test", hard=True
        )
        r2 = do_reset_vm(hard)
        assert "hard" in r2.message

    def test_get_status_existing(self, mock_get_manager):
        r = do_get_status(Hypervisor.virtualbox, "LinuxExperiment")
        assert r.status == "suspended"
        assert r.vm == "LinuxExperiment"

    def test_get_status_missing(self, mock_get_manager):
        r = do_get_status(Hypervisor.virtualbox, "NoSuchVM")
        assert "does not exist" in r.status

    def test_get_ip_when_available(self, mock_get_manager):
        r = do_get_ip(Hypervisor.virtualbox, "Win11-Test")
        assert r.ip == "192.168.56.10"

    def test_get_ip_when_missing(self, mock_get_manager):
        r = do_get_ip(Hypervisor.virtualbox, "DevBox")
        assert r.ip is None
