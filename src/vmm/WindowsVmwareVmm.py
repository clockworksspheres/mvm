import inspect
from vmm.lib.loggers import CyLogger
from vmm.lib.loggers import LogPriority as lp
from vmm.lib.run_commands import RunWith
from vmm.VirtualMachineManageTemplate import VirtualMachineManageTemplate


class WindowsVmwareVmm(VirtualMachineManageTemplate):

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

        self.vmrun = r"C:\Program Files (x86)\VMware\VMware Workstation\vmrun.exe"

    def list_vms(self):
        """
        List available VMs 
        """
        cmd = [self.vmrun, "list"]
        self.run.setCommand(cmd)
        self.run.communicate()

    def start_vm(self, vm: str = "", headless: bool = False):
        """
         Start a virtual machine

        """
        cmd = [self.vmrun, "-T", "ws", "start", vm, "nogui" if headless else "gui"]
        self.run.setCommand(cmd)
        self.run.communicate()

    def stop_vm(self, vm: str = "", hard: bool = False):
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
        cmd = [self.vmrun, "pause", vm]
        self.run.setCommand(cmd)
        self.run.communicate()

    def unpause_vm(self, vm: str = ""):
        """
        Suspend a virtual machine
        """
        cmd = [self.vmrun, "unpause", vm]
        self.run.setCommand(cmd)
        self.run.communicate()

    def reset_vm(self, vm: str = "", hard: bool = False):
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
        cmd = [self.vmrun, "list"]
        self.run.setCommand(cmd)
        out, err, retval = self.run.communicate()
        print(f"{out.strip()}")
        return out.strip()

    def get_ip(self, vm: str = ""):
        """
        get the IP address of a virtual machine 
        """
        cmd = [self.vmrun, "getGuestIPAddress", vm, "-wait"]
        self.run.setCommand(cmd)
        out, err, retval = self.run.communicate()
        print(f"{out.strip()}")
        return out.strip()

