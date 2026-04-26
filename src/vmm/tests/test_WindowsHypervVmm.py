import subprocess
import unittest
from unittest.mock import patch, MagicMock
import sys

from pathlib import Path

# Get the parent directory of the current file's parent directory
#  and add it to sys.path
parent_dir = Path(__file__).parent.parent
sys.path.append(str(parent_dir))


# Import the class under test
from WindowsHypervVmm import WindowsHypervVmm

# Helper dummy logger
class DummyLogger:
    def initializeLogs(self): pass
    def log(self, *args, **kwargs): pass


@unittest.skipUnless(sys.platform.lower().startswith("win"), "Only test on Windows")
class TestWindowsHypervVmm(unittest.TestCase):
    def setUp(self):
        self.logger = DummyLogger()
        self.vmm = WindowsHypervVmm(self.logger)

    @patch('WindowsHypervVmm.WindowsHypervVmm.run')
    def test_run_success(self, mock_run):
        """run() should call run with given command."""
        mock_run.return_value = subprocess.CompletedProcess(args=['foo'], returncode=0)
        # result = self.vmm.run(['foo'], check=True, capture_output=False, text=True, encoding='utf-8', shell=False)
        result = self.vmm.run(['foo'], check=True, capture_output=False, text=True, shell=False)

        mock_run.assert_called_once_with(
            ['foo'], check=True, capture_output=False, text=True,
            encoding='utf-8', shell=False
        )
        self.assertEqual(result.returncode, 0)

    @patch('WindowsHypervVmm.WindowsHypervVmm.run')
    def test_run_powershell_builds_cmd(self, mock_run):
        """run_powershell should prepend PS_PREFIX and call run()."""
        # Assume PS_PREFIX defined like: ["powershell", "-Command"]
        with patch('WindowsHypervVmm.WindowsHypervVmm.PS_PREFIX', ["powershell", "-Command"]):
            self.vmm.run_powershell("Get-VM")

        expected_cmd = ["powershell", "-Command", "Get-VM"]
        mock_run.assert_called_once()
        args, kwargs = mock_run.call_args
        self.assertEqual(args[0], expected_cmd)

    @patch('WindowsHypervVmm.WindowsHypervVmm.run')
    def test_list_vms(self, mock_run):
        self.vmm.list_vms()
        mock_run.assert_called_once()

    @patch('WindowsHypervVmm.WindowsHypervVmm.run')
    def test_start_vm(self, mock_run):
        self.vmm.start_vm("testvm")
        mock_run.assert_called_once()

    @patch('WindowsHypervVmm.WindowsHypervVmm.run')
    def test_stop_vm(self, mock_run):
        self.vmm.stop_vm("testvm")
        mock_run.assert_called_once()

    @patch('WindowsHypervVmm.WindowsHypervVmm.run')
    def test_pause_unpause_vm(self, mock_run):
        self.vmm.pause_vm("testvm")
        self.vmm.unpause_vm("testvm")
        self.assertEqual(mock_run.call_count, 2)

    @patch('WindowsHypervVmm.WindowsHypervVmm.run')
    def test_reset_vm(self, mock_run):
        self.vmm.reset_vm("testvm")
        mock_run.assert_called_once()

    @patch('WindowsHypervVmm.WindowsHypervVmm.run')
    def test_get_vm_status(self, mock_run):
        self.vmm.get_vm_status("testvm")
        mock_run.assert_called_once()

    @patch('WindowsHypervVmm.WindowsHypervVmm.run')
    def test_get_ip(self, mock_run):
        self.vmm.get_ip("testvm")
        mock_run.assert_called_once()

if __name__ == "__main__":
    unittest.main()

