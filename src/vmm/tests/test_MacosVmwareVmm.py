import sys
import unittest

sys.path.append("./..")
from vmm.MacosVmwareVmm import MacosVmwareVmm


@unittest.skipUnless(
    sys.platform.lower().startswith("darwin"),
    "MacosVmwareVmm tests only run on macOS (darwin)"
)
class TestMacosVmwareVmm(unittest.TestCase):

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
            # Return stubbed (stdout, stderr, exitcode)
            return self.responses.get(key, ("", "", 0))

    class DummyLogger:
        def initializeLogs(self):
            pass

        def log(self, *args, **kwargs):
            pass

    def setUp(self):
        self.logger = self.DummyLogger()
        self.vmm = MacosVmwareVmm(self.logger)

        # Replace the internal runner
        self.vmm.run = self.FakeRunWith(self.logger)

        # Replace path to vmrun to a fixed string for testing
        self.vmm.vmrun = "/fake/vmrun"

    def test_list_vms_sets_correct_command(self):
        self.vmm.list_vms()
        self.assertRaises(AssertionError)

    def test_start_vm_sets_correct_command_gui(self):
        self.vmm.start_vm("TestVM", headless=False)
        self.assertEqual(
            self.vmm.run.last_command,
            ["/fake/vmrun", "-T", "fusion", "start", "TestVM", "gui"]
        )

    def test_start_vm_sets_correct_command_headless(self):
        self.vmm.start_vm("HeadlessVM", headless=True)
        self.assertEqual(
            self.vmm.run.last_command,
            ["/fake/vmrun", "-T", "fusion", "start", "HeadlessVM", "nogui"]
        )

    def test_stop_vm_sets_correct_command_hard(self):
        self.vmm.stop_vm("vmStop", hard=True)
        self.assertEqual(
            self.vmm.run.last_command,
            ["/fake/vmrun", "stop", "vmStop", "hard"]
        )

    def test_stop_vm_sets_correct_command_soft(self):
        self.vmm.stop_vm("vmSoft", hard=False)
        self.assertEqual(
            self.vmm.run.last_command,
            ["/fake/vmrun", "stop", "vmSoft", "soft"]
        )

    def test_pause_vm_sets_correct_command(self):
        self.vmm.pause_vm("vmP")
        self.assertEqual(
            self.vmm.run.last_command,
            ["/fake/vmrun", "pause", "vmP", "soft"]
        )

    def test_unpause_vm_sets_correct_command(self):
        self.vmm.unpause_vm("vmU")
        self.assertEqual(
            self.vmm.run.last_command,
            ["/fake/vmrun", "unpause", "vmU", "soft"]
        )

    def test_reset_vm_sets_correct_command_hard(self):
        self.vmm.reset_vm("vmR", hard=True)
        self.assertEqual(
            self.vmm.run.last_command,
            ["/fake/vmrun", "reset", "vmR", "hard"]
        )

    def test_reset_vm_sets_correct_command_soft(self):
        self.vmm.reset_vm("vmR", hard=False)
        self.assertEqual(
            self.vmm.run.last_command,
            ["/fake/vmrun", "reset", "vmR", "soft"]
        )

    def test_get_ip_returns_stripped_output(self):
        key = ("/fake/vmrun", "getGuestIPAddress", "vmIP", "-wait")
        self.vmm.run.responses[key] = (" 192.168.1.100 \n", "", 0)
        ip = self.vmm.get_ip("vmIP")
        self.assertEqual(ip, "192.168.1.100")


if __name__ == "__main__":
    unittest.main()

