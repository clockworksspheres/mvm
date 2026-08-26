
"""

Only accessed from ../vmctl.py - Only access this file from one directory up...

"""

import sys
import psutil
import re
from argparse import Namespace

from pathlib import Path

parent_dir = Path(__file__).parent.parent
sys.path.append(str(parent_dir))

from PySide6.QtWidgets import (QApplication, QMainWindow)
from PySide6.QtGui import QAction, QShortcut, QKeySequence
from PySide6.QtCore import Qt

from ui.ui_mainwindow import Ui_MainWindow
from ui.consoleDialog import ConsoleStream, ConsoleDialog

from mvm_run import mvm_run

from lib.loggers import CyLogger
from lib.loggers import LogPriority as lp
from lib.run_commands import start_detached, RunWith
from ui.SimpleConsole import SimpleConsole, ConsoleStream


class VmCtlUi(QMainWindow):
    """ 
    The Main Window dialog for the ramdisk.
    """
    def __init__(self):
        super().__init__()

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.logger = CyLogger()
        self.logger.initializeLogs()
        self.rw = RunWith(self.logger)

        # Platform-specific combo items
        platform = sys.platform.lower()

        self.setWindowTitle("vmctl UI")

        #####
        # Do not change the names in either dictionary in
        # any way, or this code will not work.  The strings
        # below must match the process name acquired by 
        # psutil.process_iter for the specific hypervisor.
        # -- If you change the selections here, change the
        # associated dictionaries in the spawn_vm method.
        if platform.lower().startswith("darwin"):
            self.ui.hypervisorComboBox.addItems(["VMware Fusion",
                                                 "UTM",
                                                 "VirtualBox"])
        elif platform.lower().startswith("win"):
            self.ui.hypervisorComboBox.addItems(["VMware Workstation",
                                                 "HyperV",
                                                 "VirtualBox"])
        elif platform.lower().startswith("linux"):
            self.ui.hypervisorComboBox.addItems(["VMware Workstation",
                                                 "VirtualBox"])            

        self.ui.actionComboBox.addItems(["start", "stop", "reset",
                                         "pause", "unpause",
                                         "status", "list"])
 
        # set the stacked widget to the index 0 for "start" action 
        self.ui.stackedWidget.setCurrentIndex(0)

        # Set the default state of the "hard" radio button to "selected"
        self.ui.hardRadioButton.setChecked(True)

        # Connect combo to stack
        self.ui.actionComboBox.currentIndexChanged.connect(self.handle_combo_action)

        # Connect run action button 
        self.ui.runPushButton.clicked.connect(self.spawn_action)

        # Connect quit action button 
        self.ui.quitPushButton.clicked.connect(QApplication.quit)

        # Remove the old QTextBrowser
        old = self.ui.textBrowser
        layout = old.parent().layout()
        layout.removeWidget(old)
        old.deleteLater()

        # Create and insert your custom console
        self.ui.textBrowser = SimpleConsole()
        self.ui.verticalLayout.addWidget(self.ui.textBrowser)

        # Create stdout/stderr streams
        self.stdout_stream = ConsoleStream(logfile="/tmp/logfile")
        self.stderr_stream = ConsoleStream(logfile="/tmp/logfile")

        self.stdout_stream.text_emitted.connect(self.ui.textBrowser.append_html)
        self.stderr_stream.text_emitted.connect(self.ui.textBrowser.append_html)

        # Redirect Python stdout/stderr
        sys.stdout = self.stdout_stream
        sys.stderr = self.stderr_stream

        # Initial messages
        # message = "Second post!!"
        # print("Application started.")
        # print(f"Argparse message: {message}")

        # add a menu
        menubar = self.ui.menubar
        menubar.setNativeMenuBar(False)

        # add view menu item
        view_menu = self.ui.menubar.addMenu("View")

        # Zoom In
        act_zoom_in = QAction("Zoom In", self)
        act_zoom_in.setShortcut("Ctrl++")
        act_zoom_in.triggered.connect(self.ui.textBrowser.zoom_in)
        view_menu.addAction(act_zoom_in)

        # Zoom Out
        act_zoom_out = QAction("Zoom Out", self)
        act_zoom_out.setShortcut("Ctrl+-")
        act_zoom_out.triggered.connect(self.ui.textBrowser.zoom_out)
        view_menu.addAction(act_zoom_out)

        # Reset Zoom
        act_reset = QAction("Reset Zoom", self)
        act_reset.setShortcut("Ctrl+0")
        act_reset.triggered.connect(self.ui.textBrowser.reset_zoom)
        view_menu.addAction(act_reset)

        # Clear Console
        act_clear = QAction("Clear Console  ", self)
        act_clear.setShortcut("Ctrl+L")
        act_clear.triggered.connect(self.ui.textBrowser.clear_console)
        view_menu.addAction(act_clear)

        # -------------------------------
        # REAL FIX: UNAMBIGUOUS SHORTCUTS
        # -------------------------------
        if sys.platform.lower().startswith("darwin"):
            # macOS: use Command
            QShortcut(QKeySequence(Qt.META | Qt.Key_Equal), self, activated=self.ui.textBrowser.zoom_in)
            QShortcut(QKeySequence(Qt.META | Qt.Key_Plus), self, activated=self.ui.textBrowser.zoom_in)
            QShortcut(QKeySequence(Qt.META | Qt.Key_Minus), self, activated=self.ui.textBrowser.zoom_out)
            QShortcut(QKeySequence(Qt.META | Qt.Key_0), self, activated=self.ui.textBrowser.reset_zoom)
            QShortcut(QKeySequence(Qt.META | Qt.Key_L), self, activated=self.ui.textBrowser.clear_console)

        else:
            # Windows/Linux: use Ctrl
            QShortcut(QKeySequence(Qt.CTRL | Qt.Key_Equal), self, activated=self.ui.textBrowser.zoom_in)
            QShortcut(QKeySequence(Qt.CTRL | Qt.Key_Plus), self, activated=self.ui.textBrowser.zoom_in)
            QShortcut(QKeySequence(Qt.CTRL | Qt.Key_Minus), self, activated=self.ui.textBrowser.zoom_out)
            QShortcut(QKeySequence(Qt.CTRL | Qt.Key_0), self, activated=self.ui.textBrowser.reset_zoom)
            QShortcut(QKeySequence(Qt.CTRL | Qt.Key_L), self, activated=self.ui.textBrowser.clear_console)

        #####
        # Connect the debug button signal to slot
        self.ui.debugPushButton.clicked.connect(self.onDebugPushButtonClicked)

        self.console_dialogs = []

        # Shared stream that all open dialogs listen to
        self.stream = ConsoleStream()

        # Redirect stdout & stderr to our stream
        sys.stdout = self.stream
        sys.stderr = self.stream

        if sys.platform.lower().startswith("win32"):
            # non-modal on Windows11 only works if None is passed in rather than self.
            # problem is, all windows have to be closed separately...
            # fixed - check out closeEvent method - QApplication.closeAllWindows()
            self.conDialog = ConsoleDialog(None, title=f"Console #{len(self.console_dialogs) + 1}")
        else:
            self.conDialog = ConsoleDialog(self, title=f"Console #{len(self.console_dialogs) + 1}")

    def handle_combo_action(self, index):
        """
        """
        if index == 0:
            self.ui.stackedWidget.setCurrentIndex(0)
        elif index in (1, 2):
            self.ui.stackedWidget.setCurrentIndex(1)
        elif index in (3, 4):
            self.ui.stackedWidget.setCurrentIndex(2)
        elif index in (5, 6):
            self.ui.stackedWidget.setCurrentIndex(3)
        else:
            raise IndexError
        if index == 6:
            self.ui.vmNameLabel.hide()
            self.ui.vmNameLineEdit.hide()

        else:
            self.ui.vmNameLabel.show()
            self.ui.vmNameLineEdit.show()

    def spawn_action(self):

        current_hypervisor_index = self.ui.hypervisorComboBox.currentIndex()
        current_hypervisor_name = self.ui.hypervisorComboBox.currentText()

        # build command
        if sys.platform.lower().startswith("darwin"):
            hypervisorMap = {"vmware": "VMware Fusion", "utm": "UTM", "virtualbox": "VirtualBox"}
            hyperMap = {0: "vmware", 1: "utm", 2: "virtualbox"}

        if sys.platform.lower().startswith("win"):
            hypervisorMap = {"vmware": "VMware Workstation", "hyperv": "Hyper-V", "virtualbox": "VBoxSDS.exe"}
            hyperMap = {0: "vmware", 1: "hyperv", 2: "virtualbox"}

        hypervisorApp = hypervisorMap[hyperMap[current_hypervisor_index]]

        print(f"Looking for: {hypervisorApp}")

        matched = None
        for proc in psutil.process_iter(['pid', 'name']):
            if hypervisorApp == proc.info['name'].strip():
                print(f"{proc.info['name']}")
                matched = proc.info['name']

                action = self.ui.actionComboBox.currentText().strip()

                vmach = self.ui.vmNameLineEdit.text().strip()

                args = Namespace(
                    command = action,
                    vm = vmach,
                    hypervisor = hyperMap[current_hypervisor_index],
                    headless = False,
                    hard = True,
                )
                self.ui.textBrowser.append("==================================================")
                returned = mvm_run(args)

                if returned:
                    print(f"{returned}")
                    self.ui.textBrowser.append(f"{returned}")

        if not matched:
            print(f"Hypervisor {current_hypervisor_name} not running, start {current_hypervisor_name} first")

    def onDebugPushButtonClicked(self, checked):
        #self.conDialog = ConsoleDialog(self, title=f"Console #{len(self.console_dialogs) + 1}")

        self.ui.debugPushButton.hide()

        # Connect this dialog to the shared stream
        self.stream.text_emitted.connect(self.conDialog.append_html)

        # Disconnect when the dialog is closed (prevents errors later)
        def on_finished():
            try:
                self.stream.text_emitted.disconnect(self.conDialog.append_html)
                self.ui.debugPushButton.show()
            except TypeError:
                pass  # already disconnected
            if dialog in self.console_dialogs:
                self.console_dialogs.remove(self.conDialog)

        self.conDialog.finished.connect(on_finished)

        self.console_dialogs.append(self.conDialog)
        self.conDialog.show()
        self.raise_()

    def closeEvent(self, event):
        if sys.platform.lower().startswith("win32"):
            # Required for the way the self.conDialog is instanciated on Windows
            QApplication.closeAllWindows()
        event.accept()  # Let the window close


if __name__=="__main__":
    app = QApplication(sys.argv)
    print("started app...")
    window = VmCtlUi()
    print("initiated window")
    window.show()
    print("showing window...")
    window.raise_()
    print("raising_ window")
    sys.exit(app.exec())

