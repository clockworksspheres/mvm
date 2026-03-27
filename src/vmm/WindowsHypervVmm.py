import inspect
from vmm.lib.loggers import CyLogger
from vmm.lib.loggers import LogPriority as lp
from vmm.lib.run_commands import RunWith
from vmm.VirtualMachineManageTemplate import VirtualMachineManageTemplate


class WindowsHypervVmm(VirtualMachineManageTemplate):

    PS_PREFIX = ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command"]

    def __init__(self, logger, **kwargs):
        """
        """
        if isinstance(logger, CyLogger):
            self.logger = CyLogger()
        else:
            self.logger = CyLogger()
            self.logger.initializeLogs()

        self.logger.log(lp.ERROR, f"Initializing {self.__class__.__name__} class")

        # self.run = RunWith(self.logger)

        self.utmctl = "utmctl"

    def run(self, cmd: list, check=True, capture_output=False, text=True, shell=False):
        try:
            result = subprocess.run(
                cmd,
                check=check,
                capture_output=capture_output,
                text=text,
                encoding="utf-8" if text else None,
                shell=shell
            )   
            return result
        except subprocess.CalledProcessError as e:
            print(f"Command failed: {' '.join(cmd)}", file=sys.stderr)
            if e.stderr:
                print(e.stderr.strip(), file=sys.stderr)
            sys.exit(1)
        except FileNotFoundError:
            print(f"Command not found: {cmd[0]}", file=sys.stderr)
            sys.exit(1)

    def run_powershell(self, script: str, capture_output=False):
        """Run inline PowerShell script"""
        cmd = self.PS_PREFIX + [script]
        return self.run(cmd, capture_output=capture_output, shell=False)


    def list_vms(self):
        """
        List available VMs 
        """
        self.run_powershell("Get-VM | Select-Object Name, State, Status | Format-Table -AutoSize")

    def start_vm(self, vm: str = "", headless: bool = False):
        """
         Start a virtual machine

        """
        self.run_powershell(f"Start-VM -Name '{vm}'")

    def stop_vm(self, vm: str = "", hard: bool = True):
        """
         Stop a virtual machine
        """
        self.run_powershell(f"Stop-VM -Name '{vm}' -Force")

    def pause_vm(self, vm: str = ""):
        """
        Suspend a virtual machine
        """
        self.run_powershell(f"Suspend-VM -Name '{vm}'")

    def unpause_vm(self, vm: str = ""):
        """
        Suspend a virtual machine
        """
        self.run_powershell(f"Resume-VM -Name '{vm}'")

    def reset_vm(self, vm: str = "", hard: bool = True):
        """
        Reset a virtual machine 
        """
        self.run_powershell(f"Restart-VM -Name '{vm}' -Force")

    def get_vm_status(self, vm: str):
        """
        Get the status of a virtual machine 
        """
        self.run_powershell(
            f"Get-VM -Name '{vm}' | "
            "Select-Object Name, State, Status, Uptime | "
            "Format-List"
        )

    def get_ip(self, vm: str = ""):
        """
        get the IP address of a virtual machine 
        """
        self.run_powershell(
            f"$vm = Get-VM -Name '{vm}'; "
            "$vm | Get-VMNetworkAdapter | "
            "ForEach-Object { "
            "  $_.IpAddresses | Where-Object { $_ -match '^\\d{1,3}\\.\\d{1,3}\\.\\d{1,3}\\.\\d{1,3}$' } "
            "} | Select-Object -First 1"
        )

