"""Unit tests for FastMCP tool functions (mocked backend)."""

from __future__ import annotations

import pytest

from models import Hypervisor


@pytest.fixture
def tools(mock_get_manager):
    """Import mcp tool callables after mock is in place."""
    import mcp_tools as mt

    return mt


class TestMcpTools:
    def test_list_vms(self, tools):
        table = tools.list_vms(Hypervisor.virtualbox)
        assert isinstance(table, str)
        assert "DevBox" in table

    def test_start_vm(self, tools, mock_get_manager):
        msg = tools.start_vm(Hypervisor.virtualbox, "DevBox", headless=True)
        assert "Started" in msg
        assert "headless" in msg
        assert mock_get_manager.vms["DevBox"]["state"] == "running"

    def test_stop_vm(self, tools, mock_get_manager):
        msg = tools.stop_vm(Hypervisor.virtualbox, "Win11-Test")
        assert "Stopped" in msg
        assert mock_get_manager.vms["Win11-Test"]["state"] == "off"

    def test_pause_vm(self, tools, mock_get_manager):
        msg = tools.pause_vm(Hypervisor.virtualbox, "Win11-Test")
        assert "Paused" in msg
        assert mock_get_manager.vms["Win11-Test"]["state"] == "suspended"

    def test_unpause_vm(self, tools, mock_get_manager):
        msg = tools.unpause_vm(Hypervisor.virtualbox, "LinuxExperiment")
        assert "Resumed" in msg
        assert mock_get_manager.vms["LinuxExperiment"]["state"] == "running"

    def test_reset_vm(self, tools):
        msg = tools.reset_vm(Hypervisor.virtualbox, "Win11-Test", hard=True)
        assert "hard" in msg

    def test_get_vm_status(self, tools):
        status = tools.get_vm_status(Hypervisor.virtualbox, "Win11-Test")
        assert status == "running"

    def test_get_vm_ip_present(self, tools):
        ip = tools.get_vm_ip(Hypervisor.virtualbox, "Win11-Test")
        assert ip == "192.168.56.10"

    def test_get_vm_ip_absent(self, tools):
        ip = tools.get_vm_ip(Hypervisor.virtualbox, "DevBox")
        assert "not available" in ip.lower() or ip.startswith("IP not")

    def test_mcp_server_name(self, tools):
        assert tools.mcp.name == "mvm"
