import inspect
import re

from mvm.lib.loggers import CyLogger
from mvm.lib.loggers import LogPriority as lp
from mvm.lib.run_commands import RunWith
from mvm.ManageVirtualMachinesTemplate import ManageVirtualMachinesTemplate
from mvm.lib.mac_utm_list_status import (utm_list,
                                     utm_status,
                                    )

class MacosUtmMvm(ManageVirtualMachinesTemplate):

    def __init__(self, logger, **kwargs):
        """
        """
        if isinstance(logger, type(CyLogger)):
            self.logger = logger
        else:
            self.logger = CyLogger()
            self.logger.initializeLogs()

        # self.logger.log(lp.ERROR, f"Initializing {self.__class__.__name__} class")

        self.run = RunWith(self.logger)

        self.utmctl = "utmctl"

    def list_vms(self):
        """
        List available VMs 
        """
        vms = utm_list()

        if not vms:
            print("No VMs found or utmctl produced no output.")
            return

        print(f"{'VM Name':25} {'State':15} {'IP Address'}")
        print("-" * 60) 
        #print(f"{vms}\n")

        list_vms_state_dict = {}

        for vm in vms:
            uuid = vm["uuid"]
            name = vm["name"]

            # Get detailed status + IP
            state, ip = utm_status(uuid)

            # Fallback to list state if status didn't return one
            state = state or vm["state"]
            ip = ip or "no-ip"

            list_vms_state_dict[name] = { "state": state, "ip": ip }

            print(f"{name:25} {state:15} {ip or 'N/A'}")
            # print(f"{name} | {state} | {ip}")
        return list_vms_state_dict

    def start_vm(self, vm: str = "", headless: bool = False):
        """
         Start a virtual machine

        """
        cmd = [self.utmctl, "start", vm]
        self.run.setCommand(cmd)
        self.run.communicate()

    def stop_vm(self, vm: str = "", hard: bool = True):
        """
         Stop a virtual machine
        """
        cmd = [self.utmctl, "stop", vm]
        self.run.setCommand(cmd)
        self.run.communicate()

    def pause_vm(self, vm: str = ""):
        """
        Suspend a virtual machine
        """
        cmd = [self.utmctl, "pause", vm]
        self.run.setCommand(cmd)
        self.run.communicate()

    def unpause_vm(self, vm: str = ""):
        """
        Suspend a virtual machine
        """
        cmd = [self.utmctl, "start", vm]
        self.run.setCommand(cmd)
        self.run.communicate()

    def reset_vm(self, vm: str = "", hard: bool = True):
        """
        Reset a virtual machine 
        """
        cmd1 = [self.utmctl, "stop", vm]
        self.run.setCommand(cmd1)
        self.run.communicate()
        cmd2 = [self.utmctl, "start", vm]
        self.run.setCommand(cmd2)
        self.run.communicate()

    def get_vm_status(self, vm: str):
        """
        Get the status of a virtual machine 
        """
        vms = utm_list()

        if not vms:
           print("No VMs found or utmctl produced no output.")
           return

        # print(f"{'VM Name':25} {'State':15} {'IP Address'}")
        # print("-" * 60) 
        # print(f"{vms}\n")

        for machine in vms:
            uuid = machine["uuid"]
            name = machine["name"]

            # Get detailed status + IP
            state, ip = utm_status(uuid)

            # Fallback to list state if status didn't return one
            state = state or machine["state"]
            ip = ip or "no-ip"

            if re.match(name, vm.strip()):
                print(f"{name:25} {state:15} {ip or 'N/A'}")
            # print(f"{name} | {state} | {ip}")
        
    def get_ip(self, vm: str = ""):
        """
        get the IP address of a virtual machine 

        Not supported for macOS vm's, so it's not
        supported for all UTM vms
        """
        message = "Not supported for the UTM hypervisor"
        print(message)
        return message

