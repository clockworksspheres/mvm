import sys
import unittest
from unittest.mock import patch, MagicMock

from mvm.WindowsVmwareMvm import WindowsVmwareMvm

VM_PATH = "C:\\vm\\test.vmx"


@unittest.skipUnless(sys.platform.lower().startswith("win"), "Only test on Windows")
class TestWindowsVmwareMvm(unittest.TestCase):
    pass


def make_vm_action_test(method_name, call_builder, expected_cmd):
    @patch("mmvm.WindowsVmwareMvm.RunWith")
    @patch("mmvm.WindowsVmwareMvm.find_vm_by_display_name")
    def test(self, mock_find_vm, mock_runwith):
        # Arrange
        mock_find_vm.return_value = [VM_PATH]

        mock_run_instance = MagicMock()
        mock_runwith.return_value = mock_run_instance

        mvm = WindowsVmwareMvm(logger=MagicMock())

        # Act
        call_builder(mvm)

        # Assert
        mock_run_instance.setCommand.assert_called_once_with(expected_cmd(mvm))
        mock_run_instance.communicate.assert_called_once()

    test.__name__ = f"test_{method_name}"
    return test


# --- Define ALL cases here ---
TEST_CASES = [
    (
        "start_vm_headless",
        lambda mvm: mvm.start_vm("vm1", headless=True),
        lambda mvm: [mvm.vmrun, "-T", "ws", "start", VM_PATH, "nogui"],
    ),
    (
        "start_vm_gui",
        lambda mvm: mvm.start_vm("vm1", headless=False),
        lambda mvm: [mvm.vmrun, "-T", "ws", "start", VM_PATH, "gui"],
    ),
    (
        "stop_vm_soft",
        lambda mvm: mvm.stop_vm("vm1", hard=False),
        lambda mvm: [mvm.vmrun, "stop", VM_PATH, "soft"],
    ),
    (
        "stop_vm_hard",
        lambda mvm: mvm.stop_vm("vm1", hard=True),
        lambda mvm: [mvm.vmrun, "stop", VM_PATH, "hard"],
    ),
    (
        "pause_vm",
        lambda mvm: mvm.pause_vm("vm1"),
        lambda mvm: [mvm.vmrun, "pause", VM_PATH],
    ),
    (
        "unpause_vm",
        lambda mvm: mvm.unpause_vm("vm1"),
        lambda mvm: [mvm.vmrun, "unpause", VM_PATH],
    ),
    (
        "reset_vm_soft",
        lambda mvm: mvm.reset_vm("vm1", hard=False),
        lambda mvm: [mvm.vmrun, "reset", VM_PATH, "soft"],
    ),
    (
        "reset_vm_hard",
        lambda mvm: mvm.reset_vm("vm1", hard=True),
        lambda mvm: [mvm.vmrun, "reset", VM_PATH, "hard"],
    ),
]


# Dynamically attach tests
for name, call, expected in TEST_CASES:
    setattr(
        TestWindowsVmwareMvm,
        f"test_{name}",
        make_vm_action_test(name, call, expected),
    )


# --- Additional tests for full coverage ---

@unittest.skipUnless(sys.platform.lower().startswith("win"), "Only test on Windows")
class TestWindowsVmwareMvmExtras(unittest.TestCase):

    @patch("mvm.WindowsVmwareMvm.RunWith")
    def test_list_vms(self, mock_runwith):
        mock_run_instance = MagicMock()
        mock_runwith.return_value = mock_run_instance

        mvm = WindowsVmwareMvm(logger=MagicMock())

        mvm.list_vms()

        mock_run_instance.setCommand.assert_called_once_with(
            [mvm.vmrun, "list"]
        )
        mock_run_instance.communicate.assert_called_once()

    @patch("mvm.WindowsVmwareMvm.RunWith")
    def test_get_vm_status(self, mock_runwith):
        mock_run_instance = MagicMock()
        mock_run_instance.communicate.return_value = ("VM1\n", "", 0)
        mock_runwith.return_value = mock_run_instance

        mvm = WindowsVmwareMvm(logger=MagicMock())

        result = mvm.get_vm_status("vm1")

        self.assertEqual(result, "VM1")

    @patch("mvm.WindowsVmwareMvm.RunWith")
    @patch("mvm.WindowsVmwareMvm.find_vm_by_display_name")
    def test_get_ip(self, mock_find_vm, mock_runwith):
        mock_find_vm.return_value = [VM_PATH]

        mock_run_instance = MagicMock()
        mock_run_instance.communicate.return_value = ("192.168.1.5\n", "", 0)
        mock_runwith.return_value = mock_run_instance

        mvm = WindowsVmwareMvm(logger=MagicMock())

        result = mvm.get_ip("vm1")

        self.assertEqual(result, "192.168.1.5")

    @patch("mvm.WindowsVmwareMvm.find_vm_by_display_name")
    @patch("mvm.WindowsVmwareMvm.RunWith")
    def test_find_vm_by_display_name_method(self, mock_runwith, mock_find_vm):
        mock_find_vm.return_value = [("C:\\vm\\test.vmx",)]

        mvm = WindowsVmwareMvm(logger=MagicMock())

        result = mvm.find_vm_by_display_name("vm1")

        # NOTE: reflects your current implementation bug
        self.assertEqual(result, "C:\\vm\\test.vmx")

