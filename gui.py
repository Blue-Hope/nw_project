import os, sys, argparse, time
import _thread
from socket import *
import server as serverModule
import client as clientModule
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt, pyqtSlot

import queue

class GUIWindow(object):
    user_id = 0

    def __init__(self, args, MainWindow):
        self.init_gui(args, MainWindow)
        self.messageQueue = queue.Queue()

    def init_gui(self, args, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(794, 649)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(10, 10, 101, 21))
        self.label.setObjectName("label")
        self.spinBox = QtWidgets.QSpinBox(self.centralwidget)
        self.spinBox.setGeometry(QtCore.QRect(90, 40, 141, 31))
        self.spinBox.setMaximum(50)
        self.spinBox.setObjectName("spinBox")
        self.spinBox.valueChanged.connect(self.spinBoxChanged)
        self.label_2 = QtWidgets.QLabel(self.centralwidget)
        self.label_2.setGeometry(QtCore.QRect(10, 40, 101, 21))
        self.label_2.setObjectName("label_2")
        self.textBrowser = QtWidgets.QTextBrowser(self.centralwidget)
        self.textBrowser.setGeometry(QtCore.QRect(10, 80, 771, 481))
        self.textBrowser.setObjectName("textBrowser")
        self.textEdit = QtWidgets.QTextEdit(self.centralwidget)
        self.textEdit.setGeometry(QtCore.QRect(330, 40, 151, 31))
        self.textEdit.setObjectName("textEdit")
        self.label_3 = QtWidgets.QLabel(self.centralwidget)
        self.label_3.setGeometry(QtCore.QRect(250, 40, 101, 21))
        self.label_3.setObjectName("label_3")
        self.textEdit_2 = QtWidgets.QTextEdit(self.centralwidget)
        self.textEdit_2.setGeometry(QtCore.QRect(10, 570, 701, 31))
        self.textEdit_2.setObjectName("textEdit_2")
        self.pushButton = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton.setGeometry(QtCore.QRect(670, 30, 113, 51))
        self.pushButton.setObjectName("pushButton")
        self.pushButton.clicked.connect(self.operateClient)
        self.pushButton_2 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_2.setGeometry(QtCore.QRect(711, 565, 75, 41))
        self.pushButton_2.setObjectName("pushButton_2")
        self.pushButton_2.clicked.connect(self.sendText)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 794, 22))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

        MainWindow.show()


    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.label.setText(_translate("MainWindow", "Chat Client v1.0"))
        self.label_2.setText(_translate("MainWindow", "User Select"))
        self.textBrowser.setHtml(_translate("MainWindow", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'.AppleSystemUIFont\'; font-size:13pt; font-weight:400; font-style:normal;\">\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p></body></html>"))
        self.label_3.setText(_translate("MainWindow", "User Name"))
        self.pushButton.setText(_translate("MainWindow", "Enter"))
        self.pushButton_2.setText(_translate("MainWindow", "Send"))

    def spinBoxChanged(self):
        self.user_id = self.spinBox.value()
    
    def operateClient(self):
        _thread.start_new_thread(self.operateClientThread, ())
    
    def operateClientThread(self):
        args.user = int(self.user_id)
        if(self.textEdit.toPlainText() == ''):
            self.statusbar.showMessage("set username")
        else:
            args.username = self.textEdit.toPlainText()
            chatClient = clientModule.ChatClient(self, args)
    
    def sendText(self):
        message = self.textEdit_2.toPlainText()
        if(message == ''):
            self.statusbar.showMessage("message blanked!")
        else:
            self.messageQueue.put(message)
            self.textEdit_2.setText('')

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--client', action='store_true', default=False)
    parser.add_argument('--backlog', type=int, default=50) # how many pending connection queue will hold
    parser.add_argument('--max_data_recv', type=int, default=4096) # byte
    parser.add_argument('--port', type=int, default=8081) # server port
    parser.add_argument('--user', type=int, default=-1)
    args = parser.parse_args()

    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = GUIWindow(args, MainWindow)
    
    
    sys.exit(app.exec_())