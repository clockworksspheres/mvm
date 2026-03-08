#!/usr/bin/env python3
import subprocess
import argparse
import re
import sys

from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QTextBrowser,
    QMainWindow
)
from PySide6.QtGui import (
    QFont, QShortcut, QAction, QKeySequence
)
from PySide6.QtCore import Qt


# ---------------------------------------------------------
# SimpleConsole with monospace + zoom helpers
# ---------------------------------------------------------
class SimpleConsole(QTextBrowser):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.font_size = 12
        font = QFont("Menlo")
        font.setStyleHint(QFont.Monospace)
        font.setFixedPitch(True)
        font.setPointSize(self.font_size)
        self.setFont(font)

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
# UTM helpers
# ---------------------------------------------------------
def run_cmd(cmd):
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        return ""
    return result.stdout


def utm_list():
    output = run_cmd(["utmctl", "list"])
    lines = output.splitlines()
    vms = []

    if len(lines) <= 1:
        return vms

    for line in lines[1:]:
        parts = line.split()
        if len(parts) < 3:
            continue
        uuid = parts[0]
        state = parts[1]
        name = " ".join(parts[2:])
        vms.append({"uuid": uuid, "state": state, "name": name})

    return vms


def utm_status(uuid):
    output = run_cmd(["utmctl", "status", uuid])
    ip = None
    state = None

    for line in output.splitlines():
        line = line.strip()
        if line.startswith("State:"):
            state = line.split(":", 1)[1].strip()
        m = re.search(r"(\d+\.\d+\.\d+\.\d+)", line)
        if m:
            ip = m.group(1)

    return state, ip


# ---------------------------------------------------------
# CLI mode
# ---------------------------------------------------------
def cli_mode():
    parser = argparse.ArgumentParser(description="List UTM VMs")
    parser.add_argument("-a", "--all", action="store_true")
    args = parser.parse_args()

    vms = utm_list()
    if not vms:
        print("No VMs found.")
        return

    for vm in vms:
        uuid = vm["uuid"]
        name = vm["name"]
        state, ip = utm_status(uuid)
        state = state or vm["state"]
        ip = ip or "no-ip"
        print(f"{name} | {state} | {ip}")


# ---------------------------------------------------------
# GUI mode with menu bar + working Ctrl shortcuts
# ---------------------------------------------------------
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.console = SimpleConsole(self)

        container = QWidget(self)
        layout = QVBoxLayout(container)
        layout.addWidget(self.console)
        self.setCentralWidget(container)

        self.setWindowTitle("UTM VM Status")

        # -------------------------------
        # MENU BAR
        # -------------------------------
        menubar = self.menuBar()
        menubar.setNativeMenuBar(False)

        view_menu = menubar.addMenu("View")

        # Zoom In
        act_zoom_in = QAction("Zoom In", self)
        act_zoom_in.triggered.connect(self.console.zoom_in)
        view_menu.addAction(act_zoom_in)

        # Zoom Out
        act_zoom_out = QAction("Zoom Out", self)
        act_zoom_out.triggered.connect(self.console.zoom_out)
        view_menu.addAction(act_zoom_out)

        # Reset Zoom
        act_reset = QAction("Reset Zoom", self)
        act_reset.triggered.connect(self.console.reset_zoom)
        view_menu.addAction(act_reset)

        # Clear Console
        act_clear = QAction("Clear Console", self)
        act_clear.triggered.connect(self.console.clear_console)
        view_menu.addAction(act_clear)

        # -------------------------------
        # REAL FIX: UNAMBIGUOUS SHORTCUTS
        # -------------------------------
        QShortcut(QKeySequence(Qt.CTRL | Qt.Key_Equal), self, activated=self.console.zoom_in)
        QShortcut(QKeySequence(Qt.CTRL | Qt.Key_Plus), self, activated=self.console.zoom_in)

        QShortcut(QKeySequence(Qt.CTRL | Qt.Key_Minus), self, activated=self.console.zoom_out)

        QShortcut(QKeySequence(Qt.CTRL | Qt.Key_0), self, activated=self.console.reset_zoom)

        QShortcut(QKeySequence(Qt.CTRL | Qt.Key_L), self, activated=self.console.clear_console)

        # -------------------------------
        # Fill console
        # -------------------------------
        vms = utm_list()
        for vm in vms:
            uuid = vm["uuid"]
            name = vm["name"]
            state, ip = utm_status(uuid)
            state = state or vm["state"]
            ip = ip or "no-ip"
            self.console.append_html(f"{name} | {state} | {ip}")


def gui_mode():
    app = QApplication(sys.argv)

    # CRITICAL FIX FOR MACOS:
    app.setAttribute(Qt.AA_MacDontSwapCtrlAndMeta, True)

    window = MainWindow()
    window.resize(800, 400)
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

