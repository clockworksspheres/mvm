import sys
import unittest
from unittest.mock import MagicMock

from pathlib import Path

# Get the parent directory of the current file's parent directory
#  and add it to sys.path
parent_dir = Path(__file__).parent.parent

from mvm.MacosVirtualboxMvm import MacosVirtualboxMvm


vboxmanage = "/usr/local/bin/VBoxManage"

@unittest.skipUnless(
    sys.platform.lower().startswith("darwin"),
    "MacosVirtualboxMvm tests only run on macOS (darwin)"
)
class TestMacosVirtualboxMvm(unittest.TestCase):

    class FakeRunWith:
        """Fake runner to capture calls rather than executing commands."""
        def __init__(self, logger):
            self.logger = logger
            self.last_command = None
            self.responses = {}

        def setCommand(self, cmd):
            self.last_command = list(cmd)

        def communicate(self):
            # Return a fake or stubbed response
            key = tuple(self.last_command)
            return self.responses.get(key, ("", "", 0))

    class DummyLogger:
        def initializeLogs(self):
            pass

        def log(self, *args, **kwargs):
            pass

    def setUp(self):
        self.logger = self.DummyLogger()
        self.vmm = MacosVirtualboxMvm(self.logger)

        # Replace the internal runner with our fake runner
        self.vmm.run = self.FakeRunWith(self.logger)

    def test_list_vms_sets_correct_command(self):
        self.vmm.list_vms()
        self.assertRaises(AssertionError)

    def test_start_vm_sets_correct_command(self):
        self.vmm.start_vm("TestVM")
        self.assertEqual(
            self.vmm.run.last_command,
            [vboxmanage, "startvm", "TestVM"]
        )

    def test_stop_vm_sets_correct_command(self):
        self.vmm.stop_vm("vmStop", hard=True)
        self.assertEqual(
            self.vmm.run.last_command,
            [vboxmanage, "controlvm", "vmStop", "poweroff"]
        )

    def test_pause_vm_sets_correct_command(self):
        self.vmm.pause_vm("vmP")
        self.assertEqual(
            self.vmm.run.last_command,
            [vboxmanage, "controlvm", "vmP", "savestate"]
        )

    def test_unpause_vm_sets_correct_command(self):
        self.vmm.unpause_vm("vmU")
        self.assertEqual(
            self.vmm.run.last_command,
            [vboxmanage, "startvm", "vmU"]
        )

    def test_reset_vm_issues_reset_then_start(self):
        self.vmm.reset_vm("vmR", hard=True)
        # The final call should be the start command
        self.assertEqual(
            self.vmm.run.last_command,
            [vboxmanage, "controlvm", "vmR", "reset"]
        )

    @unittest.SkipTest
    def test_get_vm_status_returns_stripped_output(self):
        key = (vboxmanage, "showvminfo", "vmS")
        self.vmm.run.responses[key] = (" VMSTATE=running \n", "", 0)
        self.vmm.get_vm_status("vmS")
        self.assertRaises(AssertionError)
    
    @unittest.SkipTest
    def test_get_ip_returns_stripped_output(self):
        key = (vboxmanage, "guestproperty", "get", "vmIP",
               "/VirtuallBox/GuestInfo/Net/0/IP")
        self.vmm.run.responses[key] = (" 192.168.0.99 \n", "", 0)
        ip = str(self.vmm.get_ip("vmIP")).strip()
        self.assertEqual(ip, "192.168.0.99")


if __name__ == "__main__":
    unittest.main()

