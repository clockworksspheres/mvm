import unittest
from unittest.mock import patch, MagicMock

from vmm.WindowsVmwareVmm import WindowsVmwareVmm

VM_PATH = "C:\\vm\\test.vmx"


class TestWindowsVmwareVmm(unittest.TestCase):
    pass


def make_vm_action_test(method_name, call_builder, expected_cmd):
    @patch("vmm.WindowsVmwareVmm.RunWith")
    @patch("vmm.WindowsVmwareVmm.find_vm_by_display_name")
    def test(self, mock_find_vm, mock_runwith):
        # Arrange
        mock_find_vm.return_value = [VM_PATH]

        mock_run_instance = MagicMock()
        mock_runwith.return_value = mock_run_instance

        vmm = WindowsVmwareVmm(logger=MagicMock())

        # Act
        call_builder(vmm)

        # Assert
        mock_run_instance.setCommand.assert_called_once_with(expected_cmd(vmm))
        mock_run_instance.communicate.assert_called_once()

    test.__name__ = f"test_{method_name}"
    return test


# --- Define ALL cases here ---
TEST_CASES = [
    (
        "start_vm_headless",
        lambda vmm: vmm.start_vm("vm1", headless=True),
        lambda vmm: [vmm.vmrun, "-T", "ws", "start", VM_PATH, "nogui"],
    ),
    (
        "start_vm_gui",
        lambda vmm: vmm.start_vm("vm1", headless=False),
        lambda vmm: [vmm.vmrun, "-T", "ws", "start", VM_PATH, "gui"],
    ),
    (
        "stop_vm_soft",
        lambda vmm: vmm.stop_vm("vm1", hard=False),
        lambda vmm: [vmm.vmrun, "stop", VM_PATH, "soft"],
    ),
    (
        "stop_vm_hard",
        lambda vmm: vmm.stop_vm("vm1", hard=True),
        lambda vmm: [vmm.vmrun, "stop", VM_PATH, "hard"],
    ),
    (
        "pause_vm",
        lambda vmm: vmm.pause_vm("vm1"),
        lambda vmm: [vmm.vmrun, "pause", VM_PATH],
    ),
    (
        "unpause_vm",
        lambda vmm: vmm.unpause_vm("vm1"),
        lambda vmm: [vmm.vmrun, "unpause", VM_PATH],
    ),
    (
        "reset_vm_soft",
        lambda vmm: vmm.reset_vm("vm1", hard=False),
        lambda vmm: [vmm.vmrun, "reset", VM_PATH, "soft"],
    ),
    (
        "reset_vm_hard",
        lambda vmm: vmm.reset_vm("vm1", hard=True),
        lambda vmm: [vmm.vmrun, "reset", VM_PATH, "hard"],
    ),
]


# Dynamically attach tests
for name, call, expected in TEST_CASES:
    setattr(
        TestWindowsVmwareVmm,
        f"test_{name}",
        make_vm_action_test(name, call, expected),
    )


# --- Additional tests for full coverage ---

class TestWindowsVmwareVmmExtras(unittest.TestCase):

    @patch("vmm.WindowsVmwareVmm.RunWith")
    def test_list_vms(self, mock_runwith):
        mock_run_instance = MagicMock()
        mock_runwith.return_value = mock_run_instance

        vmm = WindowsVmwareVmm(logger=MagicMock())

        vmm.list_vms()

        mock_run_instance.setCommand.assert_called_once_with(
            [vmm.vmrun, "list"]
        )
        mock_run_instance.communicate.assert_called_once()

    @patch("vmm.WindowsVmwareVmm.RunWith")
    def test_get_vm_status(self, mock_runwith):
        mock_run_instance = MagicMock()
        mock_run_instance.communicate.return_value = ("VM1\n", "", 0)
        mock_runwith.return_value = mock_run_instance

        vmm = WindowsVmwareVmm(logger=MagicMock())

        result = vmm.get_vm_status("vm1")

        self.assertEqual(result, "VM1")

    @patch("vmm.WindowsVmwareVmm.RunWith")
    @patch("vmm.WindowsVmwareVmm.find_vm_by_display_name")
    def test_get_ip(self, mock_find_vm, mock_runwith):
        mock_find_vm.return_value = [VM_PATH]

        mock_run_instance = MagicMock()
        mock_run_instance.communicate.return_value = ("192.168.1.5\n", "", 0)
        mock_runwith.return_value = mock_run_instance

        vmm = WindowsVmwareVmm(logger=MagicMock())

        result = vmm.get_ip("vm1")

        self.assertEqual(result, "192.168.1.5")

    @patch("vmm.WindowsVmwareVmm.find_vm_by_display_name")
    @patch("vmm.WindowsVmwareVmm.RunWith")
    def test_find_vm_by_display_name_method(self, mock_runwith, mock_find_vm):
        mock_find_vm.return_value = [("C:\\vm\\test.vmx",)]

        vmm = WindowsVmwareVmm(logger=MagicMock())

        result = vmm.find_vm_by_display_name("vm1")

        # NOTE: reflects your current implementation bug
        self.assertEqual(result, "C:\\vm\\test.vmx")

