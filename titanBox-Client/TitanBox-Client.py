from PyQt5 import QtGui
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QLabel
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import  QIcon, QPixmap
import sys
import socket
import json
from UserPortal import UserPortal
from Home import  Home
import Encryption

host = 'localhost'
port = 5000
key = b'5478691234567869'

class Main(QMainWindow):

    def __init__(self):
        super().__init__()
        self.title = "TitanBox-Client"
        self.left = 10
        self.top = 10
        self.width = 640
        self.height = 480

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.show_window)
        self.timer.start(1000)

        self.initUI()

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left,self.top,self.width,self.height)

        self.setWindowIcon(QtGui.QIcon('image.jpeg'))

        label = QLabel(self)
        pixmap = QPixmap('image.jpeg')

        label.resize(pixmap.width(),pixmap.height())

        label.setPixmap(pixmap)
        self.resize(pixmap.width(),pixmap.height())

        self.show()

    def show_window(self):
        self.timer.stop()
        data = {'header' : 'Somebody logged in?'}
        jsonObj = json.dumps(data)
        msg = jsonObj.encode('utf-8')
        cipher = Encryption.encrypt(msg,key)
        client = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        client.connect((host,port))
        client.send(cipher)
        cipher = client.recv(1024)
        msg = Encryption.decrypt(cipher,key)
        client.close()
        jsonObj = msg.decode('utf-8')
        data = json.loads(jsonObj)
        if data['answer'] == 'YES':
            self.userportal = UserPortal()
            self.userportal.show()
            self.close()
        else:
            self.home = Home()
            self.home.show()
            self.close()

if __name__ == "__main__":
    App = QApplication(sys.argv)
    main = Main()
    sys.exit(App.exec_())
