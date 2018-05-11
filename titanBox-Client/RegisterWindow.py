from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QStatusBar, QLabel, QLineEdit
import sys
from PyQt5 import QtGui
import socket
import json
from UserPortal import UserPortal
from werkzeug.security import generate_password_hash
from Home import Home
from PyQt5.QtGui import QPixmap,QFont
import Encryption

host = 'localhost'
port = 5000
key = b'5478691234567869'


class RegisterWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.title = 'TitanBox - Client'
        self.left = 10
        self.top = 10
        self.width = 640
        self.height = 400


        label = QLabel(self)
        pixmap = QPixmap('background.jpg')
        label.resize(pixmap.width(), pixmap.height())
        label.setPixmap(pixmap)

        self.error = QLabel("",self)
        self.error.move(220,80)
        self.error.resize(280,40)

        self.username = QLineEdit(self)
        self.username.setToolTip("username")
        self.username.move(180,140)
        self.username.resize(280,40)

        self.password = QLineEdit(self)
        self.password.setToolTip("password")
        self.password.move(180,200)
        self.password.resize(280,40)
        self.password.setEchoMode(QLineEdit.Password)
        self.password.returnPressed.connect(self.register_clicked)

        self.register = QPushButton("Register",self)
        self.register.setStyleSheet("background-color: #AED6F1")
        self.register.move(180,260)
        self.register.resize(280,40)
        self.register.clicked.connect(self.register_clicked)

        self.home = QPushButton("Home",self)
        self.home.setStyleSheet("background-color: #AED6F1")
        self.home.move(520,20)
        self.home.clicked.connect(self.home_clicked)

        self.setStyleSheet("QStatusBar { color: 'white'}")

        self.initUI()

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left,self.top,self.width,self.height)

    def showStatus(self,msg):
        self.statusBar().showMessage(msg)
        QApplication.processEvents()

    def showError(self,msg):
        newFont = QFont('Times',20,QFont.Bold)
        self.error.setFont(newFont)
        self.error.setText(msg)

    def register_clicked(self):
        username = self.username.text()
        password = self.password.text()
        if username == "":
            self.showStatus("Username required!")
            return
        if password == "":
            self.showStatus("Password required!")
            return
        self.register.setDisabled(True)
        data = {'header' : 'Register','username':username,'password':password}
        jsonObj = json.dumps(data)
        msg = jsonObj.encode('utf-8')
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((host,port))
        cipher = Encryption.encrypt(msg,key)
        client.send(cipher)
        cipher = client.recv(1024)
        client.close()
        msg = Encryption.decrypt(cipher,key)
        jsonObj = msg.decode('utf-8')
        data = json.loads(jsonObj)
        if data['status'] == 200:
            self.showError("<font color=#229954>Registration Successful</font>")
        elif data['status'] == 201:
            self.showError("<font color = 'red'>User Exists</font>")
        self.register.setDisabled(False)
        client.close()

    def home_clicked(self):
        self.home = Home()
        self.home.show()
        self.close()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = RegisterWindow()
    window.show()
    sys.exit(app.exec_())