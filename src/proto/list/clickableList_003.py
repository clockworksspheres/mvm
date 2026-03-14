#!/usr/bin/env python3

import sys
import os

from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QListWidget,
    QMessageBox
)


class MainWindow(QMainWindow):

    def __init__(self, path="."):
        super().__init__()

        self.setWindowTitle("Directory Browser")

        self.list_widget = QListWidget()
        self.setCentralWidget(self.list_widget)

        self.current_path = os.path.abspath(path)

        # double click handler
        self.list_widget.itemDoubleClicked.connect(self.open_item)

        self.load_directory(self.current_path)

    def load_directory(self, path):
        self.current_path = path
        self.list_widget.clear()

        self.setWindowTitle(path)

        # allow going up
        if os.path.dirname(path) != path:
            self.list_widget.addItem("..")

        for item in sorted(os.listdir(path)):
            self.list_widget.addItem(item)

    def open_item(self, item):

        name = item.text()

        if name == "..":
            new_path = os.path.dirname(self.current_path)
        else:
            new_path = os.path.join(self.current_path, name)

        if os.path.isdir(new_path):
            self.load_directory(new_path)
        else:
            QMessageBox.information(
                self,
                "File Selected",
                f"File:\n{new_path}"
            )


if __name__ == "__main__":

    app = QApplication(sys.argv)

    window = MainWindow(".")
    window.resize(400, 300)
    window.show()

    sys.exit(app.exec())

