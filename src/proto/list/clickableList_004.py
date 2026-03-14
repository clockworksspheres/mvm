#!/usr/bin/env python3

import sys
from PySide6.QtWidgets import QApplication, QListView
from PySide6.QtWidgets import QFileSystemModel
from PySide6.QtCore import QDir

app = QApplication(sys.argv)

model = QFileSystemModel()
model.setRootPath(QDir.currentPath())

view = QListView()
view.setModel(model)
view.setRootIndex(model.index(QDir.currentPath()))

view.resize(500, 400)
view.show()

sys.exit(app.exec())

