
import os
import sys
import json
from pathlib import Path

from mvm.lib.loggers import CyLogger
from mvm.lib.loggers import LogPriority as lp
from mvm.lib.run_commands import RunWith
from mvm.ManageVirtualMachinesTemplate import ManageVirtualMachinesTemplate
from mvm.lib.vmx import find_vm_by_display_name

from mvm.lib.vmware_list_status import (find_all_vmx_files,
                                        detect_vm_status,
                                        get_vm_ip,
                                        print_status4all_vms,
                                        list_running_vms)


class WindowsVmwareMvm(ManageVirtualMachinesTemplate):

    def __init__(self, logger, **kwargs):
        if isinstance(logger, CyLogger):
            self.logger = CyLogger()
        else:
            self.logger = CyLogger()
            self.logger.initializeLogs()

       #  self.logger.log(lp.INFO, f"Initializing {self.__class__.__name__} class")

        self.run = RunWith(self.logger)

        self.vmrun = r"C:\\Program Files (x86)\\VMware\\VMware Workstation\\vmrun.exe"

        self.userhome = ""
        if sys.platform.lower().startswith("win"):
            self.userhome = os.environ.get('USERPROFILE')

    def find_vm_by_display_name(self, vmname=""):
        """
        Find the first VM with vmname in the list of paths the searched.
        """
        vmpath = ""
        vmpaths = find_vm_by_display_name(vmname)
        for vmpath in vmpaths:
            print("Found:", vmpath)
            # return the first found in the search
            break

        return vmpath[0]

    def list_vms_json(self, **kwargs):
        """
        List available VMs 
        """
        # print("Got into macosVmwareMvm list method...")
        vmx_files = find_all_vmx_files(self.userhome + "\Documents\Virtual Machines")
        # print(f"{vmx_files}")

        running_set = list_running_vms()
        ip = ""
        json_table = {}
        i = 0
        for vmx in vmx_files:
            name = vmx.stem
            status = detect_vm_status(str(vmx), running_set)

            if status == 'suspended':
                status = 'paused'

            ip = get_vm_ip(str(vmx)) if status == "running" else 'N/A'

            json_table[i] = {}
            json_table[i]["name"] = name
            json_table[i]["status"] = status
            json_table[i]["ip"] = ip or 'N/A'

            i = i + 1

        print(json.dumps(json_table, indent=2))
        return json_table

    def list_vms_table(self, **kwargs):
        """
        List available VMs 
        """
        # print("Got into macosVmwareMvm list method...")
        vmx_files = find_all_vmx_files(self.userhome + "\Documents\Virtual Machines")
        # print(f"{vmx_files}")

        running_set = list_running_vms()

        print(f"{'VM Name':30} {'State':15} {'IP Address'}")
        print("-" * 60)
        table = f"{'VM Name':30} {'State':15} {'IP Address'}\n"
        table = table + ("-" * 60)

        for vmx in vmx_files:
            name = vmx.stem
            status = detect_vm_status(str(vmx), running_set)

            if status == 'suspended':
                status = 'paused'

            ip = get_vm_ip(str(vmx)) if status == "running" else None

            print(f"{name:30} {status:12} {ip or 'N/A'}")
            table = table + f"\n{name:30} {status:12} {ip or 'N/A'}"

        return table

    def list_vms(self):
        return self.list_vms_table()

    def start_vm(self, vm: str = "", headless: bool = False):
        """
         Start a virtual machine

        """
        vmpath = find_vm_by_display_name(f"{vm}")[0]
        print(vmpath)
        cmd = [self.vmrun, "-T", "ws", "start", vmpath, "nogui" if headless else "gui"]
        self.run.setCommand(cmd)
        self.run.communicate()

    def stop_vm(self, vm: str = "", hard: bool = False):
        """
         Stop a virtual machine
        """
        vmpath = find_vm_by_display_name(f"{vm}")[0]
        print(vmpath)
        cmd = [self.vmrun, "stop", vmpath, "hard" if hard else "soft"]
        self.run.setCommand(cmd)
        self.run.communicate()

    def pause_vm(self, vm: str = ""):
        """
        Suspend a virtual machine
        """
        vmpath = find_vm_by_display_name(f"{vm}")[0]
        print(vmpath)
        cmd = [self.vmrun, "pause", vmpath]
        self.run.setCommand(cmd)
        self.run.communicate()

    def unpause_vm(self, vm: str = ""):
        """
        Suspend a virtual machine
        """
        vmpath = find_vm_by_display_name(f"{vm}")[0]
        print(vmpath)
        cmd = [self.vmrun, "unpause", vmpath]
        self.run.setCommand(cmd)
        self.run.communicate()

    def reset_vm(self, vm: str = "", hard: bool = False):
        """
        Reset a virtual machine 
        """
        vmpath = find_vm_by_display_name(f"{vm}")[0]
        print(vmpath)
        cmd = [self.vmrun, "reset", vmpath, "hard" if hard else "soft"]
        self.run.setCommand(cmd)
        self.run.communicate()

    def get_vm_status(self, vm: str, quiet: bool=False):
        """
        Get the status of a virtual machine
        """
        vmState=""
        myvm = self.find_vm_by_display_name(vm)
        if myvm:
            status = detect_vm_status(str(myvm))
            if status == 'suspended':
                status = 'paused'

            #ip = get_vm_ip(str(myvm)) if status == "running" else "N/A"
            #####
            # vmState may include the IP in the future - {name, status, ip}
            vmState = status
            if not quiet:
                print(f"{vmState}")
        else:
            vmState = "<< VM does not exist >>"
        return vmState

    def get_vm_status_json(self, vm: str=""):
        state = self.get_vm_status_json(vm, True)
        return {'state': state}

    def get_ip(self, vm: str = ""):
        """
        get the IP address of a virtual machine 
        """
        vmpath = find_vm_by_display_name(f"{vm}")[0]
        print(vmpath)
        cmd = [self.vmrun, "getGuestIPAddress", vmpath, "-wait"]
        self.run.setCommand(cmd)
        out, _, _ = self.run.communicate()
        print(f"{out.strip()}")
        return out.strip()

