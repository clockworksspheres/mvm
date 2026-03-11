import sys
import unittest

from pathlib import Path

# Get the parent directory of the current file's parent directory
#  and add it to sys.path
parent_dir = Path(__file__).parent.parent
sys.path.append(str(parent_dir))


@unittest.skipUnless(
    sys.platform.lower().startswith("win32"),
    "WindowsVmwareVmm tests only run on Windows (win32)"
)
class TestWindowsVmwareVmm(unittest.TestCase):

    from vmm.WindowsVmwareVmm import WindowsVmwareVmm

    class FakeRunWith:
        """Fake runner capturing commands instead of executing them."""
        def __init__(self, logger):
            self.logger = logger
            self.last_command = None
            self.responses = {}

        def setCommand(self, cmd):
            self.last_command = list(cmd)

        def communicate(self):
            key = tuple(self.last_command)
            return self.responses.get(key, ("", "", 0))

    class DummyLogger:
        def initializeLogs(self):
            pass

        def log(self, *args, **kwargs):
            pass

    def setUp(self):
        # Setup with a fake logger & fake runner
        self.logger = self.DummyLogger()
        self.vmm = self.WindowsVmwareVmm(self.logger)
        self.vmm.run = self.FakeRunWith(self.logger)

        # Override vmrun path to a known value for testing
        self.vmm.vmrun = r"C:\\fake\\vmrun.exe"

    def test_list_vms_sets_correct_command(self):
        self.vmm.list_vms()
        self.assertEqual(
            self.vmm.run.last_command,
            [r"C:\\fake\\vmrun.exe", "list"]
        )

    def test_start_vm_sets_correct_command_gui(self):
        self.vmm.start_vm("TestVM", headless=False)
        self.assertEqual(
            self.vmm.run.last_command,
            [r"C:\\fake\\vmrun.exe", "-T", "ws", "start", "TestVM", "gui"]
        )

    def test_start_vm_sets_correct_command_headless(self):
        self.vmm.start_vm("HeadlessVM", headless=True)
        self.assertEqual(
            self.vmm.run.last_command,
            [r"C:\\fake\\vmrun.exe", "-T", "ws", "start", "HeadlessVM", "nogui"]
        )

    def test_stop_vm_sets_correct_command_hard(self):
        self.vmm.stop_vm("VMstop", hard=True)
        self.assertEqual(
            self.vmm.run.last_command,
            [r"C:\\fake\\vmrun.exe", "stop", "VMstop", "hard"]
        )

    def test_stop_vm_sets_correct_command_soft(self):
        self.vmm.stop_vm("VMsoft", hard=False)
        self.assertEqual(
            self.vmm.run.last_command,
            [r"C:\\fake\\vmrun.exe", "stop", "VMsoft", "soft"]
        )

    def test_pause_vm_sets_correct_command(self):
        self.vmm.pause_vm("VMp")
        self.assertEqual(
            self.vmm.run.last_command,
            [r"C:\\fake\\vmrun.exe", "pause", "VMp"]
        )

    def test_unpause_vm_sets_correct_command(self):
        self.vmm.unpause_vm("VMu")
        self.assertEqual(
            self.vmm.run.last_command,
            [r"C:\\fake\\vmrun.exe", "unpause", "VMu"]
        )

    def test_reset_vm_sets_correct_command_hard(self):
        self.vmm.reset_vm("VMr", hard=True)
        self.assertEqual(
            self.vmm.run.last_command,
            [r"C:\\fake\\vmrun.exe", "reset", "VMr", "hard"]
        )

    def test_reset_vm_sets_correct_command_soft(self):
        self.vmm.reset_vm("VMr", hard=False)
        self.assertEqual(
            self.vmm.run.last_command,
            [r"C:\\fake\\vmrun.exe", "reset", "VMr", "soft"]
        )

    def test_get_vm_status_returns_stripped_output(self):
        key = (r"C:\\fake\\vmrun.exe", "list")
        self.vmm.run.responses[key] = ("  VMSTATE \n", "", 0)
        status = self.vmm.get_vm_status("ignored_vm_arg")
        self.assertEqual(status, "VMSTATE")

    def test_get_ip_returns_stripped_output(self):
        key = (r"C:\\fake\\vmrun.exe", "getGuestIPAddress", "VMip", "-wait")
        self.vmm.run.responses[key] = ("  192.168.1.123  \n", "", 0)
        ip = self.vmm.get_ip("VMip")
        self.assertEqual(ip, "192.168.1.123")


if __name__ == "__main__":
    unittest.main()

