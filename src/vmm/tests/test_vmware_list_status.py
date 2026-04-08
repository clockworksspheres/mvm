import unittest
import sys
from unittest.mock import patch, MagicMock
from pathlib import Path
import subprocess

from vmm.lib import vmware_list_status as vmware_info   # rename to your script name


class TestVMwareInfo(unittest.TestCase):

    #
    # run_vmrun()
    #
    @patch("subprocess.check_output")
    def test_run_vmrun_success(self, mock_check):
        mock_check.return_value = b"output text\n"
        result = vmware_info.run_vmrun(["cmd"])
        self.assertEqual(result, "output text")

    @patch("subprocess.check_output")
    def test_run_vmrun_failure(self, mock_check):
        mock_check.side_effect = subprocess.CalledProcessError(
            1, "cmd", output=b"error text"
        )
        result = vmware_info.run_vmrun(["cmd"])
        self.assertEqual(result, "error text")

    #
    # list_running_vms()
    #
    @patch("vmm.lib.vmware_list_status.run_vmrun")
    def test_list_running_vms(self, mock_run):
        mock_run.return_value = (
            "Total running VMs: 2\n"
            "/Users/test/VMs/Ubuntu.vmx\n"
            "/Users/test/VMs/CentOS.vmx\n"
        )
        running = vmware_info.list_running_vms()
        self.assertEqual(
            running,
            {
                "/Users/test/VMs/Ubuntu.vmx",
                "/Users/test/VMs/CentOS.vmx",
            }
        )

    #
    # get_vm_ip()
    #
    @patch("vmm.lib.vmware_list_status.run_vmrun")
    def test_get_vm_ip_success(self, mock_run):
        mock_run.return_value = "192.168.1.50"
        ip = vmware_info.get_vm_ip("/path/to/vm.vmx")
        self.assertEqual(ip, "192.168.1.50")

    @patch("vmm.lib.vmware_list_status.run_vmrun")
    def test_get_vm_ip_error(self, mock_run):
        mock_run.return_value = "Error: Unable to get IP"
        ip = vmware_info.get_vm_ip("/path/to/vm.vmx")
        self.assertIsNone(ip)

    #
    # detect_vm_status()
    #
    @unittest.skipIf(sys.platform.lower().startswith("win"), "Test doesn't work on Windows")
    @patch("pathlib.Path.iterdir")
    def test_detect_vm_status_running(self, mock_iterdir):
        running = {"/path/to/vm.vmx"}
        mock_iterdir.return_value = []
        status = vmware_info.detect_vm_status("/path/to/vm.vmx", running)
        self.assertEqual(status, "running")

    @patch("pathlib.Path.iterdir")
    def test_detect_vm_status_suspended(self, mock_iterdir):
        mock_file = MagicMock()
        mock_file.suffix = ".vmss"
        mock_iterdir.return_value = [mock_file]

        status = vmware_info.detect_vm_status("/path/to/vm.vmx", set())
        self.assertEqual(status, "suspended")

    @patch("pathlib.Path.iterdir")
    def test_detect_vm_status_off(self, mock_iterdir):
        mock_iterdir.return_value = []
        status = vmware_info.detect_vm_status("/path/to/vm.vmx", set())
        self.assertEqual(status, "off")

    #
    # find_all_vmx_files()
    #
    @patch("pathlib.Path.rglob")
    def test_find_all_vmx_files(self, mock_rglob):
        mock_rglob.return_value = [
            Path("/vm1/Ubuntu.vmx"),
            Path("/vm2/CentOS.vmx")
        ]
        result = vmware_info.find_all_vmx_files("/root")
        self.assertEqual(
            result,
            [
                Path("/vm1/Ubuntu.vmx"),
                Path("/vm2/CentOS.vmx")
            ]
        )


if __name__ == "__main__":
    unittest.main()

