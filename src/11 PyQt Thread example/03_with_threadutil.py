# -*- coding: utf-8 -*-

# @File        :   03_with_threadutil.py
# @Description :   改进版的多线程样例

# here put the import lib
import os.path as osp
from requests import Session
import sys
from time import sleep
from threading import Thread

from PyQt6.QtCore import *
from PyQt6.QtWidgets import *

# 自定义函数
sys.path.append(osp.join(osp.dirname(__file__), './'))
from threadutil import run_in_main_thread

# name = input("Please enter your name: ")  # 从控制台读取
name = osp.basename(__file__)

chat_url = "https://build-system.fman.io/chat"
server = Session()

# GUI:
app = QApplication([])

# 控件
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

append_message = run_in_main_thread(text_area.appendPlainText)  # 多线程封装

def fetch_new_messages():
    """ 解析数据 """
    while True:
        response = server.get(chat_url).text
        if response:
            append_message(response)
        # sleep(.5)  # Session 太频繁会报错 "429 Too many requests"
        sleep(3.0)

def send_message():
    """ 发送消息 """
    server.post(chat_url, {"name": name, "message": message.text()})
    message.clear()

# Signals:
message.returnPressed.connect(send_message)

thread = Thread(target=fetch_new_messages, daemon=True)  # 多线程封装
thread.start()

app.exec()
