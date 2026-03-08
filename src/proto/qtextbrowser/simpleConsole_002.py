#!/usr/bin/env python3
import subprocess
import argparse
import re
import sys

from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QTextBrowser
)
from PySide6.QtGui import QFont, QKeySequence, QShortcut


# ---------------------------------------------------------
# SimpleConsole with monospace + zoom controls + shortcuts
# ---------------------------------------------------------
class SimpleConsole(QTextBrowser):
    def __init__(self):
        super().__init__()

        self.font_size = 12
        font = QFont("Menlo")
        font.setStyleHint(QFont.Monospace)
        font.setFixedPitch(True)
        font.setPointSize(self.font_size)
        self.setFont(font)

        self.setOpenExternalLinks(True)
        self.setOpenLinks(True)

        # Keyboard shortcuts
        QShortcut(QKeySequence("Ctrl++"), self, activated=self.zoom_in)
        QShortcut(QKeySequence("Ctrl+="), self, activated=self.zoom_in)  # macOS quirk
        QShortcut(QKeySequence("Ctrl+-"), self, activated=self.zoom_out)

    def append_html(self, html):
        self.append(html)

    def zoom_in(self):
        self.font_size += 1
        self._apply_font()

    def zoom_out(self):
        if self.font_size > 6:
            self.font_size -= 1
        self._apply_font()

    def _apply_font(self):
        font = self.font()
        font.setPointSize(self.font_size)
        self.setFont(font)


# ---------------------------------------------------------
# UTM command helpers
# ---------------------------------------------------------
def run_cmd(cmd):
    """Run a command and return stdout, capturing stderr."""
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        return ""
    return result.stdout


# Parse "utmctl list" table format
def utm_list():
    output = run_cmd(["utmctl", "list"])
    lines = output.splitlines()

    vms = []

    # Skip header line
    for line in lines[1:]:
        parts = line.split()
        if len(parts) < 3:
            continue

        uuid = parts[0]
        state = parts[1]
        name = " ".join(parts[2:])  # handles names with spaces

        vms.append({"uuid": uuid, "state": state, "name": name})

    return vms


# Parse "utmctl status <uuid>" to extract IP
def utm_status(uuid):
    output = run_cmd(["utmctl", "status", uuid])

    ip = None
    state = None

    for line in output.splitlines():
        line = line.strip()

        if line.startswith("State:"):
            state = line.split(":", 1)[1].strip()

        # Extract IPv4 address
        m = re.search(r"(\d+\.\d+\.\d+\.\d+)", line)
        if m:
            ip = m.group(1)

    return state, ip


# ---------------------------------------------------------
# CLI mode (argparse)
# ---------------------------------------------------------
def cli_mode():
    parser = argparse.ArgumentParser(
        description="List all UTM VMs with name, state, and IP"
    )
    parser.add_argument(
        "-a", "--all",
        action="store_true",
        help="Show all VMs (default)"
    )
    args = parser.parse_args()

    vms = utm_list()

    if not vms:
        print("No VMs found or utmctl produced no output.")
        return

    for vm in vms:
        uuid = vm["uuid"]
        name = vm["name"]

        state, ip = utm_status(uuid)
        state = state or vm["state"]
        ip = ip or "no-ip"

        print(f"{name} | {state} | {ip}")


# ---------------------------------------------------------
# GUI mode
# ---------------------------------------------------------
def gui_mode():
    app = QApplication([])

    window = QWidget()
    layout = QVBoxLayout(window)

    console = SimpleConsole()
    layout.addWidget(console)

    btn_plus = QPushButton("Zoom +")
    btn_minus = QPushButton("Zoom -")
    layout.addWidget(btn_plus)
    layout.addWidget(btn_minus)

    btn_plus.clicked.connect(console.zoom_in)
    btn_minus.clicked.connect(console.zoom_out)

    # Fill console with VM info
    vms = utm_list()
    for vm in vms:
        uuid = vm["uuid"]
        name = vm["name"]

        state, ip = utm_status(uuid)
        state = state or vm["state"]
        ip = ip or "no-ip"

        console.append_html(f"{name} | {state} | {ip}")

    window.show()
    app.exec()


# ---------------------------------------------------------
# Entry point
# ---------------------------------------------------------
if __name__ == "__main__":
    if len(sys.argv) > 1:
        cli_mode()
    else:
        gui_mode()

