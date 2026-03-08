import subprocess
import json
import argparse

def utm_list():
    result = subprocess.run(
        ["utmctl", "list", "--json"],
        capture_output=True,
        text=True
    )
    result.check_returncode()
    return json.loads(result.stdout)

def utm_status(name):
    result = subprocess.run(
        ["utmctl", "status", name, "--json"],
        capture_output=True,
        text=True
    )
    result.check_returncode()
    return json.loads(result.stdout)

def get_ip(status):
    for iface in status.get("network", []):
        if "ipv4" in iface:
            return iface["ipv4"]
    return None

def main():
    parser = argparse.ArgumentParser(description="List UTM VM status")
    parser.add_argument("-a", "--all", action="store_true",
                        help="Show all VMs (default)")
    args = parser.parse_args()

    vms = utm_list()

    for vm in vms:
        name = vm["name"]
        status = utm_status(name)
        state = status.get("state", "unknown")
        ip = get_ip(status) or "no-ip"

        # ONE LINE OUTPUT
        print(f"{name} | {state} | {ip}")

if __name__ == "__main__":
    main()

