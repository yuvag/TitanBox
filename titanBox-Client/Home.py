from PyQt5 import QtGui
from PyQt5.QtWidgets import QPushButton, QApplication, QMainWindow, QLabel
from PyQt5.QtGui import QPixmap
import sys

class Home(QMainWindow):
    def __init__(self):
        super().__init__()
        self.title = "TitanBox-Client"
        self.left = 10
        self.top = 10
        self.width= 640
        self.height = 400

        label = QLabel(self)
        pixmap = QPixmap('background.jpg')
        label.resize(pixmap.width(),pixmap.height())
        label.setPixmap(pixmap)

        self.login = QPushButton("Login",self)
        self.login.setStyleSheet("background-color: #AED6F1")
        self.login.resize(160,40)
        self.login.move(220,180)
        self.login.clicked.connect(self.login_clicked)

        self.register = QPushButton("Register",self)
        self.register.setStyleSheet("background-color: #AED6F1")
        self.register.resize(160,40)
        self.register.move(220,240)
        self.register.clicked.connect(self.register_clicked)


        self.initUI()

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left,self.top,self.width,self.height)


    def login_clicked(self):
        from LoginWindow import  LoginWindow
        self.login = LoginWindow()
        self.login.show()
        self.close()

    def register_clicked(self):
        from RegisterWindow import RegisterWindow
        self.register = RegisterWindow()
        self.register.show()

        self.close()


if __name__ == "__main__":
    App = QApplication(sys.argv)
    home = Home()
    home.show()
    sys.exit(App.exec_())