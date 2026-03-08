#!/usr/bin/env python3
import subprocess
import argparse
import re
import sys

from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QTextBrowser,
    QMainWindow, QMenuBar
)
from PySide6.QtGui import (QFont, QKeySequence, QShortcut, QAction)


# ---------------------------------------------------------
# SimpleConsole with monospace + zoom + shortcuts
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
        QShortcut(QKeySequence("Ctrl+0"), self, activated=self.reset_zoom)
        QShortcut(QKeySequence("Ctrl+L"), self, activated=self.clear_console)

    def append_html(self, html):
        self.append(html)

    def zoom_in(self):
        self.font_size += 1
        self._apply_font()

    def zoom_out(self):
        if self.font_size > 6:
            self.font_size -= 1
        self._apply_font()

    def reset_zoom(self):
        self.font_size = 12
        self._apply_font()

    def clear_console(self):
        self.clear()

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
# GUI mode with menu bar
# ---------------------------------------------------------
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.console = SimpleConsole()

        container = QWidget()
        layout = QVBoxLayout(container)
        layout.addWidget(self.console)

        self.setCentralWidget(container)
        self.setWindowTitle("UTM VM Status")

        # Menu bar
        menubar = QMenuBar()
        view_menu = menubar.addMenu("View")

        act_zoom_in = QAction("Zoom In", self)
        act_zoom_in.triggered.connect(self.console.zoom_in)
        view_menu.addAction(act_zoom_in)

        act_zoom_out = QAction("Zoom Out", self)
        act_zoom_out.triggered.connect(self.console.zoom_out)
        view_menu.addAction(act_zoom_out)

        act_reset = QAction("Reset Zoom", self)
        act_reset.triggered.connect(self.console.reset_zoom)
        view_menu.addAction(act_reset)

        act_clear = QAction("Clear Console", self)
        act_clear.triggered.connect(self.console.clear_console)
        view_menu.addAction(act_clear)

        self.setMenuBar(menubar)

        # Fill console with VM info
        vms = utm_list()
        for vm in vms:
            uuid = vm["uuid"]
            name = vm["name"]

            state, ip = utm_status(uuid)
            state = state or vm["state"]
            ip = ip or "no-ip"

            self.console.append_html(f"{name} | {state} | {ip}")


def gui_mode():
    app = QApplication([])
    window = MainWindow()
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

