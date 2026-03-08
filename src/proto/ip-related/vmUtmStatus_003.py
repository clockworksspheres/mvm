#!/usr/bin/env python3
import subprocess
import argparse
import re


def run_cmd(cmd):
    """Run a command and return stdout as text, capturing stderr too."""
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True
    )
    if result.returncode != 0:
        # Print stderr so you can see what utmctl is doing
        print(f"Error running {' '.join(cmd)}: {result.stderr.strip()}")
        return ""
    return result.stdout


# ---------------------------------------------------------
# Get list of all VMs (plain text parsing)
# ---------------------------------------------------------
def utm_list():
    output = run_cmd(["utmctl", "list"])
    vms = []

    for line in output.splitlines():
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
    output = run_cmd(["utmctl", "status", name])

    state = "unknown"
    ip = None

    for line in output.splitlines():
        line = line.strip()

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
        help="Show all VMs (default)"
    )
    args = parser.parse_args()

    vms = utm_list()

    if not vms:
        print("No VMs found or utmctl produced no output.")
        return

    for vm in vms:
        name = vm["name"]
        state, ip = utm_status(name)
        ip = ip or "no-ip"

        print(f"{name} | {state} | {ip}")


if __name__ == "__main__":
    main()

