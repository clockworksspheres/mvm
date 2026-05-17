import unittest
from unittest.mock import patch
import subprocess

# Import your module (adjust name if needed)
from mvm.lib import virtualbox_list_status as vboxinfo


class TestVBoxInfo(unittest.TestCase):

    @patch("subprocess.check_output")
    def test_run_success(self, mock_check):
        mock_check.return_value = b"hello world\n"
        result = vboxinfo.run(["echo", "test"])
        self.assertEqual(result, "hello world")

    @patch("subprocess.check_output", side_effect=subprocess.CalledProcessError(1, "cmd"))
    def test_run_failure(self, mock_check):
        result = vboxinfo.run(["bad", "cmd"])
        self.assertEqual(result, "")

    @patch("subprocess.check_output")
    def test_list_vms(self, mock_check):
        mock_check.return_value = b'"TestVM" {1234-5678}\n"OtherVM" {abcd-efgh}\n'
        vms = vboxinfo.list_vms()
        self.assertEqual(vms, {
            "TestVM": "1234-5678",
            "OtherVM": "abcd-efgh"
        })

    @patch("subprocess.check_output")
    def test_list_running_vms(self, mock_check):
        mock_check.return_value = b'"TestVM" {1234-5678}\n'
        running = vboxinfo.list_running_vms()
        self.assertEqual(running, {"1234-5678"})

    @patch("subprocess.check_output")
    def test_get_vm_state(self, mock_check):
        mock_check.return_value = b'VMState="running"\n'
        state = vboxinfo.get_vm_state("1234")
        self.assertEqual(state, "running")

    @patch("subprocess.check_output")
    def test_get_vm_state_unknown(self, mock_check):
        mock_check.return_value = b'NoStateHere="foo"\n'
        state = vboxinfo.get_vm_state("1234")
        self.assertEqual(state, "unknown")

    @patch("subprocess.check_output")
    def test_get_vm_ip(self, mock_check):
        mock_check.return_value = b'Value: 192.168.56.101\n'
        ip = vboxinfo.get_vm_ip("1234")
        self.assertEqual(ip, "192.168.56.101")

    @patch("subprocess.check_output")
    def test_get_vm_ip_none(self, mock_check):
        mock_check.return_value = b'No value set!\n'
        ip = vboxinfo.get_vm_ip("1234")
        self.assertIsNone(ip)


if __name__ == "__main__":
    unittest.main()

