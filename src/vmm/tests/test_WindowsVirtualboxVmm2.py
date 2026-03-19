import sys
import unittest
from unittest.mock import patch, MagicMock
from pathlib import Path

# Add parent directory to sys.path
parent_dir = Path(__file__).parent.parent
sys.path.append(str(parent_dir))

VBM = "C:\\Program Files\\Oracle\\VirtualBox\\VBoxManage.exe"

@unittest.skipUnless(
    sys.platform.lower().startswith("win32"),
    "WindowsVirtualboxVmm tests only run on Windows (win32)"
)
class TestWindowsVirtualboxVmm(unittest.TestCase):

    def setUp(self):
        from vmm.WindowsVirtualboxVmm import WindowsVirtualboxVmm

        # Dummy logger
        class DummyLogger:
            def initializeLogs(self): pass
            def log(self, *args, **kwargs): pass

        self.logger = DummyLogger()
        self.vmm = WindowsVirtualboxVmm(self.logger)

        # Patch the run object on the instance
        self.run_patch = patch.object(self.vmm, "run", MagicMock())
        self.mock_run = self.run_patch.start()

        # Provide MagicMock methods
        self.mock_run.setCommand = MagicMock()
        self.mock_run.communicate = MagicMock()

        self.mock_run.communicate = MagicMock(return_value=("", "", 0))

    def tearDown(self):
        self.run_patch.stop()

    def test_list_vms_sets_correct_command(self):
        self.vmm.list_vms()
        self.mock_run.setCommand.assert_called_once_with(
            [VBM, "list", "vms"]
        )

    def test_start_vm_sets_correct_command(self):
        self.vmm.start_vm("TestVM")
        self.mock_run.setCommand.assert_called_once_with(
            [VBM, "startvm", "TestVM"]
        )

    def test_stop_vm_sets_correct_command(self):
        self.vmm.stop_vm("vmStop", hard=True)
        self.mock_run.setCommand.assert_called_once_with(
            [VBM, "controlvm", "vmStop", "poweroff"]
        )

    def test_pause_vm_sets_correct_command(self):
        self.vmm.pause_vm("vmP")
        self.mock_run.setCommand.assert_called_once_with(
            [VBM, "controlvm", "vmP", "savestate"]
        )

    def test_unpause_vm_sets_correct_command(self):
        self.vmm.unpause_vm("vmU")
        self.mock_run.setCommand.assert_called_once_with(
            [VBM, "controlvm", "vmU", "resume"]
        )

    def test_reset_vm_sets_correct_command(self):
        self.vmm.reset_vm("vmR", hard=True)
        self.mock_run.setCommand.assert_called_once_with(
            [VBM, "controlvm", "vmR", "reset"]
        )

    def test_get_vm_status_returns_stripped_output(self):
        self.mock_run.communicate.return_value = (" running \n", "", 0)
        status = self.vmm.get_vm_status("vmS")

        self.mock_run.setCommand.assert_called_once_with(
            [VBM, "showvminfo", "vmS"]
        )
        self.assertEqual(status, "running")

    def test_get_ip_returns_stripped_output(self):
        self.mock_run.communicate.return_value = (" 10.0.2.15 \n", "", 0)
        ip = self.vmm.get_ip("vmIP")

        self.mock_run.setCommand.assert_called_once_with(
            [
                VBM, "guestproperty", "get", "vmIP",
                "/VirtualBox/GuestInfo/Net/0/IP"
            ]
        )
        self.assertEqual(ip, "10.0.2.15")


if __name__ == "__main__":
    unittest.main()

