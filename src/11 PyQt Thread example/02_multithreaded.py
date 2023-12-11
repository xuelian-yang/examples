# -*- coding: utf-8 -*-

# @File        :   02_multithreaded.py
# @Description :   多线程样例

# here put the import lib
import os.path as osp

from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
from requests import Session
from threading import Thread
from time import sleep

# name = input("Please enter your name: ")  # 从控制台读取
name = osp.basename(__file__)

chat_url = "https://build-system.fman.io/chat"
server = Session()

# GUI:
app = QApplication([])

text_area = QPlainTextEdit()
text_area.setReadOnly(True)  # 只读
# text_area.setFocusPolicy(Qt.NoFocus)
message = QLineEdit()

# 布局
layout = QVBoxLayout()
layout.addWidget(text_area)
layout.addWidget(message)

# 主窗口
window = QWidget()
window.setLayout(layout)
window.show()

# Event handlers:
new_messages = []
def fetch_new_messages():
    """ 子线程循环任务 """
    while True:
        response = server.get(chat_url).text
        if response:
            new_messages.append(response)
        # sleep(.5)  # Session 太频繁会报错 "429 Too many requests"
        sleep(3.0)

thread = Thread(target=fetch_new_messages, daemon=True)  # 多线程
thread.start()

def display_new_messages():
    while new_messages:
        # text_area.appendPlainText(new_messages.pop(0))  # 包含太多 HTML Tag
        text_area.appendHtml(new_messages.pop(0))

def send_message():
    """ 发送消息 """
    server.post(chat_url, {"name": name, "message": message.text()})
    message.clear()

# Signals:
message.returnPressed.connect(send_message)
timer = QTimer()
timer.timeout.connect(display_new_messages)
timer.start(1000)

app.exec()
