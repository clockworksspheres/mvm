import unittest
from unittest.mock import patch, MagicMock
import sys

from pathlib import Path

# Get the parent directory of the current file's parent directory
#  and add it to sys.path
parent_dir = Path(__file__).parent.parent
sys.path.append(str(parent_dir))

from VirtualMachineManage import VirtualMachineManage


class TestVirtualMachineManage(unittest.TestCase):

    # ----------------------------------------------------------------------
    # VMware on macOS
    # ----------------------------------------------------------------------
    @patch("MacosVmwareVmm.MacosVmwareVmm")
    @patch("VirtualMachineManage.RunWith")
    @patch("VirtualMachineManage.CyLogger")
    def test_vmware_macos(self, mock_logger, mock_runwith, mock_vmware):
        with patch.object(sys, "platform", "darwin"):
            vmm = VirtualMachineManage("vmware")

        mock_vmware.assert_called_once_with(mock_logger.return_value)
        self.assertIs(vmm.vmm, mock_vmware.return_value)

    # ----------------------------------------------------------------------
    # VMware on Windows
    # ---------------------------------------------------------------------
    @unittest.skipUnless(sys.platform.lower().startswith("win"), "Only test on Windows")
    @patch("WindowsVmwareVmm.WindowsVmwareVmm")
    @patch("VirtualMachineManage.RunWith")
    @patch("VirtualMachineManage.CyLogger")
    def test_vmware_windows(self, mock_logger, mock_runwith, mock_vmware):
        with patch.object(sys, "platform", "win32"):
            vmm = VirtualMachineManage("vmware")

        mock_vmware.assert_called_once_with(mock_logger.return_value)
        self.assertIs(vmm.vmm, mock_vmware.return_value)

    # ----------------------------------------------------------------------
    # VirtualBox on macOS
    # ----------------------------------------------------------------------
    @patch("MacosVirtualboxVmm.MacosVirtualboxVmm")
    @patch("VirtualMachineManage.RunWith")
    @patch("VirtualMachineManage.CyLogger")
    def test_virtualbox_macos(self, mock_logger, mock_runwith, mock_vbox):
        with patch.object(sys, "platform", "darwin"):
            vmm = VirtualMachineManage("virtualbox")

        mock_vbox.assert_called_once_with(mock_logger.return_value)
        self.assertIs(vmm.vmm, mock_vbox.return_value)

    # ----------------------------------------------------------------------
    # VirtualBox on Windows
    # ----------------------------------------------------------------------
    @unittest.skipUnless(sys.platform.lower().startswith("win"), "Only test on Windows")
    @patch("WindowsVirtualboxVmm.WindowsVirtualboxVmm")
    @patch("VirtualMachineManage.RunWith")
    @patch("VirtualMachineManage.CyLogger")
    def test_virtualbox_windows(self, mock_logger, mock_runwith, mock_vbox):
        with patch.object(sys, "platform", "win32"):
            vmm = VirtualMachineManage("virtualbox")

        mock_vbox.assert_called_once_with(mock_logger.return_value)
        self.assertIs(vmm.vmm, mock_vbox.return_value)

    # ----------------------------------------------------------------------
    # UTM on macOS
    # ----------------------------------------------------------------------
    @patch("MacosUtmVmm.MacosUtmVmm")
    @patch("VirtualMachineManage.RunWith")
    @patch("VirtualMachineManage.CyLogger")
    def test_utm_macos(self, mock_logger, mock_runwith, mock_utm):
        with patch.object(sys, "platform", "darwin"):
            vmm = VirtualMachineManage("utm")

        mock_utm.assert_called_once_with(mock_logger.return_value)
        self.assertIs(vmm.vmm, mock_utm.return_value)

    # ----------------------------------------------------------------------
    # Hyper-V on Windows
    # ----------------------------------------------------------------------
    @unittest.skipUnless(sys.platform.lower().startswith("win"), "Only test on Windows")
    @patch("WindowsHypervVmm.WindowsHypervVmm")
    @patch("VirtualMachineManage.RunWith")
    @patch("VirtualMachineManage.CyLogger")
    def test_hyperv_windows(self, mock_logger, mock_runwith, mock_hyperv):
        with patch.object(sys, "platform", "win32"):
            vmm = VirtualMachineManage("hyperv")

        mock_hyperv.assert_called_once_with(mock_logger.return_value)
        self.assertIs(vmm.vmm, mock_hyperv.return_value)

    # ----------------------------------------------------------------------
    # Unsupported framework logs error
    # ----------------------------------------------------------------------
    @patch("VirtualMachineManage.CyLogger")
    @patch("VirtualMachineManage.RunWith")
    def test_unsupported_framework(self, mock_runwith, mock_logger):
        logger_instance = mock_logger.return_value

        with patch.object(sys, "platform", "darwin"):
            VirtualMachineManage("unknown")

        logger_instance.log.assert_called_once()

    # ----------------------------------------------------------------------
    # Wrapper methods forward correctly
    # ----------------------------------------------------------------------
    @patch("VirtualMachineManage.CyLogger")
    @patch("VirtualMachineManage.RunWith")
    def test_wrapper_methods(self, mock_runwith, mock_logger):
        fake_vmm = MagicMock()

        with patch.object(sys, "platform", "darwin"):
            vmm = VirtualMachineManage("utm")
            vmm.vmm = fake_vmm  # override actual implementation

        vmm.list_vms()
        fake_vmm.list_vms.assert_called_once()

        vmm.start_vm("VM1")
        fake_vmm.start_vm.assert_called_once_with("VM1")

        vmm.stop_vm("VM1")
        fake_vmm.stop_vm.assert_called_once_with("VM1")

        vmm.pause_vm("VM1")
        fake_vmm.pause_vm.assert_called_once_with("VM1")

        vmm.unpause_vm("VM1")
        fake_vmm.unpause_vm.assert_called_once_with("VM1")

        vmm.reset_vm("VM1", hard=True)
        fake_vmm.reset_vm.assert_called_once_with("VM1", True)

        vmm.get_ip("VM1")
        fake_vmm.get_ip.assert_called_once_with("VM1")


if __name__ == "__main__":
    unittest.main()

