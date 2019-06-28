# -*- coding:utf-8 -*-
"""    
time   = '2019/5/30 9:13'
author = 'Gregory'
filename = 'MainUi.py'
"""

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import sys
import threading
import paho.mqtt.client as mqtt
window_width = 1920
window_height = 1080
button_width = 48

data = ""
is_reconnect = False
ip = '192.168.134.93'
port = '61613'
user = 'admin'
passwd = 'password'
topic = "iot/"

mutex = threading.Lock()

class MosquittoSub(QThread):
    temp_update_sig = pyqtSignal()
    hum_update_sig = pyqtSignal()
    light_update_sig = pyqtSignal()

    def __init__(self):
        super(QThread, self).__init__()
        self.data = {}
        self.HOST = ip
        self.PORT = int(port)
        self.user = user
        self.passwd = passwd
        client_id = "client2"
        print(client_id)
        self.topic = topic

        self.client = mqtt.Client(client_id)  # ClientId不能重复，所以使用当前时间

    def run(self):
        self.client.username_pw_set(self.user, self.passwd)  # 必须设置，否则会返回「Connected with result code 4」
        self.client.on_connect = self.on_connect    #设置连接回调函数
        self.client.on_message = self.on_message    #设置收到消息回调函数
        self.client.connect_async(self.HOST, self.PORT, 60) #注意使用异步通信+start方式
        self.client.loop_start()
        global is_reconnect #重新连的标志
        while True:
            if is_reconnect == False:
                continue
            else:
                print("True")
                self.client.loop_stop() #订阅者循环等待消息
                self.re_connect(ip, int(port), user, passwd, topic)
                mutex.acquire()
                is_reconnect = False
                mutex.release()

    def on_connect(self, client, userdata, flags, rc):
        print("Connected with result code " + str(rc))
        self.client.subscribe(self.topic)

    def on_message(self, client, userdata, msg):
        print(msg.topic + " " + msg.payload.decode("utf-8"))
        global data
        mutex.acquire()
        data = str(msg.payload.decode("utf-8")) #获取收到的消息
        mutex.release()
        print("emit all")
        #发出更新信号
        self.temp_update_sig.emit()
        self.hum_update_sig.emit()
        self.light_update_sig.emit()

    def re_connect(self, host, port, user, passwd, topic):
        # self.client.unsubscribe("iot/+")
        self.disconnect()
        self.topic = topic
        self.client.username_pw_set(user, passwd)
        self.client.connect_async(host, port, 60)
        self.client.loop_start()

    def disconnect(self):
        self.client.disconnect()

class MainUi(QWidget):
    valid_signal = pyqtSignal()
    def __init__(self):
        super(MainUi, self).__init__()
        global ip
        global port
        global user
        global passwd

        self.widgets = []

        self.mosquitto_sub = MosquittoSub()
        self.mosquitto_sub.start()

        self.ip_label = QLabel(self)
        self.ip_label.setFixedHeight(32)
        self.ip_label.setText("ip地址：")
        self.widgets.append(self.ip_label)

        self.ip_edit = QLineEdit(self)
        self.ip_edit.setFixedWidth(button_width*3)
        self.ip_edit.setFixedHeight(32)
        self.ip_edit.setText(ip)
        self.ip_edit.textChanged.connect(self.set_text_ip)

        ip_re_str = '^((25[0-5]|2[0-4]\d|((1\d{2})|([1-9]?\d)))\.){3}(25[0-5]|2[0-4]\d|((1\d{2})|([1-9]?\d)))$'
        ip_re = QRegExp(ip_re_str)
        self.ip_edit.setValidator(QRegExpValidator(ip_re,self))
        self.widgets.append(self.ip_edit)

        self.port_label = QLabel(self)
        self.port_label.setFixedHeight(32)
        self.port_label.setText("端口号：")
        self.widgets.append(self.port_label)

        self.port_edit = QLineEdit(self)
        self.port_edit.setFixedWidth(button_width)
        self.port_edit.setFixedHeight(32)
        self.port_edit.setText(port)
        self.port_edit.textChanged.connect(self.set_text_port)

        self.port_edit.setValidator(QIntValidator(0,65535))
        self.widgets.append(self.port_edit)

        self.user_label = QLabel(self)
        self.user_label.setFixedHeight(32)
        self.user_label.setText("用户名：")
        self.widgets.append(self.user_label)

        self.user_edit = QLineEdit(self)
        self.user_edit.setFixedWidth(button_width * 4)
        self.user_edit.setFixedHeight(32)
        self.user_edit.setText(user)
        self.user_edit.textChanged.connect(self.set_text_user)

        user_re = QRegExp('^\w+$')
        self.user_edit.setValidator(QRegExpValidator(user_re,self))
        self.user_edit.setMaxLength(23)
        self.widgets.append(self.user_edit)

        self.passwd_label = QLabel(self)
        self.passwd_label.setFixedHeight(32)
        self.passwd_label.setText("密码：")
        self.widgets.append(self.passwd_label)

        self.passwd_edit = QLineEdit(self)
        self.passwd_edit.setFixedWidth(button_width * 4)
        self.passwd_edit.setFixedHeight(32)
        self.passwd_edit.setEchoMode(QLineEdit.Password)
        self.passwd_edit.setText(passwd)
        self.passwd_edit.textChanged.connect(self.set_text_passwd)


        passwd_re = QRegExp('^\w+$')
        self.passwd_edit.setValidator(QRegExpValidator(passwd_re))
        self.passwd_edit.setMaxLength(12)
        self.widgets.append(self.passwd_edit)

        self.ok_button = QPushButton(self)
        self.ok_button.setFixedHeight(32)
        self.ok_button.setFixedWidth(button_width*2)
        self.ok_button.setText('连接')
        self.ok_button.clicked.connect(self.process_all_text)
        self.widgets.append(self.ok_button)

        self.show_passwd_button = QPushButton(self)
        self.show_passwd_button.setFixedHeight(32)
        self.show_passwd_button.setFixedWidth(button_width*2)
        self.show_passwd_button.setText('显示密码')
        self.show_passwd_button.clicked.connect(self.show_passwd)
        self.widgets.append(self.show_passwd_button)

        self.right_widgets = []
        self.temp_label = QLabel(self)
        self.temp_label.setFixedHeight(32)
        self.temp_label.setText("温度：")
        self.mosquitto_sub.temp_update_sig.connect(self.update_temp)
        self.right_widgets.append(self.temp_label)

        self.temp_edit = QLineEdit(self)
        self.temp_edit.setFixedHeight(32)
        self.right_widgets.append(self.temp_edit)


        self.hum_label = QLabel(self)
        self.hum_label.setFixedHeight(32)
        self.hum_label.setText("湿度：")
        self.mosquitto_sub.hum_update_sig.connect(self.update_hum)
        self.right_widgets.append(self.hum_label)

        self.hum_edit = QLineEdit(self)
        self.hum_edit.setFixedHeight(32)
        self.right_widgets.append(self.hum_edit)

        self.light_label = QLabel(self)
        self.light_label.setFixedHeight(32)
        self.light_label.setText("光照：")
        self.mosquitto_sub.light_update_sig.connect(self.update_light)
        self.right_widgets.append(self.light_label)

        self.light_edit = QLineEdit(self)
        self.light_edit.setFixedHeight(32)
        self.right_widgets.append(self.light_edit)

        self.setGeometry(window_width / 3, window_height / 3, 300, 180)
        self.setWindowFlags(self.windowFlags()&~Qt.WindowMaximizeButtonHint)#取消最大化

        self.left_layout = QGridLayout()
        positions = [(i, j) for i in range(5) for j in range(2)]
        for position, widget in zip(positions, self.widgets):
            self.left_layout.addWidget(widget,*position)
        self.setting_widget = QWidget()
        self.setting_widget.setLayout(self.left_layout)

        self.right_layout = QGridLayout()
        positions = [(i, j) for i in range(3) for j in range(2)]
        for position, widget in zip(positions, self.right_widgets):
            self.right_layout.addWidget(widget,*position)
        self.info_widget = QWidget()
        self.info_widget.setLayout(self.right_layout)

        self.H_layout = QHBoxLayout()
        self.H_layout.addWidget(self.setting_widget)
        self.H_layout.addWidget(self.info_widget)

        self.setLayout(self.H_layout)


    def set_text_ip(self):
        global ip
        mutex.acquire()
        ip = self.ip_edit.text()
        mutex.release()

    def set_text_port(self):
        global port
        mutex.acquire()
        port = self.port_edit.text()
        mutex.release()

    def set_text_user(self):
        global user
        mutex.acquire()
        user = self.user_edit.text()
        mutex.release()

    def set_text_passwd(self):
        global passwd
        mutex.acquire()
        passwd = self.passwd_edit.text()
        mutex.release()

    def process_all_text(self):
        global ip
        global port
        global user
        global passwd
        ip_re = QRegExp('^((25[0-5]|2[0-4]\d|((1\d{2})|([1-9]?\d)))\.){3}(25[0-5]|2[0-4]\d|((1\d{2})|([1-9]?\d)))$')
        user_re = QRegExp('^\w+$')
        passwd_re = QRegExp('^\w+$')
        ip_validator = QRegExpValidator(ip_re,self)
        port_validator = QIntValidator(0,65535)
        user_validator = QRegExpValidator(user_re,self)
        passwd_validator = QRegExpValidator(passwd_re,self)

        if ip_validator.validate(ip,0)[0] != QValidator.Acceptable:
            QMessageBox.information(self,"注意","ip地址输入类型错误，请重新输入！",QMessageBox.Yes)
            return
        if port_validator.validate(port,0)[0] != QValidator.Acceptable:
            QMessageBox.information(self, "注意", "端口号输入类型错误，请重新输入！", QMessageBox.Yes)
            return
        if user_validator.validate(user,0)[0] != QValidator.Acceptable:
            QMessageBox.information(self, "注意", "用户名输入类型错误，请重新输入！", QMessageBox.Yes)
            return
        if passwd_validator.validate(passwd,0)[0] != QValidator.Acceptable:
            QMessageBox.information(self, "注意", "密码输入类型错误，请重新输入！", QMessageBox.Yes)
            return
        print('info right, ip:{}, port:{}, user:{}, passwd:{}'.format(ip,port,user,passwd))

        mutex.acquire()
        global is_reconnect
        is_reconnect = True
        mutex.release()

    def show_passwd(self):
        if self.show_passwd_button.text() == '显示密码':
            self.passwd_edit.setEchoMode(QLineEdit.Normal)
            self.show_passwd_button.setText('隐藏密码')
        else:
            self.passwd_edit.setEchoMode(QLineEdit.Password)
            self.show_passwd_button.setText('显示密码')

    def closeEvent(self, QCloseEvent):
        self.mosquitto_sub.disconnect()

    def update_temp(self):
        global data
        mutex.acquire()
        temp = str(data).split(' ')[0]
        self.temp_edit.setText(temp)
        print("set temp %s" % (temp))
        mutex.release()

    def update_hum(self):
        global data
        mutex.acquire()
        hum = str(data).split(' ')[1]
        self.hum_edit.setText(hum)
        mutex.release()

    def update_light(self):
        global data
        mutex.acquire()
        light = str(data).split(' ')[2]
        self.light_edit.setText(light)
        mutex.release()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setApplicationName("温湿度信息客户端")
    window = MainUi()
    # window.setFixedWidth(540)
    # window.setFixedHeight(400)
    window.show()
    sys.exit(app.exec_())
