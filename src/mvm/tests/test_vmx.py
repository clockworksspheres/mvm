import unittest
from unittest.mock import patch, MagicMock, mock_open
import os

# Import your module under test
import vmm.lib.vmx as vm   # <-- rename to your actual filename


class TestVMPathFunctions(unittest.TestCase):

    # ---------------------------------------------------------
    # get_default_vm_paths()
    # ---------------------------------------------------------
    @patch("vmm.lib.vmx.sys.platform", "darwin")
    @patch("vmm.lib.vmx.os.path.expanduser", side_effect=lambda p: p.replace("~", "/Users/test"))
    def test_get_default_vm_paths_mac(self, mock_expand):
        paths = vm.get_default_vm_paths()
        self.assertEqual(paths, [
            "/Users/test/Virtual Machines.localized",
            "/Users/test/Virtual Machines",
            "/Users/test/Documents/Virtual Machines.localized",
            "/Users/test/Documents/Virtual Machines",
        ])

    @patch("vmm.lib.vmx.sys.platform", "win32")
    @patch("vmm.lib.vmx.os.path.expanduser", side_effect=lambda p: p.replace("~", "C:/Users/test"))
    def test_get_default_vm_paths_windows(self, mock_expand):
        paths = vm.get_default_vm_paths()
        self.assertEqual(paths, [
            "C:/Users/test/Documents/Virtual Machines",
            "C:/Users/test/Virtual Machines",
        ])

    @patch("vmm.lib.vmx.sys.platform", "linux")
    @patch("vmm.lib.vmx.os.path.expanduser", side_effect=lambda p: p.replace("~", "/home/test"))
    def test_get_default_vm_paths_linux(self, mock_expand):
        paths = vm.get_default_vm_paths()
        self.assertEqual(paths, [
            "/home/test/vmware",
            "/var/lib/vmware/Virtual Machines",
            "/var/lib/vmware",
        ])

    @patch("vmm.lib.vmx.sys.platform", "unknownos")
    def test_get_default_vm_paths_other(self):
        paths = vm.get_default_vm_paths()
        self.assertEqual(paths, [""])

    # ---------------------------------------------------------
    # find_vm_by_display_name()
    # ---------------------------------------------------------
    @patch("vmm.lib.vmx.get_default_vm_paths", return_value=["/vms"])
    @patch("vmm.lib.vmx.os.path.exists", return_value=True)
    @patch("vmm.lib.vmx.glob.glob")
    @patch("vmm.lib.vmx.open", new_callable=mock_open, read_data='displayName = "Ubuntu"\n')
    def test_find_vm_by_display_name_match(self, mock_file, mock_glob, mock_exists, mock_paths):
        mock_glob.return_value = ["/vms/ubuntu/Ubuntu.vmx"]

        matches = vm.find_vm_by_display_name("Ubuntu")

        self.assertEqual(matches, ["/vms/ubuntu/Ubuntu.vmx"])
        mock_file.assert_called_once()

    @patch("vmm.lib.vmx.get_default_vm_paths", return_value=["/vms"])
    @patch("vmm.lib.vmx.os.path.exists", return_value=True)
    @patch("vmm.lib.vmx.glob.glob")
    @patch("vmm.lib.vmx.open", new_callable=mock_open, read_data='displayName = "Windows 11"\n')
    def test_find_vm_by_display_name_case_insensitive(
        self, mock_file, mock_glob, mock_exists, mock_paths
    ):
        mock_glob.return_value = ["/vms/win11/Win11.vmx"]

        matches = vm.find_vm_by_display_name("windows 11")

        self.assertEqual(matches, ["/vms/win11/Win11.vmx"])
        mock_file.assert_called_once()

    @patch("vmm.lib.vmx.os.path.exists")
    @patch("vmm.lib.vmx.glob.glob")
    @patch("vmm.lib.vmx.open", new_callable=mock_open, read_data='displayName = "Fedora"\n')
    def test_find_vm_by_display_name_no_match(self, mock_file, mock_glob, mock_exists):
        mock_exists.return_value = True
        mock_glob.return_value = ["/vms/fedora/Fedora.vmx"]

        matches = vm.find_vm_by_display_name("Ubuntu")

        self.assertEqual(matches, [])

    @patch("vmm.lib.vmx.os.path.exists", return_value=False)
    def test_find_vm_by_display_name_no_paths_exist(self, mock_exists):
        matches = vm.find_vm_by_display_name("Ubuntu")
        self.assertEqual(matches, [])

    @patch("vmm.lib.vmx.os.path.exists", return_value=True)
    @patch("vmm.lib.vmx.glob.glob", return_value=["/vms/bad/bad.vmx"])
    @patch("vmm.lib.vmx.open", side_effect=Exception("read error"))
    def test_find_vm_by_display_name_file_error(self, mock_file, mock_glob, mock_exists):
        matches = vm.find_vm_by_display_name("Ubuntu")
        self.assertEqual(matches, [])  # errors are swallowed


if __name__ == "__main__":
    unittest.main()
