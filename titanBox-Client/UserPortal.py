from PyQt5  import QtGui
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QListWidget, QMessageBox, QFileDialog, QInputDialog, QLineEdit , QProgressBar
import sys
import socket
import json
import Encryption
import codecs
import os
from Home import Home
from PyQt5.QtGui import QPixmap
import Encryption

host = 'localhost'
port = 5000
block_size = 800
KEY = b'5478691234567869'


class UserPortal(QMainWindow):

    def __init__(self):
        super().__init__()
        self.title = 'TitanBox - Client'
        self.left= 10
        self.top = 10
        self.width = 640
        self.height = 400


        label = QLabel(self)
        pixmap = QPixmap('background.jpg')
        label.resize(pixmap.width(), pixmap.height())
        label.setPixmap(pixmap)

        data = {'header' : 'who'}
        jsonObj = json.dumps(data)
        msg = jsonObj.encode('utf-8')
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((host,port))
        cipher = Encryption.encrypt(msg,KEY)
        client.send(cipher)

        cipher = client.recv(1024)
        msg = Encryption.decrypt(cipher,KEY)
        jsonObj = msg.decode('utf-8')
        data = json.loads(jsonObj)
        client.close()
        welcome = QLabel("Welcome "+ data['username'] + " !",self)
        welcome.move(20,20)
        welcome.resize(280,40)
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((host,port))
        data = {'header' : 'Show Files'}
        jsonObj = json.dumps(data)
        msg = jsonObj.encode('utf-8')
        cipher = Encryption.encrypt(msg,KEY)
        client.send(cipher)

        cipher = client.recv(1024)
        msg = Encryption.decrypt(cipher,KEY)
        jsonObj = msg.decode('utf-8')
        data = json.loads(jsonObj)
        list_of_files = data['List']
        client.close()
        self.list = QListWidget(self)
        self.list.move(10,100)
        self.list.resize(500,100)
        self.list.addItems(list_of_files)
        self.list.setSelectionMode(1)

        self.download = QPushButton("download",self)
        self.download.setStyleSheet("background-color: #AED6F1")
        self.download.move(520,100)
        self.download.clicked.connect(self.download_clicked)

        self.upload = QPushButton("+",self)
        self.upload.setStyleSheet("background-color: #AED6F1")
        self.upload.resize(620,40)
        self.upload.move(10,320)
        self.upload.clicked.connect(self.upload_clicked)

        self.logout = QPushButton("Logout",self)
        self.logout.setStyleSheet("background-color: #AED6F1")
        self.logout.move(540,10)
        self.logout.clicked.connect(self.logout_clicked)

        self.setStyleSheet("QStatusBar{color: 'white'}")

        self.initUI()
        client.close()

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left,self.top,self.width,self.height)

    def logout_clicked(self):
        data = {'header':'Logout'}
        jsonObj = json.dumps(data)
        msg = jsonObj.encode('utf-8')
        client = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        client.connect((host,port))
        cipher = Encryption.encrypt(msg,KEY)
        client.send(cipher)

        cipher = client.recv(1024)
        msg = Encryption.decrypt(cipher,KEY)
        jsonObj = msg.decode('utf-8')
        data = json.loads(jsonObj)
        if data['header'] == 'OK':
            self.home = Home()
            self.home.show()
            self.close()
        else :
            self.statusBar().showMessage("Error!")
            QApplication.processEvents()

    def lock_ui(self):
        self.upload.setDisabled(True)
        self.download.setDisabled(True)
        self.logout.setDisabled(True)

    def unlock_ui(self):
        self.upload.setDisabled(False)
        self.download.setDisabled(False)
        self.logout.setDisabled(False)

    def upload_clicked(self):
        self.lock_ui()
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        file_url,ok = QFileDialog.getOpenFileName(self,"Upload file","","All Files(*);;Text Files(*txt)",options = options)
        file_name = file_url.split('/')[-1]
        if ok:
            tmp,ok = QInputDialog.getText(self,"Master Password","Enter master password : ",echo = QLineEdit.Password)
            if ok:
                master_password = tmp
            else:
                self.unlock_ui()
                return
        else:
            self.unlock_ui()
            return

        file_tag = Encryption.generate_file_tag(file_url)
        data = {'header':'Match this file tag','tag':file_tag}
        jsonObj = json.dumps(data)
        msg = jsonObj.encode('utf-8')
        client = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        client.connect((host,port))
        cipher = Encryption.encrypt(msg,KEY)
        client.send(cipher)
        cipher = client.recv(1024)
        msg = Encryption.decrypt(cipher,KEY)
        client.close()
        jsonObj = msg.decode('utf-8')
        data = json.loads(jsonObj)
        if data['header'] == 'No need to upload':
            self.statusBar().showMessage('File is already uploaded!')
            QApplication.processEvents()
            self.unlock_ui()
            return
        elif data['header'] == 'POWVerification':
            #no need to upload file
            #only need to pass POW Verification
            self.statusBar().showMessage('Verifying Proof of Ownership')
            QApplication.processEvents()
            tmp = x = data['BlockNo.']
            buf = ""
            with open(file_url,'rb') as file_handle:
                buf = file_handle.read((int)(block_size/8))
                while len(buf) > 0:
                    x = x-1
                    if x==0:
                        break
                    buf = file_handle.read((int)(block_size/8))
            block_tag = Encryption.generate_block_tag(buf)
            data = {'header':'POWVerification','filetag':file_tag,'BlockNo.':tmp,'BlockTag':block_tag}
            jsonObj = json.dumps(data)
            msg = jsonObj.encode('utf-8')
            client = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
            client.connect((host,port))
            cipher = Encryption.encrypt(msg,KEY)
            client.send(cipher)
            cipher = client.recv(1024)
            msg = Encryption.decrypt(cipher,KEY)
            client.close()
            jsonObj = msg.decode('utf-8')
            data = json.loads(jsonObj)
            if data['Verified'] == 'YES':
                #Upload block keys one by one
                self.statusBar().showMessage('POW Verified!! Uploading block keys')
                QApplication.processEvents()
                total_blocks = os.stat(file_url).st_size / (int)(block_size / 8)
                count = 0
                with open(file_url,'rb') as file_handle:
                    buf = file_handle.read((int)(block_size/8))

                    while len(buf) > 0:
                        count += 1
                        self.statusBar().showMessage("Uploading keys ..." + str((count * 100) // total_blocks) + '%')
                        QApplication.processEvents()
                        block_tag = Encryption.generate_block_tag(buf)
                        master_key = Encryption.generate_key(master_password.encode('utf-8'))
                        plain_key = Encryption.generate_key(buf)
                        cipher_block = Encryption.encrypt(buf, plain_key)
                        cipher_key = Encryption.encrypt(plain_key, master_key)
                        data = {'header':'Block Keys','key':codecs.encode(cipher_key,'hex_codec').decode(),'tag':block_tag,'filename':file_name,'filetag':file_tag}
                        jsonObj = json.dumps(data)
                        msg = jsonObj.encode('utf-8')
                        client = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
                        client.connect((host,port))
                        cipher = Encryption.encrypt(msg,KEY)
                        client.send(cipher)
                        client.close()
                        buf = file_handle.read((int)(block_size/8))
            else:
                self.statusBar().showMessage('POW error!!')
                QApplication.processEvents()
                return
        elif data['header'] == 'Upload File':
            #start uploading file block by block
            self.statusBar().showMessage('Uploading file')
            QApplication.processEvents()
            total_blocks = os.stat(file_url).st_size/(int)(block_size/8)
            count = 0

            with open(file_url,'rb') as file_handle:
                buf = file_handle.read((int)(block_size/8))
                while len(buf) >0:
                    count+=1
                    self.statusBar().showMessage("Uploading file ..."+str((count*100)//total_blocks)+'%')
                    QApplication.processEvents()

                    block_tag = Encryption.generate_block_tag(buf)
                    master_key = Encryption.generate_key(master_password.encode('utf-8'))
                    plain_key = Encryption.generate_key(buf)
                    cipher_block = Encryption.encrypt(buf, plain_key)
                    cipher_key = Encryption.encrypt(plain_key, master_key)
                    data = {'header':'Match this block tag','tag':block_tag,'filename':file_name,'filetag':file_tag}
                    jsonObj = json.dumps(data)
                    msg = jsonObj.encode('utf-8')
                    client = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
                    client.connect((host,port))
                    cipher = Encryption.encrypt(msg,KEY)
                    client.send(cipher)
                    cipher = client.recv(1024)
                    msg = Encryption.decrypt(cipher,KEY)
                    client.close()
                    jsonObj = msg.decode('utf-8')
                    data = json.loads(jsonObj)
                    if data['Block Found'] == 'NO':
                        #Encrypt block and push block as well as key onto server
                        data = {'header':'Block','filename':file_name,'block':codecs.encode(cipher_block,'hex_codec').decode(),'key':codecs.encode(cipher_key,'hex_codec').decode(),'tag':block_tag,'filetag':file_tag}
                        jsonObj = json.dumps(data)
                        msg = jsonObj.encode('utf-8')
                        client = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
                        client.connect((host,port))
                        cipher = Encryption.encrypt(msg,KEY)
                        client.send(cipher)
                        client.close()
                        self.statusBar().showMessage('Block Uploaded!')
                        QApplication.processEvents()
                    else:
                        data = {'header':'Block Keys','filename':file_name,'tag':block_tag,'filetag':file_tag,'key':codecs.encode(cipher_key,'hex_codec').decode()}
                        jsonObj = json.dumps(data)
                        msg = jsonObj.encode('utf-8')
                        client = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
                        client.connect((host,port))
                        cipher = Encryption.encrypt(msg,KEY)
                        client.send(cipher)
                        client.close()
                        self.statusBar().showMessage('Block Key Uploaded')
                        QApplication.processEvents()
                    buf = file_handle.read((int)(block_size/8))
        self.userportal = UserPortal()
        self.userportal.show()
        self.userportal.statusBar().showMessage('File Uploaded Successfully!!')
        QApplication.processEvents()
        self.close()
        self.unlock_ui()

    def download_clicked(self):
        self.lock_ui()
        if self.list.selectedItems() == []:
            QMessageBox.about(self,"Error","No Item Selected")
            self.unlock_ui()
            return
        user_reply = QMessageBox.question(self,"Warning","This will remove file from server. Are you sure ?",QMessageBox.Yes|QMessageBox.No,QMessageBox.No)
        if user_reply == QMessageBox.No:
            self.unlock_ui()
            return
        else:
            options = QFileDialog.Options()
            options |= QFileDialog.DontUseNativeDialog
            filename,ok = QFileDialog.getSaveFileName(self,"Download file as","","All Files(*);;Text Files(*txt)",options = options)
            if ok:
                tmp,ok = QInputDialog.getText(self,"Master Password","Enter master password : ",echo =QLineEdit.Password)
                if ok:
                    master_password = tmp
                else:
                    self.unlock_ui()
                    return
            else:
                self.unlock_ui()
                return
                #Find how many blocks are in file

            data = {'header' : 'No. of blocks','filename' : self.list.currentItem().text()}
            jsonObj = json.dumps(data)
            msg = jsonObj.encode('utf-8')
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.connect((host,port))
            cipher = Encryption.encrypt(msg,KEY)
            client.send(cipher)

            cipher = client.recv(1024)
            msg = Encryption.decrypt(cipher,KEY)
            jsonObj = msg.decode('utf-8')
            data = json.loads(jsonObj)
            N = data['No. of blocks']
            client.close()
            master_key = Encryption.generate_key(master_password.encode('utf-8'))
            with open(filename,'wb') as file_handle:
                for i in range(N):
                    self.statusBar().showMessage('Downloading file ... ' + str((i*100)//N)+'%')
                    QApplication.processEvents()
                    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    client.connect((host,port))
                    data = {'header' : 'Send block','Block No.' : i+1,'filename':self.list.currentItem().text()}
                    jsonObj = json.dumps(data)
                    msg = jsonObj.encode('utf-8')
                    cipher = Encryption.encrypt(msg,KEY)
                    client.send(cipher)
                    #Server will send block content and block key
                    cipher = client.recv(1024)
                    msg = Encryption.decrypt(cipher,KEY)
                    jsonObj = msg.decode('utf-8')
                    data = json.loads(jsonObj)

                    key = Encryption.decrypt(codecs.decode(data['Block Key'],'hex_codec'),master_key)

                    plain_text = Encryption.decrypt(codecs.decode(data['Block Content'],'hex_codec'),key)
                    file_handle.write(plain_text)
                    client.close()
            client.close()

        data = {'header': 'Download Successful', 'filename': self.list.currentItem().text()}
        jsonObj = json.dumps(data)
        msg = jsonObj.encode('utf-8')
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((host, port))
        cipher = Encryption.encrypt(msg,KEY)
        client.send(cipher)
        cipher = ""
        while(cipher == ""):
            cipher = client.recv(1024)
            self.statusBar().showMessage("Server is deleting file")
        client.close()
        self.close()
        self.userportal = UserPortal()
        self.userportal.show()
        self.unlock_ui()
        self.userportal.statusBar().showMessage("File downloaded successfully!")
        QApplication.processEvents()

if __name__ == '__main__':
    App = QApplication(sys.argv)
    userportal = UserPortal()
    userportal.show()
    sys.exit(App.exec_())
