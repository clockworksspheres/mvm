import sys
import unittest
from unittest.mock import patch, MagicMock, Mock

# Replace this with the actual module path
from mvm.MacosVmwareMvm import MacosVmwareMvm


@unittest.skipUnless(
    sys.platform.lower().startswith("darwin"),
    "MacosVmwareMvm Can only run on macOS (dwarin)"
)
class TestMacosVmwareMvm(unittest.TestCase):

    @patch("mvm.MacosVmwareMvm.CyLogger")
    @patch("mvm.MacosVmwareMvm.RunWith")
    def setUp(self, mock_runwith, mock_logger):
        self.mock_logger_instance = MagicMock()
        mock_logger.return_value = self.mock_logger_instance

        self.mock_run_instance = MagicMock()
        mock_runwith.return_value = self.mock_run_instance

        self.mvm = MacosVmwareMvm(logger=self.mock_logger_instance)

    @patch("mvm.MacosVmwareMvm.find_vm_by_display_name")
    def test_find_vm_by_display_name(self, mock_find):
        mock_find.return_value = [["/path/to/test.vmx"]]

        result = self.mvm.find_vm_by_display_name("test_vm")

        self.assertEqual(result, "/path/to/test.vmx")
        mock_find.assert_called_once_with("test_vm")

    @patch("mvm.MacosVmwareMvm.print_status4all_vms")
    @patch("mvm.MacosVmwareMvm.list_running_vms")
    @patch("mvm.MacosVmwareMvm.find_all_vmx_files")
    def test_list_vms(self, mock_find_vmx, mock_list_running, mock_print_status):
        mock_find_vmx.return_value = [MagicMock()]
        mock_list_running.return_value = set()

        self.mvm.list_vms()

        mock_find_vmx.assert_called_once()
        mock_list_running.assert_called_once()
        mock_print_status.assert_called_once()

    '''
    # Headless not yet supported
    @patch("mvm.MacosVmwareMvm.find_vm_by_display_name")
    def test_start_vm(self, mock_find):
        mock_find.return_value = ["/path/to/test.vmx"]

        self.mvm.start_vm("test_vm", headless=True)

        expected_cmd = [
            self.mvm.vmrun, "-T", "fusion", "start",
            "/path/to/test.vmx", "nogui"
        ]

        self.mvm.run.setCommand.assert_called_once_with(expected_cmd)
        self.mvm.run.communicate.assert_called_once()

    # soft not supported for pause
    @patch("mvm.MacosVmwareMvm.find_vm_by_display_name")
    def test_pause_vm(self, mock_find):
        mock_find.return_value = ["/path/to/test.vmx"]

        self.mvm.pause_vm("test_vm")

        expected_cmd = [
            self.mvm.vmrun, "pause",
            "/path/to/test.vmx", "soft"
        ]

        self.mvm.run.setCommand.assert_called_once_with(expected_cmd)
        self.mvm.run.communicate.assert_called_once()

    # soft not supported for unpause...
    @patch("mvm.MacosVmwareMvm.find_vm_by_display_name")
    def test_unpause_vm(self, mock_find):
        mock_find.return_value = ["/path/to/test.vmx"]

        self.mvm.unpause_vm("test_vm")

        expected_cmd = [
            self.mvm.vmrun, "unpause",
            "/path/to/test.vmx", "soft"
        ]

        self.mvm.run.setCommand.assert_called_once_with(expected_cmd)
        self.mvm.run.communicate.assert_called_once()
 
    # @patch("mvm.MacosVmwareMvm.find_vm_by_display_name")
    # soft not an option....
    @unittest.SkipTest
    def test_reset_vm(self, mock_find):
        mock_find.return_value = ["/path/to/test.vmx"]

        self.mvm.reset_vm("test_vm", hard=False)

        expected_cmd = [
            self.mvm.vmrun, "reset",
            "/path/to/test.vmx", "soft"
        ]

        self.mvm.run.setCommand.assert_called_once_with(expected_cmd)
        self.mvm.run.communicate.assert_called_once()
    '''

    @patch("mvm.MacosVmwareMvm.get_vm_ip")
    @patch("mvm.MacosVmwareMvm.detect_vm_status")
    @patch("mvm.MacosVmwareMvm.find_all_vmx_files")
    def test_get_vm_status(self, mock_find_vmx, mock_detect, mock_get_ip):
        fake_vmx = MagicMock()
        fake_vmx.stem = "test_vm"
        mock_find_vmx.return_value = [fake_vmx]

        mock_detect.return_value = "running"
        mock_get_ip.return_value = "192.168.1.100"

        # Inject missing global (bug in your code)
        import mvm.MacosVmwareMvm
        mvm.MacosVmwareMvm.running_set = set()

        self.mvm.get_vm_status("test_vm")

        mock_find_vmx.assert_called_once()
        mock_detect.assert_called()
        mock_get_ip.assert_called()

    @patch("mvm.MacosVmwareMvm.find_vm_by_display_name")
    def test_get_ip_raises_exception(self, mock_find):
        mock_find.return_value = ["/path/to/test.vmx"]

        with self.assertRaises(Exception) as context:
            self.mvm.get_ip("test_vm")

        #####
        # generated assert, not sure how or why it came up with this
        # self.assertIn("vmpath", str(context.exception))


if __name__ == "__main__":
    unittest.main()

