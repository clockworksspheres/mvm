import sys
import unittest

from pathlib import Path

# Get the parent directory of the current file's parent directory
#  and add it to sys.path
parent_dir = Path(__file__).parent.parent
sys.path.append(str(parent_dir))

VBM = "C:\\Program Files\\Oracle\\VirtualBox\\VBoxManage.exe"

@unittest.skipUnless(
    sys.platform.lower().startswith("win32"),
    "WindowsVirtualboxMvm tests only run on Windows (win32)"
)
class TestWindowsVirtualboxMvm(unittest.TestCase):

    from mvm.WindowsVirtualboxMvm import WindowsVirtualboxMvm

    class FakeRunWith:
        """Fake runner capturing commands instead of executing them."""
        def __init__(self, logger):
            self.logger = logger
            self.last_command = None
            self.responses = {}

        def setCommand(self, cmd):
            self.last_command = list(cmd)

        def communicate(self):
            key = tuple(self.last_command)
            return self.responses.get(key, ("", "", 0))

    class DummyLogger:
        def initializeLogs(self):
            pass
        def log(self, *args, **kwargs):
            pass

    def setUp(self):
        self.logger = self.DummyLogger()
        self.mvm = self.WindowsVirtualboxMvm(self.logger)
        self.mvm.run = self.FakeRunWith(self.logger)

    def test_list_vms_sets_correct_command(self):
        self.mvm.list_vms()
        self.assertEqual(
            self.mvm.run.last_command,
            [VBM, "list", "vms"]
        )

    def test_start_vm_sets_correct_command(self):
        self.mvm.start_vm("TestVM")
        self.assertEqual(
            self.mvm.run.last_command,
            [VBM, "startvm", "TestVM"]
        )

    def test_stop_vm_sets_correct_command(self):
        self.mvm.stop_vm("vmStop", hard=True)
        # On Windows, closing VM might use "controlvm <name> poweroff"
        self.assertEqual(
            self.mvm.run.last_command,
            [VBM, "controlvm", "vmStop", "poweroff"]
        )

    def test_pause_vm_sets_correct_command(self):
        self.mvm.pause_vm("vmP")
        self.assertEqual(
            self.mvm.run.last_command,
            [VBM, "controlvm", "vmP", "savestate"]
        )

    def test_unpause_vm_sets_correct_command(self):
        self.mvm.unpause_vm("vmU")
        self.assertEqual(
            self.mvm.run.last_command,
            [VBM, "controlvm", "vmU", "resume"]
        )

    def test_reset_vm_sets_correct_command(self):
        self.mvm.reset_vm("vmR", hard=True)
        # VirtualBox reset usually maps to controlvm reset (hard)
        self.assertEqual(
            self.mvm.run.last_command,
            [VBM, "controlvm", "vmR", "reset"]
        )

    def test_get_vm_status_returns_stripped_output(self):
        key = (VBM, "showvminfo", "vmS")
        self.mvm.run.responses[key] = (" running \n", "", 0)
        status = self.mvm.get_vm_status("vmS")
        self.assertEqual(status, "running")

    def test_get_ip_returns_stripped_output(self):
        key = (
            VBM, "guestproperty", "get", "vmIP",
            "/VirtualBox/GuestInfo/Net/0/IP"
        )
        self.mvm.run.responses[key] = (" 10.0.2.15 \n", "", 0)
        ip = self.mvm.get_ip("vmIP")
        self.assertEqual(ip, "10.0.2.15")


if __name__ == "__main__":
    unittest.main()

