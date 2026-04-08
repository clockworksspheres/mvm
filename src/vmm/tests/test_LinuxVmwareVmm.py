import unittest
from unittest.mock import patch, MagicMock
from pathlib import Path
from io import StringIO
import sys


# Helper: deep Path mock
def make_fake_path(path_str):
    p = MagicMock(spec=Path)
    real = Path(path_str)
    p.__str__.return_value = path_str
    p.stem = real.stem
    p.name = real.name
    p.suffix = real.suffix
    p.exists.return_value = True
    return p

@unittest.skipUnless(sys.platform.lower().startswith("linux"), "Needs to run on Linux...")
class TestLinuxVmwareVmm(unittest.TestCase):

    def setUp(self):
        # Patch CyLogger
        self.p_logger = patch("vmm.LinuxVmwareVmm.CyLogger")
        self.mock_CyLogger = self.p_logger.start()

        # Patch RunWith
        self.p_runwith = patch("vmm.LinuxVmwareVmm.RunWith")
        self.mock_RunWith = self.p_runwith.start()

        # Patch tell_hw_platform
        self.p_hw = patch("vmm.LinuxVmwareVmm.tell_hw_platform", return_value="x86_64")
        self.mock_hw = self.p_hw.start()

        # Fake logger instance
        self.fake_logger = MagicMock()
        self.mock_CyLogger.return_value = self.fake_logger

        # Fake RunWith instance
        self.fake_run = MagicMock()
        self.fake_run.communicate.return_value = ("output", "", 0)
        self.mock_RunWith.return_value = self.fake_run

        # Import class under test
        from vmm.LinuxVmwareVmm import LinuxVmwareVmm
        self.LinuxVmwareVmm = LinuxVmwareVmm
        self.vm = LinuxVmwareVmm(self.fake_logger)

    def tearDown(self):
        self.p_logger.stop()
        self.p_runwith.stop()
        self.p_hw.stop()

    # ----------------------------------------------------------------------
    # Constructor
    # ----------------------------------------------------------------------
    def test_constructor_initializes_logger_and_run(self):
        self.mock_CyLogger.assert_called()
        self.mock_RunWith.assert_called()
        self.assertTrue(hasattr(self.vm, "run"))
        self.assertTrue(hasattr(self.vm, "logger"))

    def test_constructor_raises_on_arm64(self):
        with patch("vmm.LinuxVmwareVmm.tell_hw_platform", return_value="arm64"):
            from vmm.LinuxVmwareVmm import LinuxVmwareVmm
            with self.assertRaises(Exception):
                LinuxVmwareVmm(self.fake_logger)

    # ----------------------------------------------------------------------
    # find_vm_by_display_name
    # ----------------------------------------------------------------------
    @patch("vmm.LinuxVmwareVmm.find_vm_by_display_name")
    def test_find_vm_by_display_name(self, mock_find):
        mock_find.return_value = [["/vm/test.vmx"]]
        result = self.vm.find_vm_by_display_name("Ubuntu")
        self.assertEqual(result, "/vm/test.vmx")
        mock_find.assert_called_once_with("Ubuntu")

    # ----------------------------------------------------------------------
    # start_vm
    # ----------------------------------------------------------------------
    @patch("vmm.LinuxVmwareVmm.find_vm_by_display_name")
    def test_start_vm(self, mock_find):
        mock_find.return_value = ["/vm/test.vmx"]

        self.vm.start_vm("testvm", headless=True)

        expected_cmd = ["???", "-T", "fusion", "start", "/vm/test.vmx", "nogui"]
        self.fake_run.setCommand.assert_called_once_with(expected_cmd)
        self.fake_run.communicate.assert_called_once()

    # ----------------------------------------------------------------------
    # stop_vm
    # ----------------------------------------------------------------------
    @patch("vmm.LinuxVmwareVmm.find_vm_by_display_name")
    def test_stop_vm(self, mock_find):
        mock_find.return_value = ["/vm/test.vmx"]

        self.vm.stop_vm("testvm", hard=True)

        expected_cmd = ["???", "stop", "/vm/test.vmx", "hard"]
        self.fake_run.setCommand.assert_called_once_with(expected_cmd)
        self.fake_run.communicate.assert_called_once()

    # ----------------------------------------------------------------------
    # pause_vm / unpause_vm / reset_vm
    # ----------------------------------------------------------------------
    @patch("vmm.LinuxVmwareVmm.find_vm_by_display_name")
    def test_pause_vm(self, mock_find):
        mock_find.return_value = ["/vm/test.vmx"]

        self.vm.pause_vm("testvm")

        expected_cmd = ["???", "pause", "/vm/test.vmx", "soft"]
        self.fake_run.setCommand.assert_called_once_with(expected_cmd)
        self.fake_run.communicate.assert_called_once()

    @patch("vmm.LinuxVmwareVmm.find_vm_by_display_name")
    def test_unpause_vm(self, mock_find):
        mock_find.return_value = ["/vm/test.vmx"]

        self.vm.unpause_vm("testvm")

        expected_cmd = ["???", "unpause", "/vm/test.vmx", "soft"]
        self.fake_run.setCommand.assert_called_once_with(expected_cmd)
        self.fake_run.communicate.assert_called_once()

    @patch("vmm.LinuxVmwareVmm.find_vm_by_display_name")
    def test_reset_vm(self, mock_find):
        mock_find.return_value = ["/vm/test.vmx"]

        self.vm.reset_vm("testvm", hard=False)

        expected_cmd = ["???", "reset", "/vm/test.vmx", "soft"]
        self.fake_run.setCommand.assert_called_once_with(expected_cmd)
        self.fake_run.communicate.assert_called_once()

    # ----------------------------------------------------------------------
    # get_ip
    # ----------------------------------------------------------------------
    @patch("vmm.LinuxVmwareVmm.find_vm_by_display_name")
    def test_get_ip(self, mock_find):
        mock_find.return_value = ["/vm/test.vmx"]
        self.fake_run.communicate.return_value = ("192.168.1.50", "", 0)

        result = self.vm.get_ip("testvm")

        expected_cmd = ["???", "getGuestIPAddress", "/vm/test.vmx", "-wait"]
        self.fake_run.setCommand.assert_called_once_with(expected_cmd)
        self.assertEqual(result, "192.168.1.50")

    # ----------------------------------------------------------------------
    # get_vm_status — FULL COVERAGE
    # ----------------------------------------------------------------------
    @patch("vmm.LinuxVmwareVmm.get_vm_ip")
    @patch("vmm.LinuxVmwareVmm.detect_vm_status")
    @patch("vmm.LinuxVmwareVmm.list_running_vms")
    @patch("vmm.LinuxVmwareVmm.find_all_vmx_files")
    def test_get_vm_status(self, mock_find, mock_running, mock_status, mock_ip):
        fake_paths = [
            make_fake_path("/vms/Ubuntu.vmx"),
            make_fake_path("/vms/CentOS.vmx"),
        ]

        mock_find.return_value = fake_paths
        mock_running.return_value = {"Ubuntu"}
        mock_status.side_effect = ["running", "stopped"]
        mock_ip.return_value = "10.0.0.55"

        captured = StringIO()
        old_stdout = sys.stdout
        sys.stdout = captured
        try:
            self.vm.get_vm_status("ignored")
        finally:
            sys.stdout = old_stdout

        output = captured.getvalue()

        self.assertIn("VM Name", output)
        self.assertIn("State", output)
        self.assertIn("IP Address", output)

        self.assertIn("Ubuntu", output)
        self.assertIn("running", output)
        self.assertIn("10.0.0.55", output)

        self.assertIn("CentOS", output)
        self.assertIn("stopped", output)
        self.assertIn("N/A", output)

        mock_find.assert_called_once()
        mock_running.assert_called_once()
        self.assertEqual(mock_status.call_count, 2)
        mock_ip.assert_called_once_with("/vms/Ubuntu.vmx")


if __name__ == "__main__":
    unittest.main()

