import sys
import inspect
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from vmm.lib.loggers import CyLogger
from vmm.lib.loggers import LogPriority as lp
from vmm.lib.run_commands import RunWith
from vmm.VirtualMachineManageTemplate import VirtualMachineManageTemplate
from vmm.lib.vmware_fusion_list_status import (find_all_vmx_files,
                                               detect_vm_status,
                                               get_vm_ip,
                                               print_status4all_vms,
                                               list_running_vms)


class MacosVmwareVmm(VirtualMachineManageTemplate):

    def __init__(self, logger, **kwargs):
        """
        """
        if isinstance(logger, CyLogger):
            self.logger = CyLogger()
        else:
            self.logger = CyLogger()
            self.logger.initializeLogs()

       #  self.logger.log(lp.INFO, f"Initializing {self.__class__.__name__} class")

        self.run = RunWith(self.logger)

        self.vmrun = "/Applications/VMware Fusion.app/Contents/Library/vmrun"

    def list_vms(self, **kwargs):
        """
        List available VMs 
        """
        # print("Got into macosVmwareVmm list method...")
        vmx_files = find_all_vmx_files("/Users/victor/Virtual Machines.localized")
        # print(f"{vmx_files}")

        running_set = list_running_vms()
        print_status4all_vms(vmx_files)
        """
        for vmx in vmx_files:
            name = vmx.stem
            status = detect_vm_status(str(vmx), running_set)
            ip = get_vm_ip(str(vmx)) if status == "running" else None

            print(f"{name:25} {status:12} {ip or 'N/A'}")
        ""
        cmd = [self.vmrun, "list"]
        self.run.setCommand(cmd)
        output, _, _ = self.run.communicate()
        print(f"{output}")
        """

    def start_vm(self, vm: str = "", headless: bool = False):
        """
         Start a virtual machine

        """
        cmd = [self.vmrun, "-T", "fusion", "start", vm, "nogui" if headless else "gui"]
        self.run.setCommand(cmd)
        self.run.communicate()

    def stop_vm(self, vm: str = "", hard: bool = True):
        """
         Stop a virtual machine
        """
        cmd = [self.vmrun, "stop", vm, "hard" if hard else "soft"]
        self.run.setCommand(cmd)
        self.run.communicate()

    def pause_vm(self, vm: str = ""):
        """
        Suspend a virtual machine
        """
        cmd = [self.vmrun, "pause", vm, "soft"]
        self.run.setCommand(cmd)
        self.run.communicate()

    def unpause_vm(self, vm: str = ""):
        """
        Suspend a virtual machine
        """
        cmd = [self.vmrun, "unpause", vm, "soft"]
        self.run.setCommand(cmd)
        self.run.communicate()

    def reset_vm(self, vm: str = "", hard: bool = True):
        """
        Reset a virtual machine 
        """
        cmd = [self.vmrun, "reset", vm, "hard" if hard else "soft"]
        self.run.setCommand(cmd)
        self.run.communicate()

    def get_vm_status(self, vm: str):
        """
        Get the status of a virtual machine 
        """
        # print("Got into macosVmwareVmm list method...")
        vmx_files = find_all_vmx_files("/Users/victor/Virtual Machines.localized")
        # print(f"{vmx_files}")

        #running_set = list_running_vms()

        print(f"{'VM Name':30} {'State':15} {'IP Address'}")
        print("-" * 60) 

        for vmx in vmx_files:
            name = vmx.stem
            status = detect_vm_status(str(vmx), running_set)
            ip = get_vm_ip(str(vmx)) if status == "running" else None

            print(f"{name:30} {status:12} {ip or 'N/A'}")
        """
        cmd = [self.vmrun, "list", vm]
        self.run.setCommand(cmd)
        out, err, retval = self.run.communicate()
        print(f"{out.strip()}")
        return out.strip()
        """

    def get_ip(self, vm: str = ""):
        """
        get the IP address of a virtual machine 
        """
        cmd = [self.vmrun, "getGuestIPAddress", vm, "-wait"]
        self.run.setCommand(cmd)
        out, err, retval = self.run.communicate()
        print(f"{out.strip()}")
        return out.strip()

