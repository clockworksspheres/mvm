import unittest
from unittest.mock import patch, MagicMock, mock_open
from pathlib import Path

import subprocess

# Import the module under test
import vmm.lib.vmware_list_status as vm   # <-- replace with actual filename


class TestVmFunctions(unittest.TestCase):

    @patch("vmm.lib.vmware_list_status.subprocess.check_output")
    def test_run_vmrun_success(self, mock_co):
        mock_co.return_value = b"VM1\nVM2\n"
        out = vm.run_vmrun(["vmrun", "list"])
        self.assertEqual(out, "VM1\nVM2")
        mock_co.assert_called_once()

    @patch("vmm.lib.vmware_list_status.subprocess.check_output", side_effect=subprocess.CalledProcessError(1, "cmd", output=b"Error happened"))
    def test_run_vmrun_failure(self, mock_co):
        out = vm.run_vmrun(["vmrun", "list"])
        self.assertEqual(out, "Error happened")

    @patch("vmm.lib.vmware_list_status.run_vmrun")
    def test_list_running_vms(self, mock_run):
        mock_run.return_value = "/path/a.vmx\n/path/b.vmx\nnot_a_vmx\n"
        result = vm.list_running_vms()
        self.assertEqual(result, {"/path/a.vmx", "/path/b.vmx"})

    @patch("vmm.lib.vmware_list_status.RunWith")
    def test_get_vm_ip_success(self, mock_rw_cls):
        mock_rw = MagicMock()
        mock_rw.runCommand2check.return_value = (0, "192.168.1.10")
        mock_rw_cls.return_value = mock_rw

        ip = vm.get_vm_ip("/path/test.vmx")
        self.assertEqual(ip, "192.168.1.10")

        mock_rw.setCommand.assert_called_once()
        mock_rw.runCommand2check.assert_called_once()

    @patch("vmm.lib.vmware_list_status.RunWith")
    def test_get_vm_ip_error(self, mock_rw_cls):
        mock_rw = MagicMock()
        mock_rw.runCommand2check.return_value = (1, "Error: something bad")
        mock_rw_cls.return_value = mock_rw

        ip = vm.get_vm_ip("/path/test.vmx")
        self.assertIsNone(ip)

    @patch("vmm.lib.vmware_list_status.Path")
    def test_detect_vm_status_running(self, mock_path_cls):
        running = {"/vms/test.vmx"}

        mock_path = MagicMock()
        mock_path.parent.iterdir.return_value = []
        mock_path_cls.return_value = mock_path
        mock_path_cls.return_value.__str__.return_value = "/vms/test.vmx"

        status = vm.detect_vm_status("/vms/test.vmx", running)
        self.assertEqual(status, "running")

    @patch("vmm.lib.vmware_list_status.Path")
    def test_detect_vm_status_suspended(self, mock_path_cls):
        mock_file = MagicMock()
        mock_file.suffix = ".vmss"

        mock_path = MagicMock()
        mock_path.parent.iterdir.return_value = [mock_file]
        mock_path_cls.return_value = mock_path

        status = vm.detect_vm_status("/vms/test.vmx", set())
        self.assertEqual(status, "suspended")

    @patch("vmm.lib.vmware_list_status.Path")
    def test_detect_vm_status_off(self, mock_path_cls):
        mock_path = MagicMock()
        mock_path.parent.iterdir.return_value = []
        mock_path_cls.return_value = mock_path

        status = vm.detect_vm_status("/vms/test.vmx", set())
        self.assertEqual(status, "off")

    @patch("vmm.lib.vmware_list_status.Path.rglob")
    def test_find_all_vmx_files(self, mock_rglob):
        mock_rglob.return_value = [Path("/a.vmx"), Path("/b.vmx")]
        result = vm.find_all_vmx_files("/root")
        self.assertEqual(result, [Path("/a.vmx"), Path("/b.vmx")])

    @patch("vmm.lib.vmware_list_status.print")
    @patch("vmm.lib.vmware_list_status.get_vm_ip")
    @patch("vmm.lib.vmware_list_status.detect_vm_status")
    @patch("vmm.lib.vmware_list_status.find_all_vmx_files")
    @patch("vmm.lib.vmware_list_status.list_running_vms")
    def test_print_status4all_vms(
        self, mock_running, mock_find, mock_status, mock_ip, mock_print
    ):
        mock_running.return_value = {"/vms/a.vmx"}
        mock_find.return_value = [Path("/vms/a.vmx"), Path("/vms/b.vmx")]
        mock_status.side_effect = ["running", "off"]
        mock_ip.return_value = "10.0.0.5"

        vm.print_status4all_vms(None)

        self.assertTrue(mock_print.called)
        mock_ip.assert_called_once_with("/vms/a.vmx")
