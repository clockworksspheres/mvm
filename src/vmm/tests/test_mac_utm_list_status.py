import unittest
from unittest.mock import patch, MagicMock
import subprocess

# Import your module under test
import vmm.lib.mac_utm_list_status as utm   # <-- rename to your actual filename


class TestUTMFunctions(unittest.TestCase):

    # ---------------------------------------------------------
    # run_cmd()
    # ---------------------------------------------------------
    @patch("vmm.lib.mac_utm_list_status.subprocess.run")
    def test_run_cmd_success(self, mock_run):
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="VM list output\n",
            stderr=""
        )

        out = utm.run_cmd(["utmctl", "list"])
        self.assertEqual(out, "VM list output\n")
        mock_run.assert_called_once()

    @patch("vmm.lib.mac_utm_list_status.subprocess.run")
    @patch("vmm.lib.mac_utm_list_status.print")
    def test_run_cmd_failure(self, mock_print, mock_run):
        mock_run.return_value = MagicMock(
            returncode=1,
            stdout="",
            stderr="Something went wrong"
        )

        out = utm.run_cmd(["vmctl", "list"])
        self.assertEqual(out, "")
        mock_print.assert_called_once()

    # ---------------------------------------------------------
    # utm_list()
    # ---------------------------------------------------------
    @patch("vmm.lib.mac_utm_list_status.run_cmd")
    def test_utm_list_parsing(self, mock_run):
        mock_run.return_value = (
            "UUID STATE NAME\n"
            "1234 running Ubuntu\n"
            "5678 stopped Windows 11 Pro\n"
            "bad line\n"
        )

        vms = utm.utm_list()

        self.assertEqual(vms, [
            {"uuid": "1234", "state": "running", "name": "Ubuntu"},
            {"uuid": "5678", "state": "stopped", "name": "Windows 11 Pro"},
        ])

    @patch("vmm.lib.mac_utm_list_status.run_cmd")
    def test_utm_list_empty(self, mock_run):
        mock_run.return_value = "UUID STATE NAME\n"
        vms = utm.utm_list()
        self.assertEqual(vms, [])

    # ---------------------------------------------------------
    # utm_status()
    # ---------------------------------------------------------
    @patch("vmm.lib.mac_utm_list_status.run_cmd")
    def test_utm_status_extracts_state_and_ip(self, mock_run):
        mock_run.return_value = (
            "State: running\n"
            "Network: 192.168.64.3\n"
        )

        state, ip = utm.utm_status("1234")
        self.assertEqual(state, "running")
        self.assertEqual(ip, "192.168.64.3")

    @patch("vmm.lib.mac_utm_list_status.run_cmd")
    def test_utm_status_no_ip(self, mock_run):
        mock_run.return_value = (
            "State: stopped\n"
            "Network: No IP\n"
        )

        state, ip = utm.utm_status("1234")
        self.assertEqual(state, "stopped")
        self.assertIsNone(ip)

    @patch("vmm.lib.mac_utm_list_status.run_cmd")
    def test_utm_status_no_state(self, mock_run):
        mock_run.return_value = (
            "Something else\n"
            "192.168.1.10\n"
        )

        state, ip = utm.utm_status("1234")
        self.assertIsNone(state)
        self.assertEqual(ip, "192.168.1.10")


if __name__ == "__main__":
    unittest.main()

