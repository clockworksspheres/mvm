import psutil
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from VirtualMachineManage import VirtualMachineManage
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


def vmm_run(args):
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
        vmm = VirtualMachineManage(hyper)
    except HypervisorNotApplicable:
        print("Cannot run this hypervisor on this OS setup")
        sys.exit()

    cmd = args.command

    if args.command == "list":
        # print("Got a list action")
        vmm.list_vms()

    elif cmd == "start":
        vmm.start_vm(vm, headless=args.headless)
        print(f"Started {hyper} → {vm}")

    elif cmd == "stop":
        vmm.stop_vm(vm)
        print(f"Stopped {hyper} → {vm}")

    elif cmd == "pause":
        vmm.pause_vm(vm)
        print(f"Suspended {hyper} → {vm}")

    elif cmd == "unpause":
        vmm.unpause_vm(vm)
        print(f"Suspended {hyper} → {vm}")

    elif cmd == "reset":
        vmm.reset_vm(vm, hard=args.hard)
        print(f"Reset {hyper} → {vm}")

    elif cmd == "status":
        vmm.list_vms()

    elif cmd == "ip":
        vmm.get_ip(vm)


