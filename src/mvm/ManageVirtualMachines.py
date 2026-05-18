"""
Factory Class to spawn concrete Virtual Machine Managers
(mvm), based on the passed in "framework"
"""
import inspect
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from mvm.lib.loggers import CyLogger
from mvm.lib.loggers import LogPriority as lp
from mvm.lib.libHelperExceptions import HypervisorNotApplicable
from mvm.ManageVirtualMachinesTemplate import ManageVirtualMachinesTemplate

class ManageVirtualMachines(ManageVirtualMachinesTemplate):

    def __init__(self, framework, **kwargs):
        """
        """
        self.logger = CyLogger()
        self.logger.initializeLogs()

        #self.logger.log(lp.ERROR, f"Initializing {self.__class__.__name__} class")

        self.framework = framework

        if self.framework == "vmware":
            if sys.platform.lower().startswith("darwin"):
                from MacosVmwareMvm import MacosVmwareMvm
                self.mvm = MacosVmwareMvm(self.logger)
            elif sys.platform.lower().startswith("win32"):
                from lib.windows_utilities import hyper_v_enabled
                if hyper_v_enabled():
                    from WindowsVmwareMvm import WindowsVmwareMvm
                    self.mvm = WindowsVmwareMvm(self.logger)
                else:
                    raise HypervisorNotApplicable
        elif self.framework == "virtualbox":
            if sys.platform.lower().startswith("darwin"):
                from MacosVirtualboxMvm import MacosVirtualboxMvm
                self.mvm = MacosVirtualboxMvm(self.logger)
            elif sys.platform.lower().startswith("win32"):
                from lib.windows_utilities import hyper_v_enabled
                if hyper_v_enabled():
                    from WindowsVirtualboxMvm import WindowsVirtualboxMvm
                    self.mvm = WindowsVirtualboxMvm(self.logger)
                else:
                    raise HypervisorNotApplicable
            elif sys.platform.lower().startswith("linux"):
                from LinuxVirtualboxMvm import LinuxVirtualboxMvm
                self.mvm = LinuxVirtualboxMvm(self.logger)
        elif self.framework == "utm" and sys.platform.lower().startswith("darwin"):
            from MacosUtmMvm import MacosUtmMvm
            self.mvm = MacosUtmMvm(self.logger)
        elif self.framework == "hyperv" and sys.platform.lower().startswith("win32"):
            from lib.windows_utilities import hyper_v_enabled
            if not hyper_v_enabled():
                raise HypervisorNotApplicable("Hyperv isn't applicable...")
            else:
                from WindowsHypervMvm import WindowsHypervMvm
                self.mvm = WindowsHypervMvm(self.logger)
        else:
            self.logger.log(lp.ERROR, f"{self.framework} hasn't been implemented")

    def list_vms(self, **kwargs):
        """
        List available VMs      
        """
        self.mvm.list_vms(**kwargs)

    def start_vm(self, vm: str = "", headless: bool = False, **kwargs):
        """
         Start a virtual machine
        """
        self.mvm.start_vm(vm, **kwargs)

    def stop_vm(self, vm: str = "", hard: bool = True, **kwargs):
        """
         Stop a virtual machine
        """
        self.mvm.stop_vm(vm, **kwargs)

    def pause_vm(self, vm: str = "", **kwargs):
        """
        Suspend a VM
        """
        self.mvm.pause_vm(vm, **kwargs)

    def unpause_vm(self, vm: str = "", **kwargs):
        """
        Suspend a VM
        """
        self.mvm.unpause_vm(vm, **kwargs)

    def reset_vm(self, vm: str = "", hard: bool = True, **kwargs):
        """
        Reset a VM
        """
        self.mvm.reset_vm(vm, hard, **kwargs)

    def get_vm_status(self, vm: str):
        """
        Get the status of a VM
        """
        self.mvm.get_vm_status(vm)

    def get_ip(self, vm: str = "", **kwargs):
        """
        Get the IP of a VM 
        """
        ip =  self.mvm.get_ip(vm, **kwargs)
        #print(f"{ip}")
        return ip
