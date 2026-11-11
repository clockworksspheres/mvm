#!/usr/bin/env python3
"""
Unit tests for the Linux QEMU / libvirt MVM backend.

All external dependencies (libvirt, platform, shutil, os, subprocess, etc.)
are mocked so the suite runs without a real hypervisor.
"""

import json
import os
import sys
import unittest
from pathlib import Path

# Get the parent directory of the current file's parent directory
#  and add it to sys.path
parent_dir = Path(__file__).parent.parent
sys.path.append(str(parent_dir))


# ---------------------------------------------------------------------------
# On non-Linux platforms, provide a minimal skipped suite so discovery
# succeeds and the rest of the test run continues normally.
# ---------------------------------------------------------------------------
if not sys.platform.startswith("linux"):

    @unittest.skip("Requires Linux")
    class TestLinuxQemuMvm(unittest.TestCase):
        def test_placeholder(self):
            pass

else:


    from unittest.mock import (
        MagicMock,
        Mock,
        patch,
        mock_open,
        ANY,
    )


    # ---------------------------------------------------------------------------
    # Import the module under test while controlling its import-time side effects.
    # QEMU_BIN is evaluated at import time, so we supply a plausible binary.
    # Adjust the module name if your file is named differently.
    # ---------------------------------------------------------------------------
    with patch("platform.machine", return_value="x86_64"), \
        patch("shutil.which", return_value="/usr/bin/qemu-system-x86_64"), \
        patch("os.access", return_value=True), \
        patch("os.path.isfile", return_value=True):
        import mvm.LinuxQemuMvm as mvm_mod          # <-- change if the filename differs
        from mvm.LinuxQemuMvm import (
            _get_arch,
            _find_qemu_bin,
            QEMU_BIN_CANDIDATES,
            VMState,
            LinuxQemuMvm,
        )


    # ---------------------------------------------------------------------------
    # Minimal fake for a libvirt domain
    # ---------------------------------------------------------------------------
    class FakeDomain:
        def __init__(self, name, state=1):          # 1 == VIR_DOMAIN_RUNNING
            self._name = name
            self._state = state

        def name(self):
            return self._name

        def state(self):
            return (self._state, 0)

        def info(self):
            return (self._state, 0, 0, 1, 0)

        def create(self):
            pass

        def destroy(self):
            pass

        def shutdown(self):
            pass

        def reset(self, flags=0):
            pass

        def suspend(self):
            pass

        def resume(self):
            pass


    # ---------------------------------------------------------------------------
    # Module-level helpers
    # ---------------------------------------------------------------------------
    class TestGetArch(unittest.TestCase):

        @classmethod
        def setUpClass(cls):

            # ---------------------------------------------------------------------------
            # Import the module under test while controlling its import-time side effects.
            # QEMU_BIN is evaluated at import time, so we supply a plausible binary.
            # Adjust the module name if your file is named differently.
            # ---------------------------------------------------------------------------
            with patch("platform.machine", return_value="x86_64"), \
                patch("shutil.which", return_value="/usr/bin/qemu-system-x86_64"), \
                patch("os.access", return_value=True), \
                patch("os.path.isfile", return_value=True):
                import mvm.LinuxQemuMvm as mvm_mod          # <-- change if the filename differs
                from mvm.LinuxQemuMvm import (
                    _get_arch,
                    _find_qemu_bin,
                    QEMU_BIN_CANDIDATES,
                    VMState,
                    LinuxQemuMvm,
                )

        @patch("platform.machine")
        def test_x86_64_variants(self, mock_machine):
            for raw in ("x86_64", "X86_64", "amd64", "AMD64"):
                mock_machine.return_value = raw
                self.assertEqual(_get_arch(), "x86_64")

        @patch("platform.machine")
        def test_aarch64_variants(self, mock_machine):
            for raw in ("aarch64", "arm64", "ARM64"):
                mock_machine.return_value = raw
                self.assertEqual(_get_arch(), "aarch64")

        @patch("platform.machine")
        def test_arm(self, mock_machine):
            for raw in ("armv7l", "arm", "ARM"):
                mock_machine.return_value = raw
                self.assertEqual(_get_arch(), "arm")

        @patch("platform.machine")
        def test_i386(self, mock_machine):
            mock_machine.return_value = "i386"
            self.assertEqual(_get_arch(), "i386")

        @patch("platform.machine")
        def test_unknown_fallback(self, mock_machine):
            mock_machine.return_value = "riscv64"
            self.assertEqual(_get_arch(), "riscv64")


    class TestFindQemuBin(unittest.TestCase):

        @patch.object(mvm_mod, "_get_arch", return_value="x86_64")
        @patch("shutil.which")
        @patch("os.access", return_value=True)
        def test_finds_in_path(self, mock_access, mock_which, mock_arch):
            mock_which.side_effect = (
                lambda c: "/usr/bin/qemu-system-x86_64"
                if c == "qemu-system-x86_64" else None
            )
            self.assertEqual(_find_qemu_bin(), "/usr/bin/qemu-system-x86_64")

        @patch.object(mvm_mod, "_get_arch", return_value="x86_64")
        @patch("shutil.which", return_value=None)
        @patch("os.path.isfile")
        @patch("os.access", return_value=True)
        def test_finds_in_fallback_path(self, mock_access, mock_isfile, mock_which, mock_arch):
            mock_isfile.side_effect = lambda p: p == "/usr/libexec/qemu-kvm"
            self.assertEqual(_find_qemu_bin(), "/usr/libexec/qemu-kvm")

        @patch.object(mvm_mod, "_get_arch", return_value="aarch64")
        @patch("shutil.which")
        @patch("os.access", return_value=True)
        def test_aarch64_prefers_system_aarch64(self, mock_access, mock_which, mock_arch):
            mock_which.side_effect = (
                lambda c: "/usr/bin/qemu-system-aarch64"
                if c == "qemu-system-aarch64" else None
            )
            self.assertEqual(_find_qemu_bin(), "/usr/bin/qemu-system-aarch64")

        @patch.object(mvm_mod, "_get_arch", return_value="x86_64")
        @patch("shutil.which", return_value=None)
        @patch("os.path.isfile", return_value=False)
        @patch("os.access", return_value=False)
        def test_raises_when_not_found(self, mock_access, mock_isfile, mock_which, mock_arch):
            with self.assertRaises(RuntimeError) as cm:
                _find_qemu_bin()
            msg = str(cm.exception)
            self.assertIn("QEMU not found", msg)
            self.assertIn("x86_64", msg)


    # ---------------------------------------------------------------------------
    # LinuxQemuMvm
    # ---------------------------------------------------------------------------
    class TestLinuxQemuMvmInit(unittest.TestCase):

        def setUp(self):
            self.logger = MagicMock()

        @patch.object(mvm_mod, "libvirt")
        def test_init_success(self, mock_libvirt):
            mock_conn = MagicMock()
            mock_conn.listAllDomains.return_value = [FakeDomain("testvm")]
            mock_libvirt.open.return_value = mock_conn

            instance = LinuxQemuMvm(self.logger)

            self.assertIsNotNone(instance.conn)
            self.assertEqual(len(instance.domains), 1)
            mock_libvirt.open.assert_called_once_with("qemu:///system")

        @patch.object(mvm_mod, "libvirt")
        def test_init_no_vms_raises(self, mock_libvirt):
            mock_conn = MagicMock()
            mock_conn.listAllDomains.return_value = []
            mock_libvirt.open.return_value = mock_conn

            with self.assertRaises(mvm_mod.NoVmsFound):
                LinuxQemuMvm(self.logger)

        @patch.object(mvm_mod, "libvirt")
        def test_init_connection_failure(self, mock_libvirt):
            # Current implementation catches the exception and returns early
            mock_libvirt.open.side_effect = Exception("permission denied")
            instance = LinuxQemuMvm(self.logger)
            self.assertTrue(hasattr(instance, "logger"))


    class TestLinuxQemuMvmHelpers(unittest.TestCase):

        def setUp(self):
            self.logger = MagicMock()
            with patch.object(mvm_mod, "libvirt") as mock_libvirt:
                mock_conn = MagicMock()
                mock_conn.listAllDomains.return_value = [FakeDomain("dummy")]
                mock_libvirt.open.return_value = mock_conn
                mock_libvirt.VIR_DOMAIN_RUNNING = 1
                self.mvm = LinuxQemuMvm(self.logger)

        def test_vm_config_path(self):
            p = self.mvm._vm_config_path("foo")
            self.assertEqual(p, Path.home() / "mvm_vms" / "foo.json")

        def test_qmp_socket_path(self):
            p = self.mvm._qmp_socket_path("foo")
            self.assertEqual(p, self.mvm._qmp_socket_dir / "foo.sock")

        @patch("pathlib.Path.mkdir")
        def test_ensure_qmp_dir(self, mock_mkdir):
            self.mvm._ensure_qmp_dir()
            mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)

        @patch("builtins.open", new_callable=mock_open, read_data='{"memory": 2048}')
        @patch("pathlib.Path.exists", return_value=True)
        def test_load_config(self, mock_exists, mock_file):
            cfg = self.mvm._load_config("foo")
            self.assertEqual(cfg["memory"], 2048)

        @patch("pathlib.Path.exists", return_value=False)
        def test_load_config_missing(self, mock_exists):
            with self.assertRaises(ValueError):
                self.mvm._load_config("missing")

        @patch("subprocess.run")
        def test_get_pid_from_name_found(self, mock_run):
            mock_run.return_value = MagicMock(returncode=0, stdout="12345\n")
            self.assertEqual(self.mvm._get_pid_from_name("myvm"), 12345)

        @patch("subprocess.run")
        def test_get_pid_from_name_not_found(self, mock_run):
            mock_run.return_value = MagicMock(returncode=1, stdout="")
            self.assertIsNone(self.mvm._get_pid_from_name("myvm"))


    @unittest.skipUnless(sys.platform.lower().startswith("linux"), "Requires Linux")
    class TestVMState(unittest.TestCase):
        def test_constants(self):
            self.assertEqual(VMState.RUNNING, "running")
            self.assertEqual(VMState.STOPPED, "stopped")
            self.assertEqual(VMState.PAUSED, "paused")
            self.assertEqual(VMState.UNKNOWN, "unknown")


if __name__ == "__main__":
    unittest.main(verbosity=2)