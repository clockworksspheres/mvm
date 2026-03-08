#!/usr/bin/env python3
import subprocess
import argparse
import re


# ---------------------------------------------------------
# Get list of all VMs (plain text parsing)
# ---------------------------------------------------------
def utm_list():
    result = subprocess.run(
        ["utmctl", "list"],
        capture_output=True,
        text=True
    )
    result.check_returncode()

    vms = []
    for line in result.stdout.splitlines():
        # Example: Ubuntu Server (running)
        m = re.match(r"(.+?) \((.+?)\)", line.strip())
        if m:
            name, state = m.groups()
            vms.append({"name": name, "state": state})
    return vms


# ---------------------------------------------------------
# Get VM state + IP (plain text parsing)
# ---------------------------------------------------------
def utm_status(name):
    result = subprocess.run(
        ["utmctl", "status", name],
        capture_output=True,
        text=True
    )
    result.check_returncode()

    state = "unknown"
    ip = None

    for line in result.stdout.splitlines():
        line = line.strip()

        # State: running
        if line.startswith("State:"):
            state = line.split(":", 1)[1].strip()

        # Find IPv4 address anywhere in output
        m = re.search(r"(\d+\.\d+\.\d+\.\d+)", line)
        if m:
            ip = m.group(1)

    return state, ip


# ---------------------------------------------------------
# Main (argparse)
# ---------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(
        description="List all UTM VMs with name, state, and IP"
    )
    parser.add_argument(
        "-a", "--all",
        action="store_true",
        help="Show all VMs (default behavior)"
    )
    args = parser.parse_args()

    vms = utm_list()

    for vm in vms:
        name = vm["name"]
        state, ip = utm_status(name)
        ip = ip or "no-ip"

        # One-line output
        print(f"{name} | {state} | {ip}")


if __name__ == "__main__":
    main()

