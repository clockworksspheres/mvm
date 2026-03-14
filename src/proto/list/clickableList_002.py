#!/usr/bin/env python3

import sys
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QListWidget,
    QMessageBox
)


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Clickable List Example")

        self.list_widget = QListWidget()

        self.list_widget.addItems([
            "Apple",
            "Banana",
            "Cherry",
            "Orange"
        ])

        # Single click
        self.list_widget.itemClicked.connect(self.on_click)

        # Double click
        self.list_widget.itemDoubleClicked.connect(self.on_double_click)

        self.setCentralWidget(self.list_widget)

    def on_click(self, item):
        print("Clicked:", item.text())

    def on_double_click(self, item):
        QMessageBox.information(
            self,
            "Item Selected",
            f"You double-clicked: {item.text()}"
        )


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = MainWindow()
    window.resize(300, 200)
    window.show()

    sys.exit(app.exec())

