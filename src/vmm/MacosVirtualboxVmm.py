import inspect
from lib.loggers import CyLogger
from lib.loggers import LogPriority as lp
from lib.run_commands import RunWith
from VirtualMachineManageTemplate import VirtualMachineManageTemplate
from lib.mac_virtualbox_list_status import (list_vms,
                                            list_running_vms,
                                            get_vm_state,
                                            get_vm_ip)

class MacosVirtualboxVmm(VirtualMachineManageTemplate):

    def __init__(self, logger, **kwargs):
        """
        """
        if isinstance(logger, CyLogger):
            self.logger = CyLogger()
        else:
            self.logger = CyLogger()
            self.logger.initializeLogs()

        # self.logger.log(lp.ERROR, f"Initializing {self.__class__.__name__} class")

        self.run = RunWith(self.logger)

        self.vboxmanage = "/usr/local/bin/VBoxManage"

    def list_vms(self):
        """
        List available VMs 
        """

        vms = list_vms()
        running = list_running_vms()

        print(f"{'VM Name':25} {'State':15} {'IP Address'}")
        print("-" * 60) 

        for name, uuid in vms.items():
            state = get_vm_state(uuid)

            if state == "running":
                ip = get_vm_ip(uuid)
            else:
                ip = None

            print(f"{name:25} {state:15} {ip or 'N/A'}")
        return name, state, ip     


    def start_vm(self, vm: str = "", headless: bool = False):
        """
         Start a virtual machine

        """
        cmd = [self.vboxmanage, "startvm", vm]
        self.run.setCommand(cmd)
        self.run.communicate()

    def stop_vm(self, vm: str = "", hard: bool = True):
        """
         Stop a virtual machine
        """
        # cmd = [self.vboxmanage, "controlvm", vm, "acpipowerbutton"]
        cmd = [self.vboxmanage, "controlvm", vm, "poweroff"]
        self.run.setCommand(cmd)
        self.run.communicate()

    def pause_vm(self, vm: str = ""):
        """
        Suspend a virtual machine
        """
        cmd = [self.vboxmanage, "controlvm", vm, "savestate"]
        self.run.setCommand(cmd)
        self.run.communicate()

    def unpause_vm(self, vm: str = ""):
        """
        Suspend a virtual machine
        """
        cmd = [self.vboxmanage, "controlvm", vm, "resume"]
        self.run.setCommand(cmd)
        self.run.communicate()

    def reset_vm(self, vm: str = "", hard: bool = True):
        """
        Reset a virtual machine 
        """
        cmd1 = [self.vboxmanage, "controlvm", vm, "reset"]
        self.run.setCommand(cmd1)
        self.run.communicate()
        cmd2 = [self.vboxmanage, "start", vm]
        self.run.setCommand(cmd2)
        self.run.communicate()

    def get_vm_status(self, vm: str):
        """
        Get the status of a virtual machine 
        """
        name, state, ip = self.list_vms()
        return name, state, ip

    def get_ip(self, vm: str = ""):
        """
        get the IP address of a virtual machine 
        """
        cmd = [self.vboxmanage, "guestproperty", "get", vm, "/VirtuallBox/GuestInfo/Net/0/IP"]
        self.run.setCommand(cmd)
        out, err, retval = self.run.communicate()
        print(f"{out.strip()}")
        return out.strip()

