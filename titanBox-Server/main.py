import sys
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QMainWindow, QPlainTextEdit, QPushButton, QLabel, QLineEdit, QMessageBox
import LoginDBMaster
import FileDBMaster
import socket
import json
import threading
from PyQt5.QtCore import *
import traceback
import random
import Encryption

host = 'localhost'
port = 5000
KEY = b'5478691234567869'

server = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
server.bind((host,port))
server.listen(5)

string=""
users = 0
files = 0
blocks = 0
active_users = 0


class ServerSignals(QObject):
    log_changed = pyqtSignal()
    status_changed = pyqtSignal()
    records_changed = pyqtSignal()


class Server(QRunnable):

    def __init__(self):
        super(Server,self).__init__()
        self.signals = ServerSignals()

    @pyqtSlot()
    def run(self):
        global string,users,active_users,files,blocks
        string = "Server is running!"
        self.signals.log_changed.emit()
        users = LoginDBMaster.no_of_users()
        active_users = LoginDBMaster.no_of_active_users()
        files = FileDBMaster.no_of_files()
        blocks = FileDBMaster.no_of_blocks()
        self.signals.records_changed.emit()
        self.signals.status_changed.emit()
        #self.show_log("Server is running!")
        #self.show_stats(LoginDBMaster.no_of_users(), LoginDBMaster.no_of_active_users())
        #self.show_records(FileDBMaster.no_of_files(), FileDBMaster.no_of_blocks())
        while True:
            conn, addr = server.accept()
            cipher = conn.recv(1024)
            msg = Encryption.decrypt(cipher,KEY)
            jsonObj = msg.decode('utf-8')
            data = json.loads(jsonObj)
            if data['header'] == 'Login':
                string = "Login Request Received ,"+addr[0]
                self.signals.log_changed.emit()
                #self.show_log("Login Request Received" + addr[0])
                # Check if it is a valid username
                if LoginDBMaster.is_a_valid_user(data['username']) == False:
                    data = {'header': 'Login', 'status': 101}
                    string="Invalid username ,"+addr[0]
                    self.signals.log_changed.emit()
                    #self.show_log("Invalid username" + addr[0])
                    jsonObj = json.dumps(data)
                    msg = jsonObj.encode('utf-8')
                    cipher = Encryption.encrypt(msg,KEY)
                    conn.send(cipher)
                else:
                    # check whether password is correct or not
                    if LoginDBMaster.check(data['username'], data['password']):
                        # Check whether user is logged in somewhere or not
                        if LoginDBMaster.logged_in_somewhere(data['username']) == True:
                            #self.show_log("User logged in somewhere else" + addr[0])
                            string = "User logged in somewhere else ,"+addr[0]
                            self.signals.log_changed.emit()
                            data = {'header': 'Login', 'status': 103}
                            jsonObj = json.dumps(data)
                            msg = jsonObj.encode('utf-8')
                            cipher = Encryption.encrypt(msg,KEY)
                            conn.send(cipher)
                        else:
                            # Check whether some other user logged in on the machine
                            if LoginDBMaster.another_user_logged_in(addr[0]):
                                data = {'header': 'Login', 'status': 104}
                                jsonObj = json.dumps(data)
                                msg = jsonObj.encode('utf-8')
                                cipher = Encryption.encrypt(msg,KEY)
                                string = "Another user logged in ,"+addr[0]
                                self.signals.log_changed.emit()
                                #self.show_log("Another user logged in on the machine" + addr[0])
                                conn.send(cipher)
                            else:
                                LoginDBMaster.login(data['username'], addr[0])
                                data = {'header': 'Login', 'status': 100}
                                jsonObj = json.dumps(data)
                                msg = jsonObj.encode('utf-8')
                                cipher = Encryption.encrypt(msg,KEY)
                                string = "Successful login ,"+addr[0]
                                self.signals.log_changed.emit()
                                #self.show_log("Successful Login" + addr[0])
                                conn.send(cipher)
                                users = LoginDBMaster.no_of_users()
                                active_users = LoginDBMaster.no_of_active_users()
                                self.signals.status_changed.emit()
                                #self.show_stats(LoginDBMaster.no_of_users(), LoginDBMaster.no_of_active_users())
                    else:
                        string = "Invalid password ,"+addr[0]
                        self.signals.log_changed.emit()
                        #self.show_log("Invalid password" + addr[0])
                        data = {'header': 'Login', 'status': 102}
                        jsonObj = json.dumps(data)
                        msg = jsonObj.encode('utf-8')
                        cipher = Encryption.encrypt(msg,KEY)
                        conn.send(cipher)

            elif data['header'] == 'Register' :
                string = "Register Request Received ,"+addr[0]
                self.signals.log_changed.emit()
                if LoginDBMaster.is_a_valid_user(data['username']):
                    data = {'header' : 'Register','status':201}
                    jsonObj = json.dumps(data)
                    msg = jsonObj.encode('utf-8')
                    cipher = Encryption.encrypt(msg,KEY)
                    string = "Username exists "+addr[0]
                    self.signals.log_changed.emit()
                    conn.send(cipher)
                else:
                    LoginDBMaster.make_an_entry(data['username'],data['password'])
                    string = "Registration successful ,"+addr[0]
                    self.signals.log_changed.emit()
                    users = LoginDBMaster.no_of_users()
                    active_users = LoginDBMaster.no_of_active_users()
                    self.signals.status_changed.emit()
                    data = {'header' : 'Register','status':200}
                    jsonObj = json.dumps(data)
                    msg = jsonObj.encode('utf-8')
                    cipher = Encryption.encrypt(msg,KEY)
                    conn.send(cipher)

            elif data['header'] == 'who' :
                string = "Username required ,"+addr[0]
                self.signals.log_changed.emit()
                username = LoginDBMaster.username(addr[0])
                data = {'header' : 'who','username' : username}
                jsonObj = json.dumps(data)
                msg = jsonObj.encode('utf-8')
                cipher = Encryption.encrypt(msg,KEY)
                conn.send(cipher)
                string = "Username sent ,"+addr[0]
                self.signals.log_changed.emit()

            elif data['header'] == 'Show Files' :
                string = "Client is requesting list of files ,"+addr[0]
                self.signals.log_changed.emit()
                list_of_files = FileDBMaster.list_of_files(addr[0])
                data={'header':'Show Files','List':list_of_files}
                jsonObj = json.dumps(data)
                msg = jsonObj.encode('utf-8')
                cipher = Encryption.encrypt(msg,KEY)
                conn.send(cipher)
                string = "List of files sent ,"+addr[0]
                self.signals.log_changed.emit()

            elif data['header'] == 'No. of blocks':
                string = "Client is requesting no. of blocks ,"+addr[0]
                self.signals.log_changed.emit()
                N = FileDBMaster.block_count(data['filename'])
                data = {'header':'No. of blocks','No. of blocks' : N}
                jsonObj = json.dumps(data)
                msg = jsonObj.encode('utf-8')
                cipher = Encryption.encrypt(msg,KEY)
                conn.send(cipher)
                string = "No. of blocks told ,"+addr[0]
                self.signals.log_changed.emit()

            elif data['header'] == 'Logout':
                string = "Logout request received ,"+addr[0]
                self.signals.log_changed.emit()
                LoginDBMaster.logout(addr[0])
                active_users = LoginDBMaster.no_of_active_users()
                self.signals.status_changed.emit()
                data = {'header':'OK'}
                jsonObj = json.dumps(data)
                msg = jsonObj.encode('utf-8')
                cipher = Encryption.encrypt(msg,KEY)
                conn.send(cipher)
                string = "User successfully logged out ,"+addr[0]
                self.signals.log_changed.emit()

            elif data['header'] == 'Somebody logged in?':
                string = "Login Details required ,"+addr[0]
                self.signals.log_changed.emit()
                if LoginDBMaster.another_user_logged_in(addr[0]):
                    data = {'header':'Somebody logged in?','answer':'YES'}
                else:
                    data = {'header' : 'Somebody logged in?','answer':'NO'}
                jsonObj = json.dumps(data)
                msg = jsonObj.encode('utf-8')
                cipher = Encryption.encrypt(msg,KEY)
                conn.send(cipher)
                string = "Login Details sent ,"+addr[0]
                self.signals.log_changed.emit()

            elif data['header'] == 'Match this file tag':
                string = "File tag received for matching ,"+addr[0]
                self.signals.log_changed.emit()
                if FileDBMaster.match_file_tag(data['tag']):
                    #File already present in cloud POW verify the client
                    string = "File already present in cloud ,"+addr[0]
                    self.signals.log_changed.emit()
                    if FileDBMaster.do_user_have_file(data['tag'],addr[0])  :
                        data = {'header' : 'No need to upload'}
                        jsonObj = json.dumps(data)
                        msg = jsonObj.encode('utf-8')
                        cipher = Encryption.encrypt(msg,KEY)
                        conn.send(cipher)
                        string = 'User already possess the file' + addr[0]
                        self.signals.log_changed.emit()
                    else:
                        N = FileDBMaster.total_blocks(data['tag'])
                        x = random.randint(1,N)
                        data = {'header' : 'POWVerification','BlockNo.' : x}
                        jsonObj = json.dumps(data)
                        msg = jsonObj.encode('utf-8')
                        cipher = Encryption.encrypt(msg,KEY)
                        conn.send(cipher)
                        string = "Request for POW Verification sent ,"+addr[0]
                        self.signals.log_changed.emit()
                else:
                    #File is not present in the cloud
                    #Request client to upload file
                    string = "File not present in cloud ,"+addr[0]
                    self.signals.log_changed.emit()
                    data = {'header' : 'Upload File'}
                    jsonObj = json.dumps(data)
                    msg = jsonObj.encode('utf-8')
                    cipher = Encryption.encrypt(msg,KEY)
                    conn.send(cipher)
                    string = "Request for file upload sent ,"+addr[0]
                    self.signals.log_changed.emit()

            elif data['header'] == 'Match this block tag':
                string = "Block tag received for matching ,"+addr[0]
                self.signals.log_changed.emit()
                if FileDBMaster.match_block_tag(data['tag']):
                    string = "Block already present in cloud ,"+addr[0]
                    self.signals.log_changed.emit()
                    data = {'header':'Match this block tag','Block Found':'YES'}
                    jsonObj = json.dumps(data)
                    msg = jsonObj.encode('utf-8')
                    cipher = Encryption.encrypt(msg,KEY)
                    conn.send(cipher)
                    string = "Client not required to upload block ,"+addr[0]
                    self.signals.log_changed.emit()

                else:
                    string = "Block not present in cloud ,"+addr[0]
                    self.signals.log_changed.emit()
                    data = {'header':'Match this block tag','Block Found':'NO'}
                    jsonObj = json.dumps(data)
                    msg = jsonObj.encode('utf-8')
                    cipher = Encryption.encrypt(msg,KEY)
                    conn.send(cipher)
                    string = "Client required to upload block ,"+addr[0]
                    self.signals.log_changed.emit()

            elif data['header'] == 'Block':
                #Block is received
                string = "Block received ,"+addr[0]
                self.signals.log_changed.emit()
                FileDBMaster.push_block(data['block'],data['filename'],data['tag'],data['key'],addr[0],data['filetag'])
                string = "Block added to database "
                self.signals.log_changed.emit()
                files = FileDBMaster.no_of_files()
                blocks = FileDBMaster.no_of_blocks()
                self.signals.records_changed.emit()

            elif data['header'] == 'Block Key':
                #Block Key is received
                string = "Block Key received ,"+addr[0]
                self.signals.log_changed.emit()
                FileDBMaster.add_block_reference(data['tag'],addr[0],data['filetag'],data['filename'],data['key'])
                string = "Reference added to block ,"+addr[0]
                self.signals.log_changed.emit()
                files = FileDBMaster.no_of_files()
                blocks = FileDBMaster.no_of_blocks()
                self.signals.records_changed.emit()

            elif data['header'] == 'POWVerification':
                string = "Request for POW Verification received ,"+addr[0]
                self.signals.log_changed.emit()
                if FileDBMaster.verify(data['filetag'],data['BlockTag'],data['BlockNo.']):
                    string = "POW Verified ,"+addr[0]
                    self.signals.log_changed.emit()
                    FileDBMaster.add_file_reference(addr[0], data['filetag'])
                    data = {'header' : 'POWVerification','Verified':'YES'}

                else:
                    string = "POW not verified ,"+addr[0]
                    self.signals.log_changed.emit()
                    data={'header':'POWVerification','Verified':'NO'}
                jsonObj = json.dumps(data)
                msg = jsonObj.encode('utf-8')
                cipher = Encryption.encrypt(msg,KEY)
                conn.send(cipher)

            elif data['header'] == 'Block Keys':
                string = "Block Keys received ,"+addr[0]
                self.signals.log_changed.emit()
                FileDBMaster.add_key_reference(data['tag'],data['key'],addr[0])
                string = "Block Key added ,"+addr[0]
                self.signals.log_changed.emit()

            elif data['header'] == 'Send block':
                string = "Block required by client ,"+addr[0]
                self.signals.log_changed.emit()
                block,key = FileDBMaster.retrieve_block(data['Block No.'],data['filename'],addr[0])
                data = {'header':'Send block','Block Key':key,'Block Content':block}
                jsonObj = json.dumps(data)
                msg = jsonObj.encode('utf-8')
                cipher = Encryption.encrypt(msg,KEY)
                conn.send(cipher)
                string = "Block sent to client ,"+addr[0]
                files = FileDBMaster.no_of_files()
                blocks = FileDBMaster.no_of_blocks()
                self.signals.records_changed.emit()
                self.signals.log_changed.emit()

            elif data['header']=='Download Successful':
                string = "Deleting file from storage"
                self.signals.log_changed.emit()
                FileDBMaster.delete_records(data['filename'],addr[0])
                string = "Deleted!"
                data = {'header':'deleted'}
                jsonObj = json.dumps(data)
                msg = jsonObj.encode('utf-8')
                cipher = Encryption.encrypt(msg,KEY)
                conn.send(cipher)
                self.signals.log_changed.emit()
                files = FileDBMaster.no_of_files()
                blocks = FileDBMaster.no_of_blocks()
                self.signals.records_changed.emit()

class ServerWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.title = "TitanBox - Server (Running)"
        self.left = 10
        self.top = 10
        self.width = 960
        self.height = 700

        self.setWindowIcon(QIcon('image.jpeg'))

        self.log = QPlainTextEdit(self)
        self.log.move(15,15)
        self.log.resize(930,400)
        self.log.setReadOnly(True)


        self.records = QPlainTextEdit(self)
        self.records.move(15,440)
        self.records.resize(450,180)
        self.records.setReadOnly(True)

        self.stats = QPlainTextEdit(self)
        self.stats.move(480,440)
        self.stats.resize(465,180)
        self.stats.setReadOnly(True)

        host_label = QLabel("Host :",self)
        host_label.move(20,660)

        host_box = QLineEdit(self)
        host_box.move(65,660)
        host_box.setReadOnly(True)
        host_box.setText(host)

        port_label = QLabel("Port :",self)
        port_label.move(200,660)

        port_box = QLineEdit(self)
        port_box.move(250,660)
        port_box.setReadOnly(True)
        port_box.setText(str(port))

        reset = QPushButton("Reset",self)
        reset.move(840,660)
        reset.clicked.connect(self.reset_clicked)
        self.threadpool = QThreadPool()
        self.initUI()


    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left,self.top,self.width,self.height)
        self.show_records(0,0)
        self.show_stats(0,0)
        server = Server()
        server.signals.log_changed.connect(self.refresh_log)
        server.signals.status_changed.connect(self.refresh_stats)
        server.signals.records_changed.connect(self.refresh_records)
        self.threadpool.start(server)


    def refresh_log(self):
        self.show_log(string)

    def refresh_records(self):
        self.show_records(files,blocks)

    def refresh_stats(self):
        self.show_stats(users,active_users)

    def show_log(self,msg):
        self.log.appendPlainText(msg)

    def show_stats(self,users,active_users):
        self.stats.clear()
        self.stats.appendPlainText("Total Users :"+str(users))
        self.stats.appendPlainText("Users currently logged in : "+str(active_users))

    def show_records(self,files,blocks):
        self.records.clear()
        self.records.appendPlainText("Total Files : "+str(files))
        self.records.appendPlainText("Total blocks : "+str(blocks))

    def reset_clicked(self):
        if LoginDBMaster.no_of_active_users() > 0 :
            admin_reply = QMessageBox.question(self,"Busy","Clients logged in. Reset the server later.",QMessageBox.Ok,QMessageBox.Ok)
            return
        LoginDBMaster.reset()
        self.show_log("Server reset")
        self.show_records(FileDBMaster.no_of_files(),FileDBMaster.no_of_blocks())
        self.show_stats(LoginDBMaster.no_of_users(),LoginDBMaster.no_of_active_users())


App = QApplication(sys.argv)
window = ServerWindow()
window.show()
sys.exit(App.exec_())



