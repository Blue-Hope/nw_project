import os, sys, argparse, time
import _thread
from socket import *
import server as serverModule
import client as clientModule
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QPushButton
from PyQt5.QtCore import Qt, pyqtSlot

class GUIWindow(QWidget):
    def __init__(self, args):
        super().__init__()
        self.init_gui(args)

    def init_gui(self, args):
        self.setGeometry(200, 200, 800, 600)
        self.setWindowTitle('ChatProgram')

        self.lb1 = QLabel(self)
        self.lb1.setText('1. select chat type')
        self.lb1.setGeometry(13, 5, 130, 15)

        self.lb2 = QLabel(self)
        self.lb2.setText('2. content')
        self.lb2.setGeometry(13, 40, 400, 400)

        # #wg1
        # self.wg1 = QWidget(parent=self, flags=Qt.Widget)
        # self.wg1.setGeometry(10, 10, 100, 100)
        # self.wg1.setStyleSheet("background-color: yellow")
        
        # #wg2
        # self.wg2 = QWidget(parent=self, flags=Qt.Widget)
        # self.wg2.setGeometry(50, 50, 200, 200)
        # self.wg2.setStyleSheet("background-color: red")

        # #wg3
        # self.wg3 = QWidget(parent=self, flags=Qt.Widget)
        # self.wg3.setGeometry(100, 100, 100, 100)
        # self.wg3.setStyleSheet("background-color: green")

        self.btn1 = Button(parent=self, text='server')
        self.btn1.setGeometry(5, 20, 100, 40)
        self.btn2 = Button(parent=self, text='client')
        self.btn2.setGeometry(105, 20, 100, 40)

        self.show()

    def operateServer(self):
        _thread.start_new_thread(self.operateServerThread, ())
    
    def operateServerThread(self):
        chatServer = serverModule.ChatServer(self, args)

    def operateClient(self):
        _thread.start_new_thread(self.operateClientThread, ())
    
    def operateClientThread(self):
        chatClient = clientModule.ChatClient(self, args)


class Button(QPushButton):
    _rendered_msg = ""

    def __init__(self, parent, text):
        self.parent = parent
        QPushButton.__init__(self, parent=parent)
        
        self.setText(text)

        if text == 'server':
            self.pressed.connect(self._pressed_server)
        if text == 'client': 
            self.pressed.connect(self._pressed_client)

    @pyqtSlot()
    def _pressed_server(self):
        self.parent.operateServer()

    @pyqtSlot()
    def _pressed_client(self):
        self.parent.operateClient()
        
        


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--client', action='store_true', default=False)
    parser.add_argument('--backlog', type=int, default=50) # how many pending connection queue will hold
    parser.add_argument('--max_data_recv', type=int, default=4096) # byte
    parser.add_argument('--port', type=int, default=8081) # server port
    parser.add_argument('--user', type=int, default=-1)
    args = parser.parse_args()

    app = QApplication(sys.argv)
    ex = GUIWindow(args)
    
    sys.exit(app.exec_())