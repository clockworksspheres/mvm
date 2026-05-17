# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'mainwindow.ui'
##
## Created by: Qt User Interface Compiler version 6.10.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QAction, QBrush, QColor, QConicalGradient,
    QCursor, QFont, QFontDatabase, QGradient,
    QIcon, QImage, QKeySequence, QLinearGradient,
    QPainter, QPalette, QPixmap, QRadialGradient,
    QTransform)
from PySide6.QtWidgets import (QApplication, QComboBox, QGridLayout, QLabel,
    QLineEdit, QMainWindow, QMenu, QMenuBar,
    QPushButton, QRadioButton, QSizePolicy, QSpacerItem,
    QStackedWidget, QStatusBar, QTextBrowser, QVBoxLayout,
    QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(652, 448)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(MainWindow.sizePolicy().hasHeightForWidth())
        MainWindow.setSizePolicy(sizePolicy)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        sizePolicy.setHeightForWidth(self.centralwidget.sizePolicy().hasHeightForWidth())
        self.centralwidget.setSizePolicy(sizePolicy)
        self.gridLayout = QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName(u"gridLayout")
        self.hypervisorLabel = QLabel(self.centralwidget)
        self.hypervisorLabel.setObjectName(u"hypervisorLabel")

        self.gridLayout.addWidget(self.hypervisorLabel, 0, 0, 1, 1)

        self.runPushButton = QPushButton(self.centralwidget)
        self.runPushButton.setObjectName(u"runPushButton")

        self.gridLayout.addWidget(self.runPushButton, 7, 0, 1, 1)

        self.quitPushButton = QPushButton(self.centralwidget)
        self.quitPushButton.setObjectName(u"quitPushButton")

        self.gridLayout.addWidget(self.quitPushButton, 8, 0, 1, 1)

        self.vmNameLineEdit = QLineEdit(self.centralwidget)
        self.vmNameLineEdit.setObjectName(u"vmNameLineEdit")

        self.gridLayout.addWidget(self.vmNameLineEdit, 5, 0, 1, 1)

        self.hypervisorComboBox = QComboBox(self.centralwidget)
        self.hypervisorComboBox.setObjectName(u"hypervisorComboBox")

        self.gridLayout.addWidget(self.hypervisorComboBox, 1, 0, 1, 1)

        self.horizontalSpacer_3 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout.addItem(self.horizontalSpacer_3, 13, 4, 1, 1)

        self.stackedWidget = QStackedWidget(self.centralwidget)
        self.stackedWidget.setObjectName(u"stackedWidget")
        sizePolicy.setHeightForWidth(self.stackedWidget.sizePolicy().hasHeightForWidth())
        self.stackedWidget.setSizePolicy(sizePolicy)
        self.page = QWidget()
        self.page.setObjectName(u"page")
        self.headlessRadioButton = QRadioButton(self.page)
        self.headlessRadioButton.setObjectName(u"headlessRadioButton")
        self.headlessRadioButton.setGeometry(QRect(20, 20, 99, 20))
        self.stackedWidget.addWidget(self.page)
        self.page_2 = QWidget()
        self.page_2.setObjectName(u"page_2")
        self.hardRadioButton = QRadioButton(self.page_2)
        self.hardRadioButton.setObjectName(u"hardRadioButton")
        self.hardRadioButton.setGeometry(QRect(20, 20, 99, 20))
        self.stackedWidget.addWidget(self.page_2)
        self.page_4 = QWidget()
        self.page_4.setObjectName(u"page_4")
        self.stackedWidget.addWidget(self.page_4)
        self.page_3 = QWidget()
        self.page_3.setObjectName(u"page_3")
        self.verticalLayout = QVBoxLayout(self.page_3)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.textBrowser = QTextBrowser(self.page_3)
        self.textBrowser.setObjectName(u"textBrowser")

        self.verticalLayout.addWidget(self.textBrowser)

        self.stackedWidget.addWidget(self.page_3)

        self.gridLayout.addWidget(self.stackedWidget, 1, 2, 11, 3)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout.addItem(self.horizontalSpacer, 13, 2, 1, 1)

        self.actionComboBox = QComboBox(self.centralwidget)
        self.actionComboBox.setObjectName(u"actionComboBox")

        self.gridLayout.addWidget(self.actionComboBox, 3, 0, 1, 1)

        self.actionLabel = QLabel(self.centralwidget)
        self.actionLabel.setObjectName(u"actionLabel")

        self.gridLayout.addWidget(self.actionLabel, 2, 0, 1, 1)

        self.vmNameLabel = QLabel(self.centralwidget)
        self.vmNameLabel.setObjectName(u"vmNameLabel")

        self.gridLayout.addWidget(self.vmNameLabel, 4, 0, 1, 1)

        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout.addItem(self.horizontalSpacer_2, 13, 3, 1, 1)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.gridLayout.addItem(self.verticalSpacer, 9, 0, 1, 1)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 652, 39))
        self.menuvmctl = QMenu(self.menubar)
        self.menuvmctl.setObjectName(u"menuvmctl")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.menubar.addAction(self.menuvmctl.menuAction())

        self.retranslateUi(MainWindow)

        self.stackedWidget.setCurrentIndex(3)


        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.hypervisorLabel.setText(QCoreApplication.translate("MainWindow", u"Hypervisor", None))
        self.runPushButton.setText(QCoreApplication.translate("MainWindow", u"Run Action", None))
        self.quitPushButton.setText(QCoreApplication.translate("MainWindow", u"Quit", None))
        self.headlessRadioButton.setText(QCoreApplication.translate("MainWindow", u"Headless", None))
        self.hardRadioButton.setText(QCoreApplication.translate("MainWindow", u"Hard", None))
        self.actionLabel.setText(QCoreApplication.translate("MainWindow", u"Action", None))
        self.vmNameLabel.setText(QCoreApplication.translate("MainWindow", u"virtual machine name", None))
        self.menuvmctl.setTitle(QCoreApplication.translate("MainWindow", u"vmctl", None))
    # retranslateUi

