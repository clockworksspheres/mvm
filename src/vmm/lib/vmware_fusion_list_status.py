#!/usr/bin/env python3
import argparse
import subprocess
from pathlib import Path


def run_vmrun(args):
    """Run vmrun and return output as text."""
    try:
        out = subprocess.check_output(args, stderr=subprocess.STDOUT)
        return out.decode().strip()
    except subprocess.CalledProcessError as e:
        return e.output.decode().strip()


def list_running_vms():
    """Return a set of VMX paths that are currently running."""
    output = run_vmrun(["vmrun", "list"])
    running = set()

    for line in output.splitlines():
        if line.endswith(".vmx"):
            running.add(line.strip())

    return running


def get_vm_ip(vmx_path):
    """Return the VM's IP address if available."""
    output = run_vmrun(["vmrun", "getGuestIPAddress", vmx_path, "-wait"])

    if "Error" in output or "Unable" in output:
        return None

    return output.strip()


def detect_vm_status(vmx_path, running_set):
    """Return running/suspended/off."""
    vmx_path = Path(vmx_path)
    vm_dir = vmx_path.parent

    if str(vmx_path) in running_set:
        return "running"

    # Suspended VMs have .vmss files
    if any(f.suffix == ".vmss" for f in vm_dir.iterdir()):
        return "suspended"

    return "off"


def find_all_vmx_files(root):
    """Recursively find all .vmx files under a directory."""
    return list(Path(root).rglob("*.vmx"))

def print_status4all_vms(vms):
    running_set = list_running_vms()

    print(f"{'VM Name':30} {'Status':12} {'IP Address'}")
    print("-" * 60)

    vmx_files = find_all_vmx_files("/Users/victor/Virtual Machines.localized")
    for vmx in vmx_files:
        name = vmx.stem
        status = detect_vm_status(str(vmx), running_set)
        ip = get_vm_ip(str(vmx)) if status == "running" else None

        print(f"{name:30} {status:12} {ip or 'N/A'}")

def main():
    parser = argparse.ArgumentParser(
        description="List status and IP address of all VMware Fusion VMs."
    )
    parser.add_argument(
        "path",
        help="Directory containing VMware VMs (folders with .vmx files)"
    )
    args = parser.parse_args()

    root = Path(args.path)
    if not root.exists():
        print("Path does not exist.")
        return

    vmx_files = find_all_vmx_files(root)
    if not vmx_files:
        print("No .vmx files found.")
        return

    running_set = list_running_vms()

    print_status4all_vms(vms)
    """
    print(f"{'VM Name':25} {'Status':12} {'IP Address'}")
    print("-" * 60)

    for vmx in vmx_files:
        name = vmx.stem
        status = detect_vm_status(str(vmx), running_set)
        ip = get_vm_ip(str(vmx)) if status == "running" else None

        print(f"{name:25} {status:12} {ip or 'N/A'}")
    """

if __name__ == "__main__":
    main()

