#!/usr/bin/env python3

import sys
from PySide6.QtWidgets import (
    QApplication,
    QListView,
    QMessageBox
)
from PySide6.QtWidgets import QFileSystemModel
from PySide6.QtCore import QDir


app = QApplication(sys.argv)

model = QFileSystemModel()
model.setRootPath(QDir.currentPath())

view = QListView()
view.setModel(model)
view.setRootIndex(model.index(QDir.currentPath()))
view.resize(500, 400)


# SINGLE CLICK
def item_clicked(index):
    name = model.fileName(index)
    print("Clicked:", name)


# DOUBLE CLICK
def item_double_clicked(index):
    name = model.fileName(index)

    QMessageBox.information(
        view,
        "Item Selected",
        f"You double-clicked:\n{name}"
    )


view.clicked.connect(item_clicked)
view.doubleClicked.connect(item_double_clicked)

view.show()

sys.exit(app.exec())

