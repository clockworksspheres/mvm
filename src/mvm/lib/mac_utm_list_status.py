#!/usr/bin/env python3
import subprocess
import argparse
import re

utmctl = "/opt/homebrew/bin/utmctl"

def run_cmd(cmd):
    """Run a command and return stdout, capturing stderr."""
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error running {' '.join(cmd)}: {result.stderr.strip()}")
        return ""
    return result.stdout


# ---------------------------------------------------------
# Parse "utmctl list" table format
# ---------------------------------------------------------
def utm_list():
    output = run_cmd([utmctl, "list"])
    lines = output.splitlines()

    vms = []

    # Skip header line
    for line in lines[1:]:
        parts = line.split()
        if len(parts) < 3:
            continue

        uuid = parts[0]
        state = parts[1]
        name = " ".join(parts[2:])  # handles names with spaces

        vms.append({"uuid": uuid, "state": state, "name": name})

    return vms


# ---------------------------------------------------------
# Parse "utmctl status <uuid>" to extract IP
# ---------------------------------------------------------
def utm_status(uuid):
    output = run_cmd([utmctl, "status", uuid])

    ip = None
    state = None

    for line in output.splitlines():
        line = line.strip()

        if line.startswith("State:"):
            state = line.split(":", 1)[1].strip()

        # Extract IPv4 address
        m = re.search(r"(\d+\.\d+\.\d+\.\d+)", line)
        if m:
            ip = m.group(1)

    return state, ip


def utm_ips(machine):
    """
    Find the IP address of a UTM virtual machine
    
    Parameters
    ----------
    machine: str
        Can be either the virtual machine name or the uuid

    Returns
    -------
    ips: string
        a string with comma separated ipv4 IP addresses

    Raises
    ------
    ValueError
        If the input data is not a string

    Examples:
    >>> vm = "deb13"
    >>> ips = utm_ip(vm)
    >>> print(ips)
    192.168.2.1, 172.16.2.3

    """
    output = run_cmd([utmctl, "ip-address", machine])
    count = 0 
    ips = ""

    for line in output.splitlines():
        # Pattern matches 0-255 in each of the 4 octets
        ipv4_pattern = r'^(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$'

        if re.fullmatch(ipv4_pattern, line.strip()):
            if count == 0:
                ips = line.strip() + ", "
                count += 1
            else:
                ips = ips + ", " + line.strip

    return ips 



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

    print(f"{'VM Name':25} {'State':15} {'IP Address'}")
    print("-" * 60) 

    for vm in vms:
        uuid = vm["uuid"]
        name = vm["name"]

        # Get detailed status + IP
        ips = utm_ips(uuid)
        state, ip = utm_status(uuid)

        # Fallback to list state if status didn't return one
        state = state or vm["state"]
        ips = ips or "no-ip"

        print(f"{name:25} {state:15} {ips or 'N/A'}")
        # print(f"{name} | {state} | {ips}")


if __name__ == "__main__":
    main()

