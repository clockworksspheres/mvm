#!/usr/bin/env python3
"""
Linux QEMU backend for MVM — with hardware architecture detection and proper binary selection.

Supports:
  - x86_64 → qemu-system-x86_64
  - aarch64/arm64 → qemu-system-aarch64
  - armhf (32-bit ARM) → qemu-system-arm
  - i386 → qemu-system-i386
  - etc.
"""

import os
import json
import subprocess
import shutil
from pathlib import Path
from typing import Optional, Dict, List
import libvirt

from ManageVirtualMachinesTemplate import ManageVirtualMachinesTemplate
from lib.loggers import CyLogger
from lib.loggers import LogPriority as lp


# -----------------------------
# 🧠 Hardware-Aware QEMU Binary Selection
# -----------------------------

def _get_arch() -> str:
    """Return normalized architecture name (lowercase, minimal aliases)."""
    import platform
    arch = platform.machine().lower()
    
    # Normalize major aliases
    if "x86_64" in arch or arch.startswith("amd"):
        return "x86_64"
    elif arch in ("aarch64", "arm64"):
        return "aarch64"
    elif arch in ("armv7l", "arm"):
        return "arm"
    elif arch == "i386":
        return "i386"
    else:
        # Fallback — keep raw but lowercase
        return arch

# Mapping: architecture → list of candidate binary names (in preference order)
QEMU_BIN_CANDIDATES = {
    "x86_64": ["qemu-system-x86_64", "qemu-kvm"],  # some distros alias KVM to qemu-kvm
    "aarch64": ["qemu-system-aarch64", "qemu-system-arm"],
    "arm":     ["qemu-system-arm"],
    "i386":    ["qemu-system-i386", "qemu"],
}

def _find_qemu_bin() -> Optional[str]:
    """Find the appropriate QEMU binary for this architecture."""
    arch = _get_arch()
    
    candidates = QEMU_BIN_CANDIDATES.get(arch, [f"qemu-system-{arch}"])
    
    for candidate in candidates:
        # 1. Check PATH
        path = shutil.which(candidate)
        if path and os.access(path, os.X_OK):
            return path
        
        # 2. Common hardcoded fallbacks (distro-specific)
        fallback_paths = [
            f"/usr/bin/{candidate}",
            f"/usr/local/bin/{candidate}",
        ]
        
        # Add KVM-specific paths (Fedora/CentOS/RHEL)
        if arch == "x86_64":
            fallback_paths += ["/usr/libexec/qemu-kvm"]  # RHEL/CentOS
        
        for p in fallback_paths:
            if os.path.isfile(p) and os.access(p, os.X_OK):
                return p

    # Final fallback: try raw 'qemu-system-x86_64' even if not in candidates
    # (for rare archs or custom builds)
    raw_bin = f"qemu-system-{arch}"
    path = shutil.which(raw_bin) or "/usr/bin/" + raw_bin
    if os.path.isfile(path) and os.access(path, os.X_OK):
        return path

    # ❌ Not found
    raise RuntimeError(
        f"QEMU not found for architecture '{arch}'. "
        "Please install qemu-system-<arch> (e.g., 'sudo apt install qemu-system-x86'). "
        f"Tried candidates: {candidates}"
    )

# Assign once at module load (fail fast if missing)
QEMU_BIN = _find_qemu_bin()
# -----------------------------


class VMState:
    RUNNING = "running"
    STOPPED = "stopped"
    PAUSED = "paused"
    UNKNOWN = "unknown"


class LinuxQemuMvm(ManageVirtualMachinesTemplate):
    """Concrete QEMU backend — architecture-aware, uses QMP for pause/unpause."""

    VM_DIR = Path.home() / "mvm_vms"

    def __init__(self, logger: CyLogger, **kwargs):
        super().__init__()
        self._qmp_socket_dir = self.VM_DIR / "qmp"

        if isinstance(logger, CyLogger):
            self.logger = CyLogger()
        else:
            self.logger = CyLogger()
            self.logger.initializeLogs()

    def _vm_config_path(self, name: str) -> Path:
        return self.VM_DIR / f"{name}.json"

    def _qmp_socket_path(self, name: str) -> Path:
        return self._qmp_socket_dir / f"{name}.sock"

    def _ensure_qmp_dir(self):
        self._qmp_socket_dir.mkdir(parents=True, exist_ok=True)

    def list_vms_json(self):
        try:
            conn = libvirt.open("qemu:///system")  # or qemu:///session
        except Exception as e:
            print(f"Failed to connect: {e}")
            return

        domains = conn.listAllDomains()
        if not domains:
            print("No VMs found.")
            return
        
        ip = ""
        json_table = {}
        i = 0
        for dom in domains:
            name = dom.name()          # ← correct: VM name
            state = dom.state()[0]        # e.g., 1=running, 3=pause
            state_name = {
                libvirt.VIR_DOMAIN_RUNNING: "running",
                libvirt.VIR_DOMAIN_PAUSED:  "paused",
                libvirt.VIR_DOMAIN_SHUTDOWN: "shutoff",
            }.get(state, f"unknown({state})")

            json_table[i] = {}
            json_table[i]["name"] = name
            json_table[i]["status"] = state
            json_table[i]["ip"] = ip or "N/A"

            i = i + 1

        print(json.dumps(json_table, indent=2))
        return json_table

    def list_vms_table(self):
        try:
            conn = libvirt.open("qemu:///system")  # or qemu:///session
        except Exception as e:
            print(f"Failed to connect: {e}")
            return

        domains = conn.listAllDomains()
        if not domains:
            print("No VMs found.")
            return
        
        print(f"{'VM Name':30} {'State':15} {'IP address'}")
        print("-" * 60)
        table = f"{'VM Name':30} {'State':15} {'IP address'}\n"
        table = table + ("-" * 60) + "\n"
        ip = ""
        for dom in domains:
            name = dom.name()          # ← correct: VM name
            state = dom.state()[0]        # e.g., 1=running, 3=pause
            state_name = {
                libvirt.VIR_DOMAIN_RUNNING: "running",
                libvirt.VIR_DOMAIN_PAUSED:  "paused",
                libvirt.VIR_DOMAIN_SHUTDOWN: "shutoff",
            }.get(state, f"unknown({state})")

            print(f"{name:30} {state_name:15} {ip or 'N/A'}")
            table = table + f"{name:30} {state_name:15} {ip or 'N/A'}\n"
        return table

    def list_vms(self):
        return self.list_vms_table()

    def old_list_vms(self):
        try:
            conn = libvirt.open("qemu:///system")  # or qemu:///session
        except Exception as e:
            print(f"Failed to connect: {e}")
            return

        domains = conn.listAllDomains()
        if not domains:
            print("No VMs found.")
            return

        for dom in domains:
            name = dom.name()          # ← correct: VM name
            state = dom.state()[0]        # e.g., 1=running, 3=pause
            state_name = {
                libvirt.VIR_DOMAIN_RUNNING: "running",
                libvirt.VIR_DOMAIN_PAUSED:  "paused",
                libvirt.VIR_DOMAIN_SHUTDOWN: "shutoff",
            }.get(state, f"unknown({state})")

            print(f"{name:20} {state_name}")

    """
    def list_vms(self) -> List[Dict]:
        vms = []
        for cfg_file in self.VM_DIR.glob("*.json"):
            name = cfg_file.stem
            try:
                with open(cfg_file, "r") as f:
                    cfg = json.load(f)
                state = self.get_vm_state(name)
            except Exception:
                state = VMState.UNKNOWN

            cfg.setdefault("state", state)
            vms.append(cfg)

        return sorted(vms, key=lambda x: x.get("name", ""))
    """

    def start_vm(self, name: str) -> bool:
        """Start a QEMU VM — expects metadata (disk,cpu,mem) to exist."""
        cfg_path = self._vm_config_path(name)
        if not cfg_path.exists():
            print(f"VM '{name}' config missing — cannot start.")
            return False

        with open(cfg_path, "r") as f:
            cfg = json.load(f)

        disk_path = cfg.get("disk_path")
        cpu = cfg.get("cpu", 2)
        mem_mb = cfg.get("mem_mb", 2048)

        if not disk_path or not os.path.exists(disk_path):
            print(f"VM '{name}' has missing disk: {disk_path}")
            return False

        self._ensure_qmp_dir()
        qmp_sock = str(self._qmp_socket_path(name))

        cmd = [
            QEMU_BIN,  # ← Now architecture-correct!
            "-name", name,
            "-m", f"{mem_mb}M",
            "-smp", str(cpu),
            "-drive", f"file={disk_path},if=virtio,cache=unsafe",
            "-nographic",
            "-nodefaults",
            "-monitor", f"unix:{qmp_sock},server,nowait",
            "-serial", "stdio",
        ]

        try:
            proc = subprocess.Popen(cmd)
            cfg["pid"] = proc.pid
            cfg["qmp_socket"] = qmp_sock

            with open(cfg_path, "w") as f:
                json.dump(cfg, f, indent=2)

            print(f"✅ VM '{name}' started (PID {proc.pid}, using: {QEMU_BIN})")
            return True

        except Exception as e:
            print(f"❌ Failed to start VM '{name}': {e}")
            return False

    def stop_vm(self, name: str) -> bool:
        cfg_path = self._vm_config_path(name)
        if not cfg_path.exists():
            print(f"VM '{name}' config missing.")
            return False

        with open(cfg_path, "r") as f:
            cfg = json.load(f)

        pid = cfg.get("pid")
        if not pid:
            print("No PID recorded — trying process search...")
            return self._stop_by_name(name)

        try:
            os.kill(pid, 15)  # SIGTERM
            print(f"VM '{name}' stopped.")
            return True
        except ProcessLookupError:
            print(f"VM '{name}' (PID {pid}) not running.")
            return False

    def _stop_by_name(self, name: str) -> bool:
        try:
            res = subprocess.run(
                ["pgrep", "-f", f"qemu-system.*-name {name}"],
                capture_output=True, text=True
            )
            if res.returncode != 0:
                print(f"No running VM found for '{name}'.")
                return False
            pids = res.stdout.strip().split()
            for pid_str in pids:
                os.kill(int(pid_str), 15)
            print(f"Stopped VM '{name}' (PID(s): {pids})")
            return True
        except Exception as e:
            print(f"Error stopping '{name}': {e}")
            return False

    def pause_vm(self, name: str) -> bool:
        cfg = self._load_config(name)
        qmp_sock = cfg.get("qmp_socket")
        if not qmp_sock or not os.path.exists(qmp_sock):
            print(f"QMP socket missing for '{name}' — cannot pause.")
            return False

        try:
            import socket
            cmd = {"execute": "stop"}
            msg = json.dumps(cmd) + "\n"
            with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as sock:
                sock.connect(qmp_sock)
                sock.sendall(msg.encode())
                resp = json.loads(sock.recv(4096).decode())
            print(f"VM '{name}' paused via QMP.")
            return True
        except Exception as e:
            print(f"QMP pause failed: {e}")
            return False

    def unpause_vm(self, name: str) -> bool:
        cfg = self._load_config(name)
        qmp_sock = cfg.get("qmp_socket")
        if not qmp_sock or not os.path.exists(qmp_sock):
            print(f"QMP socket missing for '{name}' — cannot unpause.")
            return False

        try:
            import socket
            cmd = {"execute": "cont"}
            msg = json.dumps(cmd) + "\n"
            with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as sock:
                sock.connect(qmp_sock)
                sock.sendall(msg.encode())
                resp = json.loads(sock.recv(4096).decode())
            print(f"VM '{name}' resumed via QMP.")
            return True
        except Exception as e:
            print(f"QMP unpause failed: {e}")
            return False

    def _load_config(self, name: str) -> Dict:
        cfg_path = self._vm_config_path(name)
        if not cfg_path.exists():
            raise ValueError(f"VM '{name}' config missing.")
        with open(cfg_path, "r") as f:
            return json.load(f)

    def _get_pid_from_name(self, name: str) -> Optional[int]:
        try:
            res = subprocess.run(
                ["pgrep", "-f", f"qemu-system.*-name {name}"],
                capture_output=True, text=True
            )
            if res.returncode == 0 and res.stdout.strip():
                return int(res.stdout.strip().split()[0])
        except Exception:
            pass
        return None

    def get_vm_state(self, name: str) -> str:
        pid = self._get_pid_from_name(name)
        if not pid:
            return VMState.STOPPED

        try:
            with open(f"/proc/{pid}/stat", "r") as f:
                state_letter = f.read().split()[2]
            if state_letter == "T":
                return VMState.PAUSED
            return VMState.RUNNING
        except FileNotFoundError:
            return VMState.STOPPED


# -----------------------------
# 📊 Diagnostic / Debugging (optional)
# -----------------------------

if __name__ == "__main__":
    import sys

    # Print hardware and binary info
    try:
        print(f"Hardware architecture: {_get_arch()}")
        print(f"Selected QEMU binary: {QEMU_BIN}")
        # Verify it's executable
        if os.access(QEMU_BIN, os.X_OK):
            print("✅ Binary is executable")
        else:
            print(f"❌ Binary not executable: {QEMU_BIN}")
    except Exception as e:
        print(f"Error detecting arch/bin: {e}")

    # CLI (minimal)
    if len(sys.argv) < 3:
        print("Usage: python LinuxQemuMvm.py [start|stop|pause|unpause] <name>")
        sys.exit(1)

    cmd, name = sys.argv[1], sys.argv[2]

    logger = CyLogger()
    logger.initializeLogs()

    mvm = LinuxQemuMvm(logger)

    if cmd == "start":
        ok = mvm.start_vm(name)
    elif cmd == "stop":
        ok = mvm.stop_vm(name)
    elif cmd == "pause":
        ok = mvm.pause_vm(name)
    elif cmd == "unpause":
        ok = mvm.unpause_vm(name)
    else:
        print(f"Unknown command: {cmd}")
        sys.exit(1)

    if not ok:
        print(f"Command '{cmd}' failed.")
        sys.exit(1)
