import psutil
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from ManageVirtualMachines import ManageVirtualMachines
from lib.libHelperExceptions import HypervisorNotApplicable, HypervisorNotAvailableError

hypervisorMap = {"vmware": "VMware Fusion", "virtualbox": "VirtualBox", "utm": "UTM"}

if sys.platform.lower().startswith("win"):
    hypervisorMap = {"vmware": "VMware Fusion", "virtualbox": "VBoxSDS.exe", "hyperv": "vmms.exe"}



class HypervisorNotValid(BaseException):
    """
    Custom Exception
    """
    def __init__(self, *args, **kwargs):
        BaseException.__init__(self, *args, **kwargs)


def mvm_run(args):
    hyper = args.hypervisor
    vm = args.vm

    matched = None

    hypervisorApp = hypervisorMap[args.hypervisor.strip()]

    for proc in psutil.process_iter(['pid', 'name']):
        #if re.match(re.escape(hypervisor), proc.info['name']):
        if hypervisorApp == proc.info['name'].strip():
            print(f"{proc.info['name']}")
            matched = proc.info['name']

    if not matched:
        message = f"Hypervisor {hypervisorApp} not running, start {hypervisorApp} first"
        print(message)
        raise HypervisorNotAvailableError(message)

    try:
        mvm = ManageVirtualMachines(hyper)
    except HypervisorNotApplicable:
        print("Cannot run this hypervisor on this OS setup")
        sys.exit()

    cmd = args.command

    if args.command == "list":
        # print("Got a list action")
        mvm.list_vms()

    elif cmd == "start":
        mvm.start_vm(vm, headless=args.headless)
        print(f"Started {hyper} → {vm}")

    elif cmd == "stop":
        mvm.stop_vm(vm)
        print(f"Stopped {hyper} → {vm}")

    elif cmd == "pause":
        mvm.pause_vm(vm)
        print(f"Suspended {hyper} → {vm}")

    elif cmd == "unpause":
        mvm.unpause_vm(vm)
        print(f"Suspended {hyper} → {vm}")

    elif cmd == "reset":
        mvm.reset_vm(vm, hard=args.hard)
        print(f"Reset {hyper} → {vm}")

    elif cmd == "status":
        mvm.list_vms()

    elif cmd == "ip":
        mvm.get_ip(vm)


