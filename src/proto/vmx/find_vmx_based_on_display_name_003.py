import os
import glob
import sys

def get_default_vm_paths():
    system = sys.platform

    if system.lower().startswith("darwin"):  # macOS (VMware Fusion)
        return [
            os.path.expanduser("~/Virtual Machines.localized"),
            os.path.expanduser("~/Virtual Machines"),
            os.path.expanduser("~/Documents/Virtual Machines.localized"),
            os.path.expanduser("~/Documents/Virtual Machines"),
        ]

    elif system.lower().startswith("win"):  # VMware Workstation
        return [
            os.path.expanduser("~/Documents/Virtual Machines"),
            os.path.expanduser("~/Virtual Machines"),
        ]

    elif system.lower().startswith("linux"):  # Linux (VMware Workstation)
        return [
            os.path.expanduser("~/vmware"),
            "/var/lib/vmware/Virtual Machines",
            "/var/lib/vmware",
        ]
    else:
        return [""]


def find_vm_by_display_name(target_name, extra_paths=None):
    search_paths = get_default_vm_paths()

    if extra_paths:
        search_paths.extend(extra_paths)

    matches = []

    for base in search_paths:
        if not os.path.exists(base):
            continue

        # Find all .vmx files recursively
        vmx_files = glob.glob(os.path.join(base, "**", "*.vmx"), recursive=True)

        for vmx in vmx_files:
            try:
                with open(vmx, "r", encoding="utf-8", errors="ignore") as f:
                    for line in f:
                        if line.strip().startswith("displayName"):
                            name = line.split("=", 1)[1].strip().strip('"')
                            if name.lower() == target_name.lower():
                                matches.append(vmx)
            except Exception:
                pass

    return matches


# Example usage:
results = find_vm_by_display_name("deb13")

for r in results:
    print("Found:", r)

