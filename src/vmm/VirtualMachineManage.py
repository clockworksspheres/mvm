"""
Factory Class to spawn concrete Virtual Machine Managers
(vmm), based on the passed in "framework"
"""
import inspect
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from vmm.lib.loggers import CyLogger
from vmm.lib.loggers import LogPriority as lp
from vmm.lib.run_commands import RunWith
from vmm.lib.libHelperExceptions import HypervisorNotApplicable
from vmm.VirtualMachineManageTemplate import VirtualMachineManageTemplate

class VirtualMachineManage(VirtualMachineManageTemplate):

    def __init__(self, framework, **kwargs):
        """
        """
        self.logger = CyLogger()
        self.logger.initializeLogs()

        #self.logger.log(lp.ERROR, f"Initializing {self.__class__.__name__} class")

        self.run = RunWith(self.logger)

        self.framework = framework

        if self.framework == "vmware":
            if sys.platform.lower().startswith("darwin"):
                from MacosVmwareVmm import MacosVmwareVmm
                self.vmm = MacosVmwareVmm(self.logger)
            elif sys.platform.lower().startswith("win32"):
                from lib.windows_utilities import hyper_v_enabled
                if hyper_v_enabled():
                    raise HypervisorNotApplicable
                else:
                    from WindowsVmwareVmm import WindowsVmwareVmm
                    self.vmm = WindowsVmwareVmm(self.logger)
        elif self.framework == "virtualbox":
            if sys.platform.lower().startswith("darwin"):
                from MacosVirtualboxVmm import MacosVirtualboxVmm
                self.vmm = MacosVirtualboxVmm(self.logger)
            elif sys.platform.lower().startswith("win32"):
                from lib.windows_utilities import hyper_v_enabled
                if hyper_v_enabled():
                    raise HypervisorNotApplicable
                else:
                    from WindowsVirtualboxVmm import WindowsVirtualboxVmm
                    self.vmm = WindowsVirtualboxVmm(self.logger)
            elif sys.platform.lower().startswith("linux"):
                from LinuxVirtualboxVmm import LinuxVirtualboxVmm
                self.vmm = LinuxVirtualboxVmm(self.logger)
        elif self.framework == "utm" and sys.platform.lower().startswith("darwin"):
            from MacosUtmVmm import MacosUtmVmm
            self.vmm = MacosUtmVmm(self.logger)
        elif self.framework == "hyperv" and sys.platform.lower().startswith("win32"):
            from lib.windows_utilities import hyper_v_enabled
            if not hyper_v_enabled():
                raise HypervisorNotApplicable("Hyperv isn't applicable...")
            else:
                from WindowsHypervVmm import WindowsHypervVmm
                self.vmm = WindowsHypervVmm(self.logger)
        else:
            self.logger.log(lp.ERROR, f"{self.framework} hasn't been implemented")

    def list_vms(self, **kwargs):
        """
        List available VMs      
        """
        self.vmm.list_vms(**kwargs)

    def start_vm(self, vm: str = "", headless: bool = False, **kwargs):
        """
         Start a virtual machine
        """
        self.vmm.start_vm(vm, **kwargs)

    def stop_vm(self, vm: str = "", hard: bool = True, **kwargs):
        """
         Stop a virtual machine
        """
        self.vmm.stop_vm(vm, **kwargs)

    def pause_vm(self, vm: str = "", **kwargs):
        """
        Suspend a VM
        """
        self.vmm.pause_vm(vm, **kwargs)

    def unpause_vm(self, vm: str = "", **kwargs):
        """
        Suspend a VM
        """
        self.vmm.unpause_vm(vm, **kwargs)

    def reset_vm(self, vm: str = "", hard: bool = True, **kwargs):
        """
        Reset a VM
        """
        self.vmm.reset_vm(vm, hard, **kwargs)

    def get_vm_status(self, vm: str):
        """
        Get the status of a VM
        """
        self.vmm.get_vm_status()

    def get_ip(self, vm: str = "", **kwargs):
        """
        Get the IP of a VM 
        """
        ip =  self.vmm.get_ip(vm, **kwargs)
        #print(f"{ip}")
        return ip
