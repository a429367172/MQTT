# -*- coding:utf-8 -*-
"""    
time   = '2019/5/30 8:22'
author = 'Gregory'
filename = 'MosquittSub.py'
"""
import paho.mqtt.client as mqtt
from PyQt5.QtCore import *

class MosquittoSub(QThread):

    def __init__(self, host, port, user, passwd, topic):
        super(QThread, self).__init__()
        self.data = {}
        self.HOST = host
        self.PORT = port
        self.user = user
        self.passwd = passwd
        client_id = "client1"
        print(client_id)
        self.topic = topic
        self.success_sig = pyqtSignal()
        self.fail_sig = pyqtSignal()

        self.client = mqtt.Client(client_id)  # ClientId不能重复，所以使用当前时间

    def run(self):
        self.client.username_pw_set(self.user, self.passwd)  # 必须设置，否则会返回「Connected with result code 4」
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.connect(self.HOST, self.PORT, 60)
        self.client.loop_forever()
        # self.client.connect_async(self.HOST, self.PORT, 60)
        # self.client.loop_start()

    def on_connect(self, client, userdata, flags, rc):
        print("Connected with result code " + str(rc))
        print("type rc %s" % type(rc))
        self.client.subscribe(self.topic)
        if(rc == 0):
            self.success_sig.emit()
        else:
            self.fail_sig.emit()

    def on_message(self, client, userdata, msg):
        print(msg.topic + " " + msg.payload.decode("utf-8"))
        self.data = {msg.topic : msg.payload.decode("utf-8")}

    def re_connect(self, host, port, user, passwd, topic):
        # self.client.unsubscribe("iot/+")
        self.disconnect()
        self.topic = topic
        self.client.username_pw_set(user, passwd)
        self.client.connect(host, port, 60)

    def disconnect(self):
        self.client.disconnect()

    def get_data(self):
        return self.data


