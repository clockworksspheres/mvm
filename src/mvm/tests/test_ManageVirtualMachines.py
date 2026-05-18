import unittest
from unittest.mock import patch, MagicMock
import sys

from pathlib import Path

# Get the parent directory of the current file's parent directory
#  and add it to sys.path
parent_dir = Path(__file__).parent.parent
sys.path.append(str(parent_dir))

from mvm.ManageVirtualMachines import ManageVirtualMachines


hyper_v_enabled = None
if sys.platform.lower().startswith("win"):
    from mvm.lib.windows_utilities import hyper_v_enabled

from mvm.lib.libHelperExceptions import HypervisorNotApplicable


@unittest.skipUnless(sys.platform.lower().startswith("win"), "Only test on Windows")
class TestManageVirtualMachines(unittest.TestCase):

    if sys.platform.lower().startswith("win"):
        from mvm.lib.windows_utilities import hyper_v_enabled

    # ----------------------------------------------------------------------
    # VMware on macOS
    # ----------------------------------------------------------------------
    @patch("MacosVmwareMvm.MacosVmwareMvm")
    @patch("ManageVirtualMachines.CyLogger")
    def test_vmware_macos(self, mock_logger, mock_vmware):
        with patch.object(sys, "platform", "darwin"):
            mvm = ManageVirtualMachines("vmware")

        mock_vmware.assert_called_once_with(mock_logger.return_value)
        self.assertIs(mvm.mvm, mock_vmware.return_value)

    # ----------------------------------------------------------------------
    # VMware on Windows
    # ---------------------------------------------------------------------
    @patch("WindowsVmwareMvm.WindowsVmwareMvm")
    @patch("ManageVirtualMachines.CyLogger")
    @unittest.skipUnless(sys.platform.lower().startswith("win"), "Only test on Windows")
    def test_vmware_windows(self, mock_logger, mock_vmware):

        if hyper_v_enabled():
            unittest.SkipTest
        else:
            with patch.object(sys, "platform", "win32"):
                mvm = ManageVirtualMachines("vmware")

            mock_vmware.assert_called_once_with(mock_logger.return_value)
            self.assertIs(mvm.mvm, mock_vmware.return_value)

    # ----------------------------------------------------------------------
    # VirtualBox on macOS
    # ----------------------------------------------------------------------
    @patch("MacosVirtualboxMvm.MacosVirtualboxMvm")
    @patch("ManageVirtualMachines.CyLogger")
    def test_virtualbox_macos(self, mock_logger, mock_vbox):
        with patch.object(sys, "platform", "darwin"):
            mvm = ManageVirtualMachines("virtualbox")

        mock_vbox.assert_called_once_with(mock_logger.return_value)
        self.assertIs(mvm.mvm, mock_vbox.return_value)

    # ----------------------------------------------------------------------
    # VirtualBox on Windows
    # ----------------------------------------------------------------------
    @unittest.skipUnless(sys.platform.lower().startswith("win"), "Only test on Windows")
    @patch("WindowsVirtualboxMvm.WindowsVirtualboxMvm")
    @patch("ManageVirtualMachines.CyLogger")
    def test_virtualbox_windows(self, mock_logger, mock_vbox):
        if hyper_v_enabled():
            unittest.SkipTest
        else:
            with patch.object(sys, "platform", "win32"):
                mvm = ManageVirtualMachines("virtualbox")

            mock_vbox.assert_called_once_with(mock_logger.return_value)
            self.assertIs(mvm.mvm, mock_vbox.return_value)

    # ----------------------------------------------------------------------
    # UTM on macOS
    # ----------------------------------------------------------------------
    @patch("MacosUtmMvm.MacosUtmMvm")
    @patch("ManageVirtualMachines.CyLogger")
    def test_utm_macos(self, mock_logger, mock_utm):
        with patch.object(sys, "platform", "darwin"):
            mvm = ManageVirtualMachines("utm")

        mock_utm.assert_called_once_with(mock_logger.return_value)
        self.assertIs(mvm.mvm, mock_utm.return_value)

    # ----------------------------------------------------------------------
    # Hyper-V on Windows
    # ----------------------------------------------------------------------
    @unittest.skipUnless(sys.platform.lower().startswith("win"), "Only test on Windows")
    @patch("mvm.WindowsHypervMvm.WindowsHypervMvm")
    @patch("mvm.ManageVirtualMachines.CyLogger")
    def test_hyperv_windows(self, mock_logger, mock_hyperv):
        if not hyper_v_enabled():
            unittest.SkipTest
        else:
            with patch.object(sys, "platform", "win32"):
                mvm = ManageVirtualMachines("hyperv")

            mock_hyperv.assert_called_once_with(mock_logger.return_value)
            self.assertIs(mvm.mvm, mock_hyperv.return_value)

    # ----------------------------------------------------------------------
    # Unsupported framework logs error
    # ----------------------------------------------------------------------
    @patch("ManageVirtualMachines.CyLogger")
    def test_unsupported_framework(self, mock_logger):
        logger_instance = mock_logger.return_value

        with patch.object(sys, "platform", "darwin"):
            ManageVirtualMachines("unknown")

        logger_instance.log.assert_called_once()

    # ----------------------------------------------------------------------
    # Wrapper methods forward correctly
    # ----------------------------------------------------------------------
    @patch("mvm.ManageVirtualMachines.CyLogger")
    def test_wrapper_methods(self, mock_logger):
        fake_mvm = MagicMock()

        with patch.object(sys, "platform", "darwin"):
            mvm = ManageVirtualMachines("utm")
            mvm.mvm = fake_mvm  # override actual implementation

        mvm.list_vms()
        fake_mvm.list_vms.assert_called_once()

        mvm.start_vm("VM1")
        fake_mvm.start_vm.assert_called_once_with("VM1")

        mvm.stop_vm("VM1")
        fake_mvm.stop_vm.assert_called_once_with("VM1")

        mvm.pause_vm("VM1")
        fake_mvm.pause_vm.assert_called_once_with("VM1")

        mvm.unpause_vm("VM1")
        fake_mvm.unpause_vm.assert_called_once_with("VM1")

        mvm.reset_vm("VM1", hard=True)
        fake_mvm.reset_vm.assert_called_once_with("VM1", True)

        mvm.get_ip("VM1")
        fake_mvm.get_ip.assert_called_once_with("VM1")


if __name__ == "__main__":
    unittest.main()

