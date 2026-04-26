"""
PyLintIface — deterministic, JSON‑safe Pylint interface for use under pytest
"""

import sys
import json
import contextlib
from io import StringIO

from pylint.lint import Run
from pylint.reporters.json_reporter import JSONReporter


# ---------------------------------------------------------------------------
# Stream patching helper
# ---------------------------------------------------------------------------

@contextlib.contextmanager
def _patch_streams(out):
    old_stdout = sys.stdout
    old_stderr = sys.stderr
    sys.stderr = sys.stdout = out
    try:
        yield
    finally:
        sys.stderr = old_stderr
        sys.stdout = old_stdout


# ---------------------------------------------------------------------------
# Deterministic JSON‑safe reporter
# ---------------------------------------------------------------------------

class AjsonReporter(JSONReporter):
    """
    JSON reporter that returns a list of plain dicts instead of Message objects.
    This makes the output stable and JSON‑serializable across Pylint versions.
    """

    def get_messages(self):
        out = []
        for m in self.messages:
            out.append({
                "msg_id": m.msg_id,
                "symbol": m.symbol,
                "message": m.msg,
                "path": m.path,
                "line": m.line,
                "column": m.column,
                "category": m.category,
                "confidence": m.confidence,
            })
        return out


# ---------------------------------------------------------------------------
# Standalone function interface
# ---------------------------------------------------------------------------
def processFile(filename, compiledPackages="PyQt5,PyQt4"):
    out = StringIO()
    reporter = AjsonReporter(out)

    with _patch_streams(out):
        try:
            Run([filename, "--extension-pkg-whitelist=" + compiledPackages,
                           "--ignored-modules=psutil,requests,pywin32,win32security,win32process,win32api",
                           "--ignore-paths=*/ui/*$", "--recursive=y",
                           "--ignore=,__pycache__,.pytest_cache,.qtcreator"],
                reporter=reporter,
                exit=False)
        except SystemExit as e:
            # Handle the exit code gracefully
            print(f"Pylint failed with exit code: {e.code}")
            # perform any necessary logging or cleanup
            # do not re-raise SystemExit

    messages = reporter.get_messages()
    return messages   # <-- FIXED


# ---------------------------------------------------------------------------
# Class‑based interface (for integration into larger systems)
# ---------------------------------------------------------------------------

class PylintIface:
    """
    Class wrapper for Pylint processing with deterministic JSON output.
    """

    acquiredData = {}

    def __init__(self, compiledPackages: str = "PySide6"):
        self.compiledPackages = compiledPackages
        self.args = ["--extension-pkg-whitelist=" + self.compiledPackages,
                     "--ignored-modules=psutil,requests,pywin32,win32security,win32process,win32api",
                     "--ignore-paths=*/ui/*$", "--recursive=y",
                     "--ignore=,__pycache__,.pytest_cache,.qtcreator"]

    @contextlib.contextmanager
    def _patch_streams(self, out):
        old_stdout = sys.stdout
        old_stderr = sys.stderr
        sys.stderr = sys.stdout = out
        try:
            yield
        finally:
            sys.stderr = old_stderr
            sys.stdout = old_stdout

    class AjsonReporter(JSONReporter):
        def get_messages(self):
            out = []
            for m in self.messages:
                out.append({
                    "msg_id": m.msg_id,
                    "symbol": m.symbol,
                    "message": m.msg,
                    "path": m.path,
                    "line": m.line,
                    "column": m.column,
                    "category": m.category,
                    "confidence": m.confidence,
                })
            return out

    def processFile(self, filename):
        out = StringIO()
        areporter = self.AjsonReporter(out)

        with self._patch_streams(out):
            try:
                Run([filename] + self.args, reporter=areporter, exit=False)
                #Run([filename] + self.args, reporter=areporter)
            except SystemExit as e:
                # Handle the code gracefully
                print(f"Pylint failed with exit code: {e.code}")
                # perform logging and cleanup as necessary
                # Do not re-raise the exception

        messages = areporter.get_messages()
        self.acquiredData[filename] = messages
        return messages   # <-- FIXED

