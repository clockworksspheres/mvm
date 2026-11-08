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
import sys
import json
import subprocess
import shutil
from pathlib import Path
from typing import Optional, Dict, List
import libvirt

from ManageVirtualMachinesTemplate import ManageVirtualMachinesTemplate
from lib.loggers import CyLogger
from lib.loggers import LogPriority as lp
from lib.libHelperExceptions import NoVmsFound


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
        self.uri = "qemu:///system"

        if isinstance(logger, CyLogger):
            self.logger = CyLogger()
        else:
            self.logger = CyLogger()
            self.logger.initializeLogs()

        try:
            self.conn = libvirt.open("qemu:///system")  # or qemu:///session
        except Exception as e:
            print(f"Failed to connect: {e}")
            return

        self.domains = self.conn.listAllDomains()
        if not self.domains:
            print("No VMs found.")
            raise NoVmsFound

    def close(self):
        if self.conn:
            self.conn.close()
            self.conn = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        The standard Python way to handle resources going out 
        of scope is using the with statement.  It guarantees 
        cleanup the exact moment the block exits.
        """
        self.close()
 
    def __del__(self):
        """
        Implementing safe destructor fallback for standard scoping
        """
        try:
            if hasattr(self, 'conn') and self.conn is not None:
                self.conn.close()
        except Exception:
            # Prevent exceptions during interpreter shutdown
            pass

    def _vm_config_path(self, name: str) -> Path:
        return self.VM_DIR / f"{name}.json"

    def _qmp_socket_path(self, name: str) -> Path:
        return self._qmp_socket_dir / f"{name}.sock"

    def _ensure_qmp_dir(self):
        self._qmp_socket_dir.mkdir(parents=True, exist_ok=True)

    def list_vms_json(self):

        ip = ""
        json_table = {}
        i = 0
        for dom in self.domains:
            name = dom.name()          # ← correct: VM name
            state = dom.state()[0]        # e.g., 1=running, 3=pause
            state_name = {
                libvirt.VIR_DOMAIN_NOSTATE: "no state",
                libvirt.VIR_DOMAIN_RUNNING: "running",
                libvirt.VIR_DOMAIN_BLOCKED: "blocked",
                libvirt.VIR_DOMAIN_PAUSED: "paused",
                libvirt.VIR_DOMAIN_SHUTDOWN: "shutting down",
                libvirt.VIR_DOMAIN_SHUTOFF: "off",
                libvirt.VIR_DOMAIN_CRASHED: "crashed",
                libvirt.VIR_DOMAIN_PMSUSPENDED: "S3 Suspended (PM)",
            }.get(state, f"unknown({state})")

            json_table[i] = {}
            json_table[i]["name"] = name
            json_table[i]["status"] = state
            json_table[i]["ip"] = ip or "N/A"

            i = i + 1

        print(json.dumps(json_table, indent=2))
        return json_table

    def list_vms_table(self):
        
        print(f"{'VM Name':30} {'State':15} {'IP address'}")
        print("-" * 60)
        table = f"{'VM Name':30} {'State':15} {'IP address'}\n"
        table = table + ("-" * 60) + "\n"
        ip = ""
        for dom in self.domains:
            name = dom.name()          # ← correct: VM name
            state = dom.state()[0]        # e.g., 1=running, 3=pause
            state_name = {
                libvirt.VIR_DOMAIN_NOSTATE: "no state",
                libvirt.VIR_DOMAIN_RUNNING: "running",
                libvirt.VIR_DOMAIN_BLOCKED: "blocked",
                libvirt.VIR_DOMAIN_PAUSED: "paused",
                libvirt.VIR_DOMAIN_SHUTDOWN: "shutting down",
                libvirt.VIR_DOMAIN_SHUTOFF: "off",
                libvirt.VIR_DOMAIN_CRASHED: "crashed",
                libvirt.VIR_DOMAIN_PMSUSPENDED: "S3 Suspended (PM)",
            }.get(state, f"unknown({state})")

            print(f"{name:30} {state_name:15} {ip or 'N/A'}")
            table = table + f"{name:30} {state_name:15} {ip or 'N/A'}\n"
        return table

    def list_vms(self):
        return self.list_vms_table()

    def start_vm_headless(self, vm_name: str) -> bool:
        started = False
        try:
            self.domain = self.conn.lookupByName(vm_name)
            self.domain.create()
            print(f"VM '{vm_name}' started successfully.")
            started = True
        except libvirt.libvirtError as e:
            print(f"Failed to start VM: {e}", file=sys.stderr)

        return started

    def start_vm_with_gui(self, vm_name: str) -> bool:
        started = False
        try:
            domain = self.conn.lookupByName(vm_name)
            
            # 1. Start the VM headlessly in the background
            domain.create()
            print(f"VM '{vm_name}' started in background.")

            # 2. Fire up the desktop window client asynchronously
            # --attach tells virt-viewer to close automatically if the VM shuts down
            # --connect targets your specific hypervisor URI
            subprocess.Popen([
                "virt-viewer", 
                "--connect", self.uri, 
                "--attach", 
                vm_name
            ])
            print(f"Opening GUI window for '{vm_name}'...")
            started = True
        except libvirt.libvirtError as e:
            print(f"Failed to start VM: {e}", file=sys.stderr)
        except FileNotFoundError:
            print("Error: 'virt-viewer' is not installed on this host system.", file=sys.stderr)

    def start_vm(self, vm_name: str, headless=False) -> bool:
        started = False
        if headless:
            started = self.start_vm_headless(vm_name)
        else:
            started = self.start_vm_with_gui(vm_name)
        return started

    def stop_vm(self, vm_name: str, force: bool = True):
        """
        Stops a running virtual machine.
        
        :param vm_name: The name of the virtual machine to stop.
        :param force: If True, forcefully kills the VM (ACPI power-off). 
                      If False, sends a graceful shutdown request to the guest OS.
        """
        try:
            domain = self.conn.lookupByName(vm_name)
            
            # Check if the VM is actually running before trying to stop it
            state, *_ = domain.info()
            # 1 = libvirt.VIR_DOMAIN_RUNNING
            if state != 1:
                print(f"VM '{vm_name}' is not currently running.")
                return

            if force:
                # Forceful shutdown (Equivalent to 'virsh destroy')
                domain.destroy()
                print(f"VM '{vm_name}' was forcefully stopped (destroyed).")
            else:
                # Graceful shutdown (Equivalent to 'virsh shutdown')
                domain.shutdown()
                print(f"Graceful shutdown signal sent to VM '{vm_name}'.")

        except libvirt.libvirtError as e:
            print(f"Failed to stop VM '{vm_name}': {e}", file=sys.stderr)

    def reset_vm(self, vm_name: str, hard: bool = True):
        """
        Forcefully resets (reboots) a running virtual machine.
        Equivalent to a hard reset button on a physical computer.
        """
        try:
            domain = self.conn.lookupByName(vm_name)
            state, *_ = domain.info()
            
            # 1 = libvirt.VIR_DOMAIN_RUNNING
            # 3 = libvirt.VIR_DOMAIN_PAUSED
            if state not in (1, 3):
                print(f"VM '{vm_name}' cannot be reset because it is not active.")
                return

            # Perform the hard reset
            domain.reset(0) # 0 is standard flags parameter
            print(f"VM '{vm_name}' has been hard reset.")

        except libvirt.libvirtError as e:
            print(f"Failed to reset VM '{vm_name}': {e}", file=sys.stderr)

    def pause_vm(self, vm_name: str):
        """
        Suspends a running virtual machine, freezing its execution.
        """
        try:
            domain = self.conn.lookupByName(vm_name)
            state, *_ = domain.info()
            
            # 1 = libvirt.VIR_DOMAIN_RUNNING
            if state != 1:
                print(f"VM '{vm_name}' cannot be paused because it is not currently running.")
                return

            domain.suspend()
            print(f"VM '{vm_name}' has been paused (suspended).")

        except libvirt.libvirtError as e:
            print(f"Failed to pause VM '{vm_name}': {e}", file=sys.stderr)

    def unpause_vm(self, vm_name: str):
        """
        Resumes a paused/suspended virtual machine.
        """
        try:
            domain = self.conn.lookupByName(vm_name)
            state, *_ = domain.info()
            
            # 3 = libvirt.VIR_DOMAIN_PAUSED
            if state != 3:
                print(f"VM '{vm_name}' cannot be unpaused because it is not in a paused state.")
                return

            domain.resume()
            print(f"VM '{vm_name}' has been successfully unpaused (resumed).")

        except libvirt.libvirtError as e:
            print(f"Failed to unpause VM '{vm_name}': {e}", file=sys.stderr)

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

    def get_vm_status(self, vm_name: str) -> str:
        """
        Retrieves the current execution status of a virtual machine.

        :param vm_name: The name of the VM.
        :return: A string describing the state (e.g., 'Running', 'Paused', 'Shutoff').
        """
        # Mapping libvirt state integers to human-readable text
        state_mapping = {
            libvirt.VIR_DOMAIN_NOSTATE: "no state",
            libvirt.VIR_DOMAIN_RUNNING: "running",
            libvirt.VIR_DOMAIN_BLOCKED: "blocked",
            libvirt.VIR_DOMAIN_PAUSED: "paused",
            libvirt.VIR_DOMAIN_SHUTDOWN: "shutting down",
            libvirt.VIR_DOMAIN_SHUTOFF: "off",
            libvirt.VIR_DOMAIN_CRASHED: "crashed",
            libvirt.VIR_DOMAIN_PMSUSPENDED: "S3 Suspended (PM)",
        }

        try:
            domain = self.conn.lookupByName(vm_name)

            # Using domain.state() is slightly more direct than domain.info()
            # It returns a list: [state_integer, reason_code]
            state, _ = domain.state()

            return state_mapping.get(state, f"Unknown Code ({state})")

        except libvirt.libvirtError as e:
            # If the VM doesn't exist or connection fails
            print(f"Error checking status for '{vm_name}': {e}", file=sys.stderr)
            return "Unknown/Error"

    def get_vm_state_json(self, vm: str):
        state = self.get_vm_state(vm, True)
        return {'state': state}

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
