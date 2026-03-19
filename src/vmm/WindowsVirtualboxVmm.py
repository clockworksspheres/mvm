import inspect
from lib.loggers import CyLogger
from lib.loggers import LogPriority as lp
from lib.run_commands import RunWith
from VirtualMachineManageTemplate import VirtualMachineManageTemplate


class WindowsVirtualboxVmm(VirtualMachineManageTemplate):

    def __init__(self, logger, **kwargs):
        """
        """
        if isinstance(logger, CyLogger):
            self.logger = CyLogger()
        else:
            self.logger = CyLogger()
            self.logger.initializeLogs()

        self.logger.log(lp.ERROR, f"Initializing {self.__class__.__name__} class")

        self.run = RunWith(self.logger)

        self.vboxmanage = "C:\\Program Files\\Oracle\\VirtualBox\\VBoxManage.exe"

    def list_vms(self):
        """
        List available VMs 
        """
        cmd = [self.vboxmanage, "list", "vms"]
        self.run.setCommand(cmd)
        out, _, _ = self.run.communicate()
        print(f"{out}")

    def start_vm(self, vm: str = "", headless: bool = False):
        """
         Start a virtual machine
        """
        cmd = [self.vboxmanage, "startvm", vm]
        if headless:
            cmd += ["--type", "headless"]
        self.run.setCommand(cmd)
        self.run.communicate()

    def stop_vm(self, vm: str = "", hard: bool = True):
        """
         Stop a virtual machine
        """
        cmd = [self.vboxmanage, "controlvm", vm, "poweroff" if hard else "acpipowerbutton"]
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
        # cmd2 = [self.vboxmanage, "start", vm]
        # self.run.setCommand(cmd2)
        # self.run.communicate()

    def get_vm_status(self, vm: str):
        """
        Get the status of a virtual machine 
        """
        cmd = [self.vboxmanage, "showvminfo", vm]
        self.run.setCommand(cmd)
        out, err, retval = self.run.communicate()
        print(f"{out.strip()}")
        return out.strip()

    def get_ip(self, vm: str = ""):
        """
        get the IP address of a virtual machine 
        """
        cmd = [self.vboxmanage, "guestproperty", "get", vm, "/VirtualBox/GuestInfo/Net/0/IP"]
        self.run.setCommand(cmd)
        out, err, retval = self.run.communicate()
        print(f"{out.strip()}")
        return out.strip()

