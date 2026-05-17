
from vmm.lib.loggers import CyLogger
from vmm.lib.loggers import LogPriority as lp
from vmm.lib.run_commands import RunWith
from vmm.VirtualMachineManageTemplate import VirtualMachineManageTemplate
from vmm.lib.vmx import find_vm_by_display_name


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
        vmpath = find_vm_by_display_name(f"{vm}")[0]
        print(vmpath)
        cmd = [self.vmrun, "getGuestIPAddress", vmpath, "-wait"]
        self.run.setCommand(cmd)
        out, err, retval = self.run.communicate()
        print(f"{out.strip()}")
        return out.strip()

