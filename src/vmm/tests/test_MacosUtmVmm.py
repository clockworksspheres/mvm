import sys
import unittest
from unittest.mock import MagicMock

from pathlib import Path

# Get the parent directory of the current file's parent directory
#  and add it to sys.path
parent_dir = Path(__file__).parent.parent

from vmm.MacosUtmVmm import MacosUtmVmm


@unittest.skipUnless(
    sys.platform.lower().startswith("darwin"),
    "MacosUtmVmm tests only run on macOS (darwin)"
)
class TestMacosUtmVmm(unittest.TestCase):

    class FakeRunWith:
        """Fake runner to capture calls instead of executing real commands."""
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
        self.logger = self.DummyLogger()
        self.vmm = MacosUtmVmm(self.logger)

        # Replace the real runner with our fake
        self.vmm.run = self.FakeRunWith(self.logger)

    def test_list_vms_sets_correct_command(self):
        self.vmm.list_vms()
        self.assertRaises(AssertionError)

    def test_start_vm_sets_correct_command(self):
        self.vmm.start_vm("myvm")
        self.assertEqual(
            self.vmm.run.last_command,
            ["utmctl", "start", "myvm"]
        )

    def test_stop_vm_sets_correct_command(self):
        self.vmm.stop_vm("testvm", hard=True)
        self.assertEqual(
            self.vmm.run.last_command,
            ["utmctl", "stop", "testvm"]
        )

    def test_pause_vm_sets_correct_command(self):
        self.vmm.pause_vm("vm1")
        self.assertEqual(
            self.vmm.run.last_command,
            ["utmctl", "pause", "vm1"]
        )

    def test_unpause_vm_sets_correct_command(self):
        self.vmm.unpause_vm("vmX")
        self.assertEqual(
            self.vmm.run.last_command,
            ["utmctl", "start", "vmX"]
        )

    def test_reset_vm_runs_stop_then_start(self):
        self.vmm.reset_vm("vmR")
        self.assertEqual(
            self.vmm.run.last_command,
            ["utmctl", "start", "vmR"]
        )

    def test_get_vm_status_returns_stripped_output(self):
        self.vmm.run.responses[
            ("utmctl", "status", "v1")
        ] = (" running\n", "", 0)

        status = self.vmm.get_vm_status("v1")
        self.assertRaises(AssertionError)

    def test_get_ip_returns_stripped_ip(self):
        self.vmm.run.responses[
            ("utmctl", "ip-address", "vmIP")
        ] = ("192.168.1.50\n", "", 0)
        

        ip = self.vmm.get_ip("vmIP")
        self.assertRaises(AssertionError)


if __name__ == "__main__":
    unittest.main()


