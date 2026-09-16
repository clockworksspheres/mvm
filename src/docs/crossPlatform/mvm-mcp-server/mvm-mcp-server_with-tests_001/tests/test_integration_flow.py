"""End-to-end style flows against the REST API with a fake backend.

These exercise multi-step agent-like sequences (list → start → status → ip)
without real hypervisors.
"""

from __future__ import annotations

from models import Hypervisor


def test_agent_style_lifecycle(client, mock_get_manager):
    # 1. Discover VMs
    listed = client.get("/vms", params={"hypervisor": "virtualbox"})
    assert listed.status_code == 200
    assert "DevBox" in listed.json()["table"]

    # 2. Start headless
    started = client.post(
        "/vms/start",
        json={
            "hypervisor": "virtualbox",
            "vm": "DevBox",
            "headless": True,
        },
    )
    assert started.status_code == 200
    assert mock_get_manager.vms["DevBox"]["state"] == "running"

    # 3. Status
    status = client.get(
        "/vms/status",
        params={"hypervisor": "virtualbox", "vm": "DevBox"},
    )
    assert status.json()["status"] == "running"

    # 4. Assign IP as guest tools would, then query
    mock_get_manager.vms["DevBox"]["ip"] = "10.0.0.5"
    ip = client.get(
        "/vms/ip",
        params={"hypervisor": "virtualbox", "vm": "DevBox"},
    )
    assert ip.json()["ip"] == "10.0.0.5"

    # 5. Pause → unpause → stop
    assert (
        client.post(
            "/vms/pause",
            json={"hypervisor": "virtualbox", "vm": "DevBox"},
        ).status_code
        == 200
    )
    assert mock_get_manager.vms["DevBox"]["state"] == "suspended"

    assert (
        client.post(
            "/vms/unpause",
            json={"hypervisor": "virtualbox", "vm": "DevBox"},
        ).status_code
        == 200
    )
    assert mock_get_manager.vms["DevBox"]["state"] == "running"

    assert (
        client.post(
            "/vms/stop",
            json={"hypervisor": "virtualbox", "vm": "DevBox"},
        ).status_code
        == 200
    )
    assert mock_get_manager.vms["DevBox"]["state"] == "off"


def test_mcp_and_rest_consistent(client, mock_get_manager):
    """MCP tool surface and REST surface return consistent semantics."""
    import mcp_tools as mt

    table_mcp = mt.list_vms(Hypervisor.virtualbox)
    table_rest = client.get(
        "/vms", params={"hypervisor": "virtualbox"}
    ).json()["table"]
    assert "DevBox" in table_mcp and "DevBox" in table_rest

    mt.start_vm(Hypervisor.virtualbox, "DevBox", headless=False)
    status_mcp = mt.get_vm_status(Hypervisor.virtualbox, "DevBox")
    status_rest = client.get(
        "/vms/status",
        params={"hypervisor": "virtualbox", "vm": "DevBox"},
    ).json()["status"]
    assert status_mcp == status_rest == "running"
