#!/usr/bin/env python3
import argparse
import subprocess
import re
import sys

if sys.platform.lower().startswith("darwin"):
    vboxmanage = "/usr/local/bin/VBoxManage"
elif sys.platform.lower().startswith("linux"):
    vboxmanage = "/usr/bin/VBoxManage"
elif sys.platform.lower().startswith("win"):
    vboxmanage = "C:\\Program Files\\Oracle\\VirtualBoxi\\VBoxManage.exe"
else:
    vboxmanage = ""

def run(cmd):
    """Run a shell command and return output as text."""
    try:
        out = subprocess.check_output(cmd, stderr=subprocess.STDOUT)
        return out.decode().strip()
    except subprocess.CalledProcessError:
        return ""


def list_vms():
    """Return a dict: {vmname: uuid} for all VMs."""
    output = run([vboxmanage, "list", "vms"])
    vms = {}
    for line in output.splitlines():
        match = re.match(r'^"(.+)"\s+\{(.+)\}$', line)
        if match:
            vms[match.group(1)] = match.group(2)
    return vms


def list_running_vms():
    """Return a set of UUIDs for running VMs."""
    output = run([vboxmanage, "list", "runningvms"])
    running = set()
    for line in output.splitlines():
        match = re.match(r'^"(.+)"\s+\{(.+)\}$', line)
        if match:
            running.add(match.group(2))
    return running


def get_vm_state(uuid):
    """Return VirtualBox VM state: running, paused, saved, powered off."""
    output = run([vboxmanage, "showvminfo", uuid, "--machinereadable"])
    for line in output.splitlines():
        if line.startswith("VMState="):
            return line.split("=")[1].strip('"')
    return "unknown"


def get_vm_ip(uuid):
    """
    Get VM IP address using guestproperty.
    Works only if:
      - VM is running
      - Guest Additions installed
    """
    output = run([
        vboxmanage, "guestproperty", "get", uuid,
        "/VirtualBox/GuestInfo/Net/0/V4/IP"
    ])

    if "No value set" in output or not output:
        return None

    return output.replace("Value:", "").strip()


def main():
    parser = argparse.ArgumentParser(
        description="List VirtualBox VMs with status and IP address"
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Show all VMs (default)"
    )
    args = parser.parse_args()

    vms = list_vms()
    running = list_running_vms()

    print(f"{'VM Name':25} {'State':15} {'IP Address'}")
    print("-" * 60)

    for name, uuid in vms.items():
        state = get_vm_state(uuid)

        if state == "running":
            ip = get_vm_ip(uuid)
        else:
            ip = None

        print(f"{name:25} {state:15} {ip or 'N/A'}")


if __name__ == "__main__":
    main()

