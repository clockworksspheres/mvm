"""Integration tests for FastAPI REST endpoints."""

from __future__ import annotations

import pytest


class TestHealth:
    def test_health(self, client):
        r = client.get("/health")
        assert r.status_code == 200
        assert r.json() == {"status": "ok"}


class TestListVms:
    def test_list_ok(self, client):
        r = client.get("/vms", params={"hypervisor": "virtualbox"})
        assert r.status_code == 200
        body = r.json()
        assert body["hypervisor"] == "virtualbox"
        assert "DevBox" in body["table"]

    def test_list_invalid_hypervisor(self, client):
        r = client.get("/vms", params={"hypervisor": "parallels"})
        assert r.status_code == 422

    def test_list_missing_hypervisor(self, client):
        r = client.get("/vms")
        assert r.status_code == 422


class TestStartStop:
    def test_start(self, client):
        r = client.post(
            "/vms/start",
            json={
                "hypervisor": "virtualbox",
                "vm": "DevBox",
                "headless": True,
            },
        )
        assert r.status_code == 200
        body = r.json()
        assert body["ok"] is True
        assert "Started" in body["message"]
        assert body["vm"] == "DevBox"

    def test_start_missing_vm(self, client):
        r = client.post(
            "/vms/start",
            json={"hypervisor": "virtualbox", "vm": ""},
        )
        assert r.status_code == 422

    def test_stop(self, client):
        r = client.post(
            "/vms/stop",
            json={"hypervisor": "virtualbox", "vm": "Win11-Test"},
        )
        assert r.status_code == 200
        assert "Stopped" in r.json()["message"]


class TestPauseUnpauseReset:
    def test_pause(self, client):
        r = client.post(
            "/vms/pause",
            json={"hypervisor": "virtualbox", "vm": "Win11-Test"},
        )
        assert r.status_code == 200
        assert "Paused" in r.json()["message"]

    def test_unpause(self, client):
        r = client.post(
            "/vms/unpause",
            json={"hypervisor": "virtualbox", "vm": "LinuxExperiment"},
        )
        assert r.status_code == 200
        assert "Resumed" in r.json()["message"]

    def test_reset_hard(self, client):
        r = client.post(
            "/vms/reset",
            json={
                "hypervisor": "virtualbox",
                "vm": "Win11-Test",
                "hard": True,
            },
        )
        assert r.status_code == 200
        assert "hard" in r.json()["message"]


class TestStatusAndIp:
    def test_status(self, client):
        r = client.get(
            "/vms/status",
            params={"hypervisor": "virtualbox", "vm": "Win11-Test"},
        )
        assert r.status_code == 200
        body = r.json()
        assert body["status"] == "running"
        assert body["vm"] == "Win11-Test"

    def test_status_empty_vm(self, client):
        r = client.get(
            "/vms/status",
            params={"hypervisor": "virtualbox", "vm": ""},
        )
        assert r.status_code == 422

    def test_ip(self, client):
        r = client.get(
            "/vms/ip",
            params={"hypervisor": "virtualbox", "vm": "Win11-Test"},
        )
        assert r.status_code == 200
        assert r.json()["ip"] == "192.168.56.10"

    def test_ip_none(self, client):
        r = client.get(
            "/vms/ip",
            params={"hypervisor": "virtualbox", "vm": "DevBox"},
        )
        assert r.status_code == 200
        assert r.json()["ip"] is None


class TestErrorPropagation:
    def test_runtime_error_becomes_500(self, client, monkeypatch):
        def boom(*_a, **_k):
            raise RuntimeError("hypervisor not running")

        monkeypatch.setattr("rest_api.do_list_vms", boom)
        r = client.get("/vms", params={"hypervisor": "virtualbox"})
        assert r.status_code == 500
        assert "hypervisor not running" in r.json()["detail"]


class TestOpenApi:
    def test_openapi_available(self, client):
        r = client.get("/openapi.json")
        assert r.status_code == 200
        schema = r.json()
        assert schema["info"]["title"] == "mvm REST API"
        paths = schema["paths"]
        assert "/vms" in paths
        assert "/vms/start" in paths
        assert "/health" in paths
