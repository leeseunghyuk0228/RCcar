# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'mainUI.ui'
##
## Created by: Qt User Interface Compiler version 6.5.0
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide2.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide2.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide2.QtWidgets import (QApplication, QCheckBox, QLCDNumber, QLabel,
    QMainWindow, QMenuBar, QPushButton, QSizePolicy,
    QSlider, QStatusBar, QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(865, 686)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.label = QLabel(self.centralwidget)
        self.label.setObjectName(u"label")
        self.label.setGeometry(QRect(30, 20, 111, 51))
        font = QFont()
        font.setFamilies([u"Segoe Print"])
        font.setPointSize(24)
        self.label.setFont(font)
        self.label_2 = QLabel(self.centralwidget)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setGeometry(QRect(380, 20, 171, 51))
        self.label_2.setFont(font)
        self.label_3 = QLabel(self.centralwidget)
        self.label_3.setObjectName(u"label_3")
        self.label_3.setGeometry(QRect(30, 290, 181, 51))
        self.label_3.setFont(font)
        self.label_4 = QLabel(self.centralwidget)
        self.label_4.setObjectName(u"label_4")
        self.label_4.setGeometry(QRect(390, 280, 141, 51))
        self.label_4.setFont(font)
        self.horizontalSlider = QSlider(self.centralwidget)
        self.horizontalSlider.setObjectName(u"horizontalSlider")
        self.horizontalSlider.setGeometry(QRect(389, 110, 311, 71))
        self.horizontalSlider.setMinimum(300)
        self.horizontalSlider.setMaximum(440)
        self.horizontalSlider.setValue(375)
        self.horizontalSlider.setOrientation(Qt.Horizontal)
        self.Display_Speed = QLCDNumber(self.centralwidget)
        self.Display_Speed.setObjectName(u"Display_Speed")
        self.Display_Speed.setGeometry(QRect(30, 90, 281, 111))
        self.GoBtn = QPushButton(self.centralwidget)
        self.GoBtn.setObjectName(u"GoBtn")
        self.GoBtn.setGeometry(QRect(50, 380, 271, 51))
        self.StopBtn = QPushButton(self.centralwidget)
        self.StopBtn.setObjectName(u"StopBtn")
        self.StopBtn.setGeometry(QRect(50, 440, 271, 51))
        self.SppedUpBtn = QPushButton(self.centralwidget)
        self.SppedUpBtn.setObjectName(u"SppedUpBtn")
        self.SppedUpBtn.setGeometry(QRect(50, 500, 61, 81))
        self.SpeedDownBtn = QPushButton(self.centralwidget)
        self.SpeedDownBtn.setObjectName(u"SpeedDownBtn")
        self.SpeedDownBtn.setGeometry(QRect(120, 500, 61, 81))
        self.MotorFBtn = QPushButton(self.centralwidget)
        self.MotorFBtn.setObjectName(u"MotorFBtn")
        self.MotorFBtn.setGeometry(QRect(190, 500, 61, 81))
        self.MotorBBtn = QPushButton(self.centralwidget)
        self.MotorBBtn.setObjectName(u"MotorBBtn")
        self.MotorBBtn.setGeometry(QRect(260, 500, 61, 81))
        self.Display_Camera = QLabel(self.centralwidget)
        self.Display_Camera.setObjectName(u"label_5")
        self.Display_Camera.setGeometry(QRect(330, 300, 500, 400))
        font1 = QFont()
        font1.setPointSize(20)
        self.Display_Camera.setFont(font1)
        self.Display_Camera.setMargin(80)
        self.seeCamera = QCheckBox(self.centralwidget)
        self.seeCamera.setObjectName(u"seeCamera")
        self.seeCamera.setGeometry(QRect(540, 300, 141, 20))
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 865, 22))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        self.GoBtn.clicked.connect(MainWindow.go)
        self.StopBtn.clicked.connect(MainWindow.stop)
        self.SppedUpBtn.pressed.connect(MainWindow.speedup)
        self.SpeedDownBtn.pressed.connect(MainWindow.speeddown)
        self.MotorFBtn.clicked.connect(MainWindow.motorf)
        self.MotorBBtn.clicked.connect(MainWindow.motorb)
        self.SpeedDownBtn.released.connect(MainWindow.downreleased)
        self.SppedUpBtn.released.connect(MainWindow.upreleased)
        self.seeCamera.clicked.connect(MainWindow.isCamera)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.label.setText(QCoreApplication.translate("MainWindow", u"Speed", None))
        self.label_2.setText(QCoreApplication.translate("MainWindow", u"Direction", None))
        self.label_3.setText(QCoreApplication.translate("MainWindow", u"Command", None))
        self.label_4.setText(QCoreApplication.translate("MainWindow", u"Camera", None))
        self.GoBtn.setText(QCoreApplication.translate("MainWindow", u"Go", None))
        self.StopBtn.setText(QCoreApplication.translate("MainWindow", u"Stop", None))
        self.SppedUpBtn.setText(QCoreApplication.translate("MainWindow", u"Speed-U", None))
        self.SpeedDownBtn.setText(QCoreApplication.translate("MainWindow", u"Speed-D", None))
        self.MotorFBtn.setText(QCoreApplication.translate("MainWindow", u"Motor-F", None))
        self.MotorBBtn.setText(QCoreApplication.translate("MainWindow", u"Motor-B", None))
        self.Display_Camera.setText(QCoreApplication.translate("MainWindow", u"Waiting Camera...", None))
        self.seeCamera.setText(QCoreApplication.translate("MainWindow", u"Live Streaming", None))
    # retranslateUi
