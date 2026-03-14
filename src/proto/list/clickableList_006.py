#!/usr/bin/env python3

import sys

from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QListView,
    QFileSystemModel,
    QStackedWidget,
    QWidget,
    QVBoxLayout,
    QLabel,
    QMessageBox
)

from PySide6.QtCore import QDir


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Stacked List Example")

        # Stacked widget
        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        # ---- PAGE 1 (Directory list) ----
        page1 = QWidget()
        layout1 = QVBoxLayout(page1)

        self.model = QFileSystemModel()
        self.model.setRootPath(QDir.currentPath())

        self.view = QListView()
        self.view.setModel(self.model)
        self.view.setRootIndex(self.model.index(QDir.currentPath()))

        layout1.addWidget(self.view)

        # ---- PAGE 2 (Placeholder page) ----
        page2 = QWidget()
        layout2 = QVBoxLayout(page2)
        layout2.addWidget(QLabel("Second Page"))

        # Add pages
        self.stack.addWidget(page1)
        self.stack.addWidget(page2)

        # Connect signals
        self.view.clicked.connect(self.item_clicked)
        self.view.doubleClicked.connect(self.item_double_clicked)

    def item_clicked(self, index):
        name = self.model.fileName(index)
        print("Clicked:", name)

    def item_double_clicked(self, index):
        name = self.model.fileName(index)

        QMessageBox.information(
            self,
            "Item Selected",
            f"You double-clicked:\n{name}"
        )


if __name__ == "__main__":

    app = QApplication(sys.argv)

    window = MainWindow()
    window.resize(500, 400)
    window.show()

    sys.exit(app.exec())

