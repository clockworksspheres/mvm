import os
import glob

def find_vm_by_display_name(target_name):
    # VMware Fusion default VM directories
    search_dirs = [
        os.path.expanduser("~/Virtual Machines.localized"),
        os.path.expanduser("~/Virtual Machines"),
        os.path.expanduser("~/Documents/Virtual Machines.localized"),
        os.path.expanduser("~/Documents/Virtual Machines"),
    ]

    matches = []

    for base in search_dirs:
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


# Example:
results = find_vm_by_display_name("deb13")

for r in results:
    print("Found:", r)

