import os, sys, argparse, time
import _thread
from socket import *
import client as clientModule
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtGui import QTextCursor
from PyQt5.QtCore import Qt, pyqtSlot

import queue

chatClient = object()

class GUIWindow(object):
    user_id = 0
    clientOK = False
    dest_user = ""

    def __init__(self, args, MainWindow):
        self.mainwindow = MainWindow
        self.init_gui(args)
        self.messageQueue = queue.Queue()

    def init_gui(self, args):
        self.mainwindow.setObjectName("MainWindow")
        self.mainwindow.resize(794, 649)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(10, 10, 101, 21))
        self.label.setObjectName("label")
        # self.spinBox = QtWidgets.QSpinBox(self.centralwidget)
        # self.spinBox.setGeometry(QtCore.QRect(90, 40, 141, 31))
        # self.spinBox.setMaximum(50)
        # self.spinBox.setObjectName("spinBox")
        # self.spinBox.valueChanged.connect(self.spinBoxChanged)
        # self.label_2 = QtWidgets.QLabel(self.centralwidget)
        # self.label_2.setGeometry(QtCore.QRect(10, 40, 101, 21))
        # self.label_2.setObjectName("label_2")
        self.textBrowser = QtWidgets.QTextBrowser(self.centralwidget)
        self.textBrowser.setGeometry(QtCore.QRect(10, 80, 771, 481))
        self.textBrowser.setObjectName("textBrowser")
        self.textEdit = QtWidgets.QTextEdit(self.centralwidget) #username
        self.textEdit.setGeometry(QtCore.QRect(110, 40, 151, 31))
        self.textEdit.setObjectName("textEdit")
        self.label_3 = QtWidgets.QLabel(self.centralwidget)
        self.label_3.setGeometry(QtCore.QRect(10, 40, 101, 21))
        self.label_3.setObjectName("label_3")
        self.textEdit_2 = QtWidgets.QTextEdit(self.centralwidget) #message
        self.textEdit_2.setGeometry(QtCore.QRect(110, 570, 581, 31))
        self.textEdit_2.setObjectName("textEdit_2")
        self.textEdit_2.setReadOnly(True)
        self.pushButton = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton.setGeometry(QtCore.QRect(670, 30, 113, 51))
        self.pushButton.setObjectName("pushButton")
        self.pushButton.clicked.connect(self.operateClient)
        self.pushButton_2 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_2.setGeometry(QtCore.QRect(711, 565, 75, 41))
        self.pushButton_2.setObjectName("pushButton_2")
        self.pushButton_2.clicked.connect(self.sendText)
        self.pushButton_3 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_3.setGeometry(QtCore.QRect(560, 30, 113, 51))
        self.pushButton_3.setObjectName("pushButton")
        self.pushButton_3.clicked.connect(self.listLookUp)
        # self.pushButton_4 = QtWidgets.QPushButton(self.centralwidget)
        # self.pushButton_4.setGeometry(QtCore.QRect(640, 565, 75, 41))
        # self.pushButton_4.setObjectName("pushButton_4")
        # self.pushButton_4.clicked.connect(self.sendFile)
        self.mainwindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(self.mainwindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 794, 22))
        self.menubar.setObjectName("menubar")
        self.mainwindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(self.mainwindow)
        self.statusbar.setObjectName("statusbar")
        self.mainwindow.setStatusBar(self.statusbar)

        self.qb = ComboBox(self.centralwidget)
        self.qb.setGeometry(QtCore.QRect(10, 570, 100, 30))
        self.qb.popupAboutToBeShown.connect(self.qbSelected)
        self.qb.currentTextChanged.connect(self.setUser)



        self.retranslateUi()
        QtCore.QMetaObject.connectSlotsByName(self.mainwindow)

        self.mainwindow.show()


    def retranslateUi(self):
        _translate = QtCore.QCoreApplication.translate
        self.mainwindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.label.setText(_translate("MainWindow", "Chat Client"))
        self.textBrowser.setHtml(_translate("MainWindow", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'.AppleSystemUIFont\'; font-size:13pt; font-weight:400; font-style:normal;\">\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p></body></html>"))
        self.label_3.setText(_translate("MainWindow", "User Name"))
        self.pushButton.setText(_translate("MainWindow", "Enter"))
        self.pushButton_2.setText(_translate("MainWindow", "Send"))
        self.pushButton_3.setText(_translate("MainWindow", "List"))
        # self.pushButton_4.setText(_translate("MainWindow", "File"))

    def spinBoxChanged(self):
        self.user_id = self.spinBox.value()

    def operateClient(self):
        _thread.start_new_thread(self.operateClientThread, ())

    def operateClientThread(self):
        self.textEdit_2.setReadOnly(False)
        args.user = int(self.user_id)
        args.cli = 0
        if(self.textEdit.toPlainText() == ''):
            self.statusbar.showMessage("set username")
        else:
            args.username = self.textEdit.toPlainText()
            global chatClient
            chatClient = clientModule.ChatClient(self, args)

    def sendText(self):
        message = self.textEdit_2.toPlainText()
        if(message == ''):
            # self.statusbar.showMessage("message blanked!")
            pass
        else:
            if self.clientOK:
                self.messageQueue.put([self.dest_user, message, 0])
                self.textEdit_2.setText('')
    
    def sendFile(self):
        message = self.textEdit_2.toPlainText()
        self.openFileNameDialog()
        # self.openFileNamesDialog()
        # self.saveFileDialog()

    def openFileNameDialog(self):
        options = QtWidgets.QFileDialog.Options()
        options |= QtWidgets.QFileDialog.DontUseNativeDialog
        fileName, _ = QtWidgets.QFileDialog.getOpenFileName(self.mainwindow,"QFileDialog.getOpenFileName()", "","All Files (*);;Python Files (*.py)", options=options)
        if fileName and self.clientOK:
            if self.dest_user != "":
                self.messageQueue.put([self.dest_user, fileName, 1])
        
    
    def openFileNamesDialog(self): # not use yet
        options = QtWidgets.QFileDialog.Options()
        options |= QtWidgets.QFileDialog.DontUseNativeDialog
        files, _ = QtWidgets.QFileDialog.getOpenFileNames(self.mainwindow,"QFileDialog.getOpenFileNames()", "","All Files (*);;Python Files (*.py)", options=options)
        if files:
            print(files)
    
    def saveFileDialog(self): # not use yet
        options = QtWidgets.QFileDialog.Options()
        options |= QtWidgets.QFileDialog.DontUseNativeDialog
        fileName, _ = QtWidgets.QFileDialog.getSaveFileName(self.mainwindow,"QFileDialog.getSaveFileName()","","All Files (*);;Text Files (*.txt)", options=options)
        if fileName:
            print(fileName)

    def listLookUp(self):
        try:
            udpSock = socket(AF_INET, SOCK_DGRAM) # UDP
            destinationAddr = '13.125.249.160'
            data = "###LIST###".encode('utf-8')
            udpSock.sendto(data, (destinationAddr, args.port + 1))
            data, address = udpSock.recvfrom(args.max_data_recv)
            self.textBrowser.append(data.decode())
        except OSError as e:
            print(e)

    def qbSelected(self):
        try:
            self.qb.clear()
            udpSock = socket(AF_INET, SOCK_DGRAM) # UDP
            destinationAddr = '13.125.249.160'
            data = "###LIST###".encode('utf-8')
            udpSock.sendto(data, (destinationAddr, args.port + 1))
            data, address = udpSock.recvfrom(args.max_data_recv)
            data = data.decode()
            userlist = []
            if data == 'empty':
                self.textBrowser.append("[SYSTEM] no one connected")
            else:
                userlist = data.split('\n')
            for user in userlist:
                self.qb.addItem(user)
        except OSError as e:
            print(e)
    
    def setUser(self, selected_user):
        self.dest_user = selected_user

class ComboBox(QtWidgets.QComboBox):
    popupAboutToBeShown = QtCore.pyqtSignal()

    def showPopup(self):
        self.popupAboutToBeShown.emit()
        super(ComboBox, self).showPopup()


def exitHandle():
    print("EXT")
    try:
        chatClient.hello()
        chatClient.offClient()
    except AttributeError as e:
        print("no")
        pass

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--client', action='store_true', default=False)
    parser.add_argument('--backlog', type=int, default=50) # how many pending connection queue will hold
    parser.add_argument('--max_data_recv', type=int, default=1460) # byte
    parser.add_argument('--port', type=int, default=8081) # server port
    parser.add_argument('--user', type=int, default=-1)
    args = parser.parse_args()

    app = QtWidgets.QApplication(sys.argv)
    app.aboutToQuit.connect(exitHandle)
    MainWindow = QtWidgets.QMainWindow()
    ui = GUIWindow(args, MainWindow)

    sys.exit(app.exec_())
