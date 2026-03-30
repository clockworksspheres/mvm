import os
import glob

def find_vm_by_display_name(target_name, search_paths=None):
    """
    Search VMware Fusion/Workstation VMX files for a VM with a matching displayName.
    Returns a list of matching VMX paths.
    """

    # Default search paths for Fusion (macOS) and Workstation (Windows/Linux)
    default_paths = [
        os.path.expanduser("~/Documents/Virtual Machines.localized"),
        os.path.expanduser("~/Documents/Virtual Machines"),
        "C:\\Users\\%USERNAME%\\Documents\\Virtual Machines",
        "/var/lib/vmware/Virtual Machines",
        "/vmfs/volumes",  # ESXi (optional)
    ]

    if search_paths:
        default_paths = search_paths

    matches = []

    for base in default_paths:
        if not os.path.exists(base):
            continue

        # Recursively find all .vmx files
        for vmx in glob.glob(os.path.join(base, "**", "*.vmx"), recursive=True):
            try:
                with open(vmx, "r", encoding="utf-8", errors="ignore") as f:
                    for line in f:
                        if line.strip().startswith("displayName"):
                            # Extract the value inside quotes
                            name = line.split("=", 1)[1].strip().strip('"')
                            if name.lower() == target_name.lower():
                                matches.append(vmx)
            except Exception:
                pass

    return matches


# Example usage:
vm_name = "deb13"
results = find_vm_by_display_name(vm_name)

if results:
    print("Found VM paths:")
    for r in results:
        print("  ", r)
else:
    print("No VM found with that display name.")


