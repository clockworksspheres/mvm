import sys
import unittest
from unittest.mock import patch, MagicMock
from pathlib import Path

# Get the parent directory of the current file's parent directory
#  and add it to sys.path
parent_dir = Path(__file__).parent.parent

# Adjust import path to match your project structure
from vmm.MacosVirtualboxVmm import MacosVirtualboxVmm


class TestMacosVirtualboxVmm(unittest.TestCase):

    #
    # ────────────────────────────────────────────────────────────────
    #   Helper: create instance with mocked RunWith
    # ────────────────────────────────────────────────────────────────
    #
    @patch("vmm.MacosVirtualboxVmm.RunWith")
    def create_vmm(self, mock_runwith):
        mock_run = MagicMock()
        mock_runwith.return_value = mock_run
        vmm = MacosVirtualboxVmm(logger=MagicMock())
        return vmm, mock_run

    #
    # ────────────────────────────────────────────────────────────────
    #   Test list_vms()
    # ────────────────────────────────────────────────────────────────
    #
    @patch("vmm.MacosVirtualboxVmm.get_vm_ip")
    @patch("vmm.MacosVirtualboxVmm.get_vm_state")
    @patch("vmm.MacosVirtualboxVmm.list_running_vms")
    @patch("vmm.MacosVirtualboxVmm.list_vms")
    def test_list_vms(self, mock_list_vms, mock_list_running, mock_state, mock_ip):
        mock_list_vms.return_value = {"TestVM": "UUID123"}
        mock_list_running.return_value = ["UUID123"]
        mock_state.return_value = "running"
        mock_ip.return_value = "192.168.56.10"

        vmm, _ = self.create_vmm()

        vmm.list_vms()

        mock_list_vms.assert_called_once()
        mock_state.assert_called_with("UUID123")
        mock_ip.assert_called_with("UUID123")

    #
    # ────────────────────────────────────────────────────────────────
    #   Test start_vm()
    # ────────────────────────────────────────────────────────────────
    #
    @patch("vmm.MacosVirtualboxVmm.RunWith")
    def test_start_vm(self, mock_runwith):
        vmm, mock_run = self.create_vmm()

        vmm.start_vm("TestVM")

        mock_run.setCommand.assert_called_with(
            ["/usr/local/bin/VBoxManage", "startvm", "TestVM"]
        )
        mock_run.communicate.assert_called_once()

    #
    # ────────────────────────────────────────────────────────────────
    #   Test stop_vm()
    # ────────────────────────────────────────────────────────────────
    #
    @patch("vmm.MacosVirtualboxVmm.RunWith")
    def test_stop_vm(self, mock_runwith):
        vmm, mock_run = self.create_vmm()

        vmm.stop_vm("TestVM")

        mock_run.setCommand.assert_called_with(
            ["/usr/local/bin/VBoxManage", "controlvm", "TestVM", "poweroff"]
        )
        mock_run.communicate.assert_called_once()

    #
    # ────────────────────────────────────────────────────────────────
    #   Test pause_vm()
    # ────────────────────────────────────────────────────────────────
    #
    @patch("vmm.MacosVirtualboxVmm.RunWith")
    def test_pause_vm(self, mock_runwith):
        vmm, mock_run = self.create_vmm()

        vmm.pause_vm("TestVM")

        mock_run.setCommand.assert_called_with(
            ["/usr/local/bin/VBoxManage", "controlvm", "TestVM", "savestate"]
        )
        mock_run.communicate.assert_called_once()

    #
    # ────────────────────────────────────────────────────────────────
    #   Test unpause_vm()
    # ────────────────────────────────────────────────────────────────
    #
    @patch("vmm.MacosVirtualboxVmm.RunWith")
    def test_unpause_vm(self, mock_runwith):
        vmm, mock_run = self.create_vmm()

        vmm.unpause_vm("TestVM")

        mock_run.setCommand.assert_called_with(
            ["/usr/local/bin/VBoxManage", "controlvm", "TestVM", "resume"]
        )
        mock_run.communicate.assert_called_once()

    #
    # ────────────────────────────────────────────────────────────────
    #   Test reset_vm()
    # ────────────────────────────────────────────────────────────────
    #
    @patch("vmm.MacosVirtualboxVmm.RunWith")
    def test_reset_vm(self, mock_runwith):
        vmm, mock_run = self.create_vmm()

        vmm.reset_vm("TestVM")

        expected_calls = [
            (["/usr/local/bin/VBoxManage", "controlvm", "TestVM", "reset"],),
            ([ "/usr/local/bin/VBoxManage", "start", "TestVM"],)
        ]

        actual_calls = [call.args for call in mock_run.setCommand.call_args_list]

        self.assertEqual(actual_calls, expected_calls)
        self.assertEqual(mock_run.communicate.call_count, 2)

    #
    # ────────────────────────────────────────────────────────────────
    #   Test get_ip()
    # ────────────────────────────────────────────────────────────────
    #
    @patch("vmm.MacosVirtualboxVmm.RunWith")
    def test_get_ip(self, mock_runwith):
        vmm, mock_run = self.create_vmm()

        mock_run.communicate.return_value = ("192.168.56.10\n", "", 0)

        ip = vmm.get_ip("TestVM")

        mock_run.setCommand.assert_called_with(
            ["/usr/local/bin/VBoxManage", "guestproperty", "get",
             "TestVM", "/VirtuallBox/GuestInfo/Net/0/IP"]
        )
        self.assertEqual(ip, "192.168.56.10")

    #
    # ────────────────────────────────────────────────────────────────
    #   Test get_vm_status()
    # ────────────────────────────────────────────────────────────────
    #
    @patch("vmm.MacosVirtualboxVmm.MacosVirtualboxVmm.list_vms")
    def test_get_vm_status(self, mock_list_vms):
        mock_list_vms.return_value = ("TestVM", "running", "192.168.56.10")

        vmm, _ = self.create_vmm()

        name, state, ip = vmm.get_vm_status("TestVM")

        self.assertEqual(name, "TestVM")
        self.assertEqual(state, "running")
        self.assertEqual(ip, "192.168.56.10")


if __name__ == "__main__":
    unittest.main()

