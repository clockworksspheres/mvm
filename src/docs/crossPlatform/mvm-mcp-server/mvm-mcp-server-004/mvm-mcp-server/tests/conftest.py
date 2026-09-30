"""Shared fixtures and mocks for mvm-mcp-server tests."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock

import pytest

# Ensure project root is importable when running pytest from any cwd
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


class FakeMvm:
    """In-memory stand-in for ManageVirtualMachines concrete backends."""

    def __init__(self, hypervisor: str = "virtualbox"):
        self.hypervisor = hypervisor
        self.vms: dict[str, dict[str, Any]] = {
            "DevBox": {"state": "off", "ip": None},
            "Win11-Test": {"state": "running", "ip": "192.168.56.10"},
            "LinuxExperiment": {"state": "suspended", "ip": None},
        }
        self.calls: list[tuple[str, tuple, dict]] = []

    def _record(self, name: str, *args, **kwargs) -> None:
        self.calls.append((name, args, kwargs))

    def list_vms(self, **kwargs) -> str:
        self._record("list_vms", **kwargs)
        lines = [f"{'VM Name':25} {'State':15} {'IP Address'}", "-" * 60]
        for name, meta in self.vms.items():
            ip = meta["ip"] or "N/A"
            lines.append(f"{name:25} {meta['state']:15} {ip}")
        return "\n".join(lines)

    def start_vm(self, vm: str = "", headless: bool = False, **kwargs) -> None:
        self._record("start_vm", vm, headless=headless, **kwargs)
        if vm not in self.vms:
            self.vms[vm] = {"state": "running", "ip": None}
        else:
            self.vms[vm]["state"] = "running"

    def stop_vm(self, vm: str = "", **kwargs) -> None:
        self._record("stop_vm", vm, **kwargs)
        if vm in self.vms:
            self.vms[vm]["state"] = "off"
            self.vms[vm]["ip"] = None

    def pause_vm(self, vm: str = "", **kwargs) -> None:
        self._record("pause_vm", vm, **kwargs)
        if vm in self.vms:
            self.vms[vm]["state"] = "suspended"

    def unpause_vm(self, vm: str = "", **kwargs) -> None:
        self._record("unpause_vm", vm, **kwargs)
        if vm in self.vms:
            self.vms[vm]["state"] = "running"

    def reset_vm(self, vm: str = "", hard: bool = True, **kwargs) -> None:
        self._record("reset_vm", vm, hard=hard, **kwargs)
        if vm in self.vms:
            self.vms[vm]["state"] = "running"

    def get_vm_status(self, vm: str) -> str:
        self._record("get_vm_status", vm)
        if vm not in self.vms:
            return "<< VM does not exist >>"
        return self.vms[vm]["state"]

    def get_ip(self, vm: str = "", **kwargs):
        self._record("get_ip", vm, **kwargs)
        if vm not in self.vms:
            return None
        return self.vms[vm].get("ip")


@pytest.fixture
def fake_mvm() -> FakeMvm:
    return FakeMvm()


@pytest.fixture
def mock_get_manager(monkeypatch, fake_mvm: FakeMvm):
    """Patch core.get_manager so all do_* helpers use FakeMvm."""

    def _get(hypervisor):
        # Accept enum or str
        name = getattr(hypervisor, "value", hypervisor)
        fake_mvm.hypervisor = name
        return fake_mvm

    monkeypatch.setattr("core.get_manager", _get)
    # Also patch where rest_api / mcp_tools may have bound references via core
    monkeypatch.setattr("core.ManageVirtualMachines", lambda h: fake_mvm, raising=False)
    return fake_mvm


@pytest.fixture
def client(mock_get_manager):
    """FastAPI TestClient with mocked mvm backend."""
    from fastapi.testclient import TestClient
    from rest_api import app

    return TestClient(app)
