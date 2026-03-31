import sys
import inspect
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from vmm.lib.loggers import CyLogger
from vmm.lib.loggers import LogPriority as lp
from vmm.lib.vmx import find_vm_by_display_name
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
        if isinstance(logger, type(CyLogger)):
            self.logger = CyLogger()
        else:
            self.logger = CyLogger()
            self.logger.initializeLogs()

       #  self.logger.log(lp.INFO, f"Initializing {self.__class__.__name__} class")

        self.run = RunWith(self.logger)

        self.vmrun = "/Applications/VMware Fusion.app/Contents/Library/vmrun"

    def find_vm_by_display_name(self, vmname=""):
        """
        Find the first VM with vmname in the list of paths the searched.
        """
        vmpath = ""
        vmpaths = find_vm_by_display_name(vmname)
        print(str(vmpaths))
        for vmpath in vmpaths:
            print("Found:", vmpath)
            # return the first found in the search
            break
        print(str(vmpath))
        return vmpath[0]

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
        vmpath = find_vm_by_display_name(f"{vm}")[0]
        print(vmpath)
        cmd = [self.vmrun, "-T", "fusion", "start", str(vmpath), "nogui" if headless else "gui"]
        self.run.setCommand(cmd)
        self.run.communicate()

    def stop_vm(self, vm: str = "", hard: bool = True):
        """
         Stop a virtual machine
        """
        vmpath = find_vm_by_display_name(f"{vm}")[0]
        cmd = [self.vmrun, "stop", str(vmpath), "hard" if hard else "soft"]
        self.run.setCommand(cmd)
        self.run.communicate()

    def pause_vm(self, vm: str = ""):
        """
        Suspend a virtual machine
        """
        vmpath = find_vm_by_display_name(f"{vm}")[0]
        cmd = [self.vmrun, "pause", str(vmpath), "soft"]
        self.run.setCommand(cmd)
        self.run.communicate()

    def unpause_vm(self, vm: str = ""):
        """
        Suspend a virtual machine
        """
        vmpath = find_vm_by_display_name(f"{vm}")[0]
        cmd = [self.vmrun, "unpause", str(vmpath), "soft"]
        self.run.setCommand(cmd)
        self.run.communicate()

    def reset_vm(self, vm: str = "", hard: bool = True):
        """
        Reset a virtual machine 
        """
        vmpath = find_vm_by_display_name(f"{vm}")[0]
        cmd = [self.vmrun, "reset", str(vmpath), "hard" if hard else "soft"]
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
        vmpath = find_vm_by_display_name(str(vm))
        raise Exception(f"vmpath: {vmpath}")
        cmd = [self.vmrun, "getGuestIPAddress", str(vmpath), "-wait"]
        self.run.setCommand(cmd)
        out, err, retval = self.run.communicate()
        print(f"{out.strip()}")
        return out.strip()

