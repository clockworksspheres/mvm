#!/usr/bin/env python3

import sys
from PySide6.QtWidgets import QApplication, QListWidget, QMainWindow


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.list = QListWidget()

        self.list.addItems([
            "Item One",
            "Item Two",
            "Item Three",
            "Item Four"
        ])

        # Connect click signal
        self.list.itemClicked.connect(self.item_clicked)

        self.setCentralWidget(self.list)

    def item_clicked(self, item):
        print("Clicked:", item.text())


app = QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec()

