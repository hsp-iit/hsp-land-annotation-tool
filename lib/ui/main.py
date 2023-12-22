# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'lib/ui/main.ui'
#
# Created by: PyQt5 UI code generator 5.14.1
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(912, 557)
        MainWindow.setStyleSheet("    background-color: rgb(255, 255, 255);\n"
"")
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.lblImage1 = QtWidgets.QLabel(self.centralwidget)
        self.lblImage1.setGeometry(QtCore.QRect(30, 70, 411, 281))
        self.lblImage1.setText("")
        self.lblImage1.setPixmap(QtGui.QPixmap(":/frame/frame-002561.jpg"))
        self.lblImage1.setScaledContents(True)
        self.lblImage1.setObjectName("lblImage1")
        self.lblImage2 = QtWidgets.QLabel(self.centralwidget)
        self.lblImage2.setGeometry(QtCore.QRect(470, 70, 411, 281))
        self.lblImage2.setText("")
        self.lblImage2.setPixmap(QtGui.QPixmap(":/result/frame-002561.jpg"))
        self.lblImage2.setScaledContents(True)
        self.lblImage2.setObjectName("lblImage2")
        self.cmbItems = QtWidgets.QComboBox(self.centralwidget)
        self.cmbItems.setGeometry(QtCore.QRect(30, 20, 211, 31))
        self.cmbItems.setObjectName("cmbItems")
        self.cmbResult = QtWidgets.QComboBox(self.centralwidget)
        self.cmbResult.setGeometry(QtCore.QRect(670, 20, 211, 31))
        self.cmbResult.setObjectName("cmbResult")
        self.frame = QtWidgets.QFrame(self.centralwidget)
        self.frame.setGeometry(QtCore.QRect(30, 360, 851, 61))
        self.frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame.setLineWidth(1)
        self.frame.setObjectName("frame")
        self.pushButton = QtWidgets.QPushButton(self.frame)
        self.pushButton.setGeometry(QtCore.QRect(10, 10, 151, 41))
        self.pushButton.setStyleSheet("QPushButton {\n"
"    color: white;\n"
"    background-color: rgb(58, 134, 255);\n"
"    border-radius: 5px;\n"
"    font: bold\n"
"}\n"
"\n"
"QPushButton:pressed {\n"
"    background-color: rgb(120, 180, 255);\n"
"\n"
"}")
        self.pushButton.setObjectName("pushButton")
        self.pushButton_2 = QtWidgets.QPushButton(self.frame)
        self.pushButton_2.setGeometry(QtCore.QRect(170, 10, 151, 41))
        self.pushButton_2.setStyleSheet("QPushButton {\n"
"    color: white;\n"
"    background-color: rgb(58, 134, 255);\n"
"    border-radius: 5px;\n"
"    font: bold\n"
"}\n"
"\n"
"QPushButton:pressed {\n"
"    background-color: rgb(120, 180, 255);\n"
"\n"
"}")
        self.pushButton_2.setObjectName("pushButton_2")
        self.pushButton_8 = QtWidgets.QPushButton(self.frame)
        self.pushButton_8.setGeometry(QtCore.QRect(330, 10, 186, 41))
        self.pushButton_8.setStyleSheet("QPushButton {\n"
"    color: white;\n"
"    background-color: rgb(58, 134, 255);\n"
"    border-radius: 5px;\n"
"    font: bold\n"
"}\n"
"\n"
"QPushButton:pressed {\n"
"    background-color: rgb(120, 180, 255);\n"
"\n"
"}")
        self.pushButton_8.setObjectName("pushButton_8")
        self.frame_2 = QtWidgets.QFrame(self.centralwidget)
        self.frame_2.setGeometry(QtCore.QRect(30, 430, 851, 61))
        self.frame_2.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_2.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_2.setLineWidth(1)
        self.frame_2.setObjectName("frame_2")
        self.pushButton_3 = QtWidgets.QPushButton(self.frame_2)
        self.pushButton_3.setGeometry(QtCore.QRect(10, 10, 151, 41))
        self.pushButton_3.setStyleSheet("QPushButton {\n"
"    color: white;\n"
"    background-color: rgb(58, 134, 255);\n"
"    border-radius: 5px;\n"
"    font: bold\n"
"}\n"
"\n"
"QPushButton:pressed {\n"
"    background-color: rgb(120, 180, 255);\n"
"\n"
"}")
        self.pushButton_3.setObjectName("pushButton_3")
        self.pushButton_4 = QtWidgets.QPushButton(self.frame_2)
        self.pushButton_4.setGeometry(QtCore.QRect(170, 10, 151, 41))
        self.pushButton_4.setStyleSheet("QPushButton {\n"
"    color: white;\n"
"    background-color: rgb(58, 134, 255);\n"
"    border-radius: 5px;\n"
"    font: bold\n"
"}\n"
"\n"
"QPushButton:pressed {\n"
"    background-color: rgb(120, 180, 255);\n"
"\n"
"}")
        self.pushButton_4.setObjectName("pushButton_4")
        self.pushButton_5 = QtWidgets.QPushButton(self.frame_2)
        self.pushButton_5.setGeometry(QtCore.QRect(330, 10, 151, 41))
        self.pushButton_5.setStyleSheet("QPushButton {\n"
"    color: white;\n"
"    background-color: rgb(58, 134, 255);\n"
"    border-radius: 5px;\n"
"    font: bold\n"
"}\n"
"\n"
"QPushButton:pressed {\n"
"    background-color: rgb(120, 180, 255);\n"
"\n"
"}")
        self.pushButton_5.setObjectName("pushButton_5")
        self.pushButton_6 = QtWidgets.QPushButton(self.frame_2)
        self.pushButton_6.setGeometry(QtCore.QRect(490, 10, 151, 41))
        self.pushButton_6.setStyleSheet("QPushButton {\n"
"    color: white;\n"
"    background-color: rgb(58, 134, 255);\n"
"    border-radius: 5px;\n"
"    font: bold\n"
"}\n"
"\n"
"QPushButton:pressed {\n"
"    background-color: rgb(120, 180, 255);\n"
"\n"
"}")
        self.pushButton_6.setObjectName("pushButton_6")
        self.btnAddItem = QtWidgets.QPushButton(self.centralwidget)
        self.btnAddItem.setGeometry(QtCore.QRect(250, 20, 151, 31))
        self.btnAddItem.setStyleSheet("QPushButton {\n"
"    color: white;\n"
"    background-color: rgb(58, 134, 255);\n"
"    border-radius: 5px;\n"
"    font: bold\n"
"}\n"
"\n"
"QPushButton:pressed {\n"
"    background-color: rgb(120, 180, 255);\n"
"\n"
"}")
        self.btnAddItem.setObjectName("btnAddItem")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 912, 22))
        self.menubar.setObjectName("menubar")
        self.menuFile = QtWidgets.QMenu(self.menubar)
        self.menuFile.setObjectName("menuFile")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.menuOpen = QtWidgets.QAction(MainWindow)
        self.menuOpen.setObjectName("menuOpen")
        self.menuFile.addAction(self.menuOpen)
        self.menubar.addAction(self.menuFile.menuAction())

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.pushButton.setText(_translate("MainWindow", "< Prev"))
        self.pushButton_2.setText(_translate("MainWindow", "Next >"))
        self.pushButton_8.setText(_translate("MainWindow", "Next >"))
        self.pushButton_3.setText(_translate("MainWindow", "Select Start Frame"))
        self.pushButton_4.setText(_translate("MainWindow", "Select End Frame"))
        self.pushButton_5.setText(_translate("MainWindow", "Process"))
        self.pushButton_6.setText(_translate("MainWindow", "Refine"))
        self.btnAddItem.setText(_translate("MainWindow", "Add Item"))
        self.menuFile.setTitle(_translate("MainWindow", "File"))
        self.menuOpen.setText(_translate("MainWindow", "Open.."))


class mainProgram(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self, parent = None, args = None):
        super(mainProgram, self).__init__(parent)

        self.setupUi(self)
        # self.setFixedSize(self.size())

import sys

if __name__ == "__main__":
        print(4)
        
        app = QtWidgets.QApplication(sys.argv)
        mainGui = mainProgram()
        mainGui.show()
        
        sys.exit(app.exec_())
