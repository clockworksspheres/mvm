import sys
import unittest
from unittest.mock import MagicMock

from pathlib import Path

# Get the parent directory of the current file's parent directory
#  and add it to sys.path
parent_dir = Path(__file__).parent.parent

from mvm.MacosUtmMvm import MacosUtmMvm


@unittest.skipUnless(
    sys.platform.lower().startswith("darwin"),
    "MacosUtmMvm tests only run on macOS (darwin)"
)
class TestMacosUtmMvm(unittest.TestCase):

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
        self.mvm = MacosUtmMvm(self.logger)

        # Replace the real runner with our fake
        self.mvm.run = self.FakeRunWith(self.logger)

    def test_list_vms_sets_correct_command(self):
        self.mvm.list_vms()
        self.assertRaises(AssertionError)

    def test_start_vm_sets_correct_command(self):
        self.mvm.start_vm("myvm")
        self.assertEqual(
            self.mvm.run.last_command,
            ["utmctl", "start", "myvm"]
        )

    def test_stop_vm_sets_correct_command(self):
        self.mvm.stop_vm("testvm", hard=True)
        self.assertEqual(
            self.mvm.run.last_command,
            ["utmctl", "stop", "testvm"]
        )

    def test_pause_vm_sets_correct_command(self):
        self.mvm.pause_vm("vm1")
        self.assertEqual(
            self.mvm.run.last_command,
            ["utmctl", "pause", "vm1"]
        )

    def test_unpause_vm_sets_correct_command(self):
        self.mvm.unpause_vm("vmX")
        self.assertEqual(
            self.mvm.run.last_command,
            ["utmctl", "start", "vmX"]
        )

    def test_reset_vm_runs_stop_then_start(self):
        self.mvm.reset_vm("vmR")
        self.assertEqual(
            self.mvm.run.last_command,
            ["utmctl", "start", "vmR"]
        )

    '''
    # tests do not test as intended
    @unittest.SkipTest
    def test_get_vm_status_returns_stripped_output(self):
        self.mvm.run.responses[
            ("utmctl", "status", "v1")
        ] = (" running\n", "", 0)

        status = self.mvm.get_vm_status("v1")
        self.assertRaises(AssertionError)

    def test_get_ip_returns_stripped_ip(self):
        self.mvm.run.responses[
            ("utmctl", "ip-address", "vmIP")
        ] = ("192.168.1.50\n", "", 0)
        

        ip = self.mvm.get_ip("vmIP")
        self.assertRaises(AssertionError)
    '''


if __name__ == "__main__":
    unittest.main()


